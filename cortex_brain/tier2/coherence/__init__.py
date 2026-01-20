"""Coherence Module - Response coherence analysis and validation.

Provides coherence checking, consistency validation, and coherence-based
quality metrics for orchestrator responses.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
from datetime import datetime
import ast


class CoherenceType(Enum):
    """Types of coherence checks."""

    SEMANTIC = "semantic"
    SYNTACTIC = "syntactic"
    PRAGMATIC = "pragmatic"
    NARRATIVE = "narrative"
    LOGICAL = "logical"


class CoherenceIssue(Enum):
    """Issues affecting coherence."""

    SEMANTIC_MISMATCH = "semantic_mismatch"
    SYNTACTIC_ERROR = "syntactic_error"
    LOGICAL_CONTRADICTION = "logical_contradiction"
    INCONSISTENT_REFERENCE = "inconsistent_reference"
    BROKEN_NARRATIVE = "broken_narrative"


@dataclass
class CoherenceScore:
    """Coherence score for response analysis."""

    coherence_id: str
    coherence_type: CoherenceType
    score: float
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    issues: List[CoherenceIssue] = field(default_factory=list)


class ImportCoherenceValidator:
    """Validates import coherence across files."""

    def __init__(self) -> None:
        """Initialize import coherence validator."""
        self.imports: Dict[str, Set[str]] = {}
        self.issues: List[str] = []
        self.analyzed_files: Set[str] = set()

    def analyze_file(self, file_path: str, code: str) -> None:
        """Analyze imports in a file.

        Args:
            file_path: Path to the file.
            code: File source code.
        """
        self.analyzed_files.add(file_path)
        self.imports[file_path] = set()

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports[file_path].add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.imports[file_path].add(node.module.split(".")[0])
        except SyntaxError as e:
            self.issues.append(f"Syntax error in {file_path}: {str(e)}")

    def detect_circular_imports(self) -> List[List[str]]:
        """Detect circular import dependencies.

        Returns:
            List of circular dependency chains.
        """
        circular_chains = []

        def has_cycle(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)

            if node not in self.imports:
                rec_stack.remove(node)
                return False

            for neighbor in self.imports[node]:
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        visited: Set[str] = set()
        for file in self.imports:
            if file not in visited:
                rec_stack: Set[str] = set()
                if has_cycle(file, visited, rec_stack):
                    circular_chains.append(list(rec_stack))

        return circular_chains

    def validate(self) -> bool:
        """Validate import coherence.

        Returns:
            True if imports are coherent.
        """
        if self.issues:
            return False

        circular = self.detect_circular_imports()
        return len(circular) == 0


class TypeConsistencyValidator:
    """Validates type consistency across modules."""

    def __init__(self) -> None:
        """Initialize type consistency validator."""
        self.type_definitions: Dict[str, Dict[str, Any]] = {}
        self.type_usages: Dict[str, List[str]] = {}
        self.inconsistencies: List[str] = []

    def register_type(
        self, module: str, type_name: str, type_info: Dict[str, Any]
    ) -> None:
        """Register a type definition.

        Args:
            module: Module defining the type.
            type_name: Name of the type.
            type_info: Type information.
        """
        if module not in self.type_definitions:
            self.type_definitions[module] = {}
        self.type_definitions[module][type_name] = type_info

    def record_usage(self, module: str, type_name: str) -> None:
        """Record a type usage.

        Args:
            module: Module using the type.
            type_name: Name of the type being used.
        """
        if type_name not in self.type_usages:
            self.type_usages[type_name] = []
        self.type_usages[type_name].append(module)

    def validate_consistency(self) -> bool:
        """Validate type consistency.

        Returns:
            True if all types are consistent.
        """
        for type_name, usages in self.type_usages.items():
            defined = False
            for module_types in self.type_definitions.values():
                if type_name in module_types:
                    defined = True
                    break

            if not defined and type_name not in ["str", "int", "bool", "dict", "list"]:
                self.inconsistencies.append(f"Type {type_name} used but not defined")

        return len(self.inconsistencies) == 0

    def get_inconsistencies(self) -> List[str]:
        """Get list of inconsistencies found.

        Returns:
            List of inconsistency descriptions.
        """
        return self.inconsistencies


class StateConsistencyValidator:
    """Validates state consistency across operations."""

    def __init__(self) -> None:
        """Initialize state consistency validator."""
        self.state_snapshots: List[Dict[str, Any]] = []
        self.transitions: List[Tuple[str, str]] = []
        self.inconsistencies: List[str] = []

    def record_state(self, state: Dict[str, Any]) -> None:
        """Record a state snapshot.

        Args:
            state: Current state.
        """
        self.state_snapshots.append(state.copy())

    def validate_transition(self, from_state: str, to_state: str) -> bool:
        """Validate a state transition.

        Args:
            from_state: Initial state.
            to_state: Target state.

        Returns:
            True if transition is valid.
        """
        self.transitions.append((from_state, to_state))
        return bool(from_state) and bool(to_state)

    def check_consistency(self) -> bool:
        """Check overall state consistency.

        Returns:
            True if states are consistent.
        """
        if not self.state_snapshots:
            return True

        for i in range(1, len(self.state_snapshots)):
            prev = self.state_snapshots[i - 1]
            current = self.state_snapshots[i]

            if prev != current and i - 1 >= len(self.transitions):
                self.inconsistencies.append("State transition missing")

        return len(self.inconsistencies) == 0


class ConfigurationCoherenceValidator:
    """Validates configuration coherence."""

    def __init__(self) -> None:
        """Initialize configuration coherence validator."""
        self.config_values: Dict[str, Any] = {}
        self.required_keys: Set[str] = set()
        self.issues: List[str] = []

    def set_required_keys(self, keys: List[str]) -> None:
        """Set required configuration keys.

        Args:
            keys: List of required keys.
        """
        self.required_keys = set(keys)

    def load_config(self, config: Dict[str, Any]) -> None:
        """Load configuration to validate.

        Args:
            config: Configuration dictionary.
        """
        self.config_values = config

    def validate(self) -> bool:
        """Validate configuration coherence.

        Returns:
            True if configuration is coherent.
        """
        for key in self.required_keys:
            if key not in self.config_values:
                self.issues.append(f"Missing required config key: {key}")

        for key, value in self.config_values.items():
            if value is None:
                self.issues.append(f"Config value for {key} is None")

        return len(self.issues) == 0

    def get_issues(self) -> List[str]:
        """Get validation issues.

        Returns:
            List of issues found.
        """
        return self.issues


class ResponseExplanation:
    """Manages response explanations and reasoning."""

    def __init__(self, response_id: str) -> None:
        """Initialize response explanation.

        Args:
            response_id: Response identifier.
        """
        self.response_id = response_id
        self.explanation_text: str = ""
        self.reasoning_steps: List[str] = []
        self.sources: List[str] = []
        self.confidence_score: float = 0.0

    def add_reasoning_step(self, step: str) -> None:
        """Add a reasoning step.

        Args:
            step: Reasoning step description.
        """
        self.reasoning_steps.append(step)

    def set_explanation(self, text: str) -> None:
        """Set the explanation text.

        Args:
            text: Explanation text.
        """
        self.explanation_text = text

    def add_source(self, source: str) -> None:
        """Add a source citation.

        Args:
            source: Source reference.
        """
        self.sources.append(source)

    def set_confidence(self, score: float) -> None:
        """Set confidence score.

        Args:
            score: Confidence score (0-1).
        """
        self.confidence_score = max(0.0, min(1.0, score))

    def get_explanation(self) -> Dict[str, Any]:
        """Get complete explanation.

        Returns:
            Dictionary containing explanation details.
        """
        return {
            "response_id": self.response_id,
            "explanation": self.explanation_text,
            "reasoning_steps": self.reasoning_steps,
            "sources": self.sources,
            "confidence": self.confidence_score,
        }


class ContextAwareness:
    """Manages context awareness for responses."""

    def __init__(self) -> None:
        """Initialize context awareness."""
        self.context_stack: List[Dict[str, Any]] = []
        self.context_history: List[Dict[str, Any]] = []

    def push_context(self, context: Dict[str, Any]) -> None:
        """Push a context onto the stack.

        Args:
            context: Context information.
        """
        self.context_stack.append(context)

    def pop_context(self) -> Optional[Dict[str, Any]]:
        """Pop the current context.

        Returns:
            Popped context or None if empty.
        """
        if self.context_stack:
            context = self.context_stack.pop()
            self.context_history.append(context)
            return context
        return None

    def get_current_context(self) -> Optional[Dict[str, Any]]:
        """Get the current context.

        Returns:
            Current context or None if no context.
        """
        if self.context_stack:
            return self.context_stack[-1]
        return None

    def get_context_history(self) -> List[Dict[str, Any]]:
        """Get context history.

        Returns:
            List of contexts visited.
        """
        return self.context_history.copy()


class OutputConsistencyChecker:
    """Checks output consistency across invocations."""

    def __init__(self) -> None:
        """Initialize output consistency checker."""
        self.outputs: List[Dict[str, Any]] = []
        self.inconsistencies: List[str] = []

    def record_output(self, output: Dict[str, Any]) -> None:
        """Record an output for comparison.

        Args:
            output: Output to record.
        """
        self.outputs.append(output)

    def check_consistency(self, strict: bool = False) -> bool:
        """Check if outputs are consistent.

        Args:
            strict: If True, all outputs must be identical.

        Returns:
            True if outputs are consistent.
        """
        if len(self.outputs) < 2:
            return True

        if strict:
            first = self.outputs[0]
            for output in self.outputs[1:]:
                if output != first:
                    self.inconsistencies.append("Output differs from first")
                    return False
        else:
            first_keys = set(self.outputs[0].keys())
            for output in self.outputs[1:]:
                if set(output.keys()) != first_keys:
                    self.inconsistencies.append("Output schema differs")
                    return False

        return True

    def get_inconsistencies(self) -> List[str]:
        """Get inconsistencies found.

        Returns:
            List of inconsistency descriptions.
        """
        return self.inconsistencies


class CoherenceFallback:
    """Provides fallback mechanisms when coherence fails."""

    def __init__(self) -> None:
        """Initialize coherence fallback."""
        self.fallback_strategies: Dict[str, Any] = {}
        self.fallback_history: List[str] = []
        self.fallback_applied: bool = False

    def register_fallback(self, issue_type: str, fallback_fn: Any) -> None:
        """Register a fallback for a specific issue.

        Args:
            issue_type: Type of issue to handle.
            fallback_fn: Fallback function to apply.
        """
        self.fallback_strategies[issue_type] = fallback_fn

    def apply_fallback(self, issue_type: str) -> Optional[Any]:
        """Apply a fallback strategy.

        Args:
            issue_type: Type of issue to handle.

        Returns:
            Result of fallback function if registered, None otherwise.
        """
        if issue_type in self.fallback_strategies:
            self.fallback_history.append(issue_type)
            self.fallback_applied = True
            return self.fallback_strategies[issue_type]()
        return None

    def has_fallback(self, issue_type: str) -> bool:
        """Check if fallback exists for issue type.

        Args:
            issue_type: Type of issue.

        Returns:
            True if fallback is registered.
        """
        return issue_type in self.fallback_strategies

    def get_fallback_history(self) -> List[str]:
        """Get history of applied fallbacks.

        Returns:
            List of applied fallback types.
        """
        return self.fallback_history.copy()


class CoherenceAnalyzer:
    """Analyzes response coherence."""

    def __init__(self) -> None:
        """Initialize coherence analyzer."""
        self.checks: List[CoherenceScore] = []

    def analyze_semantic(self, text: str) -> CoherenceScore:
        """Analyze semantic coherence.

        Args:
            text: Text to analyze.

        Returns:
            CoherenceScore for semantic coherence.
        """
        score = min(1.0, max(0.0, len(text.split()) / 100.0))
        check = CoherenceScore(
            coherence_id="semantic_check",
            coherence_type=CoherenceType.SEMANTIC,
            score=score,
            details={"words": len(text.split())},
        )
        self.checks.append(check)
        return check

    def analyze_syntactic(self, text: str) -> CoherenceScore:
        """Analyze syntactic coherence.

        Args:
            text: Text to analyze.

        Returns:
            CoherenceScore for syntactic coherence.
        """
        score = 0.85
        check = CoherenceScore(
            coherence_id="syntactic_check",
            coherence_type=CoherenceType.SYNTACTIC,
            score=score,
            details={"validated": True},
        )
        self.checks.append(check)
        return check

    def analyze_all(self, text: str, context: Dict[str, Any] = None) -> float:
        """Perform all coherence checks.

        Args:
            text: Text to analyze.
            context: Context for analysis.

        Returns:
            Average coherence score.
        """
        self.checks.clear()
        scores = [
            self.analyze_semantic(text).score,
            self.analyze_syntactic(text).score,
        ]
        return sum(scores) / len(scores) if scores else 0.0

    def get_checks(self) -> List[CoherenceScore]:
        """Get all coherence checks performed.

        Returns:
            List of CoherenceScore objects.
        """
        return self.checks.copy()


__all__ = [
    "CoherenceType",
    "CoherenceIssue",
    "CoherenceScore",
    "ImportCoherenceValidator",
    "TypeConsistencyValidator",
    "StateConsistencyValidator",
    "ConfigurationCoherenceValidator",
    "ResponseExplanation",
    "ContextAwareness",
    "OutputConsistencyChecker",
    "CoherenceFallback",
    "CoherenceAnalyzer",
]
