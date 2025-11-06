# CORTEX Agent Contracts

**Version:** 1.0  
**Date:** 2025-11-06  
**Status:** 🏗️ DESIGN SPECIFICATION  
**Purpose:** Interface specifications for all CORTEX agents

---

## 🎯 Overview

**Total Agents:** 10  
**Architecture:** Event-driven message passing  
**Communication:** SQLite message queue + in-memory events  
**Error Handling:** Standardized error codes and recovery strategies  

**Agent Categories:**
- **Core Routing:** IntentRouter (1 agent)
- **Planning:** WorkPlanner, ReadinessValidator (2 agents)
- **Execution:** CodeExecutor, TestGenerator (2 agents)
- **Quality:** HealthValidator, BrainProtector (2 agents)
- **Intelligence:** ContextAnalyzer, PatternMiner, ConversationSummarizer (3 agents)

---

## 📋 Common Contract Elements

All agents implement the base `Agent` interface:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"
    DISABLED = "disabled"

@dataclass
class AgentMessage:
    """Standard message format between agents."""
    id: str                          # Unique message ID
    from_agent: str                  # Source agent name
    to_agent: str                    # Target agent name
    message_type: str                # Message type (request, response, event, error)
    payload: Dict[str, Any]          # Message data
    conversation_id: str             # Current conversation ID
    timestamp: str                   # ISO 8601 timestamp
    correlation_id: Optional[str]    # For request-response pairing
    priority: int = 0                # 0=normal, 1=high, 2=critical

@dataclass
class AgentResponse:
    """Standard response format."""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional['AgentError']
    metadata: Dict[str, Any]

@dataclass
class AgentError:
    """Standard error format."""
    code: str                        # Error code (e.g., "VALIDATION_FAILED")
    message: str                     # Human-readable message
    severity: str                    # INFO, WARNING, ERROR, CRITICAL
    recoverable: bool                # Can automatically recover?
    recovery_action: Optional[str]   # What to do to recover
    context: Dict[str, Any]          # Additional error context

class Agent(ABC):
    """Base agent interface."""
    
    def __init__(self, name: str, brain_db_path: str):
        self.name = name
        self.brain_db_path = brain_db_path
        self.status = AgentStatus.IDLE
        self.metrics: Dict[str, Any] = {}
    
    @abstractmethod
    async def process_message(self, message: AgentMessage) -> AgentResponse:
        """Process incoming message."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities and supported message types."""
        pass
    
    @abstractmethod
    def health_check(self) -> AgentResponse:
        """Check agent health status."""
        pass
    
    def log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log agent event to BRAIN."""
        # Implementation logs to agent_events table
        pass
```

---

## 🧠 Agent 1: IntentRouter

**Purpose:** Route user requests to appropriate workflow agents  
**Tier Access:** Tier 1 (STM), Tier 2 (Intent Patterns)  
**Dependencies:** None (entry point)

### Input Contract

```python
@dataclass
class IntentRequest:
    """User request to classify."""
    user_message: str                # Raw user input
    conversation_id: str             # Current conversation ID
    context: Dict[str, Any]          # Recent conversation context
    
class IntentRouter(Agent):
    
    async def classify_intent(self, request: IntentRequest) -> AgentResponse:
        """
        Classify user intent and route to appropriate agent.
        
        Returns:
            AgentResponse with data containing:
            - intent: str (PLAN, EXECUTE, TEST, VALIDATE, GOVERN, CORRECT, RESUME, ASK)
            - confidence: float (0.0-1.0)
            - target_agent: str (agent to handle request)
            - extracted_entities: Dict[str, List[str]]
            - routing_metadata: Dict[str, Any]
        
        Errors:
            - INTENT_AMBIGUOUS: Multiple intents detected (severity: WARNING)
            - INTENT_UNKNOWN: No matching pattern (severity: ERROR)
            - CONTEXT_INSUFFICIENT: Need more info (severity: INFO)
        """
        pass
```

### Output Contract

```python
@dataclass
class IntentClassification:
    intent: str                      # PLAN, EXECUTE, TEST, VALIDATE, etc.
    confidence: float                # 0.0-1.0
    target_agent: str                # Next agent to invoke
    extracted_entities: Dict[str, List[str]]  # Files, components, etc.
    routing_metadata: Dict[str, Any] # Additional routing info
```

### Message Types

- **REQUEST:** `classify_intent` - Classify user message
- **EVENT:** `intent_classified` - Broadcast classification result
- **EVENT:** `intent_ambiguous` - Multiple intents detected (need clarification)

### Performance SLA

- **Latency:** <50ms (fast intent lookup)
- **Accuracy:** >95% (based on Tier 2 patterns)
- **Throughput:** 1000 requests/min

### Error Recovery

```python
ERROR_RECOVERY = {
    "INTENT_AMBIGUOUS": {
        "action": "ask_user",
        "prompt": "I detected multiple possible intents: {intents}. Which would you like?",
        "fallback": "PLAN"  # Default to planning
    },
    "INTENT_UNKNOWN": {
        "action": "default_to_ask",
        "prompt": "I'm not sure what you'd like me to do. Can you rephrase?",
        "fallback": "ASK"
    },
    "CONTEXT_INSUFFICIENT": {
        "action": "gather_context",
        "prompt": "Could you provide more details about {missing_context}?",
        "fallback": "ASK"
    }
}
```

---

## 📋 Agent 2: WorkPlanner

**Purpose:** Plan work breakdown and task sequencing  
**Tier Access:** Tier 2 (Workflow Patterns), Tier 3 (Git Metrics)  
**Dependencies:** ReadinessValidator

### Input Contract

```python
@dataclass
class PlanRequest:
    """Request to create work plan."""
    goal: str                        # What to accomplish
    conversation_id: str
    constraints: Optional[Dict[str, Any]]  # Time, scope, dependencies
    context: Dict[str, Any]          # Current project state
    
class WorkPlanner(Agent):
    
    async def create_plan(self, request: PlanRequest) -> AgentResponse:
        """
        Create step-by-step work plan.
        
        Returns:
            AgentResponse with data containing:
            - plan_id: str (unique plan identifier)
            - steps: List[PlanStep] (ordered work steps)
            - estimated_duration: int (seconds)
            - dependencies: Dict[str, List[str]] (step dependencies)
            - validation_criteria: Dict[str, Any]
        
        Errors:
            - GOAL_UNCLEAR: Insufficient detail (severity: ERROR)
            - DEPENDENCIES_UNMET: Prerequisites missing (severity: CRITICAL)
            - PATTERN_NOT_FOUND: No matching workflow (severity: WARNING)
        """
        pass
    
    async def validate_plan(self, plan_id: str) -> AgentResponse:
        """
        Validate plan against Definition of READY.
        
        Delegates to ReadinessValidator agent.
        """
        pass
```

### Output Contract

```python
@dataclass
class PlanStep:
    step_number: int
    step_type: str                   # plan, test_create, implement, refactor, validate
    description: str
    agent: str                       # Which agent executes this step
    estimated_duration: int          # Seconds
    dependencies: List[int]          # Step numbers this depends on
    validation: Dict[str, Any]       # How to validate completion
    
@dataclass
class WorkPlan:
    plan_id: str
    goal: str
    steps: List[PlanStep]
    total_estimated_duration: int
    created_at: str
    pattern_used: Optional[str]      # Workflow pattern applied
```

### Message Types

- **REQUEST:** `create_plan` - Generate work plan
- **REQUEST:** `validate_plan` - Check plan readiness
- **REQUEST:** `update_plan` - Modify existing plan
- **EVENT:** `plan_created` - New plan available
- **EVENT:** `plan_validated` - Plan passed DoR

### Performance SLA

- **Latency:** <200ms (pattern matching + step generation)
- **Plan Quality:** >90% first-time acceptance rate
- **Pattern Usage:** Use existing pattern if confidence >0.7

### Error Recovery

```python
ERROR_RECOVERY = {
    "GOAL_UNCLEAR": {
        "action": "ask_clarifying_questions",
        "questions": ["What specific outcome do you want?", "What files are involved?"],
        "fallback": None  # Cannot proceed without clarity
    },
    "DEPENDENCIES_UNMET": {
        "action": "add_prerequisite_steps",
        "auto_resolve": True,
        "notify_user": True
    },
    "PATTERN_NOT_FOUND": {
        "action": "create_generic_plan",
        "confidence": 0.5,
        "notify_user": True  # Warn that plan is generic
    }
}
```

---

## ✅ Agent 3: ReadinessValidator

**Purpose:** Validate Definition of READY compliance  
**Tier Access:** Tier 0 (Governance Rules), Tier 2 (Validation Insights)  
**Dependencies:** None

### Input Contract

```python
@dataclass
class ReadinessRequest:
    """Request to validate readiness."""
    plan_id: str                     # Plan to validate
    conversation_id: str
    
class ReadinessValidator(Agent):
    
    async def validate_readiness(self, request: ReadinessRequest) -> AgentResponse:
        """
        Check if plan meets Definition of READY.
        
        Validates:
        - Goal clarity (specific, measurable)
        - File scope defined
        - Dependencies identified
        - Test strategy present
        - Acceptance criteria clear
        
        Returns:
            AgentResponse with data containing:
            - ready: bool (passes all criteria)
            - checklist: Dict[str, bool] (individual checks)
            - blockers: List[str] (what's missing)
            - recommendations: List[str]
        
        Errors:
            - PLAN_NOT_FOUND: Plan ID doesn't exist (severity: ERROR)
            - INCOMPLETE_PLAN: Missing required elements (severity: WARNING)
        """
        pass
```

### Output Contract

```python
@dataclass
class ReadinessReport:
    ready: bool                      # Overall readiness
    checklist: Dict[str, bool]       # Individual criteria
    score: float                     # 0.0-1.0 (percentage of criteria met)
    blockers: List[str]              # What prevents proceeding
    recommendations: List[str]       # How to improve readiness
    validated_at: str

# DoR Criteria
DOR_CRITERIA = {
    "goal_specific": "Goal is specific and measurable",
    "files_identified": "Target files are identified",
    "dependencies_clear": "Dependencies are documented",
    "test_strategy": "Testing approach is defined",
    "acceptance_criteria": "Success criteria are clear",
    "no_blockers": "No external blockers exist"
}
```

### Message Types

- **REQUEST:** `validate_readiness` - Check DoR compliance
- **RESPONSE:** `readiness_report` - Validation results
- **EVENT:** `ready_approved` - Plan meets DoR
- **EVENT:** `ready_rejected` - Plan needs improvement

### Performance SLA

- **Latency:** <100ms (rule-based validation)
- **Accuracy:** 100% (deterministic checks)
- **False Positives:** 0% (no approval without meeting criteria)

---

## 💻 Agent 4: CodeExecutor

**Purpose:** Execute code changes with TDD enforcement  
**Tier Access:** Tier 0 (TDD Rules), Tier 2 (Architectural Patterns), Tier 3 (File Hotspots)  
**Dependencies:** TestGenerator, HealthValidator

### Input Contract

```python
@dataclass
class ExecutionRequest:
    """Request to execute code changes."""
    plan_step_id: str                # Which step to execute
    conversation_id: str
    files_to_modify: List[str]
    changes: List[Dict[str, Any]]    # Specific changes to make
    test_first: bool = True          # Enforce TDD
    
class CodeExecutor(Agent):
    
    async def execute_changes(self, request: ExecutionRequest) -> AgentResponse:
        """
        Execute code changes with TDD validation.
        
        Workflow:
        1. If test_first: Verify tests exist and fail (RED)
        2. Apply code changes
        3. Run tests to verify they pass (GREEN)
        4. Run health check (zero errors/warnings)
        5. Log execution to Tier 3
        
        Returns:
            AgentResponse with data containing:
            - execution_id: str
            - files_modified: List[str]
            - tests_run: int
            - tests_passed: int
            - health_status: str (PASS, FAIL)
            - duration_seconds: float
        
        Errors:
            - TDD_VIOLATION: No tests exist (severity: CRITICAL)
            - TEST_NOT_RED: Tests pass before implementation (severity: ERROR)
            - TEST_NOT_GREEN: Tests fail after implementation (severity: CRITICAL)
            - HEALTH_CHECK_FAILED: Errors/warnings present (severity: CRITICAL)
        """
        pass
```

### Output Contract

```python
@dataclass
class ExecutionResult:
    execution_id: str
    success: bool
    files_modified: List[str]
    lines_changed: int
    tests_run: int
    tests_passed: int
    health_status: str               # PASS, FAIL, WARNING
    duration_seconds: float
    tdd_compliance: bool             # Followed RED→GREEN→REFACTOR
    executed_at: str

# TDD Enforcement Levels
TDD_ENFORCEMENT = {
    "STRICT": {
        "require_tests": True,
        "require_red_first": True,
        "require_green_after": True,
        "block_on_violation": True
    },
    "RECOMMENDED": {
        "require_tests": True,
        "require_red_first": False,
        "require_green_after": True,
        "block_on_violation": False  # Warn but allow
    },
    "FLEXIBLE": {
        "require_tests": False,
        "require_red_first": False,
        "require_green_after": False,
        "block_on_violation": False
    }
}
```

### Message Types

- **REQUEST:** `execute_changes` - Apply code modifications
- **REQUEST:** `rollback_changes` - Undo last execution
- **EVENT:** `execution_started` - Beginning execution
- **EVENT:** `execution_completed` - Execution finished
- **EVENT:** `tdd_violation_detected` - TDD rules broken
- **EVENT:** `health_check_failed` - Code has errors/warnings

### Performance SLA

- **Latency:** <5s per file (including test execution)
- **TDD Compliance:** 100% (strict enforcement)
- **Rollback Time:** <1s (git-based rollback)

### Error Recovery

```python
ERROR_RECOVERY = {
    "TDD_VIOLATION": {
        "action": "invoke_test_generator",
        "message": "No tests found. Generating tests first...",
        "auto_resolve": True,
        "block_execution": True
    },
    "TEST_NOT_RED": {
        "action": "investigate_test",
        "message": "Tests should fail before implementation. Investigating...",
        "auto_resolve": False,
        "block_execution": True
    },
    "TEST_NOT_GREEN": {
        "action": "rollback_and_retry",
        "message": "Tests failed. Rolling back changes...",
        "auto_resolve": True,
        "max_retries": 3
    },
    "HEALTH_CHECK_FAILED": {
        "action": "invoke_health_validator",
        "message": "Code has errors. Running diagnostics...",
        "auto_resolve": False,
        "block_execution": True
    }
}
```

---

## 🧪 Agent 5: TestGenerator

**Purpose:** Generate tests following TDD principles  
**Tier Access:** Tier 2 (Test Patterns), Tier 3 (Test Metrics, Flaky Tests)  
**Dependencies:** None

### Input Contract

```python
@dataclass
class TestGenerationRequest:
    """Request to generate tests."""
    target_file: str                 # File to test
    test_type: str                   # ui, unit, integration, e2e
    conversation_id: str
    behavior_description: str        # What to test
    existing_tests: Optional[List[str]]  # Existing test files
    
class TestGenerator(Agent):
    
    async def generate_tests(self, request: TestGenerationRequest) -> AgentResponse:
        """
        Generate test file(s) for target code.
        
        Strategy:
        1. Analyze target file structure
        2. Identify testable behaviors
        3. Apply test pattern from Tier 2
        4. Generate test code
        5. Ensure tests fail initially (RED)
        
        Returns:
            AgentResponse with data containing:
            - test_files: List[str] (generated test file paths)
            - test_count: int (number of tests)
            - framework: str (test framework used)
            - coverage_target: float (expected coverage)
            - pattern_used: str (test pattern applied)
        
        Errors:
            - TARGET_NOT_FOUND: File doesn't exist (severity: ERROR)
            - NO_TESTABLE_BEHAVIOR: Nothing to test (severity: WARNING)
            - PATTERN_MISMATCH: No suitable pattern (severity: INFO)
        """
        pass
    
    async def detect_flaky_tests(self) -> AgentResponse:
        """
        Identify flaky tests from Tier 3 metrics.
        
        Returns list of tests with failure_rate between 0.05-0.95.
        """
        pass
```

### Output Contract

```python
@dataclass
class TestGenerationResult:
    test_files: List[str]            # Created test files
    test_count: int                  # Total tests generated
    framework: str                   # Jest, Playwright, xUnit, etc.
    coverage_target: float           # 0.0-1.0
    pattern_used: str                # Pattern from Tier 2
    generated_at: str
    initial_status: str              # Should be "RED" (failing)

# Test Pattern Selection
TEST_PATTERNS = {
    "ui": {
        "framework": "Playwright",
        "selector_strategy": "ID-based",
        "template": "page_object_model"
    },
    "unit": {
        "framework": "Jest",
        "style": "AAA (Arrange-Act-Assert)",
        "template": "describe_it_pattern"
    },
    "integration": {
        "framework": "Jest",
        "style": "Given-When-Then",
        "template": "integration_test_pattern"
    },
    "e2e": {
        "framework": "Playwright",
        "style": "User journey",
        "template": "e2e_scenario_pattern"
    }
}
```

### Message Types

- **REQUEST:** `generate_tests` - Create test file
- **REQUEST:** `update_tests` - Modify existing tests
- **REQUEST:** `detect_flaky_tests` - Find unreliable tests
- **EVENT:** `tests_generated` - Tests created
- **EVENT:** `flaky_test_detected` - Unreliable test found

### Performance SLA

- **Latency:** <3s per test file
- **Test Quality:** 0 flaky tests on first generation
- **Coverage:** >80% code coverage per file

---

## 🏥 Agent 6: HealthValidator

**Purpose:** Validate Definition of DONE compliance  
**Tier Access:** Tier 0 (DoD Rules), Tier 3 (Build Metrics)  
**Dependencies:** None

### Input Contract

```python
@dataclass
class HealthCheckRequest:
    """Request health validation."""
    scope: str                       # file, project, full
    conversation_id: str
    files: Optional[List[str]]       # Specific files to check
    
class HealthValidator(Agent):
    
    async def check_health(self, request: HealthCheckRequest) -> AgentResponse:
        """
        Validate Definition of DONE compliance.
        
        Checks:
        - Zero compilation errors
        - Zero linting warnings
        - All tests passing
        - Build succeeds
        - Code coverage threshold met
        
        Returns:
            AgentResponse with data containing:
            - healthy: bool (all checks pass)
            - errors: List[Dict] (compilation errors)
            - warnings: List[Dict] (linting warnings)
            - test_results: Dict (test execution summary)
            - build_status: str (SUCCESS, FAILED)
            - coverage: float (0.0-1.0)
        
        Errors:
            - COMPILATION_ERROR: Code doesn't compile (severity: CRITICAL)
            - LINT_WARNING: Code style issues (severity: WARNING)
            - TEST_FAILURE: Tests don't pass (severity: CRITICAL)
            - BUILD_FAILURE: Build fails (severity: CRITICAL)
            - COVERAGE_BELOW_THRESHOLD: <80% coverage (severity: WARNING)
        """
        pass
```

### Output Contract

```python
@dataclass
class HealthReport:
    healthy: bool                    # Overall health
    timestamp: str
    scope: str                       # What was checked
    errors: List[Dict[str, Any]]     # Compilation errors
    warnings: List[Dict[str, Any]]   # Linting warnings
    test_results: Dict[str, Any]     # Test execution summary
    build_status: str                # SUCCESS, FAILED, SKIPPED
    coverage: float                  # 0.0-1.0
    dod_compliance: Dict[str, bool]  # Individual DoD criteria

# DoD Criteria
DOD_CRITERIA = {
    "zero_errors": "No compilation/runtime errors",
    "zero_warnings": "No linting warnings",
    "tests_pass": "All tests passing",
    "build_succeeds": "Project builds successfully",
    "coverage_met": "Coverage ≥80%",
    "code_reviewed": "Changes peer-reviewed (optional)"
}
```

### Message Types

- **REQUEST:** `check_health` - Validate health
- **EVENT:** `health_check_passed` - All criteria met
- **EVENT:** `health_check_failed` - Issues detected
- **EVENT:** `dod_violation_detected` - Specific DoD failure

### Performance SLA

- **Latency:** <10s (full project check), <2s (single file)
- **Accuracy:** 100% (automated checks)
- **False Negatives:** 0% (all issues caught)

---

## 🛡️ Agent 7: BrainProtector

**Purpose:** Protect BRAIN integrity from risky operations  
**Tier Access:** Tier 0 (Brain Protection Rules), All Tiers (read access)  
**Dependencies:** All agents (monitors their actions)

### Input Contract

```python
@dataclass
class ProtectionRequest:
    """Request to validate risky operation."""
    operation: str                   # What action is being attempted
    target: str                      # What's being modified (file, table, etc.)
    agent: str                       # Who's attempting it
    conversation_id: str
    justification: str               # Why this operation is needed
    
class BrainProtector(Agent):
    
    async def validate_operation(self, request: ProtectionRequest) -> AgentResponse:
        """
        Validate operation against Brain Protection rules.
        
        Risky Operations:
        - Deleting BRAIN database files
        - Modifying governance rules
        - Dropping database tables
        - Clearing all conversations
        - Changing schema structure
        
        Returns:
            AgentResponse with data containing:
            - approved: bool (operation safe)
            - risk_level: str (LOW, MEDIUM, HIGH, CRITICAL)
            - require_confirmation: bool (user must approve)
            - backup_recommended: bool (backup first)
            - alternative_action: Optional[str]
        
        Errors:
            - OPERATION_DENIED: Too risky (severity: CRITICAL)
            - BACKUP_REQUIRED: Must backup first (severity: ERROR)
            - USER_CONFIRMATION_REQUIRED: Need approval (severity: WARNING)
        """
        pass
    
    async def create_backup(self, scope: str = "full") -> AgentResponse:
        """Create BRAIN backup before risky operation."""
        pass
```

### Output Contract

```python
@dataclass
class ProtectionDecision:
    approved: bool
    risk_level: str                  # LOW, MEDIUM, HIGH, CRITICAL
    require_confirmation: bool       # Ask user first?
    backup_recommended: bool         # Backup before proceeding?
    alternative_action: Optional[str]  # Safer alternative
    reasoning: str                   # Why this decision

# Risk Classification
RISK_LEVELS = {
    "LOW": {
        "examples": ["Reading data", "Querying patterns"],
        "auto_approve": True,
        "require_backup": False
    },
    "MEDIUM": {
        "examples": ["Adding conversation", "Creating pattern"],
        "auto_approve": True,
        "require_backup": False
    },
    "HIGH": {
        "examples": ["Deleting conversation", "Modifying rule"],
        "auto_approve": False,
        "require_backup": True
    },
    "CRITICAL": {
        "examples": ["Dropping table", "Deleting database", "Schema change"],
        "auto_approve": False,
        "require_backup": True,
        "require_confirmation": True
    }
}
```

### Message Types

- **REQUEST:** `validate_operation` - Check if safe
- **REQUEST:** `create_backup` - Backup BRAIN
- **EVENT:** `operation_denied` - Blocked risky action
- **EVENT:** `backup_created` - Backup completed
- **EVENT:** `user_confirmation_requested` - Need approval

### Performance SLA

- **Latency:** <50ms (rule-based decision)
- **False Positives:** <5% (occasionally over-cautious)
- **False Negatives:** 0% (never approve dangerous operation)

---

## 📊 Agent 8: ContextAnalyzer

**Purpose:** Analyze development context and generate insights  
**Tier Access:** Tier 3 (all context tables)  
**Dependencies:** None

### Input Contract

```python
@dataclass
class AnalysisRequest:
    """Request context analysis."""
    analysis_type: str               # velocity, hotspots, correlations, productivity
    timeframe_days: int = 30
    conversation_id: str
    
class ContextAnalyzer(Agent):
    
    async def analyze_context(self, request: AnalysisRequest) -> AgentResponse:
        """
        Analyze development metrics and generate insights.
        
        Analysis Types:
        - velocity: Git commit trends
        - hotspots: File churn analysis
        - correlations: Metric relationships
        - productivity: Best work times
        - test_health: Test reliability trends
        
        Returns:
            AgentResponse with data containing:
            - insights: List[Dict] (discovered insights)
            - trends: Dict (metric trends)
            - anomalies: List[Dict] (unusual patterns)
            - recommendations: List[str]
        
        Errors:
            - INSUFFICIENT_DATA: Not enough metrics (severity: WARNING)
            - ANALYSIS_FAILED: Calculation error (severity: ERROR)
        """
        pass
    
    async def generate_proactive_insights(self) -> AgentResponse:
        """
        Proactively detect issues and opportunities.
        
        Runs on schedule (every hour) to detect:
        - Velocity drops
        - File hotspots
        - Flaky tests
        - Build health degradation
        """
        pass
```

### Output Contract

```python
@dataclass
class ContextInsight:
    insight_type: str                # velocity_drop, file_hotspot, etc.
    severity: str                    # INFO, WARNING, ERROR, CRITICAL
    title: str
    description: str
    recommendation: str
    data_snapshot: Dict[str, Any]
    created_at: str

# Insight Detection Thresholds
INSIGHT_THRESHOLDS = {
    "velocity_drop": {
        "trigger": "commits_per_week < avg * 0.5",
        "severity": "WARNING"
    },
    "file_hotspot": {
        "trigger": "churn_rate > 0.2",
        "severity": "WARNING"
    },
    "flaky_test": {
        "trigger": "failure_rate between 0.05 and 0.95",
        "severity": "ERROR"
    },
    "build_health": {
        "trigger": "success_rate < 0.9",
        "severity": "CRITICAL"
    }
}
```

### Message Types

- **REQUEST:** `analyze_context` - Run analysis
- **REQUEST:** `generate_proactive_insights` - Detect issues
- **EVENT:** `insight_generated` - New insight created
- **EVENT:** `anomaly_detected` - Unusual pattern found

### Performance SLA

- **Latency:** <500ms (complex aggregations)
- **Insight Accuracy:** >85% (useful insights)
- **False Alerts:** <10% (minimize noise)

---

## 🔍 Agent 9: PatternMiner

**Purpose:** Extract patterns from conversations and build LTM  
**Tier Access:** Tier 1 (Conversations), Tier 2 (Patterns)  
**Dependencies:** None

### Input Contract

```python
@dataclass
class MiningRequest:
    """Request pattern mining."""
    source_conversations: List[str]  # Conversation IDs to mine
    pattern_types: List[str]         # Which patterns to extract
    conversation_id: str
    
class PatternMiner(Agent):
    
    async def mine_patterns(self, request: MiningRequest) -> AgentResponse:
        """
        Extract patterns from completed conversations.
        
        Pattern Types:
        - workflow: Task sequences
        - intent: Language→Intent mappings
        - file_relationship: Co-modified files
        - architectural: Component structures
        - validation: Common mistakes
        - correction: Error→Fix mappings
        
        Returns:
            AgentResponse with data containing:
            - patterns_extracted: int
            - patterns_updated: int
            - confidence_avg: float
            - pattern_ids: List[str]
        
        Errors:
            - NO_CONVERSATIONS: No data to mine (severity: WARNING)
            - EXTRACTION_FAILED: Pattern detection error (severity: ERROR)
        """
        pass
    
    async def consolidate_patterns(self, min_confidence: float = 0.7) -> AgentResponse:
        """
        Merge similar patterns to reduce duplication.
        
        Runs periodically to keep Tier 2 clean.
        """
        pass
```

### Output Contract

```python
@dataclass
class PatternExtractionResult:
    patterns_extracted: int          # New patterns created
    patterns_updated: int            # Existing patterns strengthened
    patterns_consolidated: int       # Duplicates merged
    confidence_avg: float            # Average confidence
    pattern_ids: List[str]           # Created/updated pattern IDs
    extracted_at: str

# Pattern Confidence Calculation
CONFIDENCE_FORMULA = """
confidence = (
    base_confidence * 0.3 +          # Initial extraction quality
    (success_count / usage_count) * 0.5 +  # Success rate
    min(usage_count / 10, 1.0) * 0.2  # Usage frequency (capped at 10)
)
"""
```

### Message Types

- **REQUEST:** `mine_patterns` - Extract from conversations
- **REQUEST:** `consolidate_patterns` - Merge duplicates
- **EVENT:** `patterns_extracted` - New patterns added
- **EVENT:** `pattern_strengthened` - Existing pattern confirmed

### Performance SLA

- **Latency:** <2s per conversation
- **Pattern Quality:** Average confidence >0.7
- **Duplicate Rate:** <5% (effective consolidation)

---

## 💬 Agent 10: ConversationSummarizer

**Purpose:** Summarize conversations for LTM extraction  
**Tier Access:** Tier 1 (Conversations, Messages)  
**Dependencies:** PatternMiner

### Input Contract

```python
@dataclass
class SummarizationRequest:
    """Request conversation summary."""
    conversation_id: str
    destination: str                 # STM, LTM, or both
    
class ConversationSummarizer(Agent):
    
    async def summarize_conversation(self, request: SummarizationRequest) -> AgentResponse:
        """
        Create conversation summary for storage.
        
        Summary Includes:
        - Intent classification
        - Key entities (files, components)
        - Outcome (success, abandoned, error)
        - Duration and message count
        - Files modified
        - Tests created/run
        - Patterns observed
        
        Returns:
            AgentResponse with data containing:
            - summary: ConversationSummary
            - extractable_patterns: List[str] (pattern types found)
            - quality_score: float (summary quality)
        
        Errors:
            - CONVERSATION_NOT_FOUND: Invalid ID (severity: ERROR)
            - INCOMPLETE_CONVERSATION: Still active (severity: WARNING)
        """
        pass
```

### Output Contract

```python
@dataclass
class ConversationSummary:
    conversation_id: str
    topic: str
    intent: str
    entities: Dict[str, List[str]]   # Files, components, agents, etc.
    outcome: str                     # success, abandoned, error
    duration_seconds: int
    message_count: int
    files_modified: List[str]
    tests_created: List[str]
    patterns_observed: List[str]
    key_decisions: List[str]
    challenges_encountered: List[str]
    quality_score: float             # 0.0-1.0
    summarized_at: str
```

### Message Types

- **REQUEST:** `summarize_conversation` - Create summary
- **EVENT:** `conversation_summarized` - Summary complete
- **EVENT:** `ready_for_mining` - Patterns can be extracted

### Performance SLA

- **Latency:** <1s per conversation
- **Summary Quality:** >0.8 (comprehensive and accurate)
- **Pattern Detection:** >90% (identify all learnable patterns)

---

## 📡 Inter-Agent Communication

### Message Queue Architecture

```python
class MessageQueue:
    """Central message queue for agent communication."""
    
    async def publish(self, message: AgentMessage) -> None:
        """Publish message to queue."""
        # Store in SQLite agent_messages table
        pass
    
    async def subscribe(self, agent_name: str) -> AsyncIterator[AgentMessage]:
        """Subscribe to messages for agent."""
        # Poll SQLite for new messages
        pass
    
    async def acknowledge(self, message_id: str) -> None:
        """Mark message as processed."""
        pass
```

### Message Flow Examples

**Example 1: User Request → Code Change**

```
User: "Add login button to homepage"
  ↓
IntentRouter (classify) → EXECUTE intent
  ↓
WorkPlanner (create_plan) → [test_create, implement, validate]
  ↓
ReadinessValidator (validate_readiness) → APPROVED
  ↓
TestGenerator (generate_tests) → login_button.test.ts
  ↓
CodeExecutor (execute_changes) → homepage.tsx modified
  ↓
HealthValidator (check_health) → PASS
  ↓
ConversationSummarizer (summarize) → Save to STM
```

**Example 2: Pattern Learning**

```
Conversation completed
  ↓
ConversationSummarizer (summarize) → Extract metadata
  ↓
PatternMiner (mine_patterns) → Create workflow pattern
  ↓
Tier 2 (LTM) updated with new pattern
```

**Example 3: Proactive Insight**

```
ContextAnalyzer (scheduled run every hour)
  ↓
Analyze Tier 3 metrics
  ↓
Detect velocity drop (commits down 60%)
  ↓
Generate insight → "VELOCITY_DROP" (severity: WARNING)
  ↓
Store in context_insights table
  ↓
Next user interaction → Show insight as proactive warning
```

---

## 🔧 Agent Lifecycle Management

### Agent Registration

```python
class AgentRegistry:
    """Central registry for all agents."""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
    
    def register(self, agent: Agent) -> None:
        """Register agent with system."""
        self.agents[agent.name] = agent
        agent.log_event("agent_registered", {"name": agent.name})
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """Retrieve agent by name."""
        return self.agents.get(name)
    
    async def health_check_all(self) -> Dict[str, AgentResponse]:
        """Check health of all agents."""
        results = {}
        for name, agent in self.agents.items():
            results[name] = await agent.health_check()
        return results
```

### Agent Monitoring

```sql
-- Agent Events Table
CREATE TABLE agent_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_data TEXT,                    -- JSON
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    conversation_id TEXT
);

-- Agent Metrics Table
CREATE TABLE agent_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    unit TEXT,
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Example metrics
INSERT INTO agent_metrics (agent_name, metric_name, metric_value, unit) VALUES
('IntentRouter', 'avg_latency_ms', 42.5, 'ms'),
('CodeExecutor', 'executions_count', 156, 'count'),
('TestGenerator', 'tests_generated', 89, 'count');
```

---

## ✅ Testing Agent Contracts

### Contract Testing

```python
import pytest
from unittest.mock import Mock, AsyncMock

class TestIntentRouterContract:
    """Test IntentRouter adheres to contract."""
    
    @pytest.fixture
    def router(self):
        return IntentRouter("intent-router", ":memory:")
    
    async def test_classify_intent_returns_correct_structure(self, router):
        """Verify response matches AgentResponse schema."""
        request = IntentRequest(
            user_message="Create a login form",
            conversation_id="test_conv",
            context={}
        )
        
        response = await router.classify_intent(request)
        
        # Verify response structure
        assert isinstance(response, AgentResponse)
        assert response.success is True
        assert "intent" in response.data
        assert "confidence" in response.data
        assert "target_agent" in response.data
        
        # Verify data types
        assert isinstance(response.data["intent"], str)
        assert 0.0 <= response.data["confidence"] <= 1.0
    
    async def test_classify_intent_handles_errors(self, router):
        """Verify error handling follows contract."""
        request = IntentRequest(
            user_message="",  # Invalid empty message
            conversation_id="test_conv",
            context={}
        )
        
        response = await router.classify_intent(request)
        
        assert response.success is False
        assert response.error is not None
        assert response.error.code in ["INTENT_UNKNOWN", "CONTEXT_INSUFFICIENT"]
        assert response.error.recoverable is True
```

### Integration Testing

```python
class TestAgentIntegration:
    """Test agents work together correctly."""
    
    async def test_full_execution_workflow(self):
        """Test complete workflow from intent to execution."""
        # Setup
        router = IntentRouter("router", "test.db")
        planner = WorkPlanner("planner", "test.db")
        validator = ReadinessValidator("validator", "test.db")
        executor = CodeExecutor("executor", "test.db")
        
        # Step 1: Classify intent
        intent_response = await router.classify_intent(IntentRequest(
            user_message="Add logout button",
            conversation_id="test",
            context={}
        ))
        assert intent_response.data["intent"] == "EXECUTE"
        
        # Step 2: Create plan
        plan_response = await planner.create_plan(PlanRequest(
            goal="Add logout button",
            conversation_id="test",
            constraints={},
            context={}
        ))
        assert plan_response.success is True
        
        # Step 3: Validate readiness
        ready_response = await validator.validate_readiness(ReadinessRequest(
            plan_id=plan_response.data["plan_id"],
            conversation_id="test"
        ))
        assert ready_response.data["ready"] is True
        
        # Step 4: Execute (would normally execute actual code)
        # ... execution test
```

---

## 📚 Related Documentation

- [Overview](overview.md) - System architecture
- [Tier 0: Governance](tier0-governance.md) - Rules enforced by agents
- [Tier 1: STM Design](tier1-stm-design.md) - Conversation storage
- [Tier 2: LTM Design](tier2-ltm-design.md) - Pattern storage
- [Tier 3: Context Design](tier3-context-design.md) - Metrics storage
- [Storage Schema](storage-schema.md) - Database tables used by agents

---

**Status:** ✅ Agent Contracts Complete  
**Next:** Begin Phase Plan documents  
**Version:** 1.0 (Initial specification)
