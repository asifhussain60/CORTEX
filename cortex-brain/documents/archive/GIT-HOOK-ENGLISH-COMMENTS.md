# Git Hook: English-Only Code Comments

**Plan:** CORTEX-SETUP-001  
**Task:** Phase 3, Task 3.6  
**Version:** 1.5  
**Purpose:** Enforce English-only comments in codebase while allowing multilingual user responses

---

## 🎯 Overview

A pre-commit git hook that validates all Python code comments are written in English. This maintains global codebase maintainability while CORTEX responses can be in any of 12 supported languages.

---

## 🔒 Rationale

### Why English-Only Code?

**Global Maintainability:**
- Code is read 10x more than written
- International contributors need to understand comments
- English is the universal programming language standard
- Reduces onboarding friction for new developers

**Separation of Concerns:**
- **Code/Comments:** English (for developers)
- **User Responses:** 12 languages (for end users via templates)
- Clear boundary prevents language mixing

**Industry Standard:**
- Major open-source projects enforce English comments
- Python PEPs written in English
- Stack Overflow, GitHub discussions primarily English
- Technical documentation universally English

---

## 🔧 Implementation

### Hook Type: Pre-Commit (Blocking)

**Installation:**
- Automatic during CORTEX setup
- Script: `scripts/install_git_hooks.py`
- Generated file: `.git/hooks/pre-commit`

### Validation Logic

**1. Extract Comments from Staged Python Files:**
```python
# Comment types detected:
# 1. Single-line comments starting with #
"""
2. Docstrings in triple quotes
"""
'''
3. Multi-line docstrings
'''
```

**2. Language Detection:**
- Library: `langdetect` (Google's language detection)
- Threshold: 95% confidence for non-English detection
- Ignore: Single words, URLs, code snippets, variable names

**3. Blocking Behavior:**
- If non-English comment detected → Block commit
- Display file, line number, detected language
- Suggest translation or `--no-verify` override

---

## 📋 Usage Examples

### Scenario 1: English Comments (Pass ✅)

```python
# src/setup/modules/user_profile_module.py

def ask_language_preference():
    """
    Ask user for their preferred response language.
    
    Supports 12 languages: EN, ES, FR, DE, PT, ZH, JA, KO, HI, AR, RU, IT.
    User-facing responses will be in selected language.
    
    Returns:
        str: ISO 639-1 language code (e.g., 'en', 'es', 'fr')
    """
    print("What's your preferred response language?")
    # Display options with native script
    options = {
        "EN": "English",
        "ES": "Español",
        "FR": "Français"
    }
    return input("→ [EN/ES/FR/...]: ").lower()
```

**Git Commit:**
```bash
$ git add src/setup/modules/user_profile_module.py
$ git commit -m "Add language preference question"

✅ Pre-commit validation passed
[main abc1234] Add language preference question
```

---

### Scenario 2: Non-English Comments (Blocked ❌)

```python
# src/setup/modules/user_profile_module.py

def ask_language_preference():
    """
    Pregunta al usuario por su idioma preferido.  # Spanish
    
    Soporta 12 idiomas.
    """
    print("What's your preferred response language?")
    # Usuario selecciona su preferencia  # Spanish
    return input("→ [EN/ES/FR/...]: ").lower()
```

**Git Commit:**
```bash
$ git add src/setup/modules/user_profile_module.py
$ git commit -m "Add language preference question"

❌ Pre-commit validation failed: Non-English comments detected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
File: src/setup/modules/user_profile_module.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Line 4-6 (Docstring): Spanish detected
    """
    Pregunta al usuario por su idioma preferido.
    Soporta 12 idiomas.
    """

Line 9 (Comment): Spanish detected
    # Usuario selecciona su preferencia

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CORTEX codebase requires English-only comments for global maintainability.
User-facing responses support 12 languages via response templates.

To fix:
1. Translate comments to English
2. Or bypass: git commit --no-verify (exceptional cases only)

Suggested English translations:
Line 4-6: "Ask user for their preferred language. Supports 12 languages."
Line 9: "User selects their preference"
```

---

## 🛠️ Technical Details

### Comment Extraction

**Python AST Parsing:**
```python
import ast
import tokenize

def extract_comments(file_path):
    comments = []
    
    # 1. Extract inline comments with tokenize
    with open(file_path, 'rb') as f:
        tokens = tokenize.tokenize(f.readline)
        for token in tokens:
            if token.type == tokenize.COMMENT:
                comments.append({
                    'type': 'inline',
                    'line': token.start[0],
                    'text': token.string
                })
    
    # 2. Extract docstrings with AST
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                docstring = ast.get_docstring(node)
                if docstring:
                    comments.append({
                        'type': 'docstring',
                        'line': node.lineno,
                        'text': docstring
                    })
    
    return comments
```

### Language Detection

**Using langdetect:**
```python
from langdetect import detect, LangDetectException

def is_english(text):
    """
    Detect if text is in English.
    
    Returns:
        bool: True if English, False if other language
    """
    # Skip if too short (single words, code)
    if len(text.split()) < 3:
        return True
    
    # Skip if contains high ratio of code patterns
    if is_code_like(text):
        return True
    
    try:
        language = detect(text)
        return language == 'en'
    except LangDetectException:
        # Unclear language, assume English
        return True

def is_code_like(text):
    """Check if text looks like code rather than natural language."""
    code_indicators = [
        '(',  # Function calls
        ')',
        '=',  # Assignments
        '{',  # Dictionaries/blocks
        '}',
        '[',  # Lists
        ']',
        '->',  # Type hints
        '::',  # Namespaces
    ]
    
    # If >30% of characters are code indicators, it's likely code
    code_char_count = sum(text.count(indicator) for indicator in code_indicators)
    return code_char_count / len(text) > 0.3
```

### Hook Installation

**Auto-install during setup:**
```python
# scripts/install_git_hooks.py

def install_pre_commit_hook():
    """Install pre-commit hook for comment validation."""
    hook_path = Path('.git/hooks/pre-commit')
    
    # Generate hook script
    hook_content = """#!/usr/bin/env python3
import sys
from src.utils.comment_language_validator import validate_staged_files

if __name__ == '__main__':
    success, violations = validate_staged_files()
    
    if not success:
        print("❌ Pre-commit validation failed: Non-English comments detected")
        print()
        for violation in violations:
            print(f"File: {violation['file']}")
            print(f"Line {violation['line']}: {violation['language']} detected")
            print(f"  {violation['text']}")
            print()
        print("CORTEX codebase requires English-only comments.")
        print("To bypass: git commit --no-verify")
        sys.exit(1)
    
    print("✅ Pre-commit validation passed")
    sys.exit(0)
"""
    
    # Write and make executable
    hook_path.write_text(hook_content)
    hook_path.chmod(0o755)
```

---

## 🚫 What Gets Validated

### ✅ Validated (Must be English)

1. **Inline Comments:**
   ```python
   # This is validated
   x = 5  # This too
   ```

2. **Docstrings:**
   ```python
   def function():
       """This docstring is validated."""
       pass
   ```

3. **Module-level Comments:**
   ```python
   """
   Module description here - validated
   """
   ```

4. **Multi-line Comments:**
   ```python
   # This is a long explanation
   # that spans multiple lines
   # and is all validated
   ```

### ❌ Ignored (Not Validated)

1. **String Literals in Code:**
   ```python
   # Not validated - user-facing messages can be multilingual
   message = "Bienvenido a CORTEX"
   ```

2. **Test Data:**
   ```python
   # Not validated - test data can contain any language
   test_inputs = ["Hola", "Bonjour", "こんにちは"]
   ```

3. **Variable Names:**
   ```python
   # Not validated - though English preferred
   usuario_nombre = "John"
   ```

4. **URLs and Paths:**
   ```python
   # Not validated - technical paths
   url = "https://example.com/español"
   ```

---

## 🔓 Bypass Options

### When to Use `--no-verify`

**Legitimate Cases:**
1. Example code demonstrating multilingual support
2. Test files with intentional non-English content
3. Documentation examples showing translation
4. Legacy code migration (temporary)

**Usage:**
```bash
git commit --no-verify -m "Add multilingual test fixtures"
```

**Warning:** Use sparingly. Every bypass should be justified in commit message.

---

## 📊 Validation Examples

### False Positive Handling

**Code with Technical Terms (Pass ✅):**
```python
# Initialize DataFrame with pandas
df = pd.DataFrame()

# Use OAuth2 authentication
auth = OAuth2Session()

# Parse JSON response
data = json.loads(response)
```

**Reason:** Technical terms are English, not natural language requiring validation.

**Single-Word Comments (Pass ✅):**
```python
# TODO
# FIXME
# NOTE
# WARNING
```

**Reason:** Too short for reliable language detection.

**Code-Heavy Comments (Pass ✅):**
```python
# Call get_user(id=123) -> returns {"name": "John", "age": 30}
```

**Reason:** High ratio of code syntax, not natural language.

---

## 🎯 Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| English comment enforcement | 100% | All commits validated |
| False positive rate | <5% | Technical terms not flagged |
| False negative rate | <1% | Non-English comments caught |
| Detection accuracy | 95%+ | Correct language identification |
| Performance | <2s | Validation time for typical commit |

---

## 🔍 Testing Strategy

**Test Cases:**

1. **English Comments (Should Pass):**
   - Simple comments
   - Technical terms
   - Code-heavy comments
   - URLs and paths

2. **Non-English Comments (Should Fail):**
   - Spanish comments
   - French docstrings
   - Chinese comments
   - Arabic comments (RTL)

3. **Edge Cases:**
   - Empty comments
   - Single-word comments
   - Mixed language (English + Spanish)
   - Code with non-ASCII characters

4. **Performance:**
   - Large files (1000+ lines)
   - Many staged files (50+)
   - Minimal delay (<2s)

---

## 📚 Dependencies

**Required Libraries:**
```python
# requirements.txt
langdetect==1.0.9  # Language detection
```

**Installation:**
```bash
pip install langdetect
```

---

## 🔄 Integration with CORTEX Setup

**Automatic Installation:**

1. User runs: `python -m src.orchestrators.setup_orchestrator`
2. Setup orchestrator calls: `scripts/install_git_hooks.py`
3. Pre-commit hook generated in `.git/hooks/pre-commit`
4. Hook automatically runs on every commit

**Manual Installation:**
```bash
python scripts/install_git_hooks.py
```

**Verification:**
```bash
# Check hook is installed
ls -la .git/hooks/pre-commit

# Test hook
git add some_file.py
git commit -m "Test commit"
# Hook runs automatically
```

---

## ✅ Acceptance Criteria (From Plan)

- [ ] Git hook installed automatically during setup
- [ ] Non-English comments detected with 95%+ accuracy
- [ ] False positive rate <5% (technical terms pass)
- [ ] Clear error messages with file:line locations
- [ ] Bypass option available (`--no-verify`)
- [ ] Hook executable and properly configured
- [ ] 10+ test cases covering all scenarios
- [ ] Documentation explains usage and bypass

---

## 🌍 Relationship to Multilingual Support

**Clear Separation:**

| Context | Language | Enforcement |
|---------|----------|-------------|
| **Code & Comments** | English only | Git hook (this) |
| **User Responses** | 12 languages | Response templates |
| **String Literals** | Any language | No restriction |
| **Test Data** | Any language | No restriction |

**Rationale:**
- Code is for developers (global team needs English)
- Responses are for users (localized to their language)
- Clear boundary prevents confusion and maintains quality

---

**Related Files:**
- Plan: `cortex-brain/documents/planning/shared-environment-default-activation.md` (Phase 3, Task 3.6)
- Multilingual Summary: `cortex-brain/documents/planning/MULTILINGUAL-SUPPORT-SUMMARY.md`
- Implementation: `src/utils/comment_language_validator.py` (to be created)

**Next Action:** Implement in Phase 3 alongside multilingual response templates
