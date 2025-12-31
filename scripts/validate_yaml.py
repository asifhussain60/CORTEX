"""Find and report YAML syntax errors in brain-protection-rules.yaml"""
import yaml
from pathlib import Path

skull_file = Path('cortex-brain/brain-protection-rules.yaml')

try:
    with open(skull_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    print("✅ YAML is valid!")
except yaml.parser.ParserError as e:
    print(f"❌ YAML Parser Error:")
    print(f"  Problem: {e.problem}")
    print(f"  Context: {e.context}")
    print(f"  Problem Mark: Line {e.problem_mark.line + 1}, Column {e.problem_mark.column + 1}")
    if e.context_mark:
        print(f"  Context Mark: Line {e.context_mark.line + 1}, Column {e.context_mark.column + 1}")
    
    # Show problematic lines
    with open(skull_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        start = max(0, e.problem_mark.line - 3)
        end = min(len(lines), e.problem_mark.line + 3)
        
        print(f"\n📋 Lines {start + 1} to {end + 1}:")
        for i in range(start, end):
            marker = " >>> " if i == e.problem_mark.line else "     "
            print(f"{marker}Line {i + 1}: {lines[i].rstrip()}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
