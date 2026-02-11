"""
Domain Knowledge Merger Orchestrator - Phase 19 Core Component.

Implements the "snowball effect" for domain knowledge accumulation:
- Entities: Merge across repository scans
- Patterns: 3-tier promotion system (Candidate → Learned → Known)
- Vendors: Accumulate unique vendor dependencies
- Company Precedence: company/ YAMLs override CORTEX defaults

AC-ID: AC-PHASE-19-DOMAIN-MERGER-001
Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings), CORE-035 (Single implementation)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

from cortex.brain.core.result import Err, Ok, Result
from cortex.core.interfaces import IOrchestrator

logger = logging.getLogger(__name__)


@dataclass
class MergeMetrics:
    """Metrics for a merge operation."""
    merged_count: int = 0
    new_count: int = 0
    existing_count: int = 0
    promoted_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class DomainKnowledgeMerger(IOrchestrator):
    """
    Domain Knowledge Merger - Core snowball accumulator for Phase 19.

    Responsibilities:
    - Merge entities across repository scans (incremental accumulation)
    - Promote patterns from Tier 3 (Candidate) → Tier 2 (Learned) after 3+ occurrences
    - Accumulate vendor dependencies company-wide
    - Respect company precedence (company/ > cortex/)
    - Maintain merge history for audit trail

    3-Tier Pattern System:
    - Tier 1 (Known): Hardcoded in cortex/knowledge/patterns/ (99% confidence)
    - Tier 2 (Learned): Promoted from Tier 3 after 3+ repo scans (70-95% confidence)
    - Tier 3 (Candidate): First detection, quarantine (<70% confidence)

    Usage:
        >>> merger = DomainKnowledgeMerger()
        >>> result = merger.merge_context(
        ...     repo_name="kashkole",
        ...     lens_context={...},
        ...     company_dir=Path("company/domains")
        ... )
        >>> print(f"Merged {result['entities']['new_count']} new entities")
    """

    def __init__(self):
        """Initialize DomainKnowledgeMerger."""
        self.merge_history: List[Dict[str, Any]] = []
        self.pattern_occurrences: Dict[str, int] = {}  # Track candidate pattern frequency
        self.promotion_threshold = 3  # Promote after 3 occurrences

    def merge_entities(
        self,
        repo_name: str,
        new_entities: List[str],
        company_dir: Path,
    ) -> Dict[str, Any]:
        """
        Merge entities with existing company domain knowledge.

        Implements snowball effect:
        - Load existing entities from company/domains/entities.yaml
        - Merge new entities (preserve existing, add new)
        - Save back to YAML
        - Return metrics

        Args:
            repo_name: Repository name
            new_entities: List of newly discovered entities
            company_dir: Path to company/domains directory

        Returns:
            Dict with:
                - merged_count: Total entities after merge
                - new_count: Number of newly added entities
                - existing_count: Number of entities already present
                - all_entities: Complete list of entities
        """
        entities_yaml = company_dir / "entities.yaml"

        # Load existing
        existing_entities: List[str] = []
        if entities_yaml.exists():
            try:
                with open(entities_yaml, "r") as f:
                    data = yaml.safe_load(f) or {}
                    existing_entities = data.get("entities", [])
            except Exception as e:
                logger.warning(f"Could not load {entities_yaml}: {e}")

        # Merge (set union)
        existing_set = set(existing_entities)
        new_set = set(new_entities)
        merged_set = existing_set | new_set

        # Calculate metrics
        new_count = len(new_set - existing_set)
        existing_count = len(new_set & existing_set)

        # Save back
        try:
            with open(entities_yaml, "w") as f:
                yaml.dump({
                    "entities": sorted(list(merged_set)),
                    "last_updated": datetime.now().isoformat(),
                    "source_repos": [repo_name],
                }, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Failed to save {entities_yaml}: {e}")

        result = {
            "merged_count": len(merged_set),
            "new_count": new_count,
            "existing_count": existing_count,
            "all_entities": sorted(list(merged_set)),
        }

        # Record in history
        self.merge_history.append({
            "operation": "merge_entities",
            "repo_name": repo_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": result,
        })

        logger.info(
            f"Entities merged for {repo_name}: {new_count} new, {existing_count} existing"
        )

        return result

    def merge_patterns(
        self,
        repo_name: str,
        patterns: Dict[str, List[str]],
        company_dir: Path,
    ) -> Dict[str, Any]:
        """
        Merge patterns with 3-tier promotion system.

        Tier 3 (Candidate) → Tier 2 (Learned) promotion logic:
        - Track pattern occurrences across repos
        - After 3+ occurrences → promote to Tier 2
        - Save to company/domains/learned-patterns.yaml

        Args:
            repo_name: Repository name
            patterns: Dict with keys: known, learned, candidates
            company_dir: Path to company/domains directory

        Returns:
            Dict with:
                - candidates: Current Tier 3 patterns
                - learned: Current Tier 2 patterns
                - promoted: Patterns promoted this scan
                - occurrence_counts: Dict of pattern → count
        """
        patterns_yaml = company_dir / "learned-patterns.yaml"

        # Load existing learned patterns
        learned_patterns: List[str] = []
        if patterns_yaml.exists():
            try:
                with open(patterns_yaml, "r") as f:
                    data = yaml.safe_load(f) or {}
                    learned_patterns = data.get("learned", [])
                    # Load occurrence history
                    self.pattern_occurrences.update(
                        data.get("occurrence_counts", {})
                    )
            except Exception as e:
                logger.warning(f"Could not load {patterns_yaml}: {e}")

        # Process candidates
        promoted: List[str] = []
        candidates = patterns.get("candidates", [])

        for pattern in candidates:
            # Increment occurrence count
            self.pattern_occurrences[pattern] = (
                self.pattern_occurrences.get(pattern, 0) + 1
            )

            # Check promotion threshold
            if self.pattern_occurrences[pattern] >= self.promotion_threshold:
                if pattern not in learned_patterns:
                    learned_patterns.append(pattern)
                    promoted.append(pattern)
                    logger.info(
                        f"Pattern '{pattern}' promoted to Tier 2 after "
                        f"{self.pattern_occurrences[pattern]} occurrences"
                    )

        # Save back
        try:
            with open(patterns_yaml, "w") as f:
                yaml.dump({
                    "learned": sorted(learned_patterns),
                    "occurrence_counts": self.pattern_occurrences,
                    "last_updated": datetime.now().isoformat(),
                    "promotion_threshold": self.promotion_threshold,
                }, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Failed to save {patterns_yaml}: {e}")

        result = {
            "candidates": candidates,
            "learned": learned_patterns,
            "promoted": promoted,
            "occurrence_counts": self.pattern_occurrences.copy(),
        }

        # Record in history
        self.merge_history.append({
            "operation": "merge_patterns",
            "repo_name": repo_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": result,
        })

        return result

    def merge_vendors(
        self,
        repo_name: str,
        vendors: List[str],
        company_dir: Path,
    ) -> Dict[str, Any]:
        """
        Merge vendor dependencies company-wide.

        Args:
            repo_name: Repository name
            vendors: List of vendor identifiers
            company_dir: Path to company/domains directory

        Returns:
            Dict with:
                - total_vendors: Count of unique vendors
                - all_vendors: Complete list
                - new_vendors: Newly discovered
        """
        vendors_yaml = company_dir / "vendors.yaml"

        # Load existing
        existing_vendors: List[str] = []
        if vendors_yaml.exists():
            try:
                with open(vendors_yaml, "r") as f:
                    data = yaml.safe_load(f) or {}
                    existing_vendors = data.get("vendors", [])
            except Exception as e:
                logger.warning(f"Could not load {vendors_yaml}: {e}")

        # Merge
        existing_set = set(existing_vendors)
        new_set = set(vendors)
        merged_set = existing_set | new_set
        new_vendors = list(new_set - existing_set)

        # Save back
        try:
            with open(vendors_yaml, "w") as f:
                yaml.dump({
                    "vendors": sorted(list(merged_set)),
                    "last_updated": datetime.now().isoformat(),
                }, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Failed to save {vendors_yaml}: {e}")

        result = {
            "total_vendors": len(merged_set),
            "all_vendors": sorted(list(merged_set)),
            "new_vendors": new_vendors,
        }

        # Record in history
        self.merge_history.append({
            "operation": "merge_vendors",
            "repo_name": repo_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": result,
        })

        logger.info(f"Vendors merged for {repo_name}: {len(new_vendors)} new")

        return result

    def merge_context(
        self,
        repo_name: str,
        lens_context: Dict[str, Any],
        company_dir: Path,
    ) -> Dict[str, Any]:
        """
        Merge full LENS context (entities, patterns, vendors, frameworks).

        Args:
            repo_name: Repository name
            lens_context: Complete LENS holistic analysis
            company_dir: Path to company/domains directory

        Returns:
            Dict with merge results for all categories
        """
        company_dir.mkdir(parents=True, exist_ok=True)

        result = {
            "repo_name": repo_name,
            "timestamp": datetime.now().isoformat(),
            "success": True,
        }

        try:
            # Merge entities
            if "entities" in lens_context:
                result["entities"] = self.merge_entities(
                    repo_name=repo_name,
                    new_entities=lens_context["entities"],
                    company_dir=company_dir,
                )

            # Merge patterns
            if "patterns" in lens_context:
                result["patterns"] = self.merge_patterns(
                    repo_name=repo_name,
                    patterns=lens_context["patterns"],
                    company_dir=company_dir,
                )

            # Merge vendors
            if "vendors" in lens_context:
                result["vendors"] = self.merge_vendors(
                    repo_name=repo_name,
                    vendors=lens_context["vendors"],
                    company_dir=company_dir,
                )

        except Exception as e:
            logger.error(f"Merge context failed for {repo_name}: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)

        return result

    def get_knowledge_summary(self, company_dir: Path) -> Dict[str, Any]:
        """
        Get summary of merged company knowledge.

        Args:
            company_dir: Path to company/domains directory

        Returns:
            Dict with totals for entities, patterns, vendors
        """
        summary = {
            "total_entities": 0,
            "total_patterns": 0,
            "total_vendors": 0,
            "merge_operations": len(self.merge_history),
        }

        # Count entities
        entities_yaml = company_dir / "entities.yaml"
        if entities_yaml.exists():
            try:
                with open(entities_yaml, "r") as f:
                    data = yaml.safe_load(f) or {}
                    summary["total_entities"] = len(data.get("entities", []))
            except Exception:
                pass

        # Count patterns
        patterns_yaml = company_dir / "learned-patterns.yaml"
        if patterns_yaml.exists():
            try:
                with open(patterns_yaml, "r") as f:
                    data = yaml.safe_load(f) or {}
                    summary["total_patterns"] = len(data.get("learned", []))
            except Exception:
                pass

        # Count vendors
        vendors_yaml = company_dir / "vendors.yaml"
        if vendors_yaml.exists():
            try:
                with open(vendors_yaml, "r") as f:
                    data = yaml.safe_load(f) or {}
                    summary["total_vendors"] = len(data.get("vendors", []))
            except Exception:
                pass

        return summary

    # IOrchestrator interface

    def execute(self, parameters: Dict[str, Any]) -> Result[Any]:
        """
        Execute merge operation.

        Args:
            parameters: Dict with:
                - repo_name: str
                - lens_context: Dict
                - company_dir: str (path)

        Returns:
            Result with merge results or error
        """
        try:
            repo_name = parameters.get("repo_name", "unknown")
            lens_context = parameters.get("lens_context", {})
            company_dir = Path(parameters.get("company_dir", "company/domains"))

            result = self.merge_context(
                repo_name=repo_name,
                lens_context=lens_context,
                company_dir=company_dir,
            )

            if result.get("success"):
                return Ok(result)
            else:
                return Err(result.get("error", "Unknown error"))

        except Exception as e:
            logger.error(f"Merge execution failed: {e}", exc_info=True)
            return Err(str(e))

    def get_name(self) -> str:
        """Get orchestrator name."""
        return "DomainKnowledgeMerger"

    def get_version(self) -> str:
        """Get orchestrator version."""
        return "1.0.0"

    def initialize(self) -> Result[str]:
        """Initialize orchestrator."""
        return Ok("DomainKnowledgeMerger initialized")

    def get_mode(self):
        """Get current operation mode."""
        from cortex.brain.core.interfaces.i_orchestrator import OperationMode
        return OperationMode.EXECUTION

    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """Get exposed MCP tools."""
        return Ok({
            "merge_domain_knowledge": {
                "name": "merge_domain_knowledge",
                "description": "Merge LENS context into company domain knowledge",
                "parameters": {
                    "repo_name": {"type": "string", "required": True},
                    "lens_context": {"type": "object", "required": True},
                    "company_dir": {"type": "string", "default": "company/domains"},
                }
            },
            "get_knowledge_summary": {
                "name": "get_knowledge_summary",
                "description": "Get summary of merged company knowledge",
                "parameters": {
                    "company_dir": {"type": "string", "default": "company/domains"},
                }
            }
        })

    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """Execute operation with audit logging."""
        if operation_name == "merge_domain_knowledge":
            return self.execute(parameters)
        elif operation_name == "get_knowledge_summary":
            company_dir = Path(parameters.get("company_dir", "company/domains"))
            return Ok(self.get_knowledge_summary(company_dir))
        else:
            return Err(f"Unknown operation: {operation_name}")

    def get_description(self) -> str:
        """Get orchestrator description."""
        return "Core snowball accumulator for domain knowledge across repositories"

    def get_capabilities(self) -> List[str]:
        """Get orchestrator capabilities."""
        return [
            "merge_entities",
            "merge_patterns",
            "merge_vendors",
            "pattern_promotion",
            "knowledge_summary",
        ]

    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """Get merge history audit trail."""
        return Ok(self.merge_history[-limit:])


# Singleton
_domain_knowledge_merger = None


def get_domain_knowledge_merger() -> DomainKnowledgeMerger:
    """Get or create singleton DomainKnowledgeMerger."""
    global _domain_knowledge_merger
    if _domain_knowledge_merger is None:
        _domain_knowledge_merger = DomainKnowledgeMerger()
    return _domain_knowledge_merger
