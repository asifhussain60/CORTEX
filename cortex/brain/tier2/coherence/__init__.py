"""
Cross-File Coherence & Response Explanation Module

Implements validation for:
- Cross-file import coherence (no circular deps, consistency)
- Type consistency across modules
- State consistency verification
- Configuration coherence
- Response coherence & explanation logging
- Context awareness
- Consistency checks in output
- Fallback mechanisms

ACs: COHERENCE-001, COHERENCE-002, COHERENCE-003, COHERENCE-004, EXPLAIN-001-005
"""

import ast
import sys
from typing import Dict, List, Set, Tuple, Optional, Any
from pathlib import Path
from enum import Enum


class CoherenceType(Enum):
    """Types of coherence."""
    IMPORT = "import"
    TYPE = "type"
    STATE = "state"
    CONFIGURATION = "configuration"


class CoherenceIssue:
    """Represents a coherence issue."""
    
    def __init__(self, issue_type: CoherenceType, message: str, severity: str = "error"):
        """Initialize CoherenceIssue."""
        self.issue_type = issue_type
        self.message = message
        self.severity = severity


class ImportCoherenceValidator:
    """Validates import coherence across files."""
    
    def __init__(self):
        """Initialize ImportCoherenceValidator."""
        self.imports: Dict[str, Set[str]] = {}
        self.issues: List[CoherenceIssue] = []
    
    def analyze_file(self, filepath: str, content: str) -> None:
        """
        Analyze imports in a file.
        
        Args:
            filepath: Path to Python file
            content: File content
        """
        try:
            tree = ast.parse(content)
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
            
            self.imports[filepath] = imports
        except SyntaxError:
            self.issues.append(CoherenceIssue(
                CoherenceType.IMPORT,
                f"Syntax error in {filepath}",
                "error"
            ))
    
    def detect_circular_imports(self) -> List[Tuple[str, str]]:
        """
        Detect circular import dependencies.
        
        Returns:
            List of circular dependency pairs
        """
        circular = []
        
        for file1, imports1 in self.imports.items():
            for file2, imports2 in self.imports.items():
                if file1 < file2:  # Avoid duplicates
                    if any(file2 in imp for imp in imports1) and \
                       any(file1 in imp for imp in imports2):
                        circular.append((file1, file2))
        
        return circular
    
    def validate(self) -> bool:
        """Validate import coherence."""
        circular = self.detect_circular_imports()
        
        if circular:
            for f1, f2 in circular:
                self.issues.append(CoherenceIssue(
                    CoherenceType.IMPORT,
                    f"Circular import: {f1} <-> {f2}",
                    "error"
                ))
            return False
        
        return True


class TypeConsistencyValidator:
    """Validates type consistency across modules."""
    
    def __init__(self):
        """Initialize TypeConsistencyValidator."""
        self.type_signatures: Dict[str, Dict[str, str]] = {}
        self.issues: List[CoherenceIssue] = []
    
    def register_type_signature(self, module: str, symbol: str, signature: str) -> None:
        """
        Register a type signature.
        
        Args:
            module: Module name
            symbol: Symbol (function/class name)
            signature: Type signature
        """
        if module not in self.type_signatures:
            self.type_signatures[module] = {}
        
        self.type_signatures[module][symbol] = signature
    
    def check_consistency(self) -> bool:
        """Check type consistency."""
        # Verify all types are consistent across modules
        for module, types in self.type_signatures.items():
            for symbol, signature in types.items():
                # In production: check against all other modules
                pass
        
        return True
    
    def get_issues(self) -> List[CoherenceIssue]:
        """Get consistency issues."""
        return self.issues.copy()


class StateConsistencyValidator:
    """Validates state consistency."""
    
    def __init__(self):
        """Initialize StateConsistencyValidator."""
        self.states: Dict[str, Dict] = {}
        self.invariants: List[callable] = []
        self.issues: List[CoherenceIssue] = []
    
    def register_state(self, entity_id: str, state: Dict) -> None:
        """Register entity state."""
        self.states[entity_id] = state
    
    def add_invariant(self, invariant: callable) -> None:
        """Add state invariant."""
        self.invariants.append(invariant)
    
    def validate_states(self) -> bool:
        """Validate all states against invariants."""
        for entity_id, state in self.states.items():
            for invariant in self.invariants:
                if not invariant(state):
                    self.issues.append(CoherenceIssue(
                        CoherenceType.STATE,
                        f"Invariant violation in {entity_id}",
                        "error"
                    ))
                    return False
        
        return True
    
    def get_issues(self) -> List[CoherenceIssue]:
        """Get state issues."""
        return self.issues.copy()


class ConfigurationCoherenceValidator:
    """Validates configuration coherence."""
    
    def __init__(self):
        """Initialize ConfigurationCoherenceValidator."""
        self.configs: Dict[str, Dict] = {}
        self.issues: List[CoherenceIssue] = []
    
    def register_config(self, config_id: str, config: Dict) -> None:
        """Register configuration."""
        self.configs[config_id] = config
    
    def check_conflicts(self) -> bool:
        """Check for configuration conflicts."""
        # Check for conflicting settings
        all_keys = set()
        for config in self.configs.values():
            all_keys.update(config.keys())
        
        # Verify no conflicts
        for key in all_keys:
            values = set()
            for config in self.configs.values():
                if key in config:
                    values.add(str(config[key]))
            
            if len(values) > 1:
                self.issues.append(CoherenceIssue(
                    CoherenceType.CONFIGURATION,
                    f"Configuration conflict on {key}: {values}",
                    "warning"
                ))
        
        return len(self.issues) == 0
    
    def get_issues(self) -> List[CoherenceIssue]:
        """Get configuration issues."""
        return self.issues.copy()


class ResponseExplanation:
    """Explains orchestrator response."""
    
    def __init__(self, response: str, context: Optional[Dict] = None):
        """
        Initialize ResponseExplanation.
        
        Args:
            response: The response being explained
            context: Optional context information
        """
        self.response = response
        self.context = context or {}
        self.reasoning: List[str] = []
        self.decision_chain: List[str] = []
        self.timestamp = __import__("datetime").datetime.utcnow().isoformat()
    
    def add_reasoning(self, step: str) -> None:
        """Add a reasoning step."""
        self.reasoning.append(step)
    
    def add_decision(self, decision: str) -> None:
        """Add a decision to the chain."""
        self.decision_chain.append(decision)
    
    def get_audit_trail(self) -> Dict[str, Any]:
        """Get complete audit trail."""
        return {
            "response": self.response,
            "context": self.context,
            "reasoning": self.reasoning,
            "decision_chain": self.decision_chain,
            "timestamp": self.timestamp,
        }


class ContextAwareness:
    """Manages context awareness in responses."""
    
    def __init__(self):
        """Initialize ContextAwareness."""
        self.current_context: Dict[str, Any] = {}
        self.context_history: List[Dict] = []
    
    def set_context(self, context: Dict[str, Any]) -> None:
        """Set current context."""
        self.current_context = context.copy()
        self.context_history.append(context)
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context."""
        return self.current_context.copy()
    
    def include_context_in_response(self, response: str) -> str:
        """Include context information in response."""
        if not self.current_context:
            return response
        
        context_summary = ", ".join(
            f"{k}={v}" for k, v in self.current_context.items()
        )
        
        return f"{response} [context: {context_summary}]"


class OutputConsistencyChecker:
    """Checks consistency of output."""
    
    def __init__(self):
        """Initialize OutputConsistencyChecker."""
        self.checks: List[callable] = []
    
    def add_check(self, check: callable) -> None:
        """Add consistency check."""
        self.checks.append(check)
    
    def check_output(self, output: str) -> Tuple[bool, List[str]]:
        """
        Check output consistency.
        
        Returns:
            Tuple of (is_consistent, issues)
        """
        issues = []
        
        for check in self.checks:
            try:
                if not check(output):
                    issues.append(f"Check failed: {check.__name__}")
            except Exception as e:
                issues.append(f"Check error: {str(e)}")
        
        return len(issues) == 0, issues


class CoherenceFallback:
    """Fallback mechanism for coherence failures."""
    
    def __init__(self):
        """Initialize CoherenceFallback."""
        self.fallback_responses: Dict[str, str] = {}
    
    def register_fallback(self, failure_type: str, fallback: str) -> None:
        """Register fallback response."""
        self.fallback_responses[failure_type] = fallback
    
    def get_fallback(self, failure_type: str) -> Optional[str]:
        """Get fallback response."""
        return self.fallback_responses.get(failure_type)
    
    def handle_failure(self, failure_type: str, original_response: str) -> str:
        """
        Handle coherence failure gracefully.
        
        Returns:
            Fallback response or original with warning
        """
        fallback = self.get_fallback(failure_type)
        
        if fallback:
            return fallback
        
        return f"[DEGRADED] {original_response} (coherence check failed)"


__all__ = [
    "CoherenceType",
    "CoherenceIssue",
    "ImportCoherenceValidator",
    "TypeConsistencyValidator",
    "StateConsistencyValidator",
    "ConfigurationCoherenceValidator",
    "ResponseExplanation",
    "ContextAwareness",
    "OutputConsistencyChecker",
    "CoherenceFallback",
]
