"""
Standalone test for DirectConversationImport with docgen.md.
Bypasses package imports to avoid missing module issues.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Direct import from file
import importlib.util
spec = importlib.util.spec_from_file_location(
    "direct_import", 
    "src/operations/modules/conversations/direct_import.py"
)
direct_import = importlib.util.module_from_spec(spec)
spec.loader.exec_module(direct_import)

DirectConversationImport = direct_import.DirectConversationImport

# Test with docgen.md
print("🧠 Testing DirectConversationImport with docgen.md")
print("=" * 60)

cortex_brain = Path("cortex-brain")
project_root = Path(".")
importer = DirectConversationImport(cortex_brain)

print("\n1. Testing file extraction from '#file:docgen.md'")
file_path = importer._extract_file_path("/CORTEX capture conversation #file:docgen.md", project_root)
print(f"   → Extracted: {file_path}")
print(f"   → Exists: {file_path.exists() if file_path else 'N/A'}")

if file_path and file_path.exists():
    print(f"   → File size: {file_path.stat().st_size} bytes")
    print(f"   → Location: {file_path}")

print("\n2. Testing full import workflow")
result = importer.import_from_file_reference(
    user_request="/CORTEX capture conversation #file:docgen.md",
    project_root=project_root
)

print(f"   → Success: {result['success']}")
if result["success"]:
    print(f"\n✅ {result['message']}")
    print(f"\n📊 Details:")
    print(f"   - Conversation ID: {result['conversation_id']}")
    print(f"   - Messages imported: {result['messages_imported']}")
else:
    print(f"\n❌ Failed: {result.get('error', 'Unknown error')}")
    if 'message' in result:
        print(f"   Message: {result['message']}")

print("\n" + "=" * 60)
print("✅ Test complete!")
