"""
Conversation Importer
====================

Purpose: Main orchestrator for manual conversation import into CORTEX brain.
Coordinates parsing, extraction, and storage of captured conversations.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

from typing import Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime
import logging

from ..parsers.copilot_parser import CopilotParser
from ..extractors.semantic_extractor import SemanticExtractor
from ..integrations.conversational_channel_adapter import ConversationalChannelAdapter


logger = logging.getLogger(__name__)


class ConversationImportError(Exception):
    """Raised when conversation import fails."""
    pass


class ValidationError(Exception):
    """Raised when conversation validation fails."""
    pass


class ConversationImporter:
    """
    Main orchestrator for importing captured conversations into CORTEX brain.
    
    Workflow:
    1. Accept input (file path, text content, or clipboard)
    2. Validate conversation structure
    3. Parse with appropriate parser (CopilotParser, etc.)
    4. Extract semantic information (entities, intents, patterns)
    5. Route to ConversationalChannel for storage
    6. Return import report with statistics
    
    Example:
        ```python
        importer = ConversationImporter()
        
        # Import from file
        report = importer.import_from_file("conversation-capture-2025-11-15.md")
        
        # Import from text
        report = importer.import_from_text(conversation_text)
        
        # Import from clipboard
        report = importer.import_from_clipboard()
        ```
    """
    
    def __init__(self):
        """Initialize ConversationImporter with required components."""
        self.parser = CopilotParser()
        self.extractor = SemanticExtractor()
        self.channel_adapter = ConversationalChannelAdapter()
        
        logger.info("ConversationImporter initialized")
    
    def import_from_file(
        self,
        file_path: Union[str, Path],
        validate: bool = True,
        extract_semantics: bool = True
    ) -> Dict:
        """
        Import conversation from a file.
        
        Args:
            file_path: Path to conversation file (Markdown, JSON, or text)
            validate: Whether to validate conversation structure
            extract_semantics: Whether to extract entities/intents
        
        Returns:
            Import report dictionary with statistics and status
        
        Raises:
            ConversationImportError: If import fails
            ValidationError: If validation fails
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Conversation file not found: {file_path}")
        
        logger.info(f"Importing conversation from file: {file_path}")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise ConversationImportError(f"Failed to read file: {e}")
        
        # Import with content
        return self._import_conversation(
            content=content,
            source=str(file_path),
            validate=validate,
            extract_semantics=extract_semantics
        )
    
    def import_from_text(
        self,
        content: str,
        source: str = "manual_text",
        validate: bool = True,
        extract_semantics: bool = True
    ) -> Dict:
        """
        Import conversation from text content.
        
        Args:
            content: Conversation text (Markdown or JSON format)
            source: Source identifier (e.g., "manual_text", "clipboard")
            validate: Whether to validate conversation structure
            extract_semantics: Whether to extract entities/intents
        
        Returns:
            Import report dictionary with statistics and status
        
        Raises:
            ConversationImportError: If import fails
            ValidationError: If validation fails
        """
        logger.info(f"Importing conversation from text (source: {source})")
        
        return self._import_conversation(
            content=content,
            source=source,
            validate=validate,
            extract_semantics=extract_semantics
        )
    
    def import_from_clipboard(
        self,
        validate: bool = True,
        extract_semantics: bool = True
    ) -> Dict:
        """
        Import conversation from clipboard.
        
        Args:
            validate: Whether to validate conversation structure
            extract_semantics: Whether to extract entities/intents
        
        Returns:
            Import report dictionary with statistics and status
        
        Raises:
            ConversationImportError: If import fails
            ValidationError: If validation fails
        
        Note:
            Requires pyperclip or similar clipboard access library.
            Falls back to manual text input if clipboard unavailable.
        """
        logger.info("Importing conversation from clipboard")
        
        # Try to get clipboard content
        try:
            import pyperclip
            content = pyperclip.paste()
        except ImportError:
            raise ConversationImportError(
                "Clipboard access requires 'pyperclip' package. "
                "Install with: pip install pyperclip"
            )
        except Exception as e:
            raise ConversationImportError(f"Failed to access clipboard: {e}")
        
        if not content or not content.strip():
            raise ConversationImportError("Clipboard is empty")
        
        return self._import_conversation(
            content=content,
            source="clipboard",
            validate=validate,
            extract_semantics=extract_semantics
        )
    
    def _import_conversation(
        self,
        content: str,
        source: str,
        validate: bool,
        extract_semantics: bool
    ) -> Dict:
        """
        Internal method to orchestrate conversation import workflow.
        
        Workflow:
        1. Validate input if requested
        2. Parse conversation with CopilotParser
        3. Extract semantic information if requested
        4. Store via ConversationalChannelAdapter
        5. Generate import report
        
        Args:
            content: Conversation content
            source: Source identifier
            validate: Whether to validate
            extract_semantics: Whether to extract semantics
        
        Returns:
            Import report dictionary
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Validate input
            if validate:
                validation_result = self._validate_conversation(content)
                if not validation_result["valid"]:
                    raise ValidationError(
                        f"Validation failed: {validation_result['errors']}"
                    )
            
            # Step 2: Parse conversation
            parsed_conversation = self.parser.parse(content)
            
            if not parsed_conversation:
                raise ConversationImportError("Parser returned empty result")
            
            # Step 3: Extract semantic information
            if extract_semantics:
                semantic_data = self.extractor.extract(parsed_conversation)
                parsed_conversation["semantic_data"] = semantic_data
            
            # Step 4: Store via ConversationalChannel
            storage_result = self.channel_adapter.store_conversation(
                conversation=parsed_conversation,
                source=source
            )
            
            # Step 5: Generate import report
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Create nested import_report for test compatibility
            import_report = {
                "total_messages": len(parsed_conversation.get("messages", [])),
                "entities_extracted": len(
                    parsed_conversation.get("semantic_data", {}).get("entities", [])
                ) if extract_semantics else 0,
                "intents_detected": len(
                    parsed_conversation.get("semantic_data", {}).get("intents", [])
                ) if extract_semantics else 0,
                "quality_score": parsed_conversation.get("semantic_data", {}).get(
                    "quality_score"
                ) if extract_semantics else None,
                "duration_seconds": duration,
            }
            
            report = {
                "status": "success",  # Add status field expected by tests
                "success": True,  # Keep for backward compatibility
                "conversation_id": storage_result.get("conversation_id"),
                "conversation": parsed_conversation,  # Add full conversation data
                "source": source,
                "format": parsed_conversation.get("format"),  # Add format field
                "messages_imported": import_report["total_messages"],
                "entities_extracted": import_report["entities_extracted"],
                "intents_detected": import_report["intents_detected"],
                "quality_score": import_report["quality_score"],
                "quality_factors": parsed_conversation.get("semantic_data", {}).get(
                    "quality_factors", {}
                ) if extract_semantics else {},  # Add quality factors
                "duration_seconds": duration,
                "timestamp": datetime.now().isoformat(),
                "storage_result": storage_result,
                "import_report": import_report  # Add nested import_report for tests
            }
            
            logger.info(
                f"Conversation imported successfully: "
                f"{report['messages_imported']} messages, "
                f"{report['entities_extracted']} entities"
            )
            
            return report
        
        except Exception as e:
            logger.error(f"Conversation import failed: {e}")
            
            return {
                "status": "error",  # Add status field expected by tests
                "success": False,  # Keep for backward compatibility
                "error": str(e),
                "error_type": type(e).__name__,
                "source": source,
                "timestamp": datetime.now().isoformat()
            }
    
    def _validate_conversation(self, content: str) -> Dict:
        """
        Validate conversation structure and content.
        
        Validation checks:
        - Non-empty content
        - Minimum length (avoid accidental imports)
        - Contains conversation markers (user/assistant)
        - Valid format (Markdown or JSON)
        
        Args:
            content: Conversation content to validate
        
        Returns:
            Validation result dictionary with 'valid' boolean and 'errors' list
        """
        errors = []
        
        # Check 1: Non-empty
        if not content or not content.strip():
            errors.append("Content is empty")
        
        # Check 2: Minimum length (50 characters)
        elif len(content.strip()) < 50:
            errors.append("Content too short (minimum 50 characters)")
        
        # Check 3: Contains conversation markers
        content_lower = content.lower()
        has_user = any(marker in content_lower for marker in ["user:", "you:", "human:"])
        has_assistant = any(
            marker in content_lower 
            for marker in ["assistant:", "cortex:", "copilot:", "ai:"]
        )
        
        if not (has_user or has_assistant):
            errors.append(
                "No conversation markers found "
                "(expected 'user:', 'assistant:', etc.)"
            )
        
        # Check 4: Format detection (Markdown or JSON)
        is_markdown = "```" in content or "#" in content
        is_json = content.strip().startswith("{") and content.strip().endswith("}")
        
        if not (is_markdown or is_json):
            errors.append(
                "Unrecognized format (expected Markdown or JSON)"
            )
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def get_import_statistics(self) -> Dict:
        """
        Get statistics about imported conversations.
        
        Returns:
            Statistics dictionary from ConversationalChannelAdapter
        """
        return self.channel_adapter.get_statistics()


# Convenience function for quick imports
def quick_import(file_path: str) -> Dict:
    """
    Quick import helper function.
    
    Args:
        file_path: Path to conversation file
    
    Returns:
        Import report dictionary
    
    Example:
        ```python
        from track_a.conversation_import import quick_import
        
        report = quick_import("conversation-capture-2025-11-15.md")
        print(f"Imported {report['messages_imported']} messages")
        ```
    """
    importer = ConversationImporter()
    return importer.import_from_file(file_path)
