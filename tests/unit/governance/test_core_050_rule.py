"""
Unit Tests for CORE-050: No Quality Degradation

Tests enforcement of quality standards and infrastructure checks.

AC-ID: PHASE-51-S1-001
"""

import pytest
from pathlib import Path
import yaml
from typing import Dict, Any


@pytest.fixture
def core_rules_path() -> Path:
    """Get path to core-rules.yaml."""
    return Path("cortex-registry/_cortex-master/governance/core-rules.yaml")


@pytest.fixture
def core_rules_data(core_rules_path: Path) -> Dict[str, Any]:
    """Load core-rules.yaml data."""
    with open(core_rules_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


class TestCORE050Exists:
    """Test that CORE-050 rule exists in core-rules.yaml."""
    
    def test_core_050_rule_exists(self, core_rules_data: Dict[str, Any]):
        """Test CORE-050 exists in core_rules section."""
        core_rules = core_rules_data.get('core_rules', [])
        rule_ids = [rule['id'] for rule in core_rules]
        
        assert 'CORE-050' in rule_ids, "CORE-050 rule not found in core_rules"
    
    def test_core_050_has_required_fields(self, core_rules_data: Dict[str, Any]):
        """Test CORE-050 has all required fields."""
        core_rules = core_rules_data.get('core_rules', [])
        core_050 = next((r for r in core_rules if r['id'] == 'CORE-050'), None)
        
        assert core_050 is not None, "CORE-050 not found"
        
        required_fields = ['id', 'name', 'category', 'priority', 'description', 'enforcement']
        for field in required_fields:
            assert field in core_050, f"CORE-050 missing required field: {field}"
            assert core_050[field], f"CORE-050 field '{field}' is empty"


class TestCORE050Severity:
    """Test that CORE-050 has P0 severity."""
    
    def test_core_050_priority_is_p0(self, core_rules_data: Dict[str, Any]):
        """Test CORE-050 priority is P0."""
        core_rules = core_rules_data.get('core_rules', [])
        core_050 = next((r for r in core_rules if r['id'] == 'CORE-050'), None)
        
        assert core_050 is not None, "CORE-050 not found"
        assert core_050['priority'] == 'P0', f"Expected P0, got {core_050['priority']}"
    
    def test_core_050_enforcement_is_blocking(self, core_rules_data: Dict[str, Any]):
        """Test CORE-050 enforcement level is BLOCKED."""
        core_rules = core_rules_data.get('core_rules', [])
        core_050 = next((r for r in core_rules if r['id'] == 'CORE-050'), None)
        
        assert core_050 is not None, "CORE-050 not found"
        assert core_050['enforcement'] == 'BLOCKED', \
            f"Expected BLOCKED, got {core_050['enforcement']}"
    
    def test_core_050_in_blocked_enforcement_list(self, core_rules_data: Dict[str, Any]):
        """Test CORE-050 listed in BLOCKED enforcement matrix."""
        enforcement_levels = core_rules_data.get('enforcement_levels', {})
        blocked = enforcement_levels.get('BLOCKED', {})
        blocked_rules = blocked.get('rules', [])
        
        assert 'CORE-050' in blocked_rules, \
            "CORE-050 not in BLOCKED enforcement list"


class TestCORE050Content:
    """Test CORE-050 content and policy."""
    
    def test_core_050_name(self, core_rules_data: Dict[str, Any]):
        """Test CORE-050 name is 'No Quality Degradation'."""
        core_rules = core_rules_data.get('core_rules', [])
        core_050 = next((r for r in core_rules if r['id'] == 'CORE-050'), None)
        
        assert core_050 is not None, "CORE-050 not found"
        assert core_050['name'] == 'No Quality Degradation', \
            f"Expected 'No Quality Degradation', got '{core_050['name']}'"
    
    def test_core_050_has_policy_statement(self, core_rules_data: Dict[str, Any]):
        """Test CORE-050 includes 'Fix infrastructure, don't bypass' policy."""
        core_rules = core_rules_data.get('core_rules', [])
        core_050 = next((r for r in core_rules if r['id'] == 'CORE-050'), None)
        
        assert core_050 is not None, "CORE-050 not found"
        description = core_050.get('description', '').lower()
        
        # Check for key policy phrases
        assert any(phrase in description for phrase in [
            'fix infrastructure',
            'don\'t bypass',
            'no degradation',
            'production standards'
        ]), "CORE-050 missing key policy statement"
    
    def test_core_050_category(self, core_rules_data: Dict[str, Any]):
        """Test CORE-050 category is 'governance'."""
        core_rules = core_rules_data.get('core_rules', [])
        core_050 = next((r for r in core_rules if r['id'] == 'CORE-050'), None)
        
        assert core_050 is not None, "CORE-050 not found"
        assert core_050['category'] == 'governance', \
            f"Expected 'governance', got '{core_050['category']}'"
    
    def test_core_050_has_violation_action(self, core_rules_data: Dict[str, Any]):
        """Test CORE-050 specifies violation action."""
        core_rules = core_rules_data.get('core_rules', [])
        core_050 = next((r for r in core_rules if r['id'] == 'CORE-050'), None)
        
        assert core_050 is not None, "CORE-050 not found"
        assert 'violation_action' in core_050, "CORE-050 missing violation_action"
        assert 'block' in core_050['violation_action'].lower(), \
            "CORE-050 should specify blocking behavior"
