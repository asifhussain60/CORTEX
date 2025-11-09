# CORTEX Universal Entry Point

**Purpose:** Single command for ALL CORTEX interactions. You don't need to remember multiple commands - just use this one and CORTEX figures out what you need.

**Version:** 5.0 (Modular Architecture - UNBLOATED)  
**Status:** 🎯 PRODUCTION  
**Architecture:** Modular documentation with plug-in references

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms  
**Repository:** https://github.com/asifhussain60/CORTEX

---

## 🚀 Quick Start

### How to Use CORTEX

Just tell CORTEX what you want in natural language:

```markdown
#file:prompts/user/cortex.md

Add a purple button to the HostControlPanel
```

**Or use optional slash commands for speed:**

```markdown
#file:prompts/user/cortex.md

/mac
/setup
/resume
```

CORTEX will:
- ✅ Detect your intent (PLAN, EXECUTE, TEST, VALIDATE, etc.)
- ✅ Route to appropriate specialist agent
- ✅ Execute workflow with memory of past conversations
- ✅ Track progress for future reference

---

## 📚 Documentation Modules

**Choose what you need based on your intent:**

### 🧚 Story - "The Intern with Amnesia"
**When:** First time using CORTEX, explaining to stakeholders, understanding why CORTEX exists

**Load the story:**
```markdown
#file:prompts/shared/story.md
```

**What you'll learn:**
- Human-centered explanation of CORTEX
- The dual-hemisphere brain architecture
- How Tier 1, 2, 3 solve amnesia problem
- How agents coordinate work

---

### 🚀 Setup - Getting Started Guide
**When:** First-time installation, troubleshooting setup, cross-platform migration

**Load the setup guide:**
```markdown
#file:prompts/shared/setup-guide.md
```

**What you'll learn:**
- Environment setup (Windows, macOS, Linux)
- Dependency installation
- Brain initialization
- Configuration options
- Conversation tracking setup

---

### 🔧 Technical - Architecture & API Reference
**When:** Developer integration, API calls, architecture deep-dive, plugin development

**Load technical docs:**
```markdown
#file:prompts/shared/technical-reference.md
```

**What you'll learn:**
- Tier 1, 2, 3 API reference
- Agent system architecture
- Plugin development
- Configuration reference
- Testing protocols
- Performance benchmarks

---

### 🤖 Agents - How CORTEX Thinks
**When:** Understanding agent system, troubleshooting workflows, extending CORTEX

**Load agent documentation:**
```markdown
#file:prompts/shared/agents-guide.md
```

**What you'll learn:**
- Intent routing system
- 10 specialist agents (left + right brain)
- Corpus callosum coordination
- Workflow orchestration
- Agent responsibilities

---

### 📊 Tracking - Conversation Memory
**When:** Setting up conversation tracking, troubleshooting amnesia, enabling "continue" command

**Load tracking guide:**
```markdown
#file:prompts/shared/tracking-guide.md
```

**What you'll learn:**
- Why tracking is needed
- 3 tracking methods (PowerShell, Python CLI, Ambient Daemon)
- How to enable auto-tracking
- Troubleshooting conversation amnesia

---

### ⚙️ Configuration - Advanced Settings
**When:** Customizing CORTEX behavior, multi-machine setup, troubleshooting config

**Load configuration reference:**
```markdown
#file:prompts/shared/configuration-reference.md
```

**What you'll learn:**
- cortex.config.json structure
- Tier 1, 2, 3 configuration options
- Machine-specific settings
- Feature flags
- Path configuration

---

### 🔄 Platform Switch - Automatic Cross-Platform Setup
**When:** CORTEX automatically detects when you switch between Mac/Windows/Linux

**What happens automatically:**
- ✅ **Platform detection** on startup (Mac, Windows, or Linux)
- ✅ **Auto-configuration** when platform changes detected
- ✅ Git pull latest code
- ✅ Configure platform-specific paths and environment
- ✅ Quick dependency check
- ✅ Validate tooling (Git, Python, etc.)

**Manual override:**
```markdown
#file:prompts/user/cortex.md

setup environment
/setup
```

**Documentation:**
```markdown
#file:docs/plugins/platform-switch-plugin.md
```

**Supported Platforms:**
- 🍎 macOS (Darwin) - zsh, Unix paths
- 🪟 Windows - PowerShell, Windows paths
- 🐧 Linux - bash, Unix paths

---

## 🎯 How to Use CORTEX

### 💬 Natural Language (Recommended)

**CORTEX is designed to understand natural language.** Just tell it what you need:

```markdown
#file:prompts/user/cortex.md

Add a purple button to the dashboard
setup environment
show me where I left off
```

**Why natural language?**
- ✅ No syntax to memorize
- ✅ Context-aware understanding
- ✅ Accessible to all skill levels

---

### ⚡ Optional: Slash Commands (Power Users)

**Slash commands are shortcuts** for common operations. They're entirely optional!

#### 📦 Platform & Session Commands
| Command | Natural Language Equivalent | What It Does |
|---------|---------------------------|--------------|
| `/setup` | "setup environment" | Setup/configure current platform |
| `/resume` | "resume work" | Resume from where you left off |
| `/status` | "show progress" | Show current work status |
| `/help` | "show available commands" | Display all commands |

*Aliases for /setup: `/env`, `/environment`, `/configure`*

**Note:** Platform detection is automatic! CORTEX detects Mac/Windows/Linux on startup.

#### 🔧 VS Code Extension Commands
**Available in VS Code Chat (`@cortex`):**
- `/resume` - Resume last conversation
- `/checkpoint` - Save conversation state
- `/history` - View conversation history
- `/optimize` - Optimize token usage
- `/instruct` - Give CORTEX new instructions

---

### 📚 Documentation Access

| Command | What It Does |
|---------|--------------|
| `#file:prompts/shared/story.md` | Read "The Intern with Amnesia" story |
| `#file:prompts/shared/setup-guide.md` | View installation and setup guide |
| `#file:prompts/shared/technical-reference.md` | Access API and architecture docs |
| `#file:prompts/shared/agents-guide.md` | Learn about agent system |
| `#file:prompts/shared/tracking-guide.md` | Enable conversation memory |
| `#file:prompts/shared/configuration-reference.md` | Configure CORTEX settings |

---

## 🔌 Plugin Commands (Extensible)

**Plugins can register their own commands!** As you add plugins, new commands become available.

**Current plugins with commands:**
- **Platform Switch Plugin:** `/setup` (auto-detects Mac/Windows/Linux)

**How it works:**
1. Plugin defines commands during initialization
2. Commands are registered to global registry
3. Router expands commands to natural language
4. Intent detection and routing proceeds normally

**For plugin developers:** See `src/plugins/command_registry.py` for API

---

## ⚠️ CRITICAL: Conversation Tracking

**GitHub Copilot Chat does NOT automatically track conversations to the CORTEX brain.**

Without tracking: ❌ No memory across chats, ❌ "Make it purple" fails  
With tracking: ✅ Full conversation memory, ✅ "Make it purple" works

**See tracking guide for setup:**
```markdown
#file:prompts/shared/tracking-guide.md
```

---

## 🔄 Migration Note

**This is the NEW modular architecture (CORTEX 2.0).**

**Token Reduction:** 97.2% smaller than old monolithic file (74,047 → 2,078 tokens avg)

**What changed:**
- ❌ **OLD:** 8,701-line monolithic file (bloated)
- ✅ **NEW:** 300-line slim entry + focused modules (unbloated)

**Benefits:**
- ✅ 97% faster loading
- ✅ Cleaner, more maintainable
- ✅ Load only what you need
- ✅ Easier to extend

**Old file backed up:** `prompts/user/cortex-BACKUP-2025-11-08.md`

---

## 📦 Module Directory Structure

```
prompts/
├── user/
│   └── cortex.md (THIS FILE - slim entry point)
│
└── shared/
    ├── story.md (The Intern with Amnesia)
    ├── setup-guide.md (Installation & configuration)
    ├── technical-reference.md (API & architecture)
    ├── agents-guide.md (Agent system explained)
    ├── tracking-guide.md (Conversation memory setup)
    └── configuration-reference.md (Advanced settings)
```

**All modules available for direct reference or through this entry point.**

---

## 🎯 Intent Detection (Automatic)

CORTEX automatically detects your intent and loads appropriate modules:

| Your Request | Detected Intent | Module Loaded |
|--------------|----------------|---------------|
| "Tell me the CORTEX story" | STORY | story.md |
| "How do I install CORTEX?" | SETUP | setup-guide.md |
| "Show me the Tier 1 API" | TECHNICAL | technical-reference.md |
| "How do agents work?" | AGENTS | agents-guide.md |
| "Enable conversation tracking" | TRACKING | tracking-guide.md |
| "Add a purple button" | EXECUTE | (uses knowledge graph) |
| "Create a test plan" | PLAN | (uses knowledge graph) |

**No need to manually reference modules - CORTEX routes intelligently.**

---

## 🏆 Why This Matters

**Old monolithic approach:**
- 74,047 tokens loaded on EVERY request
- $2.22 per request (GPT-4 pricing)
- 2-3 seconds to parse
- Difficult to maintain (8,701 lines)

**New modular approach:**
- 2,078 tokens average (97.2% reduction)
- $0.06 per request (97% cost savings)
- 80ms to parse (97% faster)
- Easy to maintain (200-400 lines per module)

**Annual savings:** $25,920/year for typical usage (1,000 requests/month)

**Additional optimization:**
- Brain protection rules moved to YAML (75% token reduction)
- Configuration file: `cortex-brain/brain-protection-rules.yaml`
- Tests: `tests/tier0/test_brain_protector.py` (22/22 passing ✅)

---

## 📖 Next Steps

1. **First time?** Read the story: `#file:prompts/shared/story.md`
2. **Need to install?** Setup guide: `#file:prompts/shared/setup-guide.md`
3. **Developer?** Technical docs: `#file:prompts/shared/technical-reference.md`
4. **Enable tracking:** Tracking guide: `#file:prompts/shared/tracking-guide.md`
5. **Start working:** Just tell CORTEX what you need!

---

**Phase 3 Validation Complete:** 95-97% token reduction achieved  
**Decision:** STRONG GO (4.75/5 score)  
**Status:** Modular architecture PRODUCTION READY ✅

**Full technical details:** See `prompts/validation/PHASE-3-VALIDATION-REPORT.md`

---

*Last Updated: 2025-11-08 | CORTEX 2.0 Modular Architecture | Phase 3 Complete*
