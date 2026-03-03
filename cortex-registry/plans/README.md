# CORTEX Plans — Live Plan Store

This directory is the **active plan persistence store** for CORTEX interaction plans.

## ⚠️ Live Data Directory

This is NOT a documentation or archive directory. Plan YAML files are written here
at runtime by `cortex/orchestrators/core/interaction_plan_store.py`.

## Structure

```
plans/
  approved/   ← Approved plans ready for execution
  pending/    ← Plans awaiting approval
  archive/    ← Completed/superseded plans
```

## Usage

Plans are created, updated, and read via `InteractionPlanStore` — do not manually edit
plan files unless performing maintenance recovery.

## Governance

Authority: `cortex/orchestrators/core/interaction_plan_store.py`
