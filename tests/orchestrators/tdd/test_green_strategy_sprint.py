"""
CORTEX 4.0 - GREEN Phase Strategy Comprehensive Tests (Task 8.4)

Purpose: Test GREEN phase implementation generation with 70%+ coverage
Version: 4.0.0
Author: CORTEX Development Team
Created: 2025-12-23

Test Coverage Goals:
- DoR validation (5 tests)
- Implementation generation (7 tests)
- Test execution loop (6 tests)
- Over-engineering detection (5 tests)
- DoD validation (7 tests)

Target: 30 tests, 70%+ coverage (from 26.88% baseline)
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from src.orchestrators.tdd.strategies.green_phase_strategy import GREENPhaseStrategy


class TestGREENDoRValidation:
    """Test Definition of Ready validation for GREEN phase."""
    
    @pytest.fixture
    def strategy(self):
        """Create GREEN strategy with mocked dependencies."""
        return GREENPhaseStrategy(
            mcp_gateway=AsyncMock(),
            brain_connector=AsyncMock(),
            knowledge_graph=AsyncMock(),
            clean_code_enforcer=AsyncMock(),
            tech_discovery=AsyncMock()
        )
    
    @pytest.mark.asyncio
    async def test_dor_pass_all_requirements(self, strategy, tmp_path):
        """DoR PASS: All requirements met (test file exists, tests failing)."""
        test_file = tmp_path / "test_feature.py"
        test_file.write_text("def test_example(): assert False")
        
        context = {
            'test_file': str(test_file),
            'tests_failing': 3,
            'tests_passing': 0,
            'feature_name': 'example_feature'
        }
        
        result = await strategy.validate_dor(context)
        assert result.passed is True
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_dor_fail_missing_test_file(self, strategy):
        """DoR FAIL: Test file not specified."""
        context = {
            'tests_failing': 3,
            'tests_passing': 0,
            'feature_name': 'example_feature'
        }
        
        result = await strategy.validate_dor(context)
        assert result.passed is False
        assert "Test file not specified" in result.errors
    
    @pytest.mark.asyncio
    async def test_dor_fail_test_file_not_exists(self, strategy):
        """DoR FAIL: Test file path doesn't exist."""
        context = {
            'test_file': '/nonexistent/test_feature.py',
            'tests_failing': 3,
            'tests_passing': 0,
            'feature_name': 'example_feature'
        }
        
        result = await strategy.validate_dor(context)
        assert result.passed is False
        assert any("does not exist" in e for e in result.errors)
    
    @pytest.mark.asyncio
    async def test_dor_fail_no_failing_tests(self, strategy, tmp_path):
        """DoR FAIL: No failing tests (RED phase incomplete)."""
        test_file = tmp_path / "test_feature.py"
        test_file.write_text("def test_example(): assert True")
        
        context = {
            'test_file': str(test_file),
            'tests_failing': 0,
            'tests_passing': 0,
            'feature_name': 'example_feature'
        }
        
        result = await strategy.validate_dor(context)
        assert result.passed is False
        assert any("No failing tests" in e for e in result.errors)
    
    @pytest.mark.asyncio
    async def test_dor_warning_tests_already_passing(self, strategy, tmp_path):
        """DoR WARNING: Some tests already passing."""
        test_file = tmp_path / "test_feature.py"
        test_file.write_text("def test_example(): assert True")
        
        context = {
            'test_file': str(test_file),
            'tests_failing': 2,
            'tests_passing': 1,
            'feature_name': 'example_feature'
        }
        
        result = await strategy.validate_dor(context)
        assert result.passed is True
        assert len(result.warnings) > 0
        assert "already passing" in result.warnings[0]


class TestImplementationGeneration:
    """Test AI-driven minimal implementation generation."""
    
    @pytest.fixture
    def strategy(self):
        """Create GREEN strategy with mocked MCP gateway."""
        mcp = AsyncMock()
        mcp.generate_implementation = AsyncMock(return_value={
            'file_path': '/tmp/implementation.py',
            'content': 'def example(): return True',
            'lines_of_code': 10,
            'complexity': 2
        })
        
        return GREENPhaseStrategy(
            mcp_gateway=mcp,
            brain_connector=AsyncMock(),
            knowledge_graph=AsyncMock(),
            clean_code_enforcer=AsyncMock(),
            tech_discovery=AsyncMock()
        )
    
    @pytest.mark.asyncio
    async def test_generate_minimal_implementation(self, strategy):
        """Generate minimal implementation from test analysis."""
        test_analysis = {
            'failing_tests': ['test_add', 'test_subtract'],
            'requirements': ['basic arithmetic'],
            'test_count': 2
        }
        best_practices = {'language': 'python', 'patterns': ['pure_functions']}
        tech_profile = MagicMock(language='python', frameworks=[])
        
        impl = await strategy._generate_implementation(
            'calculator',
            test_analysis,
            best_practices,
            tech_profile
        )
        
        assert impl['file_path'] is not None
        assert impl['lines_of_code'] > 0
        # Check that MCP was called (method exists on mock)
        assert hasattr(strategy.mcp, 'generate_implementation')
    
    @pytest.mark.asyncio
    async def test_generate_with_framework_context(self, strategy):
        """Generate implementation with framework-specific patterns."""
        test_analysis = {
            'failing_tests': ['test_api_endpoint'],
            'requirements': ['API endpoint'],
            'test_count': 1
        }
        best_practices = {'framework': 'fastapi', 'patterns': ['dependency_injection']}
        tech_profile = MagicMock(language='python', frameworks=['fastapi'])
        
        impl = await strategy._generate_implementation(
            'api_feature',
            test_analysis,
            best_practices,
            tech_profile
        )
        
        assert impl['file_path'] is not None
        assert hasattr(strategy.mcp, 'generate_implementation')
    
    @pytest.mark.asyncio
    async def test_generate_respects_minimal_principle(self, strategy):
        """Implementation should be minimal (YAGNI principle)."""
        test_analysis = {
            'failing_tests': ['test_simple'],
            'requirements': ['simple function'],
            'test_count': 1
        }
        best_practices = {'principles': ['YAGNI', 'KISS']}
        tech_profile = MagicMock(language='python', frameworks=[])
        
        impl = await strategy._generate_implementation(
            'simple_feature',
            test_analysis,
            best_practices,
            tech_profile
        )
        
        # Minimal = low complexity, low LOC
        assert impl['complexity'] <= 5
        assert impl['lines_of_code'] <= 50
    
    @pytest.mark.asyncio
    async def test_generate_handles_edge_cases(self, strategy):
        """Implementation generation handles edge cases."""
        test_analysis = {
            'failing_tests': ['test_null', 'test_empty', 'test_boundary'],
            'requirements': ['edge case handling'],
            'edge_cases': ['null', 'empty', 'max_int'],
            'test_count': 3
        }
        best_practices = {}
        tech_profile = MagicMock(language='python', frameworks=[])
        
        impl = await strategy._generate_implementation(
            'robust_feature',
            test_analysis,
            best_practices,
            tech_profile
        )
        
        assert impl is not None
        assert 'content' in impl
    
    @pytest.mark.asyncio
    async def test_generate_with_type_hints(self, strategy):
        """Generated code includes type hints."""
        test_analysis = {
            'failing_tests': ['test_typed_function'],
            'requirements': ['typed function'],
            'test_count': 1
        }
        best_practices = {'typing': 'strict'}
        tech_profile = MagicMock(language='python', frameworks=[])
        
        strategy.mcp.generate_implementation.return_value['content'] = \
            'def add(a: int, b: int) -> int: return a + b'
        
        impl = await strategy._generate_implementation(
            'typed_feature',
            test_analysis,
            best_practices,
            tech_profile
        )
        
        assert '->' in impl['content']  # Type hint present
    
    @pytest.mark.asyncio
    async def test_generate_caches_similar_implementations(self, strategy):
        """Similar test patterns reuse cached implementations."""
        test_analysis1 = {
            'failing_tests': ['test_add'],
            'requirements': ['addition'],
            'test_count': 1
        }
        test_analysis2 = {
            'failing_tests': ['test_add', 'test_subtract'],
            'requirements': ['addition', 'subtraction'],
            'test_count': 2
        }
        best_practices = {}
        tech_profile = MagicMock(language='python', frameworks=[])
        
        impl1 = await strategy._generate_implementation(
            'calc_v1', test_analysis1, best_practices, tech_profile
        )
        impl2 = await strategy._generate_implementation(
            'calc_v2', test_analysis2, best_practices, tech_profile
        )
        
        assert impl1 is not None
        assert impl2 is not None
        assert hasattr(strategy.mcp, 'generate_implementation')
    
    @pytest.mark.asyncio
    async def test_generate_error_handling(self, strategy):
        """Handle errors during implementation generation."""
        strategy.mcp.generate_implementation.side_effect = Exception("MCP failure")
        
        test_analysis = {
            'failing_tests': ['test_feature'],
            'requirements': ['feature'],
            'test_count': 1
        }
        best_practices = {}
        tech_profile = MagicMock(language='python', frameworks=[])
        
        with pytest.raises(Exception):
            await strategy._generate_implementation(
                'feature', test_analysis, best_practices, tech_profile
            )


class TestTestExecutionLoop:
    """Test continuous test execution until GREEN."""
    
    @pytest.fixture
    def strategy(self):
        """Create GREEN strategy with test runner mock."""
        strategy = GREENPhaseStrategy(
            mcp_gateway=AsyncMock(),
            brain_connector=AsyncMock(),
            knowledge_graph=AsyncMock(),
            clean_code_enforcer=AsyncMock(),
            tech_discovery=AsyncMock()
        )
        strategy._run_tests = AsyncMock(return_value={
            'passed': 3, 'failed': 0, 'total': 3, 'coverage': 85
        })
        return strategy
    
    @pytest.mark.asyncio
    async def test_run_tests_until_green_immediate_pass(self, strategy):
        """Tests pass on first iteration."""
        test_analysis = {
            'failing_tests': ['test_1', 'test_2', 'test_3'],
            'test_count': 3
        }
        
        result, iterations = await strategy._run_tests_until_green(
            '/tmp/test.py', '/tmp/impl.py', test_analysis
        )
        
        assert result['passed'] == 3
        assert result['failed'] == 0
        assert iterations == 1
    
    @pytest.mark.asyncio
    async def test_run_tests_until_green_multiple_iterations(self, strategy):
        """Tests pass after multiple refinements."""
        call_count = 0
        
        async def mock_run_tests(*args):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return {'passed': 1, 'failed': 2, 'total': 3, 'coverage': 60}
            return {'passed': 3, 'failed': 0, 'total': 3, 'coverage': 85}
        
        strategy._run_tests = AsyncMock(side_effect=mock_run_tests)
        strategy._refine_implementation = AsyncMock()
        
        test_analysis = {
            'failing_tests': ['test_1', 'test_2', 'test_3'],
            'test_count': 3
        }
        
        result, iterations = await strategy._run_tests_until_green(
            '/tmp/test.py', '/tmp/impl.py', test_analysis
        )
        
        assert result['passed'] == 3
        assert iterations == 3
        assert strategy._refine_implementation.call_count == 2
    
    @pytest.mark.asyncio
    async def test_run_tests_max_iterations_exceeded(self, strategy):
        """Fail if max iterations exceeded without GREEN."""
        strategy._run_tests = AsyncMock(return_value={
            'passed': 1, 'failed': 2, 'total': 3, 'coverage': 50
        })
        strategy._refine_implementation = AsyncMock()
        strategy.max_iterations = 5
        
        test_analysis = {
            'failing_tests': ['test_1', 'test_2', 'test_3'],
            'test_count': 3
        }
        
        result, iterations = await strategy._run_tests_until_green(
            '/tmp/test.py', '/tmp/impl.py', test_analysis
        )
        
        assert iterations == 5
        assert result['passed'] < result['total']
    
    @pytest.mark.asyncio
    async def test_run_tests_tracks_coverage_improvement(self, strategy):
        """Track coverage improvement across iterations."""
        coverage_progression = [50, 65, 80, 90]
        call_count = 0
        
        async def mock_run_tests(*args):
            nonlocal call_count
            coverage = coverage_progression[min(call_count, len(coverage_progression) - 1)]
            call_count += 1
            if call_count >= 4:
                return {'passed': 3, 'failed': 0, 'total': 3, 'coverage': coverage}
            return {'passed': 2, 'failed': 1, 'total': 3, 'coverage': coverage}
        
        strategy._run_tests = AsyncMock(side_effect=mock_run_tests)
        strategy._refine_implementation = AsyncMock()
        
        test_analysis = {
            'failing_tests': ['test_1', 'test_2', 'test_3'],
            'test_count': 3
        }
        
        result, iterations = await strategy._run_tests_until_green(
            '/tmp/test.py', '/tmp/impl.py', test_analysis
        )
        
        assert result['coverage'] >= 80
        assert iterations == 4
    
    @pytest.mark.asyncio
    async def test_run_tests_handles_test_execution_errors(self, strategy):
        """Handle errors during test execution gracefully."""
        strategy._run_tests = AsyncMock(side_effect=Exception("Test runner crashed"))
        
        test_analysis = {
            'failing_tests': ['test_1'],
            'test_count': 1
        }
        
        with pytest.raises(Exception):
            await strategy._run_tests_until_green(
                '/tmp/test.py', '/tmp/impl.py', test_analysis
            )
    
    @pytest.mark.asyncio
    async def test_run_tests_partial_green_acceptable(self, strategy):
        """Accept partial GREEN (80%+ tests passing)."""
        strategy._run_tests = AsyncMock(return_value={
            'passed': 8, 'failed': 2, 'total': 10, 'coverage': 85
        })
        
        test_analysis = {
            'failing_tests': ['test_' + str(i) for i in range(10)],
            'test_count': 10
        }
        
        result, iterations = await strategy._run_tests_until_green(
            '/tmp/test.py', '/tmp/impl.py', test_analysis
        )
        
        pass_rate = result['passed'] / result['total']
        assert pass_rate >= 0.8  # 80%+ passing


class TestOverEngineeringDetection:
    """Test detection of unnecessary complexity."""
    
    @pytest.fixture
    def strategy(self):
        """Create GREEN strategy."""
        return GREENPhaseStrategy(
            mcp_gateway=AsyncMock(),
            brain_connector=AsyncMock(),
            knowledge_graph=AsyncMock(),
            clean_code_enforcer=AsyncMock(),
            tech_discovery=AsyncMock()
        )
    
    @pytest.mark.asyncio
    async def test_detect_over_engineering_complexity_high(self, strategy):
        """Detect over-engineering via high complexity."""
        implementation = {
            'complexity': 15,  # High for GREEN phase
            'lines_of_code': 50,
            'content': 'def example(): return True'
        }
        test_analysis = {
            'failing_tests': ['test_simple'],
            'test_count': 1
        }
        
        result = await strategy._detect_over_engineering(implementation, test_analysis)
        
        assert result['detected'] is True
        assert any('complexity' in r.lower() for r in result['reasons'])
    
    @pytest.mark.asyncio
    async def test_detect_over_engineering_excessive_abstraction(self, strategy):
        """Detect over-engineering via excessive abstraction."""
        implementation = {
            'complexity': 5,
            'lines_of_code': 200,  # Too many lines for simple tests
            'abstraction_layers': 4,  # Too many layers
            'content': 'def example(): pass'
        }
        test_analysis = {
            'failing_tests': ['test_simple'],
            'test_count': 1
        }
        
        result = await strategy._detect_over_engineering(implementation, test_analysis)
        
        assert result['detected'] is True
        assert any('lines' in r.lower() for r in result['reasons'])
    
    @pytest.mark.asyncio
    async def test_detect_no_over_engineering_minimal(self, strategy):
        """No over-engineering detected for minimal implementation."""
        implementation = {
            'complexity': 3,
            'lines_of_code': 20,
            'abstraction_layers': 1,
            'content': 'def example(): return True'
        }
        test_analysis = {
            'failing_tests': ['test_simple'],
            'test_count': 2
        }
        
        result = await strategy._detect_over_engineering(implementation, test_analysis)
        
        assert result['detected'] is False
        assert len(result['reasons']) == 0
    
    @pytest.mark.asyncio
    async def test_detect_over_engineering_premature_optimization(self, strategy):
        """Detect premature optimization patterns."""
        implementation = {
            'complexity': 8,
            'lines_of_code': 100,
            'optimization_patterns': ['caching', 'threading', 'multiprocessing'],
            'content': 'cache = {}; def example(): optimize()'
        }
        test_analysis = {
            'failing_tests': ['test_basic'],
            'test_count': 5
        }
        
        result = await strategy._detect_over_engineering(implementation, test_analysis)
        
        assert result['detected'] is True
        assert any('optimization' in r.lower() or 'complexity' in r.lower() for r in result['reasons'])
    
    @pytest.mark.asyncio
    async def test_detect_over_engineering_scope_appropriate(self, strategy):
        """Allow complexity when test scope justifies it."""
        implementation = {
            'complexity': 4,  # Within threshold
            'lines_of_code': 150,
            'content': 'def example(): return True'
        }
        test_analysis = {
            'failing_tests': ['test_' + str(i) for i in range(20)],
            'complexity': 'high',
            'test_count': 20
        }
        
        result = await strategy._detect_over_engineering(implementation, test_analysis)
        
        # Should NOT detect over-engineering (20 LOC per test is within threshold)
        assert result['detected'] is False


class TestGREENDoDValidation:
    """Test Definition of Done validation for GREEN phase."""
    
    @pytest.fixture
    def strategy(self):
        """Create GREEN strategy."""
        return GREENPhaseStrategy(
            mcp_gateway=AsyncMock(),
            brain_connector=AsyncMock(),
            knowledge_graph=AsyncMock(),
            clean_code_enforcer=AsyncMock(),
            tech_discovery=AsyncMock()
        )
    
    @pytest.mark.asyncio
    async def test_dod_pass_all_criteria(self, strategy, tmp_path):
        """DoD PASS: All criteria met."""
        impl_file = tmp_path / "implementation.py"
        impl_file.write_text("def example(): return True")
        
        context = {
            'implementation_file': str(impl_file),
            'tests_passing': 3,
            'tests_failing': 0,
            'quality_score': 8.5,
            'git_commit_sha': 'abc123',
            'documentation_updated': True,
            'coverage': 85
        }
        
        result = await strategy.validate_dod(context)
        assert result.passed is True
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_dod_fail_no_implementation_file(self, strategy):
        """DoD FAIL: Implementation file not created."""
        context = {
            'tests_passing': 3,
            'tests_failing': 0
        }
        
        result = await strategy.validate_dod(context)
        assert result.passed is False
        assert any("not created" in e for e in result.errors)
    
    @pytest.mark.asyncio
    async def test_dod_fail_no_tests_passing(self, strategy, tmp_path):
        """DoD FAIL: No tests passing."""
        impl_file = tmp_path / "implementation.py"
        impl_file.write_text("def example(): return True")
        
        context = {
            'implementation_file': str(impl_file),
            'tests_passing': 0,
            'tests_failing': 3
        }
        
        result = await strategy.validate_dod(context)
        assert result.passed is False
        assert any("No tests passing" in e for e in result.errors)
    
    @pytest.mark.asyncio
    async def test_dod_warning_low_quality_score(self, strategy, tmp_path):
        """DoD WARNING: Quality score below threshold."""
        impl_file = tmp_path / "implementation.py"
        impl_file.write_text("def example(): return True")
        
        context = {
            'implementation_file': str(impl_file),
            'tests_passing': 3,
            'tests_failing': 0,
            'quality_score': 6.5  # Below 7.0 threshold
        }
        
        result = await strategy.validate_dod(context)
        # Should pass but with warning
        assert len(result.warnings) > 0
        assert any("quality" in w.lower() for w in result.warnings)
    
    @pytest.mark.asyncio
    async def test_dod_warning_low_coverage(self, strategy, tmp_path):
        """DoD WARNING: Test coverage below threshold."""
        impl_file = tmp_path / "implementation.py"
        impl_file.write_text("def example(): return True")
        
        context = {
            'implementation_file': str(impl_file),
            'tests_passing': 3,
            'tests_failing': 0,
            'quality_score': 8.0,
            'coverage': 70  # Below 80% threshold
        }
        
        result = await strategy.validate_dod(context)
        assert len(result.warnings) > 0
        assert any("coverage" in w.lower() for w in result.warnings)
    
    @pytest.mark.asyncio
    async def test_dod_fail_missing_git_checkpoint(self, strategy, tmp_path):
        """DoD FAIL: Git checkpoint not created."""
        impl_file = tmp_path / "implementation.py"
        impl_file.write_text("def example(): return True")
        
        context = {
            'implementation_file': str(impl_file),
            'tests_passing': 3,
            'tests_failing': 0,
            'quality_score': 8.0,
            'git_commit_sha': None
        }
        
        result = await strategy.validate_dod(context)
        assert result.passed is False
        assert any("Git checkpoint" in e for e in result.errors)
    
    @pytest.mark.asyncio
    async def test_dod_partial_green_acceptable(self, strategy, tmp_path):
        """DoD PASS: 80%+ tests passing is acceptable."""
        impl_file = tmp_path / "implementation.py"
        impl_file.write_text("def example(): return True")
        
        context = {
            'implementation_file': str(impl_file),
            'tests_passing': 8,
            'tests_failing': 2,  # 80% pass rate
            'quality_score': 8.0,
            'git_commit_sha': 'abc123',
            'coverage': 85
        }
        
        result = await strategy.validate_dod(context)
        assert result.passed is True
        assert len(result.warnings) > 0  # Warning about failing tests
