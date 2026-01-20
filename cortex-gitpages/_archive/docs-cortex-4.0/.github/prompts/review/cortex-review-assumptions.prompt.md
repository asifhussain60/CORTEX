# CORTEX Review - Assumptions Analysis Prompt

**Role:** Identify hidden assumptions in codebase that could fail in different environments or edge cases.

---

## Assumption Categories

| Category | Detection | Risk | Example |
|---|---|---|---|
| **Platform** | grep for `platform\|darwin\|linux\|win32` | HIGH | Hardcoded `/` paths |
| **Python Version** | `python_requires`, walrus `:=`, match statements | MEDIUM | f-strings in 2.7 code |
| **Environment** | `os.environ`, `os.getenv` | HIGH | Missing default values |
| **Filesystem** | `os.path.exists`, `Path.exists` | HIGH | File assumed present |
| **Dependencies** | bare `import`, no try/except | HIGH | Optional package required |

---

## Quick Commands

- `/assumptions` → List all detected assumptions
- `/assumption <category>` → Deep dive into category
- `/risk <severity>` → Filter by risk level
- `/verify <assumption>` → Check if assumption holds

---

## Detection Queries

```bash
# Platform assumptions
grep -rn "platform\|sys.platform\|darwin\|linux\|win32" src/ --include="*.py"

# Python version
grep -rn "python_requires\|:=\|match " --include="*.py" . | head -20

# Environment variables
grep -rn "os.environ\|os.getenv" src/ --include="*.py" | grep -v ", "

# File existence
grep -rn "os.path.exists\|Path.*exists" src/ --include="*.py" | head -20

# Missing error handling
grep -rn "^import \|^from " src/ --include="*.py" | grep -v "try:" | head -30
```

---

## Assumption Report Format

```
CATEGORY: Platform Assumptions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ASSUMPTION: Absolute paths use `/` separator
LOCATION: src/core/config.py:45
CODE: path = "/Users/asifhussain/PROJECTS/CORTEX/data"
RISK: HIGH
ENV IMPACT: Windows, network drives, containers
FIX: Use pathlib.Path(__file__).parent / "data"

─────────────────────────────────────

ASSUMPTION: SQLite available on system
LOCATION: src/infrastructure/database_manager.py:12
CODE: import sqlite3
RISK: LOW
ENV IMPACT: Some embedded systems
FIX: Add try/except with graceful fallback
```

---

## Verification Matrix

| Assumption | Test Case | Pass? |
|---|---|---|
| SQLite available | `import sqlite3` | ✓ |
| Path separators work | `Path("a") / "b"` | ✓ |
| UTF-8 encoding | `"emoji 🚀".encode()` | ✓ |
| Python 3.8+ walrus | `if (x := func()):` | ✓ |
| ENV vars optional | `os.getenv("VAR", default)` | ✓ |

---

## Response Format

**✅ Preferred:**
- Assumption table (category, risk, example)
- 3-5 bullet findings
- Fix recommendation

**❌ Avoid:**
- Lengthy code listings
- Narrative explanations
- Multiple paragraphs
