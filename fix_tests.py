"""Fix ModificationRequest tests by removing obsolete 'operation=' parameter."""
import re
from pathlib import Path

test_file = Path('tests/tier0/test_brain_protector_context_management.py')
content = test_file.read_text(encoding='utf-8')

# Replace operation= parameter with nothing
# Pattern: Find 'operation="modify",' with optional whitespace and newline
updated = re.sub(r'\s*operation="modify",\s*\n', '\n', content)

# Also handle cases where it might not have trailing comma
updated = re.sub(r'\s*operation="modify"\s*\n', '\n', updated)

# Write back
test_file.write_text(updated, encoding='utf-8')

# Count replacements
original_count = content.count('operation=')
updated_count = updated.count('operation=')

print(f'✅ Removed {original_count - updated_count} operation= parameters')
print(f'✅ File updated: {test_file}')
print(f'   Remaining operation= references: {updated_count}')
