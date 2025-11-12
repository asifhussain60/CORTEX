# CORTEX Tracking Guide - Conversation Memory Setup

**Purpose:** Complete guide to conversation tracking - solving the amnesia problem  
**Audience:** Users setting up CORTEX, troubleshooting memory issues  
**Version:** 2.0 (Full Module)  
**Status:** Production Ready

---

## 🧠 Why Conversation Tracking Is Essential

### The Amnesia Problem

**GitHub Copilot forgets everything between conversations.** This is the core problem CORTEX solves.

```
Without CORTEX:
┌────────────────────────────────────────┐
│ Conversation 1 (Monday 9am)           │
│ You: "Make the button purple"         │
│ Copilot: Creates purple button ✅      │
└────────────────────────────────────────┘
           ↓ (close VS Code)
           ↓ (reopen VS Code)
┌────────────────────────────────────────┐
│ Conversation 2 (Monday 2pm)           │
│ You: "Move the button to the right"   │
│ Copilot: "Which button?" ❓           │
│ (Has no memory of purple button)      │
└────────────────────────────────────────┘

With CORTEX:
┌────────────────────────────────────────┐
│ Conversation 1 (Monday 9am)           │
│ You: "Make the button purple"         │
│ Copilot: Creates purple button ✅      │
│ CORTEX: Saves to Tier 1 memory 💾     │
└────────────────────────────────────────┘
           ↓ (close VS Code)
           ↓ (reopen VS Code)
┌────────────────────────────────────────┐
│ Conversation 2 (Monday 2pm)           │
│ You: "Move the button to the right"   │
│ CORTEX: Loads Tier 1 memory 🧠        │
│ Copilot: "Moving the purple button    │
│           to the right" ✅             │
└────────────────────────────────────────┘
```

### What CORTEX Tracks

**Per Conversation:**
- Full message history (user prompts + Copilot responses)
- Entities mentioned (files, classes, functions, variables)
- Intent patterns (what you were trying to do)
- Timestamp and duration
- Session context (active files, git branch, errors)

**Stored In:**
- **Tier 1:** `cortex-brain/tier1/conversations.db` (SQLite)
- **Format:** JSON Lines for raw messages, SQLite for indexed search

---

## 🎯 Three Tracking Methods

CORTEX provides **three methods** to capture conversation memory. Choose based on your workflow:

| Method | Platform | Setup Difficulty | Reliability | Background Capture |
|--------|----------|------------------|-------------|-------------------|
| **PowerShell Capture** | Windows | Easy | ⭐⭐⭐⭐ | No (manual trigger) |
| **Python CLI** | Cross-platform | Medium | ⭐⭐⭐⭐⭐ | No (manual command) |
| **Ambient Daemon** | Cross-platform | Hard | ⭐⭐⭐⭐⭐ | Yes (automatic) |

---

## Method 1: PowerShell Capture (Windows)

**Best For:** Windows users who want simple, reliable, manual memory capture

### How It Works

1. You finish a conversation in GitHub Copilot Chat
2. You run a PowerShell script
3. Script captures the chat window content via UI Automation
4. CORTEX stores conversation in Tier 1 memory

### Setup Steps

#### 1. Enable PowerShell Script Execution

Open PowerShell as Administrator:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. Install UIAutomation Module (if needed)

```powershell
Install-Module -Name UIAutomation -Force
```

#### 3. Test the Capture Script

```powershell
cd d:\PROJECTS\CORTEX
.\scripts\capture-copilot-chat.ps1
```

**Expected Output:**
```
🔍 Searching for GitHub Copilot Chat window...
✅ Found chat window
📋 Capturing conversation text...
💾 Saved to: cortex-brain/tier1/captures/chat-2025-11-08-15-30-45.txt
✅ Conversation captured successfully!
```

#### 4. Create a Keyboard Shortcut (Optional)

**Windows PowerToys (Recommended):**
1. Install PowerToys from Microsoft Store
2. Open PowerToys Run settings
3. Add custom action:
   - **Trigger:** `cortex-capture`
   - **Command:** `powershell.exe -File "d:\PROJECTS\CORTEX\scripts\capture-copilot-chat.ps1"`

Now you can press `Alt+Space`, type `cortex-capture`, and hit Enter.

### Verification

After capturing, verify Tier 1 memory:
```powershell
python scripts/brain_query.py --tier1 --recent 5
```

**Expected:**
```
Recent Conversations (Tier 1):
1. 2025-11-08 15:30 - "Make the button purple" (5 messages)
2. 2025-11-08 14:15 - "Add authentication system" (23 messages)
3. 2025-11-08 10:00 - "Fix null reference error" (8 messages)
```

### Troubleshooting

**Problem:** "UIAutomation module not found"
```powershell
# Solution 1: Install from PowerShell Gallery
Install-Module -Name UIAutomation -Force

# Solution 2: Manual download
# Download from: https://github.com/UIAutomation/UIAutomation
# Extract to: C:\Users\<YourName>\Documents\PowerShell\Modules\UIAutomation
```

**Problem:** "Cannot find Copilot Chat window"
```
Cause: Chat window not in focus
Solution: Click on the chat panel in VS Code, then run script again
```

**Problem:** "Script captured empty text"
```
Cause: UI timing issue
Solution: Add delay before capture
```

Edit `capture-copilot-chat.ps1`:
```powershell
Start-Sleep -Seconds 2  # Add this line before capture
$chatText = $chatWindow.GetText()
```

---

## Method 2: Python CLI Integration

**Best For:** Cross-platform users, developers who want programmatic control

### How It Works

1. You finish a conversation in GitHub Copilot Chat
2. You run `cortex remember` command
3. CORTEX reads the conversation from VS Code's internal storage
4. Stores in Tier 1 memory with indexed search

### Setup Steps

#### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `sqlite3` (conversation storage)
- `pyautogui` (window interaction)
- `pywin32` (Windows clipboard access)

#### 2. Test the CLI Command

```bash
cortex remember
```

**Expected Output:**
```
🔍 Looking for recent Copilot conversations...
✅ Found 1 new conversation
📝 Processing conversation from 15:30:45...

Conversation Summary:
  - User messages: 3
  - Copilot messages: 3
  - Entities detected: 2 files, 1 class, 1 method
  - Intent: EXECUTE (confidence 0.92)

💾 Saved to Tier 1: conversation-20251108-153045
✅ Memory updated successfully!
```

#### 3. Create Shell Alias (Optional)

**PowerShell Profile:**
```powershell
notepad $PROFILE
```

Add this line:
```powershell
function cortex-remember { python d:\PROJECTS\CORTEX\scripts\cli.py remember }
```

Now you can type `cortex-remember` anywhere.

**Bash/Zsh (Linux/Mac):**
```bash
echo 'alias cortex-remember="python ~/CORTEX/scripts/cli.py remember"' >> ~/.bashrc
source ~/.bashrc
```

### Advanced CLI Commands

#### Remember Last N Conversations
```bash
cortex remember --last 5
```

#### Remember Conversations Since Timestamp
```bash
cortex remember --since "2025-11-08 10:00"
```

#### Export Memory as JSON
```bash
cortex export --tier1 --output backup.json
```

#### Query Memory
```bash
cortex query "What did we discuss about authentication?"
```

**Output:**
```
📊 Found 2 relevant conversations:

1. 2025-11-08 14:15 (23 messages)
   Intent: PLAN
   Key topics: authentication, login, security
   Files: AuthService.cs, LoginController.cs
   
   Summary: Planned and implemented user authentication
   system with password hashing and session management.

2. 2025-11-07 16:30 (12 messages)
   Intent: FIX
   Key topics: authentication bug, null reference
   Files: AuthService.cs
   
   Summary: Fixed null reference exception in login
   validation when username was empty.
```

### Verification

```bash
cortex status --tier1
```

**Expected:**
```
Tier 1 Memory Status:
  Total conversations: 18
  Date range: 2025-10-15 to 2025-11-08
  Storage size: 2.4 MB
  Oldest conversation: 2025-10-15 09:30 (auto-archived)
  Recent conversations: 20 (FIFO limit)
  
  Entity index:
    Files: 142 tracked
    Classes: 87 tracked
    Functions: 203 tracked
  
  Intent distribution:
    EXECUTE: 45% (8 conversations)
    FIX: 25% (5 conversations)
    PLAN: 20% (4 conversations)
    TEST: 10% (2 conversations)
```

---

## Method 3: Ambient Daemon (Automatic)

**Best For:** Power users who want fully automatic, background memory capture

### How It Works

1. Daemon runs in background as VS Code starts
2. Monitors GitHub Copilot Chat window for activity
3. Automatically captures conversations when you stop typing (30s idle)
4. Stores in Tier 1 with zero user intervention

### Setup Steps

#### 1. Install Daemon Service

```bash
python scripts/cortex/install_daemon.py
```

**Expected Output:**
```
🔧 Installing CORTEX Ambient Capture Daemon...

✅ Created daemon service: cortex-ambient-capture
✅ Configured auto-start on VS Code launch
✅ Set capture interval: 30 seconds
✅ Enabled idle detection

Daemon Status: READY (not running)

To start daemon:
  python scripts/cortex/auto_capture_daemon.py --start

To enable auto-start:
  Add to VS Code tasks.json (instructions below)
```

#### 2. Configure VS Code Task (Auto-Start)

Open `.vscode/tasks.json` in your workspace:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start CORTEX Ambient Capture",
      "type": "shell",
      "command": "python",
      "args": [
        "${workspaceFolder}/scripts/cortex/auto_capture_daemon.py",
        "--start"
      ],
      "isBackground": true,
      "runOptions": {
        "runOn": "folderOpen"
      },
      "problemMatcher": []
    }
  ]
}
```

This makes the daemon start automatically when you open the workspace.

#### 3. Start the Daemon

```bash
python scripts/cortex/auto_capture_daemon.py --start
```

**Expected Output:**
```
🚀 Starting CORTEX Ambient Capture Daemon...

Configuration:
  Capture interval: 30 seconds
  Idle threshold: 30 seconds
  Storage path: cortex-brain/tier1/conversations.db
  Log level: INFO

✅ Daemon started (PID: 12345)
📡 Monitoring GitHub Copilot Chat...
💾 Auto-save enabled
```

You'll see logs in the terminal:
```
[15:30:45] 👀 Chat activity detected
[15:31:15] ⏳ Idle for 30s, capturing conversation...
[15:31:16] 💾 Captured conversation-20251108-153045 (6 messages)
[15:31:16] ✅ Stored in Tier 1 memory
```

#### 4. Verify Daemon Is Running

```bash
cortex daemon status
```

**Expected:**
```
CORTEX Ambient Daemon Status:
  Status: RUNNING ✅
  PID: 12345
  Uptime: 2 hours 15 minutes
  
  Activity:
    Conversations captured: 7
    Last capture: 2 minutes ago
    Errors: 0
  
  Performance:
    CPU usage: 0.2%
    Memory: 45 MB
    Disk writes: 14 (2.1 MB)
```

### Daemon Configuration

Edit `cortex.config.json`:
```json
{
  "ambient_capture": {
    "enabled": true,
    "idle_threshold_seconds": 30,
    "capture_interval_seconds": 5,
    "max_conversation_size_kb": 500,
    "excluded_patterns": [
      "test conversation",
      "ignore this"
    ]
  }
}
```

**Settings:**
- `idle_threshold_seconds`: How long to wait after typing stops before capturing
- `capture_interval_seconds`: How often to check for activity (default 5s)
- `max_conversation_size_kb`: Skip conversations larger than this (prevents huge logs)
- `excluded_patterns`: Don't capture conversations containing these phrases

### Troubleshooting

**Problem:** Daemon not capturing conversations
```bash
# Check daemon logs
tail -f logs/ambient-capture.log
```

Look for:
```
[ERROR] Failed to access chat window: Access denied
```

**Solution:**
```bash
# Windows: Run as Administrator
# Linux/Mac: Grant accessibility permissions
```

**Problem:** Daemon capturing too frequently
```json
// Increase idle threshold
"idle_threshold_seconds": 60  // Wait 1 minute
```

**Problem:** Daemon using too much CPU
```json
// Decrease capture interval
"capture_interval_seconds": 10  // Check every 10s instead of 5s
```

---

## 🔍 Verification & Testing

### Test Tier 1 Memory Capture

1. **Have a short conversation with Copilot:**
```
You: "What is CORTEX?"
Copilot: "CORTEX is a memory system..."
```

2. **Capture using your chosen method:**
```bash
# PowerShell:
.\scripts\capture-copilot-chat.ps1

# Python CLI:
cortex remember

# Ambient Daemon:
(automatic after 30s idle)
```

3. **Query Tier 1 memory:**
```bash
cortex query "CORTEX memory system"
```

**Expected:**
```
📊 Found 1 relevant conversation:

1. 2025-11-08 15:45 (2 messages)
   Intent: STATUS
   Key topics: CORTEX, memory system
   
   Summary: Asked about CORTEX definition and memory system
```

### Test Entity Tracking

1. **Have a conversation mentioning specific files:**
```
You: "Add a method to AuthService.cs"
Copilot: "I'll add the method to AuthService.cs"
```

2. **Capture conversation**

3. **Query entities:**
```bash
cortex entities --file "AuthService.cs"
```

**Expected:**
```
Entities for AuthService.cs:

Recent mentions:
  - 2025-11-08 15:45: Added Login method
  - 2025-11-08 14:15: Created file
  
Relationships:
  - Imports: IAuthService.cs
  - Used by: LoginController.cs
  - Tests: AuthServiceTests.cs
```

---

## 🛠️ Advanced: Conversation History Import

### Import Old Conversations (Retroactive)

If you have old Copilot conversations you want to import:

```bash
python scripts/brain_import.py --source "path/to/old-conversations.json"
```

**Expected Output:**
```
📥 Importing conversations from old-conversations.json...

Processing:
  [██████████████████████████████] 100% (47 conversations)

Results:
  ✅ Imported: 45 conversations
  ⚠️  Skipped: 2 (duplicates)
  ❌ Failed: 0
  
  Date range: 2025-08-01 to 2025-11-07
  Total messages: 1,204
  
💾 Tier 1 memory updated successfully!
```

### Export Conversations (Backup)

```bash
cortex export --tier1 --output backup-2025-11-08.json
```

Creates backup file:
```json
{
  "export_date": "2025-11-08T15:45:00Z",
  "tier": "tier1",
  "conversation_count": 20,
  "conversations": [
    {
      "id": "conversation-20251108-153045",
      "timestamp": "2025-11-08T15:30:45Z",
      "messages": [...],
      "entities": [...],
      "intent": "EXECUTE"
    }
  ]
}
```

---

## 📊 Monitoring Memory Health

### Check Memory Stats

```bash
cortex stats
```

**Expected Output:**
```
CORTEX Memory Statistics:

Tier 1 (Working Memory):
  Status: ✅ Healthy
  Conversations: 20 / 20 (FIFO limit)
  Oldest: 15 days ago (auto-archived soon)
  Storage: 2.4 MB / 50 MB limit
  
  Capture methods:
    PowerShell: 5 conversations
    Python CLI: 8 conversations
    Ambient Daemon: 7 conversations
  
  Entity tracking:
    Files: 142 tracked
    Classes: 87 tracked
    Functions: 203 tracked

Tier 2 (Knowledge Graph):
  Status: ✅ Healthy
  Patterns learned: 34
  Workflows stored: 12
  File relationships: 156
  
Tier 3 (Context Intelligence):
  Status: ✅ Healthy
  Git commits analyzed: 247
  Session analytics: 45 sessions
  File stability tracked: 142 files
```

### Memory Cleanup

CORTEX automatically archives old conversations (FIFO queue = 20 most recent). But you can manually trigger cleanup:

```bash
# Archive conversations older than 30 days
cortex archive --older-than 30

# Delete conversations older than 90 days (permanent)
cortex cleanup --older-than 90
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Conversations Not Being Captured

**Symptoms:**
```bash
cortex query "recent work"
# Returns: No conversations found
```

**Diagnosis:**
```bash
cortex daemon status  # Check if daemon is running
ls cortex-brain/tier1/captures/  # Check for capture files
```

**Solutions:**
- If daemon stopped: `cortex daemon start`
- If no captures folder: `python scripts/brain_init.py` (reinitialize)
- If permissions issue: Run as Administrator (Windows) or `sudo` (Linux)

#### 2. Duplicate Conversations

**Symptoms:**
```bash
cortex stats
# Shows: 40 conversations but should be 20
```

**Cause:** Multiple capture methods running simultaneously

**Solution:**
```bash
# Choose ONE method, disable others:
cortex daemon stop  # Stop ambient daemon
# OR configure to use only one method
```

#### 3. Memory Growing Too Large

**Symptoms:**
```bash
cortex stats
# Shows: Storage 450 MB / 50 MB limit (OVER LIMIT)
```

**Solution:**
```bash
# Archive old conversations
cortex archive --older-than 30

# Cleanup very old data
cortex cleanup --older-than 90

# Adjust FIFO limit in config
# Edit cortex.config.json:
"tier1": {
  "maxConversations": 10  // Reduce from 20
}
```

#### 4. Entities Not Being Tracked

**Symptoms:**
```bash
cortex entities --file "AuthService.cs"
# Returns: No entities found
```

**Cause:** Entity extraction not enabled or failed

**Solution:**
```bash
# Check entity extraction is enabled
cat cortex.config.json | grep entity_extraction

# Should show:
"entity_extraction": {
  "enabled": true
}

# Re-process conversations to extract entities
python scripts/brain_reindex.py --tier1 --entities
```

---

## 📚 For More Information

**Related Documentation:**
- **Setup Guide:** `#file:prompts/shared/setup-guide.md` (Initial installation)
- **Technical Reference:** `#file:prompts/shared/technical-reference.md` (Tier 1 API details)
- **Agents Guide:** `#file:prompts/shared/agents-guide.md` (How agents use memory)
- **CORTEX Story:** `#file:prompts/shared/story.md` (Why memory matters)

---

**Version:** 2.0  
**Last Updated:** November 8, 2025  
**Phase:** 3.7 Complete - Full Modular Architecture  
**Tracking Methods:** 3 (PowerShell, Python CLI, Ambient Daemon)
