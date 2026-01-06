# Documentation Orchestrator v2.0 - Quick Start

**Plan:** docs-orchestrator-v2  
**Version:** 2.0.0  
**Status:** 🟢 Active

---

## 🚀 Quick Start

This plan develops a comprehensive YAML-based documentation orchestrator that enforces glassmorphism standards, validates approved template compliance, and ensures Level 1 page uniqueness with architectural diagrams.

---

## 📋 Overview

### What This Plan Delivers
1. **5 Validators:** Template compliance, margins, logo placement, inline styles, uniqueness
2. **Audit Logging:** Every action tracked (inline removal, CSS application, validation failures)
3. **Centralized Toolkit:** 9 scattered scripts moved to cortex-toolkit orchestrator
4. **Level 1 Uniqueness:** Architecture page with 9+ diagrams, <30% overlap with orchestrators page
5. **YAML-Based Orchestrator:** Managed by master orchestrator, state-aware, rollback-safe

### Success Criteria
- ✅ 95%+ template compliance rate
- ✅ Zero inline styles across documentation
- ✅ 9+ architectural diagrams deployed
- ✅ <30% content overlap (architecture vs orchestrators)
- ✅ 100% audit logging coverage
- ✅ All scattered scripts centralized

---

## 📂 Plan Structure

```
docs-orchestrator-v2/
├── 00-docs-orchestrator-v2.md          ← Master plan (start here)
├── README.md                           ← This file
├── analysis/                           ← Deep analysis reports
│   └── (To be populated)
├── artifacts/                          ← Generated artifacts
│   └── (Validators, scripts, manifests)
├── context/
│   ├── discovery.md                    ← Problem space analysis
│   └── architecture-analysis.md        ← (To be created)
├── reports/                            ← Progress reports
│   └── (Validation reports, test results)
└── tracking/
    ├── progress-tracker.json           ← Current progress
    └── CONTINUATION-PROMPT.md          ← Resume guide
```

---

## 🎯 Current Phase

**Phase 1: Validators Registry Development**
- Status: ⏳ Ready to Start
- Duration: 4 hours
- Tasks: 4 (template compliance, margins, logo placement, uniqueness)

**Next Steps:**
1. Implement `TemplateComplianceValidator` class
2. Write unit tests (>90% coverage)
3. Integrate with audit logger
4. Test against orchestrators/index.html (baseline)

---

## 🏗️ Key Components

### Validators (5 total)
1. **TemplateComplianceValidator** - Validates against orchestrators/index.html
2. **MarginsValidator** - Checks body left/right margins (2rem)
3. **LogoPlacementValidator** - Verifies CORTEX logo atop introduction panel
4. **InlineStyleValidator** - Zero tolerance for inline styles (CRITICAL)
5. **UniquenessValidator** - Ensures <30% overlap between Level 1 pages

### Audit Logging Events
- `inline_style_removed` - Inline style attribute removed
- `css_class_applied` - CSS class added to element
- `template_validation` - Template compliance check
- `uniqueness_check` - Content overlap analysis
- `diagram_generated` - Architectural diagram created
- `state_persisted` - Standardization state saved
- `git_checkpoint_created` - Safety checkpoint created

### Toolkit Categories
- **Documentation:** remove-inline-styles, standardize-level1-views, detect-inline-styles, calculate-complexity, generate-architecture-diagrams
- **Planning:** validate-plan-structures, upgrade-plan-structures
- **Routing:** validate-orchestrator-registry, regenerate-routing-table

---

## 📖 Documentation

### Key Documents
- **Master Plan:** `00-docs-orchestrator-v2.md` (comprehensive plan with all phases)
- **Context Discovery:** `context/discovery.md` (problem space analysis)
- **Progress Tracker:** `tracking/progress-tracker.json` (real-time progress)

### External References
- **Orchestrator Manifest:** `cortex-brain/manifests/orchestrators/documentation-orchestrator.yaml`
- **Master Orchestrator Config:** `cortex-brain/config/master-orchestrator.yaml`
- **Audit Logger:** `src/orchestrators/audit_logger.py`
- **Approved Template:** `docs/orchestrators/index.html`

---

## 🚦 Getting Started

### For Developers
```bash
# 1. Review master plan
code 00-docs-orchestrator-v2.md

# 2. Review context discovery
code context/discovery.md

# 3. Start Phase 1 Task 1.1
# Implement TemplateComplianceValidator
code cortex-toolkit/validators/template_compliance_validator.py

# 4. Run tests
pytest tests/toolkit/validators/test_template_compliance_validator.py -v

# 5. Update progress tracker
code tracking/progress-tracker.json
```

### For Reviewers
```bash
# 1. Check progress
cat tracking/progress-tracker.json | grep "Progress"

# 2. Review completed tasks
git log --oneline --grep="docs-orchestrator-v2"

# 3. Validate deliverables
ls -R artifacts/
```

---

## 🎓 Key Concepts

### State-Aware Orchestration
Tracks previous standardization attempts in `html-standardization-state.json` to avoid redundant work.

### Validator Registry Pattern
Extensible validation framework with priority-based execution. Critical validators (inline styles) BLOCK if failed.

### Audit-First Architecture
Every action logged BEFORE execution for rollback safety.

### Centralized Tooling
Single source of truth for all documentation utilities via `cortex-toolkit` orchestrator.

### Uniqueness Enforcement
Automated content differentiation between Level 1 pages using TF-IDF similarity, heading analysis, diagram classification, and visual component overlap detection.

---

## 📊 Progress Summary

**Overall Progress:** 0% (0/6 phases complete)
- ✅ Phase 0: Planning & Context Discovery (COMPLETE)
- ⏳ Phase 1: Validators Registry Development (IN PROGRESS)
- 🔵 Phase 2: Audit Logger Integration (PLANNED)
- 🔵 Phase 3: Orchestrator Manifest Enhancement (PLANNED)
- 🔵 Phase 4: Centralized Toolkit Development (PLANNED)
- 🔵 Phase 5: Architecture Uniqueness Implementation (PLANNED)
- 🔵 Phase 6: Integration & Testing (PLANNED)

**Timeline:** 3 working days (24 hours total)

---

## 🔗 Quick Links

- **Master Plan:** [00-docs-orchestrator-v2.md](./00-docs-orchestrator-v2.md)
- **Context Discovery:** [context/discovery.md](./context/discovery.md)
- **Progress Tracker:** [tracking/progress-tracker.json](./tracking/progress-tracker.json)
- **Orchestrator Manifest:** [../../manifests/orchestrators/documentation-orchestrator.yaml](../../manifests/orchestrators/documentation-orchestrator.yaml)

---

## 🆘 Need Help?

**Stuck on a task?** Check the master plan's troubleshooting section.  
**Need to pause?** Update `tracking/CONTINUATION-PROMPT.md` with current state.  
**Found a blocker?** Add to `tracking/progress-tracker.json` → Blockers section.  
**Questions?** Review `context/discovery.md` for architectural context.

---

**Last Updated:** 2026-01-06  
**Next Review:** After Phase 1 completion
