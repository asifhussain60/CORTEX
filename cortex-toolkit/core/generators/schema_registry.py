#!/usr/bin/env python3
"""
CORTEX Toolkit - Schema Registry
Manages OpenAPI schema deduplication and reference tracking.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class SchemaMetadata:
    """Metadata for a registered schema"""
    schema_name: str
    schema_hash: str
    source_file: str
    namespace: str
    line_number: int
    registered_at: str
    properties_count: int
    references: List[str] = field(default_factory=list)
    referenced_by: List[str] = field(default_factory=list)


class SchemaRegistry:
    """
    Central registry for OpenAPI schemas with deduplication.
    
    Features:
    - Hash-based deduplication
    - Reference tracking (which schemas reference others)
    - Source file lineage
    - Conflict detection
    - Canonical naming
    """
    
    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize schema registry.
        
        Args:
            registry_path: Path to registry file (default: ./schema-registry.json)
        """
        self.registry_path = Path(registry_path or "./schema-registry.json")
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.metadata: Dict[str, SchemaMetadata] = {}
        
        # Load existing registry if it exists
        if self.registry_path.exists():
            self.load()
    
    def register(
        self,
        schema_name: str,
        schema_definition: Dict[str, Any],
        source_file: str,
        namespace: str = "Unknown",
        line_number: int = 0
    ) -> str:
        """
        Register a schema with deduplication.
        
        Args:
            schema_name: Name of the schema
            schema_definition: OpenAPI schema definition
            source_file: Source file path
            namespace: C# namespace
            line_number: Line number in source
        
        Returns:
            Canonical schema name (may differ if duplicate detected)
        """
        # Calculate schema hash
        schema_hash = self._hash_schema(schema_definition)
        
        # Check for exact duplicates
        duplicate_name = self._find_duplicate(schema_hash)
        if duplicate_name:
            # Schema already exists
            existing_meta = self.metadata[duplicate_name]
            
            # Update referenced_by
            if source_file not in existing_meta.referenced_by:
                existing_meta.referenced_by.append(source_file)
            
            return duplicate_name
        
        # Extract references from this schema
        references = self._extract_references(schema_definition)
        
        # Create metadata
        metadata = SchemaMetadata(
            schema_name=schema_name,
            schema_hash=schema_hash,
            source_file=source_file,
            namespace=namespace,
            line_number=line_number,
            registered_at=datetime.now().isoformat(),
            properties_count=len(schema_definition.get("properties", {})),
            references=references
        )
        
        # Register schema
        self.schemas[schema_name] = schema_definition
        self.metadata[schema_name] = metadata
        
        # Update reverse references
        for ref_name in references:
            if ref_name in self.metadata:
                if schema_name not in self.metadata[ref_name].referenced_by:
                    self.metadata[ref_name].referenced_by.append(schema_name)
        
        return schema_name
    
    def get(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """Get schema definition by name"""
        return self.schemas.get(schema_name)
    
    def get_metadata(self, schema_name: str) -> Optional[SchemaMetadata]:
        """Get schema metadata"""
        return self.metadata.get(schema_name)
    
    def get_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered schemas"""
        return self.schemas.copy()
    
    def get_reference_graph(self) -> Dict[str, List[str]]:
        """
        Get schema reference graph.
        
        Returns:
            Dictionary of schema_name -> list of schemas it references
        """
        return {name: meta.references for name, meta in self.metadata.items()}
    
    def get_reverse_reference_graph(self) -> Dict[str, List[str]]:
        """
        Get reverse reference graph.
        
        Returns:
            Dictionary of schema_name -> list of schemas that reference it
        """
        return {name: meta.referenced_by for name, meta in self.metadata.items()}
    
    def detect_circular_references(self) -> List[List[str]]:
        """
        Detect circular reference chains.
        
        Returns:
            List of circular reference paths
        """
        circular_refs = []
        visited: Set[str] = set()
        
        def dfs(node: str, path: List[str]):
            if node in path:
                # Found circular reference
                cycle_start = path.index(node)
                circular_refs.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            path.append(node)
            
            # Visit references
            if node in self.metadata:
                for ref in self.metadata[node].references:
                    dfs(ref, path.copy())
        
        # Start DFS from each node
        for schema_name in self.schemas:
            if schema_name not in visited:
                dfs(schema_name, [])
        
        return circular_refs
    
    def get_orphaned_schemas(self) -> List[str]:
        """
        Get schemas that are not referenced by any other schema.
        
        Returns:
            List of orphaned schema names
        """
        return [
            name for name, meta in self.metadata.items()
            if not meta.referenced_by
        ]
    
    def consolidate(self) -> Dict[str, str]:
        """
        Consolidate duplicate schemas under canonical names.
        
        Returns:
            Dictionary of old_name -> canonical_name for renamed schemas
        """
        renames = {}
        hash_to_canonical: Dict[str, str] = {}
        
        for name, meta in list(self.metadata.items()):
            schema_hash = meta.schema_hash
            
            if schema_hash in hash_to_canonical:
                # Duplicate found
                canonical = hash_to_canonical[schema_hash]
                if canonical != name:
                    renames[name] = canonical
                    
                    # Merge referenced_by lists
                    self.metadata[canonical].referenced_by.extend(meta.referenced_by)
                    self.metadata[canonical].referenced_by = list(set(
                        self.metadata[canonical].referenced_by
                    ))
                    
                    # Remove duplicate
                    del self.schemas[name]
                    del self.metadata[name]
            else:
                hash_to_canonical[schema_hash] = name
        
        return renames
    
    def save(self):
        """Save registry to file"""
        registry_data = {
            "version": "1.0.0",
            "updated_at": datetime.now().isoformat(),
            "schemas": self.schemas,
            "metadata": {
                name: asdict(meta) for name, meta in self.metadata.items()
            }
        }
        
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry_data, f, indent=2)
    
    def load(self):
        """Load registry from file"""
        if not self.registry_path.exists():
            return
        
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            registry_data = json.load(f)
        
        self.schemas = registry_data.get("schemas", {})
        
        # Reconstruct metadata objects
        metadata_dict = registry_data.get("metadata", {})
        self.metadata = {
            name: SchemaMetadata(**meta_data)
            for name, meta_data in metadata_dict.items()
        }
    
    def export_openapi_components(self) -> Dict[str, Any]:
        """
        Export all schemas in OpenAPI components format.
        
        Returns:
            OpenAPI components/schemas dictionary
        """
        return {
            "components": {
                "schemas": self.schemas
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        circular_refs = self.detect_circular_references()
        orphaned = self.get_orphaned_schemas()
        
        return {
            "total_schemas": len(self.schemas),
            "total_properties": sum(
                meta.properties_count for meta in self.metadata.values()
            ),
            "schemas_with_references": len([
                m for m in self.metadata.values() if m.references
            ]),
            "circular_reference_chains": len(circular_refs),
            "orphaned_schemas": len(orphaned),
            "source_files": len(set(
                meta.source_file for meta in self.metadata.values()
            )),
            "namespaces": len(set(
                meta.namespace for meta in self.metadata.values()
            ))
        }
    
    def _hash_schema(self, schema: Dict[str, Any]) -> str:
        """Calculate hash of schema definition"""
        # Normalize schema for hashing (sort keys, etc.)
        schema_json = json.dumps(schema, sort_keys=True)
        return hashlib.sha256(schema_json.encode()).hexdigest()[:16]
    
    def _find_duplicate(self, schema_hash: str) -> Optional[str]:
        """Find existing schema with same hash"""
        for name, meta in self.metadata.items():
            if meta.schema_hash == schema_hash:
                return name
        return None
    
    def _extract_references(self, schema: Dict[str, Any]) -> List[str]:
        """Extract all $ref references from schema"""
        references = []
        
        def extract_refs(obj: Any):
            if isinstance(obj, dict):
                if "$ref" in obj:
                    # Extract schema name from #/components/schemas/SchemaName
                    ref = obj["$ref"]
                    if ref.startswith("#/components/schemas/"):
                        schema_name = ref.replace("#/components/schemas/", "")
                        references.append(schema_name)
                
                for value in obj.values():
                    extract_refs(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_refs(item)
        
        extract_refs(schema)
        return list(set(references))


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Manage OpenAPI schema registry"
    )
    parser.add_argument(
        "command",
        choices=["stats", "list", "consolidate", "export", "check-circular"],
        help="Command to execute"
    )
    parser.add_argument(
        "--registry",
        default="./schema-registry.json",
        help="Path to registry file"
    )
    parser.add_argument(
        "--output",
        help="Output file for export command"
    )
    
    args = parser.parse_args()
    
    registry = SchemaRegistry(Path(args.registry))
    
    if args.command == "stats":
        stats = registry.get_stats()
        print("📊 Schema Registry Statistics")
        print("=" * 50)
        for key, value in stats.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
    
    elif args.command == "list":
        print(f"📚 Registered Schemas ({len(registry.schemas)})")
        print("=" * 50)
        for name, meta in registry.metadata.items():
            print(f"\n{name}")
            print(f"  Source: {meta.source_file}:{meta.line_number}")
            print(f"  Namespace: {meta.namespace}")
            print(f"  Properties: {meta.properties_count}")
            if meta.references:
                print(f"  References: {', '.join(meta.references)}")
            if meta.referenced_by:
                print(f"  Referenced By: {', '.join(meta.referenced_by)}")
    
    elif args.command == "consolidate":
        renames = registry.consolidate()
        if renames:
            print(f"🔄 Consolidated {len(renames)} duplicate schemas:")
            for old_name, new_name in renames.items():
                print(f"  {old_name} → {new_name}")
            registry.save()
            print("✅ Registry saved")
        else:
            print("✅ No duplicates found")
    
    elif args.command == "export":
        output_file = Path(args.output or "./schemas-components.json")
        components = registry.export_openapi_components()
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(components, f, indent=2)
        print(f"✅ Exported to {output_file}")
    
    elif args.command == "check-circular":
        circular = registry.detect_circular_references()
        if circular:
            print(f"⚠️  Found {len(circular)} circular reference chains:")
            for chain in circular:
                print(f"  {' → '.join(chain)}")
        else:
            print("✅ No circular references detected")
    
    return 0


if __name__ == "__main__":
    exit(main())
