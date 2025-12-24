CORTEX_PROMPT_FILE_PROTECTION: Entry Point Stability

CORTEX.prompt.md is the SINGLE entry point for GitHub Copilot Chat.
Its exact filename (.github/prompts/CORTEX.prompt.md) is:
- Hardcoded in GitHub Copilot discovery
- Referenced throughout all documentation
- Critical for `/CORTEX` command to work

Why This Protection Matters:

1. GitHub Copilot Discovery:
   Copilot looks for .github/prompts/CORTEX.prompt.md
   ANY rename → integration breaks completely
   No fallback mechanism exists

2. Documentation References:
   - README.md references CORTEX.prompt.md
   - Setup guides reference CORTEX.prompt.md
   - Quick start tutorials reference CORTEX.prompt.md
   All references break if renamed

3. User Confusion:
   Multiple prompt files create:
   - "Which one do I use?"
   - "Is cortex-lite the new version?"
   - Cognitive overhead increases

4. Git History Fragmentation:
   Rename creates new file in git
   Old file shows as deleted
   History split across filenames

Safe Update Procedure:

Step 1: Create Temporary File
```
.github/prompts/temp-cortex-update.md
```
- Contains new optimized content
- Reviewable before applying
- Acts as backup if issues occur

Step 2: Generate Optimized Content
- Apply token optimizations
- Restructure sections
- Update documentation references
- Add new features

Step 3: Clear Original (Atomic Update)
```python
# DELETE ALL content
Path('.github/prompts/CORTEX.prompt.md').write_text('')
```
- Prevents partial updates
- Ensures clean slate
- No merge conflicts

Step 4: Copy Complete Instructions
```python
content = Path('temp-cortex-update.md').read_text()
Path('CORTEX.prompt.md').write_text(content)
```
- Atomic replacement
- No partial content risk

Step 5: Delete Temporary File
```python
Path('temp-cortex-update.md').unlink()
```
- Clean up
- Single source of truth

Benefits:
- Filename NEVER changes (stability)
- Atomic updates (no half-updated states)
- Review capability (temp file inspection)
- Rollback support (restore from temp)
- Clean git history (single file evolution)

Real Incident Pattern Prevented:
Developer: "I'll create CORTEX-lite.prompt.md"
Result: Two prompt files coexist
User confusion: "Which is current?"
Maintenance nightmare: Multiple files diverge

This rule BLOCKS any rename attempt.
Exception: Temporary files for update workflow ARE encouraged.
