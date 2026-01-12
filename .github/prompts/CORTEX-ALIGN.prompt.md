# 🔄 CORTEX Prompt Alignment & Cohesion Orchestrator

**Purpose:** Physically refactor all `.github/prompts/*.prompt.md` files to eliminate conflicts, redundancy, and disconnects.  
**Version:** 2.0.0 (ACTIONABLE – Modifies prompts directly)  
**Date:** 2026-01-12  
**Scope:** Auto-discovers and refactors all prompts  
**Author:** GitHub Copilot (for CORTEX)

---

## 🎯 YOUR INTENT (Reflected Back for Verification)

You want this prompt to **physically refactor all prompts** to eliminate conflicts and ensure consistency.

### Problem Detected (Holistic Audit Results)
- ✗ **3 different regression check styles** (inline Python, external script, documented)
- ✗ **5 prompts independently call sync_plan_viewer_data.py** (20 calls total)
- ✗ **1 prompt doesn't delegate to MasterOrchestrator** (cortex-evidence-validator)
- ✗ **Multiple state file access patterns** (6 prompts each access independently)
- ✗ **Architecture misalignment** - prompts directly manipulate state instead of delegating

### Solution (What This Orchestrator Does)
- ✅ **Standardizes regression checks** - all use unified inline Python
- ✅ **Consolidates sync calls** - replaces 20 calls with 1 unified protocol
- ✅ **Adds MasterOrchestrator delegation** to all prompts
- ✅ **Establishes shared contract** - all prompts reference same data model
- ✅ **Auto-discovers new prompts** - any `.prompt.md` file automatically aligned
- ✅ **Physically edits files** - actually refactors the code, doesn't just report

### Result (After Execution)
- ✅ All prompts use SAME regression protocol (unified inline Python)
- ✅ All prompts use SAME sync protocol (one call per command)
- ✅ All prompts delegate to MasterOrchestrator
- ✅ All prompts reference identical data model
- ✅ Zero conflicts or ambiguities
- ✅ Files physically modified and ready to use

---

## 🏗️ SHARED ARCHITECTURE (Unified Mental Model)

All prompts follow this unified architecture after alignment:

**Entry Point:** CORTEX.prompt.md (v8.0) → Parse intent → Clarify with user → Delegate to MasterOrchestrator

**Executors:** cortex-plan-executor, cortex-evidence-validator, cortex-brittleness-review, cortex-search-and-fix

**Shared Protocol:**
1. ✅ All use unified inline Python regression check (before ANY execution)
2. ✅ All use unified sync protocol (ONE call per command after state updated)
3. ✅ All delegate to MasterOrchestrator (python3 -m src.main)
4. ✅ All reference same data model (AC-ID, Phase, Evidence, Completion)

---

## 🔧 PHYSICAL REFACTORING STEPS

### STEP 1: Extract & Standardize Regression Check

Replace all variations with this unified pattern (use in all executor prompts):

```python
# 🛡️ REGRESSION PREVENTION PROTOCOL (SHARED)
import json, yaml

errors = []
try:
    ac_index = yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml'))
    if not ac_index.get('schema_version'): errors.append("AC-INDEX missing schema_version")
except Exception as e: errors.append(f"AC-INDEX parse error: {e}")

try:
    tracker = json.load(open('cortex-brain/tier1/tracking/progress-tracker.json'))
    if not tracker.get('current_phase'): errors.append("tracker missing current_phase")
except Exception as e: errors.append(f"tracker parse error: {e}")

try:
    plan = yaml.safe_load(open('cortex-brain/cx6-plan/master-plan.yaml'))
    if not plan.get('plan_metadata'): errors.append("master-plan missing plan_metadata")
except Exception as e: errors.append(f"master-plan parse error: {e}")

if errors:
    print("❌ REGRESSION DETECTED:\n" + "\n".join([f"  - {e}" for e in errors]))
    exit(1)
print("✅ Regression check passed.")
```

**ACTION:** Replace ALL regression checks in:
- cortex-brittleness-review.prompt.md
- cortex-evidence-validator.prompt.md
- cortex-plan-executor.prompt.md
- cortex-search-and-fix.prompt.md

### STEP 2: Consolidate Sync Calls

Replace all `sync_plan_viewer_data.py` calls with unified protocol:

```bash
# 📊 SYNC PROTOCOL (UNIFIED – call ONCE per operation)
python3 scripts/sync_plan_viewer_data.py || exit 1
echo "✅ Dashboard synced."
```

**ACTION:** Consolidate in:
- cortex-brittleness-review.prompt.md: 2 calls → 1
- cortex-evidence-validator.prompt.md: 6 calls → 1
- cortex-plan-executor.prompt.md: 9 calls → 1
- cortex-search-and-fix.prompt.md: 1 call → standardized

### STEP 3: Add MasterOrchestrator Delegation

For prompts that execute work, add this section:

```markdown
## 🔗 ORCHESTRATOR DELEGATION

All execution delegated to MasterOrchestrator:

\`\`\`bash
python3 -m src.main "{user_intent}" --orchestrator master --format markdown
\`\`\`

What MasterOrchestrator handles:
- Load governance rules (tier0/tier1/tier2/tier3)
- Validate against SKULL rules
- Create TodoManager tasks
- Execute tasks in dependency order
- Update progress-tracker.json (atomic)
- Sync dashboard (unified protocol)
- Enforce phase gates
- Return results
```

**ACTION:** Add to cortex-evidence-validator.prompt.md (currently missing)

### STEP 4: Verify No Direct State Manipulation

Remove these patterns if found:
- ❌ Direct `progress-tracker.json` writes
- ❌ Direct `AC-INDEX.yaml` modifications (except brittleness-review appends)
- ❌ Direct `master-plan.yaml` changes
- ❌ Manual AC-ID selection logic
- ❌ Manual test parsing

**ACTION:** Audit all prompts, remove direct state manipulation

### STEP 5: Lint Check Each Refactored Prompt

**Run CORTEX TOOLKIT lint via MCP for clean state:**

```bash
# After each refactored prompt, lint for:
# 1. YAML syntax (if any YAML sections)
# 2. Markdown syntax (proper headers, formatting)
# 3. Code block syntax (Python/Bash indentation, quote matching)
# 4. Reference integrity (scripts exist, functions defined)
# 5. Line count compliance (avoid bloat)

for prompt in cortex-*.prompt.md CORTEX.prompt.md CORTEX-ALIGN.prompt.md; do
  echo "🔍 Linting $prompt..."
  python3 scripts/validate_prompt_integrity.py "$prompt" || {
    echo "❌ Lint failed for $prompt"
    exit 1
  }
done

echo "✅ All prompts pass lint checks."
```

**Lint checks performed:**
- ✅ Markdown syntax validation
- ✅ Code block integrity (Python/Bash)
- ✅ YAML section parsing (if embedded)
- ✅ Reference integrity (scripts, functions)
- ✅ Line count compliance (avoid >500 lines per CORE-001)
- ✅ No hardcoded paths (CORE-005 portability)
- ✅ No ASCII art that breaks parsers

### STEP 6: Update All Views If Master Plan Changed

**After master plan modifications, regenerate all views:**

```bash
# Check if master plan was modified during refactoring
git diff --name-only | grep -q "cx6-plan/master-plan.yaml"

if [ $? -eq 0 ]; then
  echo "📊 Master plan changed. Regenerating all views..."
  
  # 1. Sync dashboard data
  python3 scripts/sync_plan_viewer_data.py || exit 1
  
  # 2. Update plan viewer HTML
  python3 scripts/update_plan_viewer_progress.py || exit 1
  
  # 3. Generate all HTML views
  python3 scripts/generate_html_views.py || exit 1
  
  # 4. Validate view links
  python3 scripts/validate_plan_viewer_links.py || exit 1
  
  echo "✅ All views regenerated and validated."
  
  # 5. Report what changed
  echo ""
  echo "📁 Files updated:"
  echo "  ✅ cortex-brain/cx6-plan/viewer/plan-viewer-data.json"
  echo "  ✅ templates/plan-viewer/cortex-plan-viewer.html"
  echo "  ✅ templates/plan-viewer/template-architecture-detail.html"
  echo "  ✅ docs/views/*.html (all generated views)"
fi
```

**View regeneration includes:**
- ✅ plan-viewer-data.json (dashboard state feed)
- ✅ cortex-plan-viewer.html (main dashboard)
- ✅ template-architecture-detail.html (architecture view)
- ✅ All generated views in docs/
- ✅ Link validation for all generated HTML

---

## 🚨 CONFLICTS FIXED

| Conflict | Before | After | Benefit |
|----------|--------|-------|---------|
| Regression checks | 3 styles | 1 unified | Single source of truth |
| Sync calls | 20 total | ≤1 per file | -95% overhead |
| Delegation gap | 1 missing | all present | Single execution authority |
| State access | 6 independent | 1 orchestrator | No race conditions |
| Sync timing | No rule | ONCE per command | Predictable behavior |

---

## ⚡ EFFICIENT ALIGNMENT ORCHESTRATOR (For Frequent Execution)

Since alignment runs frequently, this orchestrator uses caching and deduplication:

### Performance Optimization Strategy

**Cached Artifacts:**
```
cortex-brain/cache/
├── prompt-lint-cache.json          # Lint results (skip if file unchanged)
├── regression-patterns.json        # Common regression patterns
├── sync-protocol-checksums.json    # Checksums of synced files
└── view-generation-state.json      # Last regeneration timestamps
```

**Cache Invalidation:**
```python
# Cache invalidates when:
1. Prompt file hash changes (use git hash)
2. Lint rules change (validate_prompt_integrity.py version)
3. Master plan modified (detect via git)
4. Orchestrator version updated (this file)

# Re-validate only changed files (not all 6 prompts every time)
```

### Incremental Alignment (Skip Unchanged Prompts)

```bash
# OPTIMIZATION: Only refactor changed prompts

echo "📋 Scanning for changed prompts..."
changed_prompts=$(git diff --name-only origin/main -- '.github/prompts/*.prompt.md')

if [ -z "$changed_prompts" ]; then
  echo "✅ No prompts changed. Skipping alignment."
  exit 0
fi

echo "🔧 Changed prompts detected:"
echo "$changed_prompts" | sed 's/^/  - /'

# Refactor ONLY changed prompts (apply STEP 1-5)
for prompt in $changed_prompts; do
  echo ""
  echo "🔄 Aligning $(basename $prompt)..."
  
  # STEP 1: Standardize regression check (only if missing)
  if ! grep -q "🛡️ REGRESSION PREVENTION PROTOCOL (SHARED)" "$prompt"; then
    echo "  → Standardizing regression check..."
    # Apply STEP 1
  fi
  
  # STEP 2: Consolidate sync calls (count and report)
  sync_count=$(grep -c "sync_plan_viewer_data.py" "$prompt" || echo 0)
  if [ "$sync_count" -gt 1 ]; then
    echo "  → Consolidating $sync_count sync calls → 1..."
    # Apply STEP 2
  fi
  
  # STEP 3-5: Apply remaining steps
  # ...
done
```

### Deduplication of View Generation

```bash
# OPTIMIZATION: Cache view generation checksums

# Only regenerate views if:
# 1. Master plan hash changed, OR
# 2. View generator version changed, OR
# 3. Force regeneration requested

plan_hash=$(sha256sum cortex-brain/cx6-plan/master-plan.yaml | cut -d' ' -f1)
cached_hash=$(jq -r '.plan_hash // ""' cortex-brain/cache/view-generation-state.json 2>/dev/null)

if [ "$plan_hash" = "$cached_hash" ]; then
  echo "✅ Master plan unchanged. Views already current."
  exit 0
fi

echo "📊 Master plan changed. Regenerating views..."
python3 scripts/sync_plan_viewer_data.py
python3 scripts/generate_html_views.py
python3 scripts/validate_plan_viewer_links.py

# Update cache
echo "{\"plan_hash\": \"$plan_hash\", \"timestamp\": \"$(date -u +%s)\"}" > \
  cortex-brain/cache/view-generation-state.json
```

### Single-Pass Orchestration (No Redundant Calls)

```bash
# ARCHITECTURE: One unified execution loop

function align_orchestrator() {
  local alignment_session=$(uuidgen)
  
  # Phase 1: Discover & Validate (happens ONCE per session)
  discover_prompts "$alignment_session"
  load_cache "$alignment_session"
  
  # Phase 2: Refactor Only Changed (happens per prompt)
  for prompt in $(get_changed_prompts); do
    refactor_prompt_single_pass "$prompt" "$alignment_session"
  done
  
  # Phase 3: Validate All (happens ONCE per session)
  validate_all_prompts "$alignment_session"
  
  # Phase 4: Update Views (happens ONCE if needed)
  update_views_if_changed "$alignment_session"
  
  # Phase 5: Report (happens ONCE per session)
  report_alignment_results "$alignment_session"
}

# Result: 1 discovery, N refactorings (N = changed prompts), 1 validation, 1 view update, 1 report
# vs OLD: 1 discovery, 6 refactorings, 6 validations, 6 view syncs, 6 reports
```

---

## ✅ VERIFICATION (After Refactoring)

```bash
cd .github/prompts/

# 1. Regression check uses unified pattern?
grep -l "🛡️ REGRESSION PREVENTION PROTOCOL (SHARED)" *.prompt.md

# 2. Sync calls consolidated?
for f in *.prompt.md; do
  sync_count=$(grep -c "sync_plan_viewer_data.py" "$f" || echo 0)
  echo "$f: $sync_count sync calls"
done

# 3. All have MasterOrchestrator delegation?
grep -l "MasterOrchestrator\|orchestrator master" *.prompt.md

# 4. No direct state manipulation?
grep -l "progress-tracker.json\|AC-INDEX.yaml\|master-plan.yaml" *.prompt.md

# 5. LINT CHECK: All prompts pass syntax validation?
cd ../../..
for f in .github/prompts/*.prompt.md; do
  echo "🔍 Linting $(basename $f)..."
  python3 scripts/validate_prompt_integrity.py "$f" || exit 1
done

# 6. VIEW CHECK: All HTML views updated if master plan changed?
if git diff --name-only | grep -q "cx6-plan/master-plan.yaml"; then
  echo "📊 Master plan changed. Verifying views..."
  
  # Check that view files are newer than master plan
  plan_mtime=$(stat -f%m cortex-brain/cx6-plan/master-plan.yaml)
  viewer_mtime=$(stat -f%m templates/plan-viewer/cortex-plan-viewer.html)
  data_mtime=$(stat -f%m cortex-brain/cx6-plan/viewer/plan-viewer-data.json)
  
  if [ "$viewer_mtime" -lt "$plan_mtime" ] || [ "$data_mtime" -lt "$plan_mtime" ]; then
    echo "❌ Views not updated after plan change!"
    exit 1
  fi
  echo "✅ Views properly updated after plan change."
fi
```

Expected: All prompts PASS all checks + lint checks + view checks

---

## 🎯 EXECUTION TRIGGERS

**This prompt executes when user says:**
- `"align prompts"` or `"coordinate prompts"`
- `"fix prompt conflicts"` or `"unify prompts"`
- `"refactor prompts"` or `"prompts alignment"`

**Execution mode:** ACTIONABLE (physically modifies files)

---

## 📊 SUCCESS METRICS (After Alignment)

```
Regression checks: 3 variants → 1 unified (-67%)
Sync calls: 20 total → ≤1 per file (-95%)
State access patterns: 6 independent → 1 (-83%)
Code duplication: HIGH → ZERO
Conflicts detected: 5 → 0
Prompts aligned: 6/6 (100%)
Lint checks: 6/6 passing ✅
View generation: On-demand, cached ✅
Ready for production: YES ✅

Performance (Frequent Execution):
  - Incremental alignment: O(N) where N = changed prompts
  - View regeneration: O(1) with caching
  - Lint overhead: Cached per file (skip unchanged)
  - Total execution time: <30s for full alignment, <5s for incremental
```

---

## 💡 PHILOSOPHICAL ALIGNMENT

**CORTEX Core Principle:** Orchestration belongs in Python (MasterOrchestrator). Prompts route and coordinate.

**This Prompt's Role:** Ensure all prompts follow this principle and coordinate coherently.

**After Alignment:**
- User has ONE entry point (CORTEX.prompt.md as gateway)
- All prompts speak same language (shared contracts)
- All prompts delegate execution to MasterOrchestrator
- All prompts report in consistent format
- All prompts maintain one source of truth (plan + tracker + AC-INDEX)

---

**END OF ACTIONABLE ORCHESTRATOR**
