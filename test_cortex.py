"""
CORTEX Test Runner - Cross-Platform

Tests CORTEX entry point on current machine with config-based path resolution.
Works on both macOS and Windows.

Usage:
    python test_cortex.py
"""

import sys
from pathlib import Path

# Add CORTEX to path
sys.path.insert(0, str(Path(__file__).parent / "CORTEX"))

from src.config import config
from src.entry_point import CortexEntry


def main():
    """Run CORTEX test."""
    print("=" * 60)
    print("CORTEX Entry Point Test")
    print("=" * 60)
    
    # Show machine info
    print("\nMachine Configuration:")
    machine_info = config.get_machine_info()
    for key, value in machine_info.items():
        print(f"  {key}: {value}")
    
    # Initialize CORTEX
    print("\nInitializing CORTEX...")
    try:
        cortex = CortexEntry()
        print("=> CortexEntry initialized successfully!")
    except Exception as e:
        print(f"ERROR: Failed to initialize: {e}")
        return 1
    
    # Test health check
    print("\nChecking system health...")
    try:
        health = cortex.get_health_status()
        print(f"  Overall Status: {health['overall_status']}")
        print(f"  Tier 1: {health['tiers'].get('tier1', {}).get('status', 'unknown')}")
        print(f"  Tier 2: {health['tiers'].get('tier2', {}).get('status', 'unknown')}")
        print(f"  Tier 3: {health['tiers'].get('tier3', {}).get('status', 'unknown')}")
    except Exception as e:
        print(f"WARNING: Health check failed: {e}")
    
    # Test simple request
    print("\nProcessing test request...")
    try:
        response = cortex.process(
            "What can you help me with?",
            resume_session=False
        )
        print("=> Request processed!")
        print(f"\nResponse preview:")
        print(response[:500] + "..." if len(response) > 500 else response)
    except Exception as e:
        print(f"ERROR: Request processing failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "=" * 60)
    print("SUCCESS: CORTEX is operational on this machine!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())

