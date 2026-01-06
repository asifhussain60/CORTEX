# Feature: Generic Vacuum Orchestrator v3
**F011** | ⚡ HIGH PRIORITY | Phase 9

---

## 🎯 Purpose

Transform the current specialized Vacuum v2 orchestrator into a **generic, reusable vacuum orchestrator** that can clean any directory structure based on configurable rules, not just CORTEX-specific folders.

---

## 📊 Current State (Vacuum v2)

**Location:** `src/orchestrators/vacuum/vacuum_orchestrator_v2.py`

**Limitations:**
- Hardcoded to CORTEX brain structure (`cortex-brain/`, `tracking/`, `.md` files)
- CORTEX-specific folder patterns (analysis, artifacts, context, reports, tracking)
- Non-reusable for user projects or other directory structures
- Brain Protection rules embedded (not externalized)

**What it does well:**
- Deep filesystem analysis
- Duplicate detection (AST-based for Python, content-based for others)
- Archive-before-delete safety
- Comprehensive reporting (JSON + Markdown)
- Dry-run mode

---

## 🎯 Target State (Vacuum v3 - Generic)

### Core Capabilities

**1. Configurable Rule System**
- YAML-based vacuum rules (`vacuum-rules.yaml`)
- User can define: folder patterns, file extensions, duplicate strategies, exclusions
- Preset templates: `cortex-brain`, `python-project`, `node-project`, `generic`

**2. Multi-Mode Operation**
- **CORTEX Mode:** Uses brain-specific rules (current behavior)
- **Project Mode:** Uses user-defined rules for any project
- **Custom Mode:** Inline rules passed via CLI/API

**3. Pluggable Analyzers**
- Python AST analyzer (existing)
- JavaScript/TypeScript analyzer (new)
- Generic content analyzer (hash-based)
- Metadata analyzer (timestamps, sizes)

**4. Flexible Reporting**
- JSON (machine-readable)
- Markdown (human-readable)
- HTML (interactive viewer)
- CSV (for spreadsheet analysis)

**5. Safety Features**
- Dry-run mode (no changes)
- Archive-before-delete (configurable location)
- Whitelist/blacklist patterns
- Size thresholds (don't delete files >X MB without confirmation)
- Git awareness (don't delete tracked files unless forced)

---

## 🏗️ Architecture

### Component Structure

```
src/orchestrators/vacuum/
├── vacuum_orchestrator_v3.py          # Main orchestrator (generic)
├── analyzers/
│   ├── base_analyzer.py               # Abstract base class
│   ├── python_analyzer.py             # Python AST-based (existing)
│   ├── javascript_analyzer.py         # JavaScript/TypeScript AST
│   ├── content_analyzer.py            # Generic content hashing
│   └── metadata_analyzer.py           # File metadata analysis
├── rules/
│   ├── rule_engine.py                 # Rule parser & executor
│   ├── presets/
│   │   ├── cortex-brain.yaml          # CORTEX-specific rules
│   │   ├── python-project.yaml        # Python project cleanup
│   │   ├── node-project.yaml          # Node.js project cleanup
│   │   └── generic.yaml               # Generic filesystem cleanup
├── reporters/
│   ├── base_reporter.py               # Abstract base class
│   ├── json_reporter.py               # JSON output
│   ├── markdown_reporter.py           # Markdown output
│   ├── html_reporter.py               # HTML interactive viewer
│   └── csv_reporter.py                # CSV output
└── manifest.yaml                      # Orchestrator manifest
```

### Rule Schema (vacuum-rules.yaml)

```yaml
vacuum_rules:
  version: "3.0"
  mode: "cortex-brain"  # cortex-brain | project | custom
  
  scan_paths:
    - path: "cortex-brain/documents/planning/active/"
      recursive: true
      max_depth: 10
  
  exclusions:
    folders:
      - ".git"
      - "__pycache__"
      - "node_modules"
    files:
      - "*.pyc"
      - ".DS_Store"
    patterns:
      - ".*backup.*"
  
  duplicate_detection:
    enabled: true
    strategies:
      - type: "ast"
        file_extensions: [".py"]
        ignore_comments: true
        ignore_whitespace: true
      - type: "content_hash"
        file_extensions: [".md", ".txt"]
      - type: "metadata"
        file_extensions: ["*"]
        compare_size: true
        compare_timestamp: false
  
  cleanup_targets:
    empty_folders: true
    duplicate_files: true
    orphaned_files: true  # Files not referenced anywhere
    old_files:
      enabled: true
      age_days: 90
      size_threshold_mb: 10
  
  safety:
    dry_run: true
    archive_before_delete: true
    archive_path: "backups/vacuum-{timestamp}/"
    confirm_deletes_over_mb: 50
    respect_git: true  # Don't delete tracked files
  
  reporting:
    formats: ["json", "markdown", "html"]
    output_path: "reports/vacuum-{timestamp}/"
```

---

## 🔄 Migration from v2 to v3

### Phase 1: Extract Generic Components
- Extract rule engine from hardcoded logic
- Create base analyzer class
- Externalize CORTEX-specific rules to YAML

### Phase 2: Add Pluggable Analyzers
- JavaScript/TypeScript analyzer
- Generic content analyzer
- Metadata analyzer

### Phase 3: Multi-Format Reporting
- HTML reporter with interactive viewer
- CSV reporter for data analysis

### Phase 4: User Project Support
- Python project preset
- Node.js project preset
- Generic preset

### Phase 5: CLI & API Enhancement
- `vacuum --mode cortex-brain --dry-run`
- `vacuum --mode project --rules custom-rules.yaml`
- `vacuum --preset python-project --path ./my-project`

---

## 📋 Acceptance Criteria

✅ **Generic Operation:**
- Can vacuum any directory structure (not CORTEX-specific)
- Rule-based configuration (YAML)
- Multiple preset templates

✅ **Safety:**
- Dry-run mode works correctly
- Archive-before-delete preserves all deleted content
- Git-aware (respects tracked files)
- Confirmation for large deletions

✅ **Analysis Quality:**
- Python AST analyzer (existing quality maintained)
- JavaScript/TypeScript analyzer (new)
- Generic content analyzer (hash-based)
- 95%+ duplicate detection accuracy

✅ **Reporting:**
- JSON, Markdown, HTML, CSV formats
- Interactive HTML viewer
- Comprehensive metrics (files scanned, duplicates found, space saved)

✅ **Performance:**
- Scans 10,000 files in <30 seconds
- Memory usage <500MB for large projects
- Parallel analysis support

✅ **Documentation:**
- User guide with examples
- Rule schema reference
- Preset customization guide
- API documentation

---

## 🎯 Success Metrics

**Reusability:**
- Used on 3+ different project types (CORTEX, Python, Node.js)
- Community contributions (custom presets)

**Performance:**
- 50% faster than v2 (parallel analysis)
- 30% less memory usage (streaming processing)

**Adoption:**
- 90% of CORTEX vacuum operations use v3
- 5+ external projects use Generic Vacuum

---

## 🔗 Dependencies

**Prerequisites:**
- F001: Planning System v5 (for plan-based vacuum operations)
- F010: Response Templates (for reporting consistency)

**Enables:**
- User project cleanup automation
- CI/CD integration (vacuum in pipelines)
- Multi-project orchestration

---

## 📝 Implementation Notes

**Backwards Compatibility:**
- Keep Vacuum v2 as `vacuum_orchestrator_v2_legacy.py`
- Vacuum v3 supports `--legacy-mode` flag for exact v2 behavior
- Migration guide for existing vacuum scripts

**Testing Strategy:**
- Unit tests for each analyzer
- Integration tests for rule engine
- End-to-end tests with test fixtures (CORTEX, Python, Node.js projects)
- Performance benchmarks (10K, 50K, 100K files)

**Rollout Strategy:**
- Phase 1: Internal CORTEX use only (validate on real workload)
- Phase 2: Opt-in beta for Python projects
- Phase 3: General release with presets
- Phase 4: Community preset contributions

---

**Status:** 📋 Planned  
**Priority:** HIGH (unlocks user project automation)  
**Effort:** 3 weeks (2 weeks dev + 1 week testing/docs)  
**Risk:** LOW (extends existing v2, minimal breaking changes)

---

**Related Documents:**
- Current Implementation: `src/orchestrators/vacuum/vacuum_orchestrator_v2.py`
- Manifest: `cortex-brain/manifests/orchestrators/vacuum-v2-manifest.yaml`
- Brain Protection: `cortex-brain/brain-protection-rules.yaml` (Vacuum rules)
