"""
Agent Type Definitions and Enums

Defines common types and enumerations used across all CORTEX agents.
"""

from enum import Enum, auto
from typing import List


class AgentType(Enum):
    """Categories of specialist agents"""
    ROUTER = auto()          # IntentRouter
    PLANNER = auto()         # WorkPlanner
    EXECUTOR = auto()        # CodeExecutor
    TESTER = auto()          # TestGenerator
    VALIDATOR = auto()       # HealthValidator
    GOVERNOR = auto()        # ChangeGovernor
    CORRECTOR = auto()       # ErrorCorrector
    RESUMER = auto()         # SessionResumer
    ANALYZER = auto()        # ScreenshotAnalyzer
    COMMITTER = auto()       # CommitHandler


class IntentType(Enum):
    """Common user intent categories"""
    # Planning intents
    PLAN = "plan"
    FEATURE = "feature"
    TASK_BREAKDOWN = "task_breakdown"
    
    # Execution intents
    CODE = "code"
    IMPLEMENT = "implement"
    CREATE_FILE = "create_file"
    EDIT_FILE = "edit_file"
    
    # Testing intents
    TEST = "test"
    TDD = "tdd"
    RUN_TESTS = "run_tests"
    
    # Health/validation intents
    HEALTH_CHECK = "health_check"
    VALIDATE = "validate"
    REVIEW = "review"
    
    # Error correction intents
    FIX = "fix"
    DEBUG = "debug"
    ERROR = "error"
    
    # Session management
    RESUME = "resume"
    CONTEXT = "context"
    
    # UI/Screenshot analysis
    SCREENSHOT = "screenshot"
    UI_ANALYSIS = "ui_analysis"
    
    # Git operations
    COMMIT = "commit"
    GIT = "git"
    
    # Governance
    CHECK_RULES = "check_rules"
    COMPLIANCE = "compliance"
    
    # Unknown/fallback
    UNKNOWN = "unknown"


class Priority(Enum):
    """Task priority levels"""
    CRITICAL = 1    # Must execute immediately
    HIGH = 2        # Execute soon
    NORMAL = 3      # Standard priority
    LOW = 4         # Can defer
    BACKGROUND = 5  # Run when idle


class ResponseStatus(Enum):
    """Agent response status codes"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    ERROR = "error"
    DEFERRED = "deferred"
    REQUIRES_INPUT = "requires_input"


class RiskLevel(Enum):
    """Risk levels for change governance"""
    LOW = "LOW"              # Simple, safe changes
    MEDIUM = "MEDIUM"        # Multiple files, moderate impact
    HIGH = "HIGH"            # Protected files, deletions
    CRITICAL = "CRITICAL"    # Governance violations, system integrity


# Intent to Agent Type mapping
INTENT_AGENT_MAP = {
    IntentType.PLAN: AgentType.PLANNER,
    IntentType.FEATURE: AgentType.PLANNER,
    IntentType.TASK_BREAKDOWN: AgentType.PLANNER,
    
    IntentType.CODE: AgentType.EXECUTOR,
    IntentType.IMPLEMENT: AgentType.EXECUTOR,
    IntentType.CREATE_FILE: AgentType.EXECUTOR,
    IntentType.EDIT_FILE: AgentType.EXECUTOR,
    
    IntentType.TEST: AgentType.TESTER,
    IntentType.TDD: AgentType.TESTER,
    IntentType.RUN_TESTS: AgentType.TESTER,
    
    IntentType.HEALTH_CHECK: AgentType.VALIDATOR,
    IntentType.VALIDATE: AgentType.VALIDATOR,
    IntentType.REVIEW: AgentType.VALIDATOR,
    
    IntentType.FIX: AgentType.CORRECTOR,
    IntentType.DEBUG: AgentType.CORRECTOR,
    IntentType.ERROR: AgentType.CORRECTOR,
    
    IntentType.RESUME: AgentType.RESUMER,
    IntentType.CONTEXT: AgentType.RESUMER,
    
    IntentType.SCREENSHOT: AgentType.ANALYZER,
    IntentType.UI_ANALYSIS: AgentType.ANALYZER,
    
    IntentType.COMMIT: AgentType.COMMITTER,
    IntentType.GIT: AgentType.COMMITTER,
    
    IntentType.CHECK_RULES: AgentType.GOVERNOR,
    IntentType.COMPLIANCE: AgentType.GOVERNOR,
}


def get_agent_for_intent(intent: IntentType) -> AgentType:
    """Map an intent to its primary agent type"""
    return INTENT_AGENT_MAP.get(intent, AgentType.ROUTER)


def get_intents_for_agent(agent_type: AgentType) -> List[IntentType]:
    """Get all intents handled by an agent type"""
    return [
        intent for intent, agent in INTENT_AGENT_MAP.items()
        if agent == agent_type
    ]
