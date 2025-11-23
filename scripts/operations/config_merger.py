"""
CORTEX Config Merger Module

Implements 3-way merge algorithm for YAML configuration files.
Preserves user customizations while adding new features from upgrades.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import json


class ConfigMerger:
    """Intelligently merges YAML configuration files during upgrades."""
    
    def __init__(self):
        """Initialize config merger."""
        self.conflicts = []
        
    def merge_yaml_files(
        self,
        base_file: Path,
        local_file: Path,
        upgrade_file: Path,
        output_file: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Perform 3-way merge of YAML files.
        
        Args:
            base_file: Original CORTEX version (e.g., v5.2.0)
            local_file: User's current version (with customizations)
            upgrade_file: New CORTEX version (e.g., v5.3.0)
            output_file: Where to save merged result (or None to return only)
            
        Returns:
            Merged dictionary
        """
        print(f"🔀 Merging configuration files...")
        print(f"   Base: {base_file.name}")
        print(f"   Local: {local_file.name}")
        print(f"   Upgrade: {upgrade_file.name}")
        
        # Load YAML files
        base_data = self._load_yaml(base_file)
        local_data = self._load_yaml(local_file)
        upgrade_data = self._load_yaml(upgrade_file)
        
        # Perform 3-way merge
        merged_data = self._three_way_merge(base_data, local_data, upgrade_data)
        
        # Save if output path provided
        if output_file:
            self._save_yaml(output_file, merged_data)
            print(f"✅ Merged configuration saved to {output_file}")
        
        # Report conflicts
        if self.conflicts:
            print(f"\n⚠️  {len(self.conflicts)} conflicts detected:")
            for conflict in self.conflicts:
                print(f"   • {conflict}")
        
        return merged_data
    
    def merge_response_templates(
        self,
        local_file: Path,
        upgrade_file: Path,
        output_file: Path
    ) -> Dict[str, Any]:
        """
        Merge response-templates.yaml with special handling for template arrays.
        
        Args:
            local_file: User's current templates
            upgrade_file: New templates from upgrade
            output_file: Where to save merged result
            
        Returns:
            Merged templates dictionary
        """
        print(f"📝 Merging response templates...")
        
        local_data = self._load_yaml(local_file)
        upgrade_data = self._load_yaml(upgrade_file)
        
        # Start with upgrade data (new templates)
        merged_data = upgrade_data.copy()
        
        # Add user-created templates (not in upgrade)
        local_templates = local_data.get('templates', [])
        upgrade_templates = upgrade_data.get('templates', [])
        
        # Build set of upgrade template IDs
        upgrade_template_ids = {t.get('id') for t in upgrade_templates if 'id' in t}
        
        # Add user templates that don't conflict
        for template in local_templates:
            template_id = template.get('id')
            if template_id and template_id not in upgrade_template_ids:
                if 'templates' not in merged_data:
                    merged_data['templates'] = []
                merged_data['templates'].append(template)
                print(f"   ✅ Preserved custom template: {template_id}")
        
        self._save_yaml(output_file, merged_data)
        print(f"✅ Templates merged: {len(merged_data.get('templates', []))} total templates")
        
        return merged_data
    
    def merge_capabilities(
        self,
        local_file: Path,
        upgrade_file: Path,
        output_file: Path
    ) -> Dict[str, Any]:
        """
        Merge capabilities.yaml with special handling for operation arrays.
        
        Args:
            local_file: User's current capabilities
            upgrade_file: New capabilities from upgrade
            output_file: Where to save merged result
            
        Returns:
            Merged capabilities dictionary
        """
        print(f"⚙️  Merging capabilities...")
        
        local_data = self._load_yaml(local_file)
        upgrade_data = self._load_yaml(upgrade_file)
        
        # Start with upgrade data (new capabilities)
        merged_data = upgrade_data.copy()
        
        # Add user-created operations
        local_ops = local_data.get('operations', [])
        upgrade_ops = upgrade_data.get('operations', [])
        
        # Build set of upgrade operation names
        upgrade_op_names = {op.get('name') for op in upgrade_ops if 'name' in op}
        
        # Add user operations that don't conflict
        for operation in local_ops:
            op_name = operation.get('name')
            if op_name and op_name not in upgrade_op_names:
                if 'operations' not in merged_data:
                    merged_data['operations'] = []
                merged_data['operations'].append(operation)
                print(f"   ✅ Preserved custom operation: {op_name}")
        
        self._save_yaml(output_file, merged_data)
        print(f"✅ Capabilities merged: {len(merged_data.get('operations', []))} total operations")
        
        return merged_data
    
    def detect_conflicts(
        self,
        base_data: Dict,
        local_data: Dict,
        upgrade_data: Dict
    ) -> List[str]:
        """
        Detect merge conflicts.
        
        Args:
            base_data: Original data
            local_data: User's modifications
            upgrade_data: New version data
            
        Returns:
            List of conflict descriptions
        """
        conflicts = []
        
        def check_key(key_path: str, base_val: Any, local_val: Any, upgrade_val: Any):
            """Recursively check for conflicts."""
            # Both modified from base
            if local_val != base_val and upgrade_val != base_val and local_val != upgrade_val:
                conflicts.append(
                    f"{key_path}: User changed to '{local_val}', upgrade changed to '{upgrade_val}'"
                )
        
        # Simple flat comparison (can be made recursive for nested dicts)
        all_keys = set(base_data.keys()) | set(local_data.keys()) | set(upgrade_data.keys())
        
        for key in all_keys:
            base_val = base_data.get(key)
            local_val = local_data.get(key)
            upgrade_val = upgrade_data.get(key)
            
            if isinstance(base_val, dict) and isinstance(local_val, dict) and isinstance(upgrade_val, dict):
                # Recursive check for nested dicts
                nested_conflicts = self.detect_conflicts(base_val, local_val, upgrade_val)
                conflicts.extend([f"{key}.{c}" for c in nested_conflicts])
            else:
                check_key(key, base_val, local_val, upgrade_val)
        
        return conflicts
    
    def _three_way_merge(
        self,
        base: Dict,
        local: Dict,
        upgrade: Dict
    ) -> Dict:
        """
        Perform 3-way merge algorithm.
        
        Strategy:
        - If only local changed: use local
        - If only upgrade changed: use upgrade
        - If both changed and same: use either
        - If both changed differently: conflict (prefer upgrade, log conflict)
        
        Args:
            base: Original version
            local: User's version
            upgrade: New version
            
        Returns:
            Merged dictionary
        """
        merged = {}
        all_keys = set(base.keys()) | set(local.keys()) | set(upgrade.keys())
        
        for key in all_keys:
            base_val = base.get(key)
            local_val = local.get(key)
            upgrade_val = upgrade.get(key)
            
            # Key only in base (removed by both)
            if key not in local and key not in upgrade:
                continue
            
            # Key only in local (user addition)
            if key not in base and key not in upgrade:
                merged[key] = local_val
                continue
            
            # Key only in upgrade (new feature)
            if key not in base and key not in local:
                merged[key] = upgrade_val
                continue
            
            # Key in all three - analyze changes
            if isinstance(base_val, dict) and isinstance(local_val, dict) and isinstance(upgrade_val, dict):
                # Recursive merge for nested dicts
                merged[key] = self._three_way_merge(base_val, local_val, upgrade_val)
            elif local_val == base_val:
                # Only upgrade changed
                merged[key] = upgrade_val
            elif upgrade_val == base_val:
                # Only local changed
                merged[key] = local_val
            elif local_val == upgrade_val:
                # Both changed to same value
                merged[key] = local_val
            else:
                # Conflict: both changed differently
                self.conflicts.append(f"{key}: local='{local_val}' vs upgrade='{upgrade_val}'")
                # Prefer upgrade version (new features)
                merged[key] = upgrade_val
        
        return merged
    
    def _load_yaml(self, file_path: Path) -> Dict:
        """Load YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if data else {}
        except FileNotFoundError:
            print(f"   ⚠️  File not found: {file_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"   ❌ YAML parse error in {file_path}: {e}")
            return {}
    
    def _save_yaml(self, file_path: Path, data: Dict) -> None:
        """Save YAML file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                indent=2
            )
    
    def generate_merge_report(self, output_file: Path) -> None:
        """
        Generate detailed merge report.
        
        Args:
            output_file: Where to save the report
        """
        report = {
            "merge_date": datetime.now().isoformat(),
            "conflicts_count": len(self.conflicts),
            "conflicts": self.conflicts,
            "resolution": "Conflicts resolved by preferring upgrade version (new features)"
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"📋 Merge report saved to {output_file}")


def main():
    """CLI entry point for testing config merger."""
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python config_merger.py <base_file> <local_file> <upgrade_file> [output_file]")
        print("\nExample:")
        print("  python config_merger.py base.yaml local.yaml upgrade.yaml merged.yaml")
        sys.exit(1)
    
    base_file = Path(sys.argv[1])
    local_file = Path(sys.argv[2])
    upgrade_file = Path(sys.argv[3])
    output_file = Path(sys.argv[4]) if len(sys.argv) > 4 else None
    
    merger = ConfigMerger()
    merged_data = merger.merge_yaml_files(base_file, local_file, upgrade_file, output_file)
    
    print(f"\n✅ Merge complete")
    print(f"   Conflicts: {len(merger.conflicts)}")
    
    if not output_file:
        print(f"\nMerged data preview:")
        print(yaml.dump(merged_data, default_flow_style=False, indent=2))


if __name__ == "__main__":
    main()
