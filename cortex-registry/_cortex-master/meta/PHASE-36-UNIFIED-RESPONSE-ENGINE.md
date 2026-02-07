# Phase 36: Unified Response Language Engine — COMPREHENSIVE PLAN

**Status:** PLANNED | **Priority:** P0 | **Duration:** 18 days | **ROI:** 0.91 (HIGH)  
**Created:** 2026-02-07 | **Target Start:** 2026-02-10  
**Tests Target:** 245 | **Coverage Target:** 85% | **LOC Target:** 5,500+

---

## 📋 Quick Reference

### 9 Stages, 18 Days

| Stage | Name | Days | Tests | LOC | Dependency |
|-------|------|------|-------|-----|------------|
| **1** | Dual Header System | 1 | 10 | 80 | None |
| **2** | Template Blocks | 3 | 40 | 1,300 | Stage 1 |
| **3** | Security-First Analysis | 3 | 35 | 600 | Stage 1 |
| **4** | Intelligent Comments | 2 | 25 | 600 | Stage 1 |
| **5** | Test Quality (FLUFF) | 2 | 30 | 600 | Stage 1 |
| **6** | Hidden Issues | 2 | 25 | 550 | Stage 1 |
| **7** | Business Context | 2 | 20 | 450 | Stage 1 |
| **8** | Multi-Role Engine | 3 | 40 | 680 | Stage 2 |
| **9** | Legacy Migration + MCP | 2 | 20 | 430 | Stages 2-8 |
| **TOTAL** | | **18** | **245** | **5,500+** | |

---

## 🎯 Vision

Create a unified, role-aware, modular response language engine:

1. **Dual Headers** — Differentiate operations (CORTEX) from architecture (CORTEX Architect)
2. **Modular Templates** — 12 atomic blocks composable into 14 role-task combinations
3. **Security-First** — Proactive P0-P2 threat analysis on every request
4. **Intelligent** — Auto-generated comments, FLUFF test detection, hidden issue discovery
5. **Role-Adaptive** — ENGINEER, PM, BUSINESS, ARCHITECT, SECURITY roles
6. **Business-Focused** — Compliance implications, user impact, revenue at risk
7. **Legacy-Free** — Consolidate 5 response systems into 1, with backward compatibility
8. **Performance-Optimized** — 50% faster response generation, block-level caching

---

## 📦 New Modules (9 Files)

```
cortex/orchestrators/response/
├── template_blocks.py                    (1,000+ LOC)
├── block_composer.py                     (300+ LOC)
├── multi_role_response_engine.py         (400+ LOC)
└── role_detector.py                      (280+ LOC)

cortex/orchestrators/core/
└── security_first_analyzer.py            (600+ LOC)

cortex/orchestrators/support/
├── intelligent_comment_generator.py      (600+ LOC)
├── test_quality_analyzer.py              (600+ LOC)
├── hidden_issue_detector.py              (550+ LOC)
└── business_context_generator.py         (450+ LOC)

cortex/mcp/tools/
└── response_analysis_tools.py            (200+ LOC)
```

---

## 📊 12 Atomic Template Blocks

| Block | Purpose | Roles | Renderable Alone |
|-------|---------|-------|-----------------|
| **HeaderBlock** | Response header | All | ✅ Yes |
| **SecurityBlock** | P0-P2 findings table | ENGINEER, ARCHITECT, SECURITY | ✅ Yes |
| **TestQualityBlock** | FLUFF detection results | ENGINEER, ARCHITECT | ✅ Yes |
| **CodeIssuesBlock** | Hidden issues (perf/mem) | ENGINEER, ARCHITECT, SECURITY | ✅ Yes |
| **BusinessContextBlock** | Executive/PM summaries | PM, BUSINESS, ARCHITECT | ✅ Yes |
| **TDDPhaseBlock** | RED-GREEN-REFACTOR flow | ENGINEER, ARCHITECT | ✅ Yes |
| **MetricsBlock** | Quality, coverage, complexity | ENGINEER, ARCHITECT | ✅ Yes |
| **RiskBlock** | Risk assessment matrix | PM, ARCHITECT, SECURITY | ✅ Yes |
| **TimelineBlock** | Milestones, dates | PM, BUSINESS, ARCHITECT | ✅ Yes |
| **VerdictBlock** | Final decision, approval | All | ✅ Yes |
| **ChallengeBlock** | Design challenges, weaknesses | ARCHITECT, ENGINEER | ✅ Yes |
| **NextStepsBlock** | Recommended actions | All | ✅ Yes |

---

## 🔒 Security-First Severity Matrix

| Severity | CWE Examples | Action | Trigger |
|----------|-------------|--------|---------|
| **P0** | CWE-94, 89, 22, 78 | HARD GATE (block execution) | Every request |
| **P1** | CWE-327, 502, Auth gaps | CHALLENGE (weakness) | Every request |
| **P2** | Input validation, Error handling | ADVISORY (synthesis) | Every request |

---

## 👥 Role Profiles (5 Roles)

| Role | Code | Technical | Business | Security | Verbosity |
|------|------|-----------|----------|----------|-----------|
| **ENGINEER** | REQUIRED | MAXIMUM | MINIMAL | P0-P2 inline | HIGH |
| **ARCHITECT** | SELECTIVE | HIGH | MODERATE | P0-P1 summary | MEDIUM-HIGH |
| **PM** | OPTIONAL | MODERATE | HIGH | Risk only | MEDIUM |
| **BUSINESS** | NONE | LOW | PRIMARY | Exec summary | LOW |
| **SECURITY** | REQUIRED | MAXIMUM | MINIMAL | ALL + CWE | HIGH |

---

## 🎨 14 Role-Task Response Templates

### IMPLEMENT Task
- **Engineer**: Header + Security + TDD + Metrics + Verdict
- **PM**: Header + Timeline + Risk + Business + Verdict
- **Business**: Header + Impact + Milestones + Verdict

### AUDIT Task
- **Engineer**: Header + P0-P2 + Fixes + Metrics + Verdict
- **PM**: Header + Risk Matrix + Verdict
- **Business**: Header + Health Score + Verdict

### QUERY Task
- **Engineer**: Header + Technical + Evidence + Verdict
- **PM**: Header + Summary + Verdict
- **Business**: Header + Plain Language + Verdict

### PLAN Task
- **Engineer**: Header + Phase Detail + Effort + Verdict
- **PM**: Header + Roadmap + Risks + Verdict
- **Business**: Header + Strategic Value + Verdict

### DEBUG Task
- **Engineer**: Header + Stack Trace + Root Cause + Verdict
- **PM**: Header + Impact + Timeline + Verdict

### SECURITY Task
- **Security**: Header + All Security + Tests + Verdict

---

## 🧪 Test Distribution (245 Total)

| Stage | Tests | Coverage |
|-------|-------|----------|
| Stage 1 | 10 | Dual headers |
| Stage 2 | 40 | Template blocks, composition, caching |
| Stage 3 | 35 | Security analysis, P0/P1/P2 classification |
| Stage 4 | 25 | Comment generation, 5 types |
| Stage 5 | 30 | FLUFF detection, 6 patterns |
| Stage 6 | 25 | Hidden issues, 5 categories |
| Stage 7 | 20 | Business context, 3 views |
| Stage 8 | 40 | Role detection, composition, verbosity |
| Stage 9 | 20 | Legacy migration, MCP tools |

**Target:** 85% code coverage across all modules

---

## 💾 Legacy Migration (5 Systems → 1)

| Legacy System | Current File | Migration Strategy | Backward Compat |
|---------------|-------------|-------------------|-----------------|
| TurnResponseGenerator | `turn_response_generator.py` | Adapter pattern | ✅ 100% |
| ResponseFormattingEngine | `response_formatting_engine.py` | Consolidate with Composer | ✅ 100% |
| ResponseTemplateEngine | `response_templates.py` | BlockComposer | ✅ 100% |
| UXOptimizer | `ux_optimizer.py` | VerbosityCalibrator | ✅ 100% |
| TurnResponseWithChallenges | `turn_response_with_challenges.py` | ChallengeBlock | ✅ 100% |

**Result:** Zero code duplication (CORE-035), cleaner codebase

---

## 🛠️ 4 New MCP Tools

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `cortex_analyze_security` | Security P0-P2 analysis | Code scope | SecurityFirstAnalysis |
| `cortex_analyze_test_quality` | FLUFF test detection | Test file(s) | TestQualityAnalysis |
| `cortex_detect_hidden_issues` | Perf/memory/concurrency | Code scope | HiddenIssueList |
| `cortex_compose_response` | Role-aware composition | Role, task, context | RoleOptimizedResponse |

---

## 📈 Key Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Response Generation Time** | 3.0 seconds | 1.5 seconds | 50% faster ⚡ |
| **Template Systems** | 5 implementations | 1 unified engine | -80% code |
| **Template Reuse** | Manual combinations | 14 templates from 12 blocks | 85% code reduction |
| **Code Coverage** | 72% | 85% | +13% 📈 |
| **Test Count** | 1,200 | 1,445 | +245 tests |
| **Time to Add Role** | 2 days | 4 hours | 12x faster 🚀 |

---

## 📋 Success Criteria

**Functional:**
- ✅ Dual header system operational
- ✅ 12 blocks independently testable
- ✅ Block composition engine working
- ✅ Security analysis P0/P1/P2 classification
- ✅ FLUFF detection >80% accurate
- ✅ Hidden issue detection >75% accurate
- ✅ Multi-role adaptation working
- ✅ Role detection >85% accurate
- ✅ 14 templates functional
- ✅ Legacy migration with backward compat
- ✅ 4 MCP tools operational

**Quality:**
- ✅ 245 tests passing (100%)
- ✅ 85% code coverage
- ✅ CORE-008: TDD enforced
- ✅ CORE-035: Zero duplication
- ✅ No security regressions
- ✅ No breaking changes

---

## 📅 Timeline (18 Days)

**Week 1:** Stages 1-3 (Headers, Blocks, Security-First)  
**Week 2:** Stages 4-5 (Comments, Test Quality)  
**Week 3:** Stages 6-7 (Hidden Issues, Business Context)  
**Week 4:** Stages 8-9 (Multi-Role, Migration + MCP)

**Buffer:** 2 days for integration, testing, cleanup

---

## 🎯 Execution Checklist

- [ ] Create phase-36-unified-response-engine.yaml ✅ DONE
- [ ] Register in index.yaml ✅ DONE
- [ ] Approval to begin Stage 1
- [ ] Complete all 9 stages
- [ ] All 245 tests passing
- [ ] 85% coverage validated
- [ ] Legacy migration complete
- [ ] MCP tools operational
- [ ] Migration guide published
- [ ] Phase completion dashboard updated

---

## 📚 References

- **Full Plan:** `cortex-registry/_cortex-master/phases/active/phase-36-unified-response-engine.yaml`
- **Response Format Spec:** `cortex-registry/_cortex-master/meta/response-format.yaml`
- **Decision Authority:** `chat01.txt` (Phase 36 session analysis)
- **Prompt Authority:** `cortex-architect.prompt.md v15.0`

---

**Ready for TDD Kickoff: Stage 1 → Stage 2 → ... → Stage 9**
