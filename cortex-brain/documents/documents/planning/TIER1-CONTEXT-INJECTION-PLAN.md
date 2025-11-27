# Tier 1 Context Injection Implementation Plan

**Date:** November 17, 2025  
**Priority:** CRITICAL - Core CORTEX Differentiator  
**Status:** Planning Phase  
**Estimated Time:** 8-12 hours

---

## 🎯 Executive Summary

**Problem:** GitHub Copilot Chat is stateless - conversations don't persist between sessions, making CORTEX lose its core value proposition (memory across sessions).

**Solution:** Implement automatic context injection that loads last 20 conversations from Tier 1 into every CORTEX request, enabling true "it" resolution and seamless continuation.

**Impact:** This transforms CORTEX from "Copilot with occasional memory" to "Copilot with consistent cross-session intelligence."

---

## 📊 Current State Analysis

### ✅ What Exists (Architecture Layer)

1. **Tier 1 Working Memory API** (`src/tier1/working_memory.py`)
   - `store_conversation()` - Save conversations
   - `get_conversation()` - Retrieve by ID
   - `search_conversations()` - Search history
   - `get_recent_conversations()` - Get last N
   - Entity tracking (files, classes, methods)
   - FIFO queue (20 conversations)

2. **Context Injector** (`src/context_injector.py`)
   - `inject_context()` - Main entry point
   - `_inject_tier1()` - Tier 1 specific injection
   - `_inject_tier2()` - Pattern injection
   - `_inject_tier3()` - Git metrics injection
   - Performance target: <200ms

3. **Database Schema** (`cortex-brain/tier1-working-memory.db`)
   - `conversations` table (20 recent)
   - `messages` table (last 10 per conversation)
   - `entities` table (files/classes/methods)
   - SQLite with indexes (18ms avg query time)

### ❌ What's Missing (Integration Layer)

1. **No Automatic Trigger**
   - Context injection exists but isn't called automatically
   - No hook into GitHub Copilot Chat entry point
   - Manual invocation required ("continue work" phrases)

2. **No Conversation Capture**
   - Current conversation not being stored automatically
   - Must manually run capture scripts (PowerShell/Python CLI)
   - No ambient daemon running by default

3. **No Session Continuity**
   - New chat sessions don't load previous context
   - "Make it purple" doesn't know what "it" refers to
   - Each session starts from zero memory

4. **No Context Rendering**
   - Even if injected, context not formatted for LLM
   - No smart summarization (full conversations = token explosion)
   - No relevance ranking (all 20 conversations = noise)

---

## 🏗️ Implementation Architecture

### Phase 1: Automatic Context Injection (3-4 hours)

**Goal:** Every CORTEX request automatically injects Tier 1 context

#### 1.1 Entry Point Hook
**File:** `.github/prompts/CORTEX.prompt.md`

**Add context injection trigger:**
```markdown
## 🧠 Automatic Context Loading

**BEFORE processing any user request:**

1. Check if Tier 1 context injection enabled (default: YES)
2. Call context injector with current conversation ID
3. Inject summarized context into LLM prompt
4. Proceed with normal intent routing

**Implementation:**
- Load last 5 conversations (not all 20 - token optimization)
- Extract entities mentioned (files, classes, methods)
- Identify current work context ("authentication feature", "bug fix", etc.)
- Format as concise summary (target: <500 tokens)
```

#### 1.2 Context Formatter
**New File:** `src/tier1/context_formatter.py`

**Purpose:** Convert raw Tier 1 data into LLM-friendly summary

**Key Methods:**
```python
def format_recent_conversations(conversations: List[Dict]) -> str:
    """
    Convert last 5 conversations into concise summary
    
    Output format:
    ---
    Recent Work Context (Last 5 Conversations):
    
    1. [2 hours ago] Added authentication system
       Files: AuthService.cs, LoginController.cs
       Status: In progress (Phase 2 of 4)
    
    2. [Yesterday] Fixed null reference bug
       Files: UserRepository.cs
       Status: Complete, tests passing
    ...
    ---
    """

def extract_active_entities(conversations: List[Dict]) -> Dict:
    """
    Identify files/classes/methods actively being worked on
    
    Returns:
    {
        'files': ['AuthService.cs', 'LoginController.cs'],
        'classes': ['AuthService', 'JwtTokenGenerator'],
        'methods': ['ValidateCredentials', 'GenerateToken'],
        'current_task': 'Phase 2: JWT implementation'
    }
    """

def resolve_pronouns(user_request: str, active_entities: Dict) -> str:
    """
    Resolve "it", "that", "this" to actual entities
    
    Example:
    Input: "Make it purple"
    Active entities: {'ui_component': 'FAB button'}
    Output: "Make the FAB button purple"
    """
```

#### 1.3 Integration with Intent Router
**File:** `src/agents/intent_router.py`

**Enhance parse() method:**
```python
def parse(self, user_message: str, context_hints: Dict = None) -> Dict:
    # NEW: Inject Tier 1 context BEFORE intent detection
    tier1_context = self._load_tier1_context()
    
    # Resolve pronouns if needed
    if self._has_pronouns(user_message):
        user_message = self._resolve_pronouns(
            user_message, 
            tier1_context['active_entities']
        )
    
    # Existing intent detection (now with resolved message)
    result = self._detect_intent(user_message)
    
    # Add context to result
    result['tier1_context'] = tier1_context
    result['context_injected'] = True
    
    return result
```

---

### Phase 2: Conversation Capture (2-3 hours)

**Goal:** Current conversation automatically stored to Tier 1

#### 2.1 GitHub Copilot Chat Hook (Workaround)
**Challenge:** GitHub Copilot doesn't expose conversation capture hooks

**Solution:** Post-conversation capture pattern

**Option A: Manual Smart Hint (Immediate)**
Add to response format in `CORTEX.prompt.md`:

```markdown
> ### 💡 CORTEX Learning Opportunity
> 
> **Capture this conversation?** 
> Say "remember this" or "capture conversation" to store in Tier 1
> 
> **Why:** Next session can reference this work automatically
```

**Option B: Ambient Daemon (Future - Phase 3)**
Background process that monitors VS Code activity and captures conversations

#### 2.2 Capture Command
**File:** `src/operations/modules/conversation_capture_module.py`

**Natural language triggers:**
- "remember this"
- "capture conversation"
- "save this chat"
- "store context"

**Implementation:**
```python
def capture_current_conversation(context: Dict) -> Dict:
    """
    Capture current conversation to Tier 1
    
    Steps:
    1. Extract conversation history from context
    2. Extract entities (files, classes, methods mentioned)
    3. Detect intent (PLAN, EXECUTE, FIX, etc.)
    4. Store to Tier 1 database
    5. Confirm to user with conversation ID
    """
```

---

### Phase 3: Smart Context Summarization (2-3 hours)

**Goal:** Token-optimized context injection (avoid prompt bloat)

#### 3.1 Relevance Scoring
**File:** `src/tier1/relevance_scorer.py`

**Score conversations by relevance to current request:**
```python
def score_conversation_relevance(
    conversation: Dict,
    current_request: str,
    current_file: Optional[str] = None
) -> float:
    """
    Score 0.0-1.0 based on:
    - Entity overlap (files/classes/methods match)
    - Temporal proximity (recent = higher score)
    - Topic similarity (NLP-based - simple keyword matching for MVP)
    - Work continuity (same feature/bug being worked on)
    """
```

#### 3.2 Adaptive Context Loading
**Strategy:** Load conversations based on relevance, not just recency

**Example:**
```
User: "Continue authentication work"
Relevance scores:
  - Conversation 3 (2 hours ago, auth system): 0.95 ⭐
  - Conversation 1 (5 min ago, UI styling): 0.20
  - Conversation 8 (yesterday, auth planning): 0.85 ⭐
  - Conversation 15 (last week, auth tests): 0.70 ⭐

Loaded conversations: 3, 8, 15 (top 3 by relevance)
Token usage: ~400 tokens (vs 1200+ for all recent)
```

#### 3.3 Summarization Tiers
**Tier 0 (Current Conversation):** Full context  
**Tier 1 (Last 2 conversations):** Moderate detail  
**Tier 2 (Last 5 conversations):** High-level summary  
**Tier 3 (Last 20 conversations):** Entity list only  

---

### Phase 4: User Experience Enhancements (1-2 hours)

#### 4.1 Context Visibility
**Show user what context is loaded:**

```markdown
🧠 **CORTEX Context Loaded**

📚 Recent Work:
   • Authentication system (Phase 2/4, in progress)
   • Bug fix: Null reference in UserRepository (complete)

📄 Active Files:
   • AuthService.cs
   • LoginController.cs
   • JwtTokenGenerator.cs

🎯 Current Task: Implement JWT token validation

[Your response continues below...]
```

#### 4.2 Context Control Commands
**Natural language:**
- "forget the last conversation" → Remove from context
- "show my context" → Display loaded Tier 1 state
- "clear context" → Start fresh (disable injection temporarily)
- "remember this" → Force capture current conversation

---

## 📝 Implementation Steps (Priority Order)

### Step 1: Context Formatter (Day 1 Morning - 2 hours)
- [ ] Create `src/tier1/context_formatter.py`
- [ ] Implement `format_recent_conversations()`
- [ ] Implement `extract_active_entities()`
- [ ] Implement `resolve_pronouns()`
- [ ] Unit tests (test_context_formatter.py)

### Step 2: Intent Router Integration (Day 1 Afternoon - 2 hours)
- [ ] Modify `src/agents/intent_router.py`
- [ ] Add `_load_tier1_context()` method
- [ ] Add pronoun resolution to `parse()`
- [ ] Update tests
- [ ] Integration test: "Make it purple" resolves correctly

### Step 3: Conversation Capture (Day 2 Morning - 2 hours)
- [ ] Create `src/operations/modules/conversation_capture_module.py`
- [ ] Add capture command to command registry
- [ ] Add smart hint to response template
- [ ] Test: Capture conversation manually
- [ ] Verify: Next session loads captured context

### Step 4: Relevance Scoring (Day 2 Afternoon - 2 hours)
- [ ] Create `src/tier1/relevance_scorer.py`
- [ ] Implement `score_conversation_relevance()`
- [ ] Implement adaptive loading strategy
- [ ] Test: Verify top-N conversations loaded by relevance

### Step 5: Context Visibility (Day 3 Morning - 1 hour)
- [ ] Add context summary to response template
- [ ] Format entity list display
- [ ] Test: User sees what context is loaded

### Step 6: Integration Testing (Day 3 Afternoon - 2 hours)
- [ ] End-to-end test: New session loads previous work
- [ ] Test: "Make it purple" resolves correctly
- [ ] Test: "Continue authentication" loads relevant conversations
- [ ] Test: Token usage stays under 500 tokens
- [ ] Test: Performance <200ms

### Step 7: Documentation (Day 4 - 1 hour)
- [ ] Update tracking-guide.md with new capture flow
- [ ] Add examples to technical-reference.md
- [ ] Update story.md with "Before/After" examples
- [ ] Create troubleshooting guide

---

## 🎯 Success Criteria

### Functional Requirements
- ✅ Every CORTEX request automatically loads Tier 1 context
- ✅ "Make it purple" resolves to correct entity from recent work
- ✅ "Continue X" loads relevant past conversations
- ✅ Manual capture: "remember this" stores conversation
- ✅ Context visible: User sees what memory is loaded

### Performance Requirements
- ✅ Context injection: <200ms (target)
- ✅ Token usage: <500 tokens per request (context overhead)
- ✅ Relevance scoring: <50ms
- ✅ Database queries: <20ms (existing performance maintained)

### User Experience Requirements
- ✅ Zero configuration: Works out of box
- ✅ Natural language: No syntax to memorize
- ✅ Transparent: User sees what context is loaded
- ✅ Controllable: Can disable/clear context anytime

---

## 🚀 Quick Win: MVP Implementation (4 hours)

**If we need to ship fast, here's the 80/20 approach:**

### MVP Scope
1. **Context Injection** (1.5 hours)
   - Load last 3 conversations (not 5)
   - Simple summary format (no fancy formatting)
   - Basic pronoun resolution ("it" → last mentioned entity)

2. **Manual Capture** (1 hour)
   - "remember this" command only
   - Store to Tier 1 with basic metadata
   - Confirmation message

3. **Intent Router Hook** (1 hour)
   - Inject context before parsing
   - Resolve pronouns in user message
   - Pass context to agents

4. **Testing** (0.5 hours)
   - Smoke test: Load context works
   - Smoke test: Pronoun resolution works
   - Smoke test: Capture works

**MVP Delivers:** Core value (memory across sessions) without all polish

---

## 🔮 Future Enhancements (Post-MVP)

### Phase 5: Ambient Capture Daemon
- Background process monitors VS Code
- Auto-captures conversations after 30s idle
- No user action required

### Phase 6: Multi-Modal Context
- Code changes detected automatically
- Git commits linked to conversations
- Test results linked to feature work

### Phase 7: Cross-Project Memory
- Share patterns across multiple projects
- "We did authentication in Project A" → Suggest same approach for Project B
- Knowledge transfer automation

---

## 💬 Example User Experience (After Implementation)

**Before (Current):**
```
Session 1:
User: "Add a purple button to the dashboard"
CORTEX: [Creates button]

Session 2 (next day):
User: "Make it bigger"
CORTEX: ❌ "What should I make bigger?"
```

**After (With Tier 1 Injection):**
```
Session 1:
User: "Add a purple button to the dashboard"
CORTEX: [Creates button]
CORTEX: 💡 Say "remember this" to save context

User: "remember this"
CORTEX: ✅ Conversation saved (ID: conv_20251117_153045)

Session 2 (next day):
User: "Make it bigger"

[CORTEX auto-loads Tier 1 context]
🧠 Context Loaded: Recent work on dashboard button

CORTEX: ✅ "I'll increase the size of the purple dashboard button from 48px to 64px"
```

**This is the transformation we're building!**

---

## 📊 ROI Analysis

**Time Investment:** 8-12 hours  
**Value Delivered:** CORTEX's core differentiator fully realized  
**Impact:** Every user interaction becomes 10x more intelligent  

**Before:** CORTEX = Copilot + occasional memory  
**After:** CORTEX = Copilot + persistent cross-session intelligence  

This is **THE** feature that makes CORTEX worth using.

---

**Next Step:** Proceed with Phase 1 (Context Injection) implementation?

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Status:** Planning Complete - Ready for Implementation
