# 🧹 CORTEX Vacuum - Architecture-Aware Cleanup

**Version:** 1.2.0 | **Status:** ✅ PRODUCTION | **Type:** Autonomous Execution  
**Author:** Asif Hussain | **Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

**Autonomous filesystem cleanup with intelligent document consolidation.**

### **Execution Mode: SILENT**
- ✅ Architecture discovery (automatic)
- ✅ Consolidation detection (automatic)
- ✅ Git checkpoint (automatic)
- ✅ Execute cleanup (automatic)
- ✅ Executive summary only (concise report)

---

## 📋 Execution Protocol (AUTONOMOUS)

### **When user says:** `vacuum <folder>`

**You execute silently:**

1. **Create git checkpoint** (automatic safety backup)
2. **Scan architecture** (read CORTEX 6 epic for AC-IDs and protected paths)
3. **Detect consolidation** (version progressions, summaries, duplicates)
4. **Execute consolidation** (merge + archive with 100% data preservation)
5. **Execute cleanup** (temp files, build artifacts, duplicates)
6. **Report executive summary** (concise results)

**NO verbose output. NO step-by-step narration. NO approval prompts.**

---

## 🎯 Executive Summary Format

**After execution, display ONLY this:**

```markdown
## 🧹 Vacuum Complete - {folder_name}

**Git Checkpoint:** {commit_id} - "{commit_message}"

### 📦 Consolidation
- {n} files consolidated → {m} enhanced + {k} archived
- {lines} duplicate lines eliminated
- 100% data preserved in archive/

### 🗑️ Cleanup
- {n} temporary files removed
- {n} build artifacts removed  
- {n} duplicate files removed
- {size} freed

### 🛡️ Protected
- {n} AC-protected components skipped
- {list of key AC-IDs}

**Details:** `{report_path}`
```

**That's it. Concise. Actionable. Complete.**

---

## 🧠 Implementation Details (For GitHub Copilot)

### **Architecture Discovery (Silent)**
1. Read: `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/`
2. Extract AC-IDs: `AC-[A-Z]+-[A-Z0-9]+-\d{3}` with paths
3. Build protection map (in memory, no output)

### **Consolidation Detection (Silent)**
1. Detect version progressions: `*-v1.md`, `*-v2.md`, `*-v3.md`
2. Detect summaries: `*-SUMMARY.md`, `*-UPDATE-*.md`, `*-IMPLEMENTATION-*.md`
3. Analyze overlap, extract unique content
4. Create consolidation plan (in memory, no output)

### **Consolidation Execution (Silent)**
1. For each group: read base, extract unique, merge intelligently
2. Archive old files to `archive/{filename}-{date}.ext`
3. Write consolidated files
4. Track metrics (files consolidated, lines eliminated)

### **Cleanup Execution (Silent)**
1. Remove: temp files, build artifacts, duplicates, empty dirs
2. Track metrics (files removed, space freed)
3. Respect protection rules (AC-protected paths never touched)

---

## 📦 Consolidation Patterns (Reference)

### **Pattern 1: Version Progressions**
- Detect: `filename-v1.md` + `filename-v2.md` + `filename-v3.md`
- Action: Keep latest, add version history section, archive older versions

### **Pattern 2: Update Summaries**
- Detect: `*-UPDATE-v14.*.md`, `*-UPDATE-v15.*.md`
- Action: Convert to YAML changelog in parent file, archive summaries

### **Pattern 3: Implementation Summaries**
- Detect: `*-SUMMARY.md`, `*-IMPLEMENTATION-*.md`
- Action: Extract metadata, merge to parent, archive summaries

### **Consolidation Rules**
✅ Extract ALL unique content  
✅ Archive to `archive/` (NEVER delete)  
✅ Add changelog/version history (NOT version dumps)  
✅ Preserve metadata (dates, authors, AC-IDs)  

---

## 🛡️ Protection Rules (Static)

**Always protected:**
- `cortex-brain/tier0/**` - Governance
- `cortex-brain/tier1/dags/**` - Active plans
- `cortex-brain/tier2/knowledge-graph.db` - Knowledge
- `cortex-brain/config/**` - Configuration
- `cortex-brain/manifests/**` - Orchestrator configs
- `src/orchestrators/**` - Orchestrators
- `src/infrastructure/**` - Infrastructure
- `src/main.py` - Entry point

**Dynamic protection (from AC-IDs):**
- Any path associated with AC-ID in CORTEX 6 epic
- New features under development
- Consolidated unified systems

---

## 📚 References

- **Vacuum Orchestrator:** `src/orchestrators/vacuum/vacuum_orchestrator_v2.py`
- **CORTEX 6 Epic:** `cortex-brain/documents/planning/active/cortex6/`
- **Brain Protection:** `cortex-brain/brain-protection-rules.yaml`

---

**Version:** 1.2.0 - Silent autonomous execution with consolidation  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
