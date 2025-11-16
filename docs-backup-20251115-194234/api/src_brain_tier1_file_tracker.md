# src.brain.tier1.file_tracker

CORTEX Brain - Tier 1: FileTracker

Purpose: Track file modifications per conversation and detect co-modification patterns

Features:
- Track which files are modified in each conversation
- Detect files frequently modified together (co-modification)
- Build file relationship graph for Tier 2 learning
- Support file categorization (source, tests, config, docs)
- Enable file-based conversation retrieval

Use Cases:
- "Show me conversations about HostControlPanel.razor"
- "What files are usually modified with this file?"
- "Which conversations touched the authentication system?"

Author: CORTEX Development Team
Version: 1.0.0
