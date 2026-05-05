"""
Preview script: shows 50 random proposed flat filenames for Bollywood library.
Run: python scripts/flatten_preview.py
"""
import random
from pathlib import Path

STOP_WORDS = {
    # Collaborator markers
    "feat", "ft", "featuring",
    # Common artists
    "badshah", "guru", "randhawa", "nora", "fatehi", "tiger", "shroff",
    "neha", "kakkar", "diljit", "shreya", "ghoshal", "sunidhi", "chauhan",
    "salman", "akshay", "hrithik", "roshan", "priyanka", "chopra",
    "varun", "dhawan", "tanishk", "zahrah", "sukumar", "samantha",
    "rashmika", "bhushan", "danish", "alfaaz", "bohemia", "malviya",
    "jacqueline", "fernandez", "shikhar", "prabhu", "deva",
    "mika", "dsp", "ranveer", "vijay", "deverakonda", "ananya", "panday", "allu",
    "payal", "raftaar", "milind", "soman", "aasthagill", "akasasingofficial",
    "palak", "tiwari", "jaani", "bpraak", "arvindr", "khaira",
    "neelkamal", "soundarya", "simar", "paradox",
    # Movies / labels
    "liger", "baaghi", "fighter", "pushpa", "devara", "khiladi",
    "bhaag", "johnny", "aranmanai", "vikrant", "rona", "robinhood",
    "ismart", "shankar", "dhamaal", "namaste", "england", "series",
    "wajah", "tum",
    # Genre / label noise
    "habibi", "arabic", "afro", "house", "reggaeton", "drop",
    "haryanvi", "melodies", "ankitvlog", "viruss", "desi",
    "playlist", "songs", "video", "music", "official",
}


def clean_title(stem: str, max_len: int = 25) -> str:
    words = stem.split()
    kept = []
    for w in words:
        if w.lower() in STOP_WORDS:
            break
        kept.append(w)
    if not kept:
        kept = words[:1]
    title = " ".join(w.title() for w in kept)
    if len(title) > max_len:
        truncated = title[: max_len + 1]
        last_space = truncated.rfind(" ")
        title = title[:last_space] if last_space > 0 else title[:max_len]
    return title.strip()


def main():
    src = Path("Z:/MUSIC/Bollywood")
    files = list(src.rglob("*.mp4"))
    print(f"Total files found: {len(files)}\n")

    random.seed(42)
    sample = random.sample(files, min(50, len(files)))
    sample.sort(key=lambda f: f.stem.lower())

    print(f"{'#':<3} {'ORIGINAL FILENAME':<52} | {'PROPOSED TITLE (≤25 chars)':<27} | LEN")
    print("-" * 90)
    for i, f in enumerate(sample, 1):
        c = clean_title(f.stem)
        flag = "  *** OVER LIMIT" if len(c) > 25 else ""
        orig = f.stem[:51]
        print(f"{i:<3} {orig:<52} | {c:<27} | {len(c)}{flag}")

    print(f"\n--- All {len(files)} files, proposed title length distribution ---")
    all_cleaned = [clean_title(f.stem) for f in files]
    over = [t for t in all_cleaned if len(t) > 25]
    print(f"  Within 25 chars : {len(all_cleaned) - len(over)}")
    print(f"  Over 25 chars   : {len(over)}")
    if over:
        print("  Titles over limit:")
        for t in over:
            print(f"    [{len(t)}] {t}")


if __name__ == "__main__":
    main()
