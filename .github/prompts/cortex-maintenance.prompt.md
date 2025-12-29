---
mode: agent
description: "CORTEX System Maintenance - Health checks, intent router validation, and prompt regeneration"
---

# 🩺 CORTEX System Maintenance

**Purpose:** Keep CORTEX 4.0 at peak performance through health checks, intent router validation, and automated prompt regeneration.

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## 🎯 9-Phase Maintenance Pipeline

| Phase | Action | Success Criteria |
|-------|--------|------------------|
| **1** | Toolkit + Interactive + Vision Validation | Scaffold generators + session workflow + auto-engagement working |
| **2** | Quick Health Check | Health score ≥90 |
| **3** | Full Diagnostic | All components wired |
| **4** | Wiring Integrity | 100% wiring coverage |
| **4.5** | Test Suite Health 🆕 | Core 100%, full ≥99% |
| **5** | Knowledge Library Validation | All guidelines accessible |
| **6** | Review Reports | Reports generated |
| **7** | Intent Router Validation | All manifests synced |
| **8** | Regenerate Lean Prompts | <200 lines each |
| **9** | Report Management | Cleanup old reports |

---

## Phase 1: Toolkit Automation Validation 🛠️

### 1a. Verify Scaffold Generators Exist

**Critical:** Ensure automation utilities are present and functional.

```bash
# Check plan scaffold generator
test -f cortex-toolkit/core/utilities/plan_scaffold_generator.py || echo "ERROR: Plan scaffold generator missing!"

# Check orchestrator scaffold generator
test -f cortex-toolkit/core/utilities/orchestrator_scaffold_generator.py || echo "ERROR: Orchestrator scaffold generator missing!"

# Verify both are registered in toolkit manifest
grep -q "plan-scaffold" cortex-toolkit/toolkit-manifest.yaml || echo "ERROR: Plan scaffold not registered!"
grep -q "orchestrator-scaffold" cortex-toolkit/toolkit-manifest.yaml || echo "ERROR: Orchestrator scaffold not registered!"
```

### 1a-2. Verify Interactive Planning Session ✨ NEW

**Critical:** Ensure interactive planning workflow is properly wired.

```bash
# Check interactive session module exists
test -f src/orchestrators/planning/interactive_session.py || echo "ERROR: Interactive session module missing!"

# Verify session states are defined
grep -q "class SessionState" src/orchestrators/planning/interactive_session.py || echo "ERROR: SessionState enum missing!"

# Check for key workflow classes
grep -q "class PlanningSession" src/orchestrators/planning/interactive_session.py || echo "ERROR: PlanningSession class missing!"
grep -q "class DiscoveryEngine" src/orchestrators/planning/interactive_session.py || echo "ERROR: DiscoveryEngine class missing!"
grep -q "class ApprovalWorkflow" src/orchestrators/planning/interactive_session.py || echo "ERROR: ApprovalWorkflow class missing!"
grep -q "class CleanupPhase" src/orchestrators/planning/interactive_session.py || echo "ERROR: CleanupPhase class missing!"
```

**Expected Workflow States:**
- `INITIALIZING` → `DISCOVERY` → `CONTEXT_GATHERING` → `USER_REVIEW`
- `USER_REVIEW` → `APPROVED` or `REFINING`
- `APPROVED` → `DRAFTING` → `CLEANUP` → `FINALIZED`

**Test Interactive Planning:**
```bash
# Run interactive planning tests (29 tests expected)
python3 -m pytest tests/orchestrators/planning/test_interactive_planning_session.py -v

# Expected: 18 session tests + 11 workflow tests = 29 total
```

### 1a-3. Verify Vision API Auto-Engagement 👁️ NEW

**Critical:** Ensure Vision API automatically engages when images are attached.

```bash
# Check vision orchestrator exists
test -f src/tier1/vision_orchestrator.py || echo "ERROR: Vision orchestrator missing!"

# Check image detector exists
test -f src/tier1/image_detector.py || echo "ERROR: Image detector missing!"

# Check vision context middleware
test -f src/operations/utilities/vision_context_middleware.py || echo "ERROR: Vision context middleware missing!"

# Verify auto-detection is enabled in config
grep -q "auto_detect_images" cortex.config.json || echo "WARNING: Auto-detect not configured!"
grep -q "auto_analyze_on_detect" cortex.config.json || echo "WARNING: Auto-analyze not configured!"
```

**Expected Features:**
- ✅ Automatic image detection in chat attachments
- ✅ Auto-engage Vision API without user prompting
- ✅ Context injection into planning/debugging workflows
- ✅ Duplicate image caching (24hr TTL)
- ✅ Token budget enforcement (500 token limit)

**Test Vision Auto-Engagement:**
```python
# Smoke test: Verify vision orchestrator detects images
from src.tier1.vision_orchestrator import VisionOrchestrator
from src.tier1.image_detector import ImageDetector

# Load config
import json
with open('cortex.config.json') as f:
    config = json.load(f)

# Initialize orchestrator
orchestrator = VisionOrchestrator(config)

# Test image detection (dry run)
result = orchestrator.process_request(
    user_request="analyze this",
    attachments=[
        {'type': 'image', 'path': '/path/to/test.png', 'mime': 'image/png'}
    ]
)

print(f"✅ Images found: {result['images_found']}")
print(f"✅ Auto-analyze: {orchestrator.auto_analyze}")
print(f"✅ Auto-inject: {orchestrator.inject_context}")
```

### 1b. Test Scaffold Generators

```bash
# Test plan scaffold generator (dry run)
python cortex-toolkit/core/utilities/plan_scaffold_generator.py "test-plan" --dry-run

# Test orchestrator scaffold generator (dry run)
python cortex-toolkit/core/utilities/orchestrator_scaffold_generator.py --type planning "test-plan" --dry-run

# List available templates
python cortex-toolkit/core/utilities/orchestrator_scaffold_generator.py --list-templates
```

**Expected Output:**
- ✅ Dry run shows 4 folders for planning (context, reports, artifacts, tracking)
- ✅ progress-tracker.json would be created
- ✅ All orchestrator templates listed (planning, sanitization, tdd, ado, maintenance)

### 1c. Verify Manifest Integration

Check that planning system manifest references automation:

```bash
# Verify automation section exists in planning manifest
grep -A 5 "automation:" cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml
```

**Expected Fields:**
- `tool:` points to `plan_scaffold_generator.py`
- `usage:` shows command syntax
- `benefits:` lists automation advantages
- `enforcement:` references maintenance requirement

### 1d. Enforcement Rule

**⚠️ MANDATORY:** All new plans MUST use scaffold generator.

**Manual folder creation is DEPRECATED** as of CORTEX 4.0.1.

**Validation:** During Phase 7 (Regenerate Prompts), verify CORTEX.prompt.md and planning-system-4.0-manifest.yaml both enforce scaffold usage.

---

## Phase 2-4: Health & Diagnostics

```bash
# Phase 2: Quick check
python3 scripts/cortex_system_doctor.py --quick

# Phase 3: Full diagnostic
python3 scripts/cortex_system_doctor.py --phase diagnose --phase scan

# Phase 4: Wiring integrity
python3 scripts/check_wiring_integrity.py
```

---

## Phase 4.5: Test Suite Health 🧪 NEW

### When to Run Tests

Run the full test suite during maintenance when:
- ✅ **Interactive planning system** has been modified
- ✅ **Core orchestrators** have been updated
- ✅ **Brain protection rules** have changed
- ✅ **Fixture patterns** need validation
- ❌ **Minor documentation updates** (skip tests)
- ❌ **Knowledge library additions** (skip tests unless validation required)

### Test Suite Execution

```bash
# Run full planning orchestrator test suite (recommended during maintenance)
python3 -m pytest tests/orchestrators/planning/ --tb=no -q

# Expected: 396+ passing, <5 failing
# Target: 99%+ pass rate

# Run core functionality tests only (faster, 29 tests)
python3 -m pytest tests/orchestrators/planning/test_interactive_planning_session.py \
                 tests/orchestrators/planning/test_toolkit_integration.py -v

# Expected: 29/29 passing (100%)

# Use test runner script for specific categories
./test_planning.sh interactive   # 18 tests - Interactive session workflow
./test_planning.sh toolkit        # 11 tests - Toolkit integration
./test_planning.sh quick          # 29 tests - Core functionality only
./test_planning.sh all            # 397 tests - Full suite
```

### Test Health Metrics

| Metric | Target | Action if Below |
|--------|--------|-----------------|
| **Core Tests Pass Rate** | 100% | CRITICAL - Fix immediately |
| **Full Suite Pass Rate** | ≥99% | Review failures, assess if obsolete |
| **Error Count** | 0 | CRITICAL - All errors must be fixed |
| **Test Execution Time** | <30s | Acceptable, monitor for regression |

### Common Test Failures

**Issue:** `ModuleNotFoundError: No module named 'core'`
- **Fix:** Fixture missing `sys.path.insert(0, cortex-toolkit/)` and toolkit structure

**Issue:** `RuntimeError: Planning root not found`
- **Fix:** Fixture missing `(tmp_path / "cortex-brain" / "documents" / "planning" / "active").mkdir(parents=True)`

**Issue:** Tests passing but functionality broken
- **Fix:** Check if test is obsolete (testing old API that was refactored)

### Test Report Location

After running tests, check:
- `cortex-brain/documents/reports/test-suite-cleanup-report-{DATE}.md` for latest health report

---

## Phase 5: Knowledge Library Validation 📚 CRITICAL

### 5a. Knowledge Library Structure Check

**Source of Truth:** `cortex-brain/knowledge/`

Verify knowledge library structure and accessibility:

```bash
# Verify knowledge library structure
test -d cortex-brain/knowledge || echo "ERROR: Knowledge library missing!"

# Count knowledge files by category
for dir in cortex-brain/knowledge/*/; do
  echo "$(basename "$dir"): $(find "$dir" -name "*.yaml" | wc -l) files"
done

# Verify README exists and is current
test -f cortex-brain/knowledge/README.md || echo "ERROR: Knowledge README missing!"

# Check for orphaned YAML files (not in a category)
find cortex-brain/knowledge/ -maxdepth 1 -name "*.yaml" -type f
```

**Expected Categories:**
- `database/` - Database best practices (Oracle, SQL Server, etc.)
- `ddd/` - Domain-Driven Design patterns
- `devops/` - DevOps and infrastructure
- `domains/` - Domain-specific knowledge (RAG, embeddings)
- `engineering/` - Software engineering principles
- `performance/` - Performance optimization
- `security/` - Security best practices
- `testing/` - Testing strategies and patterns
- `ui-ux/` - UI/UX design guidelines

### 5b. Knowledge Library Reference Validation

**Critical:** Ensure orchestrators and modules can reference knowledge library.

Verify these systems wire to knowledge library:

| System | Knowledge Usage | Verification |
|--------|----------------|--------------|
| **Code Review Orchestrator** | Validates code against guidelines | Check manifest references `cortex-brain/knowledge/` |
| **Sanitization Orchestrator** | Applies best practices during cleanup | Check for knowledge library imports |
| **Refactoring Orchestrator** | Identifies anti-patterns | Check pattern detection references |
| **TDD Orchestrator** | Guides test design | Check test pattern references |
| **Documentation Generator** | Auto-generates docs from guidelines | Check template references |

### 5c. Knowledge Library Sync Validation (NEW)

**Critical:** Ensure markdown templates stay in sync with YAML knowledge library.

```bash
# Run knowledge library sync check
python3 scripts/sync_knowledge_library.py --check-status

# Generate sync report
python3 scripts/sync_knowledge_library.py --report > cortex-brain/health-reports/knowledge-sync-report.md
```

**Expected Output:**
```
📊 Knowledge Library Sync Status

✅ glassmorphism-design-standards: none (in sync)
⚠️  [other-file]: sync_md_to_yaml (markdown changed)
```

**If out of sync detected:**
```bash
# Dry run to preview changes
python3 scripts/sync_knowledge_library.py --sync-all --dry-run

# Perform sync (updates hashes, flags manual review)
python3 scripts/sync_knowledge_library.py --sync-all
```

**Sync Registry Files:**
- `glassmorphism-design-standards.yaml` ↔ `glassmorphism-design-standards-v2.md`
- Future template ↔ YAML pairs automatically detected via `metadata.sync` section

### 5d. Knowledge File Schema Validation

Each knowledge YAML must have:

```yaml
metadata:
  title: "Guideline Name"
  category: "Category"
  version: "X.Y"
  created: "YYYY-MM-DD"
  updated: "YYYY-MM-DD"
  tags: [tag1, tag2, ...]
  
  # Sync configuration (if synced with markdown template)
  sync:
    source_markdown: "cortex-brain/documents/templates/filename.md"
    sync_enabled: true
    sync_direction: "bidirectional"
    last_sync: "2025-12-29T00:00:00Z"
  
  generated_docs:
    - path: "docs/guidelines/{category}/{filename}.md"

{category}_section:
  principle: "Core principle statement"
  importance: "Why it matters"
  rules:
    - id: "unique_id_###"
      name: "Rule Name"
      severity: "CRITICAL|HIGH|MEDIUM|LOW"
      examples:
        good: [...]
        bad: [...]
```

### 5d. Validation Commands

```bash
# Check all YAML files for metadata section
for f in cortex-brain/knowledge/**/*.yaml; do
  grep -q "metadata:" "$f" || echo "MISSING metadata: $f"
done

# Verify severity levels are valid
for f in cortex-brain/knowledge/**/*.yaml; do
  grep -E "severity: \"(CRITICAL|HIGH|MEDIUM|LOW)\"" "$f" > /dev/null || \
    echo "Invalid severity in: $f"
done

# Check for duplicate rule IDs
grep -rh "id: \"" cortex-brain/knowledge/ | sort | uniq -d

# Verify README is up to date (check statistics)
grep "Total:" cortex-brain/knowledge/README.md
```

### 5e. Integration Verification

Verify orchestrators can load knowledge library:

```bash
# Check for knowledge library imports in orchestrators
grep -r "knowledge" src/orchestrators/*.py | grep -E "(import|load|read)"

# Check for knowledge references in manifests
grep -r "knowledge" cortex-brain/manifests/orchestrators/*.yaml

# Verify brain protection rules reference knowledge library
grep -A 5 "knowledge" cortex-brain/brain-protection-rules.yaml
```

### 5f. Knowledge Library Health Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Total Guidelines | 30 | 30+ | ✅ |
| Categories | 9 | 8+ | ✅ |
| Total Rules | 525+ | 500+ | ✅ |
| Critical Rules | 77+ | 75+ | ✅ |
| Files with Metadata | 30/30 | 100% | ✅ |
| Files with Examples | 30/30 | 100% | ✅ |

---

## Phase 6: Review Reports

```bash
# Phase 5: Reports in cortex-brain/health-reports/
ls -lah cortex-brain/health-reports/
```

---

## Phase 7: Intent Router Validation ⚠️ CRITICAL

### 7a. Manifest Path Verification

**Source of Truth:** `cortex-brain/manifests/orchestrators/`

Scan all orchestrator manifests and verify CORTEX.prompt.md references them correctly:

| Manifest File | Orchestrator | Must Have Triggers |
|---------------|--------------|-------------------|
| `planning-system-4.0-manifest.yaml` | Planning System | `plan [x]`, `create a plan`, `make a plan` |
| `tdd-orchestrator-v4-manifest.yaml` | TDD Mastery | `start tdd`, `run tests`, `tdd [x]` |
| `ado-planning-manifest.yaml` | ADO Operations | `plan ado`, `ado story`, `ado feature` |
| `code-sanitization-manifest.yaml` | Sanitization | `sanitize`, `make generic`, `anonymize` |
| `refinement-orchestrator-manifest.yaml` | Refinement | `refine`, `improve cortex` |

### 7b. Output Structure Validation

Planning System MUST specify folder structure from manifest:
```yaml
output_location: cortex-brain/documents/planning/active/{PLAN_NAME}/
required_subfolders: [context/, reports/, artifacts/, tracking/]
required_files: [00-master-plan.md]
```

### 6c. Validation Commands

```bash
# Check for broken/old paths
grep -r "orchestrator-manifests" .github/prompts/  # Should return NOTHING

# Verify all manifest references exist
for f in $(grep -oh "cortex-brain/manifests/orchestrators/[^\"']*" .github/prompts/*.md); do
  [ -f "$f" ] || echo "MISSING: $f"
done
```

---

## Phase 8: Regenerate Lean Prompts

**Goal:** Create minimal, clean prompt files with proper intent routing.

### 7a. CORTEX.prompt.md Structure (Target: <200 lines)

```markdown
# 🎯 CORTEX Universal Entry Point
Version | Author | Status

## Intent Router
[Table: Command → Orchestrator → Manifest Path → Output Spec]

## Response Format (v4.0)
[4 tiers: INSTANT/FOCUSED/STRUCTURED/COMPREHENSIVE]

## Brain Protection (SKULL)
[4 rules: TDD, Discovery, Cleanup, Git Isolation]

## Quick Reference
[Command table with descriptions]
```

### 7b. copilot-instructions.md Structure (Target: <150 lines)

```markdown
# GitHub Copilot Instructions for CORTEX
## Entry Point
→ Load CORTEX.prompt.md

## Response Format
→ Defer to CORTEX.prompt.md

## Key Workflows
[Brief list with manifest references]

## Document Organization
[Category list]
```

### 7c. Wiring Rules

1. **Single Source of Truth:** `CORTEX.prompt.md` is the intent router
2. **copilot-instructions.md:** Points TO CORTEX.prompt.md, doesn't duplicate
3. **Manifests:** All orchestrators reference their manifest file
4. **Output Specs:** Planning operations include folder structure requirement
5. **Knowledge Library:** All orchestrators must reference `cortex-brain/knowledge/` for guidelines

---

## ✅ Success Criteria

| Check | Pass Condition |
|-------|----------------|
| Health Score | ≥ 90/100 |
| Wiring Coverage | 100% |
| Knowledge Library | All 9 categories present, README current |
| Knowledge Guidelines | 30+ files with valid metadata |
| Knowledge Integration | Orchestrators reference knowledge library |
| Manifest Paths | All resolve to existing files |
| Intent Triggers | Each orchestrator has ≥3 triggers |
| CORTEX.prompt.md | <200 lines, all manifests wired |
| copilot-instructions.md | <150 lines, defers to CORTEX.prompt.md |
| Output Structures | Planning System has folder spec |
| **Interactive Planning** 🆕 | Session workflow tests 29/29 passing |
| **Vision Auto-Engagement** 🆕 | Image detection and analysis wired |
| **Test Suite Health** 🆕 | Core tests 100%, full suite ≥99% |

---

## 📋 Validation Checklist

Run during every maintenance cycle:

### Core System
- [ ] Health score ≥90
- [ ] All manifest paths resolve to existing files
- [ ] No references to deprecated `orchestrator-manifests/` path
- [ ] Each orchestrator has ≥3 trigger phrases
- [ ] Planning System has output folder structure specified
- [ ] CORTEX.prompt.md is <200 lines
- [ ] copilot-instructions.md is <150 lines
- [ ] copilot-instructions.md defers to CORTEX.prompt.md (no duplication)
- [ ] Reports folder cleaned (see Phase 9)

### Knowledge Library
- [ ] Knowledge library has all 9 categories present
- [ ] Knowledge library README.md is current (stats match actual files)
- [ ] All knowledge YAML files have valid metadata section
- [ ] All knowledge rules have valid severity levels (CRITICAL/HIGH/MEDIUM/LOW)
- [ ] No duplicate rule IDs across knowledge library
- [ ] Orchestrators reference knowledge library in code/manifests
- [ ] Brain protection rules reference knowledge library

### Interactive Planning 🆕
- [ ] Interactive session module exists (`src/orchestrators/planning/interactive_session.py`)
- [ ] SessionState enum with 8 states (INITIALIZING → FINALIZED)
- [ ] PlanningSession, DiscoveryEngine, ApprovalWorkflow, CleanupPhase classes exist
- [ ] Session state transitions validated (DISCOVERY → CONTEXT_GATHERING → USER_REVIEW → APPROVED → DRAFTING → CLEANUP → FINALIZED)
- [ ] Interactive planning tests: 29/29 passing (100%)
- [ ] End-to-end workflow test passing (full lifecycle validation)
- [ ] Conversation history tracking operational
- [ ] Iterative refinement loop functional

### Vision API Auto-Engagement 🆕
- [ ] Vision orchestrator exists (`src/tier1/vision_orchestrator.py`)
- [ ] Image detector exists (`src/tier1/image_detector.py`)
- [ ] Vision context middleware exists (`src/operations/utilities/vision_context_middleware.py`)
- [ ] Config has `auto_detect_images: true`
- [ ] Config has `auto_analyze_on_detect: true`
- [ ] Config has `auto_inject_context: true`
- [ ] Image detection works for PNG, JPG, JPEG formats
- [ ] Vision API auto-engages without user prompting
- [ ] Duplicate image caching operational (24hr TTL)
- [ ] Token budget enforcement active (500 token limit)
- [ ] Context injection into planning/debugging workflows verified

### Test Suite Health 🆕
- [ ] Core tests (interactive + toolkit): 29/29 passing (100%)
- [ ] Full planning test suite: ≥396 passing (≥99% pass rate)
- [ ] Error count: 0 (no collection or import errors)
- [ ] Test execution time: <30 seconds
- [ ] Test report generated in `cortex-brain/documents/reports/`
- [ ] Known issues documented (if any failures remain)
- [ ] Obsolete tests deleted (tests for removed/refactored APIs)

---

## Phase 9: Report Management 🗑️

**Goal:** Prevent report bloat - user won't read them, CORTEX doesn't need most of them.

### 9a. Report Policy

| Report Type | Policy | Reason |
|-------------|--------|--------|
| **Timestamped operational logs** (cleanup-*, brain-tuning-*, architectural-review-*) | DELETE | Ephemeral, no reference value |
| **Benchmark/test results** (benchmark_*, DOC_QUALITY_REPORT_*) | DELETE | Temporary test data |
| **Task completion summaries** (story-*, planning-*, feature-*) | DELETE | User won't read, redundant |
| **Duplicate analyses** (unwired-components-TIMESTAMP-*) | DELETE | Keep only latest if needed |
| **Major architecture decisions** (SYSTEM-INTEGRITY-*, MOCK-STUB-AUDIT) | KEEP | Reference for future decisions |
| **Migration/refactor summaries** (ORCHESTRATOR-*, CORTEX-CLEANUP-*) | KEEP | Historical context |

### 8b. Cleanup Commands

```bash
cd cortex-brain/documents/reports/

# Delete timestamped operational JSONs
rm -f cleanup-*.json architectural-review-*.json brain-tuning-*.json

# Delete benchmark/test JSONs
rm -f benchmark_*.json DOC_QUALITY_REPORT_*.json summary_*.json

# Delete task completion summaries
rm -f story-*.md planning-*.md feature-*.md *-complete.md

# Delete duplicate analyses (keep only one if needed)
rm -f unwired-components-2025*.json unwired-components-2025*.md

# Delete operational JSONs
rm -f git-sync-*.json validation_report.json system-alignment-report-*.json

# Verify cleanup
echo "Remaining reports: $(ls -1 | wc -l)"
du -sh .
```

### 8c. Prevention Rules

**STOP creating reports for:**
- ❌ Task completion summaries
- ❌ Incremental progress updates  
- ❌ Operational logs with timestamps
- ❌ Benchmark results (use metrics database instead)

**ONLY create reports for:**
- ✅ Major architectural decisions
- ✅ System-wide migrations/refactors
- ✅ Compliance audits (when required)
- ✅ Reference documentation (non-temporal)

### 8d. Alternative: Use Metrics Database

For tracking operational data, use `cortex-brain/analytics/metrics.db` instead of JSON reports.

---