# CORTEX 4.0 LLM-Based Intent Discovery

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 9, 2025  
**Classification:** Technical Architecture Document

---

## 🎯 Overview

CORTEX 4.0 replaces keyword-based intent classification with **LLM-powered natural language understanding**, enabling contextual routing, multi-intent detection, and user preference learning.

**Transformation:**
- **From:** Pattern matching with 443 lines of keyword rules
- **To:** Intelligent understanding with conversation context

---

## 📊 Current Limitations (CORTEX 3.x)

**Keyword Matching Problems:**
```
User: "Can you help me build authentication?"
Current System: Keyword "build" → CODE intent ❌
Correct Intent: PLAN intent (comprehensive planning) ✅

User: "The login isn't working in production"
Current System: Keyword "login" → CODE intent ❌
Correct Intent: DEBUG intent (troubleshooting) ✅
```

**Statistics:**
- Accuracy: 85% (15% misclassification rate)
- Ambiguous requests: 30% require clarification
- Composite requests: Not detected (executes first intent only)
- Context-blind: Forgets previous conversation

---

## 🏗️ CORTEX 4.0 Solution: Hybrid Classification

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    USER REQUEST                           │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│              FAST PATH (< 10ms)                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Exact Command Match                               │  │
│  │  - "plan feature" → PLAN (100% confidence)         │  │
│  │  - "start tdd" → TDD (100% confidence)             │  │
│  │  - "align" → ALIGN (100% confidence)               │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  If confidence >= 80%: Return immediately                 │
└──────────────────────────────────────────────────────────┘
                          ↓ (confidence < 80%)
┌──────────────────────────────────────────────────────────┐
│              TIER 2 CACHE CHECK (< 20ms)                  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Pattern Cache Lookup                              │  │
│  │  - Similar message seen before?                    │  │
│  │  - User-specific patterns?                         │  │
│  │  - Team-wide patterns?                             │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  If cache hit: Return cached intent                       │
└──────────────────────────────────────────────────────────┘
                          ↓ (cache miss)
┌──────────────────────────────────────────────────────────┐
│              LLM CLASSIFICATION (100-500ms)               │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Natural Language Understanding                    │  │
│  │  - Conversation context (last 3-5 turns)           │  │
│  │  - Multi-intent detection                          │  │
│  │  - Confidence scoring                              │  │
│  │  - Reasoning explanation                           │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  Cache result → Return intent with metadata               │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│              TIER 2 LEARNING (async)                      │
│  - Store classification pattern                           │
│  - Update user preferences                                │
│  - Track accuracy metrics                                 │
└──────────────────────────────────────────────────────────┘
```

### Performance Targets

| Path | Latency | Coverage | Accuracy |
|------|---------|----------|----------|
| Fast Path | < 10ms | 80% | 100% |
| Cache Hit | < 20ms | 15% | 98% |
| LLM Classification | < 500ms | 5% | 97% |
| **Overall P95** | **< 100ms** | **100%** | **98%+** |

---

##

 🧠 LLM Prompt Engineering

### Intent Classification Prompt

```
SYSTEM ROLE:
You are CORTEX, an enterprise AI assistant with specialized agents.
Your task: Analyze user requests and classify intent with high accuracy.

AVAILABLE INTENTS (50+ total):
┌─────────────────────────────────────────────────────────┐
│ PLANNING INTENTS                                        │
├─────────────────────────────────────────────────────────┤
│ PLAN - Comprehensive feature planning                   │
│ ARCHITECTURE_PLANNING - System design, tech decisions   │
│ REFACTORING_PLANNING - Code restructuring strategy      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ EXECUTION INTENTS                                       │
├─────────────────────────────────────────────────────────┤
│ CODE - Implementation, feature creation                 │
│ TEST - Test creation, TDD workflow                      │
│ DEBUG - Troubleshooting, error investigation            │
│ REFACTOR - Code cleanup, optimization                   │
└─────────────────────────────────────────────────────────┘

... (full 50+ intent list)

CONTEXT:
User: "{user_message}"

Conversation History:
{last_3_conversation_turns}

INSTRUCTIONS:
1. Identify PRIMARY intent (user's main goal)
2. Detect SECONDARY intents (composite requests)
3. Assign confidence score (0.0-1.0) per intent
4. Provide brief reasoning

OUTPUT FORMAT (JSON):
{
  "primary_intent": "PLAN",
  "primary_confidence": 0.95,
  "secondary_intents": [
    {"intent": "CODE", "confidence": 0.80},
    {"intent": "TEST", "confidence": 0.75}
  ],
  "reasoning": "User wants comprehensive planning first, then implementation and testing",
  "key_indicators": ["build", "authentication", "comprehensive"],
  "execution_strategy": "sequential"
}
```

### Few-Shot Examples

**Example 1: Ambiguous Request**
```
User: "Can you help me with authentication?"
Classification:
{
  "primary_intent": "PLAN",
  "primary_confidence": 0.90,
  "reasoning": "'help with' suggests guidance, not direct implementation"
}
```

**Example 2: Composite Request**
```
User: "Plan authentication, implement OAuth, and write security tests"
Classification:
{
  "primary_intent": "PLAN",
  "primary_confidence": 0.98,
  "secondary_intents": [
    {"intent": "CODE", "confidence": 0.95},
    {"intent": "TEST", "confidence": 0.90}
  ],
  "execution_strategy": "sequential"
}
```

**Example 3: Context-Aware**
```
Previous Turn: "I'm working on the login feature"
User: "It's not working in production"
Classification:
{
  "primary_intent": "DEBUG",
  "primary_confidence": 0.92,
  "reasoning": "Context: production issue with existing feature → debug intent"
}
```

---

## 📊 Implementation Plan

### Phase 1: Foundation (Weeks 1-2)

**Deliverables:**
- `src/cortex_agents/llm_intent_classifier.py` class
- Few-shot prompt template library
- Tier 2 caching schema and implementation
- Configuration management (`cortex.config.json`)

**Success Criteria:**
- ✅ LLM classifier responds in <500ms
- ✅ Unit tests pass (20+ test cases)
- ✅ Baseline accuracy measured on 100 samples

### Phase 2: Integration (Weeks 3-4)

**Deliverables:**
- IntentRouter enhancement with hybrid logic
- Shadow mode logging (LLM vs keyword comparison)
- Performance monitoring dashboard
- Cache hit rate tracking

**Success Criteria:**
- ✅ Shadow mode collects 1000+ classifications
- ✅ LLM accuracy >90% (vs keyword baseline)
- ✅ Cache hit rate >60%

### Phase 3: Gradual Rollout (Weeks 5-6)

**Deliverables:**
- Enable LLM for low-confidence requests (< 60%)
- User feedback collection mechanism
- A/B testing framework
- Accuracy improvement monitoring

**Success Criteria:**
- ✅ 95%+ intent accuracy
- ✅ P95 latency <100ms
- ✅ Positive user feedback (4+/5)

### Phase 4: Full Deployment (Weeks 7-8)

**Deliverables:**
- Hybrid approach enabled by default
- Multi-intent orchestrator coordination
- Documentation and training materials
- Keyword rules archived (fallback only)

**Success Criteria:**
- ✅ 500+ users on hybrid system
- ✅ 98%+ accuracy sustained
- ✅ Zero production incidents

---

## 🎯 Business Value

**Quantified Benefits:**

1. **Reduced Clarification Time**
   - Current: 30% of requests need clarification
   - With LLM: 10% need clarification
   - Time saved: 2-3 minutes per interaction
   - Annual value (500 users): **$800K**

2. **Higher Accuracy**
   - Current: 85% intent accuracy
   - With LLM: 98% intent accuracy
   - Fewer frustrated users, better experience
   - Developer satisfaction: +25%

3. **Multi-Intent Handling**
   - Current: Execute first intent, ignore rest
   - With LLM: Detect all intents, orchestrate execution
   - Efficiency gain: 40% for composite requests
   - Annual value: **$500K**

4. **Reduced Maintenance**
   - Current: Manually update 443-line keyword YAML
   - With LLM: Self-adapting via learning
   - Engineering time saved: 20 hours/month
   - Annual value: **$60K**

**Total Annual Value: $1.36M**

---

## 🔒 Privacy & Security

**User Data Protection:**
- User messages cached with anonymization (remove PII)
- Conversation history limited to last 3-5 turns
- No code snippets sent to LLM (only intent-relevant text)
- Opt-out mechanism for privacy-sensitive users

**LLM Provider Options:**
1. **GitHub Copilot's LLM** (Recommended)
   - Already in user environment
   - Zero additional cost
   - Privacy controls included

2. **OpenAI API** (Alternative)
   - Higher accuracy potential
   - Cost: ~$0.002 per classification
   - Monthly cost (500 users): ~$300

---

**Copyright © 2025 Asif Hussain. All rights reserved.**
