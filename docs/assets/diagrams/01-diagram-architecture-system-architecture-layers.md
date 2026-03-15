# System Architecture Layers

```mermaid
flowchart TB
  U[User Intent] --> O[Orchestration]
  O --> I[Intelligence]
  O --> M[MCP Tools]
  O --> G[Governance Gate]
  G --> E[Execution + Validation]
```