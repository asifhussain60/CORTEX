# Code Language Enforcement - Governance Enhancement

**Plan:** CORTEX-SETUP-001  
**Version:** 1.4 → 1.5  
**Enhancement:** Code language enforcement (English-only code/comments)  
**Added:** 2025-12-03

---

## 🎯 Purpose

Ensure all code and comments remain in **English** across the CORTEX codebase, even though CORTEX supports 12 languages for user-facing responses. This maintains codebase consistency, readability, and maintainability.

---

## 📋 Policy Statement

**Code and Comments: English Only**

✅ **Allowed:**
- Code in English (variable names, function names, class names)
- Comments in English (inline, block, docstrings)
- Technical terms in English (API, JSON, REST, etc.)
- User-facing string literals in any language (for multilingual UX)

❌ **Not Allowed:**
- Code comments in Spanish, French, Chinese, etc.
- Variable names in non-Latin scripts
- Docstrings in non-English languages
- Mixed-language comments

**Rationale:**
- **Maintainability:** All developers can read and understand code
- **Code Review:** Reviewers globally can provide feedback
- **Documentation:** Consistent technical communication
- **Team Scalability:** New developers onboard faster
- **Separation of Concerns:** Multilingual UX (responses) ≠ multilingual code

---

## 🔧 Implementation

### Phase 3: Task 3.6 (NEW)

**Create Code Language Enforcement Hook**

**Detection Strategy:**
```python
# src/utils/code_language_validator.py

def detect_non_english_comments(file_path: str) -> List[Violation]:
    """
    Scan code file for non-English comments.
    Returns violations with line numbers and detected language.
    """
    violations = []
    
    # Extract comments based on file type
    comments = extract_comments(file_path)
    
    for line_num, comment in comments:
        if contains_non_latin_script(comment):
            language = detect_language(comment)
            violations.append(Violation(
                file=file_path,
                line=line_num,
                text=comment,
                detected_language=language
            ))
    
    return violations

def contains_non_latin_script(text: str) -> bool:
    """
    Detect non-Latin Unicode ranges.
    """
    ranges = {
        'CJK': (0x4E00, 0x9FFF),           # Chinese, Japanese, Korean
        'Arabic': (0x0600, 0x06FF),        # Arabic
        'Cyrillic': (0x0400, 0x04FF),      # Russian
        'Devanagari': (0x0900, 0x097F),    # Hindi
        'Hangul': (0xAC00, 0xD7AF),        # Korean
        'Hiragana': (0x3040, 0x309F),      # Japanese
        'Katakana': (0x30A0, 0x30FF),      # Japanese
    }
    
    for char in text:
        code_point = ord(char)
        for name, (start, end) in ranges.items():
            if start <= code_point <= end:
                return True
    return False
```

**File Type Support:**
- `.py` - Python (inline `#`, block `"""`, docstrings)
- `.js` / `.ts` - JavaScript/TypeScript (inline `//`, block `/* */`, JSDoc)
- `.java` - Java (inline `//`, block `/* */`, Javadoc)
- `.cpp` / `.c` - C/C++ (inline `//`, block `/* */`)
- `.go` - Go (inline `//`, block `/* */`)
- `.rs` - Rust (inline `//`, block `/* */`)

**Exemptions:**
```python
EXEMPT_FILES = [
    'cortex-brain/response-templates.yaml',     # Contains translations
    'src/response_templates/translations.py',   # Translation dictionary
    'tests/fixtures/multilingual_test_data.py', # Test data
]

EXEMPT_PATTERNS = [
    r'.*\.po$',      # Translation files
    r'.*\.pot$',     # Translation templates
    r'.*i18n.*',     # Internationalization files
]

def is_exempt(file_path: str) -> bool:
    """Check if file is exempt from language enforcement."""
    if file_path in EXEMPT_FILES:
        return True
    for pattern in EXEMPT_PATTERNS:
        if re.match(pattern, file_path):
            return True
    return False
```

---

## 🚫 Pre-Commit Hook

### Phase 8: Task 8.7 (UPDATED)

**Unified Pre-Commit Hook (Filename + Code Language)**

```bash
#!/bin/bash
# .git/hooks/pre-commit
# CORTEX Pre-Commit Governance Hook

set -e

echo "🔍 CORTEX Pre-Commit Checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check 1: Filename Length (WARNING)
echo "📏 Checking filename lengths..."
python src/utils/filename_validator.py --staged-files
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Long filenames detected (non-blocking)"
fi

# Check 2: Code Language (BLOCKING)
echo "🌐 Checking code language..."
python src/utils/code_language_validator.py --staged-files
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ COMMIT BLOCKED: Non-English code/comments detected"
    echo ""
    echo "Policy: All code and comments must be in English."
    echo "Reason: Maintainability, code review efficiency, team scalability."
    echo ""
    echo "Note: Multilingual responses are supported via user profile."
    echo "      This rule applies to code only, not user-facing strings."
    echo ""
    echo "To fix:"
    echo "  1. Translate comments to English"
    echo "  2. Check exemptions: response-templates.yaml, translations.py"
    echo ""
    echo "To bypass (not recommended): git commit --no-verify"
    exit 1
fi

echo ""
echo "✅ All pre-commit checks passed"
exit 0
```

**Installation:**
```bash
# scripts/install_git_hooks.sh

#!/bin/bash
# Install CORTEX git hooks

HOOK_DIR=".git/hooks"
HOOK_FILE="$HOOK_DIR/pre-commit"

# Create hook directory if not exists
mkdir -p "$HOOK_DIR"

# Copy pre-commit hook
cp scripts/git-hooks/pre-commit "$HOOK_FILE"
chmod +x "$HOOK_FILE"

echo "✅ Git hooks installed"
echo "   - Filename length validation (warning)"
echo "   - Code language enforcement (blocking)"
```

**Auto-Install During Setup:**
```python
# src/setup/modules/git_hooks_module.py

class GitHooksModule(BaseSetupModule):
    def execute(self, context: SetupContext) -> SetupResult:
        """Install git hooks during CORTEX setup."""
        hook_script = Path("scripts/install_git_hooks.sh")
        
        if not context.project_root / ".git":
            return SetupResult(
                success=True,
                message="Not a git repository, skipping git hooks"
            )
        
        subprocess.run(["bash", str(hook_script)], check=True)
        
        return SetupResult(
            success=True,
            message="Git hooks installed successfully"
        )
```

---

## 📊 Detection Examples

### Example 1: Python with Spanish Comments

**File:** `src/main.py`

```python
# Función principal de la aplicación
def main():
    # Inicializar el sistema
    system = System()
    system.start()
```

**Violation Report:**
```
❌ Non-English comments detected in src/main.py

Line 1: # Función principal de la aplicación
  Detected: Spanish (ES)
  Suggestion: # Main application function

Line 3: # Inicializar el sistema
  Detected: Spanish (ES)
  Suggestion: # Initialize the system

Fix these comments or use --no-verify to bypass (not recommended)
```

### Example 2: JavaScript with Chinese Comments

**File:** `src/app.js`

```javascript
// 初始化应用程序
function initApp() {
    // 设置配置
    const config = loadConfig();
    return config;
}
```

**Violation Report:**
```
❌ Non-English comments detected in src/app.js

Line 1: // 初始化应用程序
  Detected: Chinese (ZH)
  Suggestion: // Initialize application

Line 3: // 设置配置
  Detected: Chinese (ZH)
  Suggestion: // Setup configuration
```

### Example 3: Valid Multilingual String Literal

**File:** `src/messages.py`

```python
def get_welcome_message(language: str) -> str:
    """Get welcome message in user's language."""
    messages = {
        "en": "Welcome to CORTEX",
        "es": "Bienvenido a CORTEX",      # ✅ Allowed (string literal)
        "fr": "Bienvenue à CORTEX",       # ✅ Allowed (string literal)
        "zh": "欢迎使用 CORTEX",            # ✅ Allowed (string literal)
    }
    return messages.get(language, messages["en"])
```

**No Violations:** String literals are exempt (user-facing content)

---

## 🎯 Tier 0 Governance Rule

**Added to `cortex-brain/brain-protection-rules.yaml`:**

```yaml
- rule_id: "CODE_LANGUAGE_ENFORCEMENT"
  name: "Code Language Enforcement"
  severity: "blocked"
  layer: "code_quality"
  description: |
    All code and comments must be in English. This ensures:
    - Codebase maintainability (all developers can read)
    - Code review efficiency (universal understanding)
    - Documentation consistency (English technical standard)
    - Team scalability (new developers onboard faster)
    
    Note: User-facing strings can be multilingual. This rule applies
    to code structure and developer-facing comments only.
  
  rationale: |
    CORTEX supports 12 languages for USER RESPONSES, not code.
    Separation of concerns:
    - Multilingual UX: Response templates in 12 languages ✅
    - Multilingual Code: Not allowed ❌
    
    English is the universal language of programming. Mixing languages
    in code creates maintenance burden and excludes developers.
  
  scope:
    - All Python files (.py)
    - All JavaScript/TypeScript files (.js, .ts)
    - All Java files (.java)
    - All C/C++ files (.cpp, .c, .h)
    - All Go files (.go)
    - All Rust files (.rs)
  
  exemptions:
    - cortex-brain/response-templates.yaml (contains translations)
    - src/response_templates/translations.py (translation data)
    - String literals (user-facing messages)
    - Test fixture files with multilingual test data
  
  validation:
    - Unicode range detection for non-Latin scripts
    - Comment extraction (inline, block, docstrings)
    - Violation reporting with line numbers and detected language
  
  enforcement:
    - Pre-commit hook blocks commits with violations
    - Severity: BLOCKED (cannot commit without fixing)
    - Bypass: --no-verify flag (logged as warning)
  
  alternatives:
    - "Translate comment to English"
    - "Use English technical terms"
    - "Add to exemption list if truly necessary (rare)"
  
  evidence:
    - Linux Kernel: 100% English codebase, 15,000+ contributors globally
    - Python Standard Library: 100% English, used by millions
    - React: 100% English codebase, international team
    - Industry Standard: English is lingua franca of programming
```

---

## ✅ Success Criteria

### Phase 3 (Task 3.6)
- [ ] Code language validator detects non-English in 8 file types
- [ ] Unicode range detection works for CJK, Arabic, Cyrillic, Devanagari, etc.
- [ ] Exemptions work for response-templates.yaml and translations.py
- [ ] String literals ignored (user-facing messages allowed in any language)
- [ ] Violation reports show line numbers and detected language
- [ ] 15+ tests covering detection, exemptions, file types

### Phase 8 (Task 8.1, 8.7, 8.8)
- [ ] Tier 0 rule `CODE_LANGUAGE_ENFORCEMENT` added to brain-protection-rules.yaml
- [ ] Unified pre-commit hook validates filename length (warning) and code language (blocking)
- [ ] Pre-commit hook auto-installs during CORTEX setup
- [ ] Hook blocks commits with non-English code/comments
- [ ] Hook allows bypass with --no-verify (logged)
- [ ] Documentation explains policy in CORTEX.prompt.md and copilot-instructions.md
- [ ] Implementation guide created: `code-language-policy.md`

---

## 📚 Documentation Updates

**Files to Update:**

1. `.github/prompts/CORTEX.prompt.md`
   - Add "Code Language Policy" section
   - Emphasize: Multilingual responses ≠ multilingual code

2. `.github/copilot-instructions.md`
   - Update "Developer Workflows" with hook info
   - Add code language rule to conventions

3. `cortex-brain/documents/implementation-guides/code-language-policy.md` (NEW)
   - Full policy explanation
   - Detection strategy
   - Exemption list
   - Examples of violations and fixes

4. `docs/SETUP-CORTEX.md`
   - Mention git hook auto-installation
   - Explain pre-commit checks

---

## 🌍 Clarification: Multilingual UX ≠ Multilingual Code

### What IS Multilingual (✅)

**User-Facing Responses:**
```markdown
# 🧠 CORTEX Respuesta Técnica (Spanish)

## 🎯 Mi Comprensión de tu Solicitud
Deseas actualizar el archivo `src/main.py`...

## 💬 Respuesta
Voy a modificar la función `main()`:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

Este cambio permite registrar eventos...
```

**Template Translations:**
- 72 response templates in 12 languages
- Section headers translated
- Explanations in user's native language

### What IS NOT Multilingual (❌)

**Code and Comments:**
```python
# ❌ VIOLATION: Spanish comment
def procesar_datos(datos):
    # ❌ VIOLATION: Spanish comment
    resultado = transformar(datos)
    return resultado

# ✅ CORRECT: English comment
def process_data(data):
    # ✅ CORRECT: English comment
    result = transform(data)
    return result
```

**Key Principle:**
- **Responses to users:** Multilingual (12 languages)
- **Code for developers:** English only (universal standard)

---

## 🔢 Impact Summary

| Category | Before | After | Change |
|----------|--------|-------|--------|
| Supported response languages | 12 | 12 | No change |
| Allowed code languages | Any | English only | Enforced |
| Pre-commit validations | 1 (filename) | 2 (filename + code) | +1 |
| Tier 0 rules (Phase 8) | 1 | 2 | +1 |
| Estimated hours (Phase 3) | +16 | +24 | +8 |
| Total estimated hours | 152 | 160 | +8 |

---

## 📝 Estimated Effort

**Phase 3 - Task 3.6 (NEW):**
- Code language validator: 4 hours
- Unicode range detection: 2 hours
- Exemption system: 1 hour
- Testing (15+ tests): 1 hour
- **Subtotal:** 8 hours

**Phase 8 - Task 8.1 (UPDATED):**
- Add Tier 0 rule: 0.5 hours (minimal, already structured)

**Phase 8 - Task 8.7 (UPDATED):**
- Unified pre-commit hook: 1 hour (merge with existing)
- Auto-installation during setup: 1 hour

**Phase 8 - Task 8.8 (UPDATED):**
- Documentation updates: 1.5 hours

**Total Additional Effort:** 8 hours  
**Plan Total:** 152 → 160 hours

---

## 🎯 Benefits

### Maintainability
- ✅ All developers can read and understand code
- ✅ No language barriers in code review
- ✅ Consistent documentation

### Scalability
- ✅ New developers onboard faster (no translation needed)
- ✅ International teams collaborate efficiently
- ✅ Reduced cognitive load (one language for code)

### Quality
- ✅ Code review catches more issues (reviewers understand comments)
- ✅ Technical discussions easier (shared language)
- ✅ Stack Overflow / documentation search works (English terms)

### Separation of Concerns
- ✅ **Clear boundary:** UX is multilingual, code is not
- ✅ **Professional:** Industry standard (Linux, Python, React all English)
- ✅ **Pragmatic:** User-facing strings still multilingual for UX

---

**Next Action:** Approve plan v1.5 to implement code language enforcement alongside multilingual response support

*This governance ensures CORTEX is globally accessible (12 language responses) while maintaining a maintainable English codebase.*
