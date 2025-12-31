---
mode: agent
description: CORTEX Backlog Review & Enhancement System - Reviews, enhances, prioritizes, and assesses complexity for planning hand-off
---

# 📋 CORTEX Backlog Review & Enhancement System

**Version:** 4.0.0 | **Author:** Asif Hussain  
**Location:** `.asif/backlog/` | **Format:** Priority-prefixed markdown files  
**Platform:** macOS/Linux (bash commands)

---

## 🎯 Purpose

**Review, enhance, prioritize, and assess complexity** of CORTEX backlog items for optimal GitHub Copilot execution. This prompt does NOT execute backlog items—it prepares them for execution and determines if planning is required.

**Core Responsibilities:**
1. **Review** all backlog files for manual instructions/enhancements needed
2. **Enhance** instructions for Copilot executability (clear, atomic, verifiable)
3. **Prioritize** by renaming files with correct priority prefixes (00-99)
4. **Validate** format consistency and completeness
5. **🧮 Assess Complexity** - Calculate complexity score (0-100) for each item
6. **🔍 Holistic Analysis** - Analyze target file for autonomy refinements before execution
7. **🎯 Optimize Delegation** - Delegate bloat detection & decomposition to `cortex-optimize.prompt.md`
8. **🧪 TDD Evaluation** - Determine if TDD approach adds high value
9. **🛡️ Hand-Off** - Route complex items (score ≥51) to Planning/ADO Orchestrators

**Integration:** Uses `cortex-optimize.prompt.md` for deep file analysis (bloat, decomposition, technical debt)

---

## 🔄 Review & Enhancement Protocol

### When This Prompt Is Invoked:

**STEP 1: Scan All Backlog Files**
```bash
ls -la .asif/backlog/*.md | sort
```

**STEP 2: Read Every File**
For each backlog item, load complete content and assess:
- [ ] Format compliance (follows standard structure)
- [ ] Instruction clarity (Copilot can execute without ambiguity)
- [ ] File references (all paths exist and are correct)
- [ ] Success criteria (measurable and verifiable)
- [ ] Toolkit integration (checks for existing scripts)
- [ ] Priority accuracy (matches impact and urgency)

**STEP 3: Enhancement Pass**
For files needing improvement:

**A. Enhance Instructions:**
- Replace vague language: "Update the file" → "Add lines 15-20 to section X"
- Add file paths: "the config" → "`cortex-brain/config/setup.yaml`"
- Specify tools: "check toolkit" → "Run: `grep -r 'keyword' cortex-toolkit/`"
- Add verification: Include exact commands to verify success

**B. Add Missing Sections:**
- Add toolkit verification steps if creating scripts
- Add rollback instructions for destructive operations
- Add progress checkpoints for multi-step processes
- Add error handling instructions

**C. Improve Success Criteria:**
- Change "File updated" → "File contains line: `setting: true`"
- Change "Tests pass" → "Command `pytest tests/` exits with code 0"
- Add quantifiable metrics where possible

**STEP 4: Priority Assessment**
Analyze each item for business value and assign priority:

| Priority | Prefix | Criteria |
|----------|--------|----------|
| 🔴 CRITICAL | 00-09 | Blocks work, broken functionality, security issues |
| 🟠 HIGH | 10-19 | Core functionality, high ROI, user-facing improvements |
| 🟡 MEDIUM-HIGH | 20-39 | Optimization, developer experience, maintainability |
| 🟡 MEDIUM | 40-59 | Consolidation, documentation, minor improvements |
| 🟢 LOW | 60-79 | New features, nice-to-have, experimental |
| 🔵 DEFER | 80-99 | Low priority, future consideration |

**STEP 5: Renumber Files**
Rename files with proper priority prefixes:
```bash
mv .asif/backlog/old-name.md .asif/backlog/{NN}-{descriptive-name}.md
```

**STEP 6: Generate Report**
Output comprehensive review report (see format below)

**STEP 7: Complexity Assessment & Planning Hand-Off**
For each backlog item, calculate complexity score to determine if a comprehensive plan is required.

---

## 🧮 Complexity Scoring System

### Calculate Complexity Score (0-100)

For each backlog item, assess these dimensions:

| Dimension | Weight | Score Range | Criteria |
|-----------|--------|-------------|----------|
| **Effort** | 25% | 0-25 | <1hr=5, 1-2hr=10, 2-4hr=15, 4-8hr=20, >8hr=25 |
| **File Scope** | 20% | 0-20 | 1 file=5, 2-3 files=10, 4-6 files=15, >6 files=20 |
| **Dependencies** | 20% | 0-20 | None=0, 1-2 deps=10, 3+ deps=15, Cross-system=20 |
| **Risk Level** | 20% | 0-20 | Low=5, Medium=10, High=15, Critical=20 |
| **Testing Required** | 15% | 0-15 | None=0, Unit=5, Integration=10, E2E=15 |

**Total Score:** Sum of all dimensions (0-100)

### Complexity Thresholds

| Score Range | Complexity | Action |
|-------------|------------|--------|
| **0-25** | 🟢 SIMPLE | Execute directly from backlog item |
| **26-50** | 🟡 MODERATE | Execute with checkpoints, no plan needed |
| **51-75** | 🟠 COMPLEX | **🛡️ HAND-OFF to Planning Orchestrator** |
| **76-100** | 🔴 HIGHLY COMPLEX | **🛡️ HAND-OFF to Planning + ADO Orchestrators** |

### 🛡️ Planning Hand-Off Protocol

**When Score ≥ 51 (COMPLEX or HIGHLY COMPLEX):**

1. **Calculate & Display Score:**
```markdown
### 🧮 Complexity Assessment: {backlog-item-name}

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Effort | {X}/25 | {reason} |
| File Scope | {X}/20 | {reason} |
| Dependencies | {X}/20 | {reason} |
| Risk Level | {X}/20 | {reason} |
| Testing Required | {X}/15 | {reason} |
| **TOTAL** | **{X}/100** | **{COMPLEXITY_LEVEL}** |
```

2. **Determine Hand-Off Target:**
   - Score 51-75 → 🛡️ **Planning Orchestrator** (`planning-system-4.0-manifest.yaml`)
   - Score 76-100 → 🛡️ **Planning + ADO Orchestrators** (create work items for tracking)

3. **Execute Hand-Off:**
```markdown
## 🛡️ HAND-OFF: Planning Required

**Backlog Item:** `{filename}`
**Complexity Score:** {score}/100 ({LEVEL})
**Reason:** {why this needs a plan}

**ROUTING TO:** Planning Orchestrator
**Command:** `/CORTEX Plan {backlog-item-objective}`

---
⛔ STOPPING HERE - Planning Orchestrator will create comprehensive execution plan.
```

4. **For Score ≥ 76 (ADO Integration):**
```markdown
## 🛡️ HAND-OFF: Planning + ADO Required

**Backlog Item:** `{filename}`
**Complexity Score:** {score}/100 (HIGHLY COMPLEX)

**STEP 1:** Planning Orchestrator creates execution plan
**STEP 2:** ADO Orchestrator creates work items for tracking

**ROUTING TO:** Planning Orchestrator THEN ADO Orchestrator
**Commands:**
1. `/CORTEX Plan {backlog-item-objective}`
2. `ado story {backlog-item-objective}` (after plan created)

---
⛔ STOPPING HERE - Orchestrators will handle planning and work item creation.
```

### Complexity Score Examples

**Example 1: Simple (Score 22)**
```
Backlog: "Update version number in package.json"
- Effort: 5 (<1hr)
- File Scope: 5 (1 file)
- Dependencies: 0 (none)
- Risk Level: 5 (low)
- Testing: 5 (verify manually)
TOTAL: 20 → 🟢 SIMPLE → Execute directly
```

**Example 2: Complex (Score 65)**
```
Backlog: "Refactor response templates into modular system"
- Effort: 20 (4-8hr)
- File Scope: 15 (4-6 files)
- Dependencies: 15 (3+ deps)
- Risk Level: 10 (medium)
- Testing: 5 (unit tests)
TOTAL: 65 → 🟠 COMPLEX → 🛡️ HAND-OFF to Planning
```

**Example 3: Highly Complex (Score 85)**
```
Backlog: "Implement interactive learning paths system"
- Effort: 25 (>8hr)
- File Scope: 20 (>6 files)
- Dependencies: 20 (cross-system)
- Risk Level: 10 (medium)
- Testing: 10 (integration)
TOTAL: 85 → 🔴 HIGHLY COMPLEX → 🛡️ HAND-OFF to Planning + ADO
```

---

## 🔍 Holistic Analysis (Pre-Execution Refinement)

**MANDATORY:** Before executing ANY backlog item, perform holistic analysis to ensure autonomous execution readiness.

### When to Perform Holistic Analysis

**Trigger:** When user invokes backlog prompt with a specific file reference (e.g., `#file:15-docgen-prompt.md`)

### Analysis Protocol

**STEP 1: Structural Analysis**
```bash
# Run toolkit analyzer (if available)
python cortex-toolkit/core/utilities/backlog_analyzer.py --file ".asif/backlog/{filename}.md" --mode holistic
```

**If toolkit not available, perform manual analysis:**

| Category | Check | Pass Criteria |
|----------|-------|---------------|
| **Format** | Header, metadata, steps, success criteria | All sections present |
| **Clarity** | No vague language, all paths explicit | Zero ambiguity |
| **Verifiability** | Every step has verification command | 100% coverage |
| **Atomicity** | Each step = single action | No multi-action steps |
| **Dependencies** | External deps documented | All deps listed |

**STEP 2: Autonomy Gap Detection**

Scan for these autonomy blockers:

| Gap Type | Pattern | Fix |
|----------|---------|-----|
| **Vague Reference** | "the file", "the config" | Add explicit path |
| **Missing Output** | Command without expected result | Add expected output |
| **Human Judgment** | "if appropriate", "as needed" | Add decision criteria |
| **Placeholder** | `{name}`, `{value}` | Replace with actual values |
| **Ambiguous Verb** | "update", "fix", "improve" | Specify exact changes |

**STEP 3: Apply Refinements**

For each gap detected, apply fix directly to backlog item:

```markdown
### Before Refinement:
Step 3: Update the config file

### After Refinement:
Step 3: Update Configuration
Edit `cortex-brain/config/setup.yaml`:
- Line 45: Change `enable_feature: false` → `enable_feature: true`
- Verify: `grep "enable_feature: true" cortex-brain/config/setup.yaml`
- Expected: `enable_feature: true`
```

**STEP 4: Add Execution Checkpoints**

For items with complexity ≥26 (MODERATE+), add checkpoints:

```markdown
## ⏸️ Execution Checkpoints

**Checkpoint 1 (After Step X):** Verify {condition}
\`\`\`bash
{verification_command} && echo "✅ CHECKPOINT 1 PASSED" || echo "❌ FAILED"
\`\`\`

**Checkpoint 2 (After Step Y):** Verify {condition}
...
```

**STEP 5: Output Analysis Report**

```markdown
### 🔍 Holistic Analysis: {filename}

| Metric | Before | After | Status |
|--------|--------|-------|--------|
| Autonomy Score | {X}% | {Y}% | ✅/⚠️ |
| Vague References | {N} | 0 | ✅ |
| Missing Outputs | {N} | 0 | ✅ |
| Checkpoints Added | 0 | {N} | ✅ |

**Refinements Applied:** {count}
**Ready for Autonomous Execution:** YES/NO
```

**STEP 6: Optimize Prompt Delegation (Target File Analysis)**

**When backlog item targets a specific file for modification**, delegate deep analysis to `cortex-optimize.prompt.md`:

```markdown
### 🎯 Optimize Delegation Check

**Target File(s):** `{file_path}` (from backlog item)

**Delegation Required IF:**
- [ ] Target file >500 lines (prompts) / >1000 lines (code) / >300 lines (config)
- [ ] Backlog item involves refactoring or restructuring
- [ ] Multiple concerns detected in target file

**Action:** Run `cortex-optimize.prompt.md` on target file FIRST
```

**If Optimize Delegation Triggered:**

1. **Invoke Optimize Engine:**
   ```
   Reference: cortex-optimize.prompt.md
   Target: {target_file_path}
   Mode: Bloat Detection + Decomposition Analysis
   ```

2. **Bloat Detection (from Optimize):**
   | Artifact Type | Threshold | Current Lines | Status |
   |---------------|-----------|---------------|--------|
   | Prompt | 500 | {N} | ✅/⚠️ BLOATED |
   | Code | 1,000 | {N} | ✅/⚠️ BLOATED |
   | Config | 300 | {N} | ✅/⚠️ BLOATED |

3. **If BLOATED → Decomposition BEFORE Backlog Execution:**
   - Optimize generates decomposition plan (Pattern 1-5)
   - Create backlog item: `00-decompose-{filename}.md` (CRITICAL priority)
   - Execute decomposition FIRST
   - Then return to original backlog item

4. **Inject Optimize Findings:**
   ```markdown
   ## 🎯 Pre-Execution Optimization Findings
   
   **Source:** `cortex-optimize.prompt.md` analysis
   **Target:** `{file_path}`
   
   | Finding | Severity | Action |
   |---------|----------|--------|
   | {finding_1} | {P0-P3} | {action} |
   | {finding_2} | {P0-P3} | {action} |
   
   **Decomposition Required:** YES/NO
   **Technical Debt Items:** {count}
   ```

**Skip Optimize Delegation IF:**
- Backlog item is documentation-only (README, comments)
- Target file doesn't exist yet (new file creation)
- Backlog item is simple config change (<10 lines affected)

---

## 🧪 TDD Value Assessment

**MANDATORY:** Evaluate if Test-Driven Development adds HIGH value before execution.

### TDD Evaluation Criteria

| Indicator | Present? | TDD Value |
|-----------|----------|-----------|
| **Core Logic** | Business rules, calculations, algorithms | ✅ HIGH |
| **Data Transformations** | Parsing, formatting, conversion | ✅ HIGH |
| **API Contracts** | Input/output specifications | ✅ HIGH |
| **Regression-Prone** | Code that broke before | ✅ HIGH |
| **Complex Conditionals** | Multiple branches, edge cases | ✅ HIGH |
| **Documentation** | Markdown, README updates | ❌ LOW |
| **Configuration** | YAML, JSON settings | ❌ LOW |
| **UI/Styling** | CSS, visual changes | ❌ LOW |
| **File Operations** | Move, rename, delete files | ❌ LOW |
| **One-off Scripts** | Migrations, data fixes | ❌ LOW |

### TDD Decision Tree

```
IF backlog item involves:
  - Core logic OR
  - Data transformations OR
  - API contracts OR
  - Complex conditionals
THEN:
  TDD_VALUE = HIGH
  Add TDD section to backlog item
ELSE:
  TDD_VALUE = LOW
  Add simple verification approach
```

### When TDD Value = HIGH

Add this section to the backlog item:

```markdown
## 🧪 TDD Approach (Recommended)
**TDD Value:** HIGH - {reason}

### RED Phase (Write failing tests first)
1. Create test file: `tests/test_{feature}.py`
2. Write test cases for: {list expected behaviors}
3. Run tests: `pytest tests/test_{feature}.py -v`
4. Verify: All tests FAIL (expected)

### GREEN Phase (Minimal implementation)
5. Implement minimum code to pass tests
6. Run tests: `pytest tests/test_{feature}.py -v`
7. Verify: All tests PASS

### REFACTOR Phase (Clean up)
8. Improve code quality while keeping tests green
9. Final verify: `pytest tests/test_{feature}.py -v` → All PASS
```

### When TDD Value = LOW

Add this section instead:

```markdown
## 🧪 Verification Approach
**TDD Value:** LOW - {reason: documentation/config/file ops}

**Verification Method:** Manual inspection + validation commands
**No unit tests required**
```

### Toolkit Integration

**Use toolkit analyzer for TDD evaluation:**
```bash
python cortex-toolkit/core/utilities/backlog_analyzer.py --file "{backlog_file}" --evaluate-tdd
```

**Output:**
```json
{
  "tdd_value": "HIGH|LOW",
  "indicators_detected": ["core_logic", "data_transformation"],
  "recommendation": "Add TDD section with RED→GREEN→REFACTOR phases",
  "test_file_suggestion": "tests/test_{feature}.py"
}
```

---

## ⛔ CRITICAL RULES

1. **NEVER EXECUTE** backlog items—only review and enhance them
2. **NEVER DELETE** backlog files during review process
3. **ALWAYS READ ALL** files in `.asif/backlog/` directory
4. **ALWAYS ENHANCE** before renumbering (even if minor improvements)
5. **ALWAYS VERIFY** file paths and tool references
6. **ALWAYS PROVIDE** detailed report of changes made

---

## 📂 Backlog Structure

```
.asif/backlog/
├── 00-09-*.md    # 🔴 CRITICAL priority
├── 10-19-*.md    # 🟠 HIGH priority
├── 20-39-*.md    # 🟡 MEDIUM-HIGH priority
├── 40-59-*.md    # 🟡 MEDIUM priority
├── 60-79-*.md    # 🟢 LOW priority
└── 80-99-*.md    # 🔵 DEFER priority
```

**Naming Convention:** `{NN}-{descriptive-kebab-case-name}.md`
- `NN` = priority number (00-99)
- Use kebab-case for descriptive names
- Be specific: `fix-maintenance-prompt` not `maintenance-fix`

---

## 📋 Enhancement Checklist

For each backlog item, verify and enhance:

### ✅ Format Compliance
- [ ] Header with icon, title
- [ ] Metadata line: Priority | Effort | Category
- [ ] Clear objective statement (1-2 sentences)
- [ ] Numbered execution steps (atomic, sequential)
- [ ] Measurable success criteria
- [ ] Auto-delete instruction (for future execution)

### ✅ Instruction Quality
- [ ] Every step has explicit file paths (no "the config file")
- [ ] Every command is copy-pastable (no placeholders like `{name}`)
- [ ] Every verification step has exact expected output
- [ ] No ambiguous language ("update", "fix", "improve" without specifics)
- [ ] Terminal commands include expected exit codes

### ✅ Copilot Executability
- [ ] Steps are atomic (one clear action per step)
- [ ] Each step can be verified independently
- [ ] File read/write operations specify line ranges
- [ ] Search patterns use exact strings or regex
- [ ] No steps require human judgment without criteria

### ✅ Toolkit Integration
- [ ] If creating scripts: includes toolkit search step
- [ ] References `cortex-toolkit/TOOLS-INVENTORY.md` check
- [ ] Only creates new scripts if verified no alternative exists
- [ ] Updates toolkit manifest if adding new script

### ✅ Safety & Rollback
- [ ] Destructive operations have backup step
- [ ] Git commit checkpoint before major changes
- [ ] Rollback instructions for critical operations
- [ ] Dry-run mode specified where applicable

---

## 🚀 Review Protocol Execution

### Automatic Workflow (No User Input Required)

```
1. SCAN: List all .asif/backlog/*.md files
   ↓
2. READ: Load content of every file
   ↓
3. ASSESS: Rate each file (needs-major-work | needs-minor-work | ready)
   ↓
4. ENHANCE: Apply improvements to all files needing work
   ↓
5. PRIORITIZE: Assign/update priority numbers based on value
   ↓
6. RENAME: Update filenames with correct priority prefixes
   ↓
7. COMPLEXITY SCORE: Calculate complexity for each item (0-100)
   ↓
8. HOLISTIC ANALYSIS: Analyze for autonomy gaps, apply refinements
   ↓
9. OPTIMIZE DELEGATION: For items targeting files, run cortex-optimize.prompt.md
   - Bloat detection → If bloated, create decomposition backlog item first
   - Technical debt → Inject findings into backlog context
   ↓
10. TDD EVALUATION: Determine if TDD adds HIGH value
   ↓
11. REPORT: Generate comprehensive review summary
    ↓
12. HAND-OFF DECISION:
    - Score 0-50  → Ready for direct execution
    - Score 51-75 → 🛡️ HAND-OFF to Planning Orchestrator
    - Score 76-100 → 🛡️ HAND-OFF to Planning + ADO Orchestrators
```

**No user interaction needed—fully autonomous review process**

---

## 📄 Review Report Format

After reviewing all backlog items, generate this report:

```markdown
## 🧠 CORTEX Backlog Review Report
**Author:** Asif Hussain | **Date:** {date}

---

### 📊 Review Summary

**Files Reviewed:** {count}
**Files Enhanced:** {count}
**Files Renamed:** {count}
**Ready for Execution:** {count}

---

### 📋 Detailed Changes

#### 🔴 CRITICAL Priority (00-09)
| File | Status | Changes Made |
|------|--------|--------------|
| `00-{name}.md` | ✅ Enhanced | Added file paths, improved success criteria |
| `01-{name}.md` | ✅ Ready | Renumbered from 03 (elevated priority) |

#### 🟠 HIGH Priority (10-19)
| File | Status | Changes Made |
|------|--------|--------------|
...

#### 🟡 MEDIUM Priority (20-59)
...

#### 🟢 LOW Priority (60-79)
...

#### 🔵 DEFER Priority (80-99)
...

---

### 🔧 Enhancement Details

**File:** `00-maintenance-fix.md`
- ✅ Added explicit file path: `.github/prompts/cortex-maintenance.prompt.md`
- ✅ Enhanced Step 2: Added specific line ranges to read
- ✅ Improved success criteria: Added verification commands
- ✅ Added toolkit check: Search for existing preservation scripts

**File:** `01-planning-fix.md`
- ✅ Clarified progress bar requirements
- ✅ Added specific manifest sections to modify
- ✅ Added verification step with expected output
- 🔄 Renumbered: Was `03-`, elevated to `01-` (high business value)

---

### ⚠️ Issues Found

**File:** `brain-issues.md`
- ❌ Not a backlog item (conversation log)
- 🗑️ Recommended action: Delete or move to `.asif/archive/`

---

### 🧮 Complexity Scores & Hand-Off Decisions

| File | Score | Complexity | TDD Value | Action |
|------|-------|------------|-----------|--------|
| `15-docgen-prompt.md` | 40/100 | � MODERATE | LOW | Execute with checkpoints |
| `25-orchestrator-templates.md` | 42/100 | � MODERATE | LOW | Execute with checkpoints |
| `40-yaml-bloat.md` | 48/100 | � MODERATE | LOW | Execute with checkpoints |
| `45-decompose-maint.md` | 37/100 | � MODERATE | HIGH | Execute with TDD approach |
| `65-learning-paths.md` | 54/100 | � COMPLEX | HIGH | 🛡️ HAND-OFF → Planning (TDD recommended) |

#### 🛡️ Items Requiring Planning Hand-Off

**🟠 COMPLEX (Score 51-75):** X items
- Will be handed off to Planning Orchestrator for comprehensive plan creation
- Items with HIGH TDD value will include TDD phases in plan

**🔴 HIGHLY COMPLEX (Score 76-100):** X items
- Check if "ADO" mentioned in backlog item content
- If ADO mentioned: Hand off to Planning + ADO Orchestrators
- If NO ADO: Hand off to Planning Orchestrator only

---

### 📈 Priority Distribution

```
🔴 CRITICAL (00-09):  2 items  (❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚░░░░░) 75%
🟠 HIGH (10-19):      1 item   (❚❚❚❚❚░░░░░░░░░░░░░░░) 25%  
🟡 MEDIUM (20-59):    3 items  (❚❚❚❚❚❚❚❚❚❚❚❚░░░░░░░░) 60%
🟢 LOW (60-79):       2 items  (❚❚❚❚❚❚❚❚░░░░░░░░░░░░) 40%
🔵 DEFER (80-99):     0 items  (░░░░░░░░░░░░░░░░░░░░) 0%
```

---

### ✅ Next Steps

**Backlog is now optimized for execution!**

To execute items:
1. Manually read and execute individual backlog files
2. Each file contains complete execution instructions
3. Items are prioritized and ready for autonomous execution

**Recommended execution order:**
1. `00-maintenance-fix.md` (30 min) - Blocks other maintenance work
2. `00-planning-fix.md` (25 min) - High user-facing impact
3. Continue with priority 10-19, then 20-59...

---

## 📝 Standard Backlog Item Format

All backlog items should follow this structure:

```markdown
# {Icon} {Title}

**Priority:** CRITICAL|HIGH|MEDIUM|LOW | **Estimated Effort:** XX min | **Category:** {category}

---

## 🎯 Objective
{Single clear objective statement}

---

## 📋 Execution Steps

### Step 1: {Action}
{Detailed instructions Copilot can execute}

### Step 2: {Action}
{Detailed instructions}

...

---

## ✅ Success Criteria
- [ ] Criteria 1
- [ ] Criteria 2
...

---

## 🗑️ AUTO-DELETE INSTRUCTION
**After successful execution:** Delete this file with:
\`\`\`bash
rm -f /path/to/.asif/backlog/{filename}.md
\`\`\`
```

---

## 🔄 Enhancement Examples

### Example 1: Vague → Specific

**Before:**
```
### Step 2: Update the config file
Add the new setting
```

**After:**
```
### Step 2: Update Configuration
Edit `cortex-brain/config/setup.yaml`:
- Locate line 45: `enable_feature: false`
- Change to: `enable_feature: true`
- Verify: `grep "enable_feature: true" cortex-brain/config/setup.yaml`
```

### Example 2: Missing Toolkit Check

**Before:**
```
### Step 3: Create cleanup script
Write a Python script to remove old files
```

**After:**
```
### Step 3: Verify No Existing Cleanup Tool
```bash
# Check toolkit inventory first
grep -i "cleanup\|remove.*old" cortex-toolkit/TOOLS-INVENTORY.md

# Search for similar scripts
find cortex-toolkit -name "*clean*" -o -name "*remove*"
```

If no existing tool found, proceed to Step 4: Create Script
Otherwise, use existing tool: `python cortex-toolkit/{found-script}.py`
```

### Example 3: Weak Success Criteria

**Before:**
```
## ✅ Success Criteria
- [ ] File is updated
- [ ] Tests pass
```

**After:**
```
## ✅ Success Criteria
- [ ] File contains: `setting: new_value` at line 45
  Verify: `sed -n '45p' config.yaml | grep "setting: new_value"`
- [ ] All tests pass with exit code 0
  Verify: `pytest tests/ && echo $?` returns `0`
- [ ] No YAML syntax errors
  Verify: `python -c "import yaml; yaml.safe_load(open('config.yaml'))" && echo "✅ Valid"`
```

---

## 🛠️ Toolkit Integration Protocol

**MANDATORY for all backlog items that create new scripts:**

### Step 1: Search Existing Tools
```bash
# Search inventory
cat cortex-toolkit/TOOLS-INVENTORY.md | grep -i "{functionality}"

# Search by filename pattern
find cortex-toolkit -name "*{keyword}*.py"

# Search by functionality
find cortex-toolkit -name "*.py" | xargs grep -l "{function_pattern}"
```

### Step 2: Decision Tree
```
IF existing tool found:
  → Use existing tool (add usage instruction to backlog item)
ELSE IF partial functionality exists:
  → Extend existing tool (add enhancement step to backlog item)
ELSE:
  → Create new tool (add creation + documentation steps)
```

### Step 3: New Tool Template
When creating new scripts, include in backlog item:
1. Create script in appropriate category
2. Add to `cortex-toolkit/toolkit-manifest.yaml`
3. Update `cortex-toolkit/TOOLS-INVENTORY.md`
4. Add usage example in script docstring
5. Verify with: `python {script}.py --help`

---

## 🎯 Priority Assessment Guidelines

Use this decision tree to assign priority:

### Priority 00-09 (🔴 CRITICAL)
- Blocks all other work
- System is broken/unusable
- Security vulnerability
- Data loss risk
- Production outage

**Example:** "Fix broken maintenance system preventing all operations"

### Priority 10-19 (🟠 HIGH)
- High business value
- User-facing improvements
- Core functionality enhancement
- Significant pain point resolution
- Enables critical workflows

**Example:** "Add progress visualization to planning system"

### Priority 20-39 (🟡 MEDIUM-HIGH)
- Developer experience improvements
- Performance optimization
- Code maintainability
- Technical debt reduction
- Quality improvements

**Example:** "Consolidate duplicate response templates"

### Priority 40-59 (🟡 MEDIUM)
- Cleanup and organization
- Documentation improvements
- Minor optimizations
- Refactoring
- Non-critical fixes

**Example:** "Reorganize toolkit scripts by category"

### Priority 60-79 (🟢 LOW)
- New features (non-critical)
- Nice-to-have improvements
- Experimental additions
- Cosmetic changes

**Example:** "Add security dashboard tile to docs"

### Priority 80-99 (🔵 DEFER)
- Future consideration
- Low/uncertain value
- Requires more research
- Blocked by other work

**Example:** "Investigate alternative architecture pattern"
