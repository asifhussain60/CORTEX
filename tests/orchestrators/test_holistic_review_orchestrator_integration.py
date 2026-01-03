"""
Integration Tests for HolisticReviewOrchestrator.

Tests end-to-end execution of holistic reviews including artifact gathering,
pattern extraction, recommendation generation, and document creation.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.orchestrators.holistic_review_orchestrator import HolisticReviewOrchestrator
from src.database.planning_state_db import PlanningStateDB
from src.orchestrators.base.base_orchestrator_v4_1 import OrchestratorStatus


class TestHolisticReviewOrchestratorIntegration:
    """Integration tests for HolisticReviewOrchestrator."""
    
    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create temporary workspace with sample artifacts."""
        # Create parent plan structure
        parent_plan_dir = tmp_path / "cortex-brain" / "documents" / "planning" / "active" / "test-migration"
        parent_plan_dir.mkdir(parents=True)
        
        # Create tracking directory
        tracking_dir = parent_plan_dir / "tracking"
        tracking_dir.mkdir()
        
        # Create progress.json
        progress_data = {
            "plan_id": "test-migration",
            "progress": {
                "current_phase": 1,
                "overall_percent": 30
            },
            "holistic_reviews": {
                "enabled": True,
                "auto_trigger": True,
                "schedule": [
                    {
                        "review_number": 1,
                        "name": "Test Review",
                        "status": "not_started",
                        "trigger_condition": "phase_0_complete",
                        "document": "architecture/holistic-review-01.md",
                        "scope": "design"
                    }
                ]
            }
        }
        
        with open(tracking_dir / "progress.json", 'w') as f:
            json.dump(progress_data, f, indent=2)
        
        # Create architecture directory
        arch_dir = parent_plan_dir / "architecture"
        arch_dir.mkdir()
        
        # Create sibling migration directories
        for sibling in ['ado-v2-migration', 'cleanup-v2-migration', 'vacuum-v2-migration']:
            sibling_dir = tmp_path / "cortex-brain" / "documents" / "planning" / "active" / sibling
            sibling_dir.mkdir(parents=True)
            
            reports_dir = sibling_dir / "reports"
            reports_dir.mkdir()
            
            # Create sample completion report
            report_content = f"""# {sibling} Completion Report

## Architecture
- Engine-based modular design
- 4-5 specialized engines
- BaseOrchestrator v4.1 compliance

## Test Coverage
- 95%+ coverage achieved
- Unit + integration + e2e tests

## Lessons Learned
- Modular architecture improves maintainability
- Progressive analysis optimizes performance
"""
            with open(reports_dir / "completion-report.md", 'w') as f:
                f.write(report_content)
        
        return tmp_path
    
    @pytest.fixture
    def mock_config(self, tmp_path):
        """Create mock configuration file."""
        config_dir = tmp_path / "cortex-brain" / "manifests" / "orchestrators"
        config_dir.mkdir(parents=True)
        
        config_file = config_dir / "holistic-review-orchestrator.yaml"
        
        config_data = """
orchestrator:
  id: "holistic_review_orchestrator"
  name: "Holistic Review Orchestrator"
  version: "1.0.0"

execution:
  mode: "autonomous"
  execution_time_target: "45s"

phases:
  - name: "GATHER"
    execution_order: 1
  - name: "ANALYZE"
    execution_order: 2
  - name: "RECOMMEND"
    execution_order: 3
  - name: "DOCUMENT"
    execution_order: 4
  - name: "INJECT"
    execution_order: 5

scopes:
  design:
    description: "Pre-design architectural review"
  code_reuse_strategy:
    description: "Pre-implementation code reuse analysis"
"""
        
        with open(config_file, 'w') as f:
            f.write(config_data)
        
        return str(config_file)
    
    @pytest.fixture
    def mock_state_db(self, tmp_path):
        """Create mock state database."""
        db_path = tmp_path / "cortex-brain" / "database" / "planning_state.db"
        db_path.parent.mkdir(parents=True)
        
        # Use real database for integration testing
        state_db = PlanningStateDB(str(db_path))
        return state_db
    
    def test_execute_complete_workflow(self, temp_workspace, mock_config, mock_state_db, monkeypatch):
        """Test complete holistic review workflow from start to finish."""
        # Monkey-patch Path for artifact discovery
        def path_side_effect(path_str):
            if 'cortex-brain/documents' in str(path_str):
                return temp_workspace / path_str
            return Path(path_str)
        
        monkeypatch.setattr('pathlib.Path.__new__', lambda cls, *args: path_side_effect(args[0]) if args else Path())
        
        # Create orchestrator
        orchestrator = HolisticReviewOrchestrator(
            config_path=mock_config,
            state_db=mock_state_db
        )
        
        # Execute review
        result = orchestrator.execute(
            parent_plan_id="test-migration",
            review_number=1,
            review_name="Test Review",
            document_path="architecture/holistic-review-01.md",
            scope="design",
            completed_phases=[0]
        )
        
        # Verify result
        assert result.status == OrchestratorStatus.SUCCESS
        assert 'insights' in result.metadata
        assert 'patterns' in result.metadata
        assert 'recommendations' in result.metadata
        
        # Verify insights generated
        insights = result.metadata['insights']
        assert len(insights) > 0
        
        # Verify document created
        doc_path = temp_workspace / "cortex-brain" / "documents" / "planning" / "active" / "test-migration" / "architecture" / "holistic-review-01.md"
        assert doc_path.exists()
        
        # Read document and verify content
        with open(doc_path, 'r') as f:
            content = f.read()
        
        assert "# Holistic Review #1" in content
        assert "## 📊 Executive Summary" in content
        assert "## 🗂️ Artifacts Analyzed" in content
        assert "## 🎯 Patterns Extracted" in content
        assert "## 🚀 Recommendations" in content
    
    def test_gather_phase_collects_artifacts(self, temp_workspace, mock_config, mock_state_db):
        """Test that GATHER phase collects artifacts from all sources."""
        orchestrator = HolisticReviewOrchestrator(
            config_path=mock_config,
            state_db=mock_state_db
        )
        
        # Execute only GATHER phase
        gather_result = orchestrator._phase_gather(
            parent_plan_id="test-migration",
            completed_phases=[0],
            scope="design"
        )
        
        from src.orchestrators.base.base_orchestrator_v4_1 import PhaseStatus
        assert gather_result.status == PhaseStatus.SUCCESS
        
        # Verify artifacts were gathered
        assert len(orchestrator.artifacts_gathered) > 0
        
        # Check for expected artifact types
        artifact_types = [artifact['type'] for artifact in orchestrator.artifacts_gathered]
        assert 'progress_tracking' in artifact_types
        # May or may not have sibling_migration_report depending on setup
    
    def test_analyze_phase_extracts_patterns(self, temp_workspace, mock_config, mock_state_db):
        """Test that ANALYZE phase extracts architectural patterns."""
        orchestrator = HolisticReviewOrchestrator(
            config_path=mock_config,
            state_db=mock_state_db
        )
        
        # Manually populate artifacts_gathered
        orchestrator.artifacts_gathered = [
            {
                'type': 'progress_tracking',
                'source': 'test-migration/tracking/progress.json'
            },
            {
                'type': 'sibling_migration_report',
                'migration': 'Cleanup v2',
                'source': 'cleanup-v2-migration/reports/completion-report.md'
            }
        ]
        
        # Execute ANALYZE phase
        analyze_result = orchestrator._phase_analyze(
            artifacts_gathered=orchestrator.artifacts_gathered,
            scope="design"
        )
        
        from src.orchestrators.base.base_orchestrator_v4_1 import PhaseStatus
        assert analyze_result.status == PhaseStatus.SUCCESS
        
        # Verify patterns were extracted
        assert len(orchestrator.patterns_extracted) > 0
        
        # Check for expected patterns
        pattern_names = [pattern['name'] for pattern in orchestrator.patterns_extracted]
        assert 'Engine-Based Modular Architecture' in pattern_names
        assert 'BaseOrchestrator v4.1 Compliance' in pattern_names
    
    def test_recommend_phase_generates_recommendations(self, mock_config, mock_state_db):
        """Test that RECOMMEND phase generates actionable recommendations."""
        orchestrator = HolisticReviewOrchestrator(
            config_path=mock_config,
            state_db=mock_state_db
        )
        
        # Manually populate patterns
        orchestrator.patterns_extracted = [
            {
                'name': 'Engine-Based Modular Architecture',
                'description': '5 specialized engines',
                'confidence': 'HIGH',
                'applicability': 'All orchestrators'
            },
            {
                'name': 'Transactional Operations',
                'description': 'Checkpoint/rollback pattern',
                'confidence': 'HIGH',
                'applicability': 'Filesystem operations'
            }
        ]
        
        # Execute RECOMMEND phase
        recommend_result = orchestrator._phase_recommend(
            patterns=orchestrator.patterns_extracted,
            scope="design"
        )
        
        from src.orchestrators.base.base_orchestrator_v4_1 import PhaseStatus
        assert recommend_result.status == PhaseStatus.SUCCESS
        
        # Verify recommendations generated
        assert len(orchestrator.recommendations) > 0
        assert len(orchestrator.insights) > 0
        
        # Check recommendation structure
        rec = orchestrator.recommendations[0]
        assert 'category' in rec
        assert 'priority' in rec
        assert 'recommendation' in rec
        assert 'rationale' in rec
        assert 'action' in rec
    
    def test_document_phase_creates_markdown(self, temp_workspace, mock_config, mock_state_db):
        """Test that DOCUMENT phase creates properly formatted markdown."""
        orchestrator = HolisticReviewOrchestrator(
            config_path=mock_config,
            state_db=mock_state_db
        )
        
        # Populate test data
        orchestrator.artifacts_gathered = [
            {'type': 'progress_tracking', 'source': 'test.json'}
        ]
        orchestrator.patterns_extracted = [
            {
                'name': 'Test Pattern',
                'description': 'Test description',
                'confidence': 'HIGH'
            }
        ]
        orchestrator.recommendations = [
            {
                'category': 'architecture',
                'priority': 'HIGH',
                'recommendation': 'Test recommendation',
                'rationale': 'Test rationale',
                'action': 'Test action'
            }
        ]
        orchestrator.insights = ['Test insight']
        
        # Execute DOCUMENT phase
        doc_path = "architecture/holistic-review-test.md"
        document_result = orchestrator._phase_document(
            review_number=99,
            review_name="Test Review",
            document_path=doc_path,
            parent_plan_id="test-migration"
        )
        
        from src.orchestrators.base.base_orchestrator_v4_1 import PhaseStatus
        assert document_result.status == PhaseStatus.SUCCESS
        
        # Verify document was created
        full_path = Path(temp_workspace) / "cortex-brain" / "documents" / "planning" / "active" / "test-migration" / doc_path
        assert full_path.exists()
        
        # Verify content
        with open(full_path, 'r') as f:
            content = f.read()
        
        assert "# Holistic Review #99" in content
        assert "Test Review" in content
        assert "Test Pattern" in content
        assert "Test recommendation" in content
    
    def test_inject_phase_prepares_insights(self, mock_config, mock_state_db):
        """Test that INJECT phase formats insights for context injection."""
        orchestrator = HolisticReviewOrchestrator(
            config_path=mock_config,
            state_db=mock_state_db
        )
        
        # Populate insights
        orchestrator.insights = [
            'ARCHITECTURE: Use modular design',
            'CODE_REUSE: Reuse component X',
            'TESTING: Achieve 95%+ coverage'
        ]
        
        # Execute INJECT phase
        inject_result = orchestrator._phase_inject()
        
        from src.orchestrators.base.base_orchestrator_v4_1 import PhaseStatus
        assert inject_result.status == PhaseStatus.SUCCESS
        
        # Insights should be ready for injection (already formatted)
        assert len(orchestrator.insights) == 3
    
    def test_execution_with_code_reuse_scope(self, temp_workspace, mock_config, mock_state_db):
        """Test execution with code_reuse_strategy scope."""
        # Create implementation files in sibling migrations
        impl_dir = temp_workspace / "src" / "orchestrators" / "cleanup"
        impl_dir.mkdir(parents=True)
        
        impl_file = impl_dir / "cleanup_orchestrator_v2.py"
        with open(impl_file, 'w') as f:
            f.write("""
class CleanupOrchestratorV2:
    def __init__(self):
        self.filesystem_engine = FilesystemEngine()
        self.safety_validator = SafetyValidator()
""")
        
        orchestrator = HolisticReviewOrchestrator(
            config_path=mock_config,
            state_db=mock_state_db
        )
        
        # Execute with code_reuse_strategy scope
        result = orchestrator.execute(
            parent_plan_id="test-migration",
            review_number=2,
            review_name="Code Reuse Review",
            document_path="architecture/holistic-review-02.md",
            scope="code_reuse_strategy",
            completed_phases=[0, 1]
        )
        
        # Should complete successfully
        assert result.status == OrchestratorStatus.SUCCESS
        
        # Should have code reuse recommendations
        recommendations = result.metadata.get('recommendations', [])
        code_reuse_recs = [r for r in recommendations if r.get('category') == 'code_reuse']
        assert len(code_reuse_recs) > 0
    
    def test_error_handling_missing_parent_plan(self, mock_config, mock_state_db):
        """Test error handling when parent plan doesn't exist."""
        orchestrator = HolisticReviewOrchestrator(
            config_path=mock_config,
            state_db=mock_state_db
        )
        
        # Execute with nonexistent parent plan
        result = orchestrator.execute(
            parent_plan_id="nonexistent-plan",
            review_number=1,
            review_name="Test Review",
            document_path="architecture/holistic-review-01.md",
            scope="design",
            completed_phases=[0]
        )
        
        # Should handle gracefully
        assert result.status == OrchestratorStatus.FAILED
        assert len(result.errors) > 0
    
    def test_performance_target_under_45_seconds(self, temp_workspace, mock_config, mock_state_db):
        """Test that execution completes within 45 second target (mock-based estimate)."""
        import time
        
        orchestrator = HolisticReviewOrchestrator(
            config_path=mock_config,
            state_db=mock_state_db
        )
        
        start_time = time.time()
        
        result = orchestrator.execute(
            parent_plan_id="test-migration",
            review_number=1,
            review_name="Performance Test",
            document_path="architecture/holistic-review-perf.md",
            scope="design",
            completed_phases=[0]
        )
        
        execution_time = time.time() - start_time
        
        # With mocked data, should be very fast (<1s)
        # Real execution target is 45s
        assert execution_time < 45.0
        assert result.status == OrchestratorStatus.SUCCESS
        
        # Check metadata for execution time
        if 'duration_seconds' in result.metadata:
            assert result.metadata['duration_seconds'] < 45.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
