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

# Phase 1 imports
from cortex_agents.test_generator.generators.function_test_generator import FunctionTestGenerator
from cortex_agents.test_generator.templates import TemplateManager
from cortex_agents.test_generator.edge_case_analyzer import EdgeCaseAnalyzer
from cortex_agents.test_generator.domain_knowledge_integrator import DomainKnowledgeIntegrator
from cortex_agents.test_generator.error_condition_generator import ErrorConditionGenerator
from cortex_agents.test_generator.parametrized_test_generator import ParametrizedTestGenerator

# Phase 2 imports
from workflows.tdd_state_machine import TDDStateMachine, TDDState
from workflows.refactoring_intelligence import CodeSmellDetector, RefactoringEngine, CodeSmell
from workflows.page_tracking import PageTracker, TDDContext, PageLocation

# Phase 3 - M3.2: Performance optimization imports
from workflows.ast_cache import ASTCache, get_ast_cache
from workflows.pattern_cache import PatternCache, get_pattern_cache
from workflows.smell_cache import SmellCache, get_smell_cache
from workflows.batch_processor import BatchTestGenerator, BatchSmellDetector

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
    session_storage: str = "cortex-brain/tier1/tdd_sessions.db"
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
        self.page_tracker = PageTracker(config.session_storage)
        
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
    
    def start_session(self, feature_name: str, session_id: Optional[str] = None) -> str:
        """
        Start new TDD session.
        
        Args:
            feature_name: Name of feature being developed
            session_id: Optional explicit session ID
            
        Returns:
            Session ID for tracking
        """
        import uuid
        
        # Generate session ID
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
        
        # Save to tracker
        if self.config.enable_session_tracking:
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
        Verify tests pass (GREEN phase).
        
        Args:
            test_results: Results from test execution
            
        Returns:
            True if all tests pass
        """
        if not self.state_machine:
            raise RuntimeError("No active session")
        
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
        
        return tests_passing > 0
    
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
