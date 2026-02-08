"""AC-PHASE43-009: Impact Analysis Computation

Validates that impact analysis properly evaluates downstream effects,
architectural coupling, and team/delivery impact.

Target: 4/4 tests passing
AC-ID: AC-PHASE43-009
"""

import pytest
from typing import Dict, Any, List


class ImpactAnalyzer:
    """Analyze operational impact (Phase 43: AC-PHASE43-009)."""
    
    def __init__(self):
        """Initialize impact analyzer."""
        self.impact_factors = {
            "affected_modules": [],
            "affected_features": [],
            "affected_tests": [],
            "architectural_impact": "NONE",
            "team_impact": "NONE",
            "delivery_impact": "NONE",
        }
    
    def analyze_impact(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze overall impact of change.
        
        Args:
            context: Operation context with change details
            
        Returns:
            Impact analysis results
        """
        # Extract change scope
        files_changed = context.get("files_changed", [])
        dependencies = context.get("dependencies", {})
        breaking_changes = context.get("breaking_changes", [])
        affected_interfaces = context.get("affected_interfaces", [])
        
        # Compute impacts
        module_impact = self._compute_module_impact(files_changed, dependencies)
        feature_impact = self._compute_feature_impact(files_changed, context.get("features", {}))
        test_impact = self._compute_test_impact(files_changed, context.get("test_coverage", {}))
        arch_impact = self._compute_architectural_impact(breaking_changes, affected_interfaces)
        team_impact = self._compute_team_impact(context)
        delivery_impact = self._compute_delivery_impact(
            breaking_changes, 
            context.get("release_stage", "dev")
        )
        
        return {
            "summary": {
                "modules_affected": len(module_impact),
                "features_affected": len(feature_impact),
                "tests_affected": len(test_impact),
                "architectural_impact": arch_impact,
                "team_impact": team_impact,
                "delivery_impact": delivery_impact,
            },
            "details": {
                "affected_modules": module_impact,
                "affected_features": feature_impact,
                "affected_tests": test_impact,
                "breaking_changes": breaking_changes,
            },
            "recommendations": self._generate_recommendations(
                module_impact, feature_impact, test_impact, arch_impact
            ),
        }
    
    def _compute_module_impact(self, files_changed: List[str], dependencies: Dict) -> List[str]:
        """Compute which modules are affected by changes."""
        # For test purposes, directly affected files
        affected = set(files_changed)
        
        # Add downstream dependencies
        for file in files_changed:
            if file in dependencies:
                affected.update(dependencies[file])
        
        return sorted(list(affected))
    
    def _compute_feature_impact(self, files_changed: List[str], features: Dict) -> List[str]:
        """Compute which features are affected."""
        affected = set()
        
        for file in files_changed:
            for feature, feature_files in features.items():
                if file in feature_files:
                    affected.add(feature)
        
        return sorted(list(affected))
    
    def _compute_test_impact(self, files_changed: List[str], test_coverage: Dict) -> List[str]:
        """Compute which tests need re-running."""
        affected = set()
        
        for file in files_changed:
            if file in test_coverage:
                affected.update(test_coverage[file].get("tests", []))
        
        return sorted(list(affected))
    
    def _compute_architectural_impact(self, breaking_changes: List[str], 
                                      affected_interfaces: List[str]) -> str:
        """Determine architectural impact level."""
        if len(breaking_changes) > 0 or len(affected_interfaces) > 2:
            return "HIGH"
        elif len(affected_interfaces) > 0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _compute_team_impact(self, context: Dict) -> str:
        """Determine team impact (CRITICAL, HIGH, MEDIUM, LOW)."""
        affected_teams = context.get("affected_teams", [])
        is_blocking = context.get("is_blocking", False)
        
        if is_blocking and len(affected_teams) > 2:
            return "CRITICAL"
        elif len(affected_teams) > 2:
            return "HIGH"
        elif len(affected_teams) > 0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _compute_delivery_impact(self, breaking_changes: List[str], 
                                 release_stage: str = "dev") -> str:
        """Determine delivery impact based on release stage."""
        if len(breaking_changes) > 0:
            if release_stage in ["prod", "staging"]:
                return "BLOCKING"  # Need migration plan
            else:
                return "HIGH"
        else:
            return "LOW"
    
    def _generate_recommendations(self, modules: List[str], features: List[str],
                                  tests: List[str], arch_impact: str) -> List[str]:
        """Generate recommendations based on impact analysis."""
        recommendations = []
        
        if len(modules) > 5:
            recommendations.append("LARGE CHANGE: Consider breaking into smaller PRs")
        
        if len(features) > 2:
            recommendations.append("MULTI-FEATURE: Require release planning")
        
        if len(tests) > 10:
            recommendations.append("EXTENSIVE TESTING: Schedule full regression suite")
        
        if arch_impact == "HIGH":
            recommendations.append("ARCHITECTURAL: Require architecture review")
        
        if not recommendations:
            recommendations.append("ISOLATED CHANGE: Can merge with standard review")
        
        return recommendations


class TestImpactAnalysis:
    """Tests for impact analysis algorithms."""
    
    def test_impact_analyzer_initializes(self):
        """Validate ImpactAnalyzer initializes."""
        analyzer = ImpactAnalyzer()
        assert analyzer is not None, "ImpactAnalyzer should be instantiable"
        assert hasattr(analyzer, 'analyze_impact'), "Should have analyze_impact method"
    
    def test_impact_analyzer_analyzes_low_impact_changes(self):
        """Validate ImpactAnalyzer identifies low-impact changes."""
        analyzer = ImpactAnalyzer()
        
        context = {
            "files_changed": ["src/utils/string_utils.py"],
            "dependencies": {},
            "breaking_changes": [],
            "affected_interfaces": [],
            "features": {"string_utils": ["src/utils/string_utils.py"]},
            "test_coverage": {"src/utils/string_utils.py": {"tests": ["test_string_utils.py"]}},
            "affected_teams": ["tools"],
            "is_blocking": False,
            "release_stage": "dev",
        }
        
        result = analyzer.analyze_impact(context)
        
        assert isinstance(result, dict), "Should return dict"
        assert "summary" in result, "Should have summary"
        assert result["summary"]["architectural_impact"] == "LOW", \
            f"Expected LOW architectural impact, got {result['summary']['architectural_impact']}"
    
    def test_impact_analyzer_analyzes_high_impact_changes(self):
        """Validate ImpactAnalyzer identifies high-impact changes."""
        analyzer = ImpactAnalyzer()
        
        context = {
            "files_changed": [
                "cortex/core/orchestrator.py",
                "cortex/lens/analyzer.py",
                "cortex/brain/processor.py",
            ],
            "dependencies": {
                "cortex/core/orchestrator.py": ["cortex/lens/analyzer.py", "cortex/brain/processor.py"],
            },
            "breaking_changes": ["api_version_changed"],
            "affected_interfaces": ["IntentRouter", "LENSOrchestrator", "MasterOrchestrator"],
            "features": {
                "core": ["cortex/core/orchestrator.py"],
                "lens": ["cortex/lens/analyzer.py"],
                "brain": ["cortex/brain/processor.py"],
            },
            "test_coverage": {
                "cortex/core/orchestrator.py": {"tests": ["test_orchestrator.py"]},
                "cortex/lens/analyzer.py": {"tests": ["test_lens_analyzer.py"]},
            },
            "affected_teams": ["ml", "platform", "tools"],
            "is_blocking": True,
            "release_stage": "prod",
        }
        
        result = analyzer.analyze_impact(context)
        
        assert result["summary"]["modules_affected"] > 2, "Should detect multiple modules"
        assert result["summary"]["architectural_impact"] == "HIGH", \
            "Should identify HIGH architectural impact"
        assert result["summary"]["team_impact"] == "CRITICAL", \
            "Should identify CRITICAL team impact"
        assert result["summary"]["delivery_impact"] == "BLOCKING", \
            "Should identify BLOCKING delivery impact"
    
    def test_impact_analyzer_generates_recommendations(self):
        """Validate ImpactAnalyzer generates actionable recommendations."""
        analyzer = ImpactAnalyzer()
        
        context = {
            "files_changed": [f"file{i}.py" for i in range(10)],
            "dependencies": {},
            "breaking_changes": [],
            "affected_interfaces": [],
            "features": {"feature1": [f"file{i}.py" for i in range(6)]},
            "test_coverage": {f"file{i}.py": {"tests": [f"test{i}.py"]} for i in range(10)},
            "affected_teams": ["team1", "team2"],
            "is_blocking": False,
            "release_stage": "dev",
        }
        
        result = analyzer.analyze_impact(context)
        
        assert "recommendations" in result, "Should have recommendations"
        assert len(result["recommendations"]) > 0, "Should generate recommendations"
        assert all(isinstance(r, str) for r in result["recommendations"]), \
            "All recommendations should be strings"
    
    def test_impact_analyzer_handles_empty_context(self):
        """Validate ImpactAnalyzer handles empty/minimal context."""
        analyzer = ImpactAnalyzer()
        
        context = {}
        
        result = analyzer.analyze_impact(context)
        
        assert isinstance(result, dict), "Should return dict"
        assert "summary" in result, "Should always have summary"
        assert result["summary"]["architectural_impact"] in ["LOW", "MEDIUM", "HIGH"], \
            "Impact level should be valid"
