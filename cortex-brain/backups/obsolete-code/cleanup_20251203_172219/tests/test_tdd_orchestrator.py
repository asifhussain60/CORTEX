"""
Tests for TDD Orchestrator

Tests incremental TDD workflow execution including RED→GREEN→REFACTOR cycle
chunking, phase transitions, checkpoints, and integration with base orchestrator.

Part of CORTEX 3.2.1 - Incremental Work Management System
Author: Asif Hussain
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List

from src.orchestrators.tdd_orchestrator import (
    TDDOrchestrator,
    TDDPhase,
    TDDWorkRequest
)
from src.orchestrators.base_incremental_orchestrator import WorkChunk


class TestTDDWorkRequest:
    """Test TDDWorkRequest dataclass"""
    
    def test_work_request_creation(self):
        """Test basic TDD work request creation"""
        request = TDDWorkRequest(
            feature_name="UserAuth",
            test_file_path="tests/test_user_auth.py",
            implementation_file_path="src/user_auth.py",
            requirements=["User can login", "User can logout"]
        )
        
        assert request.feature_name == "UserAuth"
        assert len(request.requirements) == 2
        assert request.existing_tests == 0
        assert request.existing_methods == []
    
    def test_work_request_with_existing_code(self):
        """Test work request with existing tests and methods"""
        request = TDDWorkRequest(
            feature_name="UserAuth",
            test_file_path="tests/test_user_auth.py",
            implementation_file_path="src/user_auth.py",
            requirements=["User can reset password"],
            existing_tests=2,
            existing_methods=["login", "logout"]
        )
        
        assert request.existing_tests == 2
        assert request.existing_methods == ["login", "logout"]


class TestTDDOrchestrator:
    """Test TDD Orchestrator"""
    
    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create TDD orchestrator instance"""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(exist_ok=True)
        (brain_path / "documents" / "reports").mkdir(parents=True, exist_ok=True)
        
        return TDDOrchestrator(brain_path=brain_path)
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test TDD orchestrator initialization"""
        assert orchestrator.current_phase == TDDPhase.RED
        assert orchestrator.current_requirement_index == 0
        assert orchestrator.response_monitor is not None
    
    def test_break_into_chunks_single_requirement(self, orchestrator):
        """Test chunking for single requirement"""
        work_request = {
            "feature_name": "UserAuth",
            "test_file_path": "tests/test_auth.py",
            "implementation_file_path": "src/auth.py",
            "requirements": ["User can login with valid credentials"],
            "existing_tests": 0
        }
        
        chunks = orchestrator.break_into_chunks(work_request)
        
        # Should have: skeleton + (test + checkpoint + method + checkpoint + refactor) * 1 requirement
        # = 1 + 5 = 6 chunks
        assert len(chunks) == 6
        
        # Verify chunk sequence
        assert chunks[0].chunk_type == "skeleton"
        assert chunks[1].chunk_type == "test"  # RED
        assert chunks[2].chunk_type == "phase"  # Checkpoint RED→GREEN
        assert chunks[3].chunk_type == "method"  # GREEN
        assert chunks[4].chunk_type == "phase"  # Checkpoint GREEN→REFACTOR
        assert chunks[5].chunk_type == "section"  # REFACTOR
    
    def test_break_into_chunks_multiple_requirements(self, orchestrator):
        """Test chunking for multiple requirements"""
        work_request = {
            "feature_name": "UserAuth",
            "test_file_path": "tests/test_auth.py",
            "implementation_file_path": "src/auth.py",
            "requirements": [
                "User can login",
                "User can logout",
                "User can reset password"
            ],
            "existing_tests": 0
        }
        
        chunks = orchestrator.break_into_chunks(work_request)
        
        # Should have: skeleton + (test + checkpoint + method + checkpoint + refactor) * 3 requirements
        # = 1 + (5 * 3) = 16 chunks
        assert len(chunks) == 16
        
        # Verify each requirement gets full TDD cycle
        test_chunks = [c for c in chunks if c.chunk_type == "test"]
        method_chunks = [c for c in chunks if c.chunk_type == "method"]
        refactor_chunks = [c for c in chunks if c.chunk_type == "section"]
        
        assert len(test_chunks) == 3
        assert len(method_chunks) == 3
        assert len(refactor_chunks) == 3
    
    def test_break_into_chunks_existing_tests(self, orchestrator):
        """Test chunking with existing tests (skip skeleton)"""
        work_request = {
            "feature_name": "UserAuth",
            "test_file_path": "tests/test_auth.py",
            "implementation_file_path": "src/auth.py",
            "requirements": ["User can change email"],
            "existing_tests": 2  # Tests already exist
        }
        
        chunks = orchestrator.break_into_chunks(work_request)
        
        # Should NOT include skeleton chunk
        # = (test + checkpoint + method + checkpoint + refactor) * 1 = 5 chunks
        assert len(chunks) == 5
        assert chunks[0].chunk_type == "test"  # No skeleton
        
        # Test number should be 3 (existing 2 + this 1)
        assert chunks[0].metadata["test_number"] == 3
    
    def test_chunk_dependencies(self, orchestrator):
        """Test that chunks have correct dependencies"""
        work_request = {
            "feature_name": "UserAuth",
            "test_file_path": "tests/test_auth.py",
            "implementation_file_path": "src/auth.py",
            "requirements": ["User can login"],
            "existing_tests": 0
        }
        
        chunks = orchestrator.break_into_chunks(work_request)
        
        # Verify dependency chain
        assert chunks[1].dependencies == ["chunk-1"]  # test depends on skeleton
        assert chunks[2].dependencies == ["chunk-2"]  # checkpoint depends on test
        assert chunks[3].dependencies == ["chunk-3"]  # method depends on checkpoint
        assert chunks[4].dependencies == ["chunk-4"]  # checkpoint depends on method
        assert chunks[5].dependencies == ["chunk-5"]  # refactor depends on checkpoint
    
    def test_chunk_phases(self, orchestrator):
        """Test that chunks have correct phase metadata"""
        work_request = {
            "feature_name": "UserAuth",
            "test_file_path": "tests/test_auth.py",
            "implementation_file_path": "src/auth.py",
            "requirements": ["User can login"],
            "existing_tests": 0
        }
        
        chunks = orchestrator.break_into_chunks(work_request)
        
        # Verify phases
        assert chunks[1].metadata["phase"] == TDDPhase.RED.value
        assert chunks[2].metadata["transition"] == "RED_TO_GREEN"
        assert chunks[3].metadata["phase"] == TDDPhase.GREEN.value
        assert chunks[4].metadata["transition"] == "GREEN_TO_REFACTOR"
        assert chunks[5].metadata["phase"] == TDDPhase.REFACTOR.value
    
    def test_execute_chunk_skeleton(self, orchestrator):
        """Test executing skeleton chunk"""
        chunk = WorkChunk(
            chunk_id="chunk-1",
            chunk_type="skeleton",
            description="Create test skeleton",
            estimated_tokens=150,
            metadata={
                "phase": TDDPhase.RED.value,
                "file_path": "tests/test_auth.py",
                "feature_name": "UserAuth"
            }
        )
        
        result = orchestrator.execute_chunk(chunk)
        
        assert result["success"] is True
        assert "import pytest" in result["output"]
        assert "class Test" in result["output"]
        assert chunk.status == "complete"
    
    def test_execute_chunk_test(self, orchestrator):
        """Test executing test chunk (RED phase)"""
        chunk = WorkChunk(
            chunk_id="chunk-2",
            chunk_type="test",
            description="Write test for login",
            estimated_tokens=300,
            metadata={
                "phase": TDDPhase.RED.value,
                "requirement": "User can login with valid credentials",
                "test_number": 1,
                "file_path": "tests/test_auth.py"
            }
        )
        
        result = orchestrator.execute_chunk(chunk)
        
        assert result["success"] is True
        assert "def test_" in result["output"]
        assert "RED phase" in result["output"]
        assert "assert" in result["output"]
        assert chunk.status == "complete"
    
    def test_execute_chunk_method(self, orchestrator):
        """Test executing method chunk (GREEN phase)"""
        chunk = WorkChunk(
            chunk_id="chunk-3",
            chunk_type="method",
            description="Implement login method",
            estimated_tokens=400,
            metadata={
                "phase": TDDPhase.GREEN.value,
                "requirement": "User can login with valid credentials",
                "test_number": 1,
                "file_path": "src/auth.py"
            }
        )
        
        result = orchestrator.execute_chunk(chunk)
        
        assert result["success"] is True
        assert "def " in result["output"]
        assert "GREEN phase" in result["output"]
        assert chunk.status == "complete"
    
    def test_execute_chunk_refactoring(self, orchestrator):
        """Test executing refactoring chunk"""
        chunk = WorkChunk(
            chunk_id="chunk-4",
            chunk_type="section",
            description="Suggest refactoring",
            estimated_tokens=200,
            metadata={
                "phase": TDDPhase.REFACTOR.value,
                "requirement": "User can login with valid credentials",
                "test_number": 1,
                "file_path": "src/auth.py"
            }
        )
        
        result = orchestrator.execute_chunk(chunk)
        
        assert result["success"] is True
        assert "Refactoring" in result["output"]
        assert "Suggestions" in result["output"]
        assert chunk.status == "complete"
    
    def test_execute_chunk_phase_checkpoint(self, orchestrator):
        """Test executing phase checkpoint chunk"""
        chunk = WorkChunk(
            chunk_id="chunk-5",
            chunk_type="phase",
            description="Checkpoint: Verify test fails",
            estimated_tokens=50,
            metadata={
                "phase": "checkpoint",
                "transition": "RED_TO_GREEN",
                "test_number": 1
            }
        )
        
        result = orchestrator.execute_chunk(chunk)
        
        assert result["success"] is True
        assert "RED Phase Complete" in result["output"]
        assert "pytest" in result["output"]
        assert "test fails" in result["output"]
        assert chunk.status == "complete"
    
    def test_is_checkpoint_boundary_phase(self, orchestrator):
        """Test checkpoint at phase boundaries"""
        phase_chunk = WorkChunk(
            chunk_id="chunk-1",
            chunk_type="phase",
            description="Phase checkpoint",
            estimated_tokens=50,
            metadata={"transition": "RED_TO_GREEN"}
        )
        
        assert orchestrator._is_checkpoint_boundary(phase_chunk, [phase_chunk]) is True
    
    def test_is_checkpoint_boundary_refactor(self, orchestrator):
        """Test checkpoint after refactoring"""
        refactor_chunk = WorkChunk(
            chunk_id="chunk-1",
            chunk_type="section",
            description="Refactoring",
            estimated_tokens=200,
            metadata={"phase": TDDPhase.REFACTOR.value}
        )
        
        assert orchestrator._is_checkpoint_boundary(refactor_chunk, [refactor_chunk]) is True
    
    def test_is_checkpoint_boundary_end(self, orchestrator):
        """Test checkpoint at end of workflow"""
        chunks = [
            WorkChunk(f"chunk-{i}", "test", f"Test {i}", 100)
            for i in range(1, 4)
        ]
        
        assert orchestrator._is_checkpoint_boundary(chunks[-1], chunks) is True
        assert orchestrator._is_checkpoint_boundary(chunks[0], chunks) is False
    
    def test_execute_incremental_single_requirement(self, orchestrator):
        """Test full incremental execution for single requirement"""
        work_request = {
            "feature_name": "Calculator",
            "test_file_path": "tests/test_calc.py",
            "implementation_file_path": "src/calc.py",
            "requirements": ["Calculator can add two numbers"],
            "existing_tests": 0
        }
        
        result = orchestrator.execute_incremental(work_request)
        
        assert result["success"] is True
        assert result["chunks_executed"] == 6  # skeleton + 5 per requirement
        assert result["aborted"] is False
        assert len(result["results"]) == 6
    
    def test_execute_incremental_multiple_requirements(self, orchestrator):
        """Test full incremental execution for multiple requirements"""
        work_request = {
            "feature_name": "Calculator",
            "test_file_path": "tests/test_calc.py",
            "implementation_file_path": "src/calc.py",
            "requirements": [
                "Calculator can add two numbers",
                "Calculator can subtract two numbers"
            ],
            "existing_tests": 0
        }
        
        result = orchestrator.execute_incremental(work_request)
        
        assert result["success"] is True
        assert result["chunks_executed"] == 11  # skeleton + (5 * 2)
        assert result["aborted"] is False
    
    def test_execute_incremental_with_checkpoint_callback(self, orchestrator):
        """Test incremental execution with checkpoint approval"""
        work_request = {
            "feature_name": "Calculator",
            "test_file_path": "tests/test_calc.py",
            "implementation_file_path": "src/calc.py",
            "requirements": ["Calculator can add two numbers"],
            "existing_tests": 0
        }
        
        checkpoints_called = []
        
        def checkpoint_callback(checkpoint):
            checkpoints_called.append(checkpoint.checkpoint_id)
            return True  # Approve all
        
        result = orchestrator.execute_incremental(work_request, checkpoint_callback)
        
        assert result["success"] is True
        # Should have checkpoints at phase boundaries
        assert len(checkpoints_called) > 0
    
    def test_execute_incremental_rejected_checkpoint(self, orchestrator):
        """Test execution aborts when checkpoint rejected"""
        work_request = {
            "feature_name": "Calculator",
            "test_file_path": "tests/test_calc.py",
            "implementation_file_path": "src/calc.py",
            "requirements": ["Calculator can add two numbers"],
            "existing_tests": 0
        }
        
        def checkpoint_callback(checkpoint):
            return False  # Reject first checkpoint
        
        result = orchestrator.execute_incremental(work_request, checkpoint_callback)
        
        assert result["success"] is False
        assert result["aborted"] is True
        assert "rejected" in result["reason"]
    
    def test_requirement_to_test_name(self, orchestrator):
        """Test conversion of requirement to test method name"""
        requirement = "User can login with valid credentials"
        test_name = orchestrator._requirement_to_test_name(requirement, 1)
        
        assert test_name.startswith("test_1_")
        assert "user" in test_name
        assert "login" in test_name
    
    def test_requirement_to_method_name(self, orchestrator):
        """Test conversion of requirement to method name"""
        requirement = "Calculate the sum of two numbers"
        method_name = orchestrator._requirement_to_method_name(requirement)
        
        assert method_name.startswith("calculate")
        assert "_data" in method_name
    
    def test_error_handling_in_chunking(self, orchestrator):
        """Test graceful error handling in chunk creation"""
        # Invalid work request (missing required fields)
        work_request = {}
        
        chunks = orchestrator.break_into_chunks(work_request)
        
        # Should return at least one chunk with defaults (error recovery)
        assert len(chunks) >= 1
        assert chunks[0].chunk_type == "skeleton"
        # Orchestrator provides defaults: "Feature", empty requirements
        assert chunks[0].description == "Create test file skeleton for Feature"
    
    def test_chunk_token_limits(self, orchestrator):
        """Test that chunks respect token limits"""
        work_request = {
            "feature_name": "UserAuth",
            "test_file_path": "tests/test_auth.py",
            "implementation_file_path": "src/auth.py",
            "requirements": ["User can login"],
            "existing_tests": 0
        }
        
        chunks = orchestrator.break_into_chunks(work_request)
        
        # Verify token estimates are within limits
        test_chunks = [c for c in chunks if c.chunk_type == "test"]
        method_chunks = [c for c in chunks if c.chunk_type == "method"]
        
        for chunk in test_chunks:
            assert chunk.estimated_tokens <= orchestrator.MAX_TEST_TOKENS
        
        for chunk in method_chunks:
            assert chunk.estimated_tokens <= orchestrator.MAX_METHOD_TOKENS
