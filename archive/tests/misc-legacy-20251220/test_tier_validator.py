"""
Tests for Tier Validator

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Created: 2025-11-11
"""

import pytest
import tempfile
from pathlib import Path
import yaml
import json

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tier0.tier_validator import (
    TierValidator,
    TierLevel,
    ValidationSeverity,
    TierViolation,
    validate_brain_tiers
)


@pytest.fixture
def temp_brain_dir(tmp_path):
    """Create temporary brain directory structure."""
    brain_dir = tmp_path / "cortex-brain"
    brain_dir.mkdir()
    return brain_dir


@pytest.fixture
def validator(temp_brain_dir):
    """Create TierValidator with temp brain directory."""
    return TierValidator(brain_root=temp_brain_dir)


class TestTierValidatorInitialization:
    """Test TierValidator initialization."""
    
    def test_initializes_with_default_paths(self):
        """Verify validator initializes with default paths."""
        validator = TierValidator()
        assert validator.brain_root.name == "cortex-brain"
        assert TierLevel.TIER_0 in validator.tier_paths
        assert TierLevel.TIER_1 in validator.tier_paths
    
    def test_initializes_with_custom_brain_root(self, temp_brain_dir):
        """Verify validator accepts custom brain root."""
        validator = TierValidator(brain_root=temp_brain_dir)
        assert validator.brain_root == temp_brain_dir


class TestTier0Validation:
    """Test Tier 0 validation."""
    
    def test_detects_missing_tier0_file(self, validator):
        """Verify warning when Tier 0 file missing."""
        result = validator.validate_tier(TierLevel.TIER_0)
        assert not result.passed or len(result.warnings) > 0
    
    def test_validates_correct_tier0_structure(self, temp_brain_dir, validator):
        """Verify Tier 0 with correct structure passes."""
        tier0_path = temp_brain_dir / "brain-protection-rules.yaml"
        tier0_data = {
            "version": "2.0",
            "type": "governance",
            "protection_layers": []
        }
        with open(tier0_path, 'w') as f:
            yaml.dump(tier0_data, f)
        
        result = validator.validate_tier(TierLevel.TIER_0)
        assert result.passed
    
    def test_detects_application_data_in_tier0(self, temp_brain_dir, validator):
        """Verify critical violation for application data in Tier 0."""
        tier0_path = temp_brain_dir / "brain-protection-rules.yaml"
        tier0_data = {
            "version": "2.0",
            "conversation": "This should not be here"  # Forbidden keyword
        }
        with open(tier0_path, 'w') as f:
            yaml.dump(tier0_data, f)
        
        result = validator.validate_tier(TierLevel.TIER_0)
        assert not result.passed
        assert any(v.severity == ValidationSeverity.CRITICAL for v in result.violations)


class TestTier1Validation:
    """Test Tier 1 validation."""
    
    def test_detects_missing_tier1_file(self, validator):
        """Verify warning when Tier 1 file missing."""
        result = validator.validate_tier(TierLevel.TIER_1)
        assert len(result.warnings) > 0
    
    def test_validates_correct_jsonl_format(self, temp_brain_dir, validator):
        """Verify Tier 1 JSONL with correct format passes."""
        tier1_path = temp_brain_dir / "conversation-history.jsonl"
        entries = [
            {"timestamp": "2025-11-11T10:00:00", "conversation_id": "conv1", "role": "user", "content": "Hello"},
            {"timestamp": "2025-11-11T10:00:01", "conversation_id": "conv1", "role": "assistant", "content": "Hi"}
        ]
        with open(tier1_path, 'w') as f:
            for entry in entries:
                f.write(json.dumps(entry) + '\n')
        
        result = validator.validate_tier(TierLevel.TIER_1)
        assert result.passed or len(result.violations) == 0
    
    def test_detects_malformed_json_in_tier1(self, temp_brain_dir, validator):
        """Verify error for malformed JSON in Tier 1."""
        tier1_path = temp_brain_dir / "conversation-history.jsonl"
        with open(tier1_path, 'w') as f:
            f.write('{"valid": "json"}\n')
            f.write('not valid json\n')  # Malformed
        
        result = validator.validate_tier(TierLevel.TIER_1)
        assert not result.passed
        assert any("json" in v.message.lower() for v in result.violations)


class TestTier2Validation:
    """Test Tier 2 validation."""
    
    def test_detects_missing_tier2_file(self, validator):
        """Verify warning when Tier 2 file missing."""
        result = validator.validate_tier(TierLevel.TIER_2)
        assert len(result.warnings) > 0
    
    def test_validates_correct_knowledge_graph(self, temp_brain_dir, validator):
        """Verify Tier 2 with correct structure passes."""
        tier2_path = temp_brain_dir / "knowledge-graph.yaml"
        tier2_data = {
            "patterns": {
                "pattern1": {"confidence": 0.8, "occurrences": 5}
            }
        }
        with open(tier2_path, 'w') as f:
            yaml.dump(tier2_data, f)
        
        result = validator.validate_tier(TierLevel.TIER_2)
        assert result.passed or len(result.violations) == 0
    
    def test_detects_raw_conversation_in_tier2(self, temp_brain_dir, validator):
        """Verify critical violation for raw conversation data in Tier 2."""
        tier2_path = temp_brain_dir / "knowledge-graph.yaml"
        tier2_data = {
            "patterns": {},
            "raw_conversation": "User said hello"  # Forbidden
        }
        with open(tier2_path, 'w') as f:
            yaml.dump(tier2_data, f)
        
        result = validator.validate_tier(TierLevel.TIER_2)
        assert not result.passed
        assert any(v.severity == ValidationSeverity.CRITICAL for v in result.violations)


class TestTier3Validation:
    """Test Tier 3 validation."""
    
    def test_detects_missing_tier3_file(self, validator):
        """Verify warning when Tier 3 file missing."""
        result = validator.validate_tier(TierLevel.TIER_3)
        assert len(result.warnings) > 0
    
    def test_validates_correct_dev_context(self, temp_brain_dir, validator):
        """Verify Tier 3 with correct structure passes."""
        tier3_path = temp_brain_dir / "development-context.yaml"
        tier3_data = {
            "git_status": {"branch": "main"},
            "test_coverage": {"overall": 85.0}
        }
        with open(tier3_path, 'w') as f:
            yaml.dump(tier3_data, f)
        
        result = validator.validate_tier(TierLevel.TIER_3)
        assert result.passed or len(result.violations) == 0


class TestAllTiersValidation:
    """Test validation of all tiers."""
    
    def test_validates_all_tiers(self, validator):
        """Verify validate_all_tiers checks all tiers."""
        results = validator.validate_all_tiers()
        assert len(results) == 4  # All 4 tiers
        assert TierLevel.TIER_0 in results
        assert TierLevel.TIER_1 in results
        assert TierLevel.TIER_2 in results
        assert TierLevel.TIER_3 in results


class TestReportGeneration:
    """Test report generation."""
    
    def test_generates_readable_report(self, validator):
        """Verify report generation produces readable output."""
        results = validator.validate_all_tiers()
        report = validator.generate_report(results)
        
        assert "CORTEX TIER VALIDATION REPORT" in report
        assert "tier0" in report.lower()
        assert "tier1" in report.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
