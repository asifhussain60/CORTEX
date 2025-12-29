# Task 6.13: Planning Orchestrator Migration - Implementation Plan

## 🧠 CORTEX Phase 6 Task 6.13 - Planning Orchestrator
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## 📊 Migration Analysis

### Orchestrator Selected
**Planning Orchestrator** - YAML-based feature planning with validation and autonomous execution

### Selection Rationale
- ✅ **Moderate Size**: 792 LOC (manageable scope)
- ✅ **Clear Phase Structure**: 5 phases (DISCOVERY→VALIDATION→GENERATION→RENDERING→EXECUTION)
- ✅ **Learning Potential**: Plan generation patterns can be learned and improved
- ✅ **Parallel Opportunity**: DoR/DoD validation can run in parallel
- ✅ **Quality Assessment**: Plans benefit from LLM-as-judge evaluation
- ✅ **High Value**: Core orchestrator used for all feature planning

### Current Implementation
| Metric | Value |
|--------|-------|
| **LOC** | 792 |
| **Phases** | 5 (DISCOVERY, VALIDATION, GENERATION, RENDERING, EXECUTION) |
| **Complexity Levels** | 4 (LOW, MEDIUM, HIGH, CRITICAL) |
| **Plan Types** | 4 (skeleton, conditional, incremental, folder_based) |
| **Dependencies** | PlanExecutor, PhaseManager, GitCheckpoint, SessionManager |

---

## 🎯 Agentic Enhancement Strategy

### 1. Multi-Agent Collaboration (DISCOVERY & VALIDATION Phases)
**Component:** `MultiAgentOrchestrator`
- **DISCOVERY Enhancement:**
  - Parallel context gathering across multiple sources
  - Concurrent architectural review and threat modeling
  - Multi-source duplicate detection
  - **Benefit:** 3-5x speedup for context discovery
  
- **VALIDATION Enhancement:**
  - Parallel DoR/DoD validation checks
  - Concurrent schema validation
  - Multi-criteria compliance checking
  - **Benefit:** 2-3x speedup for validation

### 2. Agent Learning Engine (GENERATION Phase)
**Component:** `AgentLearningEngine`
- **Learn from successful plans:**
  - Task breakdown patterns by complexity
  - Estimation accuracy patterns
  - Phase structure templates
  - Acceptance criteria patterns
- **Apply learned patterns:**
  - Suggest tasks based on similar features
  - Predict story points from historical data
  - Recommend phase dependencies
- **Benefit:** +30% plan quality, -40% generation time

### 3. Context Validator (GENERATION Phase)
**Component:** `ContextValidator`
- **Pre-generation validation:**
  - Validate feature description completeness
  - Check for ambiguous requirements
  - Verify prerequisite information available
  - Detect potential planning gaps
- **Benefit:** 100% prevention of incomplete plans

### 4. Agent Evaluator (RENDERING Phase)
**Component:** `AgentEvaluator`
- **Plan quality evaluation:**
  - **Completeness**: All necessary phases/tasks included
  - **Clarity**: Tasks and criteria are well-defined
  - **Feasibility**: Estimates are realistic
  - **Testability**: Clear acceptance criteria
  - **Maintainability**: Plan structure is logical
- **Benefit:** Objective quality scoring (0.0-1.0)

---

## 🏗️ Architecture Design

### Phase-by-Phase Enhancement

#### Phase 1: DISCOVERY (Agentic Enhanced)
```python
def _execute_discovery_phase_agentic(self, feature_name: str) -> Dict[str, Any]:
    """
    Multi-agent parallel context discovery.
    
    Agents:
    - Context Gatherer: Scan codebase for related functionality
    - Architectural Reviewer: Analyze architecture patterns
    - Threat Modeler: Identify security concerns
    - Duplicate Detector: Find similar existing features
    
    Speedup: 3-5x (parallel execution)
    """
    tasks = [
        DiscoveryTask("context", self._gather_context_async),
        DiscoveryTask("architecture", self._review_architecture_async),
        DiscoveryTask("threats", self._analyze_threats_async),
        DiscoveryTask("duplicates", self._detect_duplicates_async)
    ]
    
    results = await self.multi_agent.execute_parallel(tasks)
    
    return {
        'success': True,
        'context': results['context'],
        'architecture': results['architecture'],
        'threats': results['threats'],
        'duplicates': results['duplicates'],
        'speedup': calculate_speedup(results)
    }
```

#### Phase 2: VALIDATION (Agentic Enhanced)
```python
def _execute_validation_phase_agentic(self, discovery: Dict) -> Dict[str, Any]:
    """
    Parallel DoR/DoD validation with learning-enhanced checks.
    
    Validators (parallel):
    - DoR Checker: Validate definition of ready
    - DoD Checker: Validate definition of done
    - Schema Validator: YAML schema compliance
    - TDD Validator: TDD requirements compliance
    
    Speedup: 2-3x (parallel execution)
    """
    validation_tasks = [
        ValidationTask("dor", self._validate_dor_async),
        ValidationTask("dod", self._validate_dod_async),
        ValidationTask("schema", self._validate_schema_async),
        ValidationTask("tdd", self._validate_tdd_async)
    ]
    
    results = await self.multi_agent.execute_parallel(validation_tasks)
    
    # Use ContextValidator to ensure completeness
    context_quality = self.context_validator.validate(discovery)
    
    return {
        'success': all_passed(results),
        'dor_valid': results['dor'],
        'dod_valid': results['dod'],
        'schema_valid': results['schema'],
        'tdd_valid': results['tdd'],
        'context_quality': context_quality,
        'prevented_errors': count_prevented_errors(results)
    }
```

#### Phase 3: GENERATION (Agentic Enhanced)
```python
def _execute_generation_phase_agentic(
    self,
    feature_name: str,
    complexity: PlanComplexity,
    validation: Dict
) -> Dict[str, Any]:
    """
    Learning-enhanced plan generation.
    
    Enhancements:
    - Learn from historical plans
    - Apply learned task breakdown patterns
    - Predict story points from similar features
    - Recommend phase dependencies
    
    Quality Improvement: +30%
    """
    # Check learned patterns for similar features
    learned_patterns = self.learning_engine.retrieve_patterns(
        feature_type=classify_feature(feature_name),
        complexity=complexity
    )
    
    if learned_patterns:
        # Generate plan using learned patterns
        plan_data = self._generate_from_patterns(
            feature_name,
            complexity,
            learned_patterns
        )
    else:
        # Generate plan using heuristics
        plan_data = self._generate_from_heuristics(
            feature_name,
            complexity
        )
    
    # Evaluate plan quality
    quality_metrics = self._evaluate_plan_quality(plan_data)
    
    # Learn from high-quality plans
    if quality_metrics['overall_score'] >= 0.8:
        patterns_learned = self.learning_engine.learn_from_plan(
            plan_data,
            quality_metrics
        )
    
    return {
        'success': True,
        'plan_data': plan_data,
        'quality_metrics': quality_metrics,
        'patterns_learned': patterns_learned
    }
```

#### Phase 4: RENDERING (Agentic Enhanced)
```python
def _execute_rendering_phase_agentic(
    self,
    plan_data: PlanData,
    output_dir: Path
) -> Dict[str, Any]:
    """
    Plan rendering with quality evaluation.
    
    Evaluation Criteria:
    - Completeness (all sections present)
    - Clarity (tasks well-defined)
    - Feasibility (estimates realistic)
    - Testability (acceptance criteria clear)
    - Maintainability (structure logical)
    """
    # Render markdown
    markdown_path = self._render_markdown_file(plan_data, output_dir)
    
    # Evaluate plan quality using AgentEvaluator
    quality_evaluation = self.evaluator.evaluate(
        content=plan_data,
        criteria=[
            "completeness",
            "clarity",
            "feasibility",
            "testability",
            "maintainability"
        ]
    )
    
    return {
        'success': True,
        'markdown_path': markdown_path,
        'quality_score': quality_evaluation['overall_score'],
        'quality_breakdown': quality_evaluation
    }
```

---

## 📈 Expected Performance Improvements

### Speedup Analysis
| Phase | Original | Enhanced | Improvement |
|-------|----------|----------|-------------|
| **DISCOVERY** | Sequential | Parallel (4 agents) | **3-5x faster** |
| **VALIDATION** | Sequential | Parallel (4 validators) | **2-3x faster** |
| **GENERATION** | Heuristic | Learning-enhanced | **Quality +30%** |
| **RENDERING** | Basic | Quality-evaluated | **Clarity +40%** |
| **Overall** | Linear | Optimized | **2-4x faster** |

### Quality Improvements
| Metric | Original | Enhanced | Improvement |
|--------|----------|----------|-------------|
| **Plan Quality** | Heuristic (~0.6) | LLM-evaluated (~0.85) | **+42%** |
| **Task Breakdown** | Generic | Pattern-based | **+35%** |
| **Estimation Accuracy** | Rule-based | Historical | **+50%** |
| **Incomplete Plans** | Post-failure | Pre-validated | **100% prevented** |

---

## 🗂️ Data Models

### Learned Plan Pattern
```python
@dataclass
class PlanPattern:
    """Learned plan pattern for agent learning."""
    feature_type: str
    complexity: PlanComplexity
    task_breakdown: List[Dict[str, Any]]
    phase_structure: List[str]
    estimation_accuracy: float
    quality_score: float
    usage_count: int = 1
    success_rate: float = 1.0
```

### Discovery Task
```python
@dataclass
class DiscoveryTask:
    """Task definition for multi-agent discovery."""
    task_id: str
    task_type: str  # 'context', 'architecture', 'threats', 'duplicates'
    executor: Callable
    priority: int = 1
    timeout_seconds: int = 60
```

### Validation Task
```python
@dataclass
class ValidationTask:
    """Task definition for parallel validation."""
    task_id: str
    validation_type: str  # 'dor', 'dod', 'schema', 'tdd'
    validator: Callable
    priority: int = 1
    required: bool = True
```

---

## 🧪 Test Coverage Plan

### Test Class Structure

1. **TestMultiAgentDiscovery** (4 tests)
   - Parallel context gathering
   - Architectural review integration
   - Threat modeling integration
   - Duplicate detection

2. **TestParallelValidation** (4 tests)
   - Parallel DoR/DoD validation
   - Schema validation integration
   - TDD requirements validation
   - Context quality assessment

3. **TestLearningEnhancedGeneration** (5 tests)
   - Learn from historical plans
   - Apply learned patterns
   - Generate from heuristics (fallback)
   - Pattern storage and retrieval
   - Quality-based learning threshold

4. **TestPlanQualityEvaluation** (3 tests)
   - Multi-criteria quality scoring
   - Quality evaluation fallback
   - Quality threshold enforcement

5. **TestContextValidation** (3 tests)
   - Pre-generation completeness check
   - Ambiguity detection
   - Gap identification

6. **TestEndToEndWorkflow** (3 tests)
   - Complete planning workflow
   - Auto-execution integration
   - Session management integration

7. **TestAgenticMetrics** (2 tests)
   - Metrics collection structure
   - Metrics on failure preservation

8. **TestBaseOrchestratorIntegration** (3 tests)
   - Inheritance verification
   - Configuration injection
   - Engagement hints

---

## 📝 Implementation Checklist

### Phase 1: Core Structure
- [ ] Create `planning_orchestrator_v2_migrated.py`
- [ ] Import Phase 5 agentic components
- [ ] Define new data models (PlanPattern, DiscoveryTask, ValidationTask)
- [ ] Add `_initialize_agentic_components()` method
- [ ] Preserve existing domain models

### Phase 2: Agentic Phase Methods
- [ ] Implement `_execute_discovery_phase_agentic()`
- [ ] Implement `_execute_validation_phase_agentic()`
- [ ] Implement `_execute_generation_phase_agentic()`
- [ ] Implement `_execute_rendering_phase_agentic()`
- [ ] Add helper methods for pattern learning/retrieval

### Phase 3: Quality & Learning
- [ ] Implement `_evaluate_plan_quality()`
- [ ] Implement `_learn_from_plan()`
- [ ] Implement `_generate_from_patterns()`
- [ ] Implement `_filter_low_quality_patterns()`

### Phase 4: Metrics & Results
- [ ] Add `agentic_metrics` to `PlanningResult`
- [ ] Track `parallel_speedup`, `plan_quality`, `patterns_learned`
- [ ] Update success/failure result methods
- [ ] Add engagement hints (🎭)

### Phase 5: Testing
- [ ] Create test file with 8 test classes
- [ ] Implement 25+ test methods
- [ ] Mock agentic components
- [ ] Test end-to-end workflow

### Phase 6: Documentation
- [ ] Update docstrings to v2.0
- [ ] Document agentic enhancements
- [ ] Create usage examples
- [ ] Document migration guide

---

## 🎓 Key Design Decisions

### 1. Preserve Execution Engine
- Keep `PlanExecutor`, `PhaseManager`, `GitCheckpoint`, `SessionManager`
- Agentic enhancements are **additive**, not replacement
- Execution phase remains unchanged (deterministic)

### 2. Learning Scope
- Learn task breakdown patterns per feature type
- Learn estimation accuracy per complexity level
- Learn phase dependencies per plan type
- **Do NOT** learn DoR/DoD (these are governance)

### 3. Parallel Strategy
- DISCOVERY: 4 parallel agents (context, architecture, threats, duplicates)
- VALIDATION: 4 parallel validators (DoR, DoD, schema, TDD)
- GENERATION: Sequential (learning requires historical context)
- RENDERING: Sequential (single file generation)

### 4. Quality Threshold
- Only learn from plans with quality score >= 0.8
- Require minimum 3 usage instances before applying pattern
- Fallback to heuristics if no learned patterns available

---

## 🚀 Expected Impact

### Developer Experience
- **Faster Planning**: 2-4x speedup for complete planning workflow
- **Higher Quality**: +30% improvement in plan quality scores
- **Better Estimates**: +50% estimation accuracy from learned patterns
- **Fewer Errors**: 100% prevention of incomplete plans

### System Benefits
- **Pattern Reuse**: Learn once, apply everywhere
- **Continuous Improvement**: Quality improves over time
- **Scalability**: Parallel processing handles large features
- **Consistency**: Learned patterns ensure consistent structure

---

## 📊 Migration Timeline

### Estimated Effort
- **Core Implementation**: 4-6 hours
- **Test Suite**: 2-3 hours
- **Documentation**: 1-2 hours
- **Total**: 7-11 hours

### Complexity Assessment
- **Code Volume**: ~1200 LOC (orchestrator) + ~600 LOC (tests)
- **Integration Points**: 4 agentic components + 4 existing modules
- **Risk Level**: MEDIUM (complex but follows established pattern)

---

## ✅ Success Criteria

1. ✅ **Functional**: All 5 phases execute with agentic enhancements
2. ✅ **Performance**: Measurable speedup (2-4x overall)
3. ✅ **Quality**: Plan quality scores improve (+30%)
4. ✅ **Learning**: Patterns stored and retrieved successfully
5. ✅ **Testing**: 95%+ code coverage with 25+ tests
6. ✅ **Documentation**: Complete API docs and migration guide
7. ✅ **Integration**: Clean integration with existing execution engine

---

**Status:** 📋 READY FOR IMPLEMENTATION

**Next Step:** Create `planning_orchestrator_v2_migrated.py` with agentic enhancements

**Estimated Completion:** 7-11 hours of focused development
