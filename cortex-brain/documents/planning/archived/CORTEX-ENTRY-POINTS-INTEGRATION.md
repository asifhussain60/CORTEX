# CORTEX Entry Points - Integration Sections for CORTEX.prompt.md

**Purpose:** Concise entry point sections to add to CORTEX.prompt.md that reference comprehensive help documents
**Location in CORTEX.prompt.md:** Add these after the "Response Templates" section (around line 700)
**Version:** 2.1
**Date:** 2025-11-22

---

## Entry Point: /CORTEX help (User Features)

When user says: `"help"`, `"cortex help"`, `"what can cortex do"`

**Quick Reference - User Operations:**

| Operation | Trigger Examples | Status |
|-----------|------------------|--------|
| **Demo** | "demo", "show me what cortex can do" | ✅ Ready |
| **Setup** | "setup", "configure cortex" | ✅ Ready |
| **Onboard App** | "onboard this application", "analyze my codebase" | ✅ Ready |
| **Plan Feature** | "plan a feature", "let's plan authentication" | ✅ Ready |
| **Enhance** | "enhance the dashboard", "improve authentication" | ✅ Ready |
| **Maintain** | "maintain", "cleanup", "optimize cortex" | ✅ Ready |
| **Resume** | "resume authentication", "continue dark mode work" | ✅ Ready |
| **Status** | "status", "where are we" | ✅ Ready |

**Conversation Memory:**
- `"show context"` - View what Copilot remembers
- `"forget about authentication"` - Remove specific conversations
- `"clear all context"` - Fresh start (removes ALL memory)

📘 **See comprehensive user guide:** `cortex-brain/documents/reference/CORTEX-HELP-USER.md`

---

## Entry Point: /CORTEX admin help (Admin Features)

When user says: `"admin help"`, `"cortex admin help"`, `/admin help"`

**⚠️ Admin Operations (Developer/Admin Only):**

| Operation | Trigger Examples | Purpose |
|-----------|------------------|---------|
| **Publish CORTEX** | "publish cortex", "deploy cortex to github" | Package and deploy to repository |
| **Design Sync** | "sync design", "update design docs" | Sync design with implementation |
| **Regenerate Diagrams** | "regenerate diagrams", "update architecture diagrams" | Rebuild Mermaid diagrams |
| **Enterprise Docs** | "generate documentation", "generate enterprise docs" | Build comprehensive docs |
| **Brain Export** | "export brain", "share brain patterns" | Export learned patterns |
| **Brain Import** | "import brain", "load patterns from export" | Import shared patterns |

📘 **See comprehensive admin guide:** `cortex-brain/documents/reference/CORTEX-HELP-ADMIN.md`

---

## Entry Point: /CORTEX setup

When user says: `"setup"`, `"setup environment"`, `"configure cortex"`

**Environment Setup Operation:**

Configures CORTEX development environment with platform detection (Mac/Windows/Linux).

**Profiles:**
- **Minimal** - Core functionality only
- **Standard** - Recommended (DEFAULT)
- **Full** - Everything enabled

**Usage:**
```
"setup"                       # Standard setup
"setup environment"           # Standard setup
"minimal setup"               # Core only
"full setup"                  # Everything enabled
```

**What It Does:**
1. ✅ Validates project structure
2. ✅ Detects platform (Mac/Windows/Linux)
3. ✅ Configures virtual environment
4. ✅ Installs Python dependencies
5. ✅ Initializes brain tiers (0, 1, 2, 3)
6. ✅ Runs validation tests
7. ✅ Generates setup report

**For Users:**
📘 **See user setup guide:** `publish/CORTEX/SETUP-FOR-COPILOT.md`
- One-command setup: `"onboard this application"`
- Brain preservation for existing installations
- Upgrade workflow with zero data loss

**For Developers:**
📘 **See complete setup documentation:** `cortex-brain/documents/reference/CORTEX-HELP-USER.md` (Setup Operation section)

---

## Entry Point: /CORTEX onboard application

When user says: `"onboard this application"`, `"analyze my codebase"`, `"deploy cortex to my app"`

**Application Onboarding Operation:**

Deploys CORTEX to user's application with intelligent codebase analysis.

**Profiles:**
- **Quick** - Essential setup only (no questions)
- **Standard** - Full analysis with smart questions (DEFAULT)
- **Comprehensive** - Deep analysis with recommendations

**Usage:**
```
"onboard this application"                # Standard profile
"analyze my codebase"                     # Standard profile
"quick onboard"                           # Skip questions
"comprehensive application onboarding"    # Deep analysis
```

**7-Step Workflow:**
1. ✅ Copies CORTEX entry points to `.github/`
2. ✅ Installs required tooling
3. ✅ Initializes brain databases (Tiers 1, 2, 3)
4. ✅ Crawls and indexes codebase
5. ✅ Analyzes tech stack and dependencies
6. ✅ Generates architecture documentation
7. ✅ Asks intelligent questions:
   - "I see React but no test files - shall I help set up Jest?"
   - "You have ESLint but not on pre-commit - want hooks?"
   - "No TypeScript detected - would you like type safety migration?"

**Smart Questions:**
- Only asks what's relevant to YOUR codebase
- Detects missing best practices
- Suggests improvements based on industry standards
- Can implement recommendations with tests

📘 **See detailed onboarding guide:** `cortex-brain/documents/reference/CORTEX-HELP-USER.md` (Onboard Application section)
📘 **See setup guide for users:** `publish/CORTEX/SETUP-FOR-COPILOT.md`

---

## Entry Point: /CORTEX demo

When user says: `"demo"`, `"show me what cortex can do"`, `"cortex tutorial"`, `"walkthrough"`

**Interactive Demo Operation:**

Showcases CORTEX capabilities through hands-on walkthrough.

**Profiles:**
- **Quick** (2 min) - Essential commands only
- **Standard** (3-4 min) - Core capabilities (DEFAULT)
- **Comprehensive** (5-6 min) - Full walkthrough
- **Developer** (8-10 min) - Development workflow deep-dive

**Usage:**
```
"demo"                    # Standard profile
"show me a quick demo"    # Quick profile
"comprehensive demo"      # Full walkthrough
"developer demo"          # Development deep-dive
```

**Demo Modules (Standard Profile):**

| Module | What You'll See | Duration |
|--------|----------------|----------|
| **Help System** | Natural language commands, no slash commands needed | 30s |
| **Story Transformation** | Turn technical specs into user stories with narrator voice | 45s |
| **DoD/DoR Workflow** | Definition of Done/Ready enforcement | 45s |
| **Token Optimization** | 97.2% reduction (74,047 → 2,078 avg tokens) | 30s |
| **Code Review** | Automated review with CORTEX capabilities assessment | 45s |
| **Conversation Memory** | Context tracking and restoration across sessions | 30s |

**What's Demonstrated:**
- ✅ Natural language interface (no slash commands)
- ✅ Story transformation with narrator AI
- ✅ Planning System 2.0 (DoR/DoD validation)
- ✅ Token optimization (massive cost savings)
- ✅ Code review capabilities
- ✅ Conversation memory system (Tier 1)
- ✅ Resume conversations with context restoration

📘 **See full demo documentation:** `cortex-brain/documents/reference/CORTEX-HELP-USER.md` (Demo Operation section)

**For Developers:**
- **Developer Profile** includes:
  - TDD workflow demonstration
  - Architecture analysis
  - Module implementation examples
  - Brain tier exploration
  - EPM orchestrator patterns

---

## How to Integrate These Sections

### Step 1: Locate Insertion Point in CORTEX.prompt.md

Find this section (around line 700):
```markdown
## 🎯 Command Reference & Quick Links
```

### Step 2: Insert Entry Point Sections

Add the five entry point sections above (help, admin help, setup, onboard application, demo) after the "Response Templates" section and before "Mandatory Response Format".

### Step 3: Update Cross-References

Ensure the following files reference the new help documents:

1. **cortex-operations.yaml** - Update operation descriptions to mention help docs
2. **README.md** - Link to help documents in "Getting Started" section
3. **module-definitions.yaml** - Add help doc references to demo/setup/onboard modules

### Step 4: Test Natural Language Triggers

Verify these work in GitHub Copilot Chat:
- "help" → Shows user operations table
- "admin help" → Shows admin operations table
- "setup" → Runs environment setup operation
- "onboard this application" → Runs application onboarding
- "demo" → Runs interactive demo (standard profile)

---

## Additional Integration Notes

### Template System Integration

The help commands use these response templates from `response-templates.yaml`:
- `help_table` - User help table format
- `help_detailed` - Detailed help with examples
- `admin_help` - Admin operations reference

### Operation Registry Integration

All operations are defined in `cortex-operations.yaml` with:
- `deployment_tier: user` - User-facing operations
- `deployment_tier: admin` - Admin-only operations
- `natural_language_triggers` - Phrases that activate operations
- `profiles` - Execution modes (quick, standard, comprehensive)

### Brain Integration

- User help: References Tier 1 (conversation memory)
- Admin help: References Tier 2 (knowledge graph, brain export/import)
- Setup/Onboard: Initialize all brain tiers (0, 1, 2, 3)
- Demo: Demonstrates conversation memory and context restoration

---

**Version:** 2.1
**Last Updated:** 2025-11-22
**Author:** Asif Hussain
