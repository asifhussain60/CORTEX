# CORTEX Backlog Review Prompt

**Version:** 5.0.0 | **Author:** Asif Hussain  
**Purpose:** YAML-first backlog processing with archival workflow

---

## 🎯 Primary Directive

Process backlog items from `.asif/backlog/` with **mandatory YAML conversion** before any analysis. Every MD file must be converted to YAML format and archived before being deleted.

---

## 📁 Directory Structure

```
.asif/backlog/
├── *.md                          # Active backlog items (to be processed)
├── yamls/                      # Converted YAML items
│   ├── index.yaml               # Master index of all archived items
│   └── {date}-{name}.yaml       # Individual archived items
```

---

## 🔄 Processing Workflow

### Phase 1: YAML Conversion (MANDATORY FIRST STEP)

**Before ANY analysis**, convert all `.md` files to YAML format:

```yaml
# Schema: backlog-item-v1.yaml
version: "1.0"
schema: backlog-item

metadata:
  id: ""                    # Generated: BL-{priority}-{yymmdd}-{sequence}
  original_file: ""         # Source MD filename
  converted_date: ""        # ISO 8601 timestamp
  priority: 0               # Extracted from filename prefix (10-99)
  status: "archived"        # archived | in-progress | completed | deferred
  
objective:
  title: ""                 # Clear, actionable title
  description: ""           # Full description from MD
  category: ""              # feature | fix | refactor | docs | infrastructure
  scope: []                 # Affected components/modules
  
execution:
  complexity:
    score: 0                # 1-10 based on analysis
    factors: []             # What contributes to complexity
  dependencies: []          # Other items or external deps
  estimated_effort: ""      # hours | days | sprints
  approach:
    strategy: ""            # How to implement
    key_decisions: []       # Architectural choices needed
    risks: []               # Potential blockers
    
success_criteria:
  acceptance: []            # User-visible outcomes
  technical: []             # Implementation requirements
  quality: []               # Testing/review requirements

tdd_assessment:
  applicable: false         # Is TDD appropriate?
  test_strategy: ""         # Unit/integration/e2e approach
  test_first_items: []      # What to test before implementing

hand_off:
  ready: false              # Can this be handed off?
  orchestrator: ""          # Which orchestrator handles it
  prerequisites: []         # What must exist first
  
notes:
  original_content: |       # Preserved verbatim from MD
    ...
  analysis_notes: []        # Agent observations
  related_items: []         # Links to other backlog items
```

### Phase 2: YAML Storage

Save converted YAML to `.asif/backlog/yamls/`:

**Filename Format:** `{YYYYMMDD}-{sanitized-name}.yaml`
- Date: Conversion date
- Name: Lowercase, hyphens, no special chars

**Example:**
- Source: `10-verify-planning-governance.md`
- Output: `20250615-verify-planning-governance.yaml`

### Phase 3: Delete Original MD

**After successful YAML archival:**
1. Verify YAML file exists and is valid
2. Delete the original `.md` file
3. Update `yamls/index.yaml`

### Phase 4: Index Maintenance

Maintain `yamls/index.yaml`:

```yaml
# YAML Backlog Index
version: "1.0"
last_updated: ""
total_items: 0

items:
  - id: "BL-10-250615-001"
    file: "20250615-verify-planning-governance.yaml"
    title: "Verify Planning Governance"
    priority: 10
    status: "archived"
    converted: "2025-06-15T10:30:00Z"
    
  # ... additional items
```

### Phase 5: Analysis & Scoring

**After all conversions complete**, analyze each archived item:

#### Complexity Scoring (1-10)

| Score | Label | Characteristics |
|-------|-------|-----------------|
| 1-2 | Trivial | Single file, < 1 hour, no deps |
| 3-4 | Simple | Few files, < 4 hours, minimal deps |
| 5-6 | Moderate | Multiple components, 1-2 days, some deps |
| 7-8 | Complex | Cross-cutting, 3-5 days, many deps |
| 9-10 | Major | Architectural, 1+ week, significant risk |

#### Factors to Assess

- **Code Scope:** Files/modules affected
- **Dependencies:** External/internal requirements
- **Risk:** Breaking changes, data migration
- **Testing:** Coverage requirements
- **Documentation:** Update needs

---

## 📋 Execution Protocol

### Step 1: Discovery
```bash
# List all backlog items
ls -la .asif/backlog/*.md 2>/dev/null || echo "No MD files found"
```

### Step 2: Create YAML Directory
```bash
mkdir -p .asif/backlog/yamls
```

### Step 3: Process Each Item

For each `.md` file:

1. **Read** the complete content
2. **Parse** into YAML schema sections
3. **Generate** unique ID: `BL-{priority}-{yymmdd}-{seq}`
4. **Analyze** complexity and dependencies
5. **Write** YAML to `yamls/`
6. **Delete** original MD
7. **Update** index.yaml

### Step 4: Generate Report

Output summary after all conversions:

```yaml
conversion_report:
  timestamp: ""
  items_processed: 0
  items_archived: 0
  items_failed: 0
  
  summary:
    - id: ""
      title: ""
      priority: 0
      complexity: 0
      status: ""
      
  next_actions:
    - ""
```

---

## 🎯 Response Format

### Initial Response (Discovery)

```markdown
## 🧠 CORTEX Backlog Processor

**Author:** Asif Hussain | **Version:** 5.0.0

### 📂 Discovery Results

Found **{n}** backlog items in `.asif/backlog/`:

| Priority | Filename | Status |
|----------|----------|--------|
| 10 | verify-planning-governance.md | Pending |
| 25 | orchestrator-composable-templates.md | Pending |
| ... | ... | ... |

### 🔄 Starting YAML Conversion...

**Phase 1:** Converting MD → YAML
```

### Processing Response (Per Item)

```markdown
### ✅ Converted: {filename}

**ID:** BL-{priority}-{yymmdd}-{seq}  
**Yamls:** `yamls/{date}-{name}.yaml`

<details>
<summary>YAML Preview</summary>

```yaml
# First 30 lines of converted YAML
```

</details>

**Status:** Archived → MD Deleted
```

### Completion Response

```markdown
## 🎉 BACKLOG CONVERSION COMPLETE

### 📊 Summary

| Metric | Value |
|--------|-------|
| Items Processed | {n} |
| Successfully Archived | {n} |
| Failed | {n} |

### 📈 Priority Distribution

| Priority Range | Count | Complexity Avg |
|----------------|-------|----------------|
| 10-29 (Critical) | {n} | {x.x} |
| 30-49 (High) | {n} | {x.x} |
| 50-69 (Medium) | {n} | {x.x} |
| 70-99 (Low) | {n} | {x.x} |

### 📁 YAML Storage Location

All items archived to: `.asif/backlog/yamls/`

Index updated: `yamls/index.yaml`

### 🎯 Next Actions

1. Review archived items for implementation priority
2. Select item for hand-off to appropriate orchestrator
3. Run `backlog status` to see current state
```

---

## 🔧 Commands

| Command | Action |
|---------|--------|
| `backlog` | Full conversion + archive workflow |
| `backlog status` | Show YAML index summary |
| `backlog review {id}` | Detailed analysis of specific item |
| `backlog prioritize` | Re-rank items by complexity/value |
| `backlog hand-off {id}` | Prepare item for orchestrator |

---

## ⛔ Constraints

1. **YAML First:** Never analyze MD directly - always convert first
2. **Complete Capture:** Every MD field must map to YAML schema
3. **Delete After Conversion:** MD files are removed after successful YAML conversion
4. **Index Always Updated:** Every conversion updates index.yaml
5. **Preserve Original:** Full MD content stored in `notes.original_content`

---

## 🔗 Integration Points

- **Planning Orchestrator:** Hand-off ready items with `hand_off.ready: true`
- **TDD Orchestrator:** Items with `tdd_assessment.applicable: true`
- **Maintenance Orchestrator:** Infrastructure/refactor category items

---

## 📝 Example Conversion

### Input: `10-verify-planning-governance.md`

```markdown
# Verify Planning Governance

Ensure the planning system enforces all governance rules...

## Objectives
- Validate SKULL rules are applied
- Check planning isolation
- Verify folder structure compliance

## Acceptance Criteria
- All plans follow 4-folder structure
- No implementation during planning phase
- Brain protection rules respected
```

### Output: `yamls/20250615-verify-planning-governance.yaml`

```yaml
version: "1.0"
schema: backlog-item

metadata:
  id: "BL-10-250615-001"
  original_file: "10-verify-planning-governance.md"
  converted_date: "2025-06-15T10:30:00Z"
  priority: 10
  status: "archived"

objective:
  title: "Verify Planning Governance"
  description: "Ensure the planning system enforces all governance rules"
  category: "infrastructure"
  scope:
    - "planning-system"
    - "brain-protection"
    - "SKULL-rules"

execution:
  complexity:
    score: 5
    factors:
      - "Cross-cutting governance concern"
      - "Multiple validation points"
      - "Integration with existing rules"
  dependencies:
    - "brain-protection-rules.yaml"
    - "planning-system-4.0-manifest.yaml"
  estimated_effort: "4-6 hours"
  approach:
    strategy: "Audit existing plans against governance rules"
    key_decisions:
      - "Define validation checkpoints"
      - "Determine enforcement mechanism"
    risks:
      - "May require manifest updates"

success_criteria:
  acceptance:
    - "All plans follow 4-folder structure"
    - "No implementation during planning phase"
    - "Brain protection rules respected"
  technical:
    - "Automated validation in planning orchestrator"
    - "Clear error messages on violations"
  quality:
    - "Test coverage for all governance rules"
    - "Documentation updated"

tdd_assessment:
  applicable: true
  test_strategy: "Unit tests for each governance rule validator"
  test_first_items:
    - "Test 4-folder structure enforcement"
    - "Test planning isolation detection"
    - "Test SKULL rule validation"

hand_off:
  ready: true
  orchestrator: "planning-system"
  prerequisites:
    - "Current governance rules documented"
    - "Existing plan samples for testing"

notes:
  original_content: |
    # Verify Planning Governance
    
    Ensure the planning system enforces all governance rules...
    
    ## Objectives
    - Validate SKULL rules are applied
    - Check planning isolation
    - Verify folder structure compliance
    
    ## Acceptance Criteria
    - All plans follow 4-folder structure
    - No implementation during planning phase
    - Brain protection rules respected
  analysis_notes:
    - "Critical governance item - high priority"
    - "Aligns with SKULL brain protection principles"
  related_items: []
```

---

**End of Prompt**
