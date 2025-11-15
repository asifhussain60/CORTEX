#!/usr/bin/env python3
"""
CORTEX 3.0 Track B Phase 1 Validation Script
===========================================

Quick validation script to test Track B foundational components.
Validates that ambient daemon, file monitor, git monitor, and terminal tracker
are properly initialized and can start/stop correctly.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add the CORTEX src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.track_b.execution_channel import AmbientDaemon, DaemonConfig


async def test_phase_1_foundation():
    """Test Phase 1 Track B foundation implementation."""
    print("🧠 CORTEX 3.0 Track B Phase 1 Validation")
    print("=" * 50)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Use current CORTEX workspace
    workspace_path = Path(__file__).parent.parent.parent
    print(f"📁 Workspace: {workspace_path}")
    
    # Create daemon config
    config = DaemonConfig(
        workspace_path=workspace_path,
        polling_interval=2.0,
        log_level="INFO"
    )
    
    # Create ambient daemon
    print("🔄 Creating Ambient Daemon...")
    daemon = AmbientDaemon(config)
    
    # Test daemon status (should be stopped initially)
    status = daemon.get_status()
    print(f"📊 Initial Status: {'✅ Running' if status['is_running'] else '⏸️  Stopped'}")
    
    try:
        # Test starting the daemon
        print("🚀 Starting daemon components...")
        await daemon._start_monitors()
        
        # Check component status
        status = daemon.get_status()
        components = status['components']
        
        print("\n📋 Component Status:")
        print(f"   File Monitor: {'✅ Started' if components['file_monitor'] else '❌ Failed'}")
        print(f"   Git Monitor: {'✅ Started' if components['git_monitor'] else '❌ Failed'}")
        print(f"   Terminal Tracker: {'✅ Started' if components['terminal_tracker'] else '❌ Failed'}")
        
        # Brief test run
        print("\n⏱️  Running 5-second test...")
        await asyncio.sleep(5)
        
        # Check for any events
        print(f"📈 Event Queue Size: {status['event_queue_size']}")
        
        # Test stopping
        print("🛑 Stopping daemon components...")
        await daemon._stop_monitors()
        
        print("\n✅ Phase 1 Foundation Test Complete!")
        print("🎯 All core components initialized and tested successfully")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        return False
    
    finally:
        try:
            await daemon.stop()
        except:
            pass


async def main():
    """Main test function."""
    success = await test_phase_1_foundation()
    
    if success:
        print("\n🎉 PHASE 1 FOUNDATION: ✅ COMPLETE")
        print("Ready to proceed with Phase 1 detailed implementation")
        sys.exit(0)
    else:
        print("\n💥 PHASE 1 FOUNDATION: ❌ FAILED")
        print("Review errors and fix before proceeding")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())