# TDD Cycle FSM

```mermaid
stateDiagram-v2
  [*] --> Red
  Red --> Green
  Green --> Refactor
  Refactor --> Validate
  Validate --> [*]
```