#!/usr/bin/env python3
"""Fix all API mismatches in test_cross_tier_workflows.py"""

import re
from pathlib import Path

TEST_FILE = Path("/Users/asifhussain/PROJECTS/CORTEX/tests/integration/test_cross_tier_workflows.py")

content = TEST_FILE.read_text()

# Fix 1: Replace name= with title= in add_pattern calls
content = re.sub(r'(\s+)name=', r'\1title=', content)

# Fix 2: Replace string pattern_type with PatternType enum
# Map string values to enum references
pattern_type_map = {
    'pattern_type="workflow"': 'pattern_type=PatternType.WORKFLOW',
    'pattern_type="code"': 'pattern_type=PatternType.SOLUTION',  # Map code -> SOLUTION
    'pattern_type="test"': 'pattern_type=PatternType.SOLUTION',  # Map test -> SOLUTION
    'pattern_type="concurrent"': 'pattern_type=PatternType.WORKFLOW',  # Map concurrent -> WORKFLOW
    'pattern_type="load_test"': 'pattern_type=PatternType.WORKFLOW',  # Map load_test -> WORKFLOW
}

for old, new in pattern_type_map.items():
    content = content.replace(old, new)

# Fix 3: Add PatternType import if not present
if 'from src.tier2.knowledge_graph_legacy import' not in content:
    # Find the imports section and add PatternType
    content = content.replace(
        'from src.tier2.knowledge_graph_legacy import KnowledgeGraph',
        'from src.tier2.knowledge_graph_legacy import KnowledgeGraph, PatternType'
    )

# Fix 4: Replace wildcard search "*" with empty string (searches all)
content = content.replace('query="*"', 'query=""')

# Write back
TEST_FILE.write_text(content)
print("✅ Fixed all API mismatches in test_cross_tier_workflows.py")
print("   - Replaced name= with title=")
print("   - Replaced string pattern_type with PatternType enum")
print("   - Added PatternType import")
print("   - Fixed wildcard search pattern")
