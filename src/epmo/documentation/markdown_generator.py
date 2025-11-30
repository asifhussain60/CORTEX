"""
Enhanced Markdown Generator for CORTEX EPM Documentation

Converts parsed AST data and dependency information into structured markdown
documentation with support for multi-modal content including Mermaid diagrams
and AI image prompts.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - Part of CORTEX 3.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import asdict

from .models import (
    EPMDocumentationModel, DocumentationSection, MermaidDiagram, 
    ImagePrompt, MultiModalDiagram, GenerationConfig, TemplateConfiguration,
    CodeElement, ClassModel, FileAnalysis, HealthMetrics, RemediationItem
)

logger = logging.getLogger(__name__)


class MarkdownGenerator:
    """
    Enhanced markdown generator with multi-modal content support.
    
    Generates comprehensive documentation from EPM analysis data including:
    - Code structure and API documentation
    - Health metrics and quality badges
    - Architecture diagrams (Mermaid + AI images)
    - Remediation guidance
    - Cross-references and navigation
    """
    
    def __init__(self, config: GenerationConfig):
        """
        Initialize markdown generator.
        
        Args:
            config: Generation configuration
        """
        self.config = config
        self.template_config = config.template_config
        
    def generate(self, model: EPMDocumentationModel) -> str:
        """
        Generate complete markdown documentation.
        
        Args:
            model: Complete EPM documentation model
            
        Returns:
            Generated markdown content
        """
        logger.info(f"Generating markdown for EPMO: {model.metadata.epmo_name}")
        
        sections = []
        
        # Generate header
        sections.append(self._generate_header(model))
        
        # Generate table of contents
        if len(model.sections) > 3:
            sections.append(self._generate_toc(model))
        
        # Generate overview section
        if 'overview' in self.template_config.include_sections:
            sections.append(self._generate_overview(model))
        
        # Generate architecture section with diagrams
        if 'architecture' in self.template_config.include_sections:
            sections.append(self._generate_architecture_section(model))
        
        # Generate API documentation
        if 'api' in self.template_config.include_sections:
            sections.append(self._generate_api_section(model))
        
        # Generate health section
        if 'health' in self.template_config.include_sections and model.health:
            sections.append(self._generate_health_section(model))
        
        # Generate remediation section
        if 'remediation' in self.template_config.include_sections and model.remediation:
            sections.append(self._generate_remediation_section(model))
        
        # Generate custom sections
        for section_id, content in self.template_config.custom_sections.items():
            sections.append(f"## {section_id.title()}\n\n{content}\n")
        
        # Generate footer
        sections.append(self._generate_footer(model))
        
        # Join all sections
        markdown = "\n\n".join(sections)
        
        logger.info(f"Generated {len(markdown)} characters of markdown")
        return markdown
    
    def _generate_header(self, model: EPMDocumentationModel) -> str:
        """Generate document header with metadata."""
        header_parts = []
        
        # Title
        header_parts.append(f"# {model.metadata.epmo_name} Documentation")
        
        # Metadata table
        metadata_table = [
            "| Property | Value |",
            "|----------|-------|",
            f"| **Generated** | {model.metadata.generated_at} |",
            f"| **Version** | {model.metadata.version} |",
            f"| **Format** | {model.metadata.format.value} |"
        ]
        
        if model.health:
            metadata_table.append(f"| **Health Score** | {model.health.overall_score:.1f}/100 |")
        
        if model.architecture:
            metadata_table.append(f"| **Modules** | {model.architecture.total_modules} |")
            metadata_table.append(f"| **Classes** | {model.architecture.total_classes} |")
            metadata_table.append(f"| **Functions** | {model.architecture.total_functions} |")
        
        # Visual content stats
        visual_stats = model.get_visual_stats()
        if visual_stats['total_diagrams'] > 0:
            metadata_table.append(f"| **Diagrams** | {visual_stats['total_diagrams']} ({visual_stats['mermaid_diagrams']} Mermaid, {visual_stats['image_prompts']} AI) |")
        
        header_parts.append("\n".join(metadata_table))
        
        # Quality badges
        if self.template_config.include_health_badges and model.quality_badges:
            badges = " ".join([f"![{badge}](https://img.shields.io/badge/{badge.replace(' ', '%20')}-success-green)" 
                             for badge in model.quality_badges])
            header_parts.append(f"**Quality:** {badges}")
        
        return "\n\n".join(header_parts)
    
    def _generate_toc(self, model: EPMDocumentationModel) -> str:
        """Generate table of contents."""
        toc_items = []
        
        # Standard sections
        if 'overview' in self.template_config.include_sections:
            toc_items.append("- [Overview](#overview)")
        
        if 'architecture' in self.template_config.include_sections:
            toc_items.append("- [Architecture](#architecture)")
            if model.has_visual_content():
                toc_items.append("  - [Diagrams](#diagrams)")
        
        if 'api' in self.template_config.include_sections:
            toc_items.append("- [API Reference](#api-reference)")
            # Add subsections for files
            for file_analysis in model.files[:3]:  # Limit TOC size
                module_name = file_analysis.module_name
                toc_items.append(f"  - [{module_name}](#{module_name.lower()})")
        
        if 'health' in self.template_config.include_sections and model.health:
            toc_items.append("- [Health Analysis](#health-analysis)")
        
        if 'remediation' in self.template_config.include_sections and model.remediation:
            toc_items.append("- [Remediation Guide](#remediation-guide)")
        
        # Custom sections
        for section_id in self.template_config.custom_sections.keys():
            toc_items.append(f"- [{section_id.title()}](#{section_id.lower().replace(' ', '-')})")
        
        if not toc_items:
            return ""
        
        return "## Table of Contents\n\n" + "\n".join(toc_items)
    
    def _generate_overview(self, model: EPMDocumentationModel) -> str:
        """Generate overview section."""
        overview_parts = ["## Overview"]
        
        # Summary statistics
        stats = model.get_summary_stats()
        overview_parts.append("### Summary")
        overview_parts.append(
            f"This Entry Point Module contains **{stats['total_files']} files** "
            f"with **{stats['total_classes']} classes** and **{stats['total_functions']} functions**, "
            f"totaling **{stats['total_lines']:,} lines of code**."
        )
        
        if stats['external_dependencies'] > 0:
            overview_parts.append(f"The module has **{stats['external_dependencies']} external dependencies**.")
        
        # Health summary
        if model.health:
            health_status = model.health.health_status.title()
            overview_parts.append(
                f"**Health Status:** {health_status} "
                f"(Score: {model.health.overall_score:.1f}/100)"
            )
            
            if model.health.issues_found > 0:
                fixable = stats.get('auto_fixable_items', 0)
                overview_parts.append(
                    f"**Issues:** {model.health.issues_found} total "
                    f"({fixable} auto-fixable)"
                )
        
        # Visual content summary
        if model.has_visual_content():
            visual_stats = model.get_visual_stats()
            overview_parts.append(
                f"**Visual Documentation:** {visual_stats['total_diagrams']} diagrams "
                f"({visual_stats['mermaid_diagrams']} technical, {visual_stats['image_prompts']} presentation)"
            )
        
        return "\n\n".join(overview_parts)
    
    def _generate_architecture_section(self, model: EPMDocumentationModel) -> str:
        """Generate architecture section with diagrams."""
        arch_parts = ["## Architecture"]
        
        if model.architecture:
            arch = model.architecture
            
            # Architecture overview
            arch_parts.append("### Structure")
            arch_parts.append(
                f"The architecture consists of {arch.total_modules} modules "
                f"with {arch.dependency_count} dependencies."
            )
            
            if arch.coupling_score > 0:
                arch_parts.append(f"**Coupling Score:** {arch.coupling_score:.2f}")
                arch_parts.append(f"**Cohesion Score:** {arch.cohesion_score:.2f}")
            
            if arch.circular_dependencies > 0:
                arch_parts.append(f"⚠️ **Circular Dependencies:** {arch.circular_dependencies} detected")
            
            # External dependencies
            if arch.external_dependencies:
                arch_parts.append("### External Dependencies")
                deps_list = "\n".join([f"- `{dep}`" for dep in arch.external_dependencies[:10]])
                if len(arch.external_dependencies) > 10:
                    deps_list += f"\n- ... and {len(arch.external_dependencies) - 10} more"
                arch_parts.append(deps_list)
        
        # Visual content section
        if model.has_visual_content():
            arch_parts.append("### Diagrams")
            
            # Add all diagrams
            all_diagrams = model.get_all_diagrams()
            for diagram in all_diagrams:
                if isinstance(diagram, MultiModalDiagram):
                    arch_parts.append(self._format_multimodal_diagram(diagram))
                else:
                    arch_parts.append(self._format_mermaid_diagram(diagram))
        
        return "\n\n".join(arch_parts)
    
    def _format_multimodal_diagram(self, diagram: MultiModalDiagram) -> str:
        """Format a multi-modal diagram with both Mermaid and image prompt."""
        parts = [f"#### {diagram.title}"]
        
        if diagram.description:
            parts.append(diagram.description)
        
        # Mermaid diagram
        if diagram.mermaid_diagram:
            parts.append("**Technical Diagram:**")
            parts.append(f"```mermaid\n{diagram.mermaid_diagram.mermaid_syntax}\n```")
        
        # Image prompt reference
        if diagram.image_prompt:
            parts.append("**Professional Visualization:**")
            if diagram.image_prompt.generated_image_path:
                parts.append(f"![{diagram.title}]({diagram.image_prompt.generated_image_path})")
            else:
                parts.append(f"*AI Generation Prompt:* [View Prompt]({diagram.image_prompt.prompt_file_path})")
                if diagram.image_prompt.narrative_description:
                    parts.append(f"*Description:* {diagram.image_prompt.narrative_description}")
        
        return "\n\n".join(parts)
    
    def _format_mermaid_diagram(self, diagram: MermaidDiagram) -> str:
        """Format a standard Mermaid diagram."""
        parts = [f"#### {diagram.title}"]
        
        if diagram.description:
            parts.append(diagram.description)
        
        parts.append(f"```mermaid\n{diagram.mermaid_syntax}\n```")
        
        return "\n\n".join(parts)
    
    def _generate_api_section(self, model: EPMDocumentationModel) -> str:
        """Generate API documentation section."""
        api_parts = ["## API Reference"]
        
        for file_analysis in model.files:
            if not (file_analysis.classes or file_analysis.functions):
                continue
                
            api_parts.append(f"### {file_analysis.module_name}")
            api_parts.append(f"*File: `{file_analysis.relative_path}`*")
            
            if file_analysis.docstring:
                api_parts.append(file_analysis.docstring)
            
            # Classes
            for class_model in file_analysis.classes:
                api_parts.append(self._format_class_documentation(class_model))
            
            # Functions
            for function in file_analysis.functions:
                if function.visibility == 'public':  # Only document public functions
                    api_parts.append(self._format_function_documentation(function))
        
        return "\n\n".join(api_parts)
    
    def _format_class_documentation(self, class_model: ClassModel) -> str:
        """Format documentation for a class."""
        parts = [f"#### `{class_model.name}`"]
        
        if class_model.docstring:
            parts.append(class_model.docstring)
        
        if class_model.base_classes:
            parts.append(f"**Inherits:** {', '.join(class_model.base_classes)}")
        
        # Methods
        public_methods = [m for m in class_model.methods if m.visibility == 'public']
        if public_methods:
            parts.append("**Methods:**")
            for method in public_methods:
                method_sig = f"`{method.name}({', '.join(method.parameters)})`"
                if method.return_type:
                    method_sig += f" → `{method.return_type}`"
                parts.append(f"- {method_sig}")
                if method.docstring:
                    parts.append(f"  {method.docstring}")
        
        return "\n\n".join(parts)
    
    def _format_function_documentation(self, function: CodeElement) -> str:
        """Format documentation for a function."""
        parts = []
        
        # Function signature
        signature = f"`{function.name}({', '.join(function.parameters)})`"
        if function.return_type:
            signature += f" → `{function.return_type}`"
        
        parts.append(f"#### {signature}")
        
        if function.docstring:
            parts.append(function.docstring)
        
        if function.decorators:
            parts.append(f"**Decorators:** {', '.join(function.decorators)}")
        
        return "\n\n".join(parts)
    
    def _generate_health_section(self, model: EPMDocumentationModel) -> str:
        """Generate health analysis section."""
        if not model.health:
            return ""
        
        health_parts = ["## Health Analysis"]
        
        health = model.health
        
        # Overall score
        health_parts.append(f"**Overall Health Score:** {health.overall_score:.1f}/100")
        health_parts.append(f"**Status:** {health.health_status.title()}")
        
        # Dimension scores
        if health.dimension_scores:
            health_parts.append("### Dimension Scores")
            for dimension, score in health.dimension_scores.items():
                status_emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
                health_parts.append(f"- **{dimension.title()}:** {score:.1f}/100 {status_emoji}")
        
        # Issues summary
        if health.issues_found > 0:
            health_parts.append("### Issues Summary")
            health_parts.append(f"- **Total Issues:** {health.issues_found}")
            health_parts.append(f"- **Auto-fixable:** {health.auto_fixable_issues}")
            health_parts.append(f"- **High Priority:** {health.priority_issues}")
            
            if health.estimated_fix_time_minutes > 0:
                hours = health.estimated_fix_time_minutes / 60
                health_parts.append(f"- **Estimated Fix Time:** {hours:.1f} hours")
        
        return "\n\n".join(health_parts)
    
    def _generate_remediation_section(self, model: EPMDocumentationModel) -> str:
        """Generate remediation guide section."""
        if not model.remediation:
            return ""
        
        remediation_parts = ["## Remediation Guide"]
        
        # High priority items
        high_priority = [r for r in model.remediation if r.priority == 'high']
        if high_priority:
            remediation_parts.append("### High Priority Items")
            for item in high_priority:
                remediation_parts.append(self._format_remediation_item(item))
        
        # Auto-fixable items
        auto_fixable = [r for r in model.remediation if r.auto_fixable]
        if auto_fixable:
            remediation_parts.append("### Auto-fixable Items")
            for item in auto_fixable:
                remediation_parts.append(self._format_remediation_item(item))
        
        # Other items
        other_items = [r for r in model.remediation 
                      if r.priority != 'high' and not r.auto_fixable]
        if other_items:
            remediation_parts.append("### Other Improvements")
            for item in other_items[:5]:  # Limit to top 5
                remediation_parts.append(self._format_remediation_item(item))
        
        return "\n\n".join(remediation_parts)
    
    def _format_remediation_item(self, item: RemediationItem) -> str:
        """Format a remediation item."""
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        emoji = priority_emoji.get(item.priority, "⚪")
        
        parts = [f"#### {emoji} {item.description}"]
        parts.append(f"**Priority:** {item.priority.title()}")
        parts.append(f"**Effort:** {item.estimated_effort_minutes} minutes")
        
        if item.auto_fixable:
            parts.append("**Auto-fixable:** ✅ Yes")
        
        if item.affected_files:
            files_list = ", ".join(f"`{f}`" for f in item.affected_files[:3])
            if len(item.affected_files) > 3:
                files_list += f" and {len(item.affected_files) - 3} more"
            parts.append(f"**Affected Files:** {files_list}")
        
        if item.detailed_guidance:
            parts.append(f"**Guidance:** {item.detailed_guidance}")
        
        return "\n\n".join(parts)
    
    def _generate_footer(self, model: EPMDocumentationModel) -> str:
        """Generate document footer."""
        footer_parts = []
        
        # Generation info
        footer_parts.append("---")
        footer_parts.append(f"*Generated by {model.metadata.generated_by} on {model.metadata.generated_at}*")
        
        if model.metadata.generation_time_seconds > 0:
            footer_parts.append(f"*Generation time: {model.metadata.generation_time_seconds:.2f} seconds*")
        
        # Warnings
        if model.warnings:
            footer_parts.append("\n**Warnings:**")
            for warning in model.warnings:
                footer_parts.append(f"- {warning}")
        
        return "\n\n".join(footer_parts)


def generate_markdown_documentation(
    model: EPMDocumentationModel,
    output_path: Optional[Path] = None,
    config: Optional[GenerationConfig] = None
) -> str:
    """
    Generate markdown documentation from EPM model.
    
    Args:
        model: Complete EPM documentation model
        output_path: Optional path to write markdown file
        config: Optional generation configuration
        
    Returns:
        Generated markdown content
    """
    if config is None:
        config = GenerationConfig()
    
    generator = MarkdownGenerator(config)
    markdown_content = generator.generate(model)
    
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown_content, encoding='utf-8')
        logger.info(f"Markdown documentation written to {output_path}")
    
    return markdown_content