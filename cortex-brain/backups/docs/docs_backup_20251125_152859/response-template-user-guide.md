---
title: Response Template User Guide
date: 2025-11-25
author: CORTEX Documentation Generator
---

# Response Template User Guide

## Response Template System

CORTEX uses a template-based response system for consistent, high-quality responses.

### Template Structure

All templates follow the mandatory 5-part structure:

```markdown
🧠 **CORTEX [Operation Type]**
Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX

🎯 **My Understanding Of Your Request:** [State understanding]

⚠️ **Challenge:** [✓ Accept OR ⚡ Challenge with alternatives]

💬 **Response:** [Natural language explanation]

📝 **Your Request:** [Echo user's request]

🔍 **Next Steps:** [Context-appropriate format]
```

### Template Categories

**Help & Status**
- help_table
- help_detailed
- quick_start
- status_check

**Planning**
- work_planner_success
- planning_dor_complete
- planning_dor_incomplete
- planning_security_review

**TDD & Testing**
- tdd_workflow_start
- test_generation_triggers
- refactor_triggers

**Administration**
- system_alignment_report
- cleanup_operation
- design_sync_operation

**General**
- fallback (default template)

### Template Configuration

Templates are defined in `cortex-brain/response-templates.yaml`:

```yaml
templates:
  help_table:
    triggers:
    - help
    - /help
    - what can cortex do
    response_type: table
    content: |
      [Template content]
```

### Using Templates

Templates are auto-selected based on:
1. Exact trigger match (highest priority)
2. TDD workflow detection
3. Planning workflow detection
4. Fuzzy match (70%+ similarity)
5. Fallback (default)

## Related Documentation

- [Reference: Response Templates](reference/response-templates.md)
- [Template Guide](https://github.com/asifhussain60/CORTEX/blob/CORTEX-3.0/.github/prompts/modules/template-guide.md)
