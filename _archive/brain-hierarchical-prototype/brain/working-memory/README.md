# Tier 1: Working Memory

**Purpose:** Short-term conversation history (last 20 conversations, FIFO queue).

## 📂 Contents

- \ecent-conversations/\ - Individual conversation files
- \conversation-index.yaml\ - Fast lookup index
- \ctive-conversation.jsonl\ - Current chat (symlink)

## 🔄 FIFO Queue

- **Capacity:** 20 complete conversations
- **Deletion:** When conversation #21 starts, #1 is deleted
- **No time limit:** Conversations preserved until FIFO deletion
- **Active protected:** Current conversation never deleted

## 📖 See Also

- conversation-context-manager.md - Manages this tier
- BRAIN-CONVERSATION-MEMORY-DESIGN.md - Design details
