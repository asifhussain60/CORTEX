GIT_ISOLATION_ENFORCEMENT: Core CORTEX Principle

CORTEX operates as a SEPARATE cognitive layer:

❌ NEVER DO THIS:
UserApp/
├── src/                    # User's application code
├── cortex-brain/           # ❌ WRONG - Don't commit brain!
├── src/tier0/              # ❌ WRONG - Don't copy CORTEX code!
├── src/cortex_agents/      # ❌ WRONG - Keep CORTEX separate!
└── .git/

✅ CORRECT SETUP:
UserApp/
├── src/                    # User's application code
├── team-knowledge/         # ✅ OK - Exported YAML patterns
├── .gitignore              # ✅ Must include: cortex-brain/
└── .git/

CORTEX/ (separate repo)
├── src/tier0/              # ✅ CORTEX framework code
├── src/cortex_agents/      # ✅ Agent system
├── cortex-brain/           # ✅ Local brain (not in git)
└── .git/

Why This Matters:
1. Separation of Concerns: Framework vs. Application
2. Licensing: CORTEX proprietary, user code their own license
3. Updates: CORTEX updates don't pollute user repos
4. Security: Brain knowledge stays local, never exposed
5. Clarity: Clear boundary between "your code" and "framework"

Git Hooks (setup during init):
- pre-commit: Scans for CORTEX paths, blocks commit if found
- pre-push: Double-check no CORTEX code being pushed

Exception: team-knowledge/ YAML exports allowed (knowledge sharing)
