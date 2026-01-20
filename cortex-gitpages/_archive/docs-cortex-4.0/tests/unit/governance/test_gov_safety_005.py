"""
Test suite for CORE-035: Output Determinism Verification.

Validates:
- Output hash tracking and verification
- Determinism verification for same inputs producing same outputs
- Non-determinism detection and logging
- Variance analysis
"""

import pytest
from src.core.governance.output_determinism import (
    OutputDeterminismVerifier,
    ExecutionRecord,
    DeterminismAnalysis,
    DeterminismStatus,
)


class TestExecutionRecord:
    """Tests for execution records."""
    
    def test_create_execution_record(self):
        """Test creating an execution record."""
        record = ExecutionRecord(
            input_hash="hash_in",
            output_hash="hash_out",
            output_value="output",
            execution_time=0.1
        )
        assert record.input_hash == "hash_in"
        assert record.output_value == "output"


class TestOutputDeterminismVerifier:
    """Tests for output determinism verifier."""
    
    def test_verifier_initialization(self):
        """Test verifier initialization."""
        verifier = OutputDeterminismVerifier()
        assert len(verifier.execution_history) == 0
        assert len(verifier.analysis_results) == 0
    
    def test_hash_value(self):
        """Test value hashing."""
        verifier = OutputDeterminismVerifier()
        
        hash1 = verifier._hash_value("test")
        hash2 = verifier._hash_value("test")
        hash3 = verifier._hash_value("different")
        
        assert hash1 == hash2  # Same input = same hash
        assert hash1 != hash3  # Different input = different hash
    
    def test_record_execution(self):
        """Test recording an execution."""
        verifier = OutputDeterminismVerifier()
        
        verifier.record_execution(
            input_value="input1",
            output_value="output1"
        )
        
        assert len(verifier.execution_history) > 0
    
    def test_record_multiple_executions_same_input(self):
        """Test recording multiple executions with same input."""
        verifier = OutputDeterminismVerifier()
        
        verifier.record_execution("input", "output1")
        verifier.record_execution("input", "output1")
        verifier.record_execution("input", "output1")
        
        # Should have one key in history
        assert len(verifier.execution_history) == 1
        
        # Get the records
        records_list = list(verifier.execution_history.values())
        assert len(records_list[0]) == 3


class TestDeterminismVerification:
    """Tests for determinism verification."""
    
    def test_verify_deterministic_output(self):
        """Test verification of deterministic output."""
        verifier = OutputDeterminismVerifier()
        
        # Record same input with same output multiple times
        for _ in range(3):
            verifier.record_execution("input", "output")
        
        result = verifier.verify_determinism("input")
        
        assert result.success
        assert result.value.is_deterministic
        assert result.value.determinism_status == DeterminismStatus.DETERMINISTIC
    
    def test_verify_non_deterministic_output(self):
        """Test verification of non-deterministic output."""
        verifier = OutputDeterminismVerifier()
        
        # Record same input with different outputs
        verifier.record_execution("input", "output1")
        verifier.record_execution("input", "output2")
        verifier.record_execution("input", "output3")
        
        result = verifier.verify_determinism("input")
        
        assert result.success
        assert not result.value.is_deterministic
        assert result.value.determinism_status == DeterminismStatus.NON_DETERMINISTIC
    
    def test_verify_partially_deterministic_output(self):
        """Test verification of partially deterministic output."""
        verifier = OutputDeterminismVerifier()
        
        # Record same input with mostly same output
        verifier.record_execution("input", "output1")
        verifier.record_execution("input", "output1")
        verifier.record_execution("input", "output2")
        verifier.record_execution("input", "output1")
        
        result = verifier.verify_determinism("input")
        
        assert result.success
        # Should detect some variation
        assert result.value.unique_outputs > 1
    
    def test_verify_nonexistent_input(self):
        """Test verification for non-existent input."""
        verifier = OutputDeterminismVerifier()
        result = verifier.verify_determinism("nonexistent")
        
        assert not result.success


class TestBatchVerification:
    """Tests for batch determinism verification."""
    
    def test_batch_verify_multiple_inputs(self):
        """Test batch verification of multiple inputs."""
        verifier = OutputDeterminismVerifier()
        
        # Record deterministic outputs
        verifier.record_execution("input1", "output1")
        verifier.record_execution("input1", "output1")
        
        verifier.record_execution("input2", "output2")
        verifier.record_execution("input2", "output2")
        
        result = verifier.batch_verify(["input1", "input2"])
        
        assert result.success
        assert len(result.value) == 2


class TestDeterminismReport:
    """Tests for determinism reporting."""
    
    def test_get_determinism_report_empty(self):
        """Test report with no analyses."""
        verifier = OutputDeterminismVerifier()
        report = verifier.get_determinism_report()
        
        assert report["total_analyses"] == 0
    
    def test_get_determinism_report_with_data(self):
        """Test report with determinism analyses."""
        verifier = OutputDeterminismVerifier()
        
        # Create deterministic execution
        verifier.record_execution("input1", "output")
        verifier.record_execution("input1", "output")
        verifier.verify_determinism("input1")
        
        # Create non-deterministic execution
        verifier.record_execution("input2", "output1")
        verifier.record_execution("input2", "output2")
        verifier.verify_determinism("input2")
        
        report = verifier.get_determinism_report()
        
        assert report["total_analyses"] == 2
        assert report["deterministic_count"] == 1
        assert report["non_deterministic_count"] == 1


class TestNonDeterminismDetection:
    """Tests for non-determinism detection."""
    
    def test_detect_non_determinism(self):
        """Test detecting non-deterministic outputs."""
        verifier = OutputDeterminismVerifier()
        
        # Create deterministic
        verifier.record_execution("input1", "output")
        verifier.record_execution("input1", "output")
        verifier.verify_determinism("input1")
        
        # Create non-deterministic
        verifier.record_execution("input2", "output1")
        verifier.record_execution("input2", "output2")
        verifier.verify_determinism("input2")
        
        result = verifier.detect_non_determinism()
        
        assert result.success
        assert result.value["total_non_deterministic"] == 1


class TestOutputComparison:
    """Tests for output comparison."""
    
    def test_compare_identical_outputs(self):
        """Test comparing identical outputs."""
        verifier = OutputDeterminismVerifier()
        
        comparison = verifier.compare_outputs("output", "output")
        
        assert comparison["match"] == True
    
    def test_compare_different_outputs(self):
        """Test comparing different outputs."""
        verifier = OutputDeterminismVerifier()
        
        comparison = verifier.compare_outputs("output1", "output2")
        
        assert comparison["match"] == False
        assert comparison["hash1"] != comparison["hash2"]
    
    def test_compare_different_types(self):
        """Test comparing different types."""
        verifier = OutputDeterminismVerifier()
        
        comparison = verifier.compare_outputs(123, "123")
        
        # String representations match
        assert comparison["output1"] == comparison["output2"]


class TestExecutionStatistics:
    """Tests for execution statistics."""
    
    def test_execution_statistics_empty(self):
        """Test statistics with no executions."""
        verifier = OutputDeterminismVerifier()
        stats = verifier.get_execution_statistics()
        
        assert stats["total_executions"] == 0
    
    def test_execution_statistics_with_data(self):
        """Test statistics with execution data."""
        verifier = OutputDeterminismVerifier()
        
        verifier.record_execution("input1", "output1")
        verifier.record_execution("input1", "output1")
        verifier.record_execution("input2", "output2")
        
        stats = verifier.get_execution_statistics()
        
        assert stats["total_executions"] == 3
        assert stats["total_inputs"] == 2


class TestVarianceAnalysis:
    """Tests for variance source identification."""
    
    def test_identify_variance_sources(self):
        """Test identifying variance sources."""
        verifier = OutputDeterminismVerifier()
        
        # Create non-deterministic execution
        verifier.record_execution("input", "output1")
        verifier.record_execution("input", "output2")
        verifier.verify_determinism("input")
        
        result = verifier.identify_variance_sources()
        
        assert result.success
        assert result.value["total_variance_sources"] > 0


class TestIntegration:
    """Integration tests for output determinism verification."""
    
    def test_end_to_end_determinism_workflow(self):
        """Test complete determinism verification workflow."""
        verifier = OutputDeterminismVerifier()
        
        # Simulate multiple function calls with same input
        test_input = "calculate_total"
        test_outputs = ["42", "42", "42"]
        
        for output in test_outputs:
            verifier.record_execution(test_input, output, execution_time=0.1)
        
        # Verify determinism
        result = verifier.verify_determinism(test_input)
        assert result.success
        assert result.value.is_deterministic
        
        # Get statistics
        stats = verifier.get_execution_statistics()
        assert stats["total_executions"] == 3
        
        # Get report
        report = verifier.get_determinism_report()
        assert report["deterministic_count"] == 1
    
    def test_end_to_end_non_determinism_detection(self):
        """Test detecting non-deterministic behavior."""
        verifier = OutputDeterminismVerifier()
        
        # Simulate function with varying outputs
        test_input = "generate_random"
        test_outputs = ["12345", "67890", "54321", "12345"]
        
        for output in test_outputs:
            verifier.record_execution(test_input, output)
        
        # Verify non-determinism
        result = verifier.verify_determinism(test_input)
        assert result.success
        assert not result.value.is_deterministic
        
        # Detect non-determinism
        detection = verifier.detect_non_determinism()
        assert detection.success
        assert detection.value["total_non_deterministic"] > 0
    
    def test_multiple_inputs_mixed_determinism(self):
        """Test multiple inputs with mixed determinism."""
        verifier = OutputDeterminismVerifier()
        
        # Input 1: Deterministic
        for _ in range(3):
            verifier.record_execution("input1", "consistent_output")
        
        # Input 2: Non-deterministic
        verifier.record_execution("input2", "output_a")
        verifier.record_execution("input2", "output_b")
        
        # Verify both
        verifier.verify_determinism("input1")
        verifier.verify_determinism("input2")
        
        # Check report
        report = verifier.get_determinism_report()
        assert report["total_analyses"] == 2
        assert report["deterministic_count"] == 1
        assert report["non_deterministic_count"] == 1
