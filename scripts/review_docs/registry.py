"""Check registry — central catalog of all available checks.

Checks are registered at import time via the ``@register_check`` decorator.
The ``checks`` sub-package imports every check module so that registration
happens automatically when the package is first imported.
"""

from typing import Callable, Dict

from .models import CheckDef, validate_check_signature

# Global registry populated by @register_check decorators.
CHECKS: Dict[str, CheckDef] = {}


def register_check(name: str, severity: str, scope: str):
    """Decorator that registers a check function in the global CHECKS dict.

    The function's signature is validated against the expected parameters
    for the given *scope* at registration time.  A ``TypeError`` is raised
    immediately if the signature does not match.

    Parameters
    ----------
    name:
        Unique identifier for the check (e.g. ``"heading-hierarchy"``).
    severity:
        Default severity — ``"error"`` or ``"warning"``.
    scope:
        One of ``"prose"``, ``"code_block_line"``, ``"code_block_boundary"``,
        ``"code_block_complete"``, or ``"structural"``.
    """

    def decorator(func: Callable) -> Callable:
        validate_check_signature(func, scope, name)
        CHECKS[name] = CheckDef(
            name=name, default_severity=severity, scope=scope, func=func
        )
        return func

    return decorator
