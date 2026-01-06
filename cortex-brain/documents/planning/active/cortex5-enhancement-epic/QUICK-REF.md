# CORTEX-5.5 Migration - Quick Reference Card

**Version:** 1.0.0 | **Date:** 2026-01-06

---

## 🎯 TL;DR

**Goal:** Start CORTEX5 epic on clean CORTEX-5.5 branch (85% file reduction)  
**Strategy:** START CLEAN → PULL AS NEEDED → TRACK EVERYTHING  
**Time:** 15 minutes migration + 9 weeks epic execution

---

## 📦 What You Get

| Metric | Value |
|--------|-------|
| **Files** | ~150 (vs ~1000 in CORTEX-5.0) |
| **Reduction** | 85% |
| **Directories** | 19 essential |
| **Phase 1 Scaffolding** | ✅ Ready |
| **Pull Budget** | 20 files max |
| **Technical Debt** | 0 (clean start) |

---

## 🚀 Quick Start (3 Commands)

```powershell
# 1. Migrate
.\create-cortex-5.5-branch.ps1

# 2. Commit
git commit -m "feat: Initialize CORTEX-5.5 clean branch"
git push -u origin CORTEX-5.5

# 3. Start Phase 1
code "cortex-brain/documents/planning/active/cortex5-enhancement-epic/phases/phase-01-knowledge-extension.md"
```

---

## 📋 Essential Files Included

✅ Core orchestration (master_orchestrator.py, pattern_router.py)  
✅ Active orchestrators (Planning v5, ADO v2, Investigation v2)  
✅ Brain tiers (tier0/tier1/tier2 structure)  
✅ Configuration (8 core configs + 11 manifests)  
✅ Response templates (response-templates-v4.yaml)  
✅ Phase 1 scaffolding (src/knowledge/, company_knowledge/)  

❌ Sample apps (not needed)  
❌ Old versions (cortex_3_0, orchestration_4_0)  
❌ Archives/backups (historical)  
❌ Unused orchestrators (17+ manifests)  
❌ Reports/logs (runtime generated)  

---

## 🔄 Pull from CORTEX-5.0 (When Needed)

```powershell
# Example: Phase 3 needs LLM utilities
.\pull-from-cortex-5.0.ps1 `
    -Phase 3 `
    -Files @("src/llm/llm_provider.py") `
    -Justification "LLM-based goal detection" `
    -AlternativesConsidered @("Rewrite with OpenAI SDK") `
    -DecisionRationale "Existing provider supports multiple models" `
    -Category "llm_utilities"
```

**Budget:** 0/20 pulls used (75% alert at 15 pulls)

---

## 📊 Phase Dependency Forecast

| Phase | Pull? | What | Alternative |
|-------|-------|------|-------------|
| 1 | ❌ No | All included | - |
| 2 | ❌ No | Routing included | - |
| 3 | ⚠️ Maybe | src/llm/ | Rewrite |
| 4 | ❌ No | Merge logic in Phase 1 | - |
| 5 | ⚠️ Maybe | base_orchestrator.py | New class |
| 6 | ⚠️ Maybe | AST tools | Use ast module |
| 7 | ❌ No | Rules included | - |
| 8 | ⚠️ Maybe | src/tdd/ | Rewrite |
| 9 | ✅ Likely | templates/ | Modernize |
| 10 | ❌ No | Templates included | - |
| 11 | ✅ Likely | test fixtures | Pull tests |

**Estimated:** 5-8 pulls (well under 20 budget)

---

## 🛡️ Success Criteria

**Migration Success:**
- ✅ Branch created from main (not CORTEX-5.0)
- ✅ ~150 files (85% reduction)
- ✅ Phase 1 scaffolding ready
- ✅ Pull system operational

**Epic Success (9 weeks):**
- ✅ <20 total pulls from CORTEX-5.0
- ✅ 100% pull justification documented
- ✅ 85% reduction maintained
- ✅ Zero technical debt at Phase 11

---

## 📚 Document Map

| Document | Purpose | Lines |
|----------|---------|-------|
| **MIGRATION-SUMMARY.md** | Executive summary | 650 |
| **CORTEX-5.5-MIGRATION-STRATEGY.md** | Full technical strategy | 784 |
| **CORTEX-5.5-EXECUTION-GUIDE.md** | Step-by-step guide | 468 |
| **MIGRATION-CHECKLIST.md** | Pre-flight checklist | 350 |
| **00-cortex5-epic.md** | Epic master plan (updated) | 700+ |
| **create-cortex-5.5-branch.ps1** | Automation script | 336 |
| **pull-from-cortex-5.0.ps1** | Pull tracking | 98 |

---

## ⚠️ Common Issues

### Issue: Branch already exists
```powershell
git branch -D CORTEX-5.5  # Delete and retry
```

### Issue: File not found in CORTEX-5.0
```powershell
# Skip or find alternative
# Don't block on missing files
```

### Issue: Pull budget exceeded
```powershell
# Review pulls - are they necessary?
# Consider rewrite instead of pull
# Request budget increase if justified
```

---

## 🆘 Emergency Contacts

**Questions?** → Read CORTEX-5.5-EXECUTION-GUIDE.md  
**Troubleshooting?** → See §"Troubleshooting" section  
**Pull needs?** → Use pull-from-cortex-5.0.ps1  
**Rollback?** → See MIGRATION-CHECKLIST.md §"Rollback Plan"

---

## 🎯 Critical Decisions

### ✅ GO Criteria
- All pre-migration checks pass
- Script executes successfully
- Branch validated (structure + code)
- Epic plan accessible

### ❌ NO-GO Criteria
- Script fails with errors
- File count >200 (insufficient reduction)
- Python syntax errors
- Essential files missing

---

## 📞 Next Steps After Migration

1. **Validate** → Run MIGRATION-CHECKLIST.md
2. **Phase 1** → Open phase-01-knowledge-extension.md
3. **TDD Cycle** → Write tests → Implement → Refactor
4. **Track** → Update tracking/progress-tracker.json

---

**Quick Ref Version:** 1.0.0  
**Maintained By:** CORTEX Planning System v5  
**Status:** ✅ READY FOR EXECUTION
