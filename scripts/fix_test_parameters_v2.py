"""
Fix ModificationRequest parameters in tier0 tests (v2).
Handles target_path, content, and other invalid parameters.
"""
import re
from pathlib import Path

def fix_modification_request_v2(content: str) -> str:
    """Fix ModificationRequest instantiation with proper parameters."""
    
    # Replace patterns:
    # target_path=... -> files=[str(...)]
    content = re.sub(
        r'target_path=([^,\n]+)',
        r'files=[str(\1)]',
        content
    )
    
    # Remove content= parameter entirely (put it in description instead)
    # This is trickier - need to extract content and merge with description
    lines = content.split('\n')
    fixed_lines = []
    skip_until_comma = False
    
    for i, line in enumerate(lines):
        if skip_until_comma:
            if ',' in line or ')' in line:
                skip_until_comma = False
            continue
            
        if 'content="""' in line or "content='''" in line:
            # Skip multi-line content parameter
            skip_until_comma = True
            continue
        elif 'content="' in line or "content='" in line:
            # Skip single-line content parameter
            continue
            
        fixed_lines.append(line)
    
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
    fixed = fix_modification_request_v2(original)
    
    if fixed != original:
        p.write_text(fixed, encoding='utf-8')
        changes = len([1 for a, b in zip(original.split('\n'), fixed.split('\n')) if a != b])
        print(f'✅ Fixed {file_path} ({changes} lines changed)')
    else:
        print(f'⏭️  No changes needed: {file_path}')

print('\n✅ Test parameter fixes v2 complete!')
