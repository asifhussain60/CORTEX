# CORTEX Setup Guide - Getting Started

**Purpose:** Complete installation and configuration instructions for CORTEX  
**Audience:** New users, developers setting up CORTEX in their workspace  
**Version:** 2.0 (Full Module)  
**Status:** Production Ready

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

Before installing CORTEX, ensure you have:

- **Python:** Version 3.9 or higher
- **SQLite:** Version 3.35 or higher (usually included with Python)
- **Git:** For version control (recommended)
- **VS Code:** With GitHub Copilot extension (for full integration)

**Check your versions:**
```bash
python --version   # Should be 3.9+
sqlite3 --version  # Should be 3.35+
git --version      # Any recent version
```

---

## 📦 Installation

### Step 1: Set Environment Variables

Environment variables tell CORTEX where it lives on your machine.

#### Windows (PowerShell - Run as Administrator)

```powershell
# Set environment variables
[Environment]::SetEnvironmentVariable("CORTEX_ROOT", "D:\PROJECTS\CORTEX", "User")
[Environment]::SetEnvironmentVariable("CORTEX_BRAIN_PATH", "D:\PROJECTS\CORTEX\cortex-brain", "User")

# Verify they're set
$env:CORTEX_ROOT
$env:CORTEX_BRAIN_PATH

# IMPORTANT: Close and reopen your terminal for changes to take effect
```

#### macOS / Linux (Bash / Zsh)

```bash
# Add to ~/.zshrc or ~/.bashrc
echo 'export CORTEX_ROOT="$HOME/PROJECTS/CORTEX"' >> ~/.zshrc
echo 'export CORTEX_BRAIN_PATH="$CORTEX_ROOT/cortex-brain"' >> ~/.zshrc

# Reload shell configuration
source ~/.zshrc

# Verify they're set
echo $CORTEX_ROOT
echo $CORTEX_BRAIN_PATH
```

**Important:** Replace paths with your actual CORTEX location!

---

### Step 2: Install Python Dependencies

```bash
# Navigate to CORTEX root
cd $CORTEX_ROOT

# Install required Python packages
pip install -r requirements.txt

# Expected packages:
# - pyyaml (YAML parsing)
# - pytest (testing framework)
# - pytest-cov (test coverage)
# - playwright (UI testing)
# - python-dotenv (environment config)
```

**Verify installation:**
```bash
python -c "import yaml; import pytest; print('Dependencies installed ✅')"
```

---

### Step 3: Install Optional Dependencies

#### VS Code Extension (Recommended)

The CORTEX VS Code extension provides enhanced integration.

```bash
# Navigate to extension directory
cd cortex-extension

# Install Node.js dependencies
npm install

# Build extension
npm run build

# Install in VS Code (optional - for development)
code --install-extension cortex-extension/cortex-extension-0.1.0.vsix
```

#### UI Testing (Playwright)

If you plan to run UI tests:

```bash
# Install Playwright browsers
npx playwright install

# Test Playwright installation
npx playwright test --version
```

---

### Step 4: Initialize CORTEX Brain

The setup script creates the brain directory structure and initializes databases.

```bash
# Run setup wizard
python scripts/cortex_setup.py
```

**Expected Output:**
```
🧠 CORTEX Setup Wizard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1: Environment Validation
  ✅ CORTEX_ROOT set: D:\PROJECTS\CORTEX
  ✅ CORTEX_BRAIN_PATH set: D:\PROJECTS\CORTEX\cortex-brain
  ✅ Python version: 3.11.5 (meets requirement: 3.9+)
  ✅ SQLite version: 3.42.0 (meets requirement: 3.35+)
  ✅ Write permissions verified

Phase 2: Brain Directory Creation
  ✅ Created cortex-brain/
  ✅ Created cortex-brain/tier1/
  ✅ Created cortex-brain/tier2/
  ✅ Created cortex-brain/tier3/
  ✅ Created cortex-brain/corpus-callosum/
  ✅ Created cortex-brain/schemas/

Phase 3: Database Initialization
  ✅ Initialized tier1/conversations.db
  ✅ Created table: conversations
  ✅ Created table: messages
  ✅ Created table: entities
  ✅ Created index: idx_conversations_timestamp
  
  ✅ Initialized tier2/knowledge-graph.db
  ✅ Created table: patterns
  ✅ Created table: relationships
  ✅ Created table: workflows
  ✅ Enabled FTS5 full-text search
  
  ✅ Initialized tier3/context-intelligence.db
  ✅ Created table: git_commits
  ✅ Created table: file_metrics
  ✅ Created table: session_analytics

Phase 4: Workspace Discovery
  🔍 Scanning workspace for resources...
  ✅ Found 2 database connections (MSSQL, SQLite)
  ✅ Found 1 API endpoint (localhost:5000)
  ✅ Found 47 Python files
  ✅ Found 23 test files
  ✅ Analyzed git history (last 30 days): 1,237 commits
  
Phase 5: Configuration File Creation
  ✅ Created cortex.config.json (machine-specific settings)
  ✅ Generated unique machine ID: YOUR-PC-NAME-12345
  ✅ Set default FIFO queue (20 conversations)
  ✅ Enabled pattern decay (5% per 30 days)
  ✅ Configured git analysis (30-day lookback)

Phase 6: Brain Protection Setup
  ✅ Loaded brain-protection-rules.yaml (6 protection layers)
  ✅ Validated 22 protection rules
  ✅ Initialized Brain Protector agent

✨ Setup complete! CORTEX brain is ready to use.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:
  1. Test installation: #file:prompts/user/cortex.md status
  2. Read the story: #file:prompts/shared/story.md
  3. Start working: #file:prompts/user/cortex.md <your request>

For conversation tracking setup: #file:prompts/shared/tracking-guide.md
```

---

## ⚙️ Configuration

### cortex.config.json

The setup wizard creates this file automatically, but you can customize it:

**Location:** `<CORTEX_ROOT>/cortex.config.json`

```json
{
  "machines": {
    "YOUR-PC-NAME": {
      "rootPath": "D:\\PROJECTS\\CORTEX",
      "brainPath": "D:\\PROJECTS\\CORTEX\\cortex-brain",
      "machineId": "YOUR-PC-NAME-12345"
    },
    "YOUR-LAPTOP": {
      "rootPath": "/Users/you/Projects/CORTEX",
      "brainPath": "/Users/you/Projects/CORTEX/cortex-brain",
      "machineId": "YOUR-LAPTOP-67890"
    }
  },
  "cortex": {
    "tier1": {
      "maxConversations": 20,
      "fifoEnabled": true,
      "messageRetention": 10,
      "autoCleanup": true
    },
    "tier2": {
      "patternDecay": {
        "enabled": true,
        "decayRate": 0.05,
        "minConfidence": 0.3
      },
      "fts5": {
        "enabled": true,
        "languages": ["en"]
      },
      "scopeIsolation": {
        "enabled": true,
        "allowCrossScope": false
      }
    },
    "tier3": {
      "gitAnalysis": {
        "enabled": true,
        "lookbackDays": 30,
        "includeAuthors": true,
        "trackFileHotspots": true
      },
      "sessionAnalytics": {
        "enabled": true,
        "trackProductivity": true
      }
    },
    "agents": {
      "intentRouter": {
        "confidenceThreshold": 0.7
      },
      "codeExecutor": {
        "tddEnforced": true,
        "maxFileSize": 500,
        "incrementalCreation": true
      },
      "brainProtector": {
        "enabled": true,
        "challengeThreshold": "moderate",
        "autoBlock": ["tier0_modification", "governance_changes"]
      }
    }
  }
}
```

**Configuration Options:**

- **machines:** Multi-machine support (work PC, laptop, CI server)
- **tier1.maxConversations:** FIFO queue size (default: 20)
- **tier2.decayRate:** Pattern confidence decay (default: 5% per 30 days)
- **tier3.lookbackDays:** Git analysis window (default: 30 days)
- **agents.tddEnforced:** Require TDD workflow (default: true)

---

## 🔧 Verification

### Test CORTEX Installation

After setup, verify everything works:

**Method 1: Status Check (Recommended)**
```markdown
#file:prompts/user/cortex.md status
```

**Expected Response:**
```
🧠 CORTEX System Status

Tier 0 (Instinct):
  ✅ Governance Rules: Loaded (22 core rules)
  ✅ Brain Protection: Active (6 layers)
  ✅ TDD Enforcement: Enabled

Tier 1 (Working Memory):
  ✅ Database: Connected (conversations.db)
  ✅ Conversations: 0 active (0/20 queue)
  ✅ Messages: 0 total
  ✅ FIFO Queue: Enabled
  ✅ Performance: 18ms avg query time ⚡

Tier 2 (Knowledge Graph):
  ✅ Database: Connected (knowledge-graph.db)
  ✅ Patterns: 0 learned
  ✅ Relationships: 0 tracked
  ✅ Workflows: 0 templates
  ✅ FTS5 Search: Enabled
  ✅ Performance: 92ms avg search time ⚡

Tier 3 (Context Intelligence):
  ✅ Database: Connected (context-intelligence.db)
  ✅ Git Commits: 1,237 analyzed (last 30 days)
  ✅ File Hotspots: 23 identified
  ✅ Session Data: 0 tracked sessions
  ✅ Performance: 156ms avg analysis time ⚡

Agents:
  ✅ Intent Router: Ready
  ✅ Work Planner: Ready
  ✅ Code Executor: Ready (TDD enforced)
  ✅ Test Generator: Ready
  ✅ Brain Protector: Ready (6 protection layers active)
  ✅ All 10 specialist agents: Operational

Configuration:
  ✅ cortex.config.json: Loaded
  ✅ Machine ID: YOUR-PC-NAME-12345
  ✅ Root Path: D:\PROJECTS\CORTEX
  ✅ Brain Path: D:\PROJECTS\CORTEX\cortex-brain

⚡ System Health: EXCELLENT (100%)
```

**Method 2: Python CLI**
```bash
# Check system status
python scripts/cortex_cli.py --status

# Validate all tiers
python scripts/cortex_cli.py --validate
```

---

### Common Issues & Solutions

#### Issue: "Module not found: yaml"
```bash
# Solution: Install pyyaml
pip install pyyaml
```

#### Issue: "Cannot connect to database"
```bash
# Solution: Re-run setup
python scripts/cortex_setup.py --force-reinit
```

#### Issue: "Environment variables not set"
```bash
# Windows: Verify and reset
echo $env:CORTEX_ROOT
[Environment]::SetEnvironmentVariable("CORTEX_ROOT", "D:\PROJECTS\CORTEX", "User")

# macOS/Linux: Verify and reset
echo $CORTEX_ROOT
export CORTEX_ROOT="$HOME/PROJECTS/CORTEX"
source ~/.zshrc
```

#### Issue: "Permission denied when creating directories"
```bash
# Windows: Run PowerShell as Administrator
# macOS/Linux: Check directory permissions
chmod -R 755 $CORTEX_ROOT/cortex-brain
```

---

## ⚠️ CRITICAL: Conversation Tracking Setup

**IMPORTANT:** GitHub Copilot Chat does **NOT automatically track** conversations to the CORTEX brain. Without tracking, CORTEX has no memory!

**Symptoms of missing tracking:**
- ❌ "Make it purple" doesn't know what "it" refers to
- ❌ New chat sessions start from scratch
- ❌ No conversation history in Tier 1
- ❌ No pattern learning in Tier 2

**You MUST enable tracking using one of these methods:**

### Option 1: PowerShell Capture Script (Quick - Manual)

Best for: Ad-hoc tracking after each work session

```powershell
# Navigate to CORTEX root
cd D:\PROJECTS\CORTEX

# Capture most recent Copilot conversation
.\scripts\cortex-capture.ps1 -AutoDetect

# Or provide details manually
.\scripts\cortex-capture.ps1 `
  -Message "Created authentication feature with tests" `
  -Intent EXECUTE `
  -Files "LoginController.cs,AuthTests.cs"
```

**When to use:** After completing a coding session with Copilot

---

### Option 2: Python CLI (Direct Integration)

Best for: Structured work with automatic tracking

```bash
# Process request through Python (tracks automatically)
python scripts/cortex_cli.py "Add authentication to login page"

# This will:
# 1. Route intent to appropriate agent
# 2. Execute workflow with TDD
# 3. Track conversation to Tier 1
# 4. Extract patterns to Tier 2
# 5. Update context in Tier 3

# Validate tracking is working
python scripts/cortex_cli.py --validate

# Check current session
python scripts/cortex_cli.py --session-info

# View recent conversations
python scripts/cortex_cli.py --recent 5
```

**When to use:** For programmatic CORTEX usage with full tracking

---

### Why Tracking Is Essential

**Without tracking:**
```
You: "Add button to panel"
[Copilot adds button]

You: "Make it purple"
Copilot: ❌ "What should I make purple?"
Problem: No conversation history in Tier 1
```

**With tracking enabled:**
```
You: "Add button to panel"
[CORTEX tracks: button, panel, file modified]

You: "Make it purple"
CORTEX: ✅ "Applying purple to button in panel"
Solution: Tier 1 remembers context
```

**See full tracking guide:** `#file:prompts/shared/tracking-guide.md`

---

## 🎯 First Steps After Installation

### 1. Read the CORTEX Story

Understand the "why" behind CORTEX:
```markdown
#file:prompts/shared/story.md
```

### 2. Test with a Simple Request

```markdown
#file:prompts/user/cortex.md

Tell me about this project
```

### 3. Try a Development Task

```markdown
#file:prompts/user/cortex.md

Create a plan to add user authentication
```

### 4. Enable Conversation Tracking

Choose your preferred tracking method (see above) and enable it.

### 5. Learn the Agent System

```markdown
#file:prompts/shared/agents-guide.md
```

---

## 🔄 Multi-Machine Setup

### Scenario: Work PC + Laptop

**1. Install CORTEX on both machines**
```bash
# On both machines:
git clone https://github.com/asifhussain60/CORTEX
cd CORTEX
python scripts/cortex_setup.py
```

**2. Configure machine-specific settings**

Edit `cortex.config.json`:
```json
{
  "machines": {
    "WORK-PC": {
      "rootPath": "D:\\PROJECTS\\CORTEX",
      "brainPath": "D:\\PROJECTS\\CORTEX\\cortex-brain"
    },
    "LAPTOP": {
      "rootPath": "/Users/you/Projects/CORTEX",
      "brainPath": "/Users/you/Projects/CORTEX/cortex-brain"
    }
  }
}
```

**3. Sync brain data (optional)**

```bash
# On work PC (export brain state)
python scripts/brain_export.py --output brain-backup.zip

# Transfer brain-backup.zip to laptop

# On laptop (import brain state)
python scripts/brain_import.py --input brain-backup.zip
```

---

## 📁 Directory Structure After Setup

```
CORTEX/
├── cortex-brain/                    # Brain directory (created by setup)
│   ├── tier1/
│   │   ├── conversations.db         # Short-term memory (SQLite)
│   │   └── conversation-context.jsonl
│   ├── tier2/
│   │   ├── knowledge-graph.db       # Long-term memory (SQLite)
│   │   └── knowledge-graph.yaml
│   ├── tier3/
│   │   ├── context-intelligence.db  # Development context (SQLite)
│   │   └── git-analysis.jsonl
│   ├── corpus-callosum/
│   │   └── coordination-queue.jsonl # Hemisphere communication
│   ├── schemas/
│   │   ├── tier1-schema.sql
│   │   ├── tier2-schema.sql
│   │   └── tier3-schema.sql
│   └── brain-protection-rules.yaml  # Tier 0 governance
│
├── cortex.config.json               # Machine-specific configuration
├── requirements.txt                 # Python dependencies
├── scripts/
│   ├── cortex_setup.py              # Setup wizard
│   ├── cortex_cli.py                # Command-line interface
│   └── cortex-capture.ps1           # PowerShell tracking script
│
└── prompts/
    ├── user/
    │   └── cortex.md                # Universal entry point
    └── shared/
        ├── story.md                 # The story (you're here!)
        ├── setup-guide.md           # This document
        ├── technical-reference.md   # API & architecture
        ├── agents-guide.md          # Agent system
        ├── tracking-guide.md        # Conversation tracking
        └── configuration-reference.md
```

---

## 🎓 Next Steps

### Essential Reading
1. ✅ **Setup Guide** (you just completed this!)
2. 📖 **Story Guide:** `#file:prompts/shared/story.md` - Understand the "why"
3. 🔧 **Technical Reference:** `#file:prompts/shared/technical-reference.md` - API details
4. 🤖 **Agents Guide:** `#file:prompts/shared/agents-guide.md` - How CORTEX thinks
5. 📊 **Tracking Guide:** `#file:prompts/shared/tracking-guide.md` - Enable memory

### Start Using CORTEX
```markdown
#file:prompts/user/cortex.md

<your request in natural language>
```

**Examples:**
- "Create a plan to add user authentication"
- "Add a purple button to the dashboard"
- "Test the login functionality"
- "Fix the null reference error in LoginController"
- "Show me the project status"

---

## 🆘 Getting Help

### Documentation
- **Story:** `#file:prompts/shared/story.md`
- **Technical:** `#file:prompts/shared/technical-reference.md`
- **Agents:** `#file:prompts/shared/agents-guide.md`
- **Tracking:** `#file:prompts/shared/tracking-guide.md`
- **Configuration:** `#file:prompts/shared/configuration-reference.md`

### Troubleshooting
```bash
# Run diagnostics
python scripts/cortex_cli.py --diagnose

# Check system health
python scripts/cortex_cli.py --health

# View logs
tail -f logs/cortex.log
```

### Support
- **GitHub Issues:** https://github.com/asifhussain60/CORTEX/issues
- **Documentation:** See prompts/shared/ modules
- **Email:** (contact information)

---

**Installation complete! Welcome to CORTEX. 🧠**

**Version:** 2.0  
**Last Updated:** November 8, 2025  
**Phase:** 3.7 Complete - Full Modular Architecture
