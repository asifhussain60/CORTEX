# CORTEX Capability Domains
# The six cognitive domains and their relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CORTEX CAPABILITY MAP                              │
│                                                                             │
│  ┌─────────────────────┐      ┌─────────────────────┐                       │
│  │   CORE PLATFORM     │      │   EXTENSIBILITY      │                      │
│  │                     │      │                      │                      │
│  │  • MCP Gateway      │      │  • Custom MCP tools  │                      │
│  │  • 51-orchestrator  │◄────►│  • Domain orchestrs  │                      │
│  │    dispatch          │      │  • Workflow templates│                      │
│  │  • State management │      │  • Enterprise patns  │                      │
│  │  • Health monitor   │      │  • WorkItemProvider  │                      │
│  │                     │      │  • Hot-reload        │                      │
│  └────────┬────────────┘      └──────────────────────┘                      │
│           │                                                                 │
│           │ routes requests                                                 │
│           ▼                                                                 │
│  ┌─────────────────────┐      ┌─────────────────────┐                       │
│  │   INTELLIGENCE      │      │   BRAIN              │                      │
│  │   (LENS)            │      │   (P → R → A)        │                      │
│  │                     │      │                      │                      │
│  │  • 10 analyzers     │─────►│  • Perception        │                      │
│  │  • AST, Git, Sec.   │ feeds│  • Reasoning         │                      │
│  │  • 300–800ms        │      │  • Action            │                      │
│  │  • Confidence 0–1   │      │  • URS learning      │                      │
│  │                     │      │  • 9 patterns        │                      │
│  └─────────────────────┘      └────────┬────────────┘                      │
│                                        │                                    │
│                                        │ informs                            │
│                                        ▼                                    │
│  ┌─────────────────────┐      ┌─────────────────────┐                       │
│  │   GOVERNANCE        │      │   DECISIONING        │                      │
│  │                     │      │                      │                      │
│  │  • CORE rules      │◄────►│  • IntentRouter      │                      │
│  │  • 10 agents        │gates │  • 12 intent types   │                      │
│  │  • Pre-commit       │      │  • TDD enforcement   │                      │
│  │  • CI pipeline      │      │  • Strategy ranking  │                      │
│  │  • Runtime checks   │      │  • Confidence gates  │                      │
│  │  • CORE-064 sweeps  │      │  • Challenge engine  │                      │
│  └─────────────────────┘      └──────────────────────┘                      │
│                                                                             │
│  Every domain communicates through MasterOrchestrator                       │
│  Every action is audit-logged to CortexAuditDB (SQLite WAL)                │
└─────────────────────────────────────────────────────────────────────────────┘
```
