"""
CORE-035: Output Determinism Verification

Ensures consistent, deterministic output across multiple executions:
- Output hash tracking and verification
- Determinism verification (same input = same output)
- Non-determinism detection and logging
- Variance analysis
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Hashable
import hashlib


class DeterminismStatus(Enum):
    """Status of determinism verification."""
    DETERMINISTIC = "deterministic"
    NON_DETERMINISTIC = "non_deterministic"
    PARTIALLY_DETERMINISTIC = "partially_deterministic"
    UNKNOWN = "unknown"


@dataclass
class ExecutionRecord:
    """Record of a single execution."""
    input_hash: str
    output_hash: str
    output_value: str
    execution_time: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DeterminismAnalysis:
    """Analysis of output determinism."""
    input_value: str
    input_hash: str
    execution_count: int
    unique_outputs: int
    output_hashes: List[str] = field(default_factory=list)
    determinism_status: DeterminismStatus = DeterminismStatus.UNKNOWN
    variance_percentage: float = 0.0
    is_deterministic: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Result:
    """Generic result type for error handling."""
    success: bool
    value: Optional[Any] = None
    error: Optional[str] = None
    
    @classmethod
    def ok(cls, value: Any) -> Result:
        """Create successful result."""
        return cls(success=True, value=value)
    
    @classmethod
    def error(cls, error: str) -> Result:
        """Create error result."""
        return cls(success=False, error=error)


class OutputDeterminismVerifier:
    """Verifies output determinism across executions."""
    
    def __init__(self):
        """Initialize verifier."""
        self.execution_history: Dict[str, List[ExecutionRecord]] = {}
        self.analysis_results: List[DeterminismAnalysis] = []
    
    def _hash_value(self, value: Any) -> str:
        """
        Hash a value to string.
        
        Args:
            value: Value to hash.
            
        Returns:
            Hex digest of hash.
        """
        value_str = str(value)
        return hashlib.sha256(value_str.encode()).hexdigest()
    
    def record_execution(
        self,
        input_value: Any,
        output_value: Any,
        execution_time: float = 0.0
    ) -> None:
        """
        Record an execution.
        
        Args:
            input_value: Input to the execution.
            output_value: Output from execution.
            execution_time: Time taken for execution.
        """
        input_hash = self._hash_value(input_value)
        output_hash = self._hash_value(output_value)
        
        record = ExecutionRecord(
            input_hash=input_hash,
            output_hash=output_hash,
            output_value=str(output_value),
            execution_time=execution_time
        )
        
        if input_hash not in self.execution_history:
            self.execution_history[input_hash] = []
        
        self.execution_history[input_hash].append(record)
    
    def verify_determinism(self, input_value: Any) -> Result:
        """
        Verify determinism for a given input.
        
        Args:
            input_value: Input to check.
            
        Returns:
            Result with DeterminismAnalysis.
        """
        try:
            input_hash = self._hash_value(input_value)
            
            if input_hash not in self.execution_history:
                return Result.error(f"No execution history for input")
            
            records = self.execution_history[input_hash]
            
            if len(records) == 0:
                return Result.error("No execution records found")
            
            # Get unique output hashes
            unique_hashes = set(r.output_hash for r in records)
            
            # Determine determinism status
            if len(unique_hashes) == 1:
                status = DeterminismStatus.DETERMINISTIC
                is_deterministic = True
                variance = 0.0
            elif len(unique_hashes) < len(records) / 2:
                status = DeterminismStatus.PARTIALLY_DETERMINISTIC
                is_deterministic = False
                variance = (len(unique_hashes) / len(records)) * 100
            else:
                status = DeterminismStatus.NON_DETERMINISTIC
                is_deterministic = False
                variance = (len(unique_hashes) / len(records)) * 100
            
            analysis = DeterminismAnalysis(
                input_value=str(input_value),
                input_hash=input_hash,
                execution_count=len(records),
                unique_outputs=len(unique_hashes),
                output_hashes=list(unique_hashes),
                determinism_status=status,
                variance_percentage=variance,
                is_deterministic=is_deterministic
            )
            
            self.analysis_results.append(analysis)
            return Result.ok(analysis)
            
        except Exception as e:
            return Result.error(f"Verification failed: {str(e)}")
    
    def batch_verify(self, input_values: Optional[List[Any]] = None) -> Result:
        """
        Verify determinism for multiple inputs.
        
        Args:
            input_values: List of input values to verify.
            
        Returns:
            Result with list of analyses.
        """
        try:
            inputs_to_check = input_values or list(
                set(r.input_hash for records in self.execution_history.values() for r in records)
            )
            
            if not inputs_to_check and not input_values:
                # Fall back to checking all unique inputs
                all_input_hashes = set()
                for records in self.execution_history.values():
                    for record in records:
                        all_input_hashes.add(record.input_hash)
                
                results = []
                for input_hash in all_input_hashes:
                    # Find an original input value for this hash
                    for orig_input, records in self.execution_history.items():
                        if orig_input == input_hash:
                            result = self.verify_determinism(records[0].input_hash)
                            if result.success:
                                results.append(result.value)
                            break
            else:
                results = []
                for input_val in inputs_to_check:
                    result = self.verify_determinism(input_val)
                    if result.success:
                        results.append(result.value)
            
            return Result.ok(results)
            
        except Exception as e:
            return Result.error(f"Batch verification failed: {str(e)}")
    
    def get_determinism_report(self) -> Dict[str, Any]:
        """
        Get report on overall determinism.
        
        Returns:
            Dictionary with determinism statistics.
        """
        if not self.analysis_results:
            return {
                "total_analyses": 0,
                "deterministic_count": 0,
                "non_deterministic_count": 0,
                "determinism_percentage": 0.0,
            }
        
        deterministic = sum(
            1 for a in self.analysis_results if a.is_deterministic
        )
        
        return {
            "total_analyses": len(self.analysis_results),
            "deterministic_count": deterministic,
            "non_deterministic_count": len(self.analysis_results) - deterministic,
            "determinism_percentage": (deterministic / len(self.analysis_results)) * 100,
            "average_variance": sum(a.variance_percentage for a in self.analysis_results) / len(self.analysis_results),
        }
    
    def detect_non_determinism(self) -> Result:
        """
        Detect and report non-deterministic executions.
        
        Returns:
            Result with list of non-deterministic analyses.
        """
        try:
            non_deterministic = [
                a for a in self.analysis_results 
                if a.determinism_status != DeterminismStatus.DETERMINISTIC
            ]
            
            report = {
                "total_non_deterministic": len(non_deterministic),
                "analyses": non_deterministic,
                "affected_inputs": len(set(a.input_hash for a in non_deterministic)),
            }
            
            return Result.ok(report)
            
        except Exception as e:
            return Result.error(f"Non-determinism detection failed: {str(e)}")
    
    def compare_outputs(
        self,
        output1: Any,
        output2: Any
    ) -> Dict[str, Any]:
        """
        Compare two outputs.
        
        Args:
            output1: First output.
            output2: Second output.
            
        Returns:
            Comparison results.
        """
        hash1 = self._hash_value(output1)
        hash2 = self._hash_value(output2)
        
        return {
            "output1": str(output1),
            "output2": str(output2),
            "hash1": hash1,
            "hash2": hash2,
            "match": hash1 == hash2,
            "output1_length": len(str(output1)),
            "output2_length": len(str(output2)),
        }
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """
        Get statistics on all executions.
        
        Returns:
            Dictionary with execution statistics.
        """
        if not self.execution_history:
            return {
                "total_executions": 0,
                "total_inputs": 0,
                "average_executions_per_input": 0.0,
            }
        
        total_records = sum(len(r) for r in self.execution_history.values())
        
        return {
            "total_executions": total_records,
            "total_inputs": len(self.execution_history),
            "average_executions_per_input": total_records / len(self.execution_history),
            "min_executions": min(len(r) for r in self.execution_history.values()),
            "max_executions": max(len(r) for r in self.execution_history.values()),
        }
    
    def identify_variance_sources(self) -> Result:
        """
        Identify sources of variance in outputs.
        
        Returns:
            Result with variance analysis.
        """
        try:
            variance_sources = []
            
            for analysis in self.analysis_results:
                if analysis.unique_outputs > 1:
                    variance_sources.append({
                        "input": analysis.input_value,
                        "unique_outputs": analysis.unique_outputs,
                        "variance_percentage": analysis.variance_percentage,
                        "status": analysis.determinism_status.value,
                    })
            
            return Result.ok({
                "variance_sources": variance_sources,
                "total_variance_sources": len(variance_sources),
            })
            
        except Exception as e:
            return Result.error(f"Variance analysis failed: {str(e)}")
