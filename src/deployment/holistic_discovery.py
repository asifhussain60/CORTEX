"""
Holistic Functionality Discovery for Deployment

Scans codebase for new components added since last deployment.
Verifies wiring, tests, documentation for each discovered component.
Implements HOLISTIC_CODE_DISCOVERY_ENFORCEMENT for deployment.

Author: Asif Hussain
Version: 1.0.0
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import yaml
import logging

logger = logging.getLogger(__name__)


class HolisticDiscovery:
    """Discovers and validates new functionality before deployment."""
    
    def __init__(self, cortex_root: Path):
        """Initialize discovery scanner."""
        self.cortex_root = Path(cortex_root)
        self.src_path = self.cortex_root / "src"
        self.tests_path = self.cortex_root / "tests"
        self.docs_path = self.cortex_root / "cortex-brain" / "documents"
        self.operations_yaml = self.cortex_root / "cortex-operations.yaml"
        self.manifests_path = self.cortex_root / "cortex-brain" / "orchestrator-manifests"
        
        self.discovered_components: List[Dict[str, Any]] = []
        self.wiring_gaps: List[Dict[str, Any]] = []
        
    def discover_all(self) -> Dict[str, Any]:
        """
        Run complete discovery scan.
        
        Returns:
            Discovery report with components, wiring status, gaps
        """
        logger.info("🔍 Starting holistic functionality discovery...")
        
        # Discover components
        orchestrators = self._discover_orchestrators()
        operations = self._discover_operations()
        agents = self._discover_agents()
        dashboards = self._discover_dashboards()
        
        # Verify wiring for each
        self._verify_wiring(orchestrators, component_type="orchestrator")
        self._verify_wiring(operations, component_type="operation")
        self._verify_wiring(agents, component_type="agent")
        self._verify_wiring(dashboards, component_type="dashboard")
        
        # Generate report
        report = self._generate_report()
        
        logger.info(f"✅ Discovery complete: {len(self.discovered_components)} components found")
        logger.info(f"⚠️  Wiring gaps: {len(self.wiring_gaps)}")
        
        return report
    
    def _discover_orchestrators(self) -> List[Path]:
        """Discover orchestrators in src/orchestrators/."""
        orchestrators_dir = self.src_path / "orchestrators"
        if not orchestrators_dir.exists():
            return []
        
        orchestrators = []
        for file in orchestrators_dir.glob("*_orchestrator.py"):
            if file.name == "__init__.py":
                continue
            orchestrators.append(file)
            logger.debug(f"  Found orchestrator: {file.name}")
        
        return orchestrators
    
    def _discover_operations(self) -> List[Path]:
        """Discover operations in src/operations/modules/."""
        modules_dir = self.src_path / "operations" / "modules"
        if not modules_dir.exists():
            return []
        
        operations = []
        for file in modules_dir.rglob("*.py"):
            if file.name == "__init__.py":
                continue
            if "_orchestrator" in file.name or "_module" in file.name:
                operations.append(file)
                logger.debug(f"  Found operation: {file.relative_to(self.src_path)}")
        
        return operations
    
    def _discover_agents(self) -> List[Path]:
        """Discover agents in src/cortex_agents/."""
        agents_dir = self.src_path / "cortex_agents"
        if not agents_dir.exists():
            return []
        
        agents = []
        for file in agents_dir.glob("*_agent.py"):
            if file.name == "__init__.py":
                continue
            agents.append(file)
            logger.debug(f"  Found agent: {file.name}")
        
        return agents
    
    def _discover_dashboards(self) -> List[Path]:
        """Discover dashboard modules in src/dashboard/."""
        dashboard_dir = self.src_path / "dashboard"
        if not dashboard_dir.exists():
            return []
        
        dashboards = []
        for file in dashboard_dir.rglob("*.py"):
            if file.name == "__init__.py":
                continue
            if "orchestrator" in file.name or "collector" in file.name:
                dashboards.append(file)
                logger.debug(f"  Found dashboard: {file.relative_to(self.src_path)}")
        
        return dashboards
    
    def _verify_wiring(self, components: List[Path], component_type: str):
        """
        Verify each component has proper wiring.
        
        Checks:
        1. Entry point in cortex-operations.yaml
        2. Test file exists in tests/
        3. Documentation exists (for orchestrators)
        4. Manifest exists (for orchestrators)
        """
        operations_config = self._load_operations_yaml()
        
        for component_path in components:
            component_name = component_path.stem  # filename without .py
            
            wiring_status = {
                "component": component_name,
                "type": component_type,
                "path": str(component_path.relative_to(self.cortex_root)),
                "wired_in_operations_yaml": self._check_operations_yaml_entry(component_name, operations_config),
                "has_tests": self._check_test_file(component_path),
                "has_documentation": self._check_documentation(component_name, component_type),
                "has_manifest": self._check_manifest(component_name, component_type) if component_type == "orchestrator" else None
            }
            
            # Determine if fully wired
            wiring_status["fully_wired"] = all([
                wiring_status["wired_in_operations_yaml"],
                wiring_status["has_tests"],
                wiring_status.get("has_manifest", True) is not False  # Only required for orchestrators
            ])
            
            self.discovered_components.append(wiring_status)
            
            if not wiring_status["fully_wired"]:
                self.wiring_gaps.append(wiring_status)
    
    def _load_operations_yaml(self) -> Dict[str, Any]:
        """Load cortex-operations.yaml."""
        if not self.operations_yaml.exists():
            logger.warning(f"Operations config not found: {self.operations_yaml}")
            return {}
        
        with open(self.operations_yaml) as f:
            return yaml.safe_load(f) or {}
    
    def _check_operations_yaml_entry(self, component_name: str, operations_config: Dict[str, Any]) -> bool:
        """Check if component has entry in cortex-operations.yaml."""
        operations = operations_config.get("operations", {})
        
        # Check operations
        for op_name, op_config in operations.items():
            if component_name in op_name or op_name in component_name:
                return True
            
            # Check modules list
            modules = op_config.get("modules", [])
            if component_name in modules:
                return True
        
        return False
    
    def _check_test_file(self, component_path: Path) -> bool:
        """Check if test file exists for component."""
        # Convert src/ path to tests/ path
        rel_path = component_path.relative_to(self.src_path)
        test_path = self.tests_path / rel_path.parent / f"test_{rel_path.name}"
        
        return test_path.exists()
    
    def _check_documentation(self, component_name: str, component_type: str) -> bool:
        """Check if documentation exists for component."""
        # Documentation more critical for orchestrators
        if component_type != "orchestrator":
            return True  # Not required for non-orchestrators
        
        # Check implementation guides
        guides_dir = self.docs_path / "implementation-guides"
        if guides_dir.exists():
            for doc_file in guides_dir.glob("*.md"):
                if component_name.replace("_", "-") in doc_file.name:
                    return True
        
        return False
    
    def _check_manifest(self, component_name: str, component_type: str) -> bool:
        """Check if manifest exists for orchestrator."""
        if component_type != "orchestrator":
            return None  # Not applicable
        
        manifest_name = component_name.replace("_", "-") + "-manifest.yaml"
        manifest_path = self.manifests_path / manifest_name
        
        return manifest_path.exists()
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate discovery report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report = {
            "timestamp": timestamp,
            "cortex_root": str(self.cortex_root),
            "summary": {
                "total_components": len(self.discovered_components),
                "fully_wired": len([c for c in self.discovered_components if c["fully_wired"]]),
                "wiring_gaps": len(self.wiring_gaps),
                "wiring_rate": f"{(len([c for c in self.discovered_components if c['fully_wired']]) / len(self.discovered_components) * 100):.1f}%" if self.discovered_components else "0%"
            },
            "components_by_type": self._group_by_type(),
            "discovered_components": self.discovered_components,
            "wiring_gaps": self.wiring_gaps,
            "remediation_steps": self._generate_remediation_steps()
        }
        
        return report
    
    def _group_by_type(self) -> Dict[str, int]:
        """Group components by type."""
        types = {}
        for component in self.discovered_components:
            comp_type = component["type"]
            types[comp_type] = types.get(comp_type, 0) + 1
        return types
    
    def _generate_remediation_steps(self) -> List[Dict[str, Any]]:
        """Generate remediation steps for wiring gaps."""
        steps = []
        
        for gap in self.wiring_gaps:
            component_steps = {
                "component": gap["component"],
                "type": gap["type"],
                "actions": []
            }
            
            if not gap["wired_in_operations_yaml"]:
                component_steps["actions"].append({
                    "action": "Register in cortex-operations.yaml",
                    "priority": "CRITICAL",
                    "command": f"python3 -m src.operations.align --auto-fix"
                })
            
            if not gap["has_tests"]:
                component_steps["actions"].append({
                    "action": f"Create test file: tests/{gap['path'].replace('src/', '').replace('.py', '_test.py')}",
                    "priority": "HIGH",
                    "command": f"# TDD: Write tests for {gap['component']}"
                })
            
            if gap.get("has_manifest") is False:
                component_steps["actions"].append({
                    "action": f"Create manifest: cortex-brain/orchestrator-manifests/{gap['component'].replace('_', '-')}-manifest.yaml",
                    "priority": "HIGH",
                    "command": f"# Create manifest following Planning System 2.0 pattern"
                })
            
            if not gap["has_documentation"]:
                component_steps["actions"].append({
                    "action": f"Create documentation: cortex-brain/documents/implementation-guides/{gap['component'].replace('_', '-')}.md",
                    "priority": "MEDIUM",
                    "command": f"# Document {gap['component']} implementation"
                })
            
            steps.append(component_steps)
        
        return steps
    
    def save_report(self, report: Dict[str, Any]) -> Path:
        """Save discovery report to file."""
        timestamp = report["timestamp"]
        report_dir = self.cortex_root / "cortex-brain" / "documents" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = report_dir / f"deployment-discovery-{timestamp}.md"
        
        with open(report_path, "w") as f:
            f.write(f"# Deployment Functionality Discovery Report\n\n")
            f.write(f"**Date:** {timestamp}\n")
            f.write(f"**CORTEX Root:** {report['cortex_root']}\n\n")
            f.write(f"---\n\n")
            
            # Summary
            f.write(f"## Summary\n\n")
            summary = report["summary"]
            f.write(f"- **Total Components:** {summary['total_components']}\n")
            f.write(f"- **Fully Wired:** {summary['fully_wired']}\n")
            f.write(f"- **Wiring Gaps:** {summary['wiring_gaps']}\n")
            f.write(f"- **Wiring Rate:** {summary['wiring_rate']}\n\n")
            
            # Components by Type
            f.write(f"## Components by Type\n\n")
            for comp_type, count in report["components_by_type"].items():
                f.write(f"- **{comp_type.capitalize()}s:** {count}\n")
            f.write(f"\n")
            
            # Discovered Components
            f.write(f"## Discovered Components\n\n")
            for component in report["discovered_components"]:
                status = "✅" if component["fully_wired"] else "⚠️"
                f.write(f"### {status} {component['component']} ({component['type']})\n\n")
                f.write(f"- **Path:** `{component['path']}`\n")
                f.write(f"- **Operations YAML:** {'✅' if component['wired_in_operations_yaml'] else '❌'}\n")
                f.write(f"- **Tests:** {'✅' if component['has_tests'] else '❌'}\n")
                if component.get("has_manifest") is not None:
                    f.write(f"- **Manifest:** {'✅' if component['has_manifest'] else '❌'}\n")
                if component.get("has_documentation") is not None:
                    f.write(f"- **Documentation:** {'✅' if component['has_documentation'] else '⚠️'}\n")
                f.write(f"- **Status:** {'Fully Wired' if component['fully_wired'] else 'Wiring Gaps'}\n\n")
            
            # Wiring Gaps
            if report["wiring_gaps"]:
                f.write(f"## Wiring Gaps\n\n")
                f.write(f"The following components have wiring gaps that must be addressed:\n\n")
                for gap in report["wiring_gaps"]:
                    f.write(f"### ⚠️ {gap['component']}\n\n")
                    f.write(f"**Missing:**\n")
                    if not gap["wired_in_operations_yaml"]:
                        f.write(f"- Operations YAML entry\n")
                    if not gap["has_tests"]:
                        f.write(f"- Test file\n")
                    if gap.get("has_manifest") is False:
                        f.write(f"- Manifest file\n")
                    if not gap.get("has_documentation", True):
                        f.write(f"- Documentation\n")
                    f.write(f"\n")
            
            # Remediation Steps
            if report["remediation_steps"]:
                f.write(f"## Remediation Steps\n\n")
                for step in report["remediation_steps"]:
                    f.write(f"### {step['component']}\n\n")
                    for action in step["actions"]:
                        f.write(f"**{action['priority']}:** {action['action']}\n")
                        f.write(f"```bash\n{action['command']}\n```\n\n")
            
            # Recommendations
            f.write(f"## Recommendations\n\n")
            if report["wiring_gaps"]:
                f.write(f"⚠️ **Action Required:** Address {len(report['wiring_gaps'])} wiring gaps before deployment.\n\n")
                f.write(f"1. Run alignment to register unregistered components\n")
                f.write(f"2. Create missing test files (TDD)\n")
                f.write(f"3. Create missing manifests (for orchestrators)\n")
                f.write(f"4. Document new functionality\n")
            else:
                f.write(f"✅ **All Clear:** All components properly wired and ready for deployment.\n\n")
        
        logger.info(f"📄 Discovery report saved: {report_path}")
        return report_path


def run_discovery(cortex_root: Path = None) -> Dict[str, Any]:
    """Run holistic discovery scan."""
    if cortex_root is None:
        cortex_root = Path.cwd()
    
    discovery = HolisticDiscovery(cortex_root)
    report = discovery.discover_all()
    discovery.save_report(report)
    
    return report
