"""
Agent Type Definitions and Enums

Defines common types and enumerations used across all CORTEX agents.
"""

from enum import Enum, auto
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


class AgentType(Enum):
    """Categories of specialist agents"""
    ROUTER = auto()          # IntentRouter
    ARCHITECT = auto()       # ArchitectAgent (NEW - Strategic architectural analysis)
    ARCHITECTURE_INTELLIGENCE = auto()  # ArchitectureIntelligenceAgent (NEW - Architecture health analysis)
    PLANNER = auto()         # WorkPlanner
    EXECUTOR = auto()        # CodeExecutor
    TESTER = auto()          # TestGenerator
    VALIDATOR = auto()       # HealthValidator
    GOVERNOR = auto()        # ChangeGovernor
    CORRECTOR = auto()       # ErrorCorrector
    RESUMER = auto()         # SessionResumer
    ANALYZER = auto()        # ScreenshotAnalyzer
    COMMITTER = auto()       # CommitHandler
    FEEDBACK = auto()        # FeedbackAgent (NEW - Feedback collection)
    PROFILE = auto()         # ProfileAgent (NEW - User Profile System)
    ADO_ORCHESTRATOR = auto() # ADO/Unified Entry Point (NEW - ADO Integration)


class IntentType(Enum):
    """Common user intent categories"""
    # Planning intents
    PLAN = "plan"
    FEATURE = "feature"
    TASK_BREAKDOWN = "task_breakdown"
    
    # Enhancement intents (NEW - for improving existing features)
    ENHANCE = "enhance"
    IMPROVE = "improve"
    EXTEND = "extend"
    
    # Architectural analysis intents (NEW)
    ARCHITECTURE = "architecture"
    ANALYZE_STRUCTURE = "analyze_structure" 
    CRAWL_SYSTEM = "crawl_system"
    ARCHITECTURE_REVIEW = "architecture_review"  # Architecture Intelligence Agent
    ANALYZE_ARCHITECTURAL_HEALTH = "analyze_architectural_health"
    FORECAST_TECHNICAL_DEBT = "forecast_technical_debt"
    TRACK_ARCHITECTURE_EVOLUTION = "track_architecture_evolution"
    
    # Execution intents
    CODE = "code"
    IMPLEMENT = "implement"
    CREATE_FILE = "create_file"
    EDIT_FILE = "edit_file"
    REFACTOR = "refactor"  # NEW - for code improvement without changing behavior
    
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
    
    # Conversation tracking (CORTEX 3.0 Feature 5.1)
    CAPTURE = "capture"
    IMPORT = "import"
    
    # Feedback collection (CORTEX Fix - Issue #4)
    FEEDBACK = "feedback"
    REPORT_ISSUE = "report_issue"
    
    # User profile management (NEW - User Profile System 3.2.1)
    UPDATE_PROFILE = "update_profile"
    
    # ADO (Azure DevOps) operations (NEW - ADO Integration)
    ADO_WORKITEM = "ado_workitem"
    ADO_STORY = "ado_story"
    ADO_FEATURE = "ado_feature"
    ADO_SUMMARY = "ado_summary"
    CODE_REVIEW = "code_review"
    
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
    
    # Enhancement mapping (NEW - crawl existing + plan changes)
    IntentType.ENHANCE: AgentType.ARCHITECT,  # First discovers existing, then routes to PLANNER
    IntentType.IMPROVE: AgentType.ARCHITECT,
    IntentType.EXTEND: AgentType.ARCHITECT,
    
    # Architectural analysis mapping (NEW)
    IntentType.ARCHITECTURE: AgentType.ARCHITECT,
    IntentType.ANALYZE_STRUCTURE: AgentType.ARCHITECT,
    IntentType.CRAWL_SYSTEM: AgentType.ARCHITECT,
    IntentType.ARCHITECTURE_REVIEW: AgentType.ARCHITECTURE_INTELLIGENCE,
    IntentType.ANALYZE_ARCHITECTURAL_HEALTH: AgentType.ARCHITECTURE_INTELLIGENCE,
    IntentType.FORECAST_TECHNICAL_DEBT: AgentType.ARCHITECTURE_INTELLIGENCE,
    IntentType.TRACK_ARCHITECTURE_EVOLUTION: AgentType.ARCHITECTURE_INTELLIGENCE,
    
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
    
    IntentType.FEEDBACK: AgentType.FEEDBACK,
    IntentType.REPORT_ISSUE: AgentType.FEEDBACK,
    
    IntentType.UPDATE_PROFILE: AgentType.PROFILE,
    
    # ADO operations mapping (NEW - ADO Integration)
    IntentType.ADO_WORKITEM: AgentType.ADO_ORCHESTRATOR,
    IntentType.ADO_STORY: AgentType.ADO_ORCHESTRATOR,
    IntentType.ADO_FEATURE: AgentType.ADO_ORCHESTRATOR,
    IntentType.ADO_SUMMARY: AgentType.ADO_ORCHESTRATOR,
    IntentType.CODE_REVIEW: AgentType.ADO_ORCHESTRATOR,
    
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


# =============================================================================
# Intent Classification Result (CORTEX 3.0 - Phase 1)
# =============================================================================

@dataclass
class IntentClassificationResult:
    """
    Rich classification result with intent, rule context, and confidence.
    
    Used by IntentRouter to attach governance rules based on classified intent.
    This enables intelligent rule enforcement without duplicating Tier 0 logic.
    
    Attributes:
        intent: Classified intent type
        confidence: Classification confidence (0.0-1.0)
        rule_context: Rules and behaviors relevant to this intent
        metadata: Additional classification metadata
    
    Example:
        result = IntentClassificationResult(
            intent=IntentType.CODE,
            confidence=0.9,
            rule_context={
                'rules_to_consider': ['TDD_ENFORCEMENT', 'DEFINITION_OF_DONE'],
                'intelligent_test_determination': True,
                'skip_summary_generation': True
            }
        )
    """
    intent: IntentType
    confidence: float
    rule_context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
