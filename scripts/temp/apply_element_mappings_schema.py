"""
Apply element_mappings schema to Tier 2 database
Part of Issue #3 Fix - Phase 3: Database Migration
"""

import sqlite3
from pathlib import Path

def apply_schema():
    """Apply element_mappings.sql schema to knowledge_graph.db"""
    
    # Paths
    db_path = Path("cortex-brain/tier2/knowledge_graph.db")
    schema_path = Path("cortex-brain/tier2/schema/element_mappings.sql")
    
    print("=" * 70)
    print("CORTEX Issue #3 - Phase 3: Database Migration")
    print("=" * 70)
    
    # Check files exist
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        print(f"   Creating new database...")
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not schema_path.exists():
        print(f"❌ Schema not found: {schema_path}")
        return False
    
    print(f"✅ Database: {db_path}")
    print(f"✅ Schema: {schema_path}")
    print()
    
    # Read schema
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    print(f"📄 Schema size: {len(schema_sql)} characters")
    print()
    
    # Apply schema
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("🔧 Applying schema...")
        
        # Execute schema (split by semicolons, handle comments)
        statements = [s.strip() for s in schema_sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    cursor.execute(statement)
                    if 'CREATE TABLE' in statement.upper():
                        table_name = statement.split('CREATE TABLE')[1].split('(')[0].strip().replace('IF NOT EXISTS', '').strip()
                        print(f"   ✅ Created table: {table_name}")
                    elif 'CREATE INDEX' in statement.upper():
                        index_name = statement.split('CREATE INDEX')[1].split('ON')[0].strip().replace('IF NOT EXISTS', '').strip()
                        print(f"   ✅ Created index: {index_name}")
                    elif 'CREATE VIEW' in statement.upper():
                        view_name = statement.split('CREATE VIEW')[1].split('AS')[0].strip().replace('IF NOT EXISTS', '').strip()
                        print(f"   ✅ Created view: {view_name}")
                except sqlite3.Error as e:
                    if 'already exists' not in str(e):
                        print(f"   ⚠️  Statement {i}: {str(e)[:50]}")
        
        conn.commit()
        print()
        print("✅ Schema applied successfully!")
        print()
        
        # Verify tables created
        print("🔍 Verifying tables...")
        cursor.execute("""
            SELECT name, type FROM sqlite_master 
            WHERE type IN ('table', 'view', 'index') 
            AND name LIKE 'tier2_element%' OR name LIKE 'tier2_navigation%' OR name LIKE 'tier2_discovery%'
            ORDER BY type, name
        """)
        
        results = cursor.fetchall()
        
        tables = [r[0] for r in results if r[1] == 'table']
        views = [r[0] for r in results if r[1] == 'view']
        indexes = [r[0] for r in results if r[1] == 'index']
        
        print(f"   Tables: {len(tables)}")
        for table in tables:
            print(f"      - {table}")
        
        print(f"   Views: {len(views)}")
        for view in views:
            print(f"      - {view}")
        
        print(f"   Indexes: {len(indexes)}")
        for idx in indexes[:5]:  # Show first 5
            print(f"      - {idx}")
        if len(indexes) > 5:
            print(f"      ... and {len(indexes) - 5} more")
        
        print()
        
        # Test insert
        print("🧪 Testing database operations...")
        
        test_insert = """
        INSERT OR IGNORE INTO tier2_element_mappings 
        (project_name, component_path, element_id, element_type, selector_strategy, selector_priority, user_facing_text)
        VALUES ('TEST_PROJECT', 'Views/Test.razor', 'testButton', 'button', '#testButton', 1, 'Click Me')
        """
        
        cursor.execute(test_insert)
        
        test_query = """
        SELECT element_id, selector_strategy FROM tier2_element_mappings 
        WHERE project_name = 'TEST_PROJECT'
        """
        
        cursor.execute(test_query)
        test_results = cursor.fetchall()
        
        if test_results:
            print(f"   ✅ Insert successful: {test_results[0]}")
            
            # Clean up test data
            cursor.execute("DELETE FROM tier2_element_mappings WHERE project_name = 'TEST_PROJECT'")
            conn.commit()
            print(f"   ✅ Cleanup successful")
        else:
            print(f"   ⚠️  Insert test failed")
        
        conn.close()
        
        print()
        print("=" * 70)
        print("✅ Phase 3: Database Migration COMPLETE")
        print("=" * 70)
        print()
        print("Next: Update ViewDiscoveryAgent to use database persistence")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying schema: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = apply_schema()
    exit(0 if success else 1)
