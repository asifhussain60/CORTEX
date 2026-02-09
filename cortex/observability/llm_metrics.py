"""
LLM Observability Metrics (PHASE 3).

AC-ID: AC-LENS-LLM-004
Prometheus metrics for LLM usage tracking and cost monitoring.
Compliance: CORE-011 (Type hints), CORE-012 (Docstrings)
"""

from typing import Optional

try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Fallback no-op metrics if prometheus not installed
    class Counter:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
        def inc(self, *args, **kwargs):
            pass
    
    class Histogram:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
        def observe(self, *args, **kwargs):
            pass
    
    class Gauge:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
        def set(self, *args, **kwargs):
            pass


# LLM API call counter
llm_calls_total = Counter(
    "cortex_llm_calls_total",
    "Total number of LLM API calls",
    ["provider", "model", "tier", "status"]
)

# Token usage counter
llm_tokens_used = Counter(
    "cortex_llm_tokens_used",
    "Total tokens consumed by LLM calls",
    ["provider", "model", "type"]  # typeUnion[prompt, completion]
)

# LLM call latency histogram
llm_latency_seconds = Histogram(
    "cortex_llm_latency_seconds",
    "LLM API call latency in seconds",
    ["provider", "model"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# Estimated cost counter
llm_cost_usd = Counter(
    "cortex_llm_cost_usd",
    "Estimated LLM cost in USD",
    ["provider", "model"]
)

# Budget metrics
llm_budget_remaining = Gauge(
    "cortex_llm_budget_remaining",
    "Remaining token budget",
    ["scope"]  # scopeUnion[per_request, per_user]|global
)

# Error counter
llm_errors_total = Counter(
    "cortex_llm_errors_total",
    "Total LLM API errors",
    ["provider", "error_type"]
)


def record_llm_call(
    provider: str,
    model: str,
    tier: str,
    status: str,
    latency_seconds: float,
    prompt_tokens: int,
    completion_tokens: int,
    cost_usd: float
) -> None:
    """
    Record LLM call metrics.
    
    Args:
        provider: LLM provider name (openai, anthropic, etc.)
        model: Model name (gpt-4, claude-3-opus, etc.)
        tier: Analysis tier (fast, smart, deep, crawler)
        status: Call status (success, error, timeout)
        latency_seconds: Call duration in seconds
        prompt_tokens: Input tokens used
        completion_tokens: Output tokens used
        cost_usd: Estimated cost in USD
    """
    if not PROMETHEUS_AVAILABLE:
        return  # Silently skip if prometheus not installed
    
    # Record call
    llm_calls_total.labels(
        provider=provider,
        model=model,
        tier=tier,
        status=status
    ).inc()
    
    # Record tokens
    llm_tokens_used.labels(
        provider=provider,
        model=model,
        type="prompt"
    ).inc(prompt_tokens)
    
    llm_tokens_used.labels(
        provider=provider,
        model=model,
        type="completion"
    ).inc(completion_tokens)
    
    # Record latency
    llm_latency_seconds.labels(
        provider=provider,
        model=model
    ).observe(latency_seconds)
    
    # Record cost
    llm_cost_usd.labels(
        provider=provider,
        model=model
    ).inc(cost_usd)


def record_llm_error(provider: str, error_type: str) -> None:
    """
    Record LLM error.
    
    Args:
        provider: LLM provider name
        error_type: Error type (timeout, rate_limit, api_error, etc.)
    """
    if not PROMETHEUS_AVAILABLE:
        return
    
    llm_errors_total.labels(
        provider=provider,
        error_type=error_type
    ).inc()


def update_budget_metrics(
    per_request_remaining: int,
    per_user_remaining: int,
    global_remaining: int
) -> None:
    """
    Update budget remaining metrics.
    
    Args:
        per_request_remaining: Tokens remaining for request
        per_user_remaining: Tokens remaining for user today
        global_remaining: Tokens remaining globally today
    """
    if not PROMETHEUS_AVAILABLE:
        return
    
    llm_budget_remaining.labels(scope="per_request").set(per_request_remaining)
    llm_budget_remaining.labels(scope="per_user").set(per_user_remaining)
    llm_budget_remaining.labels(scope="global").set(global_remaining)
