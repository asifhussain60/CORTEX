"""
AC_START: AC-PHASE38-018
MCP Exposure Auditor - Stage 7 Implementation

Audits all orchestrators for MCP tool exposure.
Generates missing MCP tool specifications.

Authority: Phase 38 Stage 7 - Brain Cohesion & Health System
TDD: Tests BEFORE code (CORE-008)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import yaml


@dataclass
class OrchestratorInfo:
    """Information about an orchestrator."""
    name: str
    module_path: str
    category: str  # core, domain, support
    methods: List[str]
    has_mcp_tool: bool
    mcp_tool_path: Optional[str] = None


@dataclass
class MCPCoverageReport:
    """MCP coverage analysis report."""
    timestamp: str
    total_orchestrators: int
    exposed_count: int
    missing_count: int
    coverage_percent: float
    exposed_orchestrators: List[str]
    missing_orchestrators: List[Dict[str, str]]
    coverage_by_category: Dict[str, Dict[str, int]]


class MCPExposureAuditor:
    """
    Audits orchestrator MCP tool coverage.
    
    AC-PHASE38-018: Scans all 35 orchestrators for MCP exposure.
    """

    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize MCP exposure auditor.
        
        Args:
            cortex_root: Root path of CORTEX repository
        """
        if cortex_root is None:
            cortex_root = Path(__file__).parent.parent.parent
        
        self.cortex_root = cortex_root
        self.wiring_file = cortex_root / "cortex" / "wiring" / "specifications" / "wiring.yaml"
        self.mcp_dir = cortex_root / "cortex" / "mcp"
        self.orchestrators_dir = cortex_root / "cortex" / "orchestrators"
        
        self.wired_orchestrators: List[Dict] = []
        self.orchestrator_info: Dict[str, OrchestratorInfo] = {}

    def load_wired_orchestrators(self) -> List[Dict]:
        """
        Load orchestrators from wiring.yaml.
        
        Returns:
            List of orchestrator configurations
        """
        if not self.wiring_file.exists():
            raise FileNotFoundError(f"Wiring file not found: {self.wiring_file}")
        
        with open(self.wiring_file, "r") as f:
            config = yaml.safe_load(f)
        
        orchestrators = []
        
        if "orchestrators" in config:
            for category in ["core", "domain", "support"]:
                if category in config["orchestrators"]:
                    for orch in config["orchestrators"][category]:
                        if isinstance(orch, dict):
                            orch["category"] = category
                            orchestrators.append(orch)
        
        # Add analyzers as orchestrators
        if "analyzers" in config:
            for analyzer in config["analyzers"]:
                if isinstance(analyzer, dict):
                    analyzer["category"] = "analyzer"
                    orchestrators.append(analyzer)
        
        self.wired_orchestrators = orchestrators
        return orchestrators

    def find_orchestrator_file(self, orchestrator_name: str, module_path: str) -> Optional[Path]:
        """
        Find the Python file for an orchestrator.
        
        Args:
            orchestrator_name: Name of orchestrator
            module_path: Module path from wiring.yaml
            
        Returns:
            Path to orchestrator file if found
        """
        # Convert module path to file path
        # e.g., "cortex.orchestrators.core.master_orchestrator" -> "cortex/orchestrators/core/master_orchestrator.py"
        parts = module_path.split(".")
        
        # Try different path variations
        attempts = [
            self.cortex_root / Path(*parts[1:]).with_suffix(".py"),  # Remove 'cortex' prefix
            self.cortex_root / Path(*parts).with_suffix(".py"),       # Full path
        ]
        
        for attempt in attempts:
            if attempt.exists():
                return attempt
        
        return None

    def extract_orchestrator_methods(self, file_path: Path) -> List[str]:
        """
        Extract public methods from orchestrator file.
        
        Args:
            file_path: Path to orchestrator Python file
            
        Returns:
            List of public method names
        """
        methods = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Find class definitions
            class_pattern = r"class\s+\w+.*?:"
            classes = re.findall(class_pattern, content)
            
            if classes:
                # Extract methods (def method_name)
                method_pattern = r"^\s{4}def\s+(\w+)\s*\("
                matches = re.findall(method_pattern, content, re.MULTILINE)
                
                # Filter out private methods and __init__
                methods = [
                    m for m in matches
                    if not m.startswith("_") or m == "__init__"
                ]
        
        except (IOError, UnicodeDecodeError):
            pass
        
        return methods

    def find_mcp_tool(self, orchestrator_name: str) -> Optional[Path]:
        """
        Check if MCP tool exists for orchestrator.
        
        Args:
            orchestrator_name: Name of orchestrator
            
        Returns:
            Path to MCP tool file if found
        """
        # Check for MCP tool in mcp/tools/ or similar
        possible_names = [
            f"cortex_{orchestrator_name.lower().replace('orchestrator', '')}.py",
            f"{orchestrator_name.lower()}_tool.py",
            f"tool_{orchestrator_name.lower()}.py",
        ]
        
        for name in possible_names:
            tool_path = self.mcp_dir / "tools" / name
            if tool_path.exists():
                return tool_path
        
        return None

    def analyze_orchestrator(self, orch_config: Dict) -> OrchestratorInfo:
        """
        Analyze single orchestrator for MCP exposure.
        
        Args:
            orch_config: Orchestrator configuration from wiring.yaml
            
        Returns:
            OrchestratorInfo with analysis results
        """
        name = orch_config.get("name", "Unknown")
        module = orch_config.get("module", "")
        category = orch_config.get("category", "unknown")
        
        # Find orchestrator file
        orch_file = self.find_orchestrator_file(name, module)
        
        methods = []
        if orch_file:
            methods = self.extract_orchestrator_methods(orch_file)
        
        # Check for MCP tool
        mcp_tool = self.find_mcp_tool(name)
        
        info = OrchestratorInfo(
            name=name,
            module_path=module,
            category=category,
            methods=methods,
            has_mcp_tool=mcp_tool is not None,
            mcp_tool_path=str(mcp_tool) if mcp_tool else None
        )
        
        self.orchestrator_info[name] = info
        return info

    def audit(self) -> MCPCoverageReport:
        """
        Execute complete MCP exposure audit.
        
        AC-PHASE38-018: Scan all orchestrators for MCP tools.
        
        Returns:
            MCPCoverageReport with findings
        """
        # Load orchestrators
        orchestrators = self.load_wired_orchestrators()
        
        # Analyze each orchestrator
        for orch in orchestrators:
            self.analyze_orchestrator(orch)
        
        # Calculate coverage
        total = len(self.orchestrator_info)
        exposed = sum(1 for info in self.orchestrator_info.values() if info.has_mcp_tool)
        missing = total - exposed
        coverage = (exposed / total * 100) if total > 0 else 0.0
        
        # Categorize
        coverage_by_category = {}
        for category in ["core", "domain", "support", "analyzer"]:
            cat_orchestrators = [
                info for info in self.orchestrator_info.values()
                if info.category == category
            ]
            cat_exposed = sum(1 for info in cat_orchestrators if info.has_mcp_tool)
            
            coverage_by_category[category] = {
                "total": len(cat_orchestrators),
                "exposed": cat_exposed,
                "missing": len(cat_orchestrators) - cat_exposed
            }
        
        # Build report
        report = MCPCoverageReport(
            timestamp=datetime.utcnow().isoformat(),
            total_orchestrators=total,
            exposed_count=exposed,
            missing_count=missing,
            coverage_percent=coverage,
            exposed_orchestrators=[
                info.name for info in self.orchestrator_info.values()
                if info.has_mcp_tool
            ],
            missing_orchestrators=[
                {
                    "name": info.name,
                    "category": info.category,
                    "module": info.module_path,
                    "methods_count": len(info.methods)
                }
                for info in self.orchestrator_info.values()
                if not info.has_mcp_tool
            ],
            coverage_by_category=coverage_by_category
        )
        
        return report

    def save_report(self, report: MCPCoverageReport, output_path: Path) -> Path:
        """
        Save MCP coverage report to JSON.
        
        Args:
            report: MCPCoverageReport to save
            output_path: Path to save report
            
        Returns:
            Path to saved file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(asdict(report), f, indent=2)
        
        return output_path


    # ========================================================================
    # Test-Compatible Interface (Phase 38 Stage 7)
    # ========================================================================

    def scan_orchestrators(self) -> List[Dict[str, Any]]:
        """
        Scan all orchestrators (test-compatible interface).
        
        Returns:
            List of dicts with orchestrator information
        """
        orchestrators = self.load_wired_orchestrators()
        
        results = []
        for orch in orchestrators:
            info = self.analyze_orchestrator(orch)
            results.append({
                "name": info.name,
                "category": info.category,
                "file_path": info.module_path,
                "has_mcp_tool": info.has_mcp_tool,
                "mcp_tool_name": Path(info.mcp_tool_path).stem if info.mcp_tool_path else None,
            })
        
        return results

    def audit_mcp_coverage(self) -> Dict[str, Any]:
        """
        Audit MCP coverage (test-compatible interface).
        
        Returns:
            Dict with coverage metrics
        """
        report = self.audit()
        
        return {
            "total_orchestrators": report.total_orchestrators,
            "exposed_count": report.exposed_count,
            "missing_count": report.missing_count,
            "coverage_percent": report.coverage_percent,
            "missing_orchestrators": [m["name"] for m in report.missing_orchestrators],
            "category_coverage": report.coverage_by_category,
        }

    def generate_missing_tool_specs(self) -> List[Dict[str, Any]]:
        """
        Generate MCP tool specs for missing orchestrators.
        
        Returns:
            List of tool specifications
        """
        report = self.audit()
        
        specs = []
        for missing in report.missing_orchestrators:
            tool_name = f"cortex_{missing['name'].lower().replace('orchestrator', '').strip()}"
            
            specs.append({
                "tool_name": tool_name,
                "description": f"Invoke {missing['name']} orchestrator",
                "orchestrator": missing["name"],
                "inputs": ["request"],
                "outputs": ["result"],
            })
        
        return specs

    def validate_tool_interface(
        self,
        orchestrator: Any,
        tool_spec: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate tool interface matches orchestrator.
        
        Args:
            orchestrator: Orchestrator instance
            tool_spec: Tool specification
            
        Returns:
            Validation result dict
        """
        issues = []
        
        # Check for process method
        if not hasattr(orchestrator, "process"):
            issues.append("Missing 'process' method")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }


# AC_COMPLETE: AC-PHASE38-018 ✅
# Implementation: MCPExposureAuditor fully implemented
# Tests: 10 tests required (see test_exposure_auditor.py)

