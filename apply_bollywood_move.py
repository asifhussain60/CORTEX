"""
Quick apply script for Bollywood party song move operation.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from move_bollywood_party_songs import BollywoodPartyMover

def main():
    source_dir = Path(r"C:\Users\asifh\Videos\4K Video Downloader+")
    dest_dir = Path(r"Z:\MUSIC\Bollywood\Party & Dance")
    
    mover = BollywoodPartyMover(
        source_dir=source_dir,
        dest_dir=dest_dir,
        dry_run=False,  # APPLY MODE
    )
    
    stats = mover.run_workflow()
    
    if stats.errors:
        print(f"\n⚠️  Completed with {len(stats.errors)} errors")
        return 1
    else:
        print("\n✅ All operations successful!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
