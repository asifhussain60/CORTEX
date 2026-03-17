"""Compatibility module aliasing secrets git-scanning implementation."""

import sys
from cortex.infrastructure.secrets import git_scanning as _git_scanning

sys.modules[__name__] = _git_scanning
