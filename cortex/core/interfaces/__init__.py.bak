"""Core Interfaces Package - Central location for core interface definitions.

Re-exports interfaces from parent module.

Author: CORTEX Framework
"""

import importlib.util
import sys
from pathlib import Path

# Load the interfaces.py file directly (sibling to this directory)
_interfaces_py_path = Path(__file__).parent.parent / "interfaces.py"
_spec = importlib.util.spec_from_file_location("cortex.core._interfaces_module", _interfaces_py_path)
_interfaces_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_interfaces_module)

# Export the classes
IOrchestrator = _interfaces_module.IOrchestrator
OrchestratorBase = _interfaces_module.OrchestratorBase
OperationMode = _interfaces_module.OperationMode
IExecutor = _interfaces_module.IExecutor
ExecutionContext = _interfaces_module.ExecutionContext

__all__ = ["IOrchestrator", "OrchestratorBase", "OperationMode", "IExecutor", "ExecutionContext"]
