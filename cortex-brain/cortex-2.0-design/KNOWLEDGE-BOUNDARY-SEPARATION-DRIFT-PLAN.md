# 🚨 CRITICAL: Knowledge Boundary Separation - Drift Plan

**Issue Severity:** CRITICAL  
**Discovery Date:** 2025-11-12  
**Status:** 🔴 ARCHITECTURE VIOLATION DETECTED  
**Impact:** Fundamental architecture breach - mixed concerns in CORTEX brain

---

## 📋 Executive Summary

**CRITICAL FINDING:** CORTEX architecture currently violates its core design principle by mixing two distinct knowledge boundaries within a single "cortex-brain" structure:

1. **CORTEX Core Knowledge** - Framework infrastructure, architecture, tech stack
2. **Application Knowledge** - User's application-specific data (currently polluting CORTEX brain)

**This is NOT acceptable.** The brain must be split into TWO separate, isolated boundaries.

---

## 🎯 The Problem (Root Cause Analysis)

### Current Architecture Violation

```yaml
cortex-brain/                          # ❌ MIXED CONCERNS
├── knowledge-graph.yaml               # Contains CORTEX patterns
├── architectural-patterns.yaml        # Contains user app patterns (VIOLATION!)
├── file-relationships.yaml            # Contains user app files (VIOLATION!)
├── test-patterns.yaml                 # Contains user app tests (VIOLATION!)
├── development-context.yaml           # Mixed CORTEX + user context
└── industry-standards.yaml            # Generic (acceptable)
```

### Evidence of Contamination

**From `knowledge-graph.yaml`:**
```yaml
file_relationships:
  tests/fixtures/mock-project/tests/UI/dashboard.spec.ts:  # USER APP!
  - relationship: test-coverage
    source: test-crawler                                    # USER APP CRAWLER!
    related_file: Components/**/dashboard.razor            # USER APP!
```

**From `architectural-patterns.yaml`:**
```yaml
architectural_patterns:
  api_auth: none              # USER APP PATTERN!
  ui_component_structure: feature-based  # USER APP PATTERN!
  test_framework: Playwright  # USER APP PATTERN!
```

**From `brain-protection-rules.yaml`:**
```yaml
Layer_5_Codebase_Awareness:
  - name: "Adopt User's Code Style"    # REFERS TO USER APP!
  - "**/src/crawlers/**"               # CRAWLER POLLUTION!
```

**From `src/tier3/context_intelligence.py`:**
```python
class ContextIntelligence:
    """
    Tier 3: Development Context Intelligence
    
    Provides real-time project analytics including:
    - Git activity tracking and commit velocity        # WHOSE GIT? CORTEX or USER?
    - File hotspot detection and churn analysis        # WHICH FILES? MIXED!
    """
```

### The Fundamental Violation

**CORTEX brain should ONLY know about CORTEX:**
- ✅ CORTEX tier architecture
- ✅ CORTEX agent system
- ✅ CORTEX plugin patterns
- ✅ CORTEX operations
- ✅ CORTEX testing strategies

**CORTEX brain should NEVER contain:**
- ❌ User's application patterns
- ❌ User's file relationships
- ❌ User's test suite structure
- ❌ User's architectural decisions
- ❌ User's codebase metrics

---

## 🎨 The Correct Architecture (Two Boundaries)

### Boundary 1: CORTEX Core Brain (Immutable Framework Knowledge)

```
cortex-brain/                          # ONLY CORTEX knowledge
├── core/
│   ├── architecture.yaml              # CORTEX tier system
│   ├── agents.yaml                    # CORTEX agent definitions
│   ├── operations.yaml                # CORTEX operations registry
│   ├── plugins.yaml                   # CORTEX plugin patterns
│   └── testing-strategy.yaml          # How CORTEX tests itself
│
├── tier0/                             # Governance (CORTEX rules)
│   └── brain-protection-rules.yaml
│
├── tier1/                             # CORTEX conversation history
│   └── conversation-history.db
│
├── tier2/                             # CORTEX learned patterns
│   └── cortex-knowledge-graph.yaml    # ONLY CORTEX patterns
│
└── tier3/                             # CORTEX project metrics
    └── cortex-context.db              # ONLY CORTEX development metrics
```

### Boundary 2: Application Brain (User Workspace Knowledge)

```
<USER_WORKSPACE_ROOT>/
├── .cortex/                           # Application-specific CORTEX data
│   ├── app-brain/
│   │   ├── knowledge-graph.yaml       # USER app patterns
│   │   ├── architectural-patterns.yaml # USER app architecture
│   │   ├── file-relationships.yaml    # USER app file graph
│   │   └── test-patterns.yaml         # USER app test patterns
│   │
│   ├── context/
│   │   └── app-context.db             # USER app git metrics, hotspots
│   │
│   └── config/
│       └── cortex.config.json         # USER app CORTEX configuration
```

**OR (for multi-project CORTEX deployment):**

```
~/.cortex/                             # User-level CORTEX storage
├── workspaces/
│   ├── project-a/
│   │   ├── app-brain/
│   │   └── context/
│   │
│   └── project-b/
│       ├── app-brain/
│       └── context/
│
└── global/
    └── user-preferences.yaml          # Cross-project settings
```

---

## 📊 Impact Analysis

### What's Currently Broken

| Component | Current State | Violation Type | Severity |
|-----------|---------------|----------------|----------|
| **knowledge-graph.yaml** | Mixed CORTEX + user patterns | Data contamination | 🔴 CRITICAL |
| **architectural-patterns.yaml** | User app patterns stored in CORTEX brain | Wrong boundary | 🔴 CRITICAL |
| **file-relationships.yaml** | User app file graph in CORTEX brain | Wrong boundary | 🔴 CRITICAL |
| **Tier 3 Context Intelligence** | Unclear whose context (CORTEX or user) | Ambiguous scope | 🟡 HIGH |
| **Crawlers** | References in brain protection rules | Scope pollution | 🟡 HIGH |
| **Brain Protection Layer** | References "user's code style" | Unclear boundary | 🟡 MEDIUM |

### What Needs to Happen

1. **CORTEX Brain Cleanup** (Tier 2 + Tier 3)
   - Remove ALL user application patterns
   - Remove ALL user file relationships
   - Remove ALL user architectural decisions
   - Keep ONLY CORTEX-specific knowledge

2. **Application Brain Creation** (NEW)
   - Create `.cortex/app-brain/` structure in user workspaces
   - Migrate user patterns from CORTEX brain → app brain
   - Update crawlers to populate app brain (NOT CORTEX brain)

3. **API Boundary Enforcement**
   - Clear API distinction: `cortex_brain.query()` vs `app_brain.query()`
   - Tier 2 Knowledge Graph: CORTEX-only queries
   - Tier 3 Context Intelligence: Split into `CortexContext` + `AppContext`

4. **Documentation Updates**
   - Update all architecture docs to reflect two boundaries
   - Update CORTEX.prompt.md to explain separation
   - Update setup guides to initialize both brains

---

## 🗺️ Drift Plan (Comprehensive Remediation)

### Phase 1: Design & Specification (4 hours)

**1.1 Define Boundary Contract (1 hour)**

Create `cortex-brain/cortex-2.0-design/KNOWLEDGE-BOUNDARY-CONTRACT.md`:

```markdown
# CORTEX Knowledge Boundary Contract

## Boundary 1: CORTEX Core Brain

**Scope:** Everything about CORTEX framework itself

**Allowed:**
- CORTEX tier architecture (Tier 0-3)
- CORTEX agent system (10 agents, corpus callosum)
- CORTEX operations (setup, cleanup, story refresh, etc.)
- CORTEX plugin patterns (BasePlugin, PluginRegistry)
- CORTEX testing strategies (how CORTEX tests itself)
- CORTEX development metrics (CORTEX repo git stats, CORTEX test coverage)
- CORTEX learned patterns (how CORTEX improves itself)

**Forbidden:**
- User application code patterns
- User application file relationships
- User application architectural decisions
- User application test patterns
- User application git metrics
- User application business logic

**Storage Location:** `CORTEX_ROOT/cortex-brain/`

**API:** `CortexBrain.query()`, `CortexContext.get_metrics()`

---

## Boundary 2: Application Brain

**Scope:** Everything about user's application

**Allowed:**
- User application architectural patterns
- User application file relationships
- User application test patterns
- User application git metrics
- User application hotspots
- User application learned patterns

**Forbidden:**
- CORTEX framework knowledge
- CORTEX tier architecture
- CORTEX agent definitions
- CORTEX operation definitions

**Storage Location:** `<USER_WORKSPACE>/.cortex/app-brain/`

**API:** `ApplicationBrain.query()`, `AppContext.get_metrics()`
```

**1.2 Design Application Brain Schema (2 hours)**

Create:
- `app-brain/knowledge-graph.yaml` schema
- `app-brain/architectural-patterns.yaml` schema
- `app-brain/file-relationships.yaml` schema
- `app-brain/context.db` schema (SQLite)

**1.3 Design API Separation (1 hour)**

Update:
- `src/tier2/knowledge_graph.py` → `src/tier2/cortex_knowledge_graph.py`
- Create `src/tier2/application_knowledge_graph.py`
- `src/tier3/context_intelligence.py` → Split into:
  - `src/tier3/cortex_context.py`
  - `src/tier3/application_context.py`

---

### Phase 2: Implementation (12 hours)

**2.1 Create Application Brain Infrastructure (3 hours)**

Files to create:
```python
src/app_brain/
├── __init__.py
├── application_brain.py           # Main API
├── application_knowledge_graph.py # Tier 2 for user app
├── application_context.py         # Tier 3 for user app
└── brain_locator.py               # Find app brain in user workspace
```

**Key class:**
```python
class ApplicationBrain:
    """
    Application-specific brain for user's workspace.
    
    Isolated from CORTEX core brain.
    """
    
    def __init__(self, workspace_root: Path):
        """Initialize app brain in .cortex/app-brain/"""
        self.workspace_root = workspace_root
        self.brain_dir = workspace_root / ".cortex" / "app-brain"
        self.brain_dir.mkdir(parents=True, exist_ok=True)
        
        self.knowledge_graph = ApplicationKnowledgeGraph(self.brain_dir)
        self.context = ApplicationContext(self.brain_dir)
    
    def learn_pattern(self, pattern: Dict[str, Any]):
        """Store user app pattern (NOT in CORTEX brain)"""
        self.knowledge_graph.add_pattern(pattern)
    
    def get_app_context(self) -> Dict[str, Any]:
        """Get user app context (NOT CORTEX context)"""
        return self.context.get_summary()
```

**2.2 Migrate Existing Data (4 hours)**

Create migration script: `scripts/migrate_knowledge_boundaries.py`

```python
def migrate_knowledge_boundaries():
    """
    Migrate user app data from CORTEX brain → app brain.
    
    Steps:
    1. Scan cortex-brain/knowledge-graph.yaml
    2. Identify user app patterns (e.g., file_relationships with test files)
    3. Extract and save to .cortex/app-brain/knowledge-graph.yaml
    4. Remove from CORTEX brain
    5. Validate no user data remains in CORTEX brain
    """
    
    # Load CORTEX knowledge graph
    cortex_kg = load_yaml("cortex-brain/knowledge-graph.yaml")
    
    # Split patterns
    cortex_patterns = {}
    app_patterns = {}
    
    for key, value in cortex_kg.items():
        if is_user_app_pattern(key, value):
            app_patterns[key] = value
        else:
            cortex_patterns[key] = value
    
    # Save split data
    save_yaml("cortex-brain/knowledge-graph.yaml", cortex_patterns)
    save_yaml(".cortex/app-brain/knowledge-graph.yaml", app_patterns)
    
    # Validate
    assert no_user_data_in_cortex_brain()
```

**Heuristics for detection:**
```python
def is_user_app_pattern(key: str, value: Any) -> bool:
    """Detect if pattern belongs to user app."""
    
    # File relationships pointing to user code
    if "file_relationships" in key:
        if any(user_indicator in str(value) for user_indicator in [
            "tests/fixtures/mock-project",
            "Components/",
            "dashboard.spec.ts",
            ".razor"
        ]):
            return True
    
    # Architectural patterns (user-specific)
    if key in ["api_auth", "ui_component_structure", "test_framework"]:
        return True
    
    # Test patterns from crawlers
    if "test_patterns" in key:
        return True
    
    # Default: CORTEX pattern
    return False
```

**2.3 Update Tier 2 Knowledge Graph (2 hours)**

Refactor `src/tier2/knowledge_graph.py`:

```python
class CortexKnowledgeGraph:
    """
    Tier 2 Knowledge Graph - CORTEX PATTERNS ONLY.
    
    Stores:
    - CORTEX architectural patterns (tier system, agents)
    - CORTEX learned patterns (successful workflows)
    - CORTEX industry standards (Python best practices for CORTEX)
    
    Does NOT store:
    - User application patterns (use ApplicationKnowledgeGraph)
    - User file relationships
    - User test patterns
    """
    
    def __init__(self, brain_dir: Path):
        self.graph_file = brain_dir / "tier2" / "cortex-knowledge-graph.yaml"
        self._validate_cortex_only()
    
    def _validate_cortex_only(self):
        """Ensure no user app data in CORTEX knowledge graph."""
        patterns = self.load_patterns()
        
        forbidden_keys = [
            "file_relationships",  # User app files
            "test_patterns",       # User app tests
            "ui_component_structure"  # User app architecture
        ]
        
        for key in forbidden_keys:
            if key in patterns:
                raise ValueError(
                    f"User app data detected in CORTEX brain: {key}. "
                    "Use ApplicationKnowledgeGraph instead."
                )
```

**2.4 Update Tier 3 Context Intelligence (3 hours)**

Split into two classes:

```python
# src/tier3/cortex_context.py
class CortexContext:
    """
    CORTEX development context intelligence.
    
    Tracks CORTEX repository metrics ONLY:
    - CORTEX repo git activity
    - CORTEX file hotspots
    - CORTEX test coverage
    - CORTEX build health
    """
    
    def __init__(self, cortex_repo_path: Path):
        self.repo_path = cortex_repo_path
        self.db_path = cortex_repo_path / "cortex-brain" / "tier3" / "cortex-context.db"
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get CORTEX development context."""
        return {
            "cortex_git_metrics": self.get_git_metrics(),
            "cortex_hotspots": self.get_file_hotspots(),
            "cortex_test_coverage": self.get_test_coverage()
        }


# src/tier3/application_context.py
class ApplicationContext:
    """
    User application context intelligence.
    
    Tracks user workspace metrics:
    - User app git activity
    - User app file hotspots
    - User app test coverage
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.db_path = workspace_root / ".cortex" / "context" / "app-context.db"
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get user application context."""
        return {
            "app_git_metrics": self.get_git_metrics(),
            "app_hotspots": self.get_file_hotspots(),
            "app_test_coverage": self.get_test_coverage()
        }
```

---

### Phase 3: API Updates (6 hours)

**3.1 Update Agent System (2 hours)**

Update all 10 agents to use correct brain:

```python
class ExecutorAgent:
    def __init__(self, cortex_brain: CortexBrain, app_brain: ApplicationBrain):
        self.cortex_brain = cortex_brain  # CORTEX patterns
        self.app_brain = app_brain        # User app patterns
    
    def execute(self, request: str):
        # Query CORTEX patterns for execution strategy
        cortex_patterns = self.cortex_brain.query("execution_patterns")
        
        # Query user app patterns for context
        app_patterns = self.app_brain.query("architectural_patterns")
        
        # Execute with both contexts
        return self.implement_feature(cortex_patterns, app_patterns)
```

**3.2 Update Operations (2 hours)**

Update all operations to initialize both brains:

```python
# src/operations/orchestrator.py
class OperationsOrchestrator:
    def __init__(self, workspace_root: Path):
        cortex_root = Path(__file__).parent.parent.parent
        
        # Initialize CORTEX brain (framework knowledge)
        self.cortex_brain = CortexBrain(cortex_root)
        
        # Initialize application brain (user workspace knowledge)
        self.app_brain = ApplicationBrain(workspace_root)
    
    def execute_operation(self, operation_id: str):
        # Pass both brains to operation modules
        context = {
            "cortex_brain": self.cortex_brain,
            "app_brain": self.app_brain
        }
        
        return self.orchestrate(operation_id, context)
```

**3.3 Update Crawlers (2 hours)**

Ensure crawlers populate app brain (NOT CORTEX brain):

```python
# scripts/crawlers/test_crawler.py
class TestCrawler:
    def __init__(self, workspace_root: Path):
        # Crawlers write to APPLICATION brain, NOT CORTEX brain
        self.app_brain = ApplicationBrain(workspace_root)
    
    def crawl_tests(self):
        test_patterns = self.discover_test_patterns()
        
        # Save to USER app brain
        self.app_brain.learn_pattern({
            "type": "test_patterns",
            "patterns": test_patterns
        })
        
        # DO NOT save to cortex_brain!
```

---

### Phase 4: Testing (4 hours)

**4.1 Boundary Validation Tests (2 hours)**

Create `tests/tier2/test_knowledge_boundary_separation.py`:

```python
def test_cortex_brain_contains_only_cortex_knowledge():
    """Ensure CORTEX brain has no user app data."""
    cortex_brain = CortexBrain()
    patterns = cortex_brain.load_all_patterns()
    
    # Forbidden patterns
    assert "file_relationships" not in patterns
    assert "test_patterns" not in patterns
    assert "ui_component_structure" not in patterns
    
    # Allowed patterns
    assert "cortex_tier_architecture" in patterns
    assert "cortex_agent_patterns" in patterns


def test_app_brain_contains_only_user_app_knowledge():
    """Ensure app brain has no CORTEX framework data."""
    app_brain = ApplicationBrain(workspace_root=Path.cwd())
    patterns = app_brain.load_all_patterns()
    
    # Forbidden patterns
    assert "cortex_tier_architecture" not in patterns
    assert "cortex_agent_patterns" not in patterns
    
    # Allowed patterns
    assert "architectural_patterns" in patterns
    assert "file_relationships" in patterns


def test_boundary_enforcement_on_write():
    """Test runtime validation prevents cross-contamination."""
    cortex_brain = CortexBrain()
    
    # Should raise error
    with pytest.raises(ValueError, match="User app data not allowed"):
        cortex_brain.learn_pattern({
            "type": "file_relationships",
            "source": "user_app"
        })
```

**4.2 Integration Tests (2 hours)**

Create `tests/integration/test_dual_brain_workflow.py`:

```python
def test_executor_agent_uses_both_brains():
    """Test agent queries both brains correctly."""
    cortex_brain = CortexBrain()
    app_brain = ApplicationBrain(workspace_root=Path.cwd())
    
    executor = ExecutorAgent(cortex_brain, app_brain)
    
    # Query CORTEX patterns
    cortex_patterns = executor.cortex_brain.query("execution_patterns")
    assert "feature_implementation" in cortex_patterns
    
    # Query user app patterns
    app_patterns = executor.app_brain.query("architectural_patterns")
    assert "api_auth" in app_patterns  # User-specific


def test_setup_operation_initializes_both_brains():
    """Test setup creates both CORTEX and app brains."""
    workspace = Path.cwd() / "tests" / "fixtures" / "test-workspace"
    
    # Run setup
    execute_operation("environment_setup", workspace_root=workspace)
    
    # Verify CORTEX brain exists
    assert (workspace / "CORTEX" / "cortex-brain").exists()
    
    # Verify app brain exists
    assert (workspace / ".cortex" / "app-brain").exists()
```

---

### Phase 5: Documentation (4 hours)

**5.1 Update Architecture Docs (2 hours)**

Update:
- `cortex-brain/CORTEX-UNIFIED-ARCHITECTURE.yaml`
- `.github/copilot-instructions.md`
- `prompts/shared/technical-reference.md`

Add new section:

```markdown
## Knowledge Boundary Separation

CORTEX maintains TWO separate knowledge boundaries:

### 1. CORTEX Core Brain (Framework Knowledge)
- Location: `CORTEX_ROOT/cortex-brain/`
- Scope: CORTEX framework internals
- Contains: Tier 0-3 for CORTEX itself
- API: `CortexBrain.query()`

### 2. Application Brain (User Workspace Knowledge)
- Location: `<WORKSPACE>/.cortex/app-brain/`
- Scope: User's application
- Contains: App patterns, file relationships, context
- API: `ApplicationBrain.query()`

**Critical Rule:** These boundaries NEVER mix.
```

**5.2 Update Entry Point (1 hour)**

Update `.github/prompts/CORTEX.prompt.md`:

```markdown
## 🧠 Dual Brain Architecture

CORTEX maintains separate knowledge for:
1. **CORTEX Framework** (how CORTEX works)
2. **Your Application** (how your app works)

This separation ensures:
- ✅ CORTEX knowledge stays clean
- ✅ Your app knowledge stays isolated
- ✅ No cross-contamination
- ✅ Clear API boundaries

When you ask CORTEX to help with your app, it queries BOTH brains:
- CORTEX brain for "how to execute features" (framework strategy)
- App brain for "your app's architecture" (application context)
```

**5.3 Create Migration Guide (1 hour)**

Create `docs/migration/KNOWLEDGE-BOUNDARY-MIGRATION.md`:

```markdown
# Migrating to Dual Brain Architecture

## Why This Change?

CORTEX 2.0 originally mixed framework and application knowledge in a single brain. This caused:
- Contamination of CORTEX knowledge with user app data
- Unclear boundaries for crawlers
- Difficulty maintaining CORTEX across projects

CORTEX 2.1 separates these concerns.

## What Changes?

**Before (CORTEX 2.0):**
```
cortex-brain/knowledge-graph.yaml  # Mixed CORTEX + user patterns
```

**After (CORTEX 2.1):**
```
cortex-brain/tier2/cortex-knowledge-graph.yaml  # CORTEX patterns only
.cortex/app-brain/knowledge-graph.yaml          # User app patterns only
```

## How to Migrate

Run migration script:
```bash
python scripts/migrate_knowledge_boundaries.py
```

This will:
1. Scan CORTEX brain for user app data
2. Extract user app patterns
3. Save to `.cortex/app-brain/`
4. Clean CORTEX brain
5. Validate separation
```

---

### Phase 6: Validation & Cleanup (2 hours)

**6.1 Run Migration Script (30 minutes)**

Execute:
```bash
python scripts/migrate_knowledge_boundaries.py --validate
```

**6.2 Verify No User Data in CORTEX Brain (30 minutes)**

Manual audit:
- Review `cortex-brain/knowledge-graph.yaml`
- Review `cortex-brain/tier3/cortex-context.db`
- Ensure no user app references

**6.3 Update All Tests (1 hour)**

Ensure all 455 tests pass with new boundary separation:
```bash
pytest tests/
```

---

## 📈 Success Criteria

### ✅ Phase Completion Checklist

- [ ] **Phase 1:** Boundary contract defined, schemas designed
- [ ] **Phase 2:** Application brain infrastructure created, data migrated
- [ ] **Phase 3:** All agents/operations use both brains correctly
- [ ] **Phase 4:** 30+ boundary validation tests passing
- [ ] **Phase 5:** All documentation updated
- [ ] **Phase 6:** Migration validated, no user data in CORTEX brain

### ✅ Quality Gates

1. **Zero User App Data in CORTEX Brain**
   - `cortex-brain/knowledge-graph.yaml` contains ONLY CORTEX patterns
   - `cortex-brain/tier3/cortex-context.db` tracks ONLY CORTEX metrics

2. **Clear API Separation**
   - `CortexBrain.query()` returns ONLY CORTEX knowledge
   - `ApplicationBrain.query()` returns ONLY user app knowledge

3. **All Tests Passing**
   - 455 existing tests still pass
   - 30+ new boundary validation tests pass

4. **Documentation Complete**
   - Architecture docs explain dual brain
   - Entry point documents separation
   - Migration guide available

---

## 🔗 Integration with CORTEX 2.0 Design

### Updates to Key Documents

**1. CORTEX-2.0-IMPLEMENTATION-STATUS.md**

Add new section:
```markdown
## Phase 2.1: Knowledge Boundary Separation (NEW)

**Status:** In Progress  
**Duration:** 4-6 hours (estimated)  
**Deliverables:**
- Dual brain architecture (CORTEX core + Application)
- Data migration script
- API separation (CortexBrain vs ApplicationBrain)
- 30+ boundary validation tests

**Rationale:** Critical architecture fix to prevent knowledge contamination
```

**2. CORTEX-UNIFIED-ARCHITECTURE.yaml**

Update `core_components.brain_architecture`:

```yaml
brain_architecture:
  dual_boundary_model:
    description: "CORTEX maintains TWO separate knowledge boundaries"
    
    boundary_1_cortex_core:
      location: "cortex-brain/"
      scope: "CORTEX framework internals"
      api: "CortexBrain"
      
    boundary_2_application:
      location: ".cortex/app-brain/"
      scope: "User workspace knowledge"
      api: "ApplicationBrain"
    
    enforcement:
      - "Runtime validation prevents cross-contamination"
      - "Clear API separation (CortexBrain vs ApplicationBrain)"
      - "Migration script ensures clean separation"
```

**3. brain-protection-rules.yaml**

Add new Layer 6:

```yaml
Layer_6_Knowledge_Boundary_Protection:
  name: "Knowledge Boundary Enforcement"
  severity: BLOCKING
  
  rules:
    - rule_id: "BOUNDARY-001"
      name: "No User App Data in CORTEX Brain"
      description: "CORTEX brain must contain ONLY framework knowledge"
      check: "validate_cortex_brain_purity()"
      
    - rule_id: "BOUNDARY-002"
      name: "No CORTEX Framework Data in App Brain"
      description: "Application brain must contain ONLY user app knowledge"
      check: "validate_app_brain_isolation()"
```

---

## ⏱️ Time Estimate

| Phase | Estimated Time | Priority |
|-------|----------------|----------|
| Phase 1: Design & Specification | 4 hours | 🔴 CRITICAL |
| Phase 2: Implementation | 12 hours | 🔴 CRITICAL |
| Phase 3: API Updates | 6 hours | 🔴 CRITICAL |
| Phase 4: Testing | 4 hours | 🟡 HIGH |
| Phase 5: Documentation | 4 hours | 🟡 HIGH |
| Phase 6: Validation & Cleanup | 2 hours | 🟡 HIGH |
| **TOTAL** | **32 hours** | **~4 working days** |

---

## 🚨 Risks & Mitigations

### Risk 1: Breaking Existing Functionality
**Impact:** HIGH  
**Mitigation:** Comprehensive test coverage (455 existing + 30 new tests)

### Risk 2: Incomplete Data Migration
**Impact:** MEDIUM  
**Mitigation:** Validation script ensures no data left behind

### Risk 3: API Confusion
**Impact:** LOW  
**Mitigation:** Clear naming (`CortexBrain` vs `ApplicationBrain`), documentation

---

## 📝 Next Steps

1. **Review this drift plan** with stakeholders
2. **Approve architecture change** (dual brain model)
3. **Execute Phase 1** (design & specification)
4. **Create GitHub issue** tracking all 6 phases
5. **Begin implementation** (Phase 2)

---

**Author:** Asif Hussain  
**Date:** 2025-11-12  
**Status:** 🔴 CRITICAL - Requires Immediate Action  
**Estimated Completion:** 4 working days

---

*This drift plan connects to:*
- `CORTEX-2.0-IMPLEMENTATION-STATUS.md` (Phase 2.1 addition)
- `CORTEX-UNIFIED-ARCHITECTURE.yaml` (dual_boundary_model section)
- `brain-protection-rules.yaml` (Layer 6 enforcement)
- All Tier 2/Tier 3 API changes
