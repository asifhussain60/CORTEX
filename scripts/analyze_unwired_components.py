#!/usr/bin/env python3
"""
Analyze Unwired Components in CORTEX

Systematically discovers all orchestrators, agents, modules, and checks their wiring status.
Generates comprehensive report for remediation planning.

Author: Asif Hussain
"""

import ast
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Any
from datetime import datetime
from collections import defaultdict

class UnwiredComponentAnalyzer:
    """Analyzes CORTEX components and identifies unwired functionality."""
    
    def __init__(self, project_root: Path):
        self.root = project_root
        self.results = {
            'orchestrators': [],
            'agents': [],
            'operation_modules': [],
            'setup_modules': [],
            'plugins': [],
            'summary': {}
        }
        
    def analyze_all(self) -> Dict[str, Any]:
        """Run complete analysis."""
        print("🔍 Starting comprehensive unwired component analysis...")
        
        # Phase 1: Orchestrators
        print("\n📋 Phase 1: Analyzing Orchestrators...")
        self.analyze_orchestrators()
        
        # Phase 2: Agents
        print("\n🤖 Phase 2: Analyzing Agents...")
        self.analyze_agents()
        
        # Phase 3: Operation Modules
        print("\n⚙️  Phase 3: Analyzing Operation Modules...")
        self.analyze_operation_modules()
        
        # Phase 4: Setup Modules
        print("\n🚀 Phase 4: Analyzing Setup Modules...")
        self.analyze_setup_modules()
        
        # Phase 5: Plugins
        print("\n🔌 Phase 5: Analyzing Plugins...")
        self.analyze_plugins()
        
        # Generate summary
        self.generate_summary()
        
        return self.results
    
    def analyze_orchestrators(self):
        """Analyze all orchestrators and check wiring."""
        # Find all orchestrator files
        orchestrator_files = []
        
        # src/orchestrators/
        src_orch_dir = self.root / "src" / "orchestrators"
        if src_orch_dir.exists():
            orchestrator_files.extend(src_orch_dir.rglob("*orchestrator*.py"))
        
        # src/operations/modules/*orchestrator*.py
        operations_dir = self.root / "src" / "operations" / "modules"
        if operations_dir.exists():
            orchestrator_files.extend(operations_dir.rglob("*orchestrator*.py"))
        
        # Load wiring data
        operations_yaml = self.load_operations_yaml()
        response_templates = self.load_response_templates()
        
        for file_path in orchestrator_files:
            if '__pycache__' in str(file_path) or 'test_' in file_path.name:
                continue
            
            # Skip archived files
            if 'archived' in file_path.name.lower() or 'migrated_archived' in file_path.name.lower():
                continue
            
            classes = self.extract_classes(file_path)
            for class_name in classes:
                if 'Orchestrator' not in class_name:
                    continue
                
                # Skip data classes and base classes
                if class_name in ('OrchestratorResult', 'OrchestratorConfig', 'BaseOrchestrator'):
                    continue
                
                # Check wiring
                wiring_status = self.check_orchestrator_wiring(
                    class_name, file_path, operations_yaml, response_templates
                )
                
                self.results['orchestrators'].append({
                    'name': class_name,
                    'file': str(file_path.relative_to(self.root)),
                    'in_operations_yaml': wiring_status['in_operations'],
                    'has_response_template': wiring_status['has_template'],
                    'has_triggers': wiring_status['has_triggers'],
                    'wired': wiring_status['wired'],
                    'operation_id': wiring_status.get('operation_id'),
                    'triggers': wiring_status.get('triggers', [])
                })
        
        wired_count = sum(1 for o in self.results['orchestrators'] if o['wired'])
        total = len(self.results['orchestrators'])
        print(f"   Found {total} orchestrators, {wired_count} wired ({wired_count/total*100:.1f}%)")
    
    def analyze_agents(self):
        """Analyze all agents and check wiring."""
        agents_dir = self.root / "src" / "cortex_agents"
        if not agents_dir.exists():
            return
        
        # Load AgentExecutor to see wired agents
        agent_executor_path = self.root / "src" / "entry_point" / "agent_executor.py"
        wired_agents = self.extract_wired_agents(agent_executor_path)
        
        # Load AgentType enum
        agent_types_path = agents_dir / "agent_types.py"
        agent_type_enums = self.extract_agent_types(agent_types_path)
        
        # Find all agent files
        agent_files = agents_dir.rglob("*agent*.py")
        
        for file_path in agent_files:
            if '__pycache__' in str(file_path) or 'test_' in file_path.name:
                continue
            
            classes = self.extract_classes(file_path)
            for class_name in classes:
                if not class_name.endswith('Agent') or class_name == 'BaseAgent':
                    continue
                
                # Normalize name: LearningCaptureAgent -> learningcapture
                normalized_name = class_name.lower().replace('agent', '')
                
                # Check wiring in executor
                wired = class_name in wired_agents or any(
                    normalized_name in wired.lower() 
                    for wired in wired_agents
                )
                
                # Check AgentType enum - normalize underscores for comparison
                # LEARNING_CAPTURE -> learningcapture (remove underscores)
                has_agent_type = any(
                    normalized_name == enum.lower().replace('_', '')
                    for enum in agent_type_enums
                )
                
                self.results['agents'].append({
                    'name': class_name,
                    'file': str(file_path.relative_to(self.root)),
                    'wired_in_executor': wired,
                    'has_agent_type_enum': has_agent_type,
                    'wired': wired and has_agent_type
                })
        
        wired_count = sum(1 for a in self.results['agents'] if a['wired'])
        total = len(self.results['agents'])
        print(f"   Found {total} agents, {wired_count} wired ({wired_count/total*100:.1f}%)")
    
    def analyze_operation_modules(self):
        """Analyze operation modules and check registration."""
        modules_dir = self.root / "src" / "operations" / "modules"
        if not modules_dir.exists():
            return
        
        operations_yaml = self.load_operations_yaml()
        
        # Find all *_module.py files (excluding orchestrators)
        module_files = [
            f for f in modules_dir.rglob("*_module.py")
            if '__pycache__' not in str(f) and 'test_' not in f.name
        ]
        
        for file_path in module_files:
            classes = self.extract_classes(file_path)
            for class_name in classes:
                if 'Module' not in class_name:
                    continue
                
                # Check if linked to operation
                linked = self.check_module_linkage(class_name, file_path, operations_yaml)
                
                self.results['operation_modules'].append({
                    'name': class_name,
                    'file': str(file_path.relative_to(self.root)),
                    'linked_to_operation': linked['linked'],
                    'operation_id': linked.get('operation_id'),
                    'wired': linked['linked']
                })
        
        wired_count = sum(1 for m in self.results['operation_modules'] if m['wired'])
        total = len(self.results['operation_modules'])
        print(f"   Found {total} operation modules, {wired_count} wired ({wired_count/total*100:.1f}%)")
    
    def analyze_setup_modules(self):
        """Analyze setup modules and check registration."""
        modules_dir = self.root / "src" / "setup" / "modules"
        if not modules_dir.exists():
            return
        
        # Load setup_modules.yaml
        setup_yaml_path = self.root / "src" / "setup" / "setup_modules.yaml"
        setup_yaml = {}
        if setup_yaml_path.exists():
            with open(setup_yaml_path) as f:
                setup_yaml = yaml.safe_load(f) or {}
        
        # Load module_factory.py registrations
        factory_path = self.root / "src" / "setup" / "module_factory.py"
        factory_registrations = self.extract_factory_registrations(factory_path)
        
        # Find all module files
        module_files = [
            f for f in modules_dir.glob("*_module.py")
            if '__pycache__' not in str(f) and 'test_' not in f.name
        ]
        
        for file_path in module_files:
            classes = self.extract_classes(file_path)
            for class_name in classes:
                if 'Module' not in class_name or class_name == 'BaseSetupModule':
                    continue
                
                module_id = file_path.stem.replace('_module', '')
                in_yaml = any(
                    m.get('module_id') == module_id 
                    for m in setup_yaml.get('modules', [])
                )
                in_factory = class_name in factory_registrations
                
                self.results['setup_modules'].append({
                    'name': class_name,
                    'file': str(file_path.relative_to(self.root)),
                    'module_id': module_id,
                    'in_setup_yaml': in_yaml,
                    'in_factory': in_factory,
                    'wired': in_yaml and in_factory
                })
        
        wired_count = sum(1 for m in self.results['setup_modules'] if m['wired'])
        total = len(self.results['setup_modules'])
        print(f"   Found {total} setup modules, {wired_count} wired ({wired_count/total*100:.1f}%)")
    
    def analyze_plugins(self):
        """Analyze plugins and check registration.
        
        Plugins are auto-discovered via PluginRegistry.discover_plugins().
        A plugin is considered wired if it has a register() function.
        """
        plugins_dir = self.root / "src" / "plugins"
        if not plugins_dir.exists():
            return
        
        # Find all plugin files
        plugin_files = [
            f for f in plugins_dir.glob("*_plugin.py")
            if '__pycache__' not in str(f) and f.name != 'base_plugin.py' and 'test_' not in f.name
        ]
        
        for file_path in plugin_files:
            classes = self.extract_classes(file_path)
            
            # Check if plugin has register() function (used by auto-discovery)
            has_register = self.check_plugin_has_register(file_path)
            
            for class_name in classes:
                if 'Plugin' not in class_name or class_name == 'BasePlugin':
                    continue
                
                self.results['plugins'].append({
                    'name': class_name,
                    'file': str(file_path.relative_to(self.root)),
                    'has_register_function': has_register,
                    'registered': has_register,  # Auto-discovered if has register()
                    'wired': has_register
                })
        
        wired_count = sum(1 for p in self.results['plugins'] if p['wired'])
        total = len(self.results['plugins'])
        print(f"   Found {total} plugins, {wired_count} wired ({wired_count/total*100:.1f}%)")
    
    def check_plugin_has_register(self, plugin_path: Path) -> bool:
        """Check if plugin file has a register() function for auto-discovery."""
        try:
            with open(plugin_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == 'register':
                    return True
            return False
        except:
            return False
    
    # Helper methods
    
    def extract_classes(self, file_path: Path) -> List[str]:
        """Extract class names from Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        except:
            return []
    
    def load_operations_yaml(self) -> Dict:
        """Load cortex-operations.yaml."""
        yaml_path = self.root / "cortex-operations.yaml"
        if yaml_path.exists():
            with open(yaml_path) as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def load_response_templates(self) -> Dict:
        """Load response-templates-v4.yaml."""
        templates_path = self.root / "cortex-brain" / "response-templates-v4.yaml"
        if templates_path.exists():
            with open(templates_path) as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def check_orchestrator_wiring(self, class_name: str, file_path: Path, 
                                   operations_yaml: Dict, templates: Dict) -> Dict:
        """Check if orchestrator is properly wired."""
        result = {
            'wired': False,
            'in_operations': False,
            'has_template': False,
            'has_triggers': False
        }
        
        # Normalize class name: MasterSetupOrchestrator -> mastersetup
        normalized_class = class_name.lower().replace('orchestrator', '').replace('module', '')
        
        # Check operations YAML
        for op_id, op_def in operations_yaml.get('operations', {}).items():
            modules = op_def.get('modules', [])
            # Normalize module names (remove underscores) for comparison
            for m in modules:
                normalized_module = m.lower().replace('_', '').replace('orchestrator', '').replace('module', '')
                if normalized_class == normalized_module or normalized_class in normalized_module:
                    result['in_operations'] = True
                    result['operation_id'] = op_id
                    result['triggers'] = op_def.get('natural_language', [])
                    result['has_triggers'] = len(result['triggers']) > 0
                    break
            if result['in_operations']:
                break
        
        # Check response templates
        for template_id, template_def in templates.items():
            if isinstance(template_def, dict):
                expected_orch = template_def.get('expected_orchestrator', '')
                if expected_orch == class_name:
                    result['has_template'] = True
                    break
        
        result['wired'] = result['in_operations'] and result['has_triggers']
        return result
    
    def extract_wired_agents(self, executor_path: Path) -> List[str]:
        """Extract wired agent class names from AgentExecutor."""
        wired = []
        if not executor_path.exists():
            return wired
        
        with open(executor_path) as f:
            content = f.read()
            # Look for agent instantiations
            for line in content.split('\n'):
                if 'Agent(' in line and '=' in line and not line.strip().startswith('#'):
                    # Extract agent class name
                    if 'Agent(' in line:
                        agent_name = line.split('Agent(')[0].strip().split()[-1]
                        wired.append(agent_name)
        
        return wired
    
    def extract_agent_types(self, types_path: Path) -> List[str]:
        """Extract AgentType enum values."""
        enums = []
        if not types_path.exists():
            return enums
        
        with open(types_path) as f:
            content = f.read()
            for line in content.split('\n'):
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    enum_name = line.split('=')[0].strip()
                    if enum_name.isupper():
                        enums.append(enum_name)
        
        return enums
    
    def check_module_linkage(self, class_name: str, file_path: Path, 
                            operations_yaml: Dict) -> Dict:
        """Check if module is linked to parent operation."""
        result = {'linked': False}
        
        module_id = file_path.stem.replace('_module', '').replace('_orchestrator', '')
        
        for op_id, op_def in operations_yaml.get('operations', {}).items():
            modules = op_def.get('modules', [])
            if module_id in modules or class_name.lower().replace('module', '') in [m.lower() for m in modules]:
                result['linked'] = True
                result['operation_id'] = op_id
                break
        
        return result
    
    def extract_factory_registrations(self, factory_path: Path) -> List[str]:
        """Extract registered class names from module_factory.py."""
        registered = []
        if not factory_path.exists():
            return registered
        
        with open(factory_path) as f:
            content = f.read()
            for line in content.split('\n'):
                if 'register_module_class(' in line or 'from' in line:
                    # Extract class name from import or registration
                    if 'import' in line:
                        parts = line.split('import')[-1].strip()
                        class_name = parts.split()[0].strip(',')
                        if 'Module' in class_name:
                            registered.append(class_name)
        
        return registered
    
    def extract_plugin_registrations(self, registry_path: Path) -> List[str]:
        """Extract registered plugin class names."""
        registered = []
        if not registry_path.exists():
            return registered
        
        with open(registry_path) as f:
            content = f.read()
            for line in content.split('\n'):
                if 'Plugin' in line and ('import' in line or '=' in line):
                    # Extract class name
                    if 'import' in line:
                        parts = line.split('import')[-1].strip()
                        class_name = parts.split()[0].strip(',')
                        if 'Plugin' in class_name:
                            registered.append(class_name)
        
        return registered
    
    def generate_summary(self):
        """Generate summary statistics."""
        summary = {}
        
        for category in ['orchestrators', 'agents', 'operation_modules', 'setup_modules', 'plugins']:
            items = self.results[category]
            total = len(items)
            wired = sum(1 for item in items if item.get('wired', False))
            unwired = total - wired
            
            summary[category] = {
                'total': total,
                'wired': wired,
                'unwired': unwired,
                'wiring_percentage': round(wired / total * 100, 1) if total > 0 else 0
            }
        
        # Overall
        total_all = sum(s['total'] for s in summary.values())
        wired_all = sum(s['wired'] for s in summary.values())
        
        summary['overall'] = {
            'total_components': total_all,
            'wired_components': wired_all,
            'unwired_components': total_all - wired_all,
            'overall_wiring_percentage': round(wired_all / total_all * 100, 1) if total_all > 0 else 0
        }
        
        self.results['summary'] = summary
    
    def generate_report(self, output_path: Path):
        """Generate markdown report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = output_path / f"unwired-components-analysis-{timestamp}.md"
        
        with open(report_path, 'w') as f:
            f.write(f"# CORTEX Unwired Components Analysis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Author:** Asif Hussain\n\n")
            f.write("---\n\n")
            
            # Executive Summary
            f.write("## 📊 Executive Summary\n\n")
            summary = self.results['summary']
            f.write(f"**Total Components:** {summary['overall']['total_components']}\n\n")
            f.write(f"**Wired:** {summary['overall']['wired_components']} ({summary['overall']['overall_wiring_percentage']}%)\n\n")
            f.write(f"**Unwired:** {summary['overall']['unwired_components']}\n\n")
            
            f.write("### By Category\n\n")
            f.write("| Category | Total | Wired | Unwired | % Wired |\n")
            f.write("|----------|-------|-------|---------|----------|\n")
            for category in ['orchestrators', 'agents', 'operation_modules', 'setup_modules', 'plugins']:
                stats = summary[category]
                f.write(f"| {category.replace('_', ' ').title()} | {stats['total']} | {stats['wired']} | {stats['unwired']} | {stats['wiring_percentage']}% |\n")
            
            # Detailed Findings
            for category in ['orchestrators', 'agents', 'operation_modules', 'setup_modules', 'plugins']:
                f.write(f"\n---\n\n## {category.replace('_', ' ').title()}\n\n")
                
                items = self.results[category]
                unwired = [item for item in items if not item.get('wired', False)]
                wired = [item for item in items if item.get('wired', False)]
                
                f.write(f"### ❌ Unwired ({len(unwired)})\n\n")
                if unwired:
                    for item in unwired:
                        f.write(f"- **{item['name']}**\n")
                        f.write(f"  - File: `{item['file']}`\n")
                        if category == 'orchestrators':
                            f.write(f"  - In operations.yaml: {item['in_operations_yaml']}\n")
                            f.write(f"  - Has response template: {item['has_response_template']}\n")
                            f.write(f"  - Has triggers: {item['has_triggers']}\n")
                        elif category == 'agents':
                            f.write(f"  - Wired in executor: {item['wired_in_executor']}\n")
                            f.write(f"  - Has AgentType enum: {item['has_agent_type_enum']}\n")
                        f.write("\n")
                else:
                    f.write("✅ All components wired!\n\n")
                
                f.write(f"### ✅ Wired ({len(wired)})\n\n")
                if wired:
                    for item in wired[:10]:  # Show first 10
                        f.write(f"- {item['name']}\n")
                    if len(wired) > 10:
                        f.write(f"\n... and {len(wired) - 10} more\n")
                f.write("\n")
            
            # Recommendations
            f.write("---\n\n## 🎯 Remediation Recommendations\n\n")
            f.write("### Priority Levels\n\n")
            f.write("1. **CRITICAL**: User-facing orchestrators without natural language triggers\n")
            f.write("2. **HIGH**: Core agents without executor wiring\n")
            f.write("3. **MEDIUM**: Operation modules not linked to operations\n")
            f.write("4. **LOW**: Setup modules and plugins (internal tooling)\n\n")
            
        print(f"\n📄 Report generated: {report_path}")
        return report_path


def main():
    """Main execution."""
    project_root = Path(__file__).parent.parent
    
    analyzer = UnwiredComponentAnalyzer(project_root)
    results = analyzer.analyze_all()
    
    # Save results
    output_dir = project_root / "cortex-brain" / "documents" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate report
    report_path = analyzer.generate_report(output_dir)
    
    # Save JSON
    json_path = output_dir / f"unwired-components-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"📊 JSON data saved: {json_path}")
    
    print("\n✅ Analysis complete!")
    print(f"\n📈 Overall Wiring: {results['summary']['overall']['overall_wiring_percentage']}%")
    print(f"🔧 Components needing attention: {results['summary']['overall']['unwired_components']}")


if __name__ == "__main__":
    main()
