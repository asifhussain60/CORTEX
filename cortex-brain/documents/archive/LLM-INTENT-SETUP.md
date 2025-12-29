# LLM Intent Classification Setup Guide

**Date:** December 25, 2025  
**Version:** CORTEX 4.0  
**Author:** Asif Hussain

---

## 🎯 Quick Start

Enable LLM-based intent classification in 3 steps:

### Step 1: Get API Key

**Option A: OpenAI (Recommended)**
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Copy the key (starts with `sk-`)

**Option B: Anthropic**
1. Go to https://console.anthropic.com/account/keys
2. Create new API key
3. Copy the key

### Step 2: Set Environment Variable

**macOS/Linux:**
```bash
# Add to ~/.zshrc or ~/.bashrc
export OPENAI_API_KEY="sk-your-key-here"

# Reload shell
source ~/.zshrc
```

**Windows PowerShell:**
```powershell
# Temporary (current session)
$env:OPENAI_API_KEY = "sk-your-key-here"

# Permanent (system-wide)
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-your-key-here", "User")
```

**Windows CMD:**
```cmd
setx OPENAI_API_KEY "sk-your-key-here"
```

### Step 3: Enable in Config

Edit `cortex.config.json`:

```json
{
  "llm_intent_routing": {
    "enabled": true,  // ← Change this to true
    "provider": "openai",
    "model": "gpt-3.5-turbo"
  }
}
```

---

## 🔧 Configuration Options

### Basic Configuration

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
    "max_latency_ms": 500
  }
}
```

### Provider Options

**OpenAI (GPT-3.5 Turbo):**
- **Cost:** ~$0.0015 per 1K tokens
- **Latency:** 100-300ms
- **Context:** 16K tokens
- **Best for:** General purpose, fast responses

**OpenAI (GPT-4):**
```json
{
  "provider": "openai",
  "model": "gpt-4-turbo-preview"
}
```
- **Cost:** ~$0.03 per 1K tokens
- **Latency:** 200-500ms
- **Best for:** Complex intent disambiguation

**Anthropic (Claude 3 Haiku):**
```json
{
  "provider": "anthropic",
  "model": "claude-3-haiku",
  "anthropic": {
    "api_key_env": "ANTHROPIC_API_KEY"
  }
}
```
- **Cost:** ~$0.0008 per 1K tokens
- **Latency:** 150-400ms
- **Best for:** Cost-effective, high quality

### Advanced Settings

```json
{
  "llm_intent_routing": {
    "cache_enabled": true,              // Tier 2 Knowledge Graph caching
    "fallback_to_regex": true,          // Graceful degradation
    "fast_path_threshold": 0.8,         // Confidence for keyword shortcuts
    "tier2_similarity_threshold": 0.85, // Cache hit threshold
    "max_latency_ms": 500,              // Timeout before fallback
    "temperature": 0.3                  // 0.0-1.0 (lower = more deterministic)
  }
}
```

---

## 📊 Performance Metrics

### Classification Flow

```
User Request
     ↓
1. Fast Keyword Screen (<10ms)    [80% confidence → instant return]
     ↓
2. Tier 2 Cache Check (<50ms)     [85% similarity → cache hit]
     ↓
3. LLM Classification (100-500ms) [Context-aware semantic understanding]
     ↓
4. Regex Fallback (backup)        [On timeout/error/disabled]
```

### Expected Performance

**With LLM Enabled:**
- Keyword matches: <10ms (40% of requests)
- Cache hits: <50ms (30% of requests)
- LLM calls: 100-500ms (30% of requests)
- Fallback: <50ms (rare)

**With LLM Disabled:**
- All requests: Regex fallback (<50ms)

---

## 🧪 Testing

### Verify API Key

```bash
# Test OpenAI connection
python -c "import os; print('API Key:', os.getenv('OPENAI_API_KEY')[:10] + '...')"

# Test with actual call (costs ~$0.0001)
python -c "
import openai
import os
openai.api_key = os.getenv('OPENAI_API_KEY')
response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=[{'role': 'user', 'content': 'Hello'}],
    max_tokens=10
)
print('✅ OpenAI API working')
"
```

### Run Test Suite

```bash
# Test LLM intent router (mocked, no API calls)
pytest tests/cortex_agents/test_llm_intent_router_p0.py -v

# Test with real API (requires API key, costs ~$0.01)
pytest tests/cortex_agents/test_llm_intent_router_p0.py::TestOpenAIProvider -v --no-skip
```

### Monitor Usage

```python
from src.cortex_agents.llm_intent_router import LLMIntentRouter, LLMIntentConfig

config = LLMIntentConfig(enabled=True, provider='openai')
router = LLMIntentRouter(config)

# After some classifications
metrics = router.get_performance_metrics()
print(f"Total classifications: {metrics['total_classifications']}")
print(f"LLM calls: {metrics['llm_calls']}")
print(f"Cache hits: {metrics['cache_hits']}")
print(f"Average latency: {metrics['avg_latency_ms']:.2f}ms")
```

---

## 💰 Cost Estimation

### GPT-3.5 Turbo (Recommended)

**Assumptions:**
- Average request: 200 tokens
- 1000 classifications/day
- Cache hit rate: 30%

**Daily Cost:**
```
LLM calls: 1000 × 70% = 700 calls
Tokens: 700 × 200 = 140,000 tokens
Cost: 140K / 1000 × $0.0015 = $0.21/day
```

**Monthly Cost:** ~$6.30

### Claude 3 Haiku (Most Cost-Effective)

**Daily Cost:**
```
Cost: 140K / 1000 × $0.0008 = $0.11/day
```

**Monthly Cost:** ~$3.30

### GPT-4 Turbo (High Quality)

**Daily Cost:**
```
Cost: 140K / 1000 × $0.03 = $4.20/day
```

**Monthly Cost:** ~$126

---

## 🔒 Security Best Practices

### ✅ DO

- Store API keys in environment variables
- Use `.env` file (gitignored)
- Rotate keys periodically
- Monitor usage/billing dashboards
- Set billing alerts ($10, $50, $100)

### ❌ DON'T

- Commit API keys to git
- Share keys in chat/email
- Use production keys in development
- Hardcode keys in code

### Revoke Compromised Keys

**OpenAI:**
1. Go to https://platform.openai.com/api-keys
2. Click "Revoke" on compromised key
3. Generate new key

**Anthropic:**
1. Go to https://console.anthropic.com/account/keys
2. Delete compromised key
3. Generate new key

---

## 🐛 Troubleshooting

### "LLM intent routing disabled"

**Cause:** Missing API library or invalid API key

**Fix:**
```bash
# Install required library
pip install openai  # or anthropic

# Verify API key is set
echo $OPENAI_API_KEY

# Check logs
tail -f logs/cortex.log | grep "LLM"
```

### "Fallback to regex"

**Cause:** LLM timeout or error

**Check:**
1. Network connectivity
2. API key validity
3. Billing status
4. Rate limits

**Logs:**
```bash
grep "LLM classification failed" logs/cortex.log
```

### "ImportError: No module named 'openai'"

**Fix:**
```bash
pip install openai
# or
pip install anthropic
```

---

## 📈 Monitoring & Analytics

### Performance Metrics

```python
# Get router metrics
metrics = router.get_performance_metrics()

# Example output:
{
    'total_classifications': 1000,
    'exact_matches': 400,      # 40% keyword shortcuts
    'cache_hits': 300,         # 30% Tier 2 cache
    'llm_calls': 300,          # 30% LLM calls
    'fallbacks': 0,            # 0% errors
    'avg_latency_ms': 85.3
}
```

### Cost Tracking

Track token usage in logs:
```bash
grep "tokens_used" logs/cortex.log | awk '{sum+=$NF} END {print "Total tokens:", sum}'
```

---

## 🚀 Next Steps

1. **Enable LLM:** Set `enabled: true` in config
2. **Monitor metrics:** Check performance after 100 classifications
3. **Optimize costs:** Increase cache hit rate via Tier 2 learning
4. **Tune thresholds:** Adjust `fast_path_threshold` for speed/accuracy balance

---

## 📚 Additional Resources

- **OpenAI Docs:** https://platform.openai.com/docs
- **Anthropic Docs:** https://docs.anthropic.com
- **CORTEX LLM Router:** `src/cortex_agents/llm_intent_router.py`
- **Test Suite:** `tests/cortex_agents/test_llm_intent_router_p0.py`
- **Architecture:** `cortex-brain/documents/archive/LLM-INTENT-CLASSIFICATION.md`

---

**Quick Verification:**
```bash
# Verify setup
python -c "from src.cortex_agents.llm_intent_router import LLMIntentConfig; print('✅ LLM Router available')"

# Check config
python -c "import json; config = json.load(open('cortex.config.json')); print('LLM enabled:', config.get('llm_intent_routing', {}).get('enabled', False))"
```
