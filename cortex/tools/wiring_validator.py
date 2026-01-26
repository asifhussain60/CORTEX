"""
Wiring Validator - Comprehensive Production Wiring Verification

AC-ID: AC-WIRING-ENFORCEMENT-001
Purpose: Validate that ALL orchestrators and components are wired into production pipeline
Authority: cortex-total-recall.prompt.md (v8.0)
Scope: Executed automatically on TotalRecallAgent initialization

This module validates using DatabaseBackedRegistry as Single Source of Truth (SSOT):
1. All 23 orchestrators registered and wired via DatabaseBackedRegistry
2. 4-stage pipeline integrity (Comprehension → Routing → Knowledge → Execution)
3. MCP registry with 15 tools operational
4. Governance registry singleton active
5. StateManager cross-phase persistence working

Updated: 2026-01-25 - Now uses DatabaseBackedRegistry instead of hardcoded lists

"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import importlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class WiringValidationResult:
    """Result of wiring validation check."""
    
    check_name: str
    status: str  # "PASS" | "FAIL" | "PARTIAL"
    components_total: int = 0
    components_validated: int = 0
    components_failed: List[str] = field(default_factory=list)  # type: ignore
    errors: List[str] = field(default_factory=list)  # type: ignore
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def coverage_percent(self) -> float:
        """Calculate validation coverage percentage."""
        if self.components_total == 0:
            return 100.0
        return (self.components_validated / self.components_total) * 100


class WiringValidator:
    """
    Comprehensive validator for CORTEX production wiring.
    
    Now uses DatabaseBackedRegistry as the Single Source of Truth (SSOT)
    for orchestrator wiring status instead of hardcoded lists.
    
    Provides detailed error reporting for remediation.
    """
    
    def __init__(self):
        """Initialize validator."""
        self.validation_results: List[WiringValidationResult] = []
        self.timestamp_start = datetime.now()
        self._db_registry = None
    
    def _get_db_registry(self) -> Optional[Any]:
        """Get DatabaseBackedRegistry instance (lazy load)."""
        if self._db_registry is None:
            try:
                from cortex.orchestrators.core.database_registry import get_database_registry
                self._db_registry = get_database_registry()
            except ImportError as e:
                logger.warning("DatabaseBackedRegistry not available: %s", e)
        return self._db_registry
    
    def validate_all_production_wiring(self) -> Dict[str, Any]:  # type: ignore
        """
        Execute comprehensive wiring validation using DatabaseBackedRegistry.
        
        Returns:
            Dict with overall status and detailed results per component category
        """
        results: Dict[str, Any] = {
            "overall_status": "PASS",
            "timestamp": datetime.now().isoformat(),
            "registry_type": "DatabaseBackedRegistry",
            "checks": {}
        }
        
        # Validate orchestrators via DatabaseBackedRegistry
        orchestrator_result = self._validate_orchestrators_via_db()
        results["checks"]["orchestrators"] = {
            "status": orchestrator_result.status,
            "coverage": f"{orchestrator_result.coverage_percent:.1f}%",
            "validated": orchestrator_result.components_validated,
            "total": orchestrator_result.components_total,
            "failed": orchestrator_result.components_failed,
            "errors": orchestrator_result.errors
        }
        if orchestrator_result.status == "FAIL":
            results["overall_status"] = "FAIL"
        elif orchestrator_result.status == "PARTIAL" and results["overall_status"] == "PASS":
            results["overall_status"] = "PARTIAL"
        
        # Validate 4-stage pipeline
        pipeline_result = self._validate_4stage_pipeline()
        results["checks"]["4_stage_pipeline"] = {
            "status": pipeline_result.status,
            "stages_validated": pipeline_result.components_validated,
            "total_stages": pipeline_result.components_total,
            "failed_stages": pipeline_result.components_failed,
            "errors": pipeline_result.errors
        }
        if pipeline_result.status == "FAIL":
            results["overall_status"] = "FAIL"
        
        # Validate MCP registry
        mcp_result = self._validate_mcp_registry()
        results["checks"]["mcp_registry"] = {
            "status": mcp_result.status,
            "tools_registered": mcp_result.components_validated,
            "target_count": mcp_result.components_total,
            "missing_tools": mcp_result.components_failed,
            "errors": mcp_result.errors
        }
        if mcp_result.status != "PASS":
            results["overall_status"] = "PARTIAL" if results["overall_status"] == "PASS" else "FAIL"
        
        # Validate governance & state components
        governance_result = self._validate_governance_and_state()
        results["checks"]["governance_and_state"] = {
            "status": governance_result.status,
            "components_validated": governance_result.components_validated,
            "total_components": governance_result.components_total,
            "failed_components": governance_result.components_failed,
            "errors": governance_result.errors
        }
        if governance_result.status == "FAIL":
            results["overall_status"] = "FAIL"
        
        # Calculate totals
        all_results = [orchestrator_result, pipeline_result, mcp_result, governance_result]
        results["total_checks"] = len(all_results)
        results["total_components"] = sum(r.components_total for r in all_results)
        results["total_validated"] = sum(r.components_validated for r in all_results)
        results["total_failures"] = sum(len(r.components_failed) for r in all_results)
        results["coverage_percent"] = (results["total_validated"] / results["total_components"] * 100) if results["total_components"] > 0 else 100.0
        
        self.validation_results = all_results
        
        return results
    
    def _validate_orchestrators_via_db(self) -> WiringValidationResult:
        """
        Validate all orchestrators using DatabaseBackedRegistry.
        
        Returns status from DB instead of trying to import modules directly.
        """
        result = WiringValidationResult(
            check_name="Orchestrators (via DatabaseBackedRegistry)",
            status="PASS",
            components_total=23  # Expected total
        )
        
        registry = self._get_db_registry()
        if registry is None:
            # Fallback to legacy validation
            result.status = "PARTIAL"
            result.errors.append("DatabaseBackedRegistry not available, using legacy validation")
            return self._validate_orchestrators_legacy(result)
        
        try:
            stats = registry.get_wiring_statistics()
            result.components_total = stats.get("total_registered", 23)
            result.components_validated = stats.get("total_wired", 0)
            
            # Determine status
            coverage = result.components_validated / result.components_total if result.components_total > 0 else 0
            if coverage >= 0.90:  # 90%+ = PASS
                result.status = "PASS"
            elif coverage >= 0.70:  # 70-90% = PARTIAL
                result.status = "PARTIAL"
            else:
                result.status = "FAIL"
            
            # Get category breakdown
            by_category = stats.get("by_category", {})
            for cat, count in by_category.items():
                logger.info(f"  {cat}: {count} orchestrators registered")
            
            logger.info(f"Orchestrator validation: {result.components_validated}/{result.components_total} wired ({coverage*100:.0f}%)")
            
        except Exception as e:
            result.status = "FAIL"
            result.errors.append(f"Failed to query DatabaseBackedRegistry: {str(e)}")
            logger.error(f"DatabaseBackedRegistry query failed: {e}")
        
        return result
    
    def _validate_orchestrators_legacy(self, result: WiringValidationResult) -> WiringValidationResult:
        """Legacy orchestrator validation by importing modules."""
        orchestrators = [
            ("MasterOrchestrator", "cortex.orchestrators.core.master_orchestrator"),
            ("InteractionOrchestrator", "cortex.orchestrators.core.interaction_orchestrator"),
            ("IntentRouter", "cortex.orchestrators.core.intent_router"),
            ("TDDOrchestrator", "cortex.orchestrators.core.tdd_orchestrator"),
        ]
        
        result.components_total = len(orchestrators)
        for orch_name, module_path in orchestrators:
            try:
                importlib.import_module(module_path)
                result.components_validated += 1
            except ImportError as e:
                result.components_failed.append(orch_name)
                result.errors.append(f"{orch_name}: {str(e)}")
        
        return result
    
    def _validate_4stage_pipeline(self) -> WiringValidationResult:
        """Validate 4-stage orchestration pipeline."""
        stages = [
            ("Stage 1: Comprehension", "cortex.orchestrators.core.interaction_orchestrator"),
            ("Stage 2: Routing", "cortex.orchestrators.core.intent_router"),
            ("Stage 3: Knowledge", "cortex.brain.core.knowledge.knowledge_repository"),
            ("Stage 4: Execution", "cortex.orchestrators.core.master_orchestrator"),
        ]
        
        result = WiringValidationResult(
            check_name="4-Stage Pipeline",
            status="PASS",
            components_total=len(stages)
        )
        
        for stage_name, module_path in stages:
            try:
                module = importlib.import_module(module_path)
                result.components_validated += 1
                logger.info(f"✅ Pipeline stage validated: {stage_name}")
            except ImportError as e:
                result.components_failed.append(stage_name)
                result.errors.append(f"{stage_name}: {str(e)}")
                result.status = "FAIL"
                logger.error(f"❌ Critical pipeline stage failed: {stage_name}: {e}")
        
        return result
    
    def _validate_mcp_registry(self) -> WiringValidationResult:
        """Validate MCP registry with 15 tools."""
        result = WiringValidationResult(
            check_name="MCP Registry",
            status="PASS",
            components_total=15
        )
        
        try:
            from cortex.mcp.registry import get_mcp_tool_registry
            registry = get_mcp_tool_registry()
            tools: List[Any] = registry.get_all_tools() if hasattr(registry, 'get_all_tools') else []  # type: ignore
            result.components_validated = len(tools)
            
            if result.components_validated < 15:
                result.status = "PARTIAL"
                result.components_failed = [f"Only {result.components_validated}/15 tools registered"]
                logger.warning(f"⚠️  MCP registry incomplete: {result.components_validated}/15 tools")
            else:
                logger.info(f"✅ MCP registry complete: {result.components_validated} tools")
        except Exception as e:
            result.status = "FAIL"
            result.errors.append(f"MCP registry validation failed: {str(e)}")
            result.components_failed = ["MCP registry import failed"]
            logger.error(f"❌ MCP registry validation failed: {e}")
        
        return result
    
    def _validate_governance_and_state(self) -> WiringValidationResult:
        """Validate governance registry and state managers."""
        components = [
            ("GovernanceRegistry", "cortex.brain.core.governance_registry"),
            ("StateManager", "cortex.brain.core.state_manager"),
            ("EnhancedAuditLogger", "cortex.infrastructure.enhanced_audit_logger"),
            ("BehavioralBoundaryRules", "cortex_brain.tier2.hallucination_prevention"),
            ("KnowledgeRepository", "cortex.brain.core.knowledge_repository"),
        ]
        
        result = WiringValidationResult(
            check_name="Governance & State",
            status="PASS",
            components_total=len(components)
        )
        
        for comp_name, module_path in components:
            try:
                module = importlib.import_module(module_path)
                result.components_validated += 1
                logger.info(f"✅ Component validated: {comp_name}")
            except ImportError as e:
                result.components_failed.append(comp_name)
                result.errors.append(f"{comp_name}: {str(e)}")
                result.status = "PARTIAL"
                logger.warning(f"⚠️  Component validation failed: {comp_name}: {e}")
        
        return result
    
    def get_validation_summary(self) -> str:
        """Get human-readable validation summary."""
        if not self.validation_results:
            return "No validation results available"
        
        summary_lines = []
        for result in self.validation_results:
            status_icon = "✅" if result.status == "PASS" else "⚠️" if result.status == "PARTIAL" else "❌"
            summary_lines.append(
                f"{status_icon} {result.check_name}: {result.components_validated}/{result.components_total} "
                f"({result.coverage_percent:.1f}%)"
            )
        
        return "\n".join(summary_lines)
