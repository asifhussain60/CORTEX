"""
Tests for Base Incremental Orchestrator

Tests the protocol and infrastructure for incremental work execution including
chunk management, checkpoint creation, dependency handling, and progress tracking.

Part of CORTEX 3.2.1 - Incremental Work Management System
Author: Asif Hussain
"""

import pytest
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import Mock, patch, MagicMock

from src.orchestrators.base_incremental_orchestrator import (
    WorkChunk,
    WorkCheckpoint,
    IncrementalWorkExecutor
)


# Concrete implementation for testing
class TestOrchestrator(IncrementalWorkExecutor):
    """Concrete implementation for testing abstract base class"""
    
    def break_into_chunks(self, work_request: Dict[str, Any]) -> List[WorkChunk]:
        """Break work into test chunks"""
        num_chunks = work_request.get("num_chunks", 3)
        chunks = []
        
        for i in range(num_chunks):
            chunk = WorkChunk(
                chunk_id=f"chunk-{i+1}",
                chunk_type="task" if i < num_chunks - 1 else "phase",
                description=f"Test task {i+1}",
                estimated_tokens=100
            )
            chunks.append(chunk)
        
        return chunks
    
    def execute_chunk(self, chunk: WorkChunk) -> Dict[str, Any]:
        """Execute a test chunk"""
        chunk.status = "complete"
        return {
            "success": True,
            "chunk_id": chunk.chunk_id,
            "output": f"Output from {chunk.chunk_id}",
            "token_count": 50
        }


class TestWorkChunk:
    """Test WorkChunk dataclass"""
    
    def test_work_chunk_creation(self):
        """Test basic WorkChunk creation"""
        chunk = WorkChunk(
            chunk_id="chunk-1",
            chunk_type="task",
            description="Test task",
            estimated_tokens=100
        )
        
        assert chunk.chunk_id == "chunk-1"
        assert chunk.chunk_type == "task"
        assert chunk.status == "pending"
        assert chunk.dependencies == []
    
    def test_work_chunk_with_dependencies(self):
        """Test WorkChunk with dependencies"""
        chunk = WorkChunk(
            chunk_id="chunk-2",
            chunk_type="section",
            description="Dependent task",
            estimated_tokens=200,
            dependencies=["chunk-1"]
        )
        
        assert chunk.dependencies == ["chunk-1"]
    
    def test_work_chunk_invalid_status(self):
        """Test WorkChunk rejects invalid status"""
        with pytest.raises(ValueError, match="Invalid status"):
            WorkChunk(
                chunk_id="chunk-1",
                chunk_type="task",
                description="Test",
                estimated_tokens=100,
                status="invalid"
            )
    
    def test_work_chunk_invalid_type(self):
        """Test WorkChunk rejects invalid chunk_type"""
        with pytest.raises(ValueError, match="Invalid chunk_type"):
            WorkChunk(
                chunk_id="chunk-1",
                chunk_type="invalid",
                description="Test",
                estimated_tokens=100
            )
    
    def test_work_chunk_metadata(self):
        """Test WorkChunk with custom metadata"""
        chunk = WorkChunk(
            chunk_id="chunk-1",
            chunk_type="test",
            description="Test with metadata",
            estimated_tokens=100,
            metadata={"priority": "high", "category": "unit-test"}
        )
        
        assert chunk.metadata["priority"] == "high"
        assert chunk.metadata["category"] == "unit-test"


class TestWorkCheckpoint:
    """Test WorkCheckpoint dataclass"""
    
    def test_checkpoint_creation(self):
        """Test basic WorkCheckpoint creation"""
        checkpoint = WorkCheckpoint(
            checkpoint_id="cp-1",
            chunks_completed=["chunk-1", "chunk-2"],
            preview="Completed 2 chunks",
            approval_required=True
        )
        
        assert checkpoint.checkpoint_id == "cp-1"
        assert len(checkpoint.chunks_completed) == 2
        assert checkpoint.approval_required is True
        assert checkpoint.feedback is None
    
    def test_checkpoint_to_dict(self):
        """Test checkpoint serialization to dict"""
        checkpoint = WorkCheckpoint(
            checkpoint_id="cp-1",
            chunks_completed=["chunk-1"],
            preview="Test preview",
            approval_required=False
        )
        
        data = checkpoint.to_dict()
        
        assert data["checkpoint_id"] == "cp-1"
        assert data["chunks_completed"] == ["chunk-1"]
        assert data["preview"] == "Test preview"
        assert "timestamp" in data


class TestIncrementalWorkExecutor:
    """Test IncrementalWorkExecutor base class"""
    
    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create test orchestrator instance"""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        (brain_path / "documents").mkdir()
        (brain_path / "documents" / "reports").mkdir(parents=True)
        
        return TestOrchestrator(brain_path=brain_path)
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert orchestrator.brain_path is not None
        assert orchestrator.response_monitor is not None
        assert orchestrator.checkpoints == []
        assert orchestrator.completed_chunks == []
    
    def test_break_into_chunks(self, orchestrator):
        """Test breaking work into chunks"""
        work_request = {"num_chunks": 5}
        chunks = orchestrator.break_into_chunks(work_request)
        
        assert len(chunks) == 5
        assert all(isinstance(c, WorkChunk) for c in chunks)
        assert chunks[0].chunk_id == "chunk-1"
        assert chunks[-1].chunk_type == "phase"
    
    def test_execute_chunk(self, orchestrator):
        """Test executing a single chunk"""
        chunk = WorkChunk(
            chunk_id="test-chunk",
            chunk_type="task",
            description="Test",
            estimated_tokens=100
        )
        
        result = orchestrator.execute_chunk(chunk)
        
        assert result["success"] is True
        assert result["chunk_id"] == "test-chunk"
        assert chunk.status == "complete"
    
    def test_check_dependencies_satisfied(self, orchestrator):
        """Test dependency checking when satisfied"""
        chunk = WorkChunk(
            chunk_id="chunk-2",
            chunk_type="task",
            description="Dependent task",
            estimated_tokens=100,
            dependencies=["chunk-1"]
        )
        
        completed = ["chunk-1"]
        
        assert orchestrator._check_dependencies(chunk, completed) is True
    
    def test_check_dependencies_unsatisfied(self, orchestrator):
        """Test dependency checking when unsatisfied"""
        chunk = WorkChunk(
            chunk_id="chunk-3",
            chunk_type="task",
            description="Dependent task",
            estimated_tokens=100,
            dependencies=["chunk-1", "chunk-2"]
        )
        
        completed = ["chunk-1"]  # chunk-2 not completed
        
        assert orchestrator._check_dependencies(chunk, completed) is False
    
    def test_is_checkpoint_boundary_phase(self, orchestrator):
        """Test checkpoint creation at phase boundaries"""
        chunk = WorkChunk(
            chunk_id="chunk-1",
            chunk_type="phase",
            description="Phase 1",
            estimated_tokens=100
        )
        
        all_chunks = [chunk]
        
        assert orchestrator._is_checkpoint_boundary(chunk, all_chunks) is True
    
    def test_is_checkpoint_boundary_interval(self, orchestrator):
        """Test checkpoint creation at regular intervals"""
        chunks = [
            WorkChunk(f"chunk-{i}", "task", f"Task {i}", 100)
            for i in range(1, 11)
        ]
        
        # Should checkpoint at chunk 5 (CHECKPOINT_INTERVAL = 5)
        assert orchestrator._is_checkpoint_boundary(chunks[4], chunks) is True
        assert orchestrator._is_checkpoint_boundary(chunks[3], chunks) is False
    
    def test_is_checkpoint_boundary_end(self, orchestrator):
        """Test checkpoint creation at the end"""
        chunks = [
            WorkChunk(f"chunk-{i}", "task", f"Task {i}", 100)
            for i in range(1, 4)
        ]
        
        # Should checkpoint at last chunk
        assert orchestrator._is_checkpoint_boundary(chunks[-1], chunks) is True
    
    def test_create_checkpoint(self, orchestrator):
        """Test checkpoint creation"""
        chunks = [
            WorkChunk(f"chunk-{i}", "task", f"Task {i}", 100)
            for i in range(1, 4)
        ]
        results = [
            {"success": True, "chunk_id": f"chunk-{i}"}
            for i in range(1, 4)
        ]
        
        checkpoint = orchestrator._create_checkpoint(chunks, results)
        
        assert checkpoint.checkpoint_id == "checkpoint-1"
        assert len(checkpoint.chunks_completed) == 3
        assert "Checkpoint: 3 chunks completed" in checkpoint.preview
    
    def test_execute_incremental_success(self, orchestrator):
        """Test successful incremental execution"""
        work_request = {"num_chunks": 3}
        
        result = orchestrator.execute_incremental(work_request)
        
        assert result["success"] is True
        assert result["chunks_executed"] == 3
        assert result["aborted"] is False
        assert len(result["results"]) == 3
    
    def test_execute_incremental_with_checkpoint_callback(self, orchestrator):
        """Test incremental execution with checkpoint callback"""
        work_request = {"num_chunks": 3}
        callback = Mock(return_value=True)
        
        result = orchestrator.execute_incremental(work_request, callback)
        
        assert result["success"] is True
        assert callback.called  # Checkpoint at end (phase boundary)
    
    def test_execute_incremental_rejected_checkpoint(self, orchestrator):
        """Test execution aborts when checkpoint rejected"""
        work_request = {"num_chunks": 3}
        callback = Mock(return_value=False)  # User rejects
        
        result = orchestrator.execute_incremental(work_request, callback)
        
        assert result["success"] is False
        assert result["aborted"] is True
        assert "rejected" in result["reason"]
    
    def test_execute_incremental_with_dependencies(self):
        """Test execution respects chunk dependencies"""
        
        class DependentOrchestrator(IncrementalWorkExecutor):
            def break_into_chunks(self, work_request):
                return [
                    WorkChunk("chunk-1", "task", "Task 1", 100),
                    WorkChunk("chunk-2", "task", "Task 2", 100, dependencies=["chunk-1"]),
                    WorkChunk("chunk-3", "task", "Task 3", 100, dependencies=["chunk-2"])
                ]
            
            def execute_chunk(self, chunk):
                chunk.status = "complete"
                return {
                    "success": True,
                    "chunk_id": chunk.chunk_id,
                    "output": "test",
                    "token_count": 50
                }
        
        orchestrator = DependentOrchestrator()
        result = orchestrator.execute_incremental({})
        
        assert result["success"] is True
        assert result["chunks_executed"] == 3
    
    def test_execute_incremental_blocked_dependency(self):
        """Test execution handles blocked dependencies"""
        
        class BlockedOrchestrator(IncrementalWorkExecutor):
            def break_into_chunks(self, work_request):
                return [
                    WorkChunk("chunk-1", "task", "Task 1", 100),
                    WorkChunk("chunk-2", "task", "Task 2", 100, dependencies=["chunk-999"])  # Missing dep
                ]
            
            def execute_chunk(self, chunk):
                chunk.status = "complete"
                return {
                    "success": True,
                    "chunk_id": chunk.chunk_id,
                    "output": "test",
                    "token_count": 50
                }
        
        orchestrator = BlockedOrchestrator()
        result = orchestrator.execute_incremental({})
        
        # Should execute chunk-1 but skip chunk-2
        assert result["chunks_executed"] == 1
    
    def test_get_execution_summary(self, orchestrator):
        """Test execution summary retrieval"""
        work_request = {"num_chunks": 3}
        orchestrator.execute_incremental(work_request)
        
        summary = orchestrator.get_execution_summary()
        
        assert summary["completed_chunks"] == 3
        assert summary["checkpoints_created"] > 0
        assert "checkpoint_details" in summary
    
    def test_execute_incremental_with_large_output(self, orchestrator, tmp_path):
        """Test execution with response size monitoring"""
        
        class LargeOutputOrchestrator(IncrementalWorkExecutor):
            def break_into_chunks(self, work_request):
                return [WorkChunk("chunk-1", "task", "Large output task", 5000)]
            
            def execute_chunk(self, chunk):
                chunk.status = "complete"
                # Generate output exceeding 3500 token threshold
                large_output = "word " * 4000  # ~5000 tokens
                return {
                    "success": True,
                    "chunk_id": chunk.chunk_id,
                    "output": large_output,
                    "token_count": 5000
                }
        
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(exist_ok=True)
        (brain_path / "documents" / "reports").mkdir(parents=True, exist_ok=True)
        
        orchestrator = LargeOutputOrchestrator(brain_path=brain_path)
        result = orchestrator.execute_incremental({})
        
        # Should complete but with auto-chunking flag
        assert result["success"] is True
        assert result["results"][0].get("auto_chunked") is True
