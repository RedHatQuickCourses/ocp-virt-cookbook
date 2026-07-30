#!/usr/bin/env python3
"""Thin entry point — delegates to the review_docs package.

This file exists so that ``python scripts/review-docs.py`` and
``bash scripts/review-docs.sh`` continue to work as before.

The actual implementation lives in ``scripts/review_docs/``.
"""

import sys
from pathlib import Path

# Ensure the scripts/ directory is on sys.path so that ``import review_docs``
# resolves to the local package rather than requiring an install step.
_scripts_dir = str(Path(__file__).resolve().parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from review_docs.__main__ import main  # noqa: E402

if __name__ == "__main__":
    main()
