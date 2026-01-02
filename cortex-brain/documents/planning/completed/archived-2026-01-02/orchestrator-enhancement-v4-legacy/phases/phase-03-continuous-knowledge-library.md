# Phase 3: Continuous Knowledge Library Integration

**[← Back to Master Plan](../00-MASTER-PLAN.md)** | **[Previous: Orchestrator Validation](phase-02-orchestrator-validation.md)** | **[Next: Progress Rendering →](phase-04-progress-rendering.md)**

---

## 📋 Phase Overview

| Attribute | Value |
|-----------|-------|
| **Phase ID** | 3 |
| **Name** | Continuous Knowledge Library Integration |
| **Status** | ⏸️ Not Started |
| **Duration** | ~1 week |
| **Tasks Complete** | 0/10 (0%) |
| **Dependencies** | Phase 2 (Orchestrator Validation) |

---

## 🎯 Objective

Implement **continuous knowledge library integration** - query the knowledge library at **every phase** (not just Phase -1), and **extract patterns back to the library** after each phase completes.

**Key Innovation:** This transforms the knowledge library from a static reference to a **living, growing knowledge base** that learns from every plan execution.

---

## 📊 Progress Tracker

**Phase Progress:** `░░░░░░░░░░` **0%** ⏸️ NOT STARTED

| Task ID | Task | Status | Duration |
|---------|------|--------|----------|
| 3.1 | Design knowledge library query API | ⏸️ Not Started | 4h |
| 3.2 | Implement `_query_knowledge_library_for_phase()` | ⏸️ Not Started | 6h |
| 3.3 | Add keyword detection for phase context | ⏸️ Not Started | 3h |
| 3.4 | Implement pattern extraction logic | ⏸️ Not Started | 8h |
| 3.5 | Design brain tier update schema | ⏸️ Not Started | 4h |
| 3.6 | Implement Tier 2 knowledge graph updates | ⏸️ Not Started | 8h |
| 3.7 | Implement Tier 3 dev context updates | ⏸️ Not Started | 6h |
| 3.8 | Add obsolete pattern detection | ⏸️ Not Started | 6h |
| 3.9 | Implement atomic replacement (no orphaned refs) | ⏸️ Not Started | 6h |
| 3.10 | Write tests for continuous integration | ⏸️ Not Started | 8h |

**Total:** 59 hours (~1 week)

---

## 🔍 Architecture: Continuous Knowledge Library Loop

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CONTINUOUS KNOWLEDGE LIBRARY LOOP                │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ Phase -1: Initial Knowledge Library Consultation                    │
│   ├─ Query: orchestrator patterns, invocation, progress, brain tiers│
│   └─ Output: 5 context files extracted                              │
└──────────────────┬───────────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Phase 0: Discovery                                                   │
│   ├─ Query KL: "discovery patterns", "root cause analysis"          │
│   ├─ Execute phase with enriched context                            │
│   └─ Extract: discovery workflow patterns → KL                      │
└──────────────────┬───────────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Phase 1: Invocation Bridge                                          │
│   ├─ Query KL: "mcp tool patterns", "tool invocation"               │
│   ├─ Execute phase with enriched context                            │
│   └─ Extract: MCP tool implementation patterns → KL                 │
└──────────────────┬───────────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Phase 2: Orchestrator Validation                                    │
│   ├─ Query KL: "validation patterns", "auto-healing"                │
│   ├─ Execute phase with enriched context                            │
│   └─ Extract: validation + auto-healing patterns → KL               │
└──────────────────┬───────────────────────────────────────────────────┘
                   │
                   ▼
                  ...
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Phase 11: Knowledge Extraction (Final)                              │
│   ├─ Aggregate ALL patterns from ALL phases                         │
│   ├─ Update Tier 2 knowledge graph (bidirectional links)            │
│   ├─ Update Tier 3 dev context (module registry)                    │
│   └─ Detect and replace obsolete patterns                           │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Implementation Tasks

### Task 3.1: Design Knowledge Library Query API (4h)

**Specification:**
```python
# src/orchestrators/planning/knowledge_library_integration.py

class KnowledgeLibraryIntegrator:
    """
    Continuous knowledge library integration for planning orchestrator.
    """
    
    def query_for_phase(
        self,
        phase_num: int,
        phase_name: str,
        keywords: List[str],
        previous_context: dict = None
    ) -> KnowledgeLibraryContext:
        """
        Query knowledge library for phase-specific patterns.
        
        Args:
            phase_num: Phase number (0-12)
            phase_name: Human-readable phase name
            keywords: Domain keywords (e.g., ["mcp tool", "invocation"])
            previous_context: Context from previous phases
        
        Returns:
            KnowledgeLibraryContext with:
            - files: List of relevant KL files
            - patterns: Extracted patterns
            - examples: Code examples
            - anti_patterns: What to avoid
        """
        pass
    
    def extract_patterns_from_phase(
        self,
        phase_num: int,
        artifacts: List[PhaseArtifact],
        implementation_files: List[str]
    ) -> List[ExtractedPattern]:
        """
        Extract reusable patterns from phase implementation.
        
        Args:
            phase_num: Phase number
            artifacts: Phase artifacts (specs, diagrams, etc.)
            implementation_files: Python files created
        
        Returns:
            List of patterns to add to knowledge library
        """
        pass
    
    def update_brain_tiers(
        self,
        extracted_patterns: List[ExtractedPattern],
        obsolete_patterns: List[str] = None
    ) -> BrainTierUpdateResult:
        """
        Update Tier 2/3 with extracted patterns.
        
        Updates:
        - Tier 2: knowledge-graph.yaml (pattern relationships)
        - Tier 3: development-context.yaml (module registry)
        - Tier 3: lessons-learned.yaml (what worked/didn't)
        
        Returns:
            Update report with changes made
        """
        pass
```

**Deliverable:** API specification document

---

### Task 3.2: Implement `_query_knowledge_library_for_phase()` (6h)

**Integration Point:**
```python
# src/orchestrators/planning/planning_orchestrator.py

class PlanningOrchestrator(BaseOrchestrator):
    
    def _execute_autonomous_mode(self, **kwargs) -> OrchestratorResult:
        # Phase -1: Initial consultation (existing)
        self._phase_minus_one_knowledge_consultation(kwargs)
        
        # NEW: Query before EACH phase
        for phase in self.phases:
            # Query knowledge library for phase-specific patterns
            kl_context = self.kl_integrator.query_for_phase(
                phase_num=phase.phase_num,
                phase_name=phase.name,
                keywords=phase.keywords,
                previous_context=self.context
            )
            
            # Merge with existing context
            self.context.update(kl_context)
            
            # Log what was found
            self.logger.info(
                f"✅ Knowledge Library: Loaded {len(kl_context.files)} files "
                f"for Phase {phase.phase_num} ({len(kl_context.patterns)} patterns)"
            )
            
            # Execute phase with enriched context
            phase_result = self._execute_phase(phase)
            
            # Extract patterns back to knowledge library
            extracted = self.kl_integrator.extract_patterns_from_phase(
                phase_num=phase.phase_num,
                artifacts=phase_result.artifacts,
                implementation_files=phase_result.files_created
            )
            
            # Log extraction
            self.logger.info(
                f"✅ Knowledge Extraction: Extracted {len(extracted)} patterns "
                f"from Phase {phase.phase_num}"
            )
```

**Deliverable:** Working implementation with logging

---

### Task 3.3: Add Keyword Detection for Phase Context (3h)

**Specification:**
```python
# Automatic keyword detection from phase name + description

PHASE_KEYWORD_MAP = {
    "Invocation Bridge": ["mcp tool", "tool invocation", "orchestrator execution", "hand-off"],
    "Orchestrator Validation": ["validation", "auto-healing", "compliance", "governance"],
    "Progress Rendering": ["progress bar", "visual tracking", "real-time updates"],
    "Hierarchical Structure": ["master plan", "sub-files", "2-way linking", "navigation"],
    "Brain Tier Updates": ["knowledge graph", "dev context", "obsolete data", "tier updates"],
    # ...
}

def detect_keywords_for_phase(phase_name: str, phase_description: str) -> List[str]:
    """Auto-detect keywords from phase metadata."""
    keywords = PHASE_KEYWORD_MAP.get(phase_name, [])
    
    # Add description keywords
    if "MCP" in phase_description:
        keywords.append("mcp tool")
    if "validation" in phase_description.lower():
        keywords.append("validation")
    # ...
    
    return list(set(keywords))  # Deduplicate
```

**Deliverable:** Keyword detection implementation

---

### Task 3.4: Implement Pattern Extraction Logic (8h)

**Specification:**
```python
# src/orchestrators/planning/pattern_extractor.py

class PatternExtractor:
    """
    Extract reusable patterns from phase implementation.
    """
    
    def extract_from_code(self, file_path: str) -> List[CodePattern]:
        """
        Extract patterns from Python code.
        
        Detects:
        - Class patterns (inheritance, composition)
        - Method patterns (decorators, signatures)
        - Design patterns (factory, singleton, etc.)
        """
        pass
    
    def extract_from_spec(self, spec_path: str) -> List[SpecPattern]:
        """
        Extract patterns from specification documents.
        
        Detects:
        - API contracts
        - Data schemas
        - Workflow diagrams
        """
        pass
    
    def extract_from_artifacts(self, artifacts: List[PhaseArtifact]) -> List[Pattern]:
        """
        Extract patterns from phase artifacts.
        
        Aggregates:
        - Code patterns
        - Spec patterns
        - Implementation decisions (what worked/didn't)
        """
        pass
```

**Deliverable:** Pattern extraction module

---

### Task 3.5: Design Brain Tier Update Schema (4h)

**Specification:**
```yaml
# Brain Tier Update Schema

brain_tier_update:
  version: "1.0"
  timestamp: "2026-01-02T10:30:00Z"
  plan_id: "planning-system-v5-implementation"
  phase_num: 1
  
  tier_2_updates:
    knowledge_graph:
      new_nodes:
        - id: "mcp_tool_pattern"
          type: "pattern"
          domain: "integration"
          description: "MCP tool decorator pattern for orchestrator invocation"
          related_to: ["orchestrator_pattern", "tool_invocation"]
          
      new_edges:
        - from: "mcp_tool_pattern"
          to: "orchestrator_pattern"
          relationship: "implements"
          
      obsolete_nodes:
        - id: "terminal_wrapper_pattern"  # Replaced by MCP tool
          reason: "MCP tool is more robust and type-safe"
          replaced_by: "mcp_tool_pattern"
  
  tier_3_updates:
    development_context:
      new_modules:
        - name: "src.mcp.tools.orchestrator_invocation"
          type: "mcp_tool"
          purpose: "Orchestrator invocation bridge"
          dependencies: ["src.orchestrators.base"]
          
      obsolete_modules:
        - name: "src.utils.terminal_wrapper"  # Deprecated
          reason: "Replaced by MCP tool pattern"
    
    lessons_learned:
      - lesson: "MCP tools provide better observability than terminal wrappers"
        phase: 1
        category: "integration"
        confidence: "high"
```

**Deliverable:** Schema documentation + validation schema

---

### Task 3.6: Implement Tier 2 Knowledge Graph Updates (8h)

**Implementation:**
```python
# src/brain/tier2/knowledge_graph_updater.py

class KnowledgeGraphUpdater:
    """
    Update Tier 2 knowledge graph with new patterns.
    """
    
    def add_pattern_node(
        self,
        pattern: ExtractedPattern,
        related_patterns: List[str] = None
    ) -> NodeID:
        """
        Add pattern node to knowledge graph.
        
        Creates:
        - Pattern node
        - Bidirectional edges to related patterns
        - Metadata (source, timestamp, confidence)
        """
        pass
    
    def replace_obsolete_pattern(
        self,
        obsolete_pattern_id: str,
        new_pattern_id: str,
        reason: str
    ) -> ReplacementReport:
        """
        Atomically replace obsolete pattern with new one.
        
        Steps:
        1. Find all references to obsolete pattern
        2. Update references to point to new pattern
        3. Mark obsolete pattern as deprecated
        4. Add deprecation note with reason
        5. Verify no orphaned references
        """
        pass
```

**Deliverable:** Knowledge graph updater module

---

### Task 3.7: Implement Tier 3 Dev Context Updates (6h)

**Implementation:**
```python
# src/brain/tier3/dev_context_updater.py

class DevContextUpdater:
    """
    Update Tier 3 development context with module registry changes.
    """
    
    def register_new_module(
        self,
        module_path: str,
        module_type: str,
        purpose: str,
        dependencies: List[str]
    ) -> None:
        """
        Register new module in development-context.yaml.
        """
        pass
    
    def update_file_relationships(
        self,
        file_path: str,
        imports: List[str],
        imported_by: List[str]
    ) -> None:
        """
        Update file-relationships.yaml with new dependencies.
        """
        pass
    
    def add_lesson_learned(
        self,
        lesson: str,
        phase: int,
        category: str,
        confidence: str
    ) -> None:
        """
        Add lesson to lessons-learned.yaml.
        """
        pass
```

**Deliverable:** Dev context updater module

---

## ✅ Acceptance Criteria

- [ ] Knowledge library queried at **every phase** (not just Phase -1)
- [ ] Patterns extracted after **every phase** completion
- [ ] Tier 2 knowledge graph updated automatically
- [ ] Tier 3 dev context updated automatically
- [ ] Obsolete patterns detected and replaced atomically
- [ ] No orphaned references after pattern replacement
- [ ] Performance <2s per knowledge library query
- [ ] All tests passing (unit, integration)

---

## 📊 Expected Impact

| Metric | Before (Phase -1 only) | After (Continuous) |
|--------|------------------------|-------------------|
| Knowledge Library Queries | 1 (Phase -1) | 13 (every phase) |
| Patterns Extracted | Manual | Automatic |
| Brain Tier Updates | Manual | Automatic |
| Knowledge Library Growth | Stagnant | Living, growing |
| Pattern Reuse Rate | ~20% | ~80% (target) |

---

## 🚀 Next Phase

**[Phase 4: Maintenance-Style Progress Rendering →](phase-04-progress-rendering.md)**

In the next phase, we'll implement real-time visual progress updates matching the maintenance orchestrator execution pattern.

---

**[← Back to Master Plan](../00-MASTER-PLAN.md)** | **[Previous: Orchestrator Validation](phase-02-orchestrator-validation.md)**
