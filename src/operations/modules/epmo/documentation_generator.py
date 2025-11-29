"""
CORTEX 3.0 - EPM Documentation Generator (Feature 4 - Phase 4.2)
================================================================

⚠️ DEPRECATED - Use Enterprise Documentation Orchestrator instead
Location: cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py

This module is kept for backward compatibility but will be removed in v4.0.
For new documentation generation, use the Enterprise Documentation Orchestrator:
- Unified entry point for ALL doc generation
- Includes Discovery Engine, DALL-E prompts, narratives, story, executive summary
- Admin-only (not packaged for production)

Documentation generation pipeline that converts code analysis results
into comprehensive, readable documentation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Feature 4 - Phase 4.2 (Week 2)
Effort: 15 hours (documentation generation pipeline)
Dependencies: Phase 4.1 (Code Analysis Engine) - COMPLETED
Status: DEPRECATED (use Enterprise Documentation Orchestrator)
"""

import os
import sys
import json
import yaml
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import markdown
from jinja2 import Environment, FileSystemLoader, Template

# Add CORTEX to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))


@dataclass
class DocumentationConfig:
    """Configuration for documentation generation"""
    output_format: str = "markdown"  # markdown, html, rst
    include_code_examples: bool = True
    include_diagrams: bool = True
    include_metrics: bool = True
    template_style: str = "default"  # default, minimal, comprehensive
    output_directory: str = "docs/generated"


@dataclass
class DocumentSection:
    """A section of generated documentation"""
    title: str
    content: str
    level: int  # Heading level (1-6)
    order: int  # Display order
    section_type: str  # overview, api, examples, metrics
    metadata: Dict[str, Any] = None


class DocumentationGenerator:
    """
    Generates comprehensive documentation from code analysis results.
    
    Features:
    - Multiple output formats (Markdown, HTML, RST)
    - Configurable templates and styles
    - Code example extraction and formatting
    - Automatic table of contents generation
    - Cross-reference linking
    - Metrics and statistics integration
    """
    
    def __init__(self, brain_path: str, config: Optional[DocumentationConfig] = None):
        self.brain_path = Path(brain_path)
        self.config = config or DocumentationConfig()
        
        # Setup template environment
        template_dir = self.brain_path / "templates" / "documentation"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)) if template_dir.exists() else None,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Setup output directory
        self.output_dir = Path(self.config.output_directory)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_from_analysis(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate documentation from code analysis results.
        
        Args:
            analysis_results: Results from Phase 4.1 code analysis engine
            
        Returns:
            Dictionary mapping document names to file paths
        """
        generated_docs = {}
        
        # 1. Generate project overview
        overview_doc = self._generate_project_overview(analysis_results)
        overview_path = self._save_document("project-overview", overview_doc)
        generated_docs["project_overview"] = str(overview_path)
        
        # 2. Generate API documentation
        if "api_analysis" in analysis_results:
            api_doc = self._generate_api_documentation(analysis_results["api_analysis"])
            api_path = self._save_document("api-reference", api_doc)
            generated_docs["api_reference"] = str(api_path)
        
        # 3. Generate architecture documentation
        if "architecture_analysis" in analysis_results:
            arch_doc = self._generate_architecture_documentation(analysis_results["architecture_analysis"])
            arch_path = self._save_document("architecture", arch_doc)
            generated_docs["architecture"] = str(arch_path)
        
        # 4. Generate metrics documentation
        if "metrics" in analysis_results:
            metrics_doc = self._generate_metrics_documentation(analysis_results["metrics"])
            metrics_path = self._save_document("metrics", metrics_doc)
            generated_docs["metrics"] = str(metrics_path)
        
        # 5. Generate README if requested
        if self.config.template_style in ["comprehensive", "default"]:
            readme_doc = self._generate_readme(analysis_results, generated_docs)
            readme_path = self._save_document("README", readme_doc)
            generated_docs["readme"] = str(readme_path)
        
        return generated_docs
    
    def _generate_project_overview(self, analysis_results: Dict[str, Any]) -> str:
        """Generate project overview documentation"""
        sections = []
        
        # Project summary
        if "project_info" in analysis_results:
            project_info = analysis_results["project_info"]
            sections.append(DocumentSection(
                title="Project Overview",
                content=self._format_project_summary(project_info),
                level=1,
                order=1,
                section_type="overview"
            ))
        
        # File structure
        if "file_structure" in analysis_results:
            sections.append(DocumentSection(
                title="File Structure",
                content=self._format_file_structure(analysis_results["file_structure"]),
                level=2,
                order=2,
                section_type="overview"
            ))
        
        # Key components
        if "components" in analysis_results:
            sections.append(DocumentSection(
                title="Key Components",
                content=self._format_components(analysis_results["components"]),
                level=2,
                order=3,
                section_type="overview"
            ))
        
        return self._render_document(sections, "Project Overview")
    
    def _generate_api_documentation(self, api_analysis: Dict[str, Any]) -> str:
        """Generate API reference documentation"""
        sections = []
        
        # API overview
        sections.append(DocumentSection(
            title="API Reference",
            content="Complete API reference for all public interfaces.",
            level=1,
            order=1,
            section_type="api"
        ))
        
        # Classes
        if "classes" in api_analysis:
            for class_info in api_analysis["classes"]:
                sections.append(DocumentSection(
                    title=f"Class: {class_info['name']}",
                    content=self._format_class_documentation(class_info),
                    level=2,
                    order=len(sections) + 1,
                    section_type="api"
                ))
        
        # Functions
        if "functions" in api_analysis:
            for func_info in api_analysis["functions"]:
                sections.append(DocumentSection(
                    title=f"Function: {func_info['name']}",
                    content=self._format_function_documentation(func_info),
                    level=2,
                    order=len(sections) + 1,
                    section_type="api"
                ))
        
        return self._render_document(sections, "API Reference")
    
    def _generate_architecture_documentation(self, arch_analysis: Dict[str, Any]) -> str:
        """Generate architecture documentation"""
        sections = []
        
        sections.append(DocumentSection(
            title="Architecture Overview",
            content="System architecture and design patterns.",
            level=1,
            order=1,
            section_type="overview"
        ))
        
        # System layers
        if "layers" in arch_analysis:
            sections.append(DocumentSection(
                title="System Layers",
                content=self._format_system_layers(arch_analysis["layers"]),
                level=2,
                order=2,
                section_type="overview"
            ))
        
        # Dependencies
        if "dependencies" in arch_analysis:
            sections.append(DocumentSection(
                title="Dependencies",
                content=self._format_dependencies(arch_analysis["dependencies"]),
                level=2,
                order=3,
                section_type="overview"
            ))
        
        # Design patterns
        if "patterns" in arch_analysis:
            sections.append(DocumentSection(
                title="Design Patterns",
                content=self._format_design_patterns(arch_analysis["patterns"]),
                level=2,
                order=4,
                section_type="overview"
            ))
        
        return self._render_document(sections, "Architecture")
    
    def _generate_metrics_documentation(self, metrics: Dict[str, Any]) -> str:
        """Generate metrics and statistics documentation"""
        sections = []
        
        sections.append(DocumentSection(
            title="Project Metrics",
            content="Code quality metrics and statistics.",
            level=1,
            order=1,
            section_type="metrics"
        ))
        
        # Code quality metrics
        if "quality" in metrics:
            sections.append(DocumentSection(
                title="Code Quality",
                content=self._format_quality_metrics(metrics["quality"]),
                level=2,
                order=2,
                section_type="metrics"
            ))
        
        # Test coverage
        if "coverage" in metrics:
            sections.append(DocumentSection(
                title="Test Coverage",
                content=self._format_coverage_metrics(metrics["coverage"]),
                level=2,
                order=3,
                section_type="metrics"
            ))
        
        # Performance metrics
        if "performance" in metrics:
            sections.append(DocumentSection(
                title="Performance",
                content=self._format_performance_metrics(metrics["performance"]),
                level=2,
                order=4,
                section_type="metrics"
            ))
        
        return self._render_document(sections, "Metrics")
    
    def _generate_readme(self, analysis_results: Dict[str, Any], generated_docs: Dict[str, str]) -> str:
        """Generate comprehensive README"""
        sections = []
        
        # Project title and description
        project_name = analysis_results.get("project_info", {}).get("name", "Project")
        sections.append(DocumentSection(
            title=project_name,
            content=self._format_readme_intro(analysis_results),
            level=1,
            order=1,
            section_type="overview"
        ))
        
        # Quick start
        sections.append(DocumentSection(
            title="Quick Start",
            content=self._format_quick_start(analysis_results),
            level=2,
            order=2,
            section_type="examples"
        ))
        
        # Documentation links
        if generated_docs:
            sections.append(DocumentSection(
                title="Documentation",
                content=self._format_doc_links(generated_docs),
                level=2,
                order=3,
                section_type="overview"
            ))
        
        # Key features
        if "features" in analysis_results:
            sections.append(DocumentSection(
                title="Features",
                content=self._format_features(analysis_results["features"]),
                level=2,
                order=4,
                section_type="overview"
            ))
        
        return self._render_document(sections, "README")
    
    def _format_project_summary(self, project_info: Dict[str, Any]) -> str:
        """Format project summary section"""
        lines = []
        
        if "description" in project_info:
            lines.append(project_info["description"])
            lines.append("")
        
        if "version" in project_info:
            lines.append(f"**Version:** {project_info['version']}")
        
        if "language" in project_info:
            lines.append(f"**Language:** {project_info['language']}")
        
        if "framework" in project_info:
            lines.append(f"**Framework:** {project_info['framework']}")
        
        if "total_files" in project_info:
            lines.append(f"**Files:** {project_info['total_files']}")
        
        if "lines_of_code" in project_info:
            lines.append(f"**Lines of Code:** {project_info['lines_of_code']:,}")
        
        return "\n".join(lines)
    
    def _format_file_structure(self, file_structure: List[Dict[str, Any]]) -> str:
        """Format file structure as tree"""
        lines = ["```"]
        lines.append("project/")
        
        for item in file_structure[:20]:  # Limit to first 20 items
            if item.get("type") == "directory":
                lines.append(f"├── {item['name']}/")
            else:
                lines.append(f"├── {item['name']}")
        
        if len(file_structure) > 20:
            lines.append("└── ... (more files)")
        
        lines.append("```")
        return "\n".join(lines)
    
    def _format_components(self, components: List[Dict[str, Any]]) -> str:
        """Format key components"""
        lines = []
        
        for component in components:
            lines.append(f"### {component['name']}")
            if "description" in component:
                lines.append(component["description"])
            if "location" in component:
                lines.append(f"**Location:** `{component['location']}`")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_class_documentation(self, class_info: Dict[str, Any]) -> str:
        """Format class documentation"""
        lines = []
        
        # Class signature
        if "signature" in class_info:
            lines.append(f"```python")
            lines.append(class_info["signature"])
            lines.append("```")
            lines.append("")
        
        # Description
        if "description" in class_info:
            lines.append(class_info["description"])
            lines.append("")
        
        # Methods
        if "methods" in class_info:
            lines.append("**Methods:**")
            lines.append("")
            for method in class_info["methods"]:
                lines.append(f"- `{method['name']}`: {method.get('description', '')}")
            lines.append("")
        
        # Properties
        if "properties" in class_info:
            lines.append("**Properties:**")
            lines.append("")
            for prop in class_info["properties"]:
                lines.append(f"- `{prop['name']}`: {prop.get('description', '')}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_function_documentation(self, func_info: Dict[str, Any]) -> str:
        """Format function documentation"""
        lines = []
        
        # Function signature
        if "signature" in func_info:
            lines.append(f"```python")
            lines.append(func_info["signature"])
            lines.append("```")
            lines.append("")
        
        # Description
        if "description" in func_info:
            lines.append(func_info["description"])
            lines.append("")
        
        # Parameters
        if "parameters" in func_info:
            lines.append("**Parameters:**")
            lines.append("")
            for param in func_info["parameters"]:
                param_type = param.get("type", "Any")
                param_desc = param.get("description", "")
                lines.append(f"- `{param['name']}` ({param_type}): {param_desc}")
            lines.append("")
        
        # Returns
        if "returns" in func_info:
            lines.append("**Returns:**")
            lines.append("")
            returns = func_info["returns"]
            return_type = returns.get("type", "Any")
            return_desc = returns.get("description", "")
            lines.append(f"- {return_type}: {return_desc}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _render_document(self, sections: List[DocumentSection], title: str) -> str:
        """Render document sections into final format"""
        lines = []
        
        # Document header
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Table of contents (if multiple sections)
        if len(sections) > 3:
            lines.append("## Table of Contents")
            lines.append("")
            for section in sorted(sections, key=lambda s: s.order):
                indent = "  " * (section.level - 1)
                lines.append(f"{indent}- [{section.title}](#{section.title.lower().replace(' ', '-')})")
            lines.append("")
        
        # Sections content
        for section in sorted(sections, key=lambda s: s.order):
            # Section header
            header_prefix = "#" * section.level
            lines.append(f"{header_prefix} {section.title}")
            lines.append("")
            
            # Section content
            lines.append(section.content)
            lines.append("")
        
        return "\n".join(lines)
    
    def _save_document(self, name: str, content: str) -> Path:
        """Save document to file"""
        # Determine file extension based on output format
        extensions = {
            "markdown": ".md",
            "html": ".html",
            "rst": ".rst"
        }
        ext = extensions.get(self.config.output_format, ".md")
        
        # Save file
        file_path = self.output_dir / f"{name}{ext}"
        file_path.write_text(content, encoding="utf-8")
        
        return file_path
    
    # Additional formatting methods for other sections would be implemented here...
    # (quality metrics, coverage, performance, etc.)
    
    def _format_quality_metrics(self, quality: Dict[str, Any]) -> str:
        """Format code quality metrics"""
        lines = []
        if "score" in quality:
            lines.append(f"**Overall Score:** {quality['score']}/100")
        if "issues" in quality:
            lines.append(f"**Issues:** {quality['issues']}")
        return "\n".join(lines)
    
    def _format_coverage_metrics(self, coverage: Dict[str, Any]) -> str:
        """Format test coverage metrics"""
        lines = []
        if "percentage" in coverage:
            lines.append(f"**Test Coverage:** {coverage['percentage']}%")
        if "files_covered" in coverage:
            lines.append(f"**Files Covered:** {coverage['files_covered']}")
        return "\n".join(lines)
    
    def _format_performance_metrics(self, performance: Dict[str, Any]) -> str:
        """Format performance metrics"""
        lines = []
        if "response_time" in performance:
            lines.append(f"**Avg Response Time:** {performance['response_time']}ms")
        if "memory_usage" in performance:
            lines.append(f"**Memory Usage:** {performance['memory_usage']}MB")
        return "\n".join(lines)
    
    def _format_readme_intro(self, analysis_results: Dict[str, Any]) -> str:
        """Format README introduction"""
        project_info = analysis_results.get("project_info", {})
        description = project_info.get("description", "A software project.")
        return description
    
    def _format_quick_start(self, analysis_results: Dict[str, Any]) -> str:
        """Format quick start section"""
        return "```bash\n# Installation and usage instructions\n# (customize based on project type)\n```"
    
    def _format_doc_links(self, generated_docs: Dict[str, str]) -> str:
        """Format documentation links"""
        lines = []
        for doc_name, doc_path in generated_docs.items():
            if doc_name != "readme":
                formatted_name = doc_name.replace("_", " ").title()
                lines.append(f"- [{formatted_name}]({Path(doc_path).name})")
        return "\n".join(lines)
    
    def _format_features(self, features: List[str]) -> str:
        """Format features list"""
        lines = []
        for feature in features:
            lines.append(f"- {feature}")
        return "\n".join(lines)
    
    def _format_system_layers(self, layers: List[Dict[str, Any]]) -> str:
        """Format system layers"""
        lines = []
        for layer in layers:
            lines.append(f"### {layer['name']}")
            if "description" in layer:
                lines.append(layer["description"])
            lines.append("")
        return "\n".join(lines)
    
    def _format_dependencies(self, dependencies: List[Dict[str, Any]]) -> str:
        """Format dependencies"""
        lines = []
        for dep in dependencies:
            lines.append(f"- **{dep['name']}**: {dep.get('description', '')}")
        return "\n".join(lines)
    
    def _format_design_patterns(self, patterns: List[Dict[str, Any]]) -> str:
        """Format design patterns"""
        lines = []
        for pattern in patterns:
            lines.append(f"### {pattern['name']}")
            if "description" in pattern:
                lines.append(pattern["description"])
            lines.append("")
        return "\n".join(lines)


# Export for use in EPM operations
__all__ = ['DocumentationGenerator', 'DocumentationConfig', 'DocumentSection']