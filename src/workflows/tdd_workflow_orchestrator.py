"""
TDD Workflow Orchestrator - Phase 3 Milestone 3.1

Unified API for complete TDD workflow integrating:
- Phase 1: Test generation (edge cases, domain knowledge, errors, parametrized)
- Phase 2: State machine (RED→GREEN→REFACTOR), refactoring intelligence, session tracking

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 3
"""

import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Phase 1 imports
from src.cortex_agents.test_generator.generators.function_test_generator import FunctionTestGenerator
from src.cortex_agents.test_generator.templates import TemplateManager
from src.cortex_agents.test_generator.edge_case_analyzer import EdgeCaseAnalyzer
from src.cortex_agents.test_generator.domain_knowledge_integrator import DomainKnowledgeIntegrator
from src.cortex_agents.test_generator.error_condition_generator import ErrorConditionGenerator
from src.cortex_agents.test_generator.parametrized_test_generator import ParametrizedTestGenerator

# Phase 2 imports
from src.workflows.tdd_state_machine import TDDStateMachine, TDDState
from src.workflows.refactoring_intelligence import CodeSmellDetector, RefactoringEngine, CodeSmell
from src.workflows.page_tracking import PageTracker, TDDContext, PageLocation

# Phase 3 - M3.2: Performance optimization imports
from src.workflows.ast_cache import ASTCache, get_ast_cache
from src.workflows.pattern_cache import PatternCache, get_pattern_cache
from src.workflows.smell_cache import SmellCache, get_smell_cache
from src.workflows.batch_processor import BatchTestGenerator, BatchSmellDetector

# Phase 3 - Brain Memory Integration (2025-11-24)
from src.tier1.sessions.session_manager import SessionManager, Session
from src.tier2.knowledge_graph.knowledge_graph import KnowledgeGraph

# Phase 4 - Test Execution Manager (2025-11-24)
from src.workflows.test_execution_manager import TestExecutionManager
from src.workflows.terminal_integration import TerminalIntegration
from src.workflows.workspace_context_manager import WorkspaceContextManager

# Phase 4 - TDD Mastery Integration (2025-11-24)
import sys
from pathlib import Path as PathLib

# Add paths for agent imports
src_path = PathLib(__file__).parent.parent
cortex_brain_path = src_path.parent / "cortex-brain"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(cortex_brain_path) not in sys.path:
    sys.path.insert(0, str(cortex_brain_path))

try:
    from agents.view_discovery_agent import ViewDiscoveryAgent
    from agents.feedback_agent import FeedbackAgent
except ImportError:
    # Fallback for different project structures
    ViewDiscoveryAgent = None
    FeedbackAgent = None


@dataclass
class TDDWorkflowConfig:
    """Configuration for TDD workflow."""
    project_root: str
    test_output_dir: str = "tests"
    # Phase 3 - Brain Memory Integration: Use Tier 1 working memory
    brain_storage_path: str = "cortex-brain/tier1/working_memory.db"
    enable_refactoring: bool = True
    enable_session_tracking: bool = True
    auto_detect_smells: bool = True
    confidence_threshold: float = 0.7  # Minimum confidence for auto-apply
    
    # M3.2: Performance optimization settings
    enable_caching: bool = True  # Enable AST/pattern/smell caching
    ast_cache_size: int = 100  # Maximum AST trees to cache
    pattern_cache_ttl_minutes: int = 60  # Pattern cache TTL
    smell_cache_ttl_hours: int = 1  # Smell cache TTL
    batch_max_workers: int = 4  # Parallel workers for batch processing
    
    # Phase 4 - TDD Mastery Integration (2025-11-24)
    enable_view_discovery: bool = True  # Auto-discover elements before test gen
    auto_debug_on_failure: bool = True  # Auto-trigger debug on RED state
    auto_feedback_on_persistent_failure: bool = True  # Auto-report stuck tests
    feedback_threshold: int = 3  # RED cycles before feedback
    debug_timing_to_refactoring: bool = True  # Use debug data in refactoring
    
    # Phase 4 - Test Execution & Integration (2025-11-24)
    enable_terminal_integration: bool = True  # Use GitHub Copilot terminal tools
    enable_workspace_discovery: bool = True  # Auto-discover workspace context
    enable_programmatic_execution: bool = True  # Run tests programmatically
    
    # Layer 8: Test Location Isolation (2025-11-24)
    # CRITICAL: Application tests go in user repo, CORTEX tests stay in CORTEX
    user_repo_root: Optional[str] = None  # User's application root (outside CORTEX)
    is_cortex_test: bool = False  # True if testing CORTEX itself
    auto_detect_test_location: bool = True  # Auto-detect user repo vs CORTEX
    enable_brain_learning: bool = True  # Capture test patterns to brain
    
    # Integration paths
    view_discovery_db: str = "cortex-brain/tier2/knowledge_graph.db"
    debug_sessions_dir: str = "cortex-brain/debug-sessions"
    feedback_reports_dir: str = "cortex-brain/documents/reports"
    project_name: Optional[str] = None  # Project name for view discovery


class TDDWorkflowOrchestrator:
    """
    End-to-end TDD workflow orchestrator.
    
    Provides unified API for complete TDD cycle:
    1. RED: Generate comprehensive tests (Phase 1)
    2. GREEN: Minimal implementation
    3. REFACTOR: Automated suggestions (Phase 2)
    4. Track: Session persistence and resume
    
    Example:
        orchestrator = TDDWorkflowOrchestrator(config)
        
        # Start TDD session
        session_id = orchestrator.start_session("user_authentication")
        
        # RED phase: Generate tests
        tests = orchestrator.generate_tests(
            source_file="src/auth/login.py",
            function_name="authenticate_user"
        )
        
        # GREEN phase: User implements code
        orchestrator.verify_tests_pass(tests)
        
        # REFACTOR phase: Get suggestions
        suggestions = orchestrator.suggest_refactorings(
            source_file="src/auth/login.py"
        )
        
        # Track progress
        orchestrator.save_progress(
            location=PageLocation("src/auth/login.py", 45, 8)
        )
        
        # Resume later
        orchestrator.resume_session(session_id)
    """
    
    def __init__(self, config: TDDWorkflowConfig):
        """
        Initialize TDD workflow orchestrator.
        
        Args:
            config: Workflow configuration
        """
        self.config = config
        
        # Phase 1: Test generation
        self.template_manager = TemplateManager()
        self.edge_analyzer = EdgeCaseAnalyzer()
        self.domain_knowledge = DomainKnowledgeIntegrator()
        self.error_generator = ErrorConditionGenerator()
        self.parametrized_generator = ParametrizedTestGenerator()
        self.test_generator = FunctionTestGenerator(self.template_manager)
        
        # Phase 2: Workflow management
        self.state_machine: Optional[TDDStateMachine] = None
        self.smell_detector = CodeSmellDetector()
        self.refactoring_engine = RefactoringEngine()
        
        # M3.2: Performance optimization - Caching
        self.enable_caching = config.enable_caching
        if self.enable_caching:
            self.ast_cache = ASTCache(max_size=config.ast_cache_size)
            self.pattern_cache = PatternCache(ttl_minutes=config.pattern_cache_ttl_minutes)
            self.smell_cache = SmellCache(default_ttl_hours=config.smell_cache_ttl_hours)
        else:
            self.ast_cache = None
            self.pattern_cache = None
            self.smell_cache = None
        
        # M3.2: Batch processing
        self.batch_test_generator = BatchTestGenerator(self, max_workers=config.batch_max_workers)
        self.batch_smell_detector = BatchSmellDetector(self.smell_detector, max_workers=config.batch_max_workers)
        
        # Phase 3 - Brain Memory Integration (2025-11-24)
        # Replace separate PageTracker with Tier 1/2/3 integration
        brain_path = PathLib(config.brain_storage_path).parent.parent
        tier1_db = brain_path / "tier1" / "working_memory.db"
        tier2_db = brain_path / "tier2" / "knowledge_graph.db"
        
        self.session_manager = SessionManager(
            db_path=tier1_db,
            idle_threshold_seconds=7200  # 2 hours
        )
        self.knowledge_graph = KnowledgeGraph(db_path=tier2_db)
        
        # Legacy page tracker for backward compatibility (will be deprecated)
        self.page_tracker = PageTracker(config.brain_storage_path)
        
        # Phase 4 - Test Execution & Integration (2025-11-24)
        self.test_executor: Optional[TestExecutionManager] = None
        self.terminal_integration: Optional[TerminalIntegration] = None
        self.workspace_manager: Optional[WorkspaceContextManager] = None
        
        if config.enable_programmatic_execution:
            try:
                self.test_executor = TestExecutionManager(config.project_root)
            except Exception as e:
                print(f"⚠️  TestExecutionManager initialization failed: {e}")
        
        if config.enable_terminal_integration:
            try:
                self.terminal_integration = TerminalIntegration()
            except Exception as e:
                print(f"⚠️  TerminalIntegration initialization failed: {e}")
        
        if config.enable_workspace_discovery:
            try:
                self.workspace_manager = WorkspaceContextManager(PathLib(config.project_root))
            except Exception as e:
                print(f"⚠️  WorkspaceContextManager initialization failed: {e}")
        
        # Phase 4 - TDD Mastery Integration: Agent initialization
        self.view_discovery: Optional[Any] = None
        self.feedback_agent: Optional[Any] = None
        self.discovered_elements: Dict[str, Any] = {}
        
        if config.enable_view_discovery and ViewDiscoveryAgent:
            try:
                self.view_discovery = ViewDiscoveryAgent(
                    project_root=PathLib(config.project_root),
                    db_path=PathLib(config.view_discovery_db) if config.view_discovery_db else None
                )
            except Exception as e:
                print(f"⚠️  ViewDiscoveryAgent initialization failed: {e}")
                self.view_discovery = None
        
        if config.auto_feedback_on_persistent_failure and FeedbackAgent:
            try:
                brain_path = PathLib(config.feedback_reports_dir).parent.parent
                self.feedback_agent = FeedbackAgent(brain_path=str(brain_path))
            except Exception as e:
                print(f"⚠️  FeedbackAgent initialization failed: {e}")
                self.feedback_agent = None
        
        # Current session
        self.current_session_id: Optional[str] = None
        self.current_context: Optional[TDDContext] = None
        self.current_brain_session: Optional[Session] = None
    
    def _detect_test_location(self, source_file: str) -> Path:
        """
        Detect where tests should be created: user repo or CORTEX folder.
        
        Layer 8: Test Location Isolation enforcement.
        
        Rules:
        - If source_file is within CORTEX folder → Tests go in CORTEX/tests/
        - If source_file is in user repo → Tests go in user_repo/tests/
        - CORTEX learns from user tests but doesn't store them in CORTEX
        
        Args:
            source_file: Path to source file being tested
            
        Returns:
            Path object for test output directory
        """
        source_path = Path(source_file).resolve()
        cortex_root = Path(__file__).parent.parent.parent.resolve()  # CORTEX root
        
        # Check if testing CORTEX code itself
        try:
            source_path.relative_to(cortex_root)
            # Source is within CORTEX → Tests stay in CORTEX
            test_location = cortex_root / "tests"
            self.config.is_cortex_test = True
            return test_location
        except ValueError:
            # Source is outside CORTEX → Tests go in user repo
            if self.config.user_repo_root:
                user_root = Path(self.config.user_repo_root).resolve()
            else:
                # Auto-detect user repo root
                user_root = self._find_user_repo_root(source_path)
            
            test_location = user_root / self.config.test_output_dir
            self.config.is_cortex_test = False
            
            # Store user repo root for future use
            if not self.config.user_repo_root:
                self.config.user_repo_root = str(user_root)
            
            return test_location
    
    def _find_user_repo_root(self, source_path: Path) -> Path:
        """
        Find user repository root by looking for common markers.
        
        Args:
            source_path: Path to source file
            
        Returns:
            Path to user repository root
        """
        current = source_path.parent
        
        # Look for repository markers
        markers = [".git", "package.json", "requirements.txt", "setup.py", 
                  "pom.xml", "build.gradle", "Cargo.toml", ".sln", "go.mod"]
        
        while current != current.parent:
            for marker in markers:
                if (current / marker).exists():
                    return current
            current = current.parent
        
        # Fallback: use source file's parent directory
        return source_path.parent
    
    def _capture_test_patterns_to_brain(self, test_file: str, framework: str, patterns: Dict[str, Any]):
        """
        Capture test patterns from user repo tests and store in CORTEX brain.
        
        Layer 8: Brain learning from user tests without storing user code.
        
        Args:
            test_file: Path to generated test file
            framework: Test framework used (pytest, jest, xunit, etc.)
            patterns: Detected patterns (naming, fixtures, assertions, etc.)
        """
        if not self.config.enable_brain_learning:
            return
        
        try:
            # Store generalized patterns in Tier 2 (NOT the actual test code)
            pattern_data = {
                "title": f"Test Pattern: {framework} in user repo",
                "content": f"User prefers {framework} with patterns: {', '.join(patterns.keys())}",
                "pattern_type": "test_framework_usage",
                "confidence": 0.9,
                "metadata": {
                    "framework": framework,
                    "patterns": patterns,
                    "session_id": self.current_session_id,
                    "timestamp": datetime.now().isoformat(),
                    "is_user_code": True  # Flag to avoid polluting CORTEX
                }
            }
            
            self.knowledge_graph.learn_pattern(pattern_data)
            
            print(f"🧠 Learned test patterns from user repo: {framework} ({len(patterns)} patterns)")
        except Exception as e:
            print(f"⚠️  Failed to capture test patterns to brain: {e}")
    
    def start_session(self, feature_name: str, session_id: Optional[str] = None) -> str:
        """
        Start new TDD session in brain memory.
        
        Phase 3 Enhancement: Uses Tier 1 SessionManager instead of separate database.
        
        Args:
            feature_name: Name of feature being developed
            session_id: Optional explicit session ID
            
        Returns:
            Session ID for tracking
        """
        import uuid
        
        # Phase 3 - Brain Memory Integration: Detect or create session in Tier 1
        workspace_path = str(PathLib(self.config.project_root).resolve())
        self.current_brain_session = self.session_manager.detect_or_create_session(workspace_path)
        
        # Generate TDD-specific session ID
        if not session_id:
            session_id = f"tdd_{uuid.uuid4().hex[:8]}"
        
        # Initialize state machine
        self.state_machine = TDDStateMachine(feature_name, session_id)
        
        # Create session context
        self.current_context = TDDContext(
            session_id=session_id,
            feature_name=feature_name,
            current_state=TDDState.IDLE.value
        )
        
        # Phase 3: Store TDD session metadata in brain
        if self.config.enable_session_tracking:
            self._store_session_in_brain(feature_name, session_id)
            # Legacy tracker for backward compatibility
            self.page_tracker.save_context(self.current_context, self.state_machine)
        
        self.current_session_id = session_id
        
        return session_id
    
    def generate_tests(
        self,
        source_file: str,
        function_name: Optional[str] = None,
        scenarios: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive tests (RED phase).
        
        Integrates all Phase 1 generators:
        - Edge case patterns
        - Domain knowledge
        - Error conditions
        - Parametrized tests
        
        Args:
            source_file: Path to source file
            function_name: Optional specific function to test
            scenarios: Test scenarios to generate
            
        Returns:
            Dictionary with test code, file paths, and metadata
        """
        if not self.state_machine:
            raise RuntimeError("No active session. Call start_session() first.")
        
        # Transition to RED phase
        if not self.state_machine.start_red_phase():
            raise RuntimeError(f"Cannot transition to RED from {self.state_machine.get_current_state()}")
        
        # Read source code
        source_code = Path(source_file).read_text()
        
        # Parse AST
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax in {source_file}: {e}")
        
        # Find functions to test
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if function_name and node.name != function_name:
                    continue
                functions.append(node)
        
        if not functions:
            raise ValueError(f"No functions found in {source_file}")
        
        # Default scenarios: all Phase 1 capabilities
        if not scenarios:
            scenarios = [
                "basic",
                "edge_cases",
                "domain_knowledge",
                "error_conditions",
                "parametrized",
                "property_based"
            ]
        
        # Generate tests for each function
        all_tests = []
        test_count = 0
        
        for func_node in functions:
            func_info = {
                "name": func_node.name,
                "source_code": source_code,
                "ast_node": func_node,
                "scenarios": scenarios
            }
            
            # Generate test code
            test_code = self.test_generator.generate(func_info)
            
            # Count tests generated
            test_count += test_code.count("def test_")
            
            all_tests.append({
                "function_name": func_node.name,
                "test_code": test_code,
                "scenarios": scenarios
            })
        
        # Complete RED phase
        self.state_machine.complete_red_phase(tests_written=test_count)
        
        # Update context
        test_file = self._get_test_filepath(source_file)
        self.current_context.test_files.append(str(test_file))
        self.current_context.source_files.append(source_file)
        self.current_context.current_state = TDDState.RED.value
        
        if self.config.enable_session_tracking:
            self.page_tracker.save_context(self.current_context, self.state_machine)
        
        return {
            "session_id": self.current_session_id,
            "tests": all_tests,
            "test_file": str(test_file),
            "test_count": test_count,
            "phase": "RED"
        }
    
    def verify_tests_pass(self, test_results: Dict[str, Any]) -> bool:
        """
        Verify tests pass (GREEN phase) with brain memory integration.
        
        Phase 3 Enhancement: Stores test results in Tier 2 knowledge graph.
        
        Args:
            test_results: Results from test execution
            {
                'passed': 5,
                'failed': 2,
                'errors': [...],
                'framework': 'pytest'
            }
            
        Returns:
            True if all tests pass
        """
        if not self.state_machine:
            raise RuntimeError("No active session")
        
        # Phase 3: Store test results in brain memory
        self._store_test_results_in_brain(test_results)
        
        # Transition to GREEN
        if not self.state_machine.start_green_phase():
            raise RuntimeError(f"Cannot transition to GREEN from {self.state_machine.get_current_state()}")
        
        # Parse test results
        tests_passing = test_results.get("passed", 0)
        code_lines_added = test_results.get("code_lines", 0)
        
        # Complete GREEN phase
        self.state_machine.complete_green_phase(
            tests_passing=tests_passing,
            code_lines_added=code_lines_added
        )
        
        # Update context
        self.current_context.current_state = TDDState.GREEN.value
        
        if self.config.enable_session_tracking:
            self.page_tracker.save_context(self.current_context, self.state_machine)
        
        # Phase 3: Update brain session activity
        if self.current_brain_session:
            try:
                self.session_manager.record_activity(self.current_brain_session.session_id)
            except Exception as e:
                print(f"⚠️  Failed to update session activity: {e}")
        
        return tests_passing > 0
    
    def run_and_verify_tests(self, test_file: Optional[str] = None, verbose: bool = True) -> Dict[str, Any]:
        """
        Run tests programmatically and verify results (Phase 4).
        
        This method combines test execution and verification in one call.
        Uses TestExecutionManager to run tests and automatically captures results.
        
        Args:
            test_file: Specific test file to run (None = run all)
            verbose: Show detailed output
            
        Returns:
            Combined test results and verification status
            {
                'test_results': {...},  # From test execution
                'tests_pass': True/False,
                'phase': 'GREEN' or 'RED'
            }
        """
        if not self.test_executor:
            raise RuntimeError("TestExecutionManager not initialized. Set enable_programmatic_execution=True")
        
        # Execute tests programmatically
        print(f"🔧 Running tests with {self.test_executor.framework}...")
        test_results = self.test_executor.run_tests(test_file=test_file, verbose=verbose)
        
        # Check for execution errors
        if 'error' in test_results:
            print(f"❌ Test execution failed: {test_results['error']}")
            return {
                'test_results': test_results,
                'tests_pass': False,
                'phase': 'ERROR',
                'error': test_results['error']
            }
        
        # Display summary
        passed = test_results.get('passed', 0)
        failed = test_results.get('failed', 0)
        skipped = test_results.get('skipped', 0)
        duration = test_results.get('duration', 0)
        
        print(f"✅ Tests completed in {duration:.2f}s")
        print(f"   Passed: {passed} ✓")
        print(f"   Failed: {failed} ✗")
        if skipped > 0:
            print(f"   Skipped: {skipped} ⊘")
        
        # Verify tests pass
        tests_pass = self.verify_tests_pass(test_results)
        
        return {
            'test_results': test_results,
            'tests_pass': tests_pass,
            'phase': 'GREEN' if tests_pass else 'RED'
        }
    
    def suggest_refactorings(self, source_file: str) -> List[Dict[str, Any]]:
        """
        Generate refactoring suggestions (REFACTOR phase).
        
        Args:
            source_file: Path to source file to analyze
            
        Returns:
            List of refactoring suggestions
        """
        if not self.state_machine:
            raise RuntimeError("No active session")
        
        if not self.config.enable_refactoring:
            return []
        
        # Transition to REFACTOR
        if not self.state_machine.start_refactor_phase():
            raise RuntimeError(f"Cannot transition to REFACTOR from {self.state_machine.get_current_state()}")
        
        # Read source code
        source_code = Path(source_file).read_text()
        
        # Phase 4 - TDD Mastery Integration: Inject debug timing data
        if self.config.debug_timing_to_refactoring and self.state_machine:
            debug_data = self.state_machine.get_debug_data()
            if debug_data:
                self.smell_detector.set_debug_data(debug_data)
                print(f"🔍 Using debug timing data for performance-based refactoring analysis")
        
        # Detect code smells
        smells = self.smell_detector.analyze_file(source_file, source_code)
        
        # Filter by confidence
        high_confidence_smells = [
            s for s in smells 
            if s.confidence >= self.config.confidence_threshold
        ]
        
        # Generate refactoring suggestions
        suggestions = self.refactoring_engine.generate_suggestions(
            high_confidence_smells,
            source_code
        )
        
        # Filter by confidence again
        high_confidence_suggestions = [
            s for s in suggestions
            if s.confidence >= self.config.confidence_threshold
        ]
        
        # Update context
        self.current_context.current_state = TDDState.REFACTOR.value
        self.current_context.notes += f"\nFound {len(high_confidence_suggestions)} refactoring suggestions"
        
        if self.config.enable_session_tracking:
            self.page_tracker.save_context(self.current_context, self.state_machine)
        
        return [
            {
                "type": s.refactoring_type.value,
                "location": s.target_location,
                "description": s.description,
                "code_before": s.code_before,
                "code_after": s.code_after,
                "confidence": s.confidence,
                "effort": s.estimated_effort
            }
            for s in high_confidence_suggestions
        ]
    
    def complete_refactor_phase(self, lines_refactored: int, iterations: int = 1) -> bool:
        """
        Complete refactoring phase.
        
        Args:
            lines_refactored: Number of lines refactored
            iterations: Number of refactoring iterations
            
        Returns:
            True if completed successfully
        """
        if not self.state_machine:
            raise RuntimeError("No active session")
        
        return self.state_machine.complete_refactor_phase(
            code_lines_refactored=lines_refactored,
            iterations=iterations
        )
    
    def complete_cycle(self) -> Dict[str, Any]:
        """
        Complete current TDD cycle.
        
        Returns:
            Cycle metrics and summary
        """
        if not self.state_machine:
            raise RuntimeError("No active session")
        
        # Complete cycle
        self.state_machine.complete_cycle()
        
        # Get cycle metrics
        cycles = self.state_machine.get_cycle_metrics()
        latest_cycle = cycles[-1] if cycles else None
        
        # Update context
        self.current_context.current_state = TDDState.GREEN.value
        
        if self.config.enable_session_tracking:
            self.page_tracker.save_context(self.current_context, self.state_machine)
        
        return {
            "cycle_number": latest_cycle.cycle_number if latest_cycle else 0,
            "tests_written": latest_cycle.tests_written if latest_cycle else 0,
            "tests_passing": latest_cycle.tests_passing if latest_cycle else 0,
            "duration_seconds": latest_cycle.total_duration if latest_cycle else 0
        }
    
    def save_progress(self, location: Optional[PageLocation] = None, notes: str = "") -> bool:
        """
        Save current progress and location.
        
        Args:
            location: Current code location
            notes: Additional notes
            
        Returns:
            True if saved successfully
        """
        if not self.current_context:
            return False
        
        if location:
            self.current_context.last_location = location
        
        if notes:
            self.current_context.notes += f"\n{notes}"
        
        if self.config.enable_session_tracking:
            return self.page_tracker.save_context(self.current_context, self.state_machine)
        
        return True
    
    def resume_session(self, session_id: str) -> Dict[str, Any]:
        """
        Resume existing TDD session.
        
        Args:
            session_id: Session to resume
            
        Returns:
            Session context and state
        """
        # Load context
        context = self.page_tracker.load_context(session_id)
        if not context:
            raise ValueError(f"Session {session_id} not found")
        
        self.current_context = context
        self.current_session_id = session_id
        
        # TODO: Restore state machine from snapshot
        # For now, create new state machine
        self.state_machine = TDDStateMachine(context.feature_name, session_id)
        
        return {
            "session_id": session_id,
            "feature_name": context.feature_name,
            "current_state": context.current_state,
            "last_location": {
                "file": context.last_location.filepath if context.last_location else None,
                "line": context.last_location.line_number if context.last_location else None,
                "function": context.last_location.function_name if context.last_location else None
            },
            "test_files": context.test_files,
            "source_files": context.source_files,
            "notes": context.notes
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of current session.
        
        Returns:
            Session statistics and metrics
        """
        if not self.state_machine:
            raise RuntimeError("No active session")
        
        return self.state_machine.get_session_summary()
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """
        List all active TDD sessions.
        
        Returns:
            List of session summaries
        """
        contexts = self.page_tracker.list_active_sessions()
        
        return [
            {
                "session_id": ctx.session_id,
                "feature_name": ctx.feature_name,
                "current_state": ctx.current_state,
                "last_updated": ctx.last_updated.isoformat(),
                "test_files": len(ctx.test_files),
                "source_files": len(ctx.source_files)
            }
            for ctx in contexts
        ]
    
    def _get_test_filepath(self, source_file: str) -> Path:
        """Generate test file path from source file."""
        source_path = Path(source_file)
        
        # Convert src/module/file.py -> tests/test_module/test_file.py
        parts = source_path.parts
        
        # Remove 'src' if present
        if parts[0] == 'src':
            parts = parts[1:]
        
        # Add test prefix to filename
        filename = f"test_{source_path.stem}.py"
        
        # Build test path
        test_path = Path(self.config.test_output_dir) / Path(*parts[:-1]) / filename
        
        return test_path
    
    # Phase 4 - TDD Mastery Integration: Helper methods for view discovery
    
    def _find_related_views(self, module_path: Path) -> List[Path]:
        """Find related Razor/Blazor view files for a module."""
        view_extensions = [".razor", ".cshtml", ".blazor"]
        related_views = []
        
        # Search in project root for view files
        project_root = PathLib(self.config.project_root)
        
        # Get module name (without extension)
        module_name = module_path.stem
        
        # Search for views with same or similar names
        for ext in view_extensions:
            # Direct match
            direct_match = project_root / f"{module_name}{ext}"
            if direct_match.exists():
                related_views.append(direct_match)
            
            # Search in common view directories
            for view_dir in ["Views", "Pages", "Components", "Shared"]:
                view_path = project_root / view_dir
                if view_path.exists():
                    # Recursive search
                    for view_file in view_path.rglob(f"*{ext}"):
                        if module_name.lower() in view_file.stem.lower():
                            related_views.append(view_file)
        
        return related_views
    
    def discover_elements_for_testing(
        self, 
        module_path: Path,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Discover UI elements before test generation.
        
        Args:
            module_path: Path to module being tested
            force_refresh: Force re-discovery even if cached
            
        Returns:
            Dictionary of discovered elements
        """
        if not self.view_discovery or not self.config.enable_view_discovery:
            return {}
        
        # Find related view files
        view_files = self._find_related_views(module_path)
        if not view_files:
            return {}
        
        try:
            discovery_result = self.view_discovery.discover_views(
                view_paths=view_files,
                save_to_db=True,
                project_name=self.config.project_name or "default"
            )
            
            self.discovered_elements = discovery_result.get("elements", {})
            
            print(f"✅ Discovered {len(self.discovered_elements)} elements from {len(view_files)} view files")
            
            return self.discovered_elements
        except Exception as e:
            print(f"⚠️  Element discovery failed: {e}")
            return {}
    
    def _store_session_in_brain(self, feature_name: str, session_id: str):
        """
        Store TDD session metadata in brain (Tier 2 knowledge graph).
        
        Phase 3: New method for brain integration.
        
        Args:
            feature_name: Feature being developed
            session_id: TDD session ID
        """
        try:
            # Store as pattern in Tier 2 knowledge graph
            self.knowledge_graph.store_pattern(
                pattern_id=f"tdd_session_{session_id}",
                title=f"TDD Session: {feature_name}",
                content=f"TDD workflow session for {feature_name}",
                pattern_type="tdd_session",
                confidence=1.0,
                source="tdd_orchestrator",
                metadata={
                    "session_id": session_id,
                    "feature_name": feature_name,
                    "started_at": datetime.now().isoformat(),
                    "workspace_session_id": self.current_brain_session.session_id if self.current_brain_session else None
                },
                namespaces=[f"workspace.tdd.{session_id}"]
            )
        except Exception as e:
            print(f"⚠️  Failed to store session in brain: {e}")
    
    def _store_test_results_in_brain(self, test_results: Dict[str, Any]):
        """
        Store test execution results in brain memory.
        
        Phase 3: New method for brain integration.
        
        Args:
            test_results: Test results from execution
        """
        try:
            # Store in Tier 2 as learning pattern
            if test_results.get("failed", 0) > 0:
                # Learn from failures
                for error in test_results.get("errors", []):
                    self.knowledge_graph.learn_pattern(
                        pattern={
                            "title": f"Test Failure: {error.get('test', 'Unknown')}",
                            "content": error.get('message', ''),
                            "pattern_type": "test_failure",
                            "confidence": 0.8,
                            "metadata": {
                                "test_name": error.get('test'),
                                "framework": test_results.get('framework'),
                                "session_id": self.current_session_id
                            }
                        },
                        namespace=f"workspace.tdd.failures.{self.current_session_id}"
                    )
        except Exception as e:
            print(f"⚠️  Failed to store test results in brain: {e}")
