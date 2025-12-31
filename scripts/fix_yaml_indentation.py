"""Fix YAML indentation issues in brain-protection-rules.yaml"""
import re
from pathlib import Path

skull_file = Path('cortex-brain/brain-protection-rules.yaml')

with open(skull_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Track fixes
fixes = []

# Fix 1: detection/validation/alternatives/evidence_template/rationale should be indented under rule
# Pattern: Find lines that should be indented (detection, validation, alternatives, evidence_template, rationale)
# that are at wrong indentation level after "- rule_id"

lines = content.split('\n')
fixed_lines = []
in_rule = False
rule_indent_level = 0

for i, line in enumerate(lines):
    # Detect rule_id line
    if re.match(r'^(\s*)- rule_id:', line):
        in_rule = True
        # Calculate indent level (should be either 2 or 4 spaces before the dash)
        match = re.match(r'^(\s*)- rule_id:', line)
        rule_indent_level = len(match.group(1))
        fixed_lines.append(line)
        continue
    
    # If we're in a rule, fix child properties that should be indented
    if in_rule and line.strip() and not line.strip().startswith('#'):
        # Properties that should be under the rule
        if re.match(r'^\s*(name|severity|description|detection|validation|alternatives|evidence_template|rationale):', line):
            # Check current indent
            current_indent = len(line) - len(line.lstrip())
            expected_indent = rule_indent_level + 6  # rule indent + 2 (dash+space) + 4 (property indent)
            
            if current_indent != expected_indent:
                # Fix indentation
                property_content = line.lstrip()
                fixed_line = ' ' * expected_indent + property_content
                fixes.append(f"Line {i+1}: Indent {current_indent} → {expected_indent}")
                fixed_lines.append(fixed_line)
                continue
        
        # Check if we're starting a new rule (another rule_id at same or higher level)
        if re.match(r'^(\s*)- rule_id:', line):
            in_rule = False
    
    fixed_lines.append(line)

# Write fixed content
backup_file = skull_file.with_suffix('.yaml.backup')
with open(backup_file, 'w', encoding='utf-8') as f:
    f.write(content)

with open(skull_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print(f"✅ Fixed {len(fixes)} indentation issues")
print(f"📋 Backup created: {backup_file}")
if fixes[:10]:
    print("\n🔧 Sample fixes:")
    for fix in fixes[:10]:
        print(f"  {fix}")
