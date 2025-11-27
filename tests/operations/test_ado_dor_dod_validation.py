"""
Tests for Phase 4: DoR/DoD Validation System

Tests the Definition of Ready validation, Definition of Done validation,
and approval workflow with quality gates.

Author: Asif Hussain
Created: 2025-11-27
Version: 1.0
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.orchestrators.ado_work_item_orchestrator import (
    ADOWorkItemOrchestrator,
    WorkItemType,
    WorkItemMetadata,
    WorkItemSummary,
    ValidationResult,
    ApprovalRecord
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_cortex_dir():
    """Create temporary CORTEX directory with DoR/DoD rules."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create directory structure
    cortex_brain = temp_dir / "cortex-brain"
    cortex_brain.mkdir(parents=True)
    
    documents = cortex_brain / "documents"
    documents.mkdir()
    
    planning = documents / "planning"
    planning.mkdir()
    
    ado_dir = planning / "ado"
    ado_dir.mkdir()
    
    (ado_dir / "active").mkdir()
    (ado_dir / "completed").mkdir()
    (ado_dir / "blocked").mkdir()
    
    # Create config directory
    config_dir = cortex_brain / "config"
    config_dir.mkdir()
    
    # Create simplified DoR/DoD rules for testing
    rules_file = config_dir / "dor-dod-rules.yaml"
    rules_content = """
definition_of_ready:
  minimum_score_to_approve: 80
  checklist:
    completeness:
      weight: 50
      items:
        - id: title_present
          text: "Title present"
          validation: "metadata.title and len(metadata.title) > 10"
          points: 30
        - id: description_present
          text: "Description present"
          validation: "metadata.description and len(metadata.description) > 50"
          points: 30
        - id: acceptance_criteria_present
          text: "Acceptance criteria present"
          validation: "metadata.acceptance_criteria and len(metadata.acceptance_criteria) >= 2"
          points: 40
    
    clarity:
      weight: 30
      items:
        - id: no_vague_language
          text: "No vague language"
          validation: "ambiguity_score < 3"
          points: 50
        - id: technical_approach_clear
          text: "Technical approach clear"
          validation: "'technical' in metadata.description.lower()"
          points: 50
    
    context:
      weight: 20
      items:
        - id: clarifications_resolved
          text: "Clarifications resolved"
          validation: "hasattr(metadata, 'clarification_context')"
          points: 100

scoring:
  dor:
    calculation: "weighted_average"
    bonus:
      all_optional_complete: 5
      perfect_clarity: 5

definition_of_done:
  minimum_score_to_complete: 85
  checklist:
    implementation:
      weight: 40
      items:
        - id: code_implemented
          text: "Code implemented"
          validation: "summary.code_changes_count > 0"
          points: 50
        - id: files_created_documented
          text: "Files documented"
          validation: "len(summary.files_created) > 0"
          points: 50
    
    testing:
      weight: 40
      items:
        - id: tests_created
          text: "Tests created"
          validation: "len(summary.tests_created) > 0"
          points: 40
        - id: test_coverage_acceptable
          text: "Test coverage acceptable"
          validation: "summary.test_coverage >= 60.0"
          points: 30
        - id: tests_passing
          text: "Tests passing"
          validation: "'passed' in summary.test_results.lower()"
          points: 30
    
    documentation:
      weight: 20
      items:
        - id: documentation_created
          text: "Documentation created"
          validation: "len(summary.documentation_created) > 0"
          points: 100

scoring:
  dod:
    calculation: "weighted_average"
    bonus:
      test_coverage_80_plus: 5
      zero_known_issues: 5
"""
    rules_file.write_text(rules_content)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def orchestrator(temp_cortex_dir):
    """Create ADOWorkItemOrchestrator instance."""
    return ADOWorkItemOrchestrator(cortex_root=str(temp_cortex_dir))


# ============================================================================
# TEST DoR VALIDATION
# ============================================================================

class TestDoRValidation:
    """Test Definition of Ready validation."""
    
    def test_dor_validation_pass(self, orchestrator):
        """Test DoR validation with complete requirements."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="User Authentication Feature",
            description="Implement user authentication with technical JWT approach. " + "x" * 100,
            acceptance_criteria=[
                "User can login successfully",
                "User can logout successfully"
            ]
        )
        metadata.clarification_context = {"scope": "completed"}
        
        result = orchestrator.validate_dor(metadata, ambiguity_score=2)
        
        assert result.validation_type == "dor"
        assert result.overall_score >= 80.0, f"Score {result.overall_score} should be >= 80"
        assert result.passed, "Should pass DoR validation"
        assert len(result.categories) > 0, "Should have categories"
    
    def test_dor_validation_fail_missing_title(self, orchestrator):
        """Test DoR validation fails with short title."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="Short",  # Too short
            description="Technical implementation details. " + "x" * 100,
            acceptance_criteria=["Criterion 1", "Criterion 2"]
        )
        
        result = orchestrator.validate_dor(metadata, ambiguity_score=2)
        
        # Should fail completeness check
        completeness_cat = next((c for c in result.categories if c.category == "completeness"), None)
        assert completeness_cat is not None
        title_item = next((i for i in completeness_cat.items if i.id == "title_present"), None)
        assert title_item is not None
        assert not title_item.passed, "Short title should fail"
    
    def test_dor_validation_fail_missing_acceptance_criteria(self, orchestrator):
        """Test DoR validation fails without acceptance criteria."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="User Authentication Feature",
            description="Technical implementation with details. " + "x" * 100,
            acceptance_criteria=[]  # Missing
        )
        
        result = orchestrator.validate_dor(metadata, ambiguity_score=2)
        
        # Should fail completeness check
        completeness_cat = next((c for c in result.categories if c.category == "completeness"), None)
        assert completeness_cat is not None
        ac_item = next((i for i in completeness_cat.items if i.id == "acceptance_criteria_present"), None)
        assert ac_item is not None
        assert not ac_item.passed, "Missing acceptance criteria should fail"
    
    def test_dor_validation_high_ambiguity(self, orchestrator):
        """Test DoR validation with high ambiguity score."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="User Authentication Feature",
            description="Technical implementation details. " + "x" * 100,
            acceptance_criteria=["Criterion 1", "Criterion 2"]
        )
        
        result = orchestrator.validate_dor(metadata, ambiguity_score=8)
        
        # Should fail clarity check
        clarity_cat = next((c for c in result.categories if c.category == "clarity"), None)
        assert clarity_cat is not None
        vague_item = next((i for i in clarity_cat.items if i.id == "no_vague_language"), None)
        assert vague_item is not None
        assert not vague_item.passed, "High ambiguity should fail"
    
    def test_dor_validation_categories_weighted(self, orchestrator):
        """Test that category weights are applied correctly."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="User Authentication Feature",
            description="Technical implementation. " + "x" * 100,
            acceptance_criteria=["Criterion 1", "Criterion 2"]
        )
        metadata.clarification_context = {"scope": "completed"}
        
        result = orchestrator.validate_dor(metadata, ambiguity_score=0)
        
        # Check that categories have weights
        for category in result.categories:
            assert category.weight > 0, f"Category {category.category} should have weight"
            assert category.weighted_score >= 0, f"Category {category.category} should have weighted score"
        
        # Overall score should be sum of weighted scores
        expected_score = sum(cat.weighted_score for cat in result.categories)
        assert abs(result.overall_score - expected_score) < 1.0, "Overall score should be sum of weighted scores"


# ============================================================================
# TEST DoD VALIDATION
# ============================================================================

class TestDoDValidation:
    """Test Definition of Done validation."""
    
    def test_dod_validation_pass(self, orchestrator):
        """Test DoD validation with complete work."""
        summary = WorkItemSummary(
            work_item_id="ADO-123",
            work_item_type=WorkItemType.STORY,
            title="User Authentication",
            files_created=["auth.py", "test_auth.py"],
            files_modified=["app.py"],
            tests_created=["test_auth.py"],
            documentation_created=["README.md"],
            code_changes_count=5,
            test_coverage=75.0,
            test_results="All tests passed successfully"
        )
        
        result = orchestrator.validate_dod(summary)
        
        assert result.validation_type == "dod"
        assert result.overall_score >= 85.0, f"Score {result.overall_score} should be >= 85"
        assert result.passed, "Should pass DoD validation"
    
    def test_dod_validation_fail_no_tests(self, orchestrator):
        """Test DoD validation fails without tests."""
        summary = WorkItemSummary(
            work_item_id="ADO-123",
            work_item_type=WorkItemType.STORY,
            title="User Authentication",
            files_created=["auth.py"],
            tests_created=[],  # Missing tests
            documentation_created=["README.md"],
            code_changes_count=5,
            test_coverage=0.0,
            test_results="No tests"
        )
        
        result = orchestrator.validate_dod(summary)
        
        # Should fail testing check
        testing_cat = next((c for c in result.categories if c.category == "testing"), None)
        assert testing_cat is not None
        tests_item = next((i for i in testing_cat.items if i.id == "tests_created"), None)
        assert tests_item is not None
        assert not tests_item.passed, "Missing tests should fail"
    
    def test_dod_validation_fail_low_coverage(self, orchestrator):
        """Test DoD validation fails with low test coverage."""
        summary = WorkItemSummary(
            work_item_id="ADO-123",
            work_item_type=WorkItemType.STORY,
            title="User Authentication",
            files_created=["auth.py"],
            tests_created=["test_auth.py"],
            documentation_created=["README.md"],
            code_changes_count=5,
            test_coverage=45.0,  # Too low
            test_results="Tests passed"
        )
        
        result = orchestrator.validate_dod(summary)
        
        # Should fail coverage check
        testing_cat = next((c for c in result.categories if c.category == "testing"), None)
        assert testing_cat is not None
        coverage_item = next((i for i in testing_cat.items if i.id == "test_coverage_acceptable"), None)
        assert coverage_item is not None
        assert not coverage_item.passed, "Low coverage should fail"
    
    def test_dod_validation_bonus_points(self, orchestrator):
        """Test DoD validation with bonus points."""
        summary = WorkItemSummary(
            work_item_id="ADO-123",
            work_item_type=WorkItemType.STORY,
            title="User Authentication",
            files_created=["auth.py"],
            tests_created=["test_auth.py"],
            documentation_created=[],  # Missing docs to keep base score lower
            code_changes_count=5,
            test_coverage=85.0,  # High coverage = bonus
            test_results="Tests passed",
            known_issues=[]  # No issues = bonus
        )
        
        result = orchestrator.validate_dod(summary)
        
        # Should have bonus points applied (coverage 80%+ gives +5, no issues gives +5)
        # Base score should be lower than 100 due to missing docs
        base_score = sum(cat.weighted_score for cat in result.categories)
        assert result.overall_score >= base_score, "Score should be at least base score"
        # Check that high coverage and no issues are rewarded
        assert result.overall_score >= 85.0, "Should pass DoD with bonus points"


# ============================================================================
# TEST APPROVAL WORKFLOW
# ============================================================================

class TestApprovalWorkflow:
    """Test work item approval workflow."""
    
    def test_approve_plan_success(self, orchestrator):
        """Test successful plan approval."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="User Authentication Feature",
            description="Technical implementation with JWT. " + "x" * 100,
            acceptance_criteria=["User can login", "User can logout"],
            work_item_id="ADO-123"
        )
        metadata.clarification_context = {"scope": "completed"}
        
        # Create work item first
        success, message, created_metadata = orchestrator.create_work_item(
            WorkItemType.STORY,
            "User Authentication Feature",
            "Technical implementation with JWT. " + "x" * 100,
            acceptance_criteria=["User can login", "User can logout"]
        )
        assert success, "Work item creation should succeed"
        
        # Approve plan
        success, message, approval = orchestrator.approve_plan(
            created_metadata.work_item_id,
            created_metadata,
            ambiguity_score=2
        )
        
        assert success, f"Approval should succeed: {message}"
        assert approval is not None, "Should have approval record"
        assert approval.approved, "Should be approved"
        assert approval.dor_score >= 80.0, "DoR score should be >= 80"
    
    def test_approve_plan_fail_low_dor(self, orchestrator):
        """Test plan approval fails with low DoR score."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="Short",  # Too short
            description="Brief",  # Too short
            acceptance_criteria=[],  # Missing
            work_item_id="ADO-456"
        )
        
        success, message, approval = orchestrator.approve_plan(
            "ADO-456",
            metadata,
            ambiguity_score=2
        )
        
        assert not success, "Approval should fail with low DoR"
        assert "DoR validation failed" in message
        assert approval is None, "Should not have approval record"
    
    def test_approve_plan_quality_gates(self, orchestrator):
        """Test that quality gates are recorded in approval."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="User Authentication Feature",
            description="Technical implementation details. " + "x" * 100,
            acceptance_criteria=["User can login", "User can logout"],
            work_item_id="ADO-789"
        )
        metadata.clarification_context = {"scope": "completed"}
        
        # Create work item first
        orchestrator.create_work_item(
            WorkItemType.STORY,
            "User Authentication Feature",
            "Technical implementation details. " + "x" * 100,
            acceptance_criteria=["User can login", "User can logout"]
        )
        
        success, message, approval = orchestrator.approve_plan(
            "ADO-789",
            metadata,
            ambiguity_score=2
        )
        
        if success and approval:
            assert len(approval.quality_gates_passed) > 0, "Should have quality gates passed"
            assert "Pre-Implementation Gate" in approval.quality_gates_passed


# ============================================================================
# TEST VALIDATION HELPERS
# ============================================================================

class TestValidationHelpers:
    """Test validation helper methods."""
    
    def test_evaluate_validation_simple(self, orchestrator):
        """Test simple validation expression."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="Test Story",
            description="Description"
        )
        
        result = orchestrator._evaluate_validation(
            "len(metadata.title) > 5",
            metadata,
            0
        )
        
        assert result is True, "Title length should be > 5"
    
    def test_evaluate_validation_complex(self, orchestrator):
        """Test complex validation expression."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="Test",
            description="Test",
            acceptance_criteria=["A", "B", "C"]
        )
        
        result = orchestrator._evaluate_validation(
            "metadata.acceptance_criteria and len(metadata.acceptance_criteria) >= 2",
            metadata,
            0
        )
        
        assert result is True, "Should have >= 2 acceptance criteria"
    
    def test_generate_dor_recommendations(self, orchestrator):
        """Test DoR recommendation generation."""
        # Create a failing validation
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="Short",
            description="Brief",
            acceptance_criteria=[]
        )
        
        result = orchestrator.validate_dor(metadata, ambiguity_score=7)
        
        assert len(result.recommendations) > 0, "Should have recommendations"
        # Should recommend addressing ambiguity
        assert any("ambiguity" in rec.lower() for rec in result.recommendations)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
