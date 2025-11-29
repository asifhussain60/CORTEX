"""
Integration tests for CORTEX Tier 0 Governance Engine

Tests the full workflow:
1. Migration from YAML/Markdown to SQLite
2. Rule queries and violation tracking
3. Cross-component integration
"""

import pytest
import tempfile
import yaml
from pathlib import Path
import sys

# Add cortex-brain path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'cortex-brain' / 'left-hemisphere' / 'tier0'))

from governance import GovernanceEngine
from migrate_governance import parse_yaml_rules, parse_markdown_rules


@pytest.fixture
def temp_yaml_file():
    """Create a temporary YAML rulebook for testing."""
    content = """
rules:
  - id: TEST_PHASE_GIT
    tier: 0
    severity: HIGH
    category: version_control
    description: Test git checkpoint rule
    enforcement:
      when: phase_exit
      steps:
        - commit: true
        - push: true
  
  - id: TEST_TDD
    tier: 0
    severity: CRITICAL
    category: testing
    description: Test-driven development enforcement
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(content)
        path = f.name
    
    yield Path(path)
    Path(path).unlink(missing_ok=True)


@pytest.fixture
def temp_md_file():
    """Create a temporary Markdown rules file for testing."""
    content = """
# Governance Rules

## 🎯 Tier 0 Rules (INSTINCT - PERMANENT, CANNOT BE OVERRIDDEN)

- ✅ **Rule #18:** Challenge User Changes
- ✅ **Rule #19:** Checkpoint Strategy
- ✅ **Rule #20:** Definition of DONE

## RULE #1: Test First Development

```yaml
rule_id: TDD_ENFORCEMENT
severity: CRITICAL
scope: ALL_CODE

validation:
  - RED: Write failing test first
  - GREEN: Make test pass
  - REFACTOR: Clean up code
```

## RULE #2: Brain Protection

```yaml
rule_id: BRAIN_PROTECTION
severity: HIGH
scope: BRAIN_OPS

requirements:
  - Schema validation before writes
  - Atomic transactions
  - Backup before migrations
```
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        path = f.name
    
    yield Path(path)
    Path(path).unlink(missing_ok=True)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    Path(db_path).unlink(missing_ok=True)


class TestYAMLMigration:
    """Test YAML to SQLite migration workflow."""
    
    def test_yaml_parsing(self, temp_yaml_file):
        """Test parsing YAML rulebook."""
        rules = parse_yaml_rules(temp_yaml_file)
        
        assert len(rules) == 2
        assert rules[0]['rule_id'] == 'TEST_PHASE_GIT'
        assert rules[0]['severity'] == 'HIGH'
        assert rules[0]['immutable'] is True  # tier 0
    
    def test_yaml_to_database(self, temp_yaml_file, temp_db):
        """Test full YAML migration to database."""
        rules = parse_yaml_rules(temp_yaml_file)
        
        with GovernanceEngine(temp_db) as engine:
            for rule in rules:
                engine.add_rule(rule)
            
            # Verify migration
            all_rules = engine.get_all_rules()
            assert len(all_rules) == 2
            
            # Verify rule details
            rule = engine.get_rule('TEST_PHASE_GIT')
            assert rule is not None
            assert rule['category'] == 'VERSION_CONTROL'


class TestMarkdownMigration:
    """Test Markdown to SQLite migration workflow."""
    
    def test_markdown_parsing(self, temp_md_file):
        """Test parsing Markdown rules."""
        rules = parse_markdown_rules(temp_md_file)
        
        # Should extract Tier 0 rules and numbered rules
        assert len(rules) >= 3  # 3 Tier 0 + 2 numbered
        
        # Check Tier 0 rules
        tier0_rules = [r for r in rules if r['immutable']]
        assert len(tier0_rules) >= 3
    
    def test_markdown_to_database(self, temp_md_file, temp_db):
        """Test full Markdown migration to database."""
        rules = parse_markdown_rules(temp_md_file)
        
        with GovernanceEngine(temp_db) as engine:
            for rule in rules:
                engine.add_rule(rule)
            
            # Verify migration
            all_rules = engine.get_all_rules()
            assert len(all_rules) > 0
            
            # Verify Tier 0 rules are immutable
            critical_rules = engine.get_rules_by_severity('CRITICAL')
            assert len(critical_rules) > 0


class TestEndToEndWorkflow:
    """Test complete governance workflow."""
    
    def test_full_lifecycle(self, temp_yaml_file, temp_db):
        """Test: migrate rules → query → log violations → resolve."""
        # Step 1: Migrate rules
        rules = parse_yaml_rules(temp_yaml_file)
        
        with GovernanceEngine(temp_db) as engine:
            for rule in rules:
                engine.add_rule(rule)
            
            # Step 2: Query rules
            version_control_rules = engine.get_rules_by_category('VERSION_CONTROL')
            assert len(version_control_rules) > 0
            
            # Step 3: Log a violation
            rule_id = version_control_rules[0]['rule_id']
            violation_id = engine.log_violation(
                rule_id=rule_id,
                context='Forgot to commit at phase exit',
                event_id='evt_test_123'
            )
            
            # Step 4: Verify violation logged
            violations = engine.get_violations(rule_id=rule_id)
            assert len(violations) == 1
            assert violations[0]['context'] == 'Forgot to commit at phase exit'
            
            # Step 5: Resolve violation
            engine.resolve_violation(violation_id, 'Created commit manually')
            
            # Step 6: Verify resolution
            resolved_violations = engine.get_violations(resolved=True)
            assert len(resolved_violations) == 1
            
            # Step 7: Check statistics
            stats = engine.get_statistics()
            assert stats['total_rules'] >= 2
            assert stats['total_violations'] == 1
            assert stats['unresolved_violations'] == 0
