# LLM Intent Routing - User Guide

**Version:** 1.0.0  
**Feature:** Phase 0 - Foundation & Intent Routing Enhancement  
**Status:** ✅ PRODUCTION READY  
**Date:** December 13, 2025

---

## 🎯 Overview

LLM Intent Routing replaces regex-based intent classification (70% accuracy) with intelligent LLM-powered classification (95%+ accuracy). This enhancement enables CORTEX to understand nuanced user requests, detect composite intents, and provide contextual routing.

### Key Benefits

- **95%+ Accuracy:** LLM understands context, synonyms, and intent variations
- **Multi-Intent Detection:** Identifies primary + secondary intents (e.g., "plan to implement with TDD")
- **Sub-500ms Latency:** Hybrid approach with fast path and caching
- **Graceful Fallback:** Continues working if LLM unavailable
- **Zero Breaking Changes:** Backward compatible with existing workflows

---

## 🚀 Quick Start

### 1. Prerequisites

- **OpenAI API Key** (recommended) or **Anthropic API Key**
- Python 3.8+
- CORTEX 3.8.1+

### 2. Configuration

Edit `cortex.config.json`:

```json
{
  "llm_intent_routing": {
    "enabled": true,
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "max_tokens": 500,
    "temperature": 0.3,
    "cache_enabled": true,
    "fallback_to_regex": true
  }
}
```

### 3. Set API Key

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY = "sk-..."
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="sk-..."
```

### 4. Verify

```python
# In Copilot Chat or Python console
from src.cortex_agents.intent_router import IntentRouter

config = {
    'llm_intent_routing': {
        'enabled': True,
        'provider': 'openai'
    }
}

router = IntentRouter(name="Router", config=config)
# Should see: "🎭 LLM Intent Router initialized - 95%+ accuracy mode enabled"
```

---

## 📐 Architecture

### Hybrid Classification Flow

```
User Request
    ↓
┌─────────────────────────────────────┐
│  Fast Path (< 10ms)                 │
│  Exact command matching             │
│  Confidence ≥ 0.8 → DONE            │
└─────────────────────────────────────┘
    ↓ (if confidence < 0.8)
┌─────────────────────────────────────┐
│  Tier 2 Cache (< 50ms)              │
│  Semantic similarity lookup         │
│  Similarity ≥ 0.85 → DONE           │
└─────────────────────────────────────┘
    ↓ (if no cache hit)
┌─────────────────────────────────────┐
│  LLM Classification (100-500ms)     │
│  Full NLU with context              │
│  Store result in Tier 2 → DONE     │
└─────────────────────────────────────┘
    ↓ (on error)
┌─────────────────────────────────────┐
│  Fallback to Regex (< 20ms)         │
│  Original keyword matching          │
│  Always succeeds                    │
└─────────────────────────────────────┘
```

### Performance Targets

| Method | Latency | Cache Hit Rate | Use Case |
|--------|---------|----------------|----------|
| Fast Path | < 10ms | 40% | Exact commands (help, align) |
| Tier 2 Cache | < 50ms | 30% | Similar past requests |
| LLM | 100-500ms | 30% | Complex/ambiguous requests |
| Fallback | < 20ms | As needed | Error recovery |

**Overall Target:** 80%+ requests served by fast path + cache (< 50ms)

---

## 🔧 Configuration Options

### Provider Selection

**OpenAI (Recommended):**
- **Model:** `gpt-3.5-turbo` (cost: ~$0.001/request)
- **Pros:** Fast, reliable, good JSON parsing
- **Cons:** Requires API key, external dependency

**Anthropic (Alternative):**
- **Model:** `claude-3-haiku-20240307`
- **Pros:** Excellent context understanding
- **Cons:** Higher latency, requires separate API key

```json
{
  "llm_intent_routing": {
    "provider": "anthropic",
    "model": "claude-3-haiku-20240307"
  }
}
```

### Performance Tuning

**Adjust Cache Thresholds:**
```json
{
  "llm_intent_routing": {
    "fast_path_threshold": 0.8,  // Lower = more LLM calls
    "tier2_similarity_threshold": 0.85  // Lower = more cache hits
  }
}
```

**Adjust LLM Parameters:**
```json
{
  "llm_intent_routing": {
    "temperature": 0.3,  // Lower = more deterministic
    "max_tokens": 500    // Sufficient for JSON response
  }
}
```

---

## 📊 Monitoring & Metrics

### Get Performance Metrics

```python
router = IntentRouter(name="Router", config=config)

# After some requests...
metrics = router.llm_router.get_performance_metrics()

print(f"Total classifications: {metrics['total_classifications']}")
print(f"Cache hit rate: {metrics['cache_hit_rate']:.1%}")
print(f"Average latency: {metrics['average_latency_ms']:.1f}ms")
print(f"LLM usage rate: {metrics['llm_usage_rate']:.1%}")
```

### Expected Metrics (After Warmup)

```
Total classifications: 100
Cache hit rate: 82%
Average latency: 45ms
LLM usage rate: 18%
Fallback rate: 0%
```

---

## 🎓 Usage Examples

### Example 1: Exact Command (Fast Path)

**Input:** `help`

**Routing:**
- Method: `exact_match`
- Latency: 3ms
- Confidence: 0.95
- Intent: `HELP`

### Example 2: Pattern Match (Fast Path)

**Input:** `plan authentication feature`

**Routing:**
- Method: `pattern_match`
- Latency: 8ms
- Confidence: 0.85
- Intent: `PLAN`

### Example 3: Composite Request (LLM)

**Input:** `plan to implement JWT auth with TDD`

**Routing:**
- Method: `llm_classify`
- Latency: 320ms
- Confidence: 0.9
- Primary Intent: `PLAN`
- Secondary Intents: `TDD` (0.85)
- Reasoning: "User wants planning with TDD workflow"

### Example 4: Ambiguous Request (LLM)

**Input:** `create a new authentication system`

**Routing:**
- Method: `llm_classify`
- Latency: 280ms
- Confidence: 0.85
- Intent: `PLAN` (not `CODE`)
- Reasoning: "High-level system creation suggests planning phase"

### Example 5: Cache Hit (Tier 2)

**Input:** `plan authentication feature` (second time)

**Routing:**
- Method: `tier2_cache`
- Latency: 42ms
- Confidence: 0.90
- Intent: `PLAN`
- Source: "Similar to: plan authentication feature"

---

## 💰 Cost Management

### Estimated Costs (OpenAI gpt-3.5-turbo)

- **Cost per LLM call:** ~$0.001
- **Average requests/day:** 100
- **LLM usage rate:** 30% (after cache warmup)
- **Monthly cost:** 100 × 30 × 0.3 × $0.001 = **$0.90/month**

### Cost Reduction Strategies

1. **Increase Cache Hit Rate:** Lower `tier2_similarity_threshold` to 0.80
2. **Use Fast Path More:** Add common commands to exact match list
3. **Batch Requests:** Process multiple requests in parallel
4. **Rate Limiting:** Limit LLM calls per hour/day

---

## 🚨 Troubleshooting

### Issue: "LLM Intent Router not initialized"

**Cause:** `enabled: false` or missing API key

**Solution:**
```json
{
  "llm_intent_routing": {
    "enabled": true
  }
}
```

Set environment variable:
```powershell
$env:OPENAI_API_KEY = "sk-..."
```

### Issue: High Latency (> 500ms)

**Cause:** Too many LLM calls, low cache hit rate

**Solution:**
- Increase fast path threshold: `"fast_path_threshold": 0.75`
- Lower cache threshold: `"tier2_similarity_threshold": 0.80`
- Check network connectivity

### Issue: Low Accuracy

**Cause:** Incorrect model or temperature

**Solution:**
```json
{
  "llm_intent_routing": {
    "model": "gpt-3.5-turbo",  // Not gpt-3.5-turbo-instruct
    "temperature": 0.3         // Lower = more consistent
  }
}
```

### Issue: Fallback to Regex Frequently

**Cause:** LLM API errors or rate limiting

**Solution:**
- Check API key validity
- Monitor OpenAI status page
- Reduce request rate
- Enable: `"fallback_to_regex": true` (should be default)

---

## 🔐 Security Considerations

### API Key Protection

- **Never commit API keys to git**
- Use environment variables
- Rotate keys regularly
- Monitor usage dashboards

### Data Privacy

- User requests sent to OpenAI/Anthropic APIs
- Review provider data policies
- Consider on-premise LLM for sensitive data
- Cache reduces external API calls (privacy win)

---

## 📚 Related Documentation

- **Developer Guide:** `src/cortex_agents/llm_intent_router_README.md`
- **Migration Guide:** `cortex-brain/documents/planning/LLM-INTENT-ROUTING-MIGRATION.md`
- **Phase 0 Plan:** `cortex-brain/documents/planning/features/active/phase-0-intent-routing-enhancement.md`
- **Test Suite:** `tests/integration/agents/test_llm_intent_router.py`

---

## ❓ FAQ

**Q: Do I need LLM routing for basic commands?**  
A: No, basic commands (help, align) use fast path. LLM helps with complex/ambiguous requests.

**Q: Can I disable LLM routing after enabling?**  
A: Yes, set `"enabled": false` in config. No code changes needed.

**Q: What happens if my API key expires?**  
A: Automatic fallback to regex-based routing. User experience degraded but functional.

**Q: How do I test without spending money?**  
A: Use `"enabled": false` + run test suite with mocked LLM responses.

**Q: Can I use local LLM (Ollama, LM Studio)?**  
A: Not yet. Phase 0 supports OpenAI/Anthropic only. Local LLM support planned for CORTEX 4.0.

---

**Author:** Asif Hussain  
**Contact:** github.com/asifhussain60/CORTEX  
**Last Updated:** December 13, 2025
