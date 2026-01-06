# Phase 9: Generic Vacuum Orchestrator v3
**Epic:** CORTEX5 Enhancement | **Timeline:** Week 7 (5 days) | **Priority:** HIGH

---

## 🎯 Phase Objective

Transform the specialized Vacuum v2 orchestrator into a **generic, reusable vacuum system** that can clean any directory structure based on configurable YAML rules, enabling use across CORTEX projects, user codebases, and external projects.

---

## 📊 Phase Overview

**Duration:** 5 days  
**Complexity:** Medium  
**Dependencies:** Phase 1 (Planning System v5), Phase 4 (Response Templates)  
**Enables:** User project automation, CI/CD integration

**Value Unlock:**
- CORTEX becomes useful beyond AI assistance (project maintenance tool)
- Users can vacuum their own projects with custom rules
- Community contributions (preset templates for different project types)

---

## 🏗️ Architecture Changes

### From: Vacuum v2 (Specialized)
```
vacuum_orchestrator_v2.py
├── Hardcoded CORTEX paths
├── Embedded brain protection rules
├── Python-only AST analysis
└── JSON + Markdown reports
```

### To: Vacuum v3 (Generic)
```
vacuum_orchestrator_v3.py (main)
├── analyzers/
│   ├── base_analyzer.py
│   ├── python_analyzer.py (migrated from v2)
│   ├── javascript_analyzer.py (NEW)
│   ├── content_analyzer.py (NEW)
│   └── metadata_analyzer.py (NEW)
├── rules/
│   ├── rule_engine.py (NEW)
│   └── presets/
│       ├── cortex-brain.yaml (CORTEX-specific)
│       ├── python-project.yaml (NEW)
│       ├── node-project.yaml (NEW)
│       └── generic.yaml (NEW)
├── reporters/
│   ├── base_reporter.py (NEW)
│   ├── json_reporter.py (migrated)
│   ├── markdown_reporter.py (migrated)
│   ├── html_reporter.py (NEW)
│   └── csv_reporter.py (NEW)
└── manifest.yaml (updated)
```

---

## 📋 Deliverables

### D9.1: Rule Engine & Schema (Day 1)
**Owner:** Core Team  
**Output:** `rules/rule_engine.py`, `vacuum-rules-schema.yaml`

**Tasks:**
1. Define vacuum rule schema (YAML structure)
2. Implement rule parser (YAML → Python objects)
3. Create rule validator (schema compliance checking)
4. Build rule executor (apply rules to filesystem)

**Acceptance Criteria:**
- ✅ Parse valid YAML rules without errors
- ✅ Validate rules against schema (detect malformed rules)
- ✅ Execute scan/exclusion/cleanup rules correctly
- ✅ 100% test coverage on rule engine

---

### D9.2: Pluggable Analyzer System (Day 2)
**Owner:** Core Team  
**Output:** `analyzers/` folder with 5 analyzers

**Tasks:**
1. Create `BaseAnalyzer` abstract class (interface for all analyzers)
2. Migrate Python AST analyzer from v2 to v3 structure
3. Implement JavaScript/TypeScript analyzer (AST-based via `esprima` or similar)
4. Implement content analyzer (SHA-256 hashing)
5. Implement metadata analyzer (size, timestamp comparison)

**Acceptance Criteria:**
- ✅ All analyzers implement `BaseAnalyzer` interface
- ✅ Python analyzer maintains v2 accuracy (95%+ duplicate detection)
- ✅ JavaScript analyzer detects duplicates in `.js`/`.ts` files
- ✅ Content analyzer works for all file types
- ✅ Metadata analyzer respects threshold configurations

---

### D9.3: Preset Templates (Day 2-3)
**Owner:** Core Team  
**Output:** `rules/presets/` folder with 4 presets

**Tasks:**
1. Create `cortex-brain.yaml` (migrate v2 hardcoded rules)
2. Create `python-project.yaml` (common Python project cleanup)
3. Create `node-project.yaml` (Node.js project cleanup)
4. Create `generic.yaml` (universal filesystem cleanup)

**Preset Requirements:**

**cortex-brain.yaml:**
- Scan `cortex-brain/documents/planning/active/`
- Detect duplicate plans, orphaned files
- Respect brain protection rules
- Archive to `backups/vacuum-{timestamp}/`

**python-project.yaml:**
- Scan project root
- Clean `__pycache__/`, `*.pyc`, `.pytest_cache/`, `.mypy_cache/`
- Detect duplicate Python modules (AST-based)
- Respect `.gitignore`

**node-project.yaml:**
- Scan project root
- Clean `node_modules/` (optional), `.next/`, `dist/`, `build/`
- Detect duplicate JavaScript/TypeScript files
- Respect `.gitignore`

**generic.yaml:**
- Scan any directory
- Clean empty folders, duplicate files (content-based)
- Configurable exclusions
- Safe defaults (dry-run enabled)

**Acceptance Criteria:**
- ✅ All 4 presets parse without errors
- ✅ Each preset tested on real project
- ✅ Documentation for each preset (when to use, how to customize)

---

### D9.4: Multi-Format Reporting (Day 3)
**Owner:** Core Team  
**Output:** `reporters/` folder with 5 reporters

**Tasks:**
1. Create `BaseReporter` abstract class
2. Migrate JSON/Markdown reporters from v2
3. Implement HTML reporter (interactive viewer with charts)
4. Implement CSV reporter (for spreadsheet analysis)
5. Add report aggregation (combine multiple formats)

**HTML Reporter Features:**
- Duplicate file tree visualization
- Space savings chart (pie chart)
- Before/after comparison
- Clickable file paths (open in editor)
- Responsive design (mobile-friendly)

**Acceptance Criteria:**
- ✅ All reporters implement `BaseReporter` interface
- ✅ HTML report includes interactive visualizations
- ✅ CSV report compatible with Excel/Google Sheets
- ✅ Reports can be generated individually or combined

---

### D9.5: CLI & API Enhancement (Day 4)
**Owner:** Core Team  
**Output:** Updated `vacuum_orchestrator_v3.py` with enhanced CLI

**New CLI Commands:**
```bash
# CORTEX mode (default)
vacuum --mode cortex-brain --dry-run

# Project mode with preset
vacuum --mode project --preset python-project --path ./my-project

# Custom mode with inline rules
vacuum --mode custom --rules custom-rules.yaml --path ./target

# Legacy mode (exact v2 behavior)
vacuum --legacy-mode --path cortex-brain/
```

**API Enhancement:**
```python
from src.orchestrators.vacuum import VacuumOrchestratorV3

orchestrator = VacuumOrchestratorV3(
    mode="project",
    preset="python-project",
    path="./my-project",
    dry_run=True
)
results = orchestrator.execute()
```

**Acceptance Criteria:**
- ✅ All CLI modes work correctly
- ✅ Legacy mode produces identical output to v2
- ✅ API supports programmatic usage
- ✅ Help text comprehensive (`vacuum --help`)

---

### D9.6: Testing & Documentation (Day 5)
**Owner:** Core Team + Docs Team  
**Output:** Test suite + comprehensive documentation

**Testing:**
1. Unit tests for rule engine (20+ test cases)
2. Unit tests for each analyzer (10+ test cases each)
3. Integration tests (end-to-end with test fixtures)
4. Performance benchmarks (10K, 50K, 100K files)
5. Regression tests (ensure v2 compatibility)

**Test Fixtures:**
- Small CORTEX project (100 files)
- Medium Python project (1,000 files)
- Large Node.js project (10,000 files)
- Edge cases (empty folders, symlinks, large files)

**Documentation:**
1. **User Guide** (`docs/vacuum-v3-guide.md`)
   - Quick start examples
   - Preset selection guide
   - Custom rule creation
   - Troubleshooting

2. **Rule Schema Reference** (`docs/vacuum-rules-schema.md`)
   - Complete YAML schema
   - All configuration options
   - Examples for each option

3. **API Reference** (`docs/vacuum-v3-api.md`)
   - Class documentation
   - Method signatures
   - Usage examples

4. **Migration Guide** (`docs/vacuum-v2-to-v3-migration.md`)
   - Breaking changes
   - Migration checklist
   - Side-by-side comparison

**Acceptance Criteria:**
- ✅ 100% test coverage on new components
- ✅ All integration tests pass
- ✅ Performance benchmarks meet targets (<30s for 10K files)
- ✅ Documentation complete and reviewed
- ✅ Zero critical bugs

---

## 🔄 TDD Workflow (RED → GREEN → REFACTOR)

### Day 1: Rule Engine
**RED:** Write failing tests for rule parser  
**GREEN:** Implement rule parser to pass tests  
**REFACTOR:** Optimize YAML parsing performance

### Day 2: Analyzers
**RED:** Write failing tests for JavaScript analyzer  
**GREEN:** Implement JavaScript AST analysis  
**REFACTOR:** Extract common analyzer logic to base class

### Day 3: Presets & Reporting
**RED:** Write failing tests for HTML reporter  
**GREEN:** Implement HTML generation with charts  
**REFACTOR:** DRY up reporter base class

### Day 4: CLI & API
**RED:** Write failing tests for CLI argument parsing  
**GREEN:** Implement CLI with all modes  
**REFACTOR:** Simplify mode selection logic

### Day 5: Integration
**RED:** Write failing end-to-end tests  
**GREEN:** Fix integration issues  
**REFACTOR:** Performance optimizations

---

## 📊 Success Metrics

**Functionality:**
- ✅ Vacuum 3+ different project types (CORTEX, Python, Node.js)
- ✅ All 4 presets work correctly
- ✅ Custom rules validate and execute

**Performance:**
- ✅ 50% faster than v2 (parallel analysis)
- ✅ 30% less memory usage (streaming)
- ✅ Scans 10K files in <30 seconds

**Quality:**
- ✅ 100% test coverage on new code
- ✅ 95%+ duplicate detection accuracy
- ✅ Zero critical bugs
- ✅ Documentation complete

**Adoption:**
- ✅ Used internally for 2 weeks without issues
- ✅ Positive feedback from 3+ beta testers
- ✅ 1+ external project adopts Generic Vacuum

---

## 🚨 Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Breaking changes to v2 users** | HIGH | MEDIUM | Keep v2 as legacy, provide migration guide, `--legacy-mode` flag |
| **Performance regression** | MEDIUM | LOW | Benchmark early, optimize hot paths, parallel processing |
| **Rule engine bugs** | HIGH | MEDIUM | Extensive testing, schema validation, safe defaults |
| **JavaScript analyzer complexity** | MEDIUM | MEDIUM | Use proven library (esprima), limit to common cases, fallback to content analysis |
| **Adoption resistance** | LOW | MEDIUM | Clear benefits, smooth migration, comprehensive docs |

---

## 🔗 Integration Points

**With Planning System v5:**
- Vacuum can be triggered from plans (`vacuum cortex-brain/planning/active/{plan-id}/`)
- Plan viewer shows vacuum recommendations

**With Response Templates:**
- Vacuum reports use standardized templates
- Consistent formatting across all orchestrators

**With Brain Protection:**
- Vacuum respects SKULL rules (no deleting critical files)
- Git-aware (respects tracked files)

---

## 📝 Next Steps After Phase 9

**Phase 10:** Integrate Generic Vacuum into CI/CD pipelines  
**Phase 11:** Community preset contributions (GitHub, GitLab, Bitbucket project presets)  
**Phase 12:** Cloud storage vacuum (S3, Azure Blob, GCS)

---

## 🎉 Phase Completion Criteria

✅ **All 6 deliverables complete**  
✅ **100% test coverage**  
✅ **Documentation reviewed and approved**  
✅ **Performance benchmarks met**  
✅ **Internal beta testing successful (2 weeks)**  
✅ **Migration guide validated**  
✅ **Zero blocking bugs**

**Sign-off Required:** Lead Developer, QA Lead, Documentation Lead

---

**Status:** 📋 Planned  
**Start Date:** TBD (Week 7 of CORTEX5 Epic)  
**End Date:** TBD (Week 7 + 5 days)  
**Owner:** Core Development Team

---

**Related Documents:**
- Feature Spec: `features/generic-vacuum-orchestrator.md`
- Current Implementation: `src/orchestrators/vacuum/vacuum_orchestrator_v2.py`
- Rule Schema: `docs/vacuum-rules-schema.md` (to be created)
