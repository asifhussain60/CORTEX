# NotebookLM Video Prompt -- Tutorial 04 -- Onboarding and Customisation

**Target length:** ~8 minutes
**Audience:** Platform engineers and team leads adding CORTEX to an existing repository or team
**Visual Theme:** Warm amber/gold glassmorphism (tutorial series accent)
**Prerequisite:** Tutorial 02 complete (command catalogue familiar)
**Narrator gender:** Male (T04 -- even)
**Goal:** Viewer has onboarded a real external repository and understands how to customise CORTEX governance for their team

---

## ZERO-OVERLAP DECLARATION
This tutorial exclusively owns:
- The /onboard command: LENS analysis of an external repository
- Multi-repo customisation: team-specific governance rules and workflow templates
- The "repository import" visual: external files flowing into CORTEX as particles
- Governance YAML customisation: adding team rules without touching core governance

Does NOT repeat: installation (T01), command catalogue (T02), E2E feature build (T03), VS Code navigation (T05), chat workflow intro (T06), result interpretation (T07).

---

## Steering Prompt
Paste into NotebookLM Customize - Steering Prompt:

"Create an ~8 minute hands-on tutorial for platform engineers and team leads who want to onboard an existing codebase to CORTEX and customise governance rules for their team. Cover: /onboard command and LENS analysis output, adding custom governance rules in cortex-registry/company/, and adjusting workflow templates for team-specific needs. Narration must explain what each customisation decision means for the team -- not read YAML. Use only provided sources."

---

## NARRATION RULE -- MANDATORY
The narrator never reads YAML or configuration values aloud. Every narration line explains the team impact, the governance rationale, or the extensibility principle.

---

## Cinematic treatment -- "Repository Import Flow"

**Unique opening (repository import -- T04's visual identity):**
The amber-lit CORTEX environment. An external repository appears as a floating glassmorphic box to the LEFT of the frame, labelled "existing-repo/".
Inside: files visible as stacked cards -- Python files, YAML configs, test files.
An amber particle stream begins flowing from the external repo box rightward into the CORTEX workspace.
Each file card converts as it crosses the boundary: plain card -> glassmorphic amber-bordered card with CORTEX analysis overlay.
On-screen label: "Every repository can be onboarded. CORTEX adapts to it, not the reverse."
This is T04's signature visual: the act of bringing an external codebase into the CORTEX intelligence layer.

### Visual Physics
- Background: #0a0e27
- Accent: #f5a623 amber
- External repo: slightly warmer, desaturated glassmorphism (not yet CORTEX-lit)
- Particle stream: amber with cyan highlights as files cross the boundary
- CORTEX workspace: fully lit amber environment after import

---

## Scene-by-scene breakdown

**SCENE 1 -- "The External Repository" [0:00-0:45]**
External repo box floats in. File cards visible inside. No CORTEX overlay yet.
Narrator: "Every team has existing code. CORTEX doesn't require a greenfield start. The onboarding workflow runs LENS analysis on any repository and produces a governance baseline -- what exists, what's missing, what the risk profile looks like."

**SCENE 2 -- "/onboard in Action" [0:45-2:30]**
User types `/onboard {path}` in Copilot Chat.
LENS analysis animation: Language -> Examination -> Navigation -> Synthesis. Four concentric rings activate inward.
LENS output card materialises:
- Language: Python 3.11, FastAPI, pytest
- Examination: 847 functions, 234 with type hints (28% gap)
- Navigation: 3 circular import risks, 2 undefined test fixtures
- Synthesis: P0 gap: no governance rules. P1 gap: 68% test coverage.
Particle stream begins -- files flowing from external repo into CORTEX workspace.
Narrator: "LENS does not judge the repository. It maps it. The P0 and P1 gaps are not failures -- they are the onboarding agenda. You know exactly where to focus first."

**SCENE 3 -- "Adding Team Governance Rules" [2:30-4:30]**
YAML editor panel: `cortex-registry/company/team-rules.yaml`
A new governance rule being written:
```yaml
TEAM-001:
  description: "All API endpoints must have response_model defined"
  severity: P1
  scope: cortex/api/**
```
Narrator: "Custom rules live in cortex-registry/company/ -- never in cortex-registry/core/. The core governance rules are the shared contract. Your team rules extend it. This separation is intentional: team rules can be updated without touching the framework's integrity contracts."
Lower-third: "cortex-registry/company/ -- team extension point. Never modify cortex-registry/core/"

**SCENE 4 -- "Adjusting Workflow Templates" [4:30-6:00]**
Template editor: `cortex-registry/workflows/templates/sdlc/implement-workflow.yaml`
A composite workflow shown -- team adds a custom primitive to the sequence:
```yaml
steps:
  - primitives/governance/holistic-validation-gate.yaml
  - company/team-api-contract-check.yaml    # team custom step
  - primitives/execution/ac-marker-emit.yaml
```
Narrator: "Workflow templates are composable. Adding a team step is additive -- you add a primitive, you add it to the workflow reference. The framework picks it up on the next run. No restart. No patch to core modules."

**SCENE 5 -- "Running the First Audit on the Onboarded Repo" [6:00-7:00]**
`/audit fix` fires on the onboarded repository. 9-stage pipeline.
Initial run: 14 P1 violations found. Fix cycle 1: 9 resolved. Fix cycle 2: 5 resolved. Fix cycle 3: 0 violations.
Green cascade. AC_COMPLETE.
Narrator: "The convergence loop ran three cycles -- the maximum allowed. Fourteen violations to zero. That is not exceptional performance; that is the expected outcome of a properly functioning governance pipeline on a freshly onboarded repository. The ceiling is three cycles, by design."

**SCENE 6 -- "What Onboarding Means for the Team" [7:00-End]**
Three outcome cards:
- "Shared baseline" -- every team member runs against the same governance rules
- "Extensible without conflict" -- team rules in company/ never overwrite core contracts
- "Auditable from day one" -- every change traceable in SQLite from first /audit fix run
Narrator: "Onboarding is not a one-time event. As the team adds new rules and templates, the governance layer grows with the codebase. The baseline you set today is the floor -- not the ceiling."
Outro card: "Next: Tutorial 05 -- Getting Started in VS Code"

---

## Audio direction
- Repository import: a flowing particle whoosh as files cross the workspace boundary
- LENS rings: ascending tones per ring activation (inner = highest pitch)
- Rule addition: a sharp amber "write confirmed" click when YAML is saved
- AC_COMPLETE on audit: the same clean bell tone from T03 -- establishing series continuity

---

## Production note
The particle import stream opening is T04's visual identity. Do not replace it with a generic title card. The external repo box should be visually distinct (slightly less saturated) from the CORTEX workspace until the files cross the boundary -- the transformation is the story.
