#!/usr/bin/env python3
"""
CORTEX Documentation Cleanup - Phase 1: Discovery & Verification

Scans generator modules to build definitive list of generated vs manual files.
Creates manifest for subsequent cleanup phases.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Date: 2025-11-18
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
import sys

# Add CORTEX root to path
CORTEX_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(CORTEX_ROOT))


class DocumentationDiscovery:
    """Discover generated vs manual documentation files."""
    
    def __init__(self, cortex_root: Path):
        self.cortex_root = cortex_root
        self.docs_path = cortex_root / "docs"
        self.generators_path = cortex_root / "cortex-brain" / "admin" / "documentation" / "generators"
        
        # Results
        self.generated_files: Set[str] = set()
        self.manual_files: Set[str] = set()
        self.static_assets: Set[str] = set()
        self.unknown_files: Set[str] = set()
        
    def discover_generator_outputs(self) -> Dict[str, List[str]]:
        """Scan generator modules to find all output file patterns."""
        print("🔍 Scanning generator modules for output patterns...")
        
        generator_outputs = {}
        
        # Known generators
        generators = {
            "feature_list_generator.py": [
                "FEATURES.md",
                "OPERATIONS-REFERENCE.md",
                "MODULES-REFERENCE.md",
                "CAPABILITIES-MATRIX.md",
                "FEATURE-COMPARISON.md"
            ],
            "executive_summary_generator.py": [
                "EXECUTIVE-SUMMARY.md"
            ],
            "diagrams_generator.py": [
                "diagrams/*.mmd",
                "diagrams/diagram-*.md",
                "diagrams/prompts/*.md"
            ],
            "mkdocs_generator.py": [
                "index.md"
            ]
        }
        
        for generator_file, outputs in generators.items():
            generator_path = self.generators_path / generator_file
            if generator_path.exists():
                print(f"  ✅ Found {generator_file}: {len(outputs)} outputs")
                generator_outputs[generator_file] = outputs
                
                # Add to generated files
                for output in outputs:
                    if "*" in output:
                        # Pattern - expand later
                        self.generated_files.add(output)
                    else:
                        self.generated_files.add(f"docs/{output}")
            else:
                print(f"  ⚠️  Generator not found: {generator_file}")
        
        return generator_outputs
    
    def scan_existing_files(self):
        """Scan docs/ directory for all existing files."""
        print("\n📂 Scanning docs/ directory for existing files...")
        
        if not self.docs_path.exists():
            print(f"  ❌ docs/ directory not found: {self.docs_path}")
            return
        
        # Static asset directories (never delete)
        static_dirs = {"assets", "images", "stylesheets", "overrides"}
        
        all_files = []
        for file_path in self.docs_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(self.cortex_root)
                rel_path_str = str(rel_path).replace("\\", "/")
                all_files.append(rel_path_str)
                
                # Check if in static directory
                parts = rel_path.parts
                if len(parts) > 1 and parts[1] in static_dirs:
                    self.static_assets.add(rel_path_str)
        
        print(f"  ✅ Found {len(all_files)} total files in docs/")
        print(f"  ✅ Found {len(self.static_assets)} static asset files")
        
        return all_files
    
    def check_autogen_markers(self, file_path: Path) -> bool:
        """Check if file has AUTO-GENERATED marker."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            return "AUTO-GENERATED" in content or "auto-generated" in content
        except Exception:
            return False
    
    def categorize_files(self, all_files: List[str]):
        """Categorize files as generated, manual, or unknown."""
        print("\n🏷️  Categorizing files...")
        
        # Expand patterns in generated files
        expanded_generated = set()
        for pattern in self.generated_files:
            if "*" in pattern:
                # Match pattern against actual files
                pattern_re = pattern.replace("*", ".*")
                for file in all_files:
                    if re.match(pattern_re, file):
                        expanded_generated.add(file)
            else:
                expanded_generated.add(pattern)
        
        self.generated_files = expanded_generated
        
        # Categorize each file
        for file in all_files:
            if file in self.static_assets:
                continue  # Already categorized
            
            if file in self.generated_files:
                continue  # Already categorized as generated
            
            file_path = self.cortex_root / file
            
            # Check for AUTO-GENERATED marker
            if self.check_autogen_markers(file_path):
                self.generated_files.add(file)
            else:
                # Check if it's a known manual file
                filename = Path(file).name
                if any(x in filename.lower() for x in ["report", "guide", "backup", "manual"]):
                    self.manual_files.add(file)
                else:
                    self.unknown_files.add(file)
        
        print(f"  ✅ Generated files: {len(self.generated_files)}")
        print(f"  ⚠️  Manual files: {len(self.manual_files)}")
        print(f"  ❓ Unknown files: {len(self.unknown_files)}")
        print(f"  📦 Static assets: {len(self.static_assets)}")
    
    def create_manifest(self, output_path: Path) -> Dict:
        """Create cleanup manifest JSON."""
        manifest = {
            "version": "1.0.0",
            "created": "2025-11-18",
            "cortex_root": str(self.cortex_root),
            "docs_path": str(self.docs_path),
            
            "generated_files": sorted(list(self.generated_files)),
            "manual_files": sorted(list(self.manual_files)),
            "unknown_files": sorted(list(self.unknown_files)),
            "static_assets": sorted(list(self.static_assets)),
            
            "summary": {
                "total_files": len(self.generated_files) + len(self.manual_files) + 
                              len(self.unknown_files) + len(self.static_assets),
                "generated_count": len(self.generated_files),
                "manual_count": len(self.manual_files),
                "unknown_count": len(self.unknown_files),
                "static_count": len(self.static_assets)
            },
            
            "actions": {
                "keep": len(self.generated_files) + len(self.static_assets),
                "migrate": len(self.manual_files),
                "review": len(self.unknown_files)
            }
        }
        
        # Write manifest
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n💾 Manifest saved: {output_path}")
        return manifest
    
    def print_summary(self, manifest: Dict):
        """Print discovery summary."""
        print("\n" + "="*60)
        print("📊 DISCOVERY SUMMARY")
        print("="*60)
        
        summary = manifest["summary"]
        actions = manifest["actions"]
        
        print(f"\n📁 Total Files: {summary['total_files']}")
        print(f"  ✅ Generated: {summary['generated_count']}")
        print(f"  ⚠️  Manual: {summary['manual_count']}")
        print(f"  ❓ Unknown: {summary['unknown_count']}")
        print(f"  📦 Static: {summary['static_count']}")
        
        print(f"\n🎯 Actions Required:")
        print(f"  ✅ Keep (Generated + Static): {actions['keep']}")
        print(f"  🚚 Migrate (Manual): {actions['migrate']}")
        print(f"  👀 Review (Unknown): {actions['review']}")
        
        if self.manual_files:
            print("\n⚠️  Manual Files to Migrate:")
            for file in sorted(self.manual_files):
                print(f"    • {file}")
        
        if self.unknown_files:
            print("\n❓ Unknown Files (Need Review):")
            for file in sorted(self.unknown_files)[:10]:  # Show first 10
                print(f"    • {file}")
            if len(self.unknown_files) > 10:
                print(f"    ... and {len(self.unknown_files) - 10} more")


def main():
    """Run Phase 1: Discovery & Verification."""
    print("🧠 CORTEX Documentation Cleanup - Phase 1: Discovery")
    print("="*60)
    
    cortex_root = Path(__file__).parent.parent
    discovery = DocumentationDiscovery(cortex_root)
    
    # Step 1: Discover generator outputs
    generator_outputs = discovery.discover_generator_outputs()
    
    # Step 2: Scan existing files
    all_files = discovery.scan_existing_files()
    
    # Step 3: Categorize files
    if all_files:
        discovery.categorize_files(all_files)
    
    # Step 4: Create manifest
    manifest_path = cortex_root / "cortex-brain" / "cleanup-reports" / "cleanup-manifest-2025-11-18.json"
    manifest = discovery.create_manifest(manifest_path)
    
    # Step 5: Print summary
    discovery.print_summary(manifest)
    
    print("\n" + "="*60)
    print("✅ Phase 1 Complete - Discovery manifest created")
    print("="*60)
    print(f"\n📄 Manifest: {manifest_path}")
    print("\n🔍 Next Step: Review manifest, then run Phase 2 (Migration)")


if __name__ == "__main__":
    main()
