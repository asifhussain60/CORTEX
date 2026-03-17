"""Compatibility module aliasing Azure secrets provider implementation."""

import sys
from cortex.infrastructure.secrets.providers import azure as _azure

sys.modules[__name__] = _azure
