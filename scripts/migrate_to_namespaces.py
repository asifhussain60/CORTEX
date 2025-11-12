#!/usr/bin/env python3
"""
Namespace Migration Script

Migrates existing knowledge graph patterns to namespace-based architecture.
Adds cortex.* and workspace.* namespace prefixes to existing patterns.

This is a ONE-TIME migration for Phase 2.1 implementation.

Usage:
    python scripts/migrate_to_namespaces.py --dry-run  # Preview changes
    python scripts/migrate_to_namespaces.py           # Apply migration

Author: Asif Hussain
Date: 2025-11-12
"""

import sqlite3
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class NamespaceMigrator:
    """Migrates knowledge graph to namespace-based architecture."""
    
    # Pattern keys that belong to CORTEX framework
    CORTEX_PATTERNS = {
        "validation_insights",
        "workflow_patterns",
        "architectural_patterns",
        "intent_patterns",
        "tier_architecture",
        "agent_patterns",
        "operations",
        "plugins",
        "brain_protection",
        "corpus_callosum"
    }
    
    # Pattern keys that belong to workspace (user applications)
    WORKSPACE_PATTERNS = {
        "file_relationships",
        "test_patterns",
        "api_patterns",
        "ui_patterns",
        "database_patterns"
    }
    
    def __init__(self, db_path: Path, dry_run: bool = False):
        """
        Initialize migrator.
        
        Args:
            db_path: Path to knowledge_graph.db
            dry_run: If True, preview changes without applying
        """
        self.db_path = db_path
        self.dry_run = dry_run
        self.stats = {
            "total_patterns": 0,
            "cortex_patterns": 0,
            "workspace_patterns": 0,
            "ambiguous_patterns": 0,
            "already_namespaced": 0
        }
    
    def classify_pattern(self, pattern: Dict[str, Any]) -> str:
        """
        Determine correct namespace for pattern.
        
        Args:
            pattern: Pattern dictionary from database
        
        Returns:
            Namespace string (e.g., "cortex.agent_patterns" or "workspace.default.file_relationships")
        """
        pattern_id = pattern.get("pattern_id", "")
        title = pattern.get("title", "").lower()
        source = pattern.get("source", "").lower()
        existing_namespaces = pattern.get("namespaces", [])
        
        # Already has namespace? Check if migration needed
        if existing_namespaces:
            # Check if already using new namespace format
            if any(ns.startswith("cortex.") or ns.startswith("workspace.") 
                   for ns in existing_namespaces):
                return None  # Already migrated
        
        # Check pattern ID for CORTEX framework patterns
        for cortex_key in self.CORTEX_PATTERNS:
            if cortex_key in pattern_id.lower() or cortex_key in title:
                return f"cortex.{cortex_key}"
        
        # Check source for CORTEX framework indicators
        if any(indicator in source for indicator in [
            "cortex_framework",
            "brain_protection",
            "agent_system",
            "tier0", "tier1", "tier2", "tier3"
        ]):
            # Generic CORTEX pattern
            return "cortex.framework_patterns"
        
        # Check for workspace indicators in source/title
        if any(indicator in source for indicator in [
            "user_code",
            "application",
            "workspace",
            "tests/fixtures",
            "mock-project"
        ]):
            # Detect workspace from source path
            workspace_name = self._extract_workspace_name(source, pattern_id)
            
            # Classify by pattern type
            for workspace_key in self.WORKSPACE_PATTERNS:
                if workspace_key in pattern_id.lower() or workspace_key in title:
                    return f"workspace.{workspace_name}.{workspace_key}"
            
            # Generic workspace pattern
            return f"workspace.{workspace_name}.patterns"
        
        # Default: If can't determine, mark as ambiguous for manual review
        return "workspace.default.uncategorized"
    
    def _extract_workspace_name(self, source: str, pattern_id: str) -> str:
        """
        Extract workspace/project name from source path or pattern ID.
        
        Args:
            source: Source field from pattern
            pattern_id: Pattern ID
        
        Returns:
            Workspace name (e.g., "mock-project", "ksessions", "noor")
        """
        # Check for known project names in source
        known_workspaces = ["ksessions", "noor", "mock-project", "cortex"]
        for workspace in known_workspaces:
            if workspace in source.lower():
                return workspace
        
        # Check pattern ID for project indicators
        for workspace in known_workspaces:
            if workspace in pattern_id.lower():
                return workspace
        
        # Default to "default" workspace
        return "default"
    
    def migrate(self) -> Dict[str, Any]:
        """
        Execute migration.
        
        Returns:
            Migration statistics and results
        """
        print(f"\n{'=' * 60}")
        print(f"  CORTEX Namespace Migration - Phase 2.1")
        print(f"{'=' * 60}")
        print(f"Mode: {'DRY RUN (preview only)' if self.dry_run else 'LIVE (applying changes)'}")
        print(f"Database: {self.db_path}")
        print(f"{'=' * 60}\n")
        
        if not self.db_path.exists():
            print(f"❌ ERROR: Database not found at {self.db_path}")
            return {"error": "Database not found"}
        
        # Connect to database
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Fetch all patterns
        cursor.execute("""
            SELECT pattern_id, title, content, source, scope, namespaces
            FROM patterns
        """)
        
        patterns = cursor.fetchall()
        self.stats["total_patterns"] = len(patterns)
        
        print(f"Found {len(patterns)} patterns to analyze...\n")
        
        # Classify and migrate each pattern
        migrations = []
        
        for row in patterns:
            pattern = dict(row)
            pattern["namespaces"] = json.loads(pattern.get("namespaces") or "[]")
            
            # Determine new namespace
            new_namespace = self.classify_pattern(pattern)
            
            if new_namespace is None:
                # Already migrated
                self.stats["already_namespaced"] += 1
                print(f"✓ SKIP: {pattern['pattern_id']} (already namespaced)")
                continue
            
            # Track statistics
            if new_namespace.startswith("cortex."):
                self.stats["cortex_patterns"] += 1
                icon = "🔵"
            elif "uncategorized" in new_namespace:
                self.stats["ambiguous_patterns"] += 1
                icon = "⚠️ "
            else:
                self.stats["workspace_patterns"] += 1
                icon = "🟢"
            
            migrations.append({
                "pattern_id": pattern["pattern_id"],
                "title": pattern["title"],
                "old_namespaces": pattern["namespaces"],
                "new_namespace": new_namespace
            })
            
            print(f"{icon} {pattern['pattern_id'][:40]:40} → {new_namespace}")
        
        print(f"\n{'=' * 60}")
        print(f"  Migration Summary")
        print(f"{'=' * 60}")
        print(f"Total Patterns:       {self.stats['total_patterns']}")
        print(f"Already Namespaced:   {self.stats['already_namespaced']}")
        print(f"CORTEX Patterns:      {self.stats['cortex_patterns']} (cortex.*)")
        print(f"Workspace Patterns:   {self.stats['workspace_patterns']} (workspace.*)")
        print(f"Ambiguous/Manual:     {self.stats['ambiguous_patterns']} (needs review)")
        print(f"{'=' * 60}\n")
        
        # Apply migrations if not dry run
        if not self.dry_run and migrations:
            print("Applying namespace migrations...")
            
            for migration in migrations:
                # Update pattern with new namespace
                new_namespaces = [migration["new_namespace"]]
                
                cursor.execute("""
                    UPDATE patterns
                    SET namespaces = ?
                    WHERE pattern_id = ?
                """, (json.dumps(new_namespaces), migration["pattern_id"]))
            
            conn.commit()
            print(f"✅ Successfully migrated {len(migrations)} patterns!\n")
        
        elif self.dry_run:
            print("⚠️  DRY RUN: No changes applied. Run without --dry-run to migrate.\n")
        
        conn.close()
        
        # Save migration report
        if migrations and not self.dry_run:
            report_path = self.db_path.parent / f"namespace_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w') as f:
                json.dump({
                    "migration_date": datetime.now().isoformat(),
                    "stats": self.stats,
                    "migrations": migrations
                }, f, indent=2)
            print(f"📄 Migration report saved to: {report_path}\n")
        
        return {
            "stats": self.stats,
            "migrations": migrations
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate CORTEX knowledge graph to namespace-based architecture"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        help="Path to knowledge_graph.db (default: auto-detect)"
    )
    
    args = parser.parse_args()
    
    # Determine database path
    if args.db_path:
        db_path = Path(args.db_path)
    else:
        # Auto-detect (check common locations)
        possible_paths = [
            Path("cortex-brain/tier2/knowledge_graph.db"),
            Path("../cortex-brain/tier2/knowledge_graph.db"),
            Path.home() / "CORTEX/cortex-brain/tier2/knowledge_graph.db"
        ]
        
        db_path = None
        for path in possible_paths:
            if path.exists():
                db_path = path
                break
        
        if not db_path:
            print("❌ ERROR: Could not auto-detect knowledge_graph.db")
            print("Use --db-path to specify manually")
            return 1
    
    # Run migration
    migrator = NamespaceMigrator(db_path=db_path, dry_run=args.dry_run)
    result = migrator.migrate()
    
    # Check for ambiguous patterns
    if result.get("stats", {}).get("ambiguous_patterns", 0) > 0:
        print("\n⚠️  WARNING: Some patterns could not be auto-classified.")
        print("Review patterns in 'workspace.default.uncategorized' namespace")
        print("and manually assign correct namespaces.\n")
    
    return 0


if __name__ == "__main__":
    exit(main())
