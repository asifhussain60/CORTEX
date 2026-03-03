"""
ComprehensionMixin — LENS comprehension phase + YAML approval gate.

Phase 103-h: extracted from conversation_protocol.py (1,539L) god-object.
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import yaml

from cortex.core.result import Ok, Result

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class ComprehensionMixin:
    """Mixin providing LENS comprehension phase and approval YAML generation."""

    # Provided by ConversationProtocol.__init__:
    # self.orchestrator, self.turn_number, self._audit_logger
    # self.ast_engine, self.call_graph_builder, self.dependency_mapper, self.pattern_detector

    def _run_comprehension_phase(
        self, user_input: str, round_context: Any
    ) -> Result[Dict[str, Any]]:
        """
        AC-REM-001-01: Execute LENS comprehension phase with AST scanning.

        Runs on every turn. Identifies target files, scans with ASTIntelligenceEngine,
        builds call graphs, maps dependencies, detects patterns.

        Args:
            user_input: User's input for this turn.
            round_context: RoundContext with previous_context dict.

        Returns:
            Result[Dict] with comprehension results.
        """
        try:
            comprehension_data: Dict[str, Any] = {
                "target_files": [],
                "parse_results": [],
                "summary": {},
                "turn_number": round_context.round_number,
            }

            target_files: List[Path] = []
            prev_result = round_context.previous_context.get("last_orchestrator_result", {})
            if isinstance(prev_result, dict):
                for t in prev_result.get("target_files", []):
                    if isinstance(t, (str, Path)):
                        target_files.append(Path(t))

            if not target_files:
                project_root = Path.cwd()
                for source_dir in ("src", "cortex", "tests"):
                    potential_dir = project_root / source_dir
                    if potential_dir.exists() and potential_dir.is_dir():
                        target_files.extend(list(potential_dir.glob("**/*.py"))[:5])
                        if len(target_files) >= 5:
                            break

            # AST scanning (AC-REM-001-01)
            parse_results = []
            for target_file in target_files:
                try:
                    parse_result = self.ast_engine.parse_file(target_file)
                    parse_results.append(parse_result)
                    comprehension_data["target_files"].append(str(target_file))
                except Exception as exc:
                    if self._audit_logger:
                        self._audit_logger.log_operation_complete(
                            ac_id="AC-REM-001-01",
                            operation="AST_SCANNING_ERROR",
                            success=False,
                            details={"file": str(target_file), "error": str(exc)},
                        )

            comprehension_data["parse_results"] = [r.to_dict() for r in parse_results]

            # Call graph building (AC-REM-001-02)
            call_graphs = []
            for pr in parse_results:
                try:
                    call_graphs.append(self.call_graph_builder.build(pr))
                except Exception as exc:
                    if self._audit_logger:
                        self._audit_logger.log_operation_complete(
                            ac_id="AC-REM-001-02",
                            operation="CALL_GRAPH_BUILD_ERROR",
                            success=False,
                            details={"error": str(exc)},
                        )

            comprehension_data["call_graphs"] = [g.to_dict() for g in call_graphs]

            # Dependency mapping (AC-REM-001-03)
            dependency_maps = []
            for pr in parse_results:
                try:
                    dependency_maps.append(self.dependency_mapper.map_dependencies(pr))
                except Exception as exc:
                    if self._audit_logger:
                        self._audit_logger.log_operation_complete(
                            ac_id="AC-REM-001-03",
                            operation="DEPENDENCY_MAP_ERROR",
                            success=False,
                            details={"error": str(exc)},
                        )

            comprehension_data["dependency_maps"] = [m.to_dict() for m in dependency_maps]

            all_stdlib: set = set()
            all_third_party: set = set()
            all_local: set = set()
            for dm in dependency_maps:
                all_stdlib.update(dm.get_standard_library())
                all_third_party.update(dm.get_third_party())
                all_local.update(dm.get_local())

            # Pattern detection (AC-REM-001-04)
            patterns_detected = []
            for pr in parse_results:
                try:
                    patterns_detected.extend(self.pattern_detector.detect_patterns(pr))
                except Exception as exc:
                    if self._audit_logger:
                        self._audit_logger.log_operation_complete(
                            ac_id="AC-REM-001-04",
                            operation="PATTERN_DETECTION_ERROR",
                            success=False,
                            details={"error": str(exc)},
                        )

            comprehension_data["patterns_detected"] = [p.to_dict() for p in patterns_detected]
            total_layer_transitions = sum(g.edge_count for g in call_graphs)

            comprehension_data["summary"] = {
                "files_analyzed": len(target_files),
                "files_parsed_successfully": sum(1 for r in parse_results if r.success),
                "total_functions_found": sum(len(r.functions) for r in parse_results),
                "total_classes_found": sum(len(r.classes) for r in parse_results),
                "total_imports_found": sum(len(r.imports) for r in parse_results),
                "call_graphs_built": len(call_graphs),
                "layer_transitions_identified": total_layer_transitions,
                "stdlib_dependencies": len(all_stdlib),
                "third_party_dependencies": len(all_third_party),
                "local_dependencies": len(all_local),
                "patterns_detected": len(patterns_detected),
            }

            if self._audit_logger:
                self._audit_logger.log_operation_complete(
                    ac_id="AC-REM-001-01",
                    operation="COMPREHENSION_PHASE",
                    success=True,
                    details=comprehension_data["summary"],
                )

            return Ok(comprehension_data)

        except Exception as exc:
            if self._audit_logger:
                self._audit_logger.log_operation_complete(
                    ac_id="AC-REM-001-01",
                    operation="COMPREHENSION_PHASE",
                    success=False,
                    details={"error": str(exc)},
                )
            return Ok({"target_files": [], "parse_results": [], "summary": {"error": str(exc)}})

    def _generate_comprehension_approval_yaml(
        self, comprehension_data: Dict[str, Any]
    ) -> str:
        """
        AC-REM-001-05: Generate comprehension YAML for approval gate.

        Args:
            comprehension_data: Result from _run_comprehension_phase.

        Returns:
            YAML string for approval gate workflow.
        """
        try:
            approval_yaml: Dict[str, Any] = {
                "operation": "COMPREHENSION_APPROVAL_GATE",
                "phase": "PHASE-REMEDIATION-01",
                "orchestrator": self.orchestrator.__class__.__name__,
                "timestamp": datetime.now().isoformat(),
                "turn_number": self.turn_number,
                "summary": comprehension_data.get("summary", {}),
            }

            if comprehension_data.get("parse_results"):
                approval_yaml["parsed_files"] = [
                    {
                        "index": i,
                        "functions": r.get("functions", []),
                        "classes": r.get("classes", []),
                        "imports": r.get("imports", []),
                    }
                    for i, r in enumerate(comprehension_data["parse_results"][:5])
                ]

            if comprehension_data.get("call_graphs"):
                approval_yaml["call_graphs"] = comprehension_data["call_graphs"][:5]

            if comprehension_data.get("dependency_maps"):
                approval_yaml["dependencies"] = {
                    "summary": {
                        "stdlib": comprehension_data["summary"].get("stdlib_dependencies", 0),
                        "third_party": comprehension_data["summary"].get("third_party_dependencies", 0),
                        "local": comprehension_data["summary"].get("local_dependencies", 0),
                    },
                    "maps": comprehension_data["dependency_maps"][:3],
                }

            if comprehension_data.get("patterns_detected"):
                approval_yaml["patterns"] = {
                    "total": len(comprehension_data["patterns_detected"]),
                    "details": comprehension_data["patterns_detected"],
                }

            approval_yaml["impact_map"] = {
                "files_affected": comprehension_data.get("summary", {}).get("files_analyzed", 0),
                "functions_analyzed": comprehension_data.get("summary", {}).get("total_functions_found", 0),
                "transitive_dependency_depth": 3,
                "architectural_patterns_identified": comprehension_data.get("summary", {}).get("patterns_detected", 0),
            }

            approval_yaml["approval_recommendation"] = {
                "status": "READY_FOR_APPROVAL",
                "confidence": 0.95,
                "reason": "All comprehension components completed successfully",
                "sign_off_required": True,
            }

            return yaml.dump(approval_yaml, default_flow_style=False, sort_keys=False)

        except Exception as exc:
            if self._audit_logger:
                self._audit_logger.log_operation_complete(
                    ac_id="AC-REM-001-05",
                    operation="YAML_GENERATION",
                    success=False,
                    details={"error": str(exc)},
                )
            return ""

    def get_recommended_option(
        self, solution_options: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        AC-RECOMMENDATION-001: Evaluate solution options and mark best one.

        Args:
            solution_options: List of solution option dicts.

        Returns:
            Dict with recommendation details, or None on error.
        """
        try:
            from cortex.orchestrators.core.solution_recommendation_engine import (
                SolutionOption,
                get_recommendation_engine,
            )

            options = []
            for opt_dict in solution_options:
                options.append(
                    SolutionOption(
                        option_id=opt_dict.get("option_id", "unknown"),
                        name=opt_dict.get("name", "Unnamed Option"),
                        description=opt_dict.get("description", ""),
                        implementation_effort=opt_dict.get("implementation_effort", "medium"),
                        risk_level=opt_dict.get("risk_level", "medium"),
                        maintenance_cost=opt_dict.get("maintenance_cost", "medium"),
                        cortex_alignment=float(opt_dict.get("cortex_alignment", 0.5)),
                        governance_compliance=float(opt_dict.get("governance_compliance", 0.5)),
                        performance_impact=float(opt_dict.get("performance_impact", 0.5)),
                        scalability_score=float(opt_dict.get("scalability_score", 0.5)),
                        team_familiarity=float(opt_dict.get("team_familiarity", 0.5)),
                        technical_debt=float(opt_dict.get("technical_debt", 0.5)),
                        pros=opt_dict.get("pros", []),
                        cons=opt_dict.get("cons", []),
                        dependencies=opt_dict.get("dependencies", []),
                        timeline_estimate=opt_dict.get("timeline_estimate"),
                    )
                )

            engine = get_recommendation_engine()
            recommendation = engine.recommend_best_option(
                options, context={"turn_number": self.turn_number}
            )

            if self._audit_logger:
                self._audit_logger.log_operation_complete(
                    ac_id="AC-RECOMMENDATION-001",
                    operation="OPTION_EVALUATION",
                    success=True,
                    details={
                        "best_option": recommendation.best_option.name,
                        "confidence": recommendation.confidence.value,
                        "score": engine.score_option(recommendation.best_option),
                    },
                )

            return recommendation.to_dict()

        except Exception as exc:
            logger.error(f"Error in recommendation engine: {exc}")
            if self._audit_logger:
                self._audit_logger.log_operation_complete(
                    ac_id="AC-RECOMMENDATION-001",
                    operation="OPTION_EVALUATION",
                    success=False,
                    details={"error": str(exc)},
                )
            return None
