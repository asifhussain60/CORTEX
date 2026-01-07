# CORTEX Toolkit - Planning Tools

Planning and Azure DevOps management tools.

## Tools

### plan (`cortex-plan`)

**Purpose:** Generate feature implementation plans with TDD integration.

**File:** `plan_generator.py`

**Usage:**
```bash
python cortex-toolkit/core/planning/plan_generator.py [feature]
```

**Execution Method:** `copilot_chat` (use via Copilot Chat interface)

**Features:**
- Auto-complexity detection (HIGH→incremental, LOW→skeleton)
- TDD auto-included
- DoR/DoD compliance
- Planning System 2.0 integration

---

### ado (`cortex-ado`)

**Purpose:** Azure DevOps work item management (stories, features, tasks).

**File:** `ado_manager.py`

**Usage:**
```bash
python cortex-toolkit/core/planning/ado_manager.py
```

**Execution Method:** `copilot_chat`

**Features:**
- Story/Feature/Task creation
- Completion summaries
- Code reviews
- Inherits Planning System 2.0 requirements

---

### planning-file-manager (`cortex-pfm`)

**Purpose:** Manage planning documentation files and organization.

**File:** `planning_file_manager.py`

**Usage:**
```bash
python cortex-toolkit/core/planning/planning_file_manager.py
```

**Execution Method:** `cli`

**Features:**
- Plan document organization
- File naming conventions
- Status tracking
- Integration with ADO Manager

---

## Integration

Planning tools integrate with:
- **Planning System 2.0:** Feature planning workflow
- **TDD Mastery:** Test-driven development cycle
- **ADO Operations:** Azure DevOps work items
- **Manifest System:** `planning-system-2.0-manifest.yaml`

## Compliance

All planning operations must follow:
- Definition of Ready (DoR)
- Definition of Done (DoD)
- TDD integration requirements
- Acceptance criteria gates
