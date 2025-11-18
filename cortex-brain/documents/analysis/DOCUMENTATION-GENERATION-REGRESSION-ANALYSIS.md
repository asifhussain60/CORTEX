# Documentation Generation Regression Analysis

**Date:** November 18, 2025  
**Issue:** Only 7 diagram files generated instead of expected 17  
**Severity:** HIGH - Core documentation functionality compromised  
**Status:** Root cause identified, fix in progress

---

## Executive Summary

The documentation generation system is only producing 7 diagram files (prompts + narratives) instead of the expected 17. This regression occurred because:

1. The `ImagePromptGenerator` class only generates 7 diagrams (hard-coded)
2. The test suite only validates 6 diagrams, missing the regression
3. The `regenerate_diagrams.py` script has definitions for 17 diagrams but isn't being used
4. No integration test validates diagram count against the feature list

---

## Current State

### Files Present (7 total)
Located in `docs/diagrams/`:

**Prompts:**
1. `01-tier-architecture.md` ✅
2. `02-agent-system.md` ✅
3. `03-plugin-architecture.md` ✅
4. `04-memory-flow.md` ✅
5. `05-agent-coordination.md` ✅
6. `06-basement-scene.md` ✅
7. `07-cortex-one-pager.md` ✅

**Narratives:** Same 7 files exist

---

## Missing Files (10 total)

### From Git History (Commit 817ad55)
These files existed before but were lost:

8. `08-knowledge-graph.md` ❌
9. `09-context-intelligence.md` ❌
10. `10-feature-planning.md` ❌
11. `11-performance-benchmarks.md` ❌
12. `12-token-optimization.md` ❌
13. `13-plugin-system.md` ❌
14. `14-data-flow-complete.md` ❌
15. `15-before-vs-after.md` ❌
16. `16-technical-documentation.md` ❌
17. `17-executive-feature-list.md` ❌

---

## Root Cause Analysis

### 1. ImagePromptGenerator Hard-Coded Limit

**Location:** `src/epm/modules/image_prompt_generator.py` (lines 87-109)

```python
def generate_all(self, capabilities, modules):
    # Generate each diagram type
    results = {}
    
    # 1. Tier Architecture (16:9)
    results['tier_architecture'] = self._generate_tier_architecture(tiers)
    
    # 2. Agent System (1:1)
    results['agent_system'] = self._generate_agent_system(agents)
    
    # 3. Plugin Architecture (1:1)
    results['plugin_architecture'] = self._generate_plugin_architecture(plugins)
    
    # 4. Memory Flow (16:9)
    results['memory_flow'] = self._generate_memory_flow(tiers)
    
    # 5. Agent Coordination (9:16)
    results['agent_coordination'] = self._generate_agent_coordination(agents)
    
    # 6. Basement Scene (16:9, optional)
    results['basement_scene'] = self._generate_basement_scene()
    
    # 7. One-Pager (16:9, landscape)
    results['one_pager'] = self._generate_one_pager(capabilities, agents, plugins)
    
    # ❌ STOPS HERE - Missing diagrams 8-17
```

**Problem:** Only 7 diagrams are generated. The additional 10 diagrams are never created.

---

### 2. Test Suite Doesn't Catch Regression

**Location:** `tests/epm/test_image_prompt_integration.py` (line 207)

```python
def test_all_six_diagrams_generated(self):
    """Test that all 6 diagram types are generated"""
    # ❌ Test only checks for 6 diagrams, not 17
    expected_ids = [
        "01-tier-architecture",
        "02-agent-system",
        "03-plugin-architecture",
        "04-memory-flow",
        "05-agent-coordination",
        "06-basement-scene"
    ]
    # Missing: 07-cortex-one-pager through 17-executive-feature-list
```

**Problem:** Test validates 6 diagrams but generator creates 7, and neither checks for all 17.

---

### 3. Diagram Definitions Not Used

**Location:** `cortex-brain/doc-generation-config/diagram-definitions.yaml`

This file defines 13 strategic/architectural/operational diagrams but:
- ❌ Not used by `ImagePromptGenerator`
- ❌ Only used by `DiagramGenerator` (which generates Mermaid, not prompts)
- ❌ Doesn't include all 17 diagrams from feature list

---

### 4. No Authoritative Source of Truth

**Problem:** Three different sources define different diagram counts:

| Source | Diagram Count | Used By |
|--------|--------------|---------|
| `ImagePromptGenerator.generate_all()` | 7 | EPM doc generation |
| `regenerate_diagrams.py` | 17 | Manual script (not integrated) |
| `diagram-definitions.yaml` | 13 | DiagramGenerator (Mermaid only) |
| `test_image_prompt_integration.py` | 6 | Test validation |

**No single source of truth** = Different parts of the system have different expectations.

---

## Why This Wasn't Protected By Tests

### Test Gaps Identified

1. **No Feature List Validation Test**
   - Missing: Test that validates diagram count against authoritative feature list
   - Should exist: `tests/epm/test_diagram_completeness.py`

2. **No Integration Test for Full Suite**
   - Missing: Test that runs full doc generation and validates all outputs
   - Should exist: `tests/operations/test_enterprise_documentation_completeness.py`

3. **Hard-Coded Expected Values**
   - Problem: Tests use hard-coded lists instead of reading from config
   - Solution: Tests should read expected diagrams from YAML config

4. **No Mermaid Diagram Tests**
   - Missing: Tests for Mermaid diagram generation
   - Should exist: `tests/epm/test_mermaid_diagram_generation.py`

---

## Impact Analysis

### User Impact
- **Documentation completeness:** Only 41% of diagrams generated (7/17)
- **Feature coverage:** Missing critical visualizations:
  - Knowledge Graph (Tier 2)
  - Context Intelligence (Tier 3)
  - Performance benchmarks
  - Token optimization strategy
  - Technical documentation
  - Executive feature list

### System Impact
- **EPM pipeline:** Appears successful but produces incomplete output
- **Quality metrics:** No validation catches missing files
- **Regression detection:** Silent failure - no errors or warnings

---

## Recommended Fixes

### Phase 1: Immediate Fixes (High Priority)

#### 1.1 Add Missing Diagram Generators
**File:** `src/epm/modules/image_prompt_generator.py`

Add methods for diagrams 8-17:
```python
# 8. Knowledge Graph
results['knowledge_graph'] = self._generate_knowledge_graph(tiers)

# 9. Context Intelligence
results['context_intelligence'] = self._generate_context_intelligence(tiers)

# 10. Feature Planning
results['feature_planning'] = self._generate_feature_planning()

# 11. Performance Benchmarks
results['performance_benchmarks'] = self._generate_performance_benchmarks()

# 12. Token Optimization
results['token_optimization'] = self._generate_token_optimization()

# 13. Plugin System
results['plugin_system'] = self._generate_plugin_system_detailed(plugins)

# 14. Complete Data Flow
results['data_flow_complete'] = self._generate_complete_data_flow(tiers)

# 15. Before vs After
results['before_after'] = self._generate_before_after_comparison()

# 16. Technical Documentation
results['technical_docs'] = self._generate_technical_documentation()

# 17. Executive Feature List
results['executive_features'] = self._generate_executive_feature_list(capabilities)
```

**Estimated Time:** 4-6 hours

---

#### 1.2 Create Master Diagram Configuration
**File:** `cortex-brain/doc-generation-config/master-diagram-list.yaml`

```yaml
version: "1.0"
description: "Authoritative list of all CORTEX diagrams"

diagrams:
  - id: "01"
    name: "tier-architecture"
    title: "4-Tier Brain Architecture"
    type: "architecture"
    format: "16:9"
    required: true
    
  - id: "02"
    name: "agent-system"
    title: "10 Specialized Agents"
    type: "system"
    format: "1:1"
    required: true
    
  # ... (complete list of 17)
```

**Estimated Time:** 1 hour

---

#### 1.3 Update Tests to Use Config
**File:** `tests/epm/test_image_prompt_integration.py`

```python
def test_all_diagrams_generated(self):
    """Test that ALL diagrams from master config are generated"""
    # Load expected diagrams from config
    config_path = Path("cortex-brain/doc-generation-config/master-diagram-list.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    expected_ids = [d['id'] + '-' + d['name'] for d in config['diagrams']]
    
    # Generate diagrams
    result = self.generator.generate_all(capabilities, modules)
    
    # Validate ALL diagrams were created
    for diagram_id in expected_ids:
        prompt_file = prompts_dir / f"{diagram_id}.md"
        self.assertTrue(prompt_file.exists(), f"Missing prompt: {diagram_id}.md")
        
        narrative_file = narratives_dir / f"{diagram_id}.md"
        self.assertTrue(narrative_file.exists(), f"Missing narrative: {diagram_id}.md")
```

**Estimated Time:** 2 hours

---

### Phase 2: Comprehensive Tests (Medium Priority)

#### 2.1 Create Diagram Completeness Test
**File:** `tests/epm/test_diagram_completeness.py`

Validates:
- All diagrams in config are generated
- No extra diagrams are generated
- Prompts and narratives match
- Image paths are valid
- README and STYLE-GUIDE exist

**Estimated Time:** 3 hours

---

#### 2.2 Create Mermaid Diagram Test
**File:** `tests/epm/test_mermaid_diagram_generation.py`

Validates:
- Mermaid syntax is valid
- All diagrams have corresponding Mermaid files
- Diagrams render without errors

**Estimated Time:** 2 hours

---

#### 2.3 Create End-to-End Integration Test
**File:** `tests/operations/test_enterprise_documentation_e2e.py`

Validates:
- Full documentation generation pipeline
- All expected files are created
- Quality metrics are accurate
- No regressions in file count

**Estimated Time:** 4 hours

---

### Phase 3: Architecture Improvements (Low Priority)

#### 3.1 Unify Diagram Definitions

Consolidate:
- `ImagePromptGenerator.generate_all()` → Read from config
- `regenerate_diagrams.py` → Read from config
- `diagram-definitions.yaml` → Merge into master config

**Benefit:** Single source of truth

**Estimated Time:** 3 hours

---

#### 3.2 Add Diagram Discovery

Auto-detect diagrams from:
- Feature list documents
- Capabilities.yaml
- Module definitions

**Benefit:** Automatic diagram generation based on features

**Estimated Time:** 6 hours

---

## Timeline

### Sprint 1 (This Week)
- ✅ Root cause analysis (DONE)
- 🔄 Create master diagram config (1 hour)
- 🔄 Add missing diagram generators (4-6 hours)
- 🔄 Update tests to use config (2 hours)
- 🔄 Run full test suite (1 hour)

**Total:** 8-10 hours

### Sprint 2 (Next Week)
- Create comprehensive test suite (9 hours)
- Run regression tests (2 hours)

**Total:** 11 hours

### Sprint 3 (Future)
- Architecture improvements (9 hours)

---

## Success Criteria

### Phase 1 Complete When:
- ✅ All 17 diagrams generate successfully
- ✅ Tests validate all 17 diagrams
- ✅ Master config file exists
- ✅ No test failures

### Phase 2 Complete When:
- ✅ Comprehensive test coverage (>90%)
- ✅ Mermaid diagrams validated
- ✅ E2E tests pass

### Phase 3 Complete When:
- ✅ Single source of truth for diagrams
- ✅ Auto-discovery implemented
- ✅ Documentation updated

---

## Lessons Learned

1. **Always validate against source of truth:** Don't hard-code expected values in tests
2. **Test the complete flow:** Unit tests passed but integration failed
3. **Monitor file counts:** Add assertions for expected file counts
4. **Use configuration:** External config files prevent regressions
5. **Single source of truth:** Multiple definitions = guaranteed drift

---

## Related Files

### Source Code
- `src/epm/modules/image_prompt_generator.py` (needs 10 new generators)
- `src/epm/modules/diagram_generator.py` (Mermaid only)
- `scripts/regenerate_diagrams.py` (has correct list)

### Configuration
- `cortex-brain/doc-generation-config/diagram-definitions.yaml` (incomplete)
- Need: `cortex-brain/doc-generation-config/master-diagram-list.yaml`

### Tests
- `tests/epm/test_image_prompt_integration.py` (only checks 6)
- Need: `tests/epm/test_diagram_completeness.py`
- Need: `tests/epm/test_mermaid_diagram_generation.py`
- Need: `tests/operations/test_enterprise_documentation_e2e.py`

---

**Author:** Asif Hussain (via CORTEX Analysis)  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
