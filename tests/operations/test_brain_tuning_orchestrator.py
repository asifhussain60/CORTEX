"""
Test Brain Tuning Orchestrator

Validates brain health diagnosis and optimization across all 4 tiers.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.operations.modules.brain.brain_tuning_orchestrator import BrainTuningOrchestrator


def test_brain_tuning_orchestrator_init():
    """Test orchestrator initialization."""
    project_root = Path.cwd()
    tuner = BrainTuningOrchestrator(project_root)
    
    assert tuner.project_root == project_root
    assert tuner.brain_path == project_root / "cortex-brain"
    assert tuner.tier1_db == project_root / "cortex-brain" / "tier1" / "working_memory.db"
    assert tuner.tier2_db == project_root / "cortex-brain" / "tier2" / "knowledge_graph.db"
    assert tuner.tier3_db == project_root / "cortex-brain" / "tier3" / "development_context.db"
    assert tuner.knowledge_yaml == project_root / "cortex-brain" / "knowledge-graph.yaml"


def test_brain_diagnosis():
    """Test brain health diagnosis."""
    project_root = Path.cwd()
    tuner = BrainTuningOrchestrator(project_root)
    
    diagnosis = tuner._diagnose_brain_health()
    
    assert 'tier0' in diagnosis
    assert 'tier1' in diagnosis
    assert 'tier2' in diagnosis
    assert 'tier3' in diagnosis
    assert 'overall_health_score' in diagnosis
    
    # Each tier should have health_score
    assert 'health_score' in diagnosis['tier0']
    assert 'health_score' in diagnosis['tier1']
    assert 'health_score' in diagnosis['tier2']
    assert 'health_score' in diagnosis['tier3']
    
    # Overall score should be between 0-100
    assert 0 <= diagnosis['overall_health_score'] <= 100


def test_tier0_governance_check():
    """Test Tier 0 governance health check."""
    project_root = Path.cwd()
    tuner = BrainTuningOrchestrator(project_root)
    
    tier0_health = tuner._check_tier0_governance()
    
    assert 'health_score' in tier0_health
    assert 'status' in tier0_health
    assert 'issues' in tier0_health
    
    # Should have protection rules file
    protection_rules = project_root / "cortex-brain" / "brain-protection-rules.yaml"
    if protection_rules.exists():
        assert tier0_health['health_score'] >= 80
        assert tier0_health['status'] in ['excellent', 'good']


def test_tier1_working_memory_check():
    """Test Tier 1 working memory health check."""
    project_root = Path.cwd()
    tuner = BrainTuningOrchestrator(project_root)
    
    tier1_health = tuner._check_tier1_working_memory()
    
    assert 'health_score' in tier1_health
    assert 'status' in tier1_health
    assert 'conversations' in tier1_health
    assert 'messages' in tier1_health
    assert 'entities' in tier1_health
    
    # Health score should be valid
    assert 0 <= tier1_health['health_score'] <= 100


def test_tier2_knowledge_graph_check():
    """Test Tier 2 knowledge graph health check."""
    project_root = Path.cwd()
    tuner = BrainTuningOrchestrator(project_root)
    
    tier2_health = tuner._check_tier2_knowledge_graph()
    
    assert 'health_score' in tier2_health
    assert 'status' in tier2_health
    assert 'sqlite_patterns' in tier2_health
    assert 'yaml_patterns' in tier2_health
    
    # Should detect migration need if YAML > SQLite
    if tier2_health['yaml_patterns'] > tier2_health['sqlite_patterns']:
        assert tier2_health['status'] == 'needs_migration'
        assert any('migration' in issue.lower() for issue in tier2_health['issues'])


def test_tier3_dev_context_check():
    """Test Tier 3 development context health check."""
    project_root = Path.cwd()
    tuner = BrainTuningOrchestrator(project_root)
    
    tier3_health = tuner._check_tier3_dev_context()
    
    assert 'health_score' in tier3_health
    assert 'status' in tier3_health
    assert 'git_metrics' in tier3_health
    assert 'file_hotspots' in tier3_health
    assert 'copilot_metrics' in tier3_health
    
    # Health score should be valid
    assert 0 <= tier3_health['health_score'] <= 100


def test_yaml_to_sqlite_migration_dry_run():
    """Test YAML to SQLite migration logic (dry run)."""
    project_root = Path.cwd()
    tuner = BrainTuningOrchestrator(project_root)
    
    # Get diagnosis to check current state
    diagnosis = tuner._diagnose_brain_health()
    
    yaml_patterns = diagnosis['tier2']['yaml_patterns']
    sqlite_patterns = diagnosis['tier2']['sqlite_patterns']
    
    # If YAML has patterns, migration should be possible
    if yaml_patterns > 0:
        assert tuner.knowledge_yaml.exists()


def test_metrics_tracking():
    """Test that metrics are properly tracked."""
    project_root = Path.cwd()
    tuner = BrainTuningOrchestrator(project_root)
    
    # Check initial metrics structure
    assert 'patterns_migrated' in tuner.metrics
    assert 'patterns_pruned' in tuner.metrics
    assert 'entities_validated' in tuner.metrics
    assert 'conversations_active' in tuner.metrics
    assert 'indexes_rebuilt' in tuner.metrics
    assert 'space_reclaimed_kb' in tuner.metrics
    assert 'issues_fixed' in tuner.metrics
    assert 'warnings' in tuner.metrics
    assert 'errors' in tuner.metrics
    
    # All should be initialized
    assert tuner.metrics['patterns_migrated'] == 0
    assert tuner.metrics['patterns_pruned'] == 0
    assert tuner.metrics['space_reclaimed_kb'] == 0


def test_brain_tuning_full_execution():
    """
    Test full brain tuning execution.
    
    This is an integration test that runs the full workflow.
    """
    project_root = Path.cwd()
    tuner = BrainTuningOrchestrator(project_root)
    
    result = tuner.execute()
    
    # Should return valid result
    assert 'success' in result
    assert 'duration_seconds' in result
    assert 'metrics' in result
    
    # If successful, should have health report
    if result['success']:
        assert 'health_report' in result
        assert 'diagnosis' in result
        
        # Metrics should be populated
        metrics = result['metrics']
        assert isinstance(metrics, dict)
        assert 'patterns_migrated' in metrics
        assert 'issues_fixed' in metrics


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])
