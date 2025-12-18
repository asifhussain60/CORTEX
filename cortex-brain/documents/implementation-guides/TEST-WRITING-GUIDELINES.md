# CORTEX 4.0 Test Writing Guidelines

**Version:** 1.0 | **Author:** Asif Hussain | **Date:** December 18, 2025

This guide explains how to write tests for CORTEX 4.0 using the established testing infrastructure.

---

## 📋 Quick Start

```python
import pytest
from tests.utils import (
    create_cortex_config,
    TempWorkspaceManager,
    ConfigFileBuilder,
    AssertionHelpers
)

@pytest.mark.unit
@pytest.mark.cortex_v4
def test_my_feature(cortex_workspace):
    """Test description following docstring conventions"""
    # Arrange
    config = create_cortex_config(workspace_root=cortex_workspace)
    
    # Act
    result = my_function(config)
    
    # Assert
    assert result.success
```

---

## 🏗️ Test Structure

### Arrange-Act-Assert Pattern

```python
def test_example(cortex_workspace):
    # ARRANGE - Setup test data and fixtures
    config = create_cortex_config(workspace_root=cortex_workspace)
    
    # ACT - Execute the code under test
    result = execute_feature(config)
    
    # ASSERT - Verify expected outcomes
    assert result.success
    assert result.data["key"] == "expected_value"
```

---

## 🎨 Available Fixtures

### Workspace Fixtures

#### `cortex_workspace` - Full CORTEX workspace structure
```python
def test_with_full_workspace(cortex_workspace):
    # cortex_workspace includes:
    # - cortex-brain/tier0, tier1, tier2, tier3
    # - cortex-brain/config/
    # - cortex-brain/documents/{reports, analysis, etc}
    assert (cortex_workspace / "cortex-brain").exists()
```

#### `temp_workspace` - Simple temporary directory
```python
def test_with_simple_workspace(temp_workspace):
    # Just a temporary directory, no CORTEX structure
    test_file = temp_workspace / "test.txt"
    test_file.write_text("content")
```

### Configuration Fixtures

#### `shared_config` - Workspace shared configuration
```python
def test_with_shared_config(cortex_workspace, shared_config):
    # shared_config is pre-created at:
    # {workspace}/cortex-brain/config/shared.config.json
    assert shared_config["brain"]["max_conversations"] == 70
```

#### `vscode_config` - VSCode-specific configuration
```python
def test_with_vscode_config(cortex_workspace, vscode_config):
    # vscode_config is pre-created at:
    # {workspace}/cortex-brain/config/vscode.config.json
    assert vscode_config["ide"]["integration_mode"] == "copilot_chat"
```

#### `config_manager` - ConfigManager instance
```python
def test_with_config_manager(config_manager):
    # Pre-initialized ConfigManager with test workspace
    config = config_manager.load()
    assert isinstance(config, CortexConfig)
```

#### `cortex_config` - Loaded CortexConfig
```python
def test_with_config(cortex_config):
    # Pre-loaded configuration object
    assert cortex_config.workspace_root.exists()
    assert cortex_config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]
```

### IDE Detection Fixtures

#### `mock_ide_detector_vscode` - Mock VSCode detection
```python
def test_vscode_feature(mock_ide_detector_vscode):
    # IDEDetector.detect() will return IDEType.VSCODE
    assert mock_ide_detector_vscode == IDEType.VSCODE
```

#### `mock_ide_detector_visualstudio` - Mock Visual Studio detection
```python
def test_vs_feature(mock_ide_detector_visualstudio):
    # IDEDetector.detect() will return IDEType.VISUAL_STUDIO
    pass
```

#### `reset_ide_detector_cache` - Clear IDE detection cache
```python
@pytest.mark.usefixtures("reset_ide_detector_cache")
def test_with_clean_ide_cache():
    # IDE detector cache is cleared before and after test
    pass
```

### Orchestrator Fixtures

#### `mock_orchestrator` - Simple test orchestrator
```python
def test_orchestrator(mock_orchestrator):
    result = mock_orchestrator.execute()
    assert result.success
    assert result.status == OrchestratorStatus.COMPLETED
```

---

## 🛠️ Test Utilities

### MockFactory - Create test objects

```python
from tests.utils import MockFactory

# Create CortexConfig
config = MockFactory.create_cortex_config(
    workspace_root=tmp_path,
    log_level="DEBUG",
    max_conversation_history=50
)

# Create OrchestratorResult
result = MockFactory.create_orchestrator_result(
    status=OrchestratorStatus.COMPLETED,
    success=True,
    message="Test completed"
)

# Create config dict
config_dict = MockFactory.create_config_dict(
    workspace_root=tmp_path,
    brain={"max_conversations": 150}
)
```

### TempWorkspaceManager - Temporary workspace context manager

```python
from tests.utils import TempWorkspaceManager

def test_with_temp_workspace():
    with TempWorkspaceManager() as workspace:
        # workspace has full CORTEX brain structure
        assert (workspace / "cortex-brain" / "tier1").exists()
        
        # Do your testing
        test_file = workspace / "test.txt"
        test_file.write_text("content")
    
    # Workspace automatically cleaned up after context manager
```

### ConfigFileBuilder - Build configuration files

```python
from tests.utils import ConfigFileBuilder

def test_with_custom_configs(temp_config_dir):
    builder = ConfigFileBuilder(temp_config_dir)
    
    # Chain multiple config additions
    builder \
        .add_shared_config({"brain": {"max_conversations": 70}}) \
        .add_vscode_config({"ide": {"integration_mode": "copilot_chat"}}) \
        .add_corrupted_config("bad.json")  # For error testing
    
    # Files are created in temp_config_dir
    assert (temp_config_dir / "shared.config.json").exists()
```

### AssertionHelpers - Common assertions

```python
from tests.utils import AssertionHelpers

def test_with_helpers(tmp_path, cortex_config):
    # Assert config has keys
    AssertionHelpers.assert_config_has_keys(config_dict, "brain", "orchestrator")
    
    # Assert path exists
    AssertionHelpers.assert_path_exists(tmp_path / "some_file.txt")
    
    # Assert file contains content
    AssertionHelpers.assert_file_contains(tmp_path / "file.txt", "expected text")
    
    # Assert orchestrator success
    AssertionHelpers.assert_orchestrator_success(result)
    
    # Assert no errors
    AssertionHelpers.assert_no_errors(result)
```

### TestIsolation - Cleanup utilities

```python
from tests.utils import TestIsolation

def test_with_cleanup():
    # Clear environment variables
    TestIsolation.clear_environment_vars("TEST_VAR_1", "TEST_VAR_2")
    
    # Cleanup temporary files
    TestIsolation.cleanup_temp_files(file1, file2, directory)
```

---

## 🏷️ Test Markers

### Use markers to categorize tests

```python
@pytest.mark.unit  # Fast unit test (<100ms)
@pytest.mark.integration  # Integration test (100ms-1s)
@pytest.mark.slow  # Slow test (>1s)
@pytest.mark.fast  # Very fast test (<100ms)
@pytest.mark.e2e  # End-to-end test

@pytest.mark.cortex_v4  # CORTEX 4.0 feature
@pytest.mark.cortex_internal  # Internal CORTEX test

@pytest.mark.config_test  # Configuration system
@pytest.mark.orchestrator_test  # Orchestrator
@pytest.mark.template_test  # Response templates
@pytest.mark.brain_test  # Brain tiers

@pytest.mark.requires_git  # Needs git repo
@pytest.mark.requires_ide  # Needs IDE
@pytest.mark.requires_network  # Needs network
```

### Example with markers

```python
@pytest.mark.unit
@pytest.mark.config_test
@pytest.mark.cortex_v4
def test_config_loading(config_manager):
    """Unit test for configuration loading"""
    config = config_manager.load()
    assert config.workspace_root.exists()
```

---

## 📊 Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/core/test_config_system.py
```

### Run specific test
```bash
pytest tests/core/test_config_system.py::TestConfigManager::test_load
```

### Run by marker
```bash
pytest -m unit  # Only unit tests
pytest -m "unit and config_test"  # Unit tests for config
pytest -m "not slow"  # Exclude slow tests
```

### Run with coverage
```bash
pytest --cov=src --cov-report=term-missing
pytest --cov=src --cov-report=html  # HTML report in htmlcov/
```

### Run with verbose output
```bash
pytest -v  # Verbose
pytest -vv  # Very verbose
pytest -s  # Show print statements
```

---

## 🎯 Test Writing Best Practices

### 1. Test Naming
- Use descriptive names: `test_config_loads_with_environment_overrides`
- Follow pattern: `test_{what}_{when}_{expected_result}`

### 2. Docstrings
```python
def test_example():
    """
    Test that configuration loads correctly with environment overrides.
    
    Given: A workspace with shared.config.json
    When: CORTEX_MAX_CONVERSATIONS environment variable is set
    Then: config.max_conversations should use environment value
    """
```

### 3. Arrange-Act-Assert
- Clearly separate setup, execution, and verification
- Use comments to mark sections in complex tests

### 4. One Assertion Per Test (when possible)
```python
# GOOD
def test_config_workspace_root():
    config = create_cortex_config(workspace_root=tmp_path)
    assert config.workspace_root == tmp_path

def test_config_log_level():
    config = create_cortex_config(workspace_root=tmp_path, log_level="DEBUG")
    assert config.log_level == "DEBUG"

# OK (related assertions)
def test_config_creation():
    config = create_cortex_config(workspace_root=tmp_path)
    assert config.workspace_root == tmp_path
    assert config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]
```

### 5. Test Independence
- Each test should run independently
- Don't rely on test execution order
- Use fixtures for shared setup

### 6. Use Fixtures for Repetitive Setup
```python
@pytest.fixture
def sample_config():
    return {"brain": {"max_conversations": 70}}

def test_with_sample(sample_config):
    assert sample_config["brain"]["max_conversations"] == 70
```

### 7. Parametrize for Similar Tests
```python
@pytest.mark.parametrize("ide_type,expected_filename", [
    (IDEType.VSCODE, "vscode.config.json"),
    (IDEType.VISUAL_STUDIO, "visualstudio.config.json"),
    (IDEType.UNKNOWN, "unknown.config.json"),
])
def test_config_filename(ide_type, expected_filename):
    filename = IDEDetector.get_config_filename(ide_type)
    assert filename == expected_filename
```

---

## 🚨 Common Pitfalls

### 1. Hardcoded Paths
```python
# BAD
config_file = Path("D:/PROJECTS/CORTEX/cortex-brain/config/shared.config.json")

# GOOD
config_file = cortex_workspace / "cortex-brain" / "config" / "shared.config.json"
```

### 2. Missing Cleanup
```python
# BAD
def test_example():
    os.environ["TEST_VAR"] = "value"
    # Test code...
    # TEST_VAR not cleaned up!

# GOOD
def test_example():
    with patch.dict(os.environ, {"TEST_VAR": "value"}, clear=False):
        # Test code...
    # Automatically cleaned up
```

### 3. Flaky Tests
```python
# BAD
def test_timing():
    start = time.time()
    do_work()
    assert time.time() - start < 0.1  # Flaky!

# GOOD
def test_work():
    result = do_work()
    assert result.success
    # Separate performance tests with @pytest.mark.performance
```

### 4. Testing Implementation Instead of Behavior
```python
# BAD
def test_internal_method():
    obj = MyClass()
    assert obj._internal_state == "expected"

# GOOD
def test_public_behavior():
    obj = MyClass()
    result = obj.public_method()
    assert result == "expected"
```

---

## 📈 Coverage Guidelines

### Target Coverage
- **Core modules**: 90%+ coverage
- **Orchestrators**: 80%+ coverage
- **Utilities**: 70%+ coverage
- **Overall**: 85%+ coverage

### Check Coverage
```bash
pytest --cov=src --cov-report=term-missing
```

### View HTML Report
```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html
```

### Exclude from Coverage
Add to `.coveragerc`:
```ini
[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if __name__ == .__main__.:
```

---

## 🔍 Debugging Tests

### Print Debugging
```bash
pytest -s  # Show print statements
```

### Verbose Output
```bash
pytest -vv  # Very verbose
pytest --tb=short  # Short traceback
pytest --tb=long  # Long traceback
```

### Run Single Test
```bash
pytest tests/core/test_config.py::test_specific_test -vv
```

### Drop into Debugger on Failure
```bash
pytest --pdb  # Drop into pdb on failure
pytest --pdbcls=IPython.terminal.debugger:Pdb  # Use IPython debugger
```

---

## 📝 Example Test File

```python
"""
Tests for MyFeature

Copyright © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from tests.utils import create_cortex_config, AssertionHelpers

@pytest.mark.unit
@pytest.mark.cortex_v4
class TestMyFeature:
    """Test suite for MyFeature"""
    
    def test_basic_functionality(self, cortex_workspace):
        """Test basic feature functionality"""
        # Arrange
        config = create_cortex_config(workspace_root=cortex_workspace)
        feature = MyFeature(config)
        
        # Act
        result = feature.execute()
        
        # Assert
        assert result.success
        assert result.data["key"] == "expected"
    
    @pytest.mark.parametrize("input,expected", [
        ("foo", "FOO"),
        ("bar", "BAR"),
    ])
    def test_transformation(self, input, expected):
        """Test input transformation"""
        result = transform(input)
        assert result == expected
    
    def test_error_handling(self):
        """Test error handling with invalid input"""
        with pytest.raises(ValueError, match="Invalid input"):
            MyFeature(invalid_input)
```

---

## 🎓 Additional Resources

- **pytest documentation**: https://docs.pytest.org/
- **CORTEX Test Infrastructure**: `tests/utils/test_utilities.py`
- **Example Tests**: `tests/infrastructure/test_testing_infrastructure.py`
- **Configuration Tests**: `tests/core/test_config_system.py`

---

**Quick Reference:**
- Fixtures: `cortex_workspace`, `config_manager`, `cortex_config`
- Utilities: `MockFactory`, `TempWorkspaceManager`, `ConfigFileBuilder`
- Markers: `@pytest.mark.unit`, `@pytest.mark.cortex_v4`
- Run: `pytest -m unit -v`

**Version:** 1.0 | **Author:** Asif Hussain | **Date:** December 18, 2025
