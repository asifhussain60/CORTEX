#!/usr/bin/env python3
"""Execute POC plan phases sequentially."""
import sys
import subprocess
from pathlib import Path


def main():
    phases = [
        ("Phase 1: Hello World", "scripts/poc/phase_1_hello.py"),
        ("Phase 2: File Creation", "scripts/poc/phase_2_create_file.py"),
        ("Phase 3: Validation", "scripts/poc/phase_3_validate.py")
    ]
    
    print("🚀 Starting POC Plan Execution")
    print("=" * 60)
    
    for phase_name, script_path in phases:
        print(f"\n▶️  Executing: {phase_name}")
        print("-" * 60)
        
        result = subprocess.run(
            ["python3", script_path],
            capture_output=False,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ {phase_name} failed!")
            return 1
        
        print(f"✅ {phase_name} complete")
    
    print("\n" + "=" * 60)
    print("🎉 POC Plan Execution Complete!")
    print("🏆 Architecture validated: GitHub Copilot → Terminal → Python → Results")
    return 0


if __name__ == "__main__":
    sys.exit(main())
