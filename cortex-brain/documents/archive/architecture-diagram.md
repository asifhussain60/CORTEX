# 🏗️ CORTEX Architecture Diagram

**Version:** 4.0.0  
**Created:** 2025-12-29  
**Author:** Asif Hussain

---

## 🧠 4-Tier Brain Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CORTEX ARCHITECTURE                         │
│                         (4-Tier Brain System)                       │
└─────────────────────────────────────────────────────────────────────┘

                              👤 USER
                                │
                                ├─ GitHub Copilot Chat
                                ├─ CLI Wrappers
                                └─ Interactive Sessions
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    🎯 ENTRY POINT LAYER                             │
├─────────────────────────────────────────────────────────────────────┤
│  .github/prompts/CORTEX.prompt.md                                   │
│  ├─ Intent Router (parse user request)                             │
│  ├─ Natural Language Patterns                                      │
│  └─ Operation Routing                                              │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    🎭 ORCHESTRATOR LAYER                            │
├─────────────────────────────────────────────────────────────────────┤
│  8 Specialist Orchestrators:                                        │
│  ├─ Planning System (plan creation)                                │
│  ├─ TDD Orchestrator (test-driven development)                     │
│  ├─ Refinement (7-phase improvement)                               │
│  ├─ Sanitization (code genericization)                             │
│  ├─ Maintenance (6-phase health check)                             │
│  ├─ ADO Operations (Azure DevOps integration)                      │
│  ├─ Debug Orchestrator (issue resolution)                          │
│  └─ Onboarding (user guidance)                                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    🧠 4-TIER BRAIN SYSTEM                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐    │
│  │ TIER 0: GOVERNANCE (cortex-brain/tier0/)                  │    │
│  ├───────────────────────────────────────────────────────────┤    │
│  │ • Brain protection rules (SKULL)                          │    │
│  │ • Orchestrator manifests                                  │    │
│  │ • Response templates v4.0                                 │    │
│  │ • Configuration & schemas                                 │    │
│  └───────────────────────────────────────────────────────────┘    │
│                             │                                       │
│                             ▼                                       │
│  ┌───────────────────────────────────────────────────────────┐    │
│  │ TIER 1: WORKING MEMORY (cortex-brain/tier1/)              │    │
│  ├───────────────────────────────────────────────────────────┤    │
│  │ • Conversation context (SQLite DB)                        │    │
│  │ • Session tracking                                        │    │
│  │ • Progress state management                               │    │
│  │ • User profile & preferences                              │    │
│  └───────────────────────────────────────────────────────────┘    │
│                             │                                       │
│                             ▼                                       │
│  ┌───────────────────────────────────────────────────────────┐    │
│  │ TIER 2: KNOWLEDGE GRAPH (cortex-brain/tier2/)             │    │
│  ├───────────────────────────────────────────────────────────┤    │
│  │ • File relationships (YAML)                               │    │
│  │ • Lessons learned                                         │    │
│  │ • Pattern recognition                                     │    │
│  │ • Cross-operation insights                                │    │
│  └───────────────────────────────────────────────────────────┘    │
│                             │                                       │
│                             ▼                                       │
│  ┌───────────────────────────────────────────────────────────┐    │
│  │ TIER 3: DEVELOPMENT CONTEXT (cortex-brain/tier3/)         │    │
│  ├───────────────────────────────────────────────────────────┤    │
│  │ • Project-specific memory                                 │    │
│  │ • Codebase analysis cache                                 │    │
│  │ • Tech stack context                                      │    │
│  │ • Team conventions                                        │    │
│  └───────────────────────────────────────────────────────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    🛡️ SKULL PROTECTION LAYER                       │
├─────────────────────────────────────────────────────────────────────┤
│  S - TDD Enforcement (RED→GREEN→REFACTOR)                          │
│  K - Holistic Discovery (search before create)                     │
│  U - Refactor Cleanup (remove orphaned code)                       │
│  L - Git Isolation (CORTEX ≠ user repos)                           │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                          📁 OUTPUT
                   (Plans, Tests, Reports, Artifacts)
```

---

## 🔄 Request Flow Example

**User Request:** `plan "user authentication feature"`

```
1. User Input
   └─> GitHub Copilot Chat

2. Intent Router
   └─> CORTEX.prompt.md parses request
   └─> Matches "plan" pattern
   └─> Routes to Planning System

3. Orchestrator Activation
   └─> Planning Orchestrator loads
   └─> Reads manifest: planning-system-4.0-manifest.yaml
   └─> Checks SKULL rules

4. Brain Access
   ├─> Tier 0: Load response templates
   ├─> Tier 1: Create session record
   ├─> Tier 2: Check for similar plans
   └─> Tier 3: Load project context

5. Execution
   └─> Generate plan structure
   └─> Create folder: planning/active/user-authentication-feature/
   └─> Write master plan, context files, tracker
   └─> Record to knowledge graph

6. Output
   └─> Return formatted response
   └─> User sees plan created confirmation
```

---

## 🎯 Component Interactions

### Planning System Flow
```
User Request → Intent Router → Planning Orchestrator
                                      │
                ┌─────────────────────┼─────────────────────┐
                ▼                     ▼                     ▼
         Toolkit Generator     Brain Access         SKULL Validation
         (plan scaffold)       (context/state)      (TDD/discovery)
                │                     │                     │
                └─────────────────────┴─────────────────────┘
                                      │
                                      ▼
                            Plan Folder Structure
                            + Progress Tracker
```

### TDD Workflow Flow
```
"start tdd" → TDD Orchestrator → RED Phase (write failing test)
                    │
                    ├─> SKULL: Verify test fails
                    │
                    ▼
              GREEN Phase (minimal implementation)
                    │
                    ├─> SKULL: Verify test passes
                    │
                    ▼
              REFACTOR Phase (improve code)
                    │
                    ├─> SKULL: Verify tests still pass
                    ├─> Create git checkpoint
                    │
                    ▼
              Complete (record to knowledge graph)
```

---

## 📊 Data Flow

```
┌─────────────┐
│  User Input │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Intent Router      │ ← Tier 0: Response templates
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Orchestrator       │ ← Tier 0: Manifest
└──────┬──────────────┘   Tier 1: Session state
       │                  Tier 2: Knowledge graph
       │                  Tier 3: Project context
       ▼
┌─────────────────────┐
│  SKULL Validation   │ ← Tier 0: Protection rules
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Execution          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Output Generation  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  User Response      │
└─────────────────────┘
```

---

## 🧩 Key Design Principles

### 1. Separation of Concerns
- **Entry Point:** Request parsing & routing
- **Orchestrators:** Workflow coordination
- **Brain:** State & knowledge management
- **SKULL:** Safety & quality enforcement

### 2. Manifest-Driven Configuration
Every orchestrator has a YAML manifest defining:
- Requirements (files, methods, integrations)
- Quality gates (DoR/DoD, validation)
- Workflows (phases, steps, checkpoints)

### 3. Lazy Loading & Caching
- Brain tiers loaded on-demand
- Manifests cached after first read
- Knowledge graph indexed for fast lookup

### 4. Token Optimization
- Response templates adapt to complexity
- 4 tiers: INSTANT → FOCUSED → STRUCTURED → COMPREHENSIVE
- Minimize redundancy through inheritance

### 5. Multi-Agent Coordination
- Orchestrators can invoke other orchestrators
- Example: Planning → TDD → Git Checkpoint
- State passed through Tier 1 session tracking

---

## 📐 Folder Structure

```
CORTEX/
├── .github/prompts/           # Entry points & routing
│   ├── CORTEX.prompt.md       # Main router
│   └── modules/               # Operation-specific prompts
│
├── src/
│   ├── orchestrators/         # 8 specialist orchestrators
│   ├── operations/            # CLI operation modules
│   └── utils/                 # Shared utilities
│
├── cortex-brain/
│   ├── tier0/                 # Governance
│   ├── tier1/                 # Working memory (SQLite)
│   ├── tier2/                 # Knowledge graph (YAML)
│   ├── tier3/                 # Development context
│   └── manifests/             # Orchestrator manifests
│
├── cortex-toolkit/            # Utility scripts
│   └── core/
│       ├── generators/        # Scaffold generators
│       └── utilities/         # Helper tools
│
└── scripts/
    └── cli_wrappers/          # CLI operation wrappers
```

---

## 🚀 Extension Points

### Adding New Orchestrator

1. Create orchestrator: `src/orchestrators/my_orchestrator.py`
2. Create manifest: `cortex-brain/manifests/orchestrators/my-orchestrator-manifest.yaml`
3. Add routing: Update `CORTEX.prompt.md` intent router
4. Register operation: Add to `cortex-operations.yaml`
5. Create CLI wrapper: `scripts/cli_wrappers/my_wrapper.py`

### Adding New Operation

1. Define in `cortex-operations.yaml`
2. Add natural language triggers
3. Create CLI wrapper or use Copilot Chat
4. Update help command

---

## 📚 Related Documentation

- **Brain Architecture:** `cortex-brain/documents/architecture/4-tier-brain.md`
- **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Response Templates:** `cortex-brain/response-templates-v4.yaml`
- **Orchestrator Manifests:** `cortex-brain/manifests/orchestrators/README.md`

---

**Diagram Version:** 1.0.0  
**Last Updated:** 2025-12-29  
**Maintainer:** Asif Hussain
