# 🎨 Story Dialogue Coloring Fix - Plan Directory

**Created:** December 29, 2025  
**Author:** Asif Hussain  
**Status:** ✅ PLAN COMPLETE - Ready for Implementation

---

## 📋 Quick Start

Read documents in this order:

1. **PLAN-SUMMARY.md** ⭐ START HERE - Overview & next actions
2. **00-master-plan.md** - Detailed planning document
3. **reports/analysis-findings.md** - Problem analysis
4. **context/implementation-guide.md** - How to implement the fix

---

## 📁 Directory Structure

```
story-dialogue-coloring-fix/
│
├── README.md                       ⭐ This file
├── PLAN-SUMMARY.md                 ⭐ Quick overview (START HERE)
├── 00-master-plan.md               📋 Master plan document
│
├── context/                        📚 Implementation details
│   └── implementation-guide.md     🛠️ Code changes & testing
│
├── reports/                        📊 Analysis & findings
│   ├── analysis-findings.md        🔍 Root cause analysis
│   └── uncolored-dialogues-analysis.json  📈 Raw data (1,092 dialogues)
│
├── artifacts/                      🔧 Tools & scripts
│   └── analyze-story-dialogues.py  🐍 Dialogue analysis script
│
└── tracking/                       ✅ Progress tracking
    └── progress-tracker.json       📊 Phase/task status
```

---

## 🎯 Problem Overview

**Issue:** Dialogues in "The Awakening of CORTEX" story lack character-specific coloring.

**Discovery:** Only 44.5% of dialogues are properly attributed (not 99% as documented).

**Root Causes:**
1. No conversation flow tracking
2. Missing first-person narrator detection
3. Limited context window
4. Line-by-line vs. paragraph processing

---

## 📊 Key Statistics

- **Total Dialogues:** 1,092
- **Currently Attributed:** 486 (44.5%)
- **Unattributed:** 606 (55.5%)
- **Target:** 100% attribution

### Speaker Distribution
| Speaker | Current | Target |
|---------|---------|--------|
| Asif | 273 (25%) | ~650 (60%) |
| Miss G | 198 (18%) | ~350 (32%) |
| Copilot | 13 (1%) | ~50 (5%) |
| Others | 2 (0%) | ~40 (3%) |
| **Unattributed** | **606 (55%)** | **0 (0%)** |

---

## 🛠️ Solution Summary

### 7 Key Changes to `story-viewer.js`

1. ✅ Add conversation flow tracking (alternating speakers)
2. ✅ Add first-person narrator detection (I/my → Asif)
3. ✅ Extend context window (300 + 150 chars)
4. ✅ Add Miss G voice patterns
5. ✅ Enhanced pronoun resolution
6. ✅ Reset speaker at section boundaries
7. ✅ Conflict detection for edge cases

**Target File:** `docs/story/story-viewer.js` (lines ~615-800)

---

## 🚀 Implementation Steps

### Phase 2: Enhancement (3 hours)
1. Apply 7 changes to `story-viewer.js`
2. Test locally: `python -m http.server 8000`
3. Verify Prologue + Chapter 1
4. Iterate until 95%+ attribution

### Phase 3: Testing (2 hours)
5. Test all 14 chapters
6. Re-run analysis script
7. Manual spot-check 50 dialogues
8. Verify zero regressions

### Phase 4: Documentation (1 hour)
9. Update CHARACTER-COLORS.md
10. Generate validation report
11. Commit and deploy

---

## 📈 Success Criteria

**DONE = ALL of the following:**
- ✅ 100% attribution rate (from 44.5%)
- ✅ Zero false positives (HTML/CSS not colored)
- ✅ Zero regressions (existing attributions preserved)
- ✅ All chapters verified
- ✅ Documentation updated

---

## 🔧 Tools & Commands

### Run Analysis Script
```bash
cd D:/PROJECTS/CORTEX/cortex-brain/documents/planning/active/story-dialogue-coloring-fix/artifacts
python analyze-story-dialogues.py
```

### Start Local Server
```bash
cd D:/PROJECTS/CORTEX
python -m http.server 8000
# Open: http://localhost:8000/story/viewer.html
```

### Backup Original File
```bash
cp docs/story/story-viewer.js docs/story/story-viewer.js.backup
```

---

## 📚 Document Purposes

| Document | Purpose | Audience |
|----------|---------|----------|
| **PLAN-SUMMARY.md** | Quick overview & next actions | All |
| **00-master-plan.md** | Comprehensive planning | Implementation team |
| **implementation-guide.md** | Detailed code changes | Developer |
| **analysis-findings.md** | Root cause analysis | Technical lead |
| **progress-tracker.json** | Task tracking | Project manager |

---

## ⏱️ Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Planning | 2 hours | ✅ COMPLETE |
| Enhancement | 3 hours | 📋 NEXT |
| Testing | 2 hours | 📋 PLANNED |
| Documentation | 1 hour | 📋 PLANNED |
| **TOTAL** | **8 hours** | - |

---

## 🎯 Current Status

**Phase 1 (Planning): ✅ COMPLETE**

All planning artifacts created:
- ✅ 6 documents written
- ✅ 1 Python script created
- ✅ 1,092 dialogues analyzed
- ✅ 5 root causes identified
- ✅ 7 code changes defined

**Next Phase: Implementation (Phase 2)**

Apply the 7 changes to `story-viewer.js` as detailed in `context/implementation-guide.md`.

---

## 📞 Quick Links

**Story Viewer:** http://localhost:8000/story/viewer.html  
**Target File:** `docs/story/story-viewer.js`  
**Character Colors:** `docs/story/CHARACTER-COLORS.md`  
**GitHub Pages:** https://asifhussain60.github.io/CORTEX/story/viewer.html

---

## 🔗 Related Files

- `docs/story/story-viewer.js` - Target file for changes
- `docs/story/story-viewer.css` - Styling (no changes needed)
- `docs/story/CHARACTER-COLORS.md` - Documentation to update
- `docs/story/Prologue/index.md` - Test chapter (104 dialogues)

---

**Generated by:** CORTEX Planning System 4.0  
**Website:** https://asifhussain60.github.io/CORTEX/
