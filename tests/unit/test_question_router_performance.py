import time
import statistics
import pytest

from src.operations.modules.questions.question_router import QuestionRouter


@pytest.mark.performance
def test_routing_latency_under_target_unit_scope():
    router = QuestionRouter()
    samples = []
    messages = [
        "Show CORTEX system status and brain health.",
        "How is my code quality and test coverage?",
        "What's the status of Tier2 memory?",
        "help",
        "Check build errors in my project",
    ]

    # Warm-up
    for _ in range(5):
        router.route(messages[_ % len(messages)])

    # Measure
    for i in range(30):
        msg = messages[i % len(messages)]
        t0 = time.perf_counter()
        router.route(msg)
        dt = (time.perf_counter() - t0) * 1000.0
        samples.append(dt)

    p50 = statistics.median(samples)
    p95 = sorted(samples)[int(0.95 * len(samples)) - 1]

    # Targets from plan: <100ms routing; allow modest CI variance for p95
    assert p50 < 50.0
    assert p95 < 150.0
