# Maintenance Phase 2 Cleanup Analysis

**Plan:** cleanup-v2-migration  
**Created:** January 2, 2026  
**Purpose:** Analyze current cleanup implementation for extraction

---

## 📍 Current Implementation Location

**Primary Orchestrator:**
- `src/plugins/cleanup_orchestrator.py` (577 lines)
- Status: PRODUCTION (actively used)
- Last Updated: November 11, 2025

**Maintenance Integration:**
- `.github/prompts/maintenance/phases/phase-00-cleanup-orchestrator.prompt.md`
- Invoked as Phase 0 of 11-phase maintenance pipeline
- Executes BEFORE other maintenance phases (clears bloat first)

**Configuration:**
- `cortex-brain/cleanup-rules.yaml` - YAML-based cleanup rules
- `cortex-brain/manifests/orchestrators/aggressive-cleanup-rules.yaml` - Additional rules manifest

---

## 🏗️ Current Architecture

### Class Structure

```python
class DynamicCleanupOrchestrator:
    """
    Dynamic cleanup orchestrator - performs fresh scans on every execution.
    
    Key Features:
    - YAML-based rules (no static lists)
    - Fresh workspace scanning at runtime
    - Multiple action types (delete_all, retain_recent, retain_days, archive)
    - Recursion protection (max depth: 15)
    - Safety validations (protected dirs, git status)
    - Rollback capability with manifests
    - Dry-run and live modes
    """
```

### Enums

1. **CleanupMode** - Execution mode
   - `LIVE` - Execute cleanup actions (only mode currently active)

2. **CleanupAction** - Action types
   - `DELETE_ALL` - Delete all matched items
   - `RETAIN_RECENT` - Keep N most recent, delete rest
   - `RETAIN_DAYS` - Keep files newer than N days
   - `ARCHIVE` - Move to archive directory
   - `REPORT` - Report only (no action)

3. **RiskLevel** - Risk assessment
   - `LOW` - Safe to delete (cache files)
   - `MEDIUM` - Moderate risk (logs, artifacts)
   - `HIGH` - High risk (requires validation)

### Data Structures

1. **CleanupItem** - Represents item to clean
   ```python
   @dataclass
   class CleanupItem:
       path: Path
       category: str
       action: CleanupAction
       size_bytes: int
       reason: str
       risk_level: RiskLevel
       metadata: Dict[str, Any]
   ```

2. **CleanupStats** - Execution statistics
   ```python
   @dataclass
   class CleanupStats:
       files_scanned: int
       files_deleted: int
       files_archived: int
       folders_deleted: int
       space_freed_bytes: int
       execution_time_seconds: float
       categories_processed: int
       errors: List[str]
       warnings: List[str]
   ```

---

## 🔧 Core Functionality

### 1. Rule Loading (`_load_rules`)
- Loads YAML rules from `cortex-brain/cleanup-rules.yaml`
- Falls back to default rules if file missing
- Validates rule structure

### 2. Protection System (`_load_protected_items`, `_is_protected`)
**Protected Directories:**
- `cortex-brain/tier{1,2,3}/*.db` - Brain databases
- `cortex-brain/lessons-learned.yaml`
- `cortex-brain/knowledge-graph.yaml`
- `cortex-brain/user-dictionary.yaml`
- `cortex-brain/documents/` - User content
- `.git/` - Git repository
- Active plan folders with `copilot_instructions`
- `named_templates` in response-templates-v4.yaml

**Protected Patterns:**
- Loaded from `cleanup-rules.yaml`
- Glob pattern matching
- Applied during scanning

### 3. Scanning Engine (`_safe_scan`, `scan_category`)
**Features:**
- Recursive glob pattern matching
- Max recursion depth protection (default: 15)
- Permission error handling
- Protected path filtering
- Statistics tracking

**Scan Flow:**
1. Parse category configuration
2. Iterate through path patterns
3. Perform glob matching (recursive or non-recursive)
4. Apply exclusion patterns
5. Calculate file/directory sizes
6. Create CleanupItem objects

### 4. Retention Policies (`apply_retention_policy`)

**DELETE_ALL:** Delete everything matched
- No filtering
- Immediate deletion

**RETAIN_RECENT:** Keep N most recent items
- Sort by modification time
- Keep `keep_count` items (configurable, default: 5)
- Delete rest

**RETAIN_DAYS:** Keep files newer than N days
- Calculate cutoff time (now - N days)
- Delete files older than cutoff

**ARCHIVE:** Move to archive directory
- Move items to `archive_to` location
- Preserve directory structure (optional)

### 5. Execution Engine (`execute`, `_execute_cleanup_actions`)

**Workflow:**
1. Reset statistics
2. Iterate through categories
3. Scan each category (fresh scan)
4. Apply retention policy
5. Add items to cleanup list
6. Execute cleanup actions (if LIVE mode)
7. Generate report
8. Save report to `cortex-brain/cleanup-reports/`

**Action Execution:**
- `_delete_item()` - Delete files/directories
- `_archive_item()` - Move to archive location
- Error handling with rollback capability

### 6. Reporting (`_generate_report`, `print_cleanup_report`)

**Report Structure:**
- Timestamp, mode, workspace root
- Statistics (files scanned/deleted/archived, space freed)
- Per-category summary
- Item details (first 50 items)
- Errors and warnings

**Output Formats:**
- JSON file (saved to `cortex-brain/cleanup-reports/`)
- Console output (formatted table)

---

## 📊 Current Cleanup Categories

Based on typical `cleanup-rules.yaml` structure:

1. **Python Caches** (Priority: HIGH)
   - `__pycache__/`, `*.pyc`, `*.pyo`
   - `.pytest_cache/`, `.mypy_cache/`, `.tox/`
   - `htmlcov/` (coverage reports)

2. **Build Artifacts** (Priority: MEDIUM)
   - `bin/`, `obj/`, `target/`, `build/`, `dist/`
   - `.egg-info/`, `.eggs/`

3. **Logs & Reports** (Priority: MEDIUM)
   - Large log files (>10MB)
   - Old reports (>30 days)
   - Cleanup reports (keep last 5)

4. **Temporary Files** (Priority: HIGH)
   - `*.tmp`, `.temp/`
   - Download caches

5. **Git Artifacts** (Priority: LOW)
   - Git garbage collection (`git gc`)
   - Prune unreachable objects
   - Optimize pack files

---

## 🔀 Integration Points

### Maintenance Pipeline Integration
**Location:** `.github/prompts/maintenance/phases/phase-00-cleanup-orchestrator.prompt.md`

**Execution:**
```powershell
python src/plugins/cleanup_orchestrator.py
```

**Success Criteria:**
- Exit code: 0
- Cleanup manifest generated
- Space freed ≥100MB (typical)
- All protected data intact

**Metrics Extracted:**
- Files deleted count
- Space freed (MB)
- Execution time
- Error count

### Command-Line Interface
**Direct Execution:**
```bash
python src/plugins/cleanup_orchestrator.py
```

**Always LIVE mode** (no dry-run in current implementation)

---

## ⚠️ Current Limitations

### 1. Standalone Orchestrator
- ❌ Not integrated with Master Orchestrator
- ❌ No pattern-based routing (via master-orchestrator.yaml)
- ❌ Invoked only through maintenance pipeline or CLI

### 2. State Management
- ❌ No state persistence in PlanningStateDB
- ❌ No session tracking
- ❌ No rollback beyond manifest (no state restoration)

### 3. Configuration
- ❌ No BaseOrchestrator v4.1 inheritance
- ❌ No config-driven execution (uses YAML but not manifest-based)
- ❌ No template rendering (prints to console directly)

### 4. User Interface
- ❌ No conversational mode
- ❌ No selective cleanup UI (must edit YAML or use CLI)
- ❌ No progress reporting during execution

### 5. Testing
- ❌ No comprehensive test suite
- ❌ No unit tests for category logic
- ❌ No integration tests with Master Orchestrator

---

## ✅ Strengths to Preserve

### 1. Dynamic Scanning
- ✅ Fresh scans on every execution (no stale data)
- ✅ YAML-based rules (easy to modify)
- ✅ No hardcoded file lists

### 2. Safety Features
- ✅ Protected directories/patterns
- ✅ Recursion protection (max depth: 15)
- ✅ Risk level classification
- ✅ Permission error handling

### 3. Flexibility
- ✅ Multiple action types (delete, archive, retain)
- ✅ Retention policies (recent, days)
- ✅ Per-category configuration

### 4. Reporting
- ✅ Comprehensive statistics
- ✅ Per-category breakdown
- ✅ JSON + console output
- ✅ Error/warning tracking

---

## 🎯 Migration Requirements

To convert to CleanupOrchestratorV2 (AUTONOMOUS):

### 1. BaseOrchestrator v4.1 Integration
- Inherit from `BaseOrchestratorV4_1`
- Implement `execute(**kwargs)` method
- Add config-driven execution
- Add template rendering (Jinja2)

### 2. Master Orchestrator Integration
- Register in `cortex-brain/config/master-orchestrator.yaml`
- Add routing patterns: `^(cleanup|cleanup cache|cleanup logs|cleanup full).*$`
- Implement mode detection (cache/logs/artifacts/full)

### 3. State Management
- Add PlanningStateDB integration
- Track cleanup sessions
- Store statistics per session
- Enable rollback to previous state

### 4. Selective Modes
- **cache:** Cache directories only
- **logs:** Log management only
- **artifacts:** Build artifacts only
- **full:** All categories (current behavior)
- **git:** Git optimization only

### 5. Testing
- Unit tests for each category cleaner
- Integration tests with Master Orchestrator
- Rollback tests
- Protected path validation tests
- Target: 95%+ coverage, 40+ tests

---

## 📝 Backward Compatibility

**Maintenance Pipeline:**
- ✅ Preserve CLI invocation: `python src/plugins/cleanup_orchestrator.py`
- ✅ Preserve report structure (JSON format)
- ✅ Preserve protected directories (no breaking changes)

**New Capabilities:**
- ✅ Add Master Orchestrator routing (new entry point)
- ✅ Add selective modes (new feature)
- ✅ Add state persistence (new feature)

**Deprecation Plan:**
- Phase 1: CleanupOrchestratorV2 as standalone (new)
- Phase 2: Maintenance pipeline uses v2 (migration)
- Phase 3: Deprecate `src/plugins/cleanup_orchestrator.py` (optional, keep for CLI)

---

## 🔄 Next Steps

**Phase 0.2:** Extract cleanup rules into structured categories  
**Phase 1:** Implement CleanupOrchestratorV2 with BaseOrchestrator v4.1  
**Phase 2:** Create manifest and templates  
**Phase 3:** Add comprehensive tests  
**Phase 4:** Integrate with Master Orchestrator

---

**Analysis Complete:** January 2, 2026  
**Analyzed By:** CORTEX Planning System v5  
**Next:** Phase 0.2 (Cleanup Rules Extraction)
