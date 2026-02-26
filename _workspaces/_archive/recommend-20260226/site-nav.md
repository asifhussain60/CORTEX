**Home Page (`/index.html`)**
*   **Hero Section:** Introduction to CORTEX as a production-grade AI platform that "thinks alongside your team".
*   **Role Selection Navigation:** Four distinct glassmorphism-styled cards routing to the specialized paths below.

### Path 1: Business Leaders (`/business-leaders/`)
*   **`/executive-overview.html`**
    *   **Content:** High-level summary of the "Brain" architecture, explaining the Perception → Reasoning → Action intelligence pipeline. 
    *   **Focus:** How CORTEX learns from repositories to improve strategy recommendations and execution.
*   **`/automated-governance.html`**
    *   **Content:** Details on the "immune system" of CORTEX, highlighting the automated enforcement of 35 CORE rules across pre-commit, CI, and runtime stages.
    *   **Visualization:** Embeds the interactive D3.js **`governance-pyramid.html`** (Sunburst diagram) to visualize the rule hierarchy.
*   **`/roi-and-infrastructure.html`**
    *   **Content:** Explains the cost-optimization of independent service scaling, and the tamper-proof auditability provided by the CortexAuditDB (SQLite WAL mode).

### Path 2: Product Owners (`/product-owners/`)
*   **`/capabilities-catalog.html`**
    *   **Content:** An overview of the 26 active MCP tools, mapping capabilities like repository onboarding (`cortex_onboard`) and compliance validation (`cortex_validate`) to user needs.
*   **`/sprint-integration.html`**
    *   **Content:** Explains the `ADOWorkItemProvider` and how `cortex_fetch_work_items` directly pulls Jira or Azure DevOps user stories into the developer's context.
    *   **Visualization:** Embeds the interactive D3.js **`request-lifecycle-sankey.html`** to show how user requests and sprint items flow through the orchestrator pipeline.
*   **`/quality-tracking.html`**
    *   **Content:** Focuses on the TestQualityGate, which scores every test from 0–9, and the `SweepCatalogueOrchestrator` (CORE-064) which ensures no refactoring sweep is abandoned mid-sprint.

### Path 3: Software Engineers (`/software-engineers/`)
*   **`/quick-start.html`**
    *   **Content:** The 5-minute setup guide for VS Code, Cursor, or Claude Desktop, utilizing the auto-starting Pylance-style stdio MCP server.
*   **`/lens-and-orchestration.html`**
    *   **Content:** Deep dive into the 9 parallel LENS analyzers (AST, Git History, Security, Domain, etc.) and the routing matrix for the 27 wired orchestrators.
    *   **Visualization:** Embeds the interactive D3.js **`orchestrator-tier-map.html`** to display the layered architecture of the Core, Domain, and Support tiers.
*   **`/tdd-and-extensibility.html`**
    *   **Content:** Technical documentation on the architecturally mandated CORE-008 TDD workflow (RED → GREEN → REFACTOR) and guides for adding custom hot-reloaded MCP tools.
    *   **Visualization:** Embeds the interactive D3.js **`tdd-knowledge-cycle.html`** to illustrate the circular flow of the TDD requirement.

### Path 4: Curious Learners (`/curious-learners/`)
*   **`/the-brain-analogy.html`**
    *   **Content:** A conceptual breakdown mapping system components to biology, such as LENS as the sensory cortex, the IntentRouter as the thalamus, and Governance as the immune system.
*   **`/how-cortex-works.html`**
    *   **Content:** A simplified walkthrough of the 6-stage request lifecycle, from Sensory Input (MCP Gateway) to Motor Execution (Orchestrator).
*   **`/intelligence-tiers.html`**
    *   **Content:** A plain-language guide on how CORTEX detects patterns (Perception), selects strategies (Reasoning), and plans step-by-step executions with built-in rollbacks (Action).

### Global Shared Views (`/global/`)
*   **`/faq.html`**
    *   **Content:** Expandable glassmorphism accordions covering common questions, such as the impossibility of bypassing TDD (since it is architecturally enforced) or what happens when a test scores below a 7. 
*   **`/glossary.html`**
    *   **Content:** An alphabetical reference defining core terminology like LENS, MCP Gateway, Orchestrator, and Golden Tests.
*   **`/site-map.html`**
    *   **Content:** An interactive D3.js node-graph map of this exact documentation structure, allowing a Product Owner, for example, to easily cross-navigate into the Software Engineer's orchestration spec.