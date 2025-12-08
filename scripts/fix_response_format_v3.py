"""
Fix Response Format v3.0 - Update all templates and code to use correct section names

This script updates:
1. response-templates.yaml - All template bodies
2. section_formatters.py - Code that generates sections  
3. Integration tests - Assertions checking for sections
4. Validation scripts - Section name checks

Section Name Changes (v2.0 → v3.0):
- "My Understanding Of Your Request" → "Understanding & Scope"
- "Challenge" → "Approach & Considerations" (already done)
- "Your Request" → "Impact & Changes" (already done)
"""

import re
from pathlib import Path

def fix_templates_yaml(file_path: Path) -> int:
    """Fix response-templates.yaml"""
    print(f"\n📝 Fixing {file_path.name}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Replace H2 headers (##) with H3 (###) for section headers
    # But NOT the main title "## 🧠 CORTEX"
    content = re.sub(
        r'^      ## (🎯|⚡|💬|📊|🔍) ',
        r'      ### \1 ',
        content,
        flags=re.MULTILINE
    )
    
    # Replace old section names with v3.0 names
    content = content.replace(
        '## 🎯 My Understanding Of Your Request',
        '### 🎯 Understanding & Scope'
    )
    content = content.replace(
        '### 🎯 My Understanding Of Your Request',
        '### 🎯 Understanding & Scope'
    )
    
    # Replace legacy "Challenge" and "Your Request" if any remain
    content = content.replace('## ⚠️ Challenge', '### ⚡ Approach & Considerations')
    content = content.replace('### ⚠️ Challenge', '### ⚡ Approach & Considerations')
    content = content.replace('## 📝 Your Request', '### 📊 Impact & Changes')
    content = content.replace('### 📝 Your Request', '### 📊 Impact & Changes')
    
    changes = len(content) - len(original)
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated {file_path.name} ({abs(changes)} char changes)")
        return 1
    else:
        print(f"⏭️  No changes needed in {file_path.name}")
        return 0

def fix_section_formatters(file_path: Path) -> int:
    """Fix src/response_templates/section_formatters.py"""
    print(f"\n📝 Fixing {file_path.name}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Replace in code
    content = content.replace(
        '"My Understanding Of Your Request"',
        '"Understanding & Scope"'
    )
    content = content.replace(
        "'My Understanding Of Your Request'",
        "'Understanding & Scope'"
    )
    content = content.replace(
        'f"### 🎯 My Understanding Of Your Request',
        'f"### 🎯 Understanding & Scope'
    )
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated {file_path.name}")
        return 1
    else:
        print(f"⏭️  No changes needed in {file_path.name}")
        return 0

def fix_tests(test_dir: Path) -> int:
    """Fix all test files in tests/response_templates/"""
    print(f"\n📝 Fixing test files in {test_dir.name}/...")
    
    test_files = list(test_dir.glob('test_*.py'))
    fixed = 0
    
    for test_file in test_files:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Replace assertions
        content = content.replace(
            '"## 🎯 My Understanding Of Your Request"',
            '"### 🎯 Understanding & Scope"'
        )
        content = content.replace(
            "'## 🎯 My Understanding Of Your Request'",
            "'### 🎯 Understanding & Scope'"
        )
        content = content.replace(
            '"### 🎯 My Understanding Of Your Request"',
            '"### 🎯 Understanding & Scope"'
        )
        content = content.replace(
            "'### 🎯 My Understanding Of Your Request'",
            "'### 🎯 Understanding & Scope'"
        )
        
        if content != original:
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ {test_file.name}")
            fixed += 1
    
    print(f"✅ Updated {fixed}/{len(test_files)} test files")
    return fixed

def fix_validation_scripts(scripts_dir: Path) -> int:
    """Fix validation scripts in scripts/"""
    print(f"\n📝 Fixing validation scripts...")
    
    script_files = [
        scripts_dir / 'validate_templates.py',
        scripts_dir / 'migrate_templates.py',
        scripts_dir / 'migrate_response_templates.py',
        scripts_dir / 'focused_template_migration.py'
    ]
    
    fixed = 0
    
    for script_file in script_files:
        if not script_file.exists():
            continue
            
        with open(script_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Replace in scripts
        content = content.replace(
            '"## 🎯 My Understanding Of Your Request"',
            '"### 🎯 Understanding & Scope"'
        )
        content = content.replace(
            "'## 🎯 My Understanding Of Your Request'",
            "'### 🎯 Understanding & Scope'"
        )
        content = content.replace(
            '"### 🎯 My Understanding Of Your Request"',
            '"### 🎯 Understanding & Scope"'
        )
        content = content.replace(
            "'### 🎯 My Understanding Of Your Request'",
            "'### 🎯 Understanding & Scope'"
        )
        
        if content != original:
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ {script_file.name}")
            fixed += 1
    
    print(f"✅ Updated {fixed}/{len(script_files)} script files")
    return fixed

def fix_other_sources(cortex_root: Path) -> int:
    """Fix other Python source files"""
    print(f"\n📝 Fixing other source files...")
    
    source_files = [
        cortex_root / 'src' / 'validation' / 'template_header_validator.py',
        cortex_root / 'src' / 'response_templates' / 'response_template_manager.py',
    ]
    
    fixed = 0
    
    for source_file in source_files:
        if not source_file.exists():
            continue
            
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Replace in source
        content = content.replace(
            '## 🎯 My Understanding Of Your Request',
            '### 🎯 Understanding & Scope'
        )
        content = content.replace(
            '### 🎯 My Understanding Of Your Request',
            '### 🎯 Understanding & Scope'
        )
        
        if content != original:
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ {source_file.name}")
            fixed += 1
    
    print(f"✅ Updated {fixed}/{len(source_files)} source files")
    return fixed

def main():
    """Main execution"""
    print("🔧 Response Format v3.0 Fix Script")
    print("=" * 60)
    
    cortex_root = Path(__file__).parent.parent
    
    total_fixed = 0
    
    # 1. Fix response-templates.yaml
    templates_yaml = cortex_root / 'cortex-brain' / 'response-templates.yaml'
    total_fixed += fix_templates_yaml(templates_yaml)
    
    # 2. Fix section_formatters.py
    section_formatters = cortex_root / 'src' / 'response_templates' / 'section_formatters.py'
    total_fixed += fix_section_formatters(section_formatters)
    
    # 3. Fix integration tests
    test_dir = cortex_root / 'tests' / 'response_templates'
    total_fixed += fix_tests(test_dir)
    
    # 4. Fix validation scripts
    scripts_dir = cortex_root / 'scripts'
    total_fixed += fix_validation_scripts(scripts_dir)
    
    # 5. Fix other source files
    total_fixed += fix_other_sources(cortex_root)
    
    print("\n" + "=" * 60)
    print(f"✅ Fix Complete - {total_fixed} files updated")
    print("\n📋 Next Steps:")
    print("  1. Run: pytest tests/response_templates/ -v")
    print("  2. Verify no test failures")
    print("  3. Commit changes with message:")
    print('     "fix: Update all templates to Response Format v3.0 section names"')

if __name__ == '__main__':
    main()
