# CORTEX Setup for GitHub Copilot

**One-Line Installation:** Copy this CORTEX folder into your project, then in Copilot Chat say: `onboard this application`

---

## Quick Start

1. **Copy CORTEX folder** into your project root
2. **Open GitHub Copilot Chat** in VS Code
3. **Type:** `onboard this application`
4. **Done!** CORTEX will guide you through the rest

---

## What You Get

✅ **AI Assistant** - Natural language interface for all operations  
✅ **TDD Mastery** - Automated test-driven development workflow  
✅ **Brain System** - Conversation memory, knowledge graph, context awareness  
✅ **Planning Tools** - Feature planning with DoR/DoD enforcement  
✅ **Zero Config** - Works out of the box, customizable as needed

---

## Manual Setup (Optional)

If you prefer manual setup:

1. **Install dependencies:**
   ```bash
   pip install -r CORTEX/requirements.txt
   ```

2. **Add to .gitignore:**
   ```gitignore
   # CORTEX brain data (local only)
   CORTEX/cortex-brain/*.db
   CORTEX/cortex-brain/*.db-wal
   CORTEX/cortex-brain/*.db-shm
   CORTEX/cortex-brain/tier1/
   CORTEX/cortex-brain/conversation-captures/
   ```

3. **Configure (optional):**
   - Copy `cortex.config.template.json` to `cortex.config.json`
   - Customize settings as needed

4. **Start using:**
   - In Copilot Chat: `help` - Show available commands
   - In Copilot Chat: `what can cortex do` - Full capabilities list

---

## Verification

After setup, verify CORTEX is working:

```
In Copilot Chat:
> cortex status

Expected: CORTEX responds with system health and capabilities
```

---

## Support

- **Documentation:** See `CORTEX/.github/prompts/CORTEX.prompt.md`
- **Feedback:** In Copilot Chat say `feedback` to report issues
- **Updates:** In Copilot Chat say `upgrade cortex` for latest version

---

**Version:** 3.2.0  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX
