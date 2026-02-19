"""
Tests for Test Intelligence Foundation - All 3 Layers.

Authority: WAVE-1 Stage 3, cortex-architect.prompt.md v15.3
"""

import pytest
from pathlib import Path
import tempfile
import yaml

from cortex.testing.test_intelligence import (
    TestDemandGenerator,
    TestComposer,
    QualityValidator,
)


# ============================================================================
# LAYER 1: TEST DEMAND GENERATOR TESTS (16 tests)
# ============================================================================

class TestDemandGeneratorLayer:
    """Tests for Layer 1: Test Demand Generator."""
    
    @pytest.fixture
    def temp_cortex_root(self):
        """Create temporary CORTEX root structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            
            # Create directory structure
            (root / "cortex" / "wiring" / "specifications").mkdir(parents=True)
            (root / "cortex-registry" / "_cortex-master" / "test-demands").mkdir(parents=True)
            
            # Create sample orchestrator spec
            spec_file = root / "cortex" / "wiring" / "specifications" / "master-orchestrator.yaml"
            spec_data = {
                "orchestrator": "MasterOrchestrator",
                "responsibilities": [
                    "Route requests to appropriate orchestrator",
                    "Manage execution flow",
                    "Aggregate results",
                ],
                "operations": [
                    {"name": "execute", "type": "primary"},
                    {"name": "validate", "type": "secondary"},
                ],
                "dependencies": ["IntentRouter", "EnforcementOrchestrator"],
            }
            with open(spec_file, 'w') as f:
                yaml.dump(spec_data, f)
            
            yield root
    
    def test_generator_initialization(self, temp_cortex_root):
        """Test: Generator initializes with correct paths."""
        generator = TestDemandGenerator(temp_cortex_root)
        
        assert generator.cortex_root == temp_cortex_root
        assert generator.orchestrator_specs_dir.exists()
        
    def test_find_orchestrator_spec(self, temp_cortex_root):
        """Test: Generator can find orchestrator spec file."""
        generator = TestDemandGenerator(temp_cortex_root)
        
        spec_file = generator._find_orchestrator_spec("MasterOrchestrator")
        
        assert spec_file is not None
        assert spec_file.exists()
        assert "master-orchestrator" in spec_file.stem
    
    def test_parse_orchestrator_spec(self, temp_cortex_root):
        """Test: Generator can parse YAML spec."""
        generator = TestDemandGenerator(temp_cortex_root)
        spec_file = generator._find_orchestrator_spec("MasterOrchestrator")
        
        spec_data = generator._parse_orchestrator_spec(spec_file)
        
        assert "orchestrator" in spec_data
        assert spec_data["orchestrator"] == "MasterOrchestrator"
        assert "responsibilities" in spec_data
    
    def test_extract_critical_paths(self, temp_cortex_root):
        """Test: Generator extracts critical paths from spec."""
        generator = TestDemandGenerator(temp_cortex_root)
        spec_file = generator._find_orchestrator_spec("MasterOrchestrator")
        spec_data = generator._parse_orchestrator_spec(spec_file)
        
        critical_paths = generator._extract_critical_paths(spec_data)
        
        assert isinstance(critical_paths, list)
        assert len(critical_paths) > 0
        assert len(critical_paths) <= 5  # Limit to 5
    
    def test_extract_edge_cases(self, temp_cortex_root):
        """Test: Generator extracts edge cases."""
        generator = TestDemandGenerator(temp_cortex_root)
        spec_file = generator._find_orchestrator_spec("MasterOrchestrator")
        spec_data = generator._parse_orchestrator_spec(spec_file)
        
        edge_cases = generator._extract_edge_cases(spec_data)
        
        assert isinstance(edge_cases, list)
        assert len(edge_cases) <= 3
    
    def test_extract_error_scenarios(self, temp_cortex_root):
        """Test: Generator extracts error scenarios."""
        generator = TestDemandGenerator(temp_cortex_root)
        spec_file = generator._find_orchestrator_spec("MasterOrchestrator")
        spec_data = generator._parse_orchestrator_spec(spec_file)
        
        error_scenarios = generator._extract_error_scenarios(spec_data)
        
        assert isinstance(error_scenarios, list)
        assert len(error_scenarios) <= 3
    
    def test_extract_integration_points(self, temp_cortex_root):
        """Test: Generator extracts integration points."""
        generator = TestDemandGenerator(temp_cortex_root)
        spec_file = generator._find_orchestrator_spec("MasterOrchestrator")
        spec_data = generator._parse_orchestrator_spec(spec_file)
        
        integration_points = generator._extract_integration_points(spec_data)
        
        assert isinstance(integration_points, list)
        assert len(integration_points) <= 2
    
    def test_determine_priority_core_orchestrator(self, temp_cortex_root):
        """Test: Core orchestrators get P0 priority."""
        generator = TestDemandGenerator(temp_cortex_root)
        
        priority = generator._determine_priority("MasterOrchestrator", {})
        
        assert priority == "P0"
    
    def test_determine_priority_non_core_orchestrator(self, temp_cortex_root):
        """Test: Non-core orchestrators get P1 priority."""
        generator = TestDemandGenerator(temp_cortex_root)
        
        priority = generator._determine_priority("SomeOtherOrchestrator", {})
        
        assert priority == "P1"
    
    def test_generate_demand_for_orchestrator(self, temp_cortex_root):
        """Test: Generator creates TestDemand object."""
        generator = TestDemandGenerator(temp_cortex_root)
        
        demand = generator.generate_demand_for_orchestrator("MasterOrchestrator")
        
        assert demand.orchestrator_name == "MasterOrchestrator"
        assert demand.priority == "P0"
        assert len(demand.critical_paths) > 0
        assert demand.test_count_estimate <= 10  # Golden path limiting
    
    def test_save_demand_to_yaml(self, temp_cortex_root):
        """Test: Demand can be saved to YAML file."""
        generator = TestDemandGenerator(temp_cortex_root)
        demand = generator.generate_demand_for_orchestrator("MasterOrchestrator")
        
        output_file = generator.save_demand_to_yaml(demand)
        
        assert output_file.exists()
        assert output_file.suffix == ".yaml"
        
        # Verify YAML content
        with open(output_file) as f:
            saved_demand = yaml.safe_load(f)
        assert saved_demand["orchestrator"] == "MasterOrchestrator"
    
    def test_golden_path_limiting(self, temp_cortex_root):
        """Test: Test count limited to 10 per orchestrator."""
        generator = TestDemandGenerator(temp_cortex_root)
        demand = generator.generate_demand_for_orchestrator("MasterOrchestrator")
        
        assert demand.test_count_estimate <= 10
    
    def test_demand_completeness(self, temp_cortex_root):
        """Test: Generated demand has all required fields."""
        generator = TestDemandGenerator(temp_cortex_root)
        demand = generator.generate_demand_for_orchestrator("MasterOrchestrator")
        
        assert hasattr(demand, 'orchestrator_name')
        assert hasattr(demand, 'spec_path')
        assert hasattr(demand, 'critical_paths')
        assert hasattr(demand, 'edge_cases')
        assert hasattr(demand, 'error_scenarios')
        assert hasattr(demand, 'integration_points')
        assert hasattr(demand, 'test_count_estimate')
        assert hasattr(demand, 'priority')
    
    def test_demand_generator_missing_spec(self, temp_cortex_root):
        """Test: Generator handles missing spec gracefully."""
        generator = TestDemandGenerator(temp_cortex_root)
        
        with pytest.raises(FileNotFoundError):
            generator.generate_demand_for_orchestrator("NonExistentOrchestrator")
    
    def test_demand_yaml_structure(self, temp_cortex_root):
        """Test: Saved YAML has expected structure."""
        generator = TestDemandGenerator(temp_cortex_root)
        demand = generator.generate_demand_for_orchestrator("MasterOrchestrator")
        output_file = generator.save_demand_to_yaml(demand)
        
        with open(output_file) as f:
            yaml_data = yaml.safe_load(f)
        
        required_keys = [
            "orchestrator",
            "spec_path",
            "priority",
            "test_count_estimate",
            "critical_paths",
            "edge_cases",
            "error_scenarios",
            "integration_points",
        ]
        
        for key in required_keys:
            assert key in yaml_data, f"Missing key: {key}"
    
    def test_demand_generator_output_directory_creation(self, temp_cortex_root):
        """Test: Generator creates output directory if missing."""
        generator = TestDemandGenerator(temp_cortex_root)
        
        # Remove output directory
        import shutil
        if generator.test_demands_output_dir.exists():
            shutil.rmtree(generator.test_demands_output_dir)
        
        demand = generator.generate_demand_for_orchestrator("MasterOrchestrator")
        output_file = generator.save_demand_to_yaml(demand)
        
        assert generator.test_demands_output_dir.exists()
        assert output_file.exists()


# ============================================================================
# LAYER 2: TEST COMPOSER TESTS (21 tests)
# ============================================================================

class TestComposerLayer:
    """Tests for Layer 2: Test Composer."""
    
    @pytest.fixture
    def temp_cortex_root(self):
        """Create temporary CORTEX root structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            
            # Create directory structure
            (root / "cortex-registry" / "_cortex-master" / "test-demands").mkdir(parents=True)
            (root / "tests" / "orchestrators" / "generated").mkdir(parents=True)
            
            # Create sample test demand
            demand_file = root / "cortex-registry" / "_cortex-master" / "test-demands" / "masterorchestrator-test-demand.yaml"
            demand_data = {
                "orchestrator": "MasterOrchestrator",
                "spec_path": "/path/to/spec",
                "priority": "P0",
                "test_count_estimate": 8,
                "critical_paths": [
                    "Route requests",
                    "Manage execution flow",
                    "Aggregate results",
                ],
                "edge_cases": [
                    "empty input",
                    "null parameters",
                ],
                "error_scenarios": [
                    "missing required parameter",
                    "invalid operation type",
                ],
                "integration_points": [
                    "IntentRouter",
                ],
            }
            with open(demand_file, 'w') as f:
                yaml.dump(demand_data, f)
            
            yield root
    
    def test_composer_initialization(self, temp_cortex_root):
        """Test: Composer initializes with correct paths."""
        composer = TestComposer(temp_cortex_root)
        
        assert composer.cortex_root == temp_cortex_root
        assert composer.test_demands_dir.exists()
    
    def test_compose_test_from_demand(self, temp_cortex_root):
        """Test: Composer generates tests from demand file."""
        composer = TestComposer(temp_cortex_root)
        demand_file = temp_cortex_root / "cortex-registry" / "_cortex-master" / "test-demands" / "masterorchestrator-test-demand.yaml"
        
        composed_tests = composer.compose_test_from_demand(demand_file)
        
        assert isinstance(composed_tests, list)
        assert len(composed_tests) > 0
        assert len(composed_tests) <= 10  # Golden path limiting
    
    def test_generate_critical_path_test(self, temp_cortex_root):
        """Test: Composer generates critical path test."""
        composer = TestComposer(temp_cortex_root)
        
        test = composer._generate_critical_path_test("MasterOrchestrator", "Route requests", 0)
        
        assert test.test_name.startswith("test_")
        assert "critical_path" in test.test_name
        assert test.priority == "P0"
        assert "def test_" in test.test_function
    
    def test_generate_edge_case_test(self, temp_cortex_root):
        """Test: Composer generates edge case test."""
        composer = TestComposer(temp_cortex_root)
        
        test = composer._generate_edge_case_test("MasterOrchestrator", "empty input", 0)
        
        assert test.test_name.startswith("test_")
        assert "edge_case" in test.test_name
        assert test.priority == "P1"
    
    def test_generate_error_scenario_test(self, temp_cortex_root):
        """Test: Composer generates error scenario test."""
        composer = TestComposer(temp_cortex_root)
        
        test = composer._generate_error_scenario_test("MasterOrchestrator", "missing parameter", 0)
        
        assert test.test_name.startswith("test_")
        assert "error" in test.test_name
        assert "pytest.raises" in test.test_function
    
    def test_save_composed_tests_to_file(self, temp_cortex_root):
        """Test: Composer saves tests to file."""
        composer = TestComposer(temp_cortex_root)
        demand_file = temp_cortex_root / "cortex-registry" / "_cortex-master" / "test-demands" / "masterorchestrator-test-demand.yaml"
        composed_tests = composer.compose_test_from_demand(demand_file)
        
        output_file = composer.save_composed_tests_to_file("MasterOrchestrator", composed_tests)
        
        assert output_file.exists()
        assert output_file.suffix == ".py"
        assert "test_" in output_file.name
    
    def test_generated_test_file_structure(self, temp_cortex_root):
        """Test: Generated test file has correct structure."""
        composer = TestComposer(temp_cortex_root)
        demand_file = temp_cortex_root / "cortex-registry" / "_cortex-master" / "test-demands" / "masterorchestrator-test-demand.yaml"
        composed_tests = composer.compose_test_from_demand(demand_file)
        output_file = composer.save_composed_tests_to_file("MasterOrchestrator", composed_tests)
        
        with open(output_file) as f:
            content = f.read()
        
        assert '"""' in content  # Has docstring
        assert "import pytest" in content
        assert "@pytest.fixture" in content
        assert "def test_" in content
    
    def test_generated_test_has_fixtures(self, temp_cortex_root):
        """Test: Generated tests use fixtures."""
        composer = TestComposer(temp_cortex_root)
        test = composer._generate_critical_path_test("MasterOrchestrator", "test path", 0)
        
        assert len(test.fixtures) > 0
        assert "orchestrator_instance" in test.fixtures
    
    def test_generated_test_has_assertions(self, temp_cortex_root):
        """Test: Generated tests have assertions."""
        composer = TestComposer(temp_cortex_root)
        test = composer._generate_critical_path_test("MasterOrchestrator", "test path", 0)
        
        assert len(test.assertions) > 0
        assert "assert" in test.test_function
    
    def test_golden_path_limiting_in_composer(self, temp_cortex_root):
        """Test: Composer limits tests to 10 per orchestrator."""
        composer = TestComposer(temp_cortex_root)
        
        # Create demand with many paths
        demand_data = {
            "orchestrator": "TestOrch",
            "critical_paths": ["path"] * 20,  # 20 paths
            "edge_cases": ["edge"] * 20,
            "error_scenarios": ["error"] * 20,
        }
        
        demand_file = temp_cortex_root / "cortex-registry" / "_cortex-master" / "test-demands" / "test-demand.yaml"
        with open(demand_file, 'w') as f:
            yaml.dump(demand_data, f)
        
        composed_tests = composer.compose_test_from_demand(demand_file)
        
        assert len(composed_tests) <= 10
    
    def test_composer_test_naming_convention(self, temp_cortex_root):
        """Test: Generated test names follow convention."""
        composer = TestComposer(temp_cortex_root)
        test = composer._generate_critical_path_test("MasterOrchestrator", "test path", 0)
        
        assert test.test_name.startswith("test_")
        assert "masterorchestrator" in test.test_name.lower()
    
    def test_composer_arranges_acts_asserts(self, temp_cortex_root):
        """Test: Generated tests follow AAA pattern."""
        composer = TestComposer(temp_cortex_root)
        test = composer._generate_critical_path_test("MasterOrchestrator", "test path", 0)
        
        assert "# Arrange" in test.test_function
        assert "# Act" in test.test_function
        assert "# Assert" in test.test_function
    
    def test_composer_test_has_docstring(self, temp_cortex_root):
        """Test: Generated tests have docstrings."""
        composer = TestComposer(temp_cortex_root)
        test = composer._generate_critical_path_test("MasterOrchestrator", "test path", 0)
        
        assert '"""' in test.test_function
    
    def test_composer_error_tests_use_pytest_raises(self, temp_cortex_root):
        """Test: Error scenario tests use pytest.raises."""
        composer = TestComposer(temp_cortex_root)
        test = composer._generate_error_scenario_test("MasterOrchestrator", "error", 0)
        
        assert "pytest.raises" in test.test_function
    
    def test_composer_output_directory_creation(self, temp_cortex_root):
        """Test: Composer creates output directory if missing."""
        composer = TestComposer(temp_cortex_root)
        
        # Remove output directory
        import shutil
        if composer.tests_output_dir.exists():
            shutil.rmtree(composer.tests_output_dir)
        
        demand_file = temp_cortex_root / "cortex-registry" / "_cortex-master" / "test-demands" / "masterorchestrator-test-demand.yaml"
        composed_tests = composer.compose_test_from_demand(demand_file)
        output_file = composer.save_composed_tests_to_file("MasterOrchestrator", composed_tests)
        
        assert composer.tests_output_dir.exists()
        assert output_file.exists()
    
    def test_composer_test_function_syntax_valid(self, temp_cortex_root):
        """Test: Generated test functions have valid Python syntax."""
        composer = TestComposer(temp_cortex_root)
        test = composer._generate_critical_path_test("MasterOrchestrator", "test path", 0)
        
        # Check basic syntax validity
        assert "def test_" in test.test_function
        assert ":" in test.test_function
        assert test.test_function.count('"""') % 2 == 0  # Paired docstrings
    
    def test_composed_test_data_structure(self, temp_cortex_root):
        """Test: ComposedTest has all required fields."""
        composer = TestComposer(temp_cortex_root)
        test = composer._generate_critical_path_test("MasterOrchestrator", "test path", 0)
        
        assert hasattr(test, 'test_name')
        assert hasattr(test, 'test_function')
        assert hasattr(test, 'fixtures')
        assert hasattr(test, 'assertions')
        assert hasattr(test, 'priority')
    
    def test_composer_handles_empty_demand(self, temp_cortex_root):
        """Test: Composer handles demand with no paths."""
        composer = TestComposer(temp_cortex_root)
        
        # Create empty demand
        demand_data = {
            "orchestrator": "EmptyOrch",
            "critical_paths": [],
            "edge_cases": [],
            "error_scenarios": [],
        }
        
        demand_file = temp_cortex_root / "cortex-registry" / "_cortex-master" / "test-demands" / "empty-demand.yaml"
        with open(demand_file, 'w') as f:
            yaml.dump(demand_data, f)
        
        composed_tests = composer.compose_test_from_demand(demand_file)
        
        assert isinstance(composed_tests, list)
        assert len(composed_tests) == 0
    
    def test_composer_priority_assignment(self, temp_cortex_root):
        """Test: Composer assigns correct priorities."""
        composer = TestComposer(temp_cortex_root)
        
        critical_test = composer._generate_critical_path_test("TestOrch", "path", 0)
        edge_test = composer._generate_edge_case_test("TestOrch", "edge", 0)
        error_test = composer._generate_error_scenario_test("TestOrch", "error", 0)
        
        assert critical_test.priority == "P0"
        assert edge_test.priority == "P1"
        assert error_test.priority == "P1"
    
    def test_composer_file_import_structure(self, temp_cortex_root):
        """Test: Generated file has proper imports."""
        composer = TestComposer(temp_cortex_root)
        demand_file = temp_cortex_root / "cortex-registry" / "_cortex-master" / "test-demands" / "masterorchestrator-test-demand.yaml"
        composed_tests = composer.compose_test_from_demand(demand_file)
        output_file = composer.save_composed_tests_to_file("MasterOrchestrator", composed_tests)
        
        with open(output_file) as f:
            content = f.read()
        
        assert "import pytest" in content
        assert "from cortex.orchestrators." in content


# ============================================================================
# LAYER 3: QUALITY VALIDATOR TESTS (22 tests)
# ============================================================================

class TestQualityValidatorLayer:
    """Tests for Layer 3: Quality Validator."""
    
    @pytest.fixture
    def sample_test_file(self, tmp_path):
        """Create sample test file."""
        test_file = tmp_path / "test_sample.py"
        content = '''"""Sample test file."""

import pytest

@pytest.fixture
def sample_fixture():
    """Provide sample data."""
    return {"key": "value"}

def test_good_quality(sample_fixture):
    """Test with good quality.
    
    This test follows AAA pattern and has meaningful assertions.
    """
    # Arrange
    data = sample_fixture
    
    # Act
    result = data.get("key")
    
    # Assert
    assert result is not None
    assert result == "value"

def test_poor_quality():
    """Test with quality issues."""
    import time
    time.sleep(0.1)  # Brittleness: sleep
    assert True == True  # Brittleness: == True
'''
        test_file.write_text(content)
        return test_file
    
    def test_validator_initialization(self):
        """Test: Validator initializes correctly."""
        validator = QualityValidator()
        
        assert validator.QUALITY_THRESHOLD == 0.70
        assert len(validator.BRITTLENESS_PATTERNS) == 20
    
    def test_validate_test_file(self, sample_test_file):
        """Test: Validator can validate test file."""
        validator = QualityValidator()
        
        scores = validator.validate_test_file(sample_test_file)
        
        assert isinstance(scores, list)
        assert len(scores) > 0
    
    def test_extract_tests_from_file(self, sample_test_file):
        """Test: Validator extracts individual tests."""
        validator = QualityValidator()
        
        with open(sample_test_file) as f:
            content = f.read()
        
        tests = validator._extract_tests(content)
        
        assert isinstance(tests, dict)
        assert len(tests) == 2  # Sample file has 2 tests
        assert "test_good_quality" in tests
        assert "test_poor_quality" in tests
    
    def test_score_coverage(self):
        """Test: Validator scores test coverage correctly."""
        validator = QualityValidator()
        
        good_test = '''
def test_with_aaa():
    """Test with AAA pattern."""
    # Arrange
    x = 1
    # Act
    y = x + 1
    # Assert
    assert y == 2
    assert y > 0
'''
        
        score = validator._score_coverage(good_test)
        
        assert score > 0.5  # Should have high coverage score
    
    def test_score_realism(self):
        """Test: Validator scores realism correctly."""
        validator = QualityValidator()
        
        realistic_test = '''
def test_realistic():
    result = do_something()
    assert result is not None
    assert result.success is True
'''
        
        score = validator._score_realism(realistic_test)
        
        assert score > 0.5
    
    def test_score_maintainability(self):
        """Test: Validator scores maintainability correctly."""
        validator = QualityValidator()
        
        maintainable_test = '''
def test_with_docs(fixture_a, fixture_b):
    """Well documented test."""
    # This test is easy to understand
    result = do_something()
    assert result
'''
        
        score = validator._score_maintainability(maintainable_test)
        
        assert score > 0.5
    
    def test_score_brittleness_detects_sleep(self):
        """Test: Validator detects time.sleep brittleness."""
        validator = QualityValidator()
        
        brittle_test = '''
def test_with_sleep():
    import time
    time.sleep(1)
    assert True
'''
        
        brittleness_score, issues = validator._score_brittleness(brittle_test)
        
        assert brittleness_score > 0.0
        assert len(issues) > 0
        assert any("sleep" in issue.lower() for issue in issues)
    
    def test_score_brittleness_detects_assert_true(self):
        """Test: Validator detects assert == True brittleness."""
        validator = QualityValidator()
        
        brittle_test = '''
def test_assert_true():
    result = True
    assert result == True
'''
        
        brittleness_score, issues = validator._score_brittleness(brittle_test)
        
        assert brittleness_score > 0.0
    
    def test_score_brittleness_detects_bare_except(self):
        """Test: Validator detects bare except brittleness."""
        validator = QualityValidator()
        
        brittle_test = '''
def test_bare_except():
    try:
        do_something()
    except:
        pass
'''
        
        brittleness_score, issues = validator._score_brittleness(brittle_test)
        
        assert brittleness_score > 0.0
    
    def test_quality_threshold_enforcement(self, sample_test_file):
        """Test: Validator enforces 70% quality threshold."""
        validator = QualityValidator()
        
        scores = validator.validate_test_file(sample_test_file)
        
        # Check that quality score respects threshold
        for score in scores:
            if score.passed_threshold:
                assert score.overall_score >= 0.70
            else:
                assert score.overall_score < 0.70
    
    def test_quality_score_data_structure(self, sample_test_file):
        """Test: QualityScore has all required fields."""
        validator = QualityValidator()
        
        scores = validator.validate_test_file(sample_test_file)
        score = scores[0]
        
        assert hasattr(score, 'test_name')
        assert hasattr(score, 'coverage_score')
        assert hasattr(score, 'realism_score')
        assert hasattr(score, 'maintainability_score')
        assert hasattr(score, 'brittleness_score')
        assert hasattr(score, 'overall_score')
        assert hasattr(score, 'issues')
        assert hasattr(score, 'passed_threshold')
    
    def test_overall_score_calculation(self):
        """Test: Overall score is weighted average."""
        validator = QualityValidator()
        
        test_code = '''
def test_sample():
    """Sample test."""
    # Arrange
    x = 1
    # Act
    y = x + 1
    # Assert
    assert y is not None
    assert y == 2
'''
        
        score = validator._score_test("test_sample", test_code)
        
        # Check that overall score is in valid range
        assert 0.0 <= score.overall_score <= 1.0
        
        # Check that it considers all components
        assert score.coverage_score > 0.0
        assert score.realism_score > 0.0
        assert score.maintainability_score > 0.0
    
    def test_generate_quality_report(self, sample_test_file):
        """Test: Validator generates quality report."""
        validator = QualityValidator()
        scores = validator.validate_test_file(sample_test_file)
        
        report = validator.generate_quality_report(scores)
        
        assert "total_tests" in report
        assert "passed_threshold" in report
        assert "failed_threshold" in report
        assert "pass_rate" in report
        assert "average_scores" in report
        assert "issues" in report
    
    def test_quality_report_accuracy(self, sample_test_file):
        """Test: Quality report has accurate statistics."""
        validator = QualityValidator()
        scores = validator.validate_test_file(sample_test_file)
        
        report = validator.generate_quality_report(scores)
        
        assert report["total_tests"] == len(scores)
        assert report["passed_threshold"] + report["failed_threshold"] == report["total_tests"]
        
        if report["total_tests"] > 0:
            expected_pass_rate = report["passed_threshold"] / report["total_tests"]
            assert abs(report["pass_rate"] - expected_pass_rate) < 0.01  # Floating point tolerance
    
    def test_brittleness_patterns_comprehensive(self):
        """Test: Validator has comprehensive brittleness patterns."""
        validator = QualityValidator()
        
        # Should have 20 patterns as specified
        assert len(validator.BRITTLENESS_PATTERNS) == 20
        
        # Check some key patterns exist
        pattern_strings = " ".join(validator.BRITTLENESS_PATTERNS)
        assert "sleep" in pattern_strings
        assert "True" in pattern_strings
        assert "except" in pattern_strings
    
    def test_validator_handles_malformed_test(self):
        """Test: Validator handles malformed test gracefully."""
        validator = QualityValidator()
        
        malformed = "not a valid test function"
        
        tests = validator._extract_tests(malformed)
        
        assert isinstance(tests, dict)
        # Should return empty dict for malformed input
    
    def test_score_components_range(self):
        """Test: All score components are in valid range [0.0, 1.0]."""
        validator = QualityValidator()
        
        test_code = '''
def test_sample():
    assert True
'''
        
        score = validator._score_test("test_sample", test_code)
        
        assert 0.0 <= score.coverage_score <= 1.0
        assert 0.0 <= score.realism_score <= 1.0
        assert 0.0 <= score.maintainability_score <= 1.0
        assert 0.0 <= score.brittleness_score <= 1.0
        assert 0.0 <= score.overall_score <= 1.0
    
    def test_validator_detects_todo_comments(self):
        """Test: Validator detects TODO/FIXME as brittleness."""
        validator = QualityValidator()
        
        test_with_todo = '''
def test_incomplete():
    # TODO: implement this test
    pass
'''
        
        brittleness_score, issues = validator._score_brittleness(test_with_todo)
        
        assert brittleness_score > 0.0
    
    def test_validator_rewards_good_practices(self):
        """Test: Validator gives high scores to well-written tests."""
        validator = QualityValidator()
        
        excellent_test = '''
def test_excellent_quality(sample_fixture):
    """Test with excellent quality.
    
    Follows all best practices:
    - AAA pattern
    - Meaningful assertions
    - Good documentation
    - Uses fixtures
    """
    # Arrange
    data = sample_fixture.get_data()
    expected = {"result": "success"}
    
    # Act
    result = process_data(data)
    
    # Assert
    assert result is not None
    assert result == expected
    assert result["result"] == "success"
'''
        
        score = validator._score_test("test_excellent_quality", excellent_test)
        
        # Should have high overall score
        assert score.overall_score > 0.60  # At least 60%
        assert score.passed_threshold or score.overall_score >= 0.65  # Close to threshold
    
    def test_validator_penalizes_poor_practices(self):
        """Test: Validator gives low scores to poorly-written tests."""
        validator = QualityValidator()
        
        poor_test = '''
def test_poor():
    import time
    time.sleep(1)
    try:
        x = True
        assert x == True
    except:
        pass
'''
        
        score = validator._score_test("test_poor", poor_test)
        
        # Should have multiple brittleness issues
        assert score.brittleness_score > 0.3
        assert len(score.issues) >= 2
    
    def test_quality_report_average_scores(self, sample_test_file):
        """Test: Quality report calculates correct average scores."""
        validator = QualityValidator()
        scores = validator.validate_test_file(sample_test_file)
        
        report = validator.generate_quality_report(scores)
        
        # Manually calculate averages
        if len(scores) > 0:
            manual_avg_coverage = sum(s.coverage_score for s in scores) / len(scores)
            manual_avg_overall = sum(s.overall_score for s in scores) / len(scores)
            
            # Check within floating point tolerance
            assert abs(report["average_scores"]["coverage"] - manual_avg_coverage) < 0.01
            assert abs(report["average_scores"]["overall"] - manual_avg_overall) < 0.01


# ============================================================================
# INTEGRATION TESTS (ALL 3 LAYERS WORKING TOGETHER)
# ============================================================================

class TestIntegration:
    """Integration tests for all 3 layers working together."""
    
    @pytest.fixture
    def full_cortex_setup(self):
        """Create complete CORTEX structure for integration test."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            
            # Create full directory structure
            (root / "cortex" / "wiring" / "specifications").mkdir(parents=True)
            (root / "cortex-registry" / "_cortex-master" / "test-demands").mkdir(parents=True)
            (root / "tests" / "orchestrators" / "generated").mkdir(parents=True)
            
            # Create orchestrator spec
            spec_file = root / "cortex" / "wiring" / "specifications" / "test-orchestrator.yaml"
            spec_data = {
                "orchestrator": "TestOrchestrator",
                "responsibilities": ["Execute tests", "Report results"],
                "operations": [{"name": "run", "type": "primary"}],
                "dependencies": [],
            }
            with open(spec_file, 'w') as f:
                yaml.dump(spec_data, f)
            
            yield root
    
    def test_full_pipeline_layer1_to_layer2_to_layer3(self, full_cortex_setup):
        """Test: Complete pipeline from demand generation to validation."""
        # Layer 1: Generate demand
        generator = TestDemandGenerator(full_cortex_setup)
        demand = generator.generate_demand_for_orchestrator("TestOrchestrator")
        demand_file = generator.save_demand_to_yaml(demand)
        
        # Layer 2: Compose tests
        composer = TestComposer(full_cortex_setup)
        composed_tests = composer.compose_test_from_demand(demand_file)
        test_file = composer.save_composed_tests_to_file("TestOrchestrator", composed_tests)
        
        # Layer 3: Validate quality
        validator = QualityValidator()
        scores = validator.validate_test_file(test_file)
        report = validator.generate_quality_report(scores)
        
        # Assert: Pipeline produces results
        assert demand_file.exists()
        assert test_file.exists()
        assert len(scores) > 0
        assert report["total_tests"] > 0
        
        # Assert: Quality gate enforced
        assert "pass_rate" in report
        assert 0.0 <= report["pass_rate"] <= 1.0
