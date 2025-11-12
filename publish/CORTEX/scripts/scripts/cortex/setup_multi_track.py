"""
CORTEX Multi-Track Configuration CLI

Initialize or manage multi-track development mode.

Usage:
    python scripts/cortex/setup_multi_track.py --machines AHHOME "Asifs-MacBook-Pro.local"
    python scripts/cortex/setup_multi_track.py --reset

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.operations.modules.design_sync import (
    TrackConfigManager,
    TrackNameGenerator
)
import yaml


def initialize_multi_track(machines: list[str]):
    """Initialize multi-track configuration."""
    print("🏁 Initializing Multi-Track Development Mode")
    print(f"   Machines: {', '.join(machines)}")
    print()
    
    # Load cortex-operations.yaml for module definitions
    operations_path = project_root / 'cortex-operations.yaml'
    with open(operations_path) as f:
        ops_data = yaml.safe_load(f)
    modules = ops_data.get('modules', {})
    
    # Create multi-track config
    config_path = project_root / 'cortex.config.json'
    config = TrackConfigManager.create_multi_track_config(
        machines=machines,
        modules=modules,
        config_path=config_path
    )
    
    print("✅ Multi-track configuration created!")
    print()
    print("📊 Track Assignments:")
    print()
    
    for track_id, track in config.tracks.items():
        print(f"   {track.emoji} {track.track_name}")
        print(f"      Machine: {', '.join(track.machines)}")
        print(f"      Phases: {', '.join(track.phases)}")
        print(f"      Modules: {len(track.modules)} modules")
        print(f"      Estimated: {track.estimated_hours:.1f} hours")
        print()
    
    print("🎯 Next Steps:")
    print()
    print("   1. On each machine, run:")
    print("      /CORTEX design sync")
    print()
    print("   2. Work on your assigned track:")
    print(f"      /CORTEX continue implementation for {list(config.tracks.values())[0].track_name.lower()}")
    print()
    print("   3. To consolidate progress later:")
    print("      /CORTEX design sync")
    print()


def reset_to_single_track():
    """Reset to single-track mode."""
    print("🔄 Resetting to Single-Track Mode")
    
    config_path = project_root / 'cortex.config.json'
    config = TrackConfigManager.load_from_config(config_path)
    
    if not config.is_multi_track:
        print("   Already in single-track mode!")
        return
    
    # Reset mode
    config.mode = 'single'
    TrackConfigManager.save_to_config(config, config_path)
    
    print("✅ Reset complete! Now in single-track mode.")
    print()


def show_current_config():
    """Display current track configuration."""
    config_path = project_root / 'cortex.config.json'
    config = TrackConfigManager.load_from_config(config_path)
    
    if not config.is_multi_track:
        print("📋 Current Mode: Single-Track")
        print("   (Standard linear development)")
        return
    
    print("📋 Current Mode: Multi-Track")
    print()
    
    for track_id, track in config.tracks.items():
        metrics = track.metrics
        print(f"   {track.emoji} {track.track_name}")
        print(f"      Machine: {', '.join(track.machines)}")
        print(f"      Progress: {metrics.modules_completed}/{metrics.modules_total} ({metrics.completion_percentage:.0f}%)")
        print(f"      Velocity: {metrics.velocity:.1f} modules/day")
        print(f"      Status: {metrics.status_emoji}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="CORTEX Multi-Track Configuration Manager"
    )
    
    parser.add_argument(
        '--machines',
        nargs='+',
        help='Machine hostnames to create tracks for'
    )
    
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset to single-track mode'
    )
    
    parser.add_argument(
        '--show',
        action='store_true',
        help='Show current configuration'
    )
    
    args = parser.parse_args()
    
    if args.reset:
        reset_to_single_track()
    elif args.show:
        show_current_config()
    elif args.machines:
        initialize_multi_track(args.machines)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
