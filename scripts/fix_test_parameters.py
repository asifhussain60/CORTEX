"""
Fix deprecated 'operation' parameter in tier0 tests.
Replaces operation= with intent= and adds description parameter.
"""
import re
from pathlib import Path

def fix_modification_request(content: str) -> str:
    """Fix ModificationRequest instantiation in test files."""
    
    # Pattern 1: operation="value" -> intent="value"
    content = re.sub(
        r'(\s+)operation="([^"]+)"',
        r'\1intent="\2"',
        content
    )
    
    # Pattern 2: operation='value' -> intent='value'
    content = re.sub(
        r"(\s+)operation='([^']+)'",
        r"\1intent='\2'",
        content
    )
    
    # Pattern 3: Add description if missing and intent exists
    # Look for ModificationRequest blocks without description
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        fixed_lines.append(line)
        
        # If we find intent= and next lines don't have description=
        if 'intent=' in line and 'ModificationRequest' in ''.join(lines[max(0, i-3):i+1]):
            # Look ahead to see if description exists
            has_description = False
            for j in range(i+1, min(i+5, len(lines))):
                if 'description=' in lines[j] or ')' in lines[j]:
                    has_description = 'description=' in lines[j]
                    break
            
            # If target_path or content is next, add description before it
            if not has_description and i+1 < len(lines):
                next_line = lines[i+1]
                if 'target_path=' in next_line or 'content=' in next_line or 'files=' in next_line:
                    indent = len(next_line) - len(next_line.lstrip())
                    fixed_lines.append(' ' * indent + 'description="Modification for testing",')
        
        i += 1
    
    return '\n'.join(fixed_lines)

# Fix all test files
test_files = [
    'tests/tier0/test_brain_protector_context_management.py',
    'tests/tier0/test_brain_protector_multi_template.py',
    'tests/tier0/test_brain_protector_template_architecture.py'
]

for file_path in test_files:
    p = Path(file_path)
    if not p.exists():
        print(f'❌ Not found: {file_path}')
        continue
    
    original = p.read_text(encoding='utf-8')
    fixed = fix_modification_request(original)
    
    if fixed != original:
        p.write_text(fixed, encoding='utf-8')
        changes = sum(1 for a, b in zip(original.split('\n'), fixed.split('\n')) if a != b)
        print(f'✅ Fixed {file_path} ({changes} lines changed)')
    else:
        print(f'⏭️  No changes needed: {file_path}')

print('\n✅ Test parameter fixes complete!')
