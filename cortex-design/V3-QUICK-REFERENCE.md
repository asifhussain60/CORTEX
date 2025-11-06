# CORTEX V3 Quick Reference

**Created:** 2025-11-06  
**Purpose:** Fast lookup for V3 plan execution  
**Full Plan:** See `IMPLEMENTATION-PLAN-V3.md`

---

## 📋 What Changed from V2 → V3

1. **Reorganized by Logic, Not Phases:** 6 groups (dependency-based) instead of 9 phases
2. **Added System Check:** Dedicated full system validation (GROUP 6, Task 9.1)
3. **Added Root Cleanup:** Enforcement script for approved files only (GROUP 6, Task 9.2)
4. **Specified Doc Tools:** Pandoc (Markdown→.docx), MkDocs PDF (Markdown→PDF)
5. **Added Raw Request Logging:** New Task 1.6 from user questions
6. **Atomic Execution:** Single-shot commands, no multi-step announcements

---

## 🎯 6 Groups in Execution Order

```
GROUP 1: Foundation & Validation     →  10-14 hours  (Project setup, benchmarks)
GROUP 2: Core Infrastructure         →   6-8 hours   (Tier 0, CI/CD, docs)
GROUP 3: Data Storage                →  31-37 hours  (Tiers 1-3, migration tools)
GROUP 4: Intelligence Layer          →  32-42 hours  (Agents, entry, dashboard)
GROUP 5: Migration & Validation      →   5-7 hours   (KDS → CORTEX)
GROUP 6: Finalization                →   4-6 hours   (System check, cleanup)
────────────────────────────────────────────────────────────────────
TOTAL: 88-114 hours (11-14 days)
```

---

## 📂 Root Folder - Approved Files ONLY

**After completion, CORTEX root will contain:**

```
D:\PROJECTS\KDS\CORTEX\
├── README.md                          ✅
├── The CORTEX Story.docx              ✅ (Markdown → Pandoc)
├── The CORTEX Rule Book.pdf           ✅ (MkDocs → PDF)
├── package.json                       ✅
├── requirements.txt                   ✅
├── tsconfig.json                      ✅
├── .gitignore                         ✅
├── LICENSE                            ✅ (if exists)
└── [Folders only below this]
```

**Enforcement:** `cleanup-cortex-root.ps1` removes unauthorized files

---

## 🔍 Full System Check (When CORTEX Complete)

**Location:** `CORTEX/scripts/system-check/run-full-system-check.ps1`

**What it validates (10 checks):**
1. ✅ Tier 0 (Governance) operational
2. ✅ Tier 1 (Working Memory) functional
3. ✅ Tier 2 (Knowledge Graph) searchable
4. ✅ Tier 3 (Context Intelligence) current
5. ✅ All 10 agents operational
6. ✅ Database integrity (PRAGMA checks)
7. ✅ Performance targets met (<100ms, <270KB)
8. ✅ Test coverage ≥95%
9. ✅ Documentation builds (MkDocs)
10. ✅ Root folder compliance

**Run:** `.\CORTEX\scripts\system-check\run-full-system-check.ps1`

---

## 🚀 How to Execute V3

### Step 1: Initialize TODO Tracking

```typescript
manage_todo_list({
  operation: "write",
  todoList: [
    {id: 1, title: "GROUP 1: Foundation", description: "...", status: "in-progress"},
    {id: 2, title: "GROUP 2: Infrastructure", description: "...", status: "not-started"},
    {id: 3, title: "GROUP 3: Data Storage", description: "...", status: "not-started"},
    {id: 4, title: "GROUP 4: Intelligence", description: "...", status: "not-started"},
    {id: 5, title: "GROUP 5: Migration", description: "...", status: "not-started"},
    {id: 6, title: "GROUP 6: Finalization", description: "...", status: "not-started"}
  ]
})
```

### Step 2: Execute Groups in Order

**Start with GROUP 1:**
```powershell
# Task -2.1: Backup
cd D:\PROJECTS\KDS
git add . && git commit -m "Pre-reorg checkpoint" --allow-empty && ...

# Task -2.2: New structure
cd D:\PROJECTS
git clone https://github.com/asifhussain60/CORTEX.git CORTEX

# ... Continue through GROUP 1 tasks
```

**Validate before GROUP 2:**
```powershell
Test-Path D:\PROJECTS\CORTEX
git remote -v | Select-String "CORTEX"
git tag -l | Select-String "v8-final-kds"
```

**Repeat for each group:** Execute → Validate → Proceed

### Step 3: Final Validation (GROUP 6)

```powershell
# Run full system check
.\CORTEX\scripts\system-check\run-full-system-check.ps1

# Clean root folder
.\CORTEX\scripts\cleanup-cortex-root.ps1

# Verify documentation
mkdocs build --strict
```

---

## ✅ Success Criteria (Final Checklist)

**When ALL these are true, CORTEX V3 is COMPLETE:**

### Technical
- [ ] All 4 tiers operational
- [ ] All 10 agents functional
- [ ] Database integrity validated
- [ ] Performance targets met
- [ ] Test coverage ≥95%

### Operational
- [ ] CI/CD passing
- [ ] Documentation built
- [ ] System check passes (10/10)
- [ ] Migration complete
- [ ] KDS data imported

### Documentation
- [ ] README.md created
- [ ] The CORTEX Story.docx exists
- [ ] The CORTEX Rule Book.pdf exists
- [ ] CHANGELOG.md updated
- [ ] Release notes published

### Cleanup
- [ ] Root folder clean (only approved files)
- [ ] No unauthorized files
- [ ] Git history clean
- [ ] All tests passing

---

## 🎯 Key Differences from V2

| Aspect | V2 | V3 |
|--------|----|----|
| Structure | 9 phases | 6 logical groups |
| Ordering | Sequential | Dependency-based |
| System Check | Scattered | Dedicated (GROUP 6) |
| Root Cleanup | Not specified | Automated script |
| Documentation | Mentioned | Tools specified |
| Increments | Some large | All ≤150 lines |
| Execution | Multi-step | Atomic (single-shot) |

---

## 📖 Documentation Tool Choices

**1. README.md:**
- Tool: Any text editor (VS Code recommended)
- Format: Markdown
- Location: `D:\PROJECTS\KDS\CORTEX\README.md`

**2. The CORTEX Story.docx:**
- Source: Markdown file
- Tool: Pandoc
- Command: `pandoc cortex-story.md -o "The CORTEX Story.docx"`
- Template: Use reference .docx for styling

**3. The CORTEX Rule Book.pdf:**
- Source: MkDocs site
- Tool: MkDocs with PDF plugin
- Command: `mkdocs build` (with `mkdocs-with-pdf` plugin)
- Output: `The CORTEX Rule Book.pdf` in root

---

## ⚠️ Critical Rules

**Rule #23 (Small Increments):**
- Create large files in ≤150 line chunks
- Prevents "response hit length limit" errors
- Use multiple tool calls for 300+ line files

**Rule #24 (Assumption Validation):**
- Present assumptions before implementation
- Wait for user validation
- Document validated assumptions

**Atomic Execution:**
- Single-shot commands (no announcements)
- Batch git operations (`git add && commit && push && tag`)
- One tool call per update (no read-modify-write cycles)

---

## 🔗 Quick Links

**Full Plan:** `IMPLEMENTATION-PLAN-V3.md`  
**V2 Plan:** `IMPLEMENTATION-PLAN-V2.md` (for detailed task specs)  
**Governance Rules:** `../governance/rules.md`  
**System Check:** `../CORTEX/scripts/system-check/` (after GROUP 6)  
**Root Cleanup:** `../CORTEX/scripts/cleanup-cortex-root.ps1` (after GROUP 6)

---

## 🚀 Start Execution

**Ready to begin?**

```markdown
#file:KDS/prompts/user/kds.md

Start CORTEX V3 Implementation - GROUP 1: Foundation & Validation
```

---

*Quick Reference for CORTEX Implementation Plan V3*

**Status:** 🎯 READY  
**Total Time:** 88-114 hours (11-14 days)  
**Approach:** Dependency-based, small increments, atomic execution
