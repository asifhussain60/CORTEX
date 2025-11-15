"""
CORTEX 3.0 Track B: Template Engine
===================================

Advanced template engine for zero-execution help responses and dynamic content generation.
Provides intelligent template selection, variable substitution, and contextual adaptation.

Key Features:
- Zero-execution response generation
- Dynamic template selection based on context
- Variable substitution and content adaptation
- Template performance optimization
- Integration with CORTEX brain for learning

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import logging
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import yaml


class TemplateType(Enum):
    """Types of templates."""
    HELP = "help"
    ERROR = "error"
    SUGGESTION = "suggestion"
    STATUS = "status"
    GUIDE = "guide"
    WORKFLOW = "workflow"
    CONTEXT = "context"


class TemplateFormat(Enum):
    """Template output formats."""
    MARKDOWN = "markdown"
    PLAIN_TEXT = "plain_text"
    JSON = "json"
    HTML = "html"


@dataclass
class TemplateVariable:
    """Template variable definition."""
    name: str
    var_type: str  # 'string', 'number', 'boolean', 'list', 'dict'
    description: str
    required: bool = False
    default_value: Any = None
    validator: Optional[str] = None  # Regex pattern for validation


@dataclass
class Template:
    """Template definition."""
    template_id: str
    name: str
    description: str
    template_type: TemplateType
    format: TemplateFormat
    content: str
    variables: List[TemplateVariable] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)  # Conditions for template selection
    priority: int = 0
    tags: List[str] = field(default_factory=list)
    usage_count: int = 0
    last_used: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class TemplateContext:
    """Context for template rendering."""
    user_request: str
    request_type: str
    variables: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, Any] = field(default_factory=dict)
    session_data: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RenderedTemplate:
    """Result of template rendering."""
    template_id: str
    content: str
    format: TemplateFormat
    variables_used: Dict[str, Any]
    render_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class TemplateEngine:
    """
    Advanced template engine for CORTEX Track B
    
    Provides intelligent template selection, rendering, and optimization
    for zero-execution help responses and dynamic content generation.
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        self.logger = logging.getLogger("cortex.track_b.template_engine")
        
        # Template storage
        self.templates: Dict[str, Template] = {}
        self.template_index: Dict[str, Set[str]] = {}  # Index for fast lookup
        
        # Template directories
        self.templates_dir = templates_dir or Path(__file__).parent / "templates"
        self.custom_templates_dir = self.templates_dir / "custom"
        
        # Rendering context
        self.global_variables: Dict[str, Any] = {}
        self.custom_filters: Dict[str, Callable] = {}
        
        # Performance tracking
        self.performance_stats: Dict[str, Dict[str, Any]] = {}
        
        # Initialize built-in templates and load external ones
        self._initialize_builtin_templates()
        self._load_external_templates()
        self._initialize_custom_filters()
    
    def _initialize_builtin_templates(self):
        """Initialize built-in templates."""
        builtin_templates = [
            # Help templates
            Template(
                template_id="help_quick_reference",
                name="Quick Reference",
                description="Quick reference table for common commands",
                template_type=TemplateType.HELP,
                format=TemplateFormat.MARKDOWN,
                content="""# CORTEX Quick Reference

| Command | Description | Example |
|---------|-------------|---------|
{{#each commands}}
| `{{command}}` | {{description}} | {{example}} |
{{/each}}

**Total Commands:** {{command_count}}
**Last Updated:** {{timestamp}}
""",
                variables=[
                    TemplateVariable("commands", "list", "List of command objects"),
                    TemplateVariable("command_count", "number", "Total number of commands"),
                    TemplateVariable("timestamp", "string", "Current timestamp")
                ],
                conditions=["request_type == 'help'", "format == 'quick'"],
                priority=10,
                tags=["help", "reference", "commands"]
            ),
            
            Template(
                template_id="help_detailed",
                name="Detailed Help",
                description="Detailed help with categories and examples",
                template_type=TemplateType.HELP,
                format=TemplateFormat.MARKDOWN,
                content="""# CORTEX Detailed Help

{{#each categories}}
## {{category_name}}

{{description}}

### Available Commands:
{{#each commands}}
- **`{{command}}`**: {{description}}
  - Usage: `{{usage}}`
  - Example: {{example}}
{{/each}}

---
{{/each}}

**Need more help?** Use `help <specific_command>` for detailed information.
""",
                variables=[
                    TemplateVariable("categories", "list", "List of command categories"),
                ],
                conditions=["request_type == 'help'", "format == 'detailed'"],
                priority=8,
                tags=["help", "detailed", "categories"]
            ),
            
            # Status templates
            Template(
                template_id="status_system",
                name="System Status",
                description="Current system status and health",
                template_type=TemplateType.STATUS,
                format=TemplateFormat.MARKDOWN,
                content="""# CORTEX System Status

**Status:** {{status_indicator}} {{status}}  
**Version:** {{version}}  
**Uptime:** {{uptime}}

## Components Status

| Component | Status | Details |
|-----------|---------|---------|
{{#each components}}
| {{name}} | {{status_icon}} {{status}} | {{details}} |
{{/each}}

## Recent Activity
- {{recent_activity}}

**Last Updated:** {{timestamp}}
""",
                variables=[
                    TemplateVariable("status", "string", "Overall system status"),
                    TemplateVariable("status_indicator", "string", "Status indicator emoji"),
                    TemplateVariable("version", "string", "CORTEX version"),
                    TemplateVariable("uptime", "string", "System uptime"),
                    TemplateVariable("components", "list", "List of component statuses"),
                    TemplateVariable("recent_activity", "string", "Recent activity summary"),
                    TemplateVariable("timestamp", "string", "Current timestamp")
                ],
                conditions=["request_type == 'status'"],
                priority=10,
                tags=["status", "system", "health"]
            ),
            
            # Error templates
            Template(
                template_id="error_command_not_found",
                name="Command Not Found",
                description="Error message for unknown commands",
                template_type=TemplateType.ERROR,
                format=TemplateFormat.MARKDOWN,
                content="""❌ **Command Not Found**

The command `{{command}}` is not recognized.

**Did you mean:**
{{#each suggestions}}
- `{{suggestion}}` - {{description}}
{{/each}}

**Available commands:** Use `help` to see all available commands.
""",
                variables=[
                    TemplateVariable("command", "string", "The unrecognized command"),
                    TemplateVariable("suggestions", "list", "List of suggested commands")
                ],
                conditions=["error_type == 'command_not_found'"],
                priority=10,
                tags=["error", "command", "suggestions"]
            ),
            
            # Workflow templates
            Template(
                template_id="workflow_feature_planning",
                name="Feature Planning Workflow",
                description="Interactive feature planning guide",
                template_type=TemplateType.WORKFLOW,
                format=TemplateFormat.MARKDOWN,
                content="""# 🎯 Feature Planning Workflow

**Feature:** {{feature_name}}

## Planning Steps:

### 1. Requirements Analysis
- [ ] Define user stories
- [ ] Identify acceptance criteria
- [ ] List technical requirements

### 2. Design Phase
- [ ] Create architecture design
- [ ] Define API contracts
- [ ] Plan database schema (if applicable)

### 3. Implementation Planning
- [ ] Break down into tasks
- [ ] Estimate effort
- [ ] Identify dependencies

### 4. Testing Strategy
- [ ] Plan unit tests
- [ ] Design integration tests
- [ ] Consider edge cases

**Next Step:** {{next_step}}

**Estimated Duration:** {{estimated_duration}}
""",
                variables=[
                    TemplateVariable("feature_name", "string", "Name of the feature"),
                    TemplateVariable("next_step", "string", "Suggested next step"),
                    TemplateVariable("estimated_duration", "string", "Estimated duration")
                ],
                conditions=["request_type == 'plan_feature'"],
                priority=9,
                tags=["workflow", "planning", "feature"]
            ),
        ]
        
        # Register built-in templates
        for template in builtin_templates:
            self._register_template(template)
    
    def _load_external_templates(self):
        """Load templates from external files."""
        try:
            # Ensure template directories exist
            self.templates_dir.mkdir(exist_ok=True)
            self.custom_templates_dir.mkdir(exist_ok=True)
            
            # Load YAML template definitions
            for template_file in self.templates_dir.glob("*.yaml"):
                self._load_template_file(template_file)
            
            # Load custom templates
            for template_file in self.custom_templates_dir.glob("*.yaml"):
                self._load_template_file(template_file)
                
        except Exception as e:
            self.logger.error(f"Error loading external templates: {e}")
    
    def _load_template_file(self, template_file: Path):
        """Load templates from a YAML file."""
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if 'templates' in data:
                for template_data in data['templates']:
                    template = self._create_template_from_dict(template_data)
                    if template:
                        self._register_template(template)
                        
        except Exception as e:
            self.logger.error(f"Error loading template file {template_file}: {e}")
    
    def _create_template_from_dict(self, data: Dict[str, Any]) -> Optional[Template]:
        """Create a Template object from dictionary data."""
        try:
            # Parse variables
            variables = []
            for var_data in data.get('variables', []):
                variable = TemplateVariable(
                    name=var_data['name'],
                    var_type=var_data['type'],
                    description=var_data['description'],
                    required=var_data.get('required', False),
                    default_value=var_data.get('default'),
                    validator=var_data.get('validator')
                )
                variables.append(variable)
            
            template = Template(
                template_id=data['id'],
                name=data['name'],
                description=data['description'],
                template_type=TemplateType(data['type']),
                format=TemplateFormat(data['format']),
                content=data['content'],
                variables=variables,
                conditions=data.get('conditions', []),
                priority=data.get('priority', 0),
                tags=data.get('tags', [])
            )
            
            return template
            
        except Exception as e:
            self.logger.error(f"Error creating template from dict: {e}")
            return None
    
    def _register_template(self, template: Template):
        """Register a template in the engine."""
        self.templates[template.template_id] = template
        
        # Update index for fast lookup
        for tag in template.tags:
            if tag not in self.template_index:
                self.template_index[tag] = set()
            self.template_index[tag].add(template.template_id)
        
        # Index by type
        type_key = template.template_type.value
        if type_key not in self.template_index:
            self.template_index[type_key] = set()
        self.template_index[type_key].add(template.template_id)
        
        self.logger.debug(f"Registered template: {template.template_id}")
    
    def _initialize_custom_filters(self):
        """Initialize custom template filters."""
        self.custom_filters.update({
            'format_timestamp': self._filter_format_timestamp,
            'truncate': self._filter_truncate,
            'capitalize_words': self._filter_capitalize_words,
            'status_icon': self._filter_status_icon,
            'file_extension': self._filter_file_extension,
            'relative_time': self._filter_relative_time,
        })
    
    def _filter_format_timestamp(self, timestamp: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format timestamp filter."""
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp)
            else:
                dt = timestamp
            return dt.strftime(format_str)
        except:
            return str(timestamp)
    
    def _filter_truncate(self, text: str, length: int = 50) -> str:
        """Truncate text filter."""
        if len(text) <= length:
            return text
        return text[:length-3] + "..."
    
    def _filter_capitalize_words(self, text: str) -> str:
        """Capitalize words filter."""
        return text.title()
    
    def _filter_status_icon(self, status: str) -> str:
        """Status icon filter."""
        icons = {
            'running': '🟢',
            'stopped': '🔴',
            'warning': '🟡',
            'error': '❌',
            'success': '✅',
            'pending': '⏳',
            'unknown': '❓'
        }
        return icons.get(status.lower(), '❓')
    
    def _filter_file_extension(self, filepath: str) -> str:
        """File extension filter."""
        return Path(filepath).suffix[1:] if Path(filepath).suffix else ""
    
    def _filter_relative_time(self, timestamp: str) -> str:
        """Relative time filter."""
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp)
            else:
                dt = timestamp
            
            diff = datetime.now() - dt
            
            if diff.days > 0:
                return f"{diff.days} days ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hours ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minutes ago"
            else:
                return "just now"
        except:
            return str(timestamp)
    
    def select_template(self, context: TemplateContext) -> Optional[Template]:
        """Select the best template for the given context."""
        try:
            candidates = []
            
            # Find templates matching request type
            request_type = context.request_type
            if request_type in self.template_index:
                candidates.extend(self.template_index[request_type])
            
            # Find templates matching tags from user request
            request_words = context.user_request.lower().split()
            for word in request_words:
                if word in self.template_index:
                    candidates.extend(self.template_index[word])
            
            if not candidates:
                self.logger.warning(f"No template candidates found for request: {context.user_request}")
                return None
            
            # Score candidates based on conditions and priority
            scored_templates = []
            
            for template_id in set(candidates):  # Remove duplicates
                template = self.templates[template_id]
                score = self._score_template(template, context)
                
                if score > 0:  # Only include templates that match conditions
                    scored_templates.append((score, template))
            
            if not scored_templates:
                self.logger.warning(f"No templates matched conditions for: {context.user_request}")
                return None
            
            # Return highest scoring template
            best_template = max(scored_templates, key=lambda x: x[0])[1]
            
            self.logger.debug(f"Selected template: {best_template.template_id} (score: {max(scored_templates, key=lambda x: x[0])[0]})")
            
            return best_template
            
        except Exception as e:
            self.logger.error(f"Error selecting template: {e}")
            return None
    
    def _score_template(self, template: Template, context: TemplateContext) -> float:
        """Score a template based on how well it matches the context."""
        try:
            score = template.priority  # Base score from priority
            
            # Check conditions
            conditions_met = True
            for condition in template.conditions:
                if not self._evaluate_condition(condition, context):
                    conditions_met = False
                    break
            
            if not conditions_met:
                return 0  # Template doesn't match conditions
            
            # Boost score based on tag matches
            request_words = set(context.user_request.lower().split())
            matching_tags = request_words.intersection(set(template.tags))
            score += len(matching_tags) * 2
            
            # Boost based on usage frequency (popular templates)
            score += min(template.usage_count * 0.1, 5)
            
            # Reduce score for very recently used templates (diversity)
            if template.last_used and datetime.now() - template.last_used < timedelta(minutes=5):
                score *= 0.8
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error scoring template {template.template_id}: {e}")
            return 0
    
    def _evaluate_condition(self, condition: str, context: TemplateContext) -> bool:
        """Evaluate a template condition against the context."""
        try:
            # Simple condition evaluation
            # Format: "variable == value" or "variable != value"
            
            # Replace context variables
            eval_context = {
                'request_type': context.request_type,
                'format': context.environment.get('format', 'markdown'),
                'error_type': context.environment.get('error_type'),
                'user_request': context.user_request,
                **context.variables,
                **context.environment
            }
            
            # Simple evaluation for common patterns
            for var_name, var_value in eval_context.items():
                condition = condition.replace(var_name, f"'{var_value}'" if isinstance(var_value, str) else str(var_value))
            
            # Basic evaluation (secure subset)
            if '==' in condition:
                left, right = condition.split('==', 1)
                left_val = left.strip().strip("'\"")
                right_val = right.strip().strip("'\"")
                return left_val == right_val
            elif '!=' in condition:
                left, right = condition.split('!=', 1)
                left_val = left.strip().strip("'\"")
                right_val = right.strip().strip("'\"")
                return left_val != right_val
            elif 'in' in condition:
                left, right = condition.split(' in ', 1)
                left_val = left.strip().strip("'\"")
                right_val = right.strip().strip("'\"")
                return left_val in right_val
            
            return True  # Default to true for unknown conditions
            
        except Exception as e:
            self.logger.error(f"Error evaluating condition '{condition}': {e}")
            return False
    
    def render_template(self, template: Template, context: TemplateContext) -> RenderedTemplate:
        """Render a template with the given context."""
        start_time = datetime.now()
        
        try:
            # Prepare variables for rendering
            render_vars = self._prepare_render_variables(template, context)
            
            # Apply template rendering (simplified Handlebars-like syntax)
            rendered_content = self._render_content(template.content, render_vars)
            
            # Update template usage statistics
            template.usage_count += 1
            template.last_used = datetime.now()
            
            # Calculate render time
            render_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Update performance stats
            if template.template_id not in self.performance_stats:
                self.performance_stats[template.template_id] = {
                    'total_renders': 0,
                    'total_time_ms': 0,
                    'avg_time_ms': 0
                }
            
            stats = self.performance_stats[template.template_id]
            stats['total_renders'] += 1
            stats['total_time_ms'] += render_time
            stats['avg_time_ms'] = stats['total_time_ms'] / stats['total_renders']
            
            return RenderedTemplate(
                template_id=template.template_id,
                content=rendered_content,
                format=template.format,
                variables_used=render_vars,
                render_time_ms=render_time,
                metadata={
                    'template_name': template.name,
                    'template_type': template.template_type.value
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error rendering template {template.template_id}: {e}")
            # Return error template
            return RenderedTemplate(
                template_id="error",
                content=f"Error rendering template: {str(e)}",
                format=TemplateFormat.PLAIN_TEXT,
                variables_used={},
                render_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
    
    def _prepare_render_variables(self, template: Template, context: TemplateContext) -> Dict[str, Any]:
        """Prepare variables for template rendering."""
        render_vars = {}
        
        # Add global variables
        render_vars.update(self.global_variables)
        
        # Add context variables
        render_vars.update(context.variables)
        render_vars.update(context.environment)
        
        # Add automatic variables
        render_vars.update({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'current_time': datetime.now().isoformat(),
            'user_request': context.user_request,
            'request_type': context.request_type
        })
        
        # Validate required variables
        for var in template.variables:
            if var.required and var.name not in render_vars:
                if var.default_value is not None:
                    render_vars[var.name] = var.default_value
                else:
                    render_vars[var.name] = f"[{var.name} required]"
        
        return render_vars
    
    def _render_content(self, content: str, variables: Dict[str, Any]) -> str:
        """Render template content with variables (simplified implementation)."""
        try:
            rendered = content
            
            # Simple variable substitution: {{variable}}
            for var_name, var_value in variables.items():
                pattern = f"{{{{{var_name}}}}}"
                rendered = rendered.replace(pattern, str(var_value))
            
            # Handle simple conditionals and loops (basic implementation)
            rendered = self._process_conditionals(rendered, variables)
            rendered = self._process_loops(rendered, variables)
            
            # Apply custom filters: {{variable|filter}}
            rendered = self._apply_filters(rendered, variables)
            
            return rendered
            
        except Exception as e:
            self.logger.error(f"Error rendering content: {e}")
            return content
    
    def _process_conditionals(self, content: str, variables: Dict[str, Any]) -> str:
        """Process simple conditional blocks."""
        # {{#if variable}}...{{/if}}
        if_pattern = r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}'
        
        def replace_if(match):
            var_name = match.group(1)
            inner_content = match.group(2)
            
            var_value = variables.get(var_name)
            if var_value and var_value != "false" and var_value != 0:
                return inner_content
            else:
                return ""
        
        return re.sub(if_pattern, replace_if, content, flags=re.DOTALL)
    
    def _process_loops(self, content: str, variables: Dict[str, Any]) -> str:
        """Process simple loop blocks."""
        # {{#each array}}...{{/each}}
        each_pattern = r'\{\{#each\s+(\w+)\}\}(.*?)\{\{/each\}\}'
        
        def replace_each(match):
            var_name = match.group(1)
            inner_content = match.group(2)
            
            array_value = variables.get(var_name, [])
            if not isinstance(array_value, list):
                return ""
            
            result_parts = []
            for item in array_value:
                item_content = inner_content
                
                # Replace item properties
                if isinstance(item, dict):
                    for key, value in item.items():
                        item_content = item_content.replace(f"{{{{{key}}}}}", str(value))
                else:
                    item_content = item_content.replace("{{.}}", str(item))
                
                result_parts.append(item_content)
            
            return "".join(result_parts)
        
        return re.sub(each_pattern, replace_each, content, flags=re.DOTALL)
    
    def _apply_filters(self, content: str, variables: Dict[str, Any]) -> str:
        """Apply custom filters to variables."""
        # {{variable|filter}} or {{variable|filter:arg}}
        filter_pattern = r'\{\{(\w+)\|(\w+)(?::([^}]+))?\}\}'
        
        def apply_filter(match):
            var_name = match.group(1)
            filter_name = match.group(2)
            filter_arg = match.group(3)
            
            var_value = variables.get(var_name, "")
            
            if filter_name in self.custom_filters:
                try:
                    if filter_arg:
                        return self.custom_filters[filter_name](var_value, filter_arg)
                    else:
                        return self.custom_filters[filter_name](var_value)
                except Exception as e:
                    self.logger.error(f"Error applying filter {filter_name}: {e}")
                    return str(var_value)
            
            return str(var_value)
        
        return re.sub(filter_pattern, apply_filter, content)
    
    def render_response(self, user_request: str, context_vars: Optional[Dict[str, Any]] = None) -> Optional[RenderedTemplate]:
        """High-level method to render a response for a user request."""
        try:
            # Create context
            context = TemplateContext(
                user_request=user_request,
                request_type=self._infer_request_type(user_request),
                variables=context_vars or {},
                environment={
                    'format': 'markdown',  # Default format
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Select template
            template = self.select_template(context)
            if not template:
                return None
            
            # Render template
            return self.render_template(template, context)
            
        except Exception as e:
            self.logger.error(f"Error rendering response: {e}")
            return None
    
    def _infer_request_type(self, user_request: str) -> str:
        """Infer request type from user request."""
        request_lower = user_request.lower()
        
        if any(word in request_lower for word in ['help', 'how', 'what', 'guide']):
            return 'help'
        elif any(word in request_lower for word in ['status', 'health', 'state']):
            return 'status'
        elif any(word in request_lower for word in ['plan', 'planning', 'feature']):
            return 'plan_feature'
        elif any(word in request_lower for word in ['error', 'issue', 'problem']):
            return 'error'
        else:
            return 'general'
    
    def get_template_stats(self) -> Dict[str, Any]:
        """Get statistics about template usage and performance."""
        total_templates = len(self.templates)
        used_templates = sum(1 for t in self.templates.values() if t.usage_count > 0)
        
        most_used = max(self.templates.values(), key=lambda t: t.usage_count, default=None)
        
        avg_render_time = 0
        if self.performance_stats:
            avg_render_time = sum(stats['avg_time_ms'] for stats in self.performance_stats.values()) / len(self.performance_stats)
        
        return {
            'total_templates': total_templates,
            'used_templates': used_templates,
            'usage_rate': (used_templates / total_templates * 100) if total_templates > 0 else 0,
            'most_used_template': {
                'id': most_used.template_id,
                'name': most_used.name,
                'usage_count': most_used.usage_count
            } if most_used else None,
            'average_render_time_ms': round(avg_render_time, 2),
            'performance_stats': self.performance_stats
        }