"""
Tier 3 Database Schema Migration 006: Adoption Analytics Tables

Adds tables for adoption analytics system:
- copilot_metrics
- cortex_usage_metrics  
- team_aggregations
- adoption_insights
- correlation_data

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

MIGRATION_VERSION = 6
MIGRATION_NAME = "adoption_analytics_tables"


def upgrade(conn):
    """Apply migration to add adoption analytics tables."""
    cursor = conn.cursor()
    
    # Table 1: Copilot Metrics (already created by CopilotMetricsCollector, ensure it exists)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS copilot_metrics (
            metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_date DATE NOT NULL,
            engineer_hash TEXT,
            language TEXT,
            suggestions_shown INTEGER DEFAULT 0,
            suggestions_accepted INTEGER DEFAULT 0,
            acceptance_rate REAL,
            inline_completions INTEGER DEFAULT 0,
            chat_interactions INTEGER DEFAULT 0,
            avg_suggestion_latency_ms REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(metric_date, engineer_hash, language)
        )
    """)
    
    # Table 2: CORTEX Usage Metrics (already created by CortexUsageTracker, ensure it exists)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cortex_usage_metrics (
            metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_date DATE NOT NULL,
            engineer_hash TEXT,
            intent_type TEXT,
            requests_count INTEGER DEFAULT 0,
            successful_count INTEGER DEFAULT 0,
            failed_count INTEGER DEFAULT 0,
            avg_response_time_seconds REAL,
            tokens_consumed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(metric_date, engineer_hash, intent_type)
        )
    """)
    
    # Table 3: Team Aggregations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS team_aggregations (
            aggregation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_date DATE NOT NULL,
            engineers_count INTEGER,
            total_commits INTEGER,
            total_copilot_suggestions INTEGER,
            total_cortex_requests INTEGER,
            avg_acceptance_rate REAL,
            avg_cortex_success_rate REAL,
            cost_savings_usd REAL,
            metadata_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(report_date)
        )
    """)
    
    # Table 4: Adoption Insights
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS adoption_insights (
            insight_id INTEGER PRIMARY KEY AUTOINCREMENT,
            insight_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            recommendation TEXT,
            related_entity TEXT,
            data_snapshot_json TEXT,
            acknowledged BOOLEAN DEFAULT 0,
            dismissed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
    """)
    
    # Table 5: Correlation Data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS correlation_data (
            correlation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            correlation_name TEXT NOT NULL,
            metric_a TEXT NOT NULL,
            metric_b TEXT NOT NULL,
            coefficient REAL,
            sample_size INTEGER,
            confidence_level REAL,
            insight TEXT,
            computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(correlation_name, metric_a, metric_b)
        )
    """)
    
    # Create indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_copilot_date ON copilot_metrics(metric_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_copilot_engineer ON copilot_metrics(engineer_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cortex_usage_date ON cortex_usage_metrics(metric_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cortex_usage_engineer ON cortex_usage_metrics(engineer_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cortex_usage_intent ON cortex_usage_metrics(intent_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_team_agg_date ON team_aggregations(report_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_insights_type ON adoption_insights(insight_type, created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_insights_severity ON adoption_insights(severity)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_correlation_name ON correlation_data(correlation_name)")
    
    # Create migration tracking table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            migration_id INTEGER PRIMARY KEY AUTOINCREMENT,
            version INTEGER NOT NULL UNIQUE,
            name TEXT NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Record this migration
    cursor.execute("""
        INSERT OR IGNORE INTO schema_migrations (version, name)
        VALUES (?, ?)
    """, (MIGRATION_VERSION, MIGRATION_NAME))
    
    conn.commit()
    print(f"✅ Migration {MIGRATION_VERSION} ({MIGRATION_NAME}) applied successfully")
    print(f"   - copilot_metrics table ready")
    print(f"   - cortex_usage_metrics table ready")
    print(f"   - team_aggregations table created")
    print(f"   - adoption_insights table created")
    print(f"   - correlation_data table created")
    print(f"   - 9 indexes created for query optimization")


def downgrade(conn):
    """Rollback migration to remove adoption analytics tables."""
    cursor = conn.cursor()
    
    # Drop tables in reverse order (respecting potential foreign keys)
    cursor.execute("DROP TABLE IF EXISTS correlation_data")
    cursor.execute("DROP TABLE IF EXISTS adoption_insights")
    cursor.execute("DROP TABLE IF EXISTS team_aggregations")
    # Note: We don't drop copilot_metrics or cortex_usage_metrics as they contain valuable data
    
    # Remove migration record
    cursor.execute("DELETE FROM schema_migrations WHERE version = ?", (MIGRATION_VERSION,))
    
    conn.commit()
    print(f"✅ Migration {MIGRATION_VERSION} ({MIGRATION_NAME}) rolled back")
    print(f"   - correlation_data table dropped")
    print(f"   - adoption_insights table dropped")
    print(f"   - team_aggregations table dropped")
    print(f"   ⚠️  copilot_metrics and cortex_usage_metrics preserved (data retention)")


def get_version():
    """Get migration version number."""
    return MIGRATION_VERSION


def get_name():
    """Get migration name."""
    return MIGRATION_NAME


if __name__ == "__main__":
    import sqlite3
    import sys
    from pathlib import Path
    
    # Default to CORTEX Tier 3 database
    default_db = Path(__file__).parent.parent.parent.parent / "cortex-brain" / "tier3" / "development_context.db"
    db_path = sys.argv[1] if len(sys.argv) > 1 else default_db
    
    print(f"📊 Running migration on: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
    try:
        # Check if migration already applied
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='schema_migrations'
        """)
        
        if cursor.fetchone():
            cursor.execute("SELECT version FROM schema_migrations WHERE version = ?", (MIGRATION_VERSION,))
            if cursor.fetchone():
                print(f"⚠️  Migration {MIGRATION_VERSION} already applied. Skipping.")
                sys.exit(0)
        
        # Apply migration
        upgrade(conn)
        
        # Verify tables created
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN (
                'copilot_metrics', 
                'cortex_usage_metrics', 
                'team_aggregations', 
                'adoption_insights', 
                'correlation_data'
            )
            ORDER BY name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\n✅ Verification: {len(tables)}/5 tables confirmed")
        for table in tables:
            print(f"   - {table}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()
