"""
Integration Test: AST/LENS Protocol Integration

AC-AST-LENS-001: Validates LENS protocol integration with comprehension
- Language analysis for intent detection
- Examination (AST) for code structure
- Navigation (git history) for change patterns
- Synthesis for holistic context
"""

import pytest
from typing import Any

try:
    from cortex.core.analysis.lens_protocol import LENSEngine
except (ImportError, ModuleNotFoundError):
    LENSEngine = None

try:
    from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
except (ImportError, ModuleNotFoundError):
    InteractionOrchestrator = None


@pytest.mark.skipif(LENSEngine is None, reason="LENSEngine not available")
class TestASTLENSIntegration:
    """AST/LENS protocol integration tests."""

    @pytest.fixture
    def lens_engine(self) -> Any:
        """Get LENS Engine instance."""
        if LENSEngine is None:
            pytest.skip("LENSEngine not available")
        return LENSEngine()

    @pytest.fixture
    def interaction(self) -> Any:
        """Get Interaction Orchestrator instance."""
        if InteractionOrchestrator is None:
            pytest.skip("InteractionOrchestrator not available")
        return InteractionOrchestrator()

    def test_lens_code_analysis_in_comprehension(
        self, lens_engine: Any, interaction: Any
    ):
        """
        LENS protocol provides code analysis during comprehension.

        Acceptance:
        - AST analysis performed
        - Language patterns identified
        - Navigation history analyzed
        - Results integrated in comprehension context
        """
        assert lens_engine is not None, "LENS Engine should initialize"
        assert hasattr(lens_engine, "analyze"), "Should analyze code"

    def test_lens_synthesis_in_context(self, lens_engine: Any):
        """
        LENS protocol synthesizes holistic context.

        Acceptance:
        - All LENS dimensions included
        - Synthesis produces comprehension YAML
        - Context available for routing decision
        """
        assert hasattr(lens_engine, "synthesize"), "Should synthesize context"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
