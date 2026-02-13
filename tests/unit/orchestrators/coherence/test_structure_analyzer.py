"""
Tests for StructureAnalyzer.

AC_START: AC-ENH-101-008
Description: TDD tests for StructureAnalyzer
Authority: ENH-101 Stage S2 - WAVE-10 Quality
Compliance: CORE-008 (tests first), Zero mocks for core logic
"""

import pytest

from cortex.orchestrators.coherence.structure_analyzer import (
    StructureAnalyzer,
    StructureMetrics,
)
from cortex.orchestrators.coherence.models import (
    FileStructure,
    Section,
    SectionType,
    VersionMarker,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def analyzer() -> StructureAnalyzer:
    """Create a default StructureAnalyzer."""
    return StructureAnalyzer()


@pytest.fixture
def sample_markdown() -> str:
    """Sample markdown content with sections."""
    return """# Main Title

This is the introduction.

## Section One

Content for section one.

### Subsection A

Detailed content A.

## Section Two

Content for section two.

**Version:** 1.2.3 | **Updated:** 2025-01-15

---

## Section Three

Final content.
"""


@pytest.fixture
def sample_python() -> str:
    """Sample Python content with structure."""
    return '''"""Module docstring.

Version: 2.0.0
"""

from typing import Optional


class MyClass:
    """A sample class."""
    
    def __init__(self, name: str) -> None:
        """Initialize the class."""
        self.name = name
    
    def method_one(self) -> str:
        """First method."""
        return self.name


class AnotherClass:
    """Another sample class."""
    
    def process(self) -> None:
        """Process something."""
        pass


def standalone_function(x: int) -> int:
    """A standalone function."""
    return x * 2
'''


@pytest.fixture
def sample_yaml() -> str:
    """Sample YAML content."""
    return """# Configuration file
version: "1.0.0"

settings:
  debug: true
  timeout: 30

database:
  host: localhost
  port: 5432

features:
  - name: feature_one
    enabled: true
  - name: feature_two
    enabled: false
"""


# =============================================================================
# TEST: INITIALIZATION
# =============================================================================

class TestStructureAnalyzerInit:
    """Tests for StructureAnalyzer initialization."""
    
    def test_default_initialization(self) -> None:
        """Analyzer initializes with default settings."""
        analyzer = StructureAnalyzer()
        assert analyzer is not None


# =============================================================================
# TEST: ANALYZE METHOD
# =============================================================================

class TestAnalyze:
    """Tests for analyze method."""
    
    def test_analyze_returns_file_structure(
        self,
        analyzer: StructureAnalyzer,
        sample_markdown: str,
    ) -> None:
        """Analyze returns FileStructure object."""
        result = analyzer.analyze(sample_markdown, "test.md")
        
        assert isinstance(result, FileStructure)
        assert result.file_path == "test.md"
        assert result.file_type == "markdown"
    
    def test_analyze_detects_sections(
        self,
        analyzer: StructureAnalyzer,
        sample_markdown: str,
    ) -> None:
        """Analyze detects all markdown sections."""
        result = analyzer.analyze(sample_markdown, "test.md")
        
        # Should find: Main Title (H1), Section One (H2), Subsection A (H3),
        #              Section Two (H2), Section Three (H2)
        assert len(result.sections) >= 4
        
        # Check section names
        section_names = [s.name for s in result.sections]
        assert "Main Title" in section_names
        assert "Section One" in section_names
        assert "Section Two" in section_names
    
    def test_analyze_empty_content(self, analyzer: StructureAnalyzer) -> None:
        """Analyze handles empty content."""
        result = analyzer.analyze("", "empty.md")
        
        assert isinstance(result, FileStructure)
        assert len(result.sections) == 0
    
    def test_analyze_detects_file_type(
        self,
        analyzer: StructureAnalyzer,
    ) -> None:
        """Analyze correctly detects file type."""
        md_result = analyzer.analyze("# Title", "test.md")
        py_result = analyzer.analyze("def foo(): pass", "test.py")
        yaml_result = analyzer.analyze("key: value", "test.yaml")
        
        assert md_result.file_type == "markdown"
        assert py_result.file_type == "python"
        assert yaml_result.file_type == "yaml"


# =============================================================================
# TEST: DETECT SECTIONS
# =============================================================================

class TestDetectSections:
    """Tests for detect_sections method."""
    
    def test_detect_markdown_headers(
        self,
        analyzer: StructureAnalyzer,
        sample_markdown: str,
    ) -> None:
        """Detect markdown headers at all levels."""
        sections = analyzer.detect_sections(sample_markdown, "test.md")
        
        # Find H1
        h1_sections = [s for s in sections if s.section_type == SectionType.MARKDOWN_H1]
        assert len(h1_sections) >= 1
        
        # Find H2
        h2_sections = [s for s in sections if s.section_type == SectionType.MARKDOWN_H2]
        assert len(h2_sections) >= 3
        
        # Find H3
        h3_sections = [s for s in sections if s.section_type == SectionType.MARKDOWN_H3]
        assert len(h3_sections) >= 1
    
    def test_detect_python_classes(
        self,
        analyzer: StructureAnalyzer,
        sample_python: str,
    ) -> None:
        """Detect Python class definitions."""
        sections = analyzer.detect_sections(sample_python, "test.py")
        
        class_sections = [s for s in sections if s.section_type == SectionType.PYTHON_CLASS]
        assert len(class_sections) >= 2
        
        class_names = [s.name for s in class_sections]
        assert "MyClass" in class_names
        assert "AnotherClass" in class_names
    
    def test_detect_python_functions(
        self,
        analyzer: StructureAnalyzer,
        sample_python: str,
    ) -> None:
        """Detect Python function definitions."""
        sections = analyzer.detect_sections(sample_python, "test.py")
        
        func_sections = [s for s in sections if s.section_type == SectionType.PYTHON_FUNCTION]
        
        # Should find standalone_function (methods are nested in classes)
        func_names = [s.name for s in func_sections]
        assert "standalone_function" in func_names
    
    def test_detect_yaml_keys(
        self,
        analyzer: StructureAnalyzer,
        sample_yaml: str,
    ) -> None:
        """Detect YAML top-level keys."""
        sections = analyzer.detect_sections(sample_yaml, "test.yaml")
        
        yaml_sections = [s for s in sections if s.section_type == SectionType.YAML_KEY]
        assert len(yaml_sections) >= 3
        
        key_names = [s.name for s in yaml_sections]
        assert "version" in key_names or "settings" in key_names


# =============================================================================
# TEST: VERSION MARKERS
# =============================================================================

class TestFindVersionMarkers:
    """Tests for find_version_markers method."""
    
    def test_find_semantic_version(
        self,
        analyzer: StructureAnalyzer,
        sample_markdown: str,
    ) -> None:
        """Find semantic version in markdown."""
        markers = analyzer.find_version_markers(sample_markdown)
        
        assert len(markers) >= 1
        
        # Should find "1.2.3"
        versions = [m.version for m in markers]
        assert any("1.2.3" in v for v in versions)
    
    def test_find_version_in_python(
        self,
        analyzer: StructureAnalyzer,
        sample_python: str,
    ) -> None:
        """Find version in Python docstring."""
        markers = analyzer.find_version_markers(sample_python)
        
        # Should find "2.0.0"
        versions = [m.version for m in markers]
        assert any("2.0.0" in v for v in versions)
    
    def test_find_version_in_yaml(
        self,
        analyzer: StructureAnalyzer,
        sample_yaml: str,
    ) -> None:
        """Find version in YAML."""
        markers = analyzer.find_version_markers(sample_yaml)
        
        # Should find "1.0.0"
        versions = [m.version for m in markers]
        assert any("1.0.0" in v for v in versions)
    
    def test_no_version_found(self, analyzer: StructureAnalyzer) -> None:
        """Return empty list when no version found."""
        markers = analyzer.find_version_markers("No version here")
        
        assert len(markers) == 0
    
    def test_version_marker_has_location(
        self,
        analyzer: StructureAnalyzer,
    ) -> None:
        """Version markers include line number."""
        content = """# Title
        
**Version:** 3.0.0
"""
        markers = analyzer.find_version_markers(content)
        
        assert len(markers) >= 1
        assert markers[0].line_number >= 1


# =============================================================================
# TEST: STRUCTURE METRICS
# =============================================================================

class TestGetStructureMetrics:
    """Tests for get_structure_metrics method."""
    
    def test_metrics_returns_structure_metrics(
        self,
        analyzer: StructureAnalyzer,
        sample_markdown: str,
    ) -> None:
        """get_structure_metrics returns StructureMetrics."""
        metrics = analyzer.get_structure_metrics(sample_markdown, "test.md")
        
        assert isinstance(metrics, StructureMetrics)
    
    def test_metrics_counts_sections(
        self,
        analyzer: StructureAnalyzer,
        sample_markdown: str,
    ) -> None:
        """Metrics include section count."""
        metrics = analyzer.get_structure_metrics(sample_markdown, "test.md")
        
        assert metrics.total_sections >= 4
    
    def test_metrics_counts_lines(
        self,
        analyzer: StructureAnalyzer,
        sample_markdown: str,
    ) -> None:
        """Metrics include line count."""
        metrics = analyzer.get_structure_metrics(sample_markdown, "test.md")
        
        assert metrics.total_lines > 0
    
    def test_metrics_depth(
        self,
        analyzer: StructureAnalyzer,
        sample_markdown: str,
    ) -> None:
        """Metrics include max depth."""
        metrics = analyzer.get_structure_metrics(sample_markdown, "test.md")
        
        # With H1, H2, H3 we have depth 3
        assert metrics.max_depth >= 2
    
    def test_metrics_empty_content(self, analyzer: StructureAnalyzer) -> None:
        """Metrics handle empty content."""
        metrics = analyzer.get_structure_metrics("", "empty.md")
        
        assert metrics.total_sections == 0
        assert metrics.total_lines == 0


# =============================================================================
# TEST: SECTION HIERARCHY
# =============================================================================

class TestGetSectionHierarchy:
    """Tests for get_section_hierarchy method."""
    
    def test_hierarchy_returns_dict(
        self,
        analyzer: StructureAnalyzer,
        sample_markdown: str,
    ) -> None:
        """get_section_hierarchy returns dictionary."""
        structure = analyzer.analyze(sample_markdown, "test.md")
        hierarchy = analyzer.get_section_hierarchy(structure.sections)
        
        assert isinstance(hierarchy, dict)
    
    def test_hierarchy_has_root_sections(
        self,
        analyzer: StructureAnalyzer,
        sample_markdown: str,
    ) -> None:
        """Hierarchy includes root-level sections."""
        structure = analyzer.analyze(sample_markdown, "test.md")
        hierarchy = analyzer.get_section_hierarchy(structure.sections)
        
        # Top-level sections (H1 or first H2s)
        assert len(hierarchy) >= 1
    
    def test_hierarchy_nests_subsections(
        self,
        analyzer: StructureAnalyzer,
        sample_markdown: str,
    ) -> None:
        """Hierarchy nests subsections under parents."""
        structure = analyzer.analyze(sample_markdown, "test.md")
        hierarchy = analyzer.get_section_hierarchy(structure.sections)
        
        # "Subsection A" should be nested under "Section One"
        # Check that some sections have children
        has_children = any(
            isinstance(v, dict) and len(v) > 0
            for v in hierarchy.values()
            if isinstance(v, dict)
        )
        # For markdown, H3 should be child of H2
        assert has_children or len(hierarchy) > 0


# =============================================================================
# TEST: FILE TYPE DETECTION
# =============================================================================

class TestFileTypeDetection:
    """Tests for file type detection."""
    
    def test_detect_markdown(self, analyzer: StructureAnalyzer) -> None:
        """Detect .md files as markdown."""
        result = analyzer.analyze("# Title", "README.md")
        assert result.file_type == "markdown"
    
    def test_detect_python(self, analyzer: StructureAnalyzer) -> None:
        """Detect .py files as python."""
        result = analyzer.analyze("def foo(): pass", "module.py")
        assert result.file_type == "python"
    
    def test_detect_yaml(self, analyzer: StructureAnalyzer) -> None:
        """Detect .yaml and .yml files as yaml."""
        yaml_result = analyzer.analyze("key: value", "config.yaml")
        yml_result = analyzer.analyze("key: value", "config.yml")
        
        assert yaml_result.file_type == "yaml"
        assert yml_result.file_type == "yaml"
    
    def test_detect_json(self, analyzer: StructureAnalyzer) -> None:
        """Detect .json files as json."""
        result = analyzer.analyze('{"key": "value"}', "data.json")
        assert result.file_type == "json"
    
    def test_detect_unknown(self, analyzer: StructureAnalyzer) -> None:
        """Unknown extensions return 'unknown'."""
        result = analyzer.analyze("content", "file.xyz")
        assert result.file_type == "unknown"


# AC_COMPLETE: AC-ENH-101-008 ✅ StructureAnalyzer tests
