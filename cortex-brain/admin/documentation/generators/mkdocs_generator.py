"""
MkDocs Generator

Generates MkDocs static site configuration and content pages.
Handles navigation structure, page generation, and site build.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
import yaml

from .base_generator import (
    BaseDocumentationGenerator,
    GenerationConfig,
    GenerationResult,
    GeneratorType
)


logger = logging.getLogger(__name__)


class MkDocsGenerator(BaseDocumentationGenerator):
    """
    Generates MkDocs static site for CORTEX documentation.
    
    Features:
    - Generates mkdocs.yml configuration
    - Creates navigation structure
    - Generates documentation pages from templates
    - Builds static site
    """
    
    def __init__(self, config: GenerationConfig, workspace_root: Optional[Path] = None):
        """Initialize MkDocs generator"""
        super().__init__(config, workspace_root)
        
        # Load page definitions
        self.page_definitions = self.load_config_file("page-definitions.yaml")
        
        # MkDocs configuration
        self.mkdocs_config = {
            "site_name": "CORTEX Documentation",
            "site_description": "AI-powered development assistant with persistent memory",
            "site_author": "Asif Hussain",
            "site_url": "https://cortex-docs.example.com",
            "repo_url": "https://github.com/asifhussain60/CORTEX",
            "repo_name": "CORTEX",
            "copyright": "© 2024-2025 Asif Hussain. All rights reserved.",
            "theme": {
                "name": "material",
                "palette": {
                    "primary": "indigo",
                    "accent": "purple"
                },
                "features": [
                    "navigation.tabs",
                    "navigation.sections",
                    "navigation.expand",
                    "navigation.top",
                    "search.highlight",
                    "search.share",
                    "toc.follow"
                ]
            },
            "plugins": [
                "search",
                "mermaid2"
            ],
            "markdown_extensions": [
                "pymdownx.highlight",
                "pymdownx.superfences",
                "pymdownx.tabbed",
                "admonition",
                "attr_list",
                "md_in_html"
            ],
            "nav": []
        }
    
    def get_component_name(self) -> str:
        """Component name for logging"""
        return "MkDocs Site"
    
    def collect_data(self) -> Dict[str, Any]:
        """
        Collect data needed for MkDocs generation.
        
        Returns:
            Dictionary with page definitions, existing docs, navigation structure
        """
        data = {
            "page_definitions": self.page_definitions or {},
            "workspace_root": str(self.workspace_root),
            "output_path": str(self.output_path),
            "docs_path": str(self.workspace_root / "docs")
        }
        
        # Scan existing documentation
        docs_path = self.workspace_root / "docs"
        if docs_path.exists():
            existing_pages = list(docs_path.rglob("*.md"))
            data["existing_pages"] = [str(p) for p in existing_pages]
        
        return data
    
    def generate(self) -> GenerationResult:
        """
        Generate MkDocs site configuration and content.
        
        Returns:
            GenerationResult with files generated
        """
        logger.info("Generating MkDocs site...")
        
        # Generate mkdocs.yml configuration
        self._generate_mkdocs_config()
        
        # Generate navigation structure
        self._generate_navigation()
        
        # Generate documentation pages
        self._generate_pages()
        
        # Generate index page
        self._generate_index_page()
        
        # Save generation metadata
        self.save_metadata("mkdocs-generation-metadata.json", {
            "pages_generated": len(self.files_generated),
            "config_file": str(self.workspace_root / "mkdocs.yml"),
            "site_name": self.mkdocs_config["site_name"]
        })
        
        return self._create_success_result(metadata={
            "pages_generated": len(self.files_generated),
            "navigation_sections": len(self.mkdocs_config["nav"])
        })
    
    def _generate_mkdocs_config(self):
        """Generate mkdocs.yml configuration file"""
        mkdocs_file = self.workspace_root / "mkdocs.yml"
        
        try:
            with open(mkdocs_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.mkdocs_config, f, default_flow_style=False, sort_keys=False)
            
            self.record_file_generated(mkdocs_file)
            
        except Exception as e:
            self.record_error(f"Failed to generate mkdocs.yml: {e}")
    
    def _generate_navigation(self):
        """Generate navigation structure from page definitions"""
        if not self.page_definitions:
            self.record_warning("No page definitions found, using default navigation")
            self._use_default_navigation()
            return
        
        pages = self.page_definitions.get("pages", [])
        
        # Group pages by section
        sections = {}
        for page in pages:
            output_path = page.get("output_path", "")
            if "/" in output_path:
                section = output_path.split("/")[0]
                if section not in sections:
                    sections[section] = []
                sections[section].append(page)
        
        # Build navigation structure
        nav = []
        for section, section_pages in sections.items():
            section_title = section.replace("-", " ").title()
            section_nav = {section_title: []}
            
            for page in sorted(section_pages, key=lambda p: p.get("priority", "medium")):
                page_name = page.get("name", "Untitled")
                page_path = page.get("output_path", "")
                section_nav[section_title].append({page_name: page_path})
            
            nav.append(section_nav)
        
        self.mkdocs_config["nav"] = nav
    
    def _use_default_navigation(self):
        """Use default navigation structure"""
        self.mkdocs_config["nav"] = [
            {"Home": "index.md"},
            {"Getting Started": [
                {"Quick Start": "getting-started/quick-start.md"},
                {"Installation": "getting-started/installation.md"},
                {"Configuration": "getting-started/configuration.md"}
            ]},
            {"Architecture": [
                {"Overview": "architecture/overview.md"},
                {"Tier System": "architecture/tier-system.md"},
                {"Agent Architecture": "architecture/agents.md"}
            ]},
            {"Operations": [
                {"Overview": "operations/overview.md"},
                {"Entry Point Modules": "operations/entry-point-modules.md"}
            ]},
            {"Reference": [
                {"API Reference": "reference/api.md"},
                {"Configuration": "reference/configuration.md"}
            ]}
        ]
    
    def _generate_pages(self):
        """Generate documentation pages from templates"""
        if not self.page_definitions:
            self.record_warning("No page definitions found, skipping page generation")
            return
        
        pages = self.page_definitions.get("pages", [])
        docs_path = self.workspace_root / "docs"
        
        for page in pages:
            try:
                page_name = page.get("name", "Untitled")
                output_path = page.get("output_path", "")
                
                if not output_path:
                    self.record_warning(f"Page '{page_name}' missing output_path, skipping")
                    continue
                
                # Generate page content
                content = self._generate_page_content(page)
                
                # Write page file
                page_file = docs_path / output_path
                page_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(page_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.record_file_generated(page_file)
                
            except Exception as e:
                self.record_error(f"Failed to generate page {page}: {e}")
    
    def _generate_page_content(self, page: Dict[str, Any]) -> str:
        """
        Generate page content from page definition.
        
        Args:
            page: Page definition dictionary
        
        Returns:
            Markdown content for the page
        """
        page_name = page.get("name", "Untitled")
        
        # Start with frontmatter
        content = "---\n"
        content += f"title: {page_name}\n"
        content += "generated: true\n"
        content += "---\n\n"
        
        # Add page heading
        content += f"# {page_name}\n\n"
        
        # Add placeholder content
        content += f"This page documents {page_name}.\n\n"
        content += "## Overview\n\n"
        content += f"{page_name} provides essential functionality for CORTEX.\n\n"
        content += "## Features\n\n"
        content += "- Feature 1\n"
        content += "- Feature 2\n"
        content += "- Feature 3\n\n"
        
        # Add footer
        content += "\n---\n\n"
        content += "*This page was automatically generated by CORTEX Documentation System.*\n"
        
        return content
    
    def _generate_index_page(self):
        """Generate main index.md page"""
        docs_path = self.workspace_root / "docs"
        index_file = docs_path / "index.md"
        
        content = """---
title: CORTEX Documentation
generated: true
---

# Welcome to CORTEX

CORTEX is an AI-powered development assistant with persistent memory and intelligent context management.

## Quick Links

- [Quick Start Guide](getting-started/quick-start.md)
- [Architecture Overview](architecture/overview.md)
- [Operations Guide](operations/overview.md)
- [API Reference](reference/api.md)

## What is CORTEX?

CORTEX transforms GitHub Copilot from a brilliant amnesiac into an experienced team member with:

- ✅ Persistent conversation memory (Tier 1)
- ✅ Pattern learning and knowledge graphs (Tier 2)
- ✅ Project context intelligence (Tier 3)
- ✅ Immutable governance rules (Tier 0)

## Getting Started

1. [Install CORTEX](getting-started/installation.md)
2. [Configure your workspace](getting-started/configuration.md)
3. [Follow the Quick Start guide](getting-started/quick-start.md)

---

*Documentation generated by CORTEX Documentation System*
"""
        
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.record_file_generated(index_file)
            
        except Exception as e:
            self.record_error(f"Failed to generate index page: {e}")
    
    def validate(self) -> bool:
        """
        Validate generated MkDocs site.
        
        Returns:
            True if validation passes
        """
        # Check mkdocs.yml exists
        mkdocs_file = self.workspace_root / "mkdocs.yml"
        if not mkdocs_file.exists():
            self.record_error("mkdocs.yml not generated")
            return False
        
        # Check index.md exists
        index_file = self.workspace_root / "docs" / "index.md"
        if not index_file.exists():
            self.record_error("index.md not generated")
            return False
        
        # Validate navigation structure
        if not self.mkdocs_config.get("nav"):
            self.record_warning("Navigation structure is empty")
        
        return True
