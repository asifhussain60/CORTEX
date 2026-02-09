import json
from pathlib import Path

# Check prescan data
with open('.cortex/prescan_results.json', encoding='utf-8') as f:
    data = json.load(f)

ks = data['repositories']['KSESSIONS']

print("\n=== KSESSIONS Prescan Results ===")
print(f"Total files: {ks['file_count']}")
print(f"Languages: {', '.join(ks['languages'])}")
print(f"\nPatterns:")
for pattern_type, files in ks['patterns'].items():
    print(f"  {pattern_type}: {len(files)} files")
    if files and len(files) <= 5:
        for f in files:
            print(f"    - {f}")

print("\n=== Testing Enhanced Extractors ===")
from cortex.lens.extractors.enhanced_extractors import extract_enhanced_use_cases

repo_path = Path('D:/PROJECTS/KSESSIONS')
use_cases = extract_enhanced_use_cases(repo_path)

print(f"Extracted: {len(use_cases)} use cases")
for uc in use_cases[:10]:
    print(f"  - {uc['title']} ({uc['extraction_method']})")
