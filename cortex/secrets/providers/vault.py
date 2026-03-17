"""Compatibility module aliasing Vault secrets provider implementation."""

import sys
from cortex.infrastructure.secrets.providers import vault as _vault

sys.modules[__name__] = _vault
