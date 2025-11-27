# ADO Work Item Orchestrator Guide

**Version:** 1.0  
**Status:** Production  
**Module:** src/orchestrators/ado_work_item_orchestrator.py

---

## Overview

The ADO Work Item Orchestrator creates and manages Azure DevOps work items (Stories, Features, Bugs) with structured templates, DoR/DoD validation, and ADO-formatted markdown summaries for direct copy-paste to ADO.

## Key Features

- **Structured Templates** - Form templates for different work item types
- **DoR/DoD Validation** - Zero-ambiguity requirement validation
- **ADO Formatting** - Copy-paste ready markdown output
- **Work Tracking** - Automatic summary generation on completion
- **Integration** - Shares planning core with PlanningOrchestrator

## Commands

```
plan ado
create work item
ado work item
create story
create feature
create bug
ado planning
```

## Work Item Types

- **User Story** (default)
- **Feature**
- **Bug**
- **Task**
- **Epic**

## Form Template Includes

- Title and description
- Priority (1=High, 2=Medium, 3=Low, 4=Very Low)
- Assigned to (optional)
- Iteration and area path
- Tags
- Acceptance criteria (checklist)
- Related work items

## Output Formats

- ADO-formatted markdown (copy-paste ready)
- Planning file (.md) in cortex-brain/documents/planning/ado/
- DoR/DoD validation report
- OWASP security review (if applicable)

## File Organization

```
cortex-brain/documents/planning/ado/
├── active/
├── completed/
└── blocked/
```

## Workflow

1. **Choose Work Item Type** - Story, Feature, Bug, Task, or Epic
2. **Fill Form Template** - Structured template provided
3. **Generate Plan** - DoR validation + ADO formatting
4. **Output Files** - Planning .md + ADO copy-paste summary

## Integration

- Uses ADOClient for API communication
- Shares planning core (80% code reuse)
- DoR/DoD validation engine
- OWASP security review integration
- File-based workflow for git tracking

## Work Item Metadata

**Tracked Fields:**
- work_item_type
- title, description
- assigned_to, iteration, area_path
- priority, tags
- acceptance_criteria
- related_work_items
- created_date, work_item_id

## Work Summary Generation

**Automatically Tracks:**
- Files created/modified
- Tests created
- Documentation created
- Code changes count
- Test coverage
- Duration hours
- Implementation notes
- Technical decisions
- Dependencies
- Known issues

## Performance

- Form generation: <1 second
- Validation: 2-5 seconds
- File output: <1 second
- Total: <10 seconds

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
