"""
Quick audit script to check InteractionOrchestrator usage in SQLite traces.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

def audit_orchestrator_traces():
    """Audit orchestrator traces database."""
    db_path = Path(".cortex/traces/orchestrator-traces.db")
    
    if not db_path.exists():
        print("❌ Traces database not found:", db_path)
        print("   Root Cause: Orchestrator tracing not initialized")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"\n📋 All Tables: {tables}")
    
    # Check registered orchestrators
    cursor.execute("SELECT table_name FROM trace_metadata ORDER BY table_name")
    registered = [t[0] for t in cursor.fetchall()]
    print(f"\n📊 Registered Orchestrators: {registered}")
    
    # Check registered orchestrators
    cursor.execute("SELECT table_name FROM trace_metadata ORDER BY table_name")
    registered = [t[0] for t in cursor.fetchall()]
    print(f"\n📊 Registered Orchestrators: {registered}")
    
    # Check if trace_interaction exists
    if "trace_interaction" in tables:
        cursor.execute("SELECT COUNT(*) FROM trace_interaction WHERE DATE(timestamp) = DATE('now')")
        count = cursor.fetchone()[0]
        print(f"\n✅ trace_interaction table exists")
        print(f"   Today's traces: {count}")
    elif "trace_interaction" in registered:
        print(f"\n⚠️  trace_interaction registered but table not created yet")
    else:
        print(f"\n❌ trace_interaction NOT found (table or registration)")
    
    if not tables:
        print("\n❌ No tables found in database")
        print("   Root Cause: Database exists but not initialized")
        conn.close()
        return
    
    # Check for orchestrator_traces table (doesn't exist - per-orchestrator tables used)
    # Query today's usage from ALL orchestrator tables
    all_traces_today = 0
    for table in tables:
        if table.startswith("trace_") and table not in ["trace_metadata", "trace_flush_log"]:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE DATE(timestamp) = DATE('now')")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"   {table}: {count} traces")
                    all_traces_today += count
            except Exception:
                pass
    
    print(f"\n📈 Total traces today (all orchestrators): {all_traces_today}")
    
    if "trace_interaction" not in tables:
        print("\n" + "=" * 70)
        print("❌ ROOT CAUSE: InteractionOrchestrator table NOT created")
        print("=" * 70)
        return
    
    # Check InteractionOrchestrator specifically
    cursor.execute("""
        SELECT COUNT(*) 
        FROM trace_interaction
        WHERE DATE(timestamp) = DATE('now')
    """)
    
    interaction_count = cursor.fetchone()[0]
    
    print(f"\n🎯 InteractionOrchestrator: {interaction_count} invocations today")
    
    if interaction_count == 0:
        print("\n" + "=" * 70)
        print("❌ ROOT CAUSE IDENTIFIED: InteractionOrchestrator NOT used")
        print("=" * 70)
        print("\nExpected Flow:")
        print("  User Request → Copilot Chat → InteractionOrchestrator → LENS → Response")
        print("\nActual Flow:")
        print("  User Request → Copilot Chat → Direct Agent (BYPASSING InteractionOrchestrator)")
        print("\n🔍 Evidence:")
        print("  • SQLite traces show 0 InteractionOrchestrator invocations today")
        print("  • This session had ~27 user requests")
        print("  • Expected: ~27 InteractionOrchestrator traces")
        print("  • Actual: 0 traces")
        print("\n⚠️  Impact:")
        print("  • LENS per-turn analysis NOT running")
        print("  • Challenge generation NOT triggered")
        print("  • Context synthesis NOT happening")
        print("  • Orchestration layer bypassed completely")
        print("\n🔧 Fix Required:")
        print("  1. Verify InteractionOrchestrator wired in MasterOrchestrator")
        print("  2. Check intent routing in IntentRouter")
        print("  3. Ensure MCP gateway routes through InteractionOrchestrator")
        print("  4. Add tracing calls in InteractionOrchestrator.execute()")
    
    conn.close()

if __name__ == "__main__":
    audit_orchestrator_traces()
