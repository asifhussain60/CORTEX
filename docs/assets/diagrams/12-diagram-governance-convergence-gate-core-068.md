# Convergence Gate

```mermaid
flowchart LR
  D[Detect] --> F[Fix] --> R[Rescan] --> Q{Stable?}
  Q -- No --> D
  Q -- Yes --> C[Complete]
```