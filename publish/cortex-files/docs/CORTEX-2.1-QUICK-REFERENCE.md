# CORTEX 2.1 - Quick Reference

**Version:** 2.1.0 (Interactive Planning)  
**Status:** Design Complete ✅  
**Date:** November 9, 2025

---

## 🎯 What's New

**Flagship Feature:** Interactive Feature Planning  
- CORTEX asks clarifying questions before creating plans
- One question at a time (max 5 questions)
- User controls: skip, done, back, abort
- Learns your preferences over time

---

## ⚡ New Commands (7 Total)

| Command | What It Does | When to Use |
|---------|--------------|-------------|
| `/CORTEX, refresh cortex story` | Update CORTEX story docs | After major changes |
| `/CORTEX, let's plan a feature` ⭐ | **Interactive planning** | Complex/ambiguous features |
| `/CORTEX, architect a solution` | Design architecture | System design decisions |
| `/CORTEX, refactor this module` | Interactive refactoring | Code restructuring |
| `/CORTEX, run brain protection` | Validate brain rules | Health checks |
| `/CORTEX, run tests` | Execute test suite | Testing |
| `/CORTEX, generate documentation` | Auto-generate docs | Documentation |

⭐ = New interactive planning feature

---

## 💬 Example: Interactive Planning

```
User: /CORTEX, let's plan a feature - add dark mode

CORTEX: Question 1/5: Which components need dark mode?
  A) All components
  B) Specific pages
  C) User preference toggle

User: A

CORTEX: Question 2/5: Include system preference detection?
  A) Yes (auto-detect OS theme)
  B) No (manual toggle only)

User: A

CORTEX: Perfect! Here's the plan:
  - Add theme context provider
  - Dark mode CSS variables
  - System preference detection
  - Update all components
  
Proceed? yes

CORTEX: Starting implementation! 🚀
```

---

## 📚 Key Documents

1. **Design Document:** `docs/design/CORTEX-2.1-INTERACTIVE-PLANNING.md`
   - Complete architecture and implementation guide
   - 50+ pages comprehensive design

2. **Session Summary:** `cortex-brain/CORTEX-2.1-PLANNING-SESSION.md`
   - Design decisions captured
   - User requirements and validation

3. **Entry Point:** `.github/prompts/CORTEX.prompt.md`
   - Updated with new commands
   - Version 5.1

---

## 🏗️ Architecture Summary

### New Components
- **Interactive Planner Agent** (Right Brain)
- **Question Generator Utility**
- **Tier 1 Memory Extension** (planning sessions)
- **Tier 2 Knowledge Enhancement** (user preferences)
- **Command Router Enhancement** (7 new commands)

### Design Principles
- ✅ Opt-in (not forced)
- ✅ Bounded (max 5 questions)
- ✅ Learning (remembers preferences)
- ✅ User control (skip, done, abort)
- ✅ Backward compatible

---

## 📊 Implementation Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Infrastructure | Week 1 | Core agents, Tier 1 schema |
| Phase 2: Conversation | Week 2 | State machine, user controls |
| Phase 3: Commands | Week 2 | Router integration, docs |
| Phase 4: Learning | Week 3 | Preference memory, patterns |
| Phase 5: Polish | Week 4 | UX refinements, migration |

**Total:** 4 weeks to production

---

## 🎯 Success Metrics

| Metric | Target |
|--------|--------|
| Plan accuracy | >90% |
| Questions/session | 3-5 avg |
| User satisfaction | >4/5 |
| Rework reduction | >60% |

---

## ✅ Next Steps

1. **Review design documents** ✅ DONE
2. **Approve for implementation** ← YOU ARE HERE
3. **Allocate resources** (developers, testers)
4. **Begin Phase 1** (Infrastructure)
5. **Beta testing** (Week 3)
6. **Production release** (Week 4)

---

## 🚀 Getting Started (After Implementation)

**Try it out:**
```
/CORTEX, let's plan a feature - your feature idea here
```

**Natural language also works:**
```
CORTEX, let's plan how to add authentication
```

---

*Quick Reference | CORTEX 2.1 | Ready for Implementation*
