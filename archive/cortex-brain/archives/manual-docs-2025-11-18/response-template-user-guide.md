# Response Template System - User Guide

**Version:** 2.0  
**Author:** Asif Hussain  
**Date:** 2025-11-10

---

## 🎯 Overview

The Response Template System provides a unified, zero-execution approach to formatting CORTEX responses. Instead of writing custom formatting code, you define templates in YAML that are instantly rendered with context.

### Key Benefits

✅ **Zero execution overhead** - Pre-formatted responses load instantly  
✅ **Consistent formatting** - All components use same templates  
✅ **Easy maintenance** - Edit YAML, not code  
✅ **Verbosity control** - Concise/detailed/expert modes built-in  
✅ **Extensible** - Plugins can register custom templates

---

## 📚 Quick Start

### Using Templates in Code

```python
from src.entry_point.response_formatter import ResponseFormatter

# Initialize formatter with template system
formatter = ResponseFormatter(default_verbosity='concise')

# Use a template with context
result = formatter.format_from_template(
    'executor_success',
    context={
        'files_count': 3,
        'files': [
            {'path': 'src/auth.py'},
            {'path': 'src/models.py'},
            {'path': 'tests/test_auth.py'}
        ],
        'next_action': 'Run tests'
    }
)

# Find template by trigger phrase
result = formatter.format_from_trigger('help')
```

###Using Templates from Copilot Chat

Templates work automatically! Just use natural language:

```
help                    → Returns help_table template
status                  → Returns status_check template  
getting started         → Returns quick_start template
```

---

## 🎨 Template Anatomy

### Basic Template Structure

```yaml
templates:
  template_id:
    triggers: [list of phrases that trigger this template]
    response_type: table | list | detailed | narrative | json
    context_needed: false | true
    verbosity: concise | detailed | expert
    metadata:
      category: system | agent | operation | error | plugin
    content: |
      Your template content here
      Use {{placeholders}} for dynamic values
```

### Example Template

```yaml
templates:
  executor_success:
    triggers: []
    response_type: detailed
    context_needed: true
    verbosity: concise
    metadata:
      category: agent
      agent: executor
    content: |
      ✅ **Feature Implemented**
      
      Files Modified: {{files_count}}
      {{#files}}
      • {{path}}
      {{/files}}
      
      Next: {{next_action}}
```

---

## 🔧 Placeholder Syntax

### Simple Placeholders

```yaml
content: |
  Hello {{name}}, you have {{count}} messages.
```

**Context:**
```python
{'name': 'Alice', 'count': 5}
```

**Output:**
```
Hello Alice, you have 5 messages.
```

### Conditionals

Show content only if condition is true:

```yaml
content: |
  Result: Success
  {{#if warnings}}
  ⚠️ Warnings: {{warnings}}
  {{/if}}
```

**Context (with warnings):**
```python
{'warnings': 'Some issues detected'}
```

**Output:**
```
Result: Success
⚠️ Warnings: Some issues detected
```

**Context (no warnings):**
```python
{}
```

**Output:**
```
Result: Success
```

### Loops

Iterate over lists:

```yaml
content: |
  Files Modified:
  {{#files}}
  • {{path}} ({{changes}} changes)
  {{/files}}
```

**Context:**
```python
{
    'files': [
        {'path': 'src/auth.py', 'changes': 3},
        {'path': 'src/models.py', 'changes': 5}
    ]
}
```

**Output:**
```
Files Modified:
• src/auth.py (3 changes)
• src/models.py (5 changes)
```

### Verbosity Sections

Control output by verbosity level:

```yaml
content: |
  ✅ Success
  
  [concise]
  Quick summary
  [/concise]
  
  [detailed]
  Detailed breakdown with metrics
  [/detailed]
  
  [expert]
  Full technical details and logs
  [/expert]
```

**When verbosity='concise':**
```
✅ Success
Quick summary
```

**When verbosity='detailed':**
```
✅ Success
Detailed breakdown with metrics
```

---

## 📂 Template Categories

### System Templates (15 templates)

Always available, zero-execution responses:

- `help_table` - Quick command reference
- `help_detailed` - Categorized commands
- `help_list` - Simple list format
- `status_check` - Implementation status
- `quick_start` - First-time user guide
- `version_info` - Version information
- `about` - About CORTEX
- `commands_by_category` - Organized commands
- `error_general` - Generic error
- `success_general` - Generic success
- `not_implemented` - Feature pending

### Agent Templates (20 templates)

2 per agent (success/error):

- `executor_success` / `executor_error`
- `tester_success` / `tester_error`
- `validator_success` / `validator_error`
- `work_planner_success` / `work_planner_error`
- `documenter_success` / `documenter_error`
- `intent_detector_success` / `intent_detector_error`
- `architect_success` / `architect_error`
- `health_validator_success` / `health_validator_error`
- `pattern_matcher_success` / `pattern_matcher_error`
- `learner_success` / `learner_error`

### Operation Templates (30 templates)

Lifecycle templates for operations:

- `operation_started` / `operation_progress` / `operation_complete` / `operation_failed`
- `setup_started` / `setup_complete`
- `cleanup_started` / `cleanup_complete`
- `story_refresh_started` / `story_refresh_complete`
- `docs_build_started` / `docs_build_complete`
- `brain_check_started` / `brain_check_complete`
- `tests_started` / `tests_complete`

### Error Templates (15 templates)

Standardized error reporting:

- `missing_dependency` - Missing package
- `permission_denied` - Permission issues
- `validation_failed` - Validation errors
- `file_not_found` - File missing
- `network_error` - Network issues
- `timeout_error` - Operation timeout
- `configuration_error` - Config problems
- `syntax_error` - Code syntax issues
- `import_error` - Import failures
- `runtime_error` - Runtime exceptions
- `database_error` - Database issues
- `path_error` - Invalid paths
- `type_error` - Type mismatches
- `value_error` - Invalid values
- `unknown_error` - Unexpected errors

### Plugin Templates (10 templates)

Plugin lifecycle templates:

- `plugin_registered` - Plugin registration
- `plugin_execution_started` - Plugin starting
- `plugin_execution_complete` - Plugin complete
- `plugin_execution_failed` - Plugin failed
- `platform_switch_detected` - Platform change
- `platform_switch_complete` - Platform configured
- `cleanup_scan_complete` - Cleanup scan done
- `doc_refresh_analyzing` - Doc analysis
- `doc_refresh_complete` - Docs refreshed
- `extension_scaffold_complete` - Extension created

---

## 🔌 Plugin Template Registration

Plugins can register custom templates:

```python
from src.plugins.base_plugin import BasePlugin
from src.response_templates.template_loader import Template

class MyPlugin(BasePlugin):
    def register_templates(self):
        """Register plugin-specific templates."""
        return [
            Template(
                template_id='my_plugin_success',
                triggers=[],
                response_type='narrative',
                context_needed=True,
                content='✅ {{plugin_name}} executed successfully\nResult: {{result}}',
                verbosity='concise',
                metadata={
                    'category': 'plugin',
                    'plugin_id': self.metadata.plugin_id
                }
            )
        ]
    
    def execute(self, request, context):
        # Do work...
        result = do_something()
        
        # Use template for response
        return self.format_from_template(
            'my_plugin_success',
            context={
                'plugin_name': self.metadata.name,
                'result': result
            }
        )
```

---

## 📊 Best Practices

### 1. Use Appropriate Verbosity

- **concise** (50-150 words) - Default, quick summaries
- **detailed** (200-400 words) - Structured breakdowns
- **expert** (no limit) - Full technical details

### 2. Provide Meaningful Context

Always include all required placeholders:

```python
# ✅ Good - All placeholders provided
formatter.format_from_template(
    'executor_success',
    context={
        'files_count': 3,
        'files': [...],
        'next_action': 'Run tests'
    }
)

# ❌ Bad - Missing required placeholders
formatter.format_from_template(
    'executor_success',
    context={'files_count': 3}  # Missing files and next_action
)
```

### 3. Use Conditionals for Optional Content

```yaml
content: |
  ✅ Success
  
  {{#if warnings}}
  ⚠️ Warnings: {{warnings}}
  {{/if}}
  
  {{#if recommendations}}
  💡 Recommendations:
  {{#recommendations}}
  • {{text}}
  {{/recommendations}}
  {{/if}}
```

### 4. Keep Templates Focused

One template = one purpose. Don't create mega-templates that try to handle everything.

### 5. Use Metadata for Organization

```yaml
metadata:
  category: agent
  agent: executor
  priority: high
  version: 2.0
```

---

## 🚀 Migration Guide

### Migrating from Code-Based Formatting

**Before (code-based):**
```python
def format_success(result):
    lines = []
    lines.append(f"✅ Success!")
    lines.append(f"\nFiles: {len(result.files)}")
    for file in result.files:
        lines.append(f"  • {file}")
    lines.append(f"\nNext: {result.next_action}")
    return "\n".join(lines)
```

**After (template-based):**
```python
def format_success(result):
    return formatter.format_from_template(
        'executor_success',
        context={
            'files_count': len(result.files),
            'files': [{'path': f} for f in result.files],
            'next_action': result.next_action
        }
    )
```

### Benefits of Migration

✅ 90% less code  
✅ Consistent formatting  
✅ Easy to update (change YAML, not code)  
✅ Automatic verbosity control  
✅ Better testing (test template, not formatting logic)

---

## 🎯 Examples

### Example 1: Simple Help Command

**Code:**
```python
result = formatter.format_from_trigger('help')
```

**Output:**
```
================================================================================
CORTEX COMMANDS
================================================================================

Status  Command        What It Does
--------------------------------------------------------------------------------
✅      update story   Refresh CORTEX story documentation
🔄      setup          Setup/configure environment
🔄      cleanup        Clean temporary files
...
================================================================================
```

### Example 2: Agent Success

**Code:**
```python
result = formatter.format_from_template(
    'executor_success',
    context={
        'files_count': 2,
        'files': [
            {'path': 'src/auth.py'},
            {'path': 'tests/test_auth.py'}
        ],
        'next_action': 'Run pytest'
    }
)
```

**Output:**
```
✅ **Feature Implemented**

Files Modified: 2
• src/auth.py
• tests/test_auth.py

Next: Run pytest
```

### Example 3: Error Reporting

**Code:**
```python
result = formatter.format_from_template(
    'missing_dependency',
    context={
        'package_name': 'requests',
        'required_by': 'api_client.py'
    }
)
```

**Output:**
```
❌ **Missing Dependency**

Package: requests
Required by: api_client.py

Fix: pip install requests
```

---

## 📖 Reference

### Template File Location

```
cortex-brain/response-templates.yaml
```

### API Reference

**ResponseFormatter:**
- `format_from_template(template_id, context, verbosity)` - Format using template ID
- `format_from_trigger(trigger, context, verbosity)` - Format using trigger phrase
- `register_plugin_templates(plugin_id, templates)` - Register plugin templates
- `list_available_templates(category)` - List all templates

**TemplateLoader:**
- `load_template(template_id)` - Load specific template
- `find_by_trigger(trigger)` - Find template by trigger
- `list_templates(category)` - List all templates
- `get_template_ids()` - Get all template IDs

**TemplateRenderer:**
- `render(template, context, verbosity)` - Render template
- `render_with_placeholders(template, **kwargs)` - Render with kwargs
- `apply_verbosity(content, verbosity)` - Apply verbosity filtering
- `convert_format(content, format)` - Convert format (text/markdown/json)

---

## 🆘 Troubleshooting

### Template Not Found

**Error:** `❌ Template 'my_template' not found`

**Solution:** Check template ID exists in response-templates.yaml

### Missing Placeholder Values

**Output:** `{{MISSING: placeholder_name}}`

**Solution:** Provide all required placeholders in context dictionary

### Template System Unavailable

**Warning:** `Template system unavailable: <error>`

**Solution:** Check that cortex-brain/response-templates.yaml exists and is valid YAML

### Performance Issues

If template loading is slow:
- Check file size (should be < 1MB)
- Ensure YAML is well-formed
- Consider caching template loader instance

---

**Questions?** See `cortex-brain/cortex-2.0-design/RESPONSE-TEMPLATE-ARCHITECTURE.md` for full design details.
