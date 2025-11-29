"""
Strategic Feature Validator

Validates operational health of strategic CORTEX features.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""
from typing import Dict, Any, Optional, List
from pathlib import Path

import yaml

class StrategicFeatureValidator:
    """Validates operational health of strategic CORTEX features.
    Returns a standard structure for each validator:
    {"status": "healthy|warning|critical|error", "details": {...}, "issues": [str, ...]}
    """

    def _ok(self, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"status": "healthy", "details": details or {}, "issues": []}

    def _warn(self, issues: List[str], details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"status": "warning", "details": details or {}, "issues": issues}

    def _crit(self, issues: List[str], details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"status": "critical", "details": details or {}, "issues": issues}

    def _error(self, err: Exception) -> Dict[str, Any]:
        return {"status": "error", "details": {}, "issues": [str(err)]}

    def _root(self) -> Path:
        # Workspace root is known from context
        return Path("/Users/asifhussain/PROJECTS/CORTEX")

    def _exists(self, rel: str) -> bool:
        return self._root().joinpath(rel).exists()

    def _load_response_templates(self) -> Optional[Dict[str, Any]]:
        try:
            p = self._root().joinpath("cortex-brain/response-templates.yaml")
            if not p.exists():
                return None
            with p.open("r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception:
            return None

    def _template_has_triggers(self, templates: Dict[str, Any], template_key: str, expected: List[str]) -> bool:
        try:
            tmpl = templates.get("templates", {}).get(template_key, {})
            triggers = set(tmpl.get("triggers", []) or [])
            return all(t in triggers for t in expected)
        except Exception:
            return False

    def validate_architecture_intelligence(self) -> Dict[str, Any]:
        """Validate Architecture Intelligence presence: docs, routing, and output location."""
        try:
            issues: List[str] = []
            guide_ok = self._exists(".github/prompts/modules/architecture-intelligence-guide.md")
            if not guide_ok:
                issues.append("Missing architecture-intelligence-guide.md")

            analysis_dir_ok = self._exists("cortex-brain/documents/analysis")
            if not analysis_dir_ok:
                issues.append("Missing analysis directory for reports")

            templates = self._load_response_templates()
            routing_ok = False
            if templates:
                routing_ok = self._template_has_triggers(
                    templates,
                    "architecture_intelligence",
                    ["review architecture", "architecture review"],
                )
            else:
                issues.append("response-templates.yaml missing/unreadable")

            if guide_ok and analysis_dir_ok and routing_ok:
                return self._ok({"docs": True, "routing": True, "reports_dir": True})
            if guide_ok and (analysis_dir_ok or routing_ok):
                return self._warn(issues, {"docs": guide_ok, "routing": routing_ok, "reports_dir": analysis_dir_ok})
            return self._crit(issues, {"docs": guide_ok, "routing": routing_ok, "reports_dir": analysis_dir_ok})
        except Exception as e:
            return self._error(e)

    def validate_rollback_system(self) -> Dict[str, Any]:
        """Validate Git Checkpoint rollback system: guide, rules, and tests."""
        try:
            issues: List[str] = []
            guide_ok = self._exists("cortex-brain/documents/implementation-guides/git-checkpoint-guide.md")
            rules_ok = self._exists("cortex-brain/git-checkpoint-rules.yaml")
            tests_ok = self._exists("tests/test_git_checkpoint_system.py") or self._exists("test_git_checkpoint_system.py")

            if not guide_ok:
                issues.append("Missing git-checkpoint-guide.md")
            if not rules_ok:
                issues.append("Missing git-checkpoint-rules.yaml")
            if not tests_ok:
                issues.append("Missing checkpoint system tests")

            if guide_ok and rules_ok and tests_ok:
                return self._ok({"docs": True, "rules": True, "tests": True})
            if guide_ok and (rules_ok or tests_ok):
                return self._warn(issues, {"docs": guide_ok, "rules": rules_ok, "tests": tests_ok})
            return self._crit(issues, {"docs": guide_ok, "rules": rules_ok, "tests": tests_ok})
        except Exception as e:
            return self._error(e)

    def validate_swagger_dor(self) -> Dict[str, Any]:
        """Validate planning DoR/DoD system and ADO routing in templates."""
        try:
            issues: List[str] = []
            guide_ok = self._exists(".github/prompts/modules/planning-orchestrator-guide.md")
            templates = self._load_response_templates()
            ado_routing_ok = False
            planning_routing_ok = False
            if templates:
                ado_routing_ok = self._template_has_triggers(
                    templates,
                    "ado_planning",
                    ["plan ado", "ado feature", "create ado work item"],
                )
                planning_routing_ok = self._template_has_triggers(
                    templates,
                    "work_planner_success",
                    ["plan", "planning"],
                )
            else:
                issues.append("response-templates.yaml missing/unreadable")

            if not guide_ok:
                issues.append("Missing planning-orchestrator-guide.md")

            if guide_ok and ado_routing_ok and planning_routing_ok:
                return self._ok({"docs": True, "ado_routing": True, "planning_routing": True})
            if guide_ok and (ado_routing_ok or planning_routing_ok):
                return self._warn(issues, {"docs": guide_ok, "ado_routing": ado_routing_ok, "planning_routing": planning_routing_ok})
            return self._crit(issues, {"docs": guide_ok, "ado_routing": ado_routing_ok, "planning_routing": planning_routing_ok})
        except Exception as e:
            return self._error(e)

    def validate_ux_enhancement(self) -> Dict[str, Any]:
        """Validate UX Enhancement orchestrator docs and routing."""
        try:
            issues: List[str] = []
            # Guide present
            guide_ok = self._exists(".github/prompts/modules/architecture-intelligence-guide.md") or self._exists(
                ".github/prompts/modules/hands-on-tutorial-guide.md"
            ) or self._exists(".github/prompts/modules/response-format.md")

            templates = self._load_response_templates()
            ux_routing_ok = False
            if templates:
                ux_routing_ok = self._template_has_triggers(
                    templates,
                    "ux_enhancement",
                    ["ux enhancement", "analyze ux"],
                )
            else:
                issues.append("response-templates.yaml missing/unreadable")

            orchestrator_ok = self._exists("src/orchestrators/ux_enhancement_orchestrator.py")
            if not orchestrator_ok:
                issues.append("Missing UXEnhancementOrchestrator module")

            if guide_ok and ux_routing_ok and orchestrator_ok:
                return self._ok({"docs": True, "routing": True, "orchestrator": True})
            if guide_ok and (ux_routing_ok or orchestrator_ok):
                return self._warn(issues, {"docs": guide_ok, "routing": ux_routing_ok, "orchestrator": orchestrator_ok})
            return self._crit(issues, {"docs": guide_ok, "routing": ux_routing_ok, "orchestrator": orchestrator_ok})
        except Exception as e:
            return self._error(e)

    def validate_ado_agent(self) -> Dict[str, Any]:
        """Validate ADO Agent: routing, agent implementation, and DB presence."""
        try:
            issues: List[str] = []
            templates = self._load_response_templates()
            ado_routing_ok = False
            if templates:
                ado_routing_ok = self._template_has_triggers(
                    templates,
                    "ado_operations",
                    ["ado summary", "ado pr review"],
                )
            else:
                issues.append("response-templates.yaml missing/unreadable")

            agent_ok = self._exists("src/cortex_agents/ado_agent.py") or self._exists(
                "src/cortex_agents/ado_agent/ADOAgent.py"
            )
            db_ok = self._exists("cortex-brain/ado-work-items.db")
            if not agent_ok:
                issues.append("Missing ADOAgent implementation")
            if not db_ok:
                issues.append("Missing ado-work-items.db")

            if ado_routing_ok and agent_ok and db_ok:
                return self._ok({"routing": True, "agent": True, "db": True})
            if (ado_routing_ok and (agent_ok or db_ok)) or (agent_ok and db_ok):
                return self._warn(issues, {"routing": ado_routing_ok, "agent": agent_ok, "db": db_ok})
            return self._crit(issues, {"routing": ado_routing_ok, "agent": agent_ok, "db": db_ok})
        except Exception as e:
            return self._error(e)
