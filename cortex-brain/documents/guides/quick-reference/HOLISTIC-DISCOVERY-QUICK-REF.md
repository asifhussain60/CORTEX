# Holistic Code Discovery - Quick Reference

**Rule:** HOLISTIC_CODE_DISCOVERY_ENFORCEMENT  
**Tier:** 0 (Cannot be bypassed)  
**Severity:** BLOCKED  
**Pattern:** Search-Decide-Implement (SDI)

---

## ⚡ 30-Second Summary

**Before implementing ANY new code, you MUST search for existing implementations.**

```
SEARCH → DECIDE → IMPLEMENT
   ↓         ↓         ↓
 3 tools   Matrix   Action
```

---

## 🔍 SEARCH Phase (Run All 3)

### 1. Semantic Search (Intent-Based)
```python
semantic_search("parse yaml configuration")
semantic_search("jwt token validation")
```
**Finds:** Similar functionality regardless of naming

---

### 2. Grep Search (Pattern-Based)
```python
grep_search("def.*config|load.*yaml", isRegexp=True)
grep_search("verify.*token|authenticate", isRegexp=True)
```
**Finds:** Functions/classes with matching keywords

---

### 3. Usage Analysis (Context-Based)
```python
list_code_usages("authenticate_user")
list_code_usages("ConfigParser")
```
**Finds:** How existing code is used (call sites, patterns)

---

## 🎯 DECIDE Phase (Decision Matrix)

| Discovery Result | Action | Example |
|-----------------|--------|---------|
| **Exact Match (90%+)** | ✅ REUSE | Import existing function |
| **Similar (70-90%)** | 🔧 ENHANCE | Add parameters/features |
| **Partial (50-70%)** | 🔀 CONSOLIDATE | Refactor to shared base |
| **None Found** | ✨ CREATE | Document justification |

---

## 🚀 IMPLEMENT Phase (Execute Decision)

### Reuse Example
```python
# Found existing: src/config.py::load_yaml_config()
from config import load_yaml_config

def load_settings():
    return load_yaml_config("settings.yaml")
```

### Enhance Example
```python
# Found existing but missing feature
def verify_jwt_token(token: str, check_expiry: bool = True):
    payload = jwt.decode(token, SECRET_KEY)
    if check_expiry and payload.get("exp", 0) < time.time():
        raise TokenExpiredError()
    return payload
```

### Create Example
```python
"""
ColdFusion Parser - No existing implementation

Discovery Evidence:
- semantic_search("coldfusion parser"): 0 results
- grep_search("coldfusion|cfml"): 0 results

Justification: CORTEX has no ColdFusion support
"""
class ColdFusionParser:
    # New implementation
    pass
```

---

## 🚨 Common Mistakes

### ❌ DON'T: Skip Discovery
```python
# User: "Add config parsing"
# You: *immediately writes new function*
def parse_config(path):  # BLOCKED! Didn't search first
    pass
```

### ✅ DO: Search First
```python
# User: "Add config parsing"
# You: *runs discovery*
semantic_search("parse configuration yaml")
# Found: src/config.py::load_yaml_config()
# Decision: REUSE existing
from config import load_yaml_config
```

---

## 📊 Success Metrics

- **0% duplication** for new code (target)
- **80% reuse rate** for common patterns (auth, config, logging)
- **50% fewer** "similar code" code review comments

---

## 🔗 Integration with TDD

```
Pre-RED: SEARCH (discovery before any code)
    ↓
RED: Write test (for integration or new code)
    ↓
GREEN: Implement (reuse/enhance/create)
    ↓
REFACTOR: Cleanup (remove orphaned code)
```

---

## 💡 Pro Tips

1. **Run searches in parallel** - Use all 3 strategies simultaneously
2. **Document CREATE decisions** - Explain why no reuse
3. **Enhance over duplicate** - Add parameters instead of new functions
4. **Test integrations** - When reusing, test your integration
5. **Update discovery queries** - If no results, try synonyms

---

## 📚 Full Documentation

See: `cortex-brain/documents/implementation-guides/holistic-code-navigation-pattern.md`

---

**Copyright © 2025 Asif Hussain. All rights reserved.**
