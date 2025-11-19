# Chapter 02: Building First Memory

*Part of The Intern with Amnesia - The CORTEX Story*  
*Author: Asif Hussain | © 2024-2025*  
*Generated: November 19, 2025*

---

## Overview

**Concept:** Creating persistent conversation storage  
**Technical Mapping:** Tier 1 Working Memory (FIFO queue, 20 conversations)

---

## The Story

Like your working memory that holds recent thoughts and conversations, Tier 1 is **CORTEX's solution to Copilot's amnesia problem**. It remembers your recent work.

**What's in Tier 1:**
- **Conversation History** - Complete record of last 20 conversations preserved
- **Message Continuity** - Last 10 messages in the currently active conversation
- **Entity Tracking** - Files mentioned, classes created, methods modified
- **Context References** - What "it" refers to when you say "make it purple"
- **FIFO Queue** - When conversation #21 starts, conversation #1 gets deleted (First In, First Out)
- **Active Protection** - Current conversation never deleted, even if it's the oldest

**How It Solves Amnesia:**
```
You: "Add a pulse animation to the FAB button in HostControlPanel"
→ Conversation #15 created
→ Entities tracked: FAB button, HostControlPanel.razor, pulse animation

[10 minutes later, same chat]
You: "Make it purple"
→ Brain checks Tier 1
→ Finds "FAB button" in conversation #15
→ Knows "it" = FAB button
→ Applies purple color to the correct element ✅

[2 weeks and 20 conversations later]
→ FIFO queue triggers
→ Conversation #15 deleted from Tier 1
→ BUT: Patterns extracted first
→ Moved to Tier 2 (long-term memory) for future reference
```

**Storage:** `cortex-brain/tier1/conversations.db` (SQLite), `cortex-brain/tier1/conversation-context.jsonl`  
**Performance:** <50ms query time (target), 18ms actual ⚡

---

---

## Technical Deep Dive

### Tier 1 Working Memory (FIFO queue, 20 conversations)


**Tier 1 Architecture:**
- SQLite database: `cortex-brain/tier1/conversations.db`
- JSONL context: `cortex-brain/tier1/conversation-context.jsonl`
- FIFO queue: 20 conversation limit
- Active protection: Current conversation never deleted
- Performance: <50ms query time target, 18ms actual

**What's Stored:**
- Complete conversation history
- Last 10 messages in active conversation
- Entity tracking (files, classes, methods)
- Context references
- Temporal information


---

## Key Takeaways

- Tier 1 stores last 20 conversations in FIFO queue
- Entity tracking maintains context across messages
- Active protection prevents current conversation loss
- Sub-50ms performance enables seamless interaction


---

## Next Chapter

**[Chapter 03: The Learning System](./03-the-learning-system.md)**

*Extracting patterns from experiences*
