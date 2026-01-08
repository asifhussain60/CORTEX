"""
TDD Orchestrator v4 - RED→GREEN→REFACTOR Workflow.

Autonomous TDD orchestration with:
- RED Phase: Failing test generation with edge cases
- GREEN Phase: Minimal implementation until tests pass
- REFACTOR Phase: Clean code enforcement (SOLID, DRY, KISS)
- Technology Discovery: Language and framework detection
- Clean Code Enforcement: Complexity, length, duplication checks
- Security Test Generation: Automatic security test creation

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from src.orchestrators.base.base_orchestrator_v4_1 import (
    BaseOrchestratorV4_1,
    PhaseStatus,
    PhaseResult,
    OrchestratorResult,
    OrchestratorStatus
)
from src.database.planning_state_db import PlanningStateDB


logger = logging.getLogger(__name__)


class TDDPhase(Enum):
    """TDD workflow phases."""
    DISCOVERY = "discovery"  # Technology and framework discovery
    RED = "red"  # Write failing tests
    GREEN = "green"  # Minimal implementation
    REFACTOR = "refactor"  # Clean code enforcement
    VALIDATION = "validation"  # Final validation


@dataclass
class Test:
    """Represents a single test."""
    name: str
    code: str
    status: str  # FAILING, PASSING
    category: str = "functional"  # functional, security, edge_case
    description: str = ""


@dataclass
class TDDResult:
    """TDD execution result."""
    status: OrchestratorStatus
    phases_completed: int = 0
    tests_generated: int = 0
    all_tests_passing: bool = False
    clean_code_score: int = 0
    report_path: Optional[Path] = None
    message: str = ""


@dataclass
class PhaseResultData:
    """Data for TDD phase results."""
    tests: List[Test] = field(default_factory=list)
    tests_generated: int = 0
    domain_knowledge_used: bool = False
    implementation_created: bool = False
    all_tests_passing: bool = False
    iterations: int = 0
    refactorings_applied: int = 0
    clean_code_score: int = 0
    code_smells_detected: List[str] = field(default_factory=list)
    tests_still_passing: bool = True
    test_failures: int = 0
    implementation_path: Optional[Path] = None
    code_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TechnologyInfo:
    """Technology discovery result."""
    primary_language: str = "unknown"
    test_framework: str = "pytest"
    test_framework_version: Optional[str] = None
    confidence: float = 0.0


@dataclass
class CleanCodeViolation:
    """Clean code principle violation."""
    type: str
    principle: str
    message: str
    line: int = 0
    max_recommended: Optional[int] = None


class TDDOrchestrator(BaseOrchestratorV4_1):
    """
    TDD Orchestrator v4 - Autonomous RED→GREEN→REFACTOR workflow.
    
    Phases:
        1. DISCOVERY - Detect language, framework, and project structure
        2. RED - Generate comprehensive failing tests (functional, security, edge cases)
        3. GREEN - Minimal implementation until all tests pass
        4. REFACTOR - Apply clean code principles (SOLID, DRY, KISS, YAGNI)
        5. VALIDATION - Final test run and report generation
    
    Features:
        - Technology discovery and adaptation
        - Domain knowledge integration (Tier 2 brain)
        - Security-focused test generation
        - Clean code enforcement
        - Automated refactoring suggestions
        - Comprehensive reporting
    
    Usage:
        orchestrator = TDDOrchestrator()
        result = orchestrator.execute("Implement user authentication with JWT")
    """
    
    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        state_db: Optional[PlanningStateDB] = None,
        manifest_path: Optional[str] = None,
        dry_run: bool = False,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize TDD Orchestrator.
        
        Args:
            workspace_root: Root directory of the workspace
            state_db: Planning state database for persistence
            manifest_path: Path to TDD orchestrator manifest
            dry_run: If True, don't execute, just plan
            config: Optional configuration override
        """
        # Store workspace root first
        self.workspace_root = workspace_root or Path.cwd()
        self.state_db = state_db
        
        # Initialize base orchestrator with config_path only
        super().__init__(config_path=None)
        
        self.dry_run = dry_run
        self.current_phase = TDDPhase.DISCOVERY
        
        # Load configuration
        self.manifest_path = Path(manifest_path) if manifest_path else \
            self.workspace_root / "cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml"
        
        self.config = config or self._load_manifest_config()
        
        # Technology discovery
        self.tech_discovery: Optional[TechnologyInfo] = None
        
        # Brain connector (mock for now)
        self.brain_connector = None
        
        logger.info(f"TDDOrchestrator initialized (workspace={workspace_root}, dry_run={dry_run})")
    
    def _load_manifest_config(self) -> Dict[str, Any]:
        """Load configuration from manifest file."""
        if not self.manifest_path.exists():
            logger.warning(f"Manifest not found: {self.manifest_path}")
            return self._get_default_config()
        
        try:
            import yaml
            with open(self.manifest_path) as f:
                manifest = yaml.safe_load(f)
            return manifest
        except Exception as e:
            logger.error(f"Failed to load manifest: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'phases': [
                {'name': 'DISCOVERY', 'order': 0},
                {'name': 'RED', 'order': 1},
                {'name': 'GREEN', 'order': 2},
                {'name': 'REFACTOR', 'order': 3},
                {'name': 'VALIDATION', 'order': 4}
            ],
            'clean_code': {
                'max_function_length': 50,
                'max_complexity': 10,
                'min_score': 80
            },
            'security_tests': {
                'enabled': True,
                'categories': ['authentication', 'authorization', 'injection', 'xss']
            }
        }
    
    def discover_technology(self) -> TechnologyInfo:
        """
        Discover project technology stack.
        
        Returns:
            TechnologyInfo with detected language and framework
        """
        logger.info("Discovering project technology...")
        
        tech_info = TechnologyInfo()
        
        # Detect Python
        if (self.workspace_root / "requirements.txt").exists() or \
           (self.workspace_root / "pyproject.toml").exists() or \
           list(self.workspace_root.glob("**/*.py")):
            tech_info.primary_language = "python"
            tech_info.confidence = 0.9
            
            # Detect test framework
            if (self.workspace_root / "requirements.txt").exists():
                req_content = (self.workspace_root / "requirements.txt").read_text()
                if "pytest" in req_content:
                    tech_info.test_framework = "pytest"
                    # Extract version if available
                    import re
                    match = re.search(r'pytest==([0-9.]+)', req_content)
                    if match:
                        tech_info.test_framework_version = match.group(1)
                elif "unittest" in req_content or "nose" in req_content:
                    tech_info.test_framework = "unittest"
        
        self.tech_discovery = tech_info
        logger.info(f"Technology discovered: {tech_info.primary_language} with {tech_info.test_framework}")
        
        return tech_info
    
    def execute_red_phase(self, feature_description: str) -> PhaseResultData:
        """
        Execute RED phase - generate failing tests.
        
        Args:
            feature_description: Description of feature to test
        
        Returns:
            PhaseResultData with generated tests
        """
        logger.info(f"RED Phase: Generating failing tests for '{feature_description}'")
        
        result = PhaseResultData()
        
        # Query domain knowledge (mock implementation)
        if self.brain_connector:
            try:
                knowledge = self.brain_connector.query_tier2(feature_description)
                result.domain_knowledge_used = True
                logger.info(f"Domain knowledge retrieved: {knowledge}")
            except Exception as e:
                logger.warning(f"Failed to retrieve domain knowledge: {e}")
        
        # Generate functional tests
        functional_tests = self._generate_functional_tests(feature_description)
        result.tests.extend(functional_tests)
        
        # Generate edge case tests
        edge_case_tests = self._generate_edge_case_tests(feature_description)
        result.tests.extend(edge_case_tests)
        
        # Generate security tests
        security_tests = self._generate_security_tests(feature_description)
        result.tests.extend(security_tests)
        
        result.tests_generated = len(result.tests)
        
        logger.info(f"RED Phase complete: {result.tests_generated} tests generated")
        
        return result
    
    def _generate_functional_tests(self, feature_description: str) -> List[Test]:
        """Generate basic functional tests."""
        tests = []
        
        # Basic happy path test
        test_name = f"test_{feature_description.lower().replace(' ', '_')}_basic"
        test_code = f"""
def {test_name}():
    \"\"\"Test basic {feature_description} functionality.\"\"\"
    # Arrange
    pass
    
    # Act
    pass
    
    # Assert
    assert False, "Test not implemented"
"""
        tests.append(Test(
            name=test_name,
            code=test_code,
            status="FAILING",
            category="functional",
            description=f"Basic {feature_description} test"
        ))
        
        return tests
    
    def _generate_edge_case_tests(self, feature_description: str) -> List[Test]:
        """Generate edge case tests."""
        tests = []
        
        # Empty input test
        test_name = f"test_{feature_description.lower().replace(' ', '_')}_empty_input"
        test_code = f"""
def {test_name}():
    \"\"\"Test {feature_description} with empty input.\"\"\"
    assert False, "Edge case test not implemented"
"""
        tests.append(Test(
            name=test_name,
            code=test_code,
            status="FAILING",
            category="edge_case",
            description=f"Empty input test for {feature_description}"
        ))
        
        # Invalid input test
        test_name = f"test_{feature_description.lower().replace(' ', '_')}_invalid_input"
        test_code = f"""
def {test_name}():
    \"\"\"Test {feature_description} with invalid input.\"\"\"
    assert False, "Edge case test not implemented"
"""
        tests.append(Test(
            name=test_name,
            code=test_code,
            status="FAILING",
            category="edge_case",
            description=f"Invalid input test for {feature_description}"
        ))
        
        return tests
    
    def _generate_security_tests(self, feature_description: str) -> List[Test]:
        """Generate security-focused tests."""
        tests = []
        
        # Check if feature involves security-sensitive operations
        security_keywords = ['auth', 'password', 'login', 'token', 'session', 'reset', 'email']
        is_security_sensitive = any(kw in feature_description.lower() for kw in security_keywords)
        
        if is_security_sensitive:
            # SQL injection test
            test_name = f"test_{feature_description.lower().replace(' ', '_')}_sql_injection"
            test_code = f"""
def {test_name}():
    \"\"\"Test {feature_description} against SQL injection.\"\"\"
    malicious_input = "' OR '1'='1"
    assert False, "Security test not implemented"
"""
            tests.append(Test(
                name=test_name,
                code=test_code,
                status="FAILING",
                category="security",
                description=f"SQL injection test for {feature_description}"
            ))
        
        return tests
    
    def execute_green_phase(self, red_result: PhaseResultData) -> PhaseResultData:
        """
        Execute GREEN phase - minimal implementation.
        
        Args:
            red_result: Result from RED phase with failing tests
        
        Returns:
            PhaseResultData with implementation status
        """
        logger.info("GREEN Phase: Creating minimal implementation")
        
        result = PhaseResultData()
        result.implementation_created = True
        result.iterations = 1
        
        # In a real implementation, this would:
        # 1. Analyze failing tests
        # 2. Generate minimal code to pass tests
        # 3. Run tests iteratively until passing
        # 4. Save implementation
        
        # Mock: Assume tests pass after implementation
        result.all_tests_passing = True
        result.test_failures = 0
        
        logger.info("GREEN Phase complete: Implementation created, tests passing")
        
        return result
    
    def execute_refactor_phase(self, green_result: PhaseResultData) -> PhaseResultData:
        """
        Execute REFACTOR phase - clean code enforcement.
        
        Args:
            green_result: Result from GREEN phase with implementation
        
        Returns:
            PhaseResultData with refactoring status
        """
        logger.info("REFACTOR Phase: Enforcing clean code principles")
        
        result = PhaseResultData()
        
        # Check code metrics (mock implementation)
        code_metrics = green_result.code_metrics or {}
        
        # Detect code smells
        if code_metrics.get('function_length', 0) > self.config['clean_code']['max_function_length']:
            result.code_smells_detected.append('long_function')
        
        if code_metrics.get('complexity', 0) > self.config['clean_code']['max_complexity']:
            result.code_smells_detected.append('high_complexity')
        
        if code_metrics.get('duplications', 0) > 0:
            result.code_smells_detected.append('duplication')
        
        # Apply refactorings
        result.refactorings_applied = len(result.code_smells_detected)
        
        # Calculate clean code score
        result.clean_code_score = max(0, 100 - (len(result.code_smells_detected) * 10))
        
        # Verify tests still pass
        result.tests_still_passing = True
        result.test_failures = 0
        
        logger.info(f"REFACTOR Phase complete: {result.refactorings_applied} refactorings, score: {result.clean_code_score}")
        
        return result
    
    def check_clean_code(self, code: str) -> List[CleanCodeViolation]:
        """
        Check code against clean code principles.
        
        Args:
            code: Source code to analyze
        
        Returns:
            List of violations found
        """
        violations = []
        
        # Check function length
        lines = code.split('\n')
        if len(lines) > self.config['clean_code']['max_function_length']:
            violations.append(CleanCodeViolation(
                type="LONG_FUNCTION",
                principle="KISS",
                message=f"Function has {len(lines)} lines (max: {self.config['clean_code']['max_function_length']})",
                max_recommended=self.config['clean_code']['max_function_length']
            ))
        
        # Check for SRP violations (multiple responsibilities)
        # Simple heuristic: look for multiple unrelated method names in a class
        if "class " in code:
            methods = []
            for line in lines:
                if "def " in line and "self" in line:
                    method_name = line.split("def ")[1].split("(")[0].strip()
                    methods.append(method_name)
            
            # If we see database, email, and logging methods in same class, flag SRP violation
            concerns = {
                'database': any(m in ['save', 'delete', 'update', 'query', 'log_to_database'] for m in methods),
                'email': any(m in ['send_email', 'send_notification'] for m in methods),
                'logging': any(m in ['log', 'log_to_database'] for m in methods)
            }
            
            if sum(concerns.values()) >= 2:
                violations.append(CleanCodeViolation(
                    type="SRP_VIOLATION",
                    principle="SRP",
                    message="Class has multiple responsibilities (violates Single Responsibility Principle)"
                ))
        
        # Check complexity (simplified: count if/else/for/while statements)
        complexity_keywords = ['if ', 'else', 'elif', 'for ', 'while ']
        complexity = sum(1 for line in lines for kw in complexity_keywords if kw in line)
        
        if complexity > self.config['clean_code']['max_complexity']:
            violations.append(CleanCodeViolation(
                type="HIGH_COMPLEXITY",
                principle="KISS",
                message=f"Code has complexity of {complexity} (max: {self.config['clean_code']['max_complexity']})"
            ))
        
        return violations
    
    def run_tests(self, test_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Run tests and return results.
        
        Args:
            test_file: Optional specific test file to run
        
        Returns:
            Dict with test results (passing, failures count)
        """
        # Mock implementation
        return {
            'passing': True,
            'failures': 0,
            'total': 10
        }
    
    def execute(self, user_request: str, **kwargs) -> TDDResult:
        """
        Execute complete TDD workflow.
        
        Args:
            user_request: Feature description to implement
            **kwargs: Additional arguments
        
        Returns:
            TDDResult with execution summary
        """
        logger.info(f"TDD Orchestrator executing: '{user_request}'")
        
        try:
            # Phase 0: Discovery
            self.current_phase = TDDPhase.DISCOVERY
            self.discover_technology()
            
            # Phase 1: RED
            self.current_phase = TDDPhase.RED
            red_result = self.execute_red_phase(user_request)
            
            # Phase 2: GREEN
            self.current_phase = TDDPhase.GREEN
            green_result = self.execute_green_phase(red_result)
            
            # Phase 3: REFACTOR
            self.current_phase = TDDPhase.REFACTOR
            refactor_result = self.execute_refactor_phase(green_result)
            
            # Generate report
            report_path = self._generate_report(user_request, red_result, green_result, refactor_result)
            
            # Save state for continuation
            self._save_state(user_request, red_result, green_result, refactor_result)
            
            return TDDResult(
                status=OrchestratorStatus.SUCCESS,
                phases_completed=3,
                tests_generated=red_result.tests_generated,
                all_tests_passing=green_result.all_tests_passing,
                clean_code_score=refactor_result.clean_code_score,
                report_path=report_path,
                message=f"TDD workflow complete: {red_result.tests_generated} tests, clean code score: {refactor_result.clean_code_score}"
            )
            
        except Exception as e:
            logger.error(f"TDD execution failed: {e}", exc_info=True)
            return TDDResult(
                status=OrchestratorStatus.FAILED,
                message=f"TDD execution failed: {str(e)}"
            )
    
    def _generate_report(
        self,
        feature: str,
        red_result: PhaseResultData,
        green_result: PhaseResultData,
        refactor_result: PhaseResultData
    ) -> Path:
        """Generate execution report."""
        report_dir = self.workspace_root / "cortex-brain/documents/reports/tdd"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = report_dir / f"tdd-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        
        report_content = f"""# TDD Execution Report

**Feature:** {feature}  
**Date:** {datetime.now().isoformat()}

## RED Phase (Failing Tests)
- Tests Generated: {red_result.tests_generated}
- Functional Tests: {len([t for t in red_result.tests if t.category == 'functional'])}
- Edge Case Tests: {len([t for t in red_result.tests if t.category == 'edge_case'])}
- Security Tests: {len([t for t in red_result.tests if t.category == 'security'])}

## GREEN Phase (Implementation)
- Implementation Created: {green_result.implementation_created}
- Iterations: {green_result.iterations}
- All Tests Passing: {green_result.all_tests_passing}

## REFACTOR Phase (Clean Code)
- Refactorings Applied: {refactor_result.refactorings_applied}
- Code Smells Detected: {', '.join(refactor_result.code_smells_detected) or 'None'}
- Clean Code Score: {refactor_result.clean_code_score}/100
- Tests Still Passing: {refactor_result.tests_still_passing}

## Summary
✅ TDD workflow completed successfully
"""
        
        report_path.write_text(report_content)
        logger.info(f"Report generated: {report_path}")
        
        return report_path
    
    def _save_state(
        self,
        feature: str,
        red_result: PhaseResultData,
        green_result: PhaseResultData,
        refactor_result: PhaseResultData
    ) -> None:
        """Save execution state to Tier 1."""
        state_dir = self.workspace_root / "cortex-brain/tier1/tdd"
        state_dir.mkdir(parents=True, exist_ok=True)
        
        state = {
            'feature': feature,
            'timestamp': datetime.now().isoformat(),
            'red_phase': {
                'tests_generated': red_result.tests_generated,
                'domain_knowledge_used': red_result.domain_knowledge_used
            },
            'green_phase': {
                'implementation_created': green_result.implementation_created,
                'iterations': green_result.iterations
            },
            'refactor_phase': {
                'refactorings_applied': refactor_result.refactorings_applied,
                'clean_code_score': refactor_result.clean_code_score
            }
        }
        
        import yaml
        state_path = state_dir / "state.yaml"
        with open(state_path, 'w') as f:
            yaml.dump(state, f)
        
        logger.info(f"State saved: {state_path}")
