"""CLI entry point — enables ``python -m review_docs`` invocation.

Also used by the thin ``scripts/review-docs.py`` wrapper.
"""

import argparse
import sys
from typing import List

from .config import Config, load_config
from .engine import find_all_adoc_files, review_file, run_build_check
from .formatters import JsonFormatter, TextFormatter
from .models import ReviewResult
from .registry import CHECKS


def list_checks() -> None:
    """Print all available checks."""
    print(f"{'Check Name':<30} {'Default Severity':<18} {'Scope':<15}")
    print("-" * 63)
    for name, check_def in sorted(CHECKS.items()):
        print(f"{name:<30} {check_def.default_severity:<18} {check_def.scope:<15}")


def parse_args() -> tuple[argparse.ArgumentParser, argparse.Namespace]:
    parser = argparse.ArgumentParser(
        description="Documentation Review Script for ocp-virt-cookbook.",
        epilog="Exit code: 0 if no errors, 1 if any ERROR-level issues found. "
        "Warnings alone do NOT cause non-zero exit.",
    )
    parser.add_argument(
        "files", nargs="*", help="AsciiDoc files to review"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Review all .adoc files under modules/",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Run Antora build check (validates xrefs)",
    )
    parser.add_argument(
        "--disable",
        metavar="CHECK,...",
        help="Disable specific checks by name (comma-separated)",
    )
    parser.add_argument(
        "--only",
        metavar="CHECK,...",
        help="Run only these checks (comma-separated)",
    )
    parser.add_argument(
        "--config",
        metavar="FILE",
        help="Config file path (default: .review-docs.conf in repo root)",
    )
    parser.add_argument(
        "--no-config",
        action="store_true",
        help="Ignore config file even if present",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--list-checks",
        action="store_true",
        help="List all available checks and exit",
    )

    color_group = parser.add_mutually_exclusive_group()
    color_group.add_argument(
        "--color", action="store_true", default=None, help="Force color output"
    )
    color_group.add_argument(
        "--no-color", action="store_true", help="Disable color output"
    )

    return parser, parser.parse_args()


def main() -> None:
    parser, args = parse_args()

    # --list-checks: print and exit
    if args.list_checks:
        list_checks()
        sys.exit(0)

    # Determine color
    if args.color:
        use_color = True
    elif args.no_color:
        use_color = False
    else:
        use_color = sys.stdout.isatty()

    # Create formatter
    if args.format == "json":
        formatter = JsonFormatter()
    else:
        formatter = TextFormatter(use_color)

    # Load config
    cfg = load_config(args.config, args.no_config, args.disable, args.only)

    # Collect files
    files: List[str] = []
    if args.all:
        files = find_all_adoc_files()
    files.extend(args.files or [])

    if not files:
        parser.print_help()
        sys.exit(0)

    # Review each file
    result = ReviewResult()
    build_errors = 0

    for filepath in files:
        file_result = review_file(filepath, cfg)

        # Count errors and warnings
        for finding in file_result.findings:
            if finding.severity == "error":
                result.total_errors += 1
            else:
                result.total_warnings += 1

        result.files.append(file_result)
        formatter.print_file_result(file_result)

    # Run build check if requested
    if args.build:
        formatter.print_build_status("Running Antora build check...")
        build_result = run_build_check()
        build_errors = build_result.errors
        formatter.print_build_result(build_result.findings)

    # Print summary
    formatter.print_summary(result)

    if result.total_errors > 0 or build_errors > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
