"""AC-PHASE43-021: Quality Assessment Framework

Validates multi-dimensional code quality scoring.

Target: 6/6 tests passing
AC-ID: AC-PHASE43-021
"""

import pytest
from typing import Dict, Any


class QualityAssessmentFramework:
    """Assess code quality across multiple dimensions (Phase 43: AC-PHASE43-021)."""
    
    def __init__(self):
        """Initialize quality framework."""
        self.dimensions = [
            "maintainability",
            "testability",
            "security",
            "performance",
            "documentation",
            "complexity",
        ]
    
    def assess(self, codebase_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess codebase quality across dimensions.
        
        Args:
            codebase_metrics: Metrics from code analysis
            
        Returns:
            Multi-dimensional quality assessment
        """
        scores = {}
        
        scores["maintainability"] = self._assess_maintainability(codebase_metrics)
        scores["testability"] = self._assess_testability(codebase_metrics)
        scores["security"] = self._assess_security(codebase_metrics)
        scores["performance"] = self._assess_performance(codebase_metrics)
        scores["documentation"] = self._assess_documentation(codebase_metrics)
        scores["complexity"] = self._assess_complexity(codebase_metrics)
        
        overall = self._compute_overall_score(scores)
        
        return {
            "dimensions": scores,
            "overall_score": overall,
            "grade": self._assign_grade(overall),
            "strengths": self._identify_strengths(scores),
            "weaknesses": self._identify_weaknesses(scores),
            "recommendations": self._generate_recommendations(scores),
        }
    
    def _assess_maintainability(self, metrics: Dict[str, Any]) -> float:
        """Assess code maintainability (0-1)."""
        # Based on: complexity, duplication, test coverage
        complexity = min(1.0, 1.0 / (1.0 + metrics.get("cyclomatic_complexity", 5.0) / 10.0))
        duplication = 1.0 - min(1.0, metrics.get("duplication_ratio", 0.0))
        test_impact = metrics.get("test_coverage", 0.0)
        
        return (complexity * 0.4) + (duplication * 0.3) + (test_impact * 0.3)
    
    def _assess_testability(self, metrics: Dict[str, Any]) -> float:
        """Assess code testability (0-1)."""
        # Based on: test coverage, test count, test health
        coverage = metrics.get("test_coverage", 0.0)
        test_count = min(1.0, metrics.get("test_count", 0) / 100.0)
        test_health = metrics.get("test_health_ratio", 1.0)
        
        return (coverage * 0.5) + (test_count * 0.3) + (test_health * 0.2)
    
    def _assess_security(self, metrics: Dict[str, Any]) -> float:
        """Assess code security (0-1)."""
        # Based on: known vulnerabilities, security checks
        vulnerabilities = metrics.get("known_vulnerabilities", 0)
        security_score = max(0.0, 1.0 - (vulnerabilities * 0.2))
        
        has_security_checks = metrics.get("has_security_checks", False)
        check_bonus = 0.1 if has_security_checks else 0.0
        
        return min(1.0, security_score + check_bonus)
    
    def _assess_performance(self, metrics: Dict[str, Any]) -> float:
        """Assess code performance (0-1)."""
        # Based on: performance warnings, optimization scores
        perf_warnings = metrics.get("performance_warnings", 0)
        perf_score = max(0.0, 1.0 - (perf_warnings * 0.15))
        
        optimization_level = metrics.get("optimization_level", 0.5)
        
        return (perf_score * 0.6) + (optimization_level * 0.4)
    
    def _assess_documentation(self, metrics: Dict[str, Any]) -> float:
        """Assess code documentation (0-1)."""
        # Based on: docstring coverage, comment density
        docstring_coverage = metrics.get("docstring_coverage", 0.0)
        comment_density = min(1.0, metrics.get("comment_ratio", 0.0) * 2.0)
        
        return (docstring_coverage * 0.7) + (comment_density * 0.3)
    
    def _assess_complexity(self, metrics: Dict[str, Any]) -> float:
        """Assess code complexity (0-1, higher is better)."""
        cyclomatic = metrics.get("cyclomatic_complexity", 10.0)
        cognitive = metrics.get("cognitive_complexity", 10.0)
        
        # Inverse: higher complexity = lower score
        cyc_score = 1.0 / (1.0 + cyclomatic / 5.0)
        cog_score = 1.0 / (1.0 + cognitive / 5.0)
        
        return (cyc_score * 0.5) + (cog_score * 0.5)
    
    def _compute_overall_score(self, dimension_scores: Dict[str, float]) -> float:
        """Compute overall quality score."""
        scores = list(dimension_scores.values())
        return sum(scores) / len(scores) if scores else 0.0
    
    def _assign_grade(self, score: float) -> str:
        """Assign letter grade."""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
    
    def _identify_strengths(self, scores: Dict[str, float]) -> list:
        """Identify dimension strengths."""
        return [dim for dim, score in scores.items() if score >= 0.75]
    
    def _identify_weaknesses(self, scores: Dict[str, float]) -> list:
        """Identify dimension weaknesses."""
        return [dim for dim, score in scores.items() if score < 0.6]
    
    def _generate_recommendations(self, scores: Dict[str, float]) -> list:
        """Generate improvement recommendations."""
        recommendations = []
        
        if scores.get("testability", 0.0) < 0.7:
            recommendations.append("Increase test coverage and add unit tests")
        
        if scores.get("complexity", 0.0) < 0.6:
            recommendations.append("Refactor complex methods and reduce cognitive load")
        
        if scores.get("documentation", 0.0) < 0.6:
            recommendations.append("Add docstrings and improve inline documentation")
        
        if scores.get("security", 0.0) < 0.7:
            recommendations.append("Add security checks and input validation")
        
        return recommendations


class TestQualityAssessmentFramework:
    """Tests for quality assessment."""
    
    def test_framework_initializes(self):
        """Validate framework initializes."""
        framework = QualityAssessmentFramework()
        assert framework is not None
        assert len(framework.dimensions) == 6
    
    def test_framework_assesses_high_quality_code(self):
        """Validate assessment of high-quality code."""
        framework = QualityAssessmentFramework()
        
        metrics = {
            "cyclomatic_complexity": 4.0,
            "test_coverage": 0.9,
            "duplication_ratio": 0.05,
            "test_count": 150,
            "test_health_ratio": 1.0,
            "known_vulnerabilities": 0,
            "has_security_checks": True,
            "docstring_coverage": 0.95,
        }
        
        result = framework.assess(metrics)
        
        assert result["overall_score"] > 0.65
        assert result["grade"] in ["A", "B", "C"]
    
    def test_framework_assesses_low_quality_code(self):
        """Validate assessment of low-quality code."""
        framework = QualityAssessmentFramework()
        
        metrics = {
            "cyclomatic_complexity": 25.0,
            "test_coverage": 0.2,
            "duplication_ratio": 0.4,
            "test_count": 10,
            "test_health_ratio": 0.6,
            "known_vulnerabilities": 3,
            "has_security_checks": False,
            "docstring_coverage": 0.1,
        }
        
        result = framework.assess(metrics)
        
        assert result["overall_score"] < 0.6
        assert result["grade"] in ["D", "F"]
    
    def test_framework_identifies_strengths(self):
        """Validate strength identification."""
        framework = QualityAssessmentFramework()
        
        metrics = {
            "cyclomatic_complexity": 3.0,
            "test_coverage": 0.92,
            "duplication_ratio": 0.02,
            "test_count": 200,
            "test_health_ratio": 1.0,
            "known_vulnerabilities": 0,
            "docstring_coverage": 0.88,
        }
        
        result = framework.assess(metrics)
        
        assert "testability" in result["strengths"] or "maintainability" in result["strengths"]
    
    def test_framework_identifies_weaknesses(self):
        """Validate weakness identification."""
        framework = QualityAssessmentFramework()
        
        metrics = {
            "cyclomatic_complexity": 30.0,
            "test_coverage": 0.15,
            "duplication_ratio": 0.5,
            "docstring_coverage": 0.05,
            "known_vulnerabilities": 2,
        }
        
        result = framework.assess(metrics)
        
        assert len(result["weaknesses"]) > 0
    
    def test_framework_generates_recommendations(self):
        """Validate recommendation generation."""
        framework = QualityAssessmentFramework()
        
        metrics = {
            "cyclomatic_complexity": 20.0,
            "test_coverage": 0.3,
            "docstring_coverage": 0.2,
        }
        
        result = framework.assess(metrics)
        
        assert len(result["recommendations"]) > 0
