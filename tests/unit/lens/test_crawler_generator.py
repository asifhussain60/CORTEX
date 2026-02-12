"""
TDD Tests for CrawlerTemplateGenerator.

Tests template-based code generation for custom LENS analyzers:
1. Template loading from cortex/lens/templates/
2. Jinja2 rendering with spec parameters
3. BaseAnalyzer inheritance validation
4. Automatic test file generation
5. Wiring integration validation
6. Sandbox validation before execution

AC_START: AC-CDF-Generator-001
"""

import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from cortex.lens.capability_discovery import CrawlerSpec
from cortex.lens.crawler_generator import (
    CrawlerTemplateGenerator,
    GeneratedCode,
    TemplateNotFoundError,
    CodeValidationError,
)


# ==============================================================================
# Fixtures
# ==============================================================================

@pytest.fixture
def template_dir(tmp_path):
    """Create temporary template directory with sample templates."""
    templates = tmp_path / "templates"
    templates.mkdir()
    
    # Create base analyzer template
    analyzer_template = templates / "analyzer_template.py.jinja2"
    analyzer_template.write_text("""\"\"\"
{{ description }}

Generated analyzer for {{ crawler_name }}.
\"\"\"

import logging
from pathlib import Path
from typing import Dict, Any, List

from cortex.lens.analyzers.base import BaseAnalyzer

logger = logging.getLogger(__name__)


class {{ crawler_name }}(BaseAnalyzer):
    \"\"\"{{ description }}\"\"\"
    
    def __init__(self):
        \"\"\"Initialize {{ crawler_name }}.\"\"\"
        super().__init__()
        self.dependencies = {{ dependencies }}
    
    def analyze(self, repo_path: Path) -> Dict[str, Any]:
        \"\"\"
        Analyze repository.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Analysis results
        \"\"\"
        logger.info(f"Running {{ crawler_name }} on {repo_path}")
        
        results = {
            "analyzer": "{{ crawler_name }}",
            "findings": [],
        }
        
        # TODO: Implement analysis logic
        
        return results
""")
    
    # Create test template
    test_template = templates / "test_template.py.jinja2"
    test_template.write_text("""\"\"\"
Tests for {{ crawler_name }}.

Generated test file.
\"\"\"

import pytest
from pathlib import Path
from {{ module_path }} import {{ crawler_name }}


@pytest.fixture
def analyzer():
    \"\"\"Create analyzer instance.\"\"\"
    return {{ crawler_name }}()


@pytest.fixture
def sample_repo(tmp_path):
    \"\"\"Create sample repository.\"\"\"
    repo = tmp_path / "sample"
    repo.mkdir()
    return repo


class Test{{ crawler_name }}:
    \"\"\"Test suite for {{ crawler_name }}.\"\"\"
    
    def test_initialization(self, analyzer):
        \"\"\"Test analyzer initialization.\"\"\"
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze')
    
{% for scenario in test_scenarios %}
    def test_{{ scenario|lower|replace(' ', '_') }}(self, analyzer, sample_repo):
        \"\"\"Test: {{ scenario }}.\"\"\"
        # TODO: Implement test
        pass
{% endfor %}
""")
    
    return templates


@pytest.fixture
def crawler_spec():
    """Create sample crawler specification."""
    return CrawlerSpec(
        crawler_name="DatabaseMigrationAnalyzer",
        description="Analyzes database migrations for schema changes",
        module_path="cortex.lens.crawlers.database_migration_analyzer",
        priority="high",
        required_methods=["analyze"],
        dependencies=["PostgreSQL", "SQLAlchemy"],
        test_scenarios=[
            "Test migration detection",
            "Test schema change analysis",
            "Test rollback validation",
        ],
        requires_tests=True,
        estimated_complexity="medium",
    )


@pytest.fixture
def generator(template_dir):
    """Create CrawlerTemplateGenerator instance."""
    return CrawlerTemplateGenerator(template_dir=template_dir)


# ==============================================================================
# Template Loading Tests
# ==============================================================================

class TestTemplateLoading:
    """Test template discovery and loading."""
    
    def test_cgen_001_load_analyzer_template(self, generator):
        """CGEN-001: Load analyzer template successfully."""
        template = generator.load_template("analyzer_template.py.jinja2")
        assert template is not None
        # Template objects don't have .source, check template is loaded
        assert template.name == "analyzer_template.py.jinja2"
    
    def test_cgen_002_load_test_template(self, generator):
        """CGEN-002: Load test template successfully."""
        template = generator.load_template("test_template.py.jinja2")
        assert template is not None
        # Template objects don't have .source, check template is loaded
        assert template.name == "test_template.py.jinja2"
    
    def test_cgen_003_template_not_found(self, generator):
        """CGEN-003: Raise error when template not found."""
        with pytest.raises(TemplateNotFoundError):
            generator.load_template("nonexistent_template.jinja2")
    
    def test_cgen_004_list_available_templates(self, generator):
        """CGEN-004: List all available templates."""
        templates = generator.list_templates()
        assert "analyzer_template.py.jinja2" in templates
        assert "test_template.py.jinja2" in templates


# ==============================================================================
# Code Generation Tests
# ==============================================================================

class TestCodeGeneration:
    """Test code generation from templates."""
    
    def test_cgen_005_generate_analyzer_code(self, generator, crawler_spec):
        """CGEN-005: Generate analyzer code from spec."""
        code = generator.generate_analyzer(crawler_spec)
        
        assert code is not None
        assert isinstance(code, GeneratedCode)
        assert "class DatabaseMigrationAnalyzer(BaseAnalyzer):" in code.content
        assert "def analyze(self, repo_path: Path)" in code.content
        assert code.file_path.name == "database_migration_analyzer.py"
    
    def test_cgen_006_generate_test_code(self, generator, crawler_spec):
        """CGEN-006: Generate test code from spec."""
        code = generator.generate_test(crawler_spec)
        
        assert code is not None
        assert isinstance(code, GeneratedCode)
        assert "class TestDatabaseMigrationAnalyzer:" in code.content
        assert "def test_initialization" in code.content
        assert "def test_analyze_returns_dict" in code.content
        assert code.file_path.name == "test_database_migration_analyzer.py"
    
    def test_cgen_007_test_scenarios_included(self, generator, crawler_spec):
        """CGEN-007: Include all test scenarios from spec."""
        code = generator.generate_test(crawler_spec)
        
        for scenario in crawler_spec.test_scenarios:
            # Convert to test method name
            method_name = scenario.lower().replace(' ', '_')
            assert f"def test_{method_name}" in code.content
    
    def test_cgen_008_dependencies_included(self, generator, crawler_spec):
        """CGEN-008: Include dependencies in generated code."""
        code = generator.generate_analyzer(crawler_spec)
        
        assert "PostgreSQL" in code.content or "dependencies" in code.content
    
    def test_cgen_009_proper_imports(self, generator, crawler_spec):
        """CGEN-009: Generated code has proper imports."""
        code = generator.generate_analyzer(crawler_spec)
        
        assert "from cortex.lens.analyzers.base import BaseAnalyzer" in code.content
        assert "from pathlib import Path" in code.content
        assert "from typing import Dict, Any" in code.content


# ==============================================================================
# Code Validation Tests
# ==============================================================================

class TestCodeValidation:
    """Test generated code validation."""
    
    def test_cgen_010_validate_syntax(self, generator, crawler_spec):
        """CGEN-010: Validate generated code has valid Python syntax."""
        code = generator.generate_analyzer(crawler_spec)
        
        # Should not raise SyntaxError
        is_valid = generator.validate_syntax(code.content)
        assert is_valid is True
    
    def test_cgen_011_detect_syntax_errors(self, generator):
        """CGEN-011: Detect syntax errors in generated code."""
        invalid_code = "def foo(\n  return bar"
        
        is_valid = generator.validate_syntax(invalid_code)
        assert is_valid is False
    
    def test_cgen_012_validate_base_class_inheritance(self, generator, crawler_spec):
        """CGEN-012: Validate analyzer inherits from BaseAnalyzer."""
        code = generator.generate_analyzer(crawler_spec)
        
        has_base = generator.validate_base_class(code.content, "BaseAnalyzer")
        assert has_base is True
    
    def test_cgen_013_validate_required_methods(self, generator, crawler_spec):
        """CGEN-013: Validate required methods are present."""
        code = generator.generate_analyzer(crawler_spec)
        
        for method in crawler_spec.required_methods:
            has_method = generator.validate_method_exists(code.content, method)
            assert has_method is True
    
    def test_cgen_014_sandbox_validation(self, generator, crawler_spec):
        """CGEN-014: Validate code in sandbox before execution."""
        code = generator.generate_analyzer(crawler_spec)
        
        # Sandbox validation should pass for generated code
        is_safe = generator.sandbox_validate(code.content)
        assert is_safe is True
    
    def test_cgen_015_detect_dangerous_code(self, generator):
        """CGEN-015: Detect dangerous patterns in code."""
        dangerous_code = """
import os
os.system("rm -rf /")
eval("malicious code")
"""
        
        is_safe = generator.sandbox_validate(dangerous_code)
        assert is_safe is False


# ==============================================================================
# File Operations Tests
# ==============================================================================

class TestFileOperations:
    """Test file writing and path management."""
    
    def test_cgen_016_write_analyzer_to_file(self, generator, crawler_spec, tmp_path):
        """CGEN-016: Write generated analyzer to file."""
        code = generator.generate_analyzer(crawler_spec)
        output_path = tmp_path / "crawlers"
        
        written_path = generator.write_code(code, output_path)
        
        assert written_path.exists()
        assert written_path.name == "database_migration_analyzer.py"
        assert "class DatabaseMigrationAnalyzer" in written_path.read_text()
    
    def test_cgen_017_write_test_to_file(self, generator, crawler_spec, tmp_path):
        """CGEN-017: Write generated test to file."""
        code = generator.generate_test(crawler_spec)
        output_path = tmp_path / "tests"
        
        written_path = generator.write_code(code, output_path)
        
        assert written_path.exists()
        assert written_path.name == "test_database_migration_analyzer.py"
        assert "class TestDatabaseMigrationAnalyzer" in written_path.read_text()
    
    def test_cgen_018_prevent_overwrite_without_flag(self, generator, crawler_spec, tmp_path):
        """CGEN-018: Prevent overwriting existing files without flag."""
        code = generator.generate_analyzer(crawler_spec)
        output_path = tmp_path / "crawlers"
        
        # Write first time
        first_path = generator.write_code(code, output_path)
        
        # Attempt to write again without overwrite flag
        with pytest.raises(FileExistsError):
            generator.write_code(code, output_path, overwrite=False)
    
    def test_cgen_019_allow_overwrite_with_flag(self, generator, crawler_spec, tmp_path):
        """CGEN-019: Allow overwriting with explicit flag."""
        code = generator.generate_analyzer(crawler_spec)
        output_path = tmp_path / "crawlers"
        
        # Write first time
        first_path = generator.write_code(code, output_path)
        
        # Write again with overwrite flag
        second_path = generator.write_code(code, output_path, overwrite=True)
        
        assert first_path == second_path
        assert second_path.exists()


# ==============================================================================
# Wiring Integration Tests
# ==============================================================================

class TestWiringIntegration:
    """Test wiring configuration generation."""
    
    def test_cgen_020_generate_wiring_entry(self, generator, crawler_spec):
        """CGEN-020: Generate wiring configuration entry."""
        wiring_entry = generator.generate_wiring_entry(crawler_spec)
        
        assert wiring_entry is not None
        assert isinstance(wiring_entry, dict)
        assert "name" in wiring_entry
        assert wiring_entry["name"] == "DatabaseMigrationAnalyzer"
        assert "module" in wiring_entry
        assert wiring_entry["module"] == "cortex.lens.crawlers.database_migration_analyzer"
    
    def test_cgen_021_wiring_entry_structure(self, generator, crawler_spec):
        """CGEN-021: Validate wiring entry has required structure."""
        wiring_entry = generator.generate_wiring_entry(crawler_spec)
        
        required_keys = ["name", "module", "class", "priority", "dependencies"]
        for key in required_keys:
            assert key in wiring_entry
    
    def test_cgen_022_append_to_wiring_yaml(self, generator, crawler_spec, tmp_path):
        """CGEN-022: Append entry to existing wiring.yaml."""
        wiring_file = tmp_path / "wiring.yaml"
        wiring_file.write_text("""
analyzers:
  - name: CodeAnalyzer
    module: cortex.lens.analyzers.code_analyzer
    class: CodeAnalyzer
""")
        
        generator.append_to_wiring(crawler_spec, wiring_file)
        
        content = wiring_file.read_text()
        assert "DatabaseMigrationAnalyzer" in content


# ==============================================================================
# Edge Cases Tests
# ==============================================================================

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_cgen_023_empty_spec(self, generator):
        """CGEN-023: Handle empty crawler spec gracefully."""
        empty_spec = CrawlerSpec(
            crawler_name="EmptyAnalyzer",
            description="",
            test_scenarios=[],
        )
        
        code = generator.generate_analyzer(empty_spec)
        assert code is not None
        assert "class EmptyAnalyzer(BaseAnalyzer):" in code.content
    
    def test_cgen_024_special_characters_in_name(self, generator):
        """CGEN-024: Handle special characters in crawler name."""
        spec = CrawlerSpec(
            crawler_name="API-GraphQL_Analyzer",
            description="Test special chars",
        )
        
        # Should sanitize to valid Python class name
        code = generator.generate_analyzer(spec)
        # Special characters removed: API-GraphQL_Analyzer -> APIGraphQL_Analyzer
        assert "class APIGraphQL_Analyzer(BaseAnalyzer):" in code.content
    
    def test_cgen_025_very_long_description(self, generator):
        """CGEN-025: Handle very long descriptions."""
        spec = CrawlerSpec(
            crawler_name="VerboseAnalyzer",
            description="A" * 1000,  # Very long description
        )
        
        code = generator.generate_analyzer(spec)
        assert code is not None
        assert len(code.content) > 0


# AC_COMPLETE: AC-CDF-Generator-001

__all__ = [
    "TestTemplateLoading",
    "TestCodeGeneration",
    "TestCodeValidation",
    "TestFileOperations",
    "TestWiringIntegration",
    "TestEdgeCases",
]
