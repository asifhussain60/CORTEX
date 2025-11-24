"""
CORTEX 3.0 - EPM Template Engine (Feature 4 - Phase 4.3)
========================================================

Advanced template engine for flexible documentation generation
with Jinja2 integration and multiple output formats.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Feature 4 - Phase 4.3 (Week 2)
Effort: 10 hours (template system)
Dependencies: Phase 4.2 (Documentation Generator) - JUST COMPLETED
"""

import os
import sys
import json
import yaml
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import re

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
from jinja2.exceptions import TemplateError, TemplateNotFound

# Add CORTEX to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))


@dataclass
class TemplateConfig:
    """Configuration for template engine"""
    template_directory: str = "cortex-brain/templates/documentation"
    output_format: str = "markdown"  # markdown, html, rst, pdf
    custom_filters: Dict[str, Any] = None
    auto_escape: bool = False
    trim_blocks: bool = True
    lstrip_blocks: bool = True


@dataclass
class TemplateContext:
    """Context data for template rendering"""
    project_info: Dict[str, Any]
    analysis_results: Dict[str, Any]
    generation_metadata: Dict[str, Any]
    custom_variables: Dict[str, Any] = None


class TemplateEngine:
    """
    Advanced template engine for documentation generation.
    
    Features:
    - Jinja2 template processing with custom filters
    - Multiple output formats (Markdown, HTML, RST)
    - Template inheritance and composition
    - Auto-escaping for security
    - Custom template functions and filters
    - Template validation and error handling
    """
    
    def __init__(self, config: Optional[TemplateConfig] = None):
        self.config = config or TemplateConfig()
        self.template_dir = Path(self.config.template_directory)
        
        # Ensure template directory exists
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml']) if self.config.auto_escape else False,
            trim_blocks=self.config.trim_blocks,
            lstrip_blocks=self.config.lstrip_blocks
        )
        
        # Register custom filters and functions
        self._register_custom_filters()
        self._register_custom_functions()
        
        # Create default templates if they don't exist
        self._ensure_default_templates()
    
    def render_template(self, template_name: str, context: Union[TemplateContext, Dict[str, Any]]) -> str:
        """
        Render a template with the provided context.
        
        Args:
            template_name: Name of template file (with extension)
            context: Template context data
            
        Returns:
            Rendered template content
            
        Raises:
            TemplateNotFound: If template file doesn't exist
            TemplateError: If template has syntax errors
        """
        try:
            template = self.env.get_template(template_name)
            
            # Convert TemplateContext to dict if needed
            if isinstance(context, TemplateContext):
                context_dict = self._context_to_dict(context)
            else:
                context_dict = context
            
            # Add template metadata
            context_dict['_template'] = {
                'name': template_name,
                'rendered_at': datetime.now().isoformat(),
                'engine_version': '1.0.0'
            }
            
            return template.render(**context_dict)
            
        except TemplateNotFound:
            raise TemplateNotFound(f"Template '{template_name}' not found in {self.template_dir}")
        except TemplateError as e:
            raise TemplateError(f"Template rendering error in '{template_name}': {e}")
    
    def render_string(self, template_string: str, context: Union[TemplateContext, Dict[str, Any]]) -> str:
        """
        Render a template from string content.
        
        Args:
            template_string: Template content as string
            context: Template context data
            
        Returns:
            Rendered content
        """
        try:
            template = self.env.from_string(template_string)
            
            # Convert TemplateContext to dict if needed
            if isinstance(context, TemplateContext):
                context_dict = self._context_to_dict(context)
            else:
                context_dict = context
            
            return template.render(**context_dict)
            
        except TemplateError as e:
            raise TemplateError(f"String template rendering error: {e}")
    
    def list_templates(self, pattern: Optional[str] = None) -> List[str]:
        """
        List available templates, optionally filtered by pattern.
        
        Args:
            pattern: Optional regex pattern to filter template names
            
        Returns:
            List of template filenames
        """
        templates = []
        
        for template_file in self.template_dir.rglob("*.j2"):
            relative_path = template_file.relative_to(self.template_dir)
            template_name = str(relative_path)
            
            if pattern is None or re.search(pattern, template_name):
                templates.append(template_name)
        
        return sorted(templates)
    
    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """
        Validate a template for syntax errors.
        
        Args:
            template_name: Name of template to validate
            
        Returns:
            Validation results with errors/warnings
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'template_name': template_name
        }
        
        try:
            # Try to load and parse template
            template = self.env.get_template(template_name)
            
            # Check for common issues
            template_source = template.source
            
            # Check for undefined variables (basic check)
            undefined_vars = re.findall(r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}', template_source)
            if undefined_vars:
                validation_result['warnings'].append({
                    'type': 'undefined_variables',
                    'message': f"Template references variables that may be undefined: {set(undefined_vars)}"
                })
            
            # Check for missing includes/extends
            includes = re.findall(r'\{\%\s*include\s+[\'\"](.*?)[\'\"]', template_source)
            extends = re.findall(r'\{\%\s*extends\s+[\'\"](.*?)[\'\"]', template_source)
            
            for include_path in includes + extends:
                include_file = self.template_dir / include_path
                if not include_file.exists():
                    validation_result['errors'].append({
                        'type': 'missing_include',
                        'message': f"Referenced template not found: {include_path}"
                    })
                    validation_result['valid'] = False
            
        except TemplateNotFound:
            validation_result['valid'] = False
            validation_result['errors'].append({
                'type': 'template_not_found',
                'message': f"Template file not found: {template_name}"
            })
        except TemplateError as e:
            validation_result['valid'] = False
            validation_result['errors'].append({
                'type': 'syntax_error',
                'message': str(e)
            })
        
        return validation_result
    
    def create_template(self, template_name: str, content: str, overwrite: bool = False) -> bool:
        """
        Create a new template file.
        
        Args:
            template_name: Name for the new template
            content: Template content
            overwrite: Whether to overwrite existing template
            
        Returns:
            True if created successfully, False otherwise
        """
        template_path = self.template_dir / template_name
        
        if template_path.exists() and not overwrite:
            return False
        
        template_path.parent.mkdir(parents=True, exist_ok=True)
        template_path.write_text(content, encoding='utf-8')
        return True
    
    def _context_to_dict(self, context: TemplateContext) -> Dict[str, Any]:
        """Convert TemplateContext to dictionary for rendering"""
        base_dict = asdict(context)
        
        # Flatten structure for easier template access
        result = {}
        result.update(base_dict['project_info'])
        result.update(base_dict['analysis_results'])
        result['metadata'] = base_dict['generation_metadata']
        
        if base_dict.get('custom_variables'):
            result.update(base_dict['custom_variables'])
        
        return result
    
    def _register_custom_filters(self):
        """Register custom Jinja2 filters"""
        
        def markdown_escape(text):
            """Escape special markdown characters"""
            if not isinstance(text, str):
                text = str(text)
            
            # Escape markdown special characters
            escape_chars = ['*', '_', '`', '#', '+', '-', '.', '!', '[', ']', '(', ')']
            for char in escape_chars:
                text = text.replace(char, f'\\{char}')
            return text
        
        def code_block(text, language=''):
            """Wrap text in markdown code block"""
            if not isinstance(text, str):
                text = str(text)
            return f"```{language}\n{text}\n```"
        
        def humanize_number(number):
            """Format numbers in human-readable format"""
            if not isinstance(number, (int, float)):
                return str(number)
            
            if number >= 1_000_000:
                return f"{number / 1_000_000:.1f}M"
            elif number >= 1_000:
                return f"{number / 1_000:.1f}K"
            else:
                return str(number)
        
        def file_extension(filename):
            """Get file extension from filename"""
            return Path(filename).suffix.lstrip('.')
        
        def relative_path(full_path, base_path):
            """Get relative path from base path"""
            try:
                return str(Path(full_path).relative_to(Path(base_path)))
            except ValueError:
                return str(full_path)
        
        def format_datetime(dt, fmt='%Y-%m-%d %H:%M:%S'):
            """Format datetime with custom format"""
            if isinstance(dt, str):
                try:
                    dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                except ValueError:
                    return dt
            return dt.strftime(fmt) if dt else ''
        
        # Register filters with Jinja2 environment
        self.env.filters['markdown_escape'] = markdown_escape
        self.env.filters['code_block'] = code_block
        self.env.filters['humanize_number'] = humanize_number
        self.env.filters['file_extension'] = file_extension
        self.env.filters['relative_path'] = relative_path
        self.env.filters['format_datetime'] = format_datetime
        
        # Register custom filters from config
        if self.config.custom_filters:
            for name, filter_func in self.config.custom_filters.items():
                self.env.filters[name] = filter_func
    
    def _register_custom_functions(self):
        """Register custom Jinja2 global functions"""
        
        def include_file(file_path, fallback=''):
            """Include external file content"""
            try:
                full_path = self.template_dir / file_path
                if full_path.exists():
                    return full_path.read_text(encoding='utf-8')
                else:
                    return fallback
            except Exception:
                return fallback
        
        def generate_toc(sections, max_level=3):
            """Generate table of contents from sections"""
            toc_lines = []
            for section in sections:
                if hasattr(section, 'level') and section.level <= max_level:
                    indent = '  ' * (section.level - 1)
                    anchor = section.title.lower().replace(' ', '-').replace('_', '-')
                    toc_lines.append(f"{indent}- [{section.title}](#{anchor})")
            return '\n'.join(toc_lines)
        
        def format_file_list(files, max_files=20):
            """Format file list with truncation"""
            if len(files) <= max_files:
                return '\n'.join(f"- {f}" for f in files)
            else:
                shown_files = files[:max_files]
                remaining = len(files) - max_files
                result = '\n'.join(f"- {f}" for f in shown_files)
                result += f"\n- ... and {remaining} more files"
                return result
        
        # Register global functions
        self.env.globals['include_file'] = include_file
        self.env.globals['generate_toc'] = generate_toc
        self.env.globals['format_file_list'] = format_file_list
    
    def _ensure_default_templates(self):
        """Create default templates if they don't exist"""
        
        # README template
        readme_template = """# {{ name or 'Project' }}

{{ description or 'A software project description.' }}

{% if version %}**Version:** {{ version }}{% endif %}
{% if language %}**Language:** {{ language }}{% endif %}
{% if framework %}**Framework:** {{ framework }}{% endif %}

## Quick Start

```bash
# Installation and setup instructions
# (customize based on your project)
```

{% if features %}
## Features

{% for feature in features %}
- {{ feature }}
{% endfor %}
{% endif %}

{% if components %}
## Key Components

{% for component in components %}
### {{ component.name }}
{{ component.description or '' }}
{% if component.location %}**Location:** `{{ component.location }}`{% endif %}

{% endfor %}
{% endif %}

## Documentation

{% if generated_docs %}
{% for doc_name, doc_path in generated_docs.items() %}
{% if doc_name != 'readme' %}
- [{{ doc_name.replace('_', ' ').title() }}]({{ doc_path | basename }})
{% endif %}
{% endfor %}
{% endif %}

---

Generated on: {{ _template.rendered_at | format_datetime }}
"""
        
        # API Reference template
        api_template = """# API Reference

Complete API documentation for all public interfaces.

{% if classes %}
## Classes

{% for class_info in classes %}
### {{ class_info.name }}

{% if class_info.description %}{{ class_info.description }}{% endif %}

{% if class_info.signature %}
```python
{{ class_info.signature }}
```
{% endif %}

{% if class_info.methods %}
**Methods:**

{% for method in class_info.methods %}
- `{{ method.name }}`: {{ method.description or '' }}
{% endfor %}
{% endif %}

{% if class_info.properties %}
**Properties:**

{% for prop in class_info.properties %}
- `{{ prop.name }}`: {{ prop.description or '' }}
{% endfor %}
{% endif %}

{% endfor %}
{% endif %}

{% if functions %}
## Functions

{% for func_info in functions %}
### {{ func_info.name }}

{% if func_info.description %}{{ func_info.description }}{% endif %}

{% if func_info.signature %}
```python
{{ func_info.signature }}
```
{% endif %}

{% if func_info.parameters %}
**Parameters:**

{% for param in func_info.parameters %}
- `{{ param.name }}` ({{ param.type or 'Any' }}): {{ param.description or '' }}
{% endfor %}
{% endif %}

{% if func_info.returns %}
**Returns:**

{{ func_info.returns.type or 'Any' }}: {{ func_info.returns.description or '' }}
{% endif %}

{% endfor %}
{% endif %}

---

Generated on: {{ _template.rendered_at | format_datetime }}
"""
        
        # Metrics template
        metrics_template = """# Project Metrics

Code quality metrics and statistics.

{% if quality %}
## Code Quality

**Overall Score:** {{ quality.score or 'N/A' }}/100
**Issues:** {{ quality.issues or 'N/A' }}
{% endif %}

{% if coverage %}
## Test Coverage

**Test Coverage:** {{ coverage.percentage or 'N/A' }}%
**Files Covered:** {{ coverage.files_covered or 'N/A' }}
{% endif %}

{% if performance %}
## Performance

**Avg Response Time:** {{ performance.response_time or 'N/A' }}ms
**Memory Usage:** {{ performance.memory_usage or 'N/A' }}MB
{% endif %}

{% if total_files %}
## Project Statistics

- **Total Files:** {{ total_files | humanize_number }}
{% if lines_of_code %}- **Lines of Code:** {{ lines_of_code | humanize_number }}{% endif %}
{% if test_files %}- **Test Files:** {{ test_files }}{% endif %}
{% endif %}

---

Generated on: {{ _template.rendered_at | format_datetime }}
"""
        
        # Create templates
        default_templates = {
            'README.md.j2': readme_template,
            'api-reference.md.j2': api_template,
            'metrics.md.j2': metrics_template
        }
        
        for template_name, content in default_templates.items():
            template_path = self.template_dir / template_name
            if not template_path.exists():
                template_path.parent.mkdir(parents=True, exist_ok=True)
                template_path.write_text(content, encoding='utf-8')


# Export for use in EPM operations
__all__ = ['TemplateEngine', 'TemplateConfig', 'TemplateContext']