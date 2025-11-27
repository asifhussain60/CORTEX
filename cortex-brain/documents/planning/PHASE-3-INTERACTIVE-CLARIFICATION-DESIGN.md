# Phase 3: Interactive Clarification System - Architecture Design

**Version:** 1.0  
**Date:** 2025-11-27  
**Author:** Asif Hussain  
**Status:** Design Complete, Implementation In Progress

---

## 1. Executive Summary

The Interactive Clarification System enables multi-round conversations with users to eliminate ambiguity from work item requirements before implementation begins. This system integrates with the ADO Work Item Orchestrator to provide intelligent questioning, letter-based choice selection, and context-aware clarification prompts.

**Key Goals:**
- ✅ Eliminate ambiguous requirements through structured questioning
- ✅ Provide letter-based choice format (1a, 2c, 3b) for easy selection
- ✅ Maintain conversation context across multiple rounds
- ✅ Integrate seamlessly with existing planning workflow

---

## 2. System Architecture

### 2.1 Core Components

```
┌─────────────────────────────────────────────────────────────┐
│           ADOWorkItemOrchestrator (Entry Point)             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. Create Work Item (with basic info)              │   │
│  │  2. Detect Ambiguities → Trigger Clarification      │   │
│  │  3. Enter Clarification Loop                        │   │
│  │  4. Update Work Item with Clarified Requirements    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│           ClarificationEngine (Core Logic)                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Ambiguity Detection                              │   │
│  │  • Question Generation                              │   │
│  │  • Choice Formatting (letter-based)                 │   │
│  │  • Response Validation                              │   │
│  │  • Context Integration                              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│         ConversationState (State Management)                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Round Tracking (1, 2, 3, ...)                    │   │
│  │  • History Storage (questions + answers)            │   │
│  │  • Context Preservation                             │   │
│  │  • User Choices Log                                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Data Structures

**ConversationState** (Dataclass):
```python
@dataclass
class ClarificationChoice:
    letter: str           # "1a", "2c", "3b"
    text: str            # Choice description
    category: str        # "scope", "technical", "ui", etc.

@dataclass
class ClarificationRound:
    round_number: int
    question: str
    choices: List[ClarificationChoice]
    user_response: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ConversationState:
    work_item_id: str
    rounds: List[ClarificationRound]
    context: Dict[str, Any]  # Accumulated clarifications
    is_complete: bool = False
    total_ambiguities_detected: int = 0
    total_ambiguities_resolved: int = 0
```

---

## 3. Clarification Workflow

### 3.1 Trigger Conditions

Clarification is triggered when:
1. **Vague Language Detected:** "maybe", "probably", "might", "could be"
2. **Missing Details:** No acceptance criteria, incomplete description
3. **Technical Ambiguity:** Unclear architecture, unspecified dependencies
4. **UI/UX Ambiguity:** No mockups, unclear user flow
5. **Security Concerns:** No security considerations mentioned
6. **Manual Trigger:** User explicitly requests clarification

### 3.2 Multi-Round Conversation Flow

```
Round 1: Scope Clarification
┌─────────────────────────────────────────────────────────┐
│ Question: What is the primary scope of this feature?    │
│                                                          │
│ Choices:                                                 │
│  1a. New feature (greenfield development)               │
│  1b. Enhancement to existing feature                    │
│  1c. Bug fix with refactoring                           │
│  1d. Technical debt reduction                           │
│                                                          │
│ User: 1b                                                 │
└─────────────────────────────────────────────────────────┘
                        ↓
Round 2: Technical Details
┌─────────────────────────────────────────────────────────┐
│ Question: Which component needs enhancement?            │
│                                                          │
│ Choices:                                                 │
│  2a. Frontend UI components                             │
│  2b. Backend API endpoints                              │
│  2c. Database schema                                    │
│  2d. Multiple components (specify)                      │
│                                                          │
│ User: 2a, 2b                                            │
└─────────────────────────────────────────────────────────┘
                        ↓
Round 3: User Impact
┌─────────────────────────────────────────────────────────┐
│ Question: What is the expected user impact?             │
│                                                          │
│ Choices:                                                 │
│  3a. High (core workflow change)                        │
│  3b. Medium (visible but not critical)                  │
│  3c. Low (background improvement)                       │
│                                                          │
│ User: 3b                                                 │
└─────────────────────────────────────────────────────────┘
                        ↓
Context Integration & Work Item Update
```

### 3.3 Letter-Based Choice Format

**Format:** `[round_number][letter]`

**Examples:**
- Round 1: `1a`, `1b`, `1c`, `1d`, `1e`
- Round 2: `2a`, `2b`, `2c`, `2d`
- Round 3: `3a`, `3b`, `3c`

**Multi-Select Support:** `1a, 1c` or `2b, 2d, 2e`

**Validation Rules:**
- Must start with current round number
- Letter must be in valid choice range
- Comma-separated for multi-select
- Case-insensitive parsing

---

## 4. Ambiguity Detection Engine

### 4.1 Detection Patterns

**Vague Language:**
```python
VAGUE_PATTERNS = [
    r'\b(maybe|perhaps|possibly|might|could be|probably)\b',
    r'\b(some|few|several|various|multiple)\b',
    r'\b(approximately|around|about|roughly)\b',
    r'\b(etc|and so on|among others)\b'
]
```

**Missing Information:**
```python
REQUIRED_FIELDS = {
    'acceptance_criteria': 'What are the success criteria?',
    'technical_approach': 'What is the technical implementation approach?',
    'user_flow': 'What is the expected user interaction flow?',
    'dependencies': 'What are the external dependencies?'
}
```

**Technical Clarity:**
```python
TECHNICAL_AMBIGUITY = [
    'no architecture specified',
    'unclear API contract',
    'unspecified database changes',
    'missing error handling strategy'
]
```

### 4.2 Ambiguity Scoring

Each ambiguity is scored 0-10:
- **0-3:** Low priority (can defer)
- **4-6:** Medium priority (should clarify)
- **7-10:** High priority (must clarify)

**Scoring Factors:**
- Vague language count × 2
- Missing required fields × 3
- Technical ambiguity count × 2.5
- Security concerns × 3

---

## 5. Question Generation Strategy

### 5.1 Question Categories

1. **Scope Questions** (Round 1)
   - Feature type (new/enhancement/fix)
   - Primary goal
   - Success metrics

2. **Technical Questions** (Round 2)
   - Architecture decisions
   - Technology choices
   - Integration points

3. **UI/UX Questions** (Round 3)
   - User flow details
   - Visual design elements
   - Interaction patterns

4. **Quality Questions** (Round 4)
   - Testing strategy
   - Performance requirements
   - Security considerations

### 5.2 Intelligent Question Ordering

Questions are prioritized by:
1. **Blocking Issues:** Cannot proceed without answer
2. **High-Risk Areas:** Security, data integrity, user impact
3. **Dependencies:** Questions that unlock other questions
4. **Complexity:** Simple questions first, complex later

---

## 6. Context Integration

### 6.1 Context Accumulation

After each round, update context:

```python
context = {
    'scope': {
        'type': 'enhancement',
        'components': ['frontend', 'backend'],
        'impact': 'medium'
    },
    'technical': {
        'frontend_changes': ['HostControlPanel.razor', 'UserService.cs'],
        'backend_changes': ['UserController.cs', 'UserRepository.cs'],
        'database_changes': []
    },
    'quality': {
        'test_coverage_required': True,
        'security_review_required': False,
        'performance_test_required': False
    }
}
```

### 6.2 Work Item Enrichment

Updated work item includes:

```markdown
## Clarified Requirements

### Scope (Round 1)
- Feature Type: Enhancement to existing feature
- Primary Goal: Improve user authentication flow
- Success Metric: 95% login success rate

### Technical Approach (Round 2)
- Frontend: Update HostControlPanel.razor with new auth UI
- Backend: Enhance UserController.cs with token refresh logic
- Database: No schema changes required

### User Impact (Round 3)
- Impact Level: Medium (visible but not critical)
- User Flow: Login → Token refresh → Dashboard
- Expected Downtime: None

### Quality Requirements (Round 4)
- Test Coverage: 80% minimum
- Security Review: Not required (standard auth flow)
- Performance Test: Login time <2 seconds
```

---

## 7. Integration Points

### 7.1 ADOWorkItemOrchestrator Integration

**New Method:**
```python
def clarify_requirements(self, work_item_id: str) -> Tuple[bool, str, Dict]:
    """
    Multi-round clarification conversation.
    
    Returns:
        (success, message, clarified_context)
    """
```

**Workflow Update:**
```python
# In create_work_item()
if self._needs_clarification(metadata):
    success, message, context = self.clarify_requirements(work_item_id)
    if success:
        metadata.description += self._format_clarifications(context)
        self._update_yaml_with_clarifications(work_item_id, context)
```

### 7.2 YAML Storage

Add clarification section to YAML:

```yaml
clarifications:
  rounds: 4
  completed: true
  context:
    scope:
      type: enhancement
      components: [frontend, backend]
    technical:
      frontend_changes: [HostControlPanel.razor]
      backend_changes: [UserController.cs]
    quality:
      test_coverage_required: true
```

---

## 8. Testing Strategy

### 8.1 Unit Tests

- `test_ambiguity_detection()` - Pattern matching works
- `test_question_generation()` - Questions match ambiguity type
- `test_choice_formatting()` - Letter-based format correct
- `test_response_validation()` - Valid/invalid responses
- `test_multi_select()` - Multiple choices parsed correctly

### 8.2 Integration Tests

- `test_single_round_clarification()` - One round workflow
- `test_multi_round_clarification()` - Complete 4-round workflow
- `test_context_accumulation()` - Context builds correctly
- `test_work_item_enrichment()` - Description updated properly
- `test_yaml_storage()` - Clarifications stored in YAML

### 8.3 End-to-End Tests

- `test_full_workflow()` - Create → Clarify → Approve → Complete
- `test_resume_with_clarifications()` - Resume work item with context
- `test_clarification_report()` - Generate readable report

---

## 9. User Experience

### 9.1 Prompt Format

```
🔍 CORTEX - Interactive Clarification (Round 1 of 4)

I've detected some ambiguities in your work item description. Let's clarify them together.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Question: What is the primary scope of this feature?

Choices:
  1a. New feature (greenfield development)
  1b. Enhancement to existing feature
  1c. Bug fix with refactoring
  1d. Technical debt reduction

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please respond with the letter of your choice (e.g., "1b" or "1a, 1c" for multiple).
Type "skip" to skip this question, or "done" to finish clarification.

Your response:
```

### 9.2 Progress Tracking

Show progress after each round:

```
✅ Round 1 Complete: Scope clarified (enhancement to existing feature)
⏳ Round 2 of 4: Technical approach...
```

---

## 10. Configuration

### 10.1 Clarification Rules (YAML)

**File:** `cortex-brain/config/clarification-rules.yaml`

```yaml
clarification_settings:
  max_rounds: 4
  min_rounds: 1
  auto_trigger_threshold: 6  # Ambiguity score 0-10
  
  ambiguity_detection:
    vague_language_weight: 2
    missing_fields_weight: 3
    technical_ambiguity_weight: 2.5
    security_concerns_weight: 3
  
  question_categories:
    - scope
    - technical
    - ui_ux
    - quality
  
  choice_format:
    pattern: "[round][letter]"
    multi_select_separator: ","
    case_sensitive: false
```

---

## 11. Performance Targets

- **Ambiguity Detection:** <100ms per work item
- **Question Generation:** <200ms per round
- **Response Validation:** <50ms per response
- **Context Integration:** <100ms per round
- **Total Round Time:** <500ms (excluding user input wait)

---

## 12. Success Metrics

**Phase 3 Complete When:**
- ✅ All ambiguity patterns detected correctly (95%+ accuracy)
- ✅ Letter-based choice system works flawlessly
- ✅ Multi-round conversations maintain context
- ✅ Work items enriched with clarifications
- ✅ YAML storage includes clarification data
- ✅ 15+ tests passing (100% coverage)
- ✅ Integration with ADOWorkItemOrchestrator complete
- ✅ Documentation complete

---

## 13. Implementation Plan

### Phase 3.1: Core Data Structures (30 min)
- Create ClarificationChoice dataclass
- Create ClarificationRound dataclass
- Create ConversationState dataclass
- Add to ado_work_item_orchestrator.py

### Phase 3.2: Ambiguity Detection Engine (60 min)
- Implement pattern matching
- Implement scoring algorithm
- Create ambiguity report generator
- Unit tests (5 tests)

### Phase 3.3: Question Generation System (60 min)
- Implement question templates
- Implement choice generator
- Implement letter-based formatting
- Unit tests (5 tests)

### Phase 3.4: Conversation Management (90 min)
- Implement round tracking
- Implement response validation
- Implement context accumulation
- Integration tests (5 tests)

### Phase 3.5: Orchestrator Integration (60 min)
- Add clarify_requirements() method
- Update create_work_item() workflow
- Update YAML generation
- Integration tests (3 tests)

### Phase 3.6: Documentation (30 min)
- Create user guide
- Create completion report
- Update progress tracker

**Total Time:** ~6 hours (within 8-10 hour estimate)

---

## 14. Next Steps

1. ✅ Design complete (this document)
2. ⏳ Implement core data structures
3. ⏳ Implement ambiguity detection
4. ⏳ Implement question generation
5. ⏳ Implement conversation management
6. ⏳ Integration with orchestrator
7. ⏳ Testing (15+ tests)
8. ⏳ Documentation

**Current Status:** Design complete, ready for implementation

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-27  
**Next Review:** After Phase 3 implementation complete
