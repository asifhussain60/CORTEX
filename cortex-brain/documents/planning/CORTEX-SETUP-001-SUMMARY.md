# Plan Registry Summary - CORTEX-SETUP-001

**Generated:** 2025-12-03  
**Plan Status:** Proposed (Awaiting Approval)

---

## 📋 Plan Overview

**Plan ID:** CORTEX-SETUP-001  
**Title:** Shared Environment Default Activation + User Profiling + Planning Infrastructure  
**Priority:** HIGH  
**Status:** Proposed  
**Created:** 2025-12-03  
**Estimated Duration:** 14-21 days (~3-4 weeks)  
**Estimated Hours:** 112 hours  
**Completion:** 0%

---

## 🎯 Key Features

1. **Shared Environment as Default**
   - Version-specific shared venvs (`~/.cortex/venv-3.11/`)
   - Auto-migration from single-project `.venv`
   - 83% setup time reduction (270 seconds saved per project)

2. **Interactive User Profiling**
   - 4-question setup with letter-based selection
   - Profile stored in `cortex.config.json`
   - Smart defaults (git config, GitHub CLI detection)

3. **Response Template Wiring**
   - 6 new template variants (verbose/concise × junior/intermediate/senior/principal/manager)
   - Auto-selection based on user profile
   - Personalized response style

4. **Alignment Orchestrator**
   - 8 validation checks
   - Auto-repair for common issues
   - Integration score (0-100%)

5. **Planning Infrastructure** ✨ NEW
   - Plan registry with SQLite database
   - Plan lookup API (`list_plans()`, `get_plan()`, `search_plans()`)
   - Auto-generated INDEX.md
   - Status tracking (proposed → approved → in-progress → completed)
   - CLI commands (`cortex plan list/show/search/update`)

---

## 📊 Implementation Phases

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1: Shared Environment | 3-5 days | Version-specific venvs, auto-migration, fallback |
| Phase 2: User Profiling | 2-3 days | Interactive questionnaire, profile storage, smart defaults |
| Phase 3: Response Templates | 2-3 days | 6 new templates, selection engine, customization |
| Phase 4: Alignment Orchestrator | 2-3 days | 8 validation checks, auto-repair, scoring |
| Phase 6: Planning Infrastructure | 1-2 days | Registry, lookup API, index generation, CLI |
| Phase 7: Integration & Testing | 2-3 days | E2E tests, documentation, deployment |

**Note:** Phase 6 can run partially in parallel with Phases 1-2

---

## ✅ Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| First-time setup time | 300s | <60s |
| Subsequent setup time | 30s | <5s |
| Setup time reduction | 0% | 83% |
| User profile adoption | 0% | 90% |
| Template personalization | 0% | 95% |
| Plans indexed | 0 | 100% |
| Plan lookup time | N/A | <100ms |
| Test coverage | 75% | ≥85% |

---

## 🔧 Technical Stack

**Languages:** Python 3.8+  
**Database:** SQLite (plan registry)  
**Storage:** YAML frontmatter + Markdown  
**Testing:** pytest, TDD workflow (RED→GREEN→REFACTOR)  
**CLI:** Click or argparse

---

## 🚨 Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Shared env creation fails | Fallback to single-project `.venv` |
| Migration breaks setup | Backup config, rollback available |
| Plan registry corruption | SQLite ACID, auto-backup, rebuild from files |
| User confusion | Clear instructions, defaults, preview confirmation |

---

## 📝 Approval Status

- [ ] Product Owner approves feature scope
- [ ] Architecture reviewed and approved
- [ ] STRIDE threat analysis reviewed
- [ ] DoR validation complete
- [ ] DoD criteria agreed upon
- [ ] Timeline and resources allocated
- [ ] Rollback plan reviewed

---

## 🔗 Related Documentation

- **Full Plan:** `cortex-brain/documents/planning/shared-environment-default-activation.md`
- **UX Enhancements:** `cortex-brain/documents/planning/ux-enhancements-summary.md`
- **Setup Guide:** `docs/SETUP-CORTEX.md`
- **Planning System:** `.github/prompts/modules/planning-orchestrator-guide.md`

---

## 🎓 Key Innovations

1. **Lightweight Plan Registry** - SQLite-based, <100ms queries, no full orchestrator overhead
2. **YAML Frontmatter** - Machine-readable metadata in Markdown files (best of both worlds)
3. **Auto-Organization** - Plans auto-move to active/completed based on status
4. **CLI Integration** - Natural language commands (`cortex plan list --status=active`)
5. **Self-Documenting** - Auto-generated INDEX.md always in sync

---

**Next Action:** Approve plan and begin Phase 1 implementation

*This summary is part of CORTEX Planning System 2.0*
