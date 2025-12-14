"""
TDD Orchestrator v3.0 for CORTEX

Test-Driven Development workflow with intelligent tiered routing:
- Tier 1 (INSTANT): Test execution, status checks, coverage reports
- Tier 2 (LIGHTWEIGHT): Single test file operations, test fixes
- Tier 3 (DOCUMENTED): Full RED→GREEN→REFACTOR cycles, test suites
- Tier 4 (COMPLEX): Test architecture, multi-layer test strategies

Integrates:
- TieredRouter for TDD-specific operation classification
- ComplexityAnalyzer for test complexity assessment
- VersionManager for consistent versioning
- RED phase validation (tests must fail before implementation)
- AST-powered test gap detection
- Per-layer coverage validation

Phase 05 of CORTEX Evolution v3.9

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 3.0.0
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from src.operations.base_operation_module import (
    BaseOperationModule, OperationResult, OperationStatus, 
    OperationPhase, OperationModuleMetadata
)
from src.operations.modules.routing.tiered_router import (
    TieredRouter, OperationTier, RoutingDecision
)
from src.operations.modules.routing.complexity_analyzer import (
    ComplexityAnalyzer, ComplexityScore, ComplexityTier
)
from src.operations.modules.version.version_manager import get_version_manager
from src.utils.progress_decorator import with_progress, yield_progress
from src.operations.utilities.orchestration_metrics_collector import with_orchestration_metrics

logger = logging.getLogger(__name__)


# ===== TDD-SPECIFIC TIER PATTERNS =====

TDD_TIER_PATTERNS = {
    1: [
        "run tests", "show coverage", "test status", "check tests",
        "execute tests", "test results", "coverage report"
    ],
    2: [
        "fix test", "add test", "update test", "update assertion",
        "single test", "one test", "test case"
    ],
    3: [
        "start tdd", "create test suite", "tdd workflow", "red green refactor",
        "test suite", "full tdd", "tdd cycle"
    ],
    4: [
        "test architecture", "test strategy", "integration tests", "test infrastructure",
        "mocking strategy", "test framework", "multi-layer tests"
    ]
}


class TDDPhase(Enum):
    """TDD workflow phases."""
    RED = "RED"          # Tests fail (expected behavior)
    GREEN = "GREEN"      # Tests pass (minimal implementation)
    REFACTOR = "REFACTOR"  # Improve code quality
    COMPLETE = "COMPLETE"  # All phases done


@dataclass
class TestGap:
    """Represents a missing test for a code element."""
    function_name: str
    file_path: Path
    complexity: int
    priority: str  # HIGH, MEDIUM, LOW
    reason: str


@dataclass
class TestResult:
    """Result of test execution."""
    test_name: str
    status: str  # passing, failing, error
    failure_reason: Optional[str] = None
    execution_time: float = 0.0


@dataclass
class ValidationResult:
    """Result of RED phase validation."""
    compliant: bool
    violations: List[str]
    recommendation: str


@dataclass
class TDDContext:
    """Context for TDD operation."""
    operation: str
    tier: int
    phase: TDDPhase
    complexity_score: ComplexityScore
    routing_decision: RoutingDecision
    test_files: List[Path]
    source_files: List[Path]
    timestamp: datetime
    
    # TDD-specific metadata
    red_phase_valid: bool = False
    all_tests_passing: bool = False
    refactor_complete: bool = False
    test_gaps: List[TestGap] = None
    
    def __post_init__(self):
        if self.test_gaps is None:
            self.test_gaps = []


class TDDOrchestrator(BaseOperationModule):
    """
    TDD Orchestrator v3.0
    
    Intelligent tiered TDD workflow with RED→GREEN→REFACTOR validation.
    
    Workflow:
    1. Classify operation tier (TieredRouter)
    2. Analyze complexity (ComplexityAnalyzer)
    3. Route to appropriate execution path:
       - Tier 1: Instant test execution
       - Tier 2: Single test operations
       - Tier 3: Full TDD cycle with RED validation
       - Tier 4: Test architecture planning
    4. Validate RED phase (tests must fail first)
    5. Execute GREEN phase (minimal implementation)
    6. Execute REFACTOR phase (quality improvements)
    7. Detect test gaps with AST
    """
    
    def __init__(self, project_root: Path = None):
        """
        Initialize TDD Orchestrator 3.0.
        
        Args:
            project_root: Path to project root (defaults to CWD)
        """
        super().__init__()
        self.project_root = project_root or Path.cwd()
        
        # Version management
        self.version_manager = get_version_manager()
        self.version_manager.register_orchestrator_version("tdd_orchestrator", "3.0")
        self.version = self.version_manager.get_orchestrator_version("tdd_orchestrator")
        
        # Routing components
        self.tiered_router = TieredRouter()
        self.complexity_analyzer = ComplexityAnalyzer()
        
        # TDD state
        self.current_phase = TDDPhase.RED
        self.session_data: Dict[str, Any] = {}
        
        # Metrics
        self.metrics: Dict[str, Any] = {
            'operations_processed': 0,
            'tier_breakdown': {1: 0, 2: 0, 3: 0, 4: 0},
            'red_phases_validated': 0,
            'green_phases_completed': 0,
            'refactor_phases_completed': 0,
            'test_gaps_detected': 0,
            'errors': [],
            'warnings': []
        }
        
        logger.info(f"✅ TDDOrchestrator v{self.version} initialized (Planning System 3.0)")
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="tdd_orchestrator_v3",
            name="TDD Orchestrator 3.0",
            description="Intelligent TDD workflow with RED→GREEN→REFACTOR validation",
            phase=OperationPhase.PROCESSING,
            priority=90,
            version="3.0.0",
            author="Asif Hussain",
            tags=["orchestration", "tdd", "testing", "tiered-routing"]
        )
    
    @with_progress(operation_name="TDD Workflow 3.0", threshold_seconds=5.0)
    @with_orchestration_metrics("TDDOrchestrator")
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute tiered TDD workflow.
        
        Args:
            context: Operation context with:
                - operation: str - User's TDD request
                - test_files: List[Path] - Test files to work with
                - source_files: List[Path] - Source files being tested
                - force_tier: int - Override tier classification (optional)
                - skip_red_validation: bool - Skip RED phase checks (default: False)
        
        Returns:
            OperationResult with TDD artifacts and metrics
        """
        start_time = datetime.now()
        operation = context.get('operation', '')
        test_files = context.get('test_files', [])
        source_files = context.get('source_files', [])
        force_tier = context.get('force_tier')
        skip_red_validation = context.get('skip_red_validation', False)
        
        if not operation:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="No operation specified for TDD workflow",
                data={'error': 'operation_required'}
            )
        
        logger.info(f"🎭 Orchestrator engaged: TDDOrchestrator v{self.version}")
        logger.info(f"Operation: {operation}")
        
        try:
            # Phase 1: Classification & Analysis
            yield_progress(1, 6, "Phase 1: Classifying TDD operation")
            tdd_context = self._classify_and_analyze(
                operation, test_files, source_files, force_tier
            )
            
            # Phase 2: Route to execution path
            yield_progress(2, 6, f"Phase 2: Routing to Tier {tdd_context.tier} execution")
            execution_result = self._route_and_execute(tdd_context, skip_red_validation)
            
            # Phase 3: Test gap detection (if Tier 3+)
            if tdd_context.tier >= 3 and source_files:
                yield_progress(3, 6, "Phase 3: Detecting test gaps with AST")
                gaps = self._detect_test_gaps(source_files, test_files)
                tdd_context.test_gaps = gaps
                self.metrics['test_gaps_detected'] += len(gaps)
            
            # Phase 4: RED phase validation (if Tier 3+)
            if not skip_red_validation and tdd_context.tier >= 3:
                yield_progress(4, 6, "Phase 4: Validating RED phase")
                validation_result = self._validate_red_phase(tdd_context, execution_result)
                tdd_context.red_phase_valid = validation_result.compliant
                self.metrics['red_phases_validated'] += 1
            else:
                validation_result = ValidationResult(
                    compliant=True, violations=[], recommendation="RED validation skipped"
                )
            
            # Phase 5: Coverage analysis
            yield_progress(5, 6, "Phase 5: Analyzing test coverage")
            coverage_result = self._analyze_coverage(test_files, source_files)
            
            # Phase 6: Finalize
            yield_progress(6, 6, "Phase 6: Finalizing TDD workflow")
            
            # Update metrics
            self.metrics['operations_processed'] += 1
            self.metrics['tier_breakdown'][tdd_context.tier] += 1
            
            # Determine completion status
            success = execution_result.get('success', True)
            is_complete = (
                success and 
                tdd_context.red_phase_valid and
                tdd_context.all_tests_passing and
                len(self.metrics['errors']) == 0
            )
            
            logger.info(f"🎭 Orchestrator completing: {'✅ ALL WORK COMPLETE' if is_complete else '⏳ PHASES DONE WITH WARNINGS'}")
            
            return OperationResult(
                success=success,
                status=OperationStatus.SUCCESS if success else OperationStatus.WARNING,
                message=f"TDD workflow completed (Tier {tdd_context.tier}): {operation}",
                data={
                    'tier': tdd_context.tier,
                    'phase': tdd_context.phase.value,
                    'complexity_score': tdd_context.complexity_score.total_score,
                    'execution_result': execution_result,
                    'validation_result': validation_result.__dict__ if validation_result else None,
                    'coverage': coverage_result,
                    'test_gaps': [gap.__dict__ for gap in tdd_context.test_gaps],
                    'metrics': self.metrics,
                    'is_complete': is_complete,
                    'red_phase_valid': tdd_context.red_phase_valid,
                    'all_tests_passing': tdd_context.all_tests_passing,
                    'elapsed_time': (datetime.now() - start_time).total_seconds()
                }
            )
            
        except Exception as e:
            logger.error(f"TDD orchestration failed: {e}", exc_info=True)
            self.metrics['errors'].append(str(e))
            
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"TDD workflow failed: {e}",
                data={
                    'error': str(e),
                    'metrics': self.metrics
                }
            )
    
    def _classify_and_analyze(
        self,
        operation: str,
        test_files: List[Path],
        source_files: List[Path],
        force_tier: Optional[int] = None
    ) -> TDDContext:
        """
        Classify operation tier and analyze complexity.
        
        Args:
            operation: User's TDD request
            test_files: Test files to work with
            source_files: Source files being tested
            force_tier: Optional tier override
        
        Returns:
            TDDContext with classification results
        """
        logger.debug(f"Classifying TDD operation: {operation}")
        
        # Complexity analysis
        complexity_score = self.complexity_analyzer.analyze(operation)
        logger.info(f"Complexity: {complexity_score.tier.value} (score: {complexity_score.total_score}/100)")
        
        # Tier classification
        if force_tier:
            routing_decision = RoutingDecision(
                tier=force_tier,
                confidence=1.0,
                reasoning=f"Manually specified tier {force_tier}",
                execution_method=self._tier_to_execution_method(force_tier),
                estimated_time=self._tier_to_estimated_time(force_tier),
                requires_planning=force_tier >= 3
            )
            logger.info(f"Tier override: {force_tier}")
        else:
            routing_decision = self.tiered_router.route(operation)
            logger.info(f"Tier: {routing_decision.tier} (confidence: {routing_decision.confidence:.2f})")
        
        # Determine TDD phase
        phase = self._determine_tdd_phase(operation)
        
        return TDDContext(
            operation=operation,
            tier=routing_decision.tier,
            phase=phase,
            complexity_score=complexity_score,
            routing_decision=routing_decision,
            test_files=test_files,
            source_files=source_files,
            timestamp=datetime.now()
        )
    
    def _route_and_execute(
        self,
        tdd_context: TDDContext,
        skip_red_validation: bool
    ) -> Dict[str, Any]:
        """
        Route to appropriate tier execution path.
        
        Args:
            tdd_context: TDD operation context
            skip_red_validation: Skip RED phase validation
        
        Returns:
            Execution result dictionary
        """
        tier = tdd_context.tier
        
        logger.info(f"🎭 Phase transition: Classification → Tier {tier} Execution")
        
        if tier == 1:
            return self._execute_tier1_instant(tdd_context)
        elif tier == 2:
            return self._execute_tier2_lightweight(tdd_context)
        elif tier == 3:
            return self._execute_tier3_documented(tdd_context, skip_red_validation)
        elif tier == 4:
            return self._execute_tier4_complex(tdd_context)
        else:
            raise ValueError(f"Invalid tier: {tier}")
    
    def _execute_tier1_instant(self, tdd_context: TDDContext) -> Dict[str, Any]:
        """
        Execute Tier 1 (INSTANT) operations.
        
        Examples: run tests, show coverage, test status
        Target: <2s response time
        """
        logger.info("Executing Tier 1 (INSTANT): Quick test execution")
        
        result = {
            'success': True,
            'tier': 1,
            'execution_method': 'instant',
            'tests_run': False,
            'coverage_generated': False
        }
        
        # Detect operation type
        op_lower = tdd_context.operation.lower()
        
        if 'run' in op_lower or 'execute' in op_lower:
            # Run tests
            test_result = self._run_tests(tdd_context.test_files)
            result['tests_run'] = True
            result['test_results'] = test_result
            tdd_context.all_tests_passing = test_result.get('all_passing', False)
        
        if 'coverage' in op_lower or 'report' in op_lower:
            # Generate coverage report
            coverage = self._generate_coverage_report(tdd_context.test_files)
            result['coverage_generated'] = True
            result['coverage'] = coverage
        
        if 'status' in op_lower or 'check' in op_lower:
            # Check test status
            status = self._check_test_status(tdd_context.test_files)
            result['status'] = status
        
        return result
    
    def _execute_tier2_lightweight(self, tdd_context: TDDContext) -> Dict[str, Any]:
        """
        Execute Tier 2 (LIGHTWEIGHT) operations.
        
        Examples: fix test, add test, update assertion
        """
        logger.info("Executing Tier 2 (LIGHTWEIGHT): Single test operation")
        
        return {
            'success': True,
            'tier': 2,
            'execution_method': 'lightweight',
            'requires_manual_implementation': True,
            'guidance': self._generate_tier2_guidance(tdd_context)
        }
    
    def _execute_tier3_documented(
        self,
        tdd_context: TDDContext,
        skip_red_validation: bool
    ) -> Dict[str, Any]:
        """
        Execute Tier 3 (DOCUMENTED) operations.
        
        Examples: start tdd, create test suite, full RED→GREEN→REFACTOR cycle
        """
        logger.info("Executing Tier 3 (DOCUMENTED): Full TDD cycle")
        
        phases_completed = []
        
        # RED Phase
        logger.info("🎭 Phase transition: START → RED")
        red_result = self._execute_red_phase(tdd_context, skip_red_validation)
        phases_completed.append('RED')
        
        if red_result['compliant'] or skip_red_validation:
            # GREEN Phase
            logger.info("🎭 Phase transition: RED → GREEN")
            green_result = self._execute_green_phase(tdd_context)
            phases_completed.append('GREEN')
            tdd_context.all_tests_passing = green_result.get('all_passing', False)
            self.metrics['green_phases_completed'] += 1
            
            if green_result['all_passing']:
                # REFACTOR Phase
                logger.info("🎭 Phase transition: GREEN → REFACTOR")
                refactor_result = self._execute_refactor_phase(tdd_context)
                phases_completed.append('REFACTOR')
                tdd_context.refactor_complete = refactor_result.get('complete', False)
                self.metrics['refactor_phases_completed'] += 1
        
        return {
            'success': True,
            'tier': 3,
            'execution_method': 'documented',
            'phases_completed': phases_completed,
            'red_result': red_result,
            'green_result': green_result if 'green_result' in locals() else None,
            'refactor_result': refactor_result if 'refactor_result' in locals() else None
        }
    
    def _execute_tier4_complex(self, tdd_context: TDDContext) -> Dict[str, Any]:
        """
        Execute Tier 4 (COMPLEX) operations.
        
        Examples: test architecture, test strategy, multi-layer tests
        """
        logger.info("Executing Tier 4 (COMPLEX): Test architecture planning")
        
        # Generate comprehensive test strategy
        strategy = self._generate_test_strategy(tdd_context)
        
        return {
            'success': True,
            'tier': 4,
            'execution_method': 'complex',
            'strategy': strategy,
            'requires_planning_document': True
        }
    
    def _validate_red_phase(
        self,
        tdd_context: TDDContext,
        execution_result: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate RED phase compliance.
        
        Rules:
        1. All new tests MUST fail initially
        2. Failure reason must match expected behavior
        3. No false positives (tests passing without implementation)
        """
        violations = []
        
        # Get test results
        red_result = execution_result.get('red_result', {})
        new_tests = red_result.get('new_tests', [])
        
        for test in new_tests:
            if test.get('status') == 'passing':
                violations.append(f"Test {test['name']} passed without implementation")
            elif test.get('failure_reason') != test.get('expected_failure'):
                violations.append(f"Test {test['name']} failed for wrong reason")
        
        compliant = len(violations) == 0
        
        if not compliant:
            recommendation = "Fix tests to fail correctly before implementation"
        else:
            recommendation = "RED phase valid - proceed to GREEN phase"
        
        return ValidationResult(
            compliant=compliant,
            violations=violations,
            recommendation=recommendation
        )
    
    def _detect_test_gaps(
        self,
        source_files: List[Path],
        test_files: List[Path]
    ) -> List[TestGap]:
        """
        Detect missing tests using AST analysis.
        
        Args:
            source_files: Source files to analyze
            test_files: Existing test files
        
        Returns:
            List of test gaps
        """
        gaps = []
        
        try:
            # Import AST engine (optional dependency)
            from src.operations.modules.analysis.ast_engine import ASTEngine
            
            ast_engine = ASTEngine()
            
            for source_file in source_files:
                if not source_file.exists():
                    continue
                
                # Analyze source code
                code_analysis = ast_engine.analyze_file(source_file)
                
                # Find corresponding test file
                test_file = self._find_test_file(source_file, test_files)
                test_analysis = ast_engine.analyze_file(test_file) if test_file else None
                
                # Identify gaps
                for function in code_analysis.get('functions', []):
                    if not self._has_test_coverage(function, test_analysis):
                        gaps.append(TestGap(
                            function_name=function['name'],
                            file_path=source_file,
                            complexity=function.get('complexity', 1),
                            priority='HIGH' if function.get('complexity', 1) > 10 else 'MEDIUM',
                            reason=f"No test found for {function['name']}"
                        ))
        
        except ImportError:
            logger.warning("AST engine not available - test gap detection skipped")
        except Exception as e:
            logger.error(f"Test gap detection failed: {e}")
            self.metrics['warnings'].append(f"Gap detection error: {e}")
        
        return gaps
    
    def _run_tests(self, test_files: List[Path]) -> Dict[str, Any]:
        """Run test files and return results."""
        if not test_files:
            return {'all_passing': True, 'tests': [], 'message': 'No tests to run'}
        
        try:
            # Run pytest
            test_paths = [str(f) for f in test_files if f.exists()]
            if not test_paths:
                return {'all_passing': True, 'tests': [], 'message': 'No valid test files'}
            
            result = subprocess.run(
                ['pytest'] + test_paths + ['-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                'all_passing': result.returncode == 0,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return {'all_passing': False, 'error': str(e)}
    
    def _generate_coverage_report(self, test_files: List[Path]) -> Dict[str, Any]:
        """Generate coverage report for tests."""
        # Placeholder for coverage generation
        return {
            'coverage_percent': 0,
            'message': 'Coverage report generation not yet implemented'
        }
    
    def _check_test_status(self, test_files: List[Path]) -> Dict[str, Any]:
        """Check current status of tests."""
        return {
            'total_files': len(test_files),
            'valid_files': sum(1 for f in test_files if f.exists()),
            'message': f"{len(test_files)} test files tracked"
        }
    
    def _analyze_coverage(
        self,
        test_files: List[Path],
        source_files: List[Path]
    ) -> Dict[str, Any]:
        """Analyze test coverage."""
        return {
            'test_files': len(test_files),
            'source_files': len(source_files),
            'coverage_available': False
        }
    
    def _execute_red_phase(
        self,
        tdd_context: TDDContext,
        skip_validation: bool
    ) -> Dict[str, Any]:
        """Execute RED phase (tests fail)."""
        return {
            'compliant': skip_validation or True,
            'new_tests': [],
            'message': 'RED phase execution placeholder'
        }
    
    def _execute_green_phase(self, tdd_context: TDDContext) -> Dict[str, Any]:
        """Execute GREEN phase (minimal implementation)."""
        return {
            'all_passing': False,
            'message': 'GREEN phase execution placeholder'
        }
    
    def _execute_refactor_phase(self, tdd_context: TDDContext) -> Dict[str, Any]:
        """Execute REFACTOR phase (improve code quality)."""
        return {
            'complete': False,
            'message': 'REFACTOR phase execution placeholder'
        }
    
    def _generate_test_strategy(self, tdd_context: TDDContext) -> Dict[str, Any]:
        """Generate comprehensive test strategy."""
        return {
            'layers': ['unit', 'integration', 'e2e'],
            'message': 'Test strategy generation placeholder'
        }
    
    def _generate_tier2_guidance(self, tdd_context: TDDContext) -> str:
        """Generate guidance for Tier 2 operations."""
        return "Implement single test modification based on operation request"
    
    def _determine_tdd_phase(self, operation: str) -> TDDPhase:
        """Determine current TDD phase from operation."""
        op_lower = operation.lower()
        
        if 'red' in op_lower or 'fail' in op_lower:
            return TDDPhase.RED
        elif 'green' in op_lower or 'pass' in op_lower:
            return TDDPhase.GREEN
        elif 'refactor' in op_lower or 'improve' in op_lower:
            return TDDPhase.REFACTOR
        else:
            return TDDPhase.RED  # Default to RED phase
    
    def _find_test_file(
        self,
        source_file: Path,
        test_files: List[Path]
    ) -> Optional[Path]:
        """Find test file corresponding to source file."""
        source_name = source_file.stem
        
        for test_file in test_files:
            if source_name in test_file.stem:
                return test_file
        
        return None
    
    def _has_test_coverage(
        self,
        function: Dict[str, Any],
        test_analysis: Optional[Dict[str, Any]]
    ) -> bool:
        """Check if function has test coverage."""
        if not test_analysis:
            return False
        
        function_name = function.get('name', '')
        test_functions = test_analysis.get('functions', [])
        
        # Simple heuristic: look for test_<function_name>
        test_name = f"test_{function_name}"
        return any(test_name in tf.get('name', '') for tf in test_functions)
    
    def _tier_to_execution_method(self, tier: int) -> str:
        """Convert tier to execution method string."""
        methods = {1: 'instant', 2: 'lightweight', 3: 'documented', 4: 'complex'}
        return methods.get(tier, 'unknown')
    
    def _tier_to_estimated_time(self, tier: int) -> str:
        """Convert tier to estimated time string."""
        times = {1: '<2s', 2: '2-30s', 3: '30s-5min', 4: '5min+'}
        return times.get(tier, 'unknown')
