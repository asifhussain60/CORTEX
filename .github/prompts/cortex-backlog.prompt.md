---
mode: agent
description: CORTEX Backlog Review & Enhancement System - Reviews, enhances, and prioritizes backlog items
---

# 📋 CORTEX Backlog Review & Enhancement System

**Version:** 2.0.0 | **Author:** Asif Hussain  
**Location:** `.asif/backlog/` | **Format:** Priority-prefixed markdown files

---

## 🎯 Purpose

**Review, enhance, and prioritize** CORTEX backlog items for optimal GitHub Copilot execution. This prompt does NOT execute backlog items—it prepares them for execution.

**Core Responsibilities:**
1. **Review** all backlog files for manual instructions/enhancements needed
2. **Enhance** instructions for Copilot executability (clear, atomic, verifiable)
3. **Prioritize** by renaming files with correct priority prefixes (00-99)
4. **Validate** format consistency and completeness

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
7. REPORT: Generate comprehensive review summary
```

**No user interaction needed—fully autonomous review process**

---

## � Review Report Format

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

## � Priority Assessment Guidelines

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
