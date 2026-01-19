# 🧠 CORTEX Prompt Architecture Review & Alignment
**Author:** Asif Hussain | **Phase:** PHASE-PROMPT-ARCHITECTURE | **Orchestrator:** MasterOrchestrator ✅

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## Executive Summary

Current prompt architecture (`CORTEX.prompt.md`) is comprehensive but needs:
1. **Separation of concerns** – Master Orchestrator vs. Instruction Rules
2. **Copilot-specific instructions** – For direct Claude integration
3. **Orchestrator-agnostic design** – Works with or without system prompts
4. **TIER 0 enforcement** – More direct governance integration

---

## Current State Analysis

### CORTEX.prompt.md (v3.0)
**Status:** ✅ Comprehensive Master Orchestrator specification  
**Size:** 495 lines  
**Strengths:**
- Master Orchestrator pattern clearly defined (4 stages)
- LENS Protocol fully documented
- TIER 0 rules referenced
- Response header format (CORE-029) specified

**Gaps:**
- No `copilot-instruction.md` for standalone Copilot usage
- Master Orchestrator embedded in single file (should be modular)
- Governance rules embedded as references (should be live links)
- No fallback for system prompt rejection

---

## Recommended Architecture

### File 1: CORTEX.prompt.md (Master Orchestrator)
**Purpose:** System prompt for CORTEX system agents  
**Scope:** Master Orchestrator coordination  
**Contents:**
- Intent comprehension (LENS protocol)
- 4-stage orchestrator pattern
- Governance enforcement (TIER 0)
- Response formatting (CORE-029)

### File 2: copilot-instruction.md (Copilot Integration)
**Purpose:** Direct Claude/Copilot integration without system prompts  
**Scope:** Standalone instruction set  
**Contents:**
- Quick-start guide (always present)
- Governance checklist (embedded)
- Key rules (most critical 10)
- Response format enforcement

---

## Key Improvements

| Aspect | Current | Proposed |
|--------|---------|----------|
| **Copilot Integration** | None | Full support |
| **Governance Linking** | References only | Direct rules + checkboxes |
| **Offline Operation** | Requires system prompt | Self-contained |
| **File Size** | 495 lines | CORTEX: 400 / copilot: 200 |
| **TIER 0 Enforcement** | 7 mentioned | 15 core rules embedded |
| **Response Header** | Documented | Auto-checklist |

---

## Implementation Plan

### Phase 1: Recreate CORTEX.prompt.md
- ✅ Keep Master Orchestrator pattern (4 stages)
- ✅ Streamline governance references → direct TIER 0 subset
- ✅ Modernize response header enforcement
- ✅ Remove administrative overhead

### Phase 2: Create copilot-instruction.md
- ✅ Standalone instruction set (works without system prompt)
- ✅ Quick governance checklist (top 10 TIER 0 rules)
- ✅ Embedded best practices
- ✅ Response header enforcement

### Phase 3: Validation
- ✅ Verify both files follow CORE-001 (<500 lines each)
- ✅ Test with sample requests
- ✅ Confirm TIER 0 compliance
- ✅ Document in this file

---

## Governance Alignment Checklist

| Rule | Current | Proposed | Status |
|------|---------|----------|--------|
| CORE-001 | 495 lines | Split into 2×300 | ✅ |
| CORE-003 | ❌ Code blocks | ✅ Visual format | ✅ |
| CORE-029 | ✅ Documented | ✅ Enforced | ✅ |
| CORE-011 | N/A (docs) | N/A | ✅ |
| CORE-012 | ✅ Docstrings | ✅ Complete | ✅ |

---

## Files to Recreate

1. `.github/prompts/CORTEX.prompt.md` – Master Orchestrator (delete + recreate)
2. `.github/prompts/copilot-instruction.md` – Copilot integration (create new)

**Status:** Ready for execution
