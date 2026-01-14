"""
Intelligence Middleware - User Mistake Prevention Layer.

Provides intelligent validation to prevent common user mistakes before
orchestrator execution. Part of feat04-core-orchestration intelligence layer.

Author: CORTEX feat04-core-orchestration Phase 1
Created: 2026-01-08
Version: 1.0.0
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml
import re
import logging


@dataclass
class IntelligenceRule:
    """Intelligence validation rule."""
    
    id: str
    name: str
    category: str
    severity: str  # "error" | "warning" | "info"
    condition: str
    message: str
    suggestion: Optional[str] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def evaluate(
        self,
        orchestrator_id: str,
        params: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """
        Evaluate if rule applies to current execution.
        
        Args:
            orchestrator_id: Orchestrator being validated
            params: Execution parameters
            context: Execution context
        
        Returns:
            True if rule is violated, False otherwise
        """
        # Simple condition evaluation based on rule category
        if self.category == "planning_vs_implementation":
            return self._check_planning_implementation(orchestrator_id, params)
        
        elif self.category == "missing_prerequisites":
            return self._check_prerequisites(orchestrator_id, context)
        
        elif self.category == "yaml_first":
            return self._check_yaml_first(params)
        
        elif self.category == "governance_integration":
            return self._check_governance(context)
        
        elif self.category == "todo_dependencies":
            return self._check_todo_dependencies(context)
        
        return False
    
    def _check_planning_implementation(
        self,
        orchestrator_id: str,
        params: Dict[str, Any]
    ) -> bool:
        """Check for planning vs implementation violation."""
        # Only applies to planning orchestrator
        if "planning" not in orchestrator_id.lower():
            return False
        
        # Check if params contain implementation keywords
        # Convert all param values to strings for searching
        params_str = " ".join([
            str(v).lower() for v in params.values()
        ])
        
        implementation_keywords = ["implement", "write code", "create file", "execute", "code"]
        
        return any(keyword in params_str for keyword in implementation_keywords)
    
    def _check_prerequisites(
        self,
        orchestrator_id: str,
        context: Dict[str, Any]
    ) -> bool:
        """Check for missing prerequisites."""
        if "implement" not in orchestrator_id.lower():
            return False
        
        return not context.get("test_framework_exists", True)
    
    def _check_yaml_first(self, params: Dict[str, Any]) -> bool:
        """Check for YAML-first violations."""
        file_path = params.get("file_path", "")
        if not file_path:
            return False
        
        # Check blocked patterns
        blocked_patterns = [
            r".*-PLAN\.md$",
            r".*-plan\.md$",
            r".*-implementation-plan\.md$",
            r"cortex-brain/documents/planning/.*-design\.md$"
        ]
        
        # Check if file matches any blocked pattern
        for pattern in blocked_patterns:
            if re.match(pattern, file_path):
                # Check if it's in allowed exceptions
                allowed_patterns = [
                    r"README\.md$",
                    r"CONTINUATION-PROMPT\.md$",
                    r"cortex-brain/documents/architecture/.*\.md$"
                ]
                
                if not any(re.match(p, file_path) for p in allowed_patterns):
                    return True
        
        return False
    
    def _check_governance(self, context: Dict[str, Any]) -> bool:
        """Check if governance was skipped."""
        return context.get("governance_check_skipped", False)
    
    def _check_todo_dependencies(self, context: Dict[str, Any]) -> bool:
        """Check TODO dependency violations."""
        if not context.get("has_parent_todo", False):
            return False
        
        todo_status = context.get("todo_status", "")
        return todo_status == "BLOCKED"


@dataclass
class ValidationResult:
    """Result of intelligence validation."""
    
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def format_error_message(self) -> str:
        """
        Format user-friendly error message with suggestions.
        
        Returns:
            Formatted error message
        """
        if not self.errors:
            return "Validation passed"
        
        lines = ["⚠️ Cannot proceed with this operation:", ""]
        lines.extend([f"  • {error}" for error in self.errors])
        
        if self.suggestions:
            lines.extend(["", "💡 Suggestions:", ""])
            lines.extend([f"  • {suggestion}" for suggestion in self.suggestions])
        
        return "\n".join(lines)


class IntelligenceMiddleware:
    """
    Intelligence middleware for user mistake prevention.
    
    Validates orchestrator execution requests before they run,
    catching common mistakes and providing helpful suggestions.
    
    Features:
    - Planning vs implementation separation
    - Missing prerequisites detection
    - YAML-first enforcement
    - Governance integration checking
    - TODO dependency validation
    
    Usage:
        middleware = IntelligenceMiddleware(
            rules_path="cortex-brain/config/intelligence-rules.yaml"
        )
        
        result = middleware.validate_execution(
            orchestrator_id="planning_orchestrator",
            params={"request": "plan and implement auth"},
            context={}
        )
        
        if not result.is_valid:
            print(result.format_error_message())
    """
    
    def __init__(
        self,
        rules_path: str,
        governance_merger: Optional[Any] = None,
        todo_orchestrator: Optional[Any] = None
    ):
        """
        Initialize intelligence middleware.
        
        Args:
            rules_path: Path to intelligence-rules.yaml
            governance_merger: Optional GovernanceMerger for rule checking
            todo_orchestrator: Optional TodoOrchestrator for dependency checking
        """
        self.rules_path = Path(rules_path)
        self.governance_merger = governance_merger
        self.todo_orchestrator = todo_orchestrator
        self.logger = logging.getLogger("cortex.intelligence")
        
        # Load rules from YAML
        self.rules = self._load_rules()
        
        self.logger.info(
            f"IntelligenceMiddleware initialized with {len(self.rules)} rules"
        )
    
    def _load_rules(self) -> List[IntelligenceRule]:
        """
        Load intelligence rules from YAML configuration.
        
        Returns:
            List of IntelligenceRule objects
        """
        if not self.rules_path.exists():
            self.logger.warning(f"Rules file not found: {self.rules_path}")
            return []
        
        try:
            with open(self.rules_path, 'r') as f:
                config = yaml.safe_load(f)
            
            rules = []
            for rule_data in config.get('rules', []):
                rule = IntelligenceRule(
                    id=rule_data['id'],
                    name=rule_data['name'],
                    category=rule_data['category'],
                    severity=rule_data['severity'],
                    condition=rule_data.get('condition', ''),
                    message=rule_data['message'],
                    suggestion=rule_data.get('suggestion'),
                    enabled=rule_data.get('enabled', True),
                    metadata={}
                )
                rules.append(rule)
            
            self.logger.debug(f"Loaded {len(rules)} rules from {self.rules_path}")
            return rules
        
        except Exception as e:
            self.logger.error(f"Failed to load rules: {e}", exc_info=True)
            return []
    
    def validate_execution(
        self,
        orchestrator_id: str,
        params: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate orchestrator execution before it starts.
        
        Args:
            orchestrator_id: ID of orchestrator to execute
            params: Execution parameters
            context: Execution context
        
        Returns:
            ValidationResult with validation status and messages
        """
        errors = []
        warnings = []
        suggestions = []
        rules_evaluated = 0
        rules_triggered = 0
        
        # Evaluate each enabled rule
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            rules_evaluated += 1
            
            # Check if rule is violated
            is_violated = rule.evaluate(orchestrator_id, params, context)
            
            if is_violated:
                rules_triggered += 1
                
                # Add to errors or warnings based on severity
                if rule.severity == "error":
                    errors.append(rule.message)
                elif rule.severity == "warning":
                    warnings.append(rule.message)
                
                # Add suggestion if available
                if rule.suggestion:
                    suggestions.append(rule.suggestion)
                
                self.logger.info(
                    f"Rule triggered: {rule.id} ({rule.severity}) - {rule.name}"
                )
        
        # Validation passes if no errors (warnings are non-blocking)
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            metadata={
                "rules_evaluated": rules_evaluated,
                "rules_triggered": rules_triggered,
                "orchestrator_id": orchestrator_id
            }
        )
    
    def reload_rules(self) -> None:
        """Reload rules from configuration file."""
        self.logger.info("Reloading intelligence rules...")
        self.rules = self._load_rules()
        self.logger.info(f"Reloaded {len(self.rules)} rules")
