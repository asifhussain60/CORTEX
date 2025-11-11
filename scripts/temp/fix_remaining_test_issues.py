#!/usr/bin/env python3
"""
Comprehensive fix for all remaining test issues in test_cross_tier_workflows.py
"""

import re
import uuid
from pathlib import Path

TEST_FILE = Path("/Users/asifhussain/PROJECTS/CORTEX/tests/integration/test_cross_tier_workflows.py")

content = TEST_FILE.read_text()

# Fix 1: Fix indentation on line ~180 (test_cross_tier_read_performance)
# Replace the malformed add_pattern call
old_pattern_180 = """        for i in range(20):
            tier2.add_pattern(
            pattern_id="bbe12c7b493342ee",
            pattern_type=PatternType.SOLUTION,
                title=f"pattern_{i}",
                content=f"Test pattern {i}",
                confidence=0.8,
                namespaces=["cortex-core"]
            )"""

new_pattern_180 = """        for i in range(20):
            tier2.add_pattern(
                pattern_id=f"bbe12c7b493342ee{i:02d}",
                pattern_type=PatternType.SOLUTION,
                title=f"pattern_{i}",
                content=f"Test pattern {i}",
                confidence=0.8,
                namespaces=["cortex-core"]
            )"""

content = content.replace(old_pattern_180, new_pattern_180)

# Fix 2: Fix indentation on line ~489 (test_concurrent_tier_access)
old_pattern_489 = """                for i in range(10):
                    tier2.add_pattern(
            pattern_id="b0bc67d3bcaf41e4",
            pattern_type=PatternType.SOLUTION,
                        title=f"concurrent_pattern_{i}",
                        content="Concurrent test pattern",
                        confidence=0.8,
                        namespaces=["cortex-core"]
                    )"""

new_pattern_489 = """                for i in range(10):
                    tier2.add_pattern(
                        pattern_id=f"b0bc67d3bcaf41e4{i:02d}",
                        pattern_type=PatternType.SOLUTION,
                        title=f"concurrent_pattern_{i}",
                        content="Concurrent test pattern",
                        confidence=0.8,
                        namespaces=["cortex-core"]
                    )"""

content = content.replace(old_pattern_489, new_pattern_489)

# Fix 3: Fix indentation on line ~543 (test_concurrent_writes_same_tier)
old_pattern_543 = """                for i in range(patterns_per_thread):
                    tier2.add_pattern(
            pattern_id="eae6bf8e947141fa",
            pattern_type=PatternType.WORKFLOW,
                        title=f"thread{thread_id}_pattern{i}",
                        content=f"Pattern from thread {thread_id}",
                        confidence=0.8,
                        namespaces=["test"]
                    )"""

new_pattern_543 = """                for i in range(patterns_per_thread):
                    tier2.add_pattern(
                        pattern_id=f"eae6bf8e947141fa{thread_id:02d}{i:02d}",
                        pattern_type=PatternType.WORKFLOW,
                        title=f"thread{thread_id}_pattern{i}",
                        content=f"Pattern from thread {thread_id}",
                        confidence=0.8,
                        namespaces=["test"]
                    )"""

content = content.replace(old_pattern_543, new_pattern_543)

# Fix 4: Fix indentation on line ~595 (test_tier_performance_under_load)
old_pattern_595 = """        for i in range(100):
            tier2.add_pattern(
            pattern_id="f4785998a1c34ddd",
            pattern_type=PatternType.WORKFLOW,
                title=f"load_pattern_{i}",
                content=f"Load test pattern {i}",
                confidence=0.8,
                namespaces=["test"]
            )"""

new_pattern_595 = """        for i in range(100):
            tier2.add_pattern(
                pattern_id=f"f4785998a1c34ddd{i:03d}",
                pattern_type=PatternType.WORKFLOW,
                title=f"load_pattern_{i}",
                content=f"Load test pattern {i}",
                confidence=0.8,
                namespaces=["test"]
            )"""

content = content.replace(old_pattern_595, new_pattern_595)

# Fix 5: Fix Pattern object access (line ~449)
# Replace pattern.get() dict access with pattern.metadata attribute access
old_pattern_access = """        for pattern in patterns:
            if "conversation_id" in pattern.get("metadata", {}):
                referenced_conv_id = pattern["metadata"]["conversation_id"]
                # Verify conversation exists in Tier 1
                convs = tier1.conversation_manager.get_recent_conversations(limit=100)
                conv_ids = [conv.get("id") for conv in convs]
                assert referenced_conv_id in conv_ids, f"Orphaned reference: {referenced_conv_id}\""""

new_pattern_access = """        for pattern in patterns:
            if pattern.metadata and "conversation_id" in pattern.metadata:
                referenced_conv_id = pattern.metadata["conversation_id"]
                # Verify conversation exists in Tier 1
                convs = tier1.conversation_manager.get_recent_conversations(limit=100)
                conv_ids = [conv.get("conversation_id") for conv in convs]
                assert referenced_conv_id in conv_ids, f"Orphaned reference: {referenced_conv_id}\""""

content = content.replace(old_pattern_access, new_pattern_access)

# Write back
TEST_FILE.write_text(content)

print("✅ Fixed all remaining issues in test_cross_tier_workflows.py")
print("   - Fixed indentation in 4 add_pattern calls (lines ~180, 489, 543, 595)")
print("   - Generated unique pattern IDs for each iteration (prevents UNIQUE constraint failures)")
print("   - Fixed Pattern object access (pattern.metadata instead of pattern.get('metadata'))")
print("   - Fixed conversation ID field name (conversation_id instead of id)")
