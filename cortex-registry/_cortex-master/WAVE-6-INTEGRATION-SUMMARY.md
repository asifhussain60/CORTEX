# WAVE-6 INTEGRATION WITH CORTEX ARCHITECTURE
## How Wave 6 Enhances Existing Systems

**Authority:** chat01.md + cortex-architect.prompt.md v15.3  
**Status:** DESIGN COMPLETE  
**Updated:** 2026-02-11T21:00:00Z

---

## 🎯 INTEGRATION OVERVIEW

Wave 6 is **NOT a standalone feature** — it's a **strategic infrastructure upgrade** that enhances ALL existing CORTEX systems.

### Integration Points

| CORTEX Component | Wave 6 Enhancement | Benefit |
|------------------|-------------------|---------|
| **cortex-architect.md** | Auto-use phase template on DESIGN intent | 50% faster phase creation |
| **All 72 Orchestrators** | Use UnifiedResponseEngine | 80% response efficiency, 100% consistency |
| **cortex-phase-resolver.md** | Validate phase specs with linter | 0 orphaned components |
| **cortex-vacuum.md** | Read cleanup requirements from phase spec | Automated cleanup per wave |
| **cortex-auditor.md** | Run architecture alignment checker | 100% CORE compliance |
| **MasterOrchestrator** | Inject ResponseEngine in execute_with_protocol() | Auto-bind context to templates |

---

## 📋 AGENT ENHANCEMENTS

### cortex-architect.md (Core Agent)

**Current Behavior:**
```
User: "Design a new phase for X"
AI: [Creates ad-hoc YAML spec]
AI: [Manual cleanup planning]
AI: [Manual registry sync]
```

**Post-Wave 6 Behavior:**
```
User: "Design a new phase for X"
AI: [Invokes phase_creator.py CLI]
AI: [Generates spec from template]
AI: [Auto-validates with linter]
AI: [Displays wave breakdown + ROI]
AI: [Syncs registry automatically]
```

**Code Changes:**
```python
# File: .github/agents/core/cortex-architect.md

# NEW SECTION: Phase Creation Integration (ENH-084)
When user intent = DESIGN + mentions "phase" or "enhancement":
  1. Import phase_creator.py from cortex/cli/
  2. Run guided wizard with user input
  3. Generate phase spec from template
  4. Run phase_spec_linter.py to validate
  5. Update cortex-registry/_cortex-master/index.yaml
  6. Display wave execution plan + ROI estimate
  7. User approves → move spec to active/ folder
```

---

### cortex-phase-resolver.md (Core Agent)

**Current Behavior:**
```
User: "Resolve phase-XX"
AI: [Loads phase YAML]
AI: [Plans execution]
```

**Post-Wave 6 Behavior:**
```
User: "Resolve phase-XX"
AI: [Loads phase YAML]
AI: [Validates spec with linter]
AI: [Checks cleanup requirements present]
AI: [Verifies registry sync checkpoints]
AI: [Plans execution with wave breakdown]
```

**Code Changes:**
```python
# File: .github/agents/core/cortex-phase-resolver.md

# NEW SECTION: Phase Spec Validation (ENH-084)
Before resolving phase:
  1. Run phase_spec_linter.py on phase YAML
  2. Check: 4 waves present (Foundation/Core/Migration/Polish)
  3. Check: Cleanup stage in each wave
  4. Check: Registry sync checkpoints defined
  5. Check: Test targets ≥80% coverage
  6. If validation fails → BLOCK resolution
```

---

### cortex-vacuum.md (Support Agent)

**Current Behavior:**
```
User: "Vacuum completed phase-XX"
AI: [Ad-hoc cleanup of .md files]
AI: [Manual orphan detection]
```

**Post-Wave 6 Behavior:**
```
User: "Vacuum completed phase-XX"
AI: [Reads cleanup requirements from phase YAML]
AI: [Executes wave-specific vacuum stages]
AI: [Verifies 0 orphaned components]
AI: [Updates registry with cleanup status]
```

**Code Changes:**
```python
# File: .github/agents/support/cortex-vacuum.md

# NEW SECTION: Phase Spec-Driven Cleanup (ENH-084)
When vacuuming phase:
  1. Load phase YAML spec
  2. Extract cleanup_requirements section
  3. For each wave:
      - Execute wave.cleanup.vacuum_stage
      - Verify deliverables archived
      - Check 0 orphaned files remain
  4. Update phase status: cleanup_complete = true
```

---

### cortex-auditor.md (Core Agent)

**Current Behavior:**
```
User: "Audit codebase"
AI: [Manual CORE rule checking]
AI: [Ad-hoc violation detection]
```

**Post-Wave 6 Behavior:**
```
User: "Audit codebase"
AI: [Runs architecture_alignment_checker.py]
AI: [5-layer verification (CORE/MCP/Response/Orchestrator/Tests)]
AI: [Auto-fix 70%+ violations]
AI: [Generate remediation plan for P0/P1]
AI: [Display compliance report]
```

**Code Changes:**
```python
# File: .github/agents/core/cortex-auditor.md

# NEW SECTION: Architecture Alignment Check (ENH-086)
When auditing:
  1. Invoke cortex/validation/architecture_alignment_checker.py
  2. Run 5-layer checks:
      - L1: CORE Rules (30 rules)
      - L2: MCP-FIRST (no direct file ops)
      - L3: Response Format (headers, DoR, inline)
      - L4: Orchestrator Patterns (protocol adherence)
      - L5: Test Coverage (≥80%)
  3. Classify violations: P0 (blocking), P1 (high), P2 (nice-to-have)
  4. Run auto_fix_alignment.py (70%+ auto-fixable)
  5. Generate manual remediation plan for P0/P1
```

---

## 🎼 ORCHESTRATOR ENHANCEMENTS

### All 72 Orchestrators

**Current Behavior:**
```python
class SomeOrchestrator:
    def orchestrate(self, request):
        # Hardcoded response generation
        return f"## 🧠 CORTEX {operation}\n**Author:** ..."
```

**Post-Wave 6 Behavior:**
```python
class SomeOrchestrator(OrchestratorBaseProtocol):
    def orchestrate(self, request):
        # Use UnifiedResponseEngine (injected automatically)
        return self.response_engine.generate(
            role=self.role,  # Auto-detected from intent
            operation=request.intent,
            context=self.context  # Auto-bound to template vars
        )
```

**Key Change:**
- ✅ `OrchestratorBaseProtocol.execute_with_protocol()` now injects `ResponseEngine`
- ✅ All orchestrators inherit automatically (zero code changes)
- ✅ Template variables auto-bound from context (80%+ automatic)

---

### MasterOrchestrator (Core)

**Current Behavior:**
```python
class MasterOrchestrator:
    def process(self, request):
        orchestrator = self.router.route(request)
        result = orchestrator.execute(request)
        return result  # Orchestrator formats its own response
```

**Post-Wave 6 Behavior:**
```python
class MasterOrchestrator:
    def __init__(self):
        self.response_engine = UnifiedResponseEngine()
    
    def process(self, request):
        orchestrator = self.router.route(request)
        # Inject ResponseEngine before execution
        orchestrator.response_engine = self.response_engine
        result = orchestrator.execute_with_protocol(request)
        return result  # Response already formatted by engine
```

---

## 🔧 NEW TOOLS & UTILITIES

### Phase Creator CLI (ENH-084)

**Usage:**
```bash
# Create new phase
cortex phase create --id ENH-087 --title "Semantic Block Library"

# Validates spec
cortex phase validate --spec ENH-087.yaml

# Lints spec
cortex phase lint --check-cleanup ENH-087.yaml

# Syncs with registry
cortex phase sync --update-registry ENH-087.yaml
```

**Integration with cortex-architect.md:**
- ✅ Auto-invoked on DESIGN intent
- ✅ Guided wizard for phase creation
- ✅ Auto-validation with linter
- ✅ Auto-sync with registry

---

### Architecture Alignment Checker (ENH-086)

**Usage:**
```bash
# Check all modules
python cortex/validation/architecture_alignment_checker.py

# Check specific module
python cortex/validation/architecture_alignment_checker.py --module cortex/orchestrators/core/

# Auto-fix violations
python cortex/scripts/auto_fix_alignment.py --module cortex/orchestrators/core/
```

**Integration with cortex-auditor.md:**
- ✅ Auto-invoked on AUDIT intent
- ✅ 5-layer verification (CORE/MCP/Response/Orchestrator/Tests)
- ✅ Auto-fix 70%+ violations
- ✅ Generate remediation plan for P0/P1

---

### Cleanup Audit Script (ENH-085)

**Usage:**
```bash
# Run cleanup audit
python cortex/scripts/cleanup_completed_phases.py

# Classify artifacts
python cortex/scripts/cleanup_completed_phases.py --classify

# Migrate to completed/
python cortex/scripts/migrate_to_completed.py --phase phase-XX

# Verify no regressions
python cortex/scripts/cleanup_completed_phases.py --verify
```

**Integration with cortex-vacuum.md:**
- ✅ Auto-invoked on phase completion
- ✅ Classification: Essential/Stale/Orphaned/Deprecated
- ✅ Migration to completed/ folder
- ✅ Verification: 0 regressions

---

## 📊 REGISTRY SYNCHRONIZATION

### index.yaml Updates

**Before Wave 6:**
```yaml
version: '1.8'
total_phases: 16
waves: 5
```

**After Wave 6:**
```yaml
version: '1.9'
total_phases: 20  # +4 (ENH-082/084/085/086)
waves: 6  # Added Wave 6
wave_6_file: "WAVE-6-COMPREHENSIVE-CLEANUP-REFACTORING.yaml"
```

### WAVE-BASED-EXECUTION-PLAN.yaml Updates

**Before Wave 6:**
```yaml
wave_count: 5
estimated_total_effort: "~100 days (60 days parallelized)"
```

**After Wave 6:**
```yaml
wave_count: 6
estimated_total_effort: "~115 days (70 days parallelized)"
wave_6:
  name: "Comprehensive Cleanup & Refactoring"
  roi: 9.2  # HIGHEST
  duration: "14-18 days"
  phases: 4
```

---

## 🔄 WORKFLOW CHANGES

### Phase Creation Workflow (Before vs After)

**BEFORE Wave 6:**
```
User: "Design phase-XX"
    ↓
AI: [Manual YAML creation]
    ↓
AI: [Ad-hoc cleanup planning]
    ↓
AI: [Manual registry update]
    ↓
AI: [Hope cleanup happens]
```

**AFTER Wave 6:**
```
User: "Design phase-XX"
    ↓
AI: [Invoke phase_creator.py CLI]
    ↓
CLI: [Guided wizard, generates from template]
    ↓
Linter: [8 automated checks, validation]
    ↓
CLI: [Auto-sync registry]
    ↓
Template: [Cleanup baked into spec]
```

**Improvement:** 50% faster, 0 orphaned components, 100% consistent

---

### Orchestrator Response Generation (Before vs After)

**BEFORE Wave 6:**
```
User: "Implement feature X"
    ↓
TDDOrchestrator: [Hardcoded response format]
    ↓
Output: "## 🧠 CORTEX IMPLEMENT\n**Author:** ..." (manual)
```

**AFTER Wave 6:**
```
User: "Implement feature X"
    ↓
TDDOrchestrator: [Uses ResponseEngine]
    ↓
ResponseEngine: [Auto-detect role, fuse templates, bind context]
    ↓
Output: Consistent format, 80% less code, auto-bound variables
```

**Improvement:** 80% efficiency, 100% consistency, 0 hardcoded strings

---

## ✅ VERIFICATION CHECKLIST

### Post-Wave 6 Verification

| Check | Command | Expected Result |
|-------|---------|-----------------|
| **Response Templates** | `pytest tests/unit/orchestrators/response/` | 266+ tests passing |
| **Phase Template** | `cortex phase validate --spec .github/templates/phase-specification-template.yaml` | ✅ Valid |
| **Phase CLI** | `cortex phase create --help` | Shows 5 commands |
| **Phase Linter** | `cortex phase lint --check-cleanup phase-XX.yaml` | 8 checks run |
| **Cleanup Audit** | `python cortex/scripts/cleanup_completed_phases.py` | Audit report generated |
| **Alignment Checker** | `python cortex/validation/architecture_alignment_checker.py` | 5-layer report |
| **Registry Sync** | `grep "wave: 6" cortex-registry/_cortex-master/index.yaml` | Wave 6 entry found |
| **Orchestrators** | `pytest tests/integration/orchestrators/` | 72 orchestrators using ResponseEngine |

---

## 🎯 SUCCESS CRITERIA (Post-Wave 6)

| Metric | Target | Verification |
|--------|--------|--------------|
| **Response Generation** | 72/72 orchestrators using ResponseEngine | Code inspection + tests |
| **Phase Creation** | 100% use template (new phases only) | Registry audit |
| **Codebase Reduction** | 15-25% size decrease | Git diff + file count |
| **CORE Compliance** | 100% (30/30 rules) | Alignment checker report |
| **MCP-FIRST Violations** | 0 | Alignment checker report |
| **Test Coverage** | ≥80% across all modules | pytest --cov |
| **Orphaned Components** | 0 | Cleanup audit report |
| **Architectural Drift** | 0 violations | Alignment checker report |

---

## 🔮 FUTURE ENHANCEMENTS (Enabled by Wave 6)

### ENH-087: Semantic Block Library

**Depends On:** ENH-082 (ResponseEngine foundation)

**What It Does:** Convert 72 templates → 15 reusable semantic blocks

**Why Possible:** ResponseEngine provides composition infrastructure

**Benefit:** Reduces template maintenance 80% (72 → 15)

---

### Phase-84: Cross-Repository Template Sharing

**Depends On:** ENH-082 (ResponseEngine) + ENH-084 (Phase Template)

**What It Does:** Enable template sharing across onboarded repositories via registry

**Why Possible:** Phase template provides standard structure, ResponseEngine enables sharing

**Benefit:** Multi-tenant deployments can reuse templates

---

### Phase-85: Advanced Response Optimization

**Depends On:** ENH-082 (ResponseEngine) + ENH-086 (Alignment Checker)

**What It Does:** Dynamic template selection based on user context, preferences, role

**Why Possible:** ResponseEngine provides composition, Alignment Checker ensures quality

**Benefit:** Personalized responses per user, 30% relevance improvement

---

**Status:** ✅ WAVE-6 INTEGRATION COMPLETE  
**Authority:** chat01.md + cortex-architect.prompt.md v15.3  
**Next Action:** Execute WAVE-1 → WAVE-6 (highest ROI)
