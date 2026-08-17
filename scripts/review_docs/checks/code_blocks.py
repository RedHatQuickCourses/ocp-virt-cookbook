"""Code-block checks — run on lines inside ``----`` delimited code blocks."""

import re

from ..config import Config
from ..models import FileResult, ParseState
from ..registry import register_check

# Language → line-comment prefix mapping for callout validation
# None means the language has no comment syntax
COMMENT_PREFIXES: dict[str, str | None] = {
    # C-style languages
    "c": "//", "cpp": "//", "java": "//", "javascript": "//", "js": "//",
    "typescript": "//", "ts": "//", "go": "//", "rust": "//", "swift": "//",
    "kotlin": "//", "scala": "//", "php": "//", "csharp": "//", "cs": "//",
    "groovy": "//",
    # Hash-comment languages
    "ruby": "#", "python": "#", "perl": "#", "yaml": "#", "yml": "#",
    "bash": "#", "sh": "#", "shell": "#", "zsh": "#", "makefile": "#",
    "dockerfile": "#", "r": "#", "powershell": "#", "toml": "#",
    "properties": "#", "ini": "#", "conf": "#", "awk": "#",
    # Double-semicolon languages
    "clojure": ";;", "lisp": ";;", "scheme": ";;", "elisp": ";;",
    # XML-style (special handling)
    "xml": "<!--", "html": "<!--", "sgml": "<!--", "svg": "<!--", "xhtml": "<!--",
    # Double-dash languages
    "sql": "--", "lua": "--", "haskell": "--", "ada": "--",
    # No comment support
    "json": None,
}

# A single callout token, either bare ("<1>", "<.>") or XML-commented
# ("<!--1-->", "<!--.-->").
_CALLOUT_TOKEN = r"(?:<!--(?:\d+|\.)-->|<(?:\d+|\.)>)"

# One or more callout tokens separated only by whitespace, anchored to end of
# line. A line may carry more than one callout (e.g. "code # <1> <2>"); this
# confirms a genuine trailing callout group exists and captures its start.
_CALLOUT_TAIL_RE = re.compile(rf"({_CALLOUT_TOKEN}(?:\s*{_CALLOUT_TOKEN})*)\s*$")

# Non-anchored patterns used to pull individual markers out of a substring
# once a trailing callout group has been confirmed.
_BARE_TOKEN_RE = re.compile(r"<(\d+|\.)>")
_XML_TOKEN_RE = re.compile(r"<!--(\d+|\.)-->")

# Pattern to match a callout annotation line: "<1> explanation", "<.> explanation"
_ANNOTATION_RE = re.compile(r"^<(\d+|\.)>\s")


@register_check("code-block-language", "warning", "code_block_boundary")
def check_code_block_language(
    line: str,
    line_num: int,
    state: ParseState,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check that a code block opening has a ``[source,language]`` specifier.

    Boundary checks are called when a ``----`` delimiter is encountered.
    ``state.boundary_direction`` is ``"open"`` or ``"close"``.
    ``state.prev_line`` contains the line immediately before the delimiter.
    """
    if state.boundary_direction != "open":
        return

    prev = state.prev_line
    if not re.match(r"^\[source(?:[,\s]|\])", prev):
        file_result.add_finding(
            cfg,
            "code-block-language",
            line_num,
            f"line {line_num}: Code block delimiter without [source,language] specifier",
        )


@register_check("yaml-null-timestamps", "warning", "code_block_line")
def check_yaml_null_timestamps(
    line: str,
    line_num: int,
    state: ParseState,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check for creationTimestamp: null in YAML blocks."""
    if state.code_block_lang == "yaml" and re.search(
        r"creationTimestamp:\s*null", line
    ):
        file_result.add_finding(
            cfg,
            "yaml-null-timestamps",
            line_num,
            f"line {line_num}: creationTimestamp: null found in YAML block",
        )


@register_check("yaml-flow-syntax", "warning", "code_block_line")
def check_yaml_flow_syntax(
    line: str,
    line_num: int,
    state: ParseState,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check for inline YAML flow syntax ({} or []) in YAML blocks."""
    if state.code_block_lang != "yaml":
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


def _report_bare_callouts(
    cfg: Config,
    file_result: FileResult,
    line_num: int,
    lang: str,
    markers: list[str],
    suggestion: str,
) -> None:
    """Report one finding covering every bare marker found in a callout tail."""
    if not markers:
        return
    plural = "s" if len(markers) > 1 else ""
    joined = ", ".join(markers)
    file_result.add_finding(
        cfg,
        "callout-format",
        line_num,
        f"line {line_num}: Bare callout{plural} {joined} in {lang} block; {suggestion}",
    )


@register_check("callout-format", "warning", "code_block_line")
def check_callout_format(
    line: str,
    line_num: int,
    state: ParseState,
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check that callouts in code blocks use language-appropriate comment syntax.

    A line may carry more than one callout (e.g. "code # <1> <2>"). Once a
    trailing callout group is confirmed with ``_CALLOUT_TAIL_RE``, the parse
    zone is widened back to "from the comment marker through end of line" so
    every marker is validated, not just the last one.
    """
    lang = state.code_block_lang
    if not lang or lang not in COMMENT_PREFIXES:
        return  # Unknown language, skip

    tail_match = _CALLOUT_TAIL_RE.search(line)
    if not tail_match:
        return  # No callout on this line

    prefix = COMMENT_PREFIXES[lang]
    group_start = tail_match.start(1)

    # Locate the comment marker that should precede the callout group (if
    # any) and widen the tail back to that point, so markers separated by
    # other text are still caught.
    if prefix is not None:
        prefix_pos = line.rfind(prefix, 0, group_start + 1)
        anchor = prefix_pos if prefix_pos != -1 else group_start
    else:
        anchor = group_start
    tail = line[anchor:]

    # Handle languages with no comment support: every callout is bare.
    if prefix is None:
        markers = [f"<{m}>" for m in _BARE_TOKEN_RE.findall(tail)]
        _report_bare_callouts(
            cfg,
            file_result,
            line_num,
            lang,
            markers,
            f"{lang} has no comment syntax so callouts cannot be hidden",
        )
        return

    # XML-style: expect <!--N--> format. Bare-token matching safely skips
    # markers already wrapped in "<!--...-->" since the digits there aren't
    # immediately preceded by "<".
    if prefix == "<!--":
        bare = [f"<{m}>" for m in _BARE_TOKEN_RE.findall(tail)]
        _report_bare_callouts(cfg, file_result, line_num, lang, bare, "use '<!--N-->' format")
        return

    # Standard comment prefixes (#, //, --, ;;, ...): if the prefix actually
    # precedes the callout group, every marker in the tail is considered
    # hidden by that single comment. Otherwise, every marker is bare.
    has_prefix = anchor != group_start
    if has_prefix:
        return  # Properly formatted

    bare = [f"<{m}>" for m in _BARE_TOKEN_RE.findall(tail)]
    _report_bare_callouts(
        cfg,
        file_result,
        line_num,
        lang,
        bare,
        f"use '{prefix} <N>' for valid syntax",
    )


@register_check("yaml-validation", "error", "code_block_complete")
def check_yaml_validation(
    block_content: list[str],
    block_lang: str,
    block_start_line: int,
    block_end_line: int,
    following_annotations: list[str],
    block_attrs: dict[str, str],
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Validate YAML syntax in code blocks (requires PyYAML)."""
    if block_lang != "yaml":
        return

    try:
        import yaml
    except ImportError:
        return

    yaml_content = "\n".join(block_content)
    if not yaml_content.strip():
        return

    try:
        yaml.safe_load(yaml_content)
    except Exception:
        file_result.add_finding(
            cfg,
            "yaml-validation",
            block_start_line,
            f"line {block_start_line}: Invalid YAML syntax in code block",
        )


@register_check("callout-count", "warning", "code_block_complete")
def check_callout_count(
    block_content: list[str],
    block_lang: str,
    block_start_line: int,
    block_end_line: int,
    following_annotations: list[str],
    block_attrs: dict[str, str],
    cfg: Config,
    file_result: FileResult,
) -> None:
    """Check that callout markers in code blocks match annotations that follow.

    Both auto-numbered (``<.>``) and manual-numbered callouts are accepted
    as a matter of author preference. Mixing the two styles in the same
    block is always invalid. Manual numbering with repeated markers
    requires the ``allow-duplicate-callouts`` attribute — bare or
    ``=true`` — in its attribute list, e.g.
    ``[source,yaml,allow-duplicate-callouts]``, to make that intent
    explicit.
    """

    def report(msg: str) -> None:
        file_result.add_finding(cfg, "callout-count", block_start_line, msg)

    # Count callouts in block content
    callout_numbers: set[int] = set()
    auto_callout_count = 0
    manual_callout_count = 0

    for line in block_content:
        # Non-anchored: a line may carry more than one callout marker
        # (e.g. "code # <1> <2>"), so every marker must be counted, not just
        # a single trailing one.
        matches = _BARE_TOKEN_RE.findall(line)
        for m in matches:
            if m == ".":
                auto_callout_count += 1
            else:
                callout_numbers.add(int(m))
                manual_callout_count += 1

    has_auto = auto_callout_count > 0
    has_manual = len(callout_numbers) > 0

    if not has_auto and not has_manual:
        return  # No callouts in this block

    # Count annotations
    annotation_numbers: set[int] = set()
    auto_annotation_count = 0

    for line in following_annotations:
        m = _ANNOTATION_RE.match(line)
        if m:
            val = m.group(1)
            if val == ".":
                auto_annotation_count += 1
            else:
                annotation_numbers.add(int(val))

    raw_attr = block_attrs.get("allow-duplicate-callouts")
    allow_duplicates = raw_attr is not None and raw_attr.lower() in ("", "true")

    if has_auto and has_manual:
        # Mixed auto and manual — always invalid, regardless of the attribute.
        report(
            f"line {block_start_line}: Code block mixes auto-numbered (<.>) "
            f"and manual-numbered callouts; use one style consistently",
        )
        return

    if has_auto:
        # Auto-numbered block: an allow-duplicate-callouts attribute is moot
        # since auto-numbering never repeats markers.
        if allow_duplicates:
            report(
                f"line {block_start_line}: Code block declares allow-duplicate-callouts "
                f"but uses auto-numbered (<.>) callouts; remove the attribute "
                f"or switch to manual numbering",
            )
            return

        # Auto-numbered: exact count match required.
        if auto_callout_count != auto_annotation_count:
            report(
                f"line {block_start_line}: Code block has {auto_callout_count} "
                f"auto-numbered callout(s) but {auto_annotation_count} annotation(s) follow",
            )
        return

    # Manual-numbered: respected as author preference, no suggestion to
    # switch to auto-numbering. Repeated markers require an explicit
    # allow-duplicate-callouts opt-in.
    has_duplicates = manual_callout_count > len(callout_numbers)

    if has_duplicates and not allow_duplicates:
        example = (
            f"[source,{block_lang},allow-duplicate-callouts]"
            if block_lang
            else "[source,<language>,allow-duplicate-callouts]"
        )
        report(
            f"line {block_start_line}: Code block has duplicate callout markers "
            f"without the allow-duplicate-callouts block attribute; add "
            f"allow-duplicate-callouts (e.g. {example}) to opt into repeated "
            f"markers",
        )
        return

    if allow_duplicates and not has_duplicates:
        report(
            f"line {block_start_line}: Code block declares allow-duplicate-callouts "
            f"but has no duplicate callout markers; remove the attribute",
        )
        return

    # Manual-numbered: check annotation set coverage.
    missing = callout_numbers - annotation_numbers
    if missing:
        nums = ", ".join(f"<{n}>" for n in sorted(missing))
        report(
            f"line {block_start_line}: Callout(s) {nums} in code block "
            f"have no matching annotation(s)",
        )

    unused = annotation_numbers - callout_numbers
    if unused:
        nums = ", ".join(f"<{n}>" for n in sorted(unused))
        report(
            f"line {block_start_line}: Annotation(s) {nums} not referenced "
            f"in code block",
        )
