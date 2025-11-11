# CORTEX Universal Entry Point

**Purpose:** Single command for ALL CORTEX interactions. You don't need to remember multiple commands - just use this one and CORTEX figures out what you need.

**Version:** 5.2 (Response Template Architecture)  
**Status:** ✅ PRODUCTION  
**Architecture:** Template-based responses + Modular documentation + Interactive Planning

---

## ⚡ RESPONSE TEMPLATES (NEW!)

**When user says "help" or similar:**
1. Load `#file:cortex-brain/response-templates.yaml`
2. Find matching trigger
3. Return pre-formatted response
4. **NO Python execution needed!**

**Triggers:**
- `help`, `/help`, `/CORTEX help` → Quick table
- `help detailed` → Categorized commands
- `status` → Implementation status
- `help <command>` → Command-specific help
- `quick start` → First-time user guide

### 🧠 Contextual Intelligence (Architecture Utilization)

**CORTEX automatically adapts based on work context:**

| Work Type | Response Focus | Agents Activated | Template Style |
|-----------|---------------|------------------|----------------|
| **Feature Implementation** | Code + tests | Executor, Tester, Validator | Technical detail |
| **Debugging/Issues** | Root cause analysis | Health Validator, Pattern Matcher | Diagnostic focus |
| **Testing/Validation** | Coverage + edge cases | Tester, Validator | Validation-centric |
| **Architecture/Design** | System impact | Architect, Work Planner | Strategic overview |
| **Documentation** | Clarity + examples | Documenter | User-friendly |
| **General Questions** | Concise answers | Intent Detector | Minimal detail |

**How it works:**
- Tier 2 Knowledge Graph learns from past interactions
- Pattern Matcher detects work context automatically
- Response templates adapt (but you can override anytime)
- All 10 agents coordinate via Corpus Callosum when needed

**User control:** Say "be more [concise/detailed/technical]" to adjust on the fly

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms  
**Repository:** https://github.com/asifhussain60/CORTEX

---

## 🚀 Quick Start

### How to Use CORTEX

**Need a quick reminder?**
```
/CORTEX help
```
Shows all available commands in a concise table.

Just tell CORTEX what you want in natural language:

```
Add a purple button to the HostControlPanel
```

**Or use optional slash commands for speed:**

```
/setup
/resume
/status
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
```
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
```
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
```
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
```
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
```
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
```
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
```
setup environment
/setup
```

**Documentation:**
```
#file:docs/plugins/platform-switch-plugin.md
```

**Supported Platforms:**
- 🍎 macOS (Darwin) - zsh, Unix paths
- 🪟 Windows - PowerShell, Windows paths
- 🐧 Linux - bash, Unix paths

---

## 🎯 How to Use CORTEX

### 💬 Natural Language (The CORTEX Way)

**CORTEX uses natural language only.** Just tell it what you need:

```
Add a purple button to the dashboard
setup environment
show me where I left off
demo
cleanup
refresh story
```

**Execution Modes:**

CORTEX automatically detects whether you want to preview changes or execute them:

**Dry-Run Mode (Preview Only):**
```
preview cleanup
dry-run optimization
test cleanup before running
what would cleanup do
show me what would be cleaned
simulate story refresh
```

**Live Mode (Apply Changes):**
```
cleanup workspace
run optimization
execute cleanup
actually cleanup now
apply changes
```

**Default:** If no mode keyword is detected, CORTEX defaults to live execution.

**Why natural language?**
- ✅ No syntax to memorize
- ✅ Intuitive for all skill levels
- ✅ Context-aware understanding
- ✅ Flexible and forgiving
- ✅ Works in conversation naturally
- ✅ Automatic dry-run/live detection

**Speed Options:**
- **Terse:** `setup`, `demo`, `cleanup` (5-7 characters)
- **Clear:** `setup environment`, `clean workspace` (recommended)
- **Conversational:** `I want to set up my environment` (most flexible)

**All three styles work equally well!** Choose what feels natural.

**Note:** Platform detection is automatic! CORTEX detects Mac/Windows/Linux on startup.

---

### 💡 Command Discovery

**Forgot what's available?** Ask for help:

```
help
show me what cortex can do
what commands are available
```

**Available Operations:**

| Operation | Natural Language Examples | Status | What It Does |
|-----------|--------------------------|--------|--------------|
| **Demo** | "demo", "show capabilities", "tutorial" | ✅ READY | Interactive walkthrough of CORTEX |
| **Setup** | "setup", "configure", "initialize" | ✅ READY | Configure development environment |
| **Design Sync** | "sync design", "align design", "consolidate status" | ✅ READY | Synchronize design docs with implementation |
| **Story Refresh** | "refresh story", "update story" | 🟡 VALIDATION | Validate CORTEX story structure (validation-only, see limitations) |
| **Cleanup** | "cleanup", "clean workspace", "tidy up" | 🟡 PARTIAL | Clean temp files, optimize databases |
| **Documentation** | "update docs", "build docs" | ⏸️ PENDING | Generate/build documentation site |
| **Brain Protection** | "check brain", "validate protection" | ⏸️ PENDING | Validate brain integrity |
| **Run Tests** | "run tests", "test suite" | ⏸️ PENDING | Execute test suite with coverage |

**Legend:**
- ✅ READY - Fully implemented and tested with real logic
- 🟡 VALIDATION - Validation-only (no transformation yet)
- 🟡 PARTIAL - Core works, integration testing in progress
- ⏸️ PENDING - Architecture ready, modules pending
- 🎯 PLANNED - Design phase (CORTEX 2.1+)

**Try it now:**
```python
from src.operations import execute_operation

# All natural language - no slash commands needed!
report = execute_operation('setup')  # Works!
report = execute_operation('refresh story')  # Works!
report = execute_operation('cleanup', profile='standard')  # Works!
```

### 🔧 VS Code Extension

**Note:** The VS Code extension MAY use command syntax internally (e.g., `@cortex /resume`) for UI conventions, but this is extension-specific and NOT part of core CORTEX operations.

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
| `#file:cortex-brain/cortex-2.0-design/CORTEX2-STATUS.MD` | Compact phase/task status snapshot (visual bars) |

---

## 🔌 Plugin System (Extensible)

**Plugins extend CORTEX functionality seamlessly!**

**How it works:**
1. Plugins register natural language patterns during initialization
2. Router matches user intent to plugin capabilities
3. Plugin executes with full access to CORTEX brain tiers
4. Results integrate naturally into conversation

**Example Plugin:**
```python
class MyPlugin(BasePlugin):
    def get_natural_language_patterns(self):
        return ["analyze code quality", "review code", "check quality"]
    
    def execute(self, request, context):
        # Your plugin logic here
        return {"success": True, "data": results}
```

**For plugin developers:** See `src/plugins/base_plugin.py` for API

**Current Active Plugins:**
- Platform Switch (auto-detects Mac/Windows/Linux)
- System Refactor (code restructuring)
- Doc Refresh (documentation generation)
- Extension Scaffold (VS Code extension creation)
- Configuration Wizard (setup assistance)
- Code Review (quality analysis)
- Cleanup (workspace maintenance)

---

## ⚠️ Known Limitations

### Operations in Development

**Design Sync (design_sync):**
- **Status:** ✅ PRODUCTION READY
- **Purpose:** Resolves design-implementation drift
- **Capabilities:**
  - Live implementation discovery (modules, tests, plugins, operations)
  - Design-implementation gap analysis
  - Optimization integration (runs optimize_cortex automatically)
  - MD-to-YAML conversion (structured schemas from verbose docs)
  - Status file consolidation (ONE source of truth)
  - Git tracking (all changes committed with audit trail)
- **Profiles:**
  - quick: Analysis only (no changes)
  - standard: Safe updates + consolidation
  - comprehensive: Full sync with YAML conversion
- **Why It Matters:** Sometimes design and implementation diverge during rapid development. This operation resynchronizes everything automatically.
- **Use When:** Design docs show incorrect counts, multiple status files exist, implementation reality differs from documentation

**Story Refresh (refresh_cortex_story):**
- **Status:** 🟡 VALIDATION-ONLY (not transformation yet)
- **Current Behavior:** Validates story structure and read time, but does NOT transform content
- **Why:** The story at `prompts/shared/story.md` is already in narrator voice
- **Operation:** Validates structure → Copies to `docs/awakening-of-cortex.md` → Reports validation status
- **No Changes:** Files have identical content before/after (this is expected)
- **Planned:** Phase 6 enhancement will add AI-based transformation for dynamic updates
- **SKULL-005:** Module explicitly marked as validation-only to prevent false success claims

**Vision API:**
- **Status:** 🟡 MOCK IMPLEMENTATION (optional feature)
- **Current Behavior:** Returns mock data for image analysis
- **Enable:** Set `vision_api.enabled = true` in config
- **Requires:** GitHub Copilot API access (not yet available)
- **Fallback Chain:** Copilot → OpenAI → local models → mock

### Two-Tier Status System

CORTEX distinguishes between **architecture completion** and **implementation completion**:

| Symbol | Architecture | Implementation | Meaning |
|--------|-------------|----------------|---------|
| ✅ READY | Complete | Complete | **Production-ready** with real logic |
| 🟢 NEARLY | Complete | 80%+ | **Almost ready** - minor gaps only |
| 🟡 VALIDATION | Complete | Validation-only | **Works but doesn't transform** |
| 🟡 PARTIAL | Complete | 40-60% | **Architecture solid, logic incomplete** |
| 🟠 IN PROGRESS | Partial | Partial | **Active development** |
| ⏸️ PENDING | Designed | Not started | **Architecture ready, awaiting implementation** |

**Example:** `refresh_cortex_story` is **🟡 VALIDATION** because:
- ✅ Architecture: 6/6 modules orchestrate correctly
- 🟡 Implementation: Validation-only (no transformation logic yet)

This honest reporting prevents status inflation and maintains user trust.

---

## ⚠️ CRITICAL: Conversation Tracking

**GitHub Copilot Chat does NOT automatically track conversations to the CORTEX brain.**

Without tracking: ❌ No memory across chats, ❌ "Make it purple" fails  
With tracking: ✅ Full conversation memory, ✅ "Make it purple" works

**See tracking guide for setup:**
```
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

## 🎓 Copyright & Attribution

**All CORTEX orchestrator entry points display a copyright header:**

```
================================================================================
CORTEX [Operation Name] Orchestrator
================================================================================

Version:    [version]
Profile:    [profile]
Mode:       [LIVE | DRY RUN]
Started:    [timestamp]

Author:     Asif Hussain
Copyright:  © 2024-2025 Asif Hussain. All rights reserved.
License:    Proprietary
Repository: https://github.com/asifhussain60/CORTEX

================================================================================
```

This header:
- ✅ Clearly identifies the author and copyright holder
- ✅ Shows execution mode (LIVE vs DRY RUN)
- ✅ Provides version and timestamp information
- ✅ Links to official repository
- ✅ Applies to ALL entry point orchestrators

**Copyright Notice:**

CORTEX is proprietary software developed by Asif Hussain. All rights reserved. Unauthorized reproduction or distribution is prohibited. See LICENSE file for full terms.

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

*Last Updated: 2025-11-10 | CORTEX 2.0 Natural Language Architecture*

*Note: This prompt file enables the `/CORTEX` command in GitHub Copilot Chat. All operations use natural language only - no slash commands needed for core CORTEX operations.*

*What's New in 5.3:* 
- **Natural Language Only** - Removed all slash commands for simpler, cleaner architecture
- **Interaction Design** - Single, intuitive interaction model (see `cortex-brain/interaction-design.yaml`)
- **Documentation Cleanup** - 200+ lines removed, clearer focus on natural language patterns
- **Module Status Updates** - 37/86 modules implemented (43%), 3/12 operations fully working
- See `cortex-brain/cortex-2.0-design/SLASH-COMMAND-REMOVAL-REPORT.md` for details
