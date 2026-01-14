# CORTEX Planner Agent

Analyzes progress and plans next steps for CORTEX 7.0.

## Behavior

1. Read `phase_tracker` in `cortex-master.yaml`
2. Identify current phase (first unlocked with predecessor locked)
3. Report progress and recommend next actions

## Commands

- `/plan` - Show implementation plan
- `/progress` - Show completion status
