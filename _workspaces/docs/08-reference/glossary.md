# Glossary

**Last Updated:** 2026-01-20  
**Version:** 1.0.0  
**Status:** Production Ready

Key terms and concepts used throughout CORTEX documentation. Terms are organized alphabetically and include cross-references to related documentation.

---

## A

**AC (Acceptance Criteria)**  
Specific, measurable requirements that define when a feature or fix is complete. Each phase in the CORTEX roadmap has multiple ACs with unique IDs (e.g., `AC-AR-010-01`).  
*See: `_workspaces/roadmap/cortex-master.yaml` in project root*

**Approval Matrix**  
A decision table that determines when user confirmation is required based on operation complexity. Part of the Complexity Gate (Stage 2.5).  
*See: [Orchestration Engine](../02-architecture/3-orchestration-engine.md#complexity-gate)*

**Audit Entry**  
A single record in the audit trail containing operation details, governance results, timestamp, and cryptographic hash linking to the previous entry.

**Audit Trail**  
Complete, tamper-evident record of all CORTEX actions. Uses a hash chain to ensure integrity. Contains 5000+ entries in production.  
*See: [Design Principles - Auditability](../02-architecture/2-design-principles.md#10-safety-through-auditability)*

---

## B

**BKIO (Business Knowledge Ingestion Organization)**  
The system and process for importing, structuring, and organizing domain knowledge into the Domain Brain. Supports 4 adapter types.  
*See: [Domain Brain](../02-architecture/4-domain-brain.md)*

**Bulkhead Pattern**  
Resilience pattern that isolates resources into separate pools, preventing one failing component from consuming all system capacity.  
*See: [Resilience Patterns](../02-architecture/5-resilience-patterns.md#bulkhead-pattern)*

---

## C

**Circuit Breaker**  
Resilience pattern with three states (CLOSED, OPEN, HALF_OPEN) that fails fast when a service is unhealthy, preventing cascading failures.  
*See: [Resilience Patterns](../02-architecture/5-resilience-patterns.md#circuit-breaker-pattern)*

**Complexity Gate**  
Stage 2.5 in the orchestration pipeline that analyzes operation complexity and determines if user confirmation is needed.  
*See: [Orchestration Engine](../02-architecture/3-orchestration-engine.md#stage-25-complexity-gate)*

**Complexity Score**  
Numeric value (0.0-1.0) calculated by the Complexity Gate based on factors like intent length, sensitive keywords, and production impact.

**Continuation Decision**  
The result of each conversation turn, specifying whether to continue (`should_continue`) and why (`reason`). Core to the ConversationProtocol.  
*See: [ConversationProtocol](#conversationprotocol)*

**ConversationProtocol**  
CORTEX's pattern for multi-turn interactions. Each turn produces a `ContinuationDecision` with explicit termination reasons (COMPLETE, NEEDS_INPUT, ERROR, etc.).  
*See: [Orchestration Engine](../02-architecture/3-orchestration-engine.md#conversationprotocol)*

**CORE Rules**  
The 29 fundamental governance rules in Tier 0 (SKULL layer) that are immutable and always enforced. Examples: CORE-001 (Safe Operations), CORE-002 (Audit Required).

**cortex-config.yaml**  
Primary configuration file for CORTEX. Contains settings for governance, orchestrators, resilience, and APIs.  
*See: [Installation](../01-getting-started/0-installation.md#configuration)*

---

## D

**Domain Brain**  
CORTEX component that manages domain knowledge ingestion, storage, retrieval, and conflict resolution. Supports semantic search and LENS integration.  
*See: [Domain Brain](../02-architecture/4-domain-brain.md)*

**Domain Knowledge**  
Business-specific facts, rules, and relationships stored in Tier 3. Examples: coding standards, API conventions, business rules.

---

## E

**Execution Context**  
Complete state available during orchestrator execution, including user intent, session data, governance results, and Domain Brain query results.

**Exponential Backoff**  
Retry strategy where wait times increase exponentially between attempts (e.g., 100ms → 200ms → 400ms), often with jitter to prevent thundering herd.  
*See: [Resilience Patterns](../02-architecture/5-resilience-patterns.md#retry-with-backoff)*

---

## G

**Governance Database**  
SQLite database (`governance.db`) storing rules, audit entries, and governance state. Located at `cortex_brain/state/governance.db`.

**Governance Engine**  
The component that evaluates requests against rules across all tiers, produces pass/fail decisions, and records results in the audit trail.

**Governance Tier**  
Hierarchical level of rules. Higher tiers cannot override lower tiers:
- **Tier 0**: Immutable SKULL rules (29 CORE rules)
- **Tier 1**: Architectural constraints (admin-modifiable)
- **Tier 2**: Templates (80+ scaffolding patterns)
- **Tier 3**: Domain knowledge (user-extensible)

*See: [System Overview](../02-architecture/1-system-overview.md#governance-tiers)*

---

## H

**Hallucination Prevention**  
CORTEX mechanisms that prevent AI from generating false or unsupported content. Includes behavioral boundaries, intent canonicalization, and coherence checking (Phase 11).

**Hash Chain**  
Data structure where each audit entry contains a cryptographic hash of the previous entry, making tampering detectable. CORTEX maintains 5000+ entries with unbroken chain.

**Health Check**  
Endpoint or process that verifies system health:
- **Liveness**: Is the process running?
- **Readiness**: Can it accept requests?
- **Deep Health**: Are all dependencies healthy?

*See: [Resilience Patterns](../02-architecture/5-resilience-patterns.md#health-checking)*

---

## I

**Intent**  
The user's goal or request expressed in natural language. Processed through LENS Protocol before execution.

**Intent Canonicalization**  
Process of normalizing user intent into a standard form for consistent processing and governance evaluation.

---

## J

**Jitter**  
Random variation added to retry wait times to prevent multiple clients from retrying simultaneously (thundering herd problem).

**JSON-RPC 2.0**  
Protocol used by the MCP server. Requests and responses follow the JSON-RPC 2.0 specification with `jsonrpc`, `method`, `params`, `id`, and `result`/`error` fields.  
*See: [MCP Protocol](../03-api-reference/mcp-protocol/0-specification.md)*

---

## K

**Knowledge Adapter**  
Component that ingests knowledge from specific sources into the Domain Brain. Four types: File, API, Database, Custom.  
*See: [Domain Brain](../02-architecture/4-domain-brain.md#integration-adapters)*

**Knowledge Conflict**  
When two or more knowledge entries provide contradictory information. Resolved through the Domain Brain's conflict resolution hierarchy.

**Knowledge Quality Score**  
Numeric score (0.0-1.0) indicating the reliability of a knowledge entry based on source, freshness, and validation status.

---

## L

**LENS Protocol**  
Four-phase intent comprehension method:
1. **L**anguage: Canonicalize intent, extract keywords
2. **E**xamination: Identify patterns, classify operation
3. **N**avigation: Map to capabilities, select orchestrator
4. **S**ynthesis: Generate execution plan, merge context

*See: [Orchestration Engine](../02-architecture/3-orchestration-engine.md#lens-protocol)*

**Lifecycle Hooks**  
Extension points in orchestrator execution: `before_execute`, `after_execute`, `on_error`, `on_governance_block`.

---

## M

**Master Orchestrator**  
Central orchestrator that coordinates all CORTEX operations. Implements full ConversationProtocol with LENS integration.

**MCP (Model Context Protocol)**  
Protocol for AI-native integrations. CORTEX implements MCP v2024-11-05 with JSON-RPC 2.0 over stdio transport.  
*See: [MCP Protocol](../03-api-reference/mcp-protocol/0-specification.md)*

**MCP Server**  
CORTEX component that handles MCP protocol requests. Exposes tools, resources, and prompts to AI clients like VS Code Copilot.

**Mode (Response)**  
One of 6 response composition modes: `concise`, `standard`, `detailed`, `debug`, `streaming`, `template`.  
*See: Response Composition in [Orchestration Engine](../02-architecture/3-orchestration-engine.md#response-composition)*

---

## O

**Orchestrator**  
Executable business process definition in CORTEX. Extends `OrchestratorBase` and implements `process()` method. Registered in the orchestrator registry.  
*See: [First Orchestrator Tutorial](../01-getting-started/2-first-orchestrator.md)*

**Orchestrator Registry**  
Central registry mapping orchestrator names to their implementations. Used for dynamic orchestrator lookup and instantiation.

---

## P

**Partial Mode**  
Degraded operation mode when non-critical components fail. CORTEX continues with cached data and warnings rather than failing completely.  
*See: [Resilience Patterns](../02-architecture/5-resilience-patterns.md#partial-functionality-mode)*

**Phase**  
Major development milestone in CORTEX roadmap. 25+ phases completed, each with multiple ACs and test suites.  
*See: `_workspaces/roadmap/cortex-master.yaml` in project root*

**Profile (Response)**  
One of 5 response composition profiles: `developer`, `architect`, `manager`, `operator`, `end_user`.

---

## R

**Response Composition**  
Stage 4 of orchestration that formats results using 6 modes, 5 tones, 5 profiles, and template system (Phase 24, 172 tests).  
*See: [Orchestration Engine](../02-architecture/3-orchestration-engine.md#stage-4-response-composition)*

**Resilience**  
System's ability to handle failures gracefully. CORTEX implements circuit breakers, retries, partial mode, and rollback.  
*See: [Resilience Patterns](../02-architecture/5-resilience-patterns.md)*

**Rollback**  
Automatic reversal of partially completed transactions when a step fails. All rollbacks are recorded in the audit trail.

**Rule Evaluation**  
Process of checking a request against governance rules. Produces pass/fail result with optional violation details.

---

## S

**Semantic Search**  
Finding knowledge by meaning rather than exact keywords. Domain Brain uses vector embeddings for semantic similarity.

**Session**  
A conversation context identified by `session_id`. Spans multiple turns and maintains state across requests.

**SKULL Rules**  
Tier 0 governance rules that form the "skeleton" of system safety. 29 CORE rules, immutable, always enforced.

**stdio Transport**  
MCP communication method using standard input/output streams. Default transport for CLI and VS Code integration.

---

## T

**Template System**  
80+ Tier 2 templates for scaffolding orchestrators, tests, configurations, and documentation. Part of Phase 19/20 (157 tests).

**Termination Reason**  
Why a conversation turn ended. One of: `COMPLETE`, `NEEDS_INPUT`, `NEEDS_APPROVAL`, `ERROR`, `GOVERNANCE_BLOCK`, `MAX_TURNS`.

**Tier**  
See [Governance Tier](#governance-tier).

**Tone (Response)**  
One of 5 response tones: `professional`, `casual`, `technical`, `supportive`, `concise`.

**Tool (MCP)**  
A capability exposed via MCP that AI clients can invoke. Examples: `cortex_analyze`, `cortex_orchestrate`, `cortex_knowledge_query`.  
*See: [MCP Protocol](../03-api-reference/mcp-protocol/0-specification.md#available-tools)*

**Transaction**  
Atomic unit of work with rollback capability. If any step fails, all previous steps are reversed.

**Turn**  
A single request-response cycle in a conversation. Each turn produces a `ContinuationDecision`.

---

## U

**Universal Dashboard**  
Multi-repository visualization component showing real-time metrics, audit trail, and system health (Phase 15, 48 tests).

---

## V

**Validation**  
Checking that requests meet governance rules and data requirements before execution.

**Violation**  
A failed governance rule check. Contains rule ID, message, and severity.

---

## W

**WAL Mode**  
Write-Ahead Logging mode for SQLite database, enabling better concurrency for the governance database.

**Worktree**  
Git worktree for isolated development. Used when managing multiple CORTEX branches.

---

## Acronyms Quick Reference

| Acronym | Expansion |
|---------|-----------|
| AC | Acceptance Criteria |
| BKIO | Business Knowledge Ingestion Organization |
| CLI | Command-Line Interface |
| CORE | Core Operational Rules and Enforcement |
| LENS | Language, Examination, Navigation, Synthesis |
| MCP | Model Context Protocol |
| REST | Representational State Transfer |
| SKULL | System Knowledge Universal Logic Layer |
| WAL | Write-Ahead Logging |

---

**Not finding a term?** Check the [FAQ](faq.md) or search the documentation.
