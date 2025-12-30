# 🏗️ CORTEX Architecture Overview

**Version:** 4.0.0  
**Author:** Asif Hussain  
**Purpose:** Comprehensive architectural reference for onboarding

---

## 🧠 The 4-Tier Brain System

CORTEX implements a hierarchical memory architecture inspired by human cognition:

```
cortex-brain/
├── tier0/  🏛️ GOVERNANCE         # Rules, schemas, manifests
├── tier1/  🧠 WORKING MEMORY     # Active conversations, operations
├── tier2/  📚 KNOWLEDGE GRAPH    # Long-term patterns, lessons
└── tier3/  🔧 DEV CONTEXT        # Project-specific memory
```

---

## Tier 0: Governance Layer

**Purpose:** System rules, policies, and operation definitions

**Key Components:**

### Brain Protection Rules (SKULL)
- File: `cortex-brain/brain-protection-rules.yaml`
- Enforces: TDD, holistic discovery, refactor cleanup, git isolation

### Operation Manifests
- Location: `cortex-brain/manifests/orchestrators/`
- Defines: All orchestrator behaviors, phases, outputs
- Examples: `planning-system-4.0-manifest.yaml`, `tdd-orchestrator-v4-manifest.yaml`

### Response Templates
- File: `cortex-brain/response-templates-v4.yaml`
- Adaptive tiers: INSTANT, FOCUSED, STRUCTURED, COMPREHENSIVE
- Token optimization: 95% reduction in status-only responses

### Schemas
- SQL: `cortex-brain/schema.sql` (conversation tracking)
- Compliance: `cortex-brain/compliance-tracking-schema.sql`

---

## Tier 1: Working Memory

**Purpose:** Short-term operational context (current session)

**Key Components:**

### Conversation Context
- File: `cortex-brain/conversation-context.jsonl`
- Tracks: User intents, operation chains, session metadata

### Active Operations
- Location: `cortex-brain/documents/planning/active/`
- Contains: In-progress plans, progress trackers

### Temporary Artifacts
- Cache: `cortex-brain/cache/`
- Exports: `cortex-brain/exports/`

---

## Tier 2: Knowledge Graph

**Purpose:** Long-term learned patterns and relationships

**Key Components:**

### Lessons Learned
- File: `cortex-brain/lessons-learned.yaml`
- Contains: Successful patterns, anti-patterns, best practices

### File Relationships
- File: `cortex-brain/file-relationships.yaml`
- Maps: Dependencies, impacts, coupling metrics

### Module Definitions
- File: `cortex-brain/module-definitions.yaml`
- Defines: Logical boundaries, responsibilities

---

## Tier 3: Development Context

**Purpose:** Project-specific memory and history

**Key Components:**

### Development Context
- File: `cortex-brain/development-context.yaml`
- Tracks: Project decisions, technology choices, constraints

### Git Checkpoint Rules
- File: `cortex-brain/git-checkpoint-rules.yaml`
- Defines: When to create checkpoints, commit message patterns

---

## 🎯 Intent Routing System

### Entry Point: CORTEX.prompt.md

**Flow:**
```
User Request
    ↓
Meta-directive Removal
    ↓
Intent Classification
    ↓
Orchestrator Selection
    ↓
Execution
    ↓
Response Formatting
```

### Supported Intents

| Intent | Orchestrator | Manifest |
|--------|--------------|----------|
| `plan` | Planning System | `planning-system-4.0-manifest.yaml` |
| `tdd` | TDD Mastery | `tdd-orchestrator-v4-manifest.yaml` |
| `maintenance` | System Maintenance | Via `cortex-maintenance.prompt.md` |
| `sanitize` | Code Sanitization | `code-sanitization-manifest.yaml` |
| `refine` | Refinement | `refinement-orchestrator-manifest.yaml` |
| `ado` | ADO Operations | `ado-planning-manifest.yaml` |

---

## 🔧 Orchestrator Architecture

### What is an Orchestrator?

An orchestrator is a workflow engine that coordinates multiple operations to achieve a complex goal.

### Core Orchestrators (8 Total)

1. **Planning System** - Creates structured plans with folder scaffolding
2. **TDD Mastery** - Enforces RED→GREEN→REFACTOR workflow
3. **Maintenance** - 6-phase system health pipeline
4. **Sanitization** - Removes company-specific data
5. **Refinement** - 7-phase improvement pipeline
6. **ADO Operations** - Azure DevOps work item management
7. **Contextual Review** - Code review with context awareness
8. **Git Operations** - Checkpoint management, branch operations

### Orchestrator Structure

Each orchestrator has:
- **Manifest:** YAML file defining phases, inputs, outputs
- **Implementation:** Python class in `src/orchestrators/`
- **Prompt:** Optional `.prompt.md` in `.github/prompts/`
- **Tests:** Unit tests in `tests/orchestrators/`

---

## 🛠️ Implementation Architecture

### Directory Structure

```
src/
├── cortex_agents/           # 2 specialist agents
│   ├── planning_agent.py    # Plan generation
│   └── review_agent.py      # Code review
├── orchestrators/           # 8 workflow engines
│   ├── planning/
│   ├── tdd/
│   ├── maintenance/
│   └── ...
├── response_templates/      # Template rendering
└── tier0-3/                 # Brain tier implementations
```

### Key Modules

**Planning Orchestrator:**
- File: `src/orchestrators/planning/planning_orchestrator.py`
- Uses: Toolkit `plan_scaffold_generator.py`
- Output: 4-folder structure + master plan

**TDD Orchestrator:**
- File: `src/orchestrators/tdd/tdd_orchestrator.py`
- Phases: RED → GREEN → REFACTOR
- Enforcement: SKULL rule `TDD_ENFORCEMENT`

**Maintenance Orchestrator:**
- File: `src/orchestrators/maintenance/maintenance_orchestrator.py`
- Phases: Discover → Validate → Plan → Implement → Test → Document
- Output: Health reports in `cortex-brain/health-reports/`

---

## 🔄 Data Flow

### Planning Operation Example

```
1. User: "plan user authentication"
   ↓
2. CORTEX.prompt.md parses intent
   ↓
3. Routes to Planning Orchestrator
   ↓
4. Orchestrator calls plan_scaffold_generator.py
   ↓
5. Creates folder structure:
   planning/active/user-authentication/
   ├── 00-master-plan.md
   ├── context/
   ├── reports/
   ├── artifacts/
   └── tracking/progress-tracker.json
   ↓
6. Returns formatted response (COMPREHENSIVE tier)
```

### TDD Operation Example

```
1. User: "start tdd"
   ↓
2. TDD Orchestrator activates
   ↓
3. RED Phase: "Write failing test"
   ↓
4. User writes test → runs → fails
   ↓
5. GREEN Phase: "Implement minimal code"
   ↓
6. User implements → runs → passes
   ↓
7. REFACTOR Phase: "Improve quality"
   ↓
8. User refactors → runs → still passes
   ↓
9. Git checkpoint created
```

---

## 📦 Toolkit Integration

### What is cortex-toolkit?

The toolkit provides reusable utilities for CORTEX operations:

```
cortex-toolkit/
├── core/
│   ├── utilities/
│   │   └── plan_scaffold_generator.py  # Folder structure creation
│   └── validation/
│       └── plan_validator.py           # DoR/DoD validation
├── documentation/
│   └── regenerate_prompts.py           # Prompt file generation
└── operations/
    └── git_checkpoint_manager.py       # Git operations
```

### Key Utilities

**plan_scaffold_generator.py:**
- Creates canonical 4-folder structure
- Generates progress-tracker.json
- Initializes master plan template

**plan_validator.py:**
- Validates Definition of Ready (DoR)
- Checks Definition of Done (DoD)
- Reports compliance gaps

**git_checkpoint_manager.py:**
- Creates git checkpoints during TDD
- Enforces checkpoint rules from Tier 0
- Manages branch operations

---

## 🔐 Security & Isolation

### Git Isolation Principle

**SKULL Rule:** CORTEX code never commits to user repos

**Implementation:**
- CORTEX brain: `cortex-brain/` (separate git history)
- User projects: Isolated in their own repos
- No cross-contamination

### Data Privacy

**Sanitization:**
- Removes company names, API keys, personal data
- Uses regex patterns and NLP detection
- Configurable rules in `cortex-brain/cleanup-rules.yaml`

---

## 🚀 Performance Optimization

### Token Optimization (v4.0)

**Status-Only Responses:** 95% reduction
- Before: 8000 tokens
- After: 400 tokens
- Method: Hierarchical loading pattern

**Master Hub:** 85% reduction
- Before: 8000 tokens
- After: 1200 tokens
- Method: Section-based loading

**Phase-Specific:** 70% reduction
- Before: 8000 tokens
- After: 2500 tokens
- Method: Targeted context loading

### Smart Plan Loader

File: `src/utils/smart_plan_loader.py`

**Capabilities:**
- Load only required sections
- Hierarchical context building
- Token budget awareness

---

## 📊 Monitoring & Analytics

### Health Reports

Location: `cortex-brain/health-reports/`

**Metrics Tracked:**
- File counts by category
- Test coverage percentage
- Documentation completeness
- SKULL compliance rate

### Conversation Analytics

Location: `cortex-brain/analytics/`

**Tracked:**
- Intent frequencies
- Operation success rates
- Token usage patterns
- Error occurrences

---

## 🔧 Extension Points

### Adding New Orchestrators

1. Create manifest in `cortex-brain/manifests/orchestrators/`
2. Implement in `src/orchestrators/{name}/`
3. Add route in `CORTEX.prompt.md`
4. Write tests in `tests/orchestrators/{name}/`
5. Update documentation

### Adding New Agents

1. Create agent in `src/cortex_agents/{name}_agent.py`
2. Define capabilities in `cortex-brain/capabilities.yaml`
3. Register in orchestrator manifest
4. Write integration tests

---

## 📚 Related Documents

- **Intent Router:** `.github/prompts/CORTEX.prompt.md`
- **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Response Templates:** `cortex-brain/response-templates-v4.yaml`
- **Orchestrator Manifests:** `cortex-brain/manifests/orchestrators/`
- **Toolkit Docs:** `cortex-toolkit/README.md`

---

**Copyright © 2025 Asif Hussain. All rights reserved.**
