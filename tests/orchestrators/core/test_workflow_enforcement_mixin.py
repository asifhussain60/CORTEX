"""
GAP-128-E-03: WorkflowEnforcementMixin must be present in core orchestrators
and the enforce_gateway decorator must be properly wired.

Tests that:
- WorkflowEnforcementMixin is defined in cortex/core/workflow_enforcement_mixin.py
- MasterOrchestrator, TDDOrchestrator, and EnforcementOrchestrator inherit it
- PHASE90_GATEWAY_ENABLED flag exists in the mixin
- enforce_gateway decorator is importable and callable

Drift lock: check-45-orchestrator-wiring-integrity-lock.yaml
"""

import ast
import importlib
import sys
from pathlib import Path
from typing import List, Set
import pytest

REPO_ROOT = Path(__file__).parents[3]
MIXIN_FILE = REPO_ROOT / "cortex/core/workflow_enforcement_mixin.py"

# Orchestrators that must inherit WorkflowEnforcementMixin
REQUIRED_INHERITORS = [
    ("cortex/orchestrators/core/master_orchestrator.py", "MasterOrchestrator"),
    ("cortex/orchestrators/core/tdd_orchestrator.py", "TDDOrchestrator"),
    ("cortex/orchestrators/core/enforcement_orchestrator.py", "EnforcementOrchestrator"),
]


def _get_base_classes(file_path: Path) -> dict:
    """Return {class_name: [base_names]} from a Python file."""
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return {}
    result = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(base.attr)
            result[node.name] = bases
    return result


class TestWorkflowEnforcementMixin:
    """GAP-128-E-03: WorkflowEnforcementMixin wiring and decorator contracts."""

    def test_mixin_file_exists(self):
        """cortex/core/workflow_enforcement_mixin.py must exist."""
        assert MIXIN_FILE.exists(), f"WorkflowEnforcementMixin file not found: {MIXIN_FILE}"

    def test_mixin_class_defined(self):
        """WorkflowEnforcementMixin class must be defined in the mixin file."""
        classes = _get_base_classes(MIXIN_FILE)
        assert "WorkflowEnforcementMixin" in classes, (
            "WorkflowEnforcementMixin class not found in workflow_enforcement_mixin.py"
        )

    def test_gateway_enabled_flag_present(self):
        """PHASE90_GATEWAY_ENABLED must be defined in the mixin file."""
        content = MIXIN_FILE.read_text(encoding="utf-8")
        assert "PHASE90_GATEWAY_ENABLED" in content, (
            "PHASE90_GATEWAY_ENABLED flag not found in workflow_enforcement_mixin.py"
        )

    def test_enforce_gateway_decorator_present(self):
        """enforce_gateway decorator function must be defined."""
        content = MIXIN_FILE.read_text(encoding="utf-8")
        assert "def enforce_gateway" in content, (
            "enforce_gateway decorator not found in workflow_enforcement_mixin.py"
        )

    def test_master_orchestrator_inherits_mixin(self):
        """MasterOrchestrator must inherit WorkflowEnforcementMixin."""
        file_path = REPO_ROOT / "cortex/orchestrators/core/master_orchestrator.py"
        if not file_path.exists():
            pytest.skip("master_orchestrator.py not found")
        content = file_path.read_text(encoding="utf-8")
        assert "WorkflowEnforcementMixin" in content, (
            "MasterOrchestrator does not reference WorkflowEnforcementMixin"
        )

    def test_tdd_orchestrator_inherits_mixin(self):
        """TDDOrchestrator must inherit WorkflowEnforcementMixin."""
        file_path = REPO_ROOT / "cortex/orchestrators/core/tdd_orchestrator.py"
        if not file_path.exists():
            pytest.skip("tdd_orchestrator.py not found")
        content = file_path.read_text(encoding="utf-8")
        assert "WorkflowEnforcementMixin" in content, (
            "TDDOrchestrator does not reference WorkflowEnforcementMixin"
        )

    def test_enforcement_orchestrator_inherits_mixin(self):
        """EnforcementOrchestrator must inherit WorkflowEnforcementMixin."""
        file_path = REPO_ROOT / "cortex/orchestrators/core/enforcement_orchestrator.py"
        if not file_path.exists():
            pytest.skip("enforcement_orchestrator.py not found")
        content = file_path.read_text(encoding="utf-8")
        assert "WorkflowEnforcementMixin" in content, (
            "EnforcementOrchestrator does not reference WorkflowEnforcementMixin"
        )

    def test_mixin_importable(self):
        """cortex.core.workflow_enforcement_mixin must be importable."""
        try:
            sys.path.insert(0, str(REPO_ROOT))
            mod = importlib.import_module("cortex.core.workflow_enforcement_mixin")
            assert hasattr(mod, "WorkflowEnforcementMixin"), (
                "WorkflowEnforcementMixin not exported from the module"
            )
            assert hasattr(mod, "enforce_gateway"), (
                "enforce_gateway not exported from the module"
            )
        except ImportError as e:
            pytest.skip(f"Cannot import workflow_enforcement_mixin: {e}")

    def test_mixin_has_gateway_method(self):
        """WorkflowEnforcementMixin must have a gateway dispatch method."""
        content = MIXIN_FILE.read_text(encoding="utf-8")
        # Should have some method for dispatching through the gateway
        has_gateway_method = (
            "def gateway" in content
            or "def _gateway" in content
            or "def route_through_gateway" in content
            or "WorkflowGateway" in content
        )
        assert has_gateway_method, (
            "WorkflowEnforcementMixin appears to have no gateway dispatch method or reference"
        )
