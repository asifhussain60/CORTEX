"""
GAP-003 RED: SQL-001 — IntelligenceOrchestrator and ContractValidator must not use raw sqlite3.connect().
Both must route audit persistence through .cortex-runtime/ paths.

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import inspect
import pytest
from pathlib import Path
from unittest.mock import patch
import tempfile
import os


class TestIntelligenceOrchestratorAuditPath:
    """SQL-001: IntelligenceOrchestrator must write to .cortex-runtime/, not cortex/intelligence/."""

    def test_default_audit_path_not_cortex_intelligence(self) -> None:
        """Default audit_db_path must NOT reference cortex/intelligence/ directory."""
        from cortex.orchestrators.intelligence.intelligence_orchestrator import (
            IntelligenceOrchestrator,
        )

        src = inspect.getsource(IntelligenceOrchestrator.__init__)
        # Extract Path(...) literals only
        import re
        path_calls = re.findall(r'Path\("([^"]+)"\)', src)
        for p in path_calls:
            assert "cortex_intelligence" not in p, (
                f"IntelligenceOrchestrator uses gitignored path: Path('{p}')"
            )

    def test_default_audit_path_uses_cortex_runtime(self) -> None:
        """Default audit path must be under .cortex-runtime/."""
        from cortex.orchestrators.intelligence.intelligence_orchestrator import (
            IntelligenceOrchestrator,
        )

        src = inspect.getsource(IntelligenceOrchestrator.__init__)
        import re
        path_calls = re.findall(r'Path\("([^"]+)"\)', src)
        cortex_runtime_paths = [p for p in path_calls if ".cortex-runtime" in p]
        assert len(cortex_runtime_paths) >= 1, (
            f"IntelligenceOrchestrator default path must use .cortex-runtime/. Found: {path_calls}"
        )


class TestContractValidatorAuditPath:
    """SQL-001: ContractValidator must write to .cortex-runtime/, not cortex/intelligence/wiring/."""

    def test_default_audit_path_not_cortex_intelligence(self) -> None:
        """ContractValidator default audit_db path must NOT be inside cortex/intelligence/."""
        from cortex.core.wiring.registry.contract_validator import ContractValidator

        src = inspect.getsource(ContractValidator.__init__)
        import re
        path_calls = re.findall(r'Path\("([^"]+)"\)', src)
        for p in path_calls:
            assert "cortex_intelligence" not in p, (
                f"ContractValidator uses gitignored path: Path('{p}')"
            )

    def test_default_audit_path_uses_cortex_runtime(self) -> None:
        """ContractValidator default path must resolve under .cortex-runtime/."""
        from cortex.core.wiring.registry.contract_validator import ContractValidator

        src = inspect.getsource(ContractValidator.__init__)
        import re
        path_calls = re.findall(r'Path\("([^"]+)"\)', src)
        cortex_runtime_paths = [p for p in path_calls if ".cortex-runtime" in p]
        assert len(cortex_runtime_paths) >= 1, (
            f"ContractValidator default path must use .cortex-runtime/. Found: {path_calls}"
        )

    def test_contract_validator_importable(self) -> None:
        """ContractValidator must import cleanly."""
        from cortex.core.wiring.registry.contract_validator import ContractValidator

        assert ContractValidator is not None
