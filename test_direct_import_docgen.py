"""Test DirectConversationImport with real docgen.md file."""

from pathlib import Path
from src.operations.modules.conversations.direct_import import DirectConversationImport

# Initialize
cortex_brain = Path("d:/PROJECTS/CORTEX/cortex-brain")
project_root = Path("d:/PROJECTS/CORTEX")
importer = DirectConversationImport(cortex_brain)

# Test with docgen.md
print("Testing: /CORTEX capture conversation #file:docgen.md\n")

result = importer.import_from_file_reference(
    user_request="/CORTEX capture conversation #file:docgen.md",
    project_root=project_root
)

if result["success"]:
    print("✅ SUCCESS!\n")
    print(result["message"])
    print(f"\nConversation ID: {result['conversation_id']}")
    print(f"Messages imported: {result['messages_imported']}")
else:
    print("❌ FAILED\n")
    print(f"Error: {result.get('error', 'Unknown')}")
    print(f"Message: {result.get('message', 'N/A')}")
