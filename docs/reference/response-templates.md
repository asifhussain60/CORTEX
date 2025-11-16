---
title: Response Templates Reference
description: Complete reference for CORTEX response templates
author: 
generated: true
version: ""
last_updated: 
---

# Response Templates Reference

**Purpose:** Complete reference for CORTEX response templates system  
**Audience:** Developers, contributors, template authors  
**Version:**   
**Last Updated:** 

---

## Overview

CORTEX uses pre-formatted response templates for instant, consistent answers without Python execution. Templates are loaded directly by GitHub Copilot from `cortex-brain/response-templates.yaml`.

**Benefits:**
- Instant responses (no API calls)
- Consistent formatting
- Token optimization
- Natural language triggers

---

## Template Structure

```yaml
templates:
  template_name:
    triggers:
      - "natural language phrase"
      - "alternate phrase"
    response_type: table | list | detailed | narrative
    context_needed: false | true
    verbosity: concise | detailed | expert
    metadata:
      category: system | agent | operation | error | plugin
    content: |
      🧠 **CORTEX Response**
      
      {{user_request}}
      
      Your response content here...
```

---

## Template Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `triggers` | array | Yes | Natural language patterns that activate template |
| `response_type` | string | Yes | Format: `table`, `list`, `detailed`, `narrative` |
| `context_needed` | boolean | Yes | Whether template needs dynamic data |
| `verbosity` | string | No | Response detail level |
| `metadata.category` | string | Yes | Template category for organization |
| `content` | string | Yes | Markdown response content with placeholders |

---

## Response Types

### Table Format

Best for: Command references, status information, comparisons

```yaml
response_type: table
content: |
  | Command | Description | Status |
  |---------|-------------|--------|
  | setup   | Configure   | ✅     |
```

### List Format

Best for: Command lists, feature summaries

```yaml
response_type: list
content: |
  **CORTEX Commands:**
  • setup - Configure environment
  • cleanup - Clean workspace
```

### Detailed Format

Best for: Technical explanations, multi-section responses

```yaml
response_type: detailed
content: |
  ## Section 1
  Detailed explanation...
  
  ## Section 2
  More details...
```

### Narrative Format

Best for: Conversational responses, explanations

```yaml
response_type: narrative
content: |
  CORTEX is a cognitive framework...
```

---

## Placeholders

### User Context

- `{{user_request}}` - Original user request
- `{{timestamp}}` - Current timestamp
- `{{version}}` - CORTEX version

### Dynamic Data

- `{{operation_name}}` - Current operation
- `{{status}}` - Operation status
- `{{duration}}` - Operation duration

### Conditional Blocks

```yaml
{{#if condition}}
  Content when true
{{else}}
  Content when false
{{/if}}
```

### Loops

```yaml
{{#operations}}
  • {{operation_name}}: {{status}}
{{/operations}}
```

---

## Template Categories

### System Templates

Status checks, version info, help commands

**Examples:**
- `help_table` - Command reference table
- `status_check` - System status
- `version_info` - Version information

### Agent Templates

Agent-specific responses (20 templates, 2 per agent)

**Examples:**
- `executor_success` - Code execution success
- `planner_success` - Plan creation success
- `protector_challenge` - Brain protection challenge

### Operation Templates

Operation lifecycle responses (30 templates)

**Examples:**
- `operation_started` - Operation begins
- `operation_progress` - Progress updates
- `operation_complete` - Operation finishes

### Error Templates

Error handling and troubleshooting (15 templates)

**Examples:**
- `missing_dependency` - Package not found
- `validation_failed` - Validation errors
- `permission_denied` - Access errors

---

## Creating Templates

### 1. Choose Category

Determine template category: system, agent, operation, error, plugin

### 2. Define Triggers

List natural language phrases:

```yaml
triggers:
  - "how do I plan"
  - "plan a feature"
  - "help me plan"
```

### 3. Design Content

Write Markdown response with placeholders:

```yaml
content: |
  🎯 **Feature Planning**
  
  You asked: {{user_request}}
  
  Here's how to plan a feature...
```

### 4. Test Template

```yaml
# Add to response-templates.yaml
# Test with natural language trigger
```

---

## Best Practices

### Trigger Design

✅ **Good Triggers:**
- "how do I setup"
- "setup environment"
- "configure cortex"

❌ **Bad Triggers:**
- "setup" (too short, conflicts)
- "how do I do anything" (too broad)

### Content Guidelines

- Use clear, concise language
- Include code examples where appropriate
- Add visual indicators (✅, ❌, ⚠️)
- Structure with headings
- Keep consistent formatting

### Performance

- Static templates (context_needed: false) = instant
- Dynamic templates (context_needed: true) = slight delay
- Keep templates focused (single purpose)

---

## Template Testing

Validate templates:

```bash
python scripts/validate_templates.py
```

Test specific template:

```bash
python scripts/test_template.py "help_table"
```

---

## Related Documentation

- **Response Templates:** See `cortex-brain/response-templates.yaml` (90+ templates)
- **Template User Guide:** [User Guide](../../docs/response-template-user-guide.md)

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file  
**Version:**   
**Generated:** 