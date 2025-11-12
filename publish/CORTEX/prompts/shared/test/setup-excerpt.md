# CORTEX Setup Excerpt - Getting Started Guide

**Purpose:** Quick setup and installation instructions for CORTEX  
**Audience:** New users, developers setting up CORTEX in their workspace  
**Source:** Extracted from full CORTEX documentation

---

## 🚀 Quick Start

### First-Time Setup

**Step 1: Set Environment Variables**

```powershell
# Windows (PowerShell as Administrator)
[Environment]::SetEnvironmentVariable("CORTEX_ROOT", "D:\PROJECTS\CORTEX", "User")
[Environment]::SetEnvironmentVariable("CORTEX_BRAIN_PATH", "D:\PROJECTS\CORTEX\cortex-brain", "User")

# Reload environment (close and reopen terminal)
```

```bash
# macOS/Linux (~/.zshrc or ~/.bashrc)
export CORTEX_ROOT="$HOME/PROJECTS/CORTEX"
export CORTEX_BRAIN_PATH="$CORTEX_ROOT/cortex-brain"

# Reload shell
source ~/.zshrc
```

**Step 2: Install Dependencies**

```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies (if using VS Code extension)
cd cortex-extension
npm install
```

**Step 3: Initialize CORTEX Brain**

```bash
# Run setup script
python scripts/cortex_setup.py

# This will:
# - Create brain directories (tier1, tier2, tier3)
# - Initialize SQLite databases
# - Run data migrations
# - Discover project resources
# - Setup configuration
```

**Expected Output:**
```
🧠 CORTEX Setup Wizard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1: Environment Validation
  ✅ CORTEX_ROOT set: D:\PROJECTS\CORTEX
  ✅ Python version: 3.11.5
  ✅ SQLite version: 3.42.0

Phase 2: Brain Initialization
  ✅ Created cortex-brain/tier1/
  ✅ Created cortex-brain/tier2/
  ✅ Created cortex-brain/tier3/
  ✅ Initialized conversations.db
  ✅ Initialized knowledge-graph.db
  ✅ Initialized context-intelligence.db

Phase 3: Discovery
  🔍 Scanning workspace...
  ✅ Found 2 database connections
  ✅ Found 1 API endpoint
  
Phase 4: Configuration
  ✅ Created cortex.config.json
  
✨ Setup complete! CORTEX is ready to use.

Next steps:
  1. Test with: #file:prompts/user/cortex.md status
  2. Read the story: #file:prompts/shared/test/story-excerpt.md
  3. Start working: #file:prompts/user/cortex.md <your request>
```

---

## 🖥️ Cross-Platform Setup

### Windows Setup

```powershell
# Install PowerShell auto-resume prompt (optional)
Add-Content $PROFILE @"
# CORTEX Auto-Resume
if (Test-Path `"`$env:CORTEX_ROOT/scripts/auto-resume-prompt.ps1`") {
    . `"`$env:CORTEX_ROOT/scripts/auto-resume-prompt.ps1`"
}
"@
```

### macOS/Linux Setup

```bash
# Install shell auto-resume prompt (optional)
cat >> ~/.zshrc << 'EOF'
# CORTEX Auto-Resume
if [ -f "$CORTEX_ROOT/scripts/auto-resume-prompt.sh" ]; then
    source "$CORTEX_ROOT/scripts/auto-resume-prompt.sh"
fi
EOF
```

---

## ⚙️ Configuration

### cortex.config.json

Create or edit `cortex.config.json` in your workspace root:

```json
{
  "machines": {
    "YOUR-PC-NAME": {
      "rootPath": "D:\\PROJECTS\\CORTEX",
      "brainPath": "D:\\PROJECTS\\CORTEX\\cortex-brain"
    }
  },
  "cortex": {
    "tier1": {
      "maxConversations": 20,
      "fifoEnabled": true
    },
    "tier2": {
      "patternDecay": {
        "enabled": true,
        "decayRate": 0.05
      }
    },
    "tier3": {
      "gitAnalysis": {
        "enabled": true,
        "lookbackDays": 30
      }
    }
  }
}
```

---

## 🔧 Verification

### Test CORTEX Installation

```markdown
# Check system status
#file:prompts/user/cortex.md status
```

**Expected Response:**
```
🧠 CORTEX System Status

Tier 1 (Working Memory):
  ✅ Database: Connected
  ✅ Conversations: 5 active
  ✅ Messages: 127 total
  ✅ FIFO Queue: Enabled (5/20)

Tier 2 (Knowledge Graph):
  ✅ Database: Connected
  ✅ Patterns: 42 learned
  ✅ Relationships: 156 tracked

Tier 3 (Context Intelligence):
  ✅ Database: Connected
  ✅ Git commits: 1,237 analyzed
  ✅ File hotspots: 23 identified

⚡ System Health: EXCELLENT (100%)
```

---

## ⚠️ Important: Conversation Tracking

**GitHub Copilot Chat does NOT automatically track conversations to the CORTEX brain.**

To enable conversation memory (so CORTEX remembers across chats):

### Option 1: PowerShell Capture (Quick - After Each Session)
```powershell
# Capture your conversation manually
.\scripts\cortex-capture.ps1 -AutoDetect

# Or provide message directly
.\scripts\cortex-capture.ps1 -Message "Created mkdocs documentation" -Intent EXECUTE
```

### Option 2: Python CLI (Direct Integration)
```bash
# Process through Python (tracks automatically)
python scripts/cortex_cli.py "Add authentication to login page"

# Validate tracking is working
python scripts/cortex_cli.py --validate

# Check current session
python scripts/cortex_cli.py --session-info
```

### Option 3: Ambient Daemon (Automatic - Phase 2)
```powershell
# Start background capture daemon
python scripts/cortex/auto_capture_daemon.py

# Runs in background, captures file changes, git commits automatically
```

**Why This Is Needed:**
- GitHub Copilot Chat reads `#file:prompts/user/cortex.md` as **documentation**
- It does NOT execute the Python `CortexEntry.process()` method
- Without tracking: ❌ No conversation memory, ❌ No cross-chat context
- With tracking: ✅ Remembers past conversations, ✅ "Make it purple" works

---

## 🧪 Verify Setup with Test Request

Try a simple request to verify everything works:

```markdown
#file:prompts/user/cortex.md

Tell me the CORTEX story
```

If you see the "Intern with Amnesia" story, setup is successful! ✅

---

## 📚 Next Steps

1. **Read the story:** `#file:prompts/shared/test/story-excerpt.md`
2. **Learn about agents:** See full documentation
3. **Start working:** `#file:prompts/user/cortex.md <your request>`
4. **Enable tracking:** Choose one of the 3 tracking options above

---

**Full Documentation:** See `#file:prompts/user/cortex.md` for complete CORTEX documentation  
**Related Modules:**
- Story: `#file:prompts/shared/test/story-excerpt.md`
- Technical Reference: `#file:prompts/shared/test/technical-excerpt.md`

**Troubleshooting:** If setup fails, check:
- Python version ≥3.9
- SQLite version ≥3.35
- Environment variables set correctly
- Write permissions in CORTEX directory
