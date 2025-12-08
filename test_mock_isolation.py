#!/usr/bin/env python3
"""
Test that mock source loads ONLY from mock folder
"""
import re

# Read data-loader.js
with open('cortex-brain/dashboards/ui/data-loader.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Check DATA_SOURCES definition
data_sources_match = re.search(r'const DATA_SOURCES = \{([^}]+)\}', content)
if data_sources_match:
    data_sources_content = data_sources_match.group(1)
    print("✓ Found DATA_SOURCES definition:")
    print(data_sources_content)
    
    # Verify mock points to correct path
    if "mock: '../data/repositories/mock/'" in data_sources_content:
        print("✅ PASS: Mock source correctly points to ../data/repositories/mock/")
    else:
        print("❌ FAIL: Mock source path is incorrect")
        exit(1)
else:
    print("❌ FAIL: Could not find DATA_SOURCES definition")
    exit(1)

# Check loadDashboardData function
load_function_match = re.search(
    r'export async function loadDashboardData\(source = \'mock\'\).*?const basePath = DATA_SOURCES\[source\]',
    content,
    re.DOTALL
)
if load_function_match:
    print("\n✓ Found loadDashboardData function")
    print("✓ Uses DATA_SOURCES[source] for basePath resolution")
else:
    print("❌ FAIL: loadDashboardData does not use DATA_SOURCES correctly")
    exit(1)

# Check DATA_FILES array
data_files_match = re.search(r'const DATA_FILES = \[(.*?)\]', content, re.DOTALL)
if data_files_match:
    data_files = data_files_match.group(1)
    file_count = data_files.count('.json')
    print(f"\n✓ Found DATA_FILES array with {file_count} JSON files")
    
    # List the files
    files = re.findall(r"'([^']+\.json)'", data_files)
    print(f"✓ Files loaded per source:")
    for f in files:
        print(f"  - {f}")
else:
    print("❌ FAIL: Could not find DATA_FILES array")
    exit(1)

# Check for any hardcoded paths to other repositories
hardcoded_paths = re.findall(r'/data/repositories/(luum-fresh|tcbulk|v5-coldfusion|v5-prevalidation-ws)/', content)
if hardcoded_paths:
    print(f"\n❌ FAIL: Found {len(hardcoded_paths)} hardcoded paths to other repositories:")
    for path in set(hardcoded_paths):
        print(f"  - {path}")
    exit(1)
else:
    print("\n✅ PASS: No hardcoded paths to other repositories found")

# Check loadAdditionalData function
additional_data_match = re.search(
    r'export async function loadAdditionalData\(source = \'mock\', fileName\).*?const basePath = DATA_SOURCES\[source\]',
    content,
    re.DOTALL
)
if additional_data_match:
    print("✅ PASS: loadAdditionalData uses DATA_SOURCES[source]")
else:
    print("❌ FAIL: loadAdditionalData does not use DATA_SOURCES correctly")
    exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED")
print("=" * 60)
print("\nConclusion:")
print("When source='mock' is selected:")
print("  1. All standard data files load from ../data/repositories/mock/")
print("  2. All additional data files load from ../data/repositories/mock/")
print("  3. No hardcoded paths to other repositories exist")
print("  4. Data isolation is properly implemented")
