"""
Component Integration Verification (CIV) system.

Authority: ENH-027 (Component Integration Verification)
CORE Rules: CORE-008 (TDD-first), CORE-011 (type hints), CORE-012 (docstrings)

Purpose:
    Validates CORTEX component integration across 3 layers:
    1. Wiring→Implementation alignment (orchestrators in wiring.yaml exist)
    2. MCP Tool Registration chain (@mcp_tool decorator + catalog)
    3. Health Check execution (sampled orchestrators)

Performance:
    - Layer 1: AST parsing (~5 sec)
    - Layer 2: Text search (~3 sec)
    - Layer 3: Sampled health checks (~30 sec, 5 orchestrators)
    - Total: ~40 sec (within AUDIT <60 sec budget)

Usage:
    verifier = ComponentIntegrationVerifier(workspace_root=Path.cwd())
    report = verifier.verify_all()
    print(report.to_dict())
"""

import ast
import importlib
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml


class CIVStatus(Enum):
    """CIV check status."""
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


@dataclass
class WiringImplementationResult:
    """Result of wiring→implementation alignment check."""
    status: CIVStatus
    total_orchestrators: int
    aligned_orchestrators: List[str] = field(default_factory=list)
    missing_implementations: List[str] = field(default_factory=list)
    missing_health_checks: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "total_orchestrators": self.total_orchestrators,
            "aligned_count": len(self.aligned_orchestrators),
            "missing_implementations_count": len(self.missing_implementations),
            "missing_health_checks_count": len(self.missing_health_checks),
            "execution_time_ms": self.execution_time_ms,
            "missing_implementations": self.missing_implementations,
            "missing_health_checks": self.missing_health_checks,
        }


@dataclass
class MCPToolRegistrationResult:
    """Result of MCP tool registration chain check."""
    status: CIVStatus
    total_tools: int
    registered_tools: List[str] = field(default_factory=list)
    undecorated_tools: List[str] = field(default_factory=list)
    orphaned_catalog_entries: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "total_tools": self.total_tools,
            "registered_count": len(self.registered_tools),
            "undecorated_count": len(self.undecorated_tools),
            "orphaned_count": len(self.orphaned_catalog_entries),
            "execution_time_ms": self.execution_time_ms,
            "undecorated_tools": self.undecorated_tools,
            "orphaned_catalog_entries": self.orphaned_catalog_entries,
        }


@dataclass
class HealthCheckResult:
    """Result of health check execution."""
    status: CIVStatus
    total_sampled: int
    passed_count: int
    failed_count: int
    failed_orchestrators: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "total_sampled": self.total_sampled,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "execution_time_ms": self.execution_time_ms,
            "failed_orchestrators": self.failed_orchestrators,
        }


@dataclass
class CIVReport:
    """Complete CIV report across all layers."""
    overall_status: CIVStatus
    wiring_result: WiringImplementationResult
    mcp_result: MCPToolRegistrationResult
    health_result: HealthCheckResult
    total_execution_time_ms: float
    issues_found: int

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "overall_status": self.overall_status.value,
            "total_execution_time_ms": self.total_execution_time_ms,
            "issues_found": self.issues_found,
            "layers": {
                "wiring_implementation": self.wiring_result.to_dict(),
                "mcp_tool_registration": self.mcp_result.to_dict(),
                "health_checks": self.health_result.to_dict(),
            }
        }


class ComponentIntegrationVerifier:
    """
    Verifies CORTEX component integration across 3 layers.

    Layer 1: Wiring→Implementation alignment
        - Parse wiring.yaml for orchestrator declarations
        - Verify implementation files exist
        - Validate class names and health_check methods via AST

    Layer 2: MCP Tool Registration chain
        - Find all @mcp_tool decorators in cortex/mcp/tools/
        - Verify catalog entries in mcp_tools_catalog.py
        - Detect orphaned catalog entries (no implementation)

    Layer 3: Health Check execution
        - Sample 5 random orchestrators
        - Import and instantiate
        - Execute health_check method
        - Report failures

    Args:
        workspace_root: Path to CORTEX workspace root

    Example:
        >>> verifier = ComponentIntegrationVerifier(Path.cwd())
        >>> report = verifier.verify_all()
        >>> print(f"Status: {report.overall_status}")
    """

    def __init__(self, workspace_root: Path):
        """Initialize verifier with workspace root."""
        self.workspace_root = workspace_root
        self.wiring_path = workspace_root / "cortex" / "wiring" / "specifications" / "wiring.yaml"
        self.mcp_tools_dir = workspace_root / "cortex" / "mcp" / "tools"
        self.mcp_catalog_path = workspace_root / "cortex" / "mcp" / "mcp_tools_catalog.py"

    def verify_wiring_implementation_alignment(self) -> WiringImplementationResult:
        """
        Layer 1: Verify orchestrators in wiring.yaml have implementations.

        Process:
            1. Parse wiring.yaml for orchestrator declarations
            2. For each orchestrator:
                - Check module file exists
                - Parse file with AST
                - Verify class exists
                - Verify health_check method exists

        Returns:
            WiringImplementationResult with alignment status

        Performance: ~5 sec (AST parsing for 34 orchestrators)
        """
        start_time = time.time()

        if not self.wiring_path.exists():
            return WiringImplementationResult(
                status=CIVStatus.FAIL,
                total_orchestrators=0,
                missing_implementations=["wiring.yaml not found"],
                execution_time_ms=0.0
            )

        # Parse wiring.yaml
        with open(self.wiring_path, 'r') as f:
            wiring_data = yaml.safe_load(f)

        orchestrators = []
        for category in ["core", "domain", "support"]:
            if "orchestrators" in wiring_data and category in wiring_data["orchestrators"]:
                orchestrators.extend(wiring_data["orchestrators"][category])

        aligned = []
        missing_implementations = []
        missing_health_checks = []

        for orch in orchestrators:
            name = orch.get("name")
            module_path = orch.get("module")
            class_name = orch.get("class")
            health_check_method = orch.get("health_check")

            if not all([name, module_path, class_name]):
                missing_implementations.append(f"{name} (incomplete wiring entry)")
                continue

            # Convert module path to file path
            file_path = self.workspace_root / (module_path.replace(".", "/") + ".py")

            if not file_path.exists():
                missing_implementations.append(f"{name} (file not found: {file_path})")
                continue

            # Parse file with AST
            try:
                with open(file_path, 'r') as f:
                    tree = ast.parse(f.read())

                # Find class definition
                class_found = False
                health_check_found = False

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == class_name:
                        class_found = True

                        # Check for health_check method
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and item.name == health_check_method:
                                health_check_found = True
                                break
                        break

                if not class_found:
                    missing_implementations.append(f"{name} (class {class_name} not found)")
                elif not health_check_found and health_check_method:
                    missing_health_checks.append(f"{name} (health_check method missing)")
                    aligned.append(name)
                else:
                    aligned.append(name)

            except Exception as e:
                missing_implementations.append(f"{name} (AST parse error: {str(e)})")

        execution_time = (time.time() - start_time) * 1000

        # Determine status
        if missing_implementations:
            status = CIVStatus.FAIL
        elif missing_health_checks:
            status = CIVStatus.WARNING
        else:
            status = CIVStatus.PASS

        return WiringImplementationResult(
            status=status,
            total_orchestrators=len(orchestrators),
            aligned_orchestrators=aligned,
            missing_implementations=missing_implementations,
            missing_health_checks=missing_health_checks,
            execution_time_ms=execution_time
        )

    def verify_mcp_tool_registration(self) -> MCPToolRegistrationResult:
        """
        Layer 2: Verify MCP tool registration chain.

        Process:
            1. Find all Python files in cortex/mcp/tools/
            2. Search for @mcp_tool decorator usage
            3. Parse mcp_tools_catalog.py for TOOLS dict
            4. Cross-check: decorated tools in catalog, catalog tools implemented

        Returns:
            MCPToolRegistrationResult with registration status

        Performance: ~3 sec (text search)
        """
        start_time = time.time()

        if not self.mcp_tools_dir.exists():
            return MCPToolRegistrationResult(
                status=CIVStatus.FAIL,
                total_tools=0,
                undecorated_tools=["mcp/tools/ directory not found"],
                execution_time_ms=0.0
            )

        # Find all @mcp_tool decorated functions
        decorated_tools = set()
        tool_files = list(self.mcp_tools_dir.glob("**/*.py"))

        for tool_file in tool_files:
            if tool_file.name.startswith("__"):
                continue

            try:
                with open(tool_file, 'r') as f:
                    content = f.read()

                # Simple pattern matching for @mcp_tool decorator
                if "@mcp_tool" in content:
                    # Extract tool names from decorator
                    for line in content.split("\n"):
                        if "@mcp_tool" in line and "name=" in line:
                            # Extract name from decorator
                            start = line.find('name="') + 6
                            end = line.find('"', start)
                            if start > 5 and end > start:
                                tool_name = line[start:end]
                                decorated_tools.add(tool_name)
            except Exception:
                pass

        # Parse catalog
        catalog_tools = set()
        if self.mcp_catalog_path.exists():
            try:
                with open(self.mcp_catalog_path, 'r') as f:
                    content = f.read()

                # Extract tool names from TOOLS dict (only lines with tool names as keys)
                in_tools_dict = False
                for line in content.split("\n"):
                    if "TOOLS = {" in line or "TOOLS={" in line:
                        in_tools_dict = True
                        continue
                    if in_tools_dict and "}" == line.strip():
                        in_tools_dict = False
                        continue
                    if in_tools_dict and '"' in line and ": {" in line:
                        # Extract tool name: "tool_name": {
                        parts = line.strip().split('"')
                        if len(parts) >= 2:
                            potential_tool = parts[1]
                            # Only add if it looks like a tool name (no spaces, underscores ok)
                            if "_" in potential_tool or potential_tool.islower():
                                catalog_tools.add(potential_tool)
            except Exception:
                pass

        # Find issues
        undecorated_tools = []
        orphaned_catalog_entries = []
        registered_tools = []

        # Check for tools in catalog but not decorated
        for tool in catalog_tools:
            if tool not in decorated_tools:
                orphaned_catalog_entries.append(tool)
            else:
                registered_tools.append(tool)

        # Check for decorated tools not in catalog
        for tool in decorated_tools:
            if tool not in catalog_tools:
                undecorated_tools.append(tool)

        execution_time = (time.time() - start_time) * 1000

        # Determine status
        if undecorated_tools or orphaned_catalog_entries:
            status = CIVStatus.FAIL
        else:
            status = CIVStatus.PASS

        return MCPToolRegistrationResult(
            status=status,
            total_tools=len(decorated_tools) + len(catalog_tools),
            registered_tools=registered_tools,
            undecorated_tools=undecorated_tools,
            orphaned_catalog_entries=orphaned_catalog_entries,
            execution_time_ms=execution_time
        )

    def verify_health_checks(self, sample_count: int = 5) -> HealthCheckResult:
        """
        Layer 3: Execute health checks on sampled orchestrators.

        Process:
            1. Parse wiring.yaml for orchestrators with health_check
            2. Randomly sample N orchestrators
            3. Import and instantiate each
            4. Execute health_check method
            5. Report failures

        Args:
            sample_count: Number of orchestrators to sample (default 5)

        Returns:
            HealthCheckResult with execution status

        Performance: ~30 sec (5 health check executions)
        """
        start_time = time.time()

        if not self.wiring_path.exists():
            return HealthCheckResult(
                status=CIVStatus.FAIL,
                total_sampled=0,
                passed_count=0,
                failed_count=0,
                failed_orchestrators=["wiring.yaml not found"],
                execution_time_ms=0.0
            )

        # Parse wiring.yaml
        with open(self.wiring_path, 'r') as f:
            wiring_data = yaml.safe_load(f)

        orchestrators = []
        for category in ["core", "domain", "support"]:
            if "orchestrators" in wiring_data and category in wiring_data["orchestrators"]:
                orchestrators.extend(wiring_data["orchestrators"][category])

        # Filter orchestrators with health_check
        testable = [o for o in orchestrators if o.get("health_check")]

        # Sample orchestrators
        sample_size = min(sample_count, len(testable))
        sampled = random.sample(testable, sample_size) if testable else []

        passed_count = 0
        failed_count = 0
        failed_orchestrators = []

        for orch in sampled:
            name = orch.get("name")
            module_path = orch.get("module")
            class_name = orch.get("class")
            health_check_method = orch.get("health_check")

            try:
                # Import module
                module = importlib.import_module(module_path)

                # Get class
                orch_class = getattr(module, class_name)

                # Instantiate (may require dependencies)
                # For now, assume no-arg constructor or graceful failure
                try:
                    instance = orch_class()
                except TypeError:
                    # Constructor requires args, skip
                    continue

                # Execute health check
                health_method = getattr(instance, health_check_method)
                result = health_method()

                if result:
                    passed_count += 1
                else:
                    failed_count += 1
                    failed_orchestrators.append(f"{name} (health check returned False)")

            except Exception as e:
                failed_count += 1
                failed_orchestrators.append(f"{name} ({str(e)[:50]})")

        execution_time = (time.time() - start_time) * 1000

        # Determine status
        if failed_count > 0:
            status = CIVStatus.FAIL
        elif passed_count == 0:
            status = CIVStatus.WARNING
        else:
            status = CIVStatus.PASS

        return HealthCheckResult(
            status=status,
            total_sampled=sample_size,
            passed_count=passed_count,
            failed_count=failed_count,
            failed_orchestrators=failed_orchestrators,
            execution_time_ms=execution_time
        )

    def generate_civ_report(
        self,
        wiring_result: WiringImplementationResult,
        mcp_result: MCPToolRegistrationResult,
        health_result: HealthCheckResult
    ) -> CIVReport:
        """
        Generate comprehensive CIV report.

        Args:
            wiring_result: Layer 1 result
            mcp_result: Layer 2 result
            health_result: Layer 3 result

        Returns:
            CIVReport with overall status and combined metrics
        """
        total_time = (
            wiring_result.execution_time_ms +
            mcp_result.execution_time_ms +
            health_result.execution_time_ms
        )

        issues_found = (
            len(wiring_result.missing_implementations) +
            len(wiring_result.missing_health_checks) +
            len(mcp_result.undecorated_tools) +
            len(mcp_result.orphaned_catalog_entries) +
            health_result.failed_count
        )

        # Determine overall status
        if any(r.status == CIVStatus.FAIL for r in [wiring_result, mcp_result, health_result]):
            overall_status = CIVStatus.FAIL
        elif any(r.status == CIVStatus.WARNING for r in [wiring_result, mcp_result, health_result]):
            overall_status = CIVStatus.WARNING
        else:
            overall_status = CIVStatus.PASS

        return CIVReport(
            overall_status=overall_status,
            wiring_result=wiring_result,
            mcp_result=mcp_result,
            health_result=health_result,
            total_execution_time_ms=total_time,
            issues_found=issues_found
        )

    def verify_all(self) -> CIVReport:
        """
        Execute all 3 CIV layers and generate report.

        Returns:
            CIVReport with complete validation results

        Performance: ~40 sec total (within AUDIT <60 sec budget)
        """
        wiring_result = self.verify_wiring_implementation_alignment()
        mcp_result = self.verify_mcp_tool_registration()
        health_result = self.verify_health_checks()

        return self.generate_civ_report(wiring_result, mcp_result, health_result)
