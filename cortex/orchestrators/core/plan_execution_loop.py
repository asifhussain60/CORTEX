"""PlanExecutionLoop — CAPE sub-phase 136-d.

Provides Kahn's topological sort for phase dependency graphs, a
file-based ``has_plan`` check, a policy-based ``should_continue``
gate, and a ``move_to_completed`` helper.

Author: CORTEX Framework
Compliance: CORE-008, CORE-011, CORE-012, CORE-035, CORE-064, CORE-068
AC-ID: AC-136-CAPE-004a
"""

from __future__ import annotations

import os
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List

import yaml


class PlanExecutionLoop:
    """Utilities for driving a CAPE plan through ordered phase execution.

    Provides:
    - :meth:`topological_order` — Kahn's algorithm for ``depends_on`` graphs
    - :meth:`has_plan` — file existence check
    - :meth:`should_continue` — policy-based gate evaluation
    - :meth:`move_to_completed` — persist phase completion

    Usage::

        loop = PlanExecutionLoop()
        order = loop.topological_order(phases)  # raises ValueError on cycle
        for phase_id in order:
            approved = run_gates(phase_id)
            if not loop.should_continue(gate_passed=approved, policy="HALT"):
                break
    """

    # ------------------------------------------------------------------
    # Topological ordering (Kahn's algorithm)
    # ------------------------------------------------------------------

    def topological_order(self, phases: List[Dict[str, Any]]) -> List[str]:
        """Return a topologically sorted list of phase IDs.

        Uses Kahn's algorithm (BFS-based).  Raises :class:`ValueError`
        if a cycle is detected.

        Args:
            phases: List of phase dicts.  Each must have ``"id"`` (str)
                    and ``"depends_on"`` (list of str).

        Returns:
            List of phase IDs in dependency-safe execution order
            (dependencies appear before dependents).

        Raises:
            ValueError: If a dependency cycle is detected.
        """
        in_degree: Dict[str, int] = {p["id"]: 0 for p in phases}
        graph: Dict[str, List[str]] = defaultdict(list)

        for phase in phases:
            for dep in phase.get("depends_on", []):
                graph[dep].append(phase["id"])
                in_degree[phase["id"]] += 1

        queue: deque[str] = deque(
            pid for pid, deg in in_degree.items() if deg == 0
        )
        order: List[str] = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbour in graph[node]:
                in_degree[neighbour] -= 1
                if in_degree[neighbour] == 0:
                    queue.append(neighbour)

        if len(order) != len(phases):
            raise ValueError(
                "Cycle detected in phase dependency graph — "
                f"only {len(order)} of {len(phases)} phases could be ordered."
            )
        return order

    # ------------------------------------------------------------------
    # File-based plan check
    # ------------------------------------------------------------------

    def has_plan(self, file_path: str) -> bool:
        """Return True if a phase YAML file exists at the given path.

        Args:
            file_path: Absolute or relative path to the phase YAML file.

        Returns:
            True if the file exists and is a regular file.
        """
        return Path(file_path).is_file()

    # ------------------------------------------------------------------
    # Policy gate
    # ------------------------------------------------------------------

    def should_continue(self, *, gate_passed: bool, policy: str) -> bool:
        """Decide whether execution should proceed after a gate evaluation.

        Args:
            gate_passed: True if the gate approved the phase.
            policy:      ``"HALT"`` stops on failure; ``"CONTINUE"`` proceeds.

        Returns:
            True when execution should continue.
        """
        if gate_passed:
            return True
        return policy.upper() != "HALT"

    # ------------------------------------------------------------------
    # Persist completion
    # ------------------------------------------------------------------

    def move_to_completed(self, *, src_path: str, completed_dir: str) -> str:
        """Move a phase YAML file to the completed directory and mark it COMPLETE.

        Args:
            src_path:      Absolute path to the current (planned) phase YAML.
            completed_dir: Directory where the completed file should land.

        Returns:
            Absolute path to the moved file in ``completed_dir``.
        """
        filename = Path(src_path).name
        dest_path = str(Path(completed_dir) / filename)

        # Read, update status, write to destination
        with open(src_path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}

        data["status"] = "COMPLETE"

        os.makedirs(completed_dir, exist_ok=True)
        with open(dest_path, "w", encoding="utf-8") as fh:
            yaml.dump(data, fh, default_flow_style=False, sort_keys=False)

        os.remove(src_path)
        return dest_path
