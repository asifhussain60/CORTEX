# CORTEX Learning Library

**Version:** 2.0.0 | **Author:** Asif Hussain | **Status:** ✅ Production

---

## ⚠️ Update Needed

**Last Update:** November 17, 2025 (20 days ago)  
**Recent Activity:** 166 commits in last 3 days  
**Action Required:** Run `"update learning library"` to capture lessons from recent work

---

## Welcome to CORTEX Learning Library

This learning library captures and documents lessons from git history through **interactive sessions**, helping you learn from past work and avoid repeating mistakes.

> **Note:** This is a **manual capture system** - lessons are documented through interactive prompts when you run the update command. The system does NOT automatically generate documentation from commits.

### 🎯 What It Does

The Learning Library system:
- **Scans git history** for learning-worthy commits (fixes, features, refactors)
- **Filters intelligently** using heuristics (line count, test changes, error keywords)
- **Captures lessons interactively** with problem/solution/prevention prompts
- **Detects duplicates** using FTS5 full-text similarity (70% threshold)
- **Writes to YAML** with validation and automatic backups

### 🚀 Quick Start

To capture lessons from your recent work:

```bash
# In Copilot Chat
"update learning library"
"update learning library from last 48 hours"
"capture lessons from past week"
```

The agent will:
1. Scan git commits from the specified timeframe (default: 24 hours)
2. Filter for learning-worthy candidates (heuristics: errors, tests, large changes)
3. **Prompt you interactively** for each lesson (problem, solution, prevention)
4. Check for duplicates using FTS5 full-text similarity (70% threshold)
5. Update `cortex-brain/lessons-learned.yaml` with validated lessons

### 💡 Why Interactive Capture?

**Quality over Quantity:** Interactive prompts ensure lessons are:
- **Meaningful:** You explain the actual problem/solution, not auto-generated noise
- **Accurate:** Commit messages often lack context - you provide the real story
- **Actionable:** Prevention rules are prescriptive, not vague
- **Verified:** You confirm it's worth documenting (not all commits are lessons)

**vs. Automatic:** AI cannot infer:
- Why the bug happened (commit shows fix, not root cause)
- What you learned (commit shows change, not insight)  
- How to prevent it (commit shows solution, not prevention strategy)

### 📊 Current Library Status

- **Total Lessons:** 20 captured
- **Last Update:** November 17, 2025 (20 days ago)
- **Recent Commits:** 166 in last 3 days (not yet documented)
- **Coverage:** Validation, TDD, WPF, Filesystem, Performance, Git workflows

**Action Needed:** Run `"update learning library"` to capture lessons from 166 recent commits!

### 🏗️ How It Works

**Architecture:**
1. **GitHistoryScanner** - Extracts commit metadata from git log
2. **CommitFilter** - Applies heuristics to identify learning candidates
3. **LessonCapture** - Interactive prompts for lesson details
4. **DuplicationDetector** - FTS5 similarity matching (70% threshold)
5. **YAMLWriter** - Validates and writes to `lessons-learned.yaml`
6. **LearningLibrarianAgent** - Orchestrates full workflow from natural language

**Example Workflow:**
```
User: "update learning library from last 48 hours"
  ↓
Agent extracts timeframe → 48 hours
  ↓
Scanner finds 47 commits
  ↓
Filter identifies 3 learning-worthy candidates
  ↓
User answers prompts for each lesson
  ↓
Detector checks for duplicates
  ↓
Writer saves to YAML with backup
```

### 📊 Test Coverage

The Learning Library system has excellent test coverage:

- **Phase 1 (Scanner):** 7 tests, 85% coverage
- **Phase 2 (Filter):** 6 tests, 91% coverage
- **Phase 3 (Capture):** 12 tests, 89% coverage
- **Phase 4 (Detector):** 11 tests, 89% coverage
- **Phase 5 (Writer):** 14 tests, 88% coverage
- **Phase 6 (Agent):** 9 tests, 100% pass
- **Overall:** 59 tests, 87% coverage

### 🔗 External Resources

- [CORTEX GitHub Repository](https://github.com/asifhussain60/CORTEX)
- [Planning Orchestrator Guide](https://github.com/asifhussain60/CORTEX/tree/main/.github/prompts/modules/planning-orchestrator-guide.md)
- [TDD Mastery Guide](https://github.com/asifhussain60/CORTEX/tree/main/.github/prompts/modules/tdd-mastery-guide.md)

### 📞 Support

For questions or issues:

- Use the `feedback` command in CORTEX
- Check the GitHub repository for documentation
- Review test files for implementation examples

---

**Last Updated:** December 7, 2025  
**System Version:** CORTEX 3.8.1 + Learning Library 2.0.0
