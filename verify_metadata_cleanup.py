"""Verify metadata cleanup on Bollywood files."""
from mutagen.mp4 import MP4
from pathlib import Path

# Check a few sample files that had additive words removed
sample_files = [
    "Aaj Ki Raat.mp4",
    "Balma.mp4",
    "Achacho.mp4",
    "Desi Look.mp4",
    "Dum Dum.mp4",
]

target_dir = Path(r"Z:\MUSIC\Bollywood\Bollywood Hits")

print("Verifying metadata cleanup on sample files:")
print("=" * 100)
print(f"{'Filename':<40} | {'Title Tag':<30} | {'Collection':<25}")
print("=" * 100)

for filename in sample_files:
    file_path = target_dir / filename
    if file_path.exists():
        try:
            audio = MP4(str(file_path))
            title = audio.get("©nam", ["Unknown"])[0]
            collection = audio.get("©col", ["Not set"])[0]
            print(f"{filename:<40} | {title:<30} | {collection:<25}")
        except Exception as e:
            print(f"{filename:<40} | ERROR: {e}")

print("=" * 100)
