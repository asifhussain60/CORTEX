# CORTEX V2 + Claude Agents and SKILL Development

This file defines how CORTEX V2 works with Claude-class agents and how SKILL modules are designed, validated, and evolved.

## Operating model

CORTEX V2 uses Claude agents as high-capacity reasoning partners while keeping governance and execution integrity inside CORTEX controls.

- Claude agent role:
  - Decompose complex intent.
  - Synthesize architecture and implementation pathways.
  - Generate high-quality plans and decision narratives.

- CORTEX role:
  - Enforce governance constraints.
  - Gate execution with TDD and convergence checks.
  - Maintain audit trail, phase sequencing, and production safety.

## Agent integration contract

Each Claude-integrated flow should follow this contract:

1. Intent intake and scope lock.
2. Capability boundary check against `llm-capabilities.yaml`.
3. Plan generation mapped to active phase file.
4. Tool execution through MCP interfaces only.
5. Validation gates (tests, policy checks, convergence loop).
6. Completion marker + artifact trace update.

## SKILL design blueprint

A SKILL in V2 is a bounded capability package with clear interfaces.

Required sections per SKILL:
- Purpose and execution modes.
- Inputs, outputs, and guardrails.
- Tool dependencies (MCP operations, not free-form shell assumptions).
- Governance constraints it must obey.
- Test strategy and verification evidence.
- Failure handling and fallback behavior.

Practical example:
- A `cortex-ops` SKILL can orchestrate audit + health + vacuum tasks.
- The SKILL does not bypass policy; it calls policy-enforced tools and returns compliant outcomes.

## Claude-specific best practices

- Keep prompts declarative and policy-aware.
- Avoid duplicating governance text across agent files; reference shared policy contracts.
- Use operation-based tool calls (`op`) to keep agent logic stable as internal implementations evolve.
- Keep response formats minimal, deterministic, and machine-parseable where needed.
- Add explicit “stop conditions” for long-running chains.

## Validation model for Claude + SKILL flows

Every new or changed SKILL should pass:

- Capability boundary validation (ownership is explicit).
- Workflow contract validation (all required primitives/gates present).
- Behavioral tests (happy path + failure path).
- Governance compliance checks.
- Traceability checks (phase, sweep, or completion markers where required).

## Team workflow

- Architects define SKILL boundaries and interfaces.
- Engineers implement through phase-linked tasks.
- Auditors verify governance and safety criteria.
- AI operators tune prompts and invocation patterns.

This separation keeps Claude-driven acceleration while preserving platform reliability.

## Future adaptation path

As Claude capabilities improve:

- Update `llm-capabilities.yaml` ownership tags.
- Reduce unnecessary orchestration scaffolding.
- Keep governance, certification, and safety controls stable.
- Re-run phase-level validations before promoting changes.

The result is a durable agent platform: high reasoning velocity with strict operational integrity.
