"""
Manifest Inheritance Resolver
Resolves inheritance chains and merges parent/child manifests

Purpose: Enable manifest inheritance to eliminate 60%+ redundancy
Strategy: child_overrides_parent with deep merge for dicts, append for lists

Author: Asif Hussain
Created: 2025-12-22 (Week 15 Day 2)
Version: 1.0.0
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from copy import deepcopy


class ManifestInheritanceResolver:
    """
    Resolves manifest inheritance chains and merges parent/child manifests.
    
    Supports:
    - Multi-level inheritance (Tier 1 → Tier 2 → Tier 3)
    - child_overrides_parent merge strategy
    - Deep merge for dictionaries
    - Append for lists (configurable)
    - Circular dependency detection
    """
    
    def __init__(self, manifest_base_dir: Path):
        """
        Initialize resolver with base directory for manifests.
        
        Args:
            manifest_base_dir: Base directory containing manifests
        """
        self.manifest_base_dir = Path(manifest_base_dir)
        self.loaded_manifests: Dict[str, Dict[str, Any]] = {}
        self.inheritance_chain: List[str] = []
    
    def resolve(self, manifest_path: str) -> Dict[str, Any]:
        """
        Resolve manifest with full inheritance chain.
        
        Args:
            manifest_path: Relative path to manifest file
            
        Returns:
            Fully resolved manifest with all inheritance merged
            
        Raises:
            FileNotFoundError: If manifest file doesn't exist
            ValueError: If circular inheritance detected
        """
        self.inheritance_chain = []
        self.loaded_manifests = {}
        
        return self._resolve_recursive(manifest_path)
    
    def _resolve_recursive(self, manifest_path: str) -> Dict[str, Any]:
        """
        Recursively resolve inheritance chain.
        
        Args:
            manifest_path: Relative path to manifest file
            
        Returns:
            Resolved manifest at this level
        """
        # Check for circular inheritance
        if manifest_path in self.inheritance_chain:
            raise ValueError(
                f"Circular inheritance detected: {' → '.join(self.inheritance_chain + [manifest_path])}"
            )
        
        # Check cache
        if manifest_path in self.loaded_manifests:
            return deepcopy(self.loaded_manifests[manifest_path])
        
        # Add to chain
        self.inheritance_chain.append(manifest_path)
        
        # Load manifest file
        manifest = self._load_manifest_file(manifest_path)
        
        # Check if this manifest inherits from another
        if "inherits_from" in manifest:
            parent_path = manifest["inherits_from"]
            
            # Resolve relative paths
            if not parent_path.startswith("shared/") and not Path(parent_path).is_absolute():
                parent_dir = Path(manifest_path).parent
                parent_path = str(parent_dir / parent_path)
            
            # Recursively resolve parent
            parent_manifest = self._resolve_recursive(parent_path)
            
            # Merge parent and child
            resolved = self._merge_manifests(parent_manifest, manifest)
        else:
            # No parent, this is the resolved manifest
            resolved = manifest
        
        # Cache result
        self.loaded_manifests[manifest_path] = deepcopy(resolved)
        
        # Remove from chain
        self.inheritance_chain.pop()
        
        return resolved
    
    def _load_manifest_file(self, manifest_path: str) -> Dict[str, Any]:
        """
        Load manifest YAML file.
        
        Args:
            manifest_path: Relative or absolute path to manifest
            
        Returns:
            Parsed YAML as dictionary
        """
        # Try as relative path first
        full_path = self.manifest_base_dir / manifest_path
        
        if not full_path.exists():
            # Try absolute path
            full_path = Path(manifest_path)
        
        if not full_path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            try:
                manifest = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in {manifest_path}: {e}")
        
        return manifest or {}
    
    def _merge_manifests(self, parent: Dict[str, Any], child: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge parent and child manifests with child_overrides_parent strategy.
        
        Rules:
        - Scalars: Child overrides parent
        - Dicts: Deep merge (recursive)
        - Lists: Append child to parent (configurable)
        
        Args:
            parent: Parent manifest
            child: Child manifest
            
        Returns:
            Merged manifest
        """
        merged = deepcopy(parent)
        
        for key, child_value in child.items():
            # Special handling for inherits_from (don't copy to merged)
            if key == "inherits_from":
                continue
            
            if key not in merged:
                # New key from child
                merged[key] = deepcopy(child_value)
            else:
                parent_value = merged[key]
                
                # Determine merge strategy
                if isinstance(parent_value, dict) and isinstance(child_value, dict):
                    # Deep merge dictionaries
                    merged[key] = self._merge_dicts(parent_value, child_value)
                elif isinstance(parent_value, list) and isinstance(child_value, list):
                    # Merge lists based on configuration
                    merged[key] = self._merge_lists(parent_value, child_value, key)
                else:
                    # Child overrides parent (scalars or type mismatch)
                    merged[key] = deepcopy(child_value)
        
        return merged
    
    def _merge_dicts(self, parent_dict: Dict[str, Any], child_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            parent_dict: Parent dictionary
            child_dict: Child dictionary
            
        Returns:
            Merged dictionary
        """
        merged = deepcopy(parent_dict)
        
        for key, child_value in child_dict.items():
            if key not in merged:
                merged[key] = deepcopy(child_value)
            else:
                parent_value = merged[key]
                
                if isinstance(parent_value, dict) and isinstance(child_value, dict):
                    # Recursive deep merge
                    merged[key] = self._merge_dicts(parent_value, child_value)
                elif isinstance(parent_value, list) and isinstance(child_value, list):
                    # Merge lists
                    merged[key] = self._merge_lists(parent_value, child_value, key)
                else:
                    # Child overrides
                    merged[key] = deepcopy(child_value)
        
        return merged
    
    def _merge_lists(self, parent_list: List[Any], child_list: List[Any], key: str) -> List[Any]:
        """
        Merge two lists based on configuration.
        
        Strategy determined by extensibility.merge_lists setting:
        - "append": Append child to parent (default)
        - "replace": Child replaces parent
        - "merge": Merge by unique values
        
        Args:
            parent_list: Parent list
            child_list: Child list
            key: Key name (for context-specific merging)
            
        Returns:
            Merged list
        """
        # Context-specific merging rules
        
        # For related_orchestrators, append unique
        if key in ["related_orchestrators", "capabilities"]:
            merged = list(parent_list)
            for item in child_list:
                if item not in merged:
                    merged.append(item)
            return merged
        
        # For phases, requirements, quality_gates: replace (child defines its own)
        if key in ["phases", "requirements", "quality_gates", "integrations"]:
            return deepcopy(child_list)
        
        # Default: append
        return list(parent_list) + list(child_list)
    
    def get_inheritance_chain(self, manifest_path: str) -> List[str]:
        """
        Get inheritance chain for a manifest without full resolution.
        
        Args:
            manifest_path: Relative path to manifest
            
        Returns:
            List of manifest paths in inheritance chain (root → leaf)
        """
        chain = []
        current_path = manifest_path
        visited = set()
        
        while current_path:
            # Prevent infinite loops
            if current_path in visited:
                break
            visited.add(current_path)
            
            chain.append(current_path)
            
            # Load manifest
            try:
                manifest = self._load_manifest_file(current_path)
            except (FileNotFoundError, ValueError):
                break
            
            # Check for parent
            if "inherits_from" not in manifest:
                break
            
            parent_path = manifest["inherits_from"]
            
            # Resolve relative paths based on current file's location
            if not Path(parent_path).is_absolute():
                current_dir = Path(current_path).parent
                # Resolve parent relative to current file's directory
                resolved_parent = (self.manifest_base_dir / current_dir / parent_path)
                
                # Make it relative to base_dir
                try:
                    parent_path = str(resolved_parent.relative_to(self.manifest_base_dir))
                except ValueError:
                    # Already absolute or outside base_dir
                    pass
            
            current_path = parent_path
        
        # Reverse to get root → leaf order
        return list(reversed(chain))
    
    def validate_manifest(self, manifest: Dict[str, Any]) -> List[str]:
        """
        Validate resolved manifest for required fields.
        
        Args:
            manifest: Resolved manifest dictionary
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required top-level fields
        if "schema_version" not in manifest:
            errors.append("Missing required field: schema_version")
        
        if "metadata" not in manifest:
            errors.append("Missing required field: metadata")
            return errors  # Can't validate metadata fields
        
        metadata = manifest["metadata"]
        
        # Check required metadata fields
        required_metadata = [
            "orchestrator_name",
            "version",
            "description",
            "category",
            "last_updated",
            "maintainer"
        ]
        
        for field in required_metadata:
            if field not in metadata or metadata[field] is None:
                errors.append(f"Missing required metadata field: {field}")
        
        # Validate category
        valid_categories = ["planning", "execution", "analysis", "deployment", "maintenance"]
        if "category" in metadata and metadata["category"] not in valid_categories:
            errors.append(
                f"Invalid category: {metadata['category']}. "
                f"Must be one of: {', '.join(valid_categories)}"
            )
        
        return errors


def main():
    """Example usage and testing"""
    
    # Example: Resolve a planning orchestrator manifest
    base_dir = Path(__file__).parent.parent.parent / "cortex-brain" / "manifests"
    resolver = ManifestInheritanceResolver(base_dir)
    
    # Test resolving planning-base (should inherit from base-orchestrator)
    try:
        planning_base = resolver.resolve("shared/planning-base-manifest.yaml")
        print("✓ Successfully resolved planning-base-manifest.yaml")
        print(f"  Inheritance chain: {' → '.join(resolver.get_inheritance_chain('shared/planning-base-manifest.yaml'))}")
        
        # Validate
        errors = resolver.validate_manifest(planning_base)
        if errors:
            print(f"  ⚠️  Validation errors: {errors}")
        else:
            print("  ✓ Validation passed")
        
        # Show merged metadata
        print(f"\n  Merged metadata:")
        for key, value in planning_base.get("metadata", {}).items():
            if value is not None and not isinstance(value, (dict, list)):
                print(f"    {key}: {value}")
    
    except Exception as e:
        print(f"✗ Error resolving planning-base: {e}")


if __name__ == "__main__":
    main()
