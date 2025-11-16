# CORTEX Setup Guide

Complete guide to setting up CORTEX in any repository.

---

## 🎯 Overview

The CORTEX setup command initializes the complete cognitive architecture in your repository. It's designed to be run once per project and handles everything automatically.

**Estimated Time:** 5-10 minutes  
**Requirements:** Python 3.8+, Git (optional but recommended)

---

## 🚀 Quick Start

### Option 1: GitHub Copilot Chat

The easiest way to setup CORTEX:

```
#file:prompts/user/cortex.md

setup
```

CORTEX will detect your intent and run the full setup process.

### Option 2: Terminal Command

For more control or automation:

```bash
# Setup in current directory
python scripts/cortex_setup.py

# Setup in specific directory
python scripts/cortex_setup.py --repo /path/to/project

# Custom brain location
python scripts/cortex_setup.py --brain /custom/path

# Quiet mode (only errors)
python scripts/cortex_setup.py --quiet
```

### Option 3: Python API

For programmatic setup:

```python
from src.entry_point.cortex_entry import CortexEntry

# Initialize entry point
entry = CortexEntry()

# Run setup
results = entry.setup(
    repo_path="/path/to/project",  # Optional
    verbose=True                   # Show progress
)

# Check results
if results["success"]:
    print("✅ Setup completed!")
    print(f"Files scanned: {results['phases']['crawler']['files_scanned']}")
else:
    print("❌ Setup failed!")
    for error in results["errors"]:
        print(f"  - {error}")
```

---

## 📋 What Setup Does

### Phase 1: Environment Analysis (30 seconds)

Analyzes your repository to understand its structure:

**Detects:**
- Programming languages (Python, JavaScript, TypeScript, C#, Java, etc.)
- Frameworks (Node.js, .NET, Maven, etc.)
- Total file count
- Git repository status

**Output:**
```
✓ Detected: Python, JavaScript
✓ File count: 1,247
✓ Git repository: Yes
```

### Phase 2: Tooling Installation (1-3 minutes)

Installs required dependencies based on your project:

**Python Projects:**
- pytest (testing framework)
- pytest-cov (coverage reporting)
- PyYAML (configuration)
- black, flake8, mypy (code quality)

**Node.js Projects:**
- Installs from package.json
- Runs `npm install`

**Documentation:**
- mkdocs (documentation generator)
- mkdocs-material (beautiful theme)
- mkdocs-mermaid2-plugin (diagrams)

**Output:**
```
Installing Python dependencies...
✓ Python dependencies installed

Installing Node.js dependencies...
✓ Node.js dependencies installed

Installing MkDocs for documentation...
✓ MkDocs installed
```

### Phase 3: Brain Initialization (30 seconds)

Creates the CORTEX brain directory structure:

**Created Structure:**
```
cortex-brain/
├── README.md                    # Brain overview
├── tier0/                       # Instinct (immutable rules)
│   └── rules.md                 # Core principles (TDD, SOLID, etc.)
├── tier1/                       # Working Memory
│   ├── conversations.db         # Last 20 conversations
│   └── requests.log             # Request logging
├── tier2/                       # Knowledge Graph
│   └── knowledge_graph.db       # Learned patterns
├── tier3/                       # Context Intelligence
│   └── context.db               # Project metrics
└── corpus-callosum/             # Inter-hemisphere messaging
    └── coordination-queue.jsonl # Message queue
```

**Core Rules Created (Tier 0):**
1. Definition of READY (clear requirements)
2. Test-Driven Development (RED → GREEN → REFACTOR)
3. Definition of DONE (zero errors, all tests pass)
4. Challenge Risky Changes (Brain Protector)
5. SOLID Principles (clean architecture)
6. Local-First (works offline)
7. Incremental File Creation (prevent length limits)

**Output:**
```
✓ Created brain directory: /path/to/cortex-brain
✓ Created tier0
✓ Created tier1
✓ Created tier2
✓ Created tier3
✓ Created corpus-callosum
  ✓ Created rules.md
  ✓ Created conversations.db
  ✓ Created requests.log
  ✓ Created knowledge_graph.db
  ✓ Created context.db
  ✓ Created README.md
✓ CORTEX brain initialized
```

### Phase 4: Crawler Execution (3-7 minutes)

Scans your repository to populate the knowledge graph:

**What Gets Scanned:**
- All code files (.py, .js, .ts, .cs, .java, etc.)
- File relationships and co-modification patterns
- UI elements and IDs (for test generation)
- Git history and commit patterns
- Test files and coverage

**What Gets Learned:**
- Common patterns in your codebase
- File dependencies
- Architecture conventions
- Naming patterns
- Frequently modified files (hotspots)

**Output:**
```
Starting repository scan...
This may take 5-10 minutes depending on repository size...
  ✓ Scanned 1,247 code files
✓ Crawler completed in 187.3 seconds
```

### Phase 5: Welcome Message

Displays setup summary and next steps:

```
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                      🧠 CORTEX HAS AWAKENED 🧠                          ║
║                                                                          ║
║              Welcome to Your Enhanced AI Development Partner             ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

CORTEX is now operational and ready to assist you!

📚 GET STARTED:
   File: docs/getting-started/quick-start.md
   
   Quick command:
   #file:prompts/user/cortex.md
   [Your request here]

📖 THE STORY:
   Read "The Awakening of CORTEX" - A humorous and technical tale
   File: docs/story/index.md
   
   Five chapters covering:
   - Chapter 1: The Problem (Copilot's Amnesia)
   - Chapter 2: The Solution (Dual-Hemisphere Brain)
   - Chapter 3: The Memory (Five-Tier Intelligence)
   - Chapter 4: The Protection (Six-Layer Immune System)
   - Chapter 5: The Activation (60 Sacred Tests)

🎯 FIRST STEPS:
   1. Try: #file:prompts/user/cortex.md "What can you help me with?"
   2. Read the story (seriously, it's entertaining!)
   3. Check out: docs/architecture/ for technical details

📊 SETUP SUMMARY:
   Platform: Windows
   Languages: Python, JavaScript
   Files: 1,247
   Brain: d:\projects\myapp\cortex-brain
   Tiers: tier0, tier1, tier2, tier3
   Scanned: 1,247 files

CORTEX is ready. Start with the story, then experiment!
```

---

## 🔧 Configuration

### Custom Brain Location

By default, CORTEX creates the brain in `cortex-brain/` within your repository. To use a different location:

```bash
python scripts/cortex_setup.py --brain /custom/path
```

Or in Python:

```python
entry.setup(brain_path="/custom/path")
```

### Quiet Mode

For CI/CD or automated setups:

```bash
python scripts/cortex_setup.py --quiet
```

This suppresses progress output and only shows errors or final summary.

---

## ⚠️ Troubleshooting

### Setup Fails During Tooling Installation

**Problem:** Python or Node.js dependencies fail to install

**Solutions:**
1. Check your internet connection
2. Update pip: `python -m pip install --upgrade pip`
3. Update npm: `npm install -g npm@latest`
4. Check for conflicting dependencies
5. Run setup again (it will skip completed phases)

### Brain Initialization Fails

**Problem:** Cannot create brain directory structure

**Solutions:**
1. Check write permissions for repository directory
2. Ensure no existing `cortex-brain/` directory with locked files
3. Check disk space (brain requires ~10MB minimum)

### Crawler Takes Too Long

**Problem:** Crawler exceeds 10 minutes

**Solutions:**
1. This is normal for very large repositories (>10,000 files)
2. Setup will complete, crawler just takes longer
3. Consider using `.gitignore` to exclude unnecessary directories
4. Crawler can be re-run later: `python scripts/run_crawler.py`

### Import Errors After Setup

**Problem:** `ModuleNotFoundError` when using CORTEX

**Solutions:**
1. Ensure you're in the repository root
2. Check Python path includes `src/`
3. Verify dependencies installed: `pip list | grep pytest`
4. Try: `python -m pip install -r requirements.txt`

---

## 🔄 Re-running Setup

Setup is idempotent and can be safely re-run:

```bash
# Re-run full setup
python scripts/cortex_setup.py

# Only re-initialize brain (fast)
python -c "from src.entry_point.setup_command import CortexSetup; s = CortexSetup(); s._initialize_brain()"

# Only re-run crawler
python scripts/run_crawler.py
```

**What Happens:**
- ✅ Existing brain data is preserved
- ✅ Tier databases are not overwritten
- ✅ Only missing components are created
- ✅ Conversation history is maintained

---

## 📊 Validating Setup

After setup completes, validate CORTEX is working:

### Test 1: Health Check

```
#file:prompts/user/cortex.md

Check system health
```

Should return:
```
✅ Tier 1 (Working Memory): Healthy
✅ Tier 2 (Knowledge Graph): Healthy
✅ Tier 3 (Context Intelligence): Healthy
✅ Overall Status: Healthy
```

### Test 2: Simple Request

```
#file:prompts/user/cortex.md

What can you help me with?
```

Should return a summary of CORTEX capabilities.

### Test 3: Pattern Query

```
#file:prompts/user/cortex.md

What patterns have you learned from this repository?
```

Should return patterns discovered during crawler scan.

---

## 🎯 Next Steps

After successful setup:

1. **Read the Story** - `docs/story/index.md` - Understand how CORTEX works
2. **Try Simple Commands** - Start with "What can you help me with?"
3. **Explore Examples** - Check `docs/guides/` for common workflows
4. **Review Architecture** - `docs/architecture/` for technical details
5. **Check Quick Reference** - `docs/getting-started/quick-start.md`

---

## 🆘 Getting Help

If setup fails or you encounter issues:

1. Check logs: `cortex-brain/logs/setup_YYYYMMDD_HHMMSS.log`
2. Review error messages (setup is verbose)
3. Check troubleshooting section above
4. Validate Python version: `python --version` (3.8+ required)
5. Verify Git installed: `git --version`

---

## 📝 Setup Checklist

Use this checklist to verify setup completion:

- [ ] Phase 1: Environment detected correctly
- [ ] Phase 2: All dependencies installed
- [ ] Phase 3: Brain structure created
- [ ] Phase 4: Crawler completed scan
- [ ] Phase 5: Welcome message displayed
- [ ] Health check passes
- [ ] Simple request works
- [ ] No errors in setup log

If all items checked, CORTEX is ready! 🎉

---

**Setup completed?** Head to [Quick Start Guide](quick-start.md) to start using CORTEX!
