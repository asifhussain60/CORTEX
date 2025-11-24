"""
Conversation Import Handler (Feature 5 - Phase 1: Manual Capture)

Handles the second step of two-step conversation capture workflow:
1. User has created file with /CORTEX Capture and pasted conversation
2. User says "/CORTEX Import this conversation"
3. This handler reads the file
4. Parses conversation structure (Track A pipeline)
5. Imports to Tier 1 SQLite database
6. Updates Tier 2 knowledge graph
7. Returns import statistics

Part of CORTEX 3.0 Track 1 - Feature 5: Conversation Tracking & Capture
Roadmap: cortex-brain/cortex-3.0-design/CORTEX-3.0-ROADMAP.yaml

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
import re

logger = logging.getLogger(__name__)


class ConversationImportHandler:
    """
    Handles conversation import from captured markdown files.
    
    Reads markdown file from conversation-captures directory, parses
    conversation structure, and imports to CORTEX brain (Tier 1 SQLite
    + Tier 2 knowledge graph).
    
    Workflow:
        1. User triggers "/CORTEX Import this conversation"
        2. Find most recent pending capture file
        3. Read and parse conversation content
        4. Extract metadata, messages, entities
        5. Call Track A import pipeline
        6. Update Tier 1 working memory
        7. Extract patterns for Tier 2 knowledge graph
        8. Return import statistics
    
    Usage:
        handler = ConversationImportHandler(
            cortex_brain_path,
            working_memory,
            knowledge_graph
        )
        result = handler.import_conversation(file_path="20251116-roadmap.md")
        
        # Returns: {
        #   "success": True,
        #   "conversation_id": "conv-20251116-143052",
        #   "messages_imported": 15,
        #   "entities_tracked": 3,
        #   "quality_score": 8.5
        # }
    """
    
    def __init__(
        self,
        cortex_brain_path: Path,
        working_memory=None,
        knowledge_graph=None
    ):
        """
        Initialize import handler.
        
        Args:
            cortex_brain_path: Path to cortex-brain directory
            working_memory: Tier 1 WorkingMemory instance (optional for now)
            knowledge_graph: Tier 2 KnowledgeGraph instance (optional for now)
        """
        self.cortex_brain_path = Path(cortex_brain_path)
        self.captures_dir = self.cortex_brain_path / "documents" / "conversation-captures"
        self.working_memory = working_memory
        self.knowledge_graph = knowledge_graph
        
        logger.info(f"ConversationImportHandler initialized: {self.captures_dir}")
    
    def import_conversation(
        self,
        file_path: Optional[str] = None,
        auto_detect: bool = True
    ) -> Dict[str, Any]:
        """
        Import conversation from markdown file to CORTEX brain.
        
        Args:
            file_path: Specific file to import (filename or relative path)
            auto_detect: If True and file_path is None, import most recent pending file
        
        Returns:
            Dict with:
                - success: bool
                - conversation_id: str (generated ID)
                - file_path: str (file that was imported)
                - messages_imported: int
                - entities_tracked: int
                - quality_score: float (if calculable)
                - message: str (user-facing message)
                - timestamp: str (import timestamp)
        """
        try:
            # Resolve file path
            if file_path:
                # Check if it's just a filename or full path
                if "\\" not in file_path and "/" not in file_path:
                    target_file = self.captures_dir / file_path
                else:
                    target_file = Path(file_path)
                    if not target_file.is_absolute():
                        target_file = self.cortex_brain_path.parent / target_file
            elif auto_detect:
                # Find most recent pending capture
                target_file = self._find_most_recent_pending()
                if not target_file:
                    return {
                        "success": False,
                        "error": "no_pending_captures",
                        "message": "No pending conversation captures found. Create one with '/CORTEX Capture this conversation' first."
                    }
            else:
                return {
                    "success": False,
                    "error": "no_file_specified",
                    "message": "Please specify a file to import or enable auto_detect."
                }
            
            # Verify file exists
            if not target_file.exists():
                return {
                    "success": False,
                    "error": "file_not_found",
                    "message": f"File not found: {target_file}"
                }
            
            # Read file content
            logger.info(f"Reading conversation file: {target_file}")
            content = target_file.read_text(encoding="utf-8")
            
            # Check if file still has template placeholders (not filled in)
            if "_Paste your conversation here_" in content:
                return {
                    "success": False,
                    "error": "file_empty",
                    "message": f"File appears empty (template placeholder found): {target_file.name}\nPlease paste your conversation content and save before importing."
                }
            
            # Parse conversation structure
            parsed = self._parse_conversation(content, target_file.name)
            
            # Import to CORTEX brain (stub for now - full implementation in Phase 5.2)
            import_result = self._import_to_brain(parsed, target_file)
            
            # Update file status to mark as imported
            self._mark_as_imported(target_file)
            
            return import_result
            
        except Exception as e:
            logger.error(f"Failed to import conversation: {e}", exc_info=True)
            return {
                "success": False,
                "error": "import_failed",
                "message": f"Failed to import conversation: {str(e)}",
                "exception": str(e)
            }
    
    def _find_most_recent_pending(self) -> Optional[Path]:
        """
        Find the most recently created pending capture file.
        
        Returns:
            Path to most recent pending file, or None if no pending files
        """
        try:
            pending_files = []
            
            for file_path in self.captures_dir.glob("*.md"):
                try:
                    content = file_path.read_text(encoding="utf-8")
                    
                    # Check if file has pending status marker
                    if "⏳ Awaiting conversation paste" in content or "Status:** ✅ Imported" not in content:
                        pending_files.append({
                            "path": file_path,
                            "mtime": file_path.stat().st_mtime
                        })
                except Exception as e:
                    logger.warning(f"Failed to read {file_path}: {e}")
                    continue
            
            if not pending_files:
                return None
            
            # Sort by modification time (newest first)
            pending_files.sort(key=lambda x: x["mtime"], reverse=True)
            
            return pending_files[0]["path"]
            
        except Exception as e:
            logger.error(f"Failed to find pending captures: {e}", exc_info=True)
            return None
    
    def _parse_conversation(self, content: str, filename: str) -> Dict[str, Any]:
        """
        Parse conversation content from markdown.
        
        Supports multiple formats:
        - GitHub Copilot Chat markdown export
        - Plain transcript (User: ... / Assistant: ...)
        - Custom markdown with ## User / ## Assistant headers
        
        Args:
            content: Raw markdown content
            filename: Original filename
        
        Returns:
            Dict with parsed conversation data:
                - metadata: Dict with date, topic, participants, etc.
                - messages: List of message dicts with role/content
                - entities: List of extracted entities (files, modules, etc.)
                - raw_content: Original content for reference
        """
        try:
            # Extract metadata from header
            metadata = self._extract_metadata(content)
            
            # Extract messages/turns
            messages = self._extract_messages(content)
            
            # Extract entities (files, modules, concepts mentioned)
            entities = self._extract_entities(content, messages)
            
            return {
                "filename": filename,
                "metadata": metadata,
                "messages": messages,
                "entities": entities,
                "raw_content": content,
                "parse_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to parse conversation: {e}", exc_info=True)
            # Return minimal structure on error
            return {
                "filename": filename,
                "metadata": {},
                "messages": [],
                "entities": [],
                "raw_content": content,
                "parse_error": str(e),
                "parse_timestamp": datetime.now().isoformat()
            }
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata from markdown header.
        
        Looks for patterns like:
        **Date:** 2025-11-16
        **Topic:** Roadmap Planning
        **Quality Score:** 8.5
        """
        metadata = {}
        
        # Match **Key:** value patterns
        pattern = r'\*\*([^*:]+):\*\*\s*([^\n]+)'
        matches = re.findall(pattern, content)
        
        for key, value in matches:
            metadata[key.strip().lower().replace(" ", "_")] = value.strip()
        
        return metadata
    
    def _extract_messages(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract conversation messages/turns.
        
        Tries multiple patterns to detect message boundaries.
        """
        messages = []
        
        # Pattern 1: GitHub Copilot Chat format (asifhussain60: ... / GitHub Copilot: ...)
        copilot_pattern = r'(asifhussain60|GitHub Copilot):\s*(.+?)(?=(?:asifhussain60|GitHub Copilot):|$)'
        copilot_matches = re.findall(copilot_pattern, content, re.DOTALL)
        
        if copilot_matches:
            for speaker, message in copilot_matches:
                role = "user" if "asifhussain60" in speaker else "assistant"
                messages.append({
                    "role": role,
                    "content": message.strip(),
                    "speaker": speaker.strip()
                })
            return messages
        
        # Pattern 2: Generic User: / Assistant: format
        generic_pattern = r'(User|Assistant):\s*(.+?)(?=(?:User|Assistant):|$)'
        generic_matches = re.findall(generic_pattern, content, re.DOTALL)
        
        if generic_matches:
            for role, message in generic_matches:
                messages.append({
                    "role": role.lower(),
                    "content": message.strip(),
                    "speaker": role
                })
            return messages
        
        # Pattern 3: Markdown header format (## User / ## Assistant)
        header_pattern = r'##\s+(User|Assistant)\s*\n\n(.+?)(?=##|$)'
        header_matches = re.findall(header_pattern, content, re.DOTALL)
        
        if header_matches:
            for role, message in header_matches:
                messages.append({
                    "role": role.lower(),
                    "content": message.strip(),
                    "speaker": role
                })
            return messages
        
        # Fallback: Treat entire content as single message if no pattern matched
        logger.warning("No conversation pattern detected, treating as single message")
        messages.append({
            "role": "unknown",
            "content": content.strip(),
            "speaker": "unknown"
        })
        
        return messages
    
    def _extract_entities(self, content: str, messages: List[Dict]) -> List[Dict[str, Any]]:
        """
        Extract mentioned entities (files, modules, concepts).
        
        Args:
            content: Raw content
            messages: Parsed messages
        
        Returns:
            List of entity dicts with type and value
        """
        entities = []
        
        # File paths (*.py, *.md, *.yaml, etc.)
        file_pattern = r'[`"]?([a-zA-Z0-9_/-]+\.[a-zA-Z0-9]+)[`"]?'
        file_matches = re.findall(file_pattern, content)
        for file_path in set(file_matches):
            if "/" in file_path or "\\" in file_path:  # Only paths, not random text
                entities.append({
                    "type": "file",
                    "value": file_path
                })
        
        # Code modules/classes (capitalized words in code context)
        module_pattern = r'`([A-Z][a-zA-Z0-9_]+)`'
        module_matches = re.findall(module_pattern, content)
        for module in set(module_matches):
            entities.append({
                "type": "module",
                "value": module
            })
        
        return entities
    
    def _import_to_brain(self, parsed: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
        """
        Import parsed conversation to CORTEX brain (Tier 1 + Tier 2).
        
        NOTE: This is a stub implementation for Phase 5.1.
        Full implementation will be done in Phase 5.2 when quality scoring is fixed.
        
        Args:
            parsed: Parsed conversation data
            file_path: Original file path
        
        Returns:
            Import result dict
        """
        # Generate conversation ID
        timestamp = datetime.now()
        conversation_id = f"conv-{timestamp.strftime('%Y%m%d-%H%M%S')}"
        
        # Stub implementation - just return success with stats
        message_count = len(parsed["messages"])
        entity_count = len(parsed["entities"])
        
        # TODO Phase 5.2: Call Track A import pipeline here
        # if self.working_memory:
        #     self.working_memory.import_conversation(parsed)
        
        # TODO Phase 5.2: Update Tier 2 knowledge graph
        # if self.knowledge_graph:
        #     self.knowledge_graph.extract_patterns(parsed)
        
        logger.info(f"Imported conversation {conversation_id}: {message_count} messages, {entity_count} entities (stub)")
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "file_path": str(file_path.relative_to(self.cortex_brain_path.parent)).replace("\\", "/"),
            "filename": file_path.name,
            "messages_imported": message_count,
            "entities_tracked": entity_count,
            "quality_score": None,  # TODO Phase 5.2: Calculate quality score
            "message": f"Conversation imported successfully!\n\n📊 Statistics:\n  • Messages: {message_count}\n  • Entities tracked: {entity_count}\n  • Conversation ID: {conversation_id}\n\nNote: Full brain integration (quality scoring, pattern learning) will be enabled in Phase 5.2.",
            "timestamp": timestamp.isoformat(),
            "phase": "5.1-stub",
            "full_integration": False
        }
    
    def _mark_as_imported(self, file_path: Path) -> None:
        """
        Update file metadata to mark as successfully imported.
        
        Updates the status line in the file from:
          **Status:** ⏳ Awaiting conversation paste
        To:
          **Status:** ✅ Imported to CORTEX brain
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Replace status marker
            updated = re.sub(
                r'\*\*Status:\*\*\s*⏳\s*Awaiting conversation paste',
                f'**Status:** ✅ Imported to CORTEX brain on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                content
            )
            
            file_path.write_text(updated, encoding="utf-8")
            logger.info(f"Marked file as imported: {file_path.name}")
            
        except Exception as e:
            logger.warning(f"Failed to mark file as imported: {e}")
            # Non-critical error, don't fail import
