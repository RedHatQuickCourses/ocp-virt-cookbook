"""Data model classes for the documentation review tool."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, List, Optional

if TYPE_CHECKING:
    from .config import Config


@dataclass
class Finding:
    """A single issue found during review."""

    file: str
    line: Optional[int]
    check: str
    severity: str  # "error" or "warning"
    message: str


@dataclass
class FileResult:
    """Results from reviewing a single file."""

    file: str
    findings: List[Finding] = field(default_factory=list)
    word_count: int = 0
    read_time_min: int = 0

    def add_finding(
        self, cfg: Config, check_name: str, line: int | None, message: str
    ) -> None:
        """Add a finding with the effective severity from config."""
        severity = cfg.severity(check_name)
        self.findings.append(
            Finding(
                file=self.file,
                line=line,
                check=check_name,
                severity=severity,
                message=message,
            )
        )


@dataclass
class ReviewResult:
    """Aggregate results from reviewing all files."""

    files: List[FileResult] = field(default_factory=list)
    total_errors: int = 0
    total_warnings: int = 0


@dataclass
class CheckDef:
    """Definition of a single check."""

    name: str
    default_severity: str  # "error" or "warning"
    scope: str  # "prose", "code_block_content", "code_block_boundary", or "structural"
    func: Callable
