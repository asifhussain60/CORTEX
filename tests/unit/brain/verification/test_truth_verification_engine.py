"""
Truth Verification Engine Tests

Tests for implementation truth verification and claim validation.

Phase 22 Component #4: TruthVerificationEngine Tests (30 tests)

Authority: AC-EDUCATIONAL-INTERACTION-001, CORE-030
Rule: CORE-008 (TDD)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from cortex.brain.verification.truth_verification_engine import (
    TruthVerificationEngine,
    VerificationResult,
    VerificationStatus,
    ClaimType,
    Evidence,
)


@pytest.fixture
def engine():
    """Create TruthVerificationEngine instance."""
    return TruthVerificationEngine()


@pytest.fixture
def mock_project_root(tmp_path):
    """Create mock project structure."""
    # Create directory structure
    (tmp_path / "cortex" / "orchestrators" / "core").mkdir(parents=True)
    (tmp_path / "cortex" / "wiring" / "specifications").mkdir(parents=True)
    (tmp_path / "tests" / "unit").mkdir(parents=True)
    
    # Create sample orchestrator file
    orchestrator_file = tmp_path / "cortex" / "orchestrators" / "core" / "master_orchestrator.py"
    orchestrator_file.write_text("""
class MasterOrchestrator:
    def __init__(self):
        pass
    
    def stage_2_routing(self):
        pass
    
    def execute(self, parameters):
        pass
""")
    
    # Create wiring.yaml
    wiring_file = tmp_path / "cortex" / "wiring" / "specifications" / "wiring.yaml"
    wiring_file.write_text("""
orchestrators:
  - name: MasterOrchestrator
    module: cortex.orchestrators.core.master_orchestrator
    class_name: MasterOrchestrator
""")
    
    return tmp_path


class TestVerificationStatusEnum:
    """Test VerificationStatus enum."""
    
    def test_all_status_values_exist(self):
        """Test that all expected status values exist."""
        assert VerificationStatus.VERIFIED
        assert VerificationStatus.FALSE
        assert VerificationStatus.PARTIAL
        assert VerificationStatus.UNKNOWN
        assert VerificationStatus.DRIFT


class TestClaimTypeEnum:
    """Test ClaimType enum."""
    
    def test_all_claim_types_exist(self):
        """Test that all expected claim types exist."""
        assert ClaimType.ORCHESTRATOR_EXISTS
        assert ClaimType.ORCHESTRATOR_CAPABILITY
        assert ClaimType.WIRING_CONFIG
        assert ClaimType.FILE_EXISTS
        assert ClaimType.FUNCTION_EXISTS
        assert ClaimType.CLASS_EXISTS
        assert ClaimType.TEST_COVERAGE
        assert ClaimType.MCP_TOOL


class TestEvidenceDataclass:
    """Test Evidence dataclass."""
    
    def test_creates_evidence_with_required_fields(self):
        """Test Evidence creation with required fields."""
        evidence = Evidence(
            source_type="code",
            file_path="cortex/orchestrators/master_orchestrator.py",
            line_number=42,
            description="Found class definition"
        )
        
        assert evidence.source_type == "code"
        assert evidence.file_path == "cortex/orchestrators/master_orchestrator.py"
        assert evidence.line_number == 42
        assert evidence.description == "Found class definition"


class TestVerificationResultDataclass:
    """Test VerificationResult dataclass."""
    
    def test_creates_result_with_verified_status(self):
        """Test VerificationResult creation with verified status."""
        result = VerificationResult(
            claim="MasterOrchestrator exists",
            claim_type=ClaimType.ORCHESTRATOR_EXISTS,
            status=VerificationStatus.VERIFIED,
            confidence=1.0,
            evidence=[],
            explanation="Found in codebase"
        )
        
        assert result.status == VerificationStatus.VERIFIED
        assert result.confidence == 1.0
        assert result.drift_detected is False


class TestTruthVerificationEngineInit:
    """Test TruthVerificationEngine initialization."""
    
    def test_initializes_with_default_project_root(self):
        """Test initialization with auto-detected project root."""
        engine = TruthVerificationEngine()
        
        assert engine.project_root is not None
        assert isinstance(engine.project_root, Path)
    
    def test_initializes_with_custom_project_root(self, tmp_path):
        """Test initialization with custom project root."""
        engine = TruthVerificationEngine(project_root=tmp_path)
        
        assert engine.project_root == tmp_path


class TestOrchestratorExistsVerification:
    """Test orchestrator existence verification."""
    
    def test_verifies_existing_orchestrator(self, mock_project_root):
        """Test verification of existing orchestrator."""
        engine = TruthVerificationEngine(project_root=mock_project_root)
        
        result = engine.verify_claim(
            claim="MasterOrchestrator exists",
            claim_type=ClaimType.ORCHESTRATOR_EXISTS,
            context={"orchestrator_name": "MasterOrchestrator"}
        )
        
        assert result.status == VerificationStatus.VERIFIED
        assert result.confidence == 1.0
        assert len(result.evidence) > 0
    
    def test_detects_missing_orchestrator(self, mock_project_root):
        """Test detection of missing orchestrator."""
        engine = TruthVerificationEngine(project_root=mock_project_root)
        
        result = engine.verify_claim(
            claim="NonExistentOrchestrator exists",
            claim_type=ClaimType.ORCHESTRATOR_EXISTS,
            context={"orchestrator_name": "NonExistentOrchestrator"}
        )
        
        assert result.status == VerificationStatus.FALSE
        assert result.confidence == 1.0
        assert len(result.recommendations) > 0


class TestOrchestratorCapabilityVerification:
    """Test orchestrator capability verification."""
    
    def test_verifies_orchestrator_capability(self, mock_project_root):
        """Test verification of orchestrator capability."""
        engine = TruthVerificationEngine(project_root=mock_project_root)
        
        result = engine.verify_claim(
            claim="MasterOrchestrator has stage_2_routing",
            claim_type=ClaimType.ORCHESTRATOR_CAPABILITY,
            context={
                "orchestrator_name": "MasterOrchestrator",
                "capability": "stage_2_routing"
            }
        )
        
        assert result.status == VerificationStatus.VERIFIED
        assert result.confidence >= 0.8
    
    def test_detects_missing_capability(self, mock_project_root):
        """Test detection of missing capability."""
        engine = TruthVerificationEngine(project_root=mock_project_root)
        
        result = engine.verify_claim(
            claim="MasterOrchestrator has nonexistent_method",
            claim_type=ClaimType.ORCHESTRATOR_CAPABILITY,
            context={
                "orchestrator_name": "MasterOrchestrator",
                "capability": "nonexistent_method"
            }
        )
        
        assert result.status in [VerificationStatus.PARTIAL, VerificationStatus.FALSE]


class TestWiringConfigVerification:
    """Test wiring configuration verification."""
    
    def test_verifies_wiring_yaml_exists(self, mock_project_root):
        """Test verification of wiring.yaml existence."""
        engine = TruthVerificationEngine(project_root=mock_project_root)
        
        result = engine.verify_claim(
            claim="wiring.yaml exists",
            claim_type=ClaimType.WIRING_CONFIG
        )
        
        assert result.status == VerificationStatus.VERIFIED
        assert result.confidence == 1.0
    
    def test_detects_missing_wiring_yaml(self, tmp_path):
        """Test detection of missing wiring.yaml."""
        engine = TruthVerificationEngine(project_root=tmp_path)
        
        result = engine.verify_claim(
            claim="wiring.yaml exists",
            claim_type=ClaimType.WIRING_CONFIG
        )
        
        assert result.status == VerificationStatus.FALSE
        assert "not found" in result.explanation.lower()


class TestFileExistsVerification:
    """Test file existence verification."""
    
    def test_verifies_existing_file(self, mock_project_root):
        """Test verification of existing file."""
        engine = TruthVerificationEngine(project_root=mock_project_root)
        
        result = engine.verify_claim(
            claim="File exists at cortex/orchestrators/core/master_orchestrator.py",
            claim_type=ClaimType.FILE_EXISTS,
            context={"file_path": "cortex/orchestrators/core/master_orchestrator.py"}
        )
        
        assert result.status == VerificationStatus.VERIFIED
        assert result.confidence == 1.0
    
    def test_detects_missing_file(self, mock_project_root):
        """Test detection of missing file."""
        engine = TruthVerificationEngine(project_root=mock_project_root)
        
        result = engine.verify_claim(
            claim="File exists at cortex/nonexistent.py",
            claim_type=ClaimType.FILE_EXISTS,
            context={"file_path": "cortex/nonexistent.py"}
        )
        
        assert result.status == VerificationStatus.FALSE
        assert result.confidence == 1.0


class TestFunctionExistsVerification:
    """Test function existence verification."""
    
    def test_verifies_existing_function(self, mock_project_root):
        """Test verification of existing function."""
        engine = TruthVerificationEngine(project_root=mock_project_root)
        
        result = engine.verify_claim(
            claim="Function stage_2_routing exists",
            claim_type=ClaimType.FUNCTION_EXISTS,
            context={
                "file_path": "cortex/orchestrators/core/master_orchestrator.py",
                "function_name": "stage_2_routing"
            }
        )
        
        assert result.status == VerificationStatus.VERIFIED
        assert result.confidence == 1.0
        assert len(result.evidence) > 0
    
    def test_detects_missing_function(self, mock_project_root):
        """Test detection of missing function."""
        engine = TruthVerificationEngine(project_root=mock_project_root)
        
        result = engine.verify_claim(
            claim="Function nonexistent_func exists",
            claim_type=ClaimType.FUNCTION_EXISTS,
            context={
                "file_path": "cortex/orchestrators/core/master_orchestrator.py",
                "function_name": "nonexistent_func"
            }
        )
        
        assert result.status == VerificationStatus.FALSE
        assert len(result.recommendations) > 0


class TestClassExistsVerification:
    """Test class existence verification."""
    
    def test_verifies_existing_class(self, mock_project_root):
        """Test verification of existing class."""
        engine = TruthVerificationEngine(project_root=mock_project_root)
        
        result = engine.verify_claim(
            claim="Class MasterOrchestrator exists",
            claim_type=ClaimType.CLASS_EXISTS,
            context={
                "file_path": "cortex/orchestrators/core/master_orchestrator.py",
                "class_name": "MasterOrchestrator"
            }
        )
        
        assert result.status == VerificationStatus.VERIFIED
        assert result.confidence == 1.0
        assert len(result.evidence) > 0
    
    def test_detects_missing_class(self, mock_project_root):
        """Test detection of missing class."""
        engine = TruthVerificationEngine(project_root=mock_project_root)
        
        result = engine.verify_claim(
            claim="Class NonExistentClass exists",
            claim_type=ClaimType.CLASS_EXISTS,
            context={
                "file_path": "cortex/orchestrators/core/master_orchestrator.py",
                "class_name": "NonExistentClass"
            }
        )
        
        assert result.status == VerificationStatus.FALSE
        assert result.confidence == 1.0


class TestTestCoverageVerification:
    """Test coverage verification."""
    
    def test_verifies_test_coverage_when_tests_exist(self, mock_project_root):
        """Test verification when test files exist."""
        # Create test file
        test_file = mock_project_root / "tests" / "unit" / "test_master_orchestrator.py"
        test_file.write_text("def test_something(): pass")
        
        engine = TruthVerificationEngine(project_root=mock_project_root)
        
        result = engine.verify_claim(
            claim="MasterOrchestrator has test coverage",
            claim_type=ClaimType.TEST_COVERAGE,
            context={"component_name": "MasterOrchestrator"}
        )
        
        assert result.status == VerificationStatus.VERIFIED
        assert len(result.evidence) > 0
    
    def test_detects_missing_test_coverage(self, mock_project_root):
        """Test detection of missing test coverage."""
        engine = TruthVerificationEngine(project_root=mock_project_root)
        
        result = engine.verify_claim(
            claim="NonExistentComponent has test coverage",
            claim_type=ClaimType.TEST_COVERAGE,
            context={"component_name": "NonExistentComponent"}
        )
        
        assert result.status == VerificationStatus.FALSE
        assert len(result.recommendations) > 0


class TestMCPToolVerification:
    """Test MCP tool verification."""
    
    def test_detects_missing_mcp_tools_directory(self, tmp_path):
        """Test detection when MCP tools directory doesn't exist."""
        engine = TruthVerificationEngine(project_root=tmp_path)
        
        result = engine.verify_claim(
            claim="cortex_ask MCP tool exists",
            claim_type=ClaimType.MCP_TOOL,
            context={"tool_name": "cortex_ask"}
        )
        
        assert result.status == VerificationStatus.FALSE
        assert "not found" in result.explanation.lower()


class TestExtractionHelpers:
    """Test entity extraction helper methods."""
    
    def test_extracts_orchestrator_name(self, engine):
        """Test orchestrator name extraction."""
        name = engine._extract_orchestrator_name("The MasterOrchestrator handles routing")
        assert "Orchestrator" in name
    
    def test_extracts_file_path(self, engine):
        """Test file path extraction."""
        path = engine._extract_file_path("Located at cortex/orchestrators/master.py")
        assert "cortex/" in path
    
    def test_extracts_function_name(self, engine):
        """Test function name extraction."""
        name = engine._extract_function_name("The function execute() does something")
        assert name == "execute"
    
    def test_extracts_class_name(self, engine):
        """Test class name extraction."""
        name = engine._extract_class_name("The MasterOrchestrator class")
        assert name == "MasterOrchestrator"


class TestErrorHandling:
    """Test error handling in verification."""
    
    def test_handles_unknown_claim_type_gracefully(self, engine):
        """Test handling of unknown claim type."""
        # Create a mock claim type that doesn't have a handler
        result = engine.verify_claim(
            claim="Some claim",
            claim_type=ClaimType.GIT_HISTORY  # No handler implemented yet
        )
        
        assert result.status == VerificationStatus.UNKNOWN
        assert "not implemented" in result.explanation.lower()
    
    def test_handles_verification_exceptions(self, engine, mock_project_root):
        """Test handling of exceptions during verification."""
        # Force an exception by providing invalid context
        with patch.object(engine, '_verify_file_exists', side_effect=Exception("Test error")):
            result = engine.verify_claim(
                claim="Test claim",
                claim_type=ClaimType.FILE_EXISTS
            )
            
            assert result.status == VerificationStatus.UNKNOWN
            assert "failed" in result.explanation.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
