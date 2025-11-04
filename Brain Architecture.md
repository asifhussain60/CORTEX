# KDS BRAIN Architecture Specification

This document defines the architecture, data structures, and behavior
required for the KDS BRAIN (Biologically-Inspired Reasoning and Adaptive
Intelligence Network) used for Copilot context management.

The BRAIN simulates key functions of human cognition to manage AI
context efficiently:

-   Permanent instincts (non-resettable knowledge)
-   Adaptable project-knowledge layer (resettable memory)
-   Working memory (short-term execution context)

------------------------------------------------------------------------

## System Overview

| Layer                      | Biological Analog         | Purpose                                           | Resettable    |
|----------------------------|---------------------------|---------------------------------------------------|---------------|
| Instinct Memory            | Brainstem / Basal Ganglia | Permanent rules, guardrails, behavior patterns    | ❌ No         |
| Long-Term Knowledge Memory | Cortex / Hippocampus      | Learned project structure, associations, patterns | ✅ Yes        |
| Working Memory             | Prefrontal Cortex         | Current task state & recent intent context        | 🔄 Auto-flush |

------------------------------------------------------------------------

## Directories & Files

    /KDS/brain/
      instincts.yaml            # permanent rules & constraints
      knowledge.yaml            # project knowledge graph (resettable)
      working-memory.jsonl      # short-term rolling buffer

------------------------------------------------------------------------

## File Specifications

### 1. `instincts.yaml` (Permanent)

Non-modifiable unless versioned & explicitly updated.

Purpose: enforce engineering discipline & invariant behavior.

Example structure:

``` yaml
instincts:
  enforce_tdd: true
  enforce_ui_test_ids: true
  protect_core_files: true
  avoid_monoliths: true
  ignore_temp_patterns: true

routing_thresholds:
  ask_user: 0.70
  auto_route: 0.85

commit_rules:
  semantic_commits: true
  categories:
    - feat
    - fix
    - test
    - docs
```

------------------------------------------------------------------------

### 2. `knowledge.yaml` (Resettable Learning Layer)

Stores learned associations about the specific application.

Purpose: - Understand file relationships - Track co-modification
patterns - Learn recurring tasks and flows - Build a semantic project
understanding

Structure:

``` yaml
files:
  HostControlPanel.razor:
    coedited_with:
      - DashboardService.cs
      - noor-canvas.css
    tests:
      - fab-button.spec.ts
    patterns:
      - ui
      - animation

patterns:
  ui_workflow:
    - plan
    - execute
    - test

task_patterns:
  - visual change -> create test + implement
```

------------------------------------------------------------------------

### 3. `working-memory.jsonl` (Rolling Context Buffer)

Purpose: hold last N units of attention.

Behavior: - FIFO queue - Max \~100 entries - Auto-flush on session end

Format (JSON-lines):

``` jsonl
{"timestamp":"...", "phase":"2b", "task":"hover animation", "file":"FAB.razor"}
{"timestamp":"...", "phase":"2c", "task":"add test", "file":"fab-button.spec.ts"}
```

------------------------------------------------------------------------

## BRAIN Rules

### Memory Update Triggers

| Event                   | Action                           |
|-------------------------|----------------------------------|
| Task completed          | Update working memory            |
| Plan completed          | Update knowledge layer           |
| 50+ memory events       | Consolidate to knowledge         |
| Project change detected | Reset knowledge + working memory |

------------------------------------------------------------------------

## Required Behaviors

1.  Never modify instincts  
2.  Learn only validated patterns  
3.  Forget aggressively when project resets  
4.  Prioritize recent knowledge over stale memory  
5.  If confidence \< threshold → ask user  
6.  Always maintain working memory context

------------------------------------------------------------------------

## Commands

### Reset Knowledge Layer

    kds brain reset knowledge

### Full Reset (new application)

    kds brain reset all

### Dump Memory State (debug)

    kds brain inspect

------------------------------------------------------------------------

## Summary

| Layer          | File                   | Behavior                  |
|----------------|------------------------|---------------------------|
| Instincts      | `instincts.yaml`       | Permanent, never reset    |
| Knowledge      | `knowledge.yaml`       | Learns, reset per project |
| Working Memory | `working-memory.jsonl` | Rolling context buffer    |

BRAIN = Stable instincts + adaptive learning + short-term focus.
