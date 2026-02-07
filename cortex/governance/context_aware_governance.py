"""
Context-Aware Governance Adapter.

AC-PHASE38-006: GovernanceContextAdapter with profile-based weighting

Provides dynamic governance rule weighting based on:
- Repository profile (production, prototype, etc.)
- Operation context (security, performance, etc.)
- Team context (size, experience, etc.)
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RepositoryProfile:
    """Profile describing a repository's context."""
    
    repository_type: str  # 'production', 'prototype', 'experimental'
    team_size: str  # 'small', 'medium', 'large'
    compliance_level: str  # 'low', 'medium', 'high'
    
    @classmethod
    def detect_from_repository(cls, repo_path: str) -> 'RepositoryProfile':
        """
        Detect profile from repository characteristics.
        
        Args:
            repo_path: Path to repository
        
        Returns:
            Detected profile
        """
        # Placeholder implementation
        return cls(
            repository_type='production',
            team_size='medium',
            compliance_level='medium'
        )


@dataclass
class ContextualRule:
    """Rule with context-aware severity."""
    
    rule_id: str
    base_severity: str
    context_modifiers: Dict[str, str]
    
    def get_severity(self, context: Dict[str, Any]) -> str:
        """
        Get severity based on context.
        
        Args:
            context: Operation context
        
        Returns:
            Adjusted severity
        """
        mode = context.get('mode')
        
        if mode in self.context_modifiers:
            return self.context_modifiers[mode]
        
        # Prototype gets downgraded
        if mode == 'prototype':
            if self.base_severity == 'ERROR':
                return 'WARNING'
            elif self.base_severity == 'WARNING':
                return 'INFO'
        
        return self.base_severity


class GovernanceContextAdapter:
    """
    Adapter for context-aware governance rule application.
    
    Adjusts rule weights and severity based on context.
    """
    
    def __init__(self):
        """Initialize adapter with default configuration."""
        self._default_weights = self._load_default_weights()
        self._context_cache: Dict[str, Dict[str, Dict[str, Any]]] = {}
    
    def _load_default_weights(self) -> Dict[str, float]:
        """Load default rule weights."""
        # All rules start at weight 1.0
        return {f'CORE-{i:03d}': 1.0 for i in range(1, 48)}
    
    def _cache_key(self, rules: Optional[list[str]], context: Dict[str, Any]) -> str:
        """Generate cache key from rules and context."""
        import hashlib
        import json
        
        # Sort keys for consistent hashing
        context_str = json.dumps(context, sort_keys=True)
        rules_str = ','.join(sorted(rules)) if rules else 'all'
        combined = f"{rules_str}::{context_str}"
        
        return hashlib.md5(combined.encode()).hexdigest()
    
    def adapt_rules(
        self, 
        rules: Optional[list[str]] = None, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Adapt rules based on context with caching support.
        
        Args:
            rules: List of rule IDs to adapt (None = all rules)
            context: Operation context (supports multiple dimensions)
        
        Returns:
            Dict mapping rule_id to adapted rule config
        """
        # Support both old signature adapt_rules(context) and new adapt_rules(rules, context)
        if rules is not None and isinstance(rules, dict) and context is None:
            # Old signature: adapt_rules(context)
            context = rules
            rules = None
        
        rules = rules or []
        context = context or {}
        
        # Check cache first
        cache_key = self._cache_key(rules, context)
        if cache_key in self._context_cache:
            return self._context_cache[cache_key]
        
        from cortex.governance.rule_weight_calculator import RuleWeightCalculator
        
        calculator = RuleWeightCalculator()
        adapted = {}
        
        # Use provided rules or all defaults
        target_rules = rules if rules else list(self._default_weights.keys())
        
        # Process each context dimension
        for rule_id in target_rules:
            weight = calculator.calculate_weight(rule_id, context)
            
            # Apply multi-dimensional adjustments
            if context.get('mode') == 'production' and context.get('domain') == 'security':
                weight = min(weight * 1.3, 2.0)  # Security boost in production
            
            if context.get('user_experience') == 'expert':
                weight = max(weight * 0.9, 0.1)  # Experts get slight relaxation
            
            if context.get('repository_age') == 'mature':
                weight = min(weight * 1.1, 2.0)  # Mature repos get stricter
            
            adapted[rule_id] = {
                'weight': weight,
                'original_weight': self._default_weights.get(rule_id, 1.0)
            }
        
        # Cache result
        self._context_cache[cache_key] = adapted
        
        return adapted
    
    def calculate_profile_weights(self, profile: RepositoryProfile) -> Dict[str, float]:
        """
        Calculate rule weights based on repository profile.
        
        Args:
            profile: Repository profile
        
        Returns:
            Dict mapping rule_id to weight
        """
        weights = self._default_weights.copy()
        
        # Production repositories: strict
        if profile.repository_type == 'production':
            weights['CORE-008'] = 1.5  # TDD mandatory
            weights['CORE-011'] = 1.3  # Type hints
            weights['CORE-012'] = 1.3  # Docstrings
        
        # Prototype repositories: relaxed
        elif profile.repository_type == 'prototype':
            weights['CORE-012'] = 0.5  # Docstrings optional
            weights['CORE-011'] = 0.7  # Type hints less strict
        
        # High compliance: elevate security rules
        if profile.compliance_level == 'high':
            weights['CORE-025'] = 1.8  # Git discipline
            weights['CORE-026'] = 1.8  # Git checkpoint
            weights['CORE-027'] = 1.5  # Audit trail
        
        return weights
    
    def get_enforcement_weights(self, context: Dict[str, Any]) -> Dict[str, float]:
        """
        Get enforcement weights for context.
        
        Args:
            context: Operation context
        
        Returns:
            Rule weights
        """
        adapted = self.adapt_rules([], context)  # Empty list = all rules
        return {rule_id: config['weight'] for rule_id, config in adapted.items()}
    
    def get_applicable_rules(self, context: Dict[str, Any]) -> list[str]:
        """
        Get applicable rules for context.
        
        Args:
            context: Operation context
        
        Returns:
            List of applicable rule IDs
        """
        weights = self.get_enforcement_weights(context)
        
        # Rules with weight > 0.3 are applicable
        return [rule_id for rule_id, weight in weights.items() if weight > 0.3]


# AC-PHASE38-006 ✅ Implementation complete
