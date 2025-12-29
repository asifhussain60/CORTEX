# 🧠 CORTEX LLM-Based Intent Classification (CORTEX 4.0)
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 Understanding & Scope

CORTEX currently uses text-based keyword matching for intent classification (keyword scoring with multi-word phrase detection). For CORTEX 4.0, we're transitioning to LLM-based intent classification to improve accuracy, handle natural language variations, and reduce maintenance overhead.

**Current System Analysis:**
- **Intent Router:** `src/cortex_agents/intent_router.py` - Keyword matching with scoring
- **Template Selector:** `src/utils/template_selector.py` - Priority-based keyword detection
- **Response Routing:** `cortex-brain/response-routing-rules.yaml` - 443 lines of keyword mappings
- **Coverage:** 50+ intent types across planning, coding, ADO, TDD, system operations

**Scope:**
- Design LLM-based intent classification architecture
- Plan backward-compatible migration strategy
- Identify integration points with existing systems
- Outline implementation phases

### ⚡ Approach & Considerations

**Key Challenges:**

1. **Performance:** LLM inference (100-500ms) vs keyword matching (<10ms)
2. **Cost:** API costs for intent classification on every request
3. **Reliability:** Fallback handling when LLM unavailable
4. **Accuracy:** Balancing precision vs recall across 50+ intents
5. **Context:** Leveraging conversation history and user patterns

**Opportunities:**

- **Natural Language Understanding:** Handle variations, synonyms, implicit intents
- **Multi-Intent Detection:** Identify composite requests requiring multiple orchestrators
- **Confidence Scoring:** Rich classification metadata for routing decisions
- **Learning:** Adapt to user communication patterns via Tier 2
- **Reduced Maintenance:** No manual keyword list updates

### 💬 Response

## Architecture Design

### 1. Hybrid Classification Strategy

```
User Request
    ↓
┌─────────────────────────────────────┐
│  Fast Path (< 10ms)                 │
│  - Keyword Pre-screening            │
│  - Exact command matching           │
│  - High-confidence patterns         │
└─────────────────────────────────────┘
    ↓ (if confidence < 80%)
┌─────────────────────────────────────┐
│  LLM Classification (100-500ms)     │
│  - Natural language understanding   │
│  - Multi-intent detection           │
│  - Contextual analysis              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Tier 2 Learning                    │
│  - Pattern storage                  │
│  - User-specific adaptation         │
│  - Feedback loop                    │
└─────────────────────────────────────┘
```

### 2. LLM Intent Classifier Architecture

**File:** `src/cortex_agents/llm_intent_classifier.py`

```python
class LLMIntentClassifier:
    """
    LLM-based intent classification with caching and fallback.
    
    Features:
    - Few-shot prompting with intent examples
    - Multi-intent detection (composite requests)
    - Confidence scoring per intent
    - Tier 2 caching for repeated patterns
    - Graceful degradation to keyword matching
    """
    
    def classify_intent(
        self, 
        request: AgentRequest,
        conversation_history: Optional[List[Dict]] = None
    ) -> IntentClassificationResult:
        """
        Classify user intent using LLM with contextual understanding.
        
        Args:
            request: User request
            conversation_history: Recent conversation turns (last 3-5)
        
        Returns:
            IntentClassificationResult with:
            - primary_intent: Main intent
            - secondary_intents: Additional detected intents (composite)
            - confidence: 0.0-1.0
            - reasoning: LLM's explanation
            - method: 'llm' | 'cache' | 'keyword_fallback'
        """
```

### 3. Prompt Engineering Strategy

**Intent Classification Prompt Template:**

```
You are CORTEX, an AI assistant with specialized agents for different tasks.

Analyze the user's request and identify the PRIMARY intent and any SECONDARY intents.

AVAILABLE INTENTS:
- PLAN: Feature planning, architecture design, comprehensive planning
- CODE: Implementation, coding tasks, feature creation
- TEST: Test creation, TDD workflow, test execution
- DEBUG: Debugging, error investigation, troubleshooting
- REFACTOR: Code restructuring, optimization, cleanup
- REVIEW: Code review, architecture review, quality assessment
- ADO: Azure DevOps work item creation/management
- GIT: Git operations, commits, branching
- ALIGN: System alignment, healthcheck, maintenance
- HELP: Command help, operation discovery
- SCREENSHOT: Image analysis, UI extraction
... (all 50+ intents)

USER REQUEST: "{user_message}"

CONVERSATION CONTEXT:
{conversation_history}

Respond in JSON format:
{
  "primary_intent": "intent_name",
  "primary_confidence": 0.95,
  "secondary_intents": [
    {"intent": "intent_name", "confidence": 0.70}
  ],
  "reasoning": "Brief explanation of classification",
  "key_indicators": ["phrase1", "phrase2"]
}
```

### 4. Integration Points

**A. IntentRouter Enhancement:**

```python
# src/cortex_agents/intent_router.py

def _classify_intent_with_rules(self, request: AgentRequest) -> IntentClassificationResult:
    """Enhanced classification with LLM support"""
    
    # Phase 1: Fast path (keyword pre-screening)
    fast_result = self._fast_keyword_classification(request)
    if fast_result.confidence >= 0.8:
        return fast_result
    
    # Phase 2: Check Tier 2 cache
    cached_result = self._check_tier2_cache(request)
    if cached_result:
        return cached_result
    
    # Phase 3: LLM classification
    if self.llm_classifier and self.llm_classifier.enabled:
        llm_result = self.llm_classifier.classify_intent(
            request,
            conversation_history=self._get_recent_history(request)
        )
        
        # Store in Tier 2 for future caching
        self._cache_classification(request, llm_result)
        
        return llm_result
    
    # Phase 4: Fallback to keyword only
    return fast_result
```

**B. Template Selector Integration:**

```python
# src/utils/template_selector.py

def select_template(self, user_input: str, context: Dict) -> SelectionResult:
    """Template selection with LLM intent support"""
    
    # Get intent classification from IntentRouter
    intent_result = self.intent_router.classify_intent(user_input)
    
    # Use intent confidence to guide template selection
    template = self._match_template_by_intent(
        intent_result.primary_intent,
        confidence=intent_result.primary_confidence
    )
    
    return SelectionResult(
        template_id=template,
        confidence=intent_result.primary_confidence,
        matched_intent=intent_result.primary_intent,
        orchestrator=self._get_orchestrator(intent_result)
    )
```

### 5. Performance Optimization

**Caching Strategy:**

1. **Tier 2 Pattern Cache:**
   - Store: (message_fingerprint, intent, confidence)
   - Retrieve: Fuzzy match on similar messages
   - TTL: 30 days with LRU eviction

2. **Session Cache:**
   - In-memory cache for current conversation
   - Exact string matches
   - Cleared on conversation end

3. **Intent Hierarchy:**
   - Common intents (help, plan, code) → always fast path
   - Admin intents (deploy, regenerate_prompts) → always fast path
   - Ambiguous requests → LLM classification

**Performance Targets:**

- Fast path (keyword): < 10ms (80% of requests)
- Cache hit: < 20ms (15% of requests)
- LLM classification: < 500ms (5% of requests)
- Overall P95: < 100ms

### 6. Backward Compatibility

**Phase 1 (CORTEX 3.9):**
- Add LLM classifier as **optional** component
- Default: Disabled (keyword-only)
- Config flag: `cortex.config.json → intent_classification.use_llm: false`
- Run in shadow mode (log LLM vs keyword accuracy)

**Phase 2 (CORTEX 3.9.5):**
- Enable LLM for **low-confidence** requests only
- Keyword confidence < 0.6 → trigger LLM
- Monitor accuracy improvements

**Phase 3 (CORTEX 4.0):**
- Default to hybrid approach (fast path + LLM)
- Keyword matching as fallback only
- Remove YAML keyword mappings (migrate to intent descriptions)

### 7. Cost Management

**API Cost Controls:**

1. **Free Tier Usage:**
   - Use GitHub Copilot's existing LLM context
   - Piggyback on active Copilot session
   - No additional API costs

2. **Rate Limiting:**
   - Max 100 LLM classifications/hour per user
   - Automatic fallback to keyword after limit

3. **Batch Classification:**
   - Queue low-priority classifications
   - Batch process during idle time

4. **Cost Monitoring:**
   - Track: classifications/day, cost/classification
   - Alert: >1000 classifications/day (investigate caching issues)

### 8. Multi-Intent Detection

**Composite Request Handling:**

Example: "Create a plan for user authentication, implement the login page, and write tests"

```json
{
  "primary_intent": "PLAN",
  "primary_confidence": 0.95,
  "secondary_intents": [
    {"intent": "CODE", "confidence": 0.85},
    {"intent": "TEST", "confidence": 0.80}
  ],
  "execution_strategy": "sequential",
  "orchestrator_chain": [
    {"orchestrator": "PlanningOrchestrator", "priority": 1},
    {"orchestrator": "ExecutorOrchestrator", "priority": 2},
    {"orchestrator": "TDDMasterOrchestrator", "priority": 3}
  ]
}
```

**Execution Strategies:**
- **Sequential:** Execute orchestrators in order (plan → code → test)
- **Parallel:** Independent tasks (cleanup + optimize)
- **Conditional:** Based on DoR/DoD gates (plan approved → execute)

### 9. Testing Strategy

**A. Classification Accuracy Tests:**

```python
# tests/test_llm_intent_classifier.py

def test_single_intent_classification():
    """Test LLM correctly classifies single-intent requests"""
    classifier = LLMIntentClassifier()
    
    request = AgentRequest(
        user_message="create a comprehensive plan for user authentication"
    )
    
    result = classifier.classify_intent(request)
    
    assert result.primary_intent == IntentType.PLAN
    assert result.primary_confidence >= 0.85
    assert len(result.secondary_intents) == 0

def test_multi_intent_classification():
    """Test LLM detects composite requests"""
    classifier = LLMIntentClassifier()
    
    request = AgentRequest(
        user_message="plan authentication, implement it, and write tests"
    )
    
    result = classifier.classify_intent(request)
    
    assert result.primary_intent == IntentType.PLAN
    assert len(result.secondary_intents) >= 2
    assert any(i['intent'] == IntentType.CODE for i in result.secondary_intents)
    assert any(i['intent'] == IntentType.TEST for i in result.secondary_intents)
```

**B. Performance Tests:**

- Measure latency (P50, P95, P99)
- Cache hit rate validation
- Fallback mechanism testing
- Cost per classification tracking

**C. Accuracy Baseline:**

- Capture 1000 real user requests with manual intent labels
- Compare keyword vs LLM accuracy
- Target: >95% accuracy for top 20 intents

### 10. Tier 2 Learning Integration

**Pattern Storage:**

```sql
-- cortex-brain/tier2/intent_patterns.sql

CREATE TABLE intent_classifications (
    id INTEGER PRIMARY KEY,
    message_fingerprint TEXT NOT NULL,
    user_message TEXT,
    classified_intent TEXT,
    confidence REAL,
    classification_method TEXT, -- 'keyword' | 'llm' | 'cache'
    user_feedback TEXT, -- 'correct' | 'incorrect' | null
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    conversation_id TEXT,
    UNIQUE(message_fingerprint)
);

CREATE INDEX idx_fingerprint ON intent_classifications(message_fingerprint);
CREATE INDEX idx_timestamp ON intent_classifications(timestamp DESC);
```

**Feedback Loop:**

1. User corrects intent (e.g., "I meant plan, not code")
2. Store correction in Tier 2
3. Adjust future classifications for similar patterns
4. Improve LLM prompt with learned examples

### 11. Configuration

**cortex.config.json:**

```json
{
  "intent_classification": {
    "use_llm": false,
    "llm_provider": "copilot",
    "confidence_threshold": 0.8,
    "enable_caching": true,
    "enable_multi_intent": true,
    "fallback_to_keyword": true,
    "max_classifications_per_hour": 100,
    "fast_path_intents": [
      "HELP", "ALIGN", "HEALTHCHECK", "DEPLOY", 
      "REGENERATE_PROMPTS", "LOAD_DASHBOARD"
    ]
  }
}
```

### 12. Migration Checklist

**Phase 1: Foundation (Week 1-2)**
- [ ] Create `LLMIntentClassifier` class
- [ ] Design few-shot prompt template
- [ ] Implement Tier 2 caching layer
- [ ] Add configuration flags
- [ ] Write unit tests

**Phase 2: Integration (Week 3-4)**
- [ ] Integrate with IntentRouter
- [ ] Add shadow mode logging
- [ ] Collect accuracy baseline (1000 samples)
- [ ] Performance benchmarking

**Phase 3: Validation (Week 5-6)**
- [ ] Enable for low-confidence requests
- [ ] Monitor accuracy improvements
- [ ] Collect user feedback
- [ ] Adjust prompts based on failures

**Phase 4: Full Rollout (Week 7-8)**
- [ ] Enable hybrid approach by default
- [ ] Update documentation
- [ ] Create migration guide
- [ ] Archive keyword YAML (keep as fallback)

### 📊 Impact & Changes

**Benefits:**

1. **Accuracy:** 95%+ intent classification (vs 85% keyword-only)
2. **Natural Language:** Handle "Can you help me build..." vs "plan feature"
3. **Multi-Intent:** Detect composite requests automatically
4. **Maintenance:** No manual keyword list updates
5. **Learning:** Adapt to user communication styles via Tier 2

**Risks:**

1. **Latency:** LLM adds 100-500ms (mitigated by caching)
2. **Cost:** API costs (mitigated by free tier + rate limiting)
3. **Reliability:** LLM unavailability (mitigated by keyword fallback)
4. **Complexity:** Additional debugging surface area

**Metrics to Track:**

- Classification accuracy (keyword vs LLM)
- Latency distribution (P50, P95, P99)
- Cache hit rate
- Cost per classification
- User feedback (corrections)

### 🔍 Next Steps

**Immediate Actions:**

1. **Create LLMIntentClassifier skeleton** - Basic structure with config
2. **Design prompt template** - Few-shot examples for top 20 intents
3. **Implement Tier 2 caching** - Pattern storage and retrieval
4. **Shadow mode testing** - Run LLM alongside keyword, compare results
5. **Accuracy baseline** - Collect 1000 labeled samples

**Decision Points:**

- [ ] **LLM Provider:** Use Copilot's LLM (free) vs OpenAI API (paid, higher accuracy)
- [ ] **Rollout Timeline:** Gradual (3 months) vs aggressive (1 month)
- [ ] **Fallback Strategy:** Always keyword fallback vs fail-fast with error
- [ ] **Multi-Intent:** Sequential execution vs parallel orchestrator coordination

**Follow-up Planning:**

- Create TDD implementation plan (RED phase first)
- Design integration tests with existing orchestrators
- Document prompt engineering best practices
- Set up A/B testing framework for accuracy comparison

---

**Status:** ✅ Planning Complete - Ready for Implementation  
**Next:** Create implementation plan with TDD phases  
**Dependencies:** None - can begin immediately  
**Estimated Effort:** 8 weeks (with gradual rollout)
