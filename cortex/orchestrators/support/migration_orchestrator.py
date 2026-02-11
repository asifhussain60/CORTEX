"""
MigrationOrchestrator: Technology stack migration planning and validation
Authority: Phase 52 S3
AC_START: AC-PHASE52-S3-001
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from cortex.brain.core.result import Err, Ok
from cortex.orchestrators.core.orchestrator_base_protocol import (
    OrchestratorBaseProtocol,
)

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class MigrationStep:
    """Represents a single migration step"""
    order: int
    name: str
    description: str
    estimated_hours: float
    dependencies: List[int] = field(default_factory=list)
    rollback_strategy: Optional[str] = None
    validation_criteria: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)


@dataclass
class MigrationPlan:
    """Overall migration plan"""
    source: str
    target: str
    steps: List[MigrationStep]
    total_effort_hours: float
    complexity_score: float  # 0-1.0
    risk_level: str


@dataclass
class CompatibilityIssue:
    """Represents a compatibility issue"""
    type: str
    severity: str  # critical, high, medium, low
    description: str
    affected_code: Optional[str] = None
    fix_suggestion: Optional[str] = None


@dataclass
class FeatureParityCheck:
    """Feature parity validation result"""
    all_features_present: bool
    missing_features: List[str]
    new_features: List[str]
    deprecated_features: List[str]


@dataclass
class RollbackStrategy:
    """Rollback strategy for a migration step"""
    rollback_type: str  # database, code, data, etc.
    steps: List[str]
    validation_steps: List[str]
    estimated_rollback_minutes: int
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class MigrationRisk:
    """Migration risk assessment"""
    overall_risk_score: float
    risk_level: str
    high_risk_areas: List[str]
    mitigation_strategies: List[str]
    critical_dependencies: List[str]


# ============================================================================
# MIGRATION TEMPLATES
# ============================================================================

MIGRATION_TEMPLATES = {
    "python-2.7->python-3.11": {
        "steps": [
            {"name": "Inventory & Analysis", "hours": 16},
            {"name": "Fix Syntax Issues", "hours": 24},
            {"name": "Update Dependencies", "hours": 12},
            {"name": "Test & Validate", "hours": 20},
        ],
        "complexity": 0.7,
        "risk_level": "high",
    },
    "angular-1.8->react-18": {
        "steps": [
            {"name": "Analyze Component Structure", "hours": 20},
            {"name": "Create React Component Mapping", "hours": 30},
            {"name": "Migrate Controllers & Services", "hours": 40},
            {"name": "Update Templates & Directives", "hours": 35},
            {"name": "Test Integration", "hours": 25},
        ],
        "complexity": 0.85,
        "risk_level": "high",
    },
    "django-1.11->django-4.0": {
        "steps": [
            {"name": "Update Dependencies", "hours": 8},
            {"name": "Fix Deprecated APIs", "hours": 16},
            {"name": "Update Database Migrations", "hours": 12},
            {"name": "Test Compatibility", "hours": 12},
        ],
        "complexity": 0.5,
        "risk_level": "medium",
    },
}


class MigrationOrchestrator(OrchestratorBaseProtocol):
    """Orchestrator for technology stack migration planning and validation"""

    def __init__(self):
        self.name = "MigrationOrchestrator"
        self.version = "1.0.0"

    # ========================================================================
    # MIGRATION PLAN GENERATION
    # ========================================================================

    def generate_migration_plan(self, context: Dict[str, Any]) -> Union[Ok, Err]:
        """Generate migration plan based on source and target"""
        try:
            # Determine migration type
            if context.get("source_language") and context.get("target_language"):
                migration_key = f"{context['source_language']}-{context['source_version']}->{context['target_language']}-{context['target_version']}"
            elif context.get("source_framework") and context.get("target_framework"):
                migration_key = f"{context['source_framework']}-{context['source_version']}->{context['target_framework']}-{context['target_version']}"
            else:
                return Err(error="Missing source/target information in context")

            # Look up template or create custom plan
            template = MIGRATION_TEMPLATES.get(
                next((k for k in MIGRATION_TEMPLATES.keys() if f"{context.get('source_language', context.get('source_framework'))}-{context.get('source_version')}" in k), None)
            )

            if not template:
                # Generate generic plan
                template = {
                    "steps": [
                        {"name": "Assessment & Planning", "hours": 12},
                        {"name": "Implementation", "hours": 24},
                        {"name": "Testing & Validation", "hours": 16},
                        {"name": "Deployment & Monitoring", "hours": 12},
                    ],
                    "complexity": 0.6,
                    "risk_level": "medium",
                }

            # Build migration plan
            steps = []
            total_hours = 0

            for i, step_template in enumerate(template["steps"]):
                step = MigrationStep(
                    order=i,
                    name=step_template["name"],
                    description=f"Step {i+1}: {step_template['name']}",
                    estimated_hours=step_template["hours"],
                    rollback_strategy=f"Rollback for {step_template['name']}",
                    validation_criteria=[f"Validate {step_template['name'].lower()}"],
                    risks=[f"Risk for {step_template['name']}"],
                )
                steps.append(step)
                total_hours += step_template["hours"]

            plan = MigrationPlan(
                source=f"{context.get('source_language', context.get('source_framework'))}-{context.get('source_version')}",
                target=f"{context.get('target_language', context.get('target_framework'))}-{context.get('target_version')}",
                steps=steps,
                total_effort_hours=total_hours,
                complexity_score=template["complexity"],
                risk_level=template["risk_level"],
            )

            return Ok(value=plan)
        except Exception as e:
            return Err(error=f"Migration plan generation failed: {str(e)}")

    # ========================================================================
    # BACKWARD COMPATIBILITY CHECKS
    # ========================================================================

    def check_api_compatibility(self, old_api: Dict, new_api: Dict) -> Union[Ok, Err]:
        """Check API compatibility between versions"""
        try:
            issues = []

            old_functions = {f["name"]: f for f in old_api.get("functions", [])}
            new_functions = {f["name"]: f for f in new_api.get("functions", [])}

            # Check for removed functions
            for fname, fold in old_functions.items():
                if fname not in new_functions:
                    issues.append(CompatibilityIssue(
                        type="function_removed",
                        severity="critical",
                        description=f"Function {fname} removed in new version",
                    ))

            # Check for parameter changes
            for fname, fold in old_functions.items():
                if fname in new_functions:
                    fnew = new_functions[fname]
                    old_params = set(fold.get("params", []))
                    new_params = set(fnew.get("params", []))

                    removed = old_params - new_params
                    if removed:
                        issues.append(CompatibilityIssue(
                            type="parameter_removed",
                            severity="high",
                            description=f"Function {fname} removed parameters: {removed}",
                        ))

            return Ok(value=issues)
        except Exception as e:
            return Err(error=f"API compatibility check failed: {str(e)}")

    def find_deprecated_calls(self, code: str, deprecations: Dict[str, str]) -> Union[Ok, Err]:
        """Find calls to deprecated functions"""
        try:
            found_calls = []

            for func_name, message in deprecations.items():
                if func_name + "(" in code:
                    found_calls.append(CompatibilityIssue(
                        type="deprecated_call",
                        severity="medium",
                        description=f"Call to deprecated function: {func_name}",
                        fix_suggestion=message,
                    ))

            return Ok(value=found_calls)
        except Exception as e:
            return Err(error=f"Deprecated call search failed: {str(e)}")

    def check_dependency_compatibility(self, old_deps: Dict[str, str], new_deps: Dict[str, str]) -> Union[Ok, Err]:
        """Check compatibility of dependencies"""
        try:
            report = {
                "compatible": True,
                "warnings": [],
                "major_upgrades": [],
            }

            for lib, old_version in old_deps.items():
                if lib in new_deps:
                    new_version = new_deps[lib]
                    old_major = int(old_version.split('.')[0])
                    new_major = int(new_version.split('.')[0])

                    if new_major > old_major:
                        report["major_upgrades"].append(f"{lib}: {old_version} -> {new_version}")
                        report["warnings"].append(f"Major version upgrade for {lib}")

            return Ok(value=report)
        except Exception as e:
            return Err(error=f"Dependency compatibility check failed: {str(e)}")

    def find_behavior_changes(self, code: str, language: str, source_version: str = None, target_version: str = None) -> Union[Ok, Err]:
        """Find potential behavior changes"""
        try:
            issues = []

            if language == "python":
                # Python 2 to 3 specific checks
                if source_version == "2.7":
                    if "print " in code and "print(" not in code:
                        issues.append(CompatibilityIssue(
                            type="print_statement",
                            severity="high",
                            description="Python 2 print statement found",
                            fix_suggestion="Convert to print() function",
                        ))

                    if ".iteritems()" in code:
                        issues.append(CompatibilityIssue(
                            type="iterator_method",
                            severity="high",
                            description="Python 2 .iteritems() found",
                            fix_suggestion="Use .items() in Python 3",
                        ))

                    if "xrange" in code:
                        issues.append(CompatibilityIssue(
                            type="builtin_change",
                            severity="medium",
                            description="Python 2 xrange() found",
                            fix_suggestion="Use range() in Python 3",
                        ))

            return Ok(value=issues)
        except Exception as e:
            return Err(error=f"Behavior change detection failed: {str(e)}")

    # ========================================================================
    # FEATURE PARITY CHECKS
    # ========================================================================

    def check_feature_parity(self, old_features: Dict[str, List[str]], new_features: Dict[str, List[str]]) -> Union[Ok, Err]:
        """Check feature parity between versions"""
        try:
            missing = []
            new = []
            deprecated = []

            for category, old_items in old_features.items():
                new_items = new_features.get(category, [])

                for item in old_items:
                    if item not in new_items:
                        missing.append(f"{category}.{item}")

            for category, new_items in new_features.items():
                old_items = old_features.get(category, [])

                for item in new_items:
                    if item not in old_items:
                        new.append(f"{category}.{item}")

            parity = FeatureParityCheck(
                all_features_present=len(missing) == 0,
                missing_features=missing,
                new_features=new,
                deprecated_features=deprecated,
            )

            return Ok(value=parity)
        except Exception as e:
            return Err(error=f"Feature parity check failed: {str(e)}")

    def generate_parity_tests(self, features: Dict[str, List[str]]) -> Union[Ok, Err]:
        """Generate test cases for feature parity validation"""
        try:
            tests = []

            for category, items in features.items():
                for item in items:
                    test_name = f"test_{category}_{item}"
                    tests.append({
                        "name": test_name,
                        "category": category,
                        "feature": item,
                    })

            return Ok(value=tests)
        except Exception as e:
            return Err(error=f"Parity test generation failed: {str(e)}")

    # ========================================================================
    # ROLLBACK STRATEGY GENERATION
    # ========================================================================

    def generate_rollback_strategy(self, migration_step: Dict[str, Any]) -> Union[Ok, Err]:
        """Generate rollback strategy for a migration step"""
        try:
            step_type = migration_step.get("type", "generic")

            if step_type == "database":
                steps = [
                    "Backup current database state",
                    "Stop application servers",
                    "Reverse schema changes",
                    "Verify data integrity",
                    "Restart application servers",
                ]
                validation = [
                    "Verify schema matches original",
                    "Check data consistency",
                ]
                rollback_mins = 45
            elif step_type == "code":
                steps = [
                    "Revert code to previous version",
                    "Clear caches",
                    "Restart services",
                ]
                validation = [
                    "Run tests",
                    "Verify functionality",
                ]
                rollback_mins = 15
            else:
                steps = ["Revert changes", "Validate state"]
                validation = ["Verify system stability"]
                rollback_mins = 30

            strategy = RollbackStrategy(
                rollback_type=step_type,
                steps=steps,
                validation_steps=validation,
                estimated_rollback_minutes=rollback_mins,
            )

            return Ok(value=strategy)
        except Exception as e:
            return Err(error=f"Rollback strategy generation failed: {str(e)}")

    # ========================================================================
    # RISK ASSESSMENT
    # ========================================================================

    def assess_migration_risk(self, context: Dict[str, Any]) -> Union[Ok, Err]:
        """Assess overall migration risk"""
        try:
            risk_score = 0.0
            factors = []

            # Assess codebase size
            size = context.get("codebase_size", "100k_lines")
            if "1m" in size:
                risk_score += 0.3
                factors.append("Large codebase increases risk")
            elif "500k" in size:
                risk_score += 0.2
                factors.append("Medium-large codebase")
            else:
                risk_score += 0.1

            # Assess test coverage
            coverage = context.get("test_coverage", 0.5)
            if coverage < 0.5:
                risk_score += 0.3
                factors.append("Low test coverage increases risk")
            elif coverage < 0.75:
                risk_score += 0.15

            # Assess dependencies
            dep_count = context.get("dependencies", 10)
            if dep_count > 100:
                risk_score += 0.25
                factors.append("Many dependencies increase complexity")
            elif dep_count > 50:
                risk_score += 0.15

            # Cap score at 1.0
            risk_score = min(risk_score, 1.0)

            # Determine risk level
            if risk_score >= 0.75:
                risk_level = "critical"
            elif risk_score >= 0.6:
                risk_level = "high"
            elif risk_score >= 0.4:
                risk_level = "medium"
            else:
                risk_level = "low"

            mitigation = [
                "Establish rollback procedures",
                "Create comprehensive test suite",
                "Use feature flags for gradual rollout",
                "Monitor application closely after deployment",
            ]

            risk = MigrationRisk(
                overall_risk_score=risk_score,
                risk_level=risk_level,
                high_risk_areas=factors,
                mitigation_strategies=mitigation,
                critical_dependencies=["database", "api"],
            )

            return Ok(value=risk)
        except Exception as e:
            return Err(error=f"Risk assessment failed: {str(e)}")

    # ========================================================================
    # OrchestratorBaseProtocol Implementation
    # ========================================================================

    def _execute_domain_logic(self, user_request: str, lens_context: Optional[Any], context: Dict[str, Any]) -> Union[Ok, Err]:
        """
        Execute Phase 5: Domain-specific orchestration logic (Migration Planning).
        """
        try:
            operation = context.get("operation", "generate_plan")

            if operation == "generate_plan":
                return self.generate_migration_plan(context)
            elif operation == "check_compatibility":
                return self.check_api_compatibility(context.get("old_api", {}), context.get("new_api", {}))
            elif operation == "assess_risk":
                return self.assess_migration_risk(context)
            else:
                return Err(error=f"Unknown operation: {operation}")
        except Exception as e:
            return Err(error=f"Domain logic execution failed: {str(e)}")

    def execute(self, request: Dict) -> Union[Ok, Err]:
        """Execute orchestrator operation"""
        operation = request.get("operation", "generate_plan")
        if operation == "generate_plan":
            return self.generate_migration_plan(request)
        return Err(error=f"Unknown operation: {operation}")

    def validate(self) -> Union[Ok, Err]:
        """Validate orchestrator state"""
        if not self.name:
            return Err(error="Orchestrator name not set")
        return Ok(value=True)

    def get_capabilities(self) -> List[str]:
        """Get orchestrator capabilities"""
        return [
            "generate_plan",
            "check_compatibility",
            "assess_risk",
            "generate_rollback",
            "check_feature_parity",
            "find_deprecated_calls",
        ]


# AC_COMPLETE: AC-PHASE52-S3-001
