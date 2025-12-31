"""Quick fix for test file indentation and import issues"""
from pathlib import Path
import re

def fix_test_file(file_path: Path):
    """Fix indentation and duplicate imports in test file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove duplicate import blocks
    content = re.sub(
        r'(from tests\.fixtures\.skull_framework import[^)]+\)[^\n]*\n)\s*\1+',
        r'\1',
        content
    )
    
    # Fix indented @pytest.fixture lines (should not be indented)
    content = re.sub(
        r'(\n\s+)(@pytest\.fixture\(autouse=True\))',
        r'\n    \2',
        content
    )
    
    # Write fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    test_dir = Path('tests/tier0')
    fixed = 0
    
    for test_file in test_dir.glob('test_*.py'):
        try:
            fix_test_file(test_file)
            fixed += 1
        except Exception as e:
            print(f"[ERROR] {test_file.name}: {e}")
    
    print(f"[OK] Fixed {fixed} test files")

if __name__ == '__main__':
    main()
