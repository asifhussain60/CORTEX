from datetime import datetime
import pytest

from src.tier2.plan_models import (
    Meta,
    Artifacts,
    PlanLedgerEntry,
    PlanLedger,
    FeaturePlan,
    ActivePlans,
    Decision,
    DecisionGraph,
    ReasoningChainEntry,
    TestAlignmentItem,
    TestAlignment,
    PlanForecast,
    MetricsForecast,
)


def test_plan_ledger_happy_path():
    meta = Meta(schema_version="1.0.0")
    entry = PlanLedgerEntry(
        id="PL-1",
        timestamp=datetime.utcnow(),
        actor="system",
        plan_type="feature",
        status="draft",
        artifacts=Artifacts(tasks=["t1"], risks=["r1"]) ,
        confidence=0.8,
    )
    ledger = PlanLedger(meta=meta, entries=[entry])
    assert ledger.meta.schema_version == "1.0.0"
    assert len(ledger.entries) == 1


def test_plan_ledger_missing_id_invalid():
    meta = Meta(schema_version="1.0.0")
    with pytest.raises(ValueError):
        PlanLedger(
            meta=meta,
            entries=[
                PlanLedgerEntry(
                    id="",  # invalid
                    timestamp=datetime.utcnow(),
                    actor="system",
                    plan_type="feature",
                    status="draft",
                )
            ],
        )


def test_active_plans_feature_happy():
    meta = Meta(schema_version="1.0.0")
    fp = FeaturePlan(
        id="F-1",
        summary="Add narrator voice caching",
        current_revision="rev-1",
        modules=["tier1", "tier2"],
        acceptance_criteria=["Cache hits > 80%", "Latency < 50ms"],
    )
    ap = ActivePlans(meta=meta, feature_plans=[fp])
    assert len(ap.feature_plans) == 1
    assert ap.feature_plans[0].summary.startswith("Add narrator")


def test_decision_graph_happy():
    meta = Meta(schema_version="1.0.0")
    d = Decision(
        id="D-1",
        question="Should we shard plans?",
        options=["yes", "no"],
        chosen_option="yes",
        justification="Reduce merge conflicts",
    )
    dg = DecisionGraph(meta=meta, decisions=[d])
    assert dg.decisions[0].chosen_option == "yes"


def test_reasoning_chain_entry_happy():
    r = ReasoningChainEntry(
        plan_id="F-1",
        step_index=0,
        model_version="gpt-4.1",
        input_context_hash="abcd1234",
        output_summary="Summarized constraints",
        tokens_in=120,
        tokens_out=55,
    )
    assert r.tokens_in >= r.tokens_out - 100  # arbitrary sanity check


def test_test_alignment_happy():
    meta = Meta(schema_version="1.0.0")
    item = TestAlignmentItem(
        plan_id="F-1",
        coverage_targets={"unit": 0.8, "integration": 0.6},
        enforcement_status="warn",
    )
    ta = TestAlignment(meta=meta, plans=[item])
    assert ta.plans[0].coverage_targets["unit"] == 0.8


def test_metrics_forecast_happy():
    meta = Meta(schema_version="1.0.0")
    pf = PlanForecast(
        plan_id="F-1",
        predicted_complexity=8.0,
        uncertainty_band=[6.0, 10.0],
        historical_similarity_refs=["F-0"],
        variance_from_actual=None,
    )
    mf = MetricsForecast(meta=meta, forecasts=[pf])
    assert mf.forecasts[0].predicted_complexity >= 0
