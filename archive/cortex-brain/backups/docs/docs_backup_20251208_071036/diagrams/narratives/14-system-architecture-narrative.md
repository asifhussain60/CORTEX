# CORTEX System Architecture

This diagram presents CORTEX's complete architectural view.

**User Interface** is the GitHub Copilot Chat extension in VS Code.

**CORTEX Core** orchestrates routing, memory management, and operation execution.

**Knowledge Graph (Brain)** maintains semantic relationships and learned patterns.

**Agent System** executes specialized tasks (Executor, Planner, Tester, etc.).

**Storage** persists conversations, patterns, and historical data across sessions.

This architecture separates concerns - UI handles presentation, Core handles orchestration, Agents handle execution, Brain handles memory. Each component has a clear responsibility, enabling independent evolution and testing.

CORTEX is designed as a distributed cognitive system, not a monolithic application.