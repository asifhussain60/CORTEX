# CORTEX Documentation Fresh Generation - Quick Start
**Version:** 5.0 | **Status:** ✅ READY TO USE | **Date:** 2026-01-25

---

## 🚀 One-Shot Documentation Generation

### Command
```bash
/doc-fresh-generate
```

### Workflow (2 Steps)

**Step 1: Invoke**
```
You: /doc-fresh-generate
```

**Step 2: Approve**
```
CORTEX: Display DoR classification
You: proceed
```

**Result:** All 7 phases execute automatically, generating fresh documentation

---

## 📊 What Gets Generated

### Documentation (16+ Files)
- `docs/00-README.md`
- `docs/01-getting-started/` (3 files)
- `docs/02-architecture/` (4 files + 6 diagrams)
- `docs/03-api-reference/` (3 sections)
- `docs/04-guides/` (5+ files)
- `docs/05-tutorials/` (4+ files)
- `docs/06-reference/` (3+ files)

### Diagrams (10 Total)
**Mermaid (6):**
- Approval gate decision tree
- Error recovery paths
- Circuit breaker state machine
- Master orchestrator sequence
- TDD workflow phases
- Governance rule categories

**D3.js (4):**
- Governance pyramid (interactive)
- Request lifecycle (sankey)
- TDD knowledge cycle (circular)
- Domain brain architecture (layered)

### Report
- `_workspaces/reports/FRESH-DOCUMENTATION-GENERATION-{date}.md`

---

## ⏱️ Execution Phases (Automatic)

| Phase | Action | Time |
|-------|--------|------|
| 1 | PRE-CLEANUP | 30 sec |
| 2 | DISCOVERY | 1-2 min |
| 3 | GENERATION | 2-3 min |
| 4 | DIAGRAMS | 1-2 min |
| 5 | BUILD | 1-2 min |
| 6 | VALIDATION | 1 min |
| 7 | REPORTING | 30 sec |
| **Total** | | **~10-12 min** |

---

## ✅ What's Preserved

- ✅ `serve-docs.bat`
- ✅ `serve-docs.sh`
- ✅ `_archive/`
- ✅ `assets/`
- ✅ `stylesheets/`
- ✅ `theme/`

---

## ❌ What's Deleted

- ❌ All old `*.md` files
- ❌ Old `_diagrams/`
- ❌ Old `_reports/`
- ❌ Old `_tests/`
- (Everything else is fresh)

---

## 🎯 Key Benefits

✅ **Single command** - No parameters or options  
✅ **Single approval** - Just type "proceed"  
✅ **Automatic execution** - All 7 phases run without stopping  
✅ **Fresh content** - Everything regenerated from scratch  
✅ **Complete result** - Docs + diagrams + built site + report  
✅ **Zero config** - No decisions or configuration needed  
✅ **Safe rollback** - Easy to revert via git  

---

## 📖 Next Steps After Generation

### Preview Locally
```bash
mkdocs serve
```
Open: http://localhost:8000

### Deploy to GitHub Pages
```bash
mkdocs gh-deploy
```

### Review Report
```bash
cat _workspaces/reports/FRESH-DOCUMENTATION-GENERATION-*.md
```

---

## 🔗 File Locations

| Item | Location |
|------|----------|
| **Prompt** | `.github/prompts/cortex-doc-v5.prompt.md` |
| **Chat** | `.github/.chats/chat01.md` |
| **Report** | `_workspaces/DOCUMENTATION-PROMPT-TRANSFORMATION-v5.md` |
| **Generated docs** | `docs/` (all sections) |
| **Report output** | `_workspaces/reports/FRESH-DOCUMENTATION-GENERATION-*.md` |

---

## ⚡ TL;DR

1. Type: `/doc-fresh-generate`
2. Approve: `proceed`
3. Wait: ~10 minutes
4. Result: Fresh docs in `docs/` + report in `_workspaces/reports/`

Done! 🎉
