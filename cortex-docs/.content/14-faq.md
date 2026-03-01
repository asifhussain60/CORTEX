# Frequently Asked Questions

---
title: Frequently Asked Questions
type: reference
audience: [Business Leaders, Product Owners, Software Developers, Curious Learners]
last_verified: 2026-03-01
order: 14
---

---

## General

**What is CORTEX?**
CORTEX is an AI Engineering Framework that works directly inside your IDE. It combines a deep understanding of your codebase with automated governance, test-driven development enforcement, and a full software delivery lifecycle — all accessible through natural language in GitHub Copilot Chat. It does not replace developers; it amplifies what they can accomplish per day.

**What problem does CORTEX solve?**
The core problem is quality drift — the gradual degradation of engineering standards as teams grow, codebases age, and delivery pressure increases. CORTEX makes quality automatic rather than aspirational. It enforces the same standards consistently on every line of code, for every developer, on every pull request — without manual oversight.

**What makes CORTEX different from other AI coding tools?**
Most AI coding tools generate code. CORTEX governs the full engineering process — from idea through testing, review, compliance, learning, and deployment. It understands your specific codebase, enforces your specific standards, and learns from every decision made in your environment. The governance is structural, not advisory.

**Does CORTEX replace GitHub Copilot?**
No. CORTEX works alongside GitHub Copilot. Copilot provides the AI language model capability; CORTEX orchestrates how that capability is applied — routing requests to specialist systems, enforcing governance standards, applying code intelligence, and coordinating the full delivery workflow.

**What programming languages does CORTEX support?**
CORTEX's code intelligence engine analyses Python, TypeScript, JavaScript, C#, SQL, and HTML. Governance enforcement, workflow orchestration, and the full delivery lifecycle apply to any language. MCP tools can be extended to support additional languages.

---

## Getting Started

**How long does setup take?**
For a developer with Python 3.9+ and VS Code installed: five minutes. Clone the repository, create a virtual environment, install dependencies, and open in VS Code. The AI connection configures automatically.

**Do I need cloud infrastructure or a database server?**
No. In development, CORTEX runs entirely locally. Storage uses lightweight local databases. Communication uses local streams. No Docker, no cloud accounts, no database servers, no network configuration.

**What do I need to use the AI features?**
An active GitHub Copilot subscription with Chat mode enabled. All other AI orchestration is handled by CORTEX.

**How do I know the AI connection is working?**
Open Copilot Chat in Agent mode. Click the Tools button. CORTEX tools should appear in the list. If they don't, run `python3 scripts/setup-mcp.py` in the terminal and reload VS Code.

---

## Governance and Compliance

**How many governance rules does CORTEX enforce?**
32 active governance rules organised by severity. Rules cover everything from code structure (type hints, naming conventions, file organisation) to process compliance (test-first development, complete fixes, convergence before completion) and security (secret management, dependency safety).

**Can we customise governance rules for our organisation?**
Yes. The governance rules are structured YAML files in the `cortex-registry/core/` directory. Rules can be modified, deactivated, or supplemented with organisation-specific rules. All changes are version-controlled, audited, and documented.

**What happens when a governance violation is found?**
Minor violations (warnings) surface as recommendations. Significant violations (major findings) block the relevant operation until addressed. Critical violations (blocking) prevent code from proceeding to the next stage. The audit trail records every violation found, every fix applied, and every governance gate outcome.

**Does governance apply to all developers equally?**
Yes. Governance is enforced structurally — not through peer review or manual oversight. The same rules apply regardless of seniority, team, or delivery pressure. There are no override mechanisms for governance gates.

**How is governance audited?**
Every governance gate outcome is written to the audit database with a cryptographic chain. Each record includes the rule applied, the outcome, the timestamp, and the operator (human or automated). The chain ensures that historical records cannot be modified without detection.

---

## Orchestration and AI Requests

**What kinds of requests can CORTEX handle?**
28 distinct intent types including: implementing features, fixing bugs, refactoring, auditing compliance, debugging failures, running security checks, generating documentation, managing the delivery lifecycle, learning from root cause analyses, and more. Requests are expressed in natural language.

**How does CORTEX know which specialist to use for a request?**
An Intent Router classifies incoming requests using semantic analysis. The classified intent maps to the appropriate specialist orchestrator. Each orchestrator has a specific domain of expertise — code intelligence, governance, testing, debugging, security, or lifecycle management. Routing is transparent and logged.

**Can a single request involve multiple specialists?**
Yes. Complex requests — like a full production audit with automatic fix — coordinate multiple specialists in sequence. Each specialist handles its domain, passes context to the next, and the overall result reflects all contributions. The breadcrumb trail in each response shows the full routing chain.

**What if CORTEX doesn't understand a request?**
CORTEX asks for clarification rather than guessing. If the request is ambiguous between two intent types, CORTEX surfaces the alternatives and asks which was intended. If the request is outside CORTEX's capability scope, CORTEX says so clearly.

**How long does a typical request take?**
Simple queries return in seconds. A code review returns in 5–15 seconds depending on file size. A full codebase audit with fixes can take 2–10 minutes depending on codebase size and issue count. Test suite execution time depends on suite size — the parallel runner uses all available CPU cores automatically.

---

## Testing

**Does CORTEX require tests to be written before code?**
Yes. This is a core governance rule. The test-driven approach — write a failing test, implement to make it pass, refactor — is enforced structurally. A workflow that produces code without a corresponding test will not pass the governance gate.

**How many tests does CORTEX have?**
The test suite currently has approximately 17,700 tests. Parallel execution across all CPU cores completes the full suite faster than a sequential run of a fraction of that number. A smoke subset (the most critical tests) runs in under 60 seconds.

**What are Golden Tests?**
Golden Tests are the immutable quality contracts for CORTEX's core invariants. Every core claim about CORTEX's behaviour is backed by a Golden Test. These tests cannot be skipped, cannot be modified without explicit governance approval, and must pass with no exceptions at every commit. They are the production-quality guarantee.

**Can we run only the tests relevant to our changes?**
Yes. The `make test-changed` command uses change detection to identify only the tests that cover the files you have modified. This is the recommended command for the TDD inner loop — it runs in seconds rather than minutes.

**How do we know our tests are high quality?**
CORTEX scores test quality on five dimensions: isolation (no shared state between tests), determinism (same result every run), clarity (test name describes the failure clearly), coverage (every code path exercised), and completeness (both success and failure paths tested). Low-quality tests are flagged with specific improvement recommendations.

---

## Code Intelligence

**How does CORTEX understand our specific codebase?**
The code intelligence engine — called LENS — analyses codebases across nine dimensions using six-language support. It extracts your team's conventions, naming patterns, architectural decisions, and domain language. This company-specific knowledge supplements the universal knowledge base to produce recommendations that feel native to your codebase.

**Does CORTEX analyse the entire codebase every time?**
No. Analysis uses a three-tier loading model. Only the files relevant to the current task are loaded into active context. Analysis results are cached within a session — the same file is not analysed twice. For large codebases, this makes comprehensive quality assessment practical in normal session budgets.

**How accurate is pattern detection?**
Pattern detection produces a confidence score for each finding. High-confidence detections (above 80%) drive direct recommendations. Medium-confidence detections are flagged for developer review. Low-confidence detections are logged but not surfaced. The confidence scoring prevents false positives from producing misleading recommendations.

---

## Learning and Memory

**Does CORTEX learn from mistakes?**
Yes. Every significant error — a test failure, a governance violation, a deployment issue — is analysed using one of four root cause analysis methodologies (selected automatically based on failure type). The analysis produces prevention rules that are applied to future operations. Recurring issues are detected and escalated.

**Does learning persist across sessions?**
Yes. All learning is persisted to the audit database. Prevention rules, historical analyses, and knowledge patterns survive session boundaries. A lesson learned on Monday is applied on Friday without any manual knowledge transfer.

**Can we see what CORTEX has learned?**
Yes. The learning history is queryable through the `What has CORTEX learned?` request in Copilot Chat. Specific root cause analyses can be retrieved by topic or time range. Prevention rules can be reviewed and, if appropriate, revoked.

**How does CORTEX share learning across a team?**
Learning is stored in the shared repository's runtime directory. Team members working from the same repository share the same learning history. Individual sessions can also emit learning signals that persist for the full team. Shared learning means the second developer to encounter a problem benefits from the analysis the first developer triggered.

---

## Business and ROI

**How does CORTEX affect delivery speed?**
Teams typically see faster velocity within the first sprint of adoption. The primary driver is elimination of rework: bugs caught at the time they are introduced rather than in testing or production are significantly cheaper to fix. Secondary drivers include consistent code quality that makes review faster, automated governance that replaces manual checklist processes, and knowledge preservation that prevents repeated problem-solving.

**What is the impact on defect rates?**
The governance gate catches a significant proportion of defects that would otherwise reach review, testing, or production. Specific impact depends on the team's starting baseline, but teams operating under structural governance consistently report reduction in defects escaping to later stages.

**Does CORTEX slow down development?**
The governance gate adds a small overhead to each operation. However, the time spent on rework prevention — catching issues early rather than late — consistently outweighs the overhead. Most teams report net positive throughput within the first two weeks of adoption.

**How do we track the value CORTEX is delivering?**
CORTEX tracks governance violations caught and fixed, test pass rates over time, code quality trends, session productivity metrics, and issue recurrence rates. These metrics are available through Prometheus dashboards and can be integrated into existing engineering metrics platforms.

**How does CORTEX handle regulated or compliance-sensitive environments?**
The tamper-evident audit trail supports compliance reporting. Every governance decision is documented with the rule applied, the outcome, and the timestamp. For regulated industries (finance, healthcare, defence), this trail provides documented evidence of consistent governance application — which is often a requirement for code quality certification.

---

*Answers verified against live CORTEX implementation and architecture documentation*
