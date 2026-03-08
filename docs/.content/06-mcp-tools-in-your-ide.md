# Tools in Your IDE — The MCP Gateway

---
title: MCP Gateway — 55+ CORTEX Capabilities Accessible Directly in Your Coding Assistant
type: explanation
audience: [Business Leaders, Product Owners, Software Developers, Curious Learners]
last_verified: 2026-03-08
order: 6
---

> **The central idea:** You don't need to leave your IDE to access any CORTEX capability. The Model Context Protocol makes 55+ registered CORTEX tools available directly in GitHub Copilot Chat, Cursor, or Claude Desktop — with no configuration, no server startup, and no context switching. Think of it like a smart home: you speak a command ("turn on the kitchen lights"), and the system routes it to the right device without you knowing the wiring behind the walls. CORTEX works the same way — you speak a request, and the right tool activates instantly. For programmatic access, Phase 99 added a secured HTTP transport with API key authentication.

---

## What the MCP Gateway Is

The Model Context Protocol is a standardised communication layer that connects AI coding assistants to external tools and services. CORTEX implements this protocol as a lightweight process that starts automatically when you open the workspace — the same way language analysis tools start automatically in modern IDEs, requiring no manual intervention.

Once active, every CORTEX capability is available directly in your coding assistant's chat interface. A developer in GitHub Copilot Chat can trigger a full codebase analysis, a governance compliance check, a debugging session, or a repository onboarding — all without leaving the editor or switching to a terminal.

---

## How It Starts — Zero Configuration

CORTEX uses a stdio-based transport, which means the MCP server runs as a process connected to the IDE over standard input and output streams. The IDE spawns the process, communicates through it, and manages its lifecycle — all automatically.

The key properties of this approach:

- **No manual startup** — the server starts when the workspace opens
- **No exposed network ports** — communication is in-process, not over a network socket
- **No Docker required** — the development experience requires only Python and the CORTEX repository
- **Instant availability** — tools are registered and ready within seconds of workspace open

To verify CORTEX is running, a developer simply types `cortex_verify` in Copilot Chat. If CORTEX responds, the gateway is active.

---

## The 55+ Registered Tools — Organised by Purpose

All tools are registered in a central tool registry and discovered automatically by the IDE. Calling `cortex_tools_catalog` from your coding assistant returns a live list of all registered tools with descriptions.

### Understanding and Routing

These tools handle intent classification and request lifecycle management — the entry points into CORTEX's orchestration layer.

| Tool | What It Does |
|---|---|
| **cortex_classify** | Classifies a request into one of 30 intent types and returns the routing decision |
| **cortex_orchestrator** | Routes a request directly to any of the wired orchestrators across all 9 domains |
| **cortex_request_lifecycle** | Executes the complete request lifecycle — classify, plan, execute, validate — with full audit trail |
| **cortex_challenge** | Generates two or more alternative approaches for a proposed change, with trade-off analysis |
| **cortex_ask** | Answers educational questions about CORTEX architecture with verification against live code |
| **cortex_tools_catalog** | Lists all registered tools with their categories and descriptions |

### Governance and Compliance

These tools expose the governance layer — rule checking, compliance validation, and dependency management.

| Tool | What It Does |
|---|---|
| **cortex_governance** | Executes governance actions — enforcement, blocking, remediation — with audit logging |
| **cortex_load** | Loads governance rules, audit checklists, execution modes, and response format standards |
| **cortex_validate** | Checks code or a proposed operation against active governance rules |
| **cortex_validate_request** | Runs a governance gate check on a request before execution begins |
| **cortex_registry** | Queries the CORTEX registry for governance rules, workflow templates, patterns, and plans — providing programmatic access to the full `cortex-registry/` index |

### Intelligence and Code Analysis

These tools expose the intelligence layer — code analysis, semantic operations, visual analysis, and knowledge synthesis.

| Tool | What It Does |
|---|---|
| **cortex_refactor** | Performs semantic refactoring across Python, C#, and TypeScript — extract methods, rename symbols, reorganise modules, resolve duplication — with full before-and-after analysis and governance validation |
| **cortex_vision** | Analyses screenshots using Vision API — identifies UI elements, maps visual structure to CSS selectors and HTML elements, surfaces layout discrepancies, and bridges the gap between what developers see in the browser and what exists in the code |
| **cortex_knowledge** | Synthesises knowledge from governance registries and applies it to a specific context — resolving conflicts between generic and team-specific guidance automatically |
| **cortex_learning** | Emits reinforcement signals, queries the learning history, and accesses root cause analysis with four structured methodologies — building institutional memory that prevents recurring failures |
| **cortex_brain_query** | Queries the CORTEX reinforcement signal engine — retrieve signal history, decay stale patterns, promote high-confidence signals — exposing the continuous learning state directly |
| **cortex_scan** | Hierarchical file scanning with organisation detection — scans any directory with configurable extensions and pluggable adapters for code, documentation, and media organisation |

### Contextually Intelligent Response Headers

Every response CORTEX emits includes a business or engineering principle drawn from the same literature that anchors its governance rules — *Good to Great*, *The Pragmatic Programmer*, *Site Reliability Engineering*, *The Phoenix Project*, and others.

The principle is not selected at random. The same intent classification that routes a tool call to the right orchestrator also selects the quote theme: a testing or TDD request surfaces a quality principle; a security request surfaces a resilience or trust principle; a refactoring request surfaces a lean or improvement principle. The result is a response header that looks like this:

> *"Don't leave broken windows unfixed. Neglect accelerates software rot faster than any single bad decision."*
> — Andrew Hunt & David Thomas, **The Pragmatic Programmer**

This appears on every CORTEX response — not as decoration, but as a visible expression of the governance philosophy being applied. For teams new to structured engineering practices, it creates a learning moment on every interaction. For experienced engineers, it provides a shared vocabulary that connects daily tool use to the principles that shaped the discipline.

### Intelligent Quote and Principle Selection (Phase 123-124)

CORTEX implements anti-repetition quote selection with a ring buffer (n=10) that ensures the same quote never appears twice in consecutive responses. Selection is weighted-random within theme-filtered candidates, with telemetry tracking selection latency (p95 ≤ 3ms) and repetition avoidance.

Beyond quotes, CORTEX maintains a curated library of 90 SDLC principles across 10 domains — including TDD, architecture, security, devops, code quality, and observability axioms. These principles are injected into analysis and design responses (QUERY, INVESTIGATE intents) but suppressed during operational execution (IMPLEMENT, FIX, REFACTOR) to maintain focus.

The quote library contains 120 entries across 10 themes (`quality`, `improvement`, `security`, `architecture`, `discipline`, `systems-thinking`, `strategy`, `flow`, `learning`, `universal`), all sourced from books already cited in CORTEX's governance rule definitions. The full library and theme→intent routing table are maintained as a single source of truth in the LEGO atom system at `cortex-registry/templates/response/atoms/atom-quote.yaml`.

### Planning and Audit

These tools connect CORTEX to project planning and repository assessment workflows.

| Tool | What It Does |
|---|---|
| **cortex_plan** | Creates structured remediation and project plans from audit findings |
| **cortex_onboard** | Runs a complete repository analysis — security assessment, architecture mapping, dashboard generation |
| **cortex_master_plan** | Creates, queries, updates, and synchronises phase planning documents in the master plan registry |

### Test Generation

| Tool | What It Does |
|---|---|
| **cortex_generate_tests** | Generates failing tests from a feature specification, ready for the implementation phase |

### Diagnostics and Health

| Tool | What It Does |
|---|---|
| **cortex_verify** | Verifies MCP gateway health, tool registry, environment, and architectural claims |
| **cortex_debug** | Captures debug logs, analyses errors, and generates a structured fix plan |
| **cortex_metrics** | Records and reports development metrics — build cycles, debug sessions, invocations |

### Dashboards and Reporting

| Tool | What It Does |
|---|---|
| **cortex_dashboard** | Generates and manages interactive dashboards — suite landing pages, per-repository dashboards, and full lifecycle management for visual reporting |

### Workflow and Automation

| Tool | What It Does |
|---|---|
| **cortex_workflow** | Lists, loads, and executes YAML workflow templates from the template registry |
| **cortex_enrich** | Adds metadata and context to structured data for downstream processing |
| **cortex_batch_transform** | Batch-processes collections of items with configurable triggers (size or timeout) and selectable transformation operations |
| **cortex_scaffold_files** | Writes new files from templates, checks for existing artefacts, and lists all scaffolded files — the gateway for creating new modules from canonical templates |
| **cortex_distill** | Distils a multi-turn conversation into an executable, context-dense prompt via a 5-stage pipeline: segment → reconstruct → reconcile → synthesise → compress. Eliminates noise while preserving goals, decisions, and constraints (Phase 129) |

### Maintenance

| Tool | What It Does |
|---|---|
| **cortex_vacuum** | Archives stale documentation, removes accumulated sprawl, and cleans root-level clutter |

### Version Control

| Tool | What It Does |
|---|---|
| **cortex_git** | Executes git operations — branching, committing, conflict resolution — through the governance-aware git layer |

---

## Extending with Custom Tools

The MCP tool architecture is designed for extension. Adding a new tool requires creating a single file in the tools directory, implementing the tool function using the standard base class, adding type annotations and documentation, and writing a test first. The MCP gateway discovers the new tool automatically on next startup — no registry edits, no configuration changes, no core code modifications.

This means teams can expose their own domain-specific operations as CORTEX tools, making them accessible through the same IDE interface as all built-in capabilities. A custom tool for querying an internal API, running a domain-specific validation, or interacting with a proprietary system can be added in the same way and integrated into workflow templates.

---

## Connecting to Multiple IDEs

CORTEX's MCP gateway is compatible with any tool that supports the Model Context Protocol with stdio transport.

**Visual Studio Code with GitHub Copilot Chat** is the primary integration, with automatic startup configured in the workspace settings file. No additional setup is required once the repository is cloned.

**Cursor** requires a single configuration file in the `.cursor` directory pointing to the CORTEX package. The same auto-start behaviour applies.

**Claude Desktop** requires a similar configuration file in the Claude Desktop configuration directory.

**Custom integrations** are possible for any application that can spawn a subprocess and communicate over standard input and output using JSON-RPC 2.0.

---

## Work Item Integration — Connecting Code to Delivery

CORTEX includes integration with work item management systems through a provider-agnostic protocol. The default integration targets Azure DevOps, but the same interface supports any work item system — Jira, GitHub Issues, or custom internal trackers. Sprint context pulled from work items enriches the intelligence layer's full analysis tier — meaning CORTEX can understand not just what the code does, but what the team is currently working on and why.

When work item integration is active, implementation plans include references to specific work items, evidence of completion is linked to the appropriate tracking items, and delivery metrics flow into reporting dashboards automatically.

For product owners, this integration closes the loop between the planning board and the codebase. A feature requested in the backlog can be tracked through intent classification, test generation, implementation, governance validation, and delivery — with every step linked back to the original work item. Sprint velocity becomes observable from the code itself, not just from status updates in the tracking tool.

For business leaders, work item integration means delivery metrics are grounded in engineering reality. A work item marked "done" has been tested, governance-validated, and audit-trailed — not just code-reviewed and merged.

---

*Tool catalog verified against live MCP registry (55+ tools) · Integration patterns verified against live configuration · Last verified: 2026-03-08*
