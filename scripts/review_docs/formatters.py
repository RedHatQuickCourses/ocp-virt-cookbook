"""Output formatters for the documentation review tool.

Three classes are provided:

* ``Formatter`` — abstract base defining the formatter interface.
* ``TextFormatter`` — coloured, human-readable output matching the
  original Bash script.
* ``JsonFormatter`` — machine-readable JSON (intended for CI
  annotations and downstream processing).
"""

import abc
import json
from typing import List

from .models import FileResult, Finding, ReviewResult

# ── ANSI colours ──────────────────────────────────────────────────────────────

COLOR_RED = "\033[0;31m"
COLOR_YELLOW = "\033[0;33m"
COLOR_BLUE = "\033[0;34m"
COLOR_GREEN = "\033[0;32m"
COLOR_RESET = "\033[0m"


# ── Base formatter ────────────────────────────────────────────────────────────


class Formatter(abc.ABC):
    """Abstract base class defining the formatter interface.

    Subclasses must implement two methods:

    * ``print_file_result`` — render one completed file review.
    * ``print_summary`` — render the aggregate summary (and, for
      batch formatters like JSON, flush accumulated output).

    The optional ``print_build_result`` hook renders build-check
    findings; the default delegates to ``print_file_result`` via a
    synthetic :class:`FileResult`.
    """

    @abc.abstractmethod
    def print_file_result(self, file_result: FileResult) -> None:
        """Render a single file's review results."""
        ...

    @abc.abstractmethod
    def print_summary(self, result: ReviewResult) -> None:
        """Render the final aggregate summary."""
        ...

    def print_build_status(self, message: str) -> None:
        """Print a status message before the build check starts.

        Default is a no-op (e.g. JSON formatters don't need progress
        messages).
        """

    def print_build_result(self, findings: List[Finding]) -> None:
        """Render build-check findings.

        Default implementation wraps the findings in a synthetic
        ``FileResult`` and delegates to ``print_file_result``.
        """
        if findings:
            fr = FileResult(file="(build)")
            fr.findings = list(findings)
            self.print_file_result(fr)


# ── Text formatter ────────────────────────────────────────────────────────────


class TextFormatter(Formatter):
    """Produces human-readable output matching the original Bash script."""

    def __init__(self, use_color: bool):
        self.use_color = use_color

    # -- helpers (private) --------------------------------------------------

    def _print_header(self, filepath: str) -> None:
        if self.use_color:
            print(f"{COLOR_GREEN}Reviewing: {COLOR_RESET}{filepath}")
        else:
            print(f"Reviewing: {filepath}")

    def _print_finding(self, finding: Finding) -> None:
        if finding.severity == "error":
            if self.use_color:
                print(f"{COLOR_RED}  ERROR  {COLOR_RESET}{finding.message}")
            else:
                print(f"  ERROR  {finding.message}")
        else:
            if self.use_color:
                print(f"{COLOR_YELLOW}  WARN   {COLOR_RESET}{finding.message}")
            else:
                print(f"  WARN   {finding.message}")

    def _print_info(self, message: str) -> None:
        if self.use_color:
            print(f"{COLOR_BLUE}  INFO   {COLOR_RESET}{message}")
        else:
            print(f"  INFO   {message}")

    # -- public interface ---------------------------------------------------

    def print_file_result(self, file_result: FileResult) -> None:
        self._print_header(file_result.file)
        for finding in file_result.findings:
            self._print_finding(finding)
        if file_result.word_count or file_result.read_time_min:
            self._print_info(
                f"Word count: {file_result.word_count} | "
                f"Estimated read time: {file_result.read_time_min} min"
            )
        # Blank line after each file (matching Bash behavior)
        print("")

    def print_build_status(self, message: str) -> None:
        self._print_info(message)

    def print_build_result(self, findings: List[Finding]) -> None:
        for finding in findings:
            self._print_finding(finding)

    def print_summary(self, result: ReviewResult) -> None:
        total_files = len(result.files)
        print(
            "\u2550" * 64
        )  # ════════════════════════════════════════════════════════════════
        print(
            f"Summary: {total_files} file(s) reviewed | "
            f"{result.total_errors} error(s) | {result.total_warnings} warning(s)"
        )
        print("\u2550" * 64)


# ── JSON formatter ────────────────────────────────────────────────────────────


class JsonFormatter(Formatter):
    """Produces machine-readable JSON output."""

    def __init__(self):
        self._file_results: List[dict] = []

    def print_file_result(self, file_result: FileResult) -> None:
        self._file_results.append(
            {
                "file": file_result.file,
                "word_count": file_result.word_count,
                "read_time_min": file_result.read_time_min,
                "findings": [
                    {
                        "file": f.file,
                        "line": f.line,
                        "check": f.check,
                        "severity": f.severity,
                        "message": f.message,
                    }
                    for f in file_result.findings
                ],
            }
        )

    def print_summary(self, result: ReviewResult) -> None:
        output = {
            "files": self._file_results,
            "summary": {
                "total_files": len(result.files),
                "total_errors": result.total_errors,
                "total_warnings": result.total_warnings,
            },
        }
        print(json.dumps(output, indent=2))
