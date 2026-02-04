"""Test CodeLevelPlanner."""
import pytest
from cortex.orchestrators.domain.code_level_planner import CodeLevelPlanner

def test_planner_instantiates():
    planner = CodeLevelPlanner()
    assert planner is not None

def test_analyze_task_scope():
    planner = CodeLevelPlanner()
    scope = planner.analyze_task_scope("test task")
    assert scope["estimated_files"] > 0

def test_generate_plan():
    planner = CodeLevelPlanner()
    plan = planner.generate_plan("test")
    assert plan.task_id is not None
