---
title: Getting Started with CORTEX
description: Complete guide to setup, onboarding, demo, and first steps
date: 2025-11-22
---

# Getting Started with CORTEX

Welcome to CORTEX! This guide will get you up and running in under 5 minutes.

## 🎯 Quick Links

- [Setup](#-setup) - Install and configure CORTEX
- [Onboarding](#-onboarding) - Configure GitHub Copilot integration
- [Demo](#-demo) - Interactive walkthrough
- [First Steps](#-first-steps) - Common tasks and workflows
- [Troubleshooting](#-troubleshooting) - Common issues and solutions

---

## 🚀 Setup

### Prerequisites

- Python 3.11+
- VS Code with GitHub Copilot extension
- Git

### Installation

#### Option 1: Quick Setup (Recommended for Users)

```bash
# Download CORTEX user package
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# Run automated setup
python scripts/setup_cortex.py --mode=user
```

#### Option 2: Developer Setup (Full Source)

```bash
# Clone full repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# Install dependencies
pip install -r requirements.txt

# Run tests (optional)
pytest tests/

# Setup CORTEX
python scripts/setup_cortex.py --mode=developer
```

### Configuration

1. **Copy configuration template:**
   ```bash
   cp cortex.config.example.json cortex.config.json
   ```

2. **Update workspace path:**
   ```json
   {
     "workspace_root": "/path/to/your/project",
     "brain_path": "cortex-brain/"
   }
   ```

3. **Verify setup:**
   ```bash
   python scripts/verify_setup.py
   ```

**Expected Output:**
```
✅ CORTEX setup verification complete
✅ Configuration file found
✅ Brain directories initialized
✅ Database connections successful
✅ GitHub Copilot integration ready
```

---

## 📚 Onboarding

### Step 1: Configure GitHub Copilot

1. Open VS Code
2. Install GitHub Copilot extension (if not already installed)
3. Verify `.github/copilot-instructions.md` exists in your workspace

**File:** `.github/copilot-instructions.md`

```markdown
# GitHub Copilot Instructions for CORTEX

**Entry Point:** This file enables GitHub Copilot to find and load CORTEX AI Assistant.

**Primary prompt file:** `.github/prompts/CORTEX.prompt.md`

GitHub Copilot should load this file to activate CORTEX's full capabilities.
```

### Step 2: Verify CORTEX Integration

Ask GitHub Copilot in chat:

```
help
```

**Expected Response:** CORTEX help table with available commands

If you see the CORTEX help table, integration is successful! ✅

If not, see [Troubleshooting](#-troubleshooting).

### Step 3: Test Memory System

**Store a preference:**
```
store this: I prefer Python 3.11, pytest for testing, and type hints for all functions
```

**Later session (restart VS Code), ask:**
```
what are my testing preferences?
```

**CORTEX should recall:** "You prefer pytest for testing and type hints for all functions"

---

## 🎮 Demo

### Interactive Demo (Recommended)

Run the interactive CORTEX demo with live execution:

```
demo
```

**Select Profile:**

1. **Quick** (2 minutes) - Essential commands only
2. **Standard** (3-4 minutes) - Core capabilities
3. **Comprehensive** (5-6 minutes) - Full walkthrough

**What You'll See:**
- Help system demonstration
- Story refresh workflow
- Feature planning with DoR validation
- Token optimization techniques
- Code review capabilities
- Cleanup operations
- Conversation tracking

### Manual Demo Walkthrough

#### 1. Help System

```
help
```

View all available CORTEX commands organized by category.

#### 2. Story Refresh

```
refresh story
```

Generate or update "The Awakening of CORTEX" narrative documentation.

#### 3. Feature Planning

```
plan: Add user authentication with JWT tokens
```

CORTEX guides you through:
- Definition of Ready (DoR) validation
- Requirements clarification
- Security review (OWASP checklist)
- Implementation plan generation

#### 4. Code Review

```
review my recent changes
```

CORTEX analyzes:
- Git history (last 2 days)
- Code patterns
- Potential improvements
- Security issues

#### 5. Documentation Generation

```
generate documentation
```

CORTEX generates:
- Feature discovery from Git/YAML
- Architecture documentation
- API reference
- MkDocs site

---

## ⚡ First Steps

### Common Tasks

#### Plan a New Feature

```
plan: Add user authentication with JWT tokens
```

**CORTEX Workflow:**
1. ✅ DoR validation (Definition of Ready)
2. ✅ Requirements clarification
3. ✅ Security review (OWASP checklist)
4. ✅ Implementation plan generation
5. ✅ ADO-style work item creation (optional)

#### Review Code Changes

```
review recent changes
```

**CORTEX analyzes:**
- Git commits (last 2 days by default)
- Code patterns and style
- Potential improvements
- Security vulnerabilities
- Test coverage gaps

#### Generate Documentation

```
update documentation
```

**CORTEX generates:**
- Feature discovery (Git + YAML)
- 14+ Mermaid diagrams
- 14+ DALL-E prompts
- Architecture docs
- Technical documentation
- MkDocs site

#### Store Knowledge

```
store this: We use FastAPI for REST APIs, SQLAlchemy for ORM, and pytest with 90%+ coverage target
```

**CORTEX remembers:**
- Coding preferences
- Architecture decisions
- Testing strategies
- Patterns and conventions

#### Check CORTEX Status

```
status
```

**CORTEX reports:**
- Memory usage (Tier 1-3)
- Conversation count
- Knowledge graph entities
- System health

### Quick Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `help` | Show all commands | `help` |
| `plan [feature]` | Start feature planning | `plan: Add auth` |
| `implement [feature]` | Execute implementation | `implement authentication` |
| `review [scope]` | Code review | `review recent changes` |
| `test [scope]` | Generate tests | `test UserService` |
| `document [scope]` | Generate docs | `document API` |
| `refresh story` | Update narrative | `refresh story` |
| `status` | System status | `status` |
| `demo` | Interactive demo | `demo` |

---

## 🆘 Troubleshooting

### Issue: CORTEX Not Responding

**Symptoms:** GitHub Copilot doesn't show CORTEX responses

**Solutions:**

1. **Check copilot instructions file exists:**
   ```bash
   ls -la .github/copilot-instructions.md
   ```

2. **Verify CORTEX prompt file loaded:**
   ```bash
   ls -la .github/prompts/CORTEX.prompt.md
   ```

3. **Restart VS Code:**
   - Close all VS Code windows
   - Reopen workspace
   - Ask: `help`

4. **Check GitHub Copilot status:**
   - Bottom right of VS Code
   - Should show "GitHub Copilot" icon
   - Click to verify active

### Issue: Memory Not Persisting

**Symptoms:** CORTEX forgets previous conversations

**Solutions:**

1. **Check database exists:**
   ```bash
   ls -la cortex-brain/tier1/conversation-history.db
   ```

2. **Verify database permissions:**
   ```bash
   chmod 644 cortex-brain/tier1/conversation-history.db
   ```

3. **Check storage quota:**
   ```bash
   python scripts/check_storage.py
   ```

4. **Reimport conversations (if backed up):**
   ```bash
   python scripts/import_brain.py --input=backup.json
   ```

### Issue: Tests Failing

**Symptoms:** `pytest tests/` shows failures

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version  # Must be 3.11+
   ```

2. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. **Run specific test to isolate:**
   ```bash
   pytest tests/tier0/ -v
   ```

4. **Check for environment variables:**
   ```bash
   env | grep CORTEX
   ```

### Issue: Setup Script Errors

**Symptoms:** `setup_cortex.py` fails

**Solutions:**

1. **Check Python installation:**
   ```bash
   which python
   python --version
   ```

2. **Verify Git installed:**
   ```bash
   which git
   git --version
   ```

3. **Run with verbose output:**
   ```bash
   python scripts/setup_cortex.py --mode=user --verbose
   ```

4. **Check logs:**
   ```bash
   cat logs/cortex.log
   ```

### Issue: MkDocs Build Fails

**Symptoms:** `mkdocs build` or `mkdocs serve` errors

**Solutions:**

1. **Install MkDocs:**
   ```bash
   pip install mkdocs mkdocs-material
   ```

2. **Verify mkdocs.yml exists:**
   ```bash
   ls -la mkdocs.yml
   ```

3. **Check for missing docs:**
   ```bash
   mkdocs build --verbose
   ```

4. **Regenerate documentation:**
   ```bash
   python cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py
   ```

---

## 📞 Support & Resources

### Documentation

- **[CORTEX vs COPILOT](CORTEX-VS-COPILOT.md)** - Why choose CORTEX
- **[Architecture](ARCHITECTURE.md)** - System architecture
- **[Technical Documentation](TECHNICAL-DOCUMENTATION.md)** - API reference
- **[FAQ](FAQ.md)** - Frequently asked questions

### Community

- **GitHub Issues:** https://github.com/asifhussain60/CORTEX/issues
- **Discussions:** https://github.com/asifhussain60/CORTEX/discussions
- **Documentation Site:** https://asifhussain60.github.io/CORTEX

### Contact

- **Author:** Asif Hussain
- **Email:** [Contact via GitHub]
- **Repository:** https://github.com/asifhussain60/CORTEX

---

## 🎓 Next Steps

Now that you're set up:

1. ✅ **Try the demo:** `demo` - See CORTEX in action
2. ✅ **Plan your first feature:** `plan: [your feature]`
3. ✅ **Store your preferences:** `store this: [your preferences]`
4. ✅ **Review some code:** `review recent changes`
5. ✅ **Generate documentation:** `generate documentation`

**Pro Tips:**
- CORTEX learns from your patterns - the more you use it, the better it gets
- Store your coding preferences early for consistent responses
- Use the `status` command to monitor memory usage
- Run `demo` periodically to discover new features

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Version:** 3.0  
**Last Updated:** 2025-11-22  
**Repository:** https://github.com/asifhussain60/CORTEX
