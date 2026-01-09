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

### **Step 2.5: Document Consolidation Detection (NEW)**

**After architecture discovery, scan for consolidation patterns:**

```markdown
## 📦 Document Consolidation Analysis

Analyzing acceptance-criteria directory for version progression and duplicate summaries...
```

**Actions:**
1. **Detect Version Progressions:**
   ```python
   # Pattern: base-name-vX.ext files
   version_groups = group_by_base_name(files, pattern=r"(.*)-v(\d+)\..*")
   ```

2. **Detect Summary Duplicates:**
   ```python
   # Pattern: *-SUMMARY.md, *-UPDATE-*.md, *-IMPLEMENTATION-*.md
   summary_files = filter(files, patterns=[
       r".*-SUMMARY\.md$",
       r".*-UPDATE-v[\d.]+.*\.md$",
       r".*-IMPLEMENTATION-.*\.md$"
   ])
   ```

3. **Analyze Content Overlap:**
   ```python
   for group in consolidation_candidates:
       overlap = calculate_content_overlap(group['files'])
       unique_content = extract_unique_sections(group['files'])
       
       if overlap > 70% or is_version_progression(group):
           flag_for_consolidation(group, unique_content)
   ```

4. **Display Consolidation Report:**
   ```markdown
   ### 📦 Consolidation Opportunities:
   
   **Group 1: Planning Orchestrator Workflow**
   - Files: CX6-planning-orchestrator-workflow.md (v6.0, 1200 lines)
           CX6-planning-orchestrator-workflow-v3.md (v3.0, 709 lines)
   - Overlap: 60% (shared workflow structure)
   - Unique in v3: CORTEX Toolkit spec, Realignment integration
   - **Recommendation:** Merge v3 innovations into v6.0 as version history
   - **Impact:** 1 consolidated file, 1 archived, ~700 lines deduplicated
   
   **Group 2: Acceptance Criteria Updates**
   - Files: CX6-AC-UPDATE-v14.4.0-CORRECTED-SUMMARY.md (256 lines)
           CX6-AC-UPDATE-v15.0.0-SUMMARY.md (504 lines)
   - Overlap: 0% (sequential updates)
   - Unique in each: Different AC additions (v14: planning structure, v15: alignment system)
   - **Recommendation:** Convert to YAML changelog in CX6-acceptance-criteria.yaml
   - **Impact:** 2 summaries archived, info preserved as structured data
   
   **Group 3: Implementation Summaries**
   - Files: WORKFLOW-V3-UPDATE-SUMMARY.md (241 lines)
           VACUUM-PROMPT-IMPLEMENTATION-SUMMARY.md (347 lines)
           GAP-FIX-IMPLEMENTATION-PLAN.md (645 lines)
   - **Recommendation:** Extract metadata → merge into parent docs → archive
   - **Impact:** 3 summaries archived, cleaner directory structure
   
   **Total Consolidation Potential:**
   - 7 files → 3 enhanced files + 4 archived
   - ~2000 lines of duplicate content eliminated
   - 100% data preservation (archive/ keeps originals)
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

### 📦 Consolidation Opportunities (Will MERGE + ARCHIVE):
**Group 1: Planning Orchestrator Workflow**
- Merge: CX6-planning-orchestrator-workflow-v3.md → CX6-planning-orchestrator-workflow.md
- Result: v3 innovations added as version history section
- Archive: v3 file moved to archive/

**Group 2: Acceptance Criteria Updates**
- Merge: 2 update summaries → CX6-acceptance-criteria.yaml (changelog header)
- Result: Structured version history in YAML
- Archive: v14 + v15 summaries moved to archive/

**Group 3: Implementation Summaries**
- Merge: WORKFLOW-V3-UPDATE-SUMMARY.md → parent doc
- Merge: VACUUM-PROMPT-IMPLEMENTATION-SUMMARY.md → parent doc
- Archive: Both summaries moved to archive/

**Consolidation Impact:**
- 📦 5 files archived (100% data preserved)
- ✅ 3 files enhanced with consolidated content
- 💾 ~2KB reduction (duplicate content eliminated)
- 🎯 Cleaner directory structure

### Consolidation Candidates (Will be FLAGGED for review):
- ⚠️ {old_path_1} → {new_path_1}
- ⚠️ {old_path_2} → {new_path_2}

### Standard Cleanup Targets:
- 🗑️ Temporary files (*.tmp, *.temp)
- 🗑️ Build artifacts (__pycache__, *.pyc, .pytest_cache)
- 🗑️ Duplicate files (hash-based detection)
- 🗑️ Empty directories
- 🗑️ Log files (*.log older than 7 days)

**Proceed with vacuum + consolidation? (Y/N)**
```

**Wait for user approval.**

---

### **Step 4: Execute Consolidation (If User Approved)**

**BEFORE invoking Vacuum Orchestrator, perform consolidation:**

```python
# Phase 1: Create consolidated files
consolidation_results = []

for group in consolidation_plan:
    try:
        # 1. Read base file
        base_content = read_file(group['base_file'])
        
        # 2. Extract unique content from merge sources
        enhancements = []
        for merge_source in group['merge_from']:
            unique_sections = extract_unique_content(
                source=merge_source['file'],
                base=group['base_file'],
                extract_rules=merge_source['extract']
            )
            enhancements.append({
                'source': merge_source['file'],
                'content': unique_sections
            })
        
        # 3. Create consolidated content (intelligent merge)
        if group['action'] == 'merge_with_changelog':
            consolidated = add_version_history_section(
                base=base_content,
                enhancements=enhancements
            )
        elif group['action'] == 'merge_to_yaml_header':
            consolidated = add_yaml_changelog(
                base=base_content,
                updates=enhancements
            )
        else:
            consolidated = smart_merge(base_content, enhancements)
        
        # 4. Write consolidated file
        write_file(group['base_file'], consolidated)
        
        # 5. Archive old files (NOT delete)
        for old_file in group['archive']:
            timestamp = datetime.now().strftime('%Y-%m-%d')
            archive_path = f"archive/{old_file.stem}-{timestamp}{old_file.suffix}"
            move_file(old_file, archive_path)
        
        consolidation_results.append({
            'group': group['group'],
            'status': 'success',
            'archived': len(group['archive']),
            'enhancements_merged': len(enhancements)
        })
        
    except Exception as e:
        consolidation_results.append({
            'group': group['group'],
            'status': 'failed',
            'error': str(e)
        })

# Phase 2: Display consolidation results
print("## 📦 Consolidation Complete\n")
for result in consolidation_results:
    if result['status'] == 'success':
        print(f"✅ {result['group']}: {result['archived']} files archived, "
              f"{result['enhancements_merged']} enhancements merged")
    else:
        print(f"❌ {result['group']}: FAILED - {result['error']}")
```

---

### **Step 5: Invoke Vacuum Orchestrator via MCP**

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

## � Intelligent File Consolidation

### **Phase 0.5: Document Consolidation Detection**

**CRITICAL:** When multiple versions/summaries exist, consolidate WITHOUT data loss.

### **Consolidation Patterns:**

#### **Pattern 1: Version Progression Files**

**Detect:**
- `filename-v1.md` + `filename-v2.md` + `filename-v3.md`
- `*-UPDATE-v14.*.md` + `*-UPDATE-v15.*.md`
- Same base name with version suffixes

**Action:**
```markdown
### Consolidation Plan:

**Files Detected:**
- CX6-planning-orchestrator-workflow.md (v6.0, 1200 lines)
- CX6-planning-orchestrator-workflow-v3.md (v3.0, 709 lines)

**Strategy:** Create unified changelog + keep latest version ONLY

**New Structure:**
```yaml
# CX6-planning-orchestrator-workflow.md (CONSOLIDATED)
version: 6.0.0
status: CURRENT

# Version History section (embedded changelog)
changelog:
  - version: 6.0.0
    date: 2026-01-09
    changes: ["Initial 4-phase workflow design"]
  - version: 3.0.0
    date: 2026-01-09
    changes: ["Added CORTEX Toolkit", "Added Realignment orchestrator"]
```

**Outcome:**
- ✅ Keep: `CX6-planning-orchestrator-workflow.md` (enhanced with v3 innovations)
- 🗑️ Archive: `CX6-planning-orchestrator-workflow-v3.md` → `archive/workflow-v3-2026-01-09.md`
```

#### **Pattern 2: Summary/Implementation Files**

**Detect:**
- `*-SUMMARY.md` (describes what was done)
- `*-IMPLEMENTATION-PLAN.md` (describes what to do)
- Redundant update summaries

**Action:**
```markdown
### Consolidation Plan:

**Files Detected:**
- WORKFLOW-V3-UPDATE-SUMMARY.md (241 lines) - "What was updated in v3"
- VACUUM-PROMPT-IMPLEMENTATION-SUMMARY.md (347 lines) - "What vacuum prompt does"
- CX6-AC-UPDATE-v14.4.0-CORRECTED-SUMMARY.md (256 lines)
- CX6-AC-UPDATE-v15.0.0-SUMMARY.md (504 lines)

**Strategy:** Convert to structured changelog in main documents

**For Planning Workflow:**
- ✅ Extract v3 changes from WORKFLOW-V3-UPDATE-SUMMARY.md
- ✅ Merge into CX6-planning-orchestrator-workflow.md as "## Version History"
- 🗑️ Archive: WORKFLOW-V3-UPDATE-SUMMARY.md

**For Acceptance Criteria Updates:**
- ✅ Merge v14 + v15 summaries into CX6-acceptance-criteria.yaml header
- ✅ Add `changelog:` section at top of YAML
- 🗑️ Archive: Both update summary files

**Outcome:**
- Information preserved in canonical locations
- No orphaned summaries
- Clear version history embedded in source documents
```

#### **Pattern 3: Duplicate Base Names**

**Detect:**
- Multiple files with same semantic purpose but different names
- `README.md` + `00-INDEX.md` (both serve as index)
- `ARCHITECTURE-*.md` duplicates

**Action:**
```markdown
### Consolidation Plan:

**Files Detected:**
- 00-INDEX.md (382 lines) - "Quick reference guide"
- README.md (unknown lines) - Potential duplicate

**Strategy:** Merge into single authoritative index

**Decision Tree:**
1. Compare content overlap (>70% = consolidate)
2. Keep more comprehensive version
3. Extract unique sections from other
4. Archive redundant file

**Outcome:**
- ✅ Keep: 00-INDEX.md (more comprehensive)
- 🗑️ Archive: README.md (if redundant) OR enhance 00-INDEX with README content
```

### **Consolidation Execution Protocol:**

**Step 1: Detect Consolidation Opportunities**
```python
consolidation_candidates = detect_consolidation_patterns([
    "version_progression",  # v1, v2, v3 files
    "summary_duplicates",   # *-SUMMARY.md files
    "redundant_indexes",    # README + INDEX files
    "update_summaries"      # *-UPDATE-*.md files
])
```

**Step 2: Analyze Data Uniqueness**
```python
for group in consolidation_candidates:
    base_file = group['latest_version']
    older_files = group['older_versions']
    
    unique_content = {}
    for old_file in older_files:
        unique_sections = extract_unique_content(old_file, base_file)
        if unique_sections:
            unique_content[old_file] = unique_sections
```

**Step 3: Create Consolidation Plan**
```yaml
consolidation_plan:
  - group: "planning-orchestrator-workflow"
    action: "merge_with_changelog"
    base_file: "CX6-planning-orchestrator-workflow.md"
    merge_from:
      - file: "CX6-planning-orchestrator-workflow-v3.md"
        extract: ["CORTEX Toolkit section", "Realignment section"]
        destination: "## Version History → v3.0 innovations"
    archive:
      - "CX6-planning-orchestrator-workflow-v3.md"
  
  - group: "acceptance-criteria-updates"
    action: "merge_to_yaml_header"
    base_file: "CX6-acceptance-criteria.yaml"
    merge_from:
      - file: "CX6-AC-UPDATE-v14.4.0-CORRECTED-SUMMARY.md"
        extract: ["AC-ORC-002 correction", "Planning structure rules"]
      - file: "CX6-AC-UPDATE-v15.0.0-SUMMARY.md"
        extract: ["AC-ALIGN-001 to 005", "AC-DIGEST-001 to 006"]
    archive:
      - "CX6-AC-UPDATE-v14.4.0-CORRECTED-SUMMARY.md"
      - "CX6-AC-UPDATE-v15.0.0-SUMMARY.md"
```

**Step 4: Display Consolidation Preview**
```markdown
## 📦 Consolidation Opportunities Detected

### Group 1: Planning Orchestrator Workflow
- **Current:** CX6-planning-orchestrator-workflow.md (v6.0, 1200 lines)
- **Merge:** CX6-planning-orchestrator-workflow-v3.md (v3.0, 709 lines)
- **Strategy:** Extract v3 innovations → Add to v6.0 as version history
- **Result:** 1 consolidated file + 1 archived

### Group 2: Acceptance Criteria Updates
- **Current:** CX6-acceptance-criteria.yaml (237KB)
- **Merge:** 2 update summary files (v14, v15)
- **Strategy:** Convert summaries to YAML changelog header
- **Result:** Enhanced YAML + 2 summaries archived

### Group 3: Implementation Summaries
- **Files:** WORKFLOW-V3-UPDATE-SUMMARY.md, VACUUM-PROMPT-IMPLEMENTATION-SUMMARY.md
- **Strategy:** Extract key info → Merge into parent documents → Archive summaries
- **Result:** 2 files archived, info preserved in canonical locations

**Total Impact:**
- ✅ 5 files consolidated
- 📦 5 files archived (not deleted, safe in archive/)
- 💾 ~1.5MB preserved without duplication
- 🎯 Cleaner directory, zero data loss

**Approve consolidation? (Y/N)**
```

**Step 5: Execute Consolidation (User Approved)**
```python
def execute_consolidation(plan):
    for group in plan:
        # 1. Create enhanced base file
        enhanced_content = merge_with_preservation(
            base=group['base_file'],
            sources=group['merge_from']
        )
        
        # 2. Write consolidated file
        write_file(group['base_file'], enhanced_content)
        
        # 3. Archive old files (NOT delete)
        for old_file in group['archive']:
            archive_path = f"archive/{old_file.stem}-{today()}{old_file.suffix}"
            move_file(old_file, archive_path)
        
        # 4. Log consolidation
        log_consolidation(group, preserved=True)
```

### **Consolidation Rules:**

✅ **ALWAYS:**
- Extract ALL unique content before archiving
- Move to `archive/` (NEVER delete)
- Add changelog/version history to consolidated file
- Preserve metadata (dates, authors, AC-IDs)
- Log consolidation with data preservation audit trail

❌ **NEVER:**
- Delete files without archiving
- Lose unique information during merge
- Create "version dumps" (entire old file as text block)
- Break AC-ID references or links
- Consolidate files with >50% unique content

---

## �🛡️ Brain Protection Rules

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
- [ ] **Step 2.5:** Detect document consolidation opportunities (NEW)
- [ ] **Step 3:** Extract AC-IDs and component paths
- [ ] **Step 4:** Build protection map (architecture + static rules)
- [ ] **Step 5:** Detect code consolidation patterns (superseded implementations)
- [ ] **Step 6:** Display scope, protection rules, AND consolidation plan to user
- [ ] **Step 7:** Wait for user approval (Y/N)
- [ ] **Step 8:** If approved, execute document consolidation first
- [ ] **Step 9:** Then invoke Vacuum Orchestrator via MCP for cleanup
- [ ] **Step 10:** Display results with protection/cleanup/consolidation stats
- [ ] **Step 11:** Store architecture snapshot in knowledge graph

---

## 🎯 Success Criteria

**This prompt is working correctly if:**

✅ Every invocation scans CORTEX 6 epic before cleanup  
✅ New AC-IDs are automatically detected and protected  
✅ **Document consolidation patterns detected (version progressions, summaries)**  
✅ **Consolidation preserves 100% of unique content**  
✅ **Consolidated files enhanced with version history (NOT version dumps)**  
✅ **Old files archived (NOT deleted) for safety**  
✅ Consolidation candidates are flagged (not deleted)  
✅ User approval is required before any cleanup OR consolidation  
✅ Protected components are never deleted  
✅ Dry-run mode is used by default  
✅ Detailed reports are generated  
✅ Architecture snapshots are stored in knowledge graph  
✅ Real-time adaptation works (new features protected immediately)  
✅ No false positives (legitimate code NOT flagged for deletion)  
✅ **No data loss during consolidation (audit trail verifiable)**

---

## 📚 Examples of Good Consolidation

### ✅ Example 1: Version Progression with Changelog

**Before:**
```
CX6-planning-orchestrator-workflow.md (v6.0, 1200 lines)
CX6-planning-orchestrator-workflow-v3.md (v3.0, 709 lines)
```

**After Consolidation:**
```markdown
# CX6-planning-orchestrator-workflow.md

**Version:** 6.0.0  
**Status:** ✅ CURRENT

---

## Version History

### v6.0.0 (2026-01-09)
- Initial 4-phase interactive workflow design
- Config-based approval enforcement
- Zero-ambiguity plan validation

### v3.0.0 (2026-01-09) - MERGED FROM v3 DOCUMENT
- **Added:** CORTEX Toolkit architecture (8 modular tools)
- **Added:** Realignment Orchestrator integration
- **Added:** Centralized audit infrastructure
- **Reference:** See archive/workflow-v3-2026-01-09.md for full v3 spec

---

[Rest of v6.0 content...]
```

**Archived:**
```
archive/CX6-planning-orchestrator-workflow-v3-2026-01-09.md (full original preserved)
```

**✅ Result:** Clean version progression, all innovations captured, original archived

---

### ✅ Example 2: Update Summaries to YAML Changelog

**Before:**
```
CX6-AC-UPDATE-v14.4.0-CORRECTED-SUMMARY.md (256 lines)
CX6-AC-UPDATE-v15.0.0-SUMMARY.md (504 lines)
CX6-acceptance-criteria.yaml (237KB, no changelog)
```

**After Consolidation:**
```yaml
# CX6-acceptance-criteria.yaml

# Changelog
changelog:
  - version: "15.0.0"
    date: "2026-01-09"
    summary: "Holistic alignment system + Digest utility"
    new_ac_ids:
      - AC-ALIGN-001: "Holistic plan review triggers"
      - AC-ALIGN-002: "Complexity-based plan recreation"
      - AC-ALIGN-003: "Gap detection with remediation"
      - AC-DIGEST-001: "Universal file-to-YAML converter"
      - AC-DIGEST-002: "MCP server exposure"
    reference: "archive/CX6-AC-UPDATE-v15.0.0-SUMMARY-2026-01-09.md"
  
  - version: "14.4.0"
    date: "2026-01-09"
    summary: "Planning structure correction (AC-ORC-002 aligned)"
    corrections:
      - AC-ORC-002: "Corrected to match AC-ORC-PLAN-002 approved structure"
    new_ac_ids:
      - AC-ORC-PLAN-004: "CORTEX logo requirements (200x200px)"
    reference: "archive/CX6-AC-UPDATE-v14.4.0-CORRECTED-SUMMARY-2026-01-09.md"

# Acceptance Criteria
acceptance_criteria:
  [... existing AC ...]
```

**Archived:**
```
archive/CX6-AC-UPDATE-v14.4.0-CORRECTED-SUMMARY-2026-01-09.md
archive/CX6-AC-UPDATE-v15.0.0-SUMMARY-2026-01-09.md
```

**✅ Result:** Structured changelog, easy to parse, originals archived for reference

---

### ❌ Example of BAD Consolidation (DO NOT DO THIS)

**BAD - Version Dump:**
```markdown
# CX6-planning-orchestrator-workflow.md

[v6.0 content here...]

---

## APPENDIX: Full v3.0 Document

[ENTIRE 709-line v3 document pasted here verbatim]
```

**❌ Why This is BAD:**
- Massive file bloat (1200 + 709 = 1909 lines)
- Redundant information (v6 already supersedes v3)
- Hard to process (no clear structure)
- Defeats purpose of consolidation

**✅ Correct Approach:**
Extract v3 INNOVATIONS → Add to v6 as version history → Archive v3

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
- v1.1.0: Added intelligent document consolidation (version progressions, summaries)

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
