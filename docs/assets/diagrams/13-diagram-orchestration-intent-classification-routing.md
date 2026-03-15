# Intent Routing

```mermaid
flowchart TB
  I[Intent] --> G[Intent Gateway]
  G --> P[Plan]
  G --> B[Build]
  G --> A[Audit]
  G --> D[Debug]
```