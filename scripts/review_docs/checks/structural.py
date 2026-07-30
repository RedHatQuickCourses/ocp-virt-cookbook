"""Structural checks — operate on the full file content or filesystem."""

import re
from pathlib import Path
from typing import List

from ..config import Config
from ..models import FileResult
from ..registry import register_check


@register_check("trailing-newline", "warning", "structural")
def check_trailing_newline(
    filepath: str,
    lines: List[str],
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check file ends with a newline character."""
    with open(filepath, "rb") as f:
        content = f.read()
        if content and content[-1:] != b"\n":
            file_result.add_finding(
                cfg,
                "trailing-newline",
                None,
                "File does not end with a newline character",
            )


@register_check("tutorial-sections", "warning", "structural")
def check_tutorial_sections(
    filepath: str,
    lines: List[str],
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check tutorial pages have required sections."""
    # Only applies to tutorial pages (not index or nav files)
    if not re.search(r"modules/[^/]+/pages/[^/]+\.adoc$", filepath):
        return
    if filepath.endswith("/index.adoc") or filepath.endswith("/nav.adoc"):
        return

    has_prerequisites = False
    has_summary = False

    for line in lines:
        if re.match(r"^==\s+Prerequisites", line):
            has_prerequisites = True
        if re.match(r"^==\s+(Summary|Verification)", line):
            has_summary = True

    if not has_prerequisites:
        file_result.add_finding(
            cfg,
            "tutorial-sections",
            None,
            "Tutorial page missing '== Prerequisites' section",
        )
    if not has_summary:
        file_result.add_finding(
            cfg,
            "tutorial-sections",
            None,
            "Tutorial page missing '== Summary' or '== Verification' section",
        )


@register_check("yaml-validation", "error", "structural")
def check_yaml_validation(
    filepath: str,
    lines: List[str],
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Validate YAML syntax in code blocks (requires PyYAML)."""
    try:
        import yaml  # noqa: F401
    except ImportError:
        return

    in_yaml_header = False
    in_yaml_content = False
    yaml_content = ""
    block_start_line = 0

    for line_num, line in enumerate(lines, 1):
        # Detect start of YAML block
        if re.match(r"^\[source,yaml", line):
            in_yaml_header = True
            yaml_content = ""
            block_start_line = line_num
            continue

        # Detect code block delimiter
        if re.match(r"^----", line):
            if in_yaml_header:
                in_yaml_header = False
                in_yaml_content = True
                continue
            elif in_yaml_content:
                # Validate accumulated YAML
                if yaml_content.strip():
                    try:
                        import yaml as _yaml

                        _yaml.safe_load(yaml_content)
                    except Exception:
                        file_result.add_finding(
                            cfg,
                            "yaml-validation",
                            block_start_line,
                            f"line {block_start_line}: Invalid YAML syntax in code block",
                        )
                yaml_content = ""
                in_yaml_content = False
                continue

        if in_yaml_content:
            yaml_content += line + "\n"


@register_check("nav-xrefs", "error", "structural")
def check_nav_xrefs(
    filepath: str,
    lines: List[str],
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check nav.adoc xref targets exist."""
    # Only applies to nav.adoc files
    if not filepath.endswith("/nav.adoc"):
        return

    module_dir = Path(filepath).parent
    pages_dir = module_dir / "pages"

    if not pages_dir.is_dir():
        file_result.add_finding(
            cfg,
            "nav-xrefs",
            None,
            f"Pages directory not found for {filepath}: {pages_dir}",
        )
        return

    for line_num, line in enumerate(lines, 1):
        m = re.search(r"xref:([^\[]+)\[", line)
        if m:
            target = m.group(1)
            target_file = pages_dir / target
            if not target_file.is_file():
                file_result.add_finding(
                    cfg,
                    "nav-xrefs",
                    line_num,
                    f"line {line_num} in {filepath}: xref target does not exist: {target_file}",
                )
