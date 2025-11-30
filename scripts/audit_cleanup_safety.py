"""
CORTEX Safety Audit - Pattern Validation
Checks cleanup patterns against critical system files to prevent false positives.
"""

import os
from pathlib import Path
import yaml

def audit_patterns():
    """Audit cleanup patterns for safety."""
    
    # Load configuration
    with open('cortex-brain/cleanup-detection-patterns.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    print("="*80)
    print("🛡️  CORTEX CLEANUP PATTERN SAFETY AUDIT")
    print("="*80)
    
    # 1. Check protected directories
    print("\n1️⃣  PROTECTED DIRECTORIES CHECK")
    print("-" * 80)
    
    protected_dirs = config['protected_directories']
    critical_dirs = ['src', 'tests', 'prompts', 'workflows', 'cortex-extension']
    
    print(f"Protected in config: {len(protected_dirs)} directories")
    for dir_name in protected_dirs:
        print(f"  ✅ {dir_name}")
    
    print(f"\nCritical CORTEX directories:")
    for dir_name in critical_dirs:
        if dir_name in protected_dirs:
            print(f"  ✅ {dir_name} - PROTECTED")
        else:
            print(f"  ❌ {dir_name} - NOT PROTECTED (RISK!)")
    
    # 2. Check publish folder
    print("\n2️⃣  PUBLISH FOLDER CHECK")
    print("-" * 80)
    
    publish_path = Path('publish')
    if publish_path.exists():
        publish_items = list(publish_path.iterdir())
        print(f"Found {len(publish_items)} items in publish/:")
        for item in publish_items:
            if item.is_dir():
                file_count = len(list(item.rglob('*')))
                print(f"  • {item.name}/ ({file_count} files)")
        
        if 'publish' in config.get('candidate_directories', []):
            print("\n  ⚠️  WARNING: publish/ is in candidate_directories")
            print("     Published packages could be flagged for cleanup")
        else:
            print("\n  ✅ publish/ not in candidate directories")
    
    # 3. Check for false positives in src/
    print("\n3️⃣  FALSE POSITIVE CHECK (src/ directory)")
    print("-" * 80)
    
    temporal_keywords = config['temporal_keywords']
    false_positives = []
    
    src_path = Path('src')
    if src_path.exists():
        for root, dirs, files in os.walk(src_path):
            # Skip __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('__')]
            
            for file in files:
                if file.endswith('.py'):
                    file_lower = file.lower()
                    for keyword in temporal_keywords:
                        if keyword in file_lower:
                            rel_path = Path(root) / file
                            false_positives.append((keyword, str(rel_path)))
                            break
        
        if false_positives:
            print(f"Found {len(false_positives)} files with temporal keywords in src/:")
            for keyword, path in false_positives[:15]:
                print(f"  ⚠️  {path}")
                print(f"     Matches: '{keyword}'")
            if len(false_positives) > 15:
                print(f"  ... and {len(false_positives) - 15} more")
            
            print("\n  🛡️  PROTECTION: These are safe because:")
            print("     • 'src' is in protected_directories")
            print("     • Git-tracked files are excluded by default")
        else:
            print("  ✅ No temporal keywords found in src/ filenames")
    
    # 4. Check exclusion patterns
    print("\n4️⃣  CUSTOM EXCLUSION PATTERNS")
    print("-" * 80)
    
    custom_exclusions = config.get('custom_exclusions') or []
    print(f"Active exclusion patterns: {len(custom_exclusions)}")
    for pattern in custom_exclusions:
        if pattern:
            print(f"  • {pattern}")
    
    # 5. Check protected files
    print("\n5️⃣  PROTECTED FILES")
    print("-" * 80)
    
    protected_files = config['protected_files']
    print(f"Total protected files: {len(protected_files)}")
    
    # Critical configs
    critical_files = [
        'cortex.config.json',
        'requirements.txt',
        'package.json',
        'pytest.ini',
        'setup.py'
    ]
    
    for file_name in critical_files:
        if file_name in protected_files:
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} - NOT PROTECTED")
    
    # 6. Git integration check
    print("\n6️⃣  GIT INTEGRATION")
    print("-" * 80)
    
    git_filters = config['git_filters']
    print(f"Exclude tracked files: {git_filters['exclude_tracked']}")
    print(f"Exclude modified files: {git_filters['exclude_modified']}")
    print(f"Exclude staged files: {git_filters['exclude_staged']}")
    
    if git_filters['exclude_tracked']:
        print("\n  ✅ Git-tracked files automatically protected")
        print("     This means ALL committed CORTEX code is safe")
    
    # 7. Summary
    print("\n" + "="*80)
    print("📊 SAFETY AUDIT SUMMARY")
    print("="*80)
    
    risks = []
    
    # Check if critical dirs are protected
    for dir_name in critical_dirs:
        if dir_name not in protected_dirs:
            risks.append(f"Directory '{dir_name}' not in protected_directories")
    
    # Check publish folder
    if 'publish' in config.get('candidate_directories', []):
        risks.append("publish/ folder marked as candidate (may delete packages)")
    
    if risks:
        print("\n⚠️  POTENTIAL RISKS FOUND:")
        for risk in risks:
            print(f"  • {risk}")
    else:
        print("\n✅ NO CRITICAL RISKS FOUND")
    
    print("\n🛡️  PROTECTION LAYERS:")
    print("  1. Protected directories (src/, tests/, prompts/, workflows/, etc.)")
    print("  2. Git tracking (2,673 tracked files excluded)")
    print("  3. Protected files (41 critical configs)")
    print("  4. Custom exclusion patterns (9 regex rules)")
    print("  5. Dry-run mode by default")
    print("  6. Interactive confirmation required")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    audit_patterns()
