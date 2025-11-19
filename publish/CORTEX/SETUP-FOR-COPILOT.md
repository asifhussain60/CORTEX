# CORTEX Setup for Your Application

## ⚡ Quick Start (One Command!)

### Step 1: Copy CORTEX to Your Project

**Copy this entire CORTEX folder to your application:**

```bash
# Navigate to your application
cd /path/to/your/application

# Copy CORTEX folder (creates your-app/cortex/)
cp -r /path/to/CORTEX ./cortex
```

**Result:** CORTEX now lives in `your-app/cortex/` (self-contained, ready to go!)

---

### Step 2: Open VS Code & Onboard

**Open your application in VS Code, then in Copilot Chat:**

```
onboard this application
```

**That's it!** CORTEX will:

1. ✅ Copy entry points from `cortex/.github/` to your app's `.github/` folder
2. ✅ Install required tooling (Python, Vision API, etc.)
3. ✅ Initialize brain databases (Tier 1, 2, 3)
4. ✅ Crawl and index your codebase
5. ✅ Analyze your project structure and tech stack
6. ✅ Ask intelligent questions about improvements:
   - "I see React but no test files - shall I help set up Jest + React Testing Library?"
   - "You have ESLint configured but not running on commit - want me to add pre-commit hooks?"
   - "No TypeScript detected - would you like me to migrate for better type safety?"

**Then just answer the questions** and CORTEX will implement everything with tests!

---

## 🏗️ What Happens Behind the Scenes

**Before onboarding:**
```
your-app/
├── cortex/                          # CORTEX installation (self-contained)
│   ├── .github/                     # Entry points HERE initially
│   │   ├── prompts/
│   │   │   └── CORTEX.prompt.md     # Copilot reads this
│   ├── cortex-brain/
│   ├── src/
│   └── ...
├── src/                             # Your app code
└── package.json
```

**After "onboard this application":**
```
your-app/
├── .github/                         # ✅ Entry points copied here by Module 1
│   ├── prompts/
│   │   └── CORTEX.prompt.md         # For convenience (app root location)
├── cortex/                          # CORTEX installation (unchanged)
│   ├── .github/                     # Original entry points (backup)
│   ├── cortex-brain/                # Brain initialized
│   └── ...
├── src/                             # Your app code
└── ...
```

---

## 📋 Manual Setup (If Onboarding Fails)

If automatic onboarding fails, run these steps manually:

```bash
# 1. Copy CORTEX folder to your project (if not done already)
cd /path/to/your/application
cp -r /path/to/publish/CORTEX ./cortex

# 2. Copy entry points to app root
mkdir -p .github/prompts
cp cortex/.github/prompts/CORTEX.prompt.md .github/prompts/

# 3. Install dependencies
cd cortex
pip install -r requirements.txt

# 4. Initialize brain
python -c "from src.tier1.conversation_manager import ConversationManager; ConversationManager()"

# 5. In VS Code Copilot Chat
# Type: analyze my codebase
```

---

## 🎯 What CORTEX Can Do

After onboarding, CORTEX can help you with:

- **Feature Implementation:** "Add authentication with JWT"
- **Testing:** "Create comprehensive tests for the UserService"
- **Refactoring:** "Improve code quality in src/utils/"
- **Documentation:** "Generate API documentation"
- **Architecture:** "Design a microservices architecture"

And it remembers everything from past conversations! 🧠

---

## 🔍 How Copilot Finds CORTEX

**The Magic:** When you say "onboard this application", Copilot searches your workspace for prompt files and finds `cortex/.github/prompts/CORTEX.prompt.md`. CORTEX loads, Intent Router activates, and onboarding begins!

**After Module 1 (copy_cortex_entry_points):** Entry points are also in your app's `.github/` folder for standard location convenience. Both locations work!

---

## 🆘 Troubleshooting

**Onboarding fails:**
- Check Python 3.10+ installed: `python --version`
- Check Git installed: `git --version`
- Verify CORTEX copied to `cortex/` folder: `ls cortex/`
- Try manual setup above

**Copilot doesn't recognize CORTEX:**
- Ensure `cortex/.github/prompts/CORTEX.prompt.md` exists
- Restart VS Code
- Try: `help` to see available commands

**Entry points not found:**
- Check workspace root: VS Code should be opened at application root, not inside `cortex/`
- Copilot searches recursively, will find `cortex/.github/prompts/CORTEX.prompt.md`

**Questions?**
- Check documentation: `cortex/prompts/shared/`
- GitHub: https://github.com/asifhussain60/CORTEX

---

**Version:** 2.0.0  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary
