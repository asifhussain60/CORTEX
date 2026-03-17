"""Compatibility module aliasing AWS secrets provider implementation."""

import sys
from cortex.infrastructure.secrets.providers import aws as _aws

sys.modules[__name__] = _aws
