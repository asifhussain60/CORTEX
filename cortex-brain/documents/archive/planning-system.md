# CORTEX Planning System

**Purpose:** File-based feature planning with persistent state  
**Version:** 2.0 (EPM Orchestrator)  
**Status:** ✅ Production Ready

---

## Overview

Planning System creates **persistent planning files** stored in `cortex-brain/planning/` (NOT chat-only). Plans survive conversation resets and can be resumed anytime.

---

## Trigger Detection

**PRIORITY triggers** (detect before all other intents):
- "plan"
- "let's plan"  
- "plan a feature"
- "plan this"
- "help me plan"
- "planning"
- "feature planning"
- "i want to plan"

---

## Planning Workflow

### Phase 1: Intent Detection
```
User: "plan authentication"
→ Router detects PLAN intent
→ Load: help_plan_feature.md
→ Activate: Work Planner agent (Right Brain)
```

### Phase 2: Confidence Assessment
```
High (80-100%): Proceed to breakdown
Medium (50-79%): Ask 1-2 confirming questions
Low (<50%): Ask detailed clarifying questions
```

### Phase 3: Interactive Session
```
CORTEX asks questions:
1. Authentication methods? (JWT, OAuth, SAML)
2. User types? (admins, users, guests)
3. Integration requirements?
4. Security constraints?
```

### Phase 4: Plan Generation
```
Generate multi-phase roadmap:
- Phase 1: Foundation (tasks, dependencies, risks)
- Phase 2: Core Implementation
- Phase 3: Integration
- Phase 4: Testing & Validation

Save to: cortex-brain/planning/auth-plan-2025-11-17.md
```

---

## File Structure

```
cortex-brain/planning/
  ├── auth-plan-2025-11-17.md
  ├── dashboard-plan-2025-11-15.md
  └── api-refactor-plan-2025-11-10.md

Each file contains:
- Feature name & description
- Complexity estimate
- Phase breakdown (tasks, duration, dependencies)
- Risk analysis
- Acceptance criteria
- Execution commands
```

---

## Commands

```
# Start planning
"plan authentication"

# Continue saved plan
"continue" or "resume"

# Refine plan
"add rate limiting to Phase 2"
"split Phase 3 into two phases"

# Skip questions
"skip question 3" or "skip"

# Begin execution
"start Phase 1" or "let's begin"
```

---

## Unified Planning Core (DRY Principle)

**Single source of truth:** `help_plan_feature.md`

All planning operations use this module:
- Interactive planning workflow
- Agent coordination (Work Planner)
- Phase-based breakdown
- Risk assessment
- File-based persistence

---

## .gitignore Configuration

**Brain preservation rules:**
```
# CORTEX brain files (local state, never commit)
cortex-brain/tier1/conversations.db
cortex-brain/tier2/knowledge-graph.db
cortex-brain/tier3/context-intelligence.db
cortex-brain/planning/*.md

# Planning files are workspace-specific
# Use sync strategy below for multi-machine
```

---

## Backup & Sync Strategy

### Single Machine
```bash
# Automatic backup (done by CORTEX)
# Plans saved to: cortex-brain/planning/
# No action needed
```

### Multi-Machine
```bash
# Export planning files
cortex export --planning --output planning-backup.zip

# Transfer to other machine

# Import on other machine  
cortex import --planning --input planning-backup.zip
```

---

## Implementation Status

✅ **Planning triggers:** Implemented in intent router  
✅ **Work Planner agent:** Operational (Right Brain)  
✅ **File-based workflow:** Persistent .md files  
✅ **Multi-phase breakdown:** Phase templates ready  
✅ **Risk assessment:** Integrated into planning  
✅ **Resume capability:** Load saved plans from file  

🎯 **Future:** Vision API integration for screenshot-based planning (awaiting GitHub Copilot API)

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Last Updated:** 2025-11-17 | Planning System
