# CORTEX Review System v4.0 - Quick Start Guide

**Purpose:** Run live implementation review against cortex-impl-map.yaml roadmap  
**Time:** 3-4 hours  
**Output:** Consolidated gap report ready for remediation  

---

## 🎯 QUICK START (3 Steps)

### Step 1: Understand the Review System
```bash
# Read the main review orchestrator
cat .github/prompts/cortex-review.prompt.md

# This file explains:
# - Phase 1: Gap Inventory (15 min)
# - Phase 2: Stub Detection (20 min)
# - Phase 3: Brittleness Analysis (45 min, 5 agents parallel)
# - Phase 4: Requirements Validation (10 min)
# - Phase 5: Consolidated Report (20 min)
```

### Step 2: Read Agent Frameworks
```bash
# Each agent handles one aspect of code quality

# Brittleness: Load handling, concurrency, error handling
cat .github/agents/cortex-review-brittleness.md

# Hallucination: AI safety, injection vectors, validation
cat .github/agents/cortex-review-hallucination.md

# Governance: CORE rule compliance, audit trails
cat .github/agents/cortex-review-governance.md

# Assumptions: Platform, Python version, dependencies
cat .github/agents/cortex-review-assumptions.md

# Debt: Code duplication, over-engineering, test gaps
cat .github/agents/cortex-review-debt.md
```

### Step 3: Execute Review Phases
```bash
# Phase 1: Analyze status in cortex-impl-map.yaml
# - Count COMPLETED vs actual implementation
# - Output: _workspaces/roadmap/issues/review-gap-inventory-YYYYMMDD.yaml

# Phase 2: Detect stubs
grep -rn "raise NotImplementedError" cortex/ --include="*.py"
grep -rn "^\s*pass\s*$" cortex/ --include="*.py" | grep -B 2 "def "
# - Output: _workspaces/roadmap/issues/review-stubs-YYYYMMDD.yaml

# Phase 3: Run 5 agents (can be parallel)
# Use findings from agent files to manually inspect code
# - Output: _workspaces/roadmap/issues/findings-{brittleness,hallucination,...}.yaml

# Phase 4: Validate requirements
grep -rh "^import\|^from" cortex/ --include="*.py" | sort -u > /tmp/imports.txt
diff /tmp/imports.txt requirements.txt
# - Already updated with 12 new packages
# - Output: _workspaces/roadmap/reports/requirements-analysis-YYYYMMDD.yaml

# Phase 5: Consolidate all findings
# - Output: _workspaces/roadmap/reports/review-findings-consolidated-YYYYMMDD.yaml
```

---

## 📊 WHAT YOU'LL FIND

### Gap Categories

**Type 1: FALSE COMPLETED**
```yaml
phase: "impl-governance-001-context-aware"
claim: "COMPLETED"
reality: "Only 1 of 29 rules implemented"
impact: "CRITICAL - governance broken"
```

**Type 2: STUBS (Code That Doesn't Work)**
```yaml
file: "cortex/infrastructure/graceful_degradation.py:54"
code: "raise NotImplementedError"
impact: "HIGH - fallback strategies crash"
```

**Type 3: BRITTLENESS (Works but Fragile)**
```yaml
issue: "Connection pool exhaustion"
impact: "HIGH - system hangs on pool saturation"
remediation: "Add timeout and fallback"
```

**Type 4: GOVERNANCE VIOLATIONS**
```yaml
rule: "CORE-008 (Tests before code)"
violation: "Function without test file"
severity: "CRITICAL"
```

**Type 5: ASSUMPTIONS**
```yaml
assumption: "Python 3.10+ features"
reality: "requirements.txt says 3.9+"
impact: "Code fails on Python 3.9"
```

---

## 📁 OUTPUT FILE LOCATIONS

**Gap Analysis:**
```
_workspaces/roadmap/issues/review-gap-inventory-YYYYMMDD.yaml
_workspaces/roadmap/issues/review-stubs-YYYYMMDD.yaml
```

**Agent Findings:**
```
_workspaces/roadmap/issues/findings-brittleness-YYYYMMDD.yaml
_workspaces/roadmap/issues/findings-hallucination-YYYYMMDD.yaml
_workspaces/roadmap/issues/findings-governance-YYYYMMDD.yaml
_workspaces/roadmap/issues/findings-assumptions-YYYYMMDD.yaml
_workspaces/roadmap/issues/findings-debt-YYYYMMDD.yaml
```

**Requirements & Summary:**
```
_workspaces/roadmap/reports/requirements-analysis-YYYYMMDD.yaml
_workspaces/roadmap/reports/review-findings-consolidated-YYYYMMDD.yaml
```

---

## 🔧 WHAT CHANGED

### 1. Review System (Completely Rewritten)
**Before (v3.1):**
- Chat-based analysis (Chat01 had false positives)
- No systematic stub detection
- No gap inventory against roadmap
- Relied on speculation

**After (v4.0):**
- Live code inspection against cortex-impl-map.yaml
- Systematic stub detection (NotImplementedError, pass statements)
- 5 specialized agents running in parallel
- Direct code evidence (A/B/C confidence grades only)

### 2. Agent Files (All New)
5 comprehensive agent frameworks:
- `.github/agents/cortex-review-brittleness.md` (NEW)
- `.github/agents/cortex-review-hallucination.md` (NEW)
- `.github/agents/cortex-review-governance.md` (NEW)
- `.github/agents/cortex-review-assumptions.md` (NEW)
- `.github/agents/cortex-review-debt.md` (NEW)

Each includes:
- What to look for
- Search commands
- Example violations
- Output format
- Decision tree
- Validation checklist

### 3. Requirements Update
**Added 12 new packages:**
```
anthropic==0.7.11         # AI integration (brain)
openai==1.3.9             # AI integration (alternatives)
sqlalchemy==2.0.23        # ORM (persistence)
alembic==1.12.1           # Migrations (schema versioning)
psycopg2-binary==2.9.9    # PostgreSQL (production DB)
cryptography==41.0.7      # Crypto (hash chains)
python-jose==3.3.0        # JWT (tokens)
pycryptodome==3.19.0      # Crypto primitives (extensions)
greenlet==3.0.1           # Concurrency (lightweight threads)
gevent==23.9.1            # Concurrency (async events)
structlog==23.2.0         # Structured logging (audit trails)
python-json-logger==2.0.7 # JSON logging (machine parsing)
```

**Why added:**
- These are required for full CORTEX operation
- Brain tier depends on AI packages
- Audit trail requires crypto and structured logging
- Resilience requires concurrency primitives
- Production deployment requires ORM and migrations

---

## ⚠️ KEY DIFFERENCES FROM PREVIOUS REVIEW

| Question | v3.1 | v4.0 |
|----------|------|------|
| How do you know a phase is COMPLETED? | Assumes it is | Verifies against code |
| How do you detect stubs? | Manual search | Systematic inventory |
| What if code is broken? | Chat analyzed anyway | Gap report documents it |
| How do you handle timing issues? | Checked during execution | Checked after persistence |
| Can you regenerate code blindly? | Yes (caused issues) | No - findings guide remediation |
| How long does review take? | 6-8 hours | 3-4 hours (parallel agents) |
| How do you prevent false positives? | By reviewing manually | By direct code inspection + evidence grading |

---

## 🚀 AFTER THE REVIEW

Once you have `review-findings-consolidated-YYYYMMDD.yaml`:

1. **Identify CRITICAL Gaps** (blocks all features)
2. **Sort by Severity** (CRITICAL → HIGH → MEDIUM → LOW)
3. **Map to Remediation** (send findings to cortex-builder.prompt.md)
4. **Execute Implementation** (TDD-based, phase-by-phase)
5. **Verify Completeness** (run review again to confirm)

---

## 📞 TROUBLESHOOTING

**Q: Review took longer than 3-4 hours**
A: Running agents sequentially instead of parallel. Use `&` to background them.

**Q: Too many findings - where do I start?**
A: Sort by severity. CRITICAL items block all features - fix those first.

**Q: Finding seems wrong - code looks correct**
A: Check the evidence. If evidence is A-grade (95%+ confidence), investigate why your reading differs. If evidence is B/C-grade (lower confidence), treat as advisable, not mandatory.

**Q: Can I skip Phase X?**
A: No. Each phase builds on previous:
- Phase 1 (gaps) → Phase 2 (stubs) → Phase 3 (quality) → Phase 4 (deps) → Phase 5 (report)

**Q: Requirements.txt already has these packages, why add more?**
A: Review identified that these packages are REQUIRED for full operation but were marked OPTIONAL. They're now mandatory.

---

## ✅ SUCCESS CRITERIA

Review is successful when:
- [ ] Gap inventory completed (all claimed phases verified)
- [ ] Stub inventory completed (all incomplete code identified)
- [ ] Agent findings consolidated (5 agent outputs merged)
- [ ] Requirements updated (12 new packages verified/working)
- [ ] Consolidated report generated (ready for remediation)

---

## 📖 READING ORDER

1. **Start here:** This file (quick start guide)
2. **Then read:** .github/prompts/cortex-review.prompt.md (main orchestrator)
3. **Understand agents:** .github/agents/cortex-review-*.md (5 agents)
4. **Check updates:** requirements.txt (12 new packages)
5. **Review summary:** docs/CORTEX-REVIEW-SYSTEM-V4-SUMMARY.md (overview)

---

**Version 4.0** - Live Implementation Review System  
**Created:** January 23, 2026  
**Status:** Ready for execution ✅
