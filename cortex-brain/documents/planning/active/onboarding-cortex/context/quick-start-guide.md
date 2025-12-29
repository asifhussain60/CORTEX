# ⚡ CORTEX Quick Start Guide

**Version:** 4.0.0  
**Author:** Asif Hussain  
**Purpose:** Get started with CORTEX in 10 minutes

---

## 🎯 Goal

Complete your first CORTEX operation successfully in under 10 minutes.

---

## ✅ Prerequisites (2 minutes)

Verify you have:

- [ ] VS Code installed
- [ ] GitHub Copilot extension active
- [ ] Python 3.9+ installed
- [ ] Terminal access

**Quick Check:**
```bash
code --version
python3 --version
```

---

## 📦 Installation (2 minutes)

### Option 1: Quick Install (Recommended)

In VS Code terminal:
```bash
pip install cortex-ai
```

### Option 2: Development Install

```bash
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX
pip install -e .
```

### Verify Installation

In Copilot Chat:
```
help
```

**Expected:** List of CORTEX operations

---

## 🎓 Your First Operation (5 minutes)

### Step 1: Create a Plan (2 min)

In Copilot Chat, type:
```
plan "hello world feature"
```

**What Happens:**
1. CORTEX creates folder: `cortex-brain/documents/planning/active/hello-world-feature/`
2. Generates master plan: `00-master-plan.md`
3. Creates subfolders: `context/`, `reports/`, `artifacts/`, `tracking/`
4. Initializes progress tracker

**Verify:**
```bash
ls -la cortex-brain/documents/planning/active/hello-world-feature/
```

**Expected Output:**
```
00-master-plan.md
context/
reports/
artifacts/
tracking/
```

---

### Step 2: Start TDD Workflow (3 min)

In Copilot Chat:
```
start tdd for hello world function
```

**RED Phase: Write Failing Test**

CORTEX will guide you to create:
```python
# tests/test_hello.py
def test_hello_world():
    result = hello_world()
    assert result == "Hello, World!"
```

Run test (should fail):
```bash
pytest tests/test_hello.py
```

**GREEN Phase: Implement**

CORTEX will help you create:
```python
# src/hello.py
def hello_world():
    return "Hello, World!"
```

Run test (should pass):
```bash
pytest tests/test_hello.py
```

**REFACTOR Phase: Improve**

CORTEX will suggest:
```python
# src/hello.py
def hello_world() -> str:
    """Returns a friendly greeting."""
    return "Hello, World!"
```

**Complete:**
```
complete tdd
```

**Result:** Git checkpoint created ✅

---

## 🎉 Success! You've Completed:

- ✅ Installed CORTEX
- ✅ Created your first plan
- ✅ Completed full TDD cycle (RED→GREEN→REFACTOR)
- ✅ Generated proper folder structure

**Time Invested:** ~10 minutes  
**Skills Gained:** Core CORTEX workflow

---

## 🚀 Next Steps (Choose Your Path)

### Path 1: Immediate Practice (10 min)
```
plan "todo list API"
start tdd
```

Build a simple todo list with CRUD operations.

---

### Path 2: Deep Learning (60 min)

Read full onboarding plan:
```
Open: 00-master-plan.md
```

Complete all 6 phases for comprehensive understanding.

---

### Path 3: Exploration (15 min)

Try these commands:
```
system maintenance    # Check system health
help                  # View all commands
discover plans        # See existing plans
```

---

## 🛠️ Common Quick Fixes

### "Command not recognized"

**Fix:**
```
help  # Shows correct syntax
```

**Remember:** Use natural language, not slash commands.

---

### "Module not found: cortex"

**Fix:**
```bash
pip install --upgrade cortex-ai
```

---

### "Planning folder not created"

**Fix:**
```
system maintenance  # Verifies system health
```

Check that `cortex-toolkit/` is accessible.

---

## 📖 Essential Resources

### Must-Read (5 min each)

1. **Command Reference:** `context/command-reference.md`
2. **Architecture:** `context/architecture-overview.md`
3. **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml`

### When You Need Help

**Quick answers:**
```
help
quick: [your question]
```

**Detailed guidance:**
```
explain: [concept]
```

**Full documentation:**
- Web: https://asifhussain60.github.io/CORTEX/
- Local: `.github/prompts/`

---

## 🎯 Quick Reference Card

### Top 5 Commands

```
1. plan [feature]           # Create new plan
2. start tdd                # Begin TDD workflow
3. system maintenance       # Health check
4. help                     # View commands
5. status of [plan]         # Check progress
```

### Key Shortcuts

| Action | Command |
|--------|---------|
| Create plan | `plan "feature name"` |
| Begin TDD | `start tdd` |
| Check health | `system maintenance` |
| Get help | `help` |
| Search code | `search [query]` |

---

## 🏆 Completion Checklist

Mark off as you go:

- [ ] CORTEX installed
- [ ] `help` command works
- [ ] Created first plan
- [ ] Verified folder structure
- [ ] Completed TDD cycle (RED→GREEN→REFACTOR)
- [ ] Tests passing
- [ ] Git checkpoint created

**All checked?** 🎉 You're ready to use CORTEX!

---

## 🔥 Pro Tips

### Tip 1: Always Plan First
```
plan [feature]  # THEN implement
```

Prevents duplication, ensures structure.

---

### Tip 2: TDD Always
```
start tdd  # Write test before code
```

CORTEX enforces this via SKULL rules.

---

### Tip 3: Weekly Maintenance
```
system maintenance  # Every Monday
```

Keeps codebase healthy.

---

### Tip 4: Search Before Create
```
discover plans  # Check for existing work
```

HOLISTIC_DISCOVERY prevents duplication.

---

### Tip 5: Use Natural Language
```
✅ plan user authentication
❌ /plan user-auth
```

No slash commands needed!

---

## 📊 Your Learning Progress

### Completed
- ✅ Installation
- ✅ First operation
- ✅ TDD workflow

### Next
- ⏭️ Phase 2: Core Concepts (10 min)
- ⏭️ Phase 3: Advanced Operations (15 min)
- ⏭️ Phase 4: System Architecture (20 min)

**Current Level:** Beginner → Intermediate path unlocked!

---

## 🎓 Continue Learning

**Full Onboarding:** `00-master-plan.md`  
**Architecture Deep Dive:** `context/architecture-overview.md`  
**All Commands:** `context/command-reference.md`

**Estimated Total Time:** 60 minutes for full mastery

---

## 🆘 Need Help?

**Immediate Support:**
```
help
quick: [your question]
```

**Documentation:**
- Web: https://asifhussain60.github.io/CORTEX/
- GitHub: https://github.com/asifhussain60/CORTEX

**Community:**
- Issues: https://github.com/asifhussain60/CORTEX/issues
- Discussions: https://github.com/asifhussain60/CORTEX/discussions

---

## 🎉 Congratulations!

You've completed the CORTEX Quick Start and are ready to build amazing software with AI-enhanced workflows!

**Next:** Continue to full onboarding for deeper understanding.

---

**Copyright © 2025 Asif Hussain. All rights reserved.**
