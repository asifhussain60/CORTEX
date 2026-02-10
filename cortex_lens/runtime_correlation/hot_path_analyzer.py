"""
Hot Path Analyzer

Identifies frequently executed code paths from test execution data to guide
performance optimization efforts.

Author: CORTEX Architect
Phase: Phase 66 S4
"""

from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict, Counter


class HotPathAnalyzer:
    """
    Analyze execution data to identify hot paths.
    
    Capabilities:
    - Frequent execution path identification
    - Execution frequency ranking
    - Performance bottleneck detection
    - Hot path scoring (frequency + duration)
    - Module-level aggregation
    - Critical path identification
    - Call pattern detection
    - Execution heatmap generation
    - Optimization candidate selection
    
    Usage:
        >>> analyzer = HotPathAnalyzer()
        >>> hot_paths = analyzer.identify_frequently_executed_paths(data, threshold=100)
        >>> bottlenecks = analyzer.identify_performance_bottlenecks(data)
    """
    
    def __init__(self):
        self.critical_modules = ["security", "auth", "core", "critical"]
    
    def identify_frequently_executed_paths(
        self,
        execution_data: List[Dict[str, Any]],
        threshold: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Identify frequently executed code paths.
        
        Args:
            execution_data: List of execution records
            threshold: Minimum call count to be considered hot
            
        Returns:
            List of hot path dictionaries
        """
        hot_paths = []
        
        for record in execution_data:
            call_count = record.get("call_count", 0)
            
            if call_count >= threshold:
                hot_paths.append(record)
        
        return hot_paths
    
    def rank_by_execution_frequency(
        self,
        execution_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rank paths by execution frequency.
        
        Args:
            execution_data: List of execution records
            
        Returns:
            Sorted list with rank assigned
        """
        # Sort by call_count descending
        sorted_data = sorted(
            execution_data,
            key=lambda x: x.get("call_count", 0),
            reverse=True
        )
        
        # Assign ranks
        ranked = []
        for i, record in enumerate(sorted_data, 1):
            record_copy = record.copy()
            record_copy["rank"] = i
            ranked.append(record_copy)
        
        return ranked
    
    def identify_performance_bottlenecks(
        self,
        execution_data: List[Dict[str, Any]],
        threshold_ms: float = 1000.0
    ) -> List[Dict[str, Any]]:
        """
        Identify performance bottlenecks from duration data.
        
        Bottleneck = average duration > threshold
        
        Args:
            execution_data: List with call_count and total_duration
            threshold_ms: Minimum average duration in milliseconds
            
        Returns:
            List of bottleneck dictionaries
        """
        bottlenecks = []
        
        for record in execution_data:
            call_count = record.get("call_count", 0)
            total_duration = record.get("total_duration", 0.0)
            
            if call_count > 0:
                avg_duration_ms = (total_duration / call_count) * 1000
                
                if avg_duration_ms >= threshold_ms:
                    bottleneck = record.copy()
                    bottleneck["avg_duration_ms"] = avg_duration_ms
                    bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    def calculate_hot_path_score(self, path_data: Dict[str, Any]) -> float:
        """
        Calculate hot path score combining frequency and duration.
        
        Score = (call_count * 0.6) + (total_duration * 100 * 0.4)
        
        Args:
            path_data: Path execution data
            
        Returns:
            Hot path score
        """
        call_count = path_data.get("call_count", 0)
        total_duration = path_data.get("total_duration", 0.0)
        
        # Normalize and weight
        frequency_score = call_count * 0.6
        duration_score = total_duration * 100 * 0.4
        
        return frequency_score + duration_score
    
    def aggregate_by_module(
        self,
        execution_data: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate hot paths by module.
        
        Args:
            execution_data: List of execution records
            
        Returns:
            Dictionary of module → aggregated statistics
        """
        from pathlib import Path
        
        module_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"total_calls": 0, "functions": []}
        )
        
        for record in execution_data:
            file_path = record.get("file", "")
            call_count = record.get("call_count", 0)
            
            # Extract module (directory)
            module = str(Path(file_path).parent)
            
            module_stats[module]["total_calls"] += call_count
            module_stats[module]["functions"].append(record.get("function", ""))
        
        return dict(module_stats)
    
    def identify_critical_paths(
        self,
        execution_data: List[Dict[str, Any]],
        min_calls: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Identify critical paths (hot + important files).
        
        Critical = frequently executed AND in critical modules (security, core, etc.)
        
        Args:
            execution_data: List of execution records
            min_calls: Minimum call threshold
            
        Returns:
            List of critical path dictionaries
        """
        critical_paths = []
        
        for record in execution_data:
            call_count = record.get("call_count", 0)
            file_path = record.get("file", "").lower()
            
            if call_count >= min_calls:
                # Check if in critical module
                is_critical = any(
                    keyword in file_path
                    for keyword in self.critical_modules
                )
                
                if is_critical:
                    critical_paths.append(record)
        
        return critical_paths
    
    def detect_call_patterns(
        self,
        call_sequences: List[List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Detect common call patterns from execution traces.
        
        Args:
            call_sequences: List of function call sequences
            
        Returns:
            List of detected patterns sorted by frequency
        """
        # Convert sequences to tuples for counting
        pattern_counter: Counter = Counter()
        
        for sequence in call_sequences:
            pattern = tuple(sequence)
            pattern_counter[pattern] += 1
        
        # Convert to list sorted by frequency
        patterns = []
        for pattern, frequency in pattern_counter.most_common():
            patterns.append({
                "pattern": list(pattern),
                "frequency": frequency
            })
        
        return patterns
    
    def build_execution_heatmap(
        self,
        execution_data: List[Dict[str, Any]]
    ) -> Dict[str, Dict[int, int]]:
        """
        Build execution heatmap for visualization.
        
        Args:
            execution_data: List with file, line, execution_count
            
        Returns:
            Nested dictionary: file → line → execution_count
        """
        heatmap: Dict[str, Dict[int, int]] = defaultdict(dict)
        
        for record in execution_data:
            file_path = record.get("file", "")
            line = record.get("line", 0)
            count = record.get("execution_count", 0)
            
            heatmap[file_path][line] = count
        
        return dict(heatmap)
    
    def identify_optimization_candidates(
        self,
        execution_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify code that would benefit from optimization.
        
        Candidates = high frequency + high duration + high complexity
        
        Args:
            execution_data: List with call_count, avg_duration, complexity
            
        Returns:
            List of optimization candidate dictionaries
        """
        candidates = []
        
        for record in execution_data:
            call_count = record.get("call_count", 0)
            avg_duration = record.get("avg_duration", 0.0)
            complexity = record.get("complexity", 0)
            
            # Score optimization potential
            # High impact = frequently called, slow, complex
            impact_score = (
                (call_count / 1000) * 0.4 +  # Frequency
                (avg_duration * 10) * 0.4 +   # Duration
                (complexity / 20) * 0.2        # Complexity
            )
            
            if impact_score > 0.5:  # Threshold for optimization
                candidate = record.copy()
                candidate["optimization_impact_score"] = impact_score
                candidates.append(candidate)
        
        # Sort by impact score descending
        candidates.sort(
            key=lambda x: x["optimization_impact_score"],
            reverse=True
        )
        
        return candidates
