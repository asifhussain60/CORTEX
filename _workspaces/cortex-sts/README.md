# cortex-sts/ — Sharpen The Saw (STS) Demo Material

> **Status:** Active demo material — PB-STS-001 showcase. Do NOT delete.

## Purpose

This directory contains the **Sharpen The Saw** (STS) demonstration repositories used
as live examples for CORTEX's refactoring and onboarding capabilities.

## Contents

### `CortexLabs/BadMonolith/`
A deliberately over-engineered legacy monolith used as the **before** state in the
PB-STS-001 playbook. It demonstrates common anti-patterns that CORTEX's orchestrators
are designed to detect and remediate.

### `CortexLabs/Refactored/`
The **after** state — the same codebase after CORTEX-guided refactoring. Demonstrates
the output of the full LENS → challenge → refactor pipeline.

## Playbook Reference

- Registry: `cortex-registry/_cortex-master/playbooks/sharpen-the-saw/pb-sts-001-badmonolith-refactoring.yaml`
- Gaps: `cortex-registry/_cortex-master/playbooks/sharpen-the-saw/mcp-compatibility-gaps.yaml`

## CORE Governance

These are **demo repositories**, not production code. They are intentionally not subject
to CORE-008 (TDD), CORE-011 (type hints), or CORE-028 (snake_case) — they exist to
showcase what CORTEX fixes, not to be production-ready themselves.

---
*Added: Phase 61-D — cortex-sts/ documentation clarification (CORE-002 compliant: no .txt sprawl)*
