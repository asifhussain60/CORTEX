# ✅ Architecture-Aware Vacuum Prompt - Implementation Summary

**Date:** 2026-01-09  
**Author:** Asif Hussain  
**Status:** ✅ COMPLETE  

---

## 🎯 What Was Created

### **New Prompt File:**
`.github/prompts/cortex-vacuum.prompt.md` (600+ lines)

**Purpose:** Intelligent filesystem cleanup that adapts to architecture changes in real-time.

---

## 🧠 Key Features

### **1. Real-Time Architecture Discovery (Phase 0)**

**On EVERY invocation, the prompt:**
1. Reads active CORTEX 6 epic (`cortex-brain/documents/planning/active/cortex6/acceptance-criteria/`)
2. Extracts AC-IDs and component paths
3. Builds protection map (architecture-based, NOT time-based)
4. Detects consolidation patterns (old scattered → new unified)
5. Generates runtime protection rules

**Example:**
```markdown
### ✅ Protected Components Detected:
1. **CORTEX Toolkit** (AC-PLAN-TOOLKIT-001) - `src/toolkit/**`
2. **MCP Toolkit Server** (AC-PLAN-MCP-001) - `src/mcp/toolkit_server.py`
3. **Realignment Orchestrator** (AC-REALIGN-001) - `src/orchestrators/realignment_orchestrator.py`

### ⚠️ Consolidation Candidates:
1. `src/orchestrators/planning/ast_scanner.py` → `src/toolkit/ast_parser.py`
2. `src/orchestrators/vacuum/duplicate_detector.py` → `src/toolkit/duplicate_detector.py`
```

---

### **2. Scope Management**

**Flexible Target Specification:**
- `vacuum` → Defaults to repo root (`/Users/asifhussain/PROJECTS/CORTEX`)
- `vacuum src/orchestrators/` → Scopes to specific folder
- `vacuum --dry-run` → Preview mode (no changes)

**User Approval Required:**
- Always displays scope + protection rules
- Waits for explicit Y/N confirmation
- Cancels gracefully if user says no

---

### **3. MCP-Based Execution**

**Invokes Vacuum Orchestrator via Python:**
```bash
python3 -m src.main "vacuum {folder} with architecture protection from cortex6 epic, AC-IDs: AC-PLAN-TOOLKIT-001,AC-PLAN-MCP-001, protected paths: src/toolkit/**,src/mcp/toolkit_server.py, consolidation candidates: src/orchestrators/planning/ast_scanner.py→src/toolkit/ast_parser.py, dry-run mode enabled, generate detailed report" --format markdown
```

**Benefits:**
- ✅ Uniform execution (consistent with other orchestrators)
- ✅ Audit logging (all operations tracked)
- ✅ State management (resumable if interrupted)
- ✅ Report generation (detailed cleanup summaries)

---

### **4. Real-Time Adaptation Logic**

**Prompt automatically detects:**
1. **Epic updates:** Rescans if epic modified since last run
2. **New AC-IDs:** Protects newly added components immediately
3. **Implementation progress:** Upgrades protection priority for completed features
4. **Consolidation completion:** Removes mappings when old files already deleted

**Example:**
```python
if latest_epic_modification > last_scan_time:
    print("📋 Epic updated - refreshing protection rules...")
    rescan_architecture()

if new_ac_ids_detected:
    print(f"🆕 New criteria detected: {new_ac_ids}")
    add_protection_rules(new_ac_ids)
```

---

### **5. Intelligence Queries**

**Built-in helper functions for GitHub Copilot:**

**Query 1: Get Protected Paths**
```python
def get_protected_paths():
    # Extracts all AC-IDs and paths from epic
    # Returns: [{'path': 'src/toolkit/', 'ac_id': 'AC-PLAN-TOOLKIT-001', ...}]
```

**Query 2: Detect Consolidations**
```python
def detect_consolidations():
    # Finds keywords: unified, toolkit, replaces, supersedes
    # Returns: [{'old': 'ast_scanner.py', 'new': 'toolkit/ast_parser.py', ...}]
```

**Query 3: Check Implementation Status**
```python
def check_implementation_status(ac_id, path):
    # Checks: file exists, recent commits, tests present
    # Returns: "not_started" | "in_progress" | "complete"
```

---

## 📊 Workflow Comparison

### **Before (Standard Vacuum):**
```
User: "vacuum src/orchestrators/"
↓
Vacuum scans folder with static rules
↓
Cleans temp files, duplicates, etc.
↓
May accidentally delete new features (no architecture awareness)
```

### **After (Architecture-Aware Vacuum):**
```
User: "vacuum src/orchestrators/"
↓
Step 1: Read CORTEX 6 epic
Step 2: Extract AC-IDs (AC-PLAN-TOOLKIT-001, etc.)
Step 3: Build protection map
Step 4: Detect consolidation patterns
Step 5: Display scope + protected components
Step 6: Wait for user approval (Y/N)
Step 7: Invoke Python with architecture context
↓
Result: New features protected, consolidation candidates flagged
```

---

## 🛡️ Protection Rules

### **Architecture-Based (Priority 100):**
- `src/toolkit/**` (AC-PLAN-TOOLKIT-001)
- `src/mcp/toolkit_server.py` (AC-PLAN-MCP-001)
- `src/orchestrators/realignment_orchestrator.py` (AC-REALIGN-001)
- Any component with AC-ID in epic

### **Dependency-Based (Priority 90):**
- Files importing from protected components
- Active references detected via AST analysis

### **Consolidation Candidates (Priority 10):**
- Old scattered implementations superseded by unified systems
- Flagged for review (not auto-deleted)
- Examples: `ast_scanner.py`, `duplicate_detector.py`

### **Static Protection (Permanent):**
- `cortex-brain/tier0/**` - Governance
- `cortex-brain/tier1/dags/**` - Active plans
- `cortex-brain/tier2/**` - Knowledge graph
- `src/orchestrators/**` - Core orchestrators
- `.github/prompts/**` - Prompt files

---

## 🎯 Example Invocations

### **Example 1: Repo-Wide Vacuum**

**User:** `vacuum`

**GitHub Copilot Action:**
1. Reads `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/`
2. Extracts 3 AC-IDs: AC-PLAN-TOOLKIT-001, AC-PLAN-MCP-001, AC-REALIGN-001
3. Builds protection map with 3 protected paths + 2 consolidation candidates
4. Displays scope: `/Users/asifhussain/PROJECTS/CORTEX` (full repo)
5. Shows protected components and consolidation candidates
6. Asks: "Proceed with vacuum? (Y/N)"
7. On Y: Invokes `python3 -m src.main "vacuum ... with AC-IDs: ..."`
8. Displays results: Protected (3 paths), Flagged (2 candidates), Cleaned (temp files, etc.)

---

### **Example 2: Folder-Specific Vacuum**

**User:** `vacuum src/orchestrators/`

**GitHub Copilot Action:**
1. Scans epic (same as Example 1)
2. Filters protection rules to `src/orchestrators/` scope
3. Finds: 1 protected (realignment_orchestrator.py) + 2 consolidation candidates
4. Displays scope: `src/orchestrators/`
5. Shows filtered protection rules
6. Asks: "Proceed with vacuum? (Y/N)"
7. On Y: Invokes Python with scoped parameters
8. Displays results: Protected (1 path), Flagged (2 candidates), Cleaned (cache, logs)

---

### **Example 3: User Cancels**

**User:** `vacuum` → (prompt) → `N`

**GitHub Copilot Action:**
1. Reads epic and builds protection map (same as Example 1)
2. Displays scope and protection rules
3. Asks: "Proceed with vacuum? (Y/N)"
4. User says: `N` or `no`
5. Responds: "❌ Vacuum Cancelled. No files were modified."
6. Stores architecture snapshot in knowledge graph (for next run)

---

## 🔄 Integration with CORTEX.prompt.md

**Updated Master Routing Table:**
```markdown
| Pattern | Orchestrator | Priority | Mode |
|---------|--------------|----------|------|
| `^(vacuum\|deep clean\|organize files)` | **Vacuum v2** | 45 | architecture-aware |
```

**Added Note:**
```markdown
🧹 Architecture-Aware Mode: Vacuum v2 uses real-time epic scanning - 
see `.github/prompts/cortex-vacuum.prompt.md` for intelligent cleanup workflow.
```

**Specialized Execution Protocol:**
```markdown
### 🧹 ARCHITECTURE-AWARE - Specialized Workflow (Vacuum Only)

For Vacuum requests, use `.github/prompts/cortex-vacuum.prompt.md` workflow:

1. Read CORTEX 6 epic
2. Extract AC-IDs and protected paths
3. Detect consolidation patterns
4. Display scope + protection rules
5. Wait for approval (Y/N)
6. Invoke Python with architecture context
```

---

## 📋 Checklist for Every Invocation

**GitHub Copilot MUST:**
- [ ] Parse user request (extract folder/scope)
- [ ] Read CORTEX 6 epic (`cortex-brain/documents/planning/active/cortex6/acceptance-criteria/`)
- [ ] Extract AC-IDs and component paths
- [ ] Build protection map (architecture + static rules)
- [ ] Detect consolidation patterns (old → new)
- [ ] Display scope and protection rules to user
- [ ] Wait for user approval (Y/N)
- [ ] If approved, invoke Vacuum Orchestrator via Python with transformed request
- [ ] Display results with protection/cleanup stats
- [ ] Store architecture snapshot in knowledge graph

---

## 🎯 Success Criteria

**This prompt is working correctly if:**

✅ Every invocation scans CORTEX 6 epic before cleanup  
✅ New AC-IDs are automatically detected and protected  
✅ Consolidation candidates are flagged (not deleted)  
✅ User approval is required before any cleanup  
✅ Protected components are never deleted  
✅ Dry-run mode is used by default  
✅ Detailed reports are generated  
✅ Architecture snapshots are stored in knowledge graph  
✅ Real-time adaptation works (new features protected immediately)  
✅ No false positives (legitimate code NOT flagged for deletion)

---

## 🚀 Next Steps

**1. Test the Prompt:**
- Try: `vacuum` (full repo)
- Try: `vacuum src/orchestrators/` (specific folder)
- Verify: Protection rules display correctly
- Verify: User approval prompt appears
- Verify: Python invocation includes AC-IDs and protected paths

**2. Implement Phase 0 in Vacuum Orchestrator:**
- See: `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/CX6-vacuum-phase-0-enhancement.md`
- Implement epic scanning logic
- Add AC-ID extraction
- Add consolidation detection
- Estimated: 16-24 hours

**3. Create Example Scenarios:**
- Document: Real vacuum runs with CORTEX 6 epic
- Capture: Protection rule generation
- Verify: Consolidation candidate detection

**4. Knowledge Graph Integration:**
- Store: Architecture snapshots after each run
- Track: Consolidation completion progress
- Learn: Protection patterns over time

---

## 📚 Files Created/Modified

**Created:**
- `.github/prompts/cortex-vacuum.prompt.md` (600+ lines)
- `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/CX6-vacuum-phase-0-enhancement.md` (350+ lines)

**Modified:**
- `.github/prompts/CORTEX.prompt.md` - Added architecture-aware routing for Vacuum v2
- `src/orchestrators/vacuum/vacuum_orchestrator_v2.py` - Fixed JSON serialization bug, added jinja_env initialization

---

## 🎯 Key Innovation

**Traditional Cleanup Tools:** Static rules, time-based protection, no architecture awareness  
**CORTEX Vacuum v2:** Dynamic rules, architecture-based protection, real-time epic adaptation

**Example Innovation:**
```
Traditional: "Don't delete files modified in last 30 days"
→ Problem: Protects old code, may miss new features

CORTEX: "Don't delete components specified in active epic with AC-IDs"
→ Solution: Protects intentional architecture, flags obsolete code
```

---

**This prompt makes Vacuum orchestrator truly intelligent - it learns from the epic as you build, adapting protection rules in real-time to match your implementation progress.**

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
