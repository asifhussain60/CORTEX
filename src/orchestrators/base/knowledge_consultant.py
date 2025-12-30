"""
Knowledge Library Consultant

Purpose: Actively consult the knowledge library during orchestrator operations.
Author: Asif Hussain
Created: 2025-12-30
Version: 1.0.0

Gap Addressed: GAP 4 - Knowledge Library Passive (Not Actively Consulted)
- Previous: 35+ YAML files, 525+ rules exist but never queried
- New: Active consultation with rule matching and precedence

Features:
- Active knowledge library querying
- Context-aware rule matching
- Precedence and conflict resolution
- Caching for performance
- Telemetry for rule usage
"""

import logging
import yaml
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


# ============================================================================
# Knowledge Rule Types
# ============================================================================

@dataclass
class KnowledgeRule:
    """A rule from the knowledge library."""
    rule_id: str
    category: str
    name: str
    description: str
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    precedence: int = 50  # Higher = more important (0-100)
    source_file: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsultationResult:
    """Result of knowledge library consultation."""
    matched_rules: List[KnowledgeRule]
    recommendations: List[str]
    warnings: List[str]
    context_applied: Dict[str, Any]
    consultation_time_ms: float
    rules_searched: int


# ============================================================================
# Knowledge Library Consultant
# ============================================================================

class KnowledgeConsultant:
    """
    Actively consults the knowledge library during operations.
    
    The CORTEX knowledge library contains 35+ YAML files with 525+ rules
    covering:
    - Refactoring patterns
    - Code quality standards
    - Security guidelines
    - Performance optimizations
    - TDD best practices
    - Response formatting
    
    This consultant:
    1. Loads and indexes knowledge rules
    2. Matches rules to current context
    3. Returns relevant recommendations
    4. Tracks rule usage for optimization
    
    Usage:
        consultant = KnowledgeConsultant(brain_path="/path/to/cortex-brain")
        
        result = consultant.consult(
            context={
                "operation": "refactoring",
                "language": "python",
                "complexity": "high"
            },
            query="What rules apply to class extraction?"
        )
        
        for rule in result.matched_rules:
            print(f"Rule: {rule.name}")
            print(f"Actions: {rule.actions}")
    """
    
    # Knowledge library paths (relative to brain root)
    KNOWLEDGE_PATHS = [
        "knowledge",
        "knowledge-library",
        "core",
        "manifests/orchestrators",
    ]
    
    # Category priorities
    CATEGORY_PRIORITIES = {
        "security": 100,
        "brain-protection": 95,
        "data-integrity": 90,
        "tdd": 85,
        "refactoring": 70,
        "performance": 65,
        "code-quality": 60,
        "response": 50,
        "documentation": 40,
        "formatting": 30,
    }

    def __init__(
        self,
        brain_path: str,
        enable_caching: bool = True,
        cache_ttl_seconds: int = 300
    ):
        """
        Initialize Knowledge Consultant.
        
        Args:
            brain_path: Path to cortex-brain directory
            enable_caching: Enable rule caching
            cache_ttl_seconds: Cache time-to-live in seconds
        """
        self.brain_path = Path(brain_path)
        self.enable_caching = enable_caching
        self.cache_ttl_seconds = cache_ttl_seconds
        
        # Rule storage
        self._rules: Dict[str, KnowledgeRule] = {}
        self._rules_by_category: Dict[str, List[KnowledgeRule]] = {}
        
        # Cache
        self._query_cache: Dict[str, ConsultationResult] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        # Telemetry
        self._total_consultations = 0
        self._cache_hits = 0
        self._rules_loaded = 0
        self._rule_usage: Dict[str, int] = {}
        
        # Load knowledge library
        self._load_knowledge_library()
        
        logger.info(
            f"📚 Knowledge Consultant initialized: "
            f"{self._rules_loaded} rules loaded from {brain_path}"
        )

    def consult(
        self,
        context: Dict[str, Any],
        query: Optional[str] = None,
        categories: Optional[List[str]] = None,
        max_rules: int = 10
    ) -> ConsultationResult:
        """
        Consult the knowledge library for relevant rules.
        
        Args:
            context: Current operation context
            query: Optional natural language query
            categories: Optional category filter
            max_rules: Maximum rules to return
            
        Returns:
            ConsultationResult with matched rules and recommendations
        """
        import time
        start_time = time.time()
        
        self._total_consultations += 1
        
        # Check cache
        cache_key = self._make_cache_key(context, query, categories)
        if self.enable_caching and cache_key in self._query_cache:
            if self._is_cache_valid(cache_key):
                self._cache_hits += 1
                return self._query_cache[cache_key]
        
        # Match rules to context
        matched_rules = self._match_rules(context, query, categories)
        
        # Sort by precedence
        matched_rules.sort(key=lambda r: r.precedence, reverse=True)
        
        # Limit results
        matched_rules = matched_rules[:max_rules]
        
        # Extract recommendations and warnings
        recommendations = self._extract_recommendations(matched_rules)
        warnings = self._extract_warnings(matched_rules, context)
        
        # Track rule usage
        for rule in matched_rules:
            self._rule_usage[rule.rule_id] = self._rule_usage.get(rule.rule_id, 0) + 1
        
        # Build result
        consultation_time = (time.time() - start_time) * 1000
        
        result = ConsultationResult(
            matched_rules=matched_rules,
            recommendations=recommendations,
            warnings=warnings,
            context_applied=context,
            consultation_time_ms=consultation_time,
            rules_searched=len(self._rules)
        )
        
        # Cache result
        if self.enable_caching:
            self._query_cache[cache_key] = result
            self._cache_timestamps[cache_key] = datetime.now()
        
        logger.debug(
            f"📚 Consultation complete: {len(matched_rules)} rules matched "
            f"in {consultation_time:.2f}ms"
        )
        
        return result

    def get_rules_for_operation(
        self,
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[KnowledgeRule]:
        """
        Get rules specific to an operation type.
        
        Args:
            operation: Operation type (e.g., "refactoring", "tdd", "planning")
            context: Optional additional context
            
        Returns:
            List of relevant rules
        """
        context = context or {}
        context["operation"] = operation
        
        result = self.consult(context)
        return result.matched_rules

    def check_compliance(
        self,
        action: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if an action complies with knowledge rules.
        
        Args:
            action: Proposed action
            context: Current context
            
        Returns:
            Compliance report with violations and suggestions
        """
        context["proposed_action"] = action
        
        result = self.consult(
            context,
            categories=["security", "brain-protection", "data-integrity"]
        )
        
        violations = []
        suggestions = []
        
        for rule in result.matched_rules:
            # Check if action violates rule
            for condition in rule.conditions:
                if self._check_violation(action, condition):
                    violations.append({
                        "rule": rule.name,
                        "description": rule.description,
                        "severity": self._get_severity(rule.category)
                    })
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "suggestions": result.recommendations,
            "warnings": result.warnings
        }

    def invalidate_cache(self) -> None:
        """Invalidate all cached results."""
        self._query_cache.clear()
        self._cache_timestamps.clear()
        logger.info("Knowledge cache invalidated")

    def reload_library(self) -> None:
        """Reload the knowledge library from disk."""
        self._rules.clear()
        self._rules_by_category.clear()
        self._rules_loaded = 0
        self._load_knowledge_library()
        self.invalidate_cache()
        logger.info(f"Knowledge library reloaded: {self._rules_loaded} rules")

    def get_telemetry(self) -> Dict[str, Any]:
        """Get consultant telemetry."""
        return {
            "total_consultations": self._total_consultations,
            "cache_hits": self._cache_hits,
            "cache_hit_rate": (
                self._cache_hits / self._total_consultations
                if self._total_consultations > 0 else 0
            ),
            "rules_loaded": self._rules_loaded,
            "categories": list(self._rules_by_category.keys()),
            "top_used_rules": self._get_top_used_rules(5)
        }

    # ========================================================================
    # Private Methods
    # ========================================================================

    def _load_knowledge_library(self) -> None:
        """Load all knowledge files from the brain."""
        for rel_path in self.KNOWLEDGE_PATHS:
            knowledge_dir = self.brain_path / rel_path
            
            if not knowledge_dir.exists():
                continue
            
            # Load all YAML files
            for yaml_file in knowledge_dir.rglob("*.yaml"):
                try:
                    self._load_yaml_file(yaml_file)
                except Exception as e:
                    logger.warning(f"Failed to load {yaml_file}: {e}")
            
            # Load all YML files
            for yml_file in knowledge_dir.rglob("*.yml"):
                try:
                    self._load_yaml_file(yml_file)
                except Exception as e:
                    logger.warning(f"Failed to load {yml_file}: {e}")

    def _load_yaml_file(self, file_path: Path) -> None:
        """Load rules from a YAML file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            data = yaml.safe_load(content)
            
            if not data:
                return
            
            # Extract category from filename or content
            category = self._infer_category(file_path, data)
            
            # Process different YAML structures
            rules = self._extract_rules_from_yaml(data, category, str(file_path))
            
            for rule in rules:
                self._rules[rule.rule_id] = rule
                
                if category not in self._rules_by_category:
                    self._rules_by_category[category] = []
                self._rules_by_category[category].append(rule)
                
                self._rules_loaded += 1
                
        except yaml.YAMLError as e:
            logger.warning(f"YAML parse error in {file_path}: {e}")

    def _extract_rules_from_yaml(
        self,
        data: Dict[str, Any],
        category: str,
        source_file: str
    ) -> List[KnowledgeRule]:
        """Extract rules from YAML data."""
        rules = []
        
        # Handle 'rules' key
        if "rules" in data:
            for i, rule_data in enumerate(data["rules"]):
                rule = self._parse_rule(rule_data, category, source_file, i)
                if rule:
                    rules.append(rule)
        
        # Handle 'patterns' key
        elif "patterns" in data:
            for i, pattern_data in enumerate(data["patterns"]):
                rule = self._parse_pattern(pattern_data, category, source_file, i)
                if rule:
                    rules.append(rule)
        
        # Handle 'guidelines' key
        elif "guidelines" in data:
            for i, guideline_data in enumerate(data["guidelines"]):
                rule = self._parse_guideline(guideline_data, category, source_file, i)
                if rule:
                    rules.append(rule)
        
        # Handle direct rule structure
        elif "name" in data or "description" in data:
            rule = self._parse_rule(data, category, source_file, 0)
            if rule:
                rules.append(rule)
        
        return rules

    def _parse_rule(
        self,
        data: Dict[str, Any],
        category: str,
        source_file: str,
        index: int
    ) -> Optional[KnowledgeRule]:
        """Parse a single rule from data."""
        if not isinstance(data, dict):
            return None
        
        name = data.get("name", data.get("id", f"rule_{index}"))
        rule_id = f"{category}_{Path(source_file).stem}_{name}".replace(" ", "_").lower()
        
        return KnowledgeRule(
            rule_id=rule_id,
            category=category,
            name=name,
            description=data.get("description", data.get("desc", "")),
            conditions=data.get("conditions", data.get("when", [])),
            actions=data.get("actions", data.get("then", [])),
            precedence=self._get_precedence(category, data),
            source_file=source_file,
            metadata=data.get("metadata", {})
        )

    def _parse_pattern(
        self,
        data: Dict[str, Any],
        category: str,
        source_file: str,
        index: int
    ) -> Optional[KnowledgeRule]:
        """Parse a pattern as a rule."""
        return self._parse_rule(data, category, source_file, index)

    def _parse_guideline(
        self,
        data: Dict[str, Any],
        category: str,
        source_file: str,
        index: int
    ) -> Optional[KnowledgeRule]:
        """Parse a guideline as a rule."""
        return self._parse_rule(data, category, source_file, index)

    def _infer_category(self, file_path: Path, data: Dict[str, Any]) -> str:
        """Infer category from file path or content."""
        # Check content first
        if "category" in data:
            return data["category"].lower()
        
        # Infer from filename
        filename = file_path.stem.lower()
        
        for category in self.CATEGORY_PRIORITIES.keys():
            if category in filename:
                return category
        
        # Infer from parent directory
        parent = file_path.parent.name.lower()
        if parent in self.CATEGORY_PRIORITIES:
            return parent
        
        return "general"

    def _get_precedence(self, category: str, data: Dict[str, Any]) -> int:
        """Get rule precedence."""
        # Check explicit precedence
        if "precedence" in data:
            return data["precedence"]
        if "priority" in data:
            return data["priority"]
        
        # Use category priority
        return self.CATEGORY_PRIORITIES.get(category, 50)

    def _match_rules(
        self,
        context: Dict[str, Any],
        query: Optional[str],
        categories: Optional[List[str]]
    ) -> List[KnowledgeRule]:
        """Match rules to context."""
        matched = []
        
        # Filter by categories if specified
        if categories:
            candidate_rules = []
            for cat in categories:
                candidate_rules.extend(self._rules_by_category.get(cat, []))
        else:
            candidate_rules = list(self._rules.values())
        
        for rule in candidate_rules:
            score = self._calculate_match_score(rule, context, query)
            if score > 0:
                # Attach score to rule for sorting
                rule.metadata["match_score"] = score
                matched.append(rule)
        
        return matched

    def _calculate_match_score(
        self,
        rule: KnowledgeRule,
        context: Dict[str, Any],
        query: Optional[str]
    ) -> float:
        """Calculate how well a rule matches the context."""
        score = 0.0
        
        # Context key matching
        context_text = " ".join(str(v).lower() for v in context.values())
        rule_text = f"{rule.name} {rule.description}".lower()
        
        # Simple word overlap scoring
        context_words = set(context_text.split())
        rule_words = set(rule_text.split())
        
        overlap = context_words & rule_words
        if rule_words:
            score = len(overlap) / len(rule_words)
        
        # Query matching
        if query:
            query_lower = query.lower()
            if query_lower in rule_text:
                score += 0.5
            
            # Keyword matching
            query_words = set(query_lower.split())
            query_overlap = query_words & rule_words
            if query_words:
                score += len(query_overlap) / len(query_words) * 0.3
        
        # Operation matching
        if "operation" in context:
            op = context["operation"].lower()
            if op in rule.category or op in rule_text:
                score += 0.3
        
        return min(score, 1.0)

    def _extract_recommendations(self, rules: List[KnowledgeRule]) -> List[str]:
        """Extract recommendations from matched rules."""
        recommendations = []
        
        for rule in rules:
            # Add description as recommendation
            if rule.description:
                recommendations.append(f"📋 {rule.name}: {rule.description}")
            
            # Add actions as recommendations
            for action in rule.actions:
                if isinstance(action, str):
                    recommendations.append(f"  → {action}")
                elif isinstance(action, dict) and "do" in action:
                    recommendations.append(f"  → {action['do']}")
        
        return recommendations[:20]  # Limit to 20 recommendations

    def _extract_warnings(
        self,
        rules: List[KnowledgeRule],
        context: Dict[str, Any]
    ) -> List[str]:
        """Extract warnings from matched rules."""
        warnings = []
        
        for rule in rules:
            # Check for warning conditions
            if rule.category in ["security", "brain-protection"]:
                warnings.append(
                    f"⚠️ {rule.category.upper()}: {rule.name} - {rule.description}"
                )
        
        return warnings

    def _check_violation(
        self,
        action: str,
        condition: Dict[str, Any]
    ) -> bool:
        """Check if action violates a condition."""
        if not isinstance(condition, dict):
            return False
        
        # Check for forbidden patterns
        if "forbidden" in condition:
            for pattern in condition["forbidden"]:
                if re.search(pattern, action, re.IGNORECASE):
                    return True
        
        return False

    def _get_severity(self, category: str) -> str:
        """Get severity level for a category."""
        if category in ["security", "brain-protection"]:
            return "CRITICAL"
        elif category in ["data-integrity", "tdd"]:
            return "HIGH"
        elif category in ["refactoring", "performance"]:
            return "MEDIUM"
        else:
            return "LOW"

    def _make_cache_key(
        self,
        context: Dict[str, Any],
        query: Optional[str],
        categories: Optional[List[str]]
    ) -> str:
        """Create cache key from query parameters."""
        parts = [
            str(sorted(context.items())),
            query or "",
            str(sorted(categories)) if categories else ""
        ]
        return "|".join(parts)

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid."""
        if cache_key not in self._cache_timestamps:
            return False
        
        age = datetime.now() - self._cache_timestamps[cache_key]
        return age.total_seconds() < self.cache_ttl_seconds

    def _get_top_used_rules(self, n: int) -> List[Dict[str, Any]]:
        """Get top N most used rules."""
        sorted_rules = sorted(
            self._rule_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {"rule_id": rule_id, "usage_count": count}
            for rule_id, count in sorted_rules[:n]
        ]


# ============================================================================
# Integration Helper
# ============================================================================

def create_knowledge_consultant(
    brain_path: str,
    enable_caching: bool = True
) -> KnowledgeConsultant:
    """
    Factory function to create knowledge consultant.
    
    Args:
        brain_path: Path to cortex-brain directory
        enable_caching: Enable result caching
        
    Returns:
        Configured KnowledgeConsultant instance
    """
    return KnowledgeConsultant(
        brain_path=brain_path,
        enable_caching=enable_caching
    )
