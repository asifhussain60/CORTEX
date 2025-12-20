# TDD Mastery Orchestrator: CORTEX 3.0 → 4.0 Redesign

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Date:** December 17, 2025  
**Version:** 1.0 - Architectural Analysis & Redesign

---

## 🧠 CORTEX TDD Orchestrator Architecture Review

---

### 🎯 Understanding & Scope

Comprehensive analysis of TDD Mastery orchestrator for CORTEX 4.0 redesign, examining:
- **Current 3.0 Architecture:** 2 implementations (orchestration_3_0 + workflows), 1,233+ LOC
- **Components:** 10+ modules (test generation, state machine, refactoring, vision API)
- **Integration Points:** Brain (Tier 1/2), Git checkpoints, terminal execution, screenshot analysis
- **Workflow:** RED→GREEN→REFACTOR with DoR/DoD validation

Comparison approach: Same methodology as Planning Orchestrator review.

---

### ⚡ Approach & Considerations

**Architectural Challenge:** TDD orchestrator has **dual personality problem**:

1. **orchestration_3_0/orchestrators/tdd/** (382 LOC) - Clean, minimal, phase-focused
2. **workflows/tdd_workflow_orchestrator.py** (1,233 LOC) - Feature-rich but bloated

This creates:
- **Confusion:** Which to use? When?
- **Duplication:** Overlapping functionality
- **Maintenance:** Two codebases for same workflow
- **Integration debt:** workflow version has 15+ dependencies

**Key tension:** Simplicity vs. Features - CORTEX 4.0 must resolve this.

---

### 💬 Response

## ✅ Current Architecture Assessment (CORTEX 3.0)

### Implementation 1: orchestration_3_0/orchestrators/tdd/ (Clean)

**Structure:**
```
src/orchestration_3_0/orchestrators/tdd/
├── tdd_orchestrator.py           # 382 LOC - Main orchestrator
├── phase_validator.py            # DoR/DoD validation
├── test_generator.py             # 330 LOC - RED phase
├── implementation_engine.py      # GREEN phase
├── refactoring_engine.py         # REFACTOR phase
└── metrics_collector.py          # Phase metrics
```

**✅ Strengths:**

1. **Clean Separation:** Each phase = dedicated module
2. **BaseOrchestrator Integration:** Inherits from orchestration_3_0.core
3. **Dependency Injection:** Uses DependencyContainer for testability
4. **State Machine:** FSM-based workflow validation
5. **DoR/DoD Enforcement:** Explicit validation at phase boundaries
6. **Minimal Dependencies:** 6 components, clear responsibilities

**Example Flow:**
```python
# Clean phase execution
def execute_red_phase(context):
    # 1. Validate RED DoR
    dor_result = phase_validator.validate_red_dor(context)
    
    # 2. Generate tests
    test_result = test_generator.generate_tests(context)
    
    # 3. Git checkpoint
    git_orchestrator.create_checkpoint('RED phase complete')
    
    # 4. Collect metrics
    metrics = metrics_collector.collect_phase_metrics('RED', {...})
    
    # 5. Validate RED DoD
    dod_result = phase_validator.validate_red_dod(context)
    
    return result
```

**❌ Weaknesses:**

1. **Limited Features:** Basic test generation only
2. **No Vision API:** Missing screenshot analysis
3. **No Brain Integration:** Doesn't feed Tier 2 knowledge graph
4. **No Terminal Integration:** Can't run tests programmatically
5. **No Session Persistence:** Loses state on restart
6. **Mock-Heavy:** Mocked coverage, test execution, git operations

### Implementation 2: workflows/tdd_workflow_orchestrator.py (Feature-Rich)

**Structure:**
```
src/workflows/tdd_workflow_orchestrator.py  # 1,233 LOC monolith
```

**✅ Strengths:**

1. **Comprehensive Test Generation:**
   - Edge case analysis (null, empty, max values)
   - Domain knowledge integration (Tier 2 patterns)
   - Error condition generation
   - Parametrized test generation
   - Property-based testing
   - Vision API (screenshot → UI element extraction)

2. **Advanced Refactoring:**
   - Code smell detection (god methods, duplicates, complexity)
   - Refactoring suggestions with confidence scores
   - Learning from refactoring patterns (Tier 2)
   - Debug timing injection for performance analysis

3. **Full Integration:**
   - **Tier 1 Brain:** Session persistence (SessionManager)
   - **Tier 2 Brain:** Pattern storage (KnowledgeGraph)
   - **Git Checkpoints:** Auto-checkpoint at each phase
   - **Terminal Integration:** Programmatic test execution
   - **Workspace Discovery:** Auto-detect user repo structure
   - **Vision API:** Screenshot analysis for UI testing

4. **State Management:**
   - State machine (IDLE → RED → GREEN → REFACTOR → COMPLETED)
   - Page tracking (session resume across IDE restarts)
   - Context persistence (TDDContext)

5. **Performance Optimization:**
   - AST caching (100-tree cache)
   - Pattern caching (60-min TTL)
   - Smell caching (1-hour TTL)
   - Batch processing (4 parallel workers)

**❌ Weaknesses:**

1. **Monolithic:** 1,233 LOC in single file (6x complexity threshold)
2. **15+ Dependencies:** Complex import graph
3. **Mixed Responsibilities:** 
   - Test generation (Phase 1)
   - State management (Phase 2)
   - Performance optimization (M3.2)
   - Brain integration (Phase 3)
   - Vision API (Phase 4)
   - Git/Terminal/Workspace (Phase 4)
4. **Configuration Complexity:** 25+ config options in TDDWorkflowConfig
5. **Tight Coupling:** Hardcoded integrations with agents, brain, git
6. **No BaseOrchestrator:** Doesn't use orchestration_3_0 patterns
7. **Testing Challenge:** Difficult to unit test monolith

### Architectural Comparison

| Aspect | orchestration_3_0 | workflows | CORTEX 4.0 Target |
|--------|-------------------|-----------|-------------------|
| **LOC** | 382 | 1,233 | ~600 (split into strategies) |
| **Files** | 6 modules | 1 monolith | 8 strategies + orchestrator |
| **Dependencies** | 6 (clean) | 15+ (complex) | 8 (managed by DI) |
| **BaseOrchestrator** | ✅ Yes | ❌ No | ✅ Required |
| **Brain Integration** | ❌ No | ✅ Yes (Tier 1+2) | ✅ Yes (via DIE) |
| **Test Execution** | ❌ Mocked | ✅ Programmatic | ✅ Via MCP (test runner tool) |
| **Vision API** | ❌ No | ✅ Yes | ✅ Yes (via MCP) |
| **Git Checkpoints** | ❌ Optional | ✅ Integrated | ✅ Via MCP (git tool) |
| **Refactoring** | ⚠️ Basic | ✅ Advanced | ✅ AI-driven (LLM-based) |
| **DoR/DoD** | ✅ Enforced | ⚠️ Implicit | ✅ Enforced + Documented |
| **State Machine** | ✅ FSM | ✅ FSM | ✅ Unified FSM |
| **Testability** | ✅ High | ⚠️ Low | ✅ High (DI + strategies) |

---

## 🏗️ CORTEX 4.0 Redesign: Unified TDD Orchestrator

### Core Philosophy

**From:** Dual implementations (clean vs. feature-rich)  
**To:** Single unified orchestrator with **strategy pattern** for extensibility

### Architectural Blueprint

```
┌─────────────────────────────────────────────────────────────┐
│                 CORTEX 4.0 TDD Orchestrator                 │
│                  "RED-GREEN-REFACTOR Native"                │
└─────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│           TDDOrchestrator (Unified)                        │
│  Inherits: BaseOrchestrator                                │
│  Manages: RED → GREEN → REFACTOR workflow                  │
└────────────┬───────────────────────────────────────────────┘
             │
    ┌────────┼────────┬──────────┬──────────────┐
    ↓        ↓        ↓          ↓              ↓
┌─────────┐ ┌─────┐ ┌─────────┐ ┌──────────┐ ┌────────┐
│RED      │ │GREEN│ │REFACTOR │ │Validation│ │Metrics │
│Strategy │ │Strat│ │Strategy │ │Strategy  │ │Strategy│
└─────────┘ └─────┘ └─────────┘ └──────────┘ └────────┘
    │           │         │            │           │
    ↓           ↓         ↓            ↓           ↓
┌─────────────────────────────────────────────────────────────┐
│                   MCP Gateway Integration                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ Test Runner  │ │ Git Ops      │ │ Vision API   │       │
│  │ (pytest/jest)│ │ (checkpoints)│ │ (screenshots)│       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ AST Analysis │ │ Code Smells  │ │ Refactoring  │       │
│  │ (parse code) │ │ (detect)     │ │ (AI-driven)  │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
             │
    ┌────────┼────────┬──────────┬──────────────┐
    ↓        ↓        ↓          ↓              ↓
┌─────────┐ ┌─────┐ ┌─────────┐ ┌──────────┐ ┌────────┐
│Tier 1   │ │Tier2│ │Doc Intel│ │Continuous│ │Config  │
│Session  │ │Know │ │Engine   │ │Monitor   │ │Manager │
│Manager  │ │Graph│ │(DIE)    │ │          │ │        │
└─────────┘ └─────┘ └─────────┘ └──────────┘ └────────┘
```

### Key Innovations for CORTEX 4.0

#### 1. **Phase Execution Strategies** (Strategy Pattern)

**Replace:** Hardcoded phase methods with pluggable strategies

```python
# src/orchestrators/tdd/strategies/base_strategy.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class PhaseResult:
    """Result from phase execution."""
    phase_name: str
    success: bool
    outputs: Dict[str, Any]
    metrics: Dict[str, Any]
    git_commit_sha: Optional[str] = None
    documentation_updated: bool = False
    brain_patterns_extracted: int = 0
    errors: List[str] = None


class TDDPhaseStrategy(ABC):
    """Base strategy for TDD phase execution."""
    
    @abstractmethod
    async def validate_dor(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate Definition of Ready for this phase."""
        pass
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> PhaseResult:
        """Execute phase autonomously."""
        pass
    
    @abstractmethod
    async def validate_dod(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate Definition of Done for this phase."""
        pass
    
    @abstractmethod
    async def rollback(self, context: Dict[str, Any]) -> bool:
        """Rollback phase changes if validation fails."""
        pass
```

#### 2. **RED Phase Strategy** (Test Generation)

```python
# src/orchestrators/tdd/strategies/red_phase_strategy.py
from .base_strategy import TDDPhaseStrategy, PhaseResult
from orchestrators.tdd.components.test_generator import TestGenerator
from orchestrators.tdd.components.edge_case_analyzer import EdgeCaseAnalyzer
from mcp.gateway import MCPGateway

class REDPhaseStrategy(TDDPhaseStrategy):
    """
    RED phase: Generate comprehensive tests that MUST fail.
    
    Features:
    - Edge case analysis (null, empty, boundaries)
    - Domain knowledge integration (Tier 2 patterns)
    - Error condition generation
    - Parametrized test generation
    - Vision API integration (screenshot → test cases)
    """
    
    def __init__(
        self,
        test_generator: TestGenerator,
        edge_analyzer: EdgeCaseAnalyzer,
        mcp_gateway: MCPGateway,
        brain_feeder: BrainFeeder
    ):
        self.test_generator = test_generator
        self.edge_analyzer = edge_analyzer
        self.mcp = mcp_gateway
        self.brain = brain_feeder
    
    async def validate_dor(self, context: Dict[str, Any]) -> ValidationResult:
        """
        RED DoR:
        - Feature name defined
        - Acceptance criteria clear
        - No existing tests for this feature
        - Git working directory clean
        """
        errors = []
        
        if not context.get('feature_name'):
            errors.append("Feature name not provided")
        
        if not context.get('acceptance_criteria'):
            errors.append("Acceptance criteria missing")
        
        # Check no existing tests via MCP
        test_files = await self.mcp.call_tool(
            'file_search',
            {'pattern': f"**/test_{context['feature_name']}*.py"}
        )
        
        if test_files:
            errors.append(f"Tests already exist: {test_files}")
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors
        )
    
    async def execute(self, context: Dict[str, Any]) -> PhaseResult:
        """
        Execute RED phase test generation.
        
        Steps:
        1. Analyze feature requirements
        2. Extract edge cases
        3. Integrate domain knowledge from Tier 2
        4. Generate test suite (parametrized + property-based)
        5. Run tests (MUST fail - RED validation)
        6. Git checkpoint
        7. Update documentation
        8. Feed patterns to brain
        """
        feature_name = context['feature_name']
        acceptance_criteria = context['acceptance_criteria']
        
        # 1. Analyze feature
        feature_analysis = await self._analyze_feature(
            feature_name,
            acceptance_criteria
        )
        
        # 2. Extract edge cases
        edge_cases = await self.edge_analyzer.analyze(
            feature_analysis['data_types'],
            feature_analysis['boundaries']
        )
        
        # 3. Get domain knowledge from Tier 2
        domain_patterns = await self.brain.query_patterns(
            pattern_type='test_generation',
            context={'feature': feature_name}
        )
        
        # 4. Generate tests
        test_suite = await self.test_generator.generate({
            'feature': feature_name,
            'acceptance_criteria': acceptance_criteria,
            'edge_cases': edge_cases,
            'domain_patterns': domain_patterns,
            'parametrize': True,
            'property_based': True
        })
        
        # 5. Run tests (MUST fail for RED)
        test_result = await self.mcp.call_tool(
            'test_runner',
            {
                'test_file': test_suite['file_path'],
                'expect_failure': True  # RED phase validation
            }
        )
        
        if test_result['passed'] > 0:
            raise ValueError(
                f"RED phase validation failed: {test_result['passed']} tests passing. "
                "Tests MUST fail in RED phase."
            )
        
        # 6. Git checkpoint via MCP
        git_commit = await self.mcp.call_tool(
            'git_checkpoint',
            {
                'phase': 'RED',
                'message': f"RED: Generated {test_suite['test_count']} tests for {feature_name}",
                'files': [test_suite['file_path']]
            }
        )
        
        # 7. Update documentation via DIE
        await self.mcp.call_tool(
            'documentation_intelligence',
            {
                'action': 'generate',
                'files': [test_suite['file_path']],
                'tier': 'FAST'  # Quick docs for tests
            }
        )
        
        # 8. Feed patterns to Tier 2
        patterns_extracted = await self.brain.feed_pattern({
            'pattern_type': 'test_generation',
            'feature': feature_name,
            'edge_cases_used': len(edge_cases),
            'test_techniques': test_suite['techniques'],
            'success': True
        })
        
        return PhaseResult(
            phase_name='RED',
            success=True,
            outputs={
                'test_file': test_suite['file_path'],
                'test_count': test_suite['test_count'],
                'tests_failing': test_result['failed']
            },
            metrics={
                'edge_cases': len(edge_cases),
                'domain_patterns_used': len(domain_patterns),
                'parametrized_groups': test_suite['parametrized_groups']
            },
            git_commit_sha=git_commit['sha'],
            documentation_updated=True,
            brain_patterns_extracted=1
        )
    
    async def validate_dod(self, context: Dict[str, Any]) -> ValidationResult:
        """
        RED DoD:
        - Test file created
        - Tests run successfully (framework works)
        - All tests FAIL (RED validation)
        - Git checkpoint created
        - Documentation generated
        """
        errors = []
        
        if not context.get('test_file'):
            errors.append("Test file not created")
        
        if context.get('tests_passing', 0) > 0:
            errors.append(
                f"RED phase violation: {context['tests_passing']} tests passing. "
                "All tests MUST fail in RED phase."
            )
        
        if context.get('tests_failing', 0) == 0:
            errors.append("No tests generated or tests not run")
        
        if not context.get('git_commit_sha'):
            errors.append("Git checkpoint not created")
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors
        )
    
    async def rollback(self, context: Dict[str, Any]) -> bool:
        """Rollback RED phase (delete generated test file)."""
        test_file = context.get('test_file')
        
        if test_file:
            await self.mcp.call_tool('file_delete', {'path': test_file})
        
        if context.get('git_commit_sha'):
            await self.mcp.call_tool('git_reset', {'commit': 'HEAD~1'})
        
        return True
```

#### 3. **GREEN Phase Strategy** (Minimal Implementation)

```python
# src/orchestrators/tdd/strategies/green_phase_strategy.py
class GREENPhaseStrategy(TDDPhaseStrategy):
    """
    GREEN phase: Minimal implementation to make tests pass.
    
    Features:
    - AI-driven code generation (LLM-based)
    - Over-engineering detection
    - Coverage tracking
    - Continuous test execution
    """
    
    async def execute(self, context: Dict[str, Any]) -> PhaseResult:
        """
        Execute GREEN phase implementation.
        
        Steps:
        1. Analyze failing tests
        2. Generate minimal implementation (AI-driven)
        3. Run tests continuously (RED → GREEN transition)
        4. Detect over-engineering
        5. Git checkpoint
        6. Update documentation
        """
        
        # 1. Analyze failing tests
        test_analysis = await self._analyze_test_requirements(
            context['test_file']
        )
        
        # 2. Generate minimal implementation via LLM
        implementation = await self.mcp.call_tool(
            'llm_code_generation',
            {
                'prompt': self._build_implementation_prompt(test_analysis),
                'constraints': ['minimal', 'no_premature_optimization'],
                'style': 'pythonic'
            }
        )
        
        # 3. Run tests continuously
        test_result = await self._run_tests_until_green(
            test_file=context['test_file'],
            implementation_file=implementation['file_path'],
            max_iterations=10
        )
        
        # 4. Detect over-engineering
        complexity_analysis = await self.mcp.call_tool(
            'code_complexity',
            {'file': implementation['file_path']}
        )
        
        over_engineering = self._detect_over_engineering(
            complexity_analysis,
            test_count=context['test_count']
        )
        
        if over_engineering['detected']:
            raise ValueError(
                f"Over-engineering detected: {over_engineering['reasons']}"
            )
        
        # 5. Git checkpoint
        git_commit = await self.mcp.call_tool(
            'git_checkpoint',
            {
                'phase': 'GREEN',
                'message': f"GREEN: {test_result['passed']} tests passing",
                'files': [implementation['file_path']]
            }
        )
        
        # 6. Update documentation
        await self.mcp.call_tool(
            'documentation_intelligence',
            {
                'action': 'generate',
                'files': [implementation['file_path']],
                'tier': 'FULL'  # Full docs for implementation
            }
        )
        
        return PhaseResult(
            phase_name='GREEN',
            success=True,
            outputs={
                'implementation_file': implementation['file_path'],
                'tests_passing': test_result['passed'],
                'coverage': test_result['coverage']
            },
            metrics={
                'lines_of_code': implementation['loc'],
                'complexity': complexity_analysis['cyclomatic'],
                'iterations_to_green': test_result['iterations']
            },
            git_commit_sha=git_commit['sha'],
            documentation_updated=True
        )
```

#### 4. **REFACTOR Phase Strategy** (AI-Driven Improvement)

```python
# src/orchestrators/tdd/strategies/refactor_phase_strategy.py
class REFACTORPhaseStrategy(TDDPhaseStrategy):
    """
    REFACTOR phase: AI-driven code improvement while keeping tests green.
    
    Features:
    - LLM-based refactoring suggestions
    - Code smell detection (complex, duplicated, god methods)
    - Automated refactoring with rollback safety
    - Learning from successful refactorings (Tier 2)
    """
    
    async def execute(self, context: Dict[str, Any]) -> PhaseResult:
        """
        Execute REFACTOR phase improvement.
        
        Steps:
        1. Detect code smells via AST + LLM
        2. Generate AI-driven refactoring suggestions
        3. Apply refactorings incrementally
        4. Run tests after each refactoring (safety check)
        5. Rollback if tests fail
        6. Learn successful patterns (Tier 2)
        7. Git checkpoint
        8. Update documentation
        """
        
        implementation_file = context['implementation_file']
        
        # 1. Detect code smells
        smells = await self.mcp.call_tool(
            'code_smell_detection',
            {
                'file': implementation_file,
                'techniques': ['ast_analysis', 'llm_analysis'],
                'confidence_threshold': 0.7
            }
        )
        
        if not smells['detected']:
            return PhaseResult(
                phase_name='REFACTOR',
                success=True,
                outputs={'smells_found': 0, 'message': 'No refactoring needed'},
                metrics={'smells': 0}
            )
        
        # 2. Generate AI-driven refactoring suggestions
        refactorings = await self.mcp.call_tool(
            'llm_refactoring',
            {
                'code': context['implementation_content'],
                'smells': smells['items'],
                'constraints': ['preserve_behavior', 'improve_readability'],
                'max_suggestions': 5
            }
        )
        
        # 3. Apply refactorings incrementally with rollback safety
        applied_refactorings = []
        
        for refactoring in refactorings['suggestions']:
            # Apply refactoring
            await self._apply_refactoring(implementation_file, refactoring)
            
            # 4. Run tests (safety check)
            test_result = await self.mcp.call_tool(
                'test_runner',
                {'test_file': context['test_file']}
            )
            
            if test_result['failed'] > 0:
                # 5. Rollback if tests fail
                await self._rollback_refactoring(implementation_file)
                print(f"⚠️  Refactoring '{refactoring['name']}' broke tests. Rolled back.")
            else:
                applied_refactorings.append(refactoring)
                print(f"✅ Refactoring '{refactoring['name']}' applied successfully.")
        
        # 6. Learn successful patterns (Tier 2)
        for refactoring in applied_refactorings:
            await self.brain.feed_pattern({
                'pattern_type': 'refactoring',
                'refactoring_type': refactoring['type'],
                'smell_eliminated': refactoring['smell_type'],
                'success': True,
                'context': context['feature_name']
            })
        
        # 7. Git checkpoint
        git_commit = await self.mcp.call_tool(
            'git_checkpoint',
            {
                'phase': 'REFACTOR',
                'message': f"REFACTOR: Applied {len(applied_refactorings)} improvements",
                'files': [implementation_file]
            }
        )
        
        # 8. Update documentation
        await self.mcp.call_tool(
            'documentation_intelligence',
            {
                'action': 'update',
                'files': [implementation_file],
                'tier': 'FULL'
            }
        )
        
        return PhaseResult(
            phase_name='REFACTOR',
            success=True,
            outputs={
                'smells_eliminated': len(applied_refactorings),
                'refactorings_applied': [r['name'] for r in applied_refactorings]
            },
            metrics={
                'smells_before': len(smells['items']),
                'smells_after': len(smells['items']) - len(applied_refactorings)
            },
            git_commit_sha=git_commit['sha'],
            documentation_updated=True,
            brain_patterns_extracted=len(applied_refactorings)
        )
```

#### 5. **Unified TDD Orchestrator** (Coordinator)

```python
# src/orchestrators/tdd/tdd_orchestrator.py
from orchestrators.base.base_orchestrator import BaseOrchestrator
from .strategies.red_phase_strategy import REDPhaseStrategy
from .strategies.green_phase_strategy import GREENPhaseStrategy
from .strategies.refactor_phase_strategy import REFACTORPhaseStrategy

class TDDOrchestrator(BaseOrchestrator):
    """
    Unified TDD orchestrator for CORTEX 4.0.
    
    Manages complete RED-GREEN-REFACTOR workflow with:
    - Strategy pattern for phase execution
    - DoR/DoD enforcement at phase boundaries
    - Brain integration (Tier 1/2)
    - Documentation Intelligence Engine integration
    - MCP Gateway for all tools
    - Continuous monitoring
    """
    
    def __init__(
        self,
        red_strategy: REDPhaseStrategy,
        green_strategy: GREENPhaseStrategy,
        refactor_strategy: REFACTORPhaseStrategy,
        state_machine: StateMachine,
        session_manager: SessionManager,
        continuous_monitor: ContinuousMonitor
    ):
        super().__init__(
            orchestrator_name="TDDOrchestrator",
            state_machine=state_machine,
            session_manager=session_manager
        )
        
        self.strategies = {
            'RED': red_strategy,
            'GREEN': green_strategy,
            'REFACTOR': refactor_strategy
        }
        
        self.monitor = continuous_monitor
        self.current_phase = None
    
    async def execute_workflow(
        self,
        feature_name: str,
        acceptance_criteria: List[str]
    ) -> Dict[str, Any]:
        """
        Execute complete RED-GREEN-REFACTOR workflow autonomously.
        
        Args:
            feature_name: Feature to implement
            acceptance_criteria: Acceptance criteria
            
        Returns:
            Complete workflow results with metrics
        """
        
        # Initialize context
        context = {
            'feature_name': feature_name,
            'acceptance_criteria': acceptance_criteria,
            'session_id': self.session_manager.create_session(feature_name)
        }
        
        results = {}
        
        # RED Phase
        results['RED'] = await self._execute_phase('RED', context)
        context.update(results['RED'].outputs)
        
        # GREEN Phase
        results['GREEN'] = await self._execute_phase('GREEN', context)
        context.update(results['GREEN'].outputs)
        
        # REFACTOR Phase
        results['REFACTOR'] = await self._execute_phase('REFACTOR', context)
        
        # Complete workflow
        await self.session_manager.complete_session(
            context['session_id'],
            success=all(r.success for r in results.values())
        )
        
        return {
            'success': True,
            'phases': results,
            'total_tests': results['RED'].outputs['test_count'],
            'tests_passing': results['GREEN'].outputs['tests_passing'],
            'refactorings_applied': results['REFACTOR'].outputs.get('smells_eliminated', 0)
        }
    
    async def _execute_phase(
        self,
        phase_name: str,
        context: Dict[str, Any]
    ) -> PhaseResult:
        """Execute single phase with DoR/DoD validation."""
        
        strategy = self.strategies[phase_name]
        
        # Validate DoR
        dor_result = await strategy.validate_dor(context)
        if not dor_result.passed:
            raise ValueError(f"{phase_name} DoR failed: {dor_result.errors}")
        
        # Execute phase with monitoring
        async with self.monitor.track_phase(phase_name) as monitor:
            result = await strategy.execute(context)
        
        # Validate DoD
        dod_result = await strategy.validate_dod({
            **context,
            **result.outputs
        })
        
        if not dod_result.passed:
            # Rollback on DoD failure
            await strategy.rollback(context)
            raise ValueError(f"{phase_name} DoD failed: {dod_result.errors}")
        
        return result
```

---

## 📊 Comparison: CORTEX 3.0 vs. 4.0

| Aspect | orchestration_3_0 | workflows | CORTEX 4.0 (Proposed) |
|--------|-------------------|-----------|----------------------|
| **Architecture** | 6 modules | 1 monolith | 1 orchestrator + 5 strategies |
| **LOC** | 382 (minimal) | 1,233 (bloated) | ~600 (balanced) |
| **Dependencies** | 6 (clean) | 15+ (complex) | 8 (managed by DI) |
| **Test Generation** | Basic | Comprehensive | Comprehensive + AI-enhanced |
| **Refactoring** | Basic | Advanced | AI-driven (LLM-based) |
| **Brain Integration** | ❌ No | ✅ Tier 1+2 | ✅ Tier 1+2 + DIE |
| **Test Execution** | ❌ Mocked | ✅ Programmatic | ✅ Via MCP (test runner tool) |
| **Vision API** | ❌ No | ✅ Yes | ✅ Via MCP (vision tool) |
| **Git Checkpoints** | ❌ Optional | ✅ Auto | ✅ Via MCP (git tool) |
| **Documentation** | ❌ No | ❌ No | ✅ Auto via DIE |
| **DoR/DoD** | ✅ Enforced | ⚠️ Implicit | ✅ Enforced + strategy-level |
| **Rollback** | ❌ No | ❌ No | ✅ Per-phase rollback |
| **Monitoring** | ❌ No | ❌ No | ✅ Continuous (test/build/quality) |
| **Extensibility** | ⚠️ Moderate | ❌ Low (monolith) | ✅ High (strategy pattern) |
| **Testability** | ✅ High | ❌ Low | ✅ Very high (DI + strategies) |

---

## 🚀 Migration Strategy: 3.0 → 4.0

### Phase 1: Strategy Pattern Foundation (Week 7)

**Goal:** Implement base strategy infrastructure

1. [ ] Create `TDDPhaseStrategy` abstract base class
2. [ ] Implement `PhaseResult` dataclass
3. [ ] Create `ValidationResult` with DoR/DoD support
4. [ ] Add rollback support to base strategy

### Phase 2: RED Phase Migration (Week 8)

**Goal:** Migrate test generation to strategy pattern

1. [ ] Extract test generation from both implementations
2. [ ] Implement `REDPhaseStrategy`
3. [ ] Integrate edge case analyzer
4. [ ] Connect to Tier 2 for domain knowledge
5. [ ] Add Vision API integration via MCP
6. [ ] Write comprehensive tests (85%+ coverage)

### Phase 3: GREEN Phase Migration (Week 9)

**Goal:** Migrate minimal implementation to AI-driven strategy

1. [ ] Implement `GREENPhaseStrategy`
2. [ ] Integrate LLM for code generation
3. [ ] Add over-engineering detection
4. [ ] Implement continuous test execution
5. [ ] Add coverage tracking
6. [ ] Write comprehensive tests (85%+ coverage)

### Phase 4: REFACTOR Phase Migration (Week 10)

**Goal:** Migrate refactoring to AI-driven strategy

1. [ ] Implement `REFACTORPhaseStrategy`
2. [ ] Integrate LLM for refactoring suggestions
3. [ ] Add code smell detection (AST + LLM)
4. [ ] Implement incremental refactoring with rollback
5. [ ] Add Tier 2 pattern learning
6. [ ] Write comprehensive tests (85%+ coverage)

### Phase 5: Orchestrator Integration (Week 11)

**Goal:** Complete unified orchestrator

1. [ ] Implement `TDDOrchestrator` with strategy management
2. [ ] Integrate all 3 strategies
3. [ ] Add Continuous Monitor integration
4. [ ] Connect to Documentation Intelligence Engine
5. [ ] Implement session management (Tier 1)
6. [ ] Add workflow-level DoR/DoD validation
7. [ ] Write integration tests (end-to-end workflows)

### Phase 6: Deprecate Legacy (Week 12)

**Goal:** Remove old implementations

1. [ ] Mark `workflows/tdd_workflow_orchestrator.py` as deprecated
2. [ ] Migrate all users to new `TDDOrchestrator`
3. [ ] Archive old implementations
4. [ ] Update documentation
5. [ ] Remove legacy code (post-validation)

---

## 💡 Key Innovations in CORTEX 4.0

### 1. **Strategy Pattern for Extensibility**

**Benefit:** Add new phases without modifying orchestrator

```python
# Easy to add new phase
class PERFORMANCEPhaseStrategy(TDDPhaseStrategy):
    """Performance testing phase (optional extension)."""
    
    async def execute(self, context):
        # Load testing, profiling, benchmarking
        pass

# Register in orchestrator
orchestrator.add_strategy('PERFORMANCE', PERFORMANCEPhaseStrategy())
```

### 2. **AI-Driven Code Generation & Refactoring**

**Benefit:** Leverage LLMs for intelligent implementation and improvement

```python
# LLM generates minimal implementation
implementation = await llm.generate_code(
    tests=test_cases,
    constraints=['minimal', 'pythonic', 'no_premature_optimization']
)

# LLM suggests context-aware refactorings
refactorings = await llm.suggest_refactorings(
    code=implementation,
    smells=detected_smells,
    style='functional'  # or 'oop', 'procedural'
)
```

### 3. **Rollback Safety at Phase Level**

**Benefit:** Each phase can rollback independently if DoD fails

```python
# Automatic rollback on DoD failure
if not dod_result.passed:
    await strategy.rollback(context)  # Undo all phase changes
    raise ValueError(f"Phase failed DoD: {dod_result.errors}")
```

### 4. **Continuous Monitoring During Phases**

**Benefit:** Real-time feedback on test/build status

```python
async with continuous_monitor.track_phase('GREEN') as monitor:
    # Monitor watches for:
    # - Test status changes (passing/failing)
    # - Build status changes (success/failure)
    # - Coverage changes (increasing/decreasing)
    # - Code smell introductions (refactoring needed)
    
    result = await green_strategy.execute(context)
```

### 5. **Documentation Intelligence Integration**

**Benefit:** Auto-generated documentation for all TDD artifacts

```python
# After test generation
await doc_intelligence.generate_docs(
    files=[test_file],
    tier='FAST',  # Quick docs for tests
    extract_patterns=True  # Feed Tier 2
)

# After implementation
await doc_intelligence.generate_docs(
    files=[implementation_file],
    tier='FULL',  # Comprehensive docs with examples
    extract_patterns=True
)
```

### 6. **Unified Tool Access via MCP Gateway**

**Benefit:** All tools accessed through single interface

```python
# No more scattered imports
# From: 15+ direct imports across codebase
# To: Single MCP Gateway

# Run tests
test_result = await mcp.call_tool('test_runner', {...})

# Analyze code
smells = await mcp.call_tool('code_smell_detection', {...})

# Generate code
code = await mcp.call_tool('llm_code_generation', {...})

# Git operations
commit = await mcp.call_tool('git_checkpoint', {...})

# Vision API
ui_elements = await mcp.call_tool('vision_api', {...})
```

---

## 🎯 Performance Considerations

### Latency Budget

| Operation | Current (workflows) | Target (4.0) |
|-----------|---------------------|--------------|
| **Test Generation** | 2-5s (cached) | 1-3s (MCP + caching) |
| **Test Execution** | 5-10s (pytest) | 3-7s (MCP test runner) |
| **Smell Detection** | 3-6s (AST + cache) | 2-4s (MCP + LLM) |
| **Refactoring** | 8-15s (apply + test) | 5-10s (LLM + incremental) |
| **Full Workflow** | 30-60s | 20-40s |

### Optimization Strategies

1. **Parallel Phase Execution** (where safe)
   - Test generation + Documentation (parallel)
   - Smell detection + Coverage analysis (parallel)

2. **Smart Caching**
   - AST cache (persist across sessions)
   - Pattern cache (Tier 2 with TTL)
   - LLM response cache (common refactorings)

3. **Incremental Operations**
   - Only analyze changed files
   - Only re-run affected tests
   - Only regenerate affected docs

4. **Async-First**
   - All MCP calls async
   - Non-blocking brain operations
   - Background documentation generation

---

## 📋 Implementation Checklist

### Week 7: Foundation
- [ ] Base strategy classes (3 classes)
- [ ] PhaseResult dataclass
- [ ] ValidationResult with DoR/DoD
- [ ] Rollback support
- [ ] Unit tests (90%+ coverage)

### Week 8: RED Phase
- [ ] REDPhaseStrategy implementation
- [ ] Edge case analyzer integration
- [ ] Tier 2 domain knowledge query
- [ ] Vision API integration (MCP)
- [ ] DoR/DoD validation
- [ ] Rollback implementation
- [ ] Unit + integration tests (85%+ coverage)

### Week 9: GREEN Phase
- [ ] GREENPhaseStrategy implementation
- [ ] LLM code generation integration
- [ ] Over-engineering detection
- [ ] Continuous test execution
- [ ] Coverage tracking
- [ ] DoR/DoD validation
- [ ] Rollback implementation
- [ ] Unit + integration tests (85%+ coverage)

### Week 10: REFACTOR Phase
- [ ] REFACTORPhaseStrategy implementation
- [ ] LLM refactoring suggestions
- [ ] Code smell detection (AST + LLM)
- [ ] Incremental refactoring with rollback
- [ ] Tier 2 pattern learning
- [ ] DoR/DoD validation
- [ ] Unit + integration tests (85%+ coverage)

### Week 11: Orchestrator
- [ ] TDDOrchestrator implementation
- [ ] Strategy management
- [ ] Continuous Monitor integration
- [ ] DIE integration
- [ ] Session management (Tier 1)
- [ ] Workflow DoR/DoD
- [ ] End-to-end tests (full workflows)

### Week 12: Migration & Cleanup
- [ ] Deprecate legacy implementations
- [ ] Migrate existing users
- [ ] Update documentation
- [ ] Performance validation
- [ ] Archive old code

---

## 🔍 Success Metrics

**Must achieve before Phase 3 completion:**

| Metric | Target | Validation |
|--------|--------|------------|
| **Test Coverage** | 85%+ | pytest --cov |
| **Phase Execution Time** | <10s per phase | Performance tests |
| **DoR/DoD Enforcement** | 100% | All phases validate |
| **Rollback Success Rate** | 100% | Rollback tests pass |
| **Brain Integration** | Tier 1+2 connected | Session + pattern storage verified |
| **Documentation Coverage** | 90%+ | DIE generates docs for all phases |
| **MCP Tool Usage** | 100% tool calls via MCP | No direct imports |

---

**Author:** Asif Hussain  
**Contact:** github.com/asifhussain60/CORTEX  
**Date:** December 17, 2025  
**Version:** 1.0  
