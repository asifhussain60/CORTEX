# 🚀 CORTEX Setup Guide

**Version:** 3.3.0  
**Branch:** main  
**Updated:** 2025-11-30

---

## 📦 What is This?

This is the **production-ready CORTEX deployment package** - a clean, minimal installation for end users.

**What you get:**
- ✅ Complete CORTEX source code (`src/`)
- ✅ Brain storage system (`cortex-brain/`)
- ✅ GitHub Copilot integration (`.github/prompts/`)
- ✅ Modular documentation (`prompts/`)
- ✅ Automation scripts (`scripts/`)
- ✅ Core dependencies (`requirements.txt` - 16 packages, ~123.5 MB)
- ✅ Optional tools (`optional-requirements.txt` - 6 packages, ~26.5 MB, auto-installed when needed)

**What's excluded:**
- ❌ Development tools (tests, CI/CD, build scripts)
- ❌ Documentation website (MkDocs)
- ❌ Example code
- ❌ Commit history from main branch

---

## 🎯 Quick Start

### Option 1: Clone This Branch Only (Recommended)

```bash
# Clone only the publish branch (fast, clean)
git clone -b main --single-branch https://github.com/asifhussain60/CORTEX.git
cd CORTEX
```

### Option 2: Switch to This Branch

```bash
# If you already have the repo
git fetch origin
git checkout main
```

---

## 🛠️ Installation

### 1️⃣ Prerequisites

**Required:**
- Python 3.8 or higher
- Git
- GitHub Copilot (VS Code extension)

**Check your versions:**
```bash
python --version
git --version
```

### 2️⃣ Install Core Dependencies

```bash
# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install CORTEX core dependencies (16 packages, ~123.5 MB)
pip install -r requirements.txt

# Optional: Install development tools (6 packages, ~26.5 MB)
# These auto-install when first used, or install manually:
pip install -r optional-requirements.txt
```

**💡 Lazy Loading:** Development tools (black, flake8, mypy, radon, pylint, vulture) are automatically installed the first time you use commands like `validate lint`, `format code`, or `check types`. You'll see a one-time prompt to install them.

### 3️⃣ Configure CORTEX

```bash
# Copy template configuration
cp cortex.config.template.json cortex.config.json

# Edit cortex.config.json with your paths
# (Use absolute paths for your machine)
```

### 4️⃣ Initialize Brain

```bash
# Run CORTEX setup (initializes brain storage)
# In VS Code, tell GitHub Copilot:
/CORTEX setup environment
```

Or use Python directly:
```bash
python -m src.setup.setup_orchestrator
```

### 5️⃣ Validate Installation

After initializing CORTEX, validate that everything is working correctly:

```bash
# Run installation validation
python -m src.orchestrators.setup_epm_orchestrator --validate

# Or via GitHub Copilot Chat:
/CORTEX validate installation
```

**Expected Output:**
```
🧠 CORTEX Installation Validation

Stage 1: Bootstrap Verification
  ✅ Entry Point
  ✅ Brain Structure
  ✅ Response Templates
  ✅ Orchestrators

Stage 2: Deployment Gate Validation (16 Gates)
  ✅ Gate  1: System Alignment (ERROR)
  ✅ Gate  2: TDD Integration (ERROR)
  ✅ Gate  3: Code Quality (ERROR)
  ✅ Gate  4: Test Coverage (ERROR)
  ✅ Gate  5: Documentation Complete (ERROR)
  ✅ Gate  6: Template Format (ERROR)
  ✅ Gate  7: Git Checkpoint System (ERROR)
  ✅ Gate  8: SWAGGER Entry Points (ERROR)
  ✅ Gate  9: Conversation Tracking (ERROR)
  ✅ Gate 10: Align Admin-Only (WARNING)
  ✅ Gate 11: Cleanup Data Preservation (ERROR)
  ✅ Gate 12: Deploy Manifest Valid (ERROR)
  ✅ Gate 13: TDD Mastery Integration (ERROR)
  ✅ Gate 14: User Feature Packaging (ERROR)
  ✅ Gate 15: Admin/User Separation (ERROR)
  ✅ Gate 16: Align EPM User-Only (WARNING)

📄 Validation report saved: cortex-brain/documents/reports/installation-validation-{timestamp}.md

✅ CORTEX is ready to use!
```

**If Validation Fails:**

```bash
# Auto-fix common issues
python -m src.orchestrators.setup_epm_orchestrator --validate --fix

# Example output with fixes:
🧠 CORTEX Installation Validation

Stage 1: Bootstrap Verification
  ❌ Response Templates
  ❌ Brain Structure

🔧 Attempting auto-remediation...
  ✅ Fixed: response-templates.yaml restored
  ✅ Fixed: Brain directories recreated

Re-validating after fixes...
  ✅ Response Templates
  ✅ Brain Structure

✅ CORTEX is ready to use (after auto-fixes)!
```

**View Detailed Report:**

```bash
# Check the validation report for detailed analysis
cat cortex-brain/documents/reports/installation-validation-{timestamp}.md
```

The report includes:
- Bootstrap verification results (entry point, brain, templates, orchestrators)
- 16-gate validation results with severity levels
- Specific error messages and recommendations
- Auto-remediation actions (if `--fix` was used)
- Next steps for manual fixes (if needed)

**🔍 Understanding Gate Validation:**

CORTEX uses a **16-gate validation system** to ensure complete functional integrity:

**ERROR Gates (block deployment, warn on installation):**
1. **System Alignment** - Alignment reports present
2. **TDD Integration** - Tests run before deployment
3. **Code Quality** - No mock/stub patterns in production
4. **Test Coverage** - Minimum coverage thresholds met
5. **Documentation Complete** - All features documented
6. **Template Format** - Response templates properly formatted
7. **Git Checkpoint System** - Checkpoint orchestrator complete
8. **SWAGGER Entry Points** - Swagger features wired
9. **Conversation Tracking** - Tier 1/3 databases functional
11. **Cleanup Data Preservation** - Brain data preserved
12. **Deploy Manifest Valid** - Deployment manifest exists
13. **TDD Mastery Integration** - Git checkpoints in TDD workflow
14. **User Feature Packaging** - 5 key features included
15. **Admin/User Separation** - Admin tools excluded

**WARNING Gates (non-blocking):**
10. **Align Admin-Only** - Alignment triggers admin-only
16. **Align EPM User-Only** - Setup EPM user-facing only

**What Happens on Failure:**
- **Deployment:** ERROR gates block deployment, deployment aborted
- **Installation:** All gates run, report generated, user notified
- **Auto-fix:** Common issues (templates, brain structure) auto-remediated
- **Manual fix:** Complex issues (code changes) require manual intervention

**⚠️ Common Validation Issues:**

**Issue: Missing Response Templates**
```bash
# Auto-fix
python -m src.orchestrators.setup_epm_orchestrator --validate --fix

# Or manual fix
cp cortex-brain/response-templates.yaml.bak cortex-brain/response-templates.yaml
```

**Issue: Incomplete Brain Structure**
```bash
# Auto-fix
python -m src.orchestrators.setup_epm_orchestrator --validate --fix

# Or manual fix
mkdir -p cortex-brain/tier1 cortex-brain/tier3 cortex-brain/documents/reports
```

**Issue: Gate Failures (Code-Level)**

These require code/documentation changes and cannot be auto-fixed. Review the detailed report:
```bash
cat cortex-brain/documents/reports/installation-validation-{timestamp}.md
```

Follow recommendations in the **Recommendations** section.

**✅ Validation Success Criteria:**

CORTEX is ready to use when:
- ✅ Bootstrap verification: 4/4 checks passed
- ✅ Gate validation: 14+ gates passed (ERROR gates must pass)
- ✅ Overall status: HEALTHY or WARNING
- ✅ Report shows: "CORTEX is ready to use!"

After successful validation, you can start working with CORTEX immediately!

---

## 📚 Using CORTEX

### GitHub Copilot Integration

CORTEX integrates with GitHub Copilot Chat via `.github/prompts/CORTEX.prompt.md`.

**In VS Code Copilot Chat:**
```
/CORTEX help              # Show all commands
/CORTEX                   # Main entry point
setup environment         # Configure environment
demo                      # Interactive tutorial
cleanup workspace         # Clean temporary files
```

### Natural Language Commands

CORTEX understands natural language:
```
"Add a purple button to the dashboard"
"Setup my environment"
"Show me where I left off"
"Run cleanup in dry-run mode"
```

---

## 🧠 Understanding CORTEX

### The Story

Read the human-friendly explanation:
```
#file:prompts/shared/story.md
```

### Technical Reference

Deep dive into architecture:
```
#file:prompts/shared/technical-reference.md
```

### Full Documentation

All modular docs are in `prompts/shared/`:
- `story.md` - The Intern with Amnesia
- `setup-guide.md` - Installation details
- `technical-reference.md` - API reference
- `agents-guide.md` - 10 specialist agents
- `tracking-guide.md` - Conversation memory
- `configuration-reference.md` - Config options
- `plugin-system.md` - Plugin development

---

## 🔧 Configuration

### cortex.config.json Structure

```json
{
  "cortex_root": "/absolute/path/to/CORTEX",
  "brain": {
    "tier1": {
      "database_path": "/absolute/path/to/cortex-brain/tier1/conversations.db",
      "conversation_limit": 20
    },
    "tier2": {
      "database_path": "/absolute/path/to/cortex-brain/tier2/knowledge-graph.db"
    },
    "tier3": {
      "database_path": "/absolute/path/to/cortex-brain/tier3/development-context.db"
    }
  },
  "plugins": {
    "enabled": [
      "cleanup_plugin",
      "platform_switch_plugin",
      "doc_refresh_plugin"
    ]
  }
}
```

**Important:** Use absolute paths! CORTEX works across multiple machines.

---

## 🚨 Troubleshooting

### Import Errors

```bash
# Make sure you're in the CORTEX root directory
cd /path/to/CORTEX

# Verify PYTHONPATH includes CORTEX root
export PYTHONPATH=/path/to/CORTEX:$PYTHONPATH
```

### Configuration Not Found

```bash
# Check config file exists
ls -la cortex.config.json

# Verify paths are absolute
cat cortex.config.json
```

### Brain Database Errors

```bash
# Reinitialize brain
python -m src.setup.modules.brain_initialization_module
```

### Conversation Tracking Not Working

See tracking guide:
```
#file:prompts/shared/tracking-guide.md
```

---

## 📖 Next Steps

1. **First time?** Read the story: `#file:prompts/shared/story.md`
2. **Configure:** Edit `cortex.config.json` with your paths
3. **Initialize:** Run `/CORTEX setup environment`
4. **Learn:** Run `demo` in Copilot Chat
5. **Start working:** Just tell CORTEX what you need!

---

## 📞 Support

- **Repository:** https://github.com/asifhussain60/CORTEX
- **Issues:** https://github.com/asifhussain60/CORTEX/issues
- **Documentation:** Use `#file:prompts/shared/*.md` in Copilot Chat

---

## 📄 License

**Copyright © 2024-2025 Asif Hussain. All rights reserved.**

This is proprietary software. See LICENSE file for full terms.

Unauthorized reproduction or distribution is prohibited.

---

## ✨ What Makes This Branch Special?

**This is an orphan branch:**
- ✅ No commit history from main development branch
- ✅ Minimal file size (production code only)
- ✅ Clean git history (publish commits only)
- ✅ Fast clone (no dev history to download)
- ✅ Perfect for end-user deployment

**Clone command:**
```bash
git clone -b main --single-branch https://github.com/asifhussain60/CORTEX.git
```

**Why orphan?**
- Main branch: 10,000+ commits, full dev history, test files, docs
- Publish branch: Clean slate, production code only, ~100 commits
- Result: 90% faster clone, 70% smaller disk usage

---

*Last Updated: 2025-11-30 13:52:03 | CORTEX 3.3.0*
