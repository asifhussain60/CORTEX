"""
CORTEX Tier 2: Schema Migration - Add Namespace/Scope Boundaries

This migration adds the knowledge boundary system to enforce impenetrable
separation between CORTEX core intelligence (generic) and application-specific
knowledge (KSESSIONS, NOOR, etc.).

Changes:
1. Add `scope` column: 'generic' (CORTEX) vs 'application' (apps)
2. Add `namespaces` column: JSON array supporting multi-app patterns
3. Create indexes for performance
4. Classify existing patterns based on content/source
5. Create rollback backup before migration

Usage:
    python CORTEX/src/tier2/migrate_add_boundaries.py [--dry-run] [--db-path PATH]

Args:
    --dry-run: Show what would be done without making changes
    --db-path: Path to database (default: cortex-brain/tier2/knowledge_graph.db)
"""

import sqlite3
import json
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Dict, Any


class BoundaryMigration:
    """Handles schema migration for namespace/scope boundaries."""
    
    # Classification rules
    GENERIC_KEYWORDS = [
        'test', 'tdd', 'refactor', 'solid', 'governance',
        'protection', 'cortex', 'tier', 'agent', 'workflow'
    ]
    
    APPLICATION_PATHS = [
        'SPA/', 'KSESSIONS/', 'NOOR/', 'blazor', 'signalr',
        'canvas', 'host', 'registration'
    ]
    
    SIMULATION_SOURCES = [
        'simulations/ksessions/', 'simulations/noor/',
        'simulations/spa/'
    ]
    
    def __init__(self, db_path: Path, dry_run: bool = False):
        """
        Initialize migration.
        
        Args:
            db_path: Path to SQLite database
            dry_run: If True, simulate without making changes
        """
        self.db_path = Path(db_path)
        self.dry_run = dry_run
        self.backup_path = None
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
    
    def create_backup(self) -> Path:
        """
        Create backup of database before migration.
        
        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.db_path.parent / f"{self.db_path.stem}_backup_{timestamp}.db"
        
        if not self.dry_run:
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ Backup created: {backup_path}")
        else:
            print(f"[DRY RUN] Would create backup: {backup_path}")
        
        self.backup_path = backup_path
        return backup_path
    
    def classify_pattern(
        self,
        pattern_id: str,
        title: str,
        content: str,
        source: str
    ) -> Tuple[str, List[str]]:
        """
        Classify pattern as generic or application-specific.
        
        Rules:
        1. Source from simulations/ → application, namespace from path
        2. Contains application paths → application, extract namespace
        3. Generic workflow/governance keywords → generic, CORTEX-core
        4. Protection/tier patterns → generic, CORTEX-core
        5. Default: generic if uncertain
        
        Args:
            pattern_id: Pattern identifier
            title: Pattern title
            content: Pattern content
            source: Pattern source
        
        Returns:
            Tuple of (scope, namespaces)
            - scope: 'generic' or 'application'
            - namespaces: List of namespace strings
        """
        # Combine all text for analysis
        text = f"{pattern_id} {title} {content}".lower()
        source_lower = source.lower() if source else ""
        
        # Rule 1: Source from simulations
        for sim_source in self.SIMULATION_SOURCES:
            if sim_source in source_lower:
                # Extract namespace from path (e.g., simulations/ksessions/ → KSESSIONS)
                namespace = sim_source.split('/')[-2].upper()
                return ('application', [namespace])
        
        # Rule 2: Contains application-specific paths
        for app_path in self.APPLICATION_PATHS:
            if app_path.lower() in text:
                # Extract namespace (e.g., KSESSIONS/, NOOR/)
                if '/' in app_path:
                    namespace = app_path.rstrip('/').upper()
                else:
                    # Generic application keyword (blazor, signalr)
                    # Default to application scope but generic namespace
                    return ('application', ['APPLICATION'])
                
                return ('application', [namespace])
        
        # Rule 3 & 4: Generic CORTEX patterns
        generic_count = sum(1 for keyword in self.GENERIC_KEYWORDS if keyword in text)
        if generic_count >= 2:  # At least 2 matches suggests CORTEX pattern
            return ('generic', ['CORTEX-core'])
        
        # Rule 5: Default to generic (conservative approach)
        # Rationale: Better to keep CORTEX patterns than delete them
        return ('generic', ['CORTEX-core'])
    
    def get_existing_patterns(self) -> List[Dict[str, Any]]:
        """
        Retrieve all existing patterns for classification.
        
        Returns:
            List of pattern dicts with id, title, content, source
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pattern_id, title, content, source
            FROM patterns
        """)
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                'pattern_id': row[0],
                'title': row[1],
                'content': row[2],
                'source': row[3] or ''
            })
        
        conn.close()
        return patterns
    
    def execute_migration(self) -> Dict[str, Any]:
        """
        Execute the migration.
        
        Returns:
            Migration statistics
        """
        print("\n" + "="*70)
        print("CORTEX BOUNDARY MIGRATION - Phase 1: Namespace/Scope Schema")
        print("="*70 + "\n")
        
        # Step 1: Create backup
        print("Step 1: Creating database backup...")
        self.create_backup()
        
        # Step 2: Analyze existing patterns
        print("\nStep 2: Analyzing existing patterns...")
        patterns = self.get_existing_patterns()
        print(f"Found {len(patterns)} patterns to classify")
        
        # Classify all patterns
        classifications = {}
        scope_counts = {'generic': 0, 'application': 0}
        namespace_counts = {}
        
        for pattern in patterns:
            scope, namespaces = self.classify_pattern(
                pattern['pattern_id'],
                pattern['title'],
                pattern['content'],
                pattern['source']
            )
            
            classifications[pattern['pattern_id']] = {
                'scope': scope,
                'namespaces': namespaces
            }
            
            scope_counts[scope] += 1
            for ns in namespaces:
                namespace_counts[ns] = namespace_counts.get(ns, 0) + 1
        
        # Print classification results
        print("\nClassification Results:")
        print(f"  Generic (CORTEX core): {scope_counts['generic']}")
        print(f"  Application-specific:  {scope_counts['application']}")
        print("\nNamespace Distribution:")
        for ns, count in sorted(namespace_counts.items()):
            print(f"  {ns}: {count}")
        
        # Step 3: Add schema columns
        print("\nStep 3: Adding schema columns...")
        
        if self.dry_run:
            print("[DRY RUN] Would execute:")
            print("  ALTER TABLE patterns ADD COLUMN scope TEXT DEFAULT 'generic'")
            print("  ALTER TABLE patterns ADD COLUMN namespaces TEXT DEFAULT '[\"CORTEX-core\"]'")
            print("  CREATE INDEX idx_scope ON patterns(scope)")
            print("  CREATE INDEX idx_namespaces ON patterns(namespaces)")
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # Add scope column
                cursor.execute("""
                    ALTER TABLE patterns 
                    ADD COLUMN scope TEXT DEFAULT 'generic' 
                    CHECK (scope IN ('generic', 'application'))
                """)
                print("  ✅ Added 'scope' column")
                
                # Add namespaces column (JSON array)
                cursor.execute("""
                    ALTER TABLE patterns 
                    ADD COLUMN namespaces TEXT DEFAULT '["CORTEX-core"]'
                """)
                print("  ✅ Added 'namespaces' column")
                
                # Create indexes
                cursor.execute("CREATE INDEX idx_scope ON patterns(scope)")
                print("  ✅ Created index on scope")
                
                cursor.execute("CREATE INDEX idx_namespaces ON patterns(namespaces)")
                print("  ✅ Created index on namespaces")
                
                conn.commit()
                
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print("  ⚠️  Columns already exist (migration previously run?)")
                else:
                    raise
            finally:
                conn.close()
        
        # Step 4: Update existing patterns with classifications
        print("\nStep 4: Applying classifications...")
        
        if self.dry_run:
            print(f"[DRY RUN] Would update {len(classifications)} patterns")
            # Show sample
            sample_count = min(5, len(classifications))
            print(f"\nSample classifications (first {sample_count}):")
            for i, (pattern_id, classification) in enumerate(list(classifications.items())[:sample_count]):
                print(f"  {pattern_id}:")
                print(f"    scope: {classification['scope']}")
                print(f"    namespaces: {classification['namespaces']}")
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updated_count = 0
            for pattern_id, classification in classifications.items():
                namespaces_json = json.dumps(classification['namespaces'])
                
                cursor.execute("""
                    UPDATE patterns
                    SET scope = ?, namespaces = ?
                    WHERE pattern_id = ?
                """, (classification['scope'], namespaces_json, pattern_id))
                
                updated_count += cursor.rowcount
            
            conn.commit()
            conn.close()
            
            print(f"  ✅ Updated {updated_count} patterns")
        
        # Step 5: Generate statistics
        stats = {
            'total_patterns': len(patterns),
            'generic_count': scope_counts['generic'],
            'application_count': scope_counts['application'],
            'namespaces': namespace_counts,
            'backup_path': str(self.backup_path) if self.backup_path else None,
            'dry_run': self.dry_run
        }
        
        return stats
    
    def print_summary(self, stats: Dict[str, Any]):
        """Print migration summary."""
        print("\n" + "="*70)
        print("MIGRATION SUMMARY")
        print("="*70)
        print(f"\nTotal patterns processed: {stats['total_patterns']}")
        
        if stats['total_patterns'] > 0:
            print(f"Generic (CORTEX core):    {stats['generic_count']} ({stats['generic_count']/stats['total_patterns']*100:.1f}%)")
            print(f"Application-specific:     {stats['application_count']} ({stats['application_count']/stats['total_patterns']*100:.1f}%)")
            
            print("\nNamespace breakdown:")
            for ns, count in sorted(stats['namespaces'].items()):
                print(f"  {ns}: {count}")
        else:
            print("  ⚠️  No patterns found in database (empty knowledge graph)")
        
        if stats.get('backup_path'):
            print(f"\n✅ Backup: {stats['backup_path']}")
        
        if stats['dry_run']:
            print("\n⚠️  DRY RUN MODE - No changes were made")
            print("    Run without --dry-run to apply migration")
        else:
            print("\n✅ Migration complete!")
            print("    Database schema updated with boundary system")
        
        print("="*70 + "\n")


def main():
    """Main migration entry point."""
    parser = argparse.ArgumentParser(
        description='CORTEX Tier 2 Schema Migration: Add Namespace/Scope Boundaries'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate migration without making changes'
    )
    parser.add_argument(
        '--db-path',
        type=str,
        help='Path to database (default: cortex-brain/tier2/knowledge_graph.db)'
    )
    
    args = parser.parse_args()
    
    # Determine database path
    if args.db_path:
        db_path = Path(args.db_path)
    else:
        # Default: relative to script location
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent.parent
        db_path = project_root / "cortex-brain" / "tier2" / "knowledge_graph.db"
    
    # Execute migration
    try:
        migration = BoundaryMigration(db_path, dry_run=args.dry_run)
        stats = migration.execute_migration()
        migration.print_summary(stats)
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
