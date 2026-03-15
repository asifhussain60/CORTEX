"""Extract Plex token from local config."""
from pathlib import Path
import re

config_paths = [
    Path.home() / "AppData/Local/Plex Media Server/Preferences.xml",
    Path.home() / "AppData/Roaming/Plex Media Server/Preferences.xml", 
    Path("C:/ProgramData/Plex Media Server/Preferences.xml"),
    Path("C:/Program Files/Plex/Plex Media Server/Preferences.xml"),
]

print("Searching for Plex configuration...")
for config_path in config_paths:
    print(f"  Checking: {config_path}")
    if config_path.exists():
        print(f"\n✅ Found Plex config: {config_path}")
        content = config_path.read_text(encoding="utf-8")
        
        match = re.search(r'PlexOnlineToken="([^"]+)"', content)
        if match:
            token = match.group(1)
            print(f"\n✅ Plex Token Found!")
            print(f"Token (first 20 chars): {token[:20]}...")
            print(f"\nTo use with refresh script:")
            print(f'  python scripts/plex_library_refresh.py --token "{token}" --list')
            
            # Save to temp file for easy access
            token_file = Path("plex_token.txt")
            token_file.write_text(token)
            print(f"\n✅ Token saved to: {token_file.absolute()}")
            exit(0)
        else:
            print("❌ PlexOnlineToken not found in config file")
            exit(1)

print("\n❌ Plex config not found in any standard location")
print("\nAlternative: Get token from Plex Web Interface:")
print("  1. Open Plex in browser")
print("  2. Sign in")
print("  3. Open any media item")
print("  4. Click '...' > Get Info > View XML")
print("  5. Look for X-Plex-Token in URL")
