"""
Direct Conversation Import - Usage Examples

Demonstrates streamlined file import workflow.
"""

from pathlib import Path
from src.operations.modules.conversations.direct_import import DirectConversationImport


def example_import_from_file_reference():
    """Example: Import conversation using #file: reference."""
    
    # Initialize importer
    cortex_brain = Path("d:/PROJECTS/CORTEX/cortex-brain")
    importer = DirectConversationImport(cortex_brain)
    
    # Import from file reference (as user would type)
    result = importer.import_from_file_reference(
        user_request="/CORTEX capture conversation #file:docgen.md",
        project_root=Path("d:/PROJECTS/CORTEX")
    )
    
    if result["success"]:
        print(f"✅ Success! Imported {result['messages_imported']} messages")
        print(f"   Conversation ID: {result['conversation_id']}")
    else:
        print(f"❌ Failed: {result['message']}")


def example_import_from_natural_language():
    """Example: Import using natural language."""
    
    cortex_brain = Path("d:/PROJECTS/CORTEX/cortex-brain")
    importer = DirectConversationImport(cortex_brain)
    
    # Natural language variations
    requests = [
        "import conversation from .github/CopilotChats/docgen.md",
        "capture this: .github/CopilotChats/docgen.md",
        "load conversation .github/CopilotChats/docgen.md"
    ]
    
    for request in requests:
        result = importer.import_from_file_reference(
            user_request=request,
            project_root=Path("d:/PROJECTS/CORTEX")
        )
        
        if result["success"]:
            print(f"✅ {request[:30]}... → {result['messages_imported']} messages")


def example_import_from_preloaded_content():
    """Example: Import from content GitHub Copilot already loaded."""
    
    cortex_brain = Path("d:/PROJECTS/CORTEX/cortex-brain")
    importer = DirectConversationImport(cortex_brain)
    
    # Simulate content loaded by Copilot
    content = """
asifhussain60: How do I implement direct import?

GitHub Copilot: Create a DirectConversationImport instance and call import_from_file_reference.

asifhussain60: What about pre-loaded content?

GitHub Copilot: Use import_from_content() method with the content string.
"""
    
    result = importer.import_from_content(
        content=content,
        source_description="copilot-chat-session",
        metadata={
            "source": "github_copilot_chat",
            "timestamp": "2025-11-16T14:30:00Z"
        }
    )
    
    if result["success"]:
        print(f"✅ Imported {result['messages_imported']} messages from Copilot session")


def example_common_use_cases():
    """Common use cases for direct import."""
    
    cortex_brain = Path("d:/PROJECTS/CORTEX/cortex-brain")
    importer = DirectConversationImport(cortex_brain)
    project_root = Path("d:/PROJECTS/CORTEX")
    
    # Use case 1: Import from CopilotChats folder
    print("\n1. Import from CopilotChats folder:")
    result = importer.import_from_file_reference(
        user_request="#file:docgen.md",
        project_root=project_root
    )
    print(f"   → {result.get('message', 'N/A')}")
    
    # Use case 2: Import from conversation-captures
    print("\n2. Import from conversation-captures:")
    result = importer.import_from_file_reference(
        user_request="#file:20251116-planning-session.md",
        project_root=project_root
    )
    print(f"   → {result.get('message', 'N/A')}")
    
    # Use case 3: Import with full path
    print("\n3. Import with full path:")
    result = importer.import_from_file_reference(
        user_request="#file:.github/CopilotChats/docgen.md",
        project_root=project_root
    )
    print(f"   → {result.get('message', 'N/A')}")


if __name__ == "__main__":
    print("=== Direct Conversation Import Examples ===\n")
    
    print("\n--- Example 1: File Reference Import ---")
    example_import_from_file_reference()
    
    print("\n--- Example 2: Natural Language Import ---")
    example_import_from_natural_language()
    
    print("\n--- Example 3: Pre-loaded Content Import ---")
    example_import_from_preloaded_content()
    
    print("\n--- Example 4: Common Use Cases ---")
    example_common_use_cases()
