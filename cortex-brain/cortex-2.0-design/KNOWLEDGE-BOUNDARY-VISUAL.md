# 🎨 Knowledge Boundary Separation - Visual Architecture

**Purpose:** Visual representation of the critical architecture fix  
**Issue:** Mixed CORTEX and user app knowledge in single brain  
**Solution:** Dual brain architecture with clear boundaries

---

## ❌ Current Architecture (BROKEN)

```
┌─────────────────────────────────────────────────────────────┐
│                    CORTEX BRAIN (MIXED)                      │
│                     cortex-brain/                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ knowledge-graph.yaml                               │    │
│  ├────────────────────────────────────────────────────┤    │
│  │ ✅ CORTEX patterns (correct)                       │    │
│  │    - cortex_tier_architecture                      │    │
│  │    - cortex_agent_patterns                         │    │
│  │                                                     │    │
│  │ ❌ USER APP patterns (VIOLATION!)                  │    │
│  │    - file_relationships:                           │    │
│  │        tests/fixtures/.../dashboard.spec.ts        │    │
│  │    - test_patterns: Playwright tests               │    │
│  │    - source: test-crawler (user app!)              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ architectural-patterns.yaml                        │    │
│  ├────────────────────────────────────────────────────┤    │
│  │ ❌ ALL USER APP PATTERNS (VIOLATION!)              │    │
│  │    - api_auth: none                                │    │
│  │    - ui_component_structure: feature-based         │    │
│  │    - test_framework: Playwright                    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ tier3/context.db                                   │    │
│  ├────────────────────────────────────────────────────┤    │
│  │ ❓ AMBIGUOUS: CORTEX metrics or user app metrics?  │    │
│  │    - git_metrics (which repo?)                     │    │
│  │    - file_hotspots (which files?)                  │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘

                            ⚠️ PROBLEM:
    Cannot distinguish CORTEX knowledge from user app knowledge!
```

---

## ✅ Correct Architecture (DUAL BRAIN)

```
┌─────────────────────────────────────────────────────────────┐
│              BOUNDARY 1: CORTEX CORE BRAIN                   │
│                    cortex-brain/                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ ONLY CORTEX Framework Knowledge                         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ tier2/cortex-knowledge-graph.yaml                  │    │
│  ├────────────────────────────────────────────────────┤    │
│  │ ✅ cortex_tier_architecture                        │    │
│  │ ✅ cortex_agent_patterns                           │    │
│  │ ✅ cortex_operation_patterns                       │    │
│  │ ✅ cortex_plugin_patterns                          │    │
│  │ ✅ cortex_testing_strategy                         │    │
│  │                                                     │    │
│  │ ❌ NO user app patterns allowed                    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ tier3/cortex-context.db                            │    │
│  ├────────────────────────────────────────────────────┤    │
│  │ ✅ CORTEX repository git metrics                   │    │
│  │ ✅ CORTEX file hotspots                            │    │
│  │ ✅ CORTEX test coverage                            │    │
│  │                                                     │    │
│  │ ❌ NO user app metrics                             │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  API: CortexBrain.query("cortex_patterns")                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘

                            ⬇️ ISOLATED ⬇️

┌─────────────────────────────────────────────────────────────┐
│           BOUNDARY 2: APPLICATION BRAIN                      │
│              <USER_WORKSPACE>/.cortex/                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ ONLY User Application Knowledge                         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ app-brain/knowledge-graph.yaml                     │    │
│  ├────────────────────────────────────────────────────┤    │
│  │ ✅ file_relationships (user app files)             │    │
│  │ ✅ test_patterns (user app tests)                  │    │
│  │ ✅ architectural_patterns (user app)               │    │
│  │                                                     │    │
│  │ ❌ NO CORTEX framework patterns                    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ context/app-context.db                             │    │
│  ├────────────────────────────────────────────────────┤    │
│  │ ✅ User app git metrics                            │    │
│  │ ✅ User app file hotspots                          │    │
│  │ ✅ User app test coverage                          │    │
│  │                                                     │    │
│  │ ❌ NO CORTEX metrics                               │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  API: ApplicationBrain.query("app_patterns")                │
│                                                              │
└─────────────────────────────────────────────────────────────┘

                    ✅ SOLUTION:
    Clear separation, enforced boundaries, distinct APIs
```

---

## 🔄 Agent Query Flow (Dual Brain)

```
┌────────────────────────────────────────────────────────────┐
│                   User Request                             │
│       "Add authentication to my application"               │
└────────────────┬───────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────┐
│              Intent Detector Agent                         │
│         Routes to Executor Agent                           │
└────────────────┬───────────────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────────┐
│               Executor Agent                               │
│         Needs TWO types of knowledge:                      │
│         1. How to execute (CORTEX)                         │
│         2. User app context (Application)                  │
└─────────────┬──────────────────────────────┬───────────────┘
              │                              │
              │                              │
    ┌─────────▼──────────┐        ┌─────────▼──────────┐
    │  Query CORTEX      │        │  Query Application │
    │  Brain             │        │  Brain             │
    │                    │        │                    │
    │  "How to implement │        │  "What's my app    │
    │   authentication?" │        │   architecture?"   │
    │                    │        │                    │
    │  Returns:          │        │  Returns:          │
    │  - JWT pattern     │        │  - API: REST       │
    │  - OAuth flow      │        │  - Auth: none      │
    │  - Security rules  │        │  - UI: feature-    │
    │                    │        │    based           │
    └─────────┬──────────┘        └─────────┬──────────┘
              │                              │
              │                              │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   Combined Implementation    │
              │                              │
              │ Uses CORTEX strategy         │
              │ + User app context           │
              │ = Perfect fit solution       │
              └──────────────────────────────┘
```

---

## 📊 Data Flow Comparison

### ❌ BEFORE (Mixed Boundary)

```
Crawler
   │
   │ Discovers user app patterns
   │
   ▼
cortex-brain/knowledge-graph.yaml  ❌ WRONG!
   │
   │ Mixed CORTEX + user patterns
   │
   ▼
Agent queries get contaminated data
```

### ✅ AFTER (Dual Boundary)

```
CORTEX Development
   │
   │ CORTEX improves itself
   │
   ▼
cortex-brain/tier2/cortex-knowledge-graph.yaml  ✅ CORRECT!
   │
   │ ONLY CORTEX patterns
   │
   ▼
Agents query CORTEX strategy


User App Crawler
   │
   │ Discovers user app patterns
   │
   ▼
.cortex/app-brain/knowledge-graph.yaml  ✅ CORRECT!
   │
   │ ONLY user app patterns
   │
   ▼
Agents query app context
```

---

## 🔒 Boundary Enforcement (Runtime Validation)

```python
class CortexBrain:
    """CORTEX Core Brain - Framework knowledge ONLY"""
    
    def learn_pattern(self, pattern: Dict[str, Any]):
        # Validate before storing
        if self._is_user_app_pattern(pattern):
            raise ValueError(
                "User app patterns not allowed in CORTEX brain. "
                "Use ApplicationBrain instead."
            )
        
        # Store in CORTEX brain
        self._save_pattern(pattern)
    
    def _is_user_app_pattern(self, pattern: Dict) -> bool:
        """Detect user app contamination."""
        forbidden_keys = [
            "file_relationships",    # User files
            "test_patterns",         # User tests
            "ui_component_structure" # User architecture
        ]
        
        return any(key in pattern for key in forbidden_keys)


class ApplicationBrain:
    """Application Brain - User workspace knowledge ONLY"""
    
    def learn_pattern(self, pattern: Dict[str, Any]):
        # Validate before storing
        if self._is_cortex_framework_pattern(pattern):
            raise ValueError(
                "CORTEX framework patterns not allowed in app brain. "
                "Use CortexBrain instead."
            )
        
        # Store in app brain
        self._save_pattern(pattern)
    
    def _is_cortex_framework_pattern(self, pattern: Dict) -> bool:
        """Detect CORTEX framework contamination."""
        forbidden_keys = [
            "cortex_tier_architecture",
            "cortex_agent_patterns",
            "cortex_operation_patterns"
        ]
        
        return any(key in pattern for key in forbidden_keys)
```

---

## 🗺️ Directory Structure Comparison

### ❌ BEFORE (Single Brain)

```
CORTEX/
├── cortex-brain/                    # MIXED CONCERNS ❌
│   ├── knowledge-graph.yaml         # CORTEX + user patterns
│   ├── architectural-patterns.yaml  # User app patterns
│   ├── file-relationships.yaml      # User app files
│   └── tier3/
│       └── context.db               # Ambiguous metrics
```

### ✅ AFTER (Dual Brain)

```
CORTEX/
├── cortex-brain/                    # CORTEX ONLY ✅
│   ├── tier2/
│   │   └── cortex-knowledge-graph.yaml  # CORTEX patterns
│   ├── tier3/
│   │   └── cortex-context.db            # CORTEX metrics
│   └── ... (other CORTEX files)


<USER_WORKSPACE>/
├── .cortex/                         # USER APP ONLY ✅
│   ├── app-brain/
│   │   ├── knowledge-graph.yaml     # User app patterns
│   │   ├── architectural-patterns.yaml
│   │   └── file-relationships.yaml
│   └── context/
│       └── app-context.db           # User app metrics
```

---

## 🎯 Migration Flow

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Scan CORTEX Brain for User App Contamination      │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Classify Patterns                                  │
│                                                              │
│  For each pattern in knowledge-graph.yaml:                  │
│    ├─ Is it CORTEX framework? → Keep in cortex-brain/      │
│    └─ Is it user app? → Move to .cortex/app-brain/         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Extract User App Patterns                          │
│                                                              │
│  Extracted patterns:                                         │
│    ✓ file_relationships                                     │
│    ✓ test_patterns                                          │
│    ✓ architectural_patterns (api_auth, etc.)                │
│    ✓ ui_component_structure                                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Create Application Brain Structure                 │
│                                                              │
│  .cortex/                                                    │
│  ├── app-brain/                                             │
│  │   ├── knowledge-graph.yaml (NEW)                         │
│  │   ├── architectural-patterns.yaml (NEW)                  │
│  │   └── file-relationships.yaml (NEW)                      │
│  └── context/                                               │
│      └── app-context.db (NEW)                               │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: Migrate Data                                       │
│                                                              │
│  cortex-brain/knowledge-graph.yaml                          │
│    └─ Remove: file_relationships, test_patterns             │
│                                                              │
│  .cortex/app-brain/knowledge-graph.yaml                     │
│    └─ Add: file_relationships, test_patterns                │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: Validate Separation                                │
│                                                              │
│  Checks:                                                     │
│    ✓ No user app data in cortex-brain/                     │
│    ✓ No CORTEX framework data in .cortex/app-brain/        │
│    ✓ All tests passing (455 existing + 30 new)             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📐 API Comparison

### ❌ BEFORE (Ambiguous)

```python
# Which brain is this?
knowledge_graph = KnowledgeGraph()
patterns = knowledge_graph.query("patterns")
# Returns CORTEX + user patterns (MIXED!)
```

### ✅ AFTER (Clear Separation)

```python
# Query CORTEX framework knowledge
cortex_brain = CortexBrain()
cortex_patterns = cortex_brain.query("execution_patterns")
# Returns: CORTEX strategies ONLY

# Query user application knowledge
app_brain = ApplicationBrain(workspace_root=Path.cwd())
app_patterns = app_brain.query("architectural_patterns")
# Returns: User app patterns ONLY

# Use both for complete context
executor = ExecutorAgent(cortex_brain, app_brain)
executor.execute("add authentication")
# Uses CORTEX strategy + user app context
```

---

## 🧪 Test Coverage (Boundary Validation)

```
tests/tier2/test_knowledge_boundary_separation.py

┌─────────────────────────────────────────────────────────────┐
│  Test Suite: Boundary Validation                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✓ test_cortex_brain_contains_only_cortex_knowledge()      │
│    Ensures no user app data in CORTEX brain                 │
│                                                              │
│  ✓ test_app_brain_contains_only_user_app_knowledge()       │
│    Ensures no CORTEX framework data in app brain            │
│                                                              │
│  ✓ test_boundary_enforcement_on_write()                    │
│    Runtime validation prevents cross-contamination          │
│                                                              │
│  ✓ test_cortex_brain_rejects_user_patterns()               │
│    CortexBrain.learn_pattern() raises error for user data   │
│                                                              │
│  ✓ test_app_brain_rejects_cortex_patterns()                │
│    ApplicationBrain.learn_pattern() raises error for CORTEX │
│                                                              │
│  ✓ test_migration_script_preserves_data()                  │
│    No data loss during migration                            │
│                                                              │
│  ✓ test_agents_use_both_brains_correctly()                 │
│    Agents query correct brain for each knowledge type       │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Expected Test Count: 30+ tests
Coverage Target: 100% for boundary enforcement code
```

---

## 🎓 Knowledge Boundary Contract (Summary)

| Aspect | CORTEX Core Brain | Application Brain |
|--------|-------------------|-------------------|
| **Location** | `cortex-brain/` | `.cortex/app-brain/` |
| **Scope** | CORTEX framework | User's application |
| **API** | `CortexBrain.query()` | `ApplicationBrain.query()` |
| **Allowed Patterns** | Tier architecture, agents, operations | File relationships, test patterns, app architecture |
| **Forbidden Patterns** | User app data | CORTEX framework data |
| **Context Metrics** | CORTEX repo git stats | User app git stats |
| **Enforcement** | Runtime validation | Runtime validation |
| **Migration** | Clean existing data | Populate from migration |

---

**Visual Architecture Summary:**  
✅ Two distinct brains  
✅ Clear API separation  
✅ Runtime enforcement  
✅ Complete isolation  

**Next Step:** Execute drift plan (32 hours / 4 working days)

---

*Visual diagrams generated: 2025-11-12*  
*Part of: KNOWLEDGE-BOUNDARY-SEPARATION-DRIFT-PLAN.md*
