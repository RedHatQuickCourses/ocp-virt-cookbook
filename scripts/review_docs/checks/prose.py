"""Prose checks — run on every non-comment, non-code-block line."""

import re

from ..config import Config
from ..models import FileResult, ParseState
from ..registry import register_check

# Admonition keywords (used by the admonition-capitalization check)
ADMONITIONS = r"NOTE|WARNING|TIP|IMPORTANT|CAUTION"


def _extract_prose_text(line: str) -> str:
    """Remove non-prose constructs from line, leaving only user-facing text.

    Strips URLs, xref/image/include paths, attribute definitions/references,
    source block specifiers, and inline code so checks like product-names
    and banned-terms only examine prose intended for readers.
    """
    # Skip attribute definition lines entirely (e.g., :navtitle: ...)
    if re.match(r"^:[a-zA-Z][^:]*:", line):
        return ""

    # Skip source block attribute lines (e.g., [source,yaml])
    if re.match(r"^\[source", line):
        return ""

    text = line

    # Remove inline code (backticks)
    text = re.sub(r"`[^`]+`", "", text)

    # Remove URLs (standalone or in link macros)
    text = re.sub(r"https?://[^\s\[\]]+", "", text)

    # Remove xref targets (keep display text in brackets)
    text = re.sub(r"xref:[^\[]+", "", text)

    # Remove image paths (keep alt text in brackets)
    text = re.sub(r"image::[^\[]+", "", text)

    # Remove include directives entirely (no user-facing text)
    text = re.sub(r"include::[^\[]+\[[^\]]*\]", "", text)

    # Remove attribute references
    text = re.sub(r"\{[^}]+\}", "", text)

    return text


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
    """Check product name capitalization in user-facing text."""
    # Skip inside literal or passthrough blocks (code-like content)
    if state.in_block("literal") or state.in_block("passthrough"):
        return

    prose_text = _extract_prose_text(line)
    for wrong, correct in cfg.product_names.items():
        if wrong in prose_text:
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
    """Check banned terminology in user-facing text."""
    # Skip inside literal or passthrough blocks (code-like content)
    if state.in_block("literal") or state.in_block("passthrough"):
        return

    prose_text = _extract_prose_text(line)
    for banned, replacement in cfg.banned_terms.items():
        # Use word boundaries to avoid false positives
        if re.search(
            rf"(?:^|[^a-zA-Z0-9]){re.escape(banned)}(?:[^a-zA-Z0-9]|$)", prose_text
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


@register_check("list-blank-line", "warning", "prose")
def check_list_blank_line(
    line: str,
    line_num: int,
    state: ParseState,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check that lists are preceded by a blank line.

    In AsciiDoc, a list immediately following a non-blank line (such as a
    paragraph) is not rendered as a list.  A blank line is required before
    the first list item.

    Uses ``state.in_list`` to track whether we are currently inside a
    list context (i.e. the list has already started).  Multi-line list item
    paragraphs (no ``+`` needed) followed by another list marker are valid
    AsciiDoc and should not be flagged.
    """
    # Matches the start of any AsciiDoc list item.  Derived from the
    # ``UnorderedListRx`` and ``OrderedListRx`` patterns in Asciidoctor's
    # ``rx.rb``.  Description lists (``term::``) and callout lists
    # (``<1>``) are handled separately.
    #
    # Unordered : ``-``, ``*`` through ``*****``, ``•`` (U+2022)
    # Ordered   : ``.`` through ``......`` (dot-style)
    #             ``1.`` (arabic), ``a.``/``A.`` (alpha)
    #             ``i)``/``iv)`` (lowerroman), ``I)``/``IV)`` (upperroman)
    _LIST_ITEM_RE = r"^\s*(-|\*{1,5}|\u2022|\.{1,6}|\d+\.|[a-zA-Z]\.|[IVXivx]+\))\s+"

    is_list_item = bool(re.match(_LIST_ITEM_RE, line))

    # Track list context: we leave it on a blank line.
    if not line.strip():
        state.in_list = False
        return

    # A list continuation marker (+) means we're in a list.
    if line.strip() == "+":
        state.in_list = True
        return

    if is_list_item:
        # If we're already in a list, this is a continuation — always OK.
        if state.in_list:
            return
    else:
        # Non-list, non-blank line: leave context unchanged (multi-line
        # paragraph continuation within a list item is fine).
        return

    # --- We have a list item and we are NOT already in a list context ---
    prev_line = state.prev_line

    # Previous line is blank -> OK (already handled above, but defensive)
    if not prev_line.strip():
        state.in_list = True
        return

    # Previous line is itself a list item -> OK (start of list context)
    if re.match(_LIST_ITEM_RE, prev_line):
        state.in_list = True
        return

    # Previous line is a list continuation marker -> OK
    if prev_line.strip() == "+":
        state.in_list = True
        return

    # Previous line is a description list term (ends with ::) -> OK
    if prev_line.rstrip().endswith("::"):
        state.in_list = True
        return

    # Previous line is a heading -> OK (lists can follow headings)
    if re.match(r"^=+\s+", prev_line):
        state.in_list = True
        return

    # Previous line is a block delimiter -> OK (lists inside admonition/sidebar/etc.)
    # The engine consumes delimiter lines before prose checks run, but
    # ``prev_line`` is still set to the delimiter text.
    if re.match(r"^(====|----|\.\.\.\.|(\*{4}|\+{4}|_{4})|--|\|===)\s*$", prev_line):
        state.in_list = True
        return

    # Previous line is an attribute/anchor/block-title -> OK
    if re.match(r"^(\[|:|\.|//)", prev_line):
        state.in_list = True
        return

    file_result.add_finding(
        cfg,
        "list-blank-line",
        line_num,
        f"line {line_num}: List not preceded by blank line (will not render as a list in AsciiDoc)",
    )
    # Even though we flagged it, the list has started from this point.
    state.in_list = True

