# CORTEX Entry Point Archive - 2025-11-09

## What Happened?

CORTEX entry point has been migrated from `prompts/user/cortex.md` to GitHub Copilot conventions.

## New Locations

- **Entry Point:** `.github/prompts/CORTEX.prompt.md` - Use `/CORTEX` command
- **Baseline Context:** `.github/copilot-instructions.md` - Auto-loaded for all chats
- **VS Code Setting:** `.vscode/settings.json` - Enables prompt files

## Why Archive These Files?

These files were the original CORTEX entry points but have been superseded by the GitHub Copilot integration:

1. **cortex.md** - Original universal entry point (now `.github/prompts/CORTEX.prompt.md`)
2. **cortex-slim-test.md** - Testing version (no longer needed)
3. **cortex-NEW-SLIM.md** - Experimental version (superseded)
4. **cortex-gemini-image-prompts.md** - Image generation prompts (moved to docs/)
5. **the-awakening-of-cortex.md** - Story (moved to docs/story/)

## Files Preserved for Reference

All archived files are kept for reference and historical purposes. They contain valuable documentation and evolution history.

## Migration Benefits

1. **Simpler entry:** `/CORTEX` instead of `#file:prompts/user/cortex.md`
2. **Auto-loaded context:** `.github/copilot-instructions.md` loaded automatically
3. **Better discoverability:** GitHub Copilot recognizes `.github/` conventions
4. **Cross-platform:** Works on Mac, Windows, Linux without path issues
5. **Plugin extensibility preserved:** Command registry enables auto-discovery

## Restored Entry Points

If needed, these files can be restored. However, the new GitHub Copilot integration is recommended.

---

*Archived: 2025-11-09*  
*Reason: GitHub Copilot Integration (Mode 2 - Embedded CORTEX)*  
*See: cortex-brain/cortex-2.0-design/39-github-copilot-integration-complete.md*
