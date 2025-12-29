"""
Fix YAML encoding issues for Track 2 Phase B1.1
Converts YAML files to UTF-8 encoding to prevent parse errors
"""

import sys
from pathlib import Path

def fix_encoding(filepath: str):
    """Fix encoding issues in YAML file"""
    path = Path(filepath)
    
    try:
        # Read with error handling
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Write back as clean UTF-8
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Fixed encoding: {path.name}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix {path.name}: {e}")
        return False

if __name__ == "__main__":
    files = [
        "cortex-brain/protection/brain-protection-rules.yaml",
        "cortex-brain/learning/knowledge-graph.yaml"
    ]
    
    success_count = 0
    for file in files:
        if fix_encoding(file):
            success_count += 1
    
    print(f"\n📊 Fixed {success_count}/{len(files)} files")
    sys.exit(0 if success_count == len(files) else 1)
