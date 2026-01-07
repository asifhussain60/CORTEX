# 🚀 CORTEX-5.0 Quick Launch Guide

**Start working on the gap remediation plan in 30 seconds.**

---

## ⚡ Instant Start

```bash
cd cortex-brain/documents/planning/active/CORTEX-5.0
python3 plan_orchestrator.py
```

Type `next` to begin Sub-Plan 00 (Test Coverage Sprint).

---

## 📋 Common Commands

### Interactive Mode (Recommended for Focus)
```bash
python3 plan_orchestrator.py

# Then use:
# - next      → Start next available work
# - status    → Check progress
# - update    → Update progress after completing a phase
# - complete  → Mark sub-plan done
# - note      → Record a decision
# - exit      → Save and quit
```

### Command-Line Mode (Quick Checks)
```bash
# Quick status check
python3 plan_orchestrator.py status

# Start next available sub-plan
python3 plan_orchestrator.py next

# Update progress (after completing a phase)
python3 plan_orchestrator.py update 00 25

# Mark complete
python3 plan_orchestrator.py complete 00
```

---

## 🎯 Typical Work Session

```bash
# 1. Start orchestrator
python3 plan_orchestrator.py

# 2. Check status
Command: status
# Shows: Sub-Plan 00 ready (no dependencies)

# 3. Start first work
Command: next
# Opens Sub-Plan 00: Test Coverage Sprint

# 4. Work on Phase 1 (Brain Protection Tests)
# - Open: 00-test-coverage-sprint/00-test-coverage-sprint.md
# - Write 25 tests for brain_protection/
# - Run tests to verify

# 5. Update progress
Command: update
Sub-Plan #: 00
Progress %: 12
# (Phase 1/8 = 12.5%)

# 6. Add note
Command: note
Note: Phase 1 complete - 25 brain protection tests written

# 7. Continue to Phase 2...
# Repeat steps 4-6 for each phase

# 8. Complete when all phases done
Command: complete
Sub-Plan #: 00
# Unlocks Sub-Plans 01, 02, 05

# 9. Move to next sub-plan
Command: next
# Starts Sub-Plan 01 or 02

# 10. Exit when done
Command: exit
```

---

## 📊 Progress Tracking Formula

**Per Phase:**
```
Progress % = (Completed Phases / Total Phases) * 100
```

**Sub-Plan 00 Example (8 phases):**
- Phase 1 → 12%
- Phase 2 → 25%
- Phase 3 → 37%
- Phase 4 → 50% ✨ **Gate 1 Unlocked!**
- Phase 5 → 62%
- Phase 6 → 75%
- Phase 7 → 87%
- Phase 8 → 100% ✅ **Sub-Plan Complete!**

---

## 🎯 Milestones to Watch

| Milestone | Trigger | Unlocks |
|-----------|---------|---------|
| **Gate 1: 50% Coverage** | Sub-Plan 00 @ 50% | Sub-Plans 01, 02, 05 |
| **Gate 2: 80% Coverage** | Sub-Plan 00 @ 80% | Full confidence for all work |
| **Orchestrators Complete** | Sub-Plans 01, 02 done | Sub-Plan 08 |
| **Production Ready** | Sub-Plan 09 done | 🎉 CORTEX v5 Launch! |

---

## 🔥 Pro Tips

### 1. **Check Status Often**
```bash
# Quick check without entering interactive mode
python3 plan_orchestrator.py status | head -20
```

### 2. **Combine with Git**
```bash
# After each phase
python3 plan_orchestrator.py update 00 25
git add .
git commit -m "Phase 2: Common orchestrator tests (25%)"
```

### 3. **Use Notes for Decisions**
```bash
Command: note
Note: Chose pytest-asyncio for async test support in Phase 3
```

### 4. **Review Notes Between Sessions**
```bash
Command: notes
# Shows last 10 notes to remember where you left off
```

### 5. **Stay in Interactive Mode**
- Start interactive mode once
- Work through multiple phases
- Update progress as you go
- Only exit when switching focus

---

## 🚨 Common Issues

### "Sub-plan is blocked by dependencies"
**Solution:** Check what's blocking:
```bash
python3 plan_orchestrator.py status
# Look at blocked sub-plans
# Complete dependencies first
```

### "python: command not found"
**Solution:** Use `python3`:
```bash
python3 plan_orchestrator.py
```

### Lost Track of Progress?
**Solution:** Check session notes:
```bash
Command: notes
# Shows what you did last
```

---

## 📚 Full Documentation

- **Orchestrator Guide**: `README-ORCHESTRATOR.md`
- **Master Plan**: `00-cortex-v5-gap-remediation/00-MASTER-REMEDIATION-PLAN.md`
- **Sub-Plans**: `00-test-coverage-sprint/` through `09-final-validation/`

---

## ⚡ Right Now

**Your next command:**
```bash
cd cortex-brain/documents/planning/active/CORTEX-5.0
python3 plan_orchestrator.py
```

**Then type:** `next`

**This starts:** Sub-Plan 00 - Test Coverage Sprint (Phase 1: Brain Protection Tests)

---

🎯 **Good luck!** The orchestrator will guide you through all 10 sub-plans to production readiness.
