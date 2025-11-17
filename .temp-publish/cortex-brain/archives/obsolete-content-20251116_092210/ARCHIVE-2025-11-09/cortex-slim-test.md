# CORTEX Slim Entry Point (TEST VERSION)

**Purpose:** Minimal entry point that routes to specialized modules  
**Status:** VALIDATION TEST - Phase 3 Modular Entry Point Validation  
**Version:** 2.0.0-test  
**Target Token Reduction:** 95% (7,026 lines → ~400 lines when loaded with module)

---

## 🚀 Quick Start

### How to Use CORTEX

Just tell CORTEX what you want in natural language:

```markdown
#file:prompts/user/cortex-slim-test.md

Add a purple button to the HostControlPanel
```

CORTEX will:
- ✅ Detect your intent (PLAN, EXECUTE, TEST, VALIDATE, etc.)
- ✅ Route to appropriate specialist agent
- ✅ Execute workflow with memory of past conversations
- ✅ Track progress for future reference

---

## 📚 Documentation Modules

**Select what you need based on your intent:**

### 🧚 Story - "The Intern with Amnesia"
**When to use:** First time using CORTEX, explaining to stakeholders, understanding why CORTEX exists

**Command:**
```markdown
#file:prompts/user/cortex-slim-test.md story
```

Or directly:
```markdown
#file:prompts/shared/test/story-excerpt.md
```

**What you'll learn:**
- Human-centered explanation of CORTEX
- The dual-hemisphere brain architecture
- How Tier 1, 2, 3 solve amnesia problem
- How agents coordinate work

---

### 🚀 Setup - Getting Started Guide
**When to use:** First-time installation, troubleshooting setup, cross-platform migration

**Command:**
```markdown
#file:prompts/user/cortex-slim-test.md setup
```

Or directly:
```markdown
#file:prompts/shared/test/setup-excerpt.md
```

**What you'll learn:**
- Environment setup (Windows, macOS, Linux)
- Dependency installation
- Brain initialization
- Configuration options
- Conversation tracking setup

---

### 🔧 Technical - Architecture & API Reference
**When to use:** Developer integration, API calls, architecture deep-dive, plugin development

**Command:**
```markdown
#file:prompts/user/cortex-slim-test.md technical
```

Or directly:
```markdown
#file:prompts/shared/test/technical-excerpt.md
```

**What you'll learn:**
- Tier 1, 2, 3 API reference
- Agent system architecture
- Plugin development
- Configuration reference
- Testing protocols
- Performance benchmarks

---

## 🎯 Common Commands

| Command | What It Does |
|---------|--------------|
| `#file:prompts/user/cortex-slim-test.md story` | Read "The Intern with Amnesia" story |
| `#file:prompts/user/cortex-slim-test.md setup` | View setup and installation guide |
| `#file:prompts/user/cortex-slim-test.md technical` | Access API reference and architecture |
| `#file:prompts/user/cortex.md` | Use full documentation (baseline) |

---

## ⚙️ Agent Routing (Automatic)

CORTEX automatically detects your intent and routes to the right specialist:

| Your Request | Detected Intent | Agent | Module Loaded |
|--------------|----------------|-------|---------------|
| "Tell me the CORTEX story" | STORY | Intent Router | story-excerpt.md |
| "How do I install CORTEX?" | SETUP | Intent Router | setup-excerpt.md |
| "Show me the Tier 1 API" | TECHNICAL | Intent Router | technical-excerpt.md |
| "Add a purple button" | EXECUTE | Code Executor | (uses knowledge graph) |
| "Create a test plan" | PLAN | Work Planner | (uses knowledge graph) |
| "Run tests" | TEST | Test Generator | (uses knowledge graph) |

---

## ⚠️ Important: Conversation Tracking

**GitHub Copilot Chat does NOT automatically track conversations to the CORTEX brain.**

Without tracking: ❌ No memory across chats  
With tracking: ✅ "Make it purple" works, full context

**Quick Fix:**
```powershell
# After each session (Windows)
.\scripts\cortex-capture.ps1 -AutoDetect
```

```bash
# After each session (macOS/Linux)
python scripts/cortex_cli.py --auto-capture
```

**Or use Ambient Daemon (Phase 2 - automatic):**
```bash
python scripts/cortex/auto_capture_daemon.py
```

---

## 🧪 TEST VALIDATION METRICS

**This is a TEST version for Phase 3 validation.**

**Baseline (Full cortex.md):**
- Lines: 7,026
- Estimated tokens: ~28,000

**Modular (Slim + Module):**
- Slim entry: 200 lines
- Module (story/setup/technical): 200 lines
- **Total: 400 lines**
- **Estimated tokens: ~1,600**
- **Token reduction: 94.3%**

**Test Scenarios:**
1. Story request → Loads slim + story-excerpt (400 lines total)
2. Setup request → Loads slim + setup-excerpt (400 lines total)
3. Technical request → Loads slim + technical-excerpt (400 lines total)
4. Backward compatibility → Full cortex.md still works (7,026 lines)

**Expected Results:**
- ✅ Single entry point maintained (user only uses cortex-slim-test.md)
- ✅ Module loading invisible to user
- ✅ 95% token reduction vs baseline
- ✅ Zero breaking changes to commands

**Validation Timeline:**
- Week 11, Days 1-2: Create test structure ✅
- Week 11, Days 3-4: Execute test scenarios 📋
- Week 11, Day 5: Measure token counts 📋
- Week 12, Days 1-2: Validate backward compatibility 📋
- Week 12, Days 3-4: Document results and GO/NO-GO decision 📋

---

## 🔄 Backward Compatibility

**Full documentation still available:**
```markdown
#file:prompts/user/cortex.md

<your request>
```

This loads the complete 7,026-line documentation (baseline behavior).

---

## 📊 Next Steps After Validation

**If GO (≥3.5/5 decision score):**
- Proceed to full modular split (15-21 hours)
- Split cortex.md into 10+ focused modules
- Update all documentation references
- Migration guide for users

**If NO-GO (<3.5/5 decision score):**
- Implement Python-controlled context injection
- Intelligent detection of needed documentation
- Dynamic loading within Python code
- No changes to cortex.md file

**If HYBRID (3.0-3.4/5 decision score):**
- Combine modular approach + Python injection
- Best of both worlds

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms  
**Repository:** https://github.com/asifhussain60/CORTEX

**Full Documentation:** `#file:prompts/user/cortex.md` (7,026 lines - baseline)  
**Test Validation:** Phase 3 - Modular Entry Point Validation (Week 11-12)
