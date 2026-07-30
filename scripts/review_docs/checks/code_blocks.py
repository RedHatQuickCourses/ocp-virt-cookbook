"""Code-block checks — run on lines inside ``----`` delimited code blocks."""

import re

from ..config import Config
from ..models import FileResult
from ..registry import register_check


@register_check("code-block-language", "warning", "code_block_boundary")
def check_code_block_language(
    line: str,
    line_num: int,
    state: dict,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check that a code block opening has a ``[source,language]`` specifier.

    Boundary checks are called when a ``----`` delimiter is encountered.
    ``state["boundary_direction"]`` is ``"open"`` or ``"close"``.
    ``state["prev_line"]`` contains the line immediately before the delimiter.
    """
    if state.get("boundary_direction") != "open":
        return

    prev = state.get("prev_line", "")
    m = re.match(r"^\[source,?([a-zA-Z0-9_-]*)\]", prev) or re.match(
        r"^\[source,?([a-zA-Z0-9_-]*),.*\]", prev
    )
    if not m:
        # No [source,...] attribute — but also skip bare [source] or [source ...]
        if not re.match(r"^\[source\s", prev) and not re.match(
            r"^\[source\]", prev
        ):
            file_result.add_finding(
                cfg,
                "code-block-language",
                line_num,
                f"line {line_num}: Code block delimiter without [source,language] specifier",
            )


@register_check("yaml-null-timestamps", "warning", "code_block_content")
def check_yaml_null_timestamps(
    line: str,
    line_num: int,
    state: dict,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check for creationTimestamp: null in YAML blocks."""
    if state.get("code_block_lang") == "yaml" and re.search(
        r"creationTimestamp:\s*null", line
    ):
        file_result.add_finding(
            cfg,
            "yaml-null-timestamps",
            line_num,
            f"line {line_num}: creationTimestamp: null found in YAML block",
        )


@register_check("yaml-flow-syntax", "warning", "code_block_content")
def check_yaml_flow_syntax(
    line: str,
    line_num: int,
    state: dict,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check for inline YAML flow syntax ({} or []) in YAML blocks."""
    if state.get("code_block_lang") != "yaml":
        return

    if re.search(r".*:\s*\{.*\}", line) or re.search(r".*:\s*\[.*\]", line):
        # Skip legitimate cases
        if not re.search(r"chpasswd:\s*\{.*\}", line) and not re.search(
            r"capabilities:$", line
        ):
            file_result.add_finding(
                cfg,
                "yaml-flow-syntax",
                line_num,
                f"line {line_num}: Inline YAML flow syntax detected (use block style)",
            )
