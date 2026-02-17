# .temp/ Folder - Ephemeral Workflow Instances

**Authority:** Phase 102 - Workflow Runtime Foundation  
**Purpose:** Temporary storage for hydrated workflow instances  
**Lifecycle:** Auto-deleted after 7 days

---

## Structure

```
.temp/
├── .gitignore          # Ignores all instance files
├── cleanup.sh          # Auto-delete script (run daily)
├── README.md           # This file
└── instances/          # Hydrated workflow instance YAML files
    └── (auto-deleted after 7 days)
```

---

## Workflow Instance Naming

**Format:** `{phase_id}-{timestamp}-{request_id}.yaml`

**Example:** `phase-104-2026-02-17-001.yaml`

---

## Cleanup Strategy

**Auto-delete:** Files older than 7 days removed by `cleanup.sh`

**Archive:** Failed or complex executions copied to:
- `cortex-registry/archive/executions/`

**Manual Cleanup:** Run `./cleanup.sh` anytime

---

## Git Tracking

**Status:** NOT tracked in git (ignored via `.gitignore`)

**Rationale:** Prevents bloat; instances are ephemeral execution artifacts

---

## Usage

This folder is managed automatically by `WorkflowRuntime` (Phase 102).

**Do not manually create files here.** Instances are generated during phase execution.
