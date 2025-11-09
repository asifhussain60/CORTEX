title: CORTEX 2.0 – Brain Architecture

node cortex:
  Cortex.md (Entrypoint)

node corpus_callosum:
  Corpus Callosum
  [Message Queue + DAG Engine]

node right_brain:
  RIGHT BRAIN
  Strategic Planner
  - Dispatcher
  - Planner
  - Analyst
  - Governor
  - Protector

node left_brain:
  LEFT BRAIN
  Tactical Executor
  - Builder
  - Tester
  - Fixer
  - Inspector
  - Archivist

node memory:
  5-TIER MEMORY SYSTEM
  - Tier 0: Instinct
  - Tier 1: Working Memory
  - Tier 2: Knowledge Graph
  - Tier 3: Dev Context
  - Tier 4: Events

node plugins:
  Plugin System
  - Registry, Hooks, Lifecycle

node workflows:
  Workflow Pipeline Engine
  - DAG, Retry, Parallel

node concerns:
  Cross-Cutting Concerns
  - Paths, Health, Boundaries

cortex -> corpus_callosum
corpus_callosum -> right_brain
corpus_callosum -> left_brain
right_brain -> memory
left_brain -> memory
memory -> plugins -> workflows -> concerns
