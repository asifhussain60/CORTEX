# NotebookLM Video Prompt — 09 — Knowledge, Domain Synthesis, and Governance Rules

**Target length:** 10–13 minutes
**Audience:** Architects, Engineering Leads, Team Leads onboarding new domains — people responsible for configuring what CORTEX knows about their organisation and ensuring governance rules reflect their business context
**Narrator gender:** Female (Video 09 — odd position in series, per VBP-017)
**Visual theme:** Dark-blue glassmorphism · Knowledge lattice / branching tree motif · Gold #FFD700 for domain knowledge, cyan for synthesis outputs, amber for governance enforcement
**Series position:** Configuration depth — the only video covering how CORTEX is taught your domain, how governance rules are structured and enforced, and how your team's best practices become code-level constraints

---

## 🎯 Identity Mission
This video is the **definitive knowledge configuration deep-dive** for Architects and Engineering Leads who own the answer to a critical question: *"How does CORTEX know what's right for our team — not just what's right in general?"*

Out of the box, CORTEX ships with governance rules and best practices that apply broadly. But every organisation has a domain: financial services teams have precise-decimal and audit-trail requirements; healthcare teams have privacy and access-control rules; platform teams have infrastructure-as-code and pipeline-as-code mandates. CORTEX encodes these as **domain knowledge profiles** — structured YAML files that specify which rules apply, at what severity, and whether they are enforced automatically or advisory.

This video explains three things:

1. **What the knowledge registry is** — a structured YAML library covering architecture best practices, security patterns, domain profiles (FinOps, Healthcare, DevOps, Legal, Machine Learning, and more), and your own company repositories — all queryable by CORTEX's intelligence layer at runtime.

2. **How domain synthesis works** — when CORTEX processes a request, it does not apply a single global ruleset. It queries the knowledge registry for the relevant domain context — identifying which best practices, compliance rules, and architectural patterns apply to this file, this service, this team — and synthesises a precision governance context for that operation.

3. **How governance rules are structured** — the 55+ governance YAMLs in the registry define rules at four severity levels (critical, high, medium, low), specify enforcement mode (mandatory or recommended), and in many cases include auto-fix guidance. When a rule fires, it is not an opaque failure — it names the pattern, the violation, and the remediation.

Teams that configure their domain profile invest once and benefit on every subsequent operation: every audit, every commit gate, every governance check reflects their actual compliance obligations — not a generic default.

---

## ⚠️ ZERO-OVERLAP DECLARATION
This video exclusively owns:
- Knowledge registry architecture: domain profiles (YAML), architecture best practices, security patterns, company repository profiles
- Domain synthesis mechanics: how CORTEX queries the knowledge registry per-request to assemble a precision governance context
- Governance YAML structure: severity levels, enforcement modes, auto-fix fields — readable by the engineering team, not opaque config
- How teams onboard their domain: the `/onboard` command, LENS analysis, resulting knowledge profile
- The multi-domain profile list with evidence: FinOps, Healthcare, DevOps, Legal, Machine Learning, Security Operations, Auth

Does NOT repeat: self-learning mechanics (Video 08), workflow template composition (Video 06), what CORTEX is (Video 01), architecture pipeline overview (Video 03). The business-level framing of "CORTEX learns your domain" is introduced in Video 01 — this video owns the configuration mechanics.

---

## Steering Prompt
*Select the **Explainer** format in NotebookLM, then paste into NotebookLM → Customize → Steering Prompt:*

> "Select the Explainer format to create a 10–13 minute technical walkthrough for architects and engineering leads. Cover: (1) the CORTEX knowledge registry — what it contains, how it is structured as YAML files across domain profiles, architecture best practices, and security patterns; (2) how CORTEX synthesises a precision governance context per request by querying the relevant domain knowledge rather than applying a global ruleset; (3) how governance rules are structured — severity levels, enforcement modes, auto-fix capability — and how teams read and extend them; (4) how a team onboards their own domain using the /onboard command. Tone: senior architect configuring a new system for an enterprise team — precise, practical, focused on what the lead needs to do and what they will get. Use only the provided sources, and ensure all visual generation uses a knowledge lattice / branching tree motif with Gold domain nodes, cyan synthesis outputs, and amber governance enforcement markers, overlaid on a Dark-blue glassmorphism theme."

---

## Ground-truth constraints
- Knowledge registry location: `cortex-registry/knowledge-base/`
  - Domain profiles: `profiles/` — `finops-v1.0`, `healthcare-v1.0`, `devops-v1.0`, `legal-v1.0`, `ml-v1.0`, `security-ops-v1.0`, `auth-v1.0`
  - Architecture best practices: `architecture/architecture-best-practices.yaml`
  - Security patterns: `security/owasp-top10.yaml`, `security/cicd-hardening.yaml`
  - Governance rules: `governance/compliance-rules.yaml`, `governance/data-rules.yaml`, `governance/operations-rules.yaml`, `governance/development-rules.yaml`, `governance/security-rules.yaml`
  - Company repository profiles: `repositories/` — `cortex.yaml`, `badmonolith.yaml`, `ksessions.yaml`
- Domain profile structure (evidence: `finops-v1.0`):
  - `profile.id`, `profile.name`, `profile.category`, `profile.description`, `profile.tags`
  - `rules[]` each with: `id`, `name`, `severity` (critical/high/medium/low), `description`, `pattern`, `enforcement` (mandatory/recommended), optional `auto_fix: true`
  - `compatibility`: minimum CORTEX version, Python version range
- Onboard command: `cortex_onboard_repository` MCP tool — runs LENS analysis on a repository and produces a knowledge profile including business language summary and dashboard
- 55+ governance YAMLs in `cortex-registry/core/` — enforced at pre-commit, CI, and runtime
- Domain synthesis: `KnowledgeSynthesizer` (`cortex/intelligence/learning/knowledge_synthesizer.py`) + `KnowledgeRegistryProxy` (`cortex/knowledge/registry_proxy.py`) — CORTEX queries the registry and assembles a precision context per operation
- Do NOT use acronyms in narration: say "governance rule" not "CORE-XXX", say "domain profile" not "profile ID"
- Claims permitted: "rules reflect your compliance obligations", "auto-fix available for common violations", "teams read and extend the YAML directly"
- Claims forbidden: "CORTEX writes your compliance policy", "replaces a compliance officer", "eliminates all violations"

---

## Visual ingredients
Upload as PNG/JPG:
1. `cortex-docs/assets/diagrams/15-diagram-governance-rule-enforcement-tiers.md` — governance rule tiers (Scene 5)
2. `cortex-docs/assets/diagrams/11-diagram-intelligence-lens-analysis-pipeline.md` — LENS analysis pipeline (Scene 3)
3. `cortex-docs/assets/image-prompts/shared/02-lens-intelligence-pipeline.prompt.md` — intelligence pipeline (Scene 3)
4. `cortex-docs/assets/image-prompts/learner/02-knowledge-concept-map.prompt.md` — knowledge concept relationships (Scene 2)

**Cinematic treatment — Knowledge lattice:**
The persistent visual is a branching knowledge tree — the root is CORTEX's knowledge registry. Branches extend to domain profile nodes (gold), governance rule nodes (amber), architecture pattern nodes (cyan), and company repository nodes (white). As each scene progresses, the relevant branch illuminates fully while others dim to 30% opacity (VBP-009 signaling). When domain synthesis occurs, gold threads from multiple branches converge into a single synthesis capsule (cyan) — the precision governance context assembled for that operation.

---

## Scene-by-scene breakdown

**SCENE 1 — "The Domain Problem" [0:00–1:30]**
Visual: Two teams, two codebases. Team A: financial services — a float used for a currency calculation. Team B: healthcare — a patient identifier logged in plain text. Both pass a generic AI governance check. Both are violations in their actual domain.
No CORTEX knowledge configuration yet. Knowledge tree is bare.
Narrator (female, architect-tone): *"Generic governance rules apply generically. If your organisation handles financial transactions, generic rules don't know that float is the wrong type for currency. If your team handles patient data, generic rules don't know that plain-text identifiers in logs are a compliance failure. CORTEX is configurable — because your domain is specific."*

**SCENE 2 — "The Knowledge Registry" [1:30–4:30]**
Visual: The knowledge tree materialises — root node: `cortex-registry/knowledge-base/`. Branches unfold one at a time:
  Branch 1 — Domain Profiles (gold): seven profile nodes illuminate — FinOps, Healthcare, DevOps, Legal, Machine Learning, Security Operations, Auth. Each node pulses gently.
  Branch 2 — Architecture Best Practices (cyan): `architecture-best-practices.yaml` — patterns from hexagonal architecture, domain-driven design, and security-by-design visible as sub-nodes.
  Branch 3 — Security Patterns (amber): `owasp-top10.yaml`, `cicd-hardening.yaml`.
  Branch 4 — Governance Rules (amber): five governance YAML files — compliance, data, operations, development, security.
  Branch 5 — Company Repository Profiles (white): your own repositories onboarded with business context.

The FinOps profile node expands to show its rule structure as a glassmorphic card:
```yaml
id: FIN-001
name: audit-trail-required
severity: critical
description: All financial transactions must have complete audit trails
enforcement: mandatory

id: FIN-002
name: decimal-precision
severity: high
description: Use Decimal type for monetary values, never float
auto_fix: true
enforcement: mandatory
```
Lower-third: `"Governance rules your team can read, review, and extend"`
Narrator: *"Every domain profile is a YAML file. Your team can read it, review it in a pull request, and extend it with rules specific to your compliance obligations. A rule has a name, a severity level, and an enforcement mode. Some rules include auto-fix capability — CORTEX can apply the remediation directly, not just flag the violation."*

**SCENE 3 — "Domain Synthesis: Precision Context Per Request" [4:30–7:30]**
Visual: A developer submits a request — `/audit fix` on a financial services repository. The knowledge synthesis animation begins:
  Step 1 — Repository profile detected: `finops-v1.0` profile identified from the repository's onboarding record.
  Step 2 — Domain branches illuminate: FinOps profile (gold), compliance governance rules (amber), architecture best practices for financial services (cyan). Other branches dim.
  Step 3 — Synthesis capsule assembles: gold, amber, and cyan threads converge into a single precision context capsule. Contents: 7 mandatory rules, 4 high-severity rules, 2 auto-fixable rules. Architecture patterns: hexagonal, domain-driven design.
  Step 4 — Capsule delivered to governance engine: only the relevant rules fire on this codebase.

A float-for-currency violation is detected: `FIN-002 — decimal-precision — HIGH — auto_fix: true`. Auto-fix applies. Rescan: 0 violations.

Lower-third: `"Domain synthesis — governance that knows what your code is for"`
Narrator: *"CORTEX does not apply all 55+ governance rules to every codebase. It queries the knowledge registry for the domain profile that matches this repository, assembles the relevant rules and best practices, and delivers a precision governance context. A financial services repository gets financial services rules. A healthcare repository gets healthcare rules. The synthesis happens per-request — so as your domain profile evolves, every subsequent audit reflects the updated standard."*

**SCENE 4 — "Onboarding Your Domain" [7:30–10:00]**
Visual: The `/onboard` command executes on a new repository. LENS analysis runs — four rings illuminate (Language → Examination → Navigation → Synthesis). A new company repository profile card emerges: repository name, detected architecture patterns, inferred domain tags.

The architect reviews the generated profile. Two custom rules are added manually to the YAML:
```yaml
id: TEAM-001
name: event-sourcing-required
severity: high
description: All order state changes must be recorded as domain events
enforcement: mandatory

id: TEAM-002
name: no-direct-db-in-handlers
severity: critical
description: HTTP handlers must not access database directly — use repository pattern
enforcement: mandatory
auto_fix: false
```
The new rules are committed to version control. On the next audit run, both rules fire correctly on existing violations.

Lower-third: `"Your rules. Your domain. Version-controlled."`
Narrator: *"Onboarding a repository takes a single command. CORTEX analyses the codebase with LENS, produces a knowledge profile with a plain-English business language summary, and creates a starting point for your domain configuration. Your team adds the rules that reflect your actual compliance obligations — in the same YAML format, in the same version-controlled registry. From that point forward, every governance operation on that repository reflects your standards."*

**SCENE 5 — "Governance Rules: Readable, Enforceable, Auditable" [10:00–12:00]**
Visual: The 55+ governance YAML files from `cortex-registry/core/` materialise as a catalogued grid — 55+ labelled cards, colour-coded by severity: critical (red border), high (amber border), medium (yellow border), low (grey border).
Enforcement mode filter applied: mandatory (solid border) vs. recommended (dashed border). Auto-fix filter: rules with auto-fix highlighted with a green badge.

A governance violation fires during a real audit run: type annotations missing. The rule card illuminates — name, severity, description, remediation guidance all visible. Auto-fix applies. The card dims to green: resolved.

Lower-third: `"55+ governance rules — enforced at pre-commit, continuous integration, and runtime"`
Narrator: *"Governance rules in CORTEX are not a black box. Every rule has a name, a severity level, an enforcement point, and a description your team can read. When a rule fires, the violation output names the rule, describes the problem, and — where auto-fix is available — applies the remediation. Your team is never left with an opaque red mark and no guidance."*

**SCENE 6 — "What This Gives the Architecture Lead" [12:00–End]**
Visual: Four outcome cards — architecture lead framing:
  `"Domain-specific governance"` — financial, healthcare, legal, DevOps, machine learning profiles available; extend with your own rules
  `"Readable, reviewable rules"` — YAML in version control; your team approves rule changes the same way they approve code changes
  `"Auto-fix for common violations"` — not just flagging — remediating
  `"Knowledge that evolves with your standards"` — update the profile YAML; every subsequent audit reflects the update
Narrator: *"The knowledge registry is not a configuration you set once and forget. It is a living standard that your team maintains — in the same tools and workflows you already use. When your compliance obligations change, you update the YAML. When your architectural standards evolve, you add a rule. CORTEX enforces whatever you encode."*
Final lower-third: `"Your domain. Your rules. Enforced on every commit."`

---

## Audio direction
- Warm ambient: a low, library-like hum — distinct from the technical electronic ambience of Videos 06 and 08
- Knowledge tree branch illumination: a gentle resonance tone as each branch activates — not a click, a swell
- Domain synthesis convergence: a rising crystalline tone as threads converge into the synthesis capsule
- Auto-fix resolution: a clean, single-note confirmation tone — quiet, not celebratory
- No dramatic music — this is a configuration and architecture conversation

---

## Production note
Use NotebookLM for narrative + knowledge-tree slide generation. The knowledge tree can be rendered as a progressive branching diagram with gold/amber/cyan/white nodes — NotebookLM handles layered progressive reveal well. For Scene 3 (domain synthesis), use the LENS analysis pipeline diagram (`11-diagram-intelligence-lens-analysis-pipeline.md`) as the base visual before synthesis threads converge. For Scene 5 (governance rules), use the rule enforcement tiers diagram (`15-diagram-governance-rule-enforcement-tiers.md`) — it shows the 3-checkpoint, 4-tier hierarchy that underlies the 32-rule grid. For the YAML rule card in Scene 2, use actual content from `cortex-registry/knowledge-base/profiles/finops-v1.0.yaml` (lines 27–50 are suitable). For the custom rules in Scene 4, use plausible domain-specific rules consistent with an event-sourcing architecture. For the 32-rule grid in Scene 5, render as a card catalogue — do not attempt to show all 32 rules in detail; show structure and counts.

---

## NotebookLM Setup Checklist

| Step | Action | Detail |
|------|--------|--------|
| 1 | **Select format** | Choose **Explainer** in NotebookLM format picker |
| 2 | **Set narrator** | Female voice — Video 09 is odd-position in series (VBP-017) |
| 3 | **Upload sources** | Upload all 4 visual ingredients listed above as PNG/JPG |
| 4 | **Paste steering prompt** | Copy the full steering prompt above verbatim into Customize → Steering Prompt |
| 5 | **Set length target** | 10–13 minutes |
| 6 | **Verify visual theme** | Confirm knowledge lattice / branching tree motif — gold domain nodes, cyan synthesis, amber governance, dark-blue background |
| 7 | **Lock source-only mode** | Enable "Use only provided sources" — domain profile names and rule IDs must come from actual YAML files |
| 8 | **Verify acronym discipline** | No "RCA", "URS", "TDD", "CORE-XXX" in narration — use full descriptive forms |
| 9 | **Preview Scene 3 first** | The domain synthesis animation is the conceptual core — render it alone to confirm the multi-branch convergence to a single capsule reads clearly before generating the full sequence |
