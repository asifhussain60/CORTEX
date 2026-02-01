#!/usr/bin/env python3
"""Fix secret in git history by rewriting specific commit."""
import subprocess
import sys

# The commit that needs fixing
TARGET_COMMIT = "5d5359553bc53e26d2e819f8ebe6f6425331d631"
FILE_TO_FIX = "tests/unit/brain/analysis/test_config_analyzer.py"

def run_command(cmd):
    """Run shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

# Use git filter-repo to rewrite history
filter_cmd = f"""git filter-branch --force --tree-filter "if [ -f '{FILE_TO_FIX}' ]; then sed -i 's/sk_live_/test_key_/g' '{FILE_TO_FIX}'; fi" -- 95708de3e..HEAD"""

print(f"Rewriting git history to remove secret from {TARGET_COMMIT}...")
print(f"Command: {filter_cmd}")

code, out, err = run_command(filter_cmd)
print(out)
if err:
    print(err, file=sys.stderr)

if code == 0:
    print("\n✅ History rewritten successfully!")
    print("You can now push with: git push origin CORTEX --force-with-lease")
else:
    print(f"\n❌ Failed with exit code {code}")
    sys.exit(1)
