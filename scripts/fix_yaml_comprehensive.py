"""
Fix YAML indentation issues in brain-protection-rules.yaml
Comprehensive line-by-line parser that doesn't rely on yaml.safe_load
"""
import re
from pathlib import Path
from typing import List, Tuple

def fix_yaml_indentation(file_path: Path) -> Tuple[List[str], int]:
    """
    Fix indentation issues in brain-protection-rules.yaml.
    
    Returns:
        Tuple of (fixed_lines, num_fixes)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    fixes = 0
    in_rules_list = False
    current_rule_indent = 0
    
    for i, line in enumerate(lines):
        # Track if we're in the rules list under a protection layer
        if re.match(r'^  rules:\s*$', line):
            in_rules_list = True
            fixed_lines.append(line)
            continue
        
        # Detect rule_id (marks start of a rule)
        rule_match = re.match(r'^(\s*)- rule_id:', line)
        if rule_match and in_rules_list:
            current_rule_indent = len(rule_match.group(1))
            fixed_lines.append(line)
            continue
        
        # If we're in a rule, check properties that should be indented
        if in_rules_list and current_rule_indent > 0:
            # Properties that should be at rule_indent + 6
            property_match = re.match(r'^(\s*)(name|severity|description|detection|validation|alternatives|evidence_template|rationale):', line)
            
            if property_match:
                current_indent = len(property_match.group(1))
                expected_indent = current_rule_indent + 6
                property_name = property_match.group(2)
                
                if current_indent != expected_indent:
                    # Fix the indentation
                    rest_of_line = line.lstrip()
                    fixed_line = ' ' * expected_indent + rest_of_line
                    fixed_lines.append(fixed_line)
                    fixes += 1
                    continue
            
            # Check for another rule starting (resets context)
            if re.match(r'^(\s*)- rule_id:', line):
                current_rule_indent = len(re.match(r'^(\s*)- rule_id:', line).group(1))
            
            # Check if we're exiting the rules list
            if line.strip() and not line.startswith(' '):
                in_rules_list = False
                current_rule_indent = 0
        
        # Keep line as-is
        fixed_lines.append(line)
    
    return fixed_lines, fixes

def main():
    skull_file = Path('cortex-brain/brain-protection-rules.yaml')
    backup_file = Path('cortex-brain/brain-protection-rules.yaml.backup')
    
    print("🔧 Fixing YAML indentation...")
    
    # Create backup
    with open(skull_file, 'r', encoding='utf-8') as f:
        original = f.read()
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original)
    
    print(f"📋 Backup created: {backup_file}")
    
    # Fix indentation
    fixed_lines, num_fixes = fix_yaml_indentation(skull_file)
    
    # Write fixed version
    with open(skull_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Fixed {num_fixes} indentation issues")
    
    # Validate
    try:
        import yaml
        with open(skull_file, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        print("✅ YAML validation: PASSED")
        return True
    except yaml.parser.ParserError as e:
        print(f"❌ YAML validation: FAILED")
        print(f"   Error at line {e.problem_mark.line + 1}: {e.problem}")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
