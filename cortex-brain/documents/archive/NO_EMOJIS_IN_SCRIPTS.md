NO_EMOJIS_IN_SCRIPTS: Code Quality Standard

Why Emojis Don't Belong in Scripts:

1. Encoding Issues:
   - UTF-8 encoding not universal in all environments
   - PowerShell ISE may not render correctly
   - Windows cmd.exe has encoding problems
   - Remote SSH sessions may lose emojis

2. Terminal Compatibility:
   - Some terminals don't support Unicode emojis
   - CI/CD logs may show broken characters
   - Legacy systems show question marks
   - Screen readers struggle with emojis

3. Professional Standards:
   - Scripts are code, not social media
   - Emojis reduce professional appearance
   - Industry standard: plain text markers
   - Easier to grep/search logs

4. Copy/Paste Problems:
   - Email clients may corrupt emojis
   - Documentation tools may strip emojis
   - Version control diffs show weird bytes
   - Stack Overflow code samples break

What to Use Instead:

❌ Emoji-Based:
```python
print("✅ Test passed")
print("❌ Test failed")
print("⚠️ Warning detected")
```

✅ Plain Text:
```python
print("[OK] Test passed")
print("[FAIL] Test failed")
print("[WARN] Warning detected")
```

✅ Logging Levels:
```python
logger.info("Test passed")
logger.error("Test failed")
logger.warning("Warning detected")
```

✅ ASCII Symbols:
```python
print("+ Test passed")
print("- Test failed")
print("! Warning detected")
```

Allowed Emoji Usage:
- Documentation (README.md, guides)
- User-facing messages (GitHub Copilot Chat responses)
- Markdown files (story.md, setup-guide.md)
- Comments in code (sparingly, for clarity)

Not Allowed:
- Python scripts (.py)
- PowerShell scripts (.ps1)
- Bash scripts (.sh)
- Batch files (.bat, .cmd)
- Any executable script files

Example Violation:
```python
# ❌ BAD
def run_tests():
    print("🧪 Running tests...")
    if all_pass:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")

# ✅ GOOD
def run_tests():
    print("[TEST] Running tests...")
    if all_pass:
        print("[OK] All tests passed!")
    else:
        print("[FAIL] Some tests failed!")
```

This maintains code professionalism and ensures scripts work
universally across all platforms and environments.
