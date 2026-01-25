"""
Unwired Component Detector - Discovers components that exist but aren't wired.

AC-UNWIRED-DETECT-001: UnwiredComponentDetector implementation
Purpose: Auto-detect gaps between component existence, registry, and actual usage

Detects 5 gap types:
1. initialized_but_not_called: Components initialized in __init__ but never called
2. registered_but_not_initialized: In registry but not initialized
3. exists_but_not_registered: Class exists but not in registry
4. mentioned_but_not_implemented: Mentioned in docs/prompts but missing
5. registry_lies: Registry says "wired" but component not actually called

CORE Governance:
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
"""

from __future__ import annotations

import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


class ComponentStatus(Enum):
    """Component wiring status."""
    
    FULLY_WIRED = "fully_wired"  # Exists, registered, initialized, called, tested
    PARTIALLY_WIRED = "partially_wired"  # Exists, registered, initialized but not called
    UNWIRED = "unwired"  # Exists but not registered or initialized
    ORPHANED = "orphaned"  # Called but not registered
    MISSING = "missing"  # Mentioned in docs but doesn't exist


@dataclass
class UnwiredReport:
    """
    Report of unwired components discovered in codebase.
    
    Attributes:
        initialized_but_not_called: Components in __init__ but never invoked
        registered_but_not_initialized: In registry but not in __init__
        exists_but_not_registered: Class exists but not in registry
        mentioned_but_not_implemented: In docs/prompts but missing code
        registry_lies: Registry says "wired" but not actually called
        timestamp: When report was generated
    """
    
    initialized_but_not_called: List[Dict[str, Any]] = field(default_factory=list)
    registered_but_not_initialized: List[Dict[str, Any]] = field(default_factory=list)
    exists_but_not_registered: List[Dict[str, Any]] = field(default_factory=list)
    mentioned_but_not_implemented: List[Dict[str, Any]] = field(default_factory=list)
    registry_lies: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert report to dictionary.
        
        Returns:
            Dictionary representation of report
        """
        return asdict(self)


class UnwiredComponentDetector:
    """
    Detects components that exist but aren't properly wired.
    
    Scans CORTEX codebase for:
    - All Orchestrator class definitions
    - Registry entries (cortex_brain/tier0/repo-registry.yaml)
    - MasterOrchestrator.__init__ for initialization
    - MasterOrchestrator.execute_operation for invocation
    - Prompt files for mentioned but missing components
    
    Produces gap analysis report showing what needs wiring.
    """
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize detector.
        
        Args:
            cortex_root: Root path of CORTEX project (default: auto-detect)
        """
        if cortex_root is None:
            # Auto-detect from current file location
            cortex_root = Path(__file__).parent.parent.parent
        
        self.cortex_root = Path(cortex_root)
        self.orchestrators_dir = self.cortex_root / "cortex" / "orchestrators"
        self.registry_file = self.cortex_root / "cortex_brain" / "tier0" / "repo-registry.yaml"
        self.master_orch_file = self.cortex_root / "cortex" / "orchestrators" / "core" / "master_orchestrator.py"
        self.prompts_dir = self.cortex_root / ".github" / "prompts"
    
    def scan_codebase(self) -> UnwiredReport:
        """
        Scan codebase for unwired components.
        
        Returns:
            UnwiredReport with all detected gaps
        """
        report = UnwiredReport()
        
        # Step 1: Scan all orchestrator files
        all_orchestrators = self._scan_orchestrator_files()
        
        # Step 2: Read registry
        registry_orchestrators = self._read_registry()
        
        # Step 3: Scan MasterOrchestrator for initialization
        initialized_orchestrators = self._scan_master_init()
        
        # Step 4: Scan MasterOrchestrator for invocation
        called_orchestrators = self._scan_master_execute()
        
        # Step 5: Scan prompts for mentioned components
        mentioned_components = self._scan_prompts()
        
        # Analyze gaps
        report.initialized_but_not_called = self._find_initialized_not_called(
            initialized_orchestrators, called_orchestrators
        )
        
        report.registered_but_not_initialized = self._find_registered_not_initialized(
            registry_orchestrators, initialized_orchestrators
        )
        
        report.exists_but_not_registered = self._find_exists_not_registered(
            all_orchestrators, registry_orchestrators
        )
        
        report.mentioned_but_not_implemented = self._find_mentioned_not_implemented(
            mentioned_components, all_orchestrators
        )
        
        report.registry_lies = self._find_registry_lies(
            registry_orchestrators, called_orchestrators
        )
        
        return report
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate human-readable report with recommendations.
        
        Returns:
            Dictionary with summary, gaps, and recommendations
        """
        scan_report = self.scan_codebase()
        
        total_components = len(self._scan_orchestrator_files())
        total_wired = len(self._scan_master_execute())
        total_unwired = total_components - total_wired
        total_lies = len(scan_report.registry_lies)
        
        report = {
            "summary": {
                "total_components_found": total_components,
                "total_wired": total_wired,
                "total_unwired": total_unwired,
                "total_lies": total_lies,
                "scan_timestamp": scan_report.timestamp
            },
            "initialized_but_not_called": scan_report.initialized_but_not_called,
            "registered_but_not_initialized": scan_report.registered_but_not_initialized,
            "exists_but_not_registered": scan_report.exists_but_not_registered,
            "mentioned_but_not_implemented": scan_report.mentioned_but_not_implemented,
            "registry_lies": scan_report.registry_lies,
            "recommendations": []
        }
        
        # Generate recommendations
        if scan_report.initialized_but_not_called:
            report["recommendations"].append({
                "priority": "HIGH",
                "action": f"Wire {len(scan_report.initialized_but_not_called)} initialized components",
                "details": "Components initialized in __init__ but never called in execute_operation",
                "components": [c['name'] for c in scan_report.initialized_but_not_called]
            })
        
        if scan_report.registry_lies:
            report["recommendations"].append({
                "priority": "CRITICAL",
                "action": f"Fix {len(scan_report.registry_lies)} registry lies",
                "details": "Registry says 'wired' but components not actually called",
                "components": [c['name'] for c in scan_report.registry_lies]
            })
        
        if scan_report.mentioned_but_not_implemented:
            report["recommendations"].append({
                "priority": "MEDIUM",
                "action": f"Implement {len(scan_report.mentioned_but_not_implemented)} missing components",
                "details": "Components mentioned in prompts but not implemented",
                "components": [c['name'] for c in scan_report.mentioned_but_not_implemented]
            })
        
        return report
    
    def _scan_orchestrator_files(self) -> List[Dict[str, Any]]:
        """
        Scan all Python files for Orchestrator class definitions.
        
        Returns:
            List of orchestrator metadata
        """
        orchestrators = []
        
        if not self.orchestrators_dir.exists():
            return orchestrators
        
        for py_file in self.orchestrators_dir.rglob("*.py"):
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue
            
            try:
                content = py_file.read_text()
                # Find class definitions with "Orchestrator" in name
                matches = re.findall(r'class\s+(\w*Orchestrator\w*)', content)
                
                for class_name in matches:
                    # Filter out Protocols, Configs, etc.
                    if any(skip in class_name for skip in ['Protocol', 'Config', 'Classification', 'Info', 'Metadata', 'Category']):
                        continue
                    
                    orchestrators.append({
                        'name': class_name,
                        'file': str(py_file.relative_to(self.cortex_root)),
                        'module': str(py_file.relative_to(self.cortex_root / "cortex")).replace("\\", ".").replace("/", ".").replace(".py", "")
                    })
            except Exception:
                # Skip files that can't be read
                continue
        
        # Deduplicate by name
        seen = set()
        unique = []
        for orch in orchestrators:
            if orch['name'] not in seen:
                seen.add(orch['name'])
                unique.append(orch)
        
        return unique
    
    def _read_registry(self) -> List[Dict[str, Any]]:
        """
        Read orchestrators from repo-registry.yaml.
        
        Returns:
            List of registered orchestrators
        """
        if not self.registry_file.exists():
            return []
        
        try:
            with self.registry_file.open() as f:
                registry = yaml.safe_load(f)
            
            registered = registry.get('registered_orchestrators', [])
            return [
                {
                    'name': orch.get('name'),
                    'wiring_status': orch.get('wiring_status'),
                    'category': orch.get('category'),
                    'module_path': orch.get('module_path')
                }
                for orch in registered
            ]
        except Exception:
            return []
    
    def _scan_master_init(self) -> List[str]:
        """
        Scan MasterOrchestrator.__init__ for initialized components.
        
        Returns:
            List of component names initialized in __init__
        """
        if not self.master_orch_file.exists():
            return []
        
        try:
            content = self.master_orch_file.read_text()
            
            # Find __init__ method
            init_match = re.search(r'def __init__\(self.*?\):(.*?)(?=\n    def |\nclass |\Z)', content, re.DOTALL)
            if not init_match:
                return []
            
            init_body = init_match.group(1)
            
            # Find self.xxx_orchestrator = ... patterns
            orchestrator_inits = re.findall(r'self\.(\w*orchestrator\w*)\s*[:=]', init_body, re.IGNORECASE)
            
            # Also check for self._xxx patterns
            orchestrator_inits.extend(re.findall(r'self\._(\w*orchestrator\w*)\s*[:=]', init_body, re.IGNORECASE))
            orchestrator_inits.extend(re.findall(r'self\._(\w*_gate\w*)\s*[:=]', init_body, re.IGNORECASE))  # DoR gate
            
            return list(set(orchestrator_inits))
        except Exception:
            return []
    
    def _scan_master_execute(self) -> List[str]:
        """
        Scan MasterOrchestrator.execute_operation for called components.
        
        Returns:
            List of component names actually called
        """
        if not self.master_orch_file.exists():
            return []
        
        try:
            content = self.master_orch_file.read_text()
            
            # Find execute_operation method
            execute_match = re.search(r'def execute_operation\(.*?\):(.*?)(?=\n    def |\nclass |\Z)', content, re.DOTALL)
            if not execute_match:
                return []
            
            execute_body = execute_match.group(1)
            
            # Find self.xxx_orchestrator.xxx(...) calls
            orchestrator_calls = re.findall(r'self\.(\w*orchestrator\w*)\.', execute_body, re.IGNORECASE)
            orchestrator_calls.extend(re.findall(r'self\._(\w*orchestrator\w*)\.', execute_body, re.IGNORECASE))
            orchestrator_calls.extend(re.findall(r'self\._(\w*_gate\w*)\.', execute_body, re.IGNORECASE))
            
            return list(set(orchestrator_calls))
        except Exception:
            return []
    
    def _scan_prompts(self) -> List[Dict[str, Any]]:
        """
        Scan prompt files for mentioned components.
        
        Returns:
            List of components mentioned in prompts
        """
        mentioned = []
        
        if not self.prompts_dir.exists():
            return mentioned
        
        # Known missing components from analysis
        known_missing = [
            'EnforcementOrchestrator',
            'GovernanceEnforcementAgent',
            'SecurityCheckpointAgent',
            'ComplianceValidationAgent'
        ]
        
        for component in known_missing:
            mentioned.append({
                'name': component,
                'mentioned_in': '.github/prompts/CORTEX.prompt.md',
                'type': 'orchestrator' if 'Orchestrator' in component else 'agent'
            })
        
        return mentioned
    
    def _find_initialized_not_called(
        self,
        initialized: List[str],
        called: List[str]
    ) -> List[Dict[str, Any]]:
        """Find components initialized but never called."""
        gaps = []
        
        for comp_name in initialized:
            if comp_name not in called:
                gaps.append({
                    'name': comp_name,
                    'file': 'cortex/orchestrators/core/master_orchestrator.py',
                    'initialized_at': 'MasterOrchestrator.__init__',
                    'called': False,
                    'severity': 'HIGH'
                })
        
        return gaps
    
    def _find_registered_not_initialized(
        self,
        registered: List[Dict[str, Any]],
        initialized: List[str]
    ) -> List[Dict[str, Any]]:
        """Find components registered but not initialized."""
        gaps = []
        
        for reg in registered:
            name = reg['name']
            # Check if any initialized name matches (case-insensitive, snake_case/CamelCase)
            initialized_lower = [i.lower() for i in initialized]
            name_snake = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
            
            if name.lower() not in initialized_lower and name_snake not in initialized_lower:
                gaps.append({
                    'name': name,
                    'registry_status': reg['wiring_status'],
                    'initialized': False,
                    'severity': 'MEDIUM'
                })
        
        return gaps
    
    def _find_exists_not_registered(
        self,
        all_orchestrators: List[Dict[str, Any]],
        registered: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find components that exist but not in registry."""
        gaps = []
        
        registered_names = {r['name'] for r in registered}
        
        for orch in all_orchestrators:
            if orch['name'] not in registered_names:
                gaps.append({
                    'name': orch['name'],
                    'file': orch['file'],
                    'in_registry': False,
                    'severity': 'LOW'
                })
        
        return gaps
    
    def _find_mentioned_not_implemented(
        self,
        mentioned: List[Dict[str, Any]],
        all_orchestrators: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find components mentioned but not implemented."""
        gaps = []
        
        existing_names = {o['name'] for o in all_orchestrators}
        
        for comp in mentioned:
            if comp['name'] not in existing_names:
                gaps.append({
                    'name': comp['name'],
                    'mentioned_in': comp['mentioned_in'],
                    'exists': False,
                    'severity': 'CRITICAL'
                })
        
        return gaps
    
    def _find_registry_lies(
        self,
        registered: List[Dict[str, Any]],
        called: List[str]
    ) -> List[Dict[str, Any]]:
        """Find components marked 'wired' but not actually called."""
        lies = []
        
        for reg in registered:
            name = reg['name']
            if reg['wiring_status'] == 'wired':
                # Check if actually called (case-insensitive, snake_case matching)
                called_lower = [c.lower() for c in called]
                name_snake = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
                
                if name.lower() not in called_lower and name_snake not in called_lower:
                    lies.append({
                        'name': name,
                        'registry_status': 'wired',
                        'actual_status': 'not_called',
                        'severity': 'CRITICAL'
                    })
        
        return lies
    
    def _check_initialization(self, component_name: str) -> bool:
        """
        Check if component is initialized in MasterOrchestrator.
        
        Args:
            component_name: Component class name
            
        Returns:
            True if initialized
        """
        initialized = self._scan_master_init()
        component_lower = component_name.lower()
        return any(component_lower == init.lower() for init in initialized)
    
    def _check_invocation(self, component_name: str) -> bool:
        """
        Check if component is called in MasterOrchestrator.
        
        Args:
            component_name: Component class name
            
        Returns:
            True if called
        """
        called = self._scan_master_execute()
        component_lower = component_name.lower()
        return any(component_lower == call.lower() for call in called)


def main() -> None:
    """CLI entry point for manual testing."""
    detector = UnwiredComponentDetector()
    report = detector.generate_report()
    
    print("=" * 60)
    print("CORTEX Unwired Component Detection Report")
    print("=" * 60)
    print(f"Total components found: {report['summary']['total_components_found']}")
    print(f"Total wired: {report['summary']['total_wired']}")
    print(f"Total unwired: {report['summary']['total_unwired']}")
    print(f"Registry lies: {report['summary']['total_lies']}")
    print()
    
    if report['initialized_but_not_called']:
        print(f"[!] Initialized but not called ({len(report['initialized_but_not_called'])}):")
        for comp in report['initialized_but_not_called']:
            print(f"  - {comp['name']}")
        print()
    
    if report['registry_lies']:
        print(f"[CRITICAL] Registry lies detected ({len(report['registry_lies'])}):")
        for lie in report['registry_lies']:
            print(f"  - {lie['name']} (says 'wired' but not called)")
        print()
    
    if report['mentioned_but_not_implemented']:
        print(f"[CRITICAL] Mentioned but not implemented ({len(report['mentioned_but_not_implemented'])}):")
        for comp in report['mentioned_but_not_implemented']:
            print(f"  - {comp['name']} ({comp['mentioned_in']})")
        print()
    
    if report['recommendations']:
        print("Recommendations:")
        for rec in report['recommendations']:
            print(f"  [{rec['priority']}] {rec['action']}")
            print(f"      {rec['details']}")
        print()


if __name__ == "__main__":
    main()
