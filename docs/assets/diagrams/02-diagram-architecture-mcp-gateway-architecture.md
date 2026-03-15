# MCP Gateway Architecture

```mermaid
flowchart LR
  A[Agent] --> R[MCP Registry]
  R --> C[cortex_code]
  R --> G[cortex_govern]
  R --> N[cortex_analyze]
  R --> P[cortex_plan]
  R --> L[cortex_learn]
  R --> O[cortex_ops]
```