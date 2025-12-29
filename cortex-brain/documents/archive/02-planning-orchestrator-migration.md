# Planning Orchestrator Migration Plan
## CORTEX 3.0 → 4.0 Consolidation

**Target:** Consolidate 3 separate planning systems into unified `PlanningOrchestrator`

**Version:** 1.0.0 | **Author:** Asif Hussain | **Date:** December 14, 2025

---

## 📋 Executive Summary

### Current State (CORTEX 3.0)
Three separate planning systems with overlapping responsibilities:

1. **PlanningOrchestrator** (`src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py`)
   - 1,441 lines of code
   - Feature planning with DoR/DoD validation
   - Complexity analysis (HIGH/MEDIUM/LOW)
   - Phase decomposition, risk assessment, test strategy

2. **IncrementalPlanGenerator** (`src/workflows/incremental_plan_generator.py`)
   - 352 lines of code
   - Token-budgeted planning (200 skeleton → 500 sections)
   - User checkpoints for approval/rejection
   - Memory-efficient chunked generation

3. **ComplexityAnalyzer** (`src/operations/modules/planning/complexity_analyzer.py`)
   - 204 lines of code
   - Single vs multi-phase format selection
   - Thresholds: 2 phases, 10 tasks, 5 days
   - Complexity scoring (0-100)

**Total:** 1,997 LOC scattered across 3 files

### Target State (CORTEX 4.0)
Single unified `PlanningOrchestrator` with:

- **Auto-complexity routing**: Analyzes request → routes to appropriate strategy
- **Three planning strategies**: 
  - Skeleton (LOW complexity): <2 phases, <10 tasks, <5 days
  - Incremental (MEDIUM complexity): 2-5 phases, 10-50 tasks, 5-15 days
  - Full (HIGH complexity): 5+ phases, 50+ tasks, 15+ days
- **Unified interface**: Single MCP tool (`cortex_plan`)
- **MCP integration**: All operations exposed as MCP tools
- **Event-driven**: Emits progress events for real-time tracking
- **Dependency injection**: No circular dependencies

**Target:** 800 LOC in `cortex_orchestrators/planning/`

---

## 🎯 Consolidation Strategy

### Architecture Changes

**Before (CORTEX 3.0):**
```
User Request
    ↓
[Keyword Router: "plan", "create plan", "generate plan"]
    ↓
    ├── → PlanningOrchestrator (feature planning)
    ├── → IncrementalPlanGenerator (if token budget matters)
    └── → ComplexityAnalyzer (called by both)
```

**After (CORTEX 4.0):**
```
User Request
    ↓
[LLM Intent Router: "plan authentication", "create auth plan"]
    ↓
PlanningOrchestrator (unified)
    ↓
ComplexityAnalyzer (embedded)
    ↓
    ├── SkeletonPlanningStrategy (LOW)
    ├── IncrementalPlanningStrategy (MEDIUM)
    └── FullPlanningStrategy (HIGH)
```

### Component Mapping

| **CORTEX 3.0 Component** | **CORTEX 4.0 Location** | **Changes** |
|---------------------------|-------------------------|-------------|
| `PlanningOrchestrator` | `cortex_orchestrators/planning/orchestrator.py` | Core logic preserved, refactored for DI |
| `IncrementalPlanGenerator` | `cortex_orchestrators/planning/strategies/incremental.py` | Extracted as strategy pattern |
| `ComplexityAnalyzer` | `cortex_orchestrators/planning/complexity.py` | Embedded in orchestrator |
| DoR/DoD validation | `cortex_orchestrators/planning/validators.py` | Extracted for reusability |
| Phase decomposition | `cortex_orchestrators/planning/decomposer.py` | Extracted for clarity |

---

## 🗓️ Migration Timeline

### Day 1: Foundation Setup (8 hours)

**Goal:** Create 4.0 directory structure and core interfaces

**Tasks:**

1. **Create directory structure** (1 hour)
   ```
   cortex_orchestrators/
   └── planning/
       ├── __init__.py
       ├── orchestrator.py          # Main orchestrator
       ├── complexity.py             # Complexity analyzer
       ├── validators.py             # DoR/DoD validators
       ├── decomposer.py             # Phase decomposition
       ├── strategies/
       │   ├── __init__.py
       │   ├── base.py               # Base strategy interface
       │   ├── skeleton.py           # LOW complexity
       │   ├── incremental.py        # MEDIUM complexity
       │   └── full.py               # HIGH complexity
       ├── models/
       │   ├── __init__.py
       │   ├── plan.py               # FeaturePlan, Phase, Risk
       │   └── context.py            # PlanningContext
       └── tests/
           ├── __init__.py
           ├── test_orchestrator.py
           ├── test_complexity.py
           ├── test_validators.py
           └── test_strategies.py
   ```

2. **Define base interfaces** (3 hours)
   
   **File:** `cortex_orchestrators/planning/strategies/base.py`
   ```python
   from abc import ABC, abstractmethod
   from typing import Dict, Any
   from ..models.plan import FeaturePlan
   from ..models.context import PlanningContext
   
   class PlanningStrategy(ABC):
       """Base interface for planning strategies."""
       
       @abstractmethod
       def is_applicable(self, complexity_score: float) -> bool:
           """Check if strategy applies to complexity score."""
           pass
       
       @abstractmethod
       async def generate_plan(self, context: PlanningContext) -> FeaturePlan:
           """Generate feature plan for given context."""
           pass
       
       @abstractmethod
       def get_strategy_name(self) -> str:
           """Return strategy name (skeleton/incremental/full)."""
           pass
   ```

3. **Define data models** (2 hours)
   
   **File:** `cortex_orchestrators/planning/models/plan.py`
   ```python
   from dataclasses import dataclass, field
   from datetime import datetime
   from typing import List, Dict, Any
   from enum import Enum
   
   class ComplexityLevel(Enum):
       LOW = "LOW"
       MEDIUM = "MEDIUM"
       HIGH = "HIGH"
   
   @dataclass
   class Phase:
       phase_number: int
       name: str
       description: str
       estimated_days: int
       deliverables: List[str] = field(default_factory=list)
       dependencies: List[str] = field(default_factory=list)
       acceptance_criteria: List[str] = field(default_factory=list)
   
   @dataclass
   class Risk:
       category: str  # TECHNICAL, RESOURCE, TIMELINE
       severity: str  # LOW, MEDIUM, HIGH, CRITICAL
       description: str
       mitigation: str
   
   @dataclass
   class FeaturePlan:
       feature_name: str
       description: str
       complexity: ComplexityLevel
       phases: List[Phase]
       risks: List[Risk]
       estimated_total_days: int
       created_at: datetime
       approved: bool = False
       metadata: Dict[str, Any] = field(default_factory=dict)
   ```

4. **Create test scaffolding** (2 hours)
   
   **File:** `cortex_orchestrators/planning/tests/test_orchestrator.py`
   ```python
   import pytest
   from unittest.mock import Mock, AsyncMock
   from cortex_orchestrators.planning.orchestrator import PlanningOrchestrator
   from cortex_orchestrators.planning.models.context import PlanningContext
   
   @pytest.fixture
   def mock_event_bus():
       return Mock()
   
   @pytest.fixture
   def mock_brain_engine():
       return Mock()
   
   @pytest.fixture
   def orchestrator(mock_event_bus, mock_brain_engine):
       return PlanningOrchestrator(
           event_bus=mock_event_bus,
           brain_engine=mock_brain_engine
       )
   
   @pytest.mark.asyncio
   async def test_plan_generation_low_complexity(orchestrator):
       """Test skeleton planning strategy for low complexity."""
       context = PlanningContext(
           feature_name="Add login button",
           description="Simple UI change",
           acceptance_criteria=["Button visible", "Click navigates"]
       )
       
       plan = await orchestrator.generate_plan(context)
       
       assert plan.complexity == ComplexityLevel.LOW
       assert len(plan.phases) <= 2
       assert plan.estimated_total_days < 5
   ```

**Deliverables (Day 1):**
- ✅ Directory structure created
- ✅ Base interfaces defined (`PlanningStrategy`)
- ✅ Data models defined (`FeaturePlan`, `Phase`, `Risk`)
- ✅ Test scaffolding ready (4 test files)

---

### Day 2-3: Core Orchestrator Migration (16 hours)

**Goal:** Migrate PlanningOrchestrator with MCP integration

**Tasks:**

1. **Extract ComplexityAnalyzer** (4 hours)
   
   **File:** `cortex_orchestrators/planning/complexity.py`
   ```python
   from dataclasses import dataclass
   from typing import Dict, Any
   import logging
   
   logger = logging.getLogger(__name__)
   
   @dataclass
   class ComplexityAnalysis:
       complexity_level: str  # LOW, MEDIUM, HIGH
       phase_count: int
       task_count: int
       estimated_days: float
       complexity_score: float  # 0-100
       rationale: str
   
   class ComplexityAnalyzer:
       """Analyzes feature complexity for strategy routing."""
       
       # Thresholds
       LOW_THRESHOLD = 30      # 0-30: Skeleton
       MEDIUM_THRESHOLD = 70   # 31-70: Incremental
       # 71-100: Full planning
       
       def analyze(self, feature_description: str, 
                   acceptance_criteria: List[str]) -> ComplexityAnalysis:
           """
           Analyze feature complexity using multiple factors.
           
           Factors:
           - Description length (proxy for scope)
           - Acceptance criteria count
           - Keyword detection (auth, migration, refactor = high)
           - Dependency hints (integration, API, database)
           """
           logger.info(f"🔍 Analyzing complexity: {feature_description[:50]}...")
           
           # Calculate score
           score = 0
           
           # Factor 1: Description length
           desc_words = len(feature_description.split())
           if desc_words < 20:
               score += 10
           elif desc_words < 50:
               score += 30
           else:
               score += 50
           
           # Factor 2: Acceptance criteria count
           criteria_count = len(acceptance_criteria)
           if criteria_count < 3:
               score += 10
           elif criteria_count < 8:
               score += 20
           else:
               score += 30
           
           # Factor 3: High-complexity keywords
           high_complexity_keywords = [
               'authentication', 'authorization', 'migration', 
               'refactor', 'integration', 'api', 'database'
           ]
           keyword_matches = sum(
               1 for kw in high_complexity_keywords 
               if kw in feature_description.lower()
           )
           score += keyword_matches * 10
           
           # Cap at 100
           score = min(score, 100)
           
           # Determine level
           if score <= self.LOW_THRESHOLD:
               level = "LOW"
               rationale = f"Simple feature: {desc_words} words, {criteria_count} criteria"
           elif score <= self.MEDIUM_THRESHOLD:
               level = "MEDIUM"
               rationale = f"Moderate feature: {desc_words} words, {criteria_count} criteria"
           else:
               level = "HIGH"
               rationale = f"Complex feature: {desc_words} words, {criteria_count} criteria, {keyword_matches} complexity keywords"
           
           logger.info(f"📊 Complexity: {level} (score={score})")
           
           return ComplexityAnalysis(
               complexity_level=level,
               phase_count=0,  # Estimated post-planning
               task_count=0,
               estimated_days=0.0,
               complexity_score=score,
               rationale=rationale
           )
   ```

2. **Migrate core orchestrator** (8 hours)
   
   **File:** `cortex_orchestrators/planning/orchestrator.py`
   ```python
   from typing import Optional, Dict, Any
   import logging
   from pathlib import Path
   
   from cortex_core.event_bus import EventBus
   from cortex_core.brain_engine import BrainEngine
   from cortex_mcp.server import MCPServer
   
   from .complexity import ComplexityAnalyzer, ComplexityAnalysis
   from .validators import DORValidator, DODValidator
   from .strategies.base import PlanningStrategy
   from .strategies.skeleton import SkeletonPlanningStrategy
   from .strategies.incremental import IncrementalPlanningStrategy
   from .strategies.full import FullPlanningStrategy
   from .models.plan import FeaturePlan, ComplexityLevel
   from .models.context import PlanningContext
   
   logger = logging.getLogger(__name__)
   
   class PlanningOrchestrator:
       """
       Unified planning orchestrator with auto-complexity routing.
       
       Features:
       - Auto-detects complexity (LOW/MEDIUM/HIGH)
       - Routes to appropriate strategy (Skeleton/Incremental/Full)
       - DoR/DoD validation
       - MCP tool integration
       - Event-driven progress tracking
       """
       
       def __init__(
           self,
           event_bus: EventBus,
           brain_engine: BrainEngine,
           mcp_server: Optional[MCPServer] = None
       ):
           self.event_bus = event_bus
           self.brain_engine = brain_engine
           self.mcp_server = mcp_server
           
           # Initialize components
           self.complexity_analyzer = ComplexityAnalyzer()
           self.dor_validator = DORValidator()
           self.dod_validator = DODValidator()
           
           # Initialize strategies
           self.strategies: Dict[str, PlanningStrategy] = {
               "LOW": SkeletonPlanningStrategy(),
               "MEDIUM": IncrementalPlanningStrategy(),
               "HIGH": FullPlanningStrategy()
           }
           
           # Register MCP tools
           if self.mcp_server:
               self._register_mcp_tools()
           
           logger.info("🎭 PlanningOrchestrator initialized (4.0)")
           logger.info("   ✅ Complexity analyzer ready")
           logger.info("   ✅ 3 strategies loaded (Skeleton, Incremental, Full)")
           logger.info("   ✅ DoR/DoD validators ready")
       
       async def generate_plan(self, context: PlanningContext) -> FeaturePlan:
           """
           Generate feature plan with auto-complexity routing.
           
           Workflow:
           1. Validate DoR
           2. Analyze complexity
           3. Select strategy
           4. Generate plan
           5. Validate DoD
           6. Store in brain
           """
           logger.info(f"🚀 Generating plan: {context.feature_name}")
           
           # Emit start event
           self.event_bus.emit("planning.started", {
               "feature_name": context.feature_name
           })
           
           try:
               # Step 1: DoR validation
               dor_result = self.dor_validator.validate(context)
               if not dor_result.is_valid:
                   raise ValueError(f"DoR validation failed: {dor_result.errors}")
               
               # Step 2: Complexity analysis
               complexity = self.complexity_analyzer.analyze(
                   context.description,
                   context.acceptance_criteria
               )
               
               self.event_bus.emit("planning.complexity_analyzed", {
                   "complexity_level": complexity.complexity_level,
                   "score": complexity.complexity_score
               })
               
               # Step 3: Select strategy
               strategy = self.strategies[complexity.complexity_level]
               logger.info(f"📋 Using {strategy.get_strategy_name()} strategy")
               
               # Step 4: Generate plan
               plan = await strategy.generate_plan(context)
               plan.complexity = ComplexityLevel[complexity.complexity_level]
               
               # Step 5: DoD validation
               dod_result = self.dod_validator.validate(plan)
               if not dod_result.is_valid:
                   logger.warning(f"DoD validation warnings: {dod_result.warnings}")
               
               # Step 6: Store in brain
               await self.brain_engine.store_plan(plan)
               
               # Emit completion event
               self.event_bus.emit("planning.completed", {
                   "feature_name": context.feature_name,
                   "complexity": plan.complexity.value,
                   "phases": len(plan.phases)
               })
               
               logger.info(f"✅ Plan generated: {len(plan.phases)} phases")
               return plan
               
           except Exception as e:
               self.event_bus.emit("planning.failed", {
                   "feature_name": context.feature_name,
                   "error": str(e)
               })
               raise
       
       def _register_mcp_tools(self):
           """Register MCP tools for planning operations."""
           
           @self.mcp_server.tool("cortex_plan")
           async def plan_tool(
               feature_name: str,
               description: str,
               acceptance_criteria: list[str]
           ):
               """
               Generate feature implementation plan.
               
               Auto-detects complexity and applies appropriate strategy.
               """
               context = PlanningContext(
                   feature_name=feature_name,
                   description=description,
                   acceptance_criteria=acceptance_criteria
               )
               
               plan = await self.generate_plan(context)
               
               return {
                   "feature_name": plan.feature_name,
                   "complexity": plan.complexity.value,
                   "phases": len(plan.phases),
                   "estimated_days": plan.estimated_total_days,
                   "plan_path": str(plan.metadata.get("file_path"))
               }
           
           logger.info("🔧 MCP tools registered: cortex_plan")
   ```

3. **Extract validators** (4 hours)
   
   **File:** `cortex_orchestrators/planning/validators.py`
   ```python
   from dataclasses import dataclass
   from typing import List
   import logging
   
   from .models.plan import FeaturePlan
   from .models.context import PlanningContext
   
   logger = logging.getLogger(__name__)
   
   @dataclass
   class ValidationResult:
       is_valid: bool
       errors: List[str]
       warnings: List[str]
   
   class DORValidator:
       """Definition of Ready validator."""
       
       def validate(self, context: PlanningContext) -> ValidationResult:
           """
           Validate planning context meets DoR criteria.
           
           Requirements:
           - Feature name (5+ chars)
           - Description (50+ chars)
           - Acceptance criteria (3+ items)
           """
           errors = []
           warnings = []
           
           # Feature name
           if not context.feature_name or len(context.feature_name) < 5:
               errors.append("Feature name too short (min 5 chars)")
           
           # Description
           if not context.description or len(context.description) < 50:
               errors.append("Description too short (min 50 chars)")
           
           # Acceptance criteria
           if len(context.acceptance_criteria) < 3:
               errors.append("Need at least 3 acceptance criteria")
           
           is_valid = len(errors) == 0
           
           if is_valid:
               logger.info("✅ DoR validation passed")
           else:
               logger.warning(f"❌ DoR validation failed: {errors}")
           
           return ValidationResult(
               is_valid=is_valid,
               errors=errors,
               warnings=warnings
           )
   
   class DODValidator:
       """Definition of Done validator."""
       
       def validate(self, plan: FeaturePlan) -> ValidationResult:
           """
           Validate plan meets DoD criteria.
           
           Requirements:
           - At least 1 phase
           - Each phase has deliverables
           - Test strategy defined
           - Risks assessed
           """
           errors = []
           warnings = []
           
           # Phases
           if not plan.phases or len(plan.phases) == 0:
               errors.append("Plan must have at least 1 phase")
           
           # Phase deliverables
           for phase in plan.phases:
               if not phase.deliverables:
                   warnings.append(
                       f"Phase {phase.phase_number} missing deliverables"
                   )
           
           # Test strategy
           if not hasattr(plan, 'test_strategy') or plan.test_strategy is None:
               warnings.append("Test strategy not defined")
           
           # Risks
           if not plan.risks or len(plan.risks) == 0:
               warnings.append("No risks identified")
           
           is_valid = len(errors) == 0
           
           if is_valid:
               logger.info("✅ DoD validation passed")
           else:
               logger.warning(f"❌ DoD validation failed: {errors}")
           
           return ValidationResult(
               is_valid=is_valid,
               errors=errors,
               warnings=warnings
           )
   ```

**Deliverables (Day 2-3):**
- ✅ `ComplexityAnalyzer` extracted and tested
- ✅ Core `PlanningOrchestrator` migrated with MCP integration
- ✅ DoR/DoD validators extracted
- ✅ Unit tests passing (15+ tests)

---

### Day 4-5: Strategy Implementation (16 hours)

**Goal:** Implement 3 planning strategies

**Tasks:**

1. **Skeleton strategy (LOW complexity)** (4 hours)
   
   **File:** `cortex_orchestrators/planning/strategies/skeleton.py`
   ```python
   from typing import Dict, Any
   from datetime import datetime
   import logging
   
   from .base import PlanningStrategy
   from ..models.plan import FeaturePlan, Phase, Risk, ComplexityLevel
   from ..models.context import PlanningContext
   
   logger = logging.getLogger(__name__)
   
   class SkeletonPlanningStrategy(PlanningStrategy):
       """
       Skeleton planning for LOW complexity features.
       
       Characteristics:
       - 1-2 phases
       - <10 tasks total
       - <5 days duration
       - Minimal documentation
       """
       
       def is_applicable(self, complexity_score: float) -> bool:
           return complexity_score <= 30
       
       async def generate_plan(self, context: PlanningContext) -> FeaturePlan:
           """Generate skeleton plan."""
           logger.info(f"📝 Generating skeleton plan: {context.feature_name}")
           
           # Single phase for simple features
           phases = [
               Phase(
                   phase_number=1,
                   name="Implementation",
                   description=context.description,
                   estimated_days=2,
                   deliverables=[
                       f"Implement {context.feature_name}",
                       "Unit tests",
                       "Documentation"
                   ],
                   acceptance_criteria=context.acceptance_criteria
               )
           ]
           
           # Minimal risk assessment
           risks = [
               Risk(
                   category="TIMELINE",
                   severity="LOW",
                   description="Simple feature, low risk",
                   mitigation="Standard development workflow"
               )
           ]
           
           plan = FeaturePlan(
               feature_name=context.feature_name,
               description=context.description,
               complexity=ComplexityLevel.LOW,
               phases=phases,
               risks=risks,
               estimated_total_days=2,
               created_at=datetime.now(),
               metadata={"strategy": "skeleton"}
           )
           
           logger.info("✅ Skeleton plan generated (1 phase, 2 days)")
           return plan
       
       def get_strategy_name(self) -> str:
           return "Skeleton"
   ```

2. **Incremental strategy (MEDIUM complexity)** (6 hours)
   
   **File:** `cortex_orchestrators/planning/strategies/incremental.py`
   ```python
   from typing import Dict, Any, List
   from datetime import datetime
   import logging
   
   from .base import PlanningStrategy
   from ..models.plan import FeaturePlan, Phase, Risk, ComplexityLevel
   from ..models.context import PlanningContext
   
   logger = logging.getLogger(__name__)
   
   class IncrementalPlanningStrategy(PlanningStrategy):
       """
       Incremental planning for MEDIUM complexity features.
       
       Characteristics:
       - 2-5 phases
       - 10-50 tasks
       - 5-15 days duration
       - Token-budgeted generation (500 tokens/section)
       """
       
       SECTION_TOKEN_LIMIT = 500
       
       def is_applicable(self, complexity_score: float) -> bool:
           return 30 < complexity_score <= 70
       
       async def generate_plan(self, context: PlanningContext) -> FeaturePlan:
           """Generate incremental plan with checkpoints."""
           logger.info(f"📝 Generating incremental plan: {context.feature_name}")
           
           # Decompose into phases
           phases = await self._decompose_phases(context)
           
           # Risk assessment
           risks = self._assess_risks(context, phases)
           
           # Calculate duration
           total_days = sum(p.estimated_days for p in phases)
           
           plan = FeaturePlan(
               feature_name=context.feature_name,
               description=context.description,
               complexity=ComplexityLevel.MEDIUM,
               phases=phases,
               risks=risks,
               estimated_total_days=total_days,
               created_at=datetime.now(),
               metadata={"strategy": "incremental"}
           )
           
           logger.info(f"✅ Incremental plan generated ({len(phases)} phases, {total_days} days)")
           return plan
       
       async def _decompose_phases(self, context: PlanningContext) -> List[Phase]:
           """Decompose feature into 2-5 phases."""
           # Standard phases for medium complexity
           phases = [
               Phase(
                   phase_number=1,
                   name="Foundation",
                   description=f"Setup infrastructure for {context.feature_name}",
                   estimated_days=3,
                   deliverables=[
                       "Project structure",
                       "Dependencies",
                       "Configuration"
                   ],
                   acceptance_criteria=["Infrastructure ready"]
               ),
               Phase(
                   phase_number=2,
                   name="Core Implementation",
                   description=f"Implement {context.feature_name} core logic",
                   estimated_days=5,
                   deliverables=[
                       "Core functionality",
                       "Unit tests (80% coverage)",
                       "Error handling"
                   ],
                   acceptance_criteria=context.acceptance_criteria[:2]
               ),
               Phase(
                   phase_number=3,
                   name="Integration & Testing",
                   description="Integrate and validate feature",
                   estimated_days=3,
                   deliverables=[
                       "Integration tests",
                       "E2E tests",
                       "Documentation"
                   ],
                   acceptance_criteria=context.acceptance_criteria[2:]
               )
           ]
           
           return phases
       
       def _assess_risks(self, context: PlanningContext, 
                        phases: List[Phase]) -> List[Risk]:
           """Assess implementation risks."""
           return [
               Risk(
                   category="TECHNICAL",
                   severity="MEDIUM",
                   description="Integration complexity with existing systems",
                   mitigation="Incremental integration with rollback capability"
               ),
               Risk(
                   category="TIMELINE",
                   severity="LOW",
                   description="Potential phase overruns",
                   mitigation="Daily progress tracking and adjustment"
               )
           ]
       
       def get_strategy_name(self) -> str:
           return "Incremental"
   ```

3. **Full strategy (HIGH complexity)** (6 hours)
   
   **File:** `cortex_orchestrators/planning/strategies/full.py`
   ```python
   from typing import Dict, Any, List
   from datetime import datetime
   import logging
   
   from .base import PlanningStrategy
   from ..models.plan import FeaturePlan, Phase, Risk, ComplexityLevel
   from ..models.context import PlanningContext
   
   logger = logging.getLogger(__name__)
   
   class FullPlanningStrategy(PlanningStrategy):
       """
       Full planning for HIGH complexity features.
       
       Characteristics:
       - 5+ phases
       - 50+ tasks
       - 15+ days duration
       - Comprehensive documentation
       - Master plan + worker plans
       """
       
       def is_applicable(self, complexity_score: float) -> bool:
           return complexity_score > 70
       
       async def generate_plan(self, context: PlanningContext) -> FeaturePlan:
           """Generate full comprehensive plan."""
           logger.info(f"📝 Generating full plan: {context.feature_name}")
           
           # Decompose into detailed phases
           phases = await self._decompose_detailed_phases(context)
           
           # Comprehensive risk assessment
           risks = self._comprehensive_risk_assessment(context, phases)
           
           # Calculate duration
           total_days = sum(p.estimated_days for p in phases)
           
           plan = FeaturePlan(
               feature_name=context.feature_name,
               description=context.description,
               complexity=ComplexityLevel.HIGH,
               phases=phases,
               risks=risks,
               estimated_total_days=total_days,
               created_at=datetime.now(),
               metadata={
                   "strategy": "full",
                   "requires_worker_plans": True
               }
           )
           
           logger.info(f"✅ Full plan generated ({len(phases)} phases, {total_days} days)")
           return plan
       
       async def _decompose_detailed_phases(
           self, context: PlanningContext
       ) -> List[Phase]:
           """Decompose into 5+ detailed phases."""
           phases = [
               Phase(
                   phase_number=1,
                   name="Architecture & Design",
                   description="Comprehensive design phase",
                   estimated_days=5,
                   deliverables=[
                       "Architecture diagram",
                       "Component design",
                       "API contracts",
                       "Database schema"
                   ]
               ),
               Phase(
                   phase_number=2,
                   name="Foundation",
                   description="Setup infrastructure",
                   estimated_days=4,
                   deliverables=[
                       "Project structure",
                       "Dependencies",
                       "CI/CD pipeline"
                   ]
               ),
               Phase(
                   phase_number=3,
                   name="Core Implementation",
                   description="Core feature development",
                   estimated_days=10,
                   deliverables=[
                       "Core modules",
                       "Unit tests (90% coverage)",
                       "Error handling"
                   ]
               ),
               Phase(
                   phase_number=4,
                   name="Integration",
                   description="System integration",
                   estimated_days=5,
                   deliverables=[
                       "Integration tests",
                       "External API integration",
                       "Database migration"
                   ]
               ),
               Phase(
                   phase_number=5,
                   name="Testing & Validation",
                   description="Comprehensive testing",
                   estimated_days=4,
                   deliverables=[
                       "E2E tests",
                       "Performance tests",
                       "Security tests"
                   ]
               ),
               Phase(
                   phase_number=6,
                   name="Documentation & Deployment",
                   description="Finalization",
                   estimated_days=3,
                   deliverables=[
                       "User documentation",
                       "API documentation",
                       "Deployment runbook"
                   ]
               )
           ]
           
           return phases
       
       def _comprehensive_risk_assessment(
           self, context: PlanningContext, phases: List[Phase]
       ) -> List[Risk]:
           """Comprehensive risk analysis."""
           return [
               Risk(
                   category="TECHNICAL",
                   severity="HIGH",
                   description="Complex integration with legacy systems",
                   mitigation="Phased integration with comprehensive testing"
               ),
               Risk(
                   category="RESOURCE",
                   severity="MEDIUM",
                   description="Requires specialized expertise",
                   mitigation="Team training and external consultation"
               ),
               Risk(
                   category="TIMELINE",
                   severity="MEDIUM",
                   description="Long development cycle with dependencies",
                   mitigation="Parallel workstreams and contingency buffer"
               ),
               Risk(
                   category="INTEGRATION",
                   severity="HIGH",
                   description="Multiple external dependencies",
                   mitigation="Early API contract validation and mocking"
               )
           ]
       
       def get_strategy_name(self) -> str:
           return "Full"
   ```

**Deliverables (Day 4-5):**
- ✅ 3 strategies implemented (Skeleton, Incremental, Full)
- ✅ Strategy unit tests passing (20+ tests)
- ✅ Integration tests passing (orchestrator + strategies)

---

## 🧪 Testing Strategy

### Unit Tests (40 tests)

**Test Coverage:**

1. **Complexity Analyzer** (10 tests)
   - Low complexity detection (<30 score)
   - Medium complexity detection (31-70 score)
   - High complexity detection (>70 score)
   - Keyword weighting (auth, migration, refactor)
   - Description length factor
   - Acceptance criteria factor

2. **Validators** (10 tests)
   - DoR: Valid context passes
   - DoR: Missing feature name fails
   - DoR: Short description fails
   - DoR: Insufficient criteria fails
   - DoD: Valid plan passes
   - DoD: Missing phases fails
   - DoD: Missing deliverables warns
   - DoD: Missing test strategy warns

3. **Strategies** (15 tests)
   - Skeleton: Generates 1-2 phases
   - Skeleton: Duration <5 days
   - Incremental: Generates 2-5 phases
   - Incremental: Duration 5-15 days
   - Incremental: Token budget respected
   - Full: Generates 5+ phases
   - Full: Duration 15+ days
   - Full: Worker plans flag set

4. **Orchestrator** (5 tests)
   - End-to-end LOW complexity flow
   - End-to-end MEDIUM complexity flow
   - End-to-end HIGH complexity flow
   - DoR validation failure handling
   - Event emission verification

### Integration Tests (10 tests)

1. **MCP Tool Integration** (3 tests)
   - `cortex_plan` tool registered
   - Tool invocation with valid input
   - Tool error handling

2. **Event Bus Integration** (4 tests)
   - Planning started event
   - Complexity analyzed event
   - Planning completed event
   - Planning failed event

3. **Brain Engine Integration** (3 tests)
   - Plan storage in Tier 2
   - Plan retrieval by feature name
   - Plan versioning

### E2E Tests (5 tests)

1. User requests "plan user authentication" → HIGH complexity → Full strategy
2. User requests "add logout button" → LOW complexity → Skeleton strategy
3. User requests "refactor auth module" → MEDIUM complexity → Incremental strategy
4. Invalid request (no description) → DoR failure → Error message
5. Plan approval → Autonomous execution → All phases complete

---

## 📊 Success Metrics

### Migration Completion Criteria

- ✅ All 3.0 planning code consolidated into 4.0 structure
- ✅ Zero circular dependencies (verified via `pytest --pylint`)
- ✅ 90%+ test coverage (unit + integration)
- ✅ MCP tools functional (`cortex_plan` callable from CLI)
- ✅ Event-driven progress tracking working
- ✅ DoR/DoD validation preserved

### Performance Targets

- **Planning latency**: <5 seconds for skeleton, <15 seconds for incremental, <30 seconds for full
- **Memory usage**: <100MB per planning session
- **Test execution**: <2 seconds for unit tests, <10 seconds for integration tests

### Code Quality Metrics

- **LOC reduction**: 1,997 → 800 (60% reduction)
- **Cyclomatic complexity**: <10 per function
- **Maintainability index**: >70
- **Documentation coverage**: 100% (all public methods)

---

## 🔄 Rollback Plan

If migration fails or introduces regressions:

1. **Immediate rollback**: Revert to `CORTEX-3.0` branch
2. **Preserve data**: Export all plans from Tier 2 brain
3. **Analyze failure**: Review logs, test failures, user feedback
4. **Fix forward**: Address issues in 4.0 codebase
5. **Retry migration**: After fixes validated

**Rollback triggers:**
- Test pass rate <90%
- Planning latency >2x baseline
- Critical DoR/DoD validation failures
- User-reported blocking issues

---

## 📝 Documentation Updates

### Files to Create

1. **User Guide**: `docs/orchestrators/planning-orchestrator.md`
   - How to use `cortex_plan` MCP tool
   - Complexity levels explained
   - DoR/DoD requirements
   - Example workflows

2. **Developer Guide**: `docs/dev/planning-orchestrator-dev.md`
   - Architecture overview
   - Strategy pattern explanation
   - Adding new strategies
   - Testing approach

3. **Migration Notes**: `MIGRATION-NOTES-PLANNING.md`
   - Breaking changes from 3.0
   - API differences
   - Backward compatibility notes

---

## 🚀 Next Steps

After Planning Orchestrator migration complete:

1. **ADO Orchestrator** (Day 6-8): Extend PlanningOrchestrator for ADO work items
2. **Maintenance Orchestrator** (Day 9-11): 7-phase system maintenance workflow
3. **Sanitization Orchestrator** (Day 12-14): Code anonymization with validation

---

**Approval Checklist:**

- [ ] Architecture approved (unified orchestrator + 3 strategies)
- [ ] Timeline realistic (5 days = 40 hours)
- [ ] Test coverage sufficient (55 tests)
- [ ] Success metrics clear
- [ ] Rollback plan documented

**Sign-off:** _________________________________  Date: ___________
