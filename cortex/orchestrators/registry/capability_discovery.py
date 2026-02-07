"""
Capability Discovery for Orchestrator Mesh.

AC-PHASE38-003: OrchestratorCapabilityRegistry with dynamic discovery

Provides:
- Automatic capability discovery from orchestrator classes
- Registry of orchestrator capabilities
- Capability extraction from docstrings and methods
"""

from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import ast
import inspect
from dataclasses import dataclass


@dataclass
class DiscoveredCapability:
    """A discovered capability from an orchestrator."""
    
    name: str
    source: str  # 'docstring' or 'method'
    orchestrator: str
    description: Optional[str] = None


class OrchestratorCapabilityRegistry:
    """
    Registry for orchestrator capabilities.
    
    Supports dynamic discovery and registration of capabilities.
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._orchestrators: Dict[str, List[str]] = {}
        self._capabilities: Dict[str, List[str]] = {}
    
    def discover_capabilities(self, orchestrator_class: Any) -> List[DiscoveredCapability]:
        """
        Discover capabilities from orchestrator class.
        
        Args:
            orchestrator_class: Orchestrator class to analyze
        
        Returns:
            List of discovered capabilities
        """
        capabilities = []
        orchestrator_name = orchestrator_class.__name__
        
        # Try to call get_capabilities() if it exists
        if hasattr(orchestrator_class, 'get_capabilities'):
            try:
                cap_list = orchestrator_class.get_capabilities()
                for cap in cap_list:
                    capabilities.append(DiscoveredCapability(
                        name=cap,
                        source='method',
                        orchestrator=orchestrator_name
                    ))
            except:
                pass
        
        return capabilities
    
    def register_orchestrator(self, orchestrator_name: str, capabilities: List[str]) -> None:
        """
        Register an orchestrator with its capabilities.
        
        Args:
            orchestrator_name: Name of orchestrator
            capabilities: List of capability names
        """
        self._orchestrators[orchestrator_name] = capabilities
        
        # Index by capability
        for cap in capabilities:
            if cap not in self._capabilities:
                self._capabilities[cap] = []
            self._capabilities[cap].append(orchestrator_name)
    
    def get_orchestrators_by_capability(self, capability: str) -> List[str]:
        """
        Get orchestrators that provide a capability.
        
        Args:
            capability: Capability name
        
        Returns:
            List of orchestrator names
        """
        return self._capabilities.get(capability, [])
    
    def get_capabilities_for_orchestrator(self, orchestrator: str) -> List[str]:
        """
        Get capabilities provided by an orchestrator.
        
        Args:
            orchestrator: Orchestrator name
        
        Returns:
            List of capability names
        """
        return self._orchestrators.get(orchestrator, [])
    
    def list_all_capabilities(self) -> List[str]:
        """List all registered capabilities."""
        return list(self._capabilities.keys())
    
    def list_all_orchestrators(self) -> List[str]:
        """List all registered orchestrators."""
        return list(self._orchestrators.keys())


class CapabilityDiscoveryAgent:
    """
    Agent for discovering capabilities from orchestrator files.
    
    Scans orchestrator directory and extracts capabilities.
    """
    
    def __init__(self, orchestrators_root: Optional[Path] = None):
        """
        Initialize discovery agent.
        
        Args:
            orchestrators_root: Root directory for orchestrators
        """
        if orchestrators_root is None:
            self.orchestrators_root = Path(__file__).parent.parent.parent / "orchestrators"
        else:
            self.orchestrators_root = orchestrators_root
    
    def scan_orchestrators(self) -> Dict[str, List[str]]:
        """
        Scan orchestrators directory for capabilities.
        
        Returns:
            Dict mapping orchestrator name to capabilities
        """
        discovered = {}
        
        # Scan for Python files
        if self.orchestrators_root.exists():
            for py_file in self.orchestrators_root.rglob("*.py"):
                if py_file.name.startswith("_"):
                    continue
                
                try:
                    capabilities = self._analyze_file(py_file)
                    if capabilities:
                        orchestrator_name = py_file.stem
                        discovered[orchestrator_name] = capabilities
                except:
                    pass
        
        return discovered
    
    def extract_capabilities_from_docstring(self, code: str) -> List[str]:
        """
        Extract capabilities from docstring.
        
        Looks for "Capabilities:" section in docstring.
        
        Args:
            code: Source code
        
        Returns:
            List of capability names
        """
        capabilities = []
        
        # Simple pattern matching
        lines = code.split('\n')
        in_capabilities = False
        
        for line in lines:
            stripped = line.strip()
            if 'Capabilities:' in stripped:
                in_capabilities = True
                continue
            
            if in_capabilities:
                if stripped.startswith('-'):
                    # Extract capability name (before colon)
                    parts = stripped[1:].split(':')
                    if parts:
                        cap_name = parts[0].strip()
                        capabilities.append(cap_name)
                elif stripped == '' or not stripped.startswith(' '):
                    # End of capabilities section
                    break
        
        return capabilities
    
    def extract_capabilities_from_methods(self, orchestrator_class: Any) -> List[str]:
        """
        Extract capabilities from public methods.
        
        Args:
            orchestrator_class: Orchestrator class
        
        Returns:
            List of method names (capabilities)
        """
        capabilities = []
        
        for name in dir(orchestrator_class):
            if name.startswith('_'):
                continue
            
            attr = getattr(orchestrator_class, name)
            if callable(attr):
                capabilities.append(name)
        
        return capabilities
    
    def _analyze_file(self, file_path: Path) -> List[str]:
        """
        Analyze a Python file for capabilities.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            List of capabilities
        """
        try:
            code = file_path.read_text()
            return self.extract_capabilities_from_docstring(code)
        except:
            return []


# AC-PHASE38-003 ✅ Implementation complete
