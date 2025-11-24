"""
CORTEX Capability Discovery Engine
Scans codebase to automatically discover features, modules, operations, and capabilities.
"""

import os
import ast
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Set
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Capability:
    """Represents a discovered CORTEX capability"""
    name: str
    type: str  # operation, module, plugin, agent, tier
    description: str
    status: str  # active, deprecated, planned
    files: List[str] = field(default_factory=list)
    git_added: str = None  # Date when feature was added
    git_modified: str = None  # Last modification date
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CapabilityScanner:
    """Scans CORTEX codebase to discover capabilities"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.capabilities: Dict[str, Capability] = {}
        
    def scan_all(self) -> Dict[str, Capability]:
        """Run all scanning methods and return comprehensive capability registry"""
        print("🔍 Starting CORTEX capability discovery...")
        
        # Scan different sources
        self.scan_yaml_configs()
        self.scan_source_code()
        self.scan_plugins()
        self.scan_agents()
        self.enrich_with_git_history()
        
        print(f"✅ Discovered {len(self.capabilities)} capabilities")
        return self.capabilities
    
    def scan_yaml_configs(self):
        """Scan YAML config files for operations, modules, capabilities"""
        print("📄 Scanning YAML configurations...")
        
        yaml_files = [
            'cortex-brain/cortex-operations.yaml',
            'cortex-brain/module-definitions.yaml',
            'cortex-brain/capabilities.yaml',
            'cortex-operations.yaml'
        ]
        
        for yaml_path in yaml_files:
            full_path = self.workspace_root / yaml_path
            if not full_path.exists():
                continue
                
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    
                if 'operations' in yaml_path:
                    self._parse_operations(data)
                elif 'module-definitions' in yaml_path:
                    self._parse_modules(data)
                elif 'capabilities' in yaml_path:
                    self._parse_capabilities(data)
                    
            except Exception as e:
                print(f"⚠️  Could not parse {yaml_path}: {e}")
    
    def _parse_operations(self, data: Dict):
        """Extract operations from operations YAML"""
        if not data or 'operations' not in data:
            return
            
        for op_name, op_data in data.get('operations', {}).items():
            capability = Capability(
                name=op_name,
                type='operation',
                description=op_data.get('description', ''),
                status=op_data.get('status', 'active'),
                metadata={
                    'category': op_data.get('category', ''),
                    'agents': op_data.get('agents', []),
                    'trigger_patterns': op_data.get('trigger_patterns', [])
                }
            )
            self.capabilities[f"operation:{op_name}"] = capability
    
    def _parse_modules(self, data: Dict):
        """Extract modules from module definitions"""
        if not data or 'modules' not in data:
            return
            
        for mod_name, mod_data in data.get('modules', {}).items():
            capability = Capability(
                name=mod_name,
                type='module',
                description=mod_data.get('description', ''),
                status=mod_data.get('status', 'active'),
                metadata={
                    'tier': mod_data.get('tier', ''),
                    'dependencies': mod_data.get('dependencies', []),
                    'exports': mod_data.get('exports', [])
                }
            )
            self.capabilities[f"module:{mod_name}"] = capability
    
    def _parse_capabilities(self, data: Dict):
        """Extract high-level capabilities"""
        if not data:
            return
            
        for category, items in data.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        capability = Capability(
                            name=item.get('name', ''),
                            type='capability',
                            description=item.get('description', ''),
                            status=item.get('status', 'active'),
                            metadata={'category': category}
                        )
                        self.capabilities[f"capability:{item.get('name', '')}"] = capability
    
    def scan_source_code(self):
        """Scan Python source code for classes, functions, and features"""
        print("🐍 Scanning Python source code...")
        
        src_path = self.workspace_root / 'src'
        if not src_path.exists():
            return
        
        for py_file in src_path.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    self._analyze_ast(tree, py_file)
            except Exception as e:
                print(f"⚠️  Could not parse {py_file}: {e}")
    
    def _analyze_ast(self, tree: ast.AST, file_path: Path):
        """Analyze Python AST for capabilities"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's an agent, plugin, or core component
                class_name = node.name
                docstring = ast.get_docstring(node)
                
                if 'Agent' in class_name or 'Plugin' in class_name:
                    capability_type = 'agent' if 'Agent' in class_name else 'plugin'
                    key = f"{capability_type}:{class_name}"
                    
                    if key not in self.capabilities:
                        self.capabilities[key] = Capability(
                            name=class_name,
                            type=capability_type,
                            description=docstring or f"{class_name} implementation",
                            status='active',
                            files=[str(file_path.relative_to(self.workspace_root))]
                        )
    
    def scan_plugins(self):
        """Scan plugins directory for plugin capabilities"""
        print("🔌 Scanning plugins...")
        
        plugins_path = self.workspace_root / 'src' / 'plugins'
        if not plugins_path.exists():
            return
        
        for plugin_file in plugins_path.glob('*.py'):
            if plugin_file.stem == '__init__':
                continue
                
            try:
                with open(plugin_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and 'Plugin' in node.name:
                            key = f"plugin:{node.name}"
                            if key not in self.capabilities:
                                self.capabilities[key] = Capability(
                                    name=node.name,
                                    type='plugin',
                                    description=ast.get_docstring(node) or f"{node.name} plugin",
                                    status='active',
                                    files=[str(plugin_file.relative_to(self.workspace_root))]
                                )
            except Exception as e:
                print(f"⚠️  Could not parse plugin {plugin_file}: {e}")
    
    def scan_agents(self):
        """Scan agents directory for agent capabilities"""
        print("🤖 Scanning agents...")
        
        agents_path = self.workspace_root / 'src' / 'agents'
        if not agents_path.exists():
            return
        
        for agent_file in agents_path.glob('*.py'):
            if agent_file.stem == '__init__':
                continue
                
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and 'Agent' in node.name:
                            key = f"agent:{node.name}"
                            if key not in self.capabilities:
                                self.capabilities[key] = Capability(
                                    name=node.name,
                                    type='agent',
                                    description=ast.get_docstring(node) or f"{node.name} agent",
                                    status='active',
                                    files=[str(agent_file.relative_to(self.workspace_root))]
                                )
            except Exception as e:
                print(f"⚠️  Could not parse agent {agent_file}: {e}")
    
    def enrich_with_git_history(self):
        """Use git history to determine when features were added/modified"""
        print("📜 Enriching with git history...")
        
        for key, capability in self.capabilities.items():
            if not capability.files:
                continue
            
            try:
                # Get first commit (when feature was added)
                file_path = capability.files[0]
                result = subprocess.run(
                    ['git', 'log', '--diff-filter=A', '--format=%ad', '--date=short', '--', file_path],
                    capture_output=True,
                    text=True,
                    cwd=self.workspace_root,
                    timeout=5
                )
                
                if result.stdout.strip():
                    capability.git_added = result.stdout.strip().split('\n')[-1]
                
                # Get last modification date
                result = subprocess.run(
                    ['git', 'log', '-1', '--format=%ad', '--date=short', '--', file_path],
                    capture_output=True,
                    text=True,
                    cwd=self.workspace_root,
                    timeout=5
                )
                
                if result.stdout.strip():
                    capability.git_modified = result.stdout.strip()
                    
            except Exception as e:
                # Git history enrichment is optional - don't fail if it doesn't work
                pass
    
    def get_new_capabilities(self, since_date: str = None) -> List[Capability]:
        """Get capabilities added since a specific date"""
        if not since_date:
            # Default to last 30 days
            from datetime import datetime, timedelta
            since_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        new_caps = []
        for cap in self.capabilities.values():
            if cap.git_added and cap.git_added >= since_date:
                new_caps.append(cap)
        
        return sorted(new_caps, key=lambda x: x.git_added or '', reverse=True)
    
    def get_by_type(self, capability_type: str) -> List[Capability]:
        """Get all capabilities of a specific type"""
        return [cap for cap in self.capabilities.values() if cap.type == capability_type]
    
    def export_registry(self, output_path: str):
        """Export capability registry to JSON for use by generators"""
        import json
        
        registry_data = {
            'generated_at': datetime.now().isoformat(),
            'total_capabilities': len(self.capabilities),
            'by_type': {},
            'capabilities': {}
        }
        
        # Count by type
        for cap in self.capabilities.values():
            registry_data['by_type'][cap.type] = registry_data['by_type'].get(cap.type, 0) + 1
        
        # Export all capabilities
        for key, cap in self.capabilities.items():
            registry_data['capabilities'][key] = {
                'name': cap.name,
                'type': cap.type,
                'description': cap.description,
                'status': cap.status,
                'files': cap.files,
                'git_added': cap.git_added,
                'git_modified': cap.git_modified,
                'dependencies': cap.dependencies,
                'metadata': cap.metadata
            }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(registry_data, f, indent=2)
        
        print(f"✅ Exported capability registry to {output_path}")
        return registry_data


if __name__ == '__main__':
    import sys
    
    workspace = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    scanner = CapabilityScanner(workspace)
    capabilities = scanner.scan_all()
    
    # Export to JSON
    scanner.export_registry('cortex-brain/documents/analysis/capability-registry.json')
    
    # Print summary
    print(f"\n📊 Capability Summary:")
    print(f"   Total: {len(capabilities)}")
    for cap_type in ['operation', 'module', 'plugin', 'agent', 'capability']:
        count = len(scanner.get_by_type(cap_type))
        print(f"   {cap_type.capitalize()}s: {count}")
