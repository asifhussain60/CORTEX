#!/usr/bin/env python3
"""
CORTEX Brain Exporter

Exports Tier 2 knowledge graph patterns to human-readable YAML format for sharing.
Auto-sniffs pattern structure and metadata for intelligent transfer.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import yaml
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json


class BrainExporter:
    """Export CORTEX brain patterns to YAML for knowledge sharing."""
    
    def __init__(self, brain_path: Optional[Path] = None):
        """
        Initialize brain exporter.
        
        Args:
            brain_path: Path to cortex-brain directory (auto-detected if None)
        """
        if brain_path is None:
            # Auto-detect brain path
            current = Path(__file__).resolve()
            for parent in current.parents:
                candidate = parent / "cortex-brain"
                if candidate.exists():
                    brain_path = candidate
                    break
            
            if brain_path is None:
                raise ValueError("Cannot auto-detect cortex-brain path")
        
        self.brain_path = Path(brain_path)
        self.db_path = self.brain_path / "tier2" / "knowledge_graph.db"
        self.export_dir = self.brain_path / "exports"
        self.export_dir.mkdir(exist_ok=True)
        
        # Get machine ID from config
        self.machine_id = self._get_machine_id()
        
    def _get_machine_id(self) -> str:
        """Get unique machine identifier."""
        import platform
        import socket
        
        hostname = socket.gethostname()
        system = platform.system()
        machine = platform.machine()
        
        # Create deterministic ID
        id_string = f"{hostname}-{system}-{machine}"
        return hashlib.md5(id_string.encode()).hexdigest()[:12]
    
    def export_brain(
        self,
        scope: str = "workspace",
        min_confidence: float = 0.5,
        output_path: Optional[Path] = None,
        include_metadata: bool = True
    ) -> Path:
        """
        Export brain patterns to YAML file.
        
        Args:
            scope: Pattern scope ("workspace", "cortex", or "all")
            min_confidence: Minimum confidence threshold (0.0-1.0)
            output_path: Custom output path (auto-generated if None)
            include_metadata: Include detailed metadata in export
            
        Returns:
            Path to exported YAML file
        """
        # Connect to knowledge graph database
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query based on scope
        query = """
            SELECT 
                pattern_id,
                title,
                pattern_type,
                confidence,
                content,
                scope,
                namespaces,
                created_at,
                last_accessed,
                access_count
            FROM patterns
            WHERE confidence >= ?
        """
        
        params = [min_confidence]
        
        if scope != "all":
            query += " AND scope = ?"
            params.append(scope)
        
        query += " ORDER BY confidence DESC, access_count DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Build export data structure
        export_data = self._build_export_structure(rows, scope, min_confidence)
        
        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"brain-export-{timestamp}.yaml"
            output_path = self.export_dir / filename
        
        # Add metadata signature
        export_data["signature"] = self._generate_signature(export_data)
        
        # Write YAML file
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header comment
            f.write(f"# CORTEX Brain Export\n")
            f.write(f"# Generated: {export_data['export_date']}\n")
            f.write(f"# Source: {export_data['source_machine_id']}\n")
            f.write(f"# CORTEX Version: {export_data['cortex_version']}\n")
            f.write(f"# Total Patterns: {export_data['total_patterns']}\n")
            f.write(f"#\n")
            f.write(f"# Import with: cortex import brain {output_path.name}\n")
            f.write(f"#\n\n")
            
            # Write YAML data
            yaml.dump(
                export_data,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                width=100
            )
        
        conn.close()
        
        return output_path
    
    def _build_export_structure(
        self,
        rows: List[sqlite3.Row],
        scope: str,
        min_confidence: float
    ) -> Dict[str, Any]:
        """Build export data structure from database rows."""
        patterns = {}
        namespaces_set = set()
        pattern_types_set = set()
        oldest_date = None
        newest_date = None
        
        for row in rows:
            pattern_id = row["pattern_id"]
            
            # Parse content (could be JSON or plain text)
            try:
                context = json.loads(row["content"]) if row["content"] else {}
            except json.JSONDecodeError:
                # If not JSON, treat as plain text
                context = {"content": row["content"]} if row["content"] else {}
            
            # Parse namespaces
            try:
                namespaces = json.loads(row["namespaces"]) if row["namespaces"] else []
            except json.JSONDecodeError:
                namespaces = []
            
            # Track statistics
            namespaces_set.update(namespaces)
            pattern_types_set.add(row["pattern_type"])
            
            created = row["created_at"]
            if oldest_date is None or created < oldest_date:
                oldest_date = created
            if newest_date is None or created > newest_date:
                newest_date = created
            
            # Build pattern entry
            pattern_entry = {
                "pattern_type": row["pattern_type"],
                "confidence": float(row["confidence"]),
                "access_count": row["access_count"],
                "last_accessed": row["last_accessed"],
                "created_at": created,
                "namespaces": namespaces,
                "source": self.machine_id,
                "context": context
            }
            
            patterns[pattern_id] = pattern_entry
        
        # Get CORTEX version
        cortex_version = self._get_cortex_version()
        
        # Build complete export structure
        export_data = {
            "version": "1.0",
            "export_date": datetime.now().isoformat(),
            "source_machine_id": self.machine_id,
            "cortex_version": cortex_version,
            "total_patterns": len(patterns),
            "scope": scope,
            "statistics": {
                "patterns_exported": len(patterns),
                "confidence_range": [
                    min_confidence,
                    max((p["confidence"] for p in patterns.values()), default=0.0)
                ],
                "namespaces": sorted(list(namespaces_set)),
                "pattern_types": sorted(list(pattern_types_set)),
                "oldest_pattern": oldest_date,
                "newest_pattern": newest_date
            },
            "patterns": patterns
        }
        
        return export_data
    
    def _get_cortex_version(self) -> str:
        """Get CORTEX version from package or fallback."""
        try:
            # Try to read from setup.py or __version__.py
            version_file = self.brain_path.parent / "src" / "__init__.py"
            if version_file.exists():
                with open(version_file) as f:
                    for line in f:
                        if line.startswith("__version__"):
                            return line.split("=")[1].strip().strip("\"'")
        except Exception:
            pass
        
        return "3.0.0"  # Default fallback
    
    def _generate_signature(self, export_data: Dict[str, Any]) -> str:
        """Generate SHA256 signature for export integrity verification."""
        # Create deterministic string from export data
        signature_data = {
            "export_date": export_data["export_date"],
            "source_machine_id": export_data["source_machine_id"],
            "total_patterns": export_data["total_patterns"],
            "pattern_ids": sorted(export_data["patterns"].keys())
        }
        
        signature_string = json.dumps(signature_data, sort_keys=True)
        return hashlib.sha256(signature_string.encode()).hexdigest()


def main():
    """CLI interface for brain export."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Export CORTEX brain patterns to YAML"
    )
    parser.add_argument(
        "--scope",
        choices=["workspace", "cortex", "all"],
        default="workspace",
        help="Pattern scope to export (default: workspace)"
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.5,
        help="Minimum confidence threshold (default: 0.5)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (auto-generated if not specified)"
    )
    
    args = parser.parse_args()
    
    # Export brain
    exporter = BrainExporter()
    output_path = exporter.export_brain(
        scope=args.scope,
        min_confidence=args.min_confidence,
        output_path=args.output
    )
    
    print(f"✅ Brain exported successfully!")
    print(f"📁 Location: {output_path}")
    print(f"💾 Size: {output_path.stat().st_size / 1024:.1f} KB")
    print(f"\n📋 To import on another machine:")
    print(f"   cortex import brain {output_path.name}")


if __name__ == "__main__":
    main()
