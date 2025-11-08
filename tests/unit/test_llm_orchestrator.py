import pytest

from src.llm.orchestrator import LLMOrchestrator
from src.llm.types import LLMGenerationSettings


def test_openai_primary_selection():
    orch = LLMOrchestrator(primary_provider="openai", fallback_chain=["anthropic", "local"])
    caps = orch.capabilities()
    assert caps.tool_call_support == "structured"
    resp = orch.generate("Hello world test")
    assert resp.text.startswith("[openai:")
    assert resp.confidence_state == "high"


def test_fallback_to_local_when_tools_not_supported():
    # Request tool schema but local is only none; ensure primary openai still works
    orch = LLMOrchestrator(primary_provider="openai", fallback_chain=["local"])
    resp = orch.generate("Do something", tools_schema={"name": "do_it", "params": {}})
    assert resp.confidence_state == "high"


def test_unknown_provider_error():
    with pytest.raises(ValueError):
        LLMOrchestrator(primary_provider="not-real")
