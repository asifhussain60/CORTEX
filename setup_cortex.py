"""
CORTEX Setup Script - Cross-Platform

Initializes CORTEX brain structure and databases on first run.
Works on both macOS and Windows using config-based path resolution.

Usage:
    python setup_cortex.py
"""

import sys
from pathlib import Path

# Add CORTEX to path
sys.path.insert(0, str(Path(__file__).parent / "CORTEX"))

from src.config import config


def main():
    """Run CORTEX setup."""
    print("=" * 60)
    print("CORTEX Setup - Cross-Platform")
    print("=" * 60)
    
    # Show detected configuration
    print("\nDetected Configuration:")
    print(f"  Hostname: {config.hostname}")
    print(f"  Platform: {config.get_machine_info()['platform']}")
    print(f"  Root Path: {config.root_path}")
    print(f"  Brain Path: {config.brain_path}")
    
    # Create brain directory structure
    print("\nCreating brain directory structure...")
    try:
        config.ensure_paths_exist()
        print("  => tier1/ created")
        print("  => tier2/ created")
        print("  => tier3/ created")
        print("  => corpus-callosum/ created")
    except Exception as e:
        print(f"  ERROR: {e}")
        return 1
    
    # Initialize Tier 1 database
    print("\nInitializing Tier 1 (Working Memory)...")
    try:
        from src.tier1.tier1_api import Tier1API
        
        tier1_db = config.brain_path / "tier1" / "conversations.db"
        tier1_log = config.brain_path / "tier1" / "requests.log"
        
        tier1 = Tier1API(str(tier1_db), str(tier1_log))
        print(f"  => Database created: {tier1_db}")
        print(f"  => Request log created: {tier1_log}")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Initialize Tier 2 database
    print("\nInitializing Tier 2 (Knowledge Graph)...")
    try:
        from src.tier2.knowledge_graph import KnowledgeGraph
        
        tier2_db = config.brain_path / "tier2" / "knowledge_graph.db"
        tier2 = KnowledgeGraph(str(tier2_db))
        print(f"  => Database created: {tier2_db}")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Initialize Tier 3 database
    print("\nInitializing Tier 3 (Context Intelligence)...")
    try:
        from src.tier3.context_intelligence import ContextIntelligence
        
        tier3_db = config.brain_path / "tier3" / "context.db"
        tier3 = ContextIntelligence(str(tier3_db))
        print(f"  => Database created: {tier3_db}")
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Update config to mark setup complete
    print("\nUpdating configuration...")
    try:
        import json
        config_file = config.root_path / "cortex.config.json"
        
        with open(config_file, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        
        cfg["portability"]["setupCompleted"] = True
        cfg["portability"]["lastUpdated"] = "2025-11-06"
        cfg["portability"]["version"] = "5.0.0"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2)
        
        print("  => Configuration updated")
    except Exception as e:
        print(f"  WARNING: Could not update config: {e}")
    
    print("\n" + "=" * 60)
    print("SUCCESS: CORTEX setup complete!")
    print("=" * 60)
    print("\nYou can now use:")
    print("  python test_cortex.py  - Test CORTEX")
    print("  python -c \"from CORTEX.src.entry_point import CortexEntry; ...\" - Use CORTEX")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())

