# 🛡️ Vacuum Orchestrator Phase 0: Architecture-Aware Intelligence Gathering

**Version:** 1.0.0 | **Status:** 📋 SPECIFICATION  
**Author:** Asif Hussain | **Date:** 2026-01-09  
**Epic:** CORTEX 6.0 | **Priority:** P1  
**Acceptance Criteria:** AC-VACUUM-PHASE0-001

---

## 🎯 Purpose

**Problem:** Current Vacuum Orchestrator lacks architectural awareness - it cannot distinguish between:
- ✅ New unified features (e.g., CORTEX Toolkit) vs ❌ old scattered implementations
- ✅ Active development areas vs ❌ obsolete code
- ✅ Consolidated modules vs ❌ duplicates that should be removed

**Solution:** Add **Phase 0: Architecture-Aware Pre-Scan** that reads active CORTEX 6 epic to build intelligent protection rules BEFORE cleanup begins.

---

## 📋 User Request (Original)

> "Update the vacuum orchestrator as its first step to review the folder being asked to vacuum and traverse it recursively to update itself with the new structures so it builds intelligence to not delete, what to consolidate for newly implemented features."

**Clarification:**
- ❌ NOT time-based criteria ("files modified in last N days")
- ✅ Architecture-based criteria ("components specified in active CORTEX 6 epic acceptance criteria")

---

## 🏗️ Architecture-Aware Criteria (APPROVED)

### **Source of Truth:**
`/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/planning/active/cortex6/`

### **Intelligence Sources:**
1. **Epic Documents:**
   - `CX6-planning-orchestrator-workflow-v3.md` - Planning orchestrator spec with CORTEX Toolkit
   - `ARCHITECTURE-ANALYSIS-AND-RECOMMENDATIONS.md` - Architectural decisions
   - `acceptance-criteria/*.md` - All AC-* files with component specifications

2. **Acceptance Criteria AC-IDs:**
   - `AC-PLAN-TOOLKIT-001` - CORTEX Toolkit (`src/toolkit/`)
   - `AC-PLAN-MCP-001` - MCP Toolkit Server (`src/mcp/toolkit_server.py`)
   - `AC-REALIGN-001` - Realignment Orchestrator (`src/orchestrators/realignment_orchestrator.py`)
   - `AC-PLAN-AST-001` - AST Parser (`src/toolkit/ast_parser.py`)
   - And all other AC-* identifiers

3. **Implementation Roadmap:**
   - Phase 1: CORTEX Toolkit Foundation (24-32h)
   - Phase 2: MCP Server (16-20h)
   - Phase 3: Orchestrator Refactoring (32-40h)
   - Phase 4: Realignment Orchestrator (20-28h)

---

## 🔄 Enhanced Vacuum Workflow (v3.0)

### **Current Workflow (6 Phases):**
```
Phase 1: DISCOVERY       → Filesystem traversal
Phase 2: ANALYSIS        → Duplicate detection
Phase 3: PLANNING        → Safety validation
Phase 4: APPROVAL        → Dry-run/confirmation
Phase 5: EXECUTION       → Cleanup operations
Phase 6: COMPLETION      → Report generation
```

### **NEW Workflow (7 Phases):**
```
Phase 0: ARCHITECTURE INTELLIGENCE  ← NEW: Pre-scan with epic analysis
Phase 1: DISCOVERY                  → Filesystem traversal
Phase 2: ANALYSIS                   → Duplicate detection
Phase 3: PLANNING                   → Safety validation
Phase 4: APPROVAL                   → Dry-run/confirmation
Phase 5: EXECUTION                  → Cleanup operations
Phase 6: COMPLETION                 → Report generation
```

---

## 📊 Phase 0 Specification: Architecture-Aware Pre-Scan

### **Phase 0.1: Epic Discovery**
**Action:** Locate active CORTEX 6 epic folder  
**Path:** `cortex-brain/documents/planning/active/cortex6/`  
**Output:** List of epic documents to parse

**Pseudocode:**
```python
def discover_active_epic():
    epic_path = Path("cortex-brain/documents/planning/active/cortex6")
    
    if not epic_path.exists():
        logger.warning("No active epic found - skipping architecture intelligence")
        return None
    
    return {
        'epic_path': epic_path,
        'workflow_docs': list(epic_path.glob("**/CX6-*.md")),
        'acceptance_criteria': list(epic_path.glob("acceptance-criteria/*.md")),
        'architecture_docs': list(epic_path.glob("**/ARCHITECTURE-*.md"))
    }
```

---

### **Phase 0.2: Acceptance Criteria Parsing**
**Action:** Extract AC-IDs and component paths from epic documents  
**Parser:** Markdown parser with AC-ID regex pattern  
**Output:** Protection map with AC-ID → Component mappings

**AC-ID Pattern:** `AC-[A-Z]+-[A-Z0-9]+-\d{3}`

**Example Extraction:**
```markdown
# From CX6-planning-orchestrator-workflow-v3.md:

"CORTEX Toolkit (AC-PLAN-TOOLKIT-001) in src/toolkit/"
→ PROTECT: src/toolkit/** (AC-PLAN-TOOLKIT-001)

"MCP Toolkit Server (AC-PLAN-MCP-001) at src/mcp/toolkit_server.py"
→ PROTECT: src/mcp/toolkit_server.py (AC-PLAN-MCP-001)

"Realignment Orchestrator (AC-REALIGN-001) in src/orchestrators/realignment_orchestrator.py"
→ PROTECT: src/orchestrators/realignment_orchestrator.py (AC-REALIGN-001)
```

**Pseudocode:**
```python
def parse_acceptance_criteria(epic_docs):
    protection_map = {}
    ac_id_pattern = r'AC-[A-Z]+-[A-Z0-9]+-\d{3}'
    
    for doc in epic_docs:
        content = doc.read_text()
        
        # Find all AC-IDs with surrounding context
        matches = re.finditer(
            r'([^\n]+)(' + ac_id_pattern + r')([^\n]+)',
            content
        )
        
        for match in matches:
            context = match.group(0)
            ac_id = match.group(2)
            
            # Extract file paths from context
            paths = extract_paths_from_context(context)
            
            for path in paths:
                protection_map[path] = {
                    'ac_id': ac_id,
                    'reason': context.strip(),
                    'source': doc.name
                }
    
    return protection_map
```

---

### **Phase 0.3: Consolidation Pattern Detection**
**Action:** Identify "old scattered → new unified" migrations  
**Method:** Cross-reference epic roadmap with codebase  
**Output:** Consolidation mappings (old → new)

**Detection Logic:**
```python
def detect_consolidation_patterns(protection_map, codebase_root):
    consolidation_map = {}
    
    # Identify unified systems from protection map
    unified_systems = {
        'src/toolkit/': 'CORTEX Toolkit (AC-PLAN-TOOLKIT-001)'
    }
    
    for unified_path, description in unified_systems.items():
        # Find potential scattered implementations
        toolkit_tools = [
            'semantic_search', 'ast_parser', 'git_analyzer',
            'knowledge_graph', 'pattern_detector', 'dependency_mapper',
            'duplicate_detector', 'orphan_detector'
        ]
        
        for tool in toolkit_tools:
            # Search for old scattered implementations
            old_versions = find_scattered_implementations(
                codebase_root, 
                tool,
                exclude=unified_path
            )
            
            for old_path in old_versions:
                new_path = f"{unified_path}{tool}.py"
                
                consolidation_map[str(old_path)] = {
                    'new_path': new_path,
                    'status': 'superseded',
                    'action': 'flag_for_review',
                    'unified_system': description
                }
    
    return consolidation_map
```

**Example Output:**
```yaml
consolidation_mappings:
  - old: src/orchestrators/planning/ast_scanner.py
    new: src/toolkit/ast_parser.py
    status: superseded
    action: flag_for_review
    unified_system: CORTEX Toolkit (AC-PLAN-TOOLKIT-001)
  
  - old: src/orchestrators/vacuum/duplicate_detector.py
    new: src/toolkit/duplicate_detector.py
    status: superseded
    action: flag_for_review
    unified_system: CORTEX Toolkit (AC-PLAN-TOOLKIT-001)
```

---

### **Phase 0.4: Active Dependency Analysis**
**Action:** Identify files actively importing from protected components  
**Method:** AST-based import analysis  
**Output:** Extended protection map with dependency chains

**Pseudocode:**
```python
def analyze_active_dependencies(protection_map, codebase_root):
    dependency_map = {}
    
    for protected_path in protection_map.keys():
        # Find all files importing from protected component
        importers = find_importers(codebase_root, protected_path)
        
        for importer in importers:
            dependency_map[str(importer)] = {
                'depends_on': protected_path,
                'reason': f'Active import from {protected_path}',
                'protection_level': 'dependency'
            }
    
    return dependency_map
```

**Example:**
```yaml
protection_rules:
  - pattern: src/orchestrators/planning_orchestrator_v5.py
    reason: "Active import from src/toolkit/ (AC-PLAN-TOOLKIT-001 dependency)"
    protection_level: dependency
```

---

### **Phase 0.5: Protection Rule Generation**
**Action:** Generate dynamic protection rules for Vacuum phases  
**Format:** YAML rules compatible with `vacuum-orchestrator-v2.yaml`  
**Output:** Runtime protection rules

**Generated Rules Structure:**
```yaml
runtime_protection_rules:
  architecture_based:
    - pattern: "src/toolkit/**"
      reason: "AC-PLAN-TOOLKIT-001 - New unified modular system"
      source: "CX6-planning-orchestrator-workflow-v3.md"
      priority: 100  # Highest protection
    
    - pattern: "src/mcp/toolkit_server.py"
      reason: "AC-PLAN-MCP-001 - MCP exposure layer"
      source: "acceptance-criteria/..."
      priority: 100
    
    - pattern: "src/orchestrators/realignment_orchestrator.py"
      reason: "AC-REALIGN-001 - Realignment orchestrator"
      source: "acceptance-criteria/..."
      priority: 100
  
  dependency_based:
    - pattern: "src/orchestrators/planning_orchestrator_v5.py"
      reason: "Active dependency - imports from src/toolkit/"
      source: "AST analysis"
      priority: 90
  
  consolidation_candidates:
    - pattern: "src/orchestrators/planning/ast_scanner.py"
      action: "flag_for_review"
      reason: "Superseded by src/toolkit/ast_parser.py (AC-PLAN-TOOLKIT-001)"
      status: "consolidation_candidate"
      priority: 10  # Low protection (safe to remove after migration)
    
    - pattern: "src/orchestrators/vacuum/duplicate_detector.py"
      action: "flag_for_review"
      reason: "Superseded by src/toolkit/duplicate_detector.py (AC-PLAN-TOOLKIT-001)"
      status: "consolidation_candidate"
      priority: 10
```

**Pseudocode:**
```python
def generate_protection_rules(protection_map, consolidation_map, dependency_map):
    rules = {
        'architecture_based': [],
        'dependency_based': [],
        'consolidation_candidates': []
    }
    
    # Architecture-based protection (highest priority)
    for path, metadata in protection_map.items():
        rules['architecture_based'].append({
            'pattern': path,
            'reason': metadata['reason'],
            'source': metadata['source'],
            'ac_id': metadata['ac_id'],
            'priority': 100
        })
    
    # Dependency-based protection
    for path, metadata in dependency_map.items():
        rules['dependency_based'].append({
            'pattern': path,
            'reason': metadata['reason'],
            'priority': 90
        })
    
    # Consolidation candidates (low priority)
    for old_path, metadata in consolidation_map.items():
        rules['consolidation_candidates'].append({
            'pattern': old_path,
            'action': 'flag_for_review',
            'reason': f"Superseded by {metadata['new_path']} ({metadata['unified_system']})",
            'status': 'consolidation_candidate',
            'priority': 10
        })
    
    return rules
```

---

### **Phase 0.6: Knowledge Graph Integration**
**Action:** Store intelligence in CORTEX knowledge graph  
**Location:** `cortex-brain/tier2/knowledge-graph.db`  
**Output:** Persistent architectural knowledge for future orchestrators

**Knowledge Entities:**
```python
def store_architecture_intelligence(rules, knowledge_graph):
    # Store protected components
    for rule in rules['architecture_based']:
        knowledge_graph.add_entity(
            entity_type='protected_component',
            entity_id=rule['ac_id'],
            attributes={
                'path': rule['pattern'],
                'reason': rule['reason'],
                'source': rule['source'],
                'priority': rule['priority']
            }
        )
    
    # Store consolidation mappings
    for candidate in rules['consolidation_candidates']:
        knowledge_graph.add_relationship(
            source=candidate['pattern'],
            target=extract_new_path(candidate['reason']),
            relationship_type='superseded_by',
            metadata={
                'status': candidate['status'],
                'action': candidate['action']
            }
        )
```

---

## 🎯 Integration with Existing Phases

### **Phase 1: DISCOVERY (Enhanced)**
**Before Phase 0:**
```python
def phase_discovery():
    # Simple filesystem traversal
    files = traverse_recursively(target_path)
    categorize_files(files)
```

**After Phase 0:**
```python
def phase_discovery():
    # Check runtime protection rules FIRST
    protected_paths = get_runtime_protection_rules()
    
    files = traverse_recursively(
        target_path,
        exclude=protected_paths  # Skip protected components
    )
    
    categorize_files(files, consolidation_map)
```

---

### **Phase 3: PLANNING (Enhanced)**
**Before Phase 0:**
```python
def phase_planning():
    # Static safety rules from config
    validate_against_static_rules(cleanup_candidates)
```

**After Phase 0:**
```python
def phase_planning():
    # Dynamic + static rules
    static_rules = load_static_safety_rules()
    runtime_rules = get_runtime_protection_rules()
    
    all_rules = merge_rules(static_rules, runtime_rules)
    
    validate_against_all_rules(cleanup_candidates, all_rules)
    
    # Flag consolidation candidates separately
    consolidation_report = generate_consolidation_report()
```

---

## 📊 Example Scenario: CORTEX Toolkit Protection

### **Input:**
User runs: `vacuum src/orchestrators/`

### **Phase 0 Execution:**

**Step 1: Epic Discovery**
```
✅ Found active epic: cortex-brain/documents/planning/active/cortex6/
✅ Parsing: CX6-planning-orchestrator-workflow-v3.md
✅ Parsing: ARCHITECTURE-ANALYSIS-AND-RECOMMENDATIONS.md
✅ Parsing: acceptance-criteria/*.md
```

**Step 2: AC Extraction**
```
✅ AC-PLAN-TOOLKIT-001 → src/toolkit/** (New unified modular system)
✅ AC-PLAN-MCP-001 → src/mcp/toolkit_server.py (MCP exposure)
✅ AC-REALIGN-001 → src/orchestrators/realignment_orchestrator.py (Realignment orchestrator)
```

**Step 3: Consolidation Detection**
```
⚠️  Detected scattered implementation:
   src/orchestrators/planning/ast_scanner.py
   → Superseded by: src/toolkit/ast_parser.py (AC-PLAN-TOOLKIT-001)
   → Action: FLAG_FOR_REVIEW

⚠️  Detected scattered implementation:
   src/orchestrators/vacuum/duplicate_detector.py
   → Superseded by: src/toolkit/duplicate_detector.py (AC-PLAN-TOOLKIT-001)
   → Action: FLAG_FOR_REVIEW
```

**Step 4: Dependency Analysis**
```
✅ src/orchestrators/planning_orchestrator_v5.py
   → Imports from: src/toolkit/
   → Protection: DEPENDENCY_BASED
```

**Step 5: Generated Rules**
```yaml
runtime_protection_rules:
  architecture_based:
    - src/toolkit/**                               # Priority 100
    - src/mcp/toolkit_server.py                   # Priority 100
    - src/orchestrators/realignment_orchestrator.py  # Priority 100
  
  dependency_based:
    - src/orchestrators/planning_orchestrator_v5.py  # Priority 90
  
  consolidation_candidates:
    - src/orchestrators/planning/ast_scanner.py      # Priority 10
    - src/orchestrators/vacuum/duplicate_detector.py # Priority 10
```

### **Phase 1-6 Execution (With Phase 0 Intelligence):**

**Phase 1: DISCOVERY**
```
Scanning: src/orchestrators/
✅ Skipped: src/toolkit/** (AC-PLAN-TOOLKIT-001 protection)
✅ Skipped: src/mcp/toolkit_server.py (AC-PLAN-MCP-001 protection)
✅ Skipped: realignment_orchestrator.py (AC-REALIGN-001 protection)
✅ Skipped: planning_orchestrator_v5.py (dependency protection)
⚠️  Flagged: ast_scanner.py (consolidation candidate - review before removal)
⚠️  Flagged: duplicate_detector.py (consolidation candidate - review before removal)
```

**Phase 4: APPROVAL (Dry-Run Report)**
```markdown
## Protected Components (Architecture-Based)
- ✅ src/toolkit/** (AC-PLAN-TOOLKIT-001)
- ✅ src/mcp/toolkit_server.py (AC-PLAN-MCP-001)
- ✅ src/orchestrators/realignment_orchestrator.py (AC-REALIGN-001)

## Consolidation Candidates (Review Required)
- ⚠️ src/orchestrators/planning/ast_scanner.py
  - Superseded by: src/toolkit/ast_parser.py
  - Recommendation: Remove after migration validation

- ⚠️ src/orchestrators/vacuum/duplicate_detector.py
  - Superseded by: src/toolkit/duplicate_detector.py
  - Recommendation: Remove after migration validation
```

---

## 📋 Implementation Checklist

**Phase 0.1: Epic Discovery**
- [ ] Implement `discover_active_epic()` method
- [ ] Handle missing epic gracefully (skip Phase 0)
- [ ] Test with CORTEX 6 epic folder

**Phase 0.2: AC Parsing**
- [ ] Implement `parse_acceptance_criteria()` method
- [ ] Regex pattern: `AC-[A-Z]+-[A-Z0-9]+-\d{3}`
- [ ] Extract file paths from AC context
- [ ] Test with CX6-planning-orchestrator-workflow-v3.md

**Phase 0.3: Consolidation Detection**
- [ ] Implement `detect_consolidation_patterns()` method
- [ ] Hardcode CORTEX Toolkit tools list (8 tools)
- [ ] Search for scattered implementations
- [ ] Test with src/orchestrators/ folder

**Phase 0.4: Dependency Analysis**
- [ ] Implement `analyze_active_dependencies()` method
- [ ] AST-based import finder
- [ ] Test with planning_orchestrator_v5.py imports

**Phase 0.5: Rule Generation**
- [ ] Implement `generate_protection_rules()` method
- [ ] 3-tier priority system (100, 90, 10)
- [ ] YAML-compatible output
- [ ] Test rule merging with static rules

**Phase 0.6: Knowledge Graph Integration**
- [ ] Implement `store_architecture_intelligence()` method
- [ ] Knowledge graph schema updates
- [ ] Test persistence and retrieval

**Integration:**
- [ ] Update `vacuum_orchestrator_v2.py` execute() method
- [ ] Add Phase 0 before Phase 1
- [ ] Pass runtime_rules to all phases
- [ ] Update dry-run report template

**Testing:**
- [ ] Unit tests for each Phase 0 method
- [ ] Integration test with CORTEX 6 epic
- [ ] Test consolidation candidate detection
- [ ] Test protection rule enforcement

**Documentation:**
- [ ] Update `vacuum-orchestrator-v2.yaml` manifest
- [ ] Add Phase 0 section to workflow docs
- [ ] Update dry-run report template
- [ ] Add example scenarios

---

## 🎯 Acceptance Criteria

**AC-VACUUM-PHASE0-001: Architecture-Aware Pre-Scan**
- [x] Phase 0 executes before Phase 1 (discovery)
- [ ] Reads active CORTEX 6 epic from `cortex-brain/documents/planning/active/cortex6/`
- [ ] Extracts AC-IDs and component paths from epic documents
- [ ] Generates protection rules (architecture-based, dependency-based, consolidation candidates)
- [ ] Runtime rules merged with static safety rules
- [ ] Protected components skipped in Phase 1 (discovery)
- [ ] Consolidation candidates flagged in dry-run report
- [ ] Knowledge graph stores architectural intelligence
- [ ] No false positives (legitimate new features NOT flagged for deletion)
- [ ] No false negatives (obsolete scattered implementations FLAGGED)

**AC-VACUUM-PHASE0-002: Consolidation Pattern Detection**
- [ ] Detects CORTEX Toolkit as unified system
- [ ] Identifies scattered implementations (ast_scanner.py, duplicate_detector.py, etc.)
- [ ] Maps old → new paths
- [ ] Flags consolidation candidates with action: `flag_for_review`
- [ ] Dry-run report shows consolidation recommendations

**AC-VACUUM-PHASE0-003: Dependency Protection**
- [ ] AST-based import analysis
- [ ] Files importing from protected components also protected
- [ ] Transitive dependency detection (1 level deep minimum)

---

## 🚀 Implementation Estimate

**Effort:** 16-24 hours (2-3 days)

**Breakdown:**
- Phase 0.1: Epic Discovery (2h)
- Phase 0.2: AC Parsing (4h)
- Phase 0.3: Consolidation Detection (4h)
- Phase 0.4: Dependency Analysis (3h)
- Phase 0.5: Rule Generation (2h)
- Phase 0.6: Knowledge Graph Integration (3h)
- Integration with Vacuum Phases (4h)
- Testing (6h)
- Documentation (2h)

---

## 📚 References

- **CORTEX 6 Epic:** `cortex-brain/documents/planning/active/cortex6/`
- **Vacuum v2 Orchestrator:** `src/orchestrators/vacuum/vacuum_orchestrator_v2.py`
- **Vacuum Config:** `cortex-brain/manifests/orchestrators/vacuum-orchestrator-v2.yaml`
- **Planning Workflow v3:** `CX6-planning-orchestrator-workflow-v3.md`
- **Architecture Analysis:** `ARCHITECTURE-ANALYSIS-AND-RECOMMENDATIONS.md`

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
