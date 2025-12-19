# direct_import

Direct Conversation Import - Streamlined File Import

Provides one-action import from file reference (e.g., #file:docgen.md)
Bypasses verbose two-step capture workflow for direct file imports.

Part of CORTEX 3.0 Track 1 - Feature 5: Conversation Tracking & Capture
Roadmap: cortex-brain/cortex-3.0-design/CORTEX-3.0-ROADMAP.yaml

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0.0


## Table of Contents

### Classes
- [DirectConversationImport](#directconversationimport)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** import_handler, logging, pathlib, re, typing


## Classes

### DirectConversationImport

```python
class DirectConversationImport
```

Streamlined conversation import directly from file reference.

Handles requests like:
    - /CORTEX capture conversation #file:docgen.md
    - /CORTEX import conversation from .github/CopilotChats/docgen.md
    - Capture this: [file content already loaded by Copilot]

Workflow:
    1. Extract file path from user request or context
    2. Validate file exists and is accessible
    3. Call ConversationImportHandler directly
    4. Return minimal success message (no verbose steps)

Usage:
    importer = DirectConversationImport(cortex_brain_path)
    result = importer.import_from_file_reference(
        user_request="/CORTEX capture conversation #file:docgen.md"
    )
    
    # Returns: {
    #   "success": True,
    #   "conversation_id": "conv-20251116-143052",
    #   "messages_imported": 15,
    #   "message": "Conversation imported successfully!"
    # }


**Methods:**

  #### `import_from_file_reference`

  ```python
  import_from_file_reference(self, user_request: str, project_root: Optional[Path], file_content: Optional[str]) -> Dict[str, Any]
  ```

  Import conversation directly from file reference.

Args:
    user_request: User's original request (may contain #file: reference)
    project_root: Project root path (for resolving relative paths)
    file_content: Pre-loaded file content (if Copilot already read it)

Returns:
    Dict with:
        - success: bool
        - conversation_id: str (generated ID)
        - messages_imported: int
        - entities_tracked: int
        - message: str (minimal success message)

  **Parameters:**

  - `self`
  - `user_request` (str): User's original request (may contain #file: reference)
  - `project_root` (Optional[Path]) = `None`: Project root path (for resolving relative paths)
  - `file_content` (Optional[str]) = `None`: Pre-loaded file content (if Copilot already read it)


  **Returns:** Dict[str, Any]
    Dict with: - success: bool - conversation_id: str (generated ID) - messages_imported: int - entities_tracked: int - message: str (minimal success message)


  #### `import_from_content`

  ```python
  import_from_content(self, content: str, source_description: str, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]
  ```

  Import conversation from pre-loaded content.

Useful when GitHub Copilot has already read the file.

Args:
    content: Raw conversation content
    source_description: Description of source (for logging)
    metadata: Additional metadata to attach

Returns:
    Import result dict

  **Parameters:**

  - `self`
  - `content` (str): Raw conversation content
  - `source_description` (str) = `'conversation'`: Description of source (for logging)
  - `metadata` (Optional[Dict[str, Any]]) = `None`: Additional metadata to attach


  **Returns:** Dict[str, Any]
    Import result dict



---
