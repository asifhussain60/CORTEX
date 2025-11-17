# CORTEX 2.1 Context-Tracking Enhancement

**Date:** November 9, 2025  
**Status:** Design Updated  
**Impact:** Critical UX improvement for Interactive Planning feature

---

## 🎯 Problem Identified

**User Question:**
> "User: 'A' and btw add refresh token support. HOW WILL THIS AFFECT the next question?"

**Answer:**
CORTEX should be **smart enough to skip redundant questions** when the user already provides the answer in their natural language response.

**Without Context Tracking (Bad UX):**
```
CORTEX: "What auth strategy?"
User: "JWT, and by the way, add refresh token support"

CORTEX: "Keep existing schema?"
User: "Yes"

CORTEX: "Need refresh token support?" ❌ REDUNDANT!
User: (frustrated) "I already said that..."
```

**With Context Tracking (Good UX):**
```
CORTEX: "What auth strategy?"
User: "JWT, and by the way, add refresh token support"

CORTEX: "Great! I understood you want refresh tokens too."
CORTEX: "Keep existing schema?"
User: "Yes"

CORTEX: "Perfect! I have enough info."
📋 [Generates plan with JWT + refresh tokens + existing schema]
```

---

## 🏗️ Solution: Two-Component System

### 1. AnswerParser
**Location:** `src/cortex_agents/right_brain/answer_parser.py`

**Purpose:** Extract both direct answers AND additional context from natural language.

**Key Functions:**
- `parse(question, answer)` → Returns `ParsedAnswer`
- Extracts direct answer ("JWT")
- Extracts additional keywords ("refresh token", "add", "support")
- Maps keywords to potential question topics
- Generates confidence scores (0.0-1.0)

**Example:**
```python
# Input
answer = "JWT, and by the way, add refresh token support"

# Output
ParsedAnswer(
    direct_answer="JWT",
    additional_context=["refresh token", "add", "support"],
    implied_answers={"q3_refresh_tokens": "yes"},
    confidence={"q3_refresh_tokens": 0.95}
)
```

---

### 2. QuestionFilter
**Location:** `src/cortex_agents/right_brain/question_filter.py`

**Purpose:** Skip questions that have already been answered via context.

**Key Logic:**
- Check if question has direct answer
- Check if question has implied answer with high confidence (>85%)
- Check if user preference (Tier 2) answers question
- Return filtered list of questions still needing to be asked

**Example:**
```python
# Before filtering
remaining_questions = [Q1, Q2, Q3, Q4, Q5]  # 5 questions

# After user says "JWT with refresh tokens"
context = {
    "direct_answers": {"q1": "JWT"},
    "implied_answers": {"q3": "yes"},
    "confidence": {"q3": 0.95}
}

# After filtering
filtered = filter_questions(remaining_questions, context)
# Result: [Q2, Q4, Q5]  # Q1 directly answered, Q3 skipped (95% confidence)
```

---

## 📊 Updated Metrics

### New Success Metrics for Context Tracking

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Question Efficiency Rate** | <60% | (Questions asked) / (Total potential questions) |
| **Context Extraction Accuracy** | >85% | Correct implied answers / Total implied answers |
| **Question Skip Rate** | >40% | Questions skipped via context / Total questions |

**Example after 100 sessions:**
```yaml
interactive_planning_metrics:
  total_sessions: 100
  average_questions_asked: 2.8      # Instead of 5
  average_questions_skipped: 2.2    # 44% skip rate ✅
  question_efficiency_rate: 0.56    # 56% (below 60% target ✅)
  
  context_extraction:
    total_implied_answers: 180
    correct_implied_answers: 156
    accuracy: 0.867                  # 86.7% (above 85% target ✅)
  
  user_satisfaction:
    average_rating: 4.7              # (above 4.5 target ✅)
    would_use_again: 0.94
```

---

## 📝 Updated Tier 1 Schema

**New Fields in `InteractivePlanningSession`:**
```python
questions_skipped: List[Question]      # NEW - Questions skipped via context
implied_answers: Dict[str, str]        # NEW - Question ID → implied answer
answer_confidence: Dict[str, float]    # NEW - Question ID → confidence (0-1)
total_potential_questions: int         # NEW - Total questions that could be asked
```

**Storage Example:**
```json
{
  "questions_asked": [
    {"id": "q1", "text": "What auth strategy?"},
    {"id": "q2", "text": "Keep existing schema?"}
  ],
  "questions_skipped": [
    {
      "id": "q3",
      "text": "Need refresh tokens?",
      "reason": "implied from context in answer to q1",
      "confidence": 0.95
    }
  ],
  "user_answers": {"q1": "JWT", "q2": "yes"},
  "implied_answers": {"q3": "yes"},
  "answer_confidence": {"q3": 0.95},
  "question_count": 2,
  "total_potential_questions": 5
}
```

---

## 🚀 Implementation Changes

### Updated Week 1-2 Deliverables

**NEW Components:**
3. ✅ `AnswerParser` utility
   - Extract direct + context from natural language
   - Map context to question topics
   - Generate confidence scores

4. ✅ `QuestionFilter` utility
   - Skip redundant questions (confidence threshold: 85%)
   - Log skipped questions for transparency
   - Apply user preferences from Tier 2

**NEW Tests:**
- Test answer parsing (direct + context extraction)
- Test question filtering (skip logic)
- Test confidence scoring
- Test >50% skip rate in test scenarios

**Updated Success Criteria:**
- Can extract context from natural language answers
- Can skip redundant questions (>50% skip rate in tests)
- Can store/retrieve planning sessions with context data

---

## 💡 Edge Cases Handled

### 1. Conflicting Information
**Scenario:** User says "keep schema" but later mentions "redesign user table"

**Solution:** Ask confirmation question to resolve conflict

### 2. Low Confidence Inference
**Scenario:** User says "maybe add refresh stuff?" (confidence: 0.62)

**Solution:** Don't skip question, ask for confirmation instead

### 3. Ambiguous Context
**Scenario:** User says "add some kind of tokens" (too vague)

**Solution:** Ask clarification question with multiple choice options

---

## 🎉 Benefits

### User Experience
- ⚡ **Faster conversations:** 2-3 questions instead of 5 on average
- 🎯 **More natural:** Users can "ramble" and CORTEX extracts info intelligently
- 😊 **Less frustration:** No redundant questions asking for info already provided
- 🧠 **Feels smarter:** CORTEX "remembers" what user said earlier in the answer

### Technical
- 📊 **Measurable improvement:** Question efficiency rate, skip rate, extraction accuracy
- 🧪 **Testable:** Clear success criteria and metrics
- 🔄 **Learns over time:** Tier 2 patterns improve context extraction
- 📈 **Scales well:** Works for 5 questions or 50 questions

---

## 📚 Updated Documentation

### Files Modified

1. **`docs/design/CORTEX-2.1-INTERACTIVE-PLANNING.md`**
   - Added 500+ line section: "Context-Aware Question Management"
   - New components: AnswerParser, QuestionFilter
   - Updated Tier 1 schema with context-tracking fields
   - Added conversation examples with smart question skipping
   - Added edge cases and handling strategies
   - Added benefits and metrics

2. **`docs/CORTEX-2.1-IMPLEMENTATION-ROADMAP.md`**
   - Added AnswerParser and QuestionFilter to Week 1-2 tasks
   - Updated deliverables to include context-tracking utilities
   - Updated success criteria with skip rate targets
   - Added 3 new metrics to success metrics table

---

## 🎯 Next Steps

1. ✅ Design documents updated with context-tracking
2. ⏳ Commit changes to GitHub
3. ⏳ Begin implementation (Week 1-2 of CORTEX 2.1)
4. ⏳ Test context extraction accuracy (target >85%)
5. ⏳ Test question skip rate (target >40%)
6. ⏳ User testing with real scenarios

---

## 🔗 Related Documents

- **Interactive Planning Design:** `docs/design/CORTEX-2.1-INTERACTIVE-PLANNING.md`
- **Implementation Roadmap:** `docs/CORTEX-2.1-IMPLEMENTATION-ROADMAP.md`
- **Complete CORTEX 2.1 Summary:** `cortex-brain/CORTEX-2.1-COMPLETE-SUMMARY.md`

---

*This enhancement ensures CORTEX 2.1 Interactive Planning feels truly intelligent and context-aware, dramatically improving user experience and reducing conversation friction.*

**Status:** ✅ Design Complete | ⏳ Implementation Pending  
**Priority:** HIGH (Critical UX feature)  
**Complexity:** MEDIUM (Natural language processing + confidence scoring)  
**Est. Implementation:** 3-4 days (part of Week 1-2)
