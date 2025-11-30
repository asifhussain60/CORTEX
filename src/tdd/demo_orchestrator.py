"""
Demo Orchestrator
Coordinates complete TDD demonstrations (RED→GREEN→REFACTOR).

Shows TDD workflow in action with minimal narration.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time
import json

from .demo_engine import TDDDemoEngine, DemoScenario, DemoPhase
from .code_runner import CodeRunner, ExecutionResult
from .refactoring_advisor import RefactoringAdvisor, CodeSmell, RefactoringSuggestion


class DemoStatus(Enum):
    """Status of demo session."""
    NOT_STARTED = "not_started"
    RED_PHASE = "red_phase"
    GREEN_PHASE = "green_phase"
    REFACTOR_PHASE = "refactor_phase"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PhaseResult:
    """
    Result of executing a demo phase.
    
    Attributes:
        phase: Phase that was executed
        success: Whether phase completed successfully
        execution_time: Time taken in seconds
        output: Execution output
        test_results: Test results (if applicable)
    """
    phase: DemoPhase
    success: bool
    execution_time: float
    output: str
    test_results: Optional[Dict] = None


@dataclass
class DemoSession:
    """
    Complete TDD demonstration session.
    
    Tracks workflow through RED→GREEN→REFACTOR cycle.
    """
    session_id: str
    scenario_id: str
    scenario_name: str
    status: DemoStatus
    started_at: datetime
    completed_at: Optional[datetime]
    
    # Phase results
    red_result: Optional[PhaseResult]
    green_result: Optional[PhaseResult]
    refactor_result: Optional[PhaseResult]
    
    # Summary
    total_time: float
    phases_completed: int


class DemoOrchestrator:
    """
    Orchestrates complete TDD demonstrations.
    
    Features:
    - RED→GREEN→REFACTOR workflow coordination
    - Live code execution with test results
    - Timing and metrics collection
    - Demo state persistence
    
    REMOVED (from original educational plan):
    - Learning annotations
    - Educational explanations
    - Tutorial aspects
    
    FOCUS:
    - Workflow coordination
    - Demonstration execution
    - Minimal narration (code demonstrates itself)
    """
    
    def __init__(self, 
                 demo_engine: Optional[TDDDemoEngine] = None,
                 code_runner: Optional[CodeRunner] = None,
                 refactoring_advisor: Optional[RefactoringAdvisor] = None):
        """
        Initialize Demo Orchestrator.
        
        Args:
            demo_engine: TDD demo engine (creates new if None)
            code_runner: Code execution engine (creates new if None)
            refactoring_advisor: Refactoring advisor (creates new if None)
        """
        self.demo_engine = demo_engine or TDDDemoEngine()
        self.code_runner = code_runner or CodeRunner()
        self.refactoring_advisor = refactoring_advisor or RefactoringAdvisor()
        
        # Active sessions
        self.sessions: Dict[str, DemoSession] = {}
    
    def list_scenarios(self) -> List[Dict]:
        """
        List available demo scenarios.
        
        Returns:
            List of scenario info dictionaries
        """
        scenarios = self.demo_engine.list_scenarios()
        return [
            {
                'id': s.id,
                'name': s.name,
                'description': s.description,
                'category': s.category,
                'estimated_time': s.estimated_time
            }
            for s in scenarios
        ]
    
    def start_demo(self, scenario_id: str) -> Optional[str]:
        """
        Start a new demo session.
        
        Args:
            scenario_id: ID of scenario to demonstrate
        
        Returns:
            Session ID if successful, None if scenario not found
        """
        # Get scenario
        scenario = self.demo_engine.get_scenario(scenario_id)
        if not scenario:
            return None
        
        # Create session in demo engine
        session_id = self.demo_engine.create_demo_session(scenario_id)
        if not session_id:
            return None
        
        # Create session object
        session = DemoSession(
            session_id=session_id,
            scenario_id=scenario_id,
            scenario_name=scenario.name,
            status=DemoStatus.NOT_STARTED,
            started_at=datetime.now(),
            completed_at=None,
            red_result=None,
            green_result=None,
            refactor_result=None,
            total_time=0.0,
            phases_completed=0
        )
        
        self.sessions[session_id] = session
        
        return session_id
    
    def run_complete_demo(self, session_id: str) -> DemoSession:
        """
        Run complete RED→GREEN→REFACTOR demo workflow.
        
        Args:
            session_id: Demo session identifier
        
        Returns:
            Completed DemoSession with all results
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        start_time = time.time()
        
        try:
            # Phase 1: RED - Write failing test
            print("\n" + "="*60)
            print("PHASE 1: RED - Write Failing Test")
            print("="*60)
            session.red_result = self._run_red_phase(session_id)
            session.status = DemoStatus.RED_PHASE
            session.phases_completed += 1
            
            # Phase 2: GREEN - Minimal implementation
            print("\n" + "="*60)
            print("PHASE 2: GREEN - Minimal Implementation")
            print("="*60)
            session.green_result = self._run_green_phase(session_id)
            session.status = DemoStatus.GREEN_PHASE
            session.phases_completed += 1
            
            # Phase 3: REFACTOR - Improve code
            print("\n" + "="*60)
            print("PHASE 3: REFACTOR - Improve Code")
            print("="*60)
            session.refactor_result = self._run_refactor_phase(session_id)
            session.status = DemoStatus.REFACTOR_PHASE
            session.phases_completed += 1
            
            # Complete session
            session.status = DemoStatus.COMPLETED
            session.completed_at = datetime.now()
            session.total_time = time.time() - start_time
            
            # Update demo engine
            self.demo_engine.complete_session(session_id)
            
            return session
        
        except Exception as e:
            session.status = DemoStatus.FAILED
            session.completed_at = datetime.now()
            session.total_time = time.time() - start_time
            print(f"\n❌ Demo failed: {e}")
            return session
    
    def _run_red_phase(self, session_id: str) -> PhaseResult:
        """
        Execute RED phase - write failing test.
        
        Args:
            session_id: Demo session identifier
        
        Returns:
            PhaseResult with test execution results
        """
        session = self.sessions[session_id]
        scenario = self.demo_engine.get_scenario(session.scenario_id)
        
        # Get RED phase code (test)
        test_code = self.demo_engine.get_phase_code(
            session.scenario_id,
            DemoPhase.RED
        )
        
        print("\n📝 Test Code:")
        print(test_code)
        
        # Run test (should fail)
        start_time = time.time()
        result = self.code_runner.run_tests(test_code)
        execution_time = time.time() - start_time
        
        # Display results
        print("\n" + self.code_runner.format_output(result))
        
        # Record execution
        self.demo_engine.record_execution(
            session_id,
            DemoPhase.RED,
            result.success,
            result.execution_time,
            result.output
        )
        
        # Update session phase
        self.demo_engine.update_session_phase(session_id, DemoPhase.RED)
        
        return PhaseResult(
            phase=DemoPhase.RED,
            success=not result.success,  # Test SHOULD fail in RED phase
            execution_time=execution_time,
            output=result.output,
            test_results=result.test_results
        )
    
    def _run_green_phase(self, session_id: str) -> PhaseResult:
        """
        Execute GREEN phase - minimal implementation.
        
        Args:
            session_id: Demo session identifier
        
        Returns:
            PhaseResult with test execution results
        """
        session = self.sessions[session_id]
        scenario = self.demo_engine.get_scenario(session.scenario_id)
        
        # Get GREEN phase code (implementation)
        impl_code = self.demo_engine.get_phase_code(
            session.scenario_id,
            DemoPhase.GREEN
        )
        
        print("\n💚 Implementation Code:")
        print(impl_code)
        
        # Get test code
        test_code = self.demo_engine.get_phase_code(
            session.scenario_id,
            DemoPhase.RED
        )
        
        # Run tests with implementation (should pass)
        start_time = time.time()
        result = self.code_runner.run_tests(test_code, impl_code)
        execution_time = time.time() - start_time
        
        # Display results
        print("\n" + self.code_runner.format_output(result))
        
        # Record execution
        self.demo_engine.record_execution(
            session_id,
            DemoPhase.GREEN,
            result.success,
            result.execution_time,
            result.output
        )
        
        # Update session phase
        self.demo_engine.update_session_phase(session_id, DemoPhase.GREEN)
        
        return PhaseResult(
            phase=DemoPhase.GREEN,
            success=result.success,  # Tests SHOULD pass in GREEN phase
            execution_time=execution_time,
            output=result.output,
            test_results=result.test_results
        )
    
    def _run_refactor_phase(self, session_id: str) -> PhaseResult:
        """
        Execute REFACTOR phase - improve code while keeping tests green.
        
        Args:
            session_id: Demo session identifier
        
        Returns:
            PhaseResult with refactoring results
        """
        session = self.sessions[session_id]
        scenario = self.demo_engine.get_scenario(session.scenario_id)
        
        # Get REFACTOR phase code
        refactored_code = self.demo_engine.get_phase_code(
            session.scenario_id,
            DemoPhase.REFACTOR
        )
        
        # Analyze for code smells
        green_code = self.demo_engine.get_phase_code(
            session.scenario_id,
            DemoPhase.GREEN
        )
        
        print("\n🔍 Analyzing GREEN implementation for improvement opportunities...")
        smells = self.refactoring_advisor.analyze_code(green_code)
        
        if smells:
            print(f"\n⚠️  Found {len(smells)} improvement opportunities:")
            for i, smell in enumerate(smells[:3], 1):  # Show top 3
                print(f"\n{i}. {smell.description}")
                print(f"   Priority: {smell.priority.value}")
                print(f"   Confidence: {smell.confidence:.0%}")
        
        print("\n♻️  Refactored Code:")
        print(refactored_code)
        
        # Get test code
        test_code = self.demo_engine.get_phase_code(
            session.scenario_id,
            DemoPhase.RED
        )
        
        # Run tests with refactored code (should still pass)
        start_time = time.time()
        result = self.code_runner.run_tests(test_code, refactored_code)
        execution_time = time.time() - start_time
        
        # Display results
        print("\n" + self.code_runner.format_output(result))
        
        if result.success:
            print("\n✅ Refactoring successful - all tests still pass!")
        else:
            print("\n⚠️  Refactoring broke tests - would need to fix")
        
        # Record execution
        self.demo_engine.record_execution(
            session_id,
            DemoPhase.REFACTOR,
            result.success,
            result.execution_time,
            result.output
        )
        
        # Update session phase
        self.demo_engine.update_session_phase(session_id, DemoPhase.REFACTOR)
        
        return PhaseResult(
            phase=DemoPhase.REFACTOR,
            success=result.success,  # Tests should still pass after refactoring
            execution_time=execution_time,
            output=result.output,
            test_results=result.test_results
        )
    
    def get_session(self, session_id: str) -> Optional[DemoSession]:
        """
        Get demo session by ID.
        
        Args:
            session_id: Session identifier
        
        Returns:
            DemoSession if found, None otherwise
        """
        return self.sessions.get(session_id)
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """
        Get summary of demo session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Summary dictionary with key metrics
        """
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        return {
            'session_id': session.session_id,
            'scenario': session.scenario_name,
            'status': session.status.value,
            'started_at': session.started_at.isoformat(),
            'completed_at': session.completed_at.isoformat() if session.completed_at else None,
            'total_time': f"{session.total_time:.2f}s",
            'phases_completed': session.phases_completed,
            'red_phase': {
                'success': session.red_result.success if session.red_result else None,
                'time': f"{session.red_result.execution_time:.2f}s" if session.red_result else None
            } if session.red_result else None,
            'green_phase': {
                'success': session.green_result.success if session.green_result else None,
                'time': f"{session.green_result.execution_time:.2f}s" if session.green_result else None
            } if session.green_result else None,
            'refactor_phase': {
                'success': session.refactor_result.success if session.refactor_result else None,
                'time': f"{session.refactor_result.execution_time:.2f}s" if session.refactor_result else None
            } if session.refactor_result else None
        }
    
    def cleanup(self) -> None:
        """Clean up temporary resources."""
        self.code_runner.cleanup()
