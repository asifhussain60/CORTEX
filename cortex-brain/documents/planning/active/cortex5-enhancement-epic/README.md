# CORTEX5 Enhancement Epic - Quick Start Guide

**Epic Version:** 2.0.0  
**Status:** 🟢 ACTIVE  
**Last Updated:** 2026-01-06

---

## 🎯 What is This Epic?

**CORTEX5 Enhancement Epic** transforms CORTEX from a single-purpose Python orchestration system into an **extensible business intelligence platform** with:

- **Company Knowledge Extension:** Pluggable company-specific knowledge (architecture, tech stack, APIs, standards)
- **Custom Orchestrator Registry:** Business-specific orchestrators (e.g., Selenium→Playwright converter)
- **Intelligent Override System:** Company knowledge overrides CORTEX defaults without corruption
- **Rule Layering:** Core + Company + Domain governance rules merge intelligently

**Timeline:** 9 weeks | **Phases:** 11 (3 parallel tracks) | **Complexity:** Tier 5 (Architectural)

---

## 🚀 Quick Start (5 Minutes)

### For Implementers

1. **Read the Master Plan:**
   ```
   Open: 00-cortex5-epic.md
   ```

2. **Understand Current State:**
   ```
   Open: context/discovery.md
   Read: analysis/gap-analysis.md
   ```

3. **Start Phase 1:**
   ```
   Open: phases/phase-01-knowledge-extension.md
   Follow: Implementation steps 1-10
   ```

4. **Track Progress:**
   ```
   Update: tracking/progress-tracker.json after each task
   Check: tracking/snowball.md for momentum
   ```

### For Reviewers

1. **High-Level Overview:**
   ```
   Read: 00-cortex5-epic.md (Executive Summary)
   Review: analysis/architectural-impact.md
   ```

2. **Risk Assessment:**
   ```
   Read: analysis/risk-assessment.md
   Verify: Mitigations are in place
   ```

3. **Phase Validation:**
   ```
   For each phase: Check reports/validation/phase-{N}-validation.md
   ```

### For GitHub Copilot

**To continue this epic:**
```
Continue CORTEX5 enhancement epic from phase {current_phase}
```

**To validate:**
```
Validate CORTEX5 epic progress for phase {phase_number}
```

**To generate code:**
```
Generate {component} for CORTEX5 epic phase {phase_number}
```

---

## 📁 File Navigation

### Essential Documents (Read First)

| Document | Purpose | Read Time |
|----------|---------|-----------|
| `00-cortex5-epic.md` | Master plan (complete overview) | 15 min |
| `analysis/gap-analysis.md` | Current vs. target gaps | 5 min |
| `context/discovery.md` | Workspace context | 5 min |
| `phases/phase-01-knowledge-extension.md` | First implementation phase | 10 min |

### Phase Documents (Implementation Order)

**Track 1: Core Intelligence (Weeks 1-4)**
1. `phases/phase-01-knowledge-extension.md` - Company knowledge layer
2. `phases/phase-02-orchestrator-registry.md` - Registry system
3. `phases/phase-03-goal-detection.md` - Intelligent goal detection
4. `phases/phase-04-knowledge-merge.md` - Merge & override logic

**Track 2: Business Extensibility (Weeks 5-7)**
5. `phases/phase-05-custom-framework.md` - Custom orchestrator framework
6. `phases/phase-06-selenium-playwright.md` - Reference implementation
7. `phases/phase-07-rule-layering.md` - Governance layering

**Track 3: Quality & UX (Weeks 5-7)**
8. `phases/phase-08-tdd-harness.md` - TDD test harness
9. `phases/phase-09-plan-viewer.md` - Plan viewer modernization
10. `phases/phase-10-response-templates.md` - Template optimization

**Track 4: Validation (Weeks 8-9)**
11. `phases/phase-11-integration.md` - End-to-end integration testing

### Analysis Documents (Context)

| Document | Purpose |
|----------|---------|
| `analysis/gap-analysis.md` | Current state vs. target state gaps |
| `analysis/architectural-impact.md` | System-wide impact assessment |
| `analysis/risk-assessment.md` | Risk identification & mitigation strategies |

### Context Documents (Discovery)

| Document | Purpose |
|----------|---------|
| `context/discovery.md` | Workspace context discovery |
| `context/architecture-analysis.md` | Current architecture deep dive |
| `context/dependency-mapping.md` | Phase dependencies & execution order |

### Tracking Documents (Progress)

| Document | Purpose |
|----------|---------|
| `tracking/progress-tracker.json` | Real-time progress (machine-readable) |
| `tracking/snowball.md` | Snowball effect momentum tracking |
| `tracking/CONTINUATION-PROMPT.md` | Resume guidance for GitHub Copilot |

---

## 🏗️ Epic Architecture (Visual)

### Current State (CORTEX 5.1)

```
┌─────────────────────────────────────────────┐
│           User Request                      │
└───────────────┬─────────────────────────────┘
                │
        ┌───────▼────────┐
        │ Master Orch v7 │ (hardcoded patterns)
        └───────┬────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼───┐   ┌───▼───┐   ┌───▼───┐
│ TDD   │   │ Plan  │   │ ADO   │  ... (10 core orchestrators)
└───┬───┘   └───┬───┘   └───┬───┘
    │           │           │
    └───────────┼───────────┘
                │
        ┌───────▼────────┐
        │ CORTEX Knowledge│ (Python-only)
        └────────────────┘
```

### Target State (CORTEX 5.2)

```
┌─────────────────────────────────────────────┐
│           User Request                      │
└───────────────┬─────────────────────────────┘
                │
        ┌───────▼────────┐
        │ Master Orch v7 │ (registry-based)
        └───────┬────────┘
                │
    ┌───────────┼──────────────────┐
    │           │                  │
┌───▼───┐   ┌───▼────────┐   ┌────▼──────────┐
│ Core  │   │ Core       │   │ Custom        │
│ Orch  │   │ Orch       │   │ Orch          │
│ (TDD) │   │ (Planning) │   │ (Selenium→PW) │
└───┬───┘   └───┬────────┘   └────┬──────────┘
    │           │                  │
    └───────────┼──────────────────┘
                │
    ┌───────────▼──────────────┐
    │  Knowledge Extension     │
    ├──────────────────────────┤
    │ CORTEX Core (immutable)  │
    │ Company ABC (pluggable)  │
    │ Company XYZ (pluggable)  │
    └──────────────────────────┘
                │
    ┌───────────▼──────────────┐
    │   Rule Layering          │
    ├──────────────────────────┤
    │ Core Rules (TDD, Git)    │
    │ Company Rules (Standards)│
    │ Domain Rules (PCI, HIPAA)│
    └──────────────────────────┘
```

---

## 📊 Progress Tracking

### Epic Progress (Overall)

**Current Phase:** Phase 1 (Knowledge Extension Layer)  
**Completion:** 0% (0/11 phases complete)  
**Timeline:** On track (Week 1 of 9)

### Phase Status

| Phase | Name | Status | Progress | ETA |
|-------|------|--------|----------|-----|
| 1 | Knowledge Extension | 🟡 Not Started | 0% | Week 2 |
| 2 | Orchestrator Registry | 🟡 Not Started | 0% | Week 3 |
| 3 | Goal Detection | 🟡 Not Started | 0% | Week 3 |
| 4 | Knowledge Merge | 🟡 Not Started | 0% | Week 4 |
| 5 | Custom Framework | 🟡 Not Started | 0% | Week 6 |
| 6 | Selenium→Playwright | 🟡 Not Started | 0% | Week 7 |
| 7 | Rule Layering | 🟡 Not Started | 0% | Week 7 |
| 8 | TDD Harness | 🟡 Not Started | 0% | Week 6 |
| 9 | Plan Viewer | 🟡 Not Started | 0% | Week 6 |
| 10 | Response Templates | 🟡 Not Started | 0% | Week 7 |
| 11 | Integration | 🟡 Not Started | 0% | Week 9 |

**Legend:** 🟢 Complete | 🔵 In Progress | 🟡 Not Started | 🔴 Blocked

---

## 🎯 Success Criteria (Epic-Level)

### Functional Requirements

- ✅ 3+ companies registered with independent knowledge libraries
- ✅ 2+ custom orchestrators operational (Selenium→Playwright + 1 other)
- ✅ Knowledge merge accuracy >95%
- ✅ Zero CORTEX core corruption (all changes isolated)

### Performance Requirements

- ✅ Knowledge query overhead <50ms (95th percentile)
- ✅ Custom orchestrator routing <100ms
- ✅ No performance regression on core orchestrators

### Quality Requirements

- ✅ 100% test coverage on new components
- ✅ Zero critical bugs in integration testing
- ✅ All SKULL rules enforced (TDD, Git Isolation, etc.)

### Adoption Requirements

- ✅ 2+ developers trained on custom orchestrator development
- ✅ Documentation complete (architecture, API, deployment)
- ✅ 1+ production custom orchestrator deployed

**Go-Live Criteria:** All 10 checkboxes ✅ + stakeholder sign-off

---

## ⚠️ Common Issues & Solutions

### Issue 1: "I don't know where to start"

**Solution:**
1. Read `00-cortex5-epic.md` (Executive Summary section)
2. Read `context/discovery.md` (understand current state)
3. Start `phases/phase-01-knowledge-extension.md`

### Issue 2: "Phase dependencies unclear"

**Solution:**
1. Read `context/dependency-mapping.md`
2. Check visual dependency graph in `00-cortex5-epic.md` (Snowball section)
3. Follow phases in numerical order (1→2→3→4, then parallelize)

### Issue 3: "How do I track progress?"

**Solution:**
1. Update `tracking/progress-tracker.json` after each task
2. Check `tracking/snowball.md` for momentum visualization
3. Review phase validation reports in `reports/validation/`

### Issue 4: "Custom orchestrator not routing"

**Solution:**
1. Check `cortex-brain/tier0/orchestrator-registry.yaml` (is it registered?)
2. Verify manifest syntax (`src/orchestrators/custom/{company}/manifest.yaml`)
3. Test routing: `python3 -m src.main "test {pattern}"`

### Issue 5: "Company knowledge not overriding CORTEX"

**Solution:**
1. Check knowledge folder: `cortex-brain/tier2/company-knowledge/{company-id}/`
2. Verify query priority in `CompanyKnowledgeProvider`
3. Test merge: Query known CORTEX fact, verify company override applies

---

## 📚 Key Resources

### Documentation

| Resource | Location |
|----------|----------|
| CORTEX Architecture | `cortex-brain/documents/cortex-architecture-quick-ref.md` |
| Orchestrator Docs | `cortex-brain/documents/orchestrators-quick-ref.md` |
| Master Orchestrator Entry | `.github/prompts/CORTEX.prompt.md` |
| Brain Protection Rules | `cortex-brain/brain-protection-rules.yaml` |

### Configuration Files

| File | Purpose |
|------|---------|
| `cortex-brain/config/master-orchestrator.yaml` | Orchestrator routing config |
| `cortex-brain/tier0/orchestrator-registry.yaml` | Orchestrator registry (Phase 2+) |
| `cortex-brain/response-templates-v4.yaml` | Response formatting templates |

### Implementation Reference

| Component | Location |
|-----------|----------|
| Master Orchestrator | `src/orchestrators/master_orchestrator.py` |
| Planning v5 | `src/orchestrators/planning/planning_orchestrator_v5.py` |
| Custom Orchestrator Base | `src/orchestrators/custom/base_custom_orchestrator.py` (Phase 5) |
| Company Knowledge Provider | `src/knowledge/company_knowledge_provider.py` (Phase 1) |

---

## 🤝 Getting Help

### For Implementers

**Stuck on a phase?**
1. Read phase document carefully (implementation steps are detailed)
2. Check `analysis/risk-assessment.md` for known issues
3. Review `context/architecture-analysis.md` for system understanding

**Need code examples?**
1. Check `artifacts/implementation/` (generated code from completed phases)
2. Review existing orchestrators in `src/orchestrators/` (core patterns)
3. Read `phases/phase-06-selenium-playwright.md` (complete reference implementation)

### For Reviewers

**Validating phase completion?**
1. Check `reports/validation/phase-{N}-validation.md`
2. Review test results in `artifacts/tests/phase-{N}/`
3. Verify success criteria in phase document

**Assessing risks?**
1. Read `analysis/risk-assessment.md`
2. Check mitigation status in `tracking/progress-tracker.json`
3. Review integration test results (Phase 11)

### For GitHub Copilot

**Resuming work:**
```
Read: tracking/CONTINUATION-PROMPT.md
Continue: Phase {current_phase}
```

**Generating artifacts:**
```
Context: phases/phase-{N}-{name}.md
Generate: {component_name}
Validate: Against success criteria
```

---

## 🎉 Next Steps

**You are here:** Epic created, ready for Phase 1

**Next actions:**
1. ✅ **Read master plan:** `00-cortex5-epic.md`
2. ✅ **Understand context:** `context/discovery.md`
3. ✅ **Start Phase 1:** `phases/phase-01-knowledge-extension.md`
4. ⏳ **Track progress:** Update `tracking/progress-tracker.json`

**Phase 1 deliverables:**
- Company knowledge folder structure
- `CompanyKnowledgeProvider` implementation
- Knowledge merge logic
- Validation tests

**Timeline:** 2 weeks for Phase 1 completion

---

**Epic Owner:** Asif Hussain  
**Version:** 2.0.0  
**Status:** 🟢 ACTIVE  
**Last Updated:** 2026-01-06

**Ready to start? Open `phases/phase-01-knowledge-extension.md` and begin!** 🚀
