# CORTEX Conversation Tracking

This diagram illustrates how CORTEX captures and learns from GitHub Copilot Chat interactions.

**GitHub Copilot Chat** conversations are automatically captured via ambient daemon monitoring.

**Conversation Capture** extracts markdown-formatted conversations with metadata preservation.

**Markdown Parser** structures the conversation into messages with roles (user/assistant/system).

**Tier 1 Database** stores recent conversations for immediate context injection.

**Context Injection** enriches future responses with relevant past conversations.

This closed-loop learning system ensures CORTEX improves with every interaction, building institutional knowledge over time.