"""Diagnose Plex metadata issue - why files showing as numbers."""
from mutagen.mp4 import MP4
from pathlib import Path

target_dir = Path(r"Z:\MUSIC\Bollywood\Bollywood Hits")

print("Diagnosing Plex metadata fields (sample of 10 files):")
print("=" * 120)
print(f"{'Filename':<40} | {'Title (©nam)':<25} | {'Track# (trkn)':<15} | {'Album':<20}")
print("=" * 120)

files = sorted(target_dir.rglob("*.mp4"))[:10]

for file_path in files:
    try:
        audio = MP4(str(file_path))
        
        # Extract metadata fields
        title = audio.get("\xa9nam", [""])[0] if "\xa9nam" in audio else "MISSING"
        track_num = audio.get("trkn", [("", "")])[0] if "trkn" in audio else "None"
        album = audio.get("\xa9alb", [""])[0] if "\xa9alb" in audio else "MISSING"
        
        # Format track number
        if track_num and track_num != "None":
            track_display = f"{track_num[0]}/{track_num[1]}" if isinstance(track_num, tuple) else str(track_num)
        else:
            track_display = "None"
        
        filename = file_path.name[:38]
        print(f"{filename:<40} | {title:<25} | {track_display:<15} | {album:<20}")
        
        # Show ALL metadata fields for first file
        if file_path == files[0]:
            print("\n" + "=" * 120)
            print(f"FULL METADATA for '{file_path.name}':")
            print("=" * 120)
            for key, value in audio.items():
                print(f"  {key}: {value}")
            print("=" * 120)
            print()
            
    except Exception as e:
        print(f"{file_path.name:<40} | ERROR: {e}")

print("\nPossible issues:")
print("  - If 'Track#' column shows numbers → Plex may be displaying track numbers instead of titles")
print("  - If 'Title' column shows 'MISSING' → Title tag not set properly")
print("  - Check if Plex is configured for 'Music Videos' library (needs different metadata)")
