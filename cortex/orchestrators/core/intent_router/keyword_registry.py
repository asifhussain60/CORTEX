"""
IntentKeywordRegistry — Phase 103-b GAP-103-02.

All IntentType keyword lists and the `build_operation_type_mappings()` factory
extracted from IntentRouter into a dedicated registry class.

Responsibility: Single source of truth for keyword→IntentType mappings.
SRP: Zero routing logic, zero LENS logic — keywords only.

CORE-011: Type hints on all functions.
CORE-012: Docstrings on all public APIs.
CORE-028: snake_case naming.
"""
from typing import Dict, List

from cortex.models.canonical_enums import IntentType


class IntentKeywordRegistry:
    """Registry of per-intent keyword lists and operation-type mapping factory.

    All class attributes are intentionally read-only class variables (lists).
    Callers must not mutate them; copy first if per-instance overrides are needed.
    """

    # ------------------------------------------------------------------
    # Core SDLC intents
    # ------------------------------------------------------------------
    IMPLEMENT_KEYWORDS: List[str] = [
        "create", "add", "new", "implement", "develop", "build", "construct",
        "establish", "feature", "enhancement",
        "rebuild", "rework", "stand up", "wire up", "scaffold",
        "spin up", "generate", "produce", "assemble", "fabricate",
        "make", "write", "port", "clone", "replicate",
    ]

    FIX_KEYWORDS: List[str] = [
        "fix", "bug", "issue", "error", "problem", "crash", "fail", "broken",
        "resolve", "correct", "repair", "patch", "race condition",
        "address", "remediate", "mitigate", "squash", "root out",
        "restore", "recover", "unblock", "hotfix", "incident",
    ]

    REFACTOR_KEYWORDS: List[str] = [
        "refactor", "improve", "cleanup", "restructure", "simplify", "optimize",
        "clean", "modernize", "reorganize", "rewrite", "redesign", "performance",
        "tidy", "consolidate", "decouple", "extract", "rename",
        "inline", "move", "split", "merge", "eliminate duplication",
        "clean up code", "deduplicate", "untangle",
    ]

    DOCUMENT_KEYWORDS: List[str] = [
        "file", "write", "output", "report", "generate", "save", "persist",
        "export", "create file", "write file", "output file", "report file",
    ]

    # ------------------------------------------------------------------
    # Analysis / intelligence
    # ------------------------------------------------------------------
    ANALYZE_KEYWORDS: List[str] = [
        "analyze", "analyse", "investigate", "inspect", "examine", "scan",
        "deep dive", "deep analysis", "use lens", "cortex lens", "find patterns",
        "detect", "discover", "explore", "review", "audit", "check",
    ]

    ONBOARD_KEYWORDS: List[str] = [
        "onboard", "onboarding", "setup", "initialize", "bootstrap", "configure",
        "register", "integrate", "import project", "analyze repository", "scan repo",
        "discover", "inventory",
    ]

    PLAN_KEYWORDS: List[str] = [
        "plan", "phase", "enhance cortex", "add to cortex", "modify cortex",
        "implement orchestrator", "create orchestrator", "add mcp tool",
        "update wiring", "cortex change", "cortex enhancement", "add mode",
        "deprecate", "remove orchestrator", "delete feature",
    ]

    VACUUM_KEYWORDS: List[str] = [
        "vacuum", "cleanup", "clean up", "clean", "prune", "remove junk",
        "efficient cleanup", "cortex vacuum", "vacuum repo", "remove artifacts",
        "delete cache", "clear logs", "compact", "defragment", "garbage collection",
        "purge", "archive", "organize", "tidyup", "remove old", "remove legacy",
        "remove broken", "remove unused", "remove temp", "remove temporary",
        "housekeeping", "declutter", "sweep", "spring clean", "tidy workspace",
    ]

    AUDIT_KEYWORDS: List[str] = [
        "audit", "scan repo", "production readiness", "health check", "check repo",
        "/audit", "scan for issues", "repo health", "10-point",
    ]

    DESIGN_KEYWORDS: List[str] = [
        "design", "architect", "architecture", "structure", "pattern", "blueprint",
        "design the", "architect the", "system design", "design pattern",
    ]

    DIGEST_KEYWORDS: List[str] = [
        "digest", "summarize", "summary", "what happened", "recap", "recap of",
        "give me a summary", "synthesize", "tldr", "tl;dr",
    ]

    REPHRASE_KEYWORDS: List[str] = [
        "rephrase", "reword", "token optimize", "optimize this prompt",
        "rewrite request", "make this concise", "compact this",
    ]

    INVESTIGATE_KEYWORDS: List[str] = [
        "investigate", "why is", "what causes", "deep analysis",
        "investigate the", "find the cause",
    ]

    DEBUG_KEYWORDS: List[str] = [
        "debug", "debugger", "/debug", "/debug-inject", "/debug-cleanup",
        "diagnose", "breakpoint", "stack trace", "marker injection",
        "trace the", "debug why", "debug this", "injection strategy",
        "cortex debug", "debug mode", "step through",
    ]

    HEALTH_KEYWORDS: List[str] = [
        "health", "health check", "healthcheck", "/health", "/healthcheck",
        "orchestrator status", "orchestrator health", "component health",
        "uptime", "latency", "service health", "endpoint health",
        "all orchestrators", "22 orchestrators", "health endpoint",
    ]

    SYNC_KEYWORDS: List[str] = [
        "sync", "/sync", "sync to company", "sync to work", "cross-repo sync",
        "privacy-safe", "privacy safe", "push to work repo", "folder sync",
        "sanitize sync", "cortex sync", "sync target", "one-way sync",
    ]

    TRAIN_KEYWORDS: List[str] = [
        "train", "/train", "learn from", "learn from repo", "evolve templates",
        "gap-driven training", "template evolution", "pattern training",
        "cortex train", "train from codebase", "reinforcement training",
    ]

    TOTALRECALL_KEYWORDS: List[str] = [
        "totalrecall", "total recall", "/totalrecall", "holistic refactor",
        "production readiness refactor", "everything is broken", "7-phase protocol",
        "cortex total recall", "holistic production", "full recall",
    ]

    RCA_KEYWORDS: List[str] = [
        "rca", "/rca", "root cause analysis", "root cause", "five whys", "5 whys",
        "fishbone", "ishikawa", "fault tree", "causal chain", "causal-chain",
        "why did it fail", "recurrence detection", "prevention rule",
        "rca analysis", "cortex rca", "what caused",
    ]

    # ------------------------------------------------------------------
    # Legacy / lifecycle intents
    # ------------------------------------------------------------------
    TEST_KEYWORDS: List[str] = [
        "test", "/test", "run tests", "tdd", "unit test", "integration test",
        "pytest", "test suite", "test coverage", "write tests", "golden test",
        "preflight", "smoke test", "test-driven",
    ]

    DEPLOY_KEYWORDS: List[str] = [
        "deploy", "deployment", "release", "ship", "publish", "rollout",
        "kubernetes", "helm", "docker", "canary", "production deploy",
        "deploy to prod", "cd pipeline",
    ]

    GOVERNANCE_KEYWORDS: List[str] = [
        "governance", "enforce governance", "core rule", "core-rule", "compliance",
        "enforcement", "pre-commit", "governance violation", "cortex governance",
        "governance check", "rule enforcement",
    ]

    QUERY_KEYWORDS: List[str] = [
        "query", "ask", "what is", "how does", "explain", "describe",
        "tell me", "show me", "lookup", "find", "search",
    ]

    VALIDATE_KEYWORDS: List[str] = [
        "validate", "validation", "verify", "check", "lint", "assert",
        "confirm", "ensure", "certify", "schema validation",
    ]

    MIGRATE_KEYWORDS: List[str] = [
        "migrate", "migration", "port", "move", "convert", "transition",
        "upgrade migration", "schema migration", "data migration", "alembic",
    ]

    WORKFLOW_COMPOSE_KEYWORDS: List[str] = [
        "workflow composer", "workflow compose", "compose workflow",
        "compose template", "compose a workflow", "compose a template",
        "workflow template", "workflow templates", "create workflow",
        "build workflow", "generate workflow", "dynamic workflow",
        "convergence loop", "convergence gate", "condition loop",
        "template composition", "template composer", "on the fly workflow",
        "on-the-fly workflow", "dedicated template", "dedicated workflow",
        "workflow pipeline", "compose pipeline", "toolchain workflow",
        "ast workflow", "lens workflow", "roslyn workflow",
        "workflow engine", "workflow execution", "execute workflow",
        "run workflow template", "use workflow composer",
    ]

    GOLDEN_TEST_KEYWORDS: List[str] = [
        "golden test", "golden tests",
        "response template", "response templates", "acceptance criteria",
        "e2e scenario", "e2e scenarios", "trace assertion", "trace assertions",
        "test harness", "holistic integration", "trace verified", "ac marker",
        "ac_start", "ac_complete", "golden harness", "golden scenario",
        "create golden", "review golden", "enhance golden", "consolidate golden",
        "delete golden", "copilot chat response", "vscode response",
        "chat session feedback", "user response template", "inline feedback template",
    ]

    INTRODUCE_KEYWORDS: List[str] = [
        "introduce yourself", "introduce", "who are you", "what are you",
        "what is cortex", "what's cortex", "hello", "hi", "hey",
        "get started", "getting started", "help me", "how can you help",
        "what can you do", "capabilities", "how do i use",
        "tell me about yourself", "about cortex", "meet cortex",
        "new here", "first time", "onboard me", "walk me through",
        "show me around", "tour", "welcome",
    ]

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def build_operation_type_mappings(cls) -> Dict[IntentType, List[str]]:
        """Build and return the complete IntentType → keyword-list mapping.

        Returns:
            Dict mapping every non-UNKNOWN IntentType to its keyword list.
        """
        return {
            IntentType.IMPLEMENT: cls.IMPLEMENT_KEYWORDS,
            IntentType.FIX: cls.FIX_KEYWORDS,
            IntentType.REFACTOR: cls.REFACTOR_KEYWORDS,
            IntentType.DOCUMENT: cls.DOCUMENT_KEYWORDS,
            IntentType.ANALYZE: cls.ANALYZE_KEYWORDS,
            IntentType.ONBOARD: cls.ONBOARD_KEYWORDS,
            IntentType.PLAN: cls.PLAN_KEYWORDS,
            IntentType.AUDIT: cls.AUDIT_KEYWORDS,
            IntentType.DESIGN: cls.DESIGN_KEYWORDS,
            IntentType.DIGEST: cls.DIGEST_KEYWORDS,
            IntentType.REPHRASE: cls.REPHRASE_KEYWORDS,
            IntentType.INVESTIGATE: cls.INVESTIGATE_KEYWORDS,
            IntentType.GOLDEN_TEST: cls.GOLDEN_TEST_KEYWORDS,
            IntentType.WORKFLOW_COMPOSE: cls.WORKFLOW_COMPOSE_KEYWORDS,
            IntentType.DEBUG: cls.DEBUG_KEYWORDS,
            IntentType.HEALTH: cls.HEALTH_KEYWORDS,
            IntentType.SYNC: cls.SYNC_KEYWORDS,
            IntentType.TRAIN: cls.TRAIN_KEYWORDS,
            IntentType.TOTALRECALL: cls.TOTALRECALL_KEYWORDS,
            IntentType.RCA: cls.RCA_KEYWORDS,
            IntentType.VACUUM: cls.VACUUM_KEYWORDS,
            IntentType.TEST: cls.TEST_KEYWORDS,
            IntentType.DEPLOY: cls.DEPLOY_KEYWORDS,
            IntentType.GOVERNANCE: cls.GOVERNANCE_KEYWORDS,
            IntentType.QUERY: cls.QUERY_KEYWORDS,
            IntentType.VALIDATE: cls.VALIDATE_KEYWORDS,
            IntentType.MIGRATE: cls.MIGRATE_KEYWORDS,
            IntentType.INTRODUCE: cls.INTRODUCE_KEYWORDS,
        }
