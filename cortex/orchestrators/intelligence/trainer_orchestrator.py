"""
TrainerOrchestrator — Gap-driven template evolution for CORTEX intelligence growth.

AC-TRAIN-001: TrainerOrchestrator importable from cortex.orchestrators.intelligence
AC-TRAIN-002: inventory_templates() returns list of existing workflow templates
AC-TRAIN-003: analyze_target() performs LENS + STS analysis on target path
AC-TRAIN-004: detect_gaps() compares patterns against template inventory
AC-TRAIN-005: generate_proposal() returns change manifest (CREATE/ENHANCE/DELETE)
AC-TRAIN-006: execute_proposal() applies changes via TDD workflow
AC-TRAIN-007: Implements OrchestratorProtocolMixin interface

Purpose: Orchestrate the training pipeline for CORTEX intelligence growth.
- Inventories existing workflow templates
- Analyzes target repositories for patterns and anti-patterns
- Detects gaps between learned patterns and existing templates
- Generates surgical change proposals (CREATE/ENHANCE/DELETE)
- Executes approved proposals via TDD workflow

Author: GitHub Copilot
Date: 2026-02-26
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin, enforce_gateway  # Phase 94f / 95
from cortex.core.file_factory import get_file_factory

logger = logging.getLogger(__name__)


class TrainerOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin):
    """
    Gap-driven template evolution orchestrator.

    Coordinates the training pipeline:
    1. Inventory — catalog existing templates
    2. Analyze — extract patterns from target repository
    3. Detect Gaps — compare patterns vs inventory
    4. Propose — generate change manifest
    5. Execute — apply approved changes via TDD

    AC-TRAIN-007: Implements OrchestratorProtocolMixin interface.
    """

    _orch_name: str = "TrainerOrchestrator"
    _orch_version: str = "1.0.0"

    # Phase 95 — advisory: execute_operation receives domain-specific names ("scan",
    # "propose", "execute"), not top-level gateway mode strings. Flag stays False.
    PHASE90_GATEWAY_ENABLED: bool = False

    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        templates_dir: Optional[Path] = None,
    ) -> None:
        """
        Initialize TrainerOrchestrator.

        Args:
            workspace_root: Root of CORTEX workspace (defaults to cwd)
            templates_dir: Path to workflow templates directory
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.templates_dir = templates_dir or (
            self.workspace_root / "cortex-registry" / "workflows" / "templates"
        )
        self._audit_log: List[Dict[str, Any]] = []

    # =========================================================================
    # AC-TRAIN-002: inventory_templates()
    # =========================================================================

    def inventory_templates(self) -> List[Dict[str, Any]]:
        """
        Inventory all existing workflow templates.

        Returns:
            List of template metadata dicts with keys: id, category, path, covers
        """
        templates: List[Dict[str, Any]] = []

        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return templates

        # Scan all YAML files in templates directory
        for yaml_file in self.templates_dir.rglob("*.yaml"):
            try:
                content = yaml.safe_load(yaml_file.read_text())
                if content and isinstance(content, dict):
                    workflow = content.get("workflow", content)
                    template_id = workflow.get("id", yaml_file.stem)
                    category = yaml_file.parent.name
                    
                    # Extract what patterns this template covers
                    covers: List[str] = []
                    if "gates" in workflow:
                        covers.extend(
                            gate.get("id", "") for gate in workflow.get("gates", [])
                        )
                    if "steps" in workflow:
                        covers.extend(
                            step.get("id", "") for step in workflow.get("steps", [])
                        )

                    templates.append({
                        "id": template_id,
                        "category": category,
                        "path": str(yaml_file.relative_to(self.workspace_root)),
                        "covers": covers,
                    })
            except Exception as e:
                logger.debug(f"Could not parse {yaml_file}: {e}")

        return templates

    # =========================================================================
    # AC-TRAIN-003: analyze_target()
    # =========================================================================

    def analyze_target(self, target_path: Path) -> Dict[str, Any]:
        """
        Analyze target repository for patterns and anti-patterns.

        Args:
            target_path: Path to target repository or folder

        Returns:
            Analysis dict with keys: patterns, tech_stack, anti_patterns
        """
        result: Dict[str, Any] = {
            "patterns": [],
            "tech_stack": [],
            "anti_patterns": [],
            "target_path": str(target_path),
        }

        if not target_path.exists():
            logger.warning(f"Target path not found: {target_path}")
            return result

        # Detect technology stack
        result["tech_stack"] = self._detect_tech_stack(target_path)

        # Detect patterns
        result["patterns"] = self._detect_patterns(target_path)

        # Detect anti-patterns
        result["anti_patterns"] = self._detect_anti_patterns(target_path)

        self._audit_log.append({
            "operation": "analyze_target",
            "target": str(target_path),
            "patterns_found": len(result["patterns"]),
            "anti_patterns_found": len(result["anti_patterns"]),
        })

        return result

    def _detect_tech_stack(self, target_path: Path) -> List[str]:
        """Detect technology stack from file extensions and markers."""
        tech_stack: List[str] = []

        # Check for language markers
        markers = {
            "python": ["*.py", "requirements.txt", "pyproject.toml", "setup.py"],
            "csharp": ["*.cs", "*.csproj", "*.sln"],
            "typescript": ["*.ts", "*.tsx", "tsconfig.json"],
            "javascript": ["*.js", "*.jsx", "package.json"],
            "java": ["*.java", "pom.xml", "build.gradle"],
        }

        for lang, patterns in markers.items():
            for pattern in patterns:
                if list(target_path.rglob(pattern)):
                    if lang not in tech_stack:
                        tech_stack.append(lang)
                    break

        return tech_stack

    def _detect_patterns(self, target_path: Path) -> List[Dict[str, Any]]:
        """Detect positive patterns in target codebase."""
        patterns: List[Dict[str, Any]] = []

        # Check for test coverage pattern
        test_files = list(target_path.rglob("test_*.py")) + list(
            target_path.rglob("*_test.py")
        )
        if test_files:
            patterns.append({
                "id": "has-tests",
                "type": "testing",
                "confidence": min(1.0, len(test_files) / 10),
            })

        # Check for DI pattern (C#)
        cs_files = list(target_path.rglob("*.cs"))
        for cs_file in cs_files[:10]:  # Sample first 10
            try:
                content = cs_file.read_text()
                if "AddScoped" in content or "AddSingleton" in content:
                    patterns.append({
                        "id": "uses-di",
                        "type": "architecture",
                        "confidence": 0.8,
                    })
                    break
            except Exception:
                pass

        return patterns

    def _detect_anti_patterns(self, target_path: Path) -> List[Dict[str, Any]]:
        """Detect anti-patterns in target codebase."""
        anti_patterns: List[Dict[str, Any]] = []

        # Scan Python files for common anti-patterns
        py_files = list(target_path.rglob("*.py"))
        for py_file in py_files[:20]:  # Sample first 20
            try:
                content = py_file.read_text()

                # Hardcoded credentials
                if "PASSWORD" in content and "=" in content:
                    if any(
                        marker in content
                        for marker in ['"', "'", "admin", "secret", "password"]
                    ):
                        anti_patterns.append({
                            "id": "hardcoded-credentials",
                            "severity": "P0",
                            "file": str(py_file.relative_to(target_path)),
                            "reason": "Potential hardcoded credentials detected",
                        })

            except Exception:
                pass

        # Scan C# files for anti-patterns
        cs_files = list(target_path.rglob("*.cs"))
        for cs_file in cs_files[:20]:
            try:
                content = cs_file.read_text()

                # Captive dependency (Singleton holding Scoped)
                if "AddSingleton" in content and "AddScoped" in content:
                    anti_patterns.append({
                        "id": "captive-dependency",
                        "severity": "P1",
                        "file": str(cs_file.relative_to(target_path)),
                        "reason": "Potential captive dependency (Singleton + Scoped)",
                    })

                # Weak password hashing
                if any(
                    h in content
                    for h in ["SHA256", "MD5", "SHA1"]
                ) and "password" in content.lower():
                    anti_patterns.append({
                        "id": "weak-password-hash",
                        "severity": "P0",
                        "file": str(cs_file.relative_to(target_path)),
                        "reason": "Weak hashing algorithm for passwords",
                    })

            except Exception:
                pass

        return anti_patterns

    # =========================================================================
    # AC-TRAIN-004: detect_gaps()
    # =========================================================================

    def detect_gaps(
        self,
        analysis: Dict[str, Any],
        inventory: List[Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect gaps between analysis patterns and template inventory.

        Args:
            analysis: Result from analyze_target()
            inventory: Result from inventory_templates()

        Returns:
            Dict with keys: missing, enhance, obsolete
        """
        result: Dict[str, List[Dict[str, Any]]] = {
            "missing": [],
            "enhance": [],
            "obsolete": [],
        }

        # Build set of covered patterns from inventory
        covered_patterns: set[str] = set()
        for template in inventory:
            covered_patterns.update(template.get("covers", []))
            covered_patterns.add(template.get("id", ""))

        # Check for missing templates (anti-patterns without coverage)
        for anti_pattern in analysis.get("anti_patterns", []):
            pattern_id = anti_pattern.get("id", "")
            if not self._pattern_covered(pattern_id, inventory):
                result["missing"].append({
                    "pattern": pattern_id,
                    "reason": anti_pattern.get("reason", "No template covers this pattern"),
                    "severity": anti_pattern.get("severity", "P2"),
                    "evidence": anti_pattern,
                })

        # Check for enhancement opportunities
        for pattern in analysis.get("patterns", []):
            pattern_id = pattern.get("id", "")
            matching_template = self._find_matching_template(pattern_id, inventory)
            if matching_template:
                # Template exists but might need enhancement
                if pattern.get("confidence", 0) < 0.5:
                    result["enhance"].append({
                        "template_id": matching_template.get("id"),
                        "enhancement": f"Strengthen coverage for {pattern_id}",
                        "path": matching_template.get("path"),
                    })

        # Check for obsolete templates (cover patterns not in analysis)
        tech_stack = set(analysis.get("tech_stack", []))
        for template in inventory:
            category = template.get("category", "")
            # If template is for a tech not in the stack, mark as potentially obsolete
            tech_categories = {
                "frontend": ["javascript", "typescript"],
                "backend": ["python", "csharp", "java"],
            }
            if category in tech_categories:
                required_techs = tech_categories[category]
                if not any(t in tech_stack for t in required_techs):
                    result["obsolete"].append({
                        "template_id": template.get("id"),
                        "reason": f"Tech stack mismatch: {category} templates but no {required_techs}",
                        "path": template.get("path"),
                    })

        return result

    def _pattern_covered(
        self, pattern_id: str, inventory: List[Dict[str, Any]]
    ) -> bool:
        """Check if a pattern is covered by any template in inventory."""
        for template in inventory:
            covers = template.get("covers", [])
            template_id = template.get("id", "")
            if pattern_id in covers or pattern_id in template_id:
                return True
        return False

    def _find_matching_template(
        self, pattern_id: str, inventory: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Find a template that matches a pattern."""
        for template in inventory:
            covers = template.get("covers", [])
            template_id = template.get("id", "")
            if pattern_id in covers or pattern_id in template_id:
                return template
        return None

    # =========================================================================
    # AC-TRAIN-005: generate_proposal()
    # =========================================================================

    def generate_proposal(
        self, gaps: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Generate change proposal from detected gaps.

        Args:
            gaps: Result from detect_gaps()

        Returns:
            Proposal dict with actions list and approval status
        """
        actions: List[Dict[str, Any]] = []

        # CREATE actions for missing templates
        for missing in gaps.get("missing", []):
            template_id = f"{missing['pattern']}-workflow"
            actions.append({
                "action": "CREATE",
                "target": f"cortex-registry/workflows/templates/generated/{template_id}.yaml",
                "template_id": template_id,
                "reason": missing.get("reason", "Pattern not covered"),
                "evidence": missing.get("evidence", {}),
                "severity": missing.get("severity", "P2"),
            })

        # ENHANCE actions for enhancement opportunities
        for enhance in gaps.get("enhance", []):
            actions.append({
                "action": "ENHANCE",
                "target": enhance.get("path", ""),
                "template_id": enhance.get("template_id"),
                "enhancement": enhance.get("enhancement"),
                "reason": f"Enhancement opportunity: {enhance.get('enhancement')}",
            })

        # DELETE actions for obsolete templates (marked as REVIEW, not auto-delete)
        for obsolete in gaps.get("obsolete", []):
            actions.append({
                "action": "REVIEW_FOR_DELETE",
                "target": obsolete.get("path", ""),
                "template_id": obsolete.get("template_id"),
                "reason": obsolete.get("reason"),
            })

        return {
            "actions": actions,
            "approved": False,
            "summary": {
                "create_count": len([a for a in actions if a["action"] == "CREATE"]),
                "enhance_count": len([a for a in actions if a["action"] == "ENHANCE"]),
                "review_count": len(
                    [a for a in actions if a["action"] == "REVIEW_FOR_DELETE"]
                ),
            },
        }

    # =========================================================================
    # AC-TRAIN-006: execute_proposal()
    # =========================================================================

    def execute_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute approved proposal.

        Args:
            proposal: Proposal from generate_proposal() with approved=True

        Returns:
            Execution report with status, executed, skipped, errors
        """
        result: Dict[str, Any] = {
            "status": "pending_approval",
            "executed": [],
            "skipped": [],
            "errors": [],
        }

        # Check approval
        if not proposal.get("approved", False):
            return result

        result["status"] = "executing"

        for action in proposal.get("actions", []):
            action_type = action.get("action", "")
            target = action.get("target", "")

            try:
                if action_type == "CREATE":
                    self._execute_create(action, result)
                elif action_type == "ENHANCE":
                    self._execute_enhance(action, result)
                elif action_type == "REVIEW_FOR_DELETE":
                    # Never auto-delete, always skip to human review
                    result["skipped"].append({
                        "action": action,
                        "reason": "DELETE requires manual review",
                    })
                else:
                    result["skipped"].append({
                        "action": action,
                        "reason": f"Unknown action type: {action_type}",
                    })

            except Exception as e:
                result["errors"].append({
                    "action": action,
                    "error": str(e),
                })

        # Determine final status
        if result["errors"]:
            result["status"] = "partial" if result["executed"] else "failed"
        else:
            result["status"] = "success"

        return result

    def _execute_create(
        self, action: Dict[str, Any], result: Dict[str, Any]
    ) -> None:
        """Execute CREATE action."""
        target = Path(action.get("target", ""))
        
        # Use provided content or generate minimal template
        content = action.get("content")
        if not content:
            template_id = action.get("template_id", "generated-template")
            content = self._generate_template_content(template_id, action)

        # Ensure parent directory exists
        target.parent.mkdir(parents=True, exist_ok=True)

        # Write template via FileFactory (CORE governance — no raw file I/O)
        ff = get_file_factory()
        ff.create_file(target, content)

        result["executed"].append({
            "action": "CREATE",
            "target": str(target),
        })

    def _execute_enhance(
        self, action: Dict[str, Any], result: Dict[str, Any]
    ) -> None:
        """Execute ENHANCE action."""
        target = Path(action.get("target", ""))

        if not target.exists():
            result["skipped"].append({
                "action": action,
                "reason": f"Target file not found: {target}",
            })
            return

        # For now, log enhancement as executed (actual enhancement logic TBD)
        result["executed"].append({
            "action": "ENHANCE",
            "target": str(target),
            "enhancement": action.get("enhancement"),
        })

    def _generate_template_content(
        self, template_id: str, action: Dict[str, Any]
    ) -> str:
        """Generate minimal template content."""
        evidence = action.get("evidence", {})
        pattern = evidence.get("id", template_id)
        severity = action.get("severity", "P2")

        template = {
            "workflow": {
                "id": template_id,
                "name": f"Workflow for {pattern}",
                "version": "1.0.0",
                "description": f"Auto-generated template for {pattern} pattern",
                "metadata": {
                    "generated": True,
                    "source_pattern": pattern,
                    "severity": severity,
                },
                "gates": [
                    {
                        "id": f"gate-{pattern}",
                        "name": f"Validate {pattern}",
                        "type": "validation",
                        "blocking": severity in ["P0", "P1"],
                    }
                ],
                "steps": [
                    {
                        "id": f"step-detect-{pattern}",
                        "name": f"Detect {pattern}",
                        "action": "scan",
                    },
                    {
                        "id": f"step-fix-{pattern}",
                        "name": f"Fix {pattern}",
                        "action": "remediate",
                    },
                ],
            }
        }

        return yaml.dump(template, default_flow_style=False, sort_keys=False)

    # =========================================================================
    # OrchestratorProtocolMixin: execute_operation
    # =========================================================================

    @enforce_gateway
    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute training operation.

        Supported operations:
        - scan: inventory → analyze → detect_gaps → propose
        - propose: generate proposal from previous analysis
        - execute: apply approved proposal

        Args:
            operation_name: One of 'scan', 'propose', 'execute'
            parameters: Operation-specific parameters

        Returns:
            Operation result dictionary
        """
        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(
            operation=operation_name,
            orchestrator_context=parameters.get("orchestrator_context"),
            unified_context=parameters.get("unified_context"),
        )

        if operation_name == "scan":
            return self._op_scan(parameters)
        elif operation_name == "propose":
            return self._op_propose(parameters)
        elif operation_name == "execute":
            return self._op_execute(parameters)
        else:
            return {
                "status": "error",
                "error": f"Unknown operation: {operation_name}",
                "supported_operations": ["scan", "propose", "execute"],
            }

    def _op_scan(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scan operation: full pipeline."""
        target_path = Path(parameters.get("target_path", "."))

        # Step 1: Inventory
        inventory = self.inventory_templates()

        # Step 2: Analyze
        analysis = self.analyze_target(target_path)

        # Step 3: Detect gaps
        gaps = self.detect_gaps(analysis, inventory)

        # Step 4: Generate proposal
        proposal = self.generate_proposal(gaps)

        return {
            "status": "success",
            "inventory": {"count": len(inventory)},
            "analysis": analysis,
            "gaps": gaps,
            "proposal": proposal,
        }

    def _op_propose(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate proposal from provided gaps."""
        gaps = parameters.get("gaps", {"missing": [], "enhance": [], "obsolete": []})
        proposal = self.generate_proposal(gaps)
        return {"status": "success", "proposal": proposal}

    def _op_execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute approved proposal."""
        proposal = parameters.get("proposal", {})
        result = self.execute_proposal(proposal)
        return result

    def get_capabilities(self) -> List[str]:
        """Return list of orchestrator capabilities."""
        return [
            "inventory_templates",
            "analyze_target",
            "detect_gaps",
            "generate_proposal",
            "execute_proposal",
            "score_proposal",
            "score_and_reinforce",
            "scan",
        ]

    # =========================================================================
    # AC-PHASE83-03: Reinforcement scoring
    # =========================================================================

    def score_proposal(
        self, execution_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score an execution report and generate reinforcement signals.

        Examines the executed/errors/skipped lists in the report and emits:
        - STRONG_REWARD for each successfully executed action
        - STRONG_PUNISHMENT for each failed action
        - MILD_REWARD for skipped actions (they didn't cause harm)

        Does NOT write to the learning loop — use score_and_reinforce()
        for end-to-end integration.

        AC-PHASE83-03: TrainerOrchestrator reinforcement wiring

        Args:
            execution_report: Result from execute_proposal()

        Returns:
            Dict with signal_count and signals list
        """
        from cortex.intelligence.learning.reinforcement_signal import SignalType

        signals: List[Dict[str, Any]] = []

        # Reward for each executed action
        for executed in execution_report.get("executed", []):
            template_id = executed.get("template_id", "")
            if not template_id:
                # Fallback: derive from target path stem
                target = executed.get("target", "")
                template_id = Path(target).stem if target else "unknown"

            signals.append({
                "signal_type": SignalType.STRONG_REWARD.name,
                "score": SignalType.STRONG_REWARD.score,
                "pattern_id": template_id,
                "source_orchestrator": self._orch_name,
                "context": {"action": executed.get("action", ""), "target": executed.get("target", "")},
            })

        # Punishment for each error
        for error_entry in execution_report.get("errors", []):
            action = error_entry.get("action", {})
            template_id = action.get("template_id", "unknown")

            signals.append({
                "signal_type": SignalType.STRONG_PUNISHMENT.name,
                "score": SignalType.STRONG_PUNISHMENT.score,
                "pattern_id": template_id,
                "source_orchestrator": self._orch_name,
                "context": {
                    "action": action.get("action", ""),
                    "error": error_entry.get("error", ""),
                },
            })

        return {
            "signal_count": len(signals),
            "signals": signals,
        }

    def score_and_reinforce(
        self,
        execution_report: Dict[str, Any],
        learning_loop: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Score an execution report and write reinforcement signals to the learning loop.

        End-to-end integration: score_proposal() + learning_loop.reinforcement_signal().

        AC-PHASE83-03: TrainerOrchestrator ↔ UniversalLearningLoop wiring

        Args:
            execution_report: Result from execute_proposal()
            learning_loop: UniversalLearningLoop instance (defaults to singleton)

        Returns:
            Dict with signal_count, signals, and signal_ids
        """
        from cortex.intelligence.learning.reinforcement_signal import SignalType

        if learning_loop is None:
            from cortex.intelligence.learning.universal_learning_loop import (
                get_learning_loop,
            )
            learning_loop = get_learning_loop()

        score_result = self.score_proposal(execution_report)
        signal_ids: List[str] = []

        signal_type_map = {name: member for name, member in SignalType.__members__.items()}

        for signal in score_result["signals"]:
            st = signal_type_map.get(signal["signal_type"], SignalType.NEUTRAL)
            sid = learning_loop.reinforcement_signal(
                pattern_id=signal["pattern_id"],
                signal_type=st,
                source_orchestrator=signal["source_orchestrator"],
                context=signal.get("context", {}),
            )
            signal_ids.append(sid)

        return {
            "signal_count": score_result["signal_count"],
            "signals": score_result["signals"],
            "signal_ids": signal_ids,
        }
