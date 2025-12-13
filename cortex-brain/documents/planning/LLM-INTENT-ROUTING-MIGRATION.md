# LLM Intent Routing Migration Guide

**Feature:** Phase 0 - Foundation & Intent Routing Enhancement  
**Version:** 1.0.0  
**Migration Path:** CORTEX 3.8.1 → 3.9.0  
**Date:** December 13, 2025

---

## 🎯 Executive Summary

This guide provides step-by-step instructions for migrating from regex-based intent routing (70% accuracy) to LLM-powered classification (95%+ accuracy). Migration is backward compatible, feature-flagged, and supports gradual rollout.

**Migration Timeline:** 1-2 weeks (pilot → production)

**Risk Level:** LOW (graceful fallback, feature flag controlled)

---

## 📋 Pre-Migration Checklist

- [ ] CORTEX 3.8.1+ installed
- [ ] Python 3.8+ runtime
- [ ] OpenAI API key acquired (or Anthropic)
- [ ] API key budget approved (~$1-5/month)
- [ ] Test environment available
- [ ] Rollback plan documented
- [ ] Stakeholder approval obtained

---

## 🚀 Migration Phases

### Phase 1: Pilot (Week 1, Days 1-3)

**Goal:** Validate LLM routing in test environment

**Steps:**

1. **Install Dependencies**
   ```bash
   pip install openai  # or anthropic
   pip install -r requirements.txt
   ```

2. **Configure Test Environment**
   
   Edit `cortex.config.json`:
   ```json
   {
     "llm_intent_routing": {
       "enabled": true,
       "provider": "openai",
       "model": "gpt-3.5-turbo",
       "cache_enabled": true,
       "fallback_to_regex": true
     }
   }
   ```

3. **Set API Key (Test Key)**
   ```powershell
   $env:OPENAI_API_KEY = "sk-test-..."
   ```

4. **Run Test Suite**
   ```bash
   pytest tests/integration/agents/test_llm_intent_router.py -v
   
   # Expected: 95%+ tests passing (100+/115 tests)
   ```

5. **Validate Performance**
   ```python
   from src.cortex_agents.intent_router import IntentRouter
   
   config = {
       'llm_intent_routing': {'enabled': True, 'provider': 'openai'}
   }
   router = IntentRouter(name="Test", config=config)
   
   # Test 10-20 diverse requests
   test_requests = [
       "help",
       "plan authentication feature",
       "execute all phases autonomously",
       "plan to implement JWT with TDD",
       # ... more requests
   ]
   
   for msg in test_requests:
       from src.cortex_agents.base_agent import AgentRequest
       result = router.llm_router.classify_intent(AgentRequest(user_message=msg))
       print(f"{msg} → {result.intent} ({result.confidence:.2f}, {result.method})")
   
   # Get metrics
   metrics = router.llm_router.get_performance_metrics()
   print(f"\nCache hit rate: {metrics['cache_hit_rate']:.1%}")
   print(f"Average latency: {metrics['average_latency_ms']:.1f}ms")
   ```

6. **Acceptance Criteria**
   - [ ] 95%+ test pass rate
   - [ ] Cache hit rate > 70% (after 20+ requests)
   - [ ] Average latency < 100ms
   - [ ] Zero errors or crashes
   - [ ] Fallback works on simulated API failure

**Rollback:** Set `"enabled": false` in config

---

### Phase 2: Staging (Week 1, Days 4-5)

**Goal:** Test with real user requests in staging environment

**Steps:**

1. **Deploy to Staging**
   ```bash
   # Copy config to staging
   cp cortex.config.json /path/to/staging/
   
   # Set production API key
   $env:OPENAI_API_KEY = "sk-prod-..."
   
   # Restart CORTEX
   python -m src.main
   ```

2. **Monitor Real Requests**
   
   Enable logging:
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   ```
   
   Watch for:
   - `🎭 LLM Intent Router initialized`
   - Classification method distribution (exact/cache/llm/fallback)
   - Any errors or warnings

3. **A/B Testing (Optional)**
   
   Run 50% of requests through LLM, 50% through regex:
   ```python
   import random
   
   def classify_with_ab_test(request):
       if random.random() < 0.5:
           # LLM path
           return router.llm_router.classify_intent(request)
       else:
           # Regex path
           return router._regex_based_classification(request)
   ```
   
   Compare accuracy metrics.

4. **Cost Validation**
   
   Monitor OpenAI dashboard:
   - API calls per day
   - Token usage
   - Cost per request
   
   Expected: ~30 LLM calls/100 requests = $0.03/day

5. **Acceptance Criteria**
   - [ ] 95%+ accuracy on real requests (user feedback)
   - [ ] Cost within budget ($1-5/month)
   - [ ] No performance degradation (< 500ms P95)
   - [ ] Zero production incidents
   - [ ] Stakeholder approval to proceed

**Rollback:** Set `"enabled": false`, restart

---

### Phase 3: Production Rollout (Week 2, Days 1-3)

**Goal:** Gradual rollout to all users

**Steps:**

1. **Gradual Rollout (10% → 50% → 100%)**
   
   Week 2, Day 1: **10% of users**
   ```json
   {
     "llm_intent_routing": {
       "enabled": true,
       "rollout_percentage": 10
     }
   }
   ```
   
   Week 2, Day 2: **50% of users**
   ```json
   {
     "rollout_percentage": 50
   }
   ```
   
   Week 2, Day 3: **100% of users**
   ```json
   {
     "rollout_percentage": 100
   }
   ```

2. **Monitor Production**
   
   Track metrics:
   - Intent classification accuracy (user feedback)
   - System latency (P50, P95, P99)
   - API error rate
   - Cost per day
   - User complaints/issues

3. **Alerting Setup**
   
   Create alerts for:
   - Fallback rate > 10% (API issues)
   - Average latency > 500ms (performance)
   - Daily cost > budget threshold
   - Error rate > 1%

4. **Acceptance Criteria**
   - [ ] 100% rollout complete
   - [ ] User feedback positive (95%+ accuracy perceived)
   - [ ] Cost within budget
   - [ ] Latency within SLA (< 500ms P95)
   - [ ] Zero critical incidents

---

### Phase 4: Optimization (Week 2, Days 4-7)

**Goal:** Fine-tune for cost and performance

**Steps:**

1. **Analyze Metrics**
   ```python
   metrics = router.llm_router.get_performance_metrics()
   
   print(f"Cache hit rate: {metrics['cache_hit_rate']:.1%}")
   print(f"LLM usage rate: {metrics['llm_usage_rate']:.1%}")
   print(f"Fallback rate: {metrics['fallback_rate']:.1%}")
   ```

2. **Optimize Cache Hit Rate**
   
   If cache < 80%:
   ```json
   {
     "llm_intent_routing": {
       "tier2_similarity_threshold": 0.80  // Lower = more cache hits
     }
   }
   ```

3. **Optimize Fast Path**
   
   Add frequently used commands to exact match:
   ```python
   # In llm_intent_router.py, _fast_keyword_screen()
   exact_commands = {
       'help': IntentType.HELP,
       'align': IntentType.ALIGN,
       # Add more based on logs
       'status': IntentType.HEALTH_CHECK,
       'run tests': IntentType.RUN_TESTS,
   }
   ```

4. **Cost Optimization**
   
   If cost > budget:
   - Increase cache threshold (more cache hits)
   - Add rate limiting
   - Switch to cheaper model (gpt-3.5-turbo-0125)

5. **Performance Tuning**
   
   If latency > 500ms:
   - Reduce `max_tokens` to 300
   - Enable parallel LLM calls
   - Optimize Tier 2 cache queries

---

## 📊 Success Metrics

### Key Performance Indicators (KPIs)

| Metric | Baseline (Regex) | Target (LLM) | Actual |
|--------|------------------|--------------|--------|
| Intent Accuracy | 70% | 95% | TBD |
| Average Latency | 15ms | < 100ms | TBD |
| P95 Latency | 30ms | < 500ms | TBD |
| Cache Hit Rate | 0% | 80% | TBD |
| Monthly Cost | $0 | < $5 | TBD |
| User Satisfaction | Baseline | +20% | TBD |

### Validation Methods

**Intent Accuracy:**
- Manual review of 100 random requests
- User feedback: "Did CORTEX understand your request?"
- A/B test comparison (LLM vs regex)

**Latency:**
- Built-in metrics: `router.llm_router.get_performance_metrics()`
- APM tools (if available)

**Cost:**
- OpenAI dashboard: API usage and billing
- Monthly budget alerts

**User Satisfaction:**
- Survey: "How well does CORTEX understand your requests?" (1-5 scale)
- Support ticket analysis (intent misclassification complaints)

---

## 🚨 Rollback Plan

### Trigger Conditions

Rollback if any of:
- Intent accuracy < 80% (worse than baseline)
- P95 latency > 1000ms (2x target)
- Daily cost > $1 (budget exceeded)
- Critical production incident (outage, data loss)
- Multiple user complaints (> 5 in 24 hours)

### Rollback Steps

**Immediate (< 5 minutes):**

1. **Disable LLM Routing**
   ```json
   {
     "llm_intent_routing": {
       "enabled": false
     }
   }
   ```

2. **Restart CORTEX**
   ```bash
   # Stop current process
   # Restart with updated config
   python -m src.main
   ```

3. **Verify Fallback**
   - Test basic commands (help, align)
   - Verify regex routing active
   - Check logs for "fallback_regex" method

**Post-Rollback (< 1 hour):**

4. **Root Cause Analysis**
   - Review logs for errors
   - Analyze failed requests
   - Check OpenAI API status

5. **Communication**
   - Notify stakeholders
   - Document incident
   - Schedule post-mortem

6. **Fix & Re-Test**
   - Address root cause
   - Re-run test suite
   - Repeat pilot phase

---

## 🔧 Configuration Reference

### Recommended Production Config

```json
{
  "llm_intent_routing": {
    "enabled": true,
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "max_tokens": 500,
    "temperature": 0.3,
    "cache_enabled": true,
    "fallback_to_regex": true,
    "fast_path_threshold": 0.8,
    "tier2_similarity_threshold": 0.85,
    "performance_targets": {
      "max_latency_ms": 500,
      "cache_hit_rate": 0.8
    }
  }
}
```

### Conservative Config (Cost-Optimized)

```json
{
  "llm_intent_routing": {
    "enabled": true,
    "tier2_similarity_threshold": 0.75,  // More cache hits
    "max_tokens": 300                     // Lower token cost
  }
}
```

### Aggressive Config (Performance-Optimized)

```json
{
  "llm_intent_routing": {
    "enabled": true,
    "fast_path_threshold": 0.7,          // More fast path
    "tier2_similarity_threshold": 0.90   // Higher quality cache
  }
}
```

---

## 📚 Additional Resources

- **User Guide:** `cortex-brain/documents/implementation-guides/llm-intent-routing-guide.md`
- **Developer README:** `src/cortex_agents/llm_intent_router_README.md`
- **Test Suite:** `tests/integration/agents/test_llm_intent_router.py`
- **Phase 0 Plan:** `cortex-brain/documents/planning/features/active/phase-0-intent-routing-enhancement.md`

---

## ❓ FAQ

**Q: What if OpenAI API is down?**  
A: Automatic fallback to regex routing. System continues working with 70% accuracy.

**Q: Can I use Anthropic instead of OpenAI?**  
A: Yes, set `"provider": "anthropic"` and `ANTHROPIC_API_KEY` environment variable.

**Q: How do I monitor API costs in real-time?**  
A: OpenAI dashboard → Usage → API usage (updated hourly).

**Q: Can I revert to regex permanently?**  
A: Yes, set `"enabled": false`. LLM code remains inactive.

**Q: What if accuracy is still < 95%?**  
A: Tune `temperature` (lower = more consistent), review failed requests, consider model upgrade.

---

**Migration Owner:** Asif Hussain  
**Support Contact:** github.com/asifhussain60/CORTEX  
**Last Updated:** December 13, 2025
