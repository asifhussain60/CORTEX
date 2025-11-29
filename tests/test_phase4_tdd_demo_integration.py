"""
Integration Tests for Phase 4: TDD Demo System

Tests demonstration capabilities (not educational features).
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.tdd import (
    TDDDemoEngine,
    DemoPhase,
    CodeRunner,
    RefactoringAdvisor,
    DemoOrchestrator,
    DemoSession
)


class TestTDDDemoEngine:
    """Test TDD Demo Engine."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="cortex_test_"))
        self.db_path = self.temp_dir / "test.db"
        self.demo_workspace = self.temp_dir / "workspace"
        
        self.engine = TDDDemoEngine(
            db_path=self.db_path,
            demo_workspace=self.demo_workspace
        )
    
    def teardown_method(self):
        """Cleanup test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_engine_initialization(self):
        """Test engine initializes with scenarios."""
        assert len(self.engine.scenarios) >= 3
        assert 'auth_jwt' in self.engine.scenarios
        assert 'payment_stripe' in self.engine.scenarios
        assert 'api_crud' in self.engine.scenarios
    
    def test_get_scenario(self):
        """Test retrieving scenario by ID."""
        scenario = self.engine.get_scenario('auth_jwt')
        assert scenario is not None
        assert scenario.id == 'auth_jwt'
        assert scenario.name == 'JWT Authentication'
        assert scenario.category == 'auth'
    
    def test_list_scenarios(self):
        """Test listing all scenarios."""
        scenarios = self.engine.list_scenarios()
        assert len(scenarios) >= 3
        
        names = [s.name for s in scenarios]
        assert 'JWT Authentication' in names
        assert 'Stripe Payment Processing' in names
    
    def test_create_demo_session(self):
        """Test creating demo session."""
        session_id = self.engine.create_demo_session('auth_jwt')
        assert session_id is not None
        assert 'demo_' in session_id
        assert 'auth_jwt' in session_id
    
    def test_get_phase_code(self):
        """Test retrieving code for each phase."""
        # RED phase (test)
        red_code = self.engine.get_phase_code('auth_jwt', DemoPhase.RED)
        assert red_code is not None
        assert 'def test_' in red_code
        assert 'assert' in red_code
        
        # GREEN phase (implementation)
        green_code = self.engine.get_phase_code('auth_jwt', DemoPhase.GREEN)
        assert green_code is not None
        assert 'class ' in green_code
        assert 'def ' in green_code
        
        # REFACTOR phase (improved)
        refactor_code = self.engine.get_phase_code('auth_jwt', DemoPhase.REFACTOR)
        assert refactor_code is not None
        assert 'class ' in refactor_code


class TestCodeRunner:
    """Test Code Runner."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="cortex_test_"))
        self.runner = CodeRunner(workspace=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test fixtures."""
        self.runner.cleanup()
    
    def test_validate_syntax_valid(self):
        """Test syntax validation with valid code."""
        code = "def hello(): return 'world'"
        error = self.runner.validate_syntax(code)
        assert error is None
    
    def test_validate_syntax_invalid(self):
        """Test syntax validation with invalid code."""
        code = "def hello( return 'world'"
        error = self.runner.validate_syntax(code)
        assert error is not None
        assert 'Syntax error' in error
    
    def test_execute_code_success(self):
        """Test executing valid Python code."""
        code = "print('Hello, World!')"
        result = self.runner.execute_code(code)
        
        assert result.success is True
        assert 'Hello, World!' in result.output
        assert result.execution_time > 0
    
    def test_execute_code_failure(self):
        """Test executing code with runtime error."""
        code = "raise ValueError('Test error')"
        result = self.runner.execute_code(code)
        
        assert result.success is False
        assert result.error is not None
        assert 'ValueError' in result.error
    
    def test_format_output(self):
        """Test output formatting."""
        from src.tdd.code_runner import ExecutionResult
        
        result = ExecutionResult(
            success=True,
            output="Test output",
            execution_time=0.123
        )
        
        formatted = self.runner.format_output(result)
        assert '✅ SUCCESS' in formatted
        assert 'Test output' in formatted
        assert '0.123s' in formatted


class TestRefactoringAdvisor:
    """Test Refactoring Advisor."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.advisor = RefactoringAdvisor()
    
    def test_analyze_code_finds_smells(self):
        """Test code analysis finds smells."""
        # Long method code
        code = '''
def long_method():
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    line7 = 7
    line8 = 8
    line9 = 9
    line10 = 10
    line11 = 11
    line12 = 12
    line13 = 13
    line14 = 14
    line15 = 15
    line16 = 16
    line17 = 17
    line18 = 18
    line19 = 19
    line20 = 20
    line21 = 21
    line22 = 22
    line23 = 23
    line24 = 24
    line25 = 25
    line26 = 26
    line27 = 27
    line28 = 28
    line29 = 29
    line30 = 30
    line31 = 31
    line32 = 32
'''
        
        smells = self.advisor.analyze_code(code)
        assert len(smells) > 0
        
        # Should find long method
        smell_types = [s.smell_type for s in smells]
        assert 'long_method' in smell_types
    
    def test_generate_diff(self):
        """Test diff generation."""
        before = "def old(): pass"
        after = "def new(): pass"
        
        diff = self.advisor.generate_diff(before, after)
        assert diff is not None
        assert 'old' in diff
        assert 'new' in diff


class TestDemoOrchestrator:
    """Test Demo Orchestrator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="cortex_test_"))
        
        # Create components
        self.engine = TDDDemoEngine(
            db_path=self.temp_dir / "test.db",
            demo_workspace=self.temp_dir / "workspace"
        )
        self.runner = CodeRunner(workspace=self.temp_dir / "runner")
        self.advisor = RefactoringAdvisor()
        
        # Create orchestrator
        self.orchestrator = DemoOrchestrator(
            demo_engine=self.engine,
            code_runner=self.runner,
            refactoring_advisor=self.advisor
        )
    
    def teardown_method(self):
        """Cleanup test fixtures."""
        self.orchestrator.cleanup()
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_list_scenarios(self):
        """Test listing available scenarios."""
        scenarios = self.orchestrator.list_scenarios()
        assert len(scenarios) >= 3
        
        # Check structure
        assert 'id' in scenarios[0]
        assert 'name' in scenarios[0]
        assert 'category' in scenarios[0]
    
    def test_start_demo(self):
        """Test starting demo session."""
        session_id = self.orchestrator.start_demo('auth_jwt')
        assert session_id is not None
        
        session = self.orchestrator.get_session(session_id)
        assert session is not None
        assert session.scenario_id == 'auth_jwt'
        assert session.phases_completed == 0
    
    def test_get_session_summary(self):
        """Test getting session summary."""
        session_id = self.orchestrator.start_demo('auth_jwt')
        summary = self.orchestrator.get_session_summary(session_id)
        
        assert summary is not None
        assert summary['session_id'] == session_id
        assert summary['scenario'] == 'JWT Authentication'
        assert summary['phases_completed'] == 0


class TestEndToEndDemo:
    """End-to-end demo workflow tests."""
    
    @pytest.mark.slow
    def test_complete_auth_demo(self):
        """Test complete auth demo workflow (RED-GREEN-REFACTOR)."""
        # This test takes longer due to actual code execution
        temp_dir = Path(tempfile.mkdtemp(prefix="cortex_test_"))
        
        try:
            orchestrator = DemoOrchestrator()
            session_id = orchestrator.start_demo('auth_jwt')
            
            # Note: Full demo requires pytest and dependencies
            # This test validates structure, not execution
            assert session_id is not None
            
            session = orchestrator.get_session(session_id)
            assert session is not None
            assert session.scenario_name == 'JWT Authentication'
            
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
