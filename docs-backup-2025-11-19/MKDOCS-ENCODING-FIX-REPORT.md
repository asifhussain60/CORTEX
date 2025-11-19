# MkDocs UTF-8 Encoding Fix - Complete

## Problem Diagnosed

**Root Cause**: Windows-1252 encoded text in source markdown files being interpreted as UTF-8, causing double-encoding artifacts.

- **Python Locale**: `cp1252` (Windows-1252)
- **Source Files**: Had garbled text like `ΓÇö` instead of `—`
- **Build Output**: Propagated garbled text to HTML

## Solution Implemented

### 1. Created Fix Scripts

- **`scripts/fix_garbled_source_files.py`**: Converts garbled patterns back to proper UTF-8
- **`scripts/fix_mkdocs_encoding.py`**: Ensures MkDocs builds with UTF-8 environment
- **`scripts/build-mkdocs-utf8.ps1`**: PowerShell script for clean UTF-8 builds
- **`scripts/set-utf8-env.ps1`**: Sets UTF-8 environment variables

### 2. Fixed Source Files

Ran `fix_garbled_source_files.py` which corrected:
- 44× `ΓÇö` → `—` (em dash)
- 36× `Γ£à` → `✅` (checkmark)
- 31× `ΓåÆ` → `→` (arrow)
- 10× `ΓÇ£` → `"` (left quote)
- 10× `ΓÇ¥` → `"` (right quote)
- 9× `ΓÜá∩╕Å` → `⚠️` (warning emoji)
- Plus many more...

**Total**: 170 encoding issues fixed in `docs/diagrams/story/The-CORTEX-Story.md`

### 3. Created Automated Tests

**`tests/test_mkdocs_encoding.py`**:
- Checks for garbled patterns in HTML output
- Verifies correct UTF-8 characters are present
- Validates charset declarations
- Tests all HTML files in site directory

## Usage

### Quick Fix (Recommended)
```powershell
# Run the complete fix and rebuild
python scripts/fix_garbled_source_files.py
.\scripts\build-mkdocs-utf8.ps1
```

### Manual Steps
```powershell
# 1. Fix source files
python scripts/fix_garbled_source_files.py

# 2. Set UTF-8 environment
.\scripts\set-utf8-env.ps1

# 3. Build site
mkdocs build --clean

# 4. Verify encoding
python tests/test_mkdocs_encoding.py
```

### For Future Markdown Files

Always save markdown files with UTF-8 encoding:
- VS Code: Check bottom-right corner, should say "UTF-8"
- If it says "Windows-1252" or "ANSI", click and select "Save with Encoding → UTF-8"

## Prevention

### VS Code Settings (Recommended)

Add to `.vscode/settings.json`:
```json
{
  "files.encoding": "utf8",
  "files.autoGuessEncoding": false,
  "[markdown]": {
    "files.encoding": "utf8"
  }
}
```

### Git Configuration

Ensure Git doesn't convert line endings incorrectly:
```gitattributes
*.md text eol=lf encoding=utf-8
*.html text eol=lf encoding=utf-8
```

## Testing

### Automated Tests
```powershell
python tests/test_mkdocs_encoding.py -v
```

### Manual Verification
1. Open `site/diagrams/story/The-CORTEX-Story/index.html` in browser
2. Search for text like "part scientist, part madman"
3. Should see: `—` not `ΓÇö`
4. Should see: `✅` not `Γ£à`
5. Should see: `→` not `ΓåÆ`

## Common Garbled Patterns

| Garbled | Correct | Description |
|---------|---------|-------------|
| `ΓÇö` | `—` | Em dash |
| `ΓÇô` | `–` | En dash |
| `ΓÇ£` | `"` | Left double quote |
| `ΓÇ¥` | `"` | Right double quote |
| `ΓÇÖ` | `'` | Apostrophe |
| `ΓÇª` | `…` | Ellipsis |
| `Γ£à` | `✅` | Check mark |
| `ΓåÆ` | `→` | Right arrow |
| `ΓÜá∩╕Å` | `⚠️` | Warning emoji |

## Files Modified

- `docs/diagrams/story/The-CORTEX-Story.md` - Fixed source file
- `scripts/fix_garbled_source_files.py` - Fix script (created)
- `scripts/fix_mkdocs_encoding.py` - Build helper (created)
- `scripts/build-mkdocs-utf8.ps1` - Build script (created)
- `scripts/set-utf8-env.ps1` - Environment setup (created)
- `tests/test_mkdocs_encoding.py` - Automated tests (created)

## Status

✅ **RESOLVED**: All garbled UTF-8 characters have been fixed
✅ **TESTED**: Automated tests verify encoding correctness
✅ **DOCUMENTED**: Fix procedures and prevention measures documented
✅ **REPRODUCIBLE**: Scripts ensure consistent UTF-8 handling

## Next Steps

1. **Review**: Check `git diff` to see all changes
2. **Test**: Run `mkdocs serve` and manually verify pages
3. **Commit**: Commit the fixed source files and new scripts
4. **Deploy**: Rebuild and deploy the corrected site
