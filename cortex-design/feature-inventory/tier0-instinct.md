# Tier 0: Instinct Layer - Feature Inventory

**Purpose:** Document all immutable governance rules from KDS for CORTEX migration  
**Source:** `governance/rules.md` v6.0.0  
**Date:** 2025-11-05

---

## Overview

Tier 0 is the **IMMUTABLE** foundation of CORTEX. These rules CANNOT be overridden and form the cognitive "DNA" of the system.

**Total Rules:** 22 core rules (within 20-rule soft limit)  
**Categories:**
- Interface design
- Documentation
- File management
- Safety/quality
- TDD enforcement
- SOLID principles
- Brain protection

---

## Core Principles (PERMANENT - Tier 0)

### 1. **Rule #18: Challenge User Changes**
**Purpose:** Protect system quality and efficiency

```yaml
rule_id: CHALLENGE_USER_CHANGES
severity: CRITICAL
enforcement: AUTOMATIC

when_to_challenge:
  - User proposes KDS modifications
  - Changes affect core workflow
  - Efficiency may be degraded
  - TDD/SOLID principles violated

challenge_process:
  1: Analyze proposed change
  2: Query Tier 2 (knowledge graph) for patterns
  3: Identify risks (degradation, complexity, violations)
  4: Present challenge with evidence
  5: Suggest safe alternatives
  6: Require explicit override or alternative selection

examples:
  - "Skip TDD for this feature" → Challenge with success rate data
  - "Add mode switch to agent" → Challenge with SOLID violation
  - "Hardcode dependency" → Challenge with DIP alternative
```

**File:** `governance/rules/challenge-user-changes.md`

---

### 2. **Rule #19: Checkpoint Strategy**
**Purpose:** Enable safe rollback at any point

```yaml
rule_id: CHECKPOINT_STRATEGY
severity: HIGH
enforcement: AUTOMATIC

checkpoint_triggers:
  - Before major changes
  - Before risky operations
  - User requests "create checkpoint"
  - Phase transitions

checkpoint_content:
  - Current state snapshot
  - Rollback instructions
  - Changed files list
  - Success criteria

rollback_process:
  - Detect failure
  - Restore from checkpoint
  - Report what was rolled back
  - Suggest alternative approach
```

**File:** `governance/rules/checkpoint-strategy.md`

---

### 3. **Rule #20: Definition of DONE (LEFT BRAIN)**
**Purpose:** Quality gate for all work completion

```yaml
rule_id: DEFINITION_OF_DONE
severity: CRITICAL
enforcement: MANDATORY (LEFT BRAIN validates)

criteria:
  compilation:
    - Zero errors
    - Zero warnings
    - Clean build
    
  testing:
    - All tests pass
    - New tests created for new code
    - TDD cycle completed (RED → GREEN → REFACTOR)
    
  quality:
    - Code formatted
    - No linting violations
    - Documentation updated
    
  runtime:
    - App runs without errors
    - No exceptions in logs
    - Functionality verified

validation_agent: health-validator.md (LEFT BRAIN)
enforcement: Pre-commit hook, auto-commit blocker
```

**File:** `governance/rules/definition-of-done.md`

---

### 4. **Rule #21: Definition of READY (RIGHT BRAIN)**
**Purpose:** Entry gate before work begins

```yaml
rule_id: DEFINITION_OF_READY
severity: CRITICAL
enforcement: MANDATORY (RIGHT BRAIN validates)

criteria:
  requirements:
    - User story clear and complete
    - Acceptance criteria defined
    - Testable outcomes specified
    
  scope:
    - Bounded to single feature/fix
    - Dependencies identified
    - Estimate possible
    
  resources:
    - Files to modify known
    - Architectural approach clear
    - No blocking dependencies

validation_agent: work-planner.md (RIGHT BRAIN)
enforcement: Blocks execution until DoR met
```

**File:** `governance/rules/definition-of-ready.md`

---

## File Organization Rules

### 5. **Rule #1: Dual Interface Enforcement**
```yaml
rule_id: DUAL_INTERFACE
severity: CRITICAL

user_prompts:
  location: prompts/user/
  format: Human-readable, friendly
  content: Natural language instructions
  forbidden: Technical validation logic
  
internal_agents:
  location: prompts/internal/
  format: Machine-readable, structured
  content: Validation logic, YAML specs
  forbidden: User-facing language

enforcement:
  - NEVER expose internal validation to users
  - ALWAYS use templates for user output
  - Keep technical details in internal agents
```

---

### 6. **Rule #2: Live Design Document**
```yaml
rule_id: LIVE_DESIGN_DOC
severity: CRITICAL

requirements:
  - Update after EVERY KDS change
  - Track design decisions with date
  - Delete obsolete sections (trust git)
  - Human-readable for stakeholders

workflow:
  1: Make change
  2: Update design doc
  3: Update rules.md (this file)
  4: Implement code
```

---

### 7. **Rule #3: Delete Over Archive**
```yaml
rule_id: DELETE_NOT_ARCHIVE
severity: HIGH

principles:
  - Obsolete files: DELETE immediately
  - Archive folders: FORBIDDEN
  - .old suffixes: FORBIDDEN
  - Git history: PRIMARY archive

exceptions:
  - Backups before major changes (temporary)
  - Pre-migration snapshots (one-time)
```

---

### 8. **Rule #4: One Prompt Per File**
```yaml
rule_id: ONE_PROMPT_PER_FILE
severity: MEDIUM

requirements:
  - Single responsibility per file
  - No combined prompts
  - Clear file naming
  - No mode switches within file
```

---

## TDD & Quality Rules

### 9. **Rule #5: Test-First Development (TDD)**
```yaml
rule_id: TEST_FIRST_TDD
severity: CRITICAL

workflow:
  RED:
    - Write failing test FIRST
    - Verify test fails
    - Commit RED state
    
  GREEN:
    - Implement minimum code
    - Verify test passes
    - Commit GREEN state
    
  REFACTOR:
    - Clean up code
    - Verify tests still pass
    - Commit REFACTOR state

enforcement:
  - Brain Protector challenges non-TDD requests
  - Pre-commit hook verifies tests exist
  - LEFT BRAIN validates DoD (tests pass)

violations:
  - Implementing without test: BLOCKED
  - Skipping RED phase: CHALLENGED
  - No refactor: WARNED
```

---

### 10. **Rule #6: Governance Self-Enforcement**
```yaml
rule_id: GOVERNANCE_SELF_ENFORCEMENT
severity: CRITICAL

requirements:
  - Rules apply to rule changes
  - Changes require justification
  - Version increments for modifications
  - Validation before commit

process:
  1: Propose rule change
  2: Document justification
  3: Update both KDS-DESIGN.md and rules.md
  4: Increment version
  5: Validate no conflicts
  6: Commit
```

---

## SOLID Principles (Architectural Rules)

### 11. **Rule #7: Single Responsibility (SRP)**
```yaml
rule_id: SINGLE_RESPONSIBILITY
severity: HIGH

requirements:
  - One job per agent
  - No mode switches
  - Clear boundaries
  - Delegation over expansion

violations:
  - Agent doing multiple jobs: REFACTOR
  - Mode switches: CREATE dedicated agent
  - Unclear purpose: RENAME or SPLIT
```

---

### 12. **Rule #8: Interface Segregation (ISP)**
```yaml
rule_id: INTERFACE_SEGREGATION
severity: MEDIUM

requirements:
  - Dedicated specialist agents
  - No optional modes
  - Clear contracts
  - Focused interfaces

examples:
  - error-corrector.md (dedicated to corrections)
  - test-generator.md (dedicated to testing)
  - NOT: executor.md with "correction mode"
```

---

### 13. **Rule #9: Dependency Inversion (DIP)**
```yaml
rule_id: DEPENDENCY_INVERSION
severity: HIGH

requirements:
  - Abstractions for external dependencies
  - No hardcoded paths
  - Interface-based access
  - Pluggable implementations

abstractions:
  - session-loader (file/db/cloud agnostic)
  - test-runner (framework agnostic)
  - file-accessor (path agnostic)
  - brain-query (storage agnostic)
```

---

## Brain Protection Rules

### 14. **Rule #22: Brain Protection System**
```yaml
rule_id: BRAIN_PROTECTION
severity: CRITICAL

protections:
  instinct_immutability:
    - Tier 0 rules cannot be disabled
    - TDD cannot be skipped
    - DoR/DoD cannot be bypassed
    
  tier_boundary_protection:
    - Application data not in Tier 0
    - Conversation data not in Tier 2
    - Metrics not in Tier 1
    
  solid_compliance:
    - Agents stay single-purpose
    - No mode switches
    - Abstractions required
    
  hemisphere_specialization:
    - Strategic work in RIGHT BRAIN
    - Tactical work in LEFT BRAIN
    - No cross-contamination

enforcement_agent: brain-protector.md
challenge_protocol:
  1: Detect violation
  2: Query knowledge graph for evidence
  3: Present challenge with data
  4: Suggest safe alternative
  5: Require override or alternative
```

---

## Automation Rules

### 15. **Rule #16: Automatic Brain Updates**
```yaml
rule_id: AUTO_BRAIN_UPDATE
severity: HIGH

triggers:
  event_threshold:
    - 50+ unprocessed events
    - Automatic update triggered
    
  time_threshold:
    - 24 hours since last update
    - 10+ events exist
    - Automatic update triggered
    
  session_complete:
    - All tasks in session done
    - Automatic update triggered

process:
  1: Collect events
  2: Extract patterns
  3: Update knowledge graph
  4: Update development context (if >1hr since last)
  5: Log completion
```

---

### 16. **Rule #17: Conversation Auto-Recording**
```yaml
rule_id: AUTO_CONVERSATION_RECORDING
severity: HIGH

layers:
  layer_1_copilot:
    - Import from GitHub Copilot Chat
    - Automatic parse and store
    
  layer_2_sessions:
    - Extract from session completion
    - Automatic on session end
    
  layer_3_manual:
    - record-conversation.ps1
    - For critical conversations

target: 71%+ auto-recording rate
```

---

### 17. **Rule #15: Git Commit Automation**
```yaml
rule_id: AUTO_GIT_COMMIT
severity: MEDIUM

triggers:
  - Task completion
  - DoD validated
  - Tests passing
  - Zero errors/warnings

commit_message_format:
  type: feat|fix|test|docs|refactor|style|chore
  scope: component name
  subject: Brief description
  body: Details, test status, known issues
  
enforcement: commit-handler.md agent
```

---

## Data Management Rules

### 18. **Rule #10: Tier Boundary Enforcement**
```yaml
rule_id: TIER_BOUNDARIES
severity: CRITICAL

tier_0_instinct:
  content: Governance rules, core principles
  forbidden: Application data, file paths
  
tier_1_working_memory:
  content: Last 20 conversations
  forbidden: Long-term patterns, git metrics
  
tier_2_knowledge_graph:
  content: Consolidated patterns
  forbidden: Conversation details, raw events
  
tier_3_context:
  content: Git/test/build metrics
  forbidden: Conversation data, governance rules

violations:
  auto_migrate: YES (move to correct tier)
  warn: YES (log violation)
  challenge: YES (if user-initiated)
```

---

### 19. **Rule #11: FIFO Queue Management (Tier 1)**
```yaml
rule_id: FIFO_CONVERSATION_QUEUE
severity: HIGH

capacity: 20 conversations
eviction_strategy: FIFO (oldest deleted)
protection: Active conversation never deleted

process:
  on_21st_conversation:
    1: Identify oldest non-active conversation
    2: Extract patterns to Tier 2
    3: Delete conversation from Tier 1
    4: Log deletion event
```

---

### 20. **Rule #12: Pattern Confidence Decay**
```yaml
rule_id: PATTERN_CONFIDENCE_DECAY
severity: MEDIUM

decay_logic:
  unused_60_days:
    - Reduce confidence by 10%
    
  unused_90_days:
    - Reduce confidence by 25%
    
  unused_120_days:
    - Mark for consolidation or deletion
    
  confidence_below_30:
    - Auto-delete pattern

exceptions:
  - Tier 0 rules (never decay)
  - Explicitly pinned patterns
```

---

### 21. **Rule #13: Anomaly Detection**
```yaml
rule_id: ANOMALY_DETECTION
severity: HIGH

anomalies_tracked:
  - Tier boundary violations
  - SOLID violations
  - TDD bypasses
  - Incorrect file modifications
  - Protection challenges issued

storage: kds-brain/anomalies.yaml
review_frequency: Weekly
action_threshold: 5+ similar anomalies
```

---

### 22. **Rule #14: Development Context Throttling**
```yaml
rule_id: DEV_CONTEXT_THROTTLING
severity: MEDIUM

collection_frequency:
  minimum_interval: 1 hour
  rationale: Git metrics don't change every 50 events
  
optimization:
  - Delta updates only
  - Not full re-scan
  - Efficiency over freshness
  
override: Manual trigger allowed
```

---

## Limits & Constraints

### 23. **Rule #24: System Limits**
```yaml
rule_id: SYSTEM_LIMITS
severity: MEDIUM

governance:
  soft_limit: 15 rules
  hard_limit: 20 rules
  current: 22 rules ⚠️ (approaching limit)
  
agents:
  soft_limit: 10 agents
  hard_limit: 15 agents
  current: 10 agents ✅
  
brain_storage:
  target: <500KB total
  tier_1: <200KB
  tier_2: <150KB
  tier_3: <100KB

actions_on_limits:
  approaching_soft: WARN, suggest consolidation
  at_hard: HALT, require consolidation
```

---

## Migration to CORTEX

### Changes for Tier 0 in CORTEX

1. **Rename References:**
   - KDS → CORTEX
   - kds-brain → cortex-brain
   - prompts/user/kds.md → cortex-agents/user/cortex.md

2. **Simplify Tiers:**
   - Remove Tier 4 (Events) → Merge into Tier 2 processing
   - Remove Tier 5 (Health) → Built into each tier
   - Keep Tier 0-3 as core

3. **Storage Updates:**
   - YAML → SQLite for Tier 1 & 2
   - Keep YAML for Tier 0 (human-readable governance)
   - JSON cache for Tier 3

4. **Rule Consolidation:**
   - 22 rules → Target 18 rules (within soft limit)
   - Merge similar rules
   - Simplify enforcement

---

## Files to Preserve

```
governance/
├── rules.md (2,807 lines) ✅ CRITICAL
├── rules/
│   ├── challenge-user-changes.md ✅
│   ├── checkpoint-strategy.md ✅
│   ├── definition-of-done.md ✅
│   ├── definition-of-ready.md ✅
│   └── [other rule files]
└── challenges.jsonl (protection challenge log)
```

---

## Test Requirements

**Tier 0 must have tests for:**
1. Rule enforcement (challenge triggers work)
2. TDD validation (RED → GREEN → REFACTOR detected)
3. DoR/DoD gates (block when not met)
4. Tier boundary protection (auto-migrate violations)
5. SOLID compliance checks (detect violations)
6. Brain protection (instinct immutability)

**Test Files:**
- `cortex-tests/unit/tier0-instinct-tests.ps1`
- `cortex-tests/unit/tier0-tdd-enforcement-tests.ps1`
- `cortex-tests/unit/tier0-protection-tests.ps1`

---

## Success Criteria

**Tier 0 complete when:**
- ✅ All 22 rules migrated to CORTEX governance
- ✅ Rule files converted to CORTEX naming
- ✅ All tests passing (15/15 unit tests)
- ✅ Challenge protocols working
- ✅ TDD enforcement active
- ✅ DoR/DoD gates functional
- ✅ Documentation complete

---

**Status:** Feature inventory complete  
**Next:** Tier 1 (Working Memory) feature extraction
