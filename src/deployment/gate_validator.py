"""
Enhanced Gate Validation Framework

Integrates with holistic discovery to validate deployment readiness.
Supports hierarchical gate categories, dependencies, parallel execution, and caching.

Author: Asif Hussain
Version: 1.0.0
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import logging
import json

logger = logging.getLogger(__name__)


class GateSeverity(Enum):
    """Gate severity levels."""
    CRITICAL = "CRITICAL"  # Blocks deployment
    WARNING = "WARNING"    # Logged only
    INFO = "INFO"         # Metrics only


class GateCategory(Enum):
    """Gate categories for organization."""
    QUALITY = "quality"
    SECURITY = "security"
    INTEGRATION = "integration"
    DOCUMENTATION = "documentation"
    TESTING = "testing"


@dataclass
class GateResult:
    """Result from gate execution."""
    gate_id: str
    name: str
    severity: GateSeverity
    passed: bool
    message: str
    category: Optional[GateCategory] = None
    details: Dict[str, Any] = field(default_factory=dict)
    remediation_steps: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    
    def blocks_deployment(self) -> bool:
        """Check if this gate blocks deployment when failed."""
        return self.severity == GateSeverity.CRITICAL and not self.passed


class GateValidator:
    """Enhanced gate validation with discovery integration."""
    
    def __init__(self, cortex_root: Path):
        """Initialize gate validator."""
        self.cortex_root = Path(cortex_root)
        self.gate_cache: Dict[str, GateResult] = {}
        self.reports_dir = self.cortex_root / "cortex-brain" / "documents" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def load_discovery_report(self, report_path: Path) -> Optional[Dict[str, Any]]:
        """Load discovery report for validation targets."""
        if not report_path.exists():
            logger.warning(f"Discovery report not found: {report_path}")
            return None
        
        # For now, just verify file exists
        # In production, would parse markdown/JSON report
        return {"path": str(report_path)}
    
    def get_gate_dependencies(self, gate_config: Dict[str, Any]) -> List[str]:
        """Extract gate dependencies."""
        return gate_config.get("depends_on", [])
    
    def resolve_execution_order(self, gates: List[Dict[str, Any]]) -> List[str]:
        """
        Resolve gate execution order based on dependencies.
        
        Uses topological sort to ensure dependencies execute first.
        """
        # Build dependency graph
        graph = {gate["gate_id"]: gate.get("depends_on", []) for gate in gates}
        
        # Topological sort
        visited = set()
        order = []
        
        def visit(gate_id: str):
            if gate_id in visited:
                return
            visited.add(gate_id)
            
            for dep in graph.get(gate_id, []):
                visit(dep)
            
            order.append(gate_id)
        
        for gate in gates:
            visit(gate["gate_id"])
        
        return order
    
    def get_parallel_groups(self, gates: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Group gates for parallel execution.
        
        Gates with no dependencies or same dependency level can run in parallel.
        """
        # Calculate dependency depth for each gate
        depths = {}
        
        def calculate_depth(gate_id: str, gate_map: Dict[str, Dict]) -> int:
            if gate_id in depths:
                return depths[gate_id]
            
            deps = gate_map[gate_id].get("depends_on", [])
            if not deps:
                depths[gate_id] = 0
                return 0
            
            max_dep_depth = max(calculate_depth(dep, gate_map) for dep in deps)
            depths[gate_id] = max_dep_depth + 1
            return depths[gate_id]
        
        gate_map = {gate["gate_id"]: gate for gate in gates}
        for gate in gates:
            calculate_depth(gate["gate_id"], gate_map)
        
        # Group by depth
        groups = []
        max_depth = max(depths.values()) if depths else 0
        
        for depth in range(max_depth + 1):
            group = [gate_id for gate_id, d in depths.items() if d == depth]
            if group:
                groups.append(group)
        
        return groups
    
    def cache_result(self, gate_id: str, result: GateResult):
        """Cache gate result."""
        self.gate_cache[gate_id] = result
    
    def get_cached_result(self, gate_id: str) -> Optional[GateResult]:
        """Get cached gate result."""
        return self.gate_cache.get(gate_id)
    
    def extract_validation_targets(self, discovery_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract validation targets from discovery report."""
        return discovery_data.get("discovered_components", [])
    
    def validate_component_wiring(self, component: Dict[str, Any]) -> GateResult:
        """
        Validate component wiring status.
        
        Checks that component has:
        - operations.yaml entry
        - test file
        - manifest (for orchestrators)
        - documentation (for orchestrators)
        """
        gate_id = f"wiring_{component['component']}"
        name = f"Component Wiring: {component['component']}"
        
        if component.get("fully_wired", False):
            return GateResult(
                gate_id=gate_id,
                name=name,
                severity=GateSeverity.INFO,
                passed=True,
                message=f"Component {component['component']} fully wired",
                category=GateCategory.INTEGRATION
            )
        
        # Component not fully wired - identify issues
        issues = []
        if not component.get("wired_in_operations_yaml", False):
            issues.append("Missing operations.yaml entry")
        if not component.get("has_tests", False):
            issues.append("Missing test file")
        if component.get("has_manifest") is False:
            issues.append("Missing manifest file")
        
        remediation = []
        if not component.get("wired_in_operations_yaml", False):
            remediation.append("Run: python3 -m src.operations.align --auto-fix")
        if not component.get("has_tests", False):
            remediation.append(f"Create: tests/{component['path'].replace('src/', '').replace('.py', '_test.py')}")
        
        return GateResult(
            gate_id=gate_id,
            name=name,
            severity=GateSeverity.CRITICAL,
            passed=False,
            message=f"Component {component['component']} has wiring gaps: {', '.join(issues)}",
            category=GateCategory.INTEGRATION,
            remediation_steps=remediation,
            details=component
        )
    
    def generate_remediation(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Generate remediation steps for gate failure."""
        gate_id = failure.get("gate_id")
        issue = failure.get("issue")
        component = failure.get("component")
        
        remediation = {
            "gate_id": gate_id,
            "issue": issue,
            "steps": [],
            "command": None
        }
        
        if "operations.yaml" in issue.lower():
            remediation["command"] = "python3 -m src.operations.align --auto-fix"
            remediation["steps"].append("1. Run alignment with auto-fix")
            remediation["steps"].append("2. Verify component registered in cortex-operations.yaml")
        
        if "test" in issue.lower():
            remediation["steps"].append("1. Create test file following TDD approach")
            remediation["steps"].append(f"2. Location: tests/{component}_test.py")
            remediation["command"] = f"# Create tests for {component}"
        
        return remediation
    
    def calculate_statistics(self, results: List[GateResult]) -> Dict[str, Any]:
        """Calculate gate execution statistics."""
        stats = {
            "total": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
            "failed_critical": sum(1 for r in results if not r.passed and r.severity == GateSeverity.CRITICAL),
            "failed_warning": sum(1 for r in results if not r.passed and r.severity == GateSeverity.WARNING),
            "failed_info": sum(1 for r in results if not r.passed and r.severity == GateSeverity.INFO),
            "pass_rate": 0.0,
            "total_execution_time": sum(r.execution_time for r in results)
        }
        
        if stats["total"] > 0:
            stats["pass_rate"] = (stats["passed"] / stats["total"]) * 100
        
        return stats
    
    def generate_report(self, results: List[GateResult], report_path: Path) -> Path:
        """Generate gate execution report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not report_path.parent.exists():
            report_path.parent.mkdir(parents=True)
        
        with open(report_path, "w") as f:
            f.write(f"# Deployment Gate Execution Report\n\n")
            f.write(f"**Date:** {timestamp}\n")
            f.write(f"**CORTEX Root:** {self.cortex_root}\n\n")
            f.write(f"---\n\n")
            
            # Statistics
            stats = self.calculate_statistics(results)
            f.write(f"## Summary\n\n")
            f.write(f"- **Total Gates:** {stats['total']}\n")
            f.write(f"- **Passed:** {stats['passed']}\n")
            f.write(f"- **Failed:** {stats['failed']}\n")
            f.write(f"- **Pass Rate:** {stats['pass_rate']:.1f}%\n")
            f.write(f"- **Execution Time:** {stats['total_execution_time']:.2f}s\n\n")
            
            # Failed critical gates
            critical_failures = [r for r in results if not r.passed and r.severity == GateSeverity.CRITICAL]
            if critical_failures:
                f.write(f"## ❌ Critical Failures (Blocking Deployment)\n\n")
                for result in critical_failures:
                    f.write(f"### {result.name}\n\n")
                    f.write(f"- **Gate ID:** {result.gate_id}\n")
                    f.write(f"- **Message:** {result.message}\n")
                    if result.remediation_steps:
                        f.write(f"- **Remediation:**\n")
                        for step in result.remediation_steps:
                            f.write(f"  {step}\n")
                    f.write(f"\n")
            
            # All gate results
            f.write(f"## All Gate Results\n\n")
            for result in results:
                status = "✅" if result.passed else "❌" if result.severity == GateSeverity.CRITICAL else "⚠️"
                f.write(f"### {status} {result.name}\n\n")
                f.write(f"- **Status:** {'PASSED' if result.passed else 'FAILED'}\n")
                f.write(f"- **Severity:** {result.severity.value}\n")
                if result.category:
                    f.write(f"- **Category:** {result.category.value}\n")
                f.write(f"- **Message:** {result.message}\n")
                f.write(f"\n")
        
        logger.info(f"📄 Gate report generated: {report_path}")
        return report_path
    
    def validate_all_gates(self, discovery_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate all deployment gates with discovery integration.
        
        Args:
            discovery_data: Discovery report data with validation targets
        
        Returns:
            Validation results with gate results, statistics, deployment decision
        """
        gate_results = []
        
        # If discovery data provided, validate discovered components
        if discovery_data:
            targets = self.extract_validation_targets(discovery_data)
            logger.info(f"🔍 Validating {len(targets)} discovered components")
            
            for component in targets:
                result = self.validate_component_wiring(component)
                gate_results.append(result)
                self.cache_result(result.gate_id, result)
        
        # Calculate statistics
        stats = self.calculate_statistics(gate_results)
        
        # Determine deployment decision
        blocking_failures = [r for r in gate_results if r.blocks_deployment()]
        deployment_allowed = len(blocking_failures) == 0
        
        return {
            "gate_results": gate_results,
            "statistics": stats,
            "deployment_allowed": deployment_allowed,
            "blocking_failures": blocking_failures
        }


def run_gate_validation(
    cortex_root: Path,
    discovery_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Run gate validation with discovery integration."""
    validator = GateValidator(cortex_root)
    results = validator.validate_all_gates(discovery_data=discovery_data)
    
    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = validator.reports_dir / f"deployment-gates-{timestamp}.md"
    validator.generate_report(results["gate_results"], report_path)
    
    return results
