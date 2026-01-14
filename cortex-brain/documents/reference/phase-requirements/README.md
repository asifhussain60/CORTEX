# Phase Requirements - Historical Reference

**Status:** REFERENCE ONLY (NOT SSOT)  
**Restored from:** Git commit 635224a3f (Jan 13, 2026)  
**Purpose:** Detailed component specifications and implementation guidance

## ⚠️ IMPORTANT

These files are **REFERENCE DOCUMENTATION ONLY**.

**Authoritative Sources (SSOT):**
- AC-ID definitions: `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`
- Architecture: `cortex-brain/cx6-plan/master-plan.yaml`
- Progress: `cortex-brain/tier1/tracking/progress-tracker.json`

**Use this directory for:**
- Detailed component specifications
- Implementation guidance
- Evidence requirements
- Historical context

**DO NOT:**
- Treat as source of truth
- Update these files (they're historical)
- Use for state management

## 📁 Contents

- `phase-1-foundation.yaml` - Foundation infrastructure (AC-AUDIT, AC-GOV, AC-STATE, etc.)
- `phase-2-orchestration.yaml` - Orchestration core (AC-ORCH, AC-PLAN, AC-TDD, etc.)
- `phase-3-features.yaml` - Feature orchestrators (AC-ADO, AC-VAC, AC-CRAWLER, etc.)
- `phase-4-intelligence.yaml` - Intelligence layer (AC-LLM, AC-VISION, AC-KNOWLEDGE, etc.)

## 🔍 Recovery Details

**Original Location:** `cortex-brain/cx6-plan/phases/`  
**Deleted:** January 13, 2026 (SSOT consolidation cleanup)  
**Recovered:** January 14, 2026 (for reference purposes)

**Why Deleted:**
- SSOT enforcement - master-plan.yaml designated as single authority
- Duplicate AC-ID definitions across multiple files
- Reduced verification rate false positives

**Why Restored:**
- Detailed component specifications not in AC-INDEX.yaml
- Implementation paths and test requirements
- Evidence requirements per AC-ID
- Historical context for developers
