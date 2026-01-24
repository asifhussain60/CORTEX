"""Tier2 Governance: Output Determinism

Implements CORE-035: Output Determinism Verification.
Tracks execution outputs and verifies deterministic behavior.

Author: CORTEX Framework
"""

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime


class DeterminismStatus(Enum):
    """Determinism status."""
    DETERMINISTIC = "deterministic"
    NON_DETERMINISTIC = "non_deterministic"
    UNKNOWN = "unknown"


@dataclass
class ExecutionRecord:
    """Execution record for determinism tracking."""
    input_hash: str
    output_hash: str
    output_value: Any
    execution_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict = field(default_factory=dict)


@dataclass
class DeterminismAnalysis:
    """Determinism analysis result."""
    is_deterministic: bool
    consistency_score: float
    determinism_status: DeterminismStatus
    unique_outputs: int = 1
    total_executions: int = 1
    deviation_count: int = 0
    variance_percentage: float = 0.0


@dataclass
class Result:
    """Generic result wrapper."""
    success: bool
    value: Any = None
    error: Optional[str] = None


class OutputDeterminismVerifier:
    """Verify output determinism.
    
    Tracks execution history and analyzes whether the same inputs
    consistently produce the same outputs.
    """
    
    def __init__(self):
        """Initialize the verifier."""
        self.execution_history: Dict[str, List[ExecutionRecord]] = {}
        self.analysis_results: Dict[str, DeterminismAnalysis] = {}
    
    def _hash_value(self, value: Any) -> str:
        """Generate hash for a value.
        
        Args:
            value: Value to hash
            
        Returns:
            Hash string
        """
        value_str = json.dumps(value, sort_keys=True, default=str)
        return hashlib.sha256(value_str.encode()).hexdigest()
    
    def record_execution(
        self,
        input_value: Any,
        output_value: Any,
        execution_time: float = 0.0
    ) -> None:
        """Record an execution.
        
        Args:
            input_value: Input to the execution
            output_value: Output from the execution
            execution_time: Execution time in seconds
        """
        input_hash = self._hash_value(input_value)
        output_hash = self._hash_value(output_value)
        
        record = ExecutionRecord(
            input_hash=input_hash,
            output_hash=output_hash,
            output_value=output_value,
            execution_time=execution_time
        )
        
        if input_hash not in self.execution_history:
            self.execution_history[input_hash] = []
        
        self.execution_history[input_hash].append(record)
    
    def verify_determinism(self, input_value: Any) -> Result:
        """Verify determinism for an input.
        
        Args:
            input_value: Input to verify
            
        Returns:
            Result with DeterminismAnalysis
        """
        input_hash = self._hash_value(input_value)
        
        if input_hash not in self.execution_history:
            return Result(success=False, error="No execution history for input")
        
        records = self.execution_history[input_hash]
        output_hashes = [r.output_hash for r in records]
        unique_hashes = set(output_hashes)
        
        is_deterministic = len(unique_hashes) == 1
        consistency_score = 1.0 if is_deterministic else (1.0 - (len(unique_hashes) - 1) / len(records))
        status = DeterminismStatus.DETERMINISTIC if is_deterministic else DeterminismStatus.NON_DETERMINISTIC
        
        analysis = DeterminismAnalysis(
            is_deterministic=is_deterministic,
            consistency_score=consistency_score,
            determinism_status=status,
            unique_outputs=len(unique_hashes),
            total_executions=len(records),
            deviation_count=len(records) - output_hashes.count(output_hashes[0]),
            variance_percentage=(len(unique_hashes) - 1) / len(records) * 100 if len(records) > 0 else 0
        )
        
        self.analysis_results[input_hash] = analysis
        return Result(success=True, value=analysis)
    
    def batch_verify(self, input_values: List[Any]) -> Result:
        """Verify determinism for multiple inputs.
        
        Args:
            input_values: List of inputs to verify
            
        Returns:
            Result with list of DeterminismAnalysis
        """
        results = []
        for input_value in input_values:
            result = self.verify_determinism(input_value)
            if result.success:
                results.append(result.value)
        
        return Result(success=True, value=results)
    
    def get_determinism_report(self) -> Dict[str, Any]:
        """Get determinism report.
        
        Returns:
            Report dictionary
        """
        total = len(self.analysis_results)
        deterministic = sum(1 for a in self.analysis_results.values() if a.is_deterministic)
        non_deterministic = total - deterministic
        
        return {
            "total_analyses": total,
            "deterministic_count": deterministic,
            "non_deterministic_count": non_deterministic,
            "deterministic_percentage": (deterministic / total * 100) if total > 0 else 0,
            "analyses": list(self.analysis_results.values())
        }
    
    def detect_non_determinism(self) -> Result:
        """Detect non-deterministic executions.
        
        Returns:
            Result with non-determinism summary
        """
        non_deterministic = [
            a for a in self.analysis_results.values()
            if not a.is_deterministic
        ]
        
        return Result(
            success=True,
            value={
                "total_non_deterministic": len(non_deterministic),
                "non_deterministic_inputs": [
                    h for h, a in self.analysis_results.items()
                    if not a.is_deterministic
                ]
            }
        )
    
    def compare_outputs(self, output1: Any, output2: Any) -> Dict[str, Any]:
        """Compare two outputs.
        
        Args:
            output1: First output
            output2: Second output
            
        Returns:
            Comparison result
        """
        hash1 = self._hash_value(output1)
        hash2 = self._hash_value(output2)
        
        return {
            "match": hash1 == hash2,
            "hash1": hash1,
            "hash2": hash2,
            "output1": str(output1),
            "output2": str(output2)
        }
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics.
        
        Returns:
            Statistics dictionary
        """
        total_executions = sum(len(records) for records in self.execution_history.values())
        total_inputs = len(self.execution_history)
        
        return {
            "total_executions": total_executions,
            "total_inputs": total_inputs,
            "average_executions_per_input": (total_executions / total_inputs) if total_inputs > 0 else 0
        }
    
    def identify_variance_sources(self) -> Result:
        """Identify sources of variance.
        
        Returns:
            Result with variance sources
        """
        variance_sources = []
        
        for input_hash, analysis in self.analysis_results.items():
            if not analysis.is_deterministic:
                variance_sources.append({
                    "input_hash": input_hash,
                    "unique_outputs": analysis.unique_outputs,
                    "variance_percentage": analysis.variance_percentage
                })
        
        return Result(
            success=True,
            value={
                "total_variance_sources": len(variance_sources),
                "sources": variance_sources
            }
        )


__all__ = [
    "ExecutionRecord",
    "DeterminismAnalysis",
    "OutputDeterminismVerifier",
    "DeterminismStatus",
    "Result"
]
