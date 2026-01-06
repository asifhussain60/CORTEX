"""
Lazy Import Utility - Defer expensive imports until needed.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import importlib
from types import ModuleType
from typing import Any


class LazyModule:
    """Lazy-loading module wrapper."""
    
    def __init__(self, module_name: str):
        self._module_name = module_name
        self._module: ModuleType | None = None
    
    def _load(self) -> ModuleType:
        """Load the module if not already loaded."""
        if self._module is None:
            self._module = importlib.import_module(self._module_name)
        return self._module
    
    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the loaded module."""
        return getattr(self._load(), name)


def lazy_import(module_name: str) -> LazyModule:
    """
    Create a lazy-loading module.
    
    Args:
        module_name: Full module import path
    
    Returns:
        LazyModule wrapper
    
    Example:
        _entry_module = lazy_import('src.entry_point.cortex_entry')
        # Module not imported yet
        
        entry = _entry_module.CortexEntry()
        # Module imported on first access
    """
    return LazyModule(module_name)
