# Cleanup Rules Categorization

**Plan:** cleanup-v2-migration  
**Created:** January 2, 2026  
**Source:** `cortex-brain/cleanup-rules.yaml` (975 lines, 23+ categories)

---

## 📊 Cleanup Category Grouping

Based on analysis of `cleanup-rules.yaml`, cleanup operations fall into 4 main groups:

### 1. **CACHE** (Priority: HIGH) - Quick, Safe Cleanup
**Purpose:** Remove regenerable cached data (fastest cleanup, highest impact)

**Categories:**
- `python_cache` - `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.mypy_cache/`
- `cache` - Generic cache directories
- `sweeper` - Distributed caching artifacts
- `temp_directories` - Temporary build artifacts
- `empty_directories` - Empty folders after cleanup

**Characteristics:**
- ✅ 100% safe (all regenerable)
- ✅ HIGH space savings (100MB-2GB typical)
- ✅ FAST execution (<10 seconds)
- ✅ No confirmation required
- ✅ Risk Level: LOW

**Action:** `delete_all`  
**Retention:** None (all deleted)

---

### 2. **LOGS** (Priority: MEDIUM) - Log Management
**Purpose:** Rotate, archive, and clean old logs

**Categories:**
- `logs` - Application logs (rotation threshold: 10MB)
- `build_output` - Build system logs
- `session_summaries` - Session-level logs (retain 7 days)
- `system_refactor_reports` - Refactor session reports (keep 3 most recent)
- `duplicate_cleanup_reports` - Cleanup execution reports (keep 5 most recent)

**Characteristics:**
- ⚠️ MEDIUM risk (logs may contain debug info)
- ⚠️ MEDIUM space savings (50MB-500MB typical)
- ✅ FAST execution (~5 seconds)
- ⚠️ Confirmation recommended for old logs

**Action:** `retain_recent` OR `retain_days`  
**Retention Policies:**
- **Log Rotation:** Keep logs <10MB, archive >10MB
- **Session Reports:** Keep last 3-5 most recent
- **Old Logs:** Delete logs >30 days old

---

### 3. **ARTIFACTS** (Priority: MEDIUM) - Build & Generated Files
**Purpose:** Remove build artifacts, generated docs, temporary outputs

**Categories:**
- `backup_archive` - Nested backup directories (`.backup-archive/`)
- `story_backups` - Story documentation backups (keep 5 most recent)
- `phase_reports` - Phase completion reports (keep 3 most recent)
- `workflow_checkpoints` - Workflow state snapshots (keep 5 most recent)
- `legacy_agent_backups` - Old agent backups
- `docs_awakening_backups` - Documentation backups
- `root_clutter` - Root-level generated files
- `copilot_chats_clutter` - Copilot chat transcripts
- `temp_historical_docs` - Temporary historical documentation
- `root_phase_documentation` - Misplaced phase docs
- `root_validation_scripts` - Temporary validation scripts
- `root_backup_files` - Root-level backup files (`.backup.*`)
- `root_test_outputs` - Test output files in root
- `redundant_alignment_reports` - Duplicate alignment reports
- `doc_pattern_cleanup` - Generated doc patterns

**Characteristics:**
- ⚠️ MEDIUM risk (generated, but may contain work-in-progress)
- ⚠️ MEDIUM-HIGH space savings (500MB-5GB typical)
- ⚠️ SLOW execution (~30-60 seconds, file-heavy)
- ⚠️ Confirmation recommended for recent backups

**Action:** Varies by category
- `delete_all` - Nested archives, legacy files
- `retain_recent` - Backups (keep 3-5 most recent)
- `retain_days` - Temporary docs (keep 7-30 days)

---

### 4. **GIT** (Priority: LOW) - Git Repository Optimization
**Purpose:** Optimize .git directory, clean unreachable objects

**Operations:**
- `git gc` - Garbage collection
- `git prune` - Remove unreachable objects
- `git repack` - Optimize pack files
- Clean reflog entries >90 days

**Characteristics:**
- ✅ LOW risk (git manages safety)
- ✅ MEDIUM space savings (10MB-500MB typical)
- ⚠️ SLOW execution (~2-5 minutes for large repos)
- ✅ No confirmation required (git handles safety)

**Action:** Execute git commands  
**Retention:** Git's default policies

---

## 🎯 Category to Mode Mapping (CleanupOrchestratorV2)

### Mode: `cleanup cache`
**Categories:** Cache only (Group 1)
- `python_cache`
- `cache`
- `sweeper`
- `temp_directories`
- `empty_directories`

**Expected Results:**
- Duration: <10 seconds
- Space Freed: 100MB-2GB
- Files Deleted: 50-500 files
- Confirmation: Not required

---

### Mode: `cleanup logs`
**Categories:** Logs only (Group 2)
- `logs`
- `build_output`
- `session_summaries`
- `system_refactor_reports`
- `duplicate_cleanup_reports`

**Expected Results:**
- Duration: ~5-10 seconds
- Space Freed: 50MB-500MB
- Files Deleted: 10-50 files
- Confirmation: Recommended for >10MB logs

---

### Mode: `cleanup artifacts`
**Categories:** Build artifacts & generated files (Group 3)
- `backup_archive`
- `story_backups`
- `phase_reports`
- `workflow_checkpoints`
- `legacy_agent_backups`
- `docs_awakening_backups`
- `root_clutter`
- `copilot_chats_clutter`
- `temp_historical_docs`
- `root_phase_documentation`
- `root_validation_scripts`
- `root_backup_files`
- `root_test_outputs`
- `redundant_alignment_reports`
- `doc_pattern_cleanup`

**Expected Results:**
- Duration: ~30-60 seconds
- Space Freed: 500MB-5GB
- Files Deleted: 100-1000+ files
- Confirmation: Recommended for recent files

---

### Mode: `cleanup full`
**Categories:** All groups (1+2+3)
- Cache cleanup
- Log management
- Artifact removal

**Expected Results:**
- Duration: ~45-90 seconds
- Space Freed: 650MB-7.5GB
- Files Deleted: 160-1550+ files
- Confirmation: Recommended

---

### Mode: `cleanup git`
**Categories:** Git optimization only (Group 4)
- Git garbage collection
- Git pruning
- Git repacking

**Expected Results:**
- Duration: ~2-5 minutes
- Space Freed: 10MB-500MB
- Objects Cleaned: 100-10,000
- Confirmation: Not required

---

## 🛡️ Protected Directories (NEVER DELETED)

From `cleanup-rules.yaml` line 700+:

```yaml
protected_directories:
  - "cortex-brain/tier1"
  - "cortex-brain/tier2"
  - "cortex-brain/tier3"
  - "cortex-brain/lessons-learned.yaml"
  - "cortex-brain/knowledge-graph.yaml"
  - "cortex-brain/user-dictionary.yaml"
  - "cortex-brain/documents"
  - ".git"
  - "src"
  - "tests"
  - "cortex-brain/manifests"
  - "cortex-brain/config"
```

**Additional Protection Rules:**
- Active plan folders with `copilot_instructions` block
- Named templates in `response-templates-v4.yaml`
- Files modified in last 24 hours (optional safety)

---

## 📋 Retention Policy Summary

| Category | Action | Retention | Keep Count |
|----------|--------|-----------|------------|
| Cache | `delete_all` | None | 0 |
| Logs (small) | `delete_all` | <10MB | 0 |
| Logs (large) | `archive` | Archive >10MB | All (compressed) |
| Session Reports | `retain_recent` | Keep recent | 3-5 |
| Backups | `retain_recent` | Keep recent | 5 |
| Temp Docs | `retain_days` | 7-30 days | All (within window) |
| Legacy Files | `delete_all` | None | 0 |
| Git Objects | `git prune` | >90 days | Reachable only |

---

## 🎨 Template Data Structure (For Jinja2)

```yaml
cleanup_result:
  mode: "cache"  # cache, logs, artifacts, full, git
  timestamp: "2026-01-02T10:30:00Z"
  duration_seconds: 8.5
  categories_processed: 5
  
  statistics:
    files_scanned: 1234
    files_deleted: 456
    files_archived: 10
    folders_deleted: 78
    space_freed_mb: 1250.5
    
  categories:
    python_cache:
      count: 120
      size_mb: 800.2
      items:
        - path: "__pycache__/module.cpython-311.pyc"
          size_mb: 0.5
          action: "deleted"
    
    cache:
      count: 45
      size_mb: 350.0
      items: [...]
  
  errors: []
  warnings: ["Max recursion depth reached at nested/path"]
  
  protected_skipped:
    - "cortex-brain/tier1/cortex-tier1.db"
    - ".git/objects/pack/large-pack.idx"
```

---

## 🔄 Migration Strategy

### Phase 1: Modular Category Implementations
Create separate modules for each group:

1. **`cache_cleaner.py`** - Group 1 (Cache)
   - Python cache cleanup
   - Generic cache cleanup
   - Temp directory cleanup

2. **`log_manager.py`** - Group 2 (Logs)
   - Log rotation logic
   - Log compression
   - Old log deletion

3. **`artifact_remover.py`** - Group 3 (Artifacts)
   - Backup cleanup
   - Report cleanup
   - Root clutter cleanup

4. **`git_optimizer.py`** - Group 4 (Git)
   - Git gc execution
   - Git prune execution
   - Git repack execution

### Phase 2: Orchestrator Integration
`CleanupOrchestratorV2` coordinates category modules based on mode:

```python
class CleanupOrchestratorV2(BaseOrchestratorV4_1):
    def execute(self, mode="full", **kwargs):
        if mode == "cache":
            return self.cache_cleaner.execute()
        elif mode == "logs":
            return self.log_manager.execute()
        elif mode == "artifacts":
            return self.artifact_remover.execute()
        elif mode == "full":
            results = []
            results.append(self.cache_cleaner.execute())
            results.append(self.log_manager.execute())
            results.append(self.artifact_remover.execute())
            return self._aggregate_results(results)
        elif mode == "git":
            return self.git_optimizer.execute()
```

### Phase 3: Configuration
Manifest controls behavior:

```yaml
# cleanup-orchestrator-v2.yaml
modes:
  cache:
    categories: ["python_cache", "cache", "sweeper", "temp_directories", "empty_directories"]
    confirmation_required: false
    
  logs:
    categories: ["logs", "build_output", "session_summaries", "system_refactor_reports"]
    confirmation_required: true
    log_rotation_threshold_mb: 10
    
  artifacts:
    categories: ["backup_archive", "story_backups", ...(15 categories)]
    confirmation_required: true
    retention_days: 30
    
  full:
    categories: ["cache", "logs", "artifacts"]
    confirmation_required: true
    
  git:
    operations: ["gc", "prune", "repack"]
    confirmation_required: false
```

---

## ✅ Success Criteria

**Phase 0.2 Complete When:**
- ✅ 4 cleanup groups defined (Cache, Logs, Artifacts, Git)
- ✅ Mode-to-category mapping documented
- ✅ Retention policies extracted
- ✅ Protected directories listed
- ✅ Template data structure defined
- ✅ Migration strategy documented

---

**Analysis Complete:** January 2, 2026  
**Analyzed By:** CORTEX Planning System v5  
**Next:** Phase 0.3 (Migration Strategy Document)
