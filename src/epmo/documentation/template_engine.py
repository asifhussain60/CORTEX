"""
Enhanced Template Engine for CORTEX EPM Documentation

Handles both textual content and visual references with support for
customizable templates, multiple output formats, and multi-modal content
including Mermaid diagrams and AI image prompts.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - Part of CORTEX 3.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import asdict
import json
from datetime import datetime

try:
    from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    logging.warning("Jinja2 not available - using basic string templating")

from .models import (
    EPMDocumentationModel, DocumentationSection, TemplateConfiguration,
    GenerationConfig, DocumentationFormat, MultiModalDiagram, ImagePrompt
)

logger = logging.getLogger(__name__)


class TemplateEngine:
    """
    Enhanced template engine supporting multi-modal documentation generation.
    
    Features:
    - Jinja2 templates with custom filters and functions
    - Multi-modal content support (text + diagrams + images)
    - Multiple output formats (Markdown, HTML, JSON)
    - Customizable templates and themes
    - Visual content management and references
    """
    
    def __init__(
        self,
        template_dir: Optional[Path] = None,
        config: Optional[TemplateConfiguration] = None
    ):
        """
        Initialize template engine.
        
        Args:
            template_dir: Directory containing template files
            config: Template configuration
        """
        self.template_dir = template_dir or Path(__file__).parent / 'templates'
        self.config = config or TemplateConfiguration("comprehensive")
        
        # Initialize Jinja2 environment if available
        self.jinja_env = None
        if JINJA2_AVAILABLE:
            self._setup_jinja_environment()
        
        # Create template directory if it doesn't exist
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize default templates
        self._ensure_default_templates()
    
    def _setup_jinja_environment(self):
        """Setup Jinja2 environment with custom filters and functions."""
        try:
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )
            
            # Add custom filters
            self.jinja_env.filters['format_complexity'] = self._format_complexity
            self.jinja_env.filters['format_health_score'] = self._format_health_score
            self.jinja_env.filters['format_file_size'] = self._format_file_size
            self.jinja_env.filters['truncate_list'] = self._truncate_list
            self.jinja_env.filters['visual_stats'] = self._get_visual_stats
            
            # Add global functions
            self.jinja_env.globals['current_date'] = datetime.now().isoformat()
            self.jinja_env.globals['render_diagram'] = self._render_diagram
            self.jinja_env.globals['render_image_prompt'] = self._render_image_prompt
            
            logger.info("Jinja2 environment configured with custom filters")
            
        except Exception as e:
            logger.warning(f"Could not setup Jinja2 environment: {e}")
            self.jinja_env = None
    
    def render_template(
        self,
        template_name: str,
        model: EPMDocumentationModel,
        output_format: DocumentationFormat = DocumentationFormat.MARKDOWN
    ) -> str:
        """
        Render documentation using specified template.
        
        Args:
            template_name: Name of template file
            model: EPM documentation model
            output_format: Output format
            
        Returns:
            Rendered template content
        """
        logger.info(f"Rendering template: {template_name} for {model.metadata.epmo_name}")
        
        # Prepare template context
        context = self._prepare_template_context(model, output_format)
        
        if self.jinja_env:
            return self._render_jinja_template(template_name, context)
        else:
            return self._render_basic_template(template_name, context)
    
    def _prepare_template_context(
        self,
        model: EPMDocumentationModel,
        output_format: DocumentationFormat
    ) -> Dict[str, Any]:
        """Prepare complete context for template rendering."""
        
        # Base model data
        context = {
            'model': model,
            'metadata': model.metadata,
            'files': model.files,
            'architecture': model.architecture,
            'health': model.health,
            'dependencies': model.dependencies,
            'sections': model.sections,
            'diagrams': model.diagrams,
            'multi_modal_diagrams': model.multi_modal_diagrams,
            'image_prompts': model.image_prompts,
            'remediation': model.remediation,
            'quality_badges': model.quality_badges,
            'warnings': model.warnings,
            
            # Configuration
            'config': self.config,
            'output_format': output_format,
            'include_sections': self.config.include_sections,
            'include_diagrams': self.config.include_diagrams,
            'include_health_badges': self.config.include_health_badges,
            'include_code_examples': self.config.include_code_examples,
            
            # Computed values
            'summary_stats': model.get_summary_stats(),
            'visual_stats': model.get_visual_stats(),
            'priority_remediation': model.get_priority_remediation_items(),
            'auto_fixable_items': model.get_auto_fixable_items(),
            'complex_files': model.get_files_by_complexity(5),
            'all_diagrams': model.get_all_diagrams(),
            'mermaid_diagrams': model.get_mermaid_diagrams(),
            'all_image_prompts': model.get_image_prompts_all(),
            'has_visual_content': model.has_visual_content(),
            
            # Helper functions
            'format_timestamp': lambda ts: datetime.fromisoformat(ts).strftime('%Y-%m-%d %H:%M:%S'),
            'percentage': lambda value, total: f"{(value/total*100):.1f}%" if total > 0 else "0%",
            'status_emoji': self._get_status_emoji,
            'priority_emoji': self._get_priority_emoji,
            'complexity_level': self._get_complexity_level,
        }
        
        # Add custom sections from config
        context.update(self.config.custom_sections)
        
        return context
    
    def _render_jinja_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render template using Jinja2."""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering Jinja2 template {template_name}: {e}")
            return self._render_fallback_template(template_name, context)
    
    def _render_basic_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render template using basic string substitution."""
        template_path = self.template_dir / template_name
        
        if not template_path.exists():
            logger.warning(f"Template not found: {template_path}")
            return self._render_fallback_template(template_name, context)
        
        try:
            template_content = template_path.read_text(encoding='utf-8')
            
            # Basic string substitution for common variables
            replacements = {
                '{{epmo_name}}': context['metadata'].epmo_name,
                '{{generated_at}}': context['metadata'].generated_at,
                '{{total_files}}': str(context['summary_stats']['total_files']),
                '{{total_classes}}': str(context['summary_stats']['total_classes']),
                '{{total_functions}}': str(context['summary_stats']['total_functions']),
                '{{health_score}}': f"{context['summary_stats']['health_score']:.1f}" if context['health'] else "N/A",
                '{{total_diagrams}}': str(context['visual_stats']['total_diagrams']),
            }
            
            rendered = template_content
            for placeholder, value in replacements.items():
                rendered = rendered.replace(placeholder, value)
            
            return rendered
            
        except Exception as e:
            logger.error(f"Error rendering basic template {template_name}: {e}")
            return self._render_fallback_template(template_name, context)
    
    def _render_fallback_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render minimal fallback template."""
        model = context['model']
        
        return f"""# {model.metadata.epmo_name} Documentation

**Generated:** {model.metadata.generated_at}  
**Template:** {template_name} (fallback)

## Overview

This Entry Point Module contains:
- **Files:** {context['summary_stats']['total_files']}
- **Classes:** {context['summary_stats']['total_classes']}
- **Functions:** {context['summary_stats']['total_functions']}
- **Health Score:** {context['summary_stats']['health_score']:.1f}/100

## Files

{chr(10).join([f"- `{f.relative_path}` - {f.module_name}" for f in model.files])}

---

*Generated by CORTEX EPM Documentation Generator*  
*Template rendering fallback mode*
"""
    
    def _ensure_default_templates(self):
        """Create default templates if they don't exist."""
        templates = {
            'comprehensive.md.j2': self._get_comprehensive_template(),
            'minimal.md.j2': self._get_minimal_template(),
            'api_reference.md.j2': self._get_api_template(),
            'architecture.md.j2': self._get_architecture_template(),
            'health_report.md.j2': self._get_health_template()
        }
        
        for template_name, content in templates.items():
            template_path = self.template_dir / template_name
            if not template_path.exists():
                template_path.write_text(content, encoding='utf-8')
                logger.info(f"Created default template: {template_name}")
    
    def _get_comprehensive_template(self) -> str:
        """Get comprehensive documentation template."""
        return '''# {{ model.metadata.epmo_name }} Documentation

{% if config.header_template %}
{{ config.header_template }}
{% endif %}

| Property | Value |
|----------|-------|
| **Generated** | {{ model.metadata.generated_at }} |
| **Version** | {{ model.metadata.version }} |
| **Health Score** | {{ "%.1f"|format(model.health.overall_score) }}/100 {% if model.health %}{% endif %} |
| **Components** | {{ summary_stats.total_files }} files, {{ summary_stats.total_classes }} classes, {{ summary_stats.total_functions }} functions |
{% if has_visual_content %}
| **Diagrams** | {{ visual_stats.total_diagrams }} ({{ visual_stats.mermaid_diagrams }} technical, {{ visual_stats.image_prompts }} visual) |
{% endif %}

{% if config.include_health_badges and quality_badges %}
**Quality:** {% for badge in quality_badges %}![{{ badge }}](https://img.shields.io/badge/{{ badge|replace(' ', '%20') }}-success-green) {% endfor %}
{% endif %}

## Table of Contents

- [Overview](#overview)
{% if 'architecture' in include_sections %}
- [Architecture](#architecture)
{% if has_visual_content %}
  - [Diagrams](#diagrams)
{% endif %}
{% endif %}
{% if 'api' in include_sections %}
- [API Reference](#api-reference)
{% endif %}
{% if 'health' in include_sections and model.health %}
- [Health Analysis](#health-analysis)
{% endif %}
{% if 'remediation' in include_sections and remediation %}
- [Remediation Guide](#remediation-guide)
{% endif %}

## Overview

This Entry Point Module contains **{{ summary_stats.total_files }} files** with **{{ summary_stats.total_classes }} classes** and **{{ summary_stats.total_functions }} functions**, totaling **{{ "{:,}"|format(summary_stats.total_lines) }} lines of code**.

{% if summary_stats.external_dependencies > 0 %}
The module has **{{ summary_stats.external_dependencies }} external dependencies**.
{% endif %}

{% if model.health %}
**Health Status:** {{ model.health.health_status|title }} (Score: {{ "%.1f"|format(model.health.overall_score) }}/100)

{% if model.health.issues_found > 0 %}
**Issues:** {{ model.health.issues_found }} total ({{ summary_stats.auto_fixable_items }} auto-fixable)
{% endif %}
{% endif %}

{% if has_visual_content %}
**Visual Documentation:** {{ visual_stats.total_diagrams }} diagrams ({{ visual_stats.mermaid_diagrams }} technical, {{ visual_stats.image_prompts }} presentation)
{% endif %}

{% if 'architecture' in include_sections %}
## Architecture

{% if model.architecture %}
### Structure

The architecture consists of {{ model.architecture.total_modules }} modules with {{ model.architecture.dependency_count }} dependencies.

{% if model.architecture.coupling_score > 0 %}
**Coupling Score:** {{ "%.2f"|format(model.architecture.coupling_score) }}  
**Cohesion Score:** {{ "%.2f"|format(model.architecture.cohesion_score) }}
{% endif %}

{% if model.architecture.circular_dependencies > 0 %}
⚠️ **Circular Dependencies:** {{ model.architecture.circular_dependencies }} detected
{% endif %}

### External Dependencies

{% if model.architecture.external_dependencies %}
{% for dep in model.architecture.external_dependencies[:10] %}
- `{{ dep }}`
{% endfor %}
{% if model.architecture.external_dependencies|length > 10 %}
- ... and {{ model.architecture.external_dependencies|length - 10 }} more
{% endif %}
{% endif %}
{% endif %}

{% if has_visual_content and config.include_diagrams %}
### Diagrams

{% for diagram in all_diagrams %}
{% if diagram.__class__.__name__ == 'MultiModalDiagram' %}
#### {{ diagram.title }}

{% if diagram.description %}
{{ diagram.description }}
{% endif %}

{% if diagram.mermaid_diagram %}
**Technical Diagram:**

```mermaid
{{ diagram.mermaid_diagram.mermaid_syntax }}
```
{% endif %}

{% if diagram.image_prompt %}
**Professional Visualization:**

{% if diagram.image_prompt.generated_image_path %}
![{{ diagram.title }}]({{ diagram.image_prompt.generated_image_path }})
{% else %}
*AI Generation Prompt:* [View Prompt]({{ diagram.image_prompt.prompt_file_path }})
{% if diagram.image_prompt.narrative_description %}
*Description:* {{ diagram.image_prompt.narrative_description }}
{% endif %}
{% endif %}
{% endif %}

{% else %}
#### {{ diagram.title }}

{% if diagram.description %}
{{ diagram.description }}
{% endif %}

```mermaid
{{ diagram.mermaid_syntax }}
```
{% endif %}
{% endfor %}
{% endif %}
{% endif %}

{% if 'api' in include_sections %}
## API Reference

{% for file_analysis in model.files %}
{% if file_analysis.classes or file_analysis.functions %}
### {{ file_analysis.module_name }}

*File: `{{ file_analysis.relative_path }}`*

{% if file_analysis.docstring %}
{{ file_analysis.docstring }}
{% endif %}

{% for class_model in file_analysis.classes %}
#### `{{ class_model.name }}`

{% if class_model.docstring %}
{{ class_model.docstring }}
{% endif %}

{% if class_model.base_classes %}
**Inherits:** {{ class_model.base_classes|join(', ') }}
{% endif %}

{% set public_methods = class_model.methods|selectattr("visibility", "equalto", "public")|list %}
{% if public_methods %}
**Methods:**
{% for method in public_methods %}
- `{{ method.name }}({{ method.parameters|join(', ') }})`{% if method.return_type %} → `{{ method.return_type }}`{% endif %}
{% if method.docstring %}
  {{ method.docstring }}
{% endif %}
{% endfor %}
{% endif %}
{% endfor %}

{% for function in file_analysis.functions %}
{% if function.visibility == 'public' %}
#### `{{ function.name }}({{ function.parameters|join(', ') }})`{% if function.return_type %} → `{{ function.return_type }}`{% endif %}

{% if function.docstring %}
{{ function.docstring }}
{% endif %}

{% if function.decorators %}
**Decorators:** {{ function.decorators|join(', ') }}
{% endif %}
{% endif %}
{% endfor %}
{% endif %}
{% endfor %}
{% endif %}

{% if 'health' in include_sections and model.health %}
## Health Analysis

**Overall Health Score:** {{ "%.1f"|format(model.health.overall_score) }}/100  
**Status:** {{ model.health.health_status|title }}

{% if model.health.dimension_scores %}
### Dimension Scores

{% for dimension, score in model.health.dimension_scores.items() %}
- **{{ dimension|title }}:** {{ "%.1f"|format(score) }}/100 {% if score >= 80 %}✅{% elif score >= 60 %}⚠️{% else %}❌{% endif %}
{% endfor %}
{% endif %}

{% if model.health.issues_found > 0 %}
### Issues Summary

- **Total Issues:** {{ model.health.issues_found }}
- **Auto-fixable:** {{ model.health.auto_fixable_issues }}
- **High Priority:** {{ model.health.priority_issues }}
{% if model.health.estimated_fix_time_minutes > 0 %}
- **Estimated Fix Time:** {{ "%.1f"|format(model.health.estimated_fix_time_minutes / 60) }} hours
{% endif %}
{% endif %}
{% endif %}

{% if 'remediation' in include_sections and remediation %}
## Remediation Guide

{% set high_priority = remediation|selectattr("priority", "equalto", "high")|list %}
{% if high_priority %}
### High Priority Items

{% for item in high_priority %}
#### 🔴 {{ item.description }}

**Priority:** {{ item.priority|title }}  
**Effort:** {{ item.estimated_effort_minutes }} minutes

{% if item.auto_fixable %}
**Auto-fixable:** ✅ Yes
{% endif %}

{% if item.affected_files %}
**Affected Files:** {{ item.affected_files[:3]|join(', ') }}{% if item.affected_files|length > 3 %} and {{ item.affected_files|length - 3 }} more{% endif %}
{% endif %}

{% if item.detailed_guidance %}
**Guidance:** {{ item.detailed_guidance }}
{% endif %}
{% endfor %}
{% endif %}

{% set auto_fixable = remediation|selectattr("auto_fixable", "equalto", true)|list %}
{% if auto_fixable %}
### Auto-fixable Items

{% for item in auto_fixable %}
#### ⚡ {{ item.description }}

**Effort:** {{ item.estimated_effort_minutes }} minutes
{% if item.affected_files %}
**Affected Files:** {{ item.affected_files[:3]|join(', ') }}
{% endif %}
{% endfor %}
{% endif %}
{% endif %}

---

{% if config.footer_template %}
{{ config.footer_template }}
{% else %}
*Generated by {{ model.metadata.generated_by }} on {{ model.metadata.generated_at }}*

{% if model.metadata.generation_time_seconds > 0 %}
*Generation time: {{ "%.2f"|format(model.metadata.generation_time_seconds) }} seconds*
{% endif %}

{% if warnings %}
**Warnings:**
{% for warning in warnings %}
- {{ warning }}
{% endfor %}
{% endif %}
{% endif %}
'''
    
    def _get_minimal_template(self) -> str:
        """Get minimal documentation template."""
        return '''# {{ model.metadata.epmo_name }}

**Generated:** {{ model.metadata.generated_at }}

## Overview

- **Files:** {{ summary_stats.total_files }}
- **Classes:** {{ summary_stats.total_classes }}  
- **Functions:** {{ summary_stats.total_functions }}
{% if model.health %}
- **Health:** {{ "%.1f"|format(model.health.overall_score) }}/100
{% endif %}

## Components

{% for file_analysis in model.files %}
- `{{ file_analysis.relative_path }}` - {{ file_analysis.module_name }}
{% endfor %}

---
*Generated by CORTEX EPM Documentation Generator*
'''
    
    def _get_api_template(self) -> str:
        """Get API reference template."""
        return '''# {{ model.metadata.epmo_name }} API Reference

{% for file_analysis in model.files %}
{% if file_analysis.classes or file_analysis.functions %}
## {{ file_analysis.module_name }}

*File: `{{ file_analysis.relative_path }}`*

{% for class_model in file_analysis.classes %}
### {{ class_model.name }}

{% if class_model.docstring %}
{{ class_model.docstring }}
{% endif %}

{% for method in class_model.methods %}
{% if method.visibility == 'public' %}
#### {{ method.name }}

`{{ method.name }}({{ method.parameters|join(', ') }})`{% if method.return_type %} → `{{ method.return_type }}`{% endif %}

{% if method.docstring %}
{{ method.docstring }}
{% endif %}
{% endif %}
{% endfor %}
{% endfor %}

{% for function in file_analysis.functions %}
{% if function.visibility == 'public' %}
### {{ function.name }}

`{{ function.name }}({{ function.parameters|join(', ') }})`{% if function.return_type %} → `{{ function.return_type }}`{% endif %}

{% if function.docstring %}
{{ function.docstring }}
{% endif %}
{% endif %}
{% endfor %}
{% endif %}
{% endfor %}
'''
    
    def _get_architecture_template(self) -> str:
        """Get architecture-focused template."""
        return '''# {{ model.metadata.epmo_name }} Architecture

## System Overview

{% if model.architecture %}
- **Modules:** {{ model.architecture.total_modules }}
- **Dependencies:** {{ model.architecture.dependency_count }}
- **Coupling:** {{ "%.2f"|format(model.architecture.coupling_score) }}
- **Cohesion:** {{ "%.2f"|format(model.architecture.cohesion_score) }}
{% endif %}

{% if has_visual_content and config.include_diagrams %}
## Architecture Diagrams

{% for diagram in all_diagrams %}
### {{ diagram.title }}

{% if diagram.__class__.__name__ == 'MultiModalDiagram' and diagram.mermaid_diagram %}
```mermaid
{{ diagram.mermaid_diagram.mermaid_syntax }}
```
{% elif diagram.mermaid_syntax %}
```mermaid
{{ diagram.mermaid_syntax }}
```
{% endif %}
{% endfor %}
{% endif %}

## Dependencies

{% if model.architecture and model.architecture.external_dependencies %}
### External Dependencies

{% for dep in model.architecture.external_dependencies %}
- {{ dep }}
{% endfor %}
{% endif %}

### Internal Dependencies

{% for dep in model.dependencies[:10] %}
- `{{ dep.source_module }}` → `{{ dep.target_module }}` ({{ dep.relationship_type }})
{% endfor %}
'''
    
    def _get_health_template(self) -> str:
        """Get health-focused template."""
        return '''# {{ model.metadata.epmo_name }} Health Report

## Overall Health

**Score:** {{ "%.1f"|format(model.health.overall_score) }}/100  
**Status:** {{ model.health.health_status|title }}

{% if model.health.dimension_scores %}
## Dimension Analysis

{% for dimension, score in model.health.dimension_scores.items() %}
- **{{ dimension|title }}:** {{ "%.1f"|format(score) }}/100
{% endfor %}
{% endif %}

## Issues Summary

- **Total Issues:** {{ model.health.issues_found }}
- **Auto-fixable:** {{ model.health.auto_fixable_issues }}
- **High Priority:** {{ model.health.priority_issues }}

## Remediation Plan

{% for item in priority_remediation %}
### {{ item.description }}

**Priority:** {{ item.priority|title }}  
**Effort:** {{ item.estimated_effort_minutes }} minutes  
{% if item.auto_fixable %}**Auto-fixable:** Yes{% endif %}
{% endfor %}
'''
    
    # Custom template filters
    def _format_complexity(self, value: Union[int, float]) -> str:
        """Format complexity score with descriptive label."""
        if value >= 20:
            return f"{value} (High)"
        elif value >= 10:
            return f"{value} (Medium)"
        else:
            return f"{value} (Low)"
    
    def _format_health_score(self, value: Union[int, float]) -> str:
        """Format health score with status indicator."""
        if value >= 90:
            return f"{value:.1f}/100 ✅ Excellent"
        elif value >= 80:
            return f"{value:.1f}/100 ✅ Good"
        elif value >= 70:
            return f"{value:.1f}/100 ⚠️ Fair"
        else:
            return f"{value:.1f}/100 ❌ Poor"
    
    def _format_file_size(self, bytes_size: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
    
    def _truncate_list(self, items: List[Any], limit: int = 5) -> List[Any]:
        """Truncate list to specified limit."""
        return items[:limit]
    
    def _get_visual_stats(self, model: EPMDocumentationModel) -> Dict[str, int]:
        """Get visual content statistics."""
        return model.get_visual_stats()
    
    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for status."""
        status_map = {
            'excellent': '✅',
            'good': '✅', 
            'fair': '⚠️',
            'poor': '❌',
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }
        return status_map.get(status.lower(), '⚪')
    
    def _get_priority_emoji(self, priority: str) -> str:
        """Get emoji for priority."""
        priority_map = {
            'high': '🔴',
            'medium': '🟡', 
            'low': '🟢'
        }
        return priority_map.get(priority.lower(), '⚪')
    
    def _get_complexity_level(self, complexity: Union[int, float]) -> str:
        """Get complexity level description."""
        if complexity >= 20:
            return "High"
        elif complexity >= 10:
            return "Medium"
        else:
            return "Low"
    
    def _render_diagram(self, diagram: Union[MultiModalDiagram, Any]) -> str:
        """Render diagram content."""
        if hasattr(diagram, 'mermaid_diagram') and diagram.mermaid_diagram:
            return f"```mermaid\n{diagram.mermaid_diagram.mermaid_syntax}\n```"
        elif hasattr(diagram, 'mermaid_syntax'):
            return f"```mermaid\n{diagram.mermaid_syntax}\n```"
        return "<!-- Diagram not available -->"
    
    def _render_image_prompt(self, prompt: ImagePrompt) -> str:
        """Render image prompt reference."""
        if prompt.generated_image_path:
            return f"![{prompt.title}]({prompt.generated_image_path})"
        elif prompt.prompt_file_path:
            return f"*[AI Generation Prompt]({prompt.prompt_file_path})*"
        return f"*{prompt.title} (prompt available)*"


def render_documentation(
    model: EPMDocumentationModel,
    template_name: str = "comprehensive.md.j2",
    output_format: DocumentationFormat = DocumentationFormat.MARKDOWN,
    template_dir: Optional[Path] = None,
    config: Optional[TemplateConfiguration] = None
) -> str:
    """
    Render documentation using template engine.
    
    Args:
        model: EPM documentation model
        template_name: Template file name
        output_format: Output format
        template_dir: Template directory
        config: Template configuration
        
    Returns:
        Rendered documentation content
    """
    engine = TemplateEngine(template_dir, config)
    return engine.render_template(template_name, model, output_format)