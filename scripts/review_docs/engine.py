"""Review engine — orchestrates file scanning and check execution.

This module is *pure data*: it returns :class:`FileResult` /
:class:`BuildResult` objects without producing any output.  All
formatting is handled by the caller (typically ``__main__.main``).
"""

import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from .config import Config
from .models import FileResult, Finding, ParseState
from .registry import CHECKS

# Ensure all checks are registered before the engine runs.
from . import checks as _checks  # noqa: F401


# ── Build-check result ────────────────────────────────────────────────────────


@dataclass
class BuildResult:
    """Result of running the Antora build check."""

    errors: int = 0
    findings: List[Finding] = field(default_factory=list)


# ── Block delimiter mapping ──────────────────────────────────────────────────

# Maps AsciiDoc block delimiter patterns to semantic block type names.
# The engine pushes/pops these on ``ParseState.block_stack`` as delimiters
# are encountered.  Code blocks (``----`` / ``"code_block"``) are also
# tracked on block_stack but handled in a dedicated branch because they
# carry extra metadata (language, boundary direction) and dispatch to
# their own check scopes (code_block_content, code_block_boundary).
# Note: ``--`` is a legitimate 2-character AsciiDoc open block delimiter.
# False positives are unlikely because:
#   1. Code blocks (``----``, 4+ dashes) are caught by a dedicated branch
#      *before* ``_check_block_boundary`` is called.
#   2. The match is exact (``stripped == delimiter``), so em-dash
#      replacements or ``---`` / ``----`` lines don't trigger it.
#   3. A bare ``--`` line outside of intentional block markup is
#      extremely rare in practice.
_BLOCK_DELIMITERS = {
    "|===": "table",
    "====": "admonition",
    "****": "sidebar",
    "++++": "passthrough",
    "....": "literal",
    "--": "open",
}



# ── Internal helpers ──────────────────────────────────────────────────────────


def _get_enabled_checks(cfg: Config, scope: str):
    """Get enabled checks for a given scope."""
    return [
        check_def
        for check_def in CHECKS.values()
        if check_def.scope == scope and cfg.is_enabled(check_def.name)
    ]


def _compute_word_count(lines: List[str]) -> int:
    """Compute word count excluding code blocks and comments."""
    word_count = 0
    in_block = False

    for line in lines:
        if re.match(r"^----", line):
            in_block = not in_block
            continue
        if not in_block and not re.match(r"^//", line):
            word_count += len(line.split())

    return word_count


def _check_block_boundary(line: str, state: ParseState) -> bool:
    """Check if *line* is a non-code-block delimiter and update *state*.

    Returns ``True`` if the line was consumed as a block delimiter
    (callers should skip further processing).

    AsciiDoc block delimiters are toggle-style: the same delimiter string
    opens and closes a block.  When the top of the stack matches, we pop
    (close).  When it doesn't, we scan deeper — if the block type exists
    anywhere on the stack we treat the line as a close for a mismatched
    nesting (popping back to and including that entry), otherwise we push
    (open).
    """
    stripped = line.rstrip()
    for delimiter, block_type in _BLOCK_DELIMITERS.items():
        if stripped == delimiter:
            if state.block_stack and state.block_stack[-1] == block_type:
                # Clean close — top of stack matches.
                state.block_stack.pop()
            elif block_type in state.block_stack:
                # Mismatched nesting — pop back to the matching open.
                idx = len(state.block_stack) - 1 - state.block_stack[::-1].index(block_type)
                state.block_stack = state.block_stack[:idx]
            else:
                # New open.
                state.block_stack.append(block_type)
            return True
    return False



# ── Public API ────────────────────────────────────────────────────────────────


def review_file(filepath: str, cfg: Config) -> FileResult:
    """Review a single ``.adoc`` file.

    Returns a :class:`FileResult` containing all findings, word count,
    and estimated read time.  No output is produced.
    """
    file_result = FileResult(file=filepath)

    if not os.path.isfile(filepath):
        file_result.findings.append(
            Finding(
                file=filepath,
                line=None,
                check="file-not-found",
                severity="error",
                message=f"File not found: {filepath}",
            )
        )
        return file_result

    # Read file
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()

    # Get enabled checks by scope
    prose_checks = _get_enabled_checks(cfg, "prose")
    code_block_checks = _get_enabled_checks(cfg, "code_block_content")
    boundary_checks = _get_enabled_checks(cfg, "code_block_boundary")
    structural_checks = _get_enabled_checks(cfg, "structural")

    # Line-by-line state machine
    state = ParseState()

    for line_num, line in enumerate(lines, 1):
        # Skip comment lines for prose checks
        if re.match(r"^//", line):
            state.prev_line = line
            continue

        # Track code block boundaries
        if re.match(r"^----", line):
            if not state.in_code_block:
                state.block_stack.append("code_block")
                state.code_block_start_line = line_num
                state.boundary_direction = "open"

                prev = state.prev_line
                # Detect language specifier in previous line
                m = re.match(
                    r"^\[source,?([a-zA-Z0-9_-]*)\]", prev
                ) or re.match(r"^\[source,?([a-zA-Z0-9_-]*),.*\]", prev)
                state.code_block_lang = m.group(1) if m else ""
            else:
                state.block_stack.pop()
                state.code_block_lang = ""
                state.boundary_direction = "close"

            # Run boundary checks
            for check_def in boundary_checks:
                check_def.func(line, line_num, state, cfg, file_result)

            state.prev_line = line
            continue

        # Inside code block: run code block content checks
        if state.in_code_block:
            for check_def in code_block_checks:
                check_def.func(line, line_num, state, cfg, file_result)

            state.prev_line = line
            continue

        # Track non-code-block delimiters (tables, admonitions, etc.)
        if _check_block_boundary(line, state):
            state.prev_line = line
            continue

        # Outside code block: run prose checks
        for check_def in prose_checks:
            check_def.func(line, line_num, state, cfg, file_result)

        state.prev_line = line

    # Run structural checks
    for check_def in structural_checks:
        check_def.func(filepath, lines, cfg, file_result)

    # Word count and read time
    file_result.word_count = _compute_word_count(lines)
    read_time = file_result.word_count // 200
    if read_time == 0 and file_result.word_count > 0:
        read_time = 1
    file_result.read_time_min = read_time

    return file_result


def find_all_adoc_files() -> List[str]:
    """Find all .adoc files under modules/."""
    modules_dir = Path("modules")
    if not modules_dir.is_dir():
        return []
    return sorted(str(p) for p in modules_dir.rglob("*.adoc"))


def run_build_check() -> BuildResult:
    """Run Antora build check.

    Returns a :class:`BuildResult` with any findings.  No output is
    produced.
    """
    build = BuildResult()

    if subprocess.run(["which", "pnpm"], capture_output=True).returncode != 0:
        build.findings.append(
            Finding(
                file="",
                line=None,
                check="build",
                severity="warning",
                message="pnpm not found, skipping build check",
            )
        )
        return build

    result = subprocess.run(
        ["pnpm", "run", "build"], capture_output=True, text=True
    )
    output = result.stdout + result.stderr
    if re.search(r"error|warning.*xref", output, re.IGNORECASE):
        build.findings.append(
            Finding(
                file="",
                line=None,
                check="build",
                severity="error",
                message="Antora build produced errors or broken xrefs",
            )
        )
        build.errors = 1

    return build
