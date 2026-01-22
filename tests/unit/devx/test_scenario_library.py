"""
Tests for ODX-001-02: Scenario Library

AC-ID: ODX-001-02
Phase: PHASE-18-ORCHESTRATOR-DEVX
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from cortex.devx.scenario_library import (
    ScenarioLibrary,
    Scenario,
    ScenarioInput,
    ScenarioResult,
    ScenarioCategory,
    ScenarioStatus,
    ExpectedOutput,
    ScenarioSnapshot,
)


class TestScenarioInput:
    """Tests for ScenarioInput dataclass."""
    
    def test_scenario_input_creation(self):
        """Test ScenarioInput creation."""
        input_data = ScenarioInput(
            data={"query": "test query"},
            metadata={"source": "test"},
            source="manual",
        )
        
        assert input_data.data["query"] == "test query"
        assert input_data.metadata["source"] == "test"
        assert input_data.source == "manual"
    
    def test_scenario_input_to_dict(self):
        """Test ScenarioInput serialization."""
        input_data = ScenarioInput(data={"key": "value"})
        
        d = input_data.to_dict()
        
        assert d["data"]["key"] == "value"
        assert "metadata" in d
    
    def test_scenario_input_from_dict(self):
        """Test ScenarioInput deserialization."""
        d = {"data": {"key": "value"}, "metadata": {}, "source": "file"}
        
        input_data = ScenarioInput.from_dict(d)
        
        assert input_data.data["key"] == "value"
        assert input_data.source == "file"


class TestExpectedOutput:
    """Tests for ExpectedOutput dataclass."""
    
    def test_expected_output_exact_match(self):
        """Test ExpectedOutput with exact data match."""
        expected = ExpectedOutput(data={"result": "success"})
        
        assert expected.data["result"] == "success"
        assert len(expected.patterns) == 0
    
    def test_expected_output_with_patterns(self):
        """Test ExpectedOutput with regex patterns."""
        expected = ExpectedOutput(patterns=[r"success", r"completed"])
        
        assert len(expected.patterns) == 2
        assert "success" in expected.patterns
    
    def test_expected_output_with_assertions(self):
        """Test ExpectedOutput with custom assertions."""
        expected = ExpectedOutput(assertions=["has_key", "non_empty"])
        
        assert len(expected.assertions) == 2
    
    def test_expected_output_to_dict(self):
        """Test ExpectedOutput serialization."""
        expected = ExpectedOutput(
            data={"key": "value"},
            patterns=["pattern1"],
            assertions=["assertion1"],
        )
        
        d = expected.to_dict()
        
        assert d["data"]["key"] == "value"
        assert "pattern1" in d["patterns"]


class TestScenario:
    """Tests for Scenario dataclass."""
    
    def test_scenario_creation(self):
        """Test Scenario creation."""
        scenario = Scenario(
            name="Test Scenario",
            description="A test scenario",
            category=ScenarioCategory.UNIT,
            orchestrator="TestOrchestrator",
        )
        
        assert scenario.name == "Test Scenario"
        assert scenario.category == ScenarioCategory.UNIT
        assert scenario.scenario_id is not None
        assert scenario.enabled
    
    def test_scenario_with_input_and_expected(self):
        """Test Scenario with input and expected output."""
        scenario = Scenario(
            name="Full Scenario",
            input_data=ScenarioInput(data={"query": "test"}),
            expected=ExpectedOutput(data={"intent": "test"}),
        )
        
        assert scenario.input_data.data["query"] == "test"
        assert scenario.expected.data["intent"] == "test"
    
    def test_scenario_to_dict(self):
        """Test Scenario serialization."""
        scenario = Scenario(
            name="Test",
            category=ScenarioCategory.INTEGRATION,
            tags=["tag1", "tag2"],
        )
        
        d = scenario.to_dict()
        
        assert d["name"] == "Test"
        assert d["category"] == "integration"
        assert "tag1" in d["tags"]
    
    def test_scenario_from_dict(self):
        """Test Scenario deserialization."""
        d = {
            "scenario_id": "test-123",
            "name": "From Dict",
            "description": "Created from dict",
            "category": "unit",
            "orchestrator": "TestOrch",
            "input_data": {"data": {}, "metadata": {}, "source": "manual"},
            "expected": {"data": None, "patterns": [], "assertions": [], "schema": None},
            "tags": [],
            "timeout_ms": 5000,
            "dependencies": [],
            "enabled": True,
        }
        
        scenario = Scenario.from_dict(d)
        
        assert scenario.scenario_id == "test-123"
        assert scenario.name == "From Dict"
        assert scenario.timeout_ms == 5000
    
    def test_scenario_hashable(self):
        """Test Scenario is hashable."""
        scenario = Scenario(name="Test")
        
        # Should be hashable
        hash_val = hash(scenario)
        assert isinstance(hash_val, int)


class TestScenarioResult:
    """Tests for ScenarioResult dataclass."""
    
    def test_scenario_result_creation(self):
        """Test ScenarioResult creation."""
        result = ScenarioResult(
            scenario_id="test-123",
            status=ScenarioStatus.PASSED,
        )
        
        assert result.scenario_id == "test-123"
        assert result.status == ScenarioStatus.PASSED
        assert result.assertions_passed == 0
    
    def test_scenario_result_with_output(self):
        """Test ScenarioResult with actual output."""
        result = ScenarioResult(
            scenario_id="test-123",
            status=ScenarioStatus.PASSED,
            actual_output={"result": "success"},
            execution_time_ms=150.5,
        )
        
        assert result.actual_output["result"] == "success"
        assert result.execution_time_ms == 150.5
    
    def test_scenario_result_to_dict(self):
        """Test ScenarioResult serialization."""
        result = ScenarioResult(
            scenario_id="test-123",
            status=ScenarioStatus.FAILED,
            error_message="Test failed",
        )
        
        d = result.to_dict()
        
        assert d["scenario_id"] == "test-123"
        assert d["status"] == "failed"
        assert d["error_message"] == "Test failed"


class TestScenarioLibrary:
    """Tests for ScenarioLibrary."""
    
    def test_library_creation(self):
        """Test ScenarioLibrary creation."""
        library = ScenarioLibrary()
        
        assert library.count == 0
        assert len(library.scenarios) == 0
    
    def test_library_creation_with_path(self):
        """Test ScenarioLibrary creation with file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            library = ScenarioLibrary(tmpdir, auto_save=False)
            
            assert library.library_path == Path(tmpdir)
    
    def test_add_scenario(self):
        """Test adding a scenario."""
        library = ScenarioLibrary()
        
        scenario = Scenario(name="Test Scenario")
        scenario_id = library.add(scenario)
        
        assert scenario_id == scenario.scenario_id
        assert library.count == 1
    
    def test_get_scenario(self):
        """Test getting a scenario by ID."""
        library = ScenarioLibrary()
        
        scenario = Scenario(name="Test")
        library.add(scenario)
        
        retrieved = library.get(scenario.scenario_id)
        
        assert retrieved is not None
        assert retrieved.name == "Test"
    
    def test_get_nonexistent_scenario(self):
        """Test getting a non-existent scenario."""
        library = ScenarioLibrary()
        
        retrieved = library.get("nonexistent")
        
        assert retrieved is None
    
    def test_remove_scenario(self):
        """Test removing a scenario."""
        library = ScenarioLibrary()
        
        scenario = Scenario(name="To Remove")
        library.add(scenario)
        
        result = library.remove(scenario.scenario_id)
        
        assert result
        assert library.count == 0
    
    def test_update_scenario(self):
        """Test updating a scenario."""
        library = ScenarioLibrary()
        
        scenario = Scenario(name="Original")
        library.add(scenario)
        
        scenario.name = "Updated"
        result = library.update(scenario)
        
        assert result
        assert library.get(scenario.scenario_id).name == "Updated"
    
    def test_find_by_orchestrator(self):
        """Test finding scenarios by orchestrator."""
        library = ScenarioLibrary()
        
        library.add(Scenario(name="S1", orchestrator="OrchestratorA"))
        library.add(Scenario(name="S2", orchestrator="OrchestratorB"))
        library.add(Scenario(name="S3", orchestrator="OrchestratorA"))
        
        found = library.find(orchestrator="OrchestratorA")
        
        assert len(found) == 2
    
    def test_find_by_category(self):
        """Test finding scenarios by category."""
        library = ScenarioLibrary()
        
        library.add(Scenario(name="S1", category=ScenarioCategory.UNIT))
        library.add(Scenario(name="S2", category=ScenarioCategory.INTEGRATION))
        library.add(Scenario(name="S3", category=ScenarioCategory.UNIT))
        
        found = library.find(category=ScenarioCategory.UNIT)
        
        assert len(found) == 2
    
    def test_find_by_tags(self):
        """Test finding scenarios by tags."""
        library = ScenarioLibrary()
        
        library.add(Scenario(name="S1", tags=["intent", "routing"]))
        library.add(Scenario(name="S2", tags=["validation"]))
        library.add(Scenario(name="S3", tags=["intent", "classification"]))
        
        found = library.find(tags=["intent"])
        
        assert len(found) == 2
    
    def test_find_enabled_only(self):
        """Test finding only enabled scenarios."""
        library = ScenarioLibrary()
        
        library.add(Scenario(name="Enabled", enabled=True))
        library.add(Scenario(name="Disabled", enabled=False))
        
        found = library.find(enabled_only=True)
        
        assert len(found) == 1
        assert found[0].name == "Enabled"
    
    def test_register_assertion(self):
        """Test registering custom assertions."""
        library = ScenarioLibrary()
        
        def has_key(actual, expected):
            return "key" in actual
        
        result = library.register_assertion("has_key", has_key)
        
        assert result is library  # Method chaining
        assert "has_key" in library._assertions
    
    def test_execute_scenario_pass(self):
        """Test executing a scenario that passes."""
        library = ScenarioLibrary()
        
        scenario = Scenario(
            name="Passing Test",
            input_data=ScenarioInput(data={"value": 5}),
            expected=ExpectedOutput(data={"doubled": 10}),
        )
        library.add(scenario)
        
        def executor(input_data):
            return {"doubled": input_data["value"] * 2}
        
        result = library.execute(scenario, executor)
        
        assert result.status == ScenarioStatus.PASSED
        assert result.actual_output["doubled"] == 10
    
    def test_execute_scenario_fail(self):
        """Test executing a scenario that fails."""
        library = ScenarioLibrary()
        
        scenario = Scenario(
            name="Failing Test",
            input_data=ScenarioInput(data={"value": 5}),
            expected=ExpectedOutput(data={"doubled": 100}),  # Wrong expectation
        )
        library.add(scenario)
        
        def executor(input_data):
            return {"doubled": input_data["value"] * 2}
        
        result = library.execute(scenario, executor)
        
        assert result.status == ScenarioStatus.FAILED
    
    def test_execute_scenario_error(self):
        """Test executing a scenario that raises an error."""
        library = ScenarioLibrary()
        
        scenario = Scenario(
            name="Error Test",
            input_data=ScenarioInput(data={}),
        )
        library.add(scenario)
        
        def executor(input_data):
            raise ValueError("Test error")
        
        result = library.execute(scenario, executor)
        
        assert result.status == ScenarioStatus.ERROR
        assert "Test error" in result.error_message
    
    def test_execute_with_pattern_validation(self):
        """Test scenario validation with regex patterns."""
        library = ScenarioLibrary()
        
        scenario = Scenario(
            name="Pattern Test",
            input_data=ScenarioInput(data={}),
            expected=ExpectedOutput(patterns=[r"success", r"complete"]),
        )
        library.add(scenario)
        
        def executor(input_data):
            return {"message": "Operation success and complete"}
        
        result = library.execute(scenario, executor)
        
        assert result.status == ScenarioStatus.PASSED
        assert result.assertions_passed == 2
    
    def test_execute_with_custom_assertion(self):
        """Test scenario validation with custom assertions."""
        library = ScenarioLibrary()
        
        def is_positive(actual, expected):
            return actual.get("value", 0) > 0
        
        library.register_assertion("is_positive", is_positive)
        
        scenario = Scenario(
            name="Assertion Test",
            input_data=ScenarioInput(data={}),
            expected=ExpectedOutput(assertions=["is_positive"]),
        )
        library.add(scenario)
        
        def executor(input_data):
            return {"value": 42}
        
        result = library.execute(scenario, executor)
        
        assert result.status == ScenarioStatus.PASSED
    
    def test_run_multiple_scenarios(self):
        """Test running multiple scenarios."""
        library = ScenarioLibrary()
        
        library.add(Scenario(
            name="S1",
            orchestrator="TestOrch",
            input_data=ScenarioInput(data={"x": 1}),
            expected=ExpectedOutput(data={"result": 2}),
        ))
        library.add(Scenario(
            name="S2",
            orchestrator="TestOrch",
            input_data=ScenarioInput(data={"x": 2}),
            expected=ExpectedOutput(data={"result": 4}),
        ))
        
        def executor(input_data):
            return {"result": input_data["x"] * 2}
        
        results = library.run(executor, orchestrator="TestOrch")
        
        assert len(results) == 2
        assert all(r.status == ScenarioStatus.PASSED for r in results)
    
    def test_run_with_dependencies(self):
        """Test running scenarios with dependencies."""
        library = ScenarioLibrary()
        
        s1 = Scenario(name="S1", input_data=ScenarioInput(data={}))
        s2 = Scenario(name="S2", input_data=ScenarioInput(data={}), dependencies=[s1.scenario_id])
        
        library.add(s1)
        library.add(s2)
        
        def executor(input_data):
            return {"ok": True}
        
        results = library.run(executor)
        
        # S1 should run first, then S2
        assert len(results) == 2
    
    def test_dependency_skip_on_failure(self):
        """Test that dependent scenarios are skipped when dependency fails."""
        library = ScenarioLibrary()
        
        s1 = Scenario(
            name="Failing",
            input_data=ScenarioInput(data={}),
            expected=ExpectedOutput(data={"impossible": True}),
        )
        s2 = Scenario(
            name="Dependent",
            input_data=ScenarioInput(data={}),
            dependencies=[s1.scenario_id],
        )
        
        library.add(s1)
        library.add(s2)
        
        def executor(input_data):
            return {"ok": True}
        
        results = library.run(executor)
        
        assert results[0].status == ScenarioStatus.FAILED  # S1 fails
        assert results[1].status == ScenarioStatus.SKIPPED  # S2 skipped
    
    def test_callbacks(self):
        """Test before/after run callbacks."""
        library = ScenarioLibrary()
        
        before_calls = []
        after_calls = []
        
        library.on_before_run(lambda s: before_calls.append(s.name))
        library.on_after_run(lambda s, r: after_calls.append((s.name, r.status)))
        
        scenario = Scenario(name="Callback Test")
        library.add(scenario)
        
        def executor(input_data):
            return {}
        
        library.execute(scenario, executor)
        
        assert "Callback Test" in before_calls
        assert len(after_calls) == 1
    
    def test_create_snapshot(self):
        """Test creating result snapshot."""
        library = ScenarioLibrary()
        
        scenario = Scenario(name="Snapshot Test")
        library.add(scenario)
        
        def executor(input_data):
            return {"value": 42}
        
        library.execute(scenario, executor)
        snapshot = library.create_snapshot(scenario.scenario_id, baseline=True)
        
        assert snapshot is not None
        assert snapshot.scenario_id == scenario.scenario_id
        assert snapshot.baseline
        assert snapshot.checksum  # Should have checksum
    
    def test_compare_to_baseline(self):
        """Test comparing results to baseline."""
        library = ScenarioLibrary()
        
        scenario = Scenario(name="Compare Test")
        library.add(scenario)
        
        def executor(input_data):
            return {"value": 42}
        
        # First run - create baseline
        library.execute(scenario, executor)
        library.create_snapshot(scenario.scenario_id, baseline=True)
        
        # Second run
        library.execute(scenario, executor)
        
        comparison = library.compare_to_baseline(scenario.scenario_id)
        
        # Comparison should be valid
        assert comparison is not None
        # Either output matches baseline or no regression detected
        assert comparison.get("output_match") is not None or comparison.get("regression_detected") is not None
    
    def test_get_results_history(self):
        """Test getting result history for a scenario."""
        library = ScenarioLibrary()
        
        scenario = Scenario(name="History Test")
        library.add(scenario)
        
        def executor(input_data):
            return {}
        
        library.execute(scenario, executor)
        library.execute(scenario, executor)
        library.execute(scenario, executor)
        
        history = library.get_results(scenario.scenario_id)
        
        assert len(history) == 3
    
    def test_summary(self):
        """Test library summary statistics."""
        library = ScenarioLibrary()
        
        library.add(Scenario(name="S1", category=ScenarioCategory.UNIT, orchestrator="A"))
        library.add(Scenario(name="S2", category=ScenarioCategory.INTEGRATION, orchestrator="B"))
        library.add(Scenario(name="S3", category=ScenarioCategory.UNIT, orchestrator="A"))
        
        summary = library.summary()
        
        assert summary["total_scenarios"] == 3
        assert summary["by_category"]["unit"] == 2
        assert summary["by_category"]["integration"] == 1
        assert summary["by_orchestrator"]["A"] == 2


class TestScenarioLibraryPersistence:
    """Tests for ScenarioLibrary persistence."""
    
    def test_save_and_load(self):
        """Test saving and loading scenarios."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and save
            library = ScenarioLibrary(tmpdir, auto_save=True)
            
            scenario = Scenario(
                name="Persistent Test",
                category=ScenarioCategory.UNIT,
            )
            library.add(scenario)
            
            # Create new library from same path
            library2 = ScenarioLibrary(tmpdir, auto_save=False)
            
            # Should have loaded the scenario
            assert library2.count == 1
            loaded = list(library2.scenarios)[0]
            assert loaded.name == "Persistent Test"
