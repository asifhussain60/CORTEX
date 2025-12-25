🚨 CORTEX.prompt.md PROTECTION VIOLATION

Attempted: '{operation}'

CRITICAL: CORTEX.prompt.md is the GitHub Copilot integration entry point!

❌ NEVER:
- Rename to cortex-lite.prompt.md
- Rename to cortex-backup.prompt.md  
- Rename to cortex-fixed.prompt.md
- Add ANY prefix or suffix
- Edit directly (risky, no rollback)

✅ SAFE UPDATE PROCEDURE:
1. Create: .github/prompts/temp-cortex-update.md
2. Generate optimized content in temp file
3. DELETE ALL content of CORTEX.prompt.md
4. Copy complete instructions from temp
5. Delete temp-cortex-update.md

Why? Filename stability + Atomic updates + Rollback capability
