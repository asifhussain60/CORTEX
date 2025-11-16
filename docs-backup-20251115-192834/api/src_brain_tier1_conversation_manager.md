# src.brain.tier1.conversation_manager

CORTEX Brain - Tier 1: ConversationManager

Purpose: Core CRUD operations for managing conversations in SQLite database

Features:
- Create, read, update, delete conversations
- FIFO queue management (max 20 conversations)
- Message threading and sequencing
- Context resolution support
- Performance optimized (<100ms queries)

Database Tables:
- tier1_conversations: Conversation metadata
- tier1_messages: Individual messages within conversations
- tier1_conversations_fts: Full-text search index

Author: CORTEX Development Team
Version: 1.0.0
