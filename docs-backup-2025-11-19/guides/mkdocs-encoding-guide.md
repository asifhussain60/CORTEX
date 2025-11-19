# MkDocs UTF-8 Encoding - Developer Guide

## For New Developers

### Quick Start
If you see garbled text like `ΓÇö` instead of `—`:

```powershell
# Fix it automatically
python scripts/fix_garbled_source_files.py
```

### Setup Your Environment

1. **VS Code Settings** (Recommended)
   - Copy `.vscode/settings.recommended.json` to `.vscode/settings.json`
   - Or add encoding settings manually (see below)

2. **Build MkDocs with UTF-8**
   ```powershell
   # Use our helper script
   .\scripts\build-mkdocs-utf8.ps1
   
   # Or manually
   $env:PYTHONUTF8='1'
   mkdocs build --clean
   ```

## VS Code Configuration

### Automatic (Recommended)
```powershell
# Copy recommended settings
Copy-Item .vscode/settings.recommended.json .vscode/settings.json
```

### Manual Setup
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

## How to Check File Encoding

### In VS Code
1. Open a markdown file
2. Look at bottom-right corner of editor
3. Should say "UTF-8"
4. If it says "Windows-1252" or "ANSI":
   - Click on it
   - Select "Save with Encoding"
   - Choose "UTF-8"

### From Command Line
```powershell
# Check file encoding
python -c "import chardet; print(chardet.detect(open('docs/some-file.md', 'rb').read()))"
```

## Common Issues & Solutions

### Issue: Garbled text in browser
**Symptoms**: `ΓÇö`, `Γ£à`, `≡ƒôï` instead of `—`, `✅`, `📋`

**Solution**:
```powershell
python scripts/fix_garbled_source_files.py
mkdocs build --clean
```

### Issue: "UnicodeDecodeError" during build
**Symptoms**: Python crashes reading markdown files

**Solution**:
```powershell
# Set UTF-8 environment
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'

# Then rebuild
mkdocs build --clean
```

### Issue: Git shows massive diffs
**Symptoms**: Entire file shows as changed (line ending or encoding issue)

**Solution**:
```powershell
# Normalize line endings
git add --renormalize .
git commit -m "Normalize line endings"
```

## Testing

### Run All Encoding Tests
```powershell
# Note: May need to fix platform module conflict first
python tests/test_mkdocs_encoding.py -v
```

### Quick Manual Test
```powershell
# Build and check one file
mkdocs build --clean
python -c "from pathlib import Path; print('ΓÇö' in Path('site/diagrams/story/The-CORTEX-Story/index.html').read_text(encoding='utf-8'))"
# Should print: False (no garbled text)
```

## Git Configuration

Add to `.gitattributes`:
```gitattributes
# Ensure UTF-8 encoding for text files
*.md text eol=lf encoding=utf-8
*.html text eol=lf encoding=utf-8
*.py text eol=lf encoding=utf-8
*.yml text eol=lf encoding=utf-8
*.json text eol=lf encoding=utf-8

# Binary files
*.png binary
*.jpg binary
*.gif binary
```

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `fix_garbled_source_files.py` | Fix garbled UTF-8 in markdown files |
| `fix_mkdocs_encoding.py` | Clean, build, and verify encoding |
| `build-mkdocs-utf8.ps1` | PowerShell wrapper for UTF-8 build |
| `set-utf8-env.ps1` | Set UTF-8 environment variables |

## Best Practices

### ✅ DO
- Always save files with UTF-8 encoding
- Use `scripts/build-mkdocs-utf8.ps1` for builds
- Run encoding tests before committing
- Check encoding status in VS Code status bar

### ❌ DON'T
- Don't save files with Windows-1252 or ANSI encoding
- Don't copy-paste from Word or Notepad without checking encoding
- Don't commit without testing in browser first
- Don't skip the UTF-8 environment variables on Windows

## Troubleshooting Checklist

- [ ] File saved as UTF-8? (check VS Code status bar)
- [ ] PYTHONUTF8=1 set? (run `$env:PYTHONUTF8`)
- [ ] MkDocs build clean? (no warnings about encoding)
- [ ] Browser shows correct characters? (test locally)
- [ ] Tests passing? (run test_mkdocs_encoding.py)

## Need Help?

1. **Check the encoding**: `.vscode/settings.json` has `"files.encoding": "utf8"`
2. **Run the fix script**: `python scripts/fix_garbled_source_files.py`
3. **Rebuild clean**: `mkdocs build --clean`
4. **Test**: Open `site/index.html` in browser
5. **Still broken?**: Check `docs/MKDOCS-ENCODING-FIX-REPORT.md` for detailed diagnosis

## References

- [Python UTF-8 Mode](https://peps.python.org/pep-0540/)
- [MkDocs Configuration](https://www.mkdocs.org/user-guide/configuration/)
- [UTF-8 Everywhere Manifesto](http://utf8everywhere.org/)
