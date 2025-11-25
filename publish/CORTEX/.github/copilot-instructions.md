# GitHub Copilot Instructions for CORTEX

**Entry Point:** This file enables GitHub Copilot to find and load CORTEX AI Assistant.

---

## 🎯 Main Entry Point

**Primary prompt file:** `.github/prompts/CORTEX.prompt.md`

GitHub Copilot should load this file to activate CORTEX's full capabilities.

---

## 📚 Architecture

CORTEX uses a modular architecture:

- **Main Prompt:** `.github/prompts/CORTEX.prompt.md` (command reference + routing)
- **Modules:** `.github/prompts/modules/` (specialized documentation)
  - `response-format.md` - Response structure guidelines
  - `document-organization.md` - File organization rules
  - `planning-system.md` - Feature planning workflows
  - `template-system.md` - Response template system

---

## ⚡ Quick Commands

Users can interact with CORTEX using natural language:

- `help` - Show available commands
- `onboard this application` - Initialize CORTEX in user's app
- `plan a feature` - Start interactive feature planning
- `setup environment` - Configure CORTEX environment
- `cleanup` - Clean up old files

---

## 🧠 Intelligence Layers

- **Tier 0:** Brain Protection (SKULL rules)
- **Tier 1:** Conversation Memory (context tracking)
- **Tier 2:** Knowledge Graph (pattern learning)
- **Tier 3:** Development Context (project-specific)

---

## 📦 Installation & Upgrades

CORTEX is distributed via the `main` branch:

```bash
# Clone CORTEX (initial installation)
git clone -b main --single-branch https://github.com/asifhussain60/CORTEX.git

# Upgrade to latest version (from within CORTEX directory)
git pull origin main
```

**Branch Strategy:**
- `main` - Latest stable release (for user installations and upgrades)
- `CORTEX-3.0` - Active development branch
- Feature branches - Specific feature development

---

**Version:** 2.0  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX (main branch)
