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
from .models import FileResult, Finding
from .registry import CHECKS

# Ensure all checks are registered before the engine runs.
from . import checks as _checks  # noqa: F401


# ── Build-check result ────────────────────────────────────────────────────────


@dataclass
class BuildResult:
    """Result of running the Antora build check."""

    errors: int = 0
    findings: List[Finding] = field(default_factory=list)


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
    state: dict = {
        "in_code_block": False,
        "code_block_lang": "",
        "code_block_start_line": 0,
        "prev_line": "",
        "heading_levels": [],
        "first_heading_found": False,
        "h1_count": 0,
    }

    for line_num, line in enumerate(lines, 1):
        # Skip comment lines for prose checks
        if re.match(r"^//", line):
            state["prev_line"] = line
            continue

        # Track code block boundaries
        if re.match(r"^----", line):
            if not state["in_code_block"]:
                state["in_code_block"] = True
                state["code_block_start_line"] = line_num
                state["boundary_direction"] = "open"

                prev = state["prev_line"]
                # Detect language specifier in previous line
                m = re.match(
                    r"^\[source,?([a-zA-Z0-9_-]*)\]", prev
                ) or re.match(r"^\[source,?([a-zA-Z0-9_-]*),.*\]", prev)
                state["code_block_lang"] = m.group(1) if m else ""
            else:
                state["in_code_block"] = False
                state["code_block_lang"] = ""
                state["boundary_direction"] = "close"

            # Run boundary checks
            for check_def in boundary_checks:
                check_def.func(line, line_num, state, cfg, file_result)

            state["prev_line"] = line
            continue

        # Inside code block: run code block content checks
        if state["in_code_block"]:
            for check_def in code_block_checks:
                check_def.func(line, line_num, state, cfg, file_result)

            state["prev_line"] = line
            continue

        # Outside code block: run prose checks
        for check_def in prose_checks:
            check_def.func(line, line_num, state, cfg, file_result)

        state["prev_line"] = line

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
