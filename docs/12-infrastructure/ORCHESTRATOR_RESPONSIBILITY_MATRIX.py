"""
Orchestrator Responsibility Matrix for Planning System

Document: AC-PLANNING-RESPONSIBILITIES-001
Author: GitHub Copilot
Date: 2026-01-26

This document maps user intents to orchestrator handlers and responsibility areas.
Used by PlannerOrchestrator for routing and execution gates.

CORE Rules:
- CORE-008: Each handler implements TDD for its phases
- CORE-030: Responsibility mapping verified against actual code
- CORE-035: Single handler per intent (no duplication)
"""

# =============================================================================
# ORCHESTRATOR RESPONSIBILITY MATRIX
# =============================================================================

ORCHESTRATOR_RESPONSIBILITY_MATRIX = {
    # =========================================================================
    # IMPLEMENT Intent → TDDOrchestrator
    # =========================================================================
    "IMPLEMENT": {
        "orchestrator": "TDDOrchestrator",
        "module_path": "cortex.orchestrators.core.tdd_orchestrator",
        "responsibilities": [
            "Write RED cycle tests first",
            "Implement GREEN cycle (minimal code)",
            "REFACTOR cycle for optimization",
            "Verify 100% test coverage before completion",
            "Apply CORE-008 (TDD discipline)",
            "Apply CORE-011 (type hints)",
            "Apply CORE-012 (Google-style docstrings)",
            "Apply CORE-013 (no bare except)",
        ],
        "governance_rules": [
            "CORE-008",  # TDD mandatory
            "CORE-011",  # Type hints mandatory
            "CORE-012",  # Docstrings mandatory
            "CORE-013",  # No bare except
            "CORE-026",  # Git checkpoint per phase
        ],
        "execution_gates": {
            "low_confidence_high_impact": "CONFIRM_BEFORE_EXECUTE",
            "high_confidence_low_impact": "AUTO_EXECUTE",
            "medium_confidence_medium_impact": "NOTIFY_AND_EXECUTE",
        },
        "typical_phases": [
            "RED Cycle: Write failing tests",
            "GREEN Cycle: Implement minimal code",
            "REFACTOR Cycle: Optimize + improve",
            "Git Checkpoint: Save work",
        ],
        "estimated_duration": "1-4 hours depending on scope",
    },

    # =========================================================================
    # FIX Intent → IntentRouter → FixHandler
    # =========================================================================
    "FIX": {
        "orchestrator": "IntentRouter",
        "secondary_handler": "FixHandler",
        "module_path": "cortex.orchestrators.core.intent_router",
        "responsibilities": [
            "Analyze bug/issue description",
            "Identify root cause category (logic, performance, edge case, etc)",
            "Route to specialized fix handler",
            "Write tests that reproduce bug (RED)",
            "Fix bug (GREEN)",
            "Verify fix doesn't break existing tests",
            "Apply CORE-030 (implementation truth)",
        ],
        "governance_rules": [
            "CORE-008",  # TDD for fixes
            "CORE-011",  # Type hints
            "CORE-013",  # No bare except
            "CORE-026",  # Git checkpoint
            "CORE-030",  # Implementation truth
        ],
        "execution_gates": {
            "high_confidence": "NOTIFY_AND_EXECUTE",
            "low_confidence": "CONFIRM_BEFORE_EXECUTE",
            "risk_mismatch": "BLOCKED",  # Requires design review
        },
        "typical_phases": [
            "Analyze issue",
            "Write reproduction test",
            "Identify root cause",
            "Apply minimal fix",
            "Verify all tests pass",
            "Git Checkpoint",
        ],
        "estimated_duration": "30min - 2 hours",
    },

    # =========================================================================
    # REFACTOR Intent → RefactoringOrchestrator
    # =========================================================================
    "REFACTOR": {
        "orchestrator": "RefactoringOrchestrator",
        "module_path": "cortex.orchestrators.domain.refactoring_orchestrator",
        "responsibilities": [
            "Identify refactoring target (function, class, module)",
            "Plan refactoring strategy (extract, inline, move, etc)",
            "Write tests for existing behavior",
            "Apply refactoring changes",
            "Verify all tests still pass",
            "Improve code organization",
            "Apply CORE-035 (eliminate duplication)",
        ],
        "governance_rules": [
            "CORE-008",  # TDD discipline
            "CORE-011",  # Type hints
            "CORE-035",  # No duplicate implementations
            "CORE-026",  # Git checkpoint
            "CORE-030",  # Implementation truth",
        ],
        "execution_gates": {
            "low_impact": "AUTO_EXECUTE",
            "medium_impact": "NOTIFY_AND_EXECUTE",
            "high_impact": "CONFIRM_BEFORE_EXECUTE",
        },
        "typical_phases": [
            "Analyze current code",
            "Write behavior tests",
            "Plan refactoring",
            "Apply changes",
            "Verify tests pass",
            "Git Checkpoint",
        ],
        "estimated_duration": "1-3 hours",
    },

    # =========================================================================
    # DOCUMENT Intent → DocumentationOrchestrator
    # =========================================================================
    "DOCUMENT": {
        "orchestrator": "DocumentationOrchestrator",
        "module_path": "cortex.orchestrators.documentation",
        "responsibilities": [
            "Create or update documentation",
            "Add code examples",
            "Create diagrams/visualizations",
            "Ensure consistency with existing docs",
            "Apply documentation standards",
            "Cross-reference related docs",
            "Apply CORE-012 (doc quality)",
        ],
        "governance_rules": [
            "CORE-012",  # Documentation quality
            "CORE-026",  # Git checkpoint
            "CORE-030",  # Verify docs accuracy",
        ],
        "execution_gates": {
            "low_impact": "AUTO_EXECUTE",
            "internal_only": "NOTIFY_AND_EXECUTE",
        },
        "typical_phases": [
            "Analyze documentation needs",
            "Create/update content",
            "Add examples",
            "Review for accuracy",
            "Git Checkpoint",
        ],
        "estimated_duration": "30min - 2 hours",
    },

    # =========================================================================
    # TEST Intent → TDDOrchestrator
    # =========================================================================
    "TEST": {
        "orchestrator": "TDDOrchestrator",
        "module_path": "cortex.orchestrators.core.tdd_orchestrator",
        "responsibilities": [
            "Analyze test coverage gaps",
            "Write unit tests",
            "Write integration tests",
            "Write end-to-end tests",
            "Verify test quality (assertions, edge cases)",
            "Achieve coverage targets",
            "Apply CORE-008 (TDD discipline)",
        ],
        "governance_rules": [
            "CORE-008",  # TDD discipline
            "CORE-011",  # Type hints
            "CORE-012",  # Docstrings
            "CORE-026",  # Git checkpoint
        ],
        "execution_gates": {
            "coverage_improvement": "AUTO_EXECUTE",
            "risky_areas": "CONFIRM_BEFORE_EXECUTE",
        },
        "typical_phases": [
            "Identify coverage gaps",
            "Write tests",
            "Run test suite",
            "Verify coverage improved",
            "Git Checkpoint",
        ],
        "estimated_duration": "1-3 hours",
    },

    # =========================================================================
    # ANALYZE Intent → MasterOrchestrator (default)
    # =========================================================================
    "ANALYZE": {
        "orchestrator": "MasterOrchestrator",
        "module_path": "cortex.orchestrators.core.master_orchestrator",
        "responsibilities": [
            "Perform code analysis",
            "Generate reports",
            "Identify issues/opportunities",
            "Suggest improvements",
            "Provide recommendations",
            "NO code changes (read-only)",
        ],
        "governance_rules": [
            "CORE-030",  # Implementation truth
        ],
        "execution_gates": {
            "analysis_only": "AUTO_EXECUTE",
        },
        "typical_phases": [
            "Analyze request",
            "Run static analysis",
            "Generate findings",
            "Suggest actions",
            "Report results",
        ],
        "estimated_duration": "15min - 1 hour",
    },
}

# =============================================================================
# PHASE MAPPING FOR MULTI-PHASE PLANS
# =============================================================================

PHASE_TYPE_TO_ORCHESTRATOR = {
    # Implementation phases
    "feature_implementation": "TDDOrchestrator",
    "api_endpoint_creation": "TDDOrchestrator",
    "module_creation": "TDDOrchestrator",
    "component_implementation": "TDDOrchestrator",
    
    # Fix phases
    "bug_fix": "IntentRouter",
    "performance_optimization": "RefactoringOrchestrator",
    "error_handling": "IntentRouter",
    "edge_case_fix": "IntentRouter",
    
    # Refactoring phases
    "code_refactoring": "RefactoringOrchestrator",
    "duplication_removal": "RefactoringOrchestrator",
    "structure_improvement": "RefactoringOrchestrator",
    "technical_debt_reduction": "RefactoringOrchestrator",
    
    # Testing phases
    "unit_testing": "TDDOrchestrator",
    "integration_testing": "TDDOrchestrator",
    "coverage_improvement": "TDDOrchestrator",
    
    # Documentation phases
    "api_documentation": "DocumentationOrchestrator",
    "user_guide_creation": "DocumentationOrchestrator",
    "code_documentation": "DocumentationOrchestrator",
    "architecture_documentation": "DocumentationOrchestrator",
}

# =============================================================================
# EXECUTION GATE DECISION MATRIX
# =============================================================================

EXECUTION_GATE_MATRIX = {
    # Impact/Confidence combinations determine execution gate
    ("low", "high"): "AUTO_EXECUTE",           # Low impact + high confidence → run it
    ("low", "medium"): "NOTIFY_AND_EXECUTE",   # Low impact + medium confidence → notify + run
    ("low", "low"): "NOTIFY_USER",             # Low impact + low confidence → notify, ask
    
    ("medium", "high"): "NOTIFY_AND_EXECUTE",  # Medium impact + high confidence → notify + run
    ("medium", "medium"): "CONFIRM_BEFORE_EXECUTE",  # Medium impact + medium confidence → confirm
    ("medium", "low"): "CONFIRM_BEFORE_EXECUTE",     # Medium impact + low confidence → confirm
    
    ("high", "high"): "NOTIFY_USER",           # High impact + high confidence → notify, ask permission
    ("high", "medium"): "CONFIRM_BEFORE_EXECUTE",    # High impact + medium confidence → confirm
    ("high", "low"): "BLOCKED",                # High impact + low confidence → blocked, review needed
}

# =============================================================================
# CHALLENGE GENERATION RULES
# =============================================================================

CHALLENGE_GENERATION_RULES = {
    "governance_violation": {
        "type": "GOVERNANCE",
        "severity": "high",
        "triggers": [
            "bare except clause",
            "no type hints",
            "missing docstring",
            "code duplication",
        ],
        "recommendation": "Apply CORE rules before proceeding",
    },
    
    "alternative_path": {
        "type": "ALTERNATIVE_PATH",
        "severity": "medium",
        "triggers": [
            "copy/paste pattern",
            "similar implementation exists",
            "duplication detected",
        ],
        "recommendation": "Consider extracting to shared module",
    },
    
    "scope_creep": {
        "type": "SCOPE_CREEP",
        "severity": "medium",
        "triggers": [
            "multiple AND clauses",
            "description longer than expected",
            "scope mismatch",
        ],
        "recommendation": "Break into smaller, focused requests",
    },
    
    "risk_mismatch": {
        "type": "RISK_MISMATCH",
        "severity": "high",
        "triggers": [
            "high impact + low confidence",
            "system changes + uncertainty",
        ],
        "recommendation": "Increase confidence through research/design",
    },
}

# =============================================================================
# GOVERNANCE RULE MAPPING
# =============================================================================

GOVERNANCE_RULE_MAPPING = {
    "CORE-008": {
        "name": "Test-Driven Development (TDD) Mandatory",
        "description": "Write tests BEFORE implementation",
        "enforced_by": ["TDDOrchestrator", "TDDCycleExecutor"],
        "applicability": ["IMPLEMENT", "FIX", "REFACTOR", "TEST"],
    },
    
    "CORE-011": {
        "name": "Type Hints Mandatory",
        "description": "All functions must have type hints",
        "enforced_by": ["Pylance", "CodeAnalyzer"],
        "applicability": ["IMPLEMENT", "FIX", "REFACTOR"],
    },
    
    "CORE-012": {
        "name": "Google-Style Docstrings",
        "description": "All functions/classes must have docstrings",
        "enforced_by": ["DocstringChecker"],
        "applicability": ["IMPLEMENT", "FIX", "REFACTOR", "DOCUMENT"],
    },
    
    "CORE-013": {
        "name": "No Bare Except Clauses",
        "description": "Must specify exception types",
        "enforced_by": ["Pylint", "CodeAnalyzer"],
        "applicability": ["IMPLEMENT", "FIX", "REFACTOR"],
    },
    
    "CORE-026": {
        "name": "Git Checkpoint After Major Changes",
        "description": "Commit work after each phase",
        "enforced_by": ["PhaseExecutor"],
        "applicability": ["All phases"],
    },
    
    "CORE-030": {
        "name": "Implementation Truth",
        "description": "Verify code works, don't trust docs",
        "enforced_by": ["TestExecutor", "CodeValidator"],
        "applicability": ["All phases"],
    },
    
    "CORE-035": {
        "name": "Single Canonical Implementation",
        "description": "No code duplication, single source of truth",
        "enforced_by": ["DuplicationDetector", "RefactoringOrchestrator"],
        "applicability": ["IMPLEMENT", "REFACTOR"],
    },
}

# =============================================================================
# SUMMARY
# =============================================================================

SUMMARY = """
Orchestrator Responsibility Matrix (AC-PLANNING-RESPONSIBILITIES-001)

PRIMARY HANDLERS:
1. TDDOrchestrator
   - Handles: IMPLEMENT, TEST
   - Enforces: CORE-008 (TDD), RED→GREEN→REFACTOR
   - Phases: Feature implementation, testing, coverage

2. IntentRouter → FixHandler
   - Handles: FIX
   - Enforces: Bug reproduction + fix verification
   - Phases: Bug fixes, error handling, edge cases

3. RefactoringOrchestrator
   - Handles: REFACTOR
   - Enforces: CORE-035 (no duplication)
   - Phases: Code refactoring, optimization, structure

4. DocumentationOrchestrator
   - Handles: DOCUMENT
   - Enforces: CORE-012 (documentation quality)
   - Phases: API docs, guides, architecture

5. MasterOrchestrator
   - Handles: ANALYZE
   - Enforces: Read-only analysis
   - Phases: Reporting, recommendations

EXECUTION GATES (AC-PLANNER-004):
- LOW impact + HIGH confidence    → AUTO_EXECUTE
- MEDIUM impact + MEDIUM confidence → CONFIRM_BEFORE_EXECUTE
- HIGH impact + LOW confidence     → BLOCKED (requires design review)

GOVERNANCE ENFORCEMENT:
- All code changes enforce CORE-008 (TDD)
- All code enforces CORE-011 (type hints) + CORE-012 (docstrings)
- All phases create git checkpoints (CORE-026)
- All phases verify implementation (CORE-030)

CHALLENGE SYSTEM:
- Governance violations → Severity HIGH
- Alternative paths → Severity MEDIUM
- Scope creep → Severity MEDIUM
- Risk mismatch → Severity HIGH

This matrix is used by:
1. PlannerOrchestrator to route intents
2. Phase executors to apply correct governance
3. Execution gates to determine automation level
4. Challenge engine to generate strategic questions
"""

if __name__ == "__main__":
    print(SUMMARY)
    print("\nPrimary Handlers:")
    for intent, details in ORCHESTRATOR_RESPONSIBILITY_MATRIX.items():
        print(f"  {intent} → {details['orchestrator']}")
