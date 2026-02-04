"""
Phase 22 Component #10: cortex_verify_claim MCP Tool Tests (12 tests)

Tests for standalone claim verification via MCP interface.
"""

import pytest
from unittest.mock import Mock, patch
from cortex.mcp.tools.cortex_verify_claim import (
    cortex_verify_claim,
    validate_claim,
    format_verification_result,
)


class TestCortexVerifyClaim:
    """Tests for cortex_verify_claim MCP tool functionality."""

    def test_verify_claim_basic(self):
        """Test basic claim verification."""
        result = cortex_verify_claim(
            claim="MasterOrchestrator coordinates all operations"
        )
        
        assert result["status"] == "success"
        assert "verdict" in result
        assert result["verdict"] in ["verified", "false", "partial"]

    def test_verify_claim_empty(self):
        """Test handling of empty claim."""
        result = cortex_verify_claim(claim="")
        
        assert result["status"] == "error"
        assert "error" in result
        assert "claim cannot be empty" in result["error"].lower()

    def test_verify_claim_with_evidence(self):
        """Test that verification includes evidence."""
        result = cortex_verify_claim(
            claim="EducationalOrchestrator exists in wiring.yaml"
        )
        
        assert result["status"] == "success"
        if result["verdict"] == "verified":
            assert "evidence" in result
            assert isinstance(result["evidence"], list)

    def test_verify_claim_file_reference(self):
        """Test claim with file reference."""
        result = cortex_verify_claim(
            claim="cortex/orchestrators/education/educational_orchestrator.py implements execute()",
            file_path="cortex/orchestrators/education/educational_orchestrator.py"
        )
        
        assert result["status"] == "success"
        assert "file_path" in result

    def test_verify_claim_false_claim(self):
        """Test verification of false claim."""
        result = cortex_verify_claim(
            claim="CORTEX has 1000 orchestrators"
        )
        
        assert result["status"] == "success"
        # Should detect this is false (we have 33)
        assert result["verdict"] in ["false", "partial"]

    def test_verify_claim_partial_truth(self):
        """Test partially true claim."""
        result = cortex_verify_claim(
            claim="CORTEX uses Python and JavaScript"  # True for Python, false for JS
        )
        
        assert result["status"] == "success"
        # Could be verified (Python) or partial (depends on JS detection)

    def test_verify_claim_multiple_files(self):
        """Test claim spanning multiple files."""
        result = cortex_verify_claim(
            claim="All orchestrators inherit from BaseOrchestrator",
            scope="all"
        )
        
        assert result["status"] == "success"

    def test_verify_claim_with_ast_check(self):
        """Test claim requiring AST analysis."""
        result = cortex_verify_claim(
            claim="TDDOrchestrator has generate_tests method",
            use_ast=True
        )
        
        assert result["status"] == "success"
        if result["verdict"] == "verified":
            assert "ast_evidence" in result.get("evidence", [{}])[0] or "evidence" in result

    def test_validate_claim_valid(self):
        """Test claim validation with valid input."""
        is_valid, error = validate_claim("CORTEX exists")
        assert is_valid is True
        assert error is None

    def test_validate_claim_empty(self):
        """Test claim validation with empty input."""
        is_valid, error = validate_claim("")
        assert is_valid is False
        assert error is not None

    def test_format_verification_result(self):
        """Test verification result formatting."""
        raw_result = {
            "verdict": "verified",
            "evidence": [
                {"type": "file", "path": "test.py", "line": 10}
            ],
            "confidence": 0.95
        }
        
        formatted = format_verification_result(raw_result)
        
        assert formatted["status"] == "success"
        assert formatted["verdict"] == "verified"
        assert "evidence" in formatted

    def test_verify_claim_error_handling(self):
        """Test error handling when verification fails."""
        with patch('cortex.mcp.tools.cortex_verify_claim.TruthVerificationEngine') as mock_engine:
            mock_instance = Mock()
            mock_instance.verify_claim.side_effect = Exception("Verification error")
            mock_engine.return_value = mock_instance
            
            result = cortex_verify_claim(claim="Test claim")
            
            assert result["status"] == "error"
            assert "error" in result
