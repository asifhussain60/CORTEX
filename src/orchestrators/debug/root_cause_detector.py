"""
Root Cause Detector - Identify root causes from analyzed errors

Combines error data, review findings, and debug logs to generate
ranked hypotheses about the root cause of bugs.

Author: Asif Hussain
Created: January 4, 2026
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class RootCauseDetector:
    """Detects root causes using pattern matching and analysis."""
    
    # Common root cause patterns
    PATTERNS = {
        "missing_import": {
            "keywords": ["ImportError", "ModuleNotFoundError", "no module named"],
            "confidence_boost": 0.9,
            "category": "missing_dependency"
        },
        "undefined_variable": {
            "keywords": ["NameError", "not defined", "undefined"],
            "confidence_boost": 0.85,
            "category": "logic"
        },
        "type_mismatch": {
            "keywords": ["TypeError", "expected", "got", "wrong type"],
            "confidence_boost": 0.8,
            "category": "type_mismatch"
        },
        "missing_attribute": {
            "keywords": ["AttributeError", "has no attribute", "object has no"],
            "confidence_boost": 0.8,
            "category": "type_mismatch"
        },
        "null_reference": {
            "keywords": ["NoneType", "None", "null"],
            "confidence_boost": 0.75,
            "category": "logic"
        },
        "incorrect_logic": {
            "keywords": ["AssertionError", "assert", "expected", "but got"],
            "confidence_boost": 0.7,
            "category": "logic"
        },
        "file_not_found": {
            "keywords": ["FileNotFoundError", "No such file", "cannot find"],
            "confidence_boost": 0.85,
            "category": "io"
        },
    }
    
    def __init__(self):
        """Initialize root cause detector."""
        self.logger = logger
    
    def analyze(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Perform holistic root cause analysis.
        
        Implements: DBG-006 (Holistic Root Cause Analysis)
        
        Args:
            analysis_data: Combined data from error, review, logs, tests
            
        Returns:
            Ranked list of root cause hypotheses with confidence scores
        """
        self.logger.info("Performing root cause analysis")
        
        error_data = analysis_data.get("error_data", {})
        review_findings = analysis_data.get("review_findings", {})
        debug_logs = analysis_data.get("debug_logs", [])
        test_failures = analysis_data.get("test_failures", [])
        
        # Generate hypotheses
        hypotheses = []
        
        # Pattern-based hypothesis generation
        pattern_hypotheses = self._generate_pattern_hypotheses(error_data)
        hypotheses.extend(pattern_hypotheses)
        
        # Review-based hypothesis generation
        if review_findings:
            review_hypotheses = self._generate_review_hypotheses(
                error_data, review_findings
            )
            hypotheses.extend(review_hypotheses)
        
        # Code flow analysis (if debug logs available)
        if debug_logs:
            flow_hypotheses = self._analyze_code_flow(error_data, debug_logs)
            hypotheses.extend(flow_hypotheses)
        
        # Test correlation analysis
        if test_failures:
            test_hypotheses = self._analyze_test_correlations(
                error_data, test_failures
            )
            hypotheses.extend(test_hypotheses)
        
        # Rank hypotheses by confidence
        ranked_hypotheses = self._rank_hypotheses(hypotheses)
        
        self.logger.info(f"Generated {len(ranked_hypotheses)} root cause hypotheses")
        
        return ranked_hypotheses[:5]  # Return top 5
    
    def _generate_pattern_hypotheses(
        self,
        error_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate hypotheses based on error patterns."""
        hypotheses = []
        
        error_type = error_data.get("error_type", "")
        error_message = error_data.get("raw_data", {}).get("error_message", "")
        stack_trace = error_data.get("raw_data", {}).get("stack_trace", "")
        
        combined_text = f"{error_type} {error_message} {stack_trace}".lower()
        
        # Check against known patterns
        for pattern_name, pattern_data in self.PATTERNS.items():
            matches = sum(
                1 for keyword in pattern_data["keywords"]
                if keyword.lower() in combined_text
            )
            
            if matches > 0:
                confidence = pattern_data["confidence_boost"] * (
                    matches / len(pattern_data["keywords"])
                )
                
                hypothesis = {
                    "hypothesis": self._pattern_to_hypothesis(pattern_name),
                    "confidence": confidence,
                    "source": "pattern_matching",
                    "pattern": pattern_name,
                    "category": pattern_data["category"],
                    "evidence": {
                        "matched_keywords": [
                            kw for kw in pattern_data["keywords"]
                            if kw.lower() in combined_text
                        ],
                        "error_type": error_type,
                    }
                }
                hypotheses.append(hypothesis)
        
        return hypotheses
    
    def _generate_review_hypotheses(
        self,
        error_data: Dict[str, Any],
        review_findings: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate hypotheses from review findings."""
        hypotheses = []
        
        # Get critical and blocker findings
        critical_findings = review_findings.get("classified_findings", {}).get("CRITICAL", [])
        blocker_findings = review_findings.get("classified_findings", {}).get("BLOCKER", [])
        
        # Correlate findings with error components
        affected_components = error_data.get("affected_components", [])
        
        for finding in critical_findings + blocker_findings:
            # Check if finding relates to affected components
            relevance_score = self._calculate_relevance(
                finding, affected_components
            )
            
            if relevance_score > 0.3:
                hypothesis = {
                    "hypothesis": f"Architectural issue: {finding.get('message', 'Unknown')}",
                    "confidence": 0.6 * relevance_score,
                    "source": "review_findings",
                    "category": finding.get("category", "architecture"),
                    "evidence": {
                        "finding_severity": finding.get("severity"),
                        "relevance_score": relevance_score,
                    }
                }
                hypotheses.append(hypothesis)
        
        return hypotheses
    
    def _analyze_code_flow(
        self,
        error_data: Dict[str, Any],
        debug_logs: List[str]
    ) -> List[Dict[str, Any]]:
        """Analyze code flow from debug logs."""
        hypotheses = []
        
        # Look for unexpected execution paths
        # Look for null/None values appearing
        # Look for repeated error patterns
        
        # Simple heuristic: if logs show None values before error
        none_pattern = any("None" in log for log in debug_logs)
        
        if none_pattern:
            hypothesis = {
                "hypothesis": "Variable initialized to None or not set before use",
                "confidence": 0.7,
                "source": "code_flow_analysis",
                "category": "logic",
                "evidence": {
                    "none_values_detected": True,
                    "log_count": len(debug_logs),
                }
            }
            hypotheses.append(hypothesis)
        
        return hypotheses
    
    def _analyze_test_correlations(
        self,
        error_data: Dict[str, Any],
        test_failures: List[str]
    ) -> List[Dict[str, Any]]:
        """Analyze patterns across multiple test failures."""
        hypotheses = []
        
        if len(test_failures) > 1:
            # Multiple failures suggest systemic issue
            hypothesis = {
                "hypothesis": f"Systemic issue affecting {len(test_failures)} tests",
                "confidence": 0.65,
                "source": "test_correlation",
                "category": "architecture",
                "evidence": {
                    "failure_count": len(test_failures),
                    "test_names": test_failures[:3],  # First 3
                }
            }
            hypotheses.append(hypothesis)
        
        return hypotheses
    
    def _rank_hypotheses(
        self,
        hypotheses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank hypotheses by confidence score."""
        # Sort by confidence (descending)
        ranked = sorted(
            hypotheses,
            key=lambda h: h.get("confidence", 0),
            reverse=True
        )
        
        # Add rank field
        for i, hypothesis in enumerate(ranked, 1):
            hypothesis["rank"] = i
        
        return ranked
    
    def _pattern_to_hypothesis(self, pattern_name: str) -> str:
        """Convert pattern name to hypothesis statement."""
        pattern_hypotheses = {
            "missing_import": "Missing or incorrect module import",
            "undefined_variable": "Variable used before definition or out of scope",
            "type_mismatch": "Incorrect data type passed to function or method",
            "missing_attribute": "Object missing expected attribute or method",
            "null_reference": "Variable is None when value expected",
            "incorrect_logic": "Logic error in conditional or assertion",
            "file_not_found": "File path incorrect or file does not exist",
        }
        
        return pattern_hypotheses.get(pattern_name, f"Unknown pattern: {pattern_name}")
    
    def _calculate_relevance(
        self,
        finding: Dict[str, Any],
        affected_components: List[str]
    ) -> float:
        """Calculate relevance score of review finding to error."""
        # Simple heuristic: check if finding mentions affected components
        finding_text = finding.get("message", "").lower()
        
        matches = sum(
            1 for component in affected_components
            if component.lower() in finding_text
        )
        
        if not affected_components:
            return 0.5  # Moderate relevance if no components known
        
        return min(1.0, matches / len(affected_components))
