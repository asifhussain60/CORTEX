# Holistic Code Navigation Pattern (Search-Decide-Implement)

**Version:** 1.0  
**Author:** Asif Hussain  
**Date:** December 9, 2025  
**Status:** PRODUCTION  
**Tier 0 Rule:** HOLISTIC_CODE_DISCOVERY_ENFORCEMENT

---

## 🎯 Problem Statement

**Current Behavior:** CORTEX creates duplicate implementations during refactoring because it operates on individual files without searching for existing code.

**Impact:**
- Multiple functions with identical logic but different names
- Maintenance nightmare: Which version is canonical?
- Code review burden: Reviewers catch duplicates after implementation
- Technical debt compounds with every feature

**Root Cause:** No mandatory pre-implementation discovery workflow.

---

## 🏗️ Design Pattern: Search-Decide-Implement (SDI)

### Overview

A proactive discovery pattern that prevents code duplication by searching the codebase BEFORE implementing any new functionality.

### Pattern Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    SDI WORKFLOW                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. SEARCH (Multi-Strategy Discovery)                        │
│     ├── Semantic Search (intent-based)                       │
│     ├── Grep Search (pattern-based)                          │
│     ├── Usage Analysis (dependency-based)                    │
│     └── Parallel Execution (efficiency)                      │
│                                                               │
│  2. DECIDE (Strategy Selection)                              │
│     ├── Found Exact Match    → REUSE                         │
│     ├── Found Similar        → ENHANCE                       │
│     └── Found None           → CREATE (with justification)   │
│                                                               │
│  3. IMPLEMENT (Execute Decision)                             │
│     ├── Reuse: Import + integrate                            │
│     ├── Enhance: Extend existing code                        │
│     └── Create: Document uniqueness                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Phase 1: SEARCH (Multi-Strategy Discovery)

### Strategy 1: Semantic Search (Intent-Based)

**Purpose:** Find similar functionality regardless of naming conventions.

**Example:**
```python
# User request: "Add configuration file parsing"

# Search query
semantic_search("parse configuration file yaml")
semantic_search("load settings from yaml")

# Finds:
# - src/config.py::load_yaml_config()
# - src/utils/config_loader.py::read_config()
```

**When to Use:**
- User describes functionality in natural language
- Looking for conceptually similar code
- Function names may vary across modules

---

### Strategy 2: Grep Search (Pattern-Based)

**Purpose:** Find functions/classes matching keyword patterns.

**Example:**
```python
# User request: "Add token validation"

# Search query
grep_search("def.*authenticate|def.*verify.*token|class.*Auth", isRegexp=true)

# Finds:
# - src/auth/jwt.py::verify_jwt_token()
# - src/auth/oauth.py::authenticate_oauth_token()
# - src/middleware/auth.py::AuthenticationMiddleware
```

**When to Use:**
- Specific technical terms (authenticate, validate, parse)
- Looking for implementation patterns
- Class/function naming conventions

---

### Strategy 3: Usage Analysis (Dependency-Based)

**Purpose:** Understand how existing implementations are used.

**Example:**
```python
# Found: verify_jwt_token() in src/auth/jwt.py

# Usage analysis
list_code_usages("verify_jwt_token")

# Results:
# - 12 call sites across 5 files
# - Used by: API middleware, WebSocket handler, Admin panel
# - Pattern: Always called with request.headers["Authorization"]
```

**When to Use:**
- Understanding existing API contracts
- Checking integration patterns
- Avoiding breaking changes

---

### Strategy 4: Parallel Execution (Efficiency)

**Purpose:** Run all discovery strategies simultaneously.

**Example:**
```python
# Parallel batch discovery
results = await asyncio.gather(
    semantic_search("user authentication api"),
    grep_search("def.*authenticate|class.*Auth", isRegexp=true),
    list_code_usages("authenticate")
)

# Process results
semantic_results, grep_results, usage_results = results
```

**Benefits:**
- Faster discovery (3 searches in parallel vs sequential)
- Comprehensive results
- Respects Copilot's context window

---

## 🎯 Phase 2: DECIDE (Strategy Selection)

### Decision Matrix

```
┌────────────────────┬──────────────────────────────────────────┐
│ Discovery Result   │ Action                                   │
├────────────────────┼──────────────────────────────────────────┤
│ Exact Match        │ REUSE: Import and use existing           │
│ Similar (80%+)     │ ENHANCE: Extend with new features        │
│ Partial (50-80%)   │ CONSOLIDATE: Refactor to shared base     │
│ None Found         │ CREATE: Implement with justification     │
└────────────────────┴──────────────────────────────────────────┘
```

### Example: Exact Match (REUSE)

```python
# Discovery Result
Found: src/config.py::load_yaml_config(path: str) -> dict

# Decision
REUSE existing implementation

# Implementation
from config import load_yaml_config

def load_user_settings():
    return load_yaml_config("settings.yaml")
```

---

### Example: Similar (ENHANCE)

```python
# Discovery Result
Found: src/auth/jwt.py::verify_jwt_token(token: str) -> dict
Missing: Expiration check, custom claims validation

# Decision
ENHANCE existing function

# Implementation
# Before (existing)
def verify_jwt_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY)

# After (enhanced)
def verify_jwt_token(token: str, check_expiry: bool = True, 
                     required_claims: list = None) -> dict:
    payload = jwt.decode(token, SECRET_KEY)
    
    if check_expiry and payload.get("exp", 0) < time.time():
        raise TokenExpiredError()
    
    if required_claims:
        missing = set(required_claims) - set(payload.keys())
        if missing:
            raise MissingClaimsError(missing)
    
    return payload
```

---

### Example: None Found (CREATE)

```python
# Discovery Result
No existing ColdFusion parser found

# Decision
CREATE new implementation (justified)

# Implementation
"""
ColdFusion Parser - No existing implementation found

Discovery performed:
- semantic_search("coldfusion parser cfml"): No results
- grep_search("coldfusion|cfml", isRegexp=true): No results
- file_search("**/*coldfusion*.py"): No results

Justification: 
- CORTEX has no ColdFusion parsing capability
- Required for multi-language docstring extraction
- Unique functionality (not duplicating)
"""
class ColdFusionParser:
    def parse(self, source: str) -> AST:
        # Implementation
        pass
```

---

## 🚀 Phase 3: IMPLEMENT (Execute Decision)

### Integration with TDD Workflow

```
┌────────────────────────────────────────────────────────────┐
│         SDI + TDD Integration                               │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  Pre-RED: SEARCH (holistic discovery)                       │
│     │                                                        │
│     ├─→ Found existing? → Test integration                  │
│     └─→ None found?     → Proceed to standard TDD           │
│                                                              │
│  RED: Write failing test                                    │
│     │                                                        │
│     ├─→ Reuse: Test caller integration                      │
│     ├─→ Enhance: Test new parameters                        │
│     └─→ Create: Test new implementation                     │
│                                                              │
│  GREEN: Minimal implementation                              │
│     │                                                        │
│     ├─→ Reuse: Wire up existing function                    │
│     ├─→ Enhance: Add new features to existing               │
│     └─→ Create: Implement new code                          │
│                                                              │
│  REFACTOR: Cleanup + deduplication                          │
│     │                                                        │
│     └─→ Remove orphaned code (if any)                       │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

---

## 📊 Metrics & Success Criteria

### Quantitative Metrics

```yaml
success_criteria:
  duplication_rate:
    target: 0%
    measurement: "Duplicate function implementations within 90 days"
    current_baseline: "~15% duplication rate"
  
  code_reuse_rate:
    target: 80%
    measurement: "Common patterns (auth, config, logging) reused"
    current_baseline: "~45% reuse rate"
  
  code_review_efficiency:
    target: 50%
    measurement: "Reduction in 'similar code' review comments"
    current_baseline: "~20% of reviews flag duplication"

validation:
  detection_methods:
    - AST similarity analysis (function signature comparison)
    - Semantic similarity scoring (docstring + implementation)
    - Manual code review feedback tracking
  
  enforcement:
    - Brain Protector agent blocks implementation without discovery
    - Requires evidence of search results (tool invocations)
    - Tier 0 instinct (cannot be bypassed)
```

---

## 🛠️ Copilot Implementation Guide

### For GitHub Copilot Chat

**Trigger Detection:**
```python
implementation_keywords = [
    "implement", "create function", "add method", 
    "new class", "write code", "build feature"
]

if any(keyword in user_request.lower() for keyword in implementation_keywords):
    # Trigger HOLISTIC_CODE_DISCOVERY_ENFORCEMENT
    require_discovery_before_implementation()
```

**Discovery Execution:**
```python
async def holistic_discovery(intent: str, keywords: list):
    """Execute multi-strategy discovery in parallel"""
    
    # Build search queries
    semantic_query = f"{intent} implementation"
    grep_pattern = "|".join([f"def.*{k}|class.*{k}" for k in keywords])
    
    # Parallel execution
    results = await asyncio.gather(
        semantic_search(semantic_query),
        grep_search(grep_pattern, isRegexp=True),
        file_search(f"**/*{keywords[0]}*.py")
    )
    
    return consolidate_results(results)
```

**Decision Logic:**
```python
def decide_strategy(discovery_results):
    """Determine reuse, enhance, or create"""
    
    if not discovery_results:
        return "CREATE", "No existing implementation found"
    
    similarity_scores = calculate_similarity(discovery_results)
    
    if max(similarity_scores) > 0.9:
        return "REUSE", f"Exact match: {discovery_results[0]}"
    elif max(similarity_scores) > 0.7:
        return "ENHANCE", f"Similar code: {discovery_results[0]}"
    else:
        return "CREATE", f"Partial matches: {discovery_results}"
```

---

## 🔄 Comparison with Existing Rules

### REFACTOR_CODE_CLEANUP_ENFORCEMENT (Reactive)

**Trigger:** AFTER duplication created  
**Action:** Remove orphaned/duplicate code  
**Phase:** REFACTOR  
**Benefit:** Cleanup technical debt

### HOLISTIC_CODE_DISCOVERY_ENFORCEMENT (Proactive)

**Trigger:** BEFORE implementation starts  
**Action:** Search for existing code  
**Phase:** Pre-GREEN  
**Benefit:** Prevent duplication at source

### Defense-in-Depth Strategy

```
Proactive Prevention (HOLISTIC_CODE_DISCOVERY_ENFORCEMENT)
    ↓
    ├─→ Reuse existing code (0% new duplication)
    └─→ Create with justification (documented uniqueness)

Reactive Cleanup (REFACTOR_CODE_CLEANUP_ENFORCEMENT)
    ↓
    ├─→ Remove orphaned code (legacy cleanup)
    └─→ Consolidate duplicates (pre-pattern cleanup)
```

**Together:** Zero-tolerance duplication strategy
- Prevent at creation (proactive)
- Clean up legacy (reactive)
- Continuous improvement

---

## 📝 Real-World Examples

### Example 1: Configuration Parsing (REUSE)

**User Request:** "Add YAML configuration parsing"

**Discovery:**
```python
# Semantic search
semantic_search("parse yaml configuration file")
# Found: src/config.py::load_yaml_config()

# Usage analysis
list_code_usages("load_yaml_config")
# Found: 8 call sites, well-tested, stable API
```

**Decision:** REUSE existing implementation

**Implementation:**
```python
# No new code needed - import existing
from config import load_yaml_config

# Test integration
def test_settings_loader():
    settings = load_yaml_config("settings.yaml")
    assert "database" in settings
```

**Result:** Zero duplication, immediate reuse

---

### Example 2: Token Validation (ENHANCE)

**User Request:** "Add JWT validation with expiration check"

**Discovery:**
```python
# Grep search
grep_search("def.*verify.*token|jwt", isRegexp=True)
# Found: src/auth/jwt.py::verify_jwt_token()

# Current implementation
def verify_jwt_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY)
# Missing: Expiration validation
```

**Decision:** ENHANCE existing function

**Implementation:**
```python
# Test new feature (RED)
def test_expired_token_raises_error():
    expired_token = create_expired_token()
    with pytest.raises(TokenExpiredError):
        verify_jwt_token(expired_token, check_expiry=True)

# Enhance implementation (GREEN)
def verify_jwt_token(token: str, check_expiry: bool = True) -> dict:
    payload = jwt.decode(token, SECRET_KEY)
    if check_expiry and payload.get("exp", 0) < time.time():
        raise TokenExpiredError()
    return payload

# Refactor: Update all callers (optional check_expiry parameter)
```

**Result:** Enhanced existing code, maintained single source of truth

---

### Example 3: ColdFusion Parser (CREATE)

**User Request:** "Add ColdFusion code parsing"

**Discovery:**
```python
# Multi-strategy search
semantic_search("coldfusion parser cfml tokenizer")  # No results
grep_search("coldfusion|cfml", isRegexp=True)        # No results
file_search("**/*coldfusion*.py")                    # No results
```

**Decision:** CREATE (justified - no existing implementation)

**Implementation:**
```python
"""
ColdFusion Parser - Unique Implementation

Discovery Evidence:
- semantic_search("coldfusion parser"): 0 results
- grep_search("coldfusion|cfml"): 0 results
- file_search("**/*coldfusion*.py"): 0 results

Justification:
- CORTEX has no ColdFusion parsing capability
- Required for Dashboard V3 multi-language support
- Unique functionality (not duplicating existing parsers)
"""

# Test (RED)
def test_parse_coldfusion_component():
    source = '<cfcomponent><cffunction name="test"></cffunction></cfcomponent>'
    result = ColdFusionParser().parse(source)
    assert result.functions[0].name == "test"

# Implementation (GREEN)
class ColdFusionParser:
    def parse(self, source: str) -> ColdFusionAST:
        # Tokenize, parse, build AST
        pass
```

**Result:** New code created with documented justification

---

## 🎓 Best Practices

### DO ✅

- **Search first, code later** - Always run discovery before implementation
- **Use all three strategies** - Semantic + Grep + Usage for comprehensive results
- **Document CREATE decisions** - Explain why existing code wasn't reused
- **Test integrations** - When reusing code, test the integration
- **Enhance cautiously** - Add parameters instead of duplicating

### DON'T ❌

- **Skip discovery** - Never implement without searching
- **Assume uniqueness** - Large codebases often have similar code
- **Duplicate for convenience** - Reuse is faster long-term
- **Ignore partial matches** - 70% similar = opportunity to consolidate
- **Create without justification** - Document why existing code insufficient

---

## 🔧 Troubleshooting

### Issue: Search returns too many results

**Solution:** Narrow query with more specific keywords
```python
# Too broad
semantic_search("authentication")  # 50+ results

# Better
semantic_search("jwt token validation with expiration")  # 3 results
```

---

### Issue: No results found but code exists

**Solution:** Try alternative search strategies
```python
# Semantic search fails
semantic_search("parse configuration")  # 0 results

# Try grep with synonyms
grep_search("load_config|read_settings|parse_yaml", isRegexp=True)  # Found!
```

---

### Issue: Similar code but different API

**Solution:** Consolidate into shared base
```python
# Found similar implementations
def load_json_config(path):
    return json.load(open(path))

def load_yaml_config(path):
    return yaml.safe_load(open(path))

# Consolidate
def load_config(path: str, format: str = "yaml"):
    loaders = {"json": json.load, "yaml": yaml.safe_load}
    with open(path) as f:
        return loaders[format](f)
```

---

## 📈 Expected Impact

### Immediate (Week 1-4)

- **20% reduction** in duplicate code creation
- **Discovery workflow** becomes habitual
- **Code review velocity** improves (fewer duplication discussions)

### Short-Term (Month 1-3)

- **50% reduction** in duplicate implementations
- **Reuse rate** increases to 60%
- **Codebase navigation** improves (less noise)

### Long-Term (Month 3-6)

- **80% reuse rate** for common patterns
- **Near-zero duplication** for new code
- **Maintenance burden** drops significantly
- **Onboarding speed** increases (clearer code structure)

---

## 🔗 Related Documentation

- `cortex-brain/brain-protection-rules.yaml` - HOLISTIC_CODE_DISCOVERY_ENFORCEMENT rule
- `cortex-brain/brain-protection-rules.yaml` - REFACTOR_CODE_CLEANUP_ENFORCEMENT rule
- `modules/tdd-mastery-guide.md` - TDD workflow integration
- `src/tier0/README.md` - Tier 0 governance architecture

---

**Version History:**
- **1.0** (2025-12-09): Initial pattern documentation

---

**Copyright © 2025 Asif Hussain. All rights reserved.**
