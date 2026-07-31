"""Data model classes for the documentation review tool."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from .config import Config


# ── Parse state ───────────────────────────────────────────────────────────────


@dataclass
class ParseState:
    """Line-by-line parser state maintained by the engine.

    This replaces the untyped ``state: dict`` that was shared between
    the engine and check functions.  Checks read/write named attributes
    instead of opaque string keys.  Per-check private state is available
    via :meth:`check_state`.
    """

    # ── Previous line (set by engine at end of each iteration) ────────
    prev_line: str = ""

    # ── Code-block metadata (managed by engine) ────────────────────────
    # Code blocks are also tracked on ``block_stack`` as ``"code_block"``.
    # These attributes carry code-block-specific metadata.
    code_block_lang: str = ""
    code_block_start_line: int = 0
    boundary_direction: str = ""  # "open" or "close", set at ---- boundary

    # ── Heading tracking (managed by heading-hierarchy check) ─────────
    heading_levels: List[int] = field(default_factory=list)
    first_heading_found: bool = False
    h1_count: int = 0

    # ── List context (managed by list-blank-line check) ──────────────
    in_list: bool = False

    # ── Block context (managed by engine) ────────────────────────────
    # Stack of currently-open block types.  The engine pushes/pops as
    # block delimiters are encountered — including ``----`` code blocks
    # (as ``"code_block"``), ``|===``, ``====``, ``****``, ``++++``,
    # ``--``, and ``....``.  Checks can query membership, e.g.
    # ``state.in_block("table")`` or ``state.in_block("code_block")``.
    block_stack: List[str] = field(default_factory=list)

    @property
    def in_code_block(self) -> bool:
        """Whether we are currently inside a ``----`` code block.

        Convenience property — equivalent to ``self.in_block("code_block")``.
        """
        return self.in_block("code_block")

    # ── Per-check private state ──────────────────────────────────────
    _check_state: Dict[str, Dict[str, Any]] = field(
        default_factory=dict, repr=False
    )

    def check_state(self, check_name: str) -> Dict[str, Any]:
        """Return a private state dict for the named check.

        Created lazily on first access.
        """
        if check_name not in self._check_state:
            self._check_state[check_name] = {}
        return self._check_state[check_name]

    def in_block(self, block_type: str) -> bool:
        """Return ``True`` if currently inside a block of the given type."""
        return block_type in self.block_stack


# ── Findings and results ──────────────────────────────────────────────────────


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
