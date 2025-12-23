# CORTEX 3.0: Intelligent Question Routing & Dynamic Context Collection

**Feature:** Dynamic question detection with namespace-aware routing and fresh context analysis  
**Version:** 3.0 (Future Enhancement)  
**Status:** 📋 DESIGN PHASE  
**Foundation:** Built on CORTEX 2.0 response templates  
**Author:** Asif Hussain  
**Date:** 2025-11-12

---

## 🎯 Problem Statement

**User asks:** "How is the brain doing?" or "What's my code quality?"

**Current CORTEX 2.0 behavior:**
- ✅ Static templates with `context_needed: true`
- ✅ Manual trigger matching
- ✅ Pre-defined data collectors
- ⚠️ Limited to exact trigger phrases
- ⚠️ No intelligent namespace detection
- ⚠️ No dynamic question classification

**Desired CORTEX 3.0 behavior:**
- ✅ **Intelligent question detection** (CORTEX vs application)
- ✅ **Dynamic namespace routing** (cortex.* vs workspace.*)
- ✅ **Fresh context analysis** (real-time metrics)
- ✅ **Adaptive template selection** (based on question type)
- ✅ **Smart collector orchestration** (only gather needed data)

---

## 🏗️ Architecture Overview

### High-Level Flow

```
User Question
    ↓
┌─────────────────────────────────────┐
│  QuestionRouter                     │
│  ├─ Classify question type          │
│  ├─ Detect namespace (CORTEX vs app)│
│  └─ Select appropriate template     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  CollectorOrchestrator              │
│  ├─ Determine required collectors   │
│  ├─ Execute in parallel             │
│  └─ Aggregate results               │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  TemplatePopulator                  │
│  ├─ Load selected template          │
│  ├─ Inject collected data           │
│  └─ Format response                 │
└─────────────────────────────────────┘
    ↓
Formatted Response
```

### Component Hierarchy

```
src/cortex_agents/strategic/
├── intent_router.py (existing - enhanced)
├── question_router.py (NEW - 3.0)
└── question_classifier.py (NEW - 3.0)

src/context_collectors/ (NEW directory)
├── base_collector.py
├── orchestrator.py
├── brain_metrics_collector.py
├── token_optimization_collector.py
├── workspace_health_collector.py
├── test_coverage_collector.py
├── git_metrics_collector.py
├── namespace_detector.py
└── learning_rate_calculator.py

src/template_engine/ (NEW directory)
├── template_loader.py
├── template_populator.py
└── response_formatter.py
```

---

## 📋 Component Specifications

### 1. QuestionRouter (Core Intelligence)

**Responsibilities:**
- Classify question type (status, capability, comparison, metrics)
- Detect namespace context (CORTEX framework vs user workspace)
- Route to appropriate collectors
- Select response template

**API:**

```python
class QuestionRouter:
    """
    Routes user questions to appropriate namespace and collectors.
    
    Example:
        router = QuestionRouter(tier1, tier2, tier3)
        
        result = router.route_question("How is the brain doing?")
        # Returns: {
        #   "question_type": QuestionType.CORTEX_STATUS,
        #   "namespace": "cortex.*",
        #   "collectors": ["brain_metrics", "token_optimization"],
        #   "template_id": "question_about_cortex_general",
        #   "confidence": 0.95
        # }
    """
    
    def route_question(self, question: str) -> QuestionRoutingResult:
        """
        Analyze question and determine routing.
        
        Args:
            question: User's question
        
        Returns:
            QuestionRoutingResult with type, namespace, collectors, template
        """
        
    def classify_question_type(self, question: str) -> QuestionType:
        """
        Classify question into predefined types.
        
        Types:
        - CORTEX_STATUS: "How is CORTEX doing?"
        - WORKSPACE_STATUS: "How is my project?"
        - CORTEX_CAPABILITY: "Can CORTEX do X?"
        - WORKSPACE_QUALITY: "What's my code quality?"
        - CORTEX_LEARNING: "What did CORTEX learn?"
        - NAMESPACE_INFO: "Which namespace am I in?"
        - COST_ANALYSIS: "How much am I saving?"
        - COMPARISON: "CORTEX vs Copilot?"
        """
        
    def detect_namespace(self, question: str, current_file: str = None) -> str:
        """
        Detect whether question is about CORTEX or workspace.
        
        Detection strategies:
        1. Keyword matching (cortex, brain, framework vs project, code, app)
        2. Current file context (src/tier* = cortex, src/myapp = workspace)
        3. Recent conversation history (what was discussed?)
        4. Explicit namespace mention
        
        Returns:
            - "cortex.*" for framework questions
            - "workspace.<project>.*" for application questions
        """
        
    def select_template(self, question_type: QuestionType) -> str:
        """Select appropriate response template based on question type."""
        
    def determine_collectors(
        self, 
        question_type: QuestionType,
        namespace: str
    ) -> List[str]:
        """
        Determine which data collectors are needed.
        
        Example:
            question_type = CORTEX_STATUS
            namespace = "cortex.*"
            
            Returns: [
                "brain_metrics_collector",
                "token_optimization_collector",
                "cortex_capabilities_collector"
            ]
        """
```

**Question Classification Logic:**

```python
class QuestionType(Enum):
    """Types of questions CORTEX can answer."""
    
    # CORTEX Framework Questions (namespace: cortex.*)
    CORTEX_STATUS = "cortex_status"          # "How is CORTEX doing?"
    CORTEX_CAPABILITY = "cortex_capability"  # "Can CORTEX do X?"
    CORTEX_LEARNING = "cortex_learning"      # "What did CORTEX learn?"
    CORTEX_COMPARISON = "cortex_comparison"  # "CORTEX vs Copilot?"
    CORTEX_ARCHITECTURE = "cortex_arch"      # "How does CORTEX work?"
    CORTEX_COST = "cortex_cost"              # "Token savings?"
    
    # Workspace Questions (namespace: workspace.*)
    WORKSPACE_STATUS = "workspace_status"    # "How is my project?"
    WORKSPACE_QUALITY = "workspace_quality"  # "Code quality?"
    WORKSPACE_TESTS = "workspace_tests"      # "Test coverage?"
    WORKSPACE_PATTERNS = "workspace_patterns" # "What patterns learned?"
    
    # Meta Questions (both namespaces)
    NAMESPACE_INFO = "namespace_info"        # "Which namespace?"
    LEARNING_RATE = "learning_rate"          # "How fast learning?"
    
    UNKNOWN = "unknown"                      # Fallback

# Keyword mapping for classification
QUESTION_KEYWORDS = {
    QuestionType.CORTEX_STATUS: [
        "how is cortex", "cortex doing", "brain health",
        "cortex status", "framework status"
    ],
    QuestionType.WORKSPACE_STATUS: [
        "how is project", "project status", "code quality",
        "application health", "workspace status"
    ],
    QuestionType.CORTEX_CAPABILITY: [
        "can cortex", "does cortex support", "cortex able to"
    ],
    # ... etc
}
```

---

### 2. CollectorOrchestrator (Data Gathering)

**Responsibilities:**
- Execute multiple collectors in parallel
- Handle collector failures gracefully
- Aggregate results
- Cache recent results (avoid redundant queries)

**API:**

```python
class CollectorOrchestrator:
    """
    Orchestrates data collection from multiple sources.
    
    Example:
        orchestrator = CollectorOrchestrator(tier1, tier2, tier3)
        
        data = await orchestrator.collect(
            collectors=["brain_metrics", "token_optimization"],
            namespace="cortex.*"
        )
        # Returns: {
        #   "brain_metrics": {...},
        #   "token_optimization": {...}
        # }
    """
    
    async def collect(
        self,
        collectors: List[str],
        namespace: str,
        cache_ttl: int = 60  # seconds
    ) -> Dict[str, Any]:
        """
        Execute collectors in parallel and aggregate results.
        
        Args:
            collectors: List of collector IDs to execute
            namespace: Target namespace for context
            cache_ttl: Cache time-to-live in seconds
        
        Returns:
            Dictionary of collector results
        """
        
    def get_collector(self, collector_id: str) -> BaseCollector:
        """Get collector instance by ID."""
        
    def is_cached(self, collector_id: str) -> bool:
        """Check if collector result is cached and fresh."""
```

---

### 3. Data Collectors (Fresh Analysis)

**Base Collector:**

```python
class BaseCollector(ABC):
    """Base class for all data collectors."""
    
    def __init__(self, tier1=None, tier2=None, tier3=None):
        self.tier1 = tier1
        self.tier2 = tier2
        self.tier3 = tier3
    
    @abstractmethod
    def collect(self, namespace: str, **kwargs) -> Dict[str, Any]:
        """
        Collect fresh data for template population.
        
        Args:
            namespace: Target namespace (cortex.* or workspace.*)
            **kwargs: Additional parameters
        
        Returns:
            Dictionary of collected data
        """
        pass
    
    @property
    @abstractmethod
    def collector_id(self) -> str:
        """Unique collector identifier."""
        pass
    
    @property
    def cache_ttl(self) -> int:
        """Cache time-to-live in seconds (default: 60)."""
        return 60
```

**Concrete Collectors:**

```python
class BrainMetricsCollector(BaseCollector):
    """
    Collects CORTEX brain health metrics.
    
    Data collected:
    - Tier 0 protection status
    - Tier 1 memory usage
    - Tier 2 pattern count
    - Tier 3 context freshness
    - Overall health score
    """
    
    collector_id = "brain_metrics_collector"
    
    def collect(self, namespace: str = "cortex.*", **kwargs) -> Dict[str, Any]:
        return {
            "tier0_status": self._check_tier0(),
            "tier1_conversations": self.tier1.get_conversation_count(),
            "tier1_memory_usage": self._calculate_memory_usage(),
            "tier2_patterns_count": self.tier2.get_pattern_count(namespace),
            "tier3_metrics_age": self.tier3.get_metrics_age(),
            "brain_health_score": self._calculate_health_score(),
            "session_duration_hours": self._get_session_duration()
        }


class WorkspaceHealthCollector(BaseCollector):
    """
    Collects workspace health metrics.
    
    Data collected:
    - Code quality score
    - Lint issues count
    - File organization metrics
    - Dependency health
    """
    
    collector_id = "workspace_health_collector"
    
    def collect(self, namespace: str, **kwargs) -> Dict[str, Any]:
        workspace_name = namespace.replace("workspace.", "").split(".")[0]
        
        return {
            "workspace_name": workspace_name,
            "code_health_score": self._calculate_health_score(),
            "lint_issues": self._count_lint_issues(),
            "file_organization_score": self._check_file_organization(),
            "dependency_status": self._check_dependencies(),
            "workspace_recommendation": self._generate_recommendation()
        }


class TestCoverageCollector(BaseCollector):
    """
    Collects test coverage metrics.
    
    Data collected:
    - Overall coverage percentage
    - Test pass/fail breakdown
    - Coverage by file/module
    - Recent test activity
    """
    
    collector_id = "test_coverage_collector"
    
    def collect(self, namespace: str, **kwargs) -> Dict[str, Any]:
        return {
            "coverage_percent": self._get_coverage_percentage(),
            "tests_total": self._count_tests(),
            "tests_passing": self._count_passing_tests(),
            "tests_failing": self._count_failing_tests(),
            "tests_skipped": self._count_skipped_tests(),
            "last_test_run": self._get_last_run_time(),
            "test_recommendation": self._generate_test_recommendation()
        }
```

---

### 4. TemplatePopulator (Response Generation)

**Responsibilities:**
- Load response template by ID
- Inject collected data into template
- Handle missing data gracefully
- Format final response

**API:**

```python
class TemplatePopulator:
    """
    Populates response templates with collected data.
    
    Example:
        populator = TemplatePopulator()
        
        response = populator.populate(
            template_id="question_about_cortex_general",
            data={
                "operations": [...],
                "plugins_active": 8,
                "tier1_conversations": 15
            }
        )
    """
    
    def populate(
        self,
        template_id: str,
        data: Dict[str, Any],
        verbosity: str = "concise"
    ) -> str:
        """
        Populate template with data and return formatted response.
        
        Args:
            template_id: Template identifier from response-templates.yaml
            data: Collected data from orchestrator
            verbosity: concise | detailed | expert
        
        Returns:
            Formatted response string
        """
        
    def load_template(self, template_id: str) -> Dict[str, Any]:
        """Load template from response-templates.yaml"""
        
    def inject_data(self, template: str, data: Dict[str, Any]) -> str:
        """Inject data into template using mustache-style syntax"""
        
    def apply_verbosity(self, response: str, verbosity: str) -> str:
        """
        Filter response sections based on verbosity.
        
        Sections:
        - [detailed]...[/detailed] - shown only in detailed mode
        - [expert]...[/expert] - shown only in expert mode
        """
```

---

## 🔄 Integration with CORTEX 2.0

### Backward Compatibility

**CORTEX 2.0 templates work in 3.0 without changes:**

```yaml
# 2.0 template (still works in 3.0)
question_about_cortex_general:
  triggers: ["how is cortex"]
  context_needed: true
  data_collectors:
    - brain_metrics_collector
    - token_optimization_collector
  content: |
    🧠 **CORTEX Framework Status**
    {{operations}}
```

**CORTEX 3.0 adds dynamic routing:**

```python
# 3.0 enhancement (automatic)
router = QuestionRouter()

# User asks: "how's the brain performing?"
result = router.route_question("how's the brain performing?")

# Returns:
# {
#   "question_type": QuestionType.CORTEX_STATUS,
#   "namespace": "cortex.*",
#   "template_id": "question_about_cortex_general",  # ← Matched intelligently
#   "collectors": ["brain_metrics_collector", "token_optimization_collector"],
#   "confidence": 0.92
# }
```

---

## 📊 Example Workflows

### Workflow 1: "How is the brain doing?"

```
1. User: "How is the brain doing?"

2. QuestionRouter.route_question()
   ├─ classify_question_type() → CORTEX_STATUS
   ├─ detect_namespace() → "cortex.*"
   ├─ select_template() → "question_about_cortex_general"
   └─ determine_collectors() → ["brain_metrics", "token_optimization"]

3. CollectorOrchestrator.collect()
   ├─ Parallel execution:
   │  ├─ BrainMetricsCollector.collect()
   │  │  └─ Returns: {tier1_conversations: 15, tier2_patterns: 847, ...}
   │  └─ TokenOptimizationCollector.collect()
   │     └─ Returns: {session_tokens_saved: 45000, ...}
   └─ Aggregate: {...}

4. TemplatePopulator.populate()
   ├─ Load template: "question_about_cortex_general"
   ├─ Inject data: {tier1_conversations: 15, ...}
   └─ Format: "🧠 CORTEX Framework Status\n\nCapabilities..."

5. Response returned to user
```

### Workflow 2: "What's my code quality?"

```
1. User: "What's my code quality?"

2. QuestionRouter.route_question()
   ├─ classify_question_type() → WORKSPACE_QUALITY
   ├─ detect_namespace() → "workspace.myapp.*"
   ├─ select_template() → "question_about_workspace"
   └─ determine_collectors() → ["workspace_health", "test_coverage", "git_metrics"]

3. CollectorOrchestrator.collect()
   ├─ WorkspaceHealthCollector.collect() → {code_health_score: 85, ...}
   ├─ TestCoverageCollector.collect() → {coverage_percent: 78, ...}
   └─ GitMetricsCollector.collect() → {commits_today: 5, ...}

4. TemplatePopulator.populate()
   └─ Template: "question_about_workspace"

5. Response: "📊 Your Workspace: myapp\n\nCode Quality: 85/100..."
```

---

## 🎯 Implementation Phases

### Phase 3.0.1: Foundation (4 hours)

**Deliverables:**
- `src/context_collectors/base_collector.py`
- `src/context_collectors/orchestrator.py`
- `src/cortex_agents/strategic/question_classifier.py`
- Unit tests for base components

**Success Criteria:**
- Base collector interface working
- Orchestrator can run collectors in parallel
- Question classification logic validated

### Phase 3.0.2: Core Collectors (6 hours)

**Deliverables:**
- `brain_metrics_collector.py`
- `workspace_health_collector.py`
- `test_coverage_collector.py`
- `git_metrics_collector.py`
- Integration tests

**Success Criteria:**
- All collectors return valid data
- Caching mechanism working
- Graceful error handling

### Phase 3.0.3: QuestionRouter (4 hours)

**Deliverables:**
- `question_router.py`
- Namespace detection logic
- Template selection logic
- Integration with existing IntentRouter

**Success Criteria:**
- 90%+ accuracy on question classification
- Correct namespace routing
- Template selection validated

### Phase 3.0.4: Template Engine (3 hours)

**Deliverables:**
- `template_loader.py`
- `template_populator.py`
- `response_formatter.py`
- Verbosity filtering

**Success Criteria:**
- All 2.0 templates still work
- Dynamic data injection working
- Verbosity modes functional

### Phase 3.0.5: Integration & Testing (3 hours)

**Deliverables:**
- End-to-end integration tests
- Performance benchmarks
- Documentation updates
- Example workflows

**Success Criteria:**
- 95%+ test coverage
- <200ms average response time
- All workflows passing

**Total Estimated Effort:** 20 hours (2.5 days)

---

## 📈 Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Question classification | <50ms | Using keyword matching + ML |
| Namespace detection | <30ms | File path + keyword analysis |
| Collector execution (parallel) | <150ms | 3-5 collectors in parallel |
| Template population | <20ms | String interpolation |
| **Total response time** | **<250ms** | End-to-end |
| Cache hit rate | >70% | For frequently asked questions |
| Classification accuracy | >90% | Validated against test set |

---

## 🔒 Security & Privacy

**Namespace Isolation:**
- CORTEX namespace (`cortex.*`) is **read-only** for users
- Workspace namespaces are sandboxed per project
- No cross-workspace data leakage

**Data Collection:**
- All collectors respect brain protection rules
- No sensitive data (passwords, tokens) collected
- Metrics are aggregated, not raw data

**Caching:**
- Cache cleared on workspace switch
- TTL enforced strictly
- No persistent cache across sessions

---

## 🎓 Learning from CORTEX 2.0

**What worked well:**
- ✅ Static templates with `context_needed: true`
- ✅ Metadata-driven collector specification
- ✅ Namespace-based knowledge boundaries
- ✅ YAML-based configuration

**What needs improvement:**
- ⚠️ Manual trigger matching (limited flexibility)
- ⚠️ No intelligent question classification
- ⚠️ Collectors not yet implemented (just specs)
- ⚠️ No dynamic template selection

**CORTEX 3.0 addresses these gaps while preserving 2.0 strengths.**

---

## 📚 References

**CORTEX 2.0 Foundation:**
- `cortex-brain/response-templates.yaml` - 90+ templates with collector specs
- `cortex-brain/interaction-design.yaml` - Natural language patterns
- `src/context_injector.py` - Tier 1/2/3 context injection
- `src/cortex_agents/strategic/intent_router.py` - Intent routing

**Related Documentation:**
- `cortex-brain/cortex-2.0-design/CORTEX2-STATUS.MD` - Current implementation status
- `cortex-brain/brain-protection-rules.yaml` - Namespace protection rules
- `docs/architecture/` - System architecture

---

## ✅ Success Criteria

**CORTEX 3.0 Question Routing is successful when:**

1. ✅ **Intelligent Detection:** "How's the brain?" correctly routes to CORTEX namespace
2. ✅ **Fresh Analysis:** Every response uses real-time data (not stale)
3. ✅ **Namespace Aware:** CORTEX vs workspace questions properly separated
4. ✅ **Performance:** <250ms average response time
5. ✅ **Accuracy:** >90% correct question classification
6. ✅ **Extensibility:** New collectors easy to add
7. ✅ **Backward Compatible:** All CORTEX 2.0 templates still work

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary  
**Version:** 3.0 Design Draft  
**Status:** 📋 DESIGN PHASE - Awaiting 2.0 completion  
**Foundation:** Built on CORTEX 2.0 response templates (90+ templates with collector specs)

---

*This design document outlines the CORTEX 3.0 intelligent question routing system. Implementation begins after CORTEX 2.0 ships.*
