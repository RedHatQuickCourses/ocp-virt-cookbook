"""Prose checks — run on every non-comment, non-code-block line."""

import re

from ..config import Config
from ..models import FileResult, ParseState
from ..registry import register_check

# Admonition keywords (used by the admonition-capitalization check)
ADMONITIONS = r"NOTE|WARNING|TIP|IMPORTANT|CAUTION"


@register_check("heading-hierarchy", "error", "prose")
def check_heading_hierarchy(
    line: str,
    line_num: int,
    state: ParseState,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check heading hierarchy: no skipped levels, single H1, H1 first."""
    m = re.match(r"^(=+)\s+(.+)$", line)
    if not m:
        return

    equals = m.group(1)
    level = len(equals)

    # Count H1s
    if level == 1:
        state.h1_count += 1
        if state.h1_count > 1:
            file_result.add_finding(
                cfg,
                "heading-hierarchy",
                line_num,
                f"line {line_num}: Multiple H1 headings found (should have only one)",
            )
        if state.first_heading_found:
            file_result.add_finding(
                cfg,
                "heading-hierarchy",
                line_num,
                f"line {line_num}: H1 must be the first heading in the file",
            )

    state.first_heading_found = True

    # Check for skipped levels
    if state.heading_levels:
        prev_level = state.heading_levels[-1]
        if level > prev_level + 1:
            file_result.add_finding(
                cfg,
                "heading-hierarchy",
                line_num,
                f"line {line_num}: Heading level skipped (previous: {prev_level}, current: {level})",
            )

    state.heading_levels.append(level)


@register_check("heading-blank-line", "warning", "prose")
def check_heading_blank_line(
    line: str,
    line_num: int,
    state: ParseState,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check that headings are followed by a blank line."""
    prev_line = state.prev_line

    # Check if previous line was a heading and this line is not blank
    if re.match(r"^(=+)\s+(.+)$", prev_line):
        if line and not re.match(r"^:", line) and not re.match(r"^=", line):
            file_result.add_finding(
                cfg,
                "heading-blank-line",
                line_num - 1,
                f"line {line_num - 1}: Section heading not followed by blank line",
            )


@register_check("trailing-whitespace", "warning", "prose")
def check_trailing_whitespace(
    line: str,
    line_num: int,
    state: ParseState,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check for trailing whitespace."""
    if line and re.search(r"\s$", line):
        file_result.add_finding(
            cfg,
            "trailing-whitespace",
            line_num,
            f"line {line_num}: Trailing whitespace",
        )


@register_check("bare-urls", "warning", "prose")
def check_bare_urls(
    line: str,
    line_num: int,
    state: ParseState,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check for bare URLs not in link: macro."""
    if re.search(r"https?://", line) and not re.search(r"link:https?://", line):
        # Skip xref, image, include directives, and implicit URL macro
        if not re.match(r"^(xref:|image::|include::)", line) and not re.search(
            r"https?://[^\s]+\[", line
        ):
            file_result.add_finding(
                cfg,
                "bare-urls",
                line_num,
                f"line {line_num}: Bare URL not in link: macro",
            )


@register_check("external-link-target", "warning", "prose")
def check_external_link_target(
    line: str,
    line_num: int,
    state: ParseState,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check external links for window=_blank."""
    m = re.search(r"link:(https?://[^\[]+)\[([^\]]*)\]", line)
    if m:
        link_content = m.group(2)
        if "window=_blank" not in link_content:
            file_result.add_finding(
                cfg,
                "external-link-target",
                line_num,
                f"line {line_num}: External link missing window=_blank",
            )


@register_check("image-alt-text", "warning", "prose")
def check_image_alt_text(
    line: str,
    line_num: int,
    state: ParseState,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check for images without alt text."""
    m = re.search(r"image::([^\[]+)\[\]", line)
    if m:
        file_result.add_finding(
            cfg,
            "image-alt-text",
            line_num,
            f"line {line_num}: Image has no alt text: {m.group(0)}",
        )


@register_check("product-names", "warning", "prose")
def check_product_names(
    line: str,
    line_num: int,
    state: ParseState,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check product name capitalization."""
    for wrong, correct in cfg.product_names.items():
        if wrong in line:
            file_result.add_finding(
                cfg,
                "product-names",
                line_num,
                f"line {line_num}: '{wrong}' should be '{correct}'",
            )


@register_check("banned-terms", "warning", "prose")
def check_banned_terms(
    line: str,
    line_num: int,
    state: ParseState,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check banned terminology."""
    for banned, replacement in cfg.banned_terms.items():
        # Use word boundaries to avoid false positives
        if re.search(
            rf"(?:^|[^a-zA-Z0-9]){re.escape(banned)}(?:[^a-zA-Z0-9]|$)", line
        ):
            file_result.add_finding(
                cfg,
                "banned-terms",
                line_num,
                f"line {line_num}: Banned term '{banned}' (use '{replacement}')",
            )


@register_check("admonition-capitalization", "warning", "prose")
def check_admonition_capitalization(
    line: str,
    line_num: int,
    state: ParseState,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check admonition keywords are followed by capitalized text."""
    m = re.match(rf"^({ADMONITIONS}):\s+([a-z])", line)
    if m:
        admonition = m.group(1)
        first_char = m.group(2)
        file_result.add_finding(
            cfg,
            "admonition-capitalization",
            line_num,
            f"line {line_num}: Admonition should be followed by capitalized word: {admonition}: {first_char}",
        )

