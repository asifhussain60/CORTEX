"""
IntentRouter Refactoring - Spec-Driven Intent Classification

AC-PERMANENT-FIX-010 Phase 4: Replace hardcoded keyword lists with
spec-driven intent classification using routing-rules-intent.yaml.

This module implements spec-based intent detection that replaces:
- IMPLEMENT_KEYWORDS (hardcoded list)
- FIX_KEYWORDS (hardcoded list)
- REFACTOR_KEYWORDS (hardcoded list)
- FILE_CREATION_KEYWORDS (hardcoded list)

With:
- routing_rules from routing-rules-intent.yaml
- Spec-driven keyword matching
- Structured error codes (GOVE_NNN format)

CORE Rules Applied:
- CORE-008: TDD (tests before implementation)
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
- CORE-030: Implementation truth (verified against specs)
- CORE-040: Execution specification mandate

Type Hints: 100% ✅
Docstrings: 100% ✅
"""

from dataclasses import dataclass
from typing import Any, Dict, List

# This module documents the refactoring approach
# The actual refactoring will be applied to intent_router.py


@dataclass
class RefactoringChanges:
    """Documents the changes needed for spec-driven intent routing."""

    target_file: str = "cortex/orchestrators/core/intent_router.py"

    changes: List[Dict[str, Any]] = None  # type: ignore

    def __post_init__(self) -> None:
        """Initialize refactoring changes."""
        if self.changes is None:
            self.changes = [
                {
                    "change_type": "REMOVE",
                    "location": "Lines 128-149 (class-level keyword lists)",
                    "what_to_remove": [
                        "IMPLEMENT_KEYWORDS list",
                        "FIX_KEYWORDS list",
                        "REFACTOR_KEYWORDS list",
                        "FILE_CREATION_KEYWORDS list"
                    ],
                    "reason": "These are now defined in routing-rules-intent.yaml"
                },
                {
                    "change_type": "MODIFY",
                    "location": "Lines 151-184 (__init__ method)",
                    "what_to_change": "operation_type_mappings initialization",
                    "old_code": """
            self.operation_type_mappings: Dict[IntentType, List[str]] = {
                IntentType.IMPLEMENT: self.IMPLEMENT_KEYWORDS,
                IntentType.FIX: self.FIX_KEYWORDS,
                IntentType.REFACTOR: self.REFACTOR_KEYWORDS,
                IntentType.FILE_CREATION: self.FILE_CREATION_KEYWORDS,
            }
                    """,
                    "new_code": """
            # Load keyword mappings from SpecRegistry
            try:
                routing_rules = self.spec_registry.get_routing_rules()
                self.operation_type_mappings = self._build_keyword_mappings(routing_rules)
            except Exception as e:
                # Fallback if spec loading fails
                self.logger.log_operation_complete(
                    ac_id="AC-PERMANENT-FIX-010",
                    operation="SPEC_LOADING_ERROR",
                    success=False,
                    details={"error": str(e)}
                )
                self.operation_type_mappings = {}
                    """,
                    "reason": "Load keywords from YAML spec via SpecRegistry"
                },
                {
                    "change_type": "MODIFY",
                    "location": "__init__ method",
                    "what_to_change": "Add SpecRegistry initialization",
                    "code_to_add": """
        # Initialize SpecRegistry for spec-driven routing
        from cortex.execution.spec_registry_impl import SpecRegistry
        self.spec_registry = SpecRegistry.get_registry()
                    """,
                    "reason": "Enable loading routing rules from YAML spec"
                },
                {
                    "change_type": "MODIFY",
                    "location": "__init__ method",
                    "what_to_change": "routing_rules initialization",
                    "old_code": """
            # Routing rules: (intent_type, domain) -> target_handler
            self.routing_rules: Dict[Tuple[Optional[IntentType], Optional[str]], str] = {
                # IMPLEMENT routing
                (IntentType.IMPLEMENT, "orchestrators"): "ImplementationOrchestrator",
                ...
            }
                    """,
                    "new_code": """
            # Load routing rules from spec
            try:
                routing_spec = self.spec_registry.get_routing_rules()
                self.routing_rules = self._build_routing_rules(routing_spec)
            except Exception as e:
                self.logger.log_operation_complete(
                    ac_id="AC-PERMANENT-FIX-010",
                    operation="ROUTING_SPEC_LOAD_ERROR",
                    success=False,
                    details={"error": str(e)}
                )
                self.routing_rules = {}
                    """,
                    "reason": "Load routing decisions from YAML spec"
                },
                {
                    "change_type": "ADD_NEW_METHOD",
                    "location": "After __init__ method",
                    "method_name": "_build_keyword_mappings",
                    "signature": "_build_keyword_mappings(self, routing_rules: Dict[str, Any]) -> Dict[IntentType, List[str]]",
                    "purpose": "Build keyword-to-intent mappings from routing spec",
                    "implementation_steps": [
                        "1. Iterate through routing_rules['intents']",
                        "2. For each intent, extract 'id' and 'keywords'",
                        "3. Map IntentType enum value to keywords list",
                        "4. Return mapping dict",
                        "5. Handle missing keywords gracefully"
                    ],
                    "returns": "Dict[IntentType, List[str]] mapping"
                },
                {
                    "change_type": "ADD_NEW_METHOD",
                    "location": "After __init__ method",
                    "method_name": "_build_routing_rules",
                    "signature": "_build_routing_rules(self, routing_spec: Dict[str, Any]) -> Dict[Tuple[Optional[IntentType], Optional[str]], str]",
                    "purpose": "Build routing decisions from routing spec",
                    "implementation_steps": [
                        "1. Load routing rules from routing-rules-intent.yaml",
                        "2. Use spec_registry.get_handler_for_intent()",
                        "3. Return routing map"
                    ],
                    "returns": "Dict with routing decisions"
                },
                {
                    "change_type": "MODIFY",
                    "location": "detect_intent method",
                    "what_to_change": "Use spec-driven keyword matching",
                    "current_behavior": "Uses self.operation_type_mappings (hardcoded lists)",
                    "new_behavior": "Uses self.operation_type_mappings from spec",
                    "no_code_change_needed": True,
                    "reason": "If __init__ loads specs, detect_intent uses them automatically"
                },
                {
                    "change_type": "MODIFY",
                    "location": "_route_internal method",
                    "what_to_change": "Use spec_registry.get_handler_for_intent()",
                    "old_code": """
            target_handler = self.routing_rules.get(
                routing_key,
                f"{intent_type.value.capitalize()}OrchestrationHandler"
            )
                    """,
                    "new_code": """
            # Use spec registry to get handler
            handler = self.spec_registry.get_handler_for_intent(intent_type.value)
            target_handler = handler or f"{intent_type.value.capitalize()}OrchestrationHandler"
                    """,
                    "reason": "Spec-driven handler selection"
                },
                {
                    "change_type": "MODIFY",
                    "location": "Error handling throughout",
                    "what_to_change": "Replace English error messages with GOVE_NNN codes",
                    "error_codes": [
                        "GOVE_INTENT_UNCLASSIFIED",
                        "GOVE_ROUTING_FAILED",
                        "GOVE_INVALID_CONTEXT",
                        "GOVE_HANDLER_NOT_FOUND"
                    ],
                    "reason": "CORE-040-003: Structured violation codes"
                }
            ]


class IntentRouterRefactoringGuide:
    """Step-by-step guide for refactoring IntentRouter."""

    @staticmethod
    def get_refactoring_steps() -> List[Dict[str, str]]:
        """Get ordered refactoring steps."""
        return [
            {
                "step": "1. Add imports",
                "code": "from cortex.execution.spec_registry_impl import SpecRegistry",
                "reason": "Enable spec loading"
            },
            {
                "step": "2. Initialize SpecRegistry in __init__",
                "code": "self.spec_registry = SpecRegistry.get_registry()",
                "reason": "Load routing specs"
            },
            {
                "step": "3. Remove hardcoded keyword lists",
                "code": "Delete IMPLEMENT_KEYWORDS, FIX_KEYWORDS, REFACTOR_KEYWORDS, FILE_CREATION_KEYWORDS",
                "reason": "These are now in routing-rules-intent.yaml"
            },
            {
                "step": "4. Add _build_keyword_mappings method",
                "code": "See implementation steps above",
                "reason": "Build keyword mappings from spec"
            },
            {
                "step": "5. Update operation_type_mappings initialization",
                "code": "Use spec_registry.get_routing_rules()",
                "reason": "Load from YAML instead of hardcoding"
            },
            {
                "step": "6. Add _build_routing_rules method",
                "code": "See implementation steps above",
                "reason": "Build routing rules from spec"
            },
            {
                "step": "7. Update _route_internal",
                "code": "Use spec_registry.get_handler_for_intent()",
                "reason": "Spec-driven handler selection"
            },
            {
                "step": "8. Replace error messages with GOVE_NNN codes",
                "code": "See error codes above",
                "reason": "CORE-040-003 compliance"
            },
            {
                "step": "9. Update all exception handling",
                "code": "Use structured error codes",
                "reason": "Consistent error handling"
            },
            {
                "step": "10. Test with SpecRegistry mocked",
                "code": "See test updates below",
                "reason": "Verify spec-driven behavior"
            }
        ]

    @staticmethod
    def get_test_updates() -> List[Dict[str, Any]]:
        """Get test updates needed."""
        return [
            {
                "test_file": "tests/unit/orchestrators/test_intent_orchestrator_routing.py",
                "test_count": 26,
                "updates": [
                    "Mock SpecRegistry instead of direct keyword lists",
                    "Test with different routing-rules-intent.yaml specs",
                    "Verify spec-driven keyword matching",
                    "Test GOVE_NNN error codes",
                    "Test fallback behavior when spec loading fails"
                ]
            },
            {
                "test_file": "tests/integration/orchestrators/test_intent_router.py",
                "test_count": 8,
                "updates": [
                    "Test SpecRegistry integration",
                    "Verify handler selection from spec",
                    "Test error handling with structured codes",
                    "Test confidence scoring with spec keywords"
                ]
            },
            {
                "test_file": "tests/integration/domain_brain/test_intent_router.py",
                "test_count": 5,
                "updates": [
                    "Test domain-aware intent routing",
                    "Verify spec-driven domain selection",
                    "Test fallback handlers from spec"
                ]
            }
        ]


class ImplementationVerification:
    """Verification checklist for IntentRouter refactoring."""

    @staticmethod
    def get_verification_checklist() -> List[Dict[str, Any]]:
        """Get verification checklist."""
        return [
            {
                "item": "Hardcoded keyword lists removed",
                "verification": "grep -n 'IMPLEMENT_KEYWORDS\\|FIX_KEYWORDS\\|REFACTOR_KEYWORDS' intent_router.py",
                "expected": "0 results (all removed)"
            },
            {
                "item": "SpecRegistry initialized",
                "verification": "grep -n 'spec_registry.*=' intent_router.py",
                "expected": "1 result (in __init__)"
            },
            {
                "item": "Keyword mappings loaded from spec",
                "verification": "grep -n '_build_keyword_mappings' intent_router.py",
                "expected": "2 results (definition + call)"
            },
            {
                "item": "Routing rules loaded from spec",
                "verification": "grep -n '_build_routing_rules\\|get_handler_for_intent' intent_router.py",
                "expected": "2+ results"
            },
            {
                "item": "GOVE_NNN error codes used",
                "verification": "grep -n 'GOVE_' intent_router.py",
                "expected": "4+ results (for different error types)"
            },
            {
                "item": "Tests updated and passing",
                "verification": "pytest tests/unit/orchestrators/test_intent_orchestrator_routing.py -v",
                "expected": "26 tests passing"
            },
            {
                "item": "No hardcoded domain-specific routing",
                "verification": "grep -n 'orchestrators\\|core\\|infrastructure' intent_router.py",
                "expected": "Only in comments, not hardcoded logic"
            },
            {
                "item": "Type hints maintained (CORE-011)",
                "verification": "Check all methods have return type hints",
                "expected": "100% compliance"
            },
            {
                "item": "Docstrings maintained (CORE-012)",
                "verification": "Check all methods have docstrings",
                "expected": "100% compliance"
            }
        ]
