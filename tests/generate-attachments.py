#!/usr/bin/env python3
"""
Generate attachment YAML files from Antora tutorial .adoc files.

Walks each tutorial top-to-bottom extracting every Kubernetes manifest
(in document order) and writes them as individual YAML files under
the module's attachments directory.

Usage:
    python generate-attachments.py modules/vm-configuration/pages/internal-dns-for-vms.adoc
    python generate-attachments.py --dry-run modules/networking/pages/cudn-localnet-vlan.adoc
    python generate-attachments.py --all
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


# ── Data ─────────────────────────────────────────────────────────────


@dataclass
class Resource:
    """A Kubernetes resource extracted from the tutorial."""

    order: int
    kind: str
    api_version: str
    name: str
    namespace: str | None
    yaml_content: str
    filename: str


# ── Parsing helpers ──────────────────────────────────────────────────


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


def _xref_above(lines: list[str], fence: int) -> str | None:
    """Look up to 5 lines before a fence for xref:attachment$<file>."""
    for i in range(fence - 1, max(fence - 6, -1), -1):
        m = re.search(r"xref:attachment\$([^\[]+)", lines[i])
        if m:
            return Path(m.group(1).strip()).name
        if lines[i].strip().startswith("=") or lines[i].strip() == "----":
            break
    return None


def _heredoc_yamls(block: str) -> list[str]:
    """Extract YAML from ``oc apply/create -f - <<EOF ... EOF`` blocks."""
    yamls: list[str] = []
    for seg in re.split(r"^EOF\s*$", block, flags=re.MULTILINE):
        m = re.search(
            r"oc\s+(?:apply|create)\s+-f\s+-\s*<<\s*['\"]?EOF['\"]?\s*\n", seg
        )
        if m:
            y = seg[m.end() :].strip()
            if y:
                yamls.append(y + "\n")
    return yamls


def _namespace_yamls(block: str) -> list[str]:
    """Synthesise Namespace YAML from oc new-project / oc create namespace."""
    yamls: list[str] = []
    for pat in (r"oc\s+new-project\s+(\S+)", r"oc\s+create\s+namespace\s+(\S+)"):
        for m in re.finditer(pat, block):
            yamls.append(
                f"apiVersion: v1\nkind: Namespace\nmetadata:\n"
                f"  name: {m.group(1)}\n"
            )
    return yamls


def _remove_callout_markers(block: str) -> str:
    """Sanitize codeblocks of `<.>` or `<#>` callout markers."""
    pattern = r'\s*(?:(?:#|//|;;|--)\s*)?(?:<(?:\d+|\.)>\s*)+$'
    lines = block.split("\n")
    cleaned = [re.sub(pattern, '', line) for line in lines]
    return "\n".join(cleaned)


# ── Tutorial parser ──────────────────────────────────────────────────


def parse_tutorial(adoc_path: str) -> tuple[str, list[Resource]]:
    """Parse a tutorial .adoc and return (title, [Resource ...]).

    Extracts Kubernetes manifests only — used for attachment generation.
    """
    lines = Path(adoc_path).read_text().split("\n")

    title = next(
        (l[2:].strip()
         for l in lines
         if l.startswith("= ") and not l.startswith("== ")),
        "Unknown Tutorial",
    )

    resources: list[Resource] = []
    seen: set = set()
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
        block = _remove_callout_markers(block)
        xref = _xref_above(lines, fence_open)

        yamls = _namespace_yamls(block)
        yamls += _heredoc_yamls(block)

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
            xref = None

        i = block_end + 1

    return title, resources


def resolve_paths(adoc_path: str) -> tuple[Path, str, str]:
    """Derive (repo_root, module_name, tutorial_name) from an .adoc path."""
    adoc = Path(adoc_path).resolve()
    m = re.search(r"(.+)/modules/([^/]+)/pages/([^/]+)\.adoc$", str(adoc))
    if not m:
        sys.exit(
            f"Error: expected .../modules/<module>/pages/<tutorial>.adoc\n"
            f"  got: {adoc}"
        )
    return Path(m.group(1)), m.group(2), m.group(3)


# ── Output ───────────────────────────────────────────────────────────


def write_attachments(
    resources: list[Resource], dest: Path, dry_run: bool
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


# ── CLI ──────────────────────────────────────────────────────────────


def process_file(adoc_file: str, dry_run: bool, force: bool):
    """Process a single tutorial file."""
    repo_root, module, tutorial = resolve_paths(adoc_file)
    title, resources = parse_tutorial(adoc_file)

    if not resources:
        print(f"  {module}/{tutorial}: no manifests found, skipping.")
        return

    print(f"\nTutorial: {title}")
    print(f"Module:   {module}")
    print(f"Name:     {tutorial}")
    print(f"\nExtracted {len(resources)} resource(s):\n")
    print(f"  {'#':<4} {'Kind':<30} {'Name':<35} {'Attachment'}")
    print(f"  {'─' * 4} {'─' * 30} {'─' * 35} {'─' * 30}")
    for r in resources:
        print(f"  {r.order:<4} {r.kind:<30} {r.name:<35} {r.filename}")

    att_dir = repo_root / "modules" / module / "attachments" / tutorial
    print(f"\nAttachments → {att_dir}/")
    write_attachments(resources, att_dir, dry_run)
    print()


def main():
    ap = argparse.ArgumentParser(
        description="Generate attachment YAML files from Antora tutorial .adoc files."
    )
    ap.add_argument("adoc_file", nargs="?", help="Path to the tutorial .adoc file")
    ap.add_argument(
        "--dry-run", action="store_true", help="Preview without writing files"
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing attachment files",
    )
    ap.add_argument(
        "--all",
        action="store_true",
        help="Generate attachments for all tutorials",
    )
    args = ap.parse_args()

    if args.all:
        repo_root = Path(__file__).resolve().parent.parent
        adoc_files = sorted(repo_root.glob("modules/*/pages/*.adoc"))
        adoc_files = [f for f in adoc_files if f.name != "index.adoc"]
        print(f"Processing {len(adoc_files)} tutorials...\n")
        for adoc in adoc_files:
            process_file(str(adoc), args.dry_run, args.force)
        print("Done.")
    elif args.adoc_file:
        process_file(args.adoc_file, args.dry_run, args.force)
        print("Done.")
    else:
        ap.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
