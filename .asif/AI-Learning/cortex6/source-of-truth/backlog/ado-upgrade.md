# GitHub Copilot Instructions — Enhance ADO Orchestrator (CORTEX 6.0)

## Purpose (Read First)
Enhance the **ADO Orchestrator** so it works as a **governed intake and normalization layer** that feeds the **Planning Orchestrator**.  
The ADO Orchestrator must NOT plan, execute, or bypass governance.

Users never explicitly call orchestrators.
The **Master Orchestrator** owns orchestration and sequencing.

This work must align with:
- The CORTEX 6.0 source-of-truth epic
- SKULL protection model
- Tiered brain + 4 governance categories

---

## Confirm Existing Architecture (Do Not Change)
Confirm and preserve these invariants:

### Governance Categories (exactly four)
1. CORTEX Tier 0 (core law, immutable)
2. Business Tier 0 (company compliance constraints)
3. Company Best Practices (standards & patterns)
4. Knowledge Best Practices (advisory, learned)

### Orchestration Model
- Master Orchestrator decides flow
- Pattern Router selects orchestrators
- Planning Orchestrator is mandatory before execution
- TODO Orchestrator builds execution DAG
- Execution orchestrators act only after planning + SKULL pass

Do NOT introduce new governance categories.
Do NOT allow orchestrators to bypass planning or SKULL.

---

## What the ADO Orchestrator IS
The ADO Orchestrator is a **translator and normalizer**.

Its responsibility is to:
- Ingest ADO work artifacts (User Stories, Bugs, Epics)
- Normalize them into **structured intent**
- Propose (not decide) DoR and DoD
- Enrich intent using Business Knowledge YAML
- Hand off clean input to the Planning Orchestrator

It does NOT:
- Execute work
- Write code
- Finalize DoR / DoD
- Decide legitimacy

---

## Inputs the ADO Orchestrator Must Support
The ADO Orchestrator must accept:
- Live ADO API payloads (if available)
- OR standardized **ADO-Intent YAML** (preferred, external API friendly)

Assume ADO-Intent YAML exists or will exist.
CORTEX should be decoupled from ADO whenever possible.

---

## Core ADO Orchestrator Responsibilities

### 1. Ingest
Accept ADO data or ADO-Intent YAML containing:
- Business intent
- Description
- Acceptance criteria
- Priority / risk signals
- Links / references

No assumptions about quality.

---

### 2. Normalize
Convert ADO-specific fields into a canonical CORTEX shape:
- Intent (what outcome is desired)
- Scope
- Constraints
- Signals (risk, priority, domain)
- Raw acceptance criteria (if present)

Strip tool-specific noise.
Preserve provenance.

---

### 3. Propose DoR (Definition of Ready)
Identify readiness gaps:
- Missing acceptance criteria
- Unclear scope
- Unresolved dependencies
- Missing compliance signals

These are **proposals**, not final decisions.

---

### 4. Propose DoD (Definition of Done)
From acceptance criteria + business rules, propose:
- Validation expectations
- Testing expectations
- Compliance checks
- Non-functional requirements (when known)

Again: proposals only.

---

### 5. Enrich Using Business Knowledge YAML
Load applicable rules from:
- Business Tier 0
- Company Best Practices
- Knowledge Best Practices

Examples:
- Required security checks
- Approved tech stack
- Internal APIs to use
- Testing standards

Apply enrichment deterministically.
Do NOT override higher-tier rules.

---

### 6. Produce Planning Input
Output a **Planning-Ready Intent Object** containing:
- Normalized intent
- Proposed DoR
- Proposed DoD
- Enriched constraints
- Provenance metadata

Then STOP.

Hand off to the Planning Orchestrator.

---

## Relationship to the Planning Orchestrator (Critical)
- The Planning Orchestrator has final authority on:
  - DoR validation
  - DoD finalization
  - Legitimacy of the plan
- The ADO Orchestrator must never finalize or execute.

Shared logic MUST be reused (DRY):
- YAML validation
- Governance category resolution
- Deduplication / comparison
- Audit logging
- DoR / DoD templates

Extract shared utilities/services where needed.

---

## Child Orchestrators (If Needed)

### 1. ADO-Intent Ingestion Orchestrator (Optional)
Role:
- Handle ingestion + normalization only
- No enrichment
- No DoR / DoD proposals

Useful if ADO sources grow or diversify.

---

### 2. Business Knowledge Resolver (Shared)
Role:
- Resolve which Business / Company / Knowledge rules apply
- Used by:
  - ADO Orchestrator
  - Planning Orchestrator
  - Business YAML Import Orchestrator

This should be a shared service, not duplicated logic.

---

### 3. DoR / DoD Template Engine (Shared)
Role:
- Provide reusable templates for:
  - Stories
  - Bugs
  - Epics
- Used by ADO + Planning

---

## Pattern Routing & Registration
Register the ADO Orchestrator so the Pattern Router can detect:
- ADO payloads
- ADO-Intent YAML
- Requests referencing user stories / bugs / backlog items

Users must never select orchestrators manually.

---

## Audit & Repeatability Requirements
- Every ADO ingestion must be auditable
- Preserve source references (ADO ID, link)
- Re-processing the same story must be idempotent
- No silent overwrites

---

## Definition of Done (DoD)
- ADO artifacts can be ingested deterministically
- Intent is normalized and enriched
- DoR / DoD are proposed, not enforced
- Planning Orchestrator receives clean input
- No execution occurs without planning
- No governance tier is bypassed
- Shared logic is reused (DRY)

---

## One Line to Anchor Implementation
> The ADO Orchestrator translates backlog noise into governed intent so planning can be precise and execution can be trusted.

END.
