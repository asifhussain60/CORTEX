# CORTEX Current Architecture Baseline

**Created:** January 2, 2026  
**Phase:** 0 - Foundation Setup (Task 0.3)  
**Purpose:** Document current system state before v5 transformation

---

## System Overview

CORTEX v4.0 is a multi-tier AI assistant with long-term memory, orchestrated workflows, and specialized agents. Current architecture shows **hybrid control flow** where execution logic is split between Python code and natural language manifests.

### Core Statistics

- **Total Orchestrators:** 12 active
- **Specialized Agents:** 20+
- **Brain Tiers:** 4 (Governance, Working Memory, Knowledge Graph, Dev Context)
- **Primary Language:** Python 3.13
- **State Management:** File-based (YAML, JSON, JSONL)
- **Architecture Pattern:** Hybrid (Python + Manifest instructions)

---

## Directory Structure

```
CORTEX/
├── src/
│   ├── orchestrators/           # 12 orchestrator implementations
│   ├── cortex_agents/           # 20+ specialized agents
│   ├── operations/              # Utility operations
│   ├── tier0-tier3/             # Brain tier implementations
│   └── response_templates/      # Template rendering
│
├── cortex-brain/
│   ├── tier0/ (Governance)      # Rules, policies, checkpoints
│   ├── tier1/ (Working)         # Active planning, tracking
│   ├── tier2/ (Knowledge)       # Long-term learning
│   ├── tier3/ (Dev Context)     # Technical context
│   ├── manifests/               # Orchestrator configurations
│   ├── documents/               # Organized artifacts
│   └── response-templates-v4.yaml
│
├── tests/                       # Test suite (pytest)
├── .github/prompts/             # CORTEX.prompt.md entry point
└── docs/                        # Documentation site
```

---

## Orchestrator Inventory

### 🛡️ AUTONOMOUS Orchestrators (4)

These orchestrators are **supposed** to execute autonomously but currently have hybrid control:

| Orchestrator | File | Type | Current Issues |
|--------------|------|------|----------------|
| **Planning System** | `planning_orchestrator.py` | Autonomous | Manual intervention needed, no state recovery |
| **ADO Operations** | (scattered) | Autonomous | No dedicated orchestrator, logic embedded in agents |
| **Vacuum** | (prompt-based) | Autonomous | Defined in prompt file, no Python implementation |
| **Cleanup** | (maintenance phase) | Autonomous | Part of maintenance, not standalone |

**Problem:** These orchestrators claim autonomy but execution flows through CORTEX tool calls rather than pure Python logic.

### 📋 GUIDED Orchestrators (8)

These orchestrators are **intentionally guided** by CORTEX:

| Orchestrator | File | Purpose | Manifest Dependency |
|--------------|------|---------|---------------------|
| **Upgrade** | `upgrade_orchestrator_v2.py` | System upgrades | `BaseOrchestrator` pattern |
| **Git Checkpoint** | `git_checkpoint_orchestrator.py` | Version control | Manual checkpoints |
| **Git Sync** | `git_sync_and_optimize.py` | Repository sync | Tool-call driven |
| **Rollback** | `rollback_orchestrator.py` | Phase rollback | Session state dependent |
| **Onboarding** | `onboarding_acknowledgment_orchestrator.py` | User onboarding | Interactive prompts |
| **Setup** | `master_setup_orchestrator.py` | System setup | Configuration wizard |
| **Alignment** | `alignment_orchestrator.py` | Response alignment | Template-driven |
| **Health** | `application_health_orchestrator.py` | Health checks | Diagnostic scripts |

**Status:** These work as intended but could benefit from consistent base class patterns.

---

## Agent Inventory

### Core Agents (Tier 1)

| Agent | File | Purpose | Configuration Source |
|-------|------|---------|---------------------|
| **IntentRouter** | `intent_router.py` | Route user commands | Hardcoded patterns |
| **LLMIntentClassifier** | `llm_intent_classifier.py` | AI-powered intent classification | Inline prompts |
| **InvestigationRouter** | `investigation_router.py` | Deep investigation routing | Pattern matching |
| **WelcomeBanner** | `welcome_banner_agent.py` | User greeting | ASCII art strings |

### Specialized Agents (Tier 2-3)

| Agent | File | Purpose | Dependencies |
|-------|------|---------|--------------|
| **ADO Agent** | `ado_agent.py` | Azure DevOps integration | ADO API credentials |
| **Learning Capture** | `learning_capture_agent.py` | Conversation capture | File system |
| **Session Resumer** | `session_resumer.py` | Restore sessions | JSONL logs |
| **Profile Agent** | `profile_agent.py` | User profiling | User dictionary |
| **Screenshot Analyzer** | `screenshot_analyzer.py` | Image analysis | Vision API |
| **Security Scanner** | `security_scanner_agent.py` | Security checks | Validation rules |
| **RCA Agent** | `rca_agent.py` | Root cause analysis | Investigation patterns |
| **Supply Chain** | `supply_chain_security.py` | Dependency scanning | Package manifests |
| **Incident Response** | `incident_response_automation.py` | Auto-remediation | Runbooks |

**Total:** 20+ agents with varying configuration approaches

---

## State Management Approaches

### Current Methods (Fragmented)

| Component | State Storage | Recovery Capability |
|-----------|---------------|---------------------|
| **Planning** | `progress-tracker.json` | ❌ No automatic recovery |
| **Checkpoints** | Git tags + YAML | ✅ Manual recovery |
| **Sessions** | JSONL files | ✅ Session resumer agent |
| **Conversations** | JSONL append-only | ✅ Full history |
| **Brain Tiers** | YAML files | ❌ No transactional updates |
| **Orchestrators** | In-memory | ❌ Lost on failure |

**Problem:** No centralized state management with ACID guarantees.

---

## Configuration Sources

### Manifest Files

```
cortex-brain/manifests/orchestrators/
├── planning-system-4.0-manifest.yaml      # Planning config + instructions
├── ado-planning-manifest.yaml             # ADO work item generation
├── tdd-orchestrator-v4-manifest.yaml      # TDD workflow
├── debug-orchestrator-manifest.yaml       # Debug procedures
├── code-sanitization-manifest.yaml        # Sanitization rules
├── refinement-orchestrator-manifest.yaml  # Improvement phases
└── cortex-lens-v3-manifest.yaml          # Dashboard specs
```

**Issue:** Manifests contain **both** configuration data AND natural language instructions for CORTEX to follow.

### Prompt Files

```
.github/prompts/
├── CORTEX.prompt.md                # Main entry point
├── cortex-maintenance.prompt.md    # 11-phase maintenance
├── cortex-vacuum.prompt.md         # Deep cleanup
├── cortex-refactor.prompt.md       # Refactoring guide
└── cortex-backlog.prompt.md        # Backlog management
```

**Issue:** Execution logic embedded in markdown files rather than Python code.

---

## Execution Flow (Current)

### AUTONOMOUS Orchestrators (Supposed)

```
User Command 
  → CORTEX.prompt.md (Intent Router)
  → Load manifest
  → CORTEX reads natural language instructions
  → CORTEX executes via tool calls
  → Manual coordination required
```

**Problem:** CORTEX acts as interpreter, not orchestrator owner.

### GUIDED Orchestrators (Actual)

```
User Command
  → CORTEX.prompt.md (Intent Router)
  → Load Python orchestrator
  → CORTEX calls orchestrator methods
  → Orchestrator returns results
  → CORTEX formats response
```

**Works better** but lacks consistent base class patterns.

---

## Identified Brittleness

### Critical Issues

1. **Hybrid Control Ambiguity**
   - AUTONOMOUS orchestrators require CORTEX intervention
   - Execution logic split between Python and manifests
   - No clear ownership of workflow steps

2. **No State Recovery**
   - Planning workflows fail midstream without recovery
   - No transaction boundaries
   - Manual intervention required to resume

3. **Fragmented Configuration**
   - Manifests mix data and instructions
   - No schema validation
   - Hard to parse programmatically

4. **Inconsistent Base Classes**
   - Some orchestrators extend `BaseOrchestrator`
   - Others are standalone classes
   - No shared patterns for common operations

5. **File-Based State**
   - JSON/YAML files lack ACID properties
   - Concurrent access issues
   - No query capabilities

6. **No Universal Invocation**
   - Each orchestrator has unique calling pattern
   - Intent router uses hardcoded string matching
   - No standardized protocol

---

## Dependency Map

### Orchestrators → Agents

```
PlanningOrchestrator
  ├─ Uses: FileSystem utilities
  ├─ Calls: Template renderer
  └─ Depends: progress-tracker.json format

UpgradeOrchestratorV2
  ├─ Extends: BaseOrchestrator
  ├─ Uses: Git utilities
  └─ Depends: Session state

GitCheckpointOrchestrator
  ├─ Uses: Git commands
  └─ Depends: Checkpoint rules (tier0)

RollbackOrchestrator
  ├─ Uses: PhaseCheckpointManager
  └─ Depends: Session model
```

### Agents → Brain Tiers

```
IntentRouter
  ├─ Reads: CORTEX.prompt.md (hardcoded path)
  └─ Uses: Pattern matching (no ML)

LearningCaptureAgent
  ├─ Writes: conversation-context.jsonl
  └─ Depends: Filesystem access

SessionResumer
  ├─ Reads: JSONL session logs
  └─ Reconstructs: In-memory state
```

---

## Testing Coverage

### Current State

- **Unit Tests:** ~60% coverage
- **Integration Tests:** Minimal
- **End-to-End Tests:** None for orchestrators
- **Test Organization:** Scattered across `tests/`

### Missing Tests

- Orchestrator state recovery
- Concurrent planning workflows
- Manifest schema validation
- Agent error handling
- Transaction rollback scenarios

---

## Performance Characteristics

### Bottlenecks

1. **File I/O:** Heavy YAML/JSON parsing
2. **Intent Classification:** Linear pattern matching
3. **Planning:** Manual context gathering
4. **State Queries:** Full file reads

### Response Times

| Operation | Current | Target (v5) |
|-----------|---------|-------------|
| Intent Routing | ~100ms | <50ms |
| Plan Generation | ~30s (manual) | <10s (automated) |
| State Query | ~500ms | <100ms |
| Orchestrator Invoke | Varies | <1s |

---

## Migration Readiness

### Components Ready for v5

✅ **Response Templates:** Well-structured YAML  
✅ **Brain Tier Structure:** Good organization  
✅ **Test Framework:** Pytest infrastructure exists  
✅ **Documentation:** Comprehensive but needs updates

### Components Requiring Transformation

❌ **Orchestrators:** Need pure Python implementations  
❌ **Manifests:** Need config-only format  
❌ **State Management:** Need SQLite database  
❌ **Invocation Protocol:** Need MCP layer  
❌ **Base Classes:** Need v4.1 patterns

---

## Lessons from Current Architecture

### What Works Well

1. **Brain Tier Organization:** Logical separation of concerns
2. **Document Structure:** Category-based organization prevents root clutter
3. **Response Templates:** Consistent formatting across operations
4. **Agent Specialization:** Clear responsibilities per agent

### What Needs Improvement

1. **Execution Clarity:** Who owns workflow steps?
2. **State Persistence:** Need ACID guarantees
3. **Configuration Parsing:** Need programmatic access
4. **Failure Recovery:** Need automatic resumption
5. **Testing:** Need comprehensive coverage
6. **Invocation:** Need universal protocol

---

## Comparison: v4.0 vs. v5.0 (Target)

| Aspect | v4.0 (Current) | v5.0 (Target) |
|--------|----------------|---------------|
| **Control Flow** | Hybrid (Python + Manifests) | Pure Python |
| **State** | File-based (JSON/YAML) | SQLite with ACID |
| **Manifests** | Config + Instructions | Config only |
| **Invocation** | Varied patterns | MCP protocol |
| **Recovery** | Manual intervention | Automatic from snapshots |
| **Base Class** | Inconsistent | BaseOrchestrator v4.1 |
| **Templates** | String-based | Jinja2 with injection |
| **Testing** | ~60% coverage | 100% required |

---

**Status:** ✅ Task 0.3 Complete - Baseline architecture documented  
**Next:** Complete Phase 0 and prepare git checkpoint
