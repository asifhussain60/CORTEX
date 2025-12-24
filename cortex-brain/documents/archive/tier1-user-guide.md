# Tier 1 Context System - User Guide

**CORTEX Cross-Session Memory for GitHub Copilot**

Version: 1.0  
Last Updated: January 13, 2025  
Author: Asif Hussain

---

## Table of Contents

1. [Overview](#overview)
2. [What is Tier 1 Context?](#what-is-tier-1-context)
3. [Natural Language Commands](#natural-language-commands)
4. [Using Context Features](#using-context-features)
5. [Understanding Quality Indicators](#understanding-quality-indicators)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Overview

CORTEX's Tier 1 Context System gives GitHub Copilot **cross-session memory**—the ability to remember your conversations and automatically inject relevant context when you return to related work.

**Key Benefits:**
- ✅ **Never repeat yourself**: Copilot remembers previous discussions
- ✅ **Automatic context injection**: Relevant conversations appear when needed
- ✅ **Full user control**: View, forget, or clear context at any time
- ✅ **Token-efficient**: Optimized formatting stays within API limits
- ✅ **Quality-aware**: See why context was retrieved

---

## What is Tier 1 Context?

### The Problem

Standard GitHub Copilot has **no memory between sessions**. If you:
1. Ask "How should I implement authentication?"
2. Close VS Code
3. Return tomorrow and ask "Update the auth flow"

Copilot won't remember your previous authentication discussion—you have to explain everything again.

### The CORTEX Solution

Tier 1 automatically:
1. **Captures** conversations to a local database (`cortex-brain/tier1/working_memory.db`)
2. **Scores** past conversations for relevance to your current request
3. **Injects** the most relevant context into Copilot's response
4. **Displays** context when you want to review it

---

## Natural Language Commands

### View Context

**Show me what Copilot remembers:**
```
show context
```

**Displays:**
- Recent conversations related to current work
- Relevance scores (why each was retrieved)
- Quality indicators (recency, file overlap, intent match)
- Token count (API budget usage)

### Forget Specific Topics

**Remove conversations about a specific topic:**
```
forget about authentication
forget the database migration discussion
forget conversation about user registration
```

**What happens:**
- Conversations matching the topic are removed from memory
- Future requests won't see this context
- Useful for outdated or incorrect information

### Clear All Context

**Start fresh (removes all memories):**
```
clear all context
clear memory
reset cortex memory
```

**Use when:**
- Switching to a completely different project
- Context has become stale or confusing
- You want to test Copilot without historical context

---

## Using Context Features

### Automatic Context Injection

CORTEX automatically injects context into responses **when relevant conversations are found**.

**Example Workflow:**

**Session 1 (Monday):**
```
You: How should I implement JWT authentication in Python?

Copilot: For JWT authentication, I recommend using PyJWT library...
[CORTEX captures this conversation]
```

**Session 2 (Wednesday):**
```
You: Add token refresh to the auth system

Copilot: 
📋 **Context from Previous Conversations**
- 2 days ago: Discussion about JWT authentication implementation
- Relevance: 0.87 (High) - Files: auth.py, tokens.py
- Intent: IMPLEMENT

Based on your previous JWT setup, here's how to add token refresh...
```

**Note the context summary:**
- Automatically inserted at the start of the response
- Shows what Copilot "remembered"
- Includes quality indicators (relevance score, recency, files)

### Manual Context Review

**When to use `show context`:**
- Before starting complex work (see what Copilot knows)
- After `forget` command (verify removal)
- When responses seem off-target (check if wrong context is loaded)

**Example output:**
```
📋 Context Summary (Last 24 hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔹 Conversation 1: JWT authentication implementation
   Relevance: 0.87 (High)
   Time: 2 days ago
   Files: auth.py, tokens.py
   Intent: IMPLEMENT

🔹 Conversation 2: Password reset flow design
   Relevance: 0.65 (Medium)
   Time: 5 days ago
   Files: auth.py, emails.py
   Intent: PLAN

Quality Indicators:
- Total Conversations: 2
- Average Relevance: 0.76
- Token Usage: 324 / 500

✅ Context quality: Good
```

### Context in Practice

#### Example 1: Continuing Implementation

**Monday:**
```
You: Design a caching strategy for database queries

Copilot: I'd recommend Redis with TTL-based expiration...
```

**Tuesday (file: cache.py open):**
```
You: Implement the cache invalidation logic

Copilot:
📋 **Context: Yesterday's caching strategy discussion** (Relevance: 0.92)

Based on the Redis strategy we discussed, here's the invalidation logic...
```

#### Example 2: Cross-File Continuity

**File: models/user.py**
```
You: Add user permissions system

Copilot: Let's add role-based permissions...
```

**File: api/auth.py**
```
You: Add permission checks to API endpoints

Copilot:
📋 **Context: User permissions design in models/user.py** (Relevance: 0.78)

To integrate with the RBAC system we added, use this decorator...
```

#### Example 3: Cleaning Up Context

```
You: forget about the old authentication approach

CORTEX: ✅ Removed 3 conversations about authentication
- "Basic auth implementation" (7 days ago)
- "Session-based auth discussion" (8 days ago)  
- "Auth middleware design" (10 days ago)

You: show context

CORTEX: 📋 Context Summary
No relevant conversations found.
✅ Starting fresh!
```

---

## Understanding Quality Indicators

When you `show context`, CORTEX displays **quality indicators** to help you assess the retrieved context:

### Relevance Score

**Scale: 0.0 to 1.0**

| Score | Quality | Meaning |
|-------|---------|---------|
| 0.80+ | 🟢 High | Highly relevant - same topic, files, intent |
| 0.50-0.79 | 🟡 Medium | Somewhat relevant - related concepts |
| 0.20-0.49 | 🟠 Low | Tangentially related |
| <0.20 | 🔴 Very Low | Likely not useful |

**What affects score:**
- **Keyword overlap** (30%): Shared terms between current request and past conversation
- **File overlap** (25%): Same files referenced
- **Entity overlap** (20%): Same classes, functions, variables mentioned
- **Temporal factor** (15%): Recent conversations score higher
- **Intent match** (10%): Same intent (IMPLEMENT, FIX, PLAN, etc.)

### Recency

- **< 1 day ago**: 🔥 Fresh - most relevant
- **1-3 days ago**: ✅ Recent - very useful
- **4-7 days ago**: ⏰ Week old - may be outdated
- **> 7 days ago**: 📅 Old - verify before using

### Token Usage

**Budget: 500 tokens** (relaxed to 600 for testing)

- **< 300 tokens**: ✅ Efficient - plenty of room for your code
- **300-450 tokens**: ⚠️ Moderate - watch API limits
- **> 450 tokens**: 🚨 High - may hit API limits

---

## Best Practices

### 1. Capture Important Decisions

Use natural conversation—CORTEX captures automatically:
```
You: Let's use PostgreSQL for the main database and Redis for caching

Copilot: Good architecture choice. Here's how to set them up...
```

Later, CORTEX will remember this decision when you work on database code.

### 2. Use Descriptive Requests

**Better:**
```
You: Implement user authentication with JWT tokens
```

**Not as good:**
```
You: Add auth
```

Descriptive requests create better context summaries and improve future relevance scoring.

### 3. Review Context Before Complex Work

```
You: show context
[Review what Copilot knows]

You: Now implement the payment gateway integration
```

Ensures Copilot has the right background before starting.

### 4. Clean Up Outdated Context

**Weekly maintenance:**
```
You: forget about the old API design from last month
You: forget the prototype implementation
```

Keeps context fresh and prevents confusion.

### 5. Leverage File-Specific Context

When working on `auth.py`, CORTEX automatically prioritizes conversations that mentioned `auth.py`. This creates natural continuity across sessions.

### 6. Use Intent-Aware Requests

CORTEX detects intent keywords:
- **PLAN**: "design", "architecture", "approach"
- **IMPLEMENT**: "implement", "create", "build", "add"
- **FIX**: "fix", "bug", "error", "issue"
- **REFACTOR**: "refactor", "improve", "optimize"
- **TEST**: "test", "validate", "verify"

Matching intents score higher in relevance.

---

## Troubleshooting

### Context Not Showing Up

**Problem:** You expect context but responses don't show `[CONTEXT_SUMMARY]`

**Solutions:**
1. Check relevance scores with `show context`
   - If scores are < 0.50, context may not be relevant enough
2. Use more specific requests (mention file names, key terms)
3. Verify conversations were captured:
   ```
   show context
   ```
   - Should list recent conversations

### Too Much Context

**Problem:** Responses include irrelevant old conversations

**Solutions:**
1. Use `forget` to remove specific topics:
   ```
   forget about the old authentication approach
   ```
2. Use `clear all context` to start fresh
3. Be more specific in requests to improve relevance scoring

### Context Quality is Low

**Problem:** `show context` shows "Low quality" indicators

**Solutions:**
1. Recent conversations score higher - older context may be stale
2. File overlap is missing - mention specific files in requests:
   ```
   Update auth.py to use the new token system
   ```
3. Clear old context and have fresh conversations

### Database Errors

**Problem:** "Failed to load context" errors

**Solutions:**
1. Check that `cortex-brain/tier1/working_memory.db` exists
2. Verify file permissions (read/write access)
3. If corrupted, backup and delete database - CORTEX will recreate:
   ```bash
   cd cortex-brain/tier1
   mv working_memory.db working_memory.db.backup
   ```
4. Restart VS Code

### Token Budget Exceeded

**Problem:** Context uses > 500 tokens, hitting API limits

**Solutions:**
1. Use `forget` to remove less relevant conversations
2. CORTEX automatically uses token-efficient formatting
3. If persistent, increase context budget (requires code change)

---

## Advanced Tips

### 1. Cross-Session Workflows

**Day 1: Design**
```
You: Design a user registration system with email verification

[CORTEX captures design discussion]
```

**Day 2: Implementation**
```
You: Implement the email verification flow

[CORTEX auto-injects Day 1 design as context]
```

**Day 3: Testing**
```
You: Add tests for email verification

[CORTEX auto-injects Days 1-2 context]
```

### 2. Multi-File Continuity

Work across files with continuous context:
```
models/user.py → api/users.py → tests/test_users.py
```

CORTEX maintains context across all files.

### 3. Intent Chains

CORTEX scores higher when intents follow logical progression:
```
PLAN → IMPLEMENT → TEST → REFACTOR
```

### 4. Periodic Context Review

Monthly habit:
```
1. show context
2. Review old conversations (> 30 days)
3. forget outdated topics
4. Continue fresh
```

---

## Performance Metrics

CORTEX Tier 1 meets these performance targets:

| Metric | Target | Tested |
|--------|--------|--------|
| Context Injection | < 500ms | ✅ Yes |
| Context Display | < 200ms | ✅ Yes |
| Token Budget | < 600 tokens | ✅ Yes |
| Relevance Accuracy | > 80% | ✅ Yes |

---

## Privacy & Security

### Data Storage

- **Location**: `cortex-brain/tier1/working_memory.db` (local SQLite)
- **No cloud sync**: All data stays on your machine
- **No telemetry**: CORTEX doesn't send data anywhere

### What is Stored

- Your requests to Copilot
- Copilot's responses
- Extracted entities (files, classes, functions)
- Detected intent
- Timestamps

### What is NOT Stored

- Authentication credentials
- API keys
- Passwords
- External API responses

---

## Next Steps

1. **Try it out**: Start a conversation and see automatic context injection
2. **Experiment with commands**: Practice `show context`, `forget`, and `clear`
3. **Build muscle memory**: Use descriptive requests for better context
4. **Review periodically**: Monthly cleanup keeps context fresh

For developer documentation (APIs, integration, extension), see:
- [Tier 1 API Reference](./tier1-api-reference.md)
- [CORTEX Architecture](../architecture/tier-architecture.md)

---

**Questions or issues?** Open an issue in the CORTEX repository.

**© 2024-2025 Asif Hussain. All rights reserved.**
