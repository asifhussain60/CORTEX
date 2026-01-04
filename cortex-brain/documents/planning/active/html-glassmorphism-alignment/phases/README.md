# Optional Phase Breakdown

This folder is for **optional** detailed phase documentation. The master plan (`00-master-plan.md`) contains all necessary phase information.

## Purpose

Create individual phase files here if:
- A phase is extremely complex (>10 tasks)
- Detailed sub-task breakdown needed
- Multiple team members working on same phase
- Phase requires extensive documentation

## Format

Each phase file should follow this structure:

```markdown
# Phase {N}: {Phase Name}

**Duration:** {X} hours  
**Status:** {COMPLETE | IN PROGRESS | PENDING}  
**Dependencies:** {Previous phases}

## Objective

{Clear objective statement}

## Tasks

1. {Task 1}
2. {Task 2}
...

## Deliverables

- {Deliverable 1}
- {Deliverable 2}

## Exit Criteria

- [ ] {Criterion 1}
- [ ] {Criterion 2}

## Git Checkpoint

\`\`\`bash
git add -A
git commit -m "cortex-phase-{N}: {description}"
# DO NOT PUSH - User controls when to push
\`\`\`
```

## Current Plan

**Phases 0-6:** Complete (no separate files needed)  
**Phases 7-12:** Pending (create files if needed during execution)

---

**Note:** This is an **optional** organizational tool. The master plan is the single source of truth.
