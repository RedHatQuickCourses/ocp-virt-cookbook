"""Check modules — import all to trigger ``@register_check`` registration.

To add a new check category, create a new module in this package and
import it here.
"""

from . import code_blocks  # noqa: F401
from . import prose  # noqa: F401
from . import structural  # noqa: F401
