#!/usr/bin/env python3
"""
Generate test scaffolding from Antora tutorial .adoc files.

Walks the tutorial top-to-bottom extracting every Kubernetes manifest
(in document order) into attachment YAML files and an Ansible test playbook.

Detection rules per fenced block (in priority order):
  1. oc apply/create -f - <<EOF … EOF  →  extract YAML between markers
  2. Bare [source,yaml] with apiVersion + kind + xref:attachment$ above  →  whole block
  3. oc new-project / oc create namespace  →  synthesise Namespace YAML

Usage:
    python generate-test.py modules/vm-configuration/pages/internal-dns-for-vms.adoc
    python generate-test.py --dry-run modules/networking/pages/cudn-localnet-vlan.adoc
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


# ── Data ────────────────────────────────────────────────────────────


@dataclass
class Resource:
    """A Kubernetes resource extracted from the tutorial."""

    order: int
    kind: str
    api_version: str
    name: str
    namespace: Optional[str]
    yaml_content: str
    filename: str


# ── Parser helpers ──────────────────────────────────────────────────


def _k8s_fields(yaml_text: str) -> dict:
    """Extract apiVersion, kind, metadata.name/namespace via regex."""
    d: dict = {}
    for key, rx in (
        ("api_version", r"^apiVersion:\s*(.+)$"),
        ("kind", r"^kind:\s*(.+)$"),
    ):
        m = re.search(rx, yaml_text, re.MULTILINE)
        if m:
            d[key] = m.group(1).strip().strip("\"'")

    m = re.search(r"^metadata:\s*\n((?:[ \t]+.*\n)*)", yaml_text, re.MULTILINE)
    if m:
        meta = m.group(1)
        ind = re.search(r"^([ \t]+)\S", meta, re.MULTILINE)
        if ind:
            p = re.escape(ind.group(1))
            for key in ("name", "namespace"):
                mv = re.search(f"^{p}{key}:\\s*(.+)$", meta, re.MULTILINE)
                if mv:
                    d[key] = mv.group(1).strip().strip("\"'")
    return d


def _xref_above(lines: List[str], fence: int) -> Optional[str]:
    """Look up to 5 lines before a fence for xref:attachment$<file>."""
    for i in range(fence - 1, max(fence - 6, -1), -1):
        m = re.search(r"xref:attachment\$([^\[]+)", lines[i])
        if m:
            return Path(m.group(1).strip()).name
        if lines[i].strip().startswith("=") or lines[i].strip() == "----":
            break
    return None


def _heredoc_yamls(block: str) -> List[str]:
    """Extract YAML from ``oc apply/create -f - <<EOF … EOF`` blocks."""
    yamls: List[str] = []
    for seg in re.split(r"^EOF\s*$", block, flags=re.MULTILINE):
        m = re.search(
            r"oc\s+(?:apply|create)\s+-f\s+-\s*<<\s*['\"]?EOF['\"]?\s*\n", seg
        )
        if m:
            y = seg[m.end() :].strip()
            if y:
                yamls.append(y + "\n")
    return yamls


def _namespace_yamls(block: str) -> List[str]:
    """Synthesise Namespace YAML from oc new-project / oc create namespace."""
    yamls: List[str] = []
    for pat in (r"oc\s+new-project\s+(\S+)", r"oc\s+create\s+namespace\s+(\S+)"):
        for m in re.finditer(pat, block):
            yamls.append(
                f"apiVersion: v1\nkind: Namespace\nmetadata:\n"
                f"  name: {m.group(1)}\n"
            )
    return yamls


# ── Main parser ─────────────────────────────────────────────────────


def parse_tutorial(adoc_path: str) -> Tuple[str, List[Resource]]:
    """Parse a tutorial .adoc and return (title, [Resource …])."""
    lines = Path(adoc_path).read_text().split("\n")

    # Title
    title = next(
        (l[2:].strip() for l in lines if l.startswith("= ") and not l.startswith("== ")),
        "Unknown Tutorial",
    )

    resources: List[Resource] = []
    seen: set = set()  # (kind, name, content) for deduplication
    seq = 0
    i = 0

    while i < len(lines):
        if lines[i].strip() != "----":
            i += 1
            continue

        fence_open = i
        block_end = next(
            (j for j in range(i + 1, len(lines)) if lines[j].strip() == "----"),
            None,
        )
        if block_end is None:
            i += 1
            continue

        block = "\n".join(lines[i + 1 : block_end])
        xref = _xref_above(lines, fence_open)

        # Rule 1: namespace commands (always check — may coexist with heredocs)
        yamls = _namespace_yamls(block)

        # Rule 2: oc apply/create heredoc
        yamls += _heredoc_yamls(block)

        # Rule 3: bare YAML with apiVersion + kind and a download xref
        if not yamls and xref:
            if re.search(r"^apiVersion:", block, re.MULTILINE) and re.search(
                r"^kind:", block, re.MULTILINE
            ):
                yamls = [block.strip() + "\n"]

        for y in yamls:
            f = _k8s_fields(y)
            if "kind" not in f or "name" not in f:
                continue
            key = (f["kind"], f["name"], y.strip())
            if key in seen:
                continue
            seen.add(key)
            seq += 1
            resources.append(
                Resource(
                    order=seq,
                    kind=f["kind"],
                    api_version=f.get("api_version", "v1"),
                    name=f["name"],
                    namespace=f.get("namespace"),
                    yaml_content=y,
                    filename=xref or f"{f['kind'].lower()}-{f['name']}.yaml",
                )
            )
            xref = None  # consume for first manifest only

        i = block_end + 1

    return title, resources


# ── Output generators ───────────────────────────────────────────────


def write_attachments(
    resources: List[Resource], dest: Path, dry_run: bool
) -> None:
    """Write extracted YAML to attachment files (idempotent)."""
    if not dry_run:
        dest.mkdir(parents=True, exist_ok=True)

    for r in resources:
        fp = dest / r.filename
        if fp.exists():
            if fp.read_text().strip() == r.yaml_content.strip():
                print(f"  [skip]     {r.filename}  (content matches)")
                continue
            action = "overwrite"
        else:
            action = "create"

        if dry_run:
            print(f"  [dry-run]  {r.filename}  (would {action})")
        else:
            fp.write_text(r.yaml_content)
            print(f"  [{action}]  {r.filename}")


def _var(kind: str, name: str) -> str:
    """Safe Ansible variable name."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", f"{kind.lower()}_{name}")


def generate_playbook(
    resources: List[Resource], title: str, tutorial: str, module: str
) -> str:
    """Generate an Ansible test playbook as a YAML string."""
    L: List[str] = [
        "---",
        f"- name: Test {title} Tutorial",
        "  hosts: localhost",
        "  connection: local",
        "  gather_facts: false",
        "",
        "  vars_files:",
        "    - vars.yaml",
        "",
        "  vars:",
        f'    attachment_dir: "{{{{ playbook_dir }}}}/../../../modules/{module}/attachments/{tutorial}"',
        "",
        "  tasks:",
        "    - name: Run tutorial test",
        "      block:",
    ]

    for r in resources:
        v = _var(r.kind, r.name)
        ns = [f"            namespace: {r.namespace}"] if r.namespace else []

        L += [
            f'        - name: "Apply {r.kind} {r.name}"',
            "          kubernetes.core.k8s:",
            "            state: present",
            f'            src: "{{{{ attachment_dir }}}}/{r.filename}"',
            "",
            f'        - name: "Verify {r.kind} {r.name}"',
            "          kubernetes.core.k8s_info:",
            f"            api_version: {r.api_version}",
            f"            kind: {r.kind}",
            *ns,
            f"            name: {r.name}",
            f"          register: {v}",
            f"          failed_when: {v}.resources | length == 0",
            "",
        ]

        if r.kind == "VirtualMachine":
            wv = f"vm_ready_{v}"
            L += [
                f'        - name: "Wait for VirtualMachine {r.name} to be ready"',
                "          kubernetes.core.k8s_info:",
                f"            api_version: {r.api_version}",
                "            kind: VirtualMachine",
                *ns,
                f"            name: {r.name}",
                f"          register: {wv}",
                "          until: >",
                f"            {wv}.resources | length > 0 and",
                f"            {wv}.resources[0].status.ready | default(false)",
                '          retries: "{{ (vm_timeout / 10) | int }}"',
                "          delay: 10",
                "",
            ]

    L += [
        "        - name: Test completed successfully",
        "          ansible.builtin.debug:",
        f'            msg: "{tutorial} tutorial test passed'
        f' - all resources created and verified"',
        "",
        "      always:",
        "        - name: Cleanup resources",
        "          when: cleanup | default(true)",
        "          block:",
    ]

    for r in reversed(resources):
        ns = [f"                namespace: {r.namespace}"] if r.namespace else []
        L += [
            f'            - name: "Delete {r.kind} {r.name}"',
            "              kubernetes.core.k8s:",
            "                state: absent",
            f"                api_version: {r.api_version}",
            f"                kind: {r.kind}",
            *ns,
            f"                name: {r.name}",
            "              ignore_errors: true",
            "",
        ]

    return "\n".join(L)


def generate_vars(resources: List[Resource]) -> str:
    """Generate a vars.yaml with sensible defaults."""
    L = ["---", "# Test variables (override with -e key=value)", ""]
    if any(r.kind == "VirtualMachine" for r in resources):
        L += ["# Timeout for VM readiness (seconds)", "vm_timeout: 600", ""]
    L += ["# Set to false to skip cleanup and inspect resources", "cleanup: true", ""]
    return "\n".join(L)


# ── CLI ─────────────────────────────────────────────────────────────


def resolve_paths(adoc_path: str) -> Tuple[Path, str, str]:
    """Derive (repo_root, module_name, tutorial_name) from an .adoc path."""
    adoc = Path(adoc_path).resolve()
    m = re.search(r"(.+)/modules/([^/]+)/pages/([^/]+)\.adoc$", str(adoc))
    if not m:
        sys.exit(
            f"Error: expected .../modules/<module>/pages/<tutorial>.adoc\n"
            f"  got: {adoc}"
        )
    return Path(m.group(1)), m.group(2), m.group(3)


def main():
    ap = argparse.ArgumentParser(
        description="Generate test scaffolding from Antora tutorial .adoc files."
    )
    ap.add_argument("adoc_file", help="Path to the tutorial .adoc file")
    ap.add_argument(
        "--dry-run", action="store_true", help="Preview without writing files"
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing test playbook and vars.yaml",
    )
    args = ap.parse_args()

    repo_root, module, tutorial = resolve_paths(args.adoc_file)
    title, resources = parse_tutorial(args.adoc_file)

    if not resources:
        print("No Kubernetes manifests found.")
        sys.exit(0)

    # Summary
    print(f"\nTutorial: {title}")
    print(f"Module:   {module}")
    print(f"Name:     {tutorial}")
    print(f"\nExtracted {len(resources)} resource(s):\n")
    print(f"  {'#':<4} {'Kind':<30} {'Name':<35} {'Attachment'}")
    print(f"  {'─' * 4} {'─' * 30} {'─' * 35} {'─' * 30}")
    for r in resources:
        print(f"  {r.order:<4} {r.kind:<30} {r.name:<35} {r.filename}")

    # Attachments
    att_dir = repo_root / "modules" / module / "attachments" / tutorial
    print(f"\nAttachments → {att_dir}/")
    write_attachments(resources, att_dir, args.dry_run)

    # Test scaffolding
    test_dir = repo_root / "tests" / module / tutorial
    pb_path = test_dir / f"test-{tutorial}.yaml"
    vars_path = test_dir / "vars.yaml"
    pb = generate_playbook(resources, title, tutorial, module)
    vr = generate_vars(resources)

    print(f"\nTest scaffolding → {test_dir}/")
    if args.dry_run:
        for p in (pb_path, vars_path):
            act = "would overwrite" if p.exists() else "would create"
            print(f"  [dry-run]  {p.name}  ({act})")
    else:
        test_dir.mkdir(parents=True, exist_ok=True)
        for p, c in ((pb_path, pb), (vars_path, vr)):
            if p.exists() and not args.force:
                print(
                    f"  [skip]     {p.name}"
                    f"  (already exists, use --force to overwrite)"
                )
            else:
                act = "overwrite" if p.exists() else "create"
                p.write_text(c)
                print(f"  [{act}]  {p.name}")

    print("\nDone.")


if __name__ == "__main__":
    main()
