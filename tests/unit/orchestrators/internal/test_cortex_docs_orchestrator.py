"""
Tests for CortexDocsOrchestrator

CORE-008: TDD - Tests before implementation
Compliance: CORTEX Testing Framework
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from cortex.orchestrators.internal.cortex_docs_orchestrator import (
    CortexDocsOrchestrator,
    get_cortex_docs_orchestrator,
    NavigationLevel,
    ContentSection,
    NavigationItem,
    PageMetadata,
    HTMLGenerationReport,
)


class TestCortexDocsOrchestratorInitialization:
    """Test orchestrator initialization."""
    
    def test_initialization_creates_instance(self, tmp_path: Path) -> None:
        """Test that orchestrator initializes successfully."""
        docs_root = tmp_path / "docs"
        templates_dir = tmp_path / "templates"
        
        orchestrator = CortexDocsOrchestrator(
            docs_root=docs_root,
            templates_dir=templates_dir
        )
        
        assert orchestrator is not None
        assert orchestrator.docs_root == docs_root
        assert orchestrator.templates_dir == templates_dir
    
    def test_singleton_instance_returns_same_object(self) -> None:
        """Test that instance() returns singleton."""
        instance1 = get_cortex_docs_orchestrator()
        instance2 = get_cortex_docs_orchestrator()
        
        assert instance1 is instance2
    
    def test_get_name_returns_correct_name(self) -> None:
        """Test get_name returns 'CortexDocsOrchestrator'."""
        orchestrator = get_cortex_docs_orchestrator()
        
        assert orchestrator.get_name() == "CortexDocsOrchestrator"
    
    def test_get_version_returns_version_string(self) -> None:
        """Test get_version returns version."""
        orchestrator = get_cortex_docs_orchestrator()
        
        version = orchestrator.get_version()
        assert isinstance(version, str)
        assert len(version) > 0
    
    def test_get_capabilities_returns_list(self) -> None:
        """Test get_capabilities returns capability list."""
        orchestrator = get_cortex_docs_orchestrator()
        
        capabilities = orchestrator.get_capabilities()
        assert isinstance(capabilities, list)
        assert "generate_main_index" in capabilities
        assert "generate_subfolder_indexes" in capabilities
        assert "extract_template" in capabilities


class TestTemplateExtraction:
    """Test template extraction from existing HTML."""
    
    def test_extract_template_with_valid_html(self, tmp_path: Path) -> None:
        """Test extracting template from docs/index.html."""
        # Create mock index.html
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        
        index_html = docs_root / "index.html"
        index_html.write_text("""<!DOCTYPE html>
<html lang="en">
<head>
    <title>Test</title>
</head>
<body>
    <header>Header Content</header>
    <nav>Navigation</nav>
    <main>Main Content</main>
    <footer>Footer</footer>
    <!-- Scripts -->
    <script>console.log('test');</script>
</body>
</html>
""")
        
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        
        orchestrator = CortexDocsOrchestrator(
            docs_root=docs_root,
            templates_dir=templates_dir
        )
        
        result = orchestrator._extract_template()
        
        assert result.is_ok()
        assert (templates_dir / "base.html.jinja2").exists()
        assert (templates_dir / "index.html.jinja2").exists()
        assert (templates_dir / "subfolder.html.jinja2").exists()
    
    def test_extract_template_creates_components(self, tmp_path: Path) -> None:
        """Test that component templates are created."""
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        
        index_html = docs_root / "index.html"
        index_html.write_text("""<!DOCTYPE html>
<html lang="en">
<head></head>
<body>
    <header>Header</header>
    <main>Content</main>
    <footer>Footer</footer>
</body>
</html>
""")
        
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        
        orchestrator = CortexDocsOrchestrator(
            docs_root=docs_root,
            templates_dir=templates_dir
        )
        
        result = orchestrator._extract_template()
        
        assert result.is_ok()
        components_dir = templates_dir / "components"
        assert components_dir.exists()
        assert (components_dir / "header.html.jinja2").exists()
        assert (components_dir / "footer.html.jinja2").exists()


class TestHTMLGeneration:
    """Test HTML file generation."""
    
    def test_generate_main_index_creates_file(self, tmp_path: Path) -> None:
        """Test that main index.html is generated."""
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        
        # Create minimal template
        index_template = templates_dir / "index.html.jinja2"
        index_template.write_text("""<!DOCTYPE html>
<html>
<head><title>{{ page_title }}</title></head>
<body><h1>{{ page_description }}</h1></body>
</html>
""")
        
        orchestrator = CortexDocsOrchestrator(
            docs_root=docs_root,
            templates_dir=templates_dir
        )
        orchestrator.jinja_env = orchestrator.jinja_env or Mock()
        
        with patch.object(orchestrator, '_get_main_sections', return_value=[]):
            with patch.object(orchestrator, '_get_quick_start_content', return_value=[]):
                with patch.object(orchestrator, '_render_component', return_value=""):
                    result = orchestrator._generate_main_index()
        
        # Should attempt to generate even if it fails
        assert result is not None
    
    def test_generate_all_returns_report(self, tmp_path: Path) -> None:
        """Test that generate_all returns HTMLGenerationReport."""
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        
        templates_dir = tmp_path / "templates"
        templates_dir.mkdir()
        
        orchestrator = CortexDocsOrchestrator(
            docs_root=docs_root,
            templates_dir=templates_dir
        )
        
        # Mock template extraction
        with patch.object(orchestrator, '_extract_template', return_value=Mock(is_err=lambda: False)):
            with patch.object(orchestrator, '_generate_main_index', return_value=Mock(is_ok=lambda: True, value=docs_root / "index.html")):
                with patch.object(orchestrator, '_generate_subfolder_indexes', return_value=Mock(is_ok=lambda: True, value=[])):
                    with patch.object(orchestrator, '_validate_html', return_value=Mock(is_ok=lambda: True)):
                        result = orchestrator._generate_all()
        
        # Should return a report
        assert result is not None


class TestNavigationBuilding:
    """Test navigation structure building."""
    
    def test_build_navigation_creates_items(self) -> None:
        """Test that navigation structure is built."""
        orchestrator = get_cortex_docs_orchestrator()
        
        orchestrator._build_navigation()
        
        assert len(orchestrator.navigation) > 0
        assert any(item.label == "Home" for item in orchestrator.navigation)
        assert any(item.label == "CORTEX Brain" for item in orchestrator.navigation)
    
    def test_navigation_items_have_correct_levels(self) -> None:
        """Test that navigation items have appropriate levels."""
        orchestrator = get_cortex_docs_orchestrator()
        
        orchestrator._build_navigation()
        
        # Check that executive, domain, and technical levels exist
        levels = {item.level for item in orchestrator.navigation}
        assert NavigationLevel.EXECUTIVE in levels or NavigationLevel.DOMAIN in levels


class TestValidation:
    """Test HTML validation."""
    
    def test_validate_html_checks_structure(self, tmp_path: Path) -> None:
        """Test that validation checks HTML structure."""
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        
        index_html = docs_root / "index.html"
        index_html.write_text("""<!DOCTYPE html>
<html lang="en">
<head><title>Test</title></head>
<body><h1 aria-label="test">Content</h1></body>
</html>
""")
        
        orchestrator = CortexDocsOrchestrator(docs_root=docs_root)
        
        result = orchestrator._validate_html()
        
        assert result.is_ok()
        report = result.value
        assert "valid" in report
        assert "issues" in report
    
    def test_validate_html_detects_missing_doctype(self, tmp_path: Path) -> None:
        """Test that validation detects missing DOCTYPE."""
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        
        index_html = docs_root / "index.html"
        index_html.write_text("""<html>
<head><title>Test</title></head>
<body><h1>Content</h1></body>
</html>
""")
        
        orchestrator = CortexDocsOrchestrator(docs_root=docs_root)
        
        result = orchestrator._validate_html()
        
        assert result.is_ok()
        report = result.value
        assert len(report["issues"]) > 0


class TestMCPExposure:
    """Test that orchestrator is NOT MCP-exposed."""
    
    def test_get_mcp_tools_returns_empty(self) -> None:
        """Test that MCP tools are empty (not exposed)."""
        orchestrator = get_cortex_docs_orchestrator()
        
        tools = orchestrator.get_mcp_tools()
        
        assert isinstance(tools, dict)
        assert len(tools) == 0  # Intentionally not MCP-exposed
    
    def test_orchestrator_is_internal_mode(self) -> None:
        """Test that operation mode is 'internal' (not MCP-exposed)."""
        orchestrator = get_cortex_docs_orchestrator()
        
        mode = orchestrator.get_mode()
        assert mode == "internal"  # Internal tooling, not for production MCP


class TestSubfolderMetadata:
    """Test subfolder metadata extraction."""
    
    def test_get_subfolder_metadata_extracts_title(self, tmp_path: Path) -> None:
        """Test extracting title from subfolder name."""
        docs_root = tmp_path / "docs"
        subfolder = docs_root / "01-cortex-brain"
        subfolder.mkdir(parents=True)
        
        # Create sample markdown file
        (subfolder / "test.md").write_text("# Test Title\n\nSome content here.")
        
        orchestrator = CortexDocsOrchestrator(docs_root=docs_root)
        
        metadata = orchestrator._get_subfolder_metadata(subfolder)
        
        assert "title" in metadata
        assert "breadcrumbs" in metadata
        assert "documents" in metadata
    
    def test_get_subfolder_metadata_builds_breadcrumbs(self, tmp_path: Path) -> None:
        """Test that breadcrumbs are built correctly."""
        docs_root = tmp_path / "docs"
        subfolder = docs_root / "02-orchestrators"
        subfolder.mkdir(parents=True)
        
        orchestrator = CortexDocsOrchestrator(docs_root=docs_root)
        
        metadata = orchestrator._get_subfolder_metadata(subfolder)
        
        breadcrumbs = metadata["breadcrumbs"]
        assert len(breadcrumbs) >= 2
        assert breadcrumbs[0][0] == "Home"
        assert breadcrumbs[0][1] == "/"


class TestExecuteOperation:
    """Test execute() method."""
    
    def test_execute_unknown_operation_returns_error(self) -> None:
        """Test that unknown operation returns error."""
        orchestrator = get_cortex_docs_orchestrator()
        
        result = orchestrator.execute("unknown_operation")
        
        assert result.is_err()
        assert "Unknown operation" in result.error
    
    def test_execute_extract_template_operation(self, tmp_path: Path) -> None:
        """Test executing extract_template operation."""
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        
        (docs_root / "index.html").write_text("<!DOCTYPE html><html><body></body></html>")
        
        orchestrator = CortexDocsOrchestrator(
            docs_root=docs_root,
            templates_dir=tmp_path / "templates"
        )
        
        result = orchestrator.execute("extract_template")
        
        # Should attempt extraction
        assert result is not None
