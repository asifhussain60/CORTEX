# CORTEX 3.0 → 4.0 Migration Plan

**Version:** 1.5 (Token-Optimized Structure)  
**Author:** Asif Hussain  
**Last Updated:** December 20, 2025

---

## 🚀 Quick Start

**For Status:** Read [CORTEX4-STATUS.md](./CORTEX4-STATUS.md) (~400 tokens, 95% reduction)

**For Overview:** Read [00-MASTER-PLAN.md](./00-MASTER-PLAN.md) (~800 tokens)

**For Execution:** See [AUTONOMOUS-EXECUTION-GUIDE.md](./references/AUTONOMOUS-EXECUTION-GUIDE.md) - How to execute phases autonomously

**For Details:** Navigate to specific folders below

---

## ⚡ Execution Modes

This migration supports **2 execution modes**:

1. **Supervised (Default):** Execute tasks one-by-one with manual approval
2. **Autonomous (Advanced):** Execute all phases/tasks end-to-end automatically

**Quick Commands:**
- `execute task [N]` - Run single task (supervised)
- `execute all phases autonomously` - Full E2E execution
- `execute tasks 2-10 autonomously` - Continue from task 2

See [Autonomous Execution Guide](./references/AUTONOMOUS-EXECUTION-GUIDE.md) for full details.

---

## 📁 Folder Structure

### 🎯 Core Files (Root)
- **[CORTEX4-STATUS.md](./CORTEX4-STATUS.md)** - Visual progress tracker (Tier 1: ~400 tokens)
- **[00-MASTER-PLAN.md](./00-MASTER-PLAN.md)** - Master hub with overview (Tier 2: ~800 tokens)
- **[MIGRATION-GUIDE.md](./MIGRATION-GUIDE.md)** - Token optimization guide
- **[ORCHESTRATOR-IMPACT-ANALYSIS.md](./ORCHESTRATOR-IMPACT-ANALYSIS.md)** - Integration impact
- **[FOLDER-ORGANIZATION-PLAN.md](./FOLDER-ORGANIZATION-PLAN.md)** - Organization plan

### 📂 Organized Folders

#### [metadata/](./metadata/)
Machine-readable YAML metadata
- `plan-metadata.yaml` - Smart routing configuration

#### [phases/](./phases/)
Phase detail files (Tier 3: ~2,500 tokens each)
- Phase 1-10 detail files (to be extracted)
- `README.md` - Phase navigation guide

#### [workers/](./workers/)
Week-specific work details (Tier 4: ~1,000 tokens each)
- Granular sub-task files organized by phase

#### [architecture/](./architecture/)
System architecture designs (6 files)
- CORTEX 4.0 Architecture, CORTEX Lens, Feature Discovery
- TDD Orchestrator, Documentation Orchestrator, IDE Detection

#### [specs/](./specs/)
Technical specifications (4 files)
- CORTEX Lens Phase A, Security Learning Integration
- IDE Documentation, Technical Documentation Integration

#### [implementation-plans/](./implementation-plans/)
Implementation plans (3 files)
- Agentic Enhancements, Phase 3 Migration, Phase 1.5 Scripts

#### [progress/](./progress/)
Progress tracking documents (5 files)
- Phase progress updates, gap resolutions, completion summaries

#### [standards/](./standards/)
Standards & policies (4 files)
- Progress tracking, Git commits, integration checklists

#### [references/](./references/)
Reference documentation (1 file)
- TDD Orchestrator V4 Reference

#### [archive/](./archive/)
Historical documents
- `MASTER-PLAN-original-v1.5.md` (7,283 lines, archived)

#### [reports/](./reports/)
Status reports

#### [supporting-docs/](./supporting-docs/)
Supporting documentation

---

## 🎯 Token Optimization

**Query Types:**
- **Status only:** ~400 tokens (**95% reduction**)
- **Architecture:** ~1,200 tokens (**94% reduction**)
- **Phase details:** ~2,500 tokens (**87% reduction**)
- **Week details:** ~1,000 tokens (**95% reduction**)

**Smart Loader:** `src/utils/smart_plan_loader.py` automatically routes queries

---

## 🔍 Navigation Tips

**By Purpose:**
1. Quick status → `CORTEX4-STATUS.md`
2. Architecture overview → `00-MASTER-PLAN.md`
3. Specific phase → `phases/phase-{id}.md`
4. Architecture designs → `architecture/`
5. Technical specs → `specs/`
6. Progress updates → `progress/`
7. Policies → `standards/`

**By Timeline:**
- Current work → `CORTEX4-STATUS.md`
- Historical work → `progress/` and `archive/`
- Future work → `phases/`

---

## 📊 Current Status

**Overall Progress:** 80%  
**Current Phase:** Phase 6 (Orchestrator Consolidation)  
**Current Week:** Week 9 Day 1  
**Recent Milestone:** Planning System Core MVP Complete

See [CORTEX4-STATUS.md](./CORTEX4-STATUS.md) for details.

---

## 🤖 For Orchestrators

**Load Plan Context:**
```python
from src.utils.smart_plan_loader import SmartPlanLoader

loader = SmartPlanLoader("d:/PROJECTS/CORTEX")
status = loader.load_plan_context("What's the status?")  # ~400 tokens
```

**Future:** Planning Orchestrator will auto-generate this structure (Week 9-10)

---

**Last Updated:** December 20, 2025  
**Pattern Version:** 1.0 (Token-Optimized Hierarchical Structure)

