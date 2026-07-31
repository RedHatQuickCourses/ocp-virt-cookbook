"""Configuration loading and management.

Merges defaults from the check registry with an optional ``.review-docs.conf``
file and CLI overrides (``--disable``, ``--only``).
"""

import configparser
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from .registry import CHECKS

# ── Defaults ──────────────────────────────────────────────────────────────────

# Product name patterns to check (case-sensitive)
DEFAULT_PRODUCT_NAMES: Dict[str, str] = {
    "Openshift": "OpenShift",
    "openshift": "OpenShift",
}

# Banned terminology patterns
DEFAULT_BANNED_TERMS: Dict[str, str] = {
    "k8s": "Kubernetes",
}


# ── Config dataclass ──────────────────────────────────────────────────────────


@dataclass
class Config:
    """Merged configuration from config file + CLI overrides."""

    # Maps check name -> effective severity ("error", "warning", or "disable")
    check_severities: Dict[str, str] = field(default_factory=dict)
    product_names: Dict[str, str] = field(default_factory=dict)
    banned_terms: Dict[str, str] = field(default_factory=dict)

    def is_enabled(self, check_name: str) -> bool:
        return self.check_severities.get(check_name) != "disable"

    def severity(self, check_name: str) -> str:
        sev = self.check_severities.get(check_name)
        if sev in ("error", "warning", "disable"):
            return sev
        # Fall back to the check's default
        check_def = CHECKS.get(check_name)
        return check_def.default_severity if check_def else "warning"


# ── Loader ────────────────────────────────────────────────────────────────────


def load_config(
    config_path: Optional[str],
    no_config: bool,
    disable: Optional[str],
    only: Optional[str],
) -> Config:
    """Load config from file, then apply CLI overrides.

    Parameters
    ----------
    config_path:
        Explicit path to a config file, or ``None`` to use the default
        (``.review-docs.conf`` in the repo root).
    no_config:
        If ``True``, skip loading the config file entirely.
    disable:
        Comma-separated list of check names to disable.
    only:
        Comma-separated list of check names to run exclusively.
    """
    cfg = Config(
        product_names=dict(DEFAULT_PRODUCT_NAMES),
        banned_terms=dict(DEFAULT_BANNED_TERMS),
    )

    # Set defaults from check registry
    for name, check_def in CHECKS.items():
        cfg.check_severities[name] = check_def.default_severity

    # Load config file if present and not suppressed
    if not no_config:
        if config_path is None:
            # Look for .review-docs.conf in repo root
            repo_root = Path(__file__).resolve().parent.parent.parent
            config_path = str(repo_root / ".review-docs.conf")

        if os.path.isfile(config_path):
            parser = configparser.ConfigParser()
            # Preserve key case for [product-names] and [banned-terms];
            # [checks] keys are lowercased explicitly below.
            parser.optionxform = str  # type: ignore[assignment]
            parser.read(config_path)

            if parser.has_section("checks"):
                for name, value in parser.items("checks"):
                    name = name.strip().lower()
                    value = value.strip().lower()
                    if value == "disabled":
                        value = "disable"
                    if value in ("error", "warning", "disable"):
                        cfg.check_severities[name] = value

            if parser.has_section("product-names"):
                items = dict(parser.items("product-names"))
                if items:
                    # Replace defaults only if section has actual entries
                    cfg.product_names = items

            if parser.has_section("banned-terms"):
                items = dict(parser.items("banned-terms"))
                if items:
                    cfg.banned_terms = items

    # CLI overrides: --disable
    if disable:
        for name in disable.split(","):
            name = name.strip()
            if name in cfg.check_severities:
                cfg.check_severities[name] = "disable"

    # CLI overrides: --only (disable everything except listed)
    if only:
        only_set = {n.strip() for n in only.split(",")}
        for name in cfg.check_severities:
            if name not in only_set:
                cfg.check_severities[name] = "disable"

    return cfg
