#!/usr/bin/env python3
"""
Migrate Knowledge Files from cortex-brain/knowledge/ to cortex-brain/tier3/knowledge/

Maps old category structure to new 16-domain taxonomy and updates the knowledge index.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import shutil
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Category to Domain mapping
CATEGORY_TO_DOMAIN = {
    # Direct mappings
    "security": "SECURITY",
    "testing": "TESTING-VALIDATION",
    "performance": "PERFORMANCE",
    "devops": "DEPLOYMENT",  # DevOps maps to Deployment
    
    # Engineering breakdown
    "engineering": "ARCHITECTURE",  # General engineering -> Architecture
    "engineering/api-design": "API-DESIGN",
    
    # Specialized domains
    "cloud": "DEPLOYMENT",  # Cloud maps to Deployment
    "database": "DATA-MANAGEMENT",
    "microservices": "ARCHITECTURE",
    "frontend": "ARCHITECTURE",  # Frontend -> Architecture
    "ddd": "ARCHITECTURE",  # DDD -> Architecture
    "domains": "KNOWLEDGE-CURATION",  # RAG/Embeddings -> Knowledge Curation
    "ui-ux": "DOCUMENTATION",  # UI/UX -> Documentation
}


def get_domain_for_file(file_path: Path) -> str:
    """Determine the target domain for a knowledge file."""
    # Get relative path from knowledge root
    rel_path = str(file_path.relative_to(Path("cortex-brain/knowledge")))
    
    # Check for specific subdirectory mappings first
    for category, domain in CATEGORY_TO_DOMAIN.items():
        if rel_path.startswith(category):
            return domain
    
    # Default to ARCHITECTURE
    return "ARCHITECTURE"


def extract_metadata_from_yaml(file_path: Path) -> Dict[str, Any]:
    """Extract metadata from a knowledge YAML file."""
    try:
        with open(file_path, 'r') as f:
            content = yaml.safe_load(f)
            
        if not content:
            return {}
            
        # Try to extract common metadata fields
        metadata = {
            "title": content.get("title", content.get("name", file_path.stem)),
            "description": content.get("description", content.get("summary", "")),
            "tags": content.get("tags", content.get("keywords", [])),
            "version": content.get("version", "1.0"),
        }
        
        return metadata
    except Exception as e:
        print(f"  Warning: Could not parse {file_path}: {e}")
        return {"title": file_path.stem}


def migrate_files() -> List[Dict[str, Any]]:
    """Migrate all knowledge files to tier3 structure."""
    source_dir = Path("cortex-brain/knowledge")
    target_base = Path("cortex-brain/tier3/knowledge")
    
    if not source_dir.exists():
        print(f"Source directory {source_dir} does not exist!")
        return []
    
    migrated_entries = []
    yaml_files = list(source_dir.rglob("*.yaml"))
    
    print(f"Found {len(yaml_files)} YAML files to migrate\n")
    
    for source_file in yaml_files:
        domain = get_domain_for_file(source_file)
        target_dir = target_base / domain
        target_file = target_dir / source_file.name
        
        print(f"Migrating: {source_file}")
        print(f"  -> Domain: {domain}")
        print(f"  -> Target: {target_file}")
        
        # Create target directory if needed
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(source_file, target_file)
        
        # Extract metadata for index
        metadata = extract_metadata_from_yaml(source_file)
        
        entry = {
            "id": f"KB-{domain[:3]}-{len(migrated_entries)+1:03d}",
            "domain": domain,
            "title": metadata.get("title", source_file.stem),
            "description": metadata.get("description", ""),
            "file_path": str(target_file),
            "source_file": str(source_file),
            "tags": metadata.get("tags", []),
            "version": metadata.get("version", "1.0"),
            "migrated_at": datetime.now().isoformat(),
        }
        
        migrated_entries.append(entry)
        print(f"  ✓ Migrated as {entry['id']}\n")
    
    return migrated_entries


def update_knowledge_index(entries: List[Dict[str, Any]]) -> None:
    """Update the .knowledge-index.json with migrated entries."""
    index_path = Path("cortex-brain/tier3/knowledge/.knowledge-index.json")
    
    # Load existing index
    if index_path.exists():
        with open(index_path, 'r') as f:
            index = json.load(f)
    else:
        index = {
            "metadata": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
            },
            "entries": [],
            "ac_id_mapping": {},
            "by_domain": {},
        }
    
    # Update metadata
    index["metadata"]["updated_at"] = datetime.now().isoformat()
    index["metadata"]["entry_count"] = len(entries)
    index["metadata"]["migration_note"] = "Migrated from cortex-brain/knowledge/ (CORTEX-4.0)"
    
    # Add entries
    index["entries"] = entries
    
    # Build by_domain index
    by_domain = {}
    for entry in entries:
        domain = entry["domain"]
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(entry["id"])
    
    index["by_domain"] = by_domain
    
    # Build AC-ID mapping (for knowledge entries that reference ACs)
    # This would be populated if the YAML files contain AC references
    
    # Save updated index
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"\n✓ Updated index: {index_path}")
    print(f"  - Total entries: {len(entries)}")
    print(f"  - Domains covered: {len(by_domain)}")


def main():
    print("=" * 60)
    print("CORTEX Knowledge Migration: CORTEX-4.0 -> Tier3 Structure")
    print("=" * 60 + "\n")
    
    # Migrate files
    entries = migrate_files()
    
    if not entries:
        print("No files to migrate!")
        return
    
    # Update index
    update_knowledge_index(entries)
    
    # Summary
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"Total files migrated: {len(entries)}")
    
    # Count by domain
    domain_counts = {}
    for entry in entries:
        domain = entry["domain"]
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    print("\nFiles per domain:")
    for domain, count in sorted(domain_counts.items()):
        print(f"  {domain}: {count}")
    
    print("\n✓ Migration complete!")
    print("\nNext steps:")
    print("  1. Review migrated files in cortex-brain/tier3/knowledge/")
    print("  2. git add cortex-brain/tier3/knowledge/")
    print("  3. git commit -m 'feat: Migrate 35 knowledge YAMLs to tier3 structure'")


if __name__ == "__main__":
    main()
