CORTEX Repository Truth Reference (CORTEX branch)

This reference document summarises the observed architecture, design patterns, and implemented components within the asifhussain60/CORTEX repository on the CORTEX branch. It is not a marketing document; it is meant to provide a factual baseline for comparison against any auto‑generated documentation. All statements here are supported by code or documentation citations from the repository.

1. High‑level Architecture

MCP‑first Service Architecture – CORTEX is organised into a network of orchestrators that communicate via the Model Context Protocol (MCP). Orchestrators are grouped into core, domain and support tiers, each exposed as an independent service. Benefits include decoupling, failure isolation and language agnosticism.

Brain system with four tiers – The CORTEX brain comprises immutable governance rules (Tier 0), acceptance‑criteria tracking (Tier 1), response templates and token optimisation (Tier 2), and a domain knowledge library (Tier 3). The tiers enforce incremental execution, test‑driven development (TDD), naming conventions and structured responses.

LENS – LENS provides automated analysis (Git history, AST, comments, security) and synthesises context into a “DoR” (Definition of Ready) used by orchestrators. LENS analyzers include GitHistoryAnalyzer, ASTAnalyzer, CommentExtractor and SecurityThreatAnalyzer.

Unified wiring specification – The single source of truth for orchestrator wiring is the YAML file at cortex/wiring/specifications/wiring.yaml. It defines all orchestrators, their modules, classes, tiers, priorities, dependencies, capabilities, health‑check functions, MCP adapters, metadata and phases. The WiringValidator class validates this specification and checks for circular dependencies, missing dependencies, required fields and tier ordering.

Phase registry – A registry in cortex-registry maps phases to orchestrators and tracks active/completed phases. Phase 65 (LENS Intelligence Remediation) plans to unify the knowledge pipeline, connect LENSWarmers to real analyzers, integrate ChallengeEngine, unify intelligence providers, accumulate intelligence across turns and unify context caching (eight stages with expected ROI and metrics).

Master orchestration – The MasterOrchestrator coordinates multiple stages of operation. It sets up state, routing, enforcement, TDD integration and domain orchestrators. The orchestrator initialises components such as KnowledgeRepository, TechIntelligenceOrchestrator, InteractionOrchestrator, TDDOrchestrator, and uses event buses, progress bars, audit loggers and an adaptive router.

2. Orchestrators Overview

The unified wiring specification lists 36 orchestrators plus four LENS analyzers. They are categorised as follows:

Core orchestrators (Tier 1)
Name	Purpose / capabilities	Dependencies	Notes
InteractionOrchestrator	Stage 1 comprehension; implements the LENS protocol, generates challenges and enforces patterns.	none	Exposes MCP adapter interaction_adapter and requires a ConversationProtocol with token limits.
ArchitectureGuard	Pre‑implementation validation gate; checks for architectural regression, phase alignment and brittleness.	none	Introduced at Phase 24.
IntentRouter	Classifies user intent, scores confidence and routes to domain orchestrators.	InteractionOrchestrator	
ComplexityClassifier	Classifies complexity (trivial/simple/moderate/complex/critical) and routes tasks.	IntentRouter	
LENSSynthesis	Synthesises LENS context and generates Definition of Ready; acts as an approval gate.	IntentRouter, ComplexityClassifier	
EnforcementOrchestrator	Enforces governance and Tier0 rules; performs parallel validation using the GovernanceRegistry and Audit Logger.	LENSSynthesis	
TDDOrchestrator	Handles TDD test generation and execution for Stage 3.	InteractionOrchestrator, IntentRouter	
IncrementalTaskDecomposer	Decomposes tasks into subtasks respecting token budgets; estimates PERT and performs evidence‑based sizing.	none	
WorkflowOrchestrator	Manages workflows and step orchestration.	TDDOrchestrator	
MasterOrchestrator	Stage 4 coordinator; manages stage routing and orchestrator selection.	InteractionOrchestrator, IntentRouter, LENSSynthesis, TDDOrchestrator	The top‑level orchestrator with priority 100.
ReviewOrchestrator	Holistic implementation verification and plan coherence check.	MasterOrchestrator	Performs final review before completion.
Domain orchestrators (Tier 2)

These orchestrators operate after the core stage to handle implementation planning and execution:

Name	Purpose	Dependencies	Notes
CodeLevelPlanner	Generates code‑level implementation plans (file structure, functions, interfaces) without generating code.	ComplexityClassifier	Phase 3.
CoherenceValidator	Validates cross‑layer (e.g., Python↔JavaScript) alignment and generates contract tests.	CodeLevelPlanner	Phase 4.
RefactoringOrchestrator	Supports code refactoring using patterns and smell detection.	MasterOrchestrator	
PlanningOrchestrator	Generates and manages project plans and milestones.	MasterOrchestrator	Phase 45 (stage 2).
DocumentationOrchestrator	Generates API docs, changelogs and design documents.	MasterOrchestrator	
PhaseExecutor	Executes phase tasks and manages checkpoints.	PlanningOrchestrator	
AutonomousExecutionEngine	Performs multi‑step execution autonomously.	MasterOrchestrator, TDDOrchestrator	
ConversationOrchestrator	Manages user conversations and context tracking.	InteractionOrchestrator	
Support orchestrators (Tier 3)

These provide infrastructure and auxiliary capabilities. Highlights include:

OrchestratorEventBus – Event‑driven communication backbone enabling decoupled orchestrator communication.

InteractionOrchestratorEnhancement – Adds event subscription and planning integration to the InteractionOrchestrator.

KnowledgeRepository – Central store for knowledge retrieval and relationship mapping.

GovernanceRegistry – Manages governance rules (CORE rules) and enforces them.

TechIntelligenceOrchestrator – Central knowledge hub monitoring tech ecosystems, scoring readiness and providing cross‑repo analysis.

ContextCrystallizationLayer (Phase 49) – Pre‑warms context by asynchronously loading LENS and rules into caches, enabling faster Stage 2 operations.

HolisticValidationOrchestrator – Performs cross‑system validation, regression risk scoring and architecture drift detection.

ChallengeEngine, RecommendationEngine and RecommendationGate – Provide security gates, best‑practice recommendations and regression prevention checks.

InstrumentationOrchestrator, DebuggingOrchestrator, DuplicationDetector, DigestEnhancementOrchestrator and EducationalOrchestrator – Handle metrics, debugging assistance, duplication detection, digest mode enhancements and educational interactions, respectively.

3. LENS Analyzers

LENS analyzers provide raw data used by orchestration and are defined in the unified wiring file:

GitHistoryAnalyzer – Extracts commit history, blame and author patterns.

ASTAnalyzer – Extracts code structure (functions, classes, imports).

CommentExtractor – Extracts TODOs, FIXMEs and intent hints from comments.

SecurityThreatAnalyzer – Detects common weaknesses (CWE‑94, CWE‑95, CWE‑78, CWE‑89, CWE‑327, CWE‑22) in code.

4. Governance Rules and Validation

CORE Rules (Tier 0) – The brain’s immutable rules enforce incremental execution, TDD, naming conventions, anti‑hallucination, and more. These rules apply across all orchestrators and phases.

Validation checks – The wiring specification defines validation rules such as no_circular_dependencies, all_dependencies_exist, tier_ordering and health_check_defined. These ensure the orchestrator network is a directed acyclic graph, all dependencies are valid, tier hierarchies are respected, and health checks exist.

Fallback routes – The specification defines fallback behaviour when an orchestrator fails its health check (e.g., RefactoringOrchestrator falls back to TDDOrchestrator; PlanningOrchestrator falls back to MasterOrchestrator).

5. Master Orchestrator Workflow (inferred from code)

The MasterOrchestrator is implemented in cortex/orchestrators/core/master_orchestrator.py (≈4000 lines). Its docstring identifies it as the top‑level coordinator; it initialises numerous components and performs stage‑by‑stage orchestration. Key behaviours include:

Stage 1 (Comprehension) – Delegates to InteractionOrchestrator for LENS protocol and challenge generation, then logs and audits state.

Stage 2 (Intent verification and DoR) – Calls IntentRouter to classify intent; ComplexityClassifier to estimate complexity; LENSSynthesis to synthesise knowledge and generate a Definition of Ready; EnforcementOrchestrator to enforce governance; optionally triggers ArchitectureGuard and ChallengeEngine for early gating.

Stage 3 (TDD Execution) – Invokes TDDOrchestrator to generate tests and integrate them into plan execution.

Stage 4 (Domain orchestration) – Routes to domain orchestrators (e.g., CodeLevelPlanner, RefactoringOrchestrator, AutonomousExecutionEngine) depending on the action required. It coordinates the plan executor, knowledge repository and event bus to ensure tasks are performed in the right order.

Final review – Calls ReviewOrchestrator or HolisticValidationOrchestrator before final output to verify the implementation and ensure consistency.

The Master orchestrator uses adaptive routing, dynamic context synthesis, audit logging, caching, progress bars and multiple controllers to manage complexity. It integrates with the Brain (for Tier 0–3 rules), LENS (for context and analyzers), KnowledgeRepository, GovernanceRegistry, TechIntelligenceOrchestrator and other components.

6. Intelligence & Tech Analysis Layer

TechIntelligenceOrchestrator – A support orchestrator that acts as the central knowledge hub for monitoring external tech ecosystems, scoring readiness (e.g., TDD support, security, cross‑repo usage) and synthesising best practices. It exposes MCP tools like get_tech_readiness, detect_tech_stack and synthesize_best_practices. Its functions include scanning dependencies, computing readiness scores based on best practice coverage and security tooling, synthesising recommendations, and triggering learning modules.

Persona and Detail Tools – wiring_manager.py registers persona tools (cortex_set_persona, cortex_get_persona, cortex_set_depth, etc.) and defines agents that manage persona selection, detail level and user sessions. The WiringManager provides simple cycle detection and validation for persona wiring.

LENS Context Provider & Context Crystallization – The LENSContextProvider caches context per file and company, integrates company knowledge, and uses LENS analyzers to preload context. The ContextCrystallizationLayer pre‑warms context asynchronously to accelerate Stage 2 operations.

7. Observations and Potential Gaps

Incomplete integrations – Several orchestrators (e.g., TechIntelligenceOrchestrator, ChallengeEngine, ContextCrystallizationLayer) are defined with placeholders for certain methods or rely on yet‑to‑be‑implemented analyzers. The brain tier documentation emphasises planned features like best‑practice knowledge accumulation, token optimisation and TDD enforcement; however, not all orchestrators appear to consume this intelligence uniformly.

Phase 65 tasks – The registry lists Phase 65 as planned for LENS Intelligence Remediation, aiming to unify intelligence providers, accumulate turn‑over‑turn intelligence, integrate LENSWarmers, unify context and cache, and perform end‑to‑end integration testing. These tasks are essential to fully realise the vision of an intelligent, context‑aware development companion.

Dependency on file structure – The wiring specification assumes a repository layout (cortex.orchestrators..., cortex.brain..., etc.) and may be brittle if modules are moved or renamed. The WiringValidator uses local file paths to load wiring.yaml; in a production deployment the environment must replicate this structure..

Health checks and fallback – The specification defines health checks for each orchestrator, but actual implementations may not yet provide robust health‑check logic (many health checks simply call placeholder methods). Fallback routes exist but rely on conditions like health_check_fails; these must be tested rigorously to avoid silent failures.

Security coverage – The SecurityThreatAnalyzer covers six common CWE vulnerabilities, but other threats (like CSRF, SSRF or insecure deserialization) are not mentioned. Phase 65’s integration of ChallengeEngine and security gating aims to address this.

Intelligence distribution – While the wiring lists intelligence tags for each orchestrator (e.g., lens, knowledge, synthesis), the actual code for some orchestrators does not yet implement intelligence ingestion or context accumulation. Further work is needed to ensure that the brain and LENS outputs are consumed consistently across all orchestrators.

8. Recommended Diagrams and Visualisations

To visualise the architecture and assist business stakeholders, architects, engineers and product owners, the following diagram types are most valuable:

Context diagram (C4 level 1) – Shows CORTEX interacting with external users, GitHub repositories, knowledge sources, brain tiers and LENS analyzers.

Container/Component diagram (C4 levels 2–3) – Illustrates core, domain and support orchestrators, their dependencies, tiers and priorities, plus brain components (knowledge repository, governance registry, LENS analyzers, persona manager, event bus).

Sequence diagrams – Depict the multi‑stage workflow from request → interaction → intent classification → complexity → synthesis → enforcement → TDD → domain planning → execution → review.

Dependency graph – Visualises orchestrator dependencies; highlight core vs domain vs support tiers; show fallback routes.

Data flow diagrams – Show how intelligence, knowledge and context flow between LENS analyzers, knowledge repository, brain tiers and orchestrators.

Phase roadmap – Visual timeline of phases (past, active and planned) including Phase 65 tasks and their outcomes.

These diagrams can be rendered using D3.js or other libraries and aligned with the CORTEX LENS dashboard specification.

This truth reference serves as a factual baseline for evaluating the upcoming CORTEX‑generated architecture document. It focuses on implemented components, wiring configuration and observed behaviour in the code and documentation. Any discrepancies or aspirational features in future documents can be compared against this reference to identify gaps, misalignments and brittleness.