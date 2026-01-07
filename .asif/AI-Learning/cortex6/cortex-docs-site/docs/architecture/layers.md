---
title: 6‑Layer Architecture
---

CORTEX is organized into **six layers** to keep concerns clean and enforceable:

1. **Layer 6 – Presentation**: Copilot terminal proxy, CLI, MCP clients
2. **Layer 5 – API**: MCP server (JSON‑RPC 2.0)
3. **Layer 4 – Orchestration**: Master orchestrator, TODO orchestrator, pattern router, workflow orchestrators
4. **Layer 3 – Governance**: governance merger, audit logger, resource limiter
5. **Layer 2 – State**: state manager (SQLite + WAL), checkpoint, rollback
6. **Layer 1 – Infrastructure**: file I/O, transports, logging

See the diagram page for the full flow.
