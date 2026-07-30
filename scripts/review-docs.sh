#!/bin/bash
set -euo pipefail
# Thin wrapper — delegates to the Python implementation.
# Preserves backward compatibility with Makefile targets and CI workflows.
exec python3 "$(dirname "$0")/review-docs.py" "$@"
