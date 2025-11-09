# CORTEX 2.1 - Interactive Feature Planning Design

**Version:** 2.1.0  
**Status:** 🎯 DESIGN PHASE  
**Phase:** Enhancement to CORTEX 2.0 Modular Architecture  
**Author:** Asif Hussain  
**Date:** November 9, 2025

---

## 📋 Executive Summary

CORTEX 2.1 introduces **Interactive Feature Planning** - a collaborative conversation mode where CORTEX asks clarifying questions before creating implementation plans. This enhancement addresses ambiguous requirements through guided dialogue, ensuring better alignment between user intent and implementation.

**Key Features:**
- ✅ Opt-in entry point command: `/CORTEX, let's plan a feature`
- ✅ One question at a time (conversational flow)
- ✅ Auto-detect ambiguity for targeted questioning
- ✅ Max 5 questions per planning session
- ✅ User preference memory (Tier 2 Knowledge Graph)
- ✅ Scoped to PLAN intent only (not all workflows)

**Additional Enhancement:**
- ✅ Expanded command structure (7 new entry points)
- ✅ Natural language aliases for all commands

---

## 🎯 Problem Statement

### Current State (CORTEX 2.0)

**Workflow:**
```
User: "Refactor authentication"
↓
CORTEX: *immediately analyzes and creates plan*
↓
CORTEX: *begins implementation*
```

**Problems:**
1. ❌ Assumes it understands ambiguous requirements
2. ❌ No opportunity for user to clarify scope
3. ❌ May implement wrong solution
4. ❌ Wastes time on rework

### Desired State (CORTEX 2.1)

**Workflow:**
```
User: "/CORTEX, let's plan a feature - refactor authentication"
↓
CORTEX: "What type of auth? (OAuth/JWT/Session)"
User: "JWT"
↓
CORTEX: "Keep existing user schema?"
User: "Yes"
↓
CORTEX: "Add refresh token support?"
User: "Yes"
↓
CORTEX: "Here's the plan: [detailed implementation]"
CORTEX: "Proceed with implementation? (yes/no/modify)"
User: "yes"
↓
CORTEX: *implements with confidence*
```

**Benefits:**
1. ✅ Clarifies ambiguous requirements
2. ✅ Collaborative planning process
3. ✅ Reduces rework and mistakes
4. ✅ User feels in control

---

## 🏗️ Architecture Design

### New Components

#### 1. Interactive Planning Agent (Right Brain)

**Location:** `src/cortex_agents/right_brain/interactive_planner.py`

**Responsibilities:**
- Detect ambiguity in user requests
- Generate clarifying questions (max 5)
- Manage conversation state
- Build refined plan from answers

**API:**
```python
class InteractivePlannerAgent:
    def __init__(self, tier1_memory, tier2_knowledge):
        self.memory = tier1_memory
        self.knowledge = tier2_knowledge
        self.max_questions = 5
    
    def detect_ambiguity(self, request: str) -> float:
        """
        Analyzes request for ambiguity.
        Returns: confidence score (0-100%)
        """
        pass
    
    def generate_question(self, request: str, context: Dict, question_num: int) -> Question:
        """
        Generates next clarifying question based on context.
        Returns: Question object with text, type, and options
        """
        pass
    
    def process_answer(self, question: Question, answer: str) -> Dict:
        """
        Processes user answer and updates context.
        Returns: Updated context for next question
        """
        pass
    
    def create_refined_plan(self, request: str, context: Dict) -> Plan:
        """
        Creates implementation plan with all gathered context.
        Returns: Detailed plan ready for execution
        """
        pass
    
    def should_ask_more(self, context: Dict, question_count: int) -> bool:
        """
        Decides if more questions are needed.
        Returns: True if more questions, False if ready to plan
        """
        pass
```

#### 2. Question Generator (Right Brain Utility)

**Location:** `src/cortex_agents/right_brain/question_generator.py`

**Responsibilities:**
- Generate high-quality clarifying questions
- Prioritize questions by importance
- Adapt to user's domain expertise level

**Question Types:**
```python
class QuestionType(Enum):
    REQUIRED = "required"      # Must be answered
    OPTIONAL = "optional"      # Can skip
    MULTIPLE_CHOICE = "choice" # Select from options
    FREE_TEXT = "text"        # Open-ended
    YES_NO = "boolean"        # Simple yes/no

class Question:
    text: str                  # Question text
    type: QuestionType         # Question category
    options: List[str]         # For multiple choice
    default: Optional[str]     # Default answer
    priority: int              # 1-5 (5 = critical)
    context: Dict              # Additional context
```

#### 3. User Preference Memory (Tier 2 Enhancement)

**Location:** `cortex-brain/knowledge-graph.yaml`

**New Section:**
```yaml
user_preferences:
  planning_style:
    interactive_mode_frequency: "high|medium|low"
    typical_question_count: 3
    prefers_detailed_plans: true
    domains_requiring_clarity:
      - "authentication"
      - "architecture changes"
      - "database migrations"
  
  learned_patterns:
    - pattern: "always asks about backward compatibility"
      frequency: 0.85
      actions: ["auto-include backward compat question"]
    
    - pattern: "prefers JWT over session auth"
      frequency: 0.92
      actions: ["suggest JWT as default"]
```

#### 4. Command Router Enhancement

**Location:** `src/cortex_agents/corpus_callosum/command_router.py`

**New Commands:**
```python
CORTEX_COMMANDS = {
    # Existing
    "/setup": "setup_environment",
    "/resume": "resume_conversation",
    "/status": "show_status",
    
    # NEW for CORTEX 2.1
    "/refresh-story": "refresh_cortex_story",
    "/plan-feature": "interactive_feature_planning",
    "/architect": "architecture_design",
    "/refactor": "refactor_module",
    "/brain-protect": "run_brain_protection",
    "/run-tests": "execute_test_suite",
    "/generate-docs": "generate_documentation",
}

# Natural language equivalents
NL_EQUIVALENTS = {
    "let's plan a feature": "/plan-feature",
    "let's design architecture": "/architect",
    "let's refactor this": "/refactor",
    "refresh the story": "/refresh-story",
    "run brain protection": "/brain-protect",
    "run tests": "/run-tests",
    "generate documentation": "/generate-docs",
}
```

---

## 🎯 User Experience Flow

### Entry Point

**User invokes interactive planning:**
```
/CORTEX, let's plan a feature - refactor authentication system
```

Or natural language:
```
CORTEX, let's plan how to refactor authentication
```

### Conversation Flow

```
┌─────────────────────────────────────────────────┐
│ User: "/CORTEX, let's plan a feature -          │
│        refactor authentication"                 │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ CORTEX: "I'll ask up to 5 questions to create   │
│          the best plan. Type 'skip' to use      │
│          defaults or 'done' when satisfied."    │
│                                                 │
│ Question 1/5: What authentication strategy?    │
│   A) OAuth 2.0                                  │
│   B) JWT tokens                                 │
│   C) Session-based                              │
│   D) Other (specify)                            │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ User: "B - JWT tokens"                          │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ CORTEX: "Got it! ✅ JWT tokens"                 │
│                                                 │
│ Question 2/5: Should I keep the existing       │
│               user data schema?                 │
│   A) Yes (safer, less migration)                │
│   B) No (redesign schema)                       │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ User: "A"                                       │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ CORTEX: "Perfect! ✅ Keep existing schema"      │
│                                                 │
│ Question 3/5: Add refresh token support?       │
│   A) Yes                                        │
│   B) No                                         │
│   C) Add later                                  │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ User: "A"                                       │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ CORTEX: "Excellent! ✅ Refresh tokens included" │
│                                                 │
│ Question 4/5: Migrate existing sessions        │
│               automatically?                    │
│   A) Yes (convert all sessions)                 │
│   B) No (users re-login)                        │
│   C) Hybrid (grace period)                      │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ User: "done"                                    │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ CORTEX: "I have enough to create a great plan!" │
│                                                 │
│ 📋 IMPLEMENTATION PLAN                          │
│ ═══════════════════════════════════════════════ │
│                                                 │
│ Phase 1: JWT Infrastructure                     │
│   - Install jsonwebtoken library                │
│   - Create token generation service             │
│   - Add refresh token endpoints                 │
│   - Estimated: 3 hours                          │
│                                                 │
│ Phase 2: Authentication Middleware              │
│   - Update auth middleware for JWT              │
│   - Add token validation                        │
│   - Keep existing user schema                   │
│   - Estimated: 2 hours                          │
│                                                 │
│ Phase 3: Testing                                │
│   - Unit tests for token service                │
│   - Integration tests for auth flow             │
│   - Security tests                              │
│   - Estimated: 2 hours                          │
│                                                 │
│ Total: ~7 hours                                 │
│                                                 │
│ Proceed with implementation?                    │
│   - Type 'yes' to begin                         │
│   - Type 'modify' to adjust plan                │
│   - Type 'save' to save plan for later          │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ User: "yes"                                     │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ CORTEX: "Starting implementation! 🚀"           │
│         Switching to Executor Agent..."         │
└─────────────────────────────────────────────────┘
```

### User Controls

**During questioning:**
- `skip` - Use default answer for current question
- `done` - Finish questions early, proceed with available info
- `back` - Go back to previous question
- `restart` - Start questioning over
- `abort` - Cancel interactive planning

**After plan generated:**
- `yes` - Proceed with implementation
- `no` - Cancel and exit
- `modify` - Edit specific parts of plan
- `save` - Save plan to Tier 1 memory for later

---

## 🎯 Context-Aware Question Management

### Overview: Smart Question Skipping

**Problem:** Inefficient questioning when users provide additional information in their answers.

**Example:**
```
CORTEX: "What authentication strategy? (OAuth 2.0 / JWT / Session)"
User: "B (JWT), and by the way, add refresh token support"
```

**Without Context Tracking:**
- CORTEX asks Question 2: "Keep existing user schema?"
- CORTEX asks Question 3: "Need refresh token support?" ❌ **REDUNDANT!**

**With Context Tracking:**
- CORTEX extracts "add refresh token support" from answer
- CORTEX skips Question 3 (already answered)
- CORTEX asks Question 2 only

**Result:** Faster conversations, better UX, reduced user frustration.

---

### Architecture: Two-Component System

#### 1. AnswerParser (Natural Language Processor)

**Location:** `src/cortex_agents/right_brain/answer_parser.py`

**Purpose:** Extract both direct answers and additional context from natural language responses.

**Core Logic:**
```python
class AnswerParser:
    """
    Parses user answers to extract:
    1. Direct answer to the question asked
    2. Additional context/preferences mentioned
    3. Implied decisions from context
    """
    
    def parse(self, question: Question, answer: str) -> ParsedAnswer:
        """
        Parses user answer into structured format.
        
        Args:
            question: The question that was asked
            answer: User's natural language response
            
        Returns:
            ParsedAnswer with direct_answer + additional_context
        """
        # 1. Extract direct answer
        direct_answer = self._extract_direct_answer(question, answer)
        
        # 2. Extract additional keywords/phrases
        additional_context = self._extract_additional_context(answer)
        
        # 3. Map context to potential question topics
        implied_answers = self._map_context_to_questions(
            additional_context, 
            self.remaining_questions
        )
        
        return ParsedAnswer(
            direct_answer=direct_answer,
            additional_context=additional_context,
            implied_answers=implied_answers
        )

class ParsedAnswer:
    """Structured representation of user's answer."""
    direct_answer: str                    # Answer to question asked
    additional_context: List[str]         # Keywords extracted
    implied_answers: Dict[str, Any]       # Question ID -> inferred answer
    confidence: Dict[str, float]          # Question ID -> confidence (0-1)
```

**Example Parsing:**

**Input:**
- Question: "What authentication strategy?"
- Answer: "JWT, and by the way, add refresh token support"

**Output:**
```python
ParsedAnswer(
    direct_answer="JWT",
    additional_context=["refresh token", "add", "support"],
    implied_answers={
        "q3_refresh_tokens": "yes"  # Question 3: Need refresh tokens?
    },
    confidence={
        "q3_refresh_tokens": 0.95   # Very high confidence
    }
)
```

**Advanced Example:**

**Input:**
- Question: "Keep existing user schema?"
- Answer: "Yes, but add OAuth provider field for social login"

**Output:**
```python
ParsedAnswer(
    direct_answer="yes",
    additional_context=["OAuth provider", "social login", "add field"],
    implied_answers={
        "q4_social_login": "yes",        # Question 4: Support social login?
        "q5_oauth_providers": "yes"      # Question 5: OAuth integration?
    },
    confidence={
        "q4_social_login": 0.92,
        "q5_oauth_providers": 0.88
    }
)
```

#### 2. QuestionFilter (Dynamic Question Skipper)

**Location:** `src/cortex_agents/right_brain/question_filter.py`

**Purpose:** Decide which questions to skip based on accumulated context.

**Core Logic:**
```python
class QuestionFilter:
    """
    Filters out redundant questions based on:
    1. Direct answers from previous responses
    2. Implied answers from context parsing
    3. User preferences from Tier 2 memory
    """
    
    def filter_questions(
        self, 
        remaining_questions: List[Question],
        accumulated_context: Dict,
        confidence_threshold: float = 0.85
    ) -> List[Question]:
        """
        Filters questions that can be skipped.
        
        Args:
            remaining_questions: Questions not yet asked
            accumulated_context: All context gathered so far
            confidence_threshold: Min confidence to skip (default 85%)
            
        Returns:
            Filtered list of questions that still need asking
        """
        filtered = []
        
        for question in remaining_questions:
            # Check if already answered directly
            if self._has_direct_answer(question, accumulated_context):
                self._log_skip(question, "direct answer provided")
                continue
            
            # Check if answered with high confidence inference
            if self._has_implied_answer(question, accumulated_context, confidence_threshold):
                self._log_skip(question, "implied from context")
                continue
            
            # Check user preferences (Tier 2)
            if self._matches_learned_preference(question, accumulated_context):
                self._log_skip(question, "matches user preference")
                continue
            
            # Question still needed
            filtered.append(question)
        
        return filtered
    
    def _has_direct_answer(self, question: Question, context: Dict) -> bool:
        """Check if question already answered explicitly."""
        return question.id in context.get("direct_answers", {})
    
    def _has_implied_answer(
        self, 
        question: Question, 
        context: Dict, 
        threshold: float
    ) -> bool:
        """Check if question answered with sufficient confidence."""
        implied = context.get("implied_answers", {})
        confidence = context.get("confidence", {})
        
        return (
            question.id in implied and 
            confidence.get(question.id, 0) >= threshold
        )
    
    def _matches_learned_preference(
        self, 
        question: Question, 
        context: Dict
    ) -> bool:
        """Check if Tier 2 learned preferences answer question."""
        preferences = context.get("user_preferences", {})
        return question.topic in preferences
```

---

### Conversation Flow with Context Tracking

#### Example 1: Maximum Efficiency (User Provides Everything Upfront)

**Scenario:** User anticipates all questions and provides info immediately.

```
┌─────────────────────────────────────────────────┐
│ User: "Refactor authentication to JWT with      │
│        refresh tokens, keep existing schema,    │
│        add social login with Google/GitHub"     │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ CORTEX: Processing request...                   │
│                                                 │
│ 🔍 Context Analysis:                            │
│   ✓ Auth strategy: JWT                          │
│   ✓ Refresh tokens: Yes                         │
│   ✓ Schema preservation: Yes                    │
│   ✓ Social login: Yes (Google, GitHub)          │
│                                                 │
│ All questions answered! Moving to planning...   │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 📋 IMPLEMENTATION PLAN                          │
│ (Generated without asking ANY questions)        │
└─────────────────────────────────────────────────┘
```

**Questions Skipped:** 5/5 (100% efficiency)

#### Example 2: Partial Context (User Provides Some Info)

**Scenario:** User mentions 2 things, CORTEX infers 1 more, asks about remaining 2.

**Original Question Set:**
1. What authentication strategy? (OAuth 2.0 / JWT / Session)
2. Keep existing user schema? (Yes / No)
3. Need refresh token support? (Yes / No)
4. Support social login? (Yes / No)
5. Which OAuth providers? (Google / GitHub / Facebook / Custom)

**Conversation:**

```
┌─────────────────────────────────────────────────┐
│ User: "Refactor authentication system"          │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ CORTEX: "I detected some ambiguity. Let me ask  │
│          a few quick questions (max 5)..."      │
│                                                 │
│ Question 1/5:                                   │
│ What authentication strategy do you prefer?     │
│   A) OAuth 2.0                                  │
│   B) JWT                                        │
│   C) Session-based                              │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ User: "B, and by the way, add refresh token     │
│        support"                                 │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ CORTEX: (Internal Processing)                   │
│                                                 │
│ AnswerParser:                                   │
│   - Direct answer: JWT                          │
│   - Additional context: ["refresh token",       │
│     "add", "support"]                           │
│   - Implied answers: {q3: "yes"}                │
│   - Confidence: {q3: 0.95}                      │
│                                                 │
│ QuestionFilter:                                 │
│   - Question 1: ✓ Answered (JWT)                │
│   - Question 3: ✓ Skip (implied, 95% conf)      │
│   - Question 2: ? Still needed                  │
│   - Question 4: ? Still needed                  │
│   - Question 5: X Skip (depends on Q4)          │
│                                                 │
│ Next question: Q2 (skip Q3)                     │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ CORTEX: "Great! I understood you want refresh   │
│          tokens too."                           │
│                                                 │
│ Question 2/5:                                   │
│ Keep existing user schema or redesign?          │
│   A) Keep existing                              │
│   B) Redesign from scratch                      │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ User: "A"                                       │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ CORTEX: Question 3/5:                           │
│ Support social login (OAuth providers)?         │
│   A) Yes                                        │
│   B) No                                         │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ User: "done"                                    │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ CORTEX: "Perfect! I have enough info."          │
│                                                 │
│ 📋 IMPLEMENTATION PLAN                          │
│ (Assumes no social login based on "done")       │
└─────────────────────────────────────────────────┘
```

**Questions Asked:** 3/5 (40% reduction)
**Questions Skipped:** Q3 (answered in context), Q5 (dependent on Q4)

#### Example 3: Ambiguous Context (Clarification Needed)

**Scenario:** User mentions something unclear, CORTEX asks for confirmation.

```
┌─────────────────────────────────────────────────┐
│ User: "Add some kind of tokens"                 │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ CORTEX: Question 1/5:                           │
│ What type of token-based authentication?        │
│   A) JWT (JSON Web Tokens)                      │
│   B) OAuth 2.0 access tokens                    │
│   C) Custom token system                        │
└─────────────────────────────────────────────────┘
```

**Reason:** "Some kind of tokens" is too ambiguous (confidence < 60%), so CORTEX asks for clarification instead of assuming.

---

### Edge Cases & Handling

#### 1. Conflicting Information

**Scenario:**
- Question 1: "Keep schema?" → User: "Yes"
- Question 3: User mentions "redesign user table"

**Handling:**
```python
if self._detect_conflict(context):
    # Ask confirmation question
    return Question(
        text="I noticed a potential conflict. Earlier you said keep "
             "the schema, but just mentioned redesigning the user table. "
             "Which do you prefer?",
        type=QuestionType.MULTIPLE_CHOICE,
        options=["Keep schema", "Redesign user table", "Hybrid approach"]
    )
```

#### 2. Low Confidence Inference

**Scenario:**
- User says: "Maybe add refresh stuff?"
- Confidence: 0.62 (below 0.85 threshold)

**Handling:**
```python
if confidence < self.threshold:
    # Don't skip, ask for confirmation
    return Question(
        text="I think you mentioned refresh tokens - is that right?",
        type=QuestionType.YES_NO
    )
```

#### 3. Implied Negative Answer

**Scenario:**
- User provides complete info about JWT but never mentions OAuth

**Handling:**
```python
# If user is specific about one option and silent on others
# AND we're past the question budget (4/5 questions)
# Assume negative for unmentioned topics
implied_answers["social_login"] = "no"
confidence["social_login"] = 0.70  # Medium confidence
```

---

### Benefits & Metrics

**User Experience Benefits:**
- ⚡ **Faster conversations:** Average 2-3 questions instead of 5
- 🎯 **More natural:** Users can "ramble" and CORTEX extracts info
- 😊 **Less frustration:** No redundant questions
- 🧠 **Feels smarter:** CORTEX "remembers" what user said

**Technical Metrics:**
- **Question Efficiency Rate:** (Questions asked) / (Total potential questions)
  - Target: < 60% (ask less than 3 out of 5 questions on average)
- **Context Extraction Accuracy:** Correct implied answers / Total implied answers
  - Target: > 85%
- **User Satisfaction:** Survey rating after interactive sessions
  - Target: > 4.5/5.0

**Example Metrics After 100 Sessions:**
```yaml
interactive_planning_metrics:
  total_sessions: 100
  average_questions_asked: 2.8
  average_questions_skipped: 2.2
  question_efficiency_rate: 0.56  # 56% (good!)
  
  context_extraction:
    total_implied_answers: 180
    correct_implied_answers: 156
    accuracy: 0.867  # 86.7% (above target!)
  
  user_satisfaction:
    average_rating: 4.7
    would_use_again: 0.94
```

---

## 🧠 Tier 1 Memory Integration

### New Conversation Type: Interactive Planning Session

**Schema Extension:**
```python
class InteractivePlanningSession:
    session_id: str                    # UUID
    conversation_id: str               # Links to parent conversation
    started_at: datetime
    completed_at: Optional[datetime]
    status: str                        # "in_progress|completed|abandoned"
    
    original_request: str              # Initial user request
    ambiguity_score: float             # 0-100% detected ambiguity
    
    questions_asked: List[Question]    # All questions asked
    questions_skipped: List[Question]  # Questions skipped via context (NEW)
    user_answers: Dict[str, str]       # Question ID -> direct answer
    implied_answers: Dict[str, str]    # Question ID -> implied answer (NEW)
    answer_confidence: Dict[str, float] # Question ID -> confidence score (NEW)
    question_count: int                # How many questions actually asked
    total_potential_questions: int     # Total questions that could be asked (NEW)
    
    final_plan: Optional[Plan]         # Generated plan
    plan_approved: bool                # User approved?
    implementation_started: bool       # Began execution?
    
    user_preferences_learned: Dict     # Patterns learned this session
```

**Storage:**
```json
{
  "session_id": "uuid-abc-123",
  "conversation_id": "conv-xyz-789",
  "started_at": "2025-11-09T10:30:00Z",
  "completed_at": "2025-11-09T10:42:00Z",
  "status": "completed",
  
  "original_request": "refactor authentication system",
  "ambiguity_score": 78.5,
  
  "questions_asked": [
    {
      "id": "q1",
      "text": "What authentication strategy?",
      "type": "multiple_choice",
      "options": ["OAuth 2.0", "JWT", "Session"],
      "priority": 5
    },
    {
      "id": "q2",
      "text": "Keep existing user schema?",
      "type": "yes_no",
      "priority": 4
    }
  ],
  
  "questions_skipped": [
    {
      "id": "q3",
      "text": "Need refresh token support?",
      "type": "yes_no",
      "reason": "implied from context in answer to q1",
      "confidence": 0.95
    }
  ],
  
  "user_answers": {
    "q1": "JWT",
    "q2": "yes"
  },
  
  "implied_answers": {
    "q3": "yes"
  },
  
  "answer_confidence": {
    "q3": 0.95
  },
  
  "question_count": 2,
  "total_potential_questions": 5,
  "final_plan": { /* plan object */ },
  "plan_approved": true,
  "implementation_started": true,
  
  "user_preferences_learned": {
    "prefers_jwt": true,
    "conservative_schema_changes": true,
    "mentions_refresh_tokens_proactively": true
  }
}
```

---

## 📊 Tier 2 Knowledge Graph Enhancement

### Learning from Interactive Sessions

**Pattern Recognition:**
```yaml
interactive_planning_patterns:
  authentication_projects:
    common_preferences:
      - auth_type: "JWT"
        frequency: 0.87
        confidence: "high"
      
      - schema_preservation: true
        frequency: 0.92
        confidence: "very_high"
    
    typical_questions_needed: 3
    average_planning_time: "12 minutes"
    success_rate: 0.94
  
  architecture_changes:
    common_preferences:
      - backward_compatibility: true
        frequency: 0.95
        confidence: "very_high"
      
      - phased_rollout: true
        frequency: 0.78
        confidence: "high"
    
    typical_questions_needed: 5
    average_planning_time: "18 minutes"
    success_rate: 0.89

user_preference_evolution:
  - timestamp: "2025-11-09"
    learned: "user prefers interactive mode for auth changes"
    confidence: 0.95
    source: "3 consecutive interactive planning sessions"
  
  - timestamp: "2025-11-08"
    learned: "user typically answers 3-4 questions then says 'done'"
    confidence: 0.82
    source: "observed pattern across 5 sessions"
```

---

## 🔌 New Command Structure (CORTEX 2.1)

### Expanded Entry Point Commands

| Command | Natural Language | Intent | Agent(s) |
|---------|------------------|--------|----------|
| `/CORTEX, refresh cortex story` | "refresh the story"<br>"update story" | STORY | Documenter |
| `/CORTEX, let's plan a feature` | "let's plan"<br>"plan feature" | PLAN | Interactive Planner → Work Planner |
| `/CORTEX, architect a solution` | "let's design architecture"<br>"architect this" | ARCHITECT | Architect → Interactive Planner |
| `/CORTEX, refactor this module` | "let's refactor"<br>"refactor this" | REFACTOR | Interactive Planner → Executor |
| `/CORTEX, run brain protection` | "check brain protection"<br>"validate brain" | VALIDATE | Health Validator |
| `/CORTEX, run tests` | "run tests"<br>"test this" | TEST | Tester |
| `/CORTEX, generate documentation` | "generate docs"<br>"document this" | DOCUMENT | Documenter |

### Command Registration

**Plugin System:**
```python
# In command_registry.py
CORTEX_2_1_COMMANDS = {
    CommandMetadata(
        command="/refresh-story",
        natural_language_equivalent="refresh the cortex story",
        plugin_id="core",
        description="Refresh and update CORTEX story documentation",
        aliases=["/story", "/update-story"]
    ),
    
    CommandMetadata(
        command="/plan-feature",
        natural_language_equivalent="let's plan a feature",
        plugin_id="interactive_planner",
        description="Interactive feature planning with guided questions",
        aliases=["/plan", "/collaborate"]
    ),
    
    CommandMetadata(
        command="/architect",
        natural_language_equivalent="architect a solution",
        plugin_id="interactive_planner",
        description="Collaborative architecture design",
        aliases=["/design", "/architecture"]
    ),
    
    CommandMetadata(
        command="/refactor",
        natural_language_equivalent="refactor this module",
        plugin_id="interactive_planner",
        description="Interactive refactoring with clarifying questions",
        aliases=["/refactor-module"]
    ),
    
    CommandMetadata(
        command="/brain-protect",
        natural_language_equivalent="run brain protection",
        plugin_id="brain_protector",
        description="Validate brain protection rules",
        aliases=["/validate-brain", "/check-brain"]
    ),
    
    CommandMetadata(
        command="/run-tests",
        natural_language_equivalent="run tests",
        plugin_id="tester",
        description="Execute test suite",
        aliases=["/test", "/tests"]
    ),
    
    CommandMetadata(
        command="/generate-docs",
        natural_language_equivalent="generate documentation",
        plugin_id="documenter",
        description="Auto-generate project documentation",
        aliases=["/docs", "/document"]
    ),
}
```

---

## 🧪 Implementation Phases

### Phase 1: Core Infrastructure (Week 1)

**Goal:** Build interactive planning agent foundation

**Tasks:**
1. Create `InteractivePlannerAgent` class
2. Implement ambiguity detection
3. Build question generator utility
4. Add Tier 1 memory schema for sessions
5. Unit tests for question generation

**Deliverables:**
- ✅ `src/cortex_agents/right_brain/interactive_planner.py`
- ✅ `src/cortex_agents/right_brain/question_generator.py`
- ✅ Tier 1 schema migration
- ✅ Test coverage: 85%+

### Phase 2: Conversation Flow (Week 2)

**Goal:** Implement question-answer loop

**Tasks:**
1. Build conversation state machine
2. Implement user control commands (skip, done, back)
3. Add progress tracking (Question 1/5)
4. Create plan generation from answers
5. Integration tests for full flow

**Deliverables:**
- ✅ State machine implementation
- ✅ User control handlers
- ✅ Plan generation logic
- ✅ Integration tests

### Phase 3: Command Router Integration (Week 2)

**Goal:** Hook into CORTEX command system

**Tasks:**
1. Register new commands in command registry
2. Update command router
3. Add natural language equivalents
4. Update CORTEX.prompt.md documentation
5. Test command routing

**Deliverables:**
- ✅ 7 new commands registered
- ✅ Router integration complete
- ✅ Documentation updated
- ✅ E2E tests passing

### Phase 4: Tier 2 Learning (Week 3)

**Goal:** User preference memory and learning

**Tasks:**
1. Extend knowledge graph schema
2. Implement preference extraction
3. Build pattern recognition
4. Add adaptive questioning (uses learned preferences)
5. Test learning over time

**Deliverables:**
- ✅ Knowledge graph extensions
- ✅ Preference learning system
- ✅ Adaptive behavior
- ✅ Long-term learning tests

### Phase 5: Polish & Documentation (Week 4)

**Goal:** Production-ready release

**Tasks:**
1. User experience refinements
2. Error handling and edge cases
3. Performance optimization
4. Comprehensive documentation
5. Migration guide from 2.0 to 2.1

**Deliverables:**
- ✅ Polished UX
- ✅ Error handling complete
- ✅ Performance benchmarks
- ✅ User documentation
- ✅ Migration guide

---

## 🎯 Success Metrics

### Quantitative Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Ambiguity detection accuracy** | >80% | User confirms plan matches intent |
| **Questions needed per session** | 3-5 average | Logged in Tier 1 memory |
| **User satisfaction** | >4/5 rating | Post-session feedback |
| **Plan approval rate** | >85% | User says "yes" vs "modify" |
| **Rework reduction** | >60% | Compare to non-interactive plans |
| **Session completion rate** | >90% | Sessions not abandoned |

### Qualitative Metrics

- ✅ Users feel in control of planning
- ✅ Questions are relevant and clear
- ✅ Plans are more accurate
- ✅ Reduced frustration from misunderstood requirements
- ✅ Natural conversation flow (not robotic)

---

## 🔒 Brain Protection Integration

### New Instinct Rules

**Location:** `cortex-brain/brain-protection-rules.yaml`

```yaml
# CORTEX 2.1 Interactive Planning Rules
interactive_planning:
  max_questions_per_session: 5
  
  question_generation:
    - rule: "Never ask questions that can be inferred from context"
      severity: "warning"
      
    - rule: "Always provide sensible defaults for optional questions"
      severity: "warning"
      
    - rule: "Prioritize critical questions first"
      severity: "error"
  
  user_control:
    - rule: "Must respect 'skip', 'done', and 'abort' commands immediately"
      severity: "critical"
      
    - rule: "Never force user to answer all questions"
      severity: "critical"
  
  memory:
    - rule: "Must save incomplete sessions to Tier 1 for resume capability"
      severity: "error"
      
    - rule: "Must learn preferences after 3+ similar sessions"
      severity: "warning"
```

---

## 🧪 Testing Strategy

### Unit Tests

**Location:** `tests/tier2/test_interactive_planner.py`

```python
def test_ambiguity_detection():
    """Test detecting ambiguous vs clear requests"""
    pass

def test_question_generation():
    """Test generating relevant questions"""
    pass

def test_answer_processing():
    """Test processing user answers correctly"""
    pass

def test_max_question_limit():
    """Test enforcing 5 question maximum"""
    pass

def test_user_preference_learning():
    """Test learning patterns from sessions"""
    pass
```

### Integration Tests

**Location:** `tests/integration/test_interactive_planning_flow.py`

```python
def test_full_planning_session():
    """Test complete question-answer-plan flow"""
    pass

def test_early_termination():
    """Test user saying 'done' before all questions"""
    pass

def test_session_resumption():
    """Test resuming interrupted planning session"""
    pass

def test_preference_adaptation():
    """Test adapting questions based on learned preferences"""
    pass
```

### E2E Tests

**Location:** `tests/e2e/test_cortex_2_1_commands.py`

```python
def test_plan_feature_command():
    """Test /plan-feature command end-to-end"""
    pass

def test_all_new_commands():
    """Test all 7 new CORTEX 2.1 commands"""
    pass
```

---

## 📚 Documentation Updates

### Files to Update

1. **`.github/prompts/CORTEX.prompt.md`**
   - Add 7 new commands
   - Update command table
   - Add interactive planning section

2. **`prompts/shared/agents-guide.md`**
   - Document Interactive Planner agent
   - Update agent coordination flow

3. **`docs/COMMAND-QUICK-REFERENCE.md`**
   - Add new command syntax
   - Add examples

4. **`README.md`**
   - Highlight CORTEX 2.1 features
   - Update version number

5. **New File:** `docs/guides/INTERACTIVE-PLANNING-GUIDE.md`
   - User guide for interactive planning
   - Best practices
   - Examples

---

## 🚀 Rollout Plan

### Phase 1: Internal Testing (Week 1-2)
- ✅ Core team testing
- ✅ Fix critical bugs
- ✅ Gather initial feedback

### Phase 2: Beta Release (Week 3)
- ✅ Limited beta to 10 users
- ✅ Monitor usage metrics
- ✅ Refine question quality

### Phase 3: Production Release (Week 4)
- ✅ Public release of CORTEX 2.1
- ✅ Documentation complete
- ✅ Migration guide published

### Phase 4: Learning Period (Month 2)
- ✅ Gather usage patterns
- ✅ Refine preference learning
- ✅ Optimize question generation

---

## 🔄 Migration from CORTEX 2.0 to 2.1

### Breaking Changes

**None!** CORTEX 2.1 is backward compatible.

### New Features

- ✅ Interactive planning (opt-in)
- ✅ 7 new commands
- ✅ User preference learning

### Migration Steps

1. **Pull latest code:**
   ```bash
   git pull origin CORTEX-2.1
   ```

2. **Run database migration:**
   ```bash
   python scripts/migrate_to_2_1.py
   ```

3. **Update configuration:**
   ```bash
   # Add to cortex.config.json
   {
     "interactive_planning": {
       "enabled": true,
       "max_questions": 5,
       "learn_preferences": true
     }
   }
   ```

4. **Test new commands:**
   ```bash
   /CORTEX, let's plan a feature - test feature
   ```

---

## 🎯 Future Enhancements (CORTEX 2.2+)

### Potential Features

1. **Multi-Language Support**
   - Questions in user's preferred language
   - Localized command aliases

2. **Voice Mode**
   - Speak answers instead of typing
   - Integration with voice assistants

3. **Visual Planning**
   - Diagrams during planning
   - Interactive architecture visualization

4. **Team Collaboration**
   - Multiple users in planning session
   - Vote on answers

5. **AI-Generated Examples**
   - Show example implementations during planning
   - Preview code snippets

---

## 📊 Appendix: Example Sessions

### Example 1: Simple Feature (2 Questions)

```
User: /CORTEX, let's plan a feature - add dark mode

CORTEX: Question 1/5: Which components need dark mode?
  A) All components
  B) Specific pages (specify)
  C) User preference toggle

User: A

CORTEX: Question 2/5: Include system preference detection?
  A) Yes (auto-detect OS theme)
  B) No (manual toggle only)

User: A

CORTEX: Perfect! Here's the plan:
  - Add theme context provider
  - Implement dark mode CSS variables
  - Add system preference detection
  - Update all components

Proceed? yes
```

### Example 2: Complex Refactor (5 Questions)

```
User: /CORTEX, let's plan a feature - migrate to microservices

CORTEX: This is a complex change. I'll ask up to 5 questions.

Question 1/5: Which monolith components to extract?
  A) All at once
  B) Phase by phase (specify order)
  C) High-priority services first

User: C

CORTEX: Question 2/5: What's the highest priority service?
  (Free text)

User: Authentication service

CORTEX: Question 3/5: Communication pattern?
  A) REST APIs
  B) GraphQL
  C) gRPC
  D) Message queue (async)

User: done

CORTEX: I have enough! Here's the plan:
  - Extract authentication service first
  - Use REST APIs (common pattern)
  - Implement API gateway
  - Gradual migration strategy
  
Proceed? yes
```

---

## 🏁 Conclusion

CORTEX 2.1 introduces **collaborative intelligence** - the ability for CORTEX to partner with users in planning through guided conversation. This enhancement maintains CORTEX's efficiency for clear requests while adding powerful clarification capabilities for ambiguous scenarios.

**Key Benefits:**
- ✅ Better alignment on requirements
- ✅ Reduced implementation rework
- ✅ User feels in control
- ✅ Learns user preferences over time
- ✅ Backward compatible with CORTEX 2.0

**Next Steps:**
1. Review and approve design
2. Begin Phase 1 implementation
3. Set up beta testing program
4. Plan public release

---

*Design Document Version: 1.0*  
*Last Updated: November 9, 2025*  
*Status: Ready for Implementation Review*
