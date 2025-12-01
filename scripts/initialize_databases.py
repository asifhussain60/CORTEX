"""
Initialize CORTEX database files.

This script creates the required database files for CORTEX's 3-tier memory architecture:
- tier1/working_memory.db (Working Memory)
- tier2/knowledge_graph.db (Knowledge Graph)
- tier3/development_context.db (Context Intelligence)

The classes handle schema initialization automatically via CREATE TABLE IF NOT EXISTS.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tier1.working_memory import WorkingMemory
from tier2.knowledge_graph import KnowledgeGraph
from tier3.context_intelligence import ContextIntelligence

def initialize_databases():
    """Initialize all three tier databases."""
    brain_path = Path(__file__).parent / "cortex-brain"
    
    print("🧠 CORTEX Database Initialization")
    print("=" * 50)
    
    # Tier 1: Working Memory
    print("\n📊 Initializing Tier 1: Working Memory...")
    tier1_db = brain_path / "tier1" / "working_memory.db"
    try:
        wm = WorkingMemory(db_path=tier1_db)
        if wm.initialize():
            print(f"   ✅ Created: {tier1_db}")
        else:
            print(f"   ❌ Failed to initialize Tier 1")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Tier 2: Knowledge Graph
    print("\n🕸️  Initializing Tier 2: Knowledge Graph...")
    tier2_db = brain_path / "tier2" / "knowledge_graph.db"
    try:
        kg = KnowledgeGraph(db_path=str(tier2_db))
        print(f"   ✅ Created: {tier2_db}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Tier 3: Context Intelligence
    print("\n🎯 Initializing Tier 3: Context Intelligence...")
    tier3_db = brain_path / "tier3" / "development_context.db"
    try:
        ci = ContextIntelligence(db_path=tier3_db)
        print(f"   ✅ Created: {tier3_db}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All databases initialized successfully!")
    print("\nYou can now run: python -m src.main optimize")
    return True

if __name__ == "__main__":
    success = initialize_databases()
    sys.exit(0 if success else 1)
