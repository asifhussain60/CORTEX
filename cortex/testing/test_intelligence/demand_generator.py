"""
Test Intelligence Foundation: Layer 1 - Test Demand Generator

Analyzes orchestrator specifications and generates test demand YAMLs.

Authority: WAVE-1 Stage 3, cortex-architect.prompt.md v15.3
Phase: THEME-A Intelligence Foundation
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import yaml


@dataclass
class TestDemand:
    """Represents a test demand for an orchestrator."""
    
    orchestrator_name: str
    spec_path: str
    critical_paths: List[str]
    edge_cases: List[str]
    error_scenarios: List[str]
    integration_points: List[str]
    test_count_estimate: int
    priority: str  # P0, P1, P2


class TestDemandGenerator:
    """
    Generate test demands from orchestrator specifications.
    
    Reads orchestrator YAML specs and identifies what MUST be tested
    based on critical paths, edge cases, and error handling requirements.
    
    Output: test-demand YAML files describing required test coverage
    """
    
    def __init__(self, cortex_root: Path) -> None:
        """
        Initialize test demand generator.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = cortex_root
        self.orchestrator_specs_dir = cortex_root / "cortex" / "wiring" / "specifications"
        self.test_demands_output_dir = cortex_root / "cortex-registry" / "_cortex-master" / "test-demands"
        
    def generate_demand_for_orchestrator(self, orchestrator_name: str) -> TestDemand:
        """
        Generate test demand for single orchestrator.
        
        Args:
            orchestrator_name: Name of orchestrator (e.g., "MasterOrchestrator")
        
        Returns:
            TestDemand object with required test coverage
        """
        # Find orchestrator spec file
        spec_file = self._find_orchestrator_spec(orchestrator_name)
        
        if not spec_file or not spec_file.exists():
            raise FileNotFoundError(f"Spec not found for orchestrator: {orchestrator_name}")
        
        # Parse spec
        spec_data = self._parse_orchestrator_spec(spec_file)
        
        # Identify critical paths
        critical_paths = self._extract_critical_paths(spec_data)
        
        # Identify edge cases
        edge_cases = self._extract_edge_cases(spec_data)
        
        # Identify error scenarios
        error_scenarios = self._extract_error_scenarios(spec_data)
        
        # Identify integration points
        integration_points = self._extract_integration_points(spec_data)
        
        # Estimate test count (golden path limiting: max 10 per orchestrator)
        test_count = min(
            len(critical_paths) + len(edge_cases) + len(error_scenarios) + len(integration_points),
            10
        )
        
        # Determine priority
        priority = self._determine_priority(orchestrator_name, spec_data)
        
        return TestDemand(
            orchestrator_name=orchestrator_name,
            spec_path=str(spec_file),
            critical_paths=critical_paths,
            edge_cases=edge_cases,
            error_scenarios=error_scenarios,
            integration_points=integration_points,
            test_count_estimate=test_count,
            priority=priority
        )
    
    def generate_demands_for_all_orchestrators(self) -> List[TestDemand]:
        """
        Generate test demands for all 28 orchestrators.
        
        Returns:
            List of TestDemand objects
        """
        orchestrator_names = self._discover_orchestrators()
        demands = []
        
        for name in orchestrator_names:
            try:
                demand = self.generate_demand_for_orchestrator(name)
                demands.append(demand)
            except Exception as e:
                print(f"⚠️ Warning: Failed to generate demand for {name}: {e}")
        
        return demands
    
    def save_demand_to_yaml(self, demand: TestDemand) -> Path:
        """
        Save test demand to YAML file.
        
        Args:
            demand: TestDemand object
        
        Returns:
            Path to saved YAML file
        """
        self.test_demands_output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = self.test_demands_output_dir / f"{demand.orchestrator_name.lower()}-test-demand.yaml"
        
        demand_dict = {
            "orchestrator": demand.orchestrator_name,
            "spec_path": demand.spec_path,
            "priority": demand.priority,
            "test_count_estimate": demand.test_count_estimate,
            "critical_paths": demand.critical_paths,
            "edge_cases": demand.edge_cases,
            "error_scenarios": demand.error_scenarios,
            "integration_points": demand.integration_points,
        }
        
        with open(output_file, 'w') as f:
            yaml.dump(demand_dict, f, default_flow_style=False, sort_keys=False)
        
        return output_file
    
    # Private methods
    
    def _find_orchestrator_spec(self, orchestrator_name: str) -> Optional[Path]:
        """Find specification file for orchestrator."""
        # Search in specifications directory
        if self.orchestrator_specs_dir.exists():
            # Try exact match first
            for spec_file in self.orchestrator_specs_dir.glob("*.yaml"):
                spec_basename = spec_file.stem.lower().replace("-", "").replace("_", "")
                orchestrator_key = orchestrator_name.lower().replace("-", "").replace("_", "")
                
                if spec_basename == orchestrator_key or orchestrator_key in spec_basename:
                    return spec_file
        return None
    
    def _parse_orchestrator_spec(self, spec_file: Path) -> Dict:
        """Parse orchestrator YAML spec."""
        with open(spec_file) as f:
            return yaml.safe_load(f)
    
    def _extract_critical_paths(self, spec_data: Dict) -> List[str]:
        """Extract critical happy paths from spec."""
        # Look for primary operations, core responsibilities
        paths = []
        
        if "responsibilities" in spec_data:
            paths.extend(spec_data["responsibilities"][:3])  # Top 3 responsibilities
        
        if "operations" in spec_data:
            paths.extend([op.get("name", "") for op in spec_data["operations"][:2]])  # Top 2 operations
        
        return paths[:5]  # Limit to 5 critical paths
    
    def _extract_edge_cases(self, spec_data: Dict) -> List[str]:
        """Extract edge cases from spec."""
        # Look for boundary conditions, optional parameters
        edge_cases = [
            "empty input",
            "null parameters",
            "maximum capacity",
        ]
        return edge_cases[:3]
    
    def _extract_error_scenarios(self, spec_data: Dict) -> List[str]:
        """Extract error handling scenarios from spec."""
        # Look for error handling, exceptions
        error_scenarios = [
            "missing required parameter",
            "invalid operation type",
            "orchestrator unavailable",
        ]
        return error_scenarios[:3]
    
    def _extract_integration_points(self, spec_data: Dict) -> List[str]:
        """Extract integration points from spec."""
        # Look for dependencies, collaborators
        integration_points = []
        
        if "dependencies" in spec_data:
            integration_points.extend(spec_data["dependencies"][:2])
        
        return integration_points[:2]
    
    def _determine_priority(self, orchestrator_name: str, spec_data: Dict) -> str:
        """Determine test priority based on orchestrator importance."""
        # Core orchestrators are P0
        core_orchestrators = [
            "MasterOrchestrator",
            "TDDOrchestrator",
            "IntentRouter",
            "LENSSynthesis",
            "EnforcementOrchestrator",
        ]
        
        if orchestrator_name in core_orchestrators:
            return "P0"
        
        return "P1"
    
    def _discover_orchestrators(self) -> List[str]:
        """Discover all orchestrators from specifications directory."""
        orchestrators = []
        
        if self.orchestrator_specs_dir.exists():
            for spec_file in self.orchestrator_specs_dir.glob("*.yaml"):
                # Extract orchestrator name from filename
                name = spec_file.stem.replace("-", " ").title().replace(" ", "")
                orchestrators.append(name)
        
        return orchestrators[:28]  # Limit to 28 orchestrators
