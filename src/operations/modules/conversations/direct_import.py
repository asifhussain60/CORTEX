"""
Direct Conversation Import - Streamlined File Import

Provides one-action import from file reference (e.g., #file:docgen.md)
Bypasses verbose two-step capture workflow for direct file imports.

Part of CORTEX 3.0 Track 1 - Feature 5: Conversation Tracking & Capture
Roadmap: cortex-brain/cortex-3.0-design/CORTEX-3.0-ROADMAP.yaml

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging
import re

from .import_handler import ConversationImportHandler

logger = logging.getLogger(__name__)


class DirectConversationImport:
    """
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
    """
    
    def __init__(self, cortex_brain_path: Path):
        """
        Initialize direct import handler.
        
        Args:
            cortex_brain_path: Path to cortex-brain directory
        """
        self.cortex_brain_path = Path(cortex_brain_path)
        self.import_handler = ConversationImportHandler(cortex_brain_path)
        
        logger.info(f"DirectConversationImport initialized: {self.cortex_brain_path}")
    
    def import_from_file_reference(
        self,
        user_request: str,
        project_root: Optional[Path] = None,
        file_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
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
        """
        try:
            # Extract file path from request
            file_path = self._extract_file_path(user_request, project_root)
            
            if not file_path:
                return {
                    "success": False,
                    "error": "no_file_reference",
                    "message": "No file reference found in request. Use #file:path or provide file path."
                }
            
            # Validate file exists
            if not file_path.exists():
                return {
                    "success": False,
                    "error": "file_not_found",
                    "message": f"File not found: {file_path}"
                }
            
            logger.info(f"Direct import from file: {file_path}")
            
            # Import using standard import handler
            result = self.import_handler.import_conversation(
                file_path=str(file_path),
                auto_detect=False
            )
            
            # Simplify response for streamlined workflow
            if result["success"]:
                return {
                    "success": True,
                    "conversation_id": result["conversation_id"],
                    "file_path": str(file_path),
                    "messages_imported": result["messages_imported"],
                    "entities_tracked": result["entities_tracked"],
                    "message": f"✅ Conversation imported successfully!\n\n📊 {result['messages_imported']} messages imported from {file_path.name}"
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Direct import failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": "import_failed",
                "message": f"Import failed: {str(e)}",
                "exception": str(e)
            }
    
    def _extract_file_path(
        self,
        user_request: str,
        project_root: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Extract file path from user request.
        
        Supports patterns:
            - #file:docgen.md
            - #file:.github/CopilotChats/docgen.md
            - from .github/CopilotChats/docgen.md
            - import .github/CopilotChats/docgen.md
        
        Args:
            user_request: User's request string
            project_root: Project root for resolving relative paths
        
        Returns:
            Resolved file path or None if not found
        """
        # Pattern 1: #file:path
        file_ref_match = re.search(r'#file:([^\s]+)', user_request)
        if file_ref_match:
            path_str = file_ref_match.group(1)
            return self._resolve_path(path_str, project_root)
        
        # Pattern 2: from/import path
        from_match = re.search(r'(?:from|import)\s+([^\s]+\.md)', user_request, re.IGNORECASE)
        if from_match:
            path_str = from_match.group(1)
            return self._resolve_path(path_str, project_root)
        
        # Pattern 3: Direct path mention (e.g., ".github/CopilotChats/docgen.md")
        path_match = re.search(r'([\.a-zA-Z0-9_/-]+\.md)', user_request)
        if path_match:
            path_str = path_match.group(1)
            candidate = self._resolve_path(path_str, project_root)
            if candidate and candidate.exists():
                return candidate
        
        return None
    
    def _resolve_path(
        self,
        path_str: str,
        project_root: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Resolve file path string to absolute Path.
        
        Args:
            path_str: Path string from user request
            project_root: Project root for relative path resolution
        
        Returns:
            Resolved Path or None if invalid
        """
        try:
            path = Path(path_str)
            
            # Absolute path
            if path.is_absolute():
                return path if path.exists() else None
            
            # Relative to project root
            if project_root:
                candidate = project_root / path
                if candidate.exists():
                    return candidate
            
            # Relative to current working directory
            candidate = Path.cwd() / path
            if candidate.exists():
                return candidate
            
            # Try common locations
            if project_root:
                common_locations = [
                    project_root / ".github" / "CopilotChats" / path.name,
                    project_root / "cortex-brain" / "documents" / "conversation-captures" / path.name,
                ]
                for location in common_locations:
                    if location.exists():
                        return location
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to resolve path '{path_str}': {e}")
            return None
    
    def import_from_content(
        self,
        content: str,
        source_description: str = "conversation",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Import conversation from pre-loaded content.
        
        Useful when GitHub Copilot has already read the file.
        
        Args:
            content: Raw conversation content
            source_description: Description of source (for logging)
            metadata: Additional metadata to attach
        
        Returns:
            Import result dict
        """
        try:
            # Parse conversation from content
            parsed = self.import_handler._parse_conversation(content, source_description)
            
            # Add custom metadata if provided
            if metadata:
                parsed["metadata"].update(metadata)
            
            # Import to brain (stub implementation)
            import_result = self.import_handler._import_to_brain(
                parsed,
                Path(f"direct-import-{source_description}")
            )
            
            # Simplify response
            if import_result["success"]:
                return {
                    "success": True,
                    "conversation_id": import_result["conversation_id"],
                    "messages_imported": import_result["messages_imported"],
                    "entities_tracked": import_result["entities_tracked"],
                    "message": f"✅ Conversation imported successfully!\n\n📊 {import_result['messages_imported']} messages imported"
                }
            else:
                return import_result
                
        except Exception as e:
            logger.error(f"Content import failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": "import_failed",
                "message": f"Import failed: {str(e)}",
                "exception": str(e)
            }
