#!/usr/bin/env python3
"""
CORTEX Wiring Integrity Checker

Ensures all components remain properly wired to the system.
Detects and reports unwired orchestrators, agents, modules, and plugins.

Features:
- Continuous monitoring mode
- Auto-wire suggestions
- Integration with cortex-operations.yaml
- Pre-commit hook integration

Usage:
    python scripts/check_wiring_integrity.py              # Check all components
    python scripts/check_wiring_integrity.py --fix        # Auto-generate wire suggestions
    python scripts/check_wiring_integrity.py --monitor    # Continuous monitoring
    python scripts/check_wiring_integrity.py --pre-commit # For git hooks

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import ast
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class WiringStatus:
    """Status of a component's wiring."""
    name: str
    file_path: str
    component_type: str  # orchestrator, agent, module, plugin
    is_wired: bool
    wired_in: List[str] = field(default_factory=list)  # Where it's wired
    suggested_wiring: str = ""


@dataclass
class WiringReport:
    """Complete wiring integrity report."""
    timestamp: str
    total_components: int = 0
    wired_components: int = 0
    unwired_components: int = 0
    components: List[WiringStatus] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    @property
    def wiring_percentage(self) -> float:
        if self.total_components == 0:
            return 100.0
        return (self.wired_components / self.total_components) * 100


class WiringIntegrityChecker:
    """
    Checks and maintains wiring integrity for CORTEX components.
    
    Ensures:
    - All orchestrators are registered in cortex-operations.yaml
    - All agents are registered in response templates or operations
    - All modules have proper entry points
    - All plugins are discoverable
    """
    
    def __init__(self, project_root: Path):
        self.root = project_root
        self.operations_yaml = project_root / "cortex-brain" / "manifests" / "operations" / "cortex-operations.yaml"
        self.response_templates = project_root / "cortex-brain" / "response-templates-v4.yaml"
        
        # Cache loaded configurations
        self._operations_cache = None
        self._templates_cache = None
    
    def check_all(self) -> WiringReport:
        """Check wiring integrity for all components."""
        report = WiringReport(timestamp=datetime.now().isoformat())
        
        print("🔌 Checking CORTEX Wiring Integrity...\n")
        
        # 1. Check orchestrators
        print("📋 Checking Orchestrators...")
        orchestrator_status = self._check_orchestrators()
        report.components.extend(orchestrator_status)
        
        # 2. Check agents
        print("🤖 Checking Agents...")
        agent_status = self._check_agents()
        report.components.extend(agent_status)
        
        # 3. Check operation modules
        print("⚙️  Checking Operation Modules...")
        module_status = self._check_modules()
        report.components.extend(module_status)
        
        # 4. Check plugins
        print("🔌 Checking Plugins...")
        plugin_status = self._check_plugins()
        report.components.extend(plugin_status)
        
        # Calculate totals
        report.total_components = len(report.components)
        report.wired_components = len([c for c in report.components if c.is_wired])
        report.unwired_components = report.total_components - report.wired_components
        
        # Generate suggestions for unwired components
        for component in report.components:
            if not component.is_wired:
                suggestion = self._generate_wiring_suggestion(component)
                if suggestion:
                    report.suggestions.append(suggestion)
        
        return report
    
    def _load_operations_yaml(self) -> Dict[str, Any]:
        """Load and cache cortex-operations.yaml."""
        if self._operations_cache is not None:
            return self._operations_cache
        
        if not self.operations_yaml.exists():
            return {}
        
        with open(self.operations_yaml, 'r', encoding='utf-8') as f:
            self._operations_cache = yaml.safe_load(f) or {}
        
        return self._operations_cache
    
    def _load_response_templates(self) -> Dict[str, Any]:
        """Load and cache response templates."""
        if self._templates_cache is not None:
            return self._templates_cache
        
        if not self.response_templates.exists():
            return {}
        
        with open(self.response_templates, 'r', encoding='utf-8') as f:
            self._templates_cache = yaml.safe_load(f) or {}
        
        return self._templates_cache
    
    def _get_wired_names(self) -> Set[str]:
        """Get all component names that are wired in configurations."""
        wired = set()
        
        operations = self._load_operations_yaml()
        templates = self._load_response_templates()
        
        # From operations yaml
        operations_dict = operations if isinstance(operations, dict) else {}
        for op_name, op_data in operations_dict.get('operations', {}).items():
            wired.add(op_name)
            if isinstance(op_data, dict):
                # Add handler/orchestrator names
                handler = op_data.get('handler', '')
                if handler:
                    wired.add(handler)
                orchestrator = op_data.get('orchestrator', '')
                if orchestrator:
                    wired.add(orchestrator)
        
        # From response templates
        templates_dict = templates if isinstance(templates, dict) else {}
        for template_name, template_data in templates_dict.get('templates', {}).items():
            wired.add(template_name)
        
        return wired
    
    def _extract_classes(self, file_path: Path) -> List[str]:
        """Extract class names from a Python file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        except Exception:
            return []
    
    def _check_orchestrators(self) -> List[WiringStatus]:
        """Check orchestrator wiring status."""
        status_list = []
        wired_names = self._get_wired_names()
        
        # Find all orchestrator files
        orchestrator_dirs = [
            self.root / "src" / "orchestrators",
            self.root / "src" / "operations" / "modules" / "orchestration",
        ]
        
        for orch_dir in orchestrator_dirs:
            if not orch_dir.exists():
                continue
            
            for py_file in orch_dir.rglob("*orchestrator*.py"):
                if '__pycache__' in str(py_file) or 'test_' in py_file.name:
                    continue
                if 'archived' in py_file.name.lower():
                    continue
                
                classes = self._extract_classes(py_file)
                for class_name in classes:
                    if 'Orchestrator' not in class_name:
                        continue
                    if class_name in ('OrchestratorResult', 'OrchestratorConfig', 'BaseOrchestrator'):
                        continue
                    
                    # Check if wired
                    is_wired = any(
                        class_name.lower() in wn.lower() or
                        class_name.replace('Orchestrator', '').lower() in wn.lower()
                        for wn in wired_names
                    )
                    
                    status = WiringStatus(
                        name=class_name,
                        file_path=str(py_file.relative_to(self.root)),
                        component_type='orchestrator',
                        is_wired=is_wired,
                        wired_in=['cortex-operations.yaml'] if is_wired else []
                    )
                    status_list.append(status)
        
        wired_count = len([s for s in status_list if s.is_wired])
        print(f"   Found {len(status_list)} orchestrators, {wired_count} wired")
        
        return status_list
    
    def _check_agents(self) -> List[WiringStatus]:
        """Check agent wiring status."""
        status_list = []
        wired_names = self._get_wired_names()
        
        agent_dir = self.root / "src" / "cortex_agents"
        if not agent_dir.exists():
            return status_list
        
        for py_file in agent_dir.rglob("*agent*.py"):
            if '__pycache__' in str(py_file) or 'test_' in py_file.name:
                continue
            
            classes = self._extract_classes(py_file)
            for class_name in classes:
                if 'Agent' not in class_name:
                    continue
                if class_name in ('BaseAgent', 'AgentConfig'):
                    continue
                
                is_wired = any(
                    class_name.lower() in wn.lower()
                    for wn in wired_names
                )
                
                status = WiringStatus(
                    name=class_name,
                    file_path=str(py_file.relative_to(self.root)),
                    component_type='agent',
                    is_wired=is_wired,
                    wired_in=['response-templates-v4.yaml'] if is_wired else []
                )
                status_list.append(status)
        
        wired_count = len([s for s in status_list if s.is_wired])
        print(f"   Found {len(status_list)} agents, {wired_count} wired")
        
        return status_list
    
    def _check_modules(self) -> List[WiringStatus]:
        """Check operation module wiring status."""
        status_list = []
        wired_names = self._get_wired_names()
        
        modules_dir = self.root / "src" / "operations" / "modules"
        if not modules_dir.exists():
            return status_list
        
        for py_file in modules_dir.rglob("*.py"):
            if '__pycache__' in str(py_file) or 'test_' in py_file.name:
                continue
            if py_file.name.startswith('_'):
                continue
            
            # Get module name from file
            module_name = py_file.stem
            
            # Check if wired
            is_wired = any(
                module_name.lower() in wn.lower()
                for wn in wired_names
            )
            
            status = WiringStatus(
                name=module_name,
                file_path=str(py_file.relative_to(self.root)),
                component_type='module',
                is_wired=is_wired,
                wired_in=['cortex-operations.yaml'] if is_wired else []
            )
            status_list.append(status)
        
        wired_count = len([s for s in status_list if s.is_wired])
        print(f"   Found {len(status_list)} modules, {wired_count} wired")
        
        return status_list
    
    def _check_plugins(self) -> List[WiringStatus]:
        """Check plugin wiring status."""
        status_list = []
        wired_names = self._get_wired_names()
        
        plugins_dir = self.root / "src" / "plugins"
        if not plugins_dir.exists():
            return status_list
        
        for py_file in plugins_dir.rglob("*plugin*.py"):
            if '__pycache__' in str(py_file) or 'test_' in py_file.name:
                continue
            
            classes = self._extract_classes(py_file)
            for class_name in classes:
                if 'Plugin' not in class_name:
                    continue
                if class_name in ('BasePlugin', 'PluginConfig'):
                    continue
                
                is_wired = any(
                    class_name.lower() in wn.lower()
                    for wn in wired_names
                )
                
                status = WiringStatus(
                    name=class_name,
                    file_path=str(py_file.relative_to(self.root)),
                    component_type='plugin',
                    is_wired=is_wired,
                    wired_in=['cortex-operations.yaml'] if is_wired else []
                )
                status_list.append(status)
        
        wired_count = len([s for s in status_list if s.is_wired])
        print(f"   Found {len(status_list)} plugins, {wired_count} wired")
        
        return status_list
    
    def _generate_wiring_suggestion(self, component: WiringStatus) -> str:
        """Generate a wiring suggestion for an unwired component."""
        if component.component_type == 'orchestrator':
            # Generate cortex-operations.yaml entry
            op_name = component.name.replace('Orchestrator', '').lower()
            return f"""
# Add to cortex-operations.yaml:
operations:
  {op_name}:
    handler: {component.name}
    description: "{component.name} operation"
    execution_method: copilot_chat
    file: {component.file_path}
"""
        elif component.component_type == 'agent':
            return f"# Register {component.name} in response-templates-v4.yaml or operations"
        
        return ""
    
    def print_report(self, report: WiringReport):
        """Print wiring report to console."""
        print("\n" + "=" * 70)
        print("🔌 WIRING INTEGRITY REPORT")
        print("=" * 70)
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   Total Components: {report.total_components}")
        print(f"   Wired:   {report.wired_components} ✅")
        print(f"   Unwired: {report.unwired_components} {'❌' if report.unwired_components > 0 else '✅'}")
        print(f"   Coverage: {report.wiring_percentage:.1f}%")
        
        # Unwired components
        unwired = [c for c in report.components if not c.is_wired]
        if unwired:
            print(f"\n⚠️  Unwired Components ({len(unwired)}):")
            for component in unwired:
                print(f"   - [{component.component_type}] {component.name}")
                print(f"     File: {component.file_path}")
        
        # Wiring suggestions
        if report.suggestions:
            print(f"\n💡 Wiring Suggestions:")
            for i, suggestion in enumerate(report.suggestions[:3], 1):
                print(f"\n{i}. {suggestion[:200]}...")
        
        # Status
        if report.unwired_components == 0:
            print(f"\n✅ All components are properly wired!")
        else:
            print(f"\n⚠️  {report.unwired_components} component(s) need wiring")
        
        print("\n" + "=" * 70)


def run_pre_commit_check() -> int:
    """Run as pre-commit hook - fails if critical components unwired."""
    checker = WiringIntegrityChecker(PROJECT_ROOT)
    report = checker.check_all()
    
    # Only fail on unwired orchestrators (critical)
    critical_unwired = [
        c for c in report.components 
        if not c.is_wired and c.component_type == 'orchestrator'
    ]
    
    if critical_unwired:
        print(f"\n❌ Pre-commit failed: {len(critical_unwired)} unwired orchestrator(s)")
        for c in critical_unwired:
            print(f"   - {c.name} ({c.file_path})")
        return 1
    
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='CORTEX Wiring Integrity Checker',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Generate wiring suggestions'
    )
    
    parser.add_argument(
        '--pre-commit',
        action='store_true',
        help='Run as pre-commit hook (strict mode)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal output'
    )
    
    args = parser.parse_args()
    
    if args.pre_commit:
        sys.exit(run_pre_commit_check())
    
    checker = WiringIntegrityChecker(PROJECT_ROOT)
    report = checker.check_all()
    
    if not args.quiet:
        checker.print_report(report)
    
    # Save report
    output_dir = PROJECT_ROOT / "cortex-brain" / "health-reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = output_dir / f"wiring-report-{timestamp}.json"
    
    import json
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': report.timestamp,
            'total': report.total_components,
            'wired': report.wired_components,
            'unwired': report.unwired_components,
            'coverage': report.wiring_percentage,
            'components': [
                {
                    'name': c.name,
                    'type': c.component_type,
                    'file': c.file_path,
                    'wired': c.is_wired
                } for c in report.components
            ]
        }, f, indent=2)
    
    if not args.quiet:
        print(f"\n📄 Report saved: {report_path}")
    
    # Exit with error if unwired components
    sys.exit(0 if report.unwired_components == 0 else 1)


if __name__ == '__main__':
    main()
