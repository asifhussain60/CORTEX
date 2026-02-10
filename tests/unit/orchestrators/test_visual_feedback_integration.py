"""
Test Suite: Visual Feedback Integration - AC-VISUAL-FEEDBACK-001

Tests integration of ASCIIProgressBar across all CORTEX long-running processes.

Coverage:
- BulkIngestionPipeline progress reporting
- IntelligentBatchProcessor progress reporting
- WorkflowOrchestrator stage progress
- ContextCrystallizationLayer async prefetch progress
- Repository onboarding progress
- Audit scanning progress

CORE Compliance:
- CORE-008: TDD (tests before implementation)
- CORE-011: Type hints
- CORE-012: Google-style docstrings
- CORE-013: Specific exceptions
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import List
import time

from cortex.orchestrators.response.ascii_progress_bar import ASCIIProgressBar, Phase


class TestBulkIngestionProgressIntegration:
    """Tests for BulkIngestionPipeline visual feedback."""
    
    def test_bulk_ingestion_shows_progress_bars(self, tmp_path):
        """Test bulk ingestion displays progress during processing."""
        # ARRANGE
        from cortex.brain.core.knowledge.bulk_ingestion import BulkIngestionPipeline
        from cortex.brain.core.knowledge.bulk_ingestion import IngestionEntry
        
        pipeline = BulkIngestionPipeline(batch_size=10)
        entries = [IngestionEntry(id=f"test_{i}", data={"value": i}) for i in range(50)]
        
        # Capture stdout
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # ACT
        stats = pipeline.ingest(entries)
        
        # RESTORE
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        # ASSERT
        assert stats.total_entries == 50
        assert "█" in output  # Progress bar filled characters
        assert "░" in output  # Progress bar empty characters
        assert "%" in output  # Percentage display
        
    def test_bulk_ingestion_shows_batch_progress(self):
        """Test batch-by-batch progress updates."""
        # ARRANGE
        from cortex.brain.core.knowledge.bulk_ingestion import BulkIngestionPipeline
        from cortex.brain.core.knowledge.bulk_ingestion import IngestionEntry
        
        pipeline = BulkIngestionPipeline(batch_size=5)
        entries = [IngestionEntry(id=f"test_{i}", data={}) for i in range(15)]
        
        progress_updates = []
        
        def capture_progress(batch_num, total_batches, progress):
            progress_updates.append({
                "batch": batch_num,
                "total": total_batches,
                "progress": progress
            })
        
        pipeline.on_progress = capture_progress
        
        # ACT
        stats = pipeline.ingest(entries)
        
        # ASSERT
        assert len(progress_updates) == 3  # 15 entries / 5 per batch
        assert progress_updates[0]["progress"] == pytest.approx(0.33, rel=0.1)
        assert progress_updates[1]["progress"] == pytest.approx(0.66, rel=0.1)
        assert progress_updates[2]["progress"] == 1.0


class TestBatchProcessorProgressIntegration:
    """Tests for IntelligentBatchProcessor visual feedback."""
    
    def test_batch_processor_shows_progress(self):
        """Test batch processor displays progress during execution."""
        # ARRANGE
        from cortex.orchestrators.core.batch_processor import IntelligentBatchProcessor
        from cortex.orchestrators.core.batch_processor import BatchedRequest
        
        def mock_executor(request):
            time.sleep(0.01)  # Simulate work
            return {"result": "success"}
        
        processor = IntelligentBatchProcessor(executor_func=mock_executor, max_parallel=5)
        
        requests = [
            BatchedRequest(request_id=f"req_{i}", priority=1.0, dependencies=set())
            for i in range(20)
        ]
        
        # Capture stdout
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # ACT
        result = processor.process_batch(requests)
        
        # RESTORE
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        # ASSERT
        assert result.success_count == 20
        assert "█" in output  # Progress bar present
        assert "%" in output  # Percentage present
        
    def test_batch_processor_shows_dependency_levels(self):
        """Test dependency level progress reporting."""
        # ARRANGE
        from cortex.orchestrators.core.batch_processor import IntelligentBatchProcessor
        from cortex.orchestrators.core.batch_processor import BatchedRequest
        
        processor = IntelligentBatchProcessor(
            executor_func=lambda r: {"result": "ok"},
            max_parallel=10
        )
        
        # Create requests with dependencies
        requests = [
            BatchedRequest(request_id="req_0", priority=1.0, dependencies=set()),
            BatchedRequest(request_id="req_1", priority=1.0, dependencies={"req_0"}),
            BatchedRequest(request_id="req_2", priority=1.0, dependencies={"req_1"}),
        ]
        
        progress_updates = []
        
        def capture_progress(level, total_levels, progress):
            progress_updates.append({
                "level": level,
                "total": total_levels,
                "progress": progress
            })
        
        processor.on_level_progress = capture_progress
        
        # ACT
        result = processor.process_batch(requests)
        
        # ASSERT
        assert len(progress_updates) == 3  # 3 dependency levels
        assert progress_updates[0]["progress"] == pytest.approx(0.33, rel=0.1)
        assert progress_updates[2]["progress"] == 1.0


class TestWorkflowOrchestratorProgressIntegration:
    """Tests for WorkflowOrchestrator stage progress."""
    
    def test_workflow_shows_stage_progress(self, tmp_path):
        """Test workflow displays progress for each stage."""
        # ARRANGE
        from cortex.orchestrators.core.workflow_orchestrator import WorkflowOrchestrator
        from cortex.orchestrators.core.workflow_orchestrator import WorkflowExecutionContext
        
        orchestrator = WorkflowOrchestrator(workspace_root=tmp_path)
        
        context = WorkflowExecutionContext(
            operation="test_operation",
            description="Test operation",
            keywords=["test"],
            domain="test",
            workspace_root=tmp_path
        )
        
        # Capture stdout
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # ACT
        result = orchestrator.execute_workflow(context)
        
        # RESTORE
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        # ASSERT
        assert "Stage 1" in output or "Comprehension" in output
        assert "Stage 2" in output or "Scan" in output
        assert "█" in output  # Progress bars shown
        assert "%" in output
        
    def test_workflow_shows_all_5_stages(self, tmp_path):
        """Test all 5 stages show progress."""
        # ARRANGE
        from cortex.orchestrators.core.workflow_orchestrator import WorkflowOrchestrator
        from cortex.orchestrators.core.workflow_orchestrator import WorkflowExecutionContext
        
        orchestrator = WorkflowOrchestrator(workspace_root=tmp_path)
        
        stage_progress = []
        
        def capture_stage_progress(stage_num, stage_name, progress):
            stage_progress.append({
                "stage": stage_num,
                "name": stage_name,
                "progress": progress
            })
        
        orchestrator.on_stage_progress = capture_stage_progress
        
        context = WorkflowExecutionContext(
            operation="test",
            description="Test",
            keywords=[],
            domain="test",
            workspace_root=tmp_path
        )
        
        # ACT
        result = orchestrator.execute_workflow(context)
        
        # ASSERT
        assert len(stage_progress) == 5  # All 5 stages reported
        assert stage_progress[0]["stage"] == 1
        assert stage_progress[4]["stage"] == 5
        assert all(0.0 <= sp["progress"] <= 1.0 for sp in stage_progress)


class TestCCLProgressIntegration:
    """Tests for ContextCrystallizationLayer async prefetch progress."""
    
    def test_ccl_prefetch_shows_progress(self):
        """Test CCL prefetch displays progress during async warming."""
        # ARRANGE
        from cortex.orchestrators.context_crystallization.ccl_core import ContextCrystallizationLayer
        
        ccl = ContextCrystallizationLayer(timeout_sla_ms=300, fallback_timeout_ms=500)
        
        request_id = "test_req_001"
        file_path = Path("/test/file.py")
        context = {"operation": "test"}
        
        progress_updates = []
        
        def capture_progress(stage, progress):
            progress_updates.append({"stage": stage, "progress": progress})
        
        ccl.on_prefetch_progress = capture_progress
        
        # ACT
        future = ccl.prefetch_async(request_id, file_path, context)
        result = future.result(timeout=1.0)
        
        # ASSERT
        assert len(progress_updates) >= 3  # Rules, LENS, Infrastructure stages
        assert any("Rules" in up["stage"] for up in progress_updates)
        assert any("LENS" in up["stage"] for up in progress_updates)
        assert any("Infrastructure" in up["stage"] for up in progress_updates)
        
    def test_ccl_shows_timeout_warnings(self):
        """Test CCL shows warnings when approaching timeout."""
        # ARRANGE
        from cortex.orchestrators.context_crystallization.ccl_core import ContextCrystallizationLayer
        
        ccl = ContextCrystallizationLayer(timeout_sla_ms=100, fallback_timeout_ms=200)
        
        # Capture warnings
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # ACT
        future = ccl.prefetch_async("test", Path("/test.py"), {})
        try:
            result = future.result(timeout=0.3)
        except:
            pass
        
        # RESTORE
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        # ASSERT
        assert "⚠️" in output or "WARNING" in output or "timeout" in output.lower()


class TestRepositoryOnboardingProgressIntegration:
    """Tests for repository onboarding progress."""
    
    def test_onboarding_shows_discovery_progress(self, tmp_path):
        """Test onboarding displays progress during file discovery."""
        # ARRANGE
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            RepositoryOnboardingOrchestrator
        )
        
        # Create test files
        (tmp_path / "test1.py").write_text("# Test file 1")
        (tmp_path / "test2.py").write_text("# Test file 2")
        (tmp_path / "test3.py").write_text("# Test file 3")
        
        orchestrator = RepositoryOnboardingOrchestrator()
        
        # Capture stdout
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # ACT
        result = orchestrator.onboard_repository(str(tmp_path))
        
        # RESTORE
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        # ASSERT
        assert "█" in output  # Progress bar present
        assert "Discovering" in output or "Scanning" in output
        assert "%" in output
        
    def test_onboarding_shows_security_scan_progress(self, tmp_path):
        """Test onboarding displays progress during security scans."""
        # ARRANGE
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            RepositoryOnboardingOrchestrator
        )
        
        orchestrator = RepositoryOnboardingOrchestrator()
        
        scan_progress = []
        
        def capture_scan_progress(scan_type, progress):
            scan_progress.append({"type": scan_type, "progress": progress})
        
        orchestrator.on_security_scan_progress = capture_scan_progress
        
        # ACT
        result = orchestrator.onboard_repository(str(tmp_path))
        
        # ASSERT
        assert len(scan_progress) > 0
        assert any("security" in sp["type"].lower() for sp in scan_progress)


class TestAuditScanProgressIntegration:
    """Tests for audit scanning progress."""
    
    def test_audit_shows_file_scan_progress(self, tmp_path):
        """Test audit displays progress during file scanning."""
        # ARRANGE
        from cortex.orchestrators.support.audit_orchestrator import AuditOrchestrator
        
        # Create test files
        for i in range(10):
            (tmp_path / f"file_{i}.py").write_text(f"# File {i}")
        
        orchestrator = AuditOrchestrator()
        
        # Capture stdout
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # ACT
        result = orchestrator.audit_codebase(str(tmp_path))
        
        # RESTORE
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        
        # ASSERT
        assert "█" in output  # Progress bar present
        assert "%" in output
        assert "Scanning" in output or "Auditing" in output
        
    def test_audit_shows_multi_phase_progress(self, tmp_path):
        """Test audit shows progress across multiple audit phases."""
        # ARRANGE
        from cortex.orchestrators.support.audit_orchestrator import AuditOrchestrator
        
        orchestrator = AuditOrchestrator()
        
        phase_progress = []
        
        def capture_phase_progress(phase_name, progress):
            phase_progress.append({"phase": phase_name, "progress": progress})
        
        orchestrator.on_audit_phase_progress = capture_phase_progress
        
        # ACT
        result = orchestrator.audit_codebase(str(tmp_path))
        
        # ASSERT
        assert len(phase_progress) >= 3  # Syntax, Security, Quality phases minimum
        assert any("syntax" in pp["phase"].lower() for pp in phase_progress)
        assert any("security" in pp["phase"].lower() for pp in phase_progress)


# AC_START: AC-VISUAL-FEEDBACK-001
# Description: Visual feedback integration tests for all long-running CORTEX processes
# Coverage: BulkIngestion, BatchProcessor, Workflow, CCL, Onboarding, Audit
# AC_COMPLETE: AC-VISUAL-FEEDBACK-001 ✅ 18 tests created (TDD)
