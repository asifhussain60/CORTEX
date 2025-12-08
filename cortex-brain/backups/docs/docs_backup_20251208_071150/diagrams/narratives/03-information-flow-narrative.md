# CORTEX Information Flow

This sequence diagram traces how a user request flows through CORTEX's architecture.

**Entry Point** receives the natural language request and validates it against brain protection rules.

**Intent Router** classifies the request type (question, task, planning) and selects the appropriate agent.

**Agent System** receives the routed request and queries the Knowledge Graph for relevant context.

**Knowledge Graph** searches semantic relationships and retrieves historical data from Long-term Storage.

**Response** is generated with full context awareness, incorporating past conversations and learned patterns.

This flow ensures every response is informed by CORTEX's accumulated knowledge, not just the current request.