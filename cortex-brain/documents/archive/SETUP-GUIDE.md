# CORTEX Setup Guide

**Version:** 3.8.1  
**Last Updated:** December 11, 2025  
**Author:** Asif Hussain

---

## 🎯 Two Deployment Scenarios

CORTEX supports two deployment models:

### **New Users: Full Installation** (Recommended)
Download and install CORTEX in your repository. Complete control and isolation.

### **Existing Users: Workspace-Only Mode** (Advanced)
Already have CORTEX installed? Use workspace-only mode to avoid duplicate installations across multiple repositories.

---

## 📥 New User Installation

### Step 1: Download CORTEX

**Option A: Clone from GitHub (Latest)**
```bash
# Clone the main branch (production-ready)
git clone https://github.com/asifhussain60/CORTEX.git

# Or clone to specific location
git clone https://github.com/asifhussain60/CORTEX.git ~/cortex-ai
```

**Option B: Download Release Package**
```bash
# Download latest release
# Visit: https://github.com/asifhussain60/CORTEX/releases
# Download: cortex-[version]-production.tar.gz

# Extract to your preferred location
tar -xzf cortex-[version]-production.tar.gz
cd CORTEX
```

### Step 2: Install Dependencies

**Prerequisites:**
- Python 3.8+ (3.10+ recommended)
- Git installed and configured
- VS Code with GitHub Copilot extension

**Install Python Dependencies:**
```bash
# Navigate to CORTEX directory
cd CORTEX

# Install core dependencies
pip install -r requirements.txt

# Optional: Install development tools (testing, docs)
pip install -r optional-requirements.txt
```

### Step 3: Configure CORTEX

**Create Machine-Specific Configuration:**
```bash
# Copy template to create your config
cp cortex.config.template.json cortex.config.json

# Edit cortex.config.json with your machine hostname
# Set rootPath to where you cloned CORTEX
```

**Example Configuration:**
```json
{
  "machines": {
    "YOUR-MACHINE-NAME": {
      "rootPath": "C:\\PROJECTS\\CORTEX",
      "brainPath": "C:\\PROJECTS\\CORTEX\\cortex-brain"
    }
  }
}
```

### Step 4: Initialize CORTEX Brain

**Automatic Initialization:**
```bash
# From CORTEX directory
python -m src.main

# Or use GitHub Copilot Chat
# In VS Code: Open Copilot Chat and type "help"
```

**What Gets Initialized:**
- ✅ Tier 1 Database (Working Memory) - 70 conversation FIFO
- ✅ Tier 2 Database (Knowledge Graph) - Pattern learning
- ✅ Tier 3 Database (Dev Context) - Project metrics
- ✅ Brain Protection Rules (SKULL) - Quality enforcement
- ✅ Response Templates (62 templates) - Consistent responses

**Validation:**
```bash
# Run health check
python scripts/cli_wrappers/healthcheck_wrapper.py

# You should see:
# Status: ✓ HEALTHY
# Overall Score: 85-100/100
```

### Step 5: Activate in VS Code

**GitHub Copilot Auto-Discovery:**

CORTEX is automatically discovered by GitHub Copilot when you open a workspace with `.github/copilot-instructions.md`.

**Manual Activation (if needed):**
1. Open VS Code in the CORTEX directory
2. Open GitHub Copilot Chat (Ctrl+Shift+I or Cmd+Shift+I)
3. Type: `help`
4. CORTEX should respond with available operations

**First Command:**
```
help
```

You should see CORTEX's command reference with all available operations.

---

## 🔄 Existing User: Workspace-Only Mode

**Problem:** You already have CORTEX installed but work across 10+ repositories. Installing CORTEX 10 times is wasteful and creates maintenance overhead.

**Solution:** Use workspace-only mode with a **single centralized CORTEX installation**.

### Current Architecture (Isolated)

Each repository gets its own CORTEX installation:
```
~/projects/
├── app1/
│   └── CORTEX/              # Full installation (194 MB)
├── app2/
│   └── CORTEX/              # Full installation (194 MB)
├── app3/
│   └── CORTEX/              # Full installation (194 MB)
└── ... (7 more copies = 1.94 GB wasted)
```

### Workspace-Only Mode (Centralized)

**Step 1: Create Central CORTEX Installation**
```bash
# Install CORTEX once in a central location
mkdir -p ~/.cortex
cd ~/.cortex
git clone https://github.com/asifhussain60/CORTEX.git central

# Install dependencies
cd central
pip install -r requirements.txt

# Initialize brain
python -m src.main
```

**Step 2: Configure Each Workspace**

For each project repository, create a lightweight workspace link:

```bash
# In your project directory
cd ~/projects/your-app

# Create CORTEX workspace directory
mkdir -p CORTEX/Workspaces/your-app

# Create .cortex-link file pointing to central installation
echo "~/.cortex/central" > CORTEX/.cortex-link

# Add to .gitignore (CORTEX workspace is local-only)
echo "CORTEX/" >> .gitignore
```

**Step 3: Activate in Each Workspace**

When you open a project in VS Code:
1. CORTEX detects `.cortex-link` file
2. Routes to central installation
3. Uses workspace-specific brain storage: `CORTEX/Workspaces/your-app/`

**Benefits:**
- ✅ **Single Installation:** 194 MB vs 1.94 GB (10 repos)
- ✅ **Single Update:** Update once, all projects benefit
- ✅ **Workspace Isolation:** Each project has its own brain/context
- ✅ **Git Clean:** CORTEX/ directory is gitignored (not committed)

### How It Works

**Central CORTEX Structure:**
```
~/.cortex/central/
├── src/                    # Core code (shared)
├── cortex-brain/
│   ├── response-templates.yaml  # Shared templates
│   ├── brain-protection-rules.yaml  # Shared rules
│   └── Workspaces/         # Workspace-specific brains
│       ├── app1/
│       │   ├── tier1-working-memory.db
│       │   ├── tier2-knowledge-graph.db
│       │   └── tier3-dev-context.db
│       ├── app2/
│       │   ├── tier1-working-memory.db
│       │   ├── tier2-knowledge-graph.db
│       │   └── tier3-dev-context.db
│       └── app3/
│           └── ... (isolated brain storage)
```

**Project Repository Structure:**
```
~/projects/your-app/
├── src/                    # Your application code
├── CORTEX/
│   ├── .cortex-link       # Points to ~/.cortex/central
│   └── Workspaces/        # Symlink to central (auto-managed)
│       └── your-app/      # Workspace-specific brain
└── .gitignore             # Excludes CORTEX/
```

---

## 🔮 Coming in CORTEX 4.0: Zero-Install Experience

**Current Challenge:**
- 10 repositories = 10 CORTEX installations OR complex workspace-only setup
- Python dependencies required on every machine
- Manual configuration per machine

**CORTEX 4.0 Solution: Centralized Deployment with MCP**

### Architecture (Planned Q2 2026)

```
CORTEX Central Platform (Cloud/On-Prem Kubernetes)
    ├── Core Engine (Stateless, Auto-scale)
    ├── Company Brain Storage (Postgres, Redis)
    └── MCP Gateway (Tool Federation)
           ↕ HTTPS/gRPC API
    VS Code Extension (5MB thin client)
           └── Local Cache (Tier 3 only)
```

### What This Means for You

**Install Process (Future):**
1. Install CORTEX VS Code Extension from marketplace (5 MB, 10 seconds)
2. Connect to your organization's CORTEX platform
3. Start coding (zero Python, zero git clones, zero configuration)

**Benefits:**
- ✅ **Zero Local Install:** Just a VS Code extension
- ✅ **Instant Updates:** Rolling Kubernetes deployments (zero downtime)
- ✅ **Shared Infrastructure:** One platform serves all developers
- ✅ **No Version Drift:** Everyone on same version automatically
- ✅ **99.9% Uptime:** Kubernetes high availability
- ✅ **No Python Required:** All code runs centrally

**Model Context Protocol (MCP) Integration:**

CORTEX 4.0 will use MCP to federate all development tools:
```
MCP Gateway
    ├── Development Tools MCP (Git, Docker, K8s, Testing)
    ├── Enterprise Tools MCP (ADO, Jira, Confluence)
    └── Security Tools MCP (SAST, Dependency Scanners)
```

**Impact:**
- Add new tools without CORTEX code changes
- Centralized access control and governance
- Standard protocol for all integrations
- 70% faster tool integration

**Timeline:**
- **Q1 2026:** MCP Gateway prototype
- **Q2 2026:** Central platform MVP (10-50 users)
- **Q3 2026:** Production deployment (500+ users)
- **Q4 2026:** Enterprise scale (10,000+ users)

---

## 🚨 Troubleshooting

### Issue: "Module not found" errors
**Solution:**
```bash
# Ensure dependencies installed
pip install -r requirements.txt

# Check Python version (3.8+ required)
python --version
```

### Issue: CORTEX not responding in Copilot Chat
**Solution:**
```bash
# Verify .github/copilot-instructions.md exists
ls .github/copilot-instructions.md

# Restart VS Code
# Open Copilot Chat and type "help"
```

### Issue: Health check shows "Tier 3 missing"
**Solution:**
This is expected for fresh installations. Tier 3 (dev context) is initialized on first use.
```bash
# Force initialization
python -m src.tier3.initialize_dev_context
```

### Issue: Permission errors on Windows
**Solution:**
```bash
# Run as Administrator or add Python to PATH
# Ensure C:\PROJECTS\CORTEX is not in a protected directory
```

### Issue: Workspace-only mode not working
**Solution:**
```bash
# Verify .cortex-link file exists and points to valid path
cat CORTEX/.cortex-link

# Ensure central CORTEX is initialized
cd ~/.cortex/central
python scripts/cli_wrappers/healthcheck_wrapper.py
```

---

## 📚 Next Steps

**After Installation:**
1. ✅ Read: [README.md](README.md) - Complete feature overview
2. ✅ Try: `help` - See all available operations
3. ✅ Learn: `plan authentication feature` - Test Planning System
4. ✅ Explore: `load dashboard` - Launch Admin Dashboard
5. ✅ Master: `start tdd` - Begin TDD workflow

**Documentation:**
- `.github/prompts/CORTEX.prompt.md` - Complete entry point guide
- `cortex-brain/brain-protection-rules.yaml` - Quality enforcement rules
- `cortex-operations.yaml` - All 302 operations reference

**Support:**
- GitHub Issues: [https://github.com/asifhussain60/CORTEX/issues](https://github.com/asifhussain60/CORTEX/issues)
- Documentation: [https://asifhussain60.github.io/CORTEX/](https://asifhussain60.github.io/CORTEX/)

---

## 📄 License

**CORTEX is Source-Available:** Use allowed, no public contributions accepted.

When using CORTEX, please credit: "CORTEX by Asif Hussain (https://github.com/asifhussain60/CORTEX)"

**Copyright © 2025 Asif Hussain. All rights reserved.**

---

**Questions?** Type `help` in GitHub Copilot Chat to get started!
