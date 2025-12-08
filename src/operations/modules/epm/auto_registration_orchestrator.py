"""
Auto-Registration Orchestrator for Discovered Features

Automatically registers discovered orchestrators in cortex-operations.yaml:
- Extracts metadata from discovered features
- Generates natural language triggers from docstrings
- Creates properly formatted YAML entries
- Supports dry-run mode for preview
- Approval workflow for safety

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class RegistrationEntry:
    """YAML entry for operation registration"""
    operation_name: str
    display_name: str
    deployment_tier: str
    category: str
    natural_language: List[str]
    modules: List[str]
    description: str
    version: str = "1.0.0"
    author: str = "Asif Hussain"


class AutoRegistrationOrchestrator:
    """Orchestrates automatic registration of discovered features"""
    
    def __init__(self, project_root: Path = None):
        """
        Initialize orchestrator
        
        Args:
            project_root: CORTEX project root
        """
        self.project_root = project_root or Path.cwd()
        self.operations_yaml = self.project_root / "cortex-operations.yaml"
        
        if not self.operations_yaml.exists():
            raise FileNotFoundError(f"cortex-operations.yaml not found at {self.operations_yaml}")
    
    def extract_natural_language_triggers(self, docstring: str, operation_name: str) -> List[str]:
        """
        Extract natural language triggers from docstring
        
        Args:
            docstring: Operation docstring
            operation_name: Operation name (e.g., "brain_tuning")
        
        Returns:
            List of natural language trigger phrases
        """
        triggers = []
        
        # Base trigger from operation name
        base_trigger = operation_name.replace('_', ' ')
        triggers.append(base_trigger)
        
        if not docstring:
            return triggers
        
        # Look for command patterns in docstring
        command_patterns = [
            r'Commands?:\s*\n((?:[-*]\s*.+\n?)+)',
            r'Usage:\s*`([^`]+)`',
            r'Triggers?:\s*\n((?:[-*]\s*.+\n?)+)',
        ]
        
        for pattern in command_patterns:
            matches = re.findall(pattern, docstring, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                # Extract commands from bullet lists
                lines = match.strip().split('\n')
                for line in lines:
                    cmd = re.sub(r'^[-*]\s*', '', line).strip()
                    cmd = cmd.strip('`"\'')
                    if cmd and len(cmd.split()) <= 5 and cmd not in triggers:
                        triggers.append(cmd.lower())
        
        # Add verb variations
        verbs = ['run', 'start', 'execute', 'perform', 'do']
        for verb in verbs:
            variant = f"{verb} {base_trigger}"
            if variant not in triggers:
                triggers.append(variant)
        
        return triggers[:5]  # Top 5
    
    def infer_deployment_tier(self, module_path: str, docstring: str) -> str:
        """
        Infer deployment tier from module path and docstring
        
        Args:
            module_path: Module path (e.g., "src.operations.modules.brain...")
            docstring: Operation docstring
        
        Returns:
            'user', 'dual', or 'admin'
        """
        # Admin indicators
        if 'admin' in module_path.lower():
            return 'admin'
        
        admin_keywords = ['deploy', 'publish', 'generate docs', 'alignment']
        if docstring and any(kw in docstring.lower() for kw in admin_keywords):
            return 'admin'
        
        # Dual context indicators
        dual_keywords = ['ado', 'azure devops', 'work item', 'architecture review']
        if docstring and any(kw in docstring.lower() for kw in dual_keywords):
            return 'dual'
        
        # Default to user
        return 'user'
    
    def infer_category(self, operation_name: str, module_path: str) -> str:
        """
        Infer category from operation name and module path
        
        Args:
            operation_name: Operation name
            module_path: Module path
        
        Returns:
            Category name
        """
        categories = {
            'planning': ['plan', 'feature', 'ado', 'work_item'],
            'development': ['tdd', 'test', 'debug', 'develop'],
            'git': ['commit', 'checkpoint', 'push', 'pull', 'git'],
            'review': ['review', 'pr', 'code_review', 'architectural'],
            'analysis': ['analyze', 'health', 'rca', 'lint'],
            'deployment': ['deploy', 'release', 'publish'],
            'maintenance': ['cleanup', 'optimize', 'tune', 'maintenance'],
            'brain': ['brain', 'memory', 'knowledge'],
            'dashboard': ['dashboard', 'report', 'metrics'],
            'system': ['system', 'healthcheck', 'status']
        }
        
        operation_lower = operation_name.lower()
        module_lower = module_path.lower()
        
        for category, keywords in categories.items():
            if any(kw in operation_lower or kw in module_lower for kw in keywords):
                return category
        
        return 'general'
    
    def generate_registration_entry(self, discovered_feature: Dict) -> RegistrationEntry:
        """
        Generate registration entry from discovered feature
        
        Args:
            discovered_feature: Feature dict from OrchestratorScanner
        
        Returns:
            RegistrationEntry ready for YAML
        """
        class_name = discovered_feature['class_name']
        operation_name = discovered_feature['operation_name']
        module_path = discovered_feature['module_path']
        docstring = discovered_feature.get('docstring', '')
        
        # Extract metadata
        display_name = self._class_to_display_name(class_name)
        triggers = self.extract_natural_language_triggers(docstring, operation_name)
        tier = self.infer_deployment_tier(module_path, docstring)
        category = self.infer_category(operation_name, module_path)
        
        # Extract description (first line of docstring)
        description = docstring.split('\n')[0].strip() if docstring else f"{display_name} operation"
        
        # Module path for registration
        modules = [module_path.replace('src.', '')]
        
        return RegistrationEntry(
            operation_name=operation_name,
            display_name=display_name,
            deployment_tier=tier,
            category=category,
            natural_language=triggers,
            modules=modules,
            description=description
        )
    
    def _class_to_display_name(self, class_name: str) -> str:
        """Convert ClassNameOrchestrator to Display Name"""
        # Remove 'Orchestrator' suffix
        name = class_name.replace('Orchestrator', '')
        
        # Split CamelCase and join with spaces
        words = re.findall(r'[A-Z][a-z]*', name)
        return ' '.join(words)
    
    def format_yaml_entry(self, entry: RegistrationEntry) -> str:
        """
        Format registration entry as YAML string
        
        Args:
            entry: RegistrationEntry to format
        
        Returns:
            Formatted YAML string
        """
        yaml_dict = {
            entry.operation_name: {
                'name': entry.display_name,
                'deployment_tier': entry.deployment_tier,
                'category': entry.category,
                'natural_language': entry.natural_language,
                'modules': entry.modules,
                'description': entry.description,
                'version': entry.version,
                'author': entry.author,
                'auto_registered': datetime.now().strftime('%Y-%m-%d')
            }
        }
        
        return yaml.dump(yaml_dict, default_flow_style=False, sort_keys=False)
    
    def register_features(
        self, 
        unregistered_features: List[Dict],
        dry_run: bool = True,
        require_approval: bool = True
    ) -> Dict:
        """
        Register unregistered features in cortex-operations.yaml
        
        Args:
            unregistered_features: List of discovered features to register
            dry_run: If True, only preview without writing
            require_approval: If True, ask for user approval
        
        Returns:
            Registration result summary
        """
        print(f"\n[AUTO-REGISTER] Processing {len(unregistered_features)} features...")
        
        # Generate entries
        entries = []
        for feature in unregistered_features:
            entry = self.generate_registration_entry(feature)
            entries.append(entry)
        
        # Preview
        print("\n[PREVIEW] Generated YAML Entries:")
        print("=" * 60)
        for entry in entries:
            print(f"\n{entry.operation_name}:")
            print(f"  Display Name: {entry.display_name}")
            print(f"  Tier: {entry.deployment_tier}")
            print(f"  Category: {entry.category}")
            print(f"  Triggers: {', '.join(entry.natural_language[:3])}")
        
        if dry_run:
            print("\n[DRY RUN] No changes made")
            return {
                "success": True,
                "dry_run": True,
                "entries_generated": len(entries),
                "entries": [entry.__dict__ for entry in entries]
            }
        
        # Approval
        if require_approval:
            print("\n[APPROVAL] Register these features? (yes/no): ", end='')
            response = input().strip().lower()
            if response not in ['yes', 'y']:
                print("[CANCELLED] Registration cancelled by user")
                return {
                    "success": False,
                    "cancelled": True,
                    "reason": "User declined approval"
                }
        
        # Load existing operations
        with open(self.operations_yaml, 'r') as f:
            operations = yaml.safe_load(f) or {}
        
        # Add new entries
        registered_count = 0
        for entry in entries:
            if entry.operation_name not in operations:
                operations[entry.operation_name] = {
                    'name': entry.display_name,
                    'deployment_tier': entry.deployment_tier,
                    'category': entry.category,
                    'natural_language': entry.natural_language,
                    'modules': entry.modules,
                    'description': entry.description,
                    'version': entry.version,
                    'author': entry.author,
                    'auto_registered': datetime.now().strftime('%Y-%m-%d')
                }
                registered_count += 1
        
        # Backup original
        backup_path = self.operations_yaml.with_suffix('.yaml.backup')
        with open(self.operations_yaml, 'r') as src:
            with open(backup_path, 'w') as dst:
                dst.write(src.read())
        
        # Write updated YAML
        with open(self.operations_yaml, 'w') as f:
            yaml.dump(operations, f, default_flow_style=False, sort_keys=False)
        
        print(f"\n[SUCCESS] Registered {registered_count} features")
        print(f"[BACKUP] Original saved to {backup_path}")
        
        return {
            "success": True,
            "registered_count": registered_count,
            "backup_path": str(backup_path),
            "entries": [entry.__dict__ for entry in entries]
        }


def main():
    """Entry point for testing"""
    import json
    from src.discovery.orchestrator_scanner import OrchestratorScanner
    
    # Discover features
    project_root = Path.cwd()
    scanner = OrchestratorScanner(project_root)
    orchestrators = scanner.discover()
    
    # Load existing operations
    operations_yaml = project_root / "cortex-operations.yaml"
    with open(operations_yaml, 'r') as f:
        existing_ops = yaml.safe_load(f) or {}
    
    # Find unregistered
    unregistered = []
    for orch_name, orch_info in orchestrators.items():
        # Convert to operation name
        op_name = orch_name.replace('Orchestrator', '')
        op_name = re.sub(r'(?<!^)(?=[A-Z])', '_', op_name).lower()
        
        if op_name not in existing_ops:
            unregistered.append({
                'class_name': orch_name,
                'operation_name': op_name,
                'path': str(orch_info['path']),
                'module_path': orch_info['module_path'],
                'docstring': orch_info.get('docstring', '')
            })
    
    print(f"Found {len(unregistered)} unregistered features")
    
    # Test registration
    orchestrator = AutoRegistrationOrchestrator(project_root)
    result = orchestrator.register_features(
        unregistered[:3],  # Test with first 3
        dry_run=True
    )
    
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
