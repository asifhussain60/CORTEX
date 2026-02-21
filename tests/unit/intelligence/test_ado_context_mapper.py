"""
Phase 20 Sub-Phase A — TDD RED Tests: ADOContextMapper

Authority: AC-P20-001, AC-P20-002, AC-P20-003, AC-P20-009, AC-P20-013
Rule: CORE-008 (TDD-first), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import pytest

from cortex.repositories.work_item_provider import WorkItem


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_workitem(
    item_id: str = "1",
    title: str = "Story",
    state: str = "Active",
    iteration: str = "Sprint 42",
    area: str = "CORTEX\\Backend",
) -> WorkItem:
    """Build a WorkItem with ADO-style raw fields."""
    return WorkItem(
        id=item_id,
        title=title,
        description="",
        state=state,
        type="User Story",
        tags=[],
        url=f"https://dev.azure.com/org/project/_workitems/edit/{item_id}",
        raw={
            "fields": {
                "System.IterationPath": iteration,
                "System.AreaPath": area,
                "System.State": state,
            }
        },
    )


# ---------------------------------------------------------------------------
# AC-P20-001 — module is importable
# ---------------------------------------------------------------------------

def test_ado_context_mapper_importable() -> None:
    """AC-P20-001: ADOContextMapper importable from cortex.intelligence.knowledge.ado_context_mapper."""
    from cortex.intelligence.knowledge import ado_context_mapper  # noqa: F401

    assert hasattr(ado_context_mapper, "ADOContextMapper"), (
        "ADOContextMapper class must be exported from ado_context_mapper module"
    )


# ---------------------------------------------------------------------------
# AC-P20-002 — map() returns sprint_context dict with sprint_name + stories
# ---------------------------------------------------------------------------

def test_map_returns_sprint_name() -> None:
    """AC-P20-002a: ADOContextMapper.map() extracts sprint_name from IterationPath."""
    from cortex.intelligence.knowledge.ado_context_mapper import ADOContextMapper

    stories = [_make_workitem(iteration="MyTeam\\Sprint 42")]
    result = ADOContextMapper.map(stories)

    assert "sprint_name" in result, "map() must return sprint_name key"
    assert "Sprint 42" in result["sprint_name"], (
        f"sprint_name should contain 'Sprint 42', got: {result['sprint_name']!r}"
    )


def test_map_returns_stories_list() -> None:
    """AC-P20-002b: ADOContextMapper.map() returns stories list with id/title/state/area_path."""
    from cortex.intelligence.knowledge.ado_context_mapper import ADOContextMapper

    stories = [
        _make_workitem("10", "Implement login", "Active"),
        _make_workitem("11", "Fix logout bug", "Resolved"),
    ]
    result = ADOContextMapper.map(stories)

    assert "stories" in result, "map() must return stories list"
    assert len(result["stories"]) == 2
    s0 = result["stories"][0]
    assert s0["id"] == "10"
    assert s0["title"] == "Implement login"
    assert s0["state"] == "Active"
    assert "area_path" in s0


def test_map_returns_open_and_in_progress_counts() -> None:
    """AC-P20-002c: map() returns open_count and in_progress_count."""
    from cortex.intelligence.knowledge.ado_context_mapper import ADOContextMapper

    stories = [
        _make_workitem("1", state="Active"),
        _make_workitem("2", state="Active"),
        _make_workitem("3", state="Resolved"),
        _make_workitem("4", state="New"),
    ]
    result = ADOContextMapper.map(stories)

    assert "open_count" in result
    assert "in_progress_count" in result
    # "Active" → in_progress; "New" + "Resolved" → differ
    assert result["in_progress_count"] == 2, (
        f"Expected 2 in-progress, got {result['in_progress_count']}"
    )


# ---------------------------------------------------------------------------
# AC-P20-002d — missing IterationPath handled gracefully
# ---------------------------------------------------------------------------

def test_map_handles_missing_iteration_path() -> None:
    """AC-P20-002d: map() degrades gracefully when IterationPath is absent."""
    from cortex.intelligence.knowledge.ado_context_mapper import ADOContextMapper

    item = WorkItem(
        id="99",
        title="Story without iteration",
        description="",
        state="New",
        type="User Story",
        tags=[],
        url="",
        raw={"fields": {}},  # No IterationPath
    )
    result = ADOContextMapper.map([item])

    assert "sprint_name" in result
    # Should not raise — value may be empty/None/unknown
    assert result["sprint_name"] is not None or result["sprint_name"] == ""


# ---------------------------------------------------------------------------
# AC-P20-009 — empty stories list handled
# ---------------------------------------------------------------------------

def test_map_empty_stories() -> None:
    """AC-P20-009: map() with empty stories list returns empty sprint context dict."""
    from cortex.intelligence.knowledge.ado_context_mapper import ADOContextMapper

    result = ADOContextMapper.map([])

    assert isinstance(result, dict), "map([]) must return a dict"
    assert result.get("open_count", 0) == 0
    assert result.get("stories", []) == []


# ---------------------------------------------------------------------------
# AC-P20-013 — map() is a classmethod / staticmethod (no instance needed)
# ---------------------------------------------------------------------------

def test_map_is_callable_without_instantiation() -> None:
    """AC-P20-013: ADOContextMapper.map() is callable as a class/staticmethod."""
    from cortex.intelligence.knowledge.ado_context_mapper import ADOContextMapper

    # Must work without creating an instance
    result = ADOContextMapper.map([_make_workitem()])
    assert isinstance(result, dict)
