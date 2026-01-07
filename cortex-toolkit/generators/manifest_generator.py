"""
Manifest Generator for Scripts/Utilities.

Auto-generates manifest.yaml files for all utilities with metadata.

Part of Phase P05.2: Manifest Generation System.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List
import sys

# Import ScriptsUtilitiesManager
import importlib.util
spec = importlib.util.spec_from_file_location(
    'manager',
    Path(__file__).parent.parent / 'core' / 'scripts_utilities_manager.py'
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ScriptsUtilitiesManager = module.ScriptsUtilitiesManager


def generate_utility_manifest(metadata) -> Dict[str, Any]:
    """Generate manifest entry for a utility."""
    return {
        'name': metadata.name,
        'file_path': metadata.file_path,
        'category': metadata.category,
        'description': metadata.description,
        'capabilities': metadata.capabilities,
        'dependencies': metadata.dependencies,
        'usage_stats': {
            'execution_count': metadata.usage_count,
            'last_used': metadata.last_used,
            'avg_duration_ms': metadata.avg_duration_ms,
            'success_rate': metadata.success_rate,
        }
    }


def generate_category_manifest(utilities: List) -> Dict[str, Any]:
    """Generate manifest for a category."""
    return {
        'category_name': utilities[0].category if utilities else 'unknown',
        'utility_count': len(utilities),
        'utilities': [generate_utility_manifest(u) for u in utilities]
    }


def generate_all_manifests():
    """Generate manifest files for all utilities."""
    # Detect project root
    current = Path(__file__).resolve()
    for parent in [current.parent] + list(current.parents):
        if (parent / "cortex.config.json").exists():
            project_root = parent
            break
    else:
        project_root = current.parent.parent.parent
    
    manager = ScriptsUtilitiesManager(
        scripts_dir=str(project_root / "scripts" / "utilities"),
        toolkit_dir=str(project_root / "cortex-toolkit" / "scripts-utilities"),
    )
    
    # Discover all utilities
    utilities = manager.discover_utilities()
    print(f"✅ Discovered {len(utilities)} utilities")
    
    # Group by category
    by_category = {}
    for util in utilities:
        if util.category not in by_category:
            by_category[util.category] = []
        by_category[util.category].append(util)
    
    # Create category directories and manifests
    toolkit_dir = project_root / "cortex-toolkit" / "scripts-utilities"
    toolkit_dir.mkdir(parents=True, exist_ok=True)
    
    for category, category_utils in by_category.items():
        # Create category directory
        category_dir = toolkit_dir / category
        category_dir.mkdir(exist_ok=True)
        
        # Generate category manifest
        manifest = generate_category_manifest(category_utils)
        manifest_path = category_dir / "manifest.yaml"
        
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Generated manifest: {category}/manifest.yaml ({len(category_utils)} utilities)")
    
    # Generate master manifest
    master_manifest = {
        'schema_version': '1.0',
        'total_utilities': len(utilities),
        'categories': list(by_category.keys()),
        'category_breakdown': {cat: len(utils) for cat, utils in by_category.items()},
        'generated_date': str(Path(__file__).stat().st_mtime),
    }
    
    master_path = toolkit_dir / "manifest.yaml"
    with open(master_path, 'w') as f:
        yaml.dump(master_manifest, f, default_flow_style=False, sort_keys=False)
    
    print(f"\n✅ Master manifest generated: cortex-toolkit/scripts-utilities/manifest.yaml")
    print(f"📁 Total: {len(by_category)} categories, {len(utilities)} utilities")


if __name__ == "__main__":
    generate_all_manifests()
