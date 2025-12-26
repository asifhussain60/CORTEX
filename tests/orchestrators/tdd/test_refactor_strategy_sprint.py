"""
TDD Orchestrator v4 - REFACTOR Strategy Coverage Sprint

Target: Increase refactor_phase_strategy.py from 17.30% → 70%
Focus: 40 new tests covering critical uncovered paths

Author: CORTEX Test Suite
Created: December 23, 2025
Sprint: Week 2 - Orchestration Layer Testing
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
from datetime import datetime

from src.orchestrators.tdd.strategies.refactor_phase_strategy import REFACTORPhaseStrategy
from src.orchestrators.tdd.tdd_orchestrator import ValidationResult, PhaseResult


@pytest.fixture
def mock_dependencies():
    """Create mocked dependencies for REFACTOR strategy."""
    return {
        'mcp_gateway': AsyncMock(),
        'brain_connector': AsyncMock(),
        'knowledge_graph': AsyncMock(),
        'clean_code_enforcer': AsyncMock(),
        'tech_discovery': AsyncMock()
    }


@pytest.fixture
def refactor_strategy(mock_dependencies):
    """Create REFACTOR strategy with mocked dependencies."""
    return REFACTORPhaseStrategy(
        mcp_gateway=mock_dependencies['mcp_gateway'],
        brain_connector=mock_dependencies['brain_connector'],
        knowledge_graph=mock_dependencies['knowledge_graph'],
        clean_code_enforcer=mock_dependencies['clean_code_enforcer'],
        tech_discovery=mock_dependencies['tech_discovery']
    )


@pytest.fixture
def valid_refactor_context(tmp_path):
    """Create valid REFACTOR context."""
    impl_file = tmp_path / "calculator.py"
    impl_file.write_text("def add(a, b):\n    return a + b")
    
    test_file = tmp_path / "test_calculator.py"
    test_file.write_text("def test_add():\n    assert add(2, 3) == 5")
    
    return {
        'feature_name': 'Calculator',
        'implementation_file': str(impl_file),
        'test_file': str(test_file),
        'tests_passing': 5,
        'tests_failing': 0,
        'baseline_tests_passing': 5,
        'tech_profile': Mock(language='Python', frameworks=['pytest'])
    }


# ============================================================================
# Test Group 1: DoR Validation (10 tests)
# ============================================================================

class TestREFACTORDoRValidation:
    """Test REFACTOR Definition of Ready validation."""
    
    @pytest.mark.asyncio
    async def test_dor_pass_all_requirements(self, refactor_strategy, valid_refactor_context):
        """Test DoR passes when all requirements met."""
        result = await refactor_strategy.validate_dor(valid_refactor_context)
        
        assert result.passed is True
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_dor_fail_missing_implementation_file(self, refactor_strategy):
        """Test DoR fails when implementation file not specified."""
        context = {'tests_passing': 5, 'tests_failing': 0}
        result = await refactor_strategy.validate_dor(context)
        
        assert result.passed is False
        assert any('Implementation file not specified' in e for e in result.errors)
    
    @pytest.mark.asyncio
    async def test_dor_fail_implementation_file_not_exists(self, refactor_strategy):
        """Test DoR fails when implementation file doesn't exist."""
        context = {
            'implementation_file': '/nonexistent/file.py',
            'tests_passing': 5,
            'tests_failing': 0,
            'test_file': '/tmp/test.py'
        }
        result = await refactor_strategy.validate_dor(context)
        
        assert result.passed is False
        assert any('does not exist' in e for e in result.errors)
    
    @pytest.mark.asyncio
    async def test_dor_fail_no_tests_passing(self, refactor_strategy, tmp_path):
        """Test DoR fails when no tests passing."""
        impl_file = tmp_path / "code.py"
        impl_file.write_text("pass")
        
        context = {
            'implementation_file': str(impl_file),
            'tests_passing': 0,
            'tests_failing': 0,
            'test_file': str(tmp_path / "test.py")
        }
        result = await refactor_strategy.validate_dor(context)
        
        assert result.passed is False
        assert any('No tests passing' in e for e in result.errors)
    
    @pytest.mark.asyncio
    async def test_dor_warning_tests_failing(self, refactor_strategy, valid_refactor_context):
        """Test DoR warns when tests failing."""
        valid_refactor_context['tests_failing'] = 2
        result = await refactor_strategy.validate_dor(valid_refactor_context)
        
        assert len(result.warnings) > 0
        assert any('tests failing' in w for w in result.warnings)
    
    @pytest.mark.asyncio
    async def test_dor_fail_missing_test_file(self, refactor_strategy, tmp_path):
        """Test DoR fails when test file missing."""
        impl_file = tmp_path / "code.py"
        impl_file.write_text("pass")
        
        context = {
            'implementation_file': str(impl_file),
            'tests_passing': 5,
            'tests_failing': 0,
            'test_file': '/nonexistent/test.py'
        }
        result = await refactor_strategy.validate_dor(context)
        
        assert result.passed is False
        assert any('Test file not found' in e for e in result.errors)
    
    @pytest.mark.asyncio
    async def test_dor_logging_pass(self, refactor_strategy, valid_refactor_context, caplog):
        """Test DoR logs PASS when validation succeeds."""
        await refactor_strategy.validate_dor(valid_refactor_context)
        assert '✅ PASS' in caplog.text
    
    @pytest.mark.asyncio
    async def test_dor_logging_fail(self, refactor_strategy, caplog):
        """Test DoR logs FAIL when validation fails."""
        await refactor_strategy.validate_dor({})
        assert '❌ FAIL' in caplog.text
    
    @pytest.mark.asyncio
    async def test_dor_multiple_errors(self, refactor_strategy):
        """Test DoR accumulates multiple errors."""
        context = {
            'tests_passing': 0,
            'tests_failing': 5
        }
        result = await refactor_strategy.validate_dor(context)
        
        assert result.passed is False
        assert len(result.errors) >= 2  # Implementation file + no tests passing
    
    @pytest.mark.asyncio
    async def test_dor_edge_case_empty_context(self, refactor_strategy):
        """Test DoR handles empty context gracefully."""
        result = await refactor_strategy.validate_dor({})
        
        assert result.passed is False
        assert len(result.errors) > 0


# ============================================================================
# Test Group 2: Code Smell Detection (8 tests)
# ============================================================================

class TestCodeSmellDetection:
    """Test code smell detection logic."""
    
    @pytest.mark.asyncio
    async def test_detect_code_smells_god_method(self, refactor_strategy, tmp_path):
        """Test detection of god methods (>50 lines)."""
        impl_file = tmp_path / "god_method.py"
        impl_file.write_text("\n".join([f"    line{i}" for i in range(60)]))
        
        baseline = {'violations': [{'type': 'function_length', 'lines': 60}]}
        smells = await refactor_strategy._detect_code_smells(str(impl_file), baseline)
        
        assert len(smells) > 0
        assert any(s['type'] == 'function_length' for s in smells)
    
    @pytest.mark.asyncio
    async def test_detect_code_smells_high_complexity(self, refactor_strategy, tmp_path):
        """Test detection of high cyclomatic complexity."""
        impl_file = tmp_path / "complex.py"
        impl_file.write_text("def complex():\n    if x and y or z:\n        pass")
        
        baseline = {'violations': [{'type': 'complexity', 'score': 15}]}
        smells = await refactor_strategy._detect_code_smells(str(impl_file), baseline)
        
        assert len(smells) > 0
        assert any(s['type'] == 'complexity' for s in smells)
    
    @pytest.mark.asyncio
    async def test_detect_code_smells_duplicates(self, refactor_strategy, tmp_path):
        """Test detection of duplicate code blocks."""
        impl_file = tmp_path / "duplicates.py"
        code = "def a():\n    return 1\ndef b():\n    return 1"
        impl_file.write_text(code)
        
        baseline = {'violations': [{'type': 'duplication', 'lines': [1, 3]}]}
        smells = await refactor_strategy._detect_code_smells(str(impl_file), baseline)
        
        assert len(smells) > 0
        assert any(s['type'] == 'duplication' for s in smells)
    
    @pytest.mark.asyncio
    async def test_detect_code_smells_poor_naming(self, refactor_strategy, tmp_path):
        """Test detection of poor naming conventions."""
        impl_file = tmp_path / "naming.py"
        impl_file.write_text("def x():\n    a = 1\n    return a")
        
        baseline = {'violations': [{'type': 'naming', 'names': ['x', 'a']}]}
        smells = await refactor_strategy._detect_code_smells(str(impl_file), baseline)
        
        assert len(smells) > 0
        assert any(s['type'] == 'naming' for s in smells)
    
    @pytest.mark.asyncio
    async def test_detect_code_smells_empty_baseline(self, refactor_strategy, tmp_path):
        """Test code smell detection with empty baseline."""
        impl_file = tmp_path / "clean.py"
        impl_file.write_text("def add(a, b):\n    return a + b")
        
        baseline = {'violations': []}
        smells = await refactor_strategy._detect_code_smells(str(impl_file), baseline)
        
        assert len(smells) == 0
    
    @pytest.mark.asyncio
    async def test_detect_code_smells_god_object(self, refactor_strategy, tmp_path):
        """Test detection of god objects (>10 methods)."""
        impl_file = tmp_path / "god_object.py"
        methods = "\n".join([f"    def method{i}(self): pass" for i in range(15)])
        impl_file.write_text(f"class God:\n{methods}")
        
        baseline = {'violations': [{'type': 'god_object', 'methods': 15}]}
        smells = await refactor_strategy._detect_code_smells(str(impl_file), baseline)
        
        assert len(smells) > 0
        assert any(s['type'] == 'god_object' for s in smells)
    
    @pytest.mark.asyncio
    async def test_detect_code_smells_prioritization(self, refactor_strategy, tmp_path):
        """Test code smells are prioritized by severity."""
        impl_file = tmp_path / "mixed.py"
        impl_file.write_text("def x():\n    " + "\n    ".join([f"line{i}" for i in range(60)]))
        
        baseline = {
            'violations': [
                {'type': 'function_length', 'lines': 60, 'severity': 'high'},
                {'type': 'naming', 'names': ['x'], 'severity': 'low'}
            ]
        }
        smells = await refactor_strategy._detect_code_smells(str(impl_file), baseline)
        
        assert smells[0]['severity'] == 'high'
    
    @pytest.mark.asyncio
    async def test_detect_code_smells_caching(self, refactor_strategy, tmp_path):
        """Test code smell detection results are cached."""
        impl_file = tmp_path / "cached.py"
        impl_file.write_text("def add(a, b): return a + b")
        
        baseline = {'violations': [{'type': 'test', 'id': 1}]}
        
        # First call
        smells1 = await refactor_strategy._detect_code_smells(str(impl_file), baseline)
        # Second call (should use cache)
        smells2 = await refactor_strategy._detect_code_smells(str(impl_file), baseline)
        
        assert smells1 == smells2


# ============================================================================
# Test Group 3: Refactoring Suggestions (7 tests)
# ============================================================================

class TestRefactoringSuggestions:
    """Test AI-driven refactoring suggestion generation."""
    
    @pytest.mark.asyncio
    async def test_generate_refactoring_extract_method(self, refactor_strategy, tmp_path):
        """Test suggestion to extract method from long function."""
        impl_file = tmp_path / "long.py"
        impl_file.write_text("\n".join([f"    line{i}" for i in range(60)]))
        
        code_smells = [{'type': 'function_length', 'lines': 60}]
        best_practices = ['Extract method for code blocks >20 lines']
        
        suggestions = await refactor_strategy._generate_refactoring_suggestions(
            str(impl_file), code_smells, best_practices
        )
        
        assert len(suggestions) > 0
        assert any('extract' in s['type'].lower() for s in suggestions)
    
    @pytest.mark.asyncio
    async def test_generate_refactoring_simplify_complexity(self, refactor_strategy, tmp_path):
        """Test suggestion to simplify complex conditionals."""
        impl_file = tmp_path / "complex.py"
        impl_file.write_text("if a and b or c and d or e: pass")
        
        code_smells = [{'type': 'complexity', 'score': 15}]
        best_practices = ['Reduce complexity using early returns']
        
        suggestions = await refactor_strategy._generate_refactoring_suggestions(
            str(impl_file), code_smells, best_practices
        )
        
        assert len(suggestions) > 0
        assert any('simplify' in s['type'].lower() or 'complexity' in s['type'].lower() for s in suggestions)
    
    @pytest.mark.asyncio
    async def test_generate_refactoring_eliminate_duplication(self, refactor_strategy, tmp_path):
        """Test suggestion to eliminate duplicate code."""
        impl_file = tmp_path / "dup.py"
        impl_file.write_text("def a():\n    return 1\ndef b():\n    return 1")
        
        code_smells = [{'type': 'duplication', 'blocks': 2}]
        best_practices = ['DRY principle: extract common code']
        
        suggestions = await refactor_strategy._generate_refactoring_suggestions(
            str(impl_file), code_smells, best_practices
        )
        
        assert len(suggestions) > 0
        assert any('duplication' in s['type'].lower() for s in suggestions)
    
    @pytest.mark.asyncio
    async def test_generate_refactoring_improve_naming(self, refactor_strategy, tmp_path):
        """Test suggestion to improve variable naming."""
        impl_file = tmp_path / "naming.py"
        impl_file.write_text("def x(a): return a + 1")
        
        code_smells = [{'type': 'naming', 'names': ['x', 'a']}]
        best_practices = ['Use descriptive names for functions and variables']
        
        suggestions = await refactor_strategy._generate_refactoring_suggestions(
            str(impl_file), code_smells, best_practices
        )
        
        assert len(suggestions) > 0
        assert any('naming' in s['type'].lower() or 'rename' in s['type'].lower() for s in suggestions)
    
    @pytest.mark.asyncio
    async def test_generate_refactoring_with_framework_patterns(self, refactor_strategy, tmp_path):
        """Test suggestions incorporate framework-specific patterns."""
        impl_file = tmp_path / "flask_app.py"
        impl_file.write_text("def handle_request(): pass")
        
        code_smells = [{'type': 'god_method', 'lines': 100}]
        best_practices = ['Flask: Use blueprints for large applications']
        
        suggestions = await refactor_strategy._generate_refactoring_suggestions(
            str(impl_file), code_smells, best_practices
        )
        
        assert len(suggestions) > 0
    
    @pytest.mark.asyncio
    async def test_generate_refactoring_empty_smells(self, refactor_strategy, tmp_path):
        """Test suggestion generation with no code smells."""
        impl_file = tmp_path / "clean.py"
        impl_file.write_text("def add(a, b): return a + b")
        
        code_smells = []
        best_practices = []
        
        suggestions = await refactor_strategy._generate_refactoring_suggestions(
            str(impl_file), code_smells, best_practices
        )
        
        assert len(suggestions) == 0
    
    @pytest.mark.asyncio
    async def test_generate_refactoring_prioritization(self, refactor_strategy, tmp_path):
        """Test suggestions are prioritized by impact."""
        impl_file = tmp_path / "mixed.py"
        impl_file.write_text("def x():\n    " + "\n    ".join([f"line{i}" for i in range(60)]))
        
        code_smells = [
            {'type': 'function_length', 'lines': 60, 'impact': 'high'},
            {'type': 'naming', 'names': ['x'], 'impact': 'low'}
        ]
        best_practices = ['Extract method', 'Improve naming']
        
        suggestions = await refactor_strategy._generate_refactoring_suggestions(
            str(impl_file), code_smells, best_practices
        )
        
        assert suggestions[0]['impact'] == 'high'


# ============================================================================
# Test Group 4: Incremental Refactoring Application (7 tests)
# ============================================================================

class TestIncrementalRefactoring:
    """Test incremental refactoring with test validation."""
    
    @pytest.mark.asyncio
    async def test_apply_refactoring_single_success(self, refactor_strategy, tmp_path):
        """Test applying single refactoring successfully."""
        impl_file = tmp_path / "code.py"
        impl_file.write_text("def x(): return 1")
        
        test_file = tmp_path / "test_code.py"
        test_file.write_text("def test_x(): assert x() == 1")
        
        refactorings = [{'type': 'rename', 'old': 'x', 'new': 'get_value'}]
        
        refactor_strategy.mcp.call = AsyncMock(return_value={'tests_passing': 1})
        
        applied = await refactor_strategy._apply_refactorings_incrementally(
            str(impl_file), str(test_file), refactorings
        )
        
        assert len(applied) == 1
        assert applied[0]['type'] == 'rename'
    
    @pytest.mark.asyncio
    async def test_apply_refactoring_rollback_on_failure(self, refactor_strategy, tmp_path):
        """Test rollback when refactoring breaks tests."""
        impl_file = tmp_path / "code.py"
        impl_file.write_text("def add(a, b): return a + b")
        
        test_file = tmp_path / "test_code.py"
        test_file.write_text("def test_add(): assert add(2, 3) == 5")
        
        refactorings = [{'type': 'change_logic', 'new_code': 'return a - b'}]
        
        refactor_strategy.mcp.call = AsyncMock(return_value={'tests_passing': 0})
        
        applied = await refactor_strategy._apply_refactorings_incrementally(
            str(impl_file), str(test_file), refactorings
        )
        
        assert len(applied) == 0  # Should rollback
    
    @pytest.mark.asyncio
    async def test_apply_refactoring_multiple_incremental(self, refactor_strategy, tmp_path):
        """Test applying multiple refactorings incrementally."""
        impl_file = tmp_path / "code.py"
        impl_file.write_text("def x(): return 1")
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): assert x() == 1")
        
        refactorings = [
            {'type': 'rename', 'old': 'x', 'new': 'get_value'},
            {'type': 'add_docstring', 'docstring': '"""Return value."""'}
        ]
        
        refactor_strategy.mcp.call = AsyncMock(return_value={'tests_passing': 1})
        
        applied = await refactor_strategy._apply_refactorings_incrementally(
            str(impl_file), str(test_file), refactorings
        )
        
        assert len(applied) == 2
    
    @pytest.mark.asyncio
    async def test_apply_refactoring_stop_on_first_failure(self, refactor_strategy, tmp_path):
        """Test refactoring stops on first failure."""
        impl_file = tmp_path / "code.py"
        test_file = tmp_path / "test.py"
        
        refactorings = [
            {'type': 'good', 'result': 'success'},
            {'type': 'bad', 'result': 'breaks_tests'},
            {'type': 'never_reached', 'result': 'skipped'}
        ]
        
        refactor_strategy.mcp.call = AsyncMock(side_effect=[
            {'tests_passing': 1},  # First succeeds
            {'tests_passing': 0},  # Second fails
        ])
        
        applied = await refactor_strategy._apply_refactorings_incrementally(
            str(impl_file), str(test_file), refactorings
        )
        
        assert len(applied) == 1  # Only first refactoring applied
    
    @pytest.mark.asyncio
    async def test_apply_refactoring_validation_after_each(self, refactor_strategy, tmp_path):
        """Test tests run after each refactoring."""
        impl_file = tmp_path / "code.py"
        test_file = tmp_path / "test.py"
        
        refactorings = [{'type': 'ref1'}, {'type': 'ref2'}]
        
        refactor_strategy.mcp.call = AsyncMock(return_value={'tests_passing': 1})
        
        await refactor_strategy._apply_refactorings_incrementally(
            str(impl_file), str(test_file), refactorings
        )
        
        assert refactor_strategy.mcp.call.call_count == 2  # Called after each refactoring
    
    @pytest.mark.asyncio
    async def test_apply_refactoring_empty_list(self, refactor_strategy, tmp_path):
        """Test handling of empty refactoring list."""
        impl_file = tmp_path / "code.py"
        test_file = tmp_path / "test.py"
        
        applied = await refactor_strategy._apply_refactorings_incrementally(
            str(impl_file), str(test_file), []
        )
        
        assert len(applied) == 0
    
    @pytest.mark.asyncio
    async def test_apply_refactoring_metrics_tracking(self, refactor_strategy, tmp_path):
        """Test refactoring metrics are tracked."""
        impl_file = tmp_path / "code.py"
        test_file = tmp_path / "test.py"
        
        refactorings = [{'type': 'ref1', 'lines_changed': 10}]
        
        refactor_strategy.mcp.call = AsyncMock(return_value={'tests_passing': 1})
        
        applied = await refactor_strategy._apply_refactorings_incrementally(
            str(impl_file), str(test_file), refactorings
        )
        
        assert 'lines_changed' in applied[0]


# ============================================================================
# Test Group 5: DoD Validation (8 tests)
# ============================================================================

class TestREFACTORDoDValidation:
    """Test REFACTOR Definition of Done validation."""
    
    @pytest.mark.asyncio
    async def test_dod_pass_all_criteria(self, refactor_strategy):
        """Test DoD passes when all criteria met."""
        context = {
            'tests_passing': 10,
            'baseline_tests_passing': 10,
            'quality_improvement': 5.0,
            'smells_eliminated': 3,
            'refactorings_applied': 3,
            'git_commit_sha': 'abc123',
            'documentation_updated': True,
            'new_smells_introduced': 0
        }
        
        result = await refactor_strategy.validate_dod(context)
        
        assert result.passed is True
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_dod_fail_test_regression(self, refactor_strategy):
        """Test DoD fails on test regressions."""
        context = {
            'tests_passing': 8,
            'baseline_tests_passing': 10,
            'quality_improvement': 0,
            'smells_eliminated': 0
        }
        
        result = await refactor_strategy.validate_dod(context)
        
        assert result.passed is False
        assert any('Test regression' in e for e in result.errors)
    
    @pytest.mark.asyncio
    async def test_dod_fail_quality_decreased(self, refactor_strategy):
        """Test DoD fails when quality score decreased."""
        context = {
            'tests_passing': 10,
            'baseline_tests_passing': 10,
            'quality_improvement': -2.0,
            'smells_eliminated': 0
        }
        
        result = await refactor_strategy.validate_dod(context)
        
        assert result.passed is False
        assert any('Quality decreased' in e for e in result.errors)
    
    @pytest.mark.asyncio
    async def test_dod_warning_no_smells_eliminated(self, refactor_strategy):
        """Test DoD warns when no smells eliminated."""
        context = {
            'tests_passing': 10,
            'baseline_tests_passing': 10,
            'quality_improvement': 0,
            'smells_eliminated': 0,
            'refactorings_applied': 2
        }
        
        result = await refactor_strategy.validate_dod(context)
        
        assert len(result.warnings) > 0
        assert any('No code smells eliminated' in w for w in result.warnings)
    
    @pytest.mark.asyncio
    async def test_dod_warning_new_smells_introduced(self, refactor_strategy):
        """Test DoD warns when new smells introduced."""
        context = {
            'tests_passing': 10,
            'baseline_tests_passing': 10,
            'quality_improvement': 1.0,
            'smells_eliminated': 2,
            'new_smells_introduced': 1
        }
        
        result = await refactor_strategy.validate_dod(context)
        
        assert len(result.warnings) > 0
        assert any('new code smell' in w for w in result.warnings)
    
    @pytest.mark.asyncio
    async def test_dod_fail_no_git_checkpoint(self, refactor_strategy):
        """Test DoD fails when git checkpoint missing."""
        context = {
            'tests_passing': 10,
            'baseline_tests_passing': 10,
            'quality_improvement': 2.0,
            'smells_eliminated': 1,
            'git_commit_sha': None
        }
        
        result = await refactor_strategy.validate_dod(context)
        
        assert result.passed is False
        assert any('Git checkpoint not created' in e for e in result.errors)
    
    @pytest.mark.asyncio
    async def test_dod_fail_documentation_not_updated(self, refactor_strategy):
        """Test DoD fails when documentation not updated."""
        context = {
            'tests_passing': 10,
            'baseline_tests_passing': 10,
            'quality_improvement': 2.0,
            'smells_eliminated': 1,
            'git_commit_sha': 'abc123',
            'documentation_updated': False
        }
        
        result = await refactor_strategy.validate_dod(context)
        
        assert result.passed is False
        assert any('Documentation not updated' in e for e in result.errors)
    
    @pytest.mark.asyncio
    async def test_dod_logging(self, refactor_strategy, caplog):
        """Test DoD validation is logged."""
        context = {
            'tests_passing': 10,
            'baseline_tests_passing': 10,
            'quality_improvement': 5.0,
            'smells_eliminated': 3,
            'git_commit_sha': 'abc123',
            'documentation_updated': True
        }
        
        await refactor_strategy.validate_dod(context)
        
        assert 'REFACTOR DoD validation' in caplog.text


# ============================================================================
# Run Configuration
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
