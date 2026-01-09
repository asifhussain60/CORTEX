# 🧹 CORTEX Vacuum - Architecture-Aware Cleanup

**Version:** 1.0.0 | **Status:** ✅ PRODUCTION | **Type:** MCP-Based Autonomous Cleanup  
**Author:** Asif Hussain | **Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

**Intelligent filesystem cleanup that adapts to architecture changes in real-time.**

### **Key Capabilities:**
1. **Architecture-Aware:** Reads active CORTEX 6 epic to protect new features
2. **Real-Time Adaptation:** Updates protection rules on every invocation
3. **Consolidation Detection:** Identifies old scattered implementations superseded by unified systems
4. **MCP-Based Execution:** Uses Vacuum Orchestrator via Model Context Protocol
5. **User Approval Required:** Always confirms before cleanup

---

## 🧠 Architecture Intelligence System

### **Phase 0: Pre-Scan Architecture Discovery**

**On EVERY invocation, you MUST:**

1. **Read Active CORTEX 6 Epic**
   ```
   Path: /Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/planning/active/cortex6/acceptance-criteria/
   ```

2. **Parse All Acceptance Criteria Files**
   - Search for AC-IDs: `AC-[A-Z]+-[A-Z0-9]+-\d{3}`
   - Extract component paths and descriptions
   - Build protection map

3. **Identify Protected Components**
   ```
   Pattern: "Component X (AC-XXX-YYY-001) in src/path/to/component"
   
   Extract:
   - AC-ID: AC-XXX-YYY-001
   - Path: src/path/to/component
   - Reason: Component X description
   ```

4. **Detect Consolidation Patterns**
   - Look for "unified", "toolkit", "consolidated", "replaces", "supersedes"
   - Identify old scattered implementations
   - Map: old_path → new_path (consolidation candidate)

5. **Build Real-Time Protection Rules**
   ```yaml
   architecture_protection:
     - pattern: "src/toolkit/**"
       ac_id: "AC-PLAN-TOOLKIT-001"
       reason: "CORTEX Toolkit - New unified modular system"
       priority: 100
     
     - pattern: "src/mcp/toolkit_server.py"
       ac_id: "AC-PLAN-MCP-001"
       reason: "MCP Toolkit Server - MCP exposure layer"
       priority: 100
   
   consolidation_candidates:
     - old: "src/orchestrators/planning/ast_scanner.py"
       new: "src/toolkit/ast_parser.py"
       reason: "Superseded by CORTEX Toolkit"
       action: "flag_for_review"
   ```

---

## 📋 Invocation Protocol

### **Step 1: Parse User Request**

**User says:** `vacuum <folder>` OR `vacuum` (defaults to repo root)

**Extract:**
- `target_folder`: User-specified path or `/Users/asifhussain/PROJECTS/CORTEX`
- `scope`: "folder" or "repo"

---

### **Step 2: Architecture Discovery (MANDATORY)**

**YOU MUST execute this BEFORE calling Vacuum Orchestrator:**

```markdown
## 🧠 Architecture Discovery

Reading active CORTEX 6 epic for real-time protection rules...

**Scanning:** `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/`
```

**Actions:**
1. Use `read_file` to scan these files:
   - `CX6-planning-orchestrator-workflow-v3.md`
   - `ARCHITECTURE-ANALYSIS-AND-RECOMMENDATIONS.md`
   - All `AC-*.md` files in acceptance-criteria folder

2. Extract ALL occurrences of:
   ```regex
   AC-[A-Z]+-[A-Z0-9]+-\d{3}
   ```

3. For each AC-ID, extract:
   - Component path (look for `src/`, `cortex-brain/`, file paths)
   - Component description
   - Status (implementation phase, roadmap position)

4. Display findings:
   ```markdown
   ### ✅ Protected Components Detected:
   1. **CORTEX Toolkit** (AC-PLAN-TOOLKIT-001)
      - Path: `src/toolkit/**`
      - Status: Phase 1 implementation (24-32h)
      - Protection: FULL
   
   2. **MCP Toolkit Server** (AC-PLAN-MCP-001)
      - Path: `src/mcp/toolkit_server.py`
      - Status: Phase 2 implementation (16-20h)
      - Protection: FULL
   
   3. **Realignment Orchestrator** (AC-REALIGN-001)
      - Path: `src/orchestrators/realignment_orchestrator.py`
      - Status: Phase 4 implementation (20-28h)
      - Protection: FULL
   
   ### ⚠️ Consolidation Candidates:
   1. `src/orchestrators/planning/ast_scanner.py`
      → Superseded by: `src/toolkit/ast_parser.py`
      → Action: Flag for review (safe to remove after toolkit migration)
   
   2. `src/orchestrators/vacuum/duplicate_detector.py`
      → Superseded by: `src/toolkit/duplicate_detector.py`
      → Action: Flag for review (safe to remove after toolkit migration)
   ```

---

### **Step 3: Scope Confirmation**

**Display to user:**

```markdown
## 🎯 Vacuum Scope

**Target:** `{target_folder}`
**Scope:** {folder/repo}

### Protected Components (Will NOT be deleted):
- ✅ src/toolkit/** (AC-PLAN-TOOLKIT-001)
- ✅ src/mcp/toolkit_server.py (AC-PLAN-MCP-001)
- ✅ src/orchestrators/realignment_orchestrator.py (AC-REALIGN-001)
- ✅ {any other AC-protected paths}

### Consolidation Candidates (Will be FLAGGED for review):
- ⚠️ {old_path_1} → {new_path_1}
- ⚠️ {old_path_2} → {new_path_2}

### Standard Cleanup Targets:
- 🗑️ Temporary files (*.tmp, *.temp)
- 🗑️ Build artifacts (__pycache__, *.pyc, .pytest_cache)
- 🗑️ Duplicate files (hash-based detection)
- 🗑️ Empty directories
- 🗑️ Log files (*.log older than 7 days)

**Proceed with vacuum? (Y/N)**
```

**Wait for user approval.**

---

### **Step 4: Invoke Vacuum Orchestrator via MCP**

**ONLY after user approval (Y/yes), execute:**

```python
python3 -m src.main "vacuum {target_folder} with architecture protection from cortex6 epic, AC-IDs: {comma_separated_ac_ids}, protected paths: {comma_separated_protected_paths}, consolidation candidates: {comma_separated_old_paths}, dry-run mode enabled, generate detailed report" --format markdown
```

**Transformation Rules:**
- Include all AC-IDs found in Step 2
- Include all protected paths
- Include consolidation mappings (old → new)
- Always use dry-run mode first
- Request detailed report

**Example:**
```bash
python3 -m src.main "vacuum /Users/asifhussain/PROJECTS/CORTEX with architecture protection from cortex6 epic, AC-IDs: AC-PLAN-TOOLKIT-001,AC-PLAN-MCP-001,AC-REALIGN-001, protected paths: src/toolkit/**,src/mcp/toolkit_server.py,src/orchestrators/realignment_orchestrator.py, consolidation candidates: src/orchestrators/planning/ast_scanner.py→src/toolkit/ast_parser.py, dry-run mode enabled, generate detailed report" --format markdown
```

---

### **Step 5: Display Results**

**After Vacuum Orchestrator completes:**

```markdown
## 🧹 Vacuum Results

### Protected (Skipped):
- ✅ {count} files protected by architecture rules
- ✅ {list of AC-IDs and paths}

### Consolidation Candidates Flagged:
- ⚠️ {old_path} → {new_path} (review recommended)

### Cleaned:
- 🗑️ {count} temporary files removed
- 🗑️ {count} build artifacts removed
- 🗑️ {count} duplicate files removed
- 🗑️ {size_mb} MB freed

### Report:
📄 {path_to_vacuum_report}
```

---

## 🛡️ Brain Protection Rules

### **CRITICAL: NEVER Delete These (Static Protection)**

**Governance (Tier 0):**
- `cortex-brain/tier0/**` - Core rules, SKULL protection
- `cortex-brain/brain-protection-rules.yaml`
- `.github/prompts/CORTEX.prompt.md`

**Active Plans (Tier 1):**
- `cortex-brain/tier1/dags/**` - Active execution graphs
- `cortex-brain/documents/planning/active/**` - All active plans

**Knowledge (Tier 2):**
- `cortex-brain/tier2/knowledge-graph.db` - Learned patterns
- `cortex-brain/knowledge/**` - Permanent knowledge base

**Configuration:**
- `cortex-brain/config/**` - System configuration
- `cortex-brain/manifests/**` - Orchestrator manifests

**Source Code:**
- `src/orchestrators/**` - All orchestrators (unless consolidation candidate)
- `src/infrastructure/**` - Core infrastructure
- `src/main.py` - Entry point

---

## 🔄 Real-Time Adaptation Logic

### **On Every Invocation:**

1. **Epic Freshness Check**
   ```python
   # Check if epic documents were modified since last run
   epic_path = "cortex-brain/documents/planning/active/cortex6/"
   latest_modification = get_latest_mtime(epic_path)
   
   if latest_modification > last_scan_time:
       print("📋 Epic updated since last scan - refreshing protection rules...")
       rescan_architecture()
   ```

2. **New AC-ID Detection**
   ```python
   # Compare current AC-IDs with previous scan
   current_ac_ids = extract_ac_ids(epic_documents)
   new_ac_ids = current_ac_ids - previous_ac_ids
   
   if new_ac_ids:
       print(f"🆕 New acceptance criteria detected: {new_ac_ids}")
       add_protection_rules(new_ac_ids)
   ```

3. **Implementation Progress Tracking**
   ```python
   # Check roadmap phase completion
   for ac_id, component in protected_components.items():
       if is_implemented(component['path']):
           print(f"✅ {ac_id} implementation detected at {component['path']}")
           upgrade_protection_priority(component['path'], priority=100)
   ```

4. **Consolidation Validation**
   ```python
   # Verify old implementations still exist
   for old_path, new_path in consolidation_map.items():
       if not exists(old_path):
           print(f"✅ {old_path} already removed (consolidation complete)")
           remove_from_consolidation_map(old_path)
       elif exists(new_path) and not imports_exist(old_path):
           print(f"⚠️ {old_path} safe to remove (no active imports)")
           upgrade_consolidation_recommendation(old_path, "safe_to_delete")
   ```

---

## 📊 Architecture Intelligence Queries

### **Query 1: Find All Protected Paths**

```python
def get_protected_paths():
    epic_path = Path("cortex-brain/documents/planning/active/cortex6/acceptance-criteria")
    protected = []
    
    for doc in epic_path.glob("**/*.md"):
        content = doc.read_text()
        
        # Find AC-IDs with surrounding context
        matches = re.finditer(
            r'([^\n]+)(AC-[A-Z]+-[A-Z0-9]+-\d{3})([^\n]+)',
            content
        )
        
        for match in matches:
            context = match.group(0)
            ac_id = match.group(2)
            
            # Extract file paths from context
            paths = re.findall(r'`([^`]+\.(py|yaml|json|md))`', context)
            paths += re.findall(r'src/[\w/]+', context)
            
            for path in paths:
                protected.append({
                    'path': path,
                    'ac_id': ac_id,
                    'source': doc.name,
                    'context': context.strip()
                })
    
    return protected
```

### **Query 2: Detect Consolidation Patterns**

```python
def detect_consolidations():
    epic_path = Path("cortex-brain/documents/planning/active/cortex6/acceptance-criteria")
    consolidations = []
    
    # Keywords indicating consolidation
    keywords = [
        'unified', 'toolkit', 'consolidated', 'replaces', 
        'supersedes', 'superseded', 'migration', 'extract',
        'refactor', 'old scattered', 'new unified'
    ]
    
    for doc in epic_path.glob("**/*.md"):
        content = doc.read_text()
        
        for keyword in keywords:
            if keyword in content.lower():
                # Extract context around keyword
                paragraphs = content.split('\n\n')
                for para in paragraphs:
                    if keyword in para.lower():
                        # Look for old → new path mappings
                        old_paths = re.findall(r'old[:\s]+`?([^`\n]+)`?', para, re.I)
                        new_paths = re.findall(r'new[:\s]+`?([^`\n]+)`?', para, re.I)
                        
                        if old_paths and new_paths:
                            consolidations.append({
                                'old': old_paths[0],
                                'new': new_paths[0],
                                'reason': para[:200],
                                'source': doc.name
                            })
    
    return consolidations
```

### **Query 3: Check Implementation Status**

```python
def check_implementation_status(ac_id, path):
    # Check if component exists
    if not Path(path).exists():
        return "not_started"
    
    # Check for recent commits
    result = subprocess.run(
        ['git', 'log', '--since=7.days', '--oneline', '--', path],
        capture_output=True,
        text=True
    )
    
    if result.stdout.strip():
        return "in_progress"
    
    # Check for tests
    test_path = path.replace('src/', 'tests/').replace('.py', '_test.py')
    if Path(test_path).exists():
        return "complete"
    
    return "unknown"
```

---

## 🎯 Example Invocations

### **Example 1: Vacuum Entire Repo**

**User:** `vacuum`

**Your Response:**
```markdown
## 🧠 Architecture Discovery

Reading active CORTEX 6 epic for real-time protection rules...

**Scanning:** `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/`

### ✅ Protected Components Detected:
1. **CORTEX Toolkit** (AC-PLAN-TOOLKIT-001) - `src/toolkit/**`
2. **MCP Toolkit Server** (AC-PLAN-MCP-001) - `src/mcp/toolkit_server.py`
3. **Realignment Orchestrator** (AC-REALIGN-001) - `src/orchestrators/realignment_orchestrator.py`

### ⚠️ Consolidation Candidates:
1. `src/orchestrators/planning/ast_scanner.py` → `src/toolkit/ast_parser.py`

---

## 🎯 Vacuum Scope

**Target:** `/Users/asifhussain/PROJECTS/CORTEX`
**Scope:** Full repository

**Proceed with vacuum? (Y/N)**
```

---

### **Example 2: Vacuum Specific Folder**

**User:** `vacuum src/orchestrators/`

**Your Response:**
```markdown
## 🧠 Architecture Discovery

Reading active CORTEX 6 epic for real-time protection rules...

### ✅ Protected in src/orchestrators/:
- `src/orchestrators/realignment_orchestrator.py` (AC-REALIGN-001)

### ⚠️ Consolidation Candidates in src/orchestrators/:
- `src/orchestrators/planning/ast_scanner.py` → `src/toolkit/ast_parser.py`
- `src/orchestrators/vacuum/duplicate_detector.py` → `src/toolkit/duplicate_detector.py`

---

## 🎯 Vacuum Scope

**Target:** `src/orchestrators/`
**Scope:** Folder

**Proceed with vacuum? (Y/N)**
```

---

### **Example 3: User Says No**

**User Response:** `N` or `no`

**Your Response:**
```markdown
## ❌ Vacuum Cancelled

No files were modified. Architecture protection rules were updated for future use.

**Tip:** To see what would be cleaned without confirmation, use: `vacuum --dry-run`
```

---

## ⚠️ Error Handling

### **Epic Not Found**
```markdown
⚠️ **Warning:** Active CORTEX 6 epic not found at expected path.

Falling back to static protection rules from `cortex-brain/brain-protection-rules.yaml`.

**Note:** Real-time architecture awareness disabled. Consider verifying epic path.
```

### **No AC-IDs Found**
```markdown
⚠️ **Warning:** No acceptance criteria (AC-IDs) found in epic documents.

Using standard Vacuum protection rules. New features may not be automatically protected.
```

### **MCP Connection Failed**
```markdown
❌ **Error:** Cannot connect to Vacuum Orchestrator via MCP.

**Troubleshooting:**
1. Verify Python environment: `python3 -m src.main --version`
2. Check Vacuum Orchestrator: `python3 -m src.orchestrators.vacuum.vacuum_orchestrator_v2 --help`
3. Review logs: `cortex-brain/logs/vacuum-orchestrator.log`
```

---

## 🧠 Learning & Adaptation

### **After Each Run:**

1. **Store Architecture Snapshot**
   ```python
   snapshot = {
       'timestamp': datetime.now().isoformat(),
       'ac_ids': list(protected_ac_ids),
       'protected_paths': list(protected_paths),
       'consolidation_map': consolidation_map,
       'files_cleaned': cleanup_stats
   }
   
   save_to_knowledge_graph(snapshot)
   ```

2. **Update Protection Patterns**
   ```python
   # Learn from what was protected
   for path in protected_paths:
       pattern = extract_pattern(path)
       add_to_learned_patterns(pattern, reason="architecture_protection")
   ```

3. **Track Consolidation Progress**
   ```python
   # Monitor consolidation completion
   for old_path, new_path in consolidation_map.items():
       if not exists(old_path):
           mark_consolidation_complete(old_path, new_path)
   ```

---

## 📋 Checklist for Every Invocation

- [ ] **Step 1:** Parse user request (extract folder/scope)
- [ ] **Step 2:** Read CORTEX 6 epic (`cortex-brain/documents/planning/active/cortex6/acceptance-criteria/`)
- [ ] **Step 3:** Extract AC-IDs and component paths
- [ ] **Step 4:** Build protection map (architecture + static rules)
- [ ] **Step 5:** Detect consolidation patterns
- [ ] **Step 6:** Display scope and protection rules to user
- [ ] **Step 7:** Wait for user approval (Y/N)
- [ ] **Step 8:** If approved, invoke Vacuum Orchestrator via MCP
- [ ] **Step 9:** Display results with protection/cleanup stats
- [ ] **Step 10:** Store architecture snapshot in knowledge graph

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

## 📚 References

- **Vacuum Orchestrator v2:** `src/orchestrators/vacuum/vacuum_orchestrator_v2.py`
- **Vacuum Config:** `cortex-brain/manifests/orchestrators/vacuum-orchestrator-v2.yaml`
- **Phase 0 Spec:** `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/CX6-vacuum-phase-0-enhancement.md`
- **CORTEX 6 Epic:** `cortex-brain/documents/planning/active/cortex6/`
- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Master Orchestrator:** `.github/prompts/CORTEX.prompt.md`

---

**Version History:**
- v1.0.0: Initial architecture-aware vacuum prompt with real-time adaptation

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
