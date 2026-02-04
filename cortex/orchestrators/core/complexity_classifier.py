"""
Intelligent Complexity Classification for CORTEX tasks.

Purpose: Determine planning depth and resource requirements based on task complexity
Authority: CORTEX-SELF-IMPROVEMENT-SDLC.yaml Phase 2
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)

Classification Levels:
- TRIVIAL: LOC < 5, no planning
- SIMPLE: LOC 5-50, lightweight planning
- MODERATE: LOC 50-200, standard planning
- COMPLEX: LOC > 200, full planning
- CRITICAL: Breaking changes, security-sensitive, mandatory extended review
"""

import logging
from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ComplexityLevel(str, Enum):
    """Task complexity classification levels."""
    TRIVIAL = "TRIVIAL"
    SIMPLE = "SIMPLE"
    MODERATE = "MODERATE"
    COMPLEX = "COMPLEX"
    CRITICAL = "CRITICAL"


@dataclass
class ComplexityAnalysis:
    """Result of complexity classification analysis."""
    level: ComplexityLevel
    estimated_loc: int
    affected_layers: List[str]
    modules_touched: int
    is_security_sensitive: bool
    is_governance_affecting: bool
    planning_required: bool
    planning_depth: str  # "none", "lightweight", "standard", "full"
    estimated_hours: float
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"


class ComplexityClassifier:
    """Classifies task complexity to determine planning depth."""
    
    def __init__(self):
        """Initialize ComplexityClassifier."""
        self.keyword_patterns = {
            "security": ["auth", "crypto", "password", "token", "secret", "permission"],
            "governance": ["rule", "compliance", "audit", "governance", "enforcement"],
            "breaking": ["breaking", "migration", "schema", "refactor", "deprecat"],
            "multi_layer": ["frontend", "backend", "database", "api", "layer"],
            "high_impact": ["system", "core", "infrastructure", "orchestrator"],
        }
    
    def classify_complexity(
        self,
        task_description: str,
        estimated_loc_impact: Optional[int] = None,
        target_modules: Optional[List[str]] = None,
        is_security_sensitive: Optional[bool] = None,
        is_governance_affecting: Optional[bool] = None,
    ) -> ComplexityAnalysis:
        """Classify task complexity based on multiple signals.
        
        Args:
            task_description: Description of the task
            estimated_loc_impact: Pre-estimated LOC impact (optional)
            target_modules: Modules affected (optional)
            is_security_sensitive: Whether task affects security (optional)
            is_governance_affecting: Whether task affects governance (optional)
        
        Returns:
            ComplexityAnalysis with detailed breakdown
        """
        # Analyze LOC impact
        if estimated_loc_impact is None:
            estimated_loc_impact = self._estimate_loc_impact(task_description)
        
        # Identify affected layers
        if target_modules is None:
            target_modules = self._identify_target_modules(task_description)
        affected_layers = self._identify_affected_layers(target_modules, task_description)
        
        # Count modules touched
        modules_touched = len(set(target_modules)) if target_modules else 0
        
        # Check security sensitivity
        if is_security_sensitive is None:
            is_security_sensitive = self._check_security_sensitivity(task_description)
        
        # Check governance impact
        if is_governance_affecting is None:
            is_governance_affecting = self._check_governance_impact(task_description)
        
        # Determine complexity level
        level = self._determine_level(
            estimated_loc_impact,
            affected_layers,
            modules_touched,
            is_security_sensitive,
            is_governance_affecting,
        )
        
        # Determine planning requirements
        planning_required, planning_depth = self._determine_planning(level)
        
        # Estimate effort
        estimated_hours = self._estimate_effort(
            estimated_loc_impact,
            len(affected_layers),
            modules_touched,
            is_security_sensitive,
        )
        
        # Assess risk level
        risk_level = self._assess_risk(
            level,
            is_security_sensitive,
            is_governance_affecting,
            len(affected_layers),
        )
        
        return ComplexityAnalysis(
            level=level,
            estimated_loc=estimated_loc_impact,
            affected_layers=affected_layers,
            modules_touched=modules_touched,
            is_security_sensitive=is_security_sensitive,
            is_governance_affecting=is_governance_affecting,
            planning_required=planning_required,
            planning_depth=planning_depth,
            estimated_hours=estimated_hours,
            risk_level=risk_level,
        )
    
    def _estimate_loc_impact(self, task_description: str) -> int:
        """Estimate lines of code impact from task description.
        
        Args:
            task_description: Description to analyze
        
        Returns:
            Estimated LOC impact
        """
        score = 0
        desc_lower = task_description.lower()
        
        # Keywords indicating larger changes
        high_impact_keywords = ["refactor", "redesign", "migrate", "rewrite", "system"]
        medium_impact_keywords = ["add", "implement", "create", "extend"]
        low_impact_keywords = ["fix", "update", "adjust", "minor"]
        
        # Count keyword occurrences
        for keyword in high_impact_keywords:
            if keyword in desc_lower:
                score += 200
        for keyword in medium_impact_keywords:
            if keyword in desc_lower:
                score += 50
        for keyword in low_impact_keywords:
            if keyword in desc_lower:
                score += 5
        
        # No keywords found - assume small change
        if score == 0:
            score = 10
        
        return score
    
    def _identify_target_modules(self, task_description: str) -> List[str]:
        """Identify target modules from task description.
        
        Args:
            task_description: Description to analyze
        
        Returns:
            List of target module names (or empty if not identified)
        """
        known_modules = [
            "orchestrator", "event_bus", "planning", "interaction",
            "tdd", "review", "mcp", "challenge", "lens",
            "frontend", "backend", "api", "database",
        ]
        
        found = []
        for module in known_modules:
            if module in task_description.lower():
                found.append(module)
        
        return found if found else ["general"]
    
    def _identify_affected_layers(
        self, target_modules: List[str], task_description: str
    ) -> List[str]:
        """Identify which architectural layers are affected.
        
        Args:
            target_modules: Modules involved
            task_description: Task description
        
        Returns:
            List of affected layers
        """
        layers = set()
        desc_lower = task_description.lower()
        
        # Map modules to layers
        layer_keywords = {
            "infrastructure": ["bus", "infrastructure", "event", "wiring"],
            "core": ["orchestrator", "core", "interaction", "master"],
            "domain": ["planning", "refactoring", "documentation"],
            "api": ["mcp", "api", "tool", "endpoint"],
            "frontend": ["frontend", "ui", "component", "javascript"],
            "backend": ["backend", "python", "api", "data"],
            "data": ["database", "schema", "model", "data"],
        }
        
        for layer, keywords in layer_keywords.items():
            for keyword in keywords:
                if any(kw in desc_lower for kw in keywords):
                    layers.add(layer)
                    break
        
        # Default to at least one layer
        return list(layers) if layers else ["core"]
    
    def _check_security_sensitivity(self, task_description: str) -> bool:
        """Check if task is security-sensitive.
        
        Args:
            task_description: Task description
        
        Returns:
            True if security-sensitive
        """
        desc_lower = task_description.lower()
        keywords = self.keyword_patterns.get("security", [])
        return any(kw in desc_lower for kw in keywords)
    
    def _check_governance_impact(self, task_description: str) -> bool:
        """Check if task affects governance/compliance.
        
        Args:
            task_description: Task description
        
        Returns:
            True if governance-affecting
        """
        desc_lower = task_description.lower()
        keywords = self.keyword_patterns.get("governance", [])
        return any(kw in desc_lower for kw in keywords)
    
    def _determine_level(
        self,
        loc_impact: int,
        affected_layers: List[str],
        modules_touched: int,
        is_security_sensitive: bool,
        is_governance_affecting: bool,
    ) -> ComplexityLevel:
        """Determine complexity level based on signals.
        
        Args:
            loc_impact: Estimated LOC impact
            affected_layers: Number of layers affected
            modules_touched: Number of modules touched
            is_security_sensitive: Whether security-sensitive
            is_governance_affecting: Whether governance-affecting
        
        Returns:
            ComplexityLevel classification
        """
        # CRITICAL: Security or governance affecting
        if is_security_sensitive or is_governance_affecting:
            return ComplexityLevel.CRITICAL
        
        # COMPLEX: Multiple layers, high LOC, or many modules
        if len(affected_layers) > 1 or loc_impact > 200 or modules_touched > 2:
            return ComplexityLevel.COMPLEX
        
        # MODERATE: Multiple modules or moderate LOC
        if modules_touched > 1 or loc_impact > 50:
            return ComplexityLevel.MODERATE
        
        # SIMPLE: Single module, low-to-moderate LOC
        if loc_impact > 5:
            return ComplexityLevel.SIMPLE
        
        # TRIVIAL: Minimal change
        return ComplexityLevel.TRIVIAL
    
    def _determine_planning(self, level: ComplexityLevel) -> tuple:
        """Determine planning requirements based on complexity.
        
        Args:
            level: Complexity level
        
        Returns:
            Tuple of (planning_required: bool, planning_depth: str)
        """
        planning_map = {
            ComplexityLevel.TRIVIAL: (False, "none"),
            ComplexityLevel.SIMPLE: (True, "lightweight"),
            ComplexityLevel.MODERATE: (True, "standard"),
            ComplexityLevel.COMPLEX: (True, "full"),
            ComplexityLevel.CRITICAL: (True, "full"),
        }
        return planning_map.get(level, (True, "full"))
    
    def _estimate_effort(
        self,
        loc_impact: int,
        num_layers: int,
        modules_touched: int,
        is_security_sensitive: bool,
    ) -> float:
        """Estimate effort in hours.
        
        Args:
            loc_impact: Estimated LOC impact
            num_layers: Number of layers affected
            modules_touched: Number of modules
            is_security_sensitive: Whether security-sensitive
        
        Returns:
            Estimated hours
        """
        # Base estimate: 1 LOC per minute
        base_hours = loc_impact / 60
        
        # Multi-layer multiplier (0.5-1.0 additional hours per layer beyond first)
        layer_factor = max(0, (num_layers - 1) * 0.5)
        
        # Module coordination factor
        module_factor = modules_touched * 0.5
        
        # Security overhead
        security_factor = 2.0 if is_security_sensitive else 0
        
        total = base_hours + layer_factor + module_factor + security_factor
        
        # Add 20% buffer for unknowns
        return total * 1.2
    
    def _assess_risk(
        self,
        level: ComplexityLevel,
        is_security_sensitive: bool,
        is_governance_affecting: bool,
        num_layers: int,
    ) -> str:
        """Assess risk level of task.
        
        Args:
            level: Complexity level
            is_security_sensitive: Whether security-sensitive
            is_governance_affecting: Whether governance-affecting
            num_layers: Number of layers affected
        
        Returns:
            Risk level string ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        """
        if is_security_sensitive or is_governance_affecting:
            return "CRITICAL"
        
        if level == ComplexityLevel.COMPLEX:
            return "HIGH"
        
        if level == ComplexityLevel.MODERATE or num_layers > 1:
            return "MEDIUM"
        
        return "LOW"


# Singleton instance
_classifier_instance: Optional[ComplexityClassifier] = None


def get_complexity_classifier() -> ComplexityClassifier:
    """Get the global ComplexityClassifier instance.
    
    Returns:
        The global ComplexityClassifier
    """
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = ComplexityClassifier()
    return _classifier_instance
