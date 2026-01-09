# 🧹 CORTEX Vacuum - Architecture-Aware Cleanup

**Version:** 1.3.0 | **Status:** ✅ PRODUCTION | **Type:** Autonomous Execution  
**Author:** Asif Hussain | **Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

**Autonomous filesystem cleanup with intelligent document consolidation and orchestrator discovery.**

### **Execution Mode: SILENT**
- ✅ Architecture discovery (automatic)
- ✅ Consolidation detection (automatic)
- ✅ Git checkpoint (automatic)
- ✅ Execute consolidation (automatic)
- ✅ Execute cleanup (automatic)
- ✅ **Create navigation indices** (automatic)
- ✅ Executive summary only (concise report)

---

## 📋 Execution Protocol (AUTONOMOUS)

### **When user says:** `vacuum <folder>`

**You execute silently:**

1. **Create git checkpoint** (automatic safety backup)
2. **Scan architecture** (read CORTEX 6 epic for AC-IDs and protected paths)
3. **Detect consolidation** (version progressions, summaries, duplicates)
4. **Execute consolidation** (merge + archive with 100% data preservation)
5. **Create navigation indices** (00-INDEX.md updates or RELOCATION-MAP.yaml)
6. **Execute cleanup** (temp files, build artifacts, duplicates)
7. **Report executive summary** (concise results with index references)

**NO verbose output. NO step-by-step narration. NO approval prompts.**

---

## 🎯 Executive Summary Format

**After execution, display ONLY this:**

```markdown
## 🧹 Vacuum Complete - {folder_name}

**Git Checkpoint:** {commit_id} - "{commit_message}"

### 📦 Consolidation
- {n} files consolidated → {m} enhanced + {k} archived
- {n} files relocated to {k} categorical subfolders
- {lines} duplicate lines eliminated
- 100% data preserved in archive/
- Navigation index: {updated|created} - {path}

### 🗂️ Organization
- Root-level files: {before} → {after} ({percent}% reduction)
- Subfolders created: {list}
- Reference tracking: {00-INDEX.md|RELOCATION-MAP.yaml}

### 🗑️ Cleanup
- {n} temporary files removed
- {n} build artifacts removed  
- {n} duplicate files removed
- {size} freed

### 🛡️ Protected
- {n} AC-protected components skipped
- {list of key AC-IDs}

**Navigation:** See `{index_path}` for complete relocation map
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
4. **Create/update reference index** (00-INDEX.md or RELOCATION-MAP.yaml)
5. Track metrics (files consolidated, lines eliminated)

### **Reference Index Generation**
When files are relocated to subfolders, create/update navigation aids:

**Option 1: Update existing 00-INDEX.md**
- Add "📚 Document Hierarchy (Organized)" section
- List all subfolders with purpose descriptions
- Include file counts and categories
- Update "Quick Reference by Use Case" with new paths

**Option 2: Create RELOCATION-MAP.yaml** (if no INDEX exists)
```yaml
relocated_files:
  - original: "CX6-planning-workflow.md"
    new_location: "workflows/CX6-planning-workflow.md"
    category: "workflows"
    reason: "Orchestrator workflow documentation"
  
  - original: "GAP-FIX-SUMMARY.md"
    new_location: "summaries/GAP-FIX-SUMMARY.md"
    category: "summaries"
    reason: "Implementation summary"

folder_structure:
  workflows/:
    purpose: "Orchestrator workflows & processes"
    files: ["CX6-planning-workflow.md"]
  
  summaries/:
    purpose: "Update summaries & implementation reports"
    files: ["GAP-FIX-SUMMARY.md", "PLAN-UPDATE-SUMMARY.md"]
  
  archive/:
    purpose: "Historical versions & superseded docs"
    files: ["workflow-v1.md", "workflow-v2.md"]

metadata:
  vacuum_date: "2026-01-09"
  files_relocated: 18
  root_level_before: 23
  root_level_after: 8
  data_preservation: "100% (archived)"
```

### **Cleanup Execution (Silent)**
1. Remove: temp files, build artifacts, duplicates, empty dirs
2. Track metrics (files removed, space freed)
3. Respect protection rules (AC-protected paths never touched)
4. **Generate relocation tracking** for orchestrator discovery

---

## 📦 Consolidation Patterns (Reference)

### **Pattern 1: Version Progressions**
- Detect: `filename-v1.md` + `filename-v2.md` + `filename-v3.md`
- Action: Keep latest, add version history section, archive older versions
- **Index Update:** Add version history reference in 00-INDEX.md

### **Pattern 2: Update Summaries**
- Detect: `*-UPDATE-v14.*.md`, `*-UPDATE-v15.*.md`, `*-SUMMARY.md`
- Action: Move to `summaries/` subfolder, update parent index
- **Index Update:** Create summaries/ section with file listing

### **Pattern 3: Implementation Summaries**
- Detect: `*-SUMMARY.md`, `*-IMPLEMENTATION-*.md`, `*-PLAN.md`
- Action: Extract metadata, move to appropriate folder, create reference
- **Index Update:** Add to categorical section with purpose description

### **Pattern 4: Workflow Documents**
- Detect: `*-workflow*.md`, `*-orchestrator*.md`, `*-process*.md`
- Action: Move to `workflows/` subfolder
- **Index Update:** Add workflows/ section with descriptions

### **Pattern 5: Analysis Documents**
- Detect: `*-ANALYSIS*.md`, `*-RECOMMENDATIONS*.md`, `*-REVIEW*.md`
- Action: Move to `analysis/` subfolder
- **Index Update:** Add analysis/ section

### **Consolidation Rules**
✅ Extract ALL unique content  
✅ Archive to `archive/` (NEVER delete)  
✅ Add changelog/version history (NOT version dumps)  
✅ Preserve metadata (dates, authors, AC-IDs)  
✅ **Create/update navigation indices** (00-INDEX.md or RELOCATION-MAP.yaml)  
✅ **Update parent folder README** with subfolder references  

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

## 🔍 Orchestrator Discovery Intelligence

**After vacuum consolidation, orchestrators can discover relocated files via:**

### **Method 1: Read 00-INDEX.md (Preferred)**
```python
# Orchestrators should check for 00-INDEX.md first
index_path = folder / "00-INDEX.md"
if index_path.exists():
    # Parse hierarchy section for subfolder structure
    # Extract file locations from categorical listings
    # Use "Quick Reference by Use Case" for contextual discovery
```

### **Method 2: Read RELOCATION-MAP.yaml (Fallback)**
```python
# If 00-INDEX.md doesn't exist, check for RELOCATION-MAP.yaml
map_path = folder / "RELOCATION-MAP.yaml"
if map_path.exists():
    relocation_data = yaml.safe_load(map_path.read_text())
    # Access: relocated_files[], folder_structure{}, metadata{}
```

### **Method 3: Semantic Pattern Discovery (Auto-fallback)**
```python
# If no index exists, orchestrators use pattern matching
patterns = {
    "workflows": ["*workflow*.md", "*orchestrator*.md", "*process*.md"],
    "summaries": ["*SUMMARY*.md", "*UPDATE*.md", "*IMPLEMENTATION*.md"],
    "analysis": ["*ANALYSIS*.md", "*RECOMMENDATIONS*.md", "*REVIEW*.md"],
    "requirements": ["*requirements*.yaml", "*specs*.yaml"],
    "strategies": ["*strategy*.yaml", "*framework*.yaml"],
    "enhancements": ["*enhancement*.md", "*improvement*.md"],
    "archive": ["*-v[0-9]*.md", "*-legacy*.md", "*-old*.md"]
}
```

### **Best Practice for Orchestrators**
1. **Always check for 00-INDEX.md** (most comprehensive)
2. **Fall back to RELOCATION-MAP.yaml** (machine-readable)
3. **Use semantic patterns** (robust auto-discovery)
4. **Cache discovered structure** (performance optimization)

### **Vacuum Creates These Automatically**
- Updates existing `00-INDEX.md` with new structure
- Creates `RELOCATION-MAP.yaml` if no index exists
- Ensures both human-readable and machine-parseable navigation

---

**Version:** 1.3.0 - Added orchestrator discovery intelligence  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
