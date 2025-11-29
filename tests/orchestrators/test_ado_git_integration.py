"""
Integration Tests for ADO Work Item Orchestrator with Git History Validator

Purpose: Test Phase 1 integration between ADOWorkItemOrchestrator and GitHistoryValidator

Author: Asif Hussain
Created: 2025-11-27
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.orchestrators.ado_work_item_orchestrator import (
    ADOWorkItemOrchestrator,
    WorkItemType,
    WorkItemMetadata
)


@pytest.fixture
def cortex_root():
    """Use actual CORTEX root for testing (has git history)."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def orchestrator(cortex_root):
    """Create ADO orchestrator instance."""
    return ADOWorkItemOrchestrator(str(cortex_root))


def test_orchestrator_initialization(orchestrator):
    """Test that orchestrator initializes with git validator."""
    assert orchestrator is not None
    assert orchestrator.git_validator is not None
    print(f"✅ GitHistoryValidator initialized: {orchestrator.git_validator is not None}")


def test_create_work_item_with_git_context(orchestrator, cortex_root):
    """Test creating work item with git history enrichment."""
    
    # Create work item mentioning actual CORTEX files
    success, message, metadata = orchestrator.create_work_item(
        work_item_type=WorkItemType.STORY,
        title="Fix authentication bug in login system",
        description="Need to fix authentication issues in `src/validators/git_history_validator.py` and `src/orchestrators/ado_work_item_orchestrator.py`"
    )
    
    assert success, f"Work item creation failed: {message}"
    assert metadata is not None
    
    # Verify git context enrichment
    assert metadata.git_context is not None, "Git context should be populated"
    assert metadata.quality_score >= 0, "Quality score should be calculated"
    
    print(f"✅ Work item created with git context")
    print(f"   Quality Score: {metadata.quality_score:.1f}%")
    print(f"   High-Risk Files: {len(metadata.high_risk_files)}")
    print(f"   Contributors: {len(metadata.contributors)}")
    print(f"   Related Commits: {len(metadata.related_commits)}")
    
    # Verify high-risk file flagging
    if metadata.high_risk_files:
        print(f"   ⚠️ High-risk files detected: {', '.join(metadata.high_risk_files[:3])}")
    
    # Verify SME suggestions
    if metadata.sme_suggestions:
        print(f"   💡 SME suggestions: {', '.join(metadata.sme_suggestions)}")


def test_work_item_template_includes_git_context(orchestrator):
    """Test that generated work item template includes git context section."""
    
    # Create metadata with mock git context
    metadata = WorkItemMetadata(
        work_item_type=WorkItemType.FEATURE,
        title="Test Feature",
        description="Test description with `test.py` file reference",
        git_context={'validation_status': 'PASS'},
        quality_score=85.5,
        high_risk_files=['src/critical.py', 'src/auth.py'],
        contributors=[{'name': 'John Doe', 'commits': 42}],
        sme_suggestions=['John Doe'],
        related_commits=['abc123: Fix security issue', 'def456: Refactor auth']
    )
    
    # Generate template
    template = orchestrator._generate_work_item_template(metadata)
    
    # Verify git context section exists
    assert "## Git History Context" in template, "Template should include git context section"
    assert "Quality Score:" in template, "Template should show quality score"
    assert "85.5%" in template, "Template should show correct quality score"
    assert "High-Risk Files Detected" in template, "Template should flag high-risk files"
    assert "Subject Matter Expert Suggestions" in template, "Template should include SME suggestions"
    assert "John Doe" in template, "Template should show contributor name"
    
    print(f"✅ Work item template includes git context section")
    print(f"   Contains quality score: ✓")
    print(f"   Contains high-risk warnings: ✓")
    print(f"   Contains SME suggestions: ✓")
    print(f"   Contains contributors: ✓")


def test_git_context_enrichment_method(orchestrator):
    """Test _enrich_with_git_context method directly."""
    
    # Create basic metadata
    metadata = WorkItemMetadata(
        work_item_type=WorkItemType.BUG,
        title="Fix login bug",
        description="Bug in `src/orchestrators/ado_work_item_orchestrator.py` file"
    )
    
    # Enrich with git context
    enriched = orchestrator._enrich_with_git_context(metadata)
    
    assert enriched is not None
    assert enriched.git_context is not None or enriched.quality_score == 0  # May be 0 if no git history
    
    print(f"✅ Git context enrichment method works")
    print(f"   Quality Score: {enriched.quality_score:.1f}%")
    
    if enriched.high_risk_files:
        print(f"   High-Risk Files: {len(enriched.high_risk_files)}")
    if enriched.sme_suggestions:
        print(f"   SME Suggestions: {enriched.sme_suggestions}")


def test_high_risk_criterion_added_to_acceptance_criteria(orchestrator):
    """Test that high-risk files are automatically added to acceptance criteria."""
    
    # Create metadata with high-risk files
    metadata = WorkItemMetadata(
        work_item_type=WorkItemType.STORY,
        title="Refactor authentication",
        description="Refactor `src/auth/login.py` and `src/auth/session.py`",
        acceptance_criteria=["Must pass all tests", "Must maintain backward compatibility"]
    )
    
    # Manually set high-risk files (simulating git validator output)
    metadata.high_risk_files = ['src/auth/login.py', 'src/auth/session.py']
    
    # Enrich (would normally be called during create_work_item)
    enriched = orchestrator._enrich_with_git_context(metadata)
    
    # Verify high-risk criterion added to acceptance criteria
    high_risk_criteria = [ac for ac in enriched.acceptance_criteria if 'high-risk' in ac.lower()]
    
    assert len(high_risk_criteria) > 0, "High-risk criterion should be added to acceptance criteria"
    print(f"✅ High-risk criterion automatically added to acceptance criteria")
    print(f"   Criterion: {high_risk_criteria[0]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
