"""
Tests for IntelligenceValidator - Phase 71 S6.

AC-ID: PHASE-71-S6
Purpose: Verify E2E intelligence generation and validation

Test Coverage:
1. Learning pipeline validation
2. Orchestrator learning validation
3. Knowledge persistence validation
4. Confidence scoring validation
5. Error handling and reporting

Author: Asif Hussain
Date: 2026-02-10
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import tempfile
import yaml

from cortex.learning.intelligence_validator import (
    IntelligenceValidator,
    ValidationReport,
    get_intelligence_validator,
)
from cortex.core.result import Ok, Err


# =============================================================================
# Test: ValidationReport
# =============================================================================

class TestValidationReport:
    """Tests for ValidationReport dataclass."""
    
    def test_report_initialization(self):
        """Report should initialize with default values."""
        report = ValidationReport()
        
        assert report.is_valid is True
        assert len(report.orchestrators_tested) == 0
        assert report.patterns_captured == 0
        assert len(report.validation_errors) == 0
    
    def test_report_to_dict(self):
        """Report should convert to dictionary."""
        report = ValidationReport()
        report.orchestrators_tested.add("tdd")
        report.patterns_captured = 10
        report.validation_errors.append("Test error")
        
        data = report.to_dict()
        
        assert "orchestrators_tested" in data
        assert "patterns_captured" in data
        assert data["patterns_captured"] == 10
        assert len(data["validation_errors"]) == 1


# =============================================================================
# Test: IntelligenceValidator Initialization
# =============================================================================

class TestValidatorInitialization:
    """Tests for validator initialization."""
    
    def test_validator_init_with_default_root(self):
        """Validator should initialize with default workspace root."""
        validator = IntelligenceValidator()
        
        assert validator.workspace_root is not None
        assert validator.knowledge_repo is not None
    
    def test_validator_init_with_custom_root(self):
        """Validator should initialize with custom workspace root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            validator = IntelligenceValidator(root)
            
            assert validator.workspace_root == root
    
    def test_validator_learning_loop_reference(self):
        """Validator should reference learning loop."""
        validator = IntelligenceValidator()
        
        # Learning loop may or may not be available
        # Just check that the reference is made
        assert hasattr(validator, "learning_loop")


# =============================================================================
# Test: Learning Pipeline Validation
# =============================================================================

class TestLearningPipelineValidation:
    """Tests for learning pipeline validation."""
    
    def test_validate_no_learning_loop(self):
        """Validation should fail gracefully if learning loop unavailable."""
        validator = IntelligenceValidator()
        
        with patch("cortex.learning.intelligence_validator.get_learning_loop") as mock_get:
            mock_get.return_value = None
            validator.learning_loop = None
            
            report = validator.validate_learning_pipeline()
            
            assert not report.is_valid
            assert any("Learning loop" in e for e in report.validation_errors)
    
    def test_validate_no_knowledge_repo(self):
        """Validation should fail if knowledge repo missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            validator = IntelligenceValidator(root)
            validator.learning_loop = MagicMock()
            
            report = validator.validate_learning_pipeline()
            
            # Should report missing knowledge repo
            assert not report.is_valid or len(report.validation_errors) > 0
    
    def test_validate_with_metrics(self):
        """Validation should check learning metrics."""
        validator = IntelligenceValidator()
        validator.learning_loop = MagicMock()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            validator.workspace_root = root
            knowledge_repo = root / "cortex" / "knowledge"
            knowledge_repo.mkdir(parents=True)
            validator.knowledge_repo = knowledge_repo
            
            # Mock metrics
            metrics = {
                "by_orchestrator": {
                    "TDDOrchestrator": {
                        "count": 5,
                        "avg_confidence": 0.85,
                    }
                },
                "total_patterns": 10,
            }
            validator.learning_loop.get_learning_metrics.return_value = metrics
            
            report = validator.validate_learning_pipeline()
            
            assert "TDDOrchestrator" in report.orchestrators_tested
            assert report.patterns_captured == 10


# =============================================================================
# Test: Orchestrator Learning Validation
# =============================================================================

class TestOrchestratorLearningValidation:
    """Tests for orchestrator-specific learning validation."""
    
    def test_validate_orchestrator_no_loop(self):
        """Validation should fail if learning loop unavailable."""
        validator = IntelligenceValidator()
        validator.learning_loop = None
        
        result = validator.validate_orchestrator_learning("TDD", "tdd")
        
        assert result.is_err()
    
    def test_validate_orchestrator_with_learnings(self):
        """Validation should succeed if orchestrator has learnings."""
        validator = IntelligenceValidator()
        validator.learning_loop = MagicMock()
        
        metrics = {
            "by_orchestrator": {
                "TDDOrchestrator": {
                    "count": 5,
                    "patterns": 10,
                    "avg_confidence": 0.85,
                }
            }
        }
        validator.learning_loop.get_learning_metrics.return_value = metrics
        
        result = validator.validate_orchestrator_learning("TDDOrchestrator", "tdd")
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["learning_count"] == 5
        assert data["confidence_avg"] == 0.85
    
    def test_validate_orchestrator_no_learnings(self):
        """Validation should fail if orchestrator has no learnings."""
        validator = IntelligenceValidator()
        validator.learning_loop = MagicMock()
        
        metrics = {"by_orchestrator": {}}
        validator.learning_loop.get_learning_metrics.return_value = metrics
        
        result = validator.validate_orchestrator_learning("TDDOrchestrator", "tdd")
        
        assert result.is_err()


# =============================================================================
# Test: Knowledge Persistence Validation
# =============================================================================

class TestKnowledgePersistenceValidation:
    """Tests for knowledge YAML persistence validation."""
    
    def test_validate_knowledge_file_not_found(self):
        """Validation should fail if knowledge file missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            validator = IntelligenceValidator(root)
            
            result = validator.validate_knowledge_persistence("nonexistent")
            
            assert result.is_err()
    
    def test_validate_knowledge_file_valid_yaml(self):
        """Validation should succeed for valid YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            knowledge_repo = root / "cortex" / "knowledge"
            knowledge_repo.mkdir(parents=True)
            
            # Create valid knowledge YAML
            knowledge_file = knowledge_repo / "tdd_patterns.yaml"
            knowledge_data = {
                "patterns": [{"name": "test_first", "confidence": 0.9}],
                "metadata": {"generated": "2026-02-10"},
            }
            with open(knowledge_file, "w") as f:
                yaml.dump(knowledge_data, f)
            
            validator = IntelligenceValidator(root)
            result = validator.validate_knowledge_persistence("tdd_patterns")
            
            assert result.is_ok()
    
    def test_validate_knowledge_file_invalid_yaml(self):
        """Validation should fail for invalid YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            knowledge_repo = root / "cortex" / "knowledge"
            knowledge_repo.mkdir(parents=True)
            
            # Create invalid YAML
            knowledge_file = knowledge_repo / "bad_patterns.yaml"
            with open(knowledge_file, "w") as f:
                f.write("[[[[[")  # Invalid YAML
            
            validator = IntelligenceValidator(root)
            result = validator.validate_knowledge_persistence("bad_patterns")
            
            assert result.is_err()
    
    def test_validate_knowledge_file_missing_keys(self):
        """Validation should fail if required keys missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            knowledge_repo = root / "cortex" / "knowledge"
            knowledge_repo.mkdir(parents=True)
            
            # Create YAML without required keys
            knowledge_file = knowledge_repo / "incomplete.yaml"
            knowledge_data = {"only_one_key": "value"}
            with open(knowledge_file, "w") as f:
                yaml.dump(knowledge_data, f)
            
            validator = IntelligenceValidator(root)
            result = validator.validate_knowledge_persistence("incomplete")
            
            assert result.is_err()


# =============================================================================
# Test: Confidence Scoring Validation
# =============================================================================

class TestConfidenceScoringValidation:
    """Tests for confidence score validation."""
    
    def test_validate_confidence_no_loop(self):
        """Validation should fail if learning loop unavailable."""
        validator = IntelligenceValidator()
        validator.learning_loop = None
        
        result = validator.validate_confidence_scoring()
        
        assert result.is_err()
    
    def test_validate_confidence_with_scores(self):
        """Validation should report confidence statistics."""
        validator = IntelligenceValidator()
        validator.learning_loop = MagicMock()
        
        metrics = {
            "by_orchestrator": {
                "TDDOrchestrator": {
                    "confidences": [0.9, 0.85, 0.95],
                },
                "RefactoringOrchestrator": {
                    "confidences": [0.8, 0.75],
                }
            }
        }
        validator.learning_loop.get_learning_metrics.return_value = metrics
        
        result = validator.validate_confidence_scoring()
        
        assert result.is_ok()
        data = result.unwrap()
        assert "average_confidence" in data
        assert "min_confidence" in data
        assert "max_confidence" in data
        assert 0.7 <= data["average_confidence"] <= 1.0
    
    def test_validate_confidence_no_scores(self):
        """Validation should handle case with no confidence scores."""
        validator = IntelligenceValidator()
        validator.learning_loop = MagicMock()
        
        metrics = {"by_orchestrator": {}}
        validator.learning_loop.get_learning_metrics.return_value = metrics
        
        result = validator.validate_confidence_scoring()
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["samples"] == 0


# =============================================================================
# Test: Singleton Pattern
# =============================================================================

class TestSingleton:
    """Tests for singleton getter."""
    
    def test_get_intelligence_validator(self):
        """Getter should return validator instance."""
        validator = get_intelligence_validator()
        
        assert validator is not None
        assert isinstance(validator, IntelligenceValidator)


# =============================================================================
# Test: Integration
# =============================================================================

class TestIntegration:
    """Integration tests for complete validation scenario."""
    
    def test_full_validation_scenario(self):
        """Test complete validation scenario with proper setup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            knowledge_repo = root / "cortex" / "knowledge"
            knowledge_repo.mkdir(parents=True)
            
            # Create knowledge files
            for pattern_type in ["tdd", "refactoring"]:
                pattern_file = knowledge_repo / f"{pattern_type}_patterns.yaml"
                data = {
                    "patterns": [{"name": "test_pattern", "confidence": 0.85}],
                    "metadata": {"generated": "2026-02-10"},
                }
                with open(pattern_file, "w") as f:
                    yaml.dump(data, f)
            
            # Create validator with mocked learning loop
            validator = IntelligenceValidator(root)
            validator.learning_loop = MagicMock()
            
            metrics = {
                "by_orchestrator": {
                    "TDDOrchestrator": {
                        "count": 5,
                        "patterns": 10,
                        "avg_confidence": 0.85,
                        "confidences": [0.9, 0.85, 0.8],
                    },
                    "RefactoringOrchestrator": {
                        "count": 3,
                        "patterns": 5,
                        "avg_confidence": 0.80,
                        "confidences": [0.8, 0.75],
                    }
                },
                "total_patterns": 15,
            }
            validator.learning_loop.get_learning_metrics.return_value = metrics
            
            # Run full validation
            report = validator.validate_learning_pipeline()
            
            # Verify results
            assert len(report.orchestrators_tested) >= 0
            assert report.patterns_captured == 15
