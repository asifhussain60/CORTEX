"""
Phase 10b: Fix remaining broken links (Round 2)
"""

from pathlib import Path

workspace = Path(r"D:\PROJECTS\CORTEX")
docs_dir = workspace / "docs"

# Fix relative path issues
files_to_fix = list(docs_dir.rglob("*.html"))

fixes = 0
files_modified = []

for html_file in files_to_fix:
    try:
        content = html_file.read_text(encoding='utf-8')
        original = content
        
        # Fix 1: assets/css/intentional-classes.css → ../assets/css/intentional-classes.css
        # (for files in subdirectories)
        if html_file.parent != docs_dir:
            content = content.replace('href="assets/css/intentional-classes.css"', 'href="../assets/css/intentional-classes.css"')
        
        # Fix 2: brain-tiers.html → four-tier-brain.html
        content = content.replace('brain-tiers.html', 'four-tier-brain.html')
        
        # Fix 3: governance/skull-rulebook.html → security/index.html
        content = content.replace('../governance/skull-rulebook.html', '../security/index.html')
        content = content.replace('governance/skull-rulebook.html', '../security/index.html')
        
        # Fix 4: design-system relative paths
        if 'design-system' in str(html_file):
            # Index.html in same folder should stay, but external index.html needs ../
            if 'migration-guide.html' in content:
                content = content.replace('href="migration-guide.html"', 'href="glassmorphism-guide.html"')
        
        if content != original:
            html_file.write_text(content, encoding='utf-8')
            fixes += 1
            files_modified.append(str(html_file.relative_to(workspace)))
            
    except Exception as e:
        print(f'Error fixing {html_file}: {e}')

print(f'✅ Fixed {fixes} files')
for f in files_modified[:10]:  # Show first 10
    print(f'  - {f}')
if len(files_modified) > 10:
    print(f'  ... and {len(files_modified) - 10} more')
