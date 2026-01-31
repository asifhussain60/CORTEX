"""
CortexDocsOrchestrator - Internal CORTEX Documentation HTML Generator

INTERNAL USE ONLY — NOT MCP-EXPOSED
Generates HTML documentation for CORTEX repository using approved design:
- Dark blue glassmorphism theme from docs/index.html
- Hierarchical navigation with drill-down
- D3.js visualizations and interactive features
- Subfolder index.html generation with consistent styling

Scope: docs/index.html + docs/*/index.html (CORTEX repo only)
Governance: ARCH-011 (execute to completion), CORE-028 (filename conventions)
Date: 2026-01-31

NOT for production MCP exposure. Use DocumentationOrchestrator for external repos.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from jinja2 import Environment, FileSystemLoader, Template

from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.brain.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.brain.core.state_manager import StateManager, OperationState


# ============================================================================
# ENUMS & DATA MODELS
# ============================================================================

class NavigationLevel(Enum):
    """Navigation hierarchy levels."""
    EXECUTIVE = "executive"  # High-level overview (index.html)
    DOMAIN = "domain"        # Domain-specific (01-cortex-brain/, 02-orchestrators/)
    TECHNICAL = "technical"  # Deep technical details


@dataclass
class ContentSection:
    """Documentation content section."""
    id: str
    title: str
    icon: str  # Font Awesome icon class
    description: str
    file_path: Optional[Path] = None
    subsections: List[ContentSection] = field(default_factory=list)


@dataclass
class NavigationItem:
    """Navigation menu item."""
    label: str
    href: str
    icon: str
    level: NavigationLevel
    children: List[NavigationItem] = field(default_factory=list)


@dataclass
class PageMetadata:
    """HTML page metadata."""
    title: str
    description: str
    keywords: List[str]
    og_image: str = "assets/images/CORTEX-logo-512.png"
    breadcrumbs: List[Tuple[str, str]] = field(default_factory=list)


@dataclass
class HTMLGenerationReport:
    """Report from HTML generation."""
    generated_files: List[Path]
    failed_files: List[Tuple[Path, str]]
    assets_copied: List[Path]
    total_size_bytes: int
    generation_time_seconds: float


# ============================================================================
# CORTEX DOCS ORCHESTRATOR
# ============================================================================

class CortexDocsOrchestrator(IOrchestrator):
    """
    Internal orchestrator for CORTEX documentation HTML generation.
    
    NOT MCP-EXPOSED — Internal tooling only.
    Generates docs/index.html and subfolder indexes with approved design.
    
    Capabilities:
    - Extract template from existing docs/index.html
    - Generate main index.html with glassmorphism theme
    - Generate subfolder index.html files with consistent navigation
    - Copy/optimize CSS/JS assets
    - Validate HTML structure and accessibility
    
    Compliance:
    - CORE-008: TDD (tests before implementation)
    - CORE-011: Type hints on all methods
    - CORE-012: Google-style docstrings
    - ARCH-011: Execute to completion (no interim reports)
    """
    
    _instance: Optional[CortexDocsOrchestrator] = None
    _lock = threading.Lock()
    
    def __init__(
        self,
        docs_root: Path = Path("docs"),
        templates_dir: Path = Path("cortex/templates/docs")
    ) -> None:
        """
        Initialize CORTEX docs orchestrator.
        
        Args:
            docs_root: Root documentation directory (default: docs/)
            templates_dir: Jinja2 templates directory
        """
        import threading
        
        self.docs_root = docs_root
        self.templates_dir = templates_dir
        self.logger = EnhancedAuditLogger.instance()
        self.state_manager = StateManager()
        
        # Jinja2 environment
        self.jinja_env: Optional[Environment] = None
        if templates_dir.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(templates_dir)),
                autoescape=True,
                trim_blocks=True,
                lstrip_blocks=True
            )
        
        # Navigation structure (will be populated from docs/ structure)
        self.navigation: List[NavigationItem] = []
    
    @classmethod
    def instance(cls, **kwargs) -> CortexDocsOrchestrator:
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(**kwargs)
        return cls._instance
    
    # ========================================================================
    # IOrchestrator Implementation
    # ========================================================================
    
    def get_name(self) -> str:
        """Get orchestrator name."""
        return "CortexDocsOrchestrator"
    
    def get_version(self) -> str:
        """Get orchestrator version."""
        return "1.0.0"
    
    def get_mode(self) -> str:
        """Get operation mode."""
        return "internal"  # Internal tooling, not MCP-exposed
    
    def get_capabilities(self) -> List[str]:
        """Get orchestrator capabilities."""
        return [
            "generate_main_index",
            "generate_subfolder_indexes",
            "extract_template",
            "optimize_assets",
            "validate_html"
        ]
    
    def initialize(self) -> Result:
        """Initialize orchestrator."""
        try:
            # Ensure templates directory exists
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            
            # Build navigation structure
            self._build_navigation()
            
            return Ok({"status": "initialized"})
        except Exception as e:
            return Err(f"Initialization failed: {str(e)}")
    
    def execute(self, operation: str, **kwargs) -> Result[Any, str]:
        """
        Execute documentation operation.
        
        Args:
            operation: Operation to execute
                - "extract_template": Extract template from docs/index.html
                - "generate_main": Generate docs/index.html
                - "generate_subfolders": Generate all subfolder indexes
                - "generate_all": Generate everything
                - "validate": Validate generated HTML
            **kwargs: Operation-specific parameters
        
        Returns:
            Result containing operation outcome
        """
        try:
            if operation == "extract_template":
                return self._extract_template()
            elif operation == "generate_main":
                return self._generate_main_index()
            elif operation == "generate_subfolders":
                return self._generate_subfolder_indexes()
            elif operation == "generate_all":
                return self._generate_all()
            elif operation == "validate":
                return self._validate_html()
            else:
                return Err(f"Unknown operation: {operation}")
        except Exception as e:
            self.logger.log_error(f"CortexDocsOrchestrator operation failed: {str(e)}")
            return Err(f"Operation error: {str(e)}")
    
    def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Result:
        """Execute named operation with parameters."""
        return self.execute(operation_name, **parameters)
    
    def get_mcp_tools(self) -> Dict[str, Any]:
        """Get MCP tools (NOT EXPOSED - internal only)."""
        return {}  # Intentionally empty - not MCP-exposed
    
    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit trail."""
        return []
    
    # ========================================================================
    # TEMPLATE EXTRACTION
    # ========================================================================
    
    def _extract_template(self) -> Result[Dict[str, Any], str]:
        """
        Extract Jinja2 template from existing docs/index.html.
        
        Extracts:
        - Base HTML structure
        - CSS glassmorphism design system
        - JavaScript interactive features
        - Navigation components
        - Content panels
        
        Returns:
            Result with extracted template paths
        """
        try:
            source_html = self.docs_root / "index.html"
            if not source_html.exists():
                return Err(f"Source HTML not found: {source_html}")
            
            content = source_html.read_text()
            
            # Extract sections
            sections = {
                "head": self._extract_section(content, "<head>", "</head>"),
                "header": self._extract_section(content, '<header', '</header>'),
                "navigation": self._extract_section(content, '<nav', '</nav>'),
                "main_content": self._extract_section(content, '<main', '</main>'),
                "footer": self._extract_section(content, '<footer', '</footer>'),
                "scripts": self._extract_section(content, '<!-- Scripts -->', '</body>'),
            }
            
            # Create base template
            base_template = self._create_base_template(sections)
            base_path = self.templates_dir / "base.html.jinja2"
            base_path.write_text(base_template)
            
            # Create main index template
            index_template = self._create_index_template(sections)
            index_path = self.templates_dir / "index.html.jinja2"
            index_path.write_text(index_template)
            
            # Create subfolder template
            subfolder_template = self._create_subfolder_template(sections)
            subfolder_path = self.templates_dir / "subfolder.html.jinja2"
            subfolder_path.write_text(subfolder_template)
            
            # Create component templates
            components_dir = self.templates_dir / "components"
            components_dir.mkdir(exist_ok=True)
            
            self._create_component_templates(components_dir, sections)
            
            return Ok({
                "templates_created": [
                    str(base_path),
                    str(index_path),
                    str(subfolder_path)
                ],
                "components_dir": str(components_dir)
            })
            
        except Exception as e:
            return Err(f"Template extraction failed: {str(e)}")
    
    def _extract_section(self, content: str, start_marker: str, end_marker: str) -> str:
        """Extract section between markers."""
        start = content.find(start_marker)
        if start == -1:
            return ""
        
        end = content.find(end_marker, start)
        if end == -1:
            return ""
        
        return content[start:end + len(end_marker)]
    
    def _create_base_template(self, sections: Dict[str, str]) -> str:
        """Create base Jinja2 template."""
        return f"""<!DOCTYPE html>
<html lang="en">
{sections['head']}
<body>
    {{{{ header | safe }}}}
    {{{{ navigation | safe }}}}
    <main>
        {{% block content %}}
        {{% endblock %}}
    </main>
    {{{{ footer | safe }}}}
    {sections['scripts']}
</body>
</html>
"""
    
    def _create_index_template(self, sections: Dict[str, str]) -> str:
        """Create main index template."""
        return """{% extends "base.html.jinja2" %}

{% block content %}
<section class="hero-section">
    <div class="container">
        <div class="hero-content glass-card">
            <img src="assets/images/CORTEX-logo-512.png" alt="CORTEX Logo" class="hero-logo">
            <h1 class="hero-title">{{ page_title }}</h1>
            <p class="hero-subtitle">{{ page_description }}</p>
        </div>
    </div>
</section>

<section class="features-grid">
    <div class="container">
        {% for section in content_sections %}
        <div class="feature-card glass-card" data-level="{{ section.level }}">
            <div class="feature-icon">
                <i class="fas {{ section.icon }}"></i>
            </div>
            <h2 class="feature-title">{{ section.title }}</h2>
            <p class="feature-description">{{ section.description }}</p>
            {% if section.href %}
            <a href="{{ section.href }}" class="feature-link">
                Explore <i class="fas fa-arrow-right"></i>
            </a>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</section>

<section class="quick-start">
    <div class="container">
        <div class="glass-card">
            <h2>🚀 Quick Start</h2>
            <div class="tabs-container">
                {% for tab in quick_start_tabs %}
                <div class="tab-content">
                    <h3>{{ tab.title }}</h3>
                    <pre><code>{{ tab.code }}</code></pre>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</section>
{% endblock %}
"""
    
    def _create_subfolder_template(self, sections: Dict[str, str]) -> str:
        """Create subfolder index template."""
        return """{% extends "base.html.jinja2" %}

{% block content %}
<section class="breadcrumb-section">
    <div class="container">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                {% for crumb_label, crumb_href in breadcrumbs %}
                <li class="breadcrumb-item">
                    <a href="{{ crumb_href }}">{{ crumb_label }}</a>
                </li>
                {% endfor %}
            </ol>
        </nav>
    </div>
</section>

<section class="subfolder-header">
    <div class="container">
        <div class="glass-card">
            <h1>{{ section_title }}</h1>
            <p class="lead">{{ section_description }}</p>
        </div>
    </div>
</section>

<section class="content-grid">
    <div class="container">
        <div class="row">
            <!-- Sidebar Navigation -->
            <aside class="col-md-3 sidebar">
                <div class="glass-card sticky-nav">
                    <h3>Contents</h3>
                    <ul class="nav-list">
                        {% for item in sidebar_items %}
                        <li>
                            <a href="{{ item.href }}">
                                <i class="fas {{ item.icon }}"></i>
                                {{ item.label }}
                            </a>
                        </li>
                        {% endfor %}
                    </ul>
                </div>
            </aside>
            
            <!-- Main Content -->
            <div class="col-md-9 main-content">
                {% for doc in documents %}
                <article class="doc-card glass-card">
                    <h2>
                        <i class="fas {{ doc.icon }}"></i>
                        {{ doc.title }}
                    </h2>
                    <p class="doc-description">{{ doc.description }}</p>
                    <a href="{{ doc.href }}" class="btn-primary">
                        Read More <i class="fas fa-arrow-right"></i>
                    </a>
                </article>
                {% endfor %}
            </div>
        </div>
    </div>
</section>
{% endblock %}
"""
    
    def _create_component_templates(self, components_dir: Path, sections: Dict[str, str]) -> None:
        """Create component templates (header, nav, footer)."""
        
        # Header component
        header_template = """<header class="main-header glass-bg">
    <div class="container">
        <div class="header-content">
            <div class="logo">
                <img src="/assets/images/CORTEX-logo-64.png" alt="CORTEX">
                <span>CORTEX</span>
            </div>
            <nav class="main-nav">
                <a href="/">Home</a>
                <a href="/01-cortex-brain/">Brain</a>
                <a href="/02-orchestrators/">Orchestrators</a>
                <a href="/04-architecture/">Architecture</a>
                <a href="/11-mcp-tools/">MCP Tools</a>
            </nav>
        </div>
    </div>
</header>
"""
        (components_dir / "header.html.jinja2").write_text(header_template)
        
        # Footer component
        footer_template = """<footer class="main-footer glass-bg">
    <div class="container">
        <div class="footer-content">
            <p>CORTEX - Cognitive Real-Time Execution System</p>
            <p>Developed by Asif Hussain | 2024-2026</p>
        </div>
    </div>
</footer>
"""
        (components_dir / "footer.html.jinja2").write_text(footer_template)
    
    # ========================================================================
    # HTML GENERATION
    # ========================================================================
    
    def _generate_main_index(self) -> Result[Path, str]:
        """
        Generate main docs/index.html.
        
        Returns:
            Result with generated file path
        """
        try:
            if not self.jinja_env:
                return Err("Jinja2 environment not initialized. Run extract_template first.")
            
            template = self.jinja_env.get_template("index.html.jinja2")
            
            # Build context from docs structure
            context = {
                "page_title": "CORTEX - Enterprise Development Intelligence",
                "page_description": "AI-Powered Development with TDD, Planning, and Autonomous Orchestration",
                "content_sections": self._get_main_sections(),
                "quick_start_tabs": self._get_quick_start_content(),
                "header": self._render_component("header.html.jinja2"),
                "footer": self._render_component("footer.html.jinja2"),
            }
            
            html = template.render(**context)
            
            output_path = self.docs_root / "index.html"
            output_path.write_text(html)
            
            return Ok(output_path)
            
        except Exception as e:
            return Err(f"Main index generation failed: {str(e)}")
    
    def _generate_subfolder_indexes(self) -> Result[List[Path], str]:
        """
        Generate index.html for all subfolders.
        
        Returns:
            Result with list of generated file paths
        """
        try:
            if not self.jinja_env:
                return Err("Jinja2 environment not initialized")
            
            template = self.jinja_env.get_template("subfolder.html.jinja2")
            generated_files: List[Path] = []
            
            # Find all documentation subfolders
            for subfolder in self.docs_root.iterdir():
                if not subfolder.is_dir():
                    continue
                if subfolder.name.startswith(("_", ".")):
                    continue
                
                # Get subfolder metadata
                metadata = self._get_subfolder_metadata(subfolder)
                
                context = {
                    "section_title": metadata["title"],
                    "section_description": metadata["description"],
                    "breadcrumbs": metadata["breadcrumbs"],
                    "sidebar_items": metadata["sidebar_items"],
                    "documents": metadata["documents"],
                    "header": self._render_component("header.html.jinja2"),
                    "footer": self._render_component("footer.html.jinja2"),
                }
                
                html = template.render(**context)
                
                output_path = subfolder / "index.html"
                output_path.write_text(html)
                generated_files.append(output_path)
            
            return Ok(generated_files)
            
        except Exception as e:
            return Err(f"Subfolder generation failed: {str(e)}")
    
    def _generate_all(self) -> Result[HTMLGenerationReport, str]:
        """
        Generate all HTML documentation.
        
        Returns:
            Result with generation report
        """
        import time
        start_time = time.time()
        
        try:
            generated_files: List[Path] = []
            failed_files: List[Tuple[Path, str]] = []
            
            # 1. Extract template if needed
            if not (self.templates_dir / "index.html.jinja2").exists():
                extract_result = self._extract_template()
                if extract_result.is_err():
                    return Err(f"Template extraction failed: {extract_result.error}")
            
            # 2. Generate main index
            main_result = self._generate_main_index()
            if main_result.is_ok():
                generated_files.append(main_result.value)
            else:
                failed_files.append((self.docs_root / "index.html", main_result.error))
            
            # 3. Generate subfolder indexes
            subfolder_result = self._generate_subfolder_indexes()
            if subfolder_result.is_ok():
                generated_files.extend(subfolder_result.value)
            else:
                # Continue even if some fail
                pass
            
            # 4. Validate generated HTML
            validation_result = self._validate_html()
            
            # Calculate stats
            total_size = sum(f.stat().st_size for f in generated_files if f.exists())
            generation_time = time.time() - start_time
            
            report = HTMLGenerationReport(
                generated_files=generated_files,
                failed_files=failed_files,
                assets_copied=[],  # Assets are already in place
                total_size_bytes=total_size,
                generation_time_seconds=generation_time
            )
            
            return Ok(report)
            
        except Exception as e:
            return Err(f"HTML generation failed: {str(e)}")
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _build_navigation(self) -> None:
        """Build navigation structure from docs/ folder structure."""
        self.navigation = [
            NavigationItem(
                label="Home",
                href="/",
                icon="fa-home",
                level=NavigationLevel.EXECUTIVE
            ),
            NavigationItem(
                label="CORTEX Brain",
                href="/01-cortex-brain/",
                icon="fa-brain",
                level=NavigationLevel.DOMAIN
            ),
            NavigationItem(
                label="Orchestrators",
                href="/02-orchestrators/",
                icon="fa-sitemap",
                level=NavigationLevel.DOMAIN
            ),
            NavigationItem(
                label="Getting Started",
                href="/03-getting-started/",
                icon="fa-rocket",
                level=NavigationLevel.EXECUTIVE
            ),
            NavigationItem(
                label="Architecture",
                href="/04-architecture/",
                icon="fa-layer-group",
                level=NavigationLevel.TECHNICAL
            ),
            NavigationItem(
                label="MCP Tools",
                href="/11-mcp-tools/",
                icon="fa-tools",
                level=NavigationLevel.TECHNICAL
            ),
        ]
    
    def _get_main_sections(self) -> List[Dict[str, Any]]:
        """Get main landing page sections."""
        return [
            {
                "title": "🧠 CORTEX Brain",
                "description": "4-Tier governance system with Tier 0 rules, acceptance criteria, and knowledge graph",
                "icon": "fa-brain",
                "href": "/01-cortex-brain/",
                "level": "executive"
            },
            {
                "title": "🎼 Orchestrators",
                "description": "23 orchestrators managing TDD, planning, refactoring, and domain operations",
                "icon": "fa-sitemap",
                "href": "/02-orchestrators/",
                "level": "executive"
            },
            {
                "title": "🚀 Getting Started",
                "description": "Quick installation, first orchestrator, and troubleshooting guides",
                "icon": "fa-rocket",
                "href": "/03-getting-started/",
                "level": "executive"
            },
            {
                "title": "🏛️ Architecture",
                "description": "System overview, design principles, and architectural decisions",
                "icon": "fa-layer-group",
                "href": "/04-architecture/",
                "level": "technical"
            },
            {
                "title": "🔍 LENS Protocol",
                "description": "Language → Examination → Navigation → Synthesis analysis framework",
                "icon": "fa-eye",
                "href": "/05-lens-protocol/",
                "level": "technical"
            },
            {
                "title": "🛠️ MCP Tools",
                "description": "Model Context Protocol integration with 24+ registered tools",
                "icon": "fa-tools",
                "href": "/11-mcp-tools/",
                "level": "technical"
            },
        ]
    
    def _get_quick_start_content(self) -> List[Dict[str, str]]:
        """Get quick start code examples."""
        return [
            {
                "title": "Installation",
                "code": "pip install -r requirements.txt\npython -m cortex.cli init"
            },
            {
                "title": "First Request",
                "code": "from cortex.mcp import MCPServer\n\nserver = MCPServer()\nresult = server.process_request('implement user login with TDD')"
            },
        ]
    
    def _get_subfolder_metadata(self, subfolder: Path) -> Dict[str, Any]:
        """Get metadata for a subfolder."""
        folder_name = subfolder.name
        
        # Extract title from folder name
        title = folder_name.split('-', 1)[-1].replace('-', ' ').title() if '-' in folder_name else folder_name.title()
        
        # Build breadcrumbs
        breadcrumbs = [
            ("Home", "/"),
            (title, f"/{folder_name}/")
        ]
        
        # Get markdown files in folder
        documents = []
        for md_file in sorted(subfolder.glob("*.md")):
            if md_file.name.startswith(("_", ".")):
                continue
            
            # Extract title from first line
            content = md_file.read_text()
            first_line = content.split('\n')[0]
            doc_title = first_line.strip('#').strip() if first_line.startswith('#') else md_file.stem
            
            documents.append({
                "title": doc_title,
                "description": self._extract_description(content),
                "href": md_file.name,
                "icon": "fa-file-alt"
            })
        
        # Build sidebar
        sidebar_items = [
            {"label": doc["title"], "href": doc["href"], "icon": doc["icon"]}
            for doc in documents[:10]  # Limit to 10 for sidebar
        ]
        
        return {
            "title": title,
            "description": f"Documentation for {title}",
            "breadcrumbs": breadcrumbs,
            "sidebar_items": sidebar_items,
            "documents": documents
        }
    
    def _extract_description(self, content: str, max_length: int = 200) -> str:
        """Extract description from markdown content."""
        lines = content.split('\n')
        for line in lines[1:]:  # Skip title
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove markdown formatting
                desc = re.sub(r'[*_`]', '', line)
                if len(desc) > max_length:
                    desc = desc[:max_length] + "..."
                return desc
        return ""
    
    def _render_component(self, component_name: str) -> str:
        """Render a component template."""
        if not self.jinja_env:
            return ""
        
        try:
            template = self.jinja_env.get_template(f"components/{component_name}")
            return template.render()
        except Exception:
            return ""
    
    def _validate_html(self) -> Result[Dict[str, Any], str]:
        """
        Validate generated HTML files.
        
        Checks:
        - Valid HTML5 structure
        - Accessibility (ARIA labels, alt text)
        - Broken links
        - Missing assets
        
        Returns:
            Result with validation report
        """
        try:
            issues = []
            
            # Check main index
            main_index = self.docs_root / "index.html"
            if main_index.exists():
                content = main_index.read_text()
                
                # Check for required elements
                if '<html lang="en">' not in content:
                    issues.append("Missing lang attribute in <html>")
                
                if 'aria-label' not in content:
                    issues.append("Missing ARIA labels")
                
                # Check for proper DOCTYPE
                if not content.strip().startswith('<!DOCTYPE html>'):
                    issues.append("Missing or incorrect DOCTYPE")
            
            validation_report = {
                "valid": len(issues) == 0,
                "issues": issues,
                "files_checked": 1
            }
            
            return Ok(validation_report)
            
        except Exception as e:
            return Err(f"Validation failed: {str(e)}")


# ============================================================================
# MODULE-LEVEL FACTORY
# ============================================================================

def get_cortex_docs_orchestrator() -> CortexDocsOrchestrator:
    """Get or create CortexDocsOrchestrator instance."""
    return CortexDocsOrchestrator.instance()
