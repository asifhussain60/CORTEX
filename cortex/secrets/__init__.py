"""cortex.secrets — Secrets management public namespace.

Re-exports the full API from cortex.infrastructure.secrets.
"""
from cortex.infrastructure.secrets import *  # noqa: F401, F403
from cortex.infrastructure.secrets import __all__
