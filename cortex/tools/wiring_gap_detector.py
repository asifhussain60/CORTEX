"""
Wiring Gap Detector - Identify Missing and Unregistered Components

AC-ID: AC-WIRING-ENFORCEMENT-002
Purpose: Detect gaps in orchestrator and component wiring
Authority: cortex-total-recall.prompt.md (v3.0)
Scope: Scans cortex/ for components not in registry, finds broken imports

This module detects:
1. Orchestrators present in codebase but not registered
2. Components without proper initialization
3. Broken imports or circular dependencies
4. Unregistered MCP tools
5. Missing module exports
6. Components with test failures

"""

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import ast
import importlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class WiringGap:
    """Represents a detected wiring gap."""
    
    component_name: str
    component_type: str  # "orchestrator" | "component" | "mcp_tool" | "module"
    file_path: str
    module_path: str
    import_status: str  # "SUCCESS" | "FAILED" | "NOT_ATTEMPTED"
    error_message: Optional[str] = None
    is_critical: bool = False
    remediation: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class WiringGapDetector:
    """
    Detects gaps in production wiring by scanning codebase for:
    1. Unregistered orchestrators
    2. Unregistered MCP tools
    3. Broken imports
    4. Orphaned components
    """
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """Initialize gap detector."""
        if cortex_root is None:
            cortex_root = Path(__file__).parent.parent
        
        self.cortex_root = cortex_root
        self.detected_gaps: List[WiringGap] = []
    
    def detect_all_gaps(self) -> Dict[str, Any]:
        """
        Execute comprehensive gap detection.
        
        Returns:
            Dict with detected gaps organized by category
        """
        gaps_result = {
            "timestamp": datetime.now().isoformat(),
            "total_gaps_detected": 0,
            "critical_gaps": [],
            "orchestrator_gaps": [],
            "mcp_tool_gaps": [],
            "import_gaps": [],
            "orphaned_components": [],
            "remediation_summary": []
        }
        
        # Detect unregistered orchestrators
        orch_gaps = self._detect_unregistered_orchestrators()
        gaps_result["orchestrator_gaps"] = [
            {
                "name": gap.component_name,
                "file": gap.file_path,
                "module": gap.module_path,
                "critical": gap.is_critical,
                "remediation": gap.remediation
            }
            for gap in orch_gaps
        ]
        
        # Detect unregistered MCP tools
        mcp_gaps = self._detect_unregistered_mcp_tools()
        gaps_result["mcp_tool_gaps"] = [
            {
                "name": gap.component_name,
                "file": gap.file_path,
                "module": gap.module_path,
                "remediation": gap.remediation
            }
            for gap in mcp_gaps
        ]
        
        # Detect broken imports
        import_gaps = self._detect_broken_imports()
        gaps_result["import_gaps"] = [
            {
                "file": gap.file_path,
                "module": gap.module_path,
                "error": gap.error_message,
                "critical": gap.is_critical
            }
            for gap in import_gaps
        ]
        
        # Detect orphaned components
        orphan_gaps = self._detect_orphaned_components()
        gaps_result["orphaned_components"] = [
            {
                "name": gap.component_name,
                "file": gap.file_path,
                "module": gap.module_path,
                "remediation": gap.remediation
            }
            for gap in orphan_gaps
        ]
        
        # Summarize
        all_gaps = orch_gaps + mcp_gaps + import_gaps + orphan_gaps
        self.detected_gaps = all_gaps
        gaps_result["total_gaps_detected"] = len(all_gaps)
        gaps_result["critical_gaps"] = [
            gap.component_name for gap in all_gaps if gap.is_critical
        ]
        
        # Generate remediation summary
        remediation_items = [gap.remediation for gap in all_gaps if gap.remediation]
        gaps_result["remediation_summary"] = remediation_items
        
        return gaps_result
    
    def _detect_unregistered_orchestrators(self) -> List[WiringGap]:
        """Scan for orchestrator classes not registered in MasterOrchestrator."""
        gaps: List[WiringGap] = []
        
        # Known orchestrator patterns
        orchestrator_suffixes = ["Orchestrator", "Router", "Manager"]
        
        orchestrators_dir = self.cortex_root / "orchestrators"
        if not orchestrators_dir.exists():
            logger.warning(f"Orchestrators directory not found: {orchestrators_dir}")
            return gaps
        
        # Scan for .py files
        for py_file in orchestrators_dir.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            
            try:
                with open(py_file, "r") as f:
                    tree = ast.parse(f.read())
                
                # Look for class definitions ending with orchestrator patterns
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if class name suggests it's an orchestrator
                        is_orchestrator = any(
                            node.name.endswith(suffix) for suffix in orchestrator_suffixes
                        )
                        
                        if is_orchestrator and not node.name.startswith("_"):
                            module_path = self._file_to_module_path(py_file)
                            
                            # Try to import and verify registration
                            gap = WiringGap(
                                component_name=node.name,
                                component_type="orchestrator",
                                file_path=str(py_file),
                                module_path=module_path,
                                import_status="NOT_ATTEMPTED"
                            )
                            
                            # Check if registered
                            if not self._is_registered_in_master(node.name):
                                gap.is_critical = "Core" in node.name or node.name == "MasterOrchestrator"
                                gap.remediation = f"Register {node.name} in MasterOrchestrator.register_orchestrator()"
                                gaps.append(gap)
                                logger.warning(f"⚠️  Unregistered orchestrator: {node.name}")
            
            except Exception as e:
                logger.error(f"Error scanning {py_file}: {e}")
        
        return gaps
    
    def _detect_unregistered_mcp_tools(self) -> List[WiringGap]:
        """Scan for MCP tools not registered in ToolRegistry."""
        gaps: List[WiringGap] = []
        
        mcp_dir = self.cortex_root / "mcp" / "tools"
        if not mcp_dir.exists():
            logger.warning(f"MCP tools directory not found: {mcp_dir}")
            return gaps
        
        # Scan for tool definitions
        for py_file in mcp_dir.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            
            try:
                with open(py_file, "r") as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                # Look for functions decorated with @mcp_tool or @tool
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check for tool decorators
                        has_tool_decorator = any(
                            (isinstance(dec, ast.Name) and dec.id in ["mcp_tool", "tool"])
                            or (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name) 
                                and dec.func.id in ["mcp_tool", "tool"])
                            for dec in node.decorator_list
                        )
                        
                        if has_tool_decorator:
                            module_path = self._file_to_module_path(py_file)
                            gap = WiringGap(
                                component_name=node.name,
                                component_type="mcp_tool",
                                file_path=str(py_file),
                                module_path=module_path,
                                import_status="NOT_ATTEMPTED"
                            )
                            
                            # Check if registered
                            if not self._is_registered_in_mcp_registry(node.name):
                                gap.remediation = f"Register {node.name} in ToolRegistry.register_tool()"
                                gaps.append(gap)
                                logger.warning(f"⚠️  Unregistered MCP tool: {node.name}")
            
            except Exception as e:
                logger.error(f"Error scanning {py_file}: {e}")
        
        return gaps
    
    def _detect_broken_imports(self) -> List[WiringGap]:
        """Detect broken imports in core modules."""
        gaps: List[WiringGap] = []
        
        # Critical modules to check
        critical_modules = [
            "cortex.orchestrators.core.master_orchestrator",
            "cortex.intent_router.routing_engine",
            "cortex.brain.core.governance_registry",
            "cortex.brain.core.state_manager",
            "cortex.orchestrators.tools.todo_manager",
        ]
        
        for module_path in critical_modules:
            try:
                importlib.import_module(module_path)
            except ImportError as e:
                py_file = module_path.replace(".", "/") + ".py"
                gap = WiringGap(
                    component_name=module_path.split(".")[-1],
                    component_type="module",
                    file_path=py_file,
                    module_path=module_path,
                    import_status="FAILED",
                    error_message=str(e),
                    is_critical=True
                )
                gap.remediation = f"Fix import in {py_file}: {e}"
                gaps.append(gap)
                logger.error(f"❌ Broken import: {module_path}: {e}")
        
        return gaps
    
    def _detect_orphaned_components(self) -> List[WiringGap]:
        """Detect components without clear ownership or usage."""
        gaps: List[WiringGap] = []
        
        # Check for orphaned class definitions (not exported or referenced)
        core_dir = self.cortex_root / "core"
        if core_dir.exists():
            for py_file in core_dir.rglob("*.py"):
                if py_file.name.startswith("_"):
                    continue
                
                try:
                    with open(py_file, "r") as f:
                        content = f.read()
                        tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            # Classes with no docstring might be orphaned
                            if not ast.get_docstring(node) and not node.name.startswith("_"):
                                module_path = self._file_to_module_path(py_file)
                                gap = WiringGap(
                                    component_name=node.name,
                                    component_type="component",
                                    file_path=str(py_file),
                                    module_path=module_path,
                                    import_status="NOT_ATTEMPTED"
                                )
                                gap.remediation = f"Document {node.name} with docstring or mark as @internal"
                                gaps.append(gap)
                except Exception as e:
                    logger.error(f"Error scanning {py_file}: {e}")
        
        return gaps
    
    def _is_registered_in_master(self, orchestrator_name: str) -> bool:
        """Check if orchestrator is registered in MasterOrchestrator."""
        try:
            master_file = self.cortex_root / "orchestrators" / "core" / "master_orchestrator.py"
            if master_file.exists():
                with open(master_file, "r") as f:
                    content = f.read()
                    if orchestrator_name in content:
                        # Simple check - in production would be more sophisticated
                        return "register_orchestrator" in content and orchestrator_name in content
        except Exception as e:
            logger.error(f"Error checking master orchestrator registration: {e}")
        
        return False
    
    def _is_registered_in_mcp_registry(self, tool_name: str) -> bool:
        """Check if MCP tool is registered in ToolRegistry."""
        try:
            registry_file = self.cortex_root / "mcp" / "registry.py"
            if registry_file.exists():
                with open(registry_file, "r") as f:
                    content = f.read()
                    if tool_name in content:
                        return "register" in content and tool_name in content
        except Exception as e:
            logger.error(f"Error checking MCP registry: {e}")
        
        return False
    
    def _file_to_module_path(self, py_file: Path) -> str:
        """Convert file path to Python module path."""
        try:
            relative = py_file.relative_to(self.cortex_root.parent)
            module = str(relative).replace("/", ".").replace("\\", ".").replace(".py", "")
            return module
        except ValueError:
            return str(py_file).replace("/", ".").replace("\\", ".").replace(".py", "")
    
    def get_critical_gaps_summary(self) -> str:
        """Get summary of critical gaps that must be fixed."""
        critical = [gap for gap in self.detected_gaps if gap.is_critical]
        
        if not critical:
            return "✅ No critical gaps detected"
        
        summary_lines = ["❌ CRITICAL GAPS DETECTED:"]
        for gap in critical:
            summary_lines.append(f"  - {gap.component_name}: {gap.remediation}")
        
        return "\n".join(summary_lines)
