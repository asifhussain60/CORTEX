"""
Conversation Capture Handler (Feature 5 - Phase 1: Manual Capture)

Handles the first step of two-step conversation capture workflow:
1. User says "/CORTEX Capture this conversation"
2. This handler creates empty file at cortex-brain/documents/conversation-captures/
3. Returns clickable link for user to open and paste
4. User saves file after pasting
5. User triggers import with /CORTEX Import (handled by import_handler.py)

Part of CORTEX 3.0 Track 1 - Feature 5: Conversation Tracking & Capture
Roadmap: cortex-brain/cortex-3.0-design/CORTEX-3.0-ROADMAP.yaml

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConversationCaptureHandler:
    """
    Handles conversation capture requests from users.
    
    Creates empty markdown file with proper naming convention and metadata
    template. Returns file path for user to open and paste conversation content.
    
    Workflow:
        1. User says "/CORTEX Capture this conversation"
        2. Parse optional description from user message
        3. Create empty file with YYYYMMDD-[description].md naming
        4. Add markdown template with metadata placeholders
        5. Return file path as clickable link
        6. User opens file, pastes conversation, saves
        7. User triggers "/CORTEX Import" (separate handler)
    
    Usage:
        handler = ConversationCaptureHandler(cortex_brain_path)
        result = handler.capture_conversation(description="roadmap planning")
        
        # Returns: {
        #   "success": True,
        #   "file_path": "cortex-brain/documents/conversation-captures/20251116-roadmap-planning.md",
        #   "message": "Empty conversation file created. Click to open, paste content, and save."
        # }
    """
    
    def __init__(self, cortex_brain_path: Path):
        """
        Initialize capture handler.
        
        Args:
            cortex_brain_path: Path to cortex-brain directory (e.g., d:/PROJECTS/CORTEX/cortex-brain)
        """
        self.cortex_brain_path = Path(cortex_brain_path)
        self.captures_dir = self.cortex_brain_path / "documents" / "conversation-captures"
        
        # Ensure captures directory exists
        self.captures_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ConversationCaptureHandler initialized: {self.captures_dir}")
    
    def capture_conversation(
        self,
        description: Optional[str] = None,
        topic: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create empty conversation capture file for user to paste into.
        
        Args:
            description: Brief description for filename (optional, will sanitize)
            topic: Conversation topic for metadata (optional)
            metadata: Additional metadata to include in template (optional)
        
        Returns:
            Dict with:
                - success: bool
                - file_path: str (relative to project root)
                - absolute_path: str (full filesystem path)
                - message: str (user-facing message)
                - timestamp: str (ISO format)
        
        Example:
            result = handler.capture_conversation(description="api design")
            # Creates: 20251116-api-design.md
        """
        try:
            # Generate filename
            timestamp = datetime.now()
            date_prefix = timestamp.strftime("%Y%m%d")
            
            # Sanitize description for filename
            if description:
                # Remove special characters, keep alphanumeric and dashes
                sanitized = "".join(c if c.isalnum() or c in " -_" else "" for c in description)
                # Replace spaces with dashes, remove multiple dashes
                sanitized = "-".join(filter(None, sanitized.lower().split()))
                # Truncate to reasonable length to avoid Windows path length limits
                max_desc_length = 100  # Conservative limit for description portion
                if len(sanitized) > max_desc_length:
                    sanitized = sanitized[:max_desc_length].rstrip("-")
                filename = f"{date_prefix}-{sanitized}.md"
            else:
                # Auto-generate description from timestamp
                time_suffix = timestamp.strftime("%H%M%S")
                filename = f"{date_prefix}-{time_suffix}-conversation.md"
            
            # Full file path
            file_path = self.captures_dir / filename
            
            # Check if file already exists
            if file_path.exists():
                logger.warning(f"File already exists: {file_path}")
                return {
                    "success": False,
                    "error": "file_exists",
                    "message": f"File already exists: {filename}. Choose a different description or delete the existing file.",
                    "file_path": str(file_path.relative_to(self.cortex_brain_path.parent)),
                    "absolute_path": str(file_path)
                }
            
            # Create markdown template
            template = self._generate_template(
                timestamp=timestamp,
                topic=topic or description or "Conversation",
                metadata=metadata
            )
            
            # Write empty file with template
            file_path.write_text(template, encoding="utf-8")
            
            logger.info(f"Created conversation capture file: {file_path}")
            
            # Construct relative path from project root
            relative_path = file_path.relative_to(self.cortex_brain_path.parent)
            
            return {
                "success": True,
                "file_path": str(relative_path).replace("\\", "/"),  # Use forward slashes
                "absolute_path": str(file_path),
                "filename": filename,
                "message": f"Empty conversation file created: {filename}\n\nNext steps:\n1. Open the file (click link above)\n2. Paste your conversation content\n3. Save the file\n4. Say '/CORTEX Import this conversation' to import to brain",
                "timestamp": timestamp.isoformat(),
                "captures_dir": str(self.captures_dir)
            }
            
        except Exception as e:
            logger.error(f"Failed to create conversation capture file: {e}", exc_info=True)
            return {
                "success": False,
                "error": "creation_failed",
                "message": f"Failed to create conversation file: {str(e)}",
                "exception": str(e)
            }
    
    def _generate_template(
        self,
        timestamp: datetime,
        topic: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate markdown template for conversation capture file.
        
        Args:
            timestamp: Capture timestamp
            topic: Conversation topic
            metadata: Additional metadata to include
        
        Returns:
            Markdown template string
        """
        date_str = timestamp.strftime("%Y-%m-%d")
        time_str = timestamp.strftime("%H:%M:%S")
        
        # Build metadata section
        meta_lines = [
            f"**Date:** {date_str}",
            f"**Time:** {time_str}",
            f"**Topic:** {topic}",
            "**Participants:** User, GitHub Copilot",
            "**Status:** ⏳ Awaiting conversation paste"
        ]
        
        # Add custom metadata if provided
        if metadata:
            for key, value in metadata.items():
                meta_lines.append(f"**{key.title()}:** {value}")
        
        # Construct template
        template = f"""# Conversation Capture: {topic}

{chr(10).join(meta_lines)}

**Quality Score:** _To be calculated on import_

---

## Instructions

1. **Copy** your GitHub Copilot Chat conversation
2. **Paste** it below this line (replace this instruction)
3. **Save** this file
4. **Import** by saying: `/CORTEX Import this conversation`

---

## Conversation Content

_Paste your conversation here..._

<!-- 
CORTEX will parse this file when you trigger import.
Supported formats:
- GitHub Copilot Chat markdown export
- Plain conversation transcript (User: ... / Assistant: ...)
- Custom markdown with ## User / ## Assistant headers
-->

---

**Captured:** {timestamp.isoformat()}  
**Status:** Ready for user to paste conversation content  
**Next Step:** Paste conversation above and save file
"""
        
        return template
    
    def list_pending_captures(self) -> Dict[str, Any]:
        """
        List all pending conversation captures (files with status "Awaiting conversation paste").
        
        Returns:
            Dict with:
                - success: bool
                - pending_files: List[Dict] with file info
                - count: int
        """
        try:
            pending_files = []
            
            for file_path in self.captures_dir.glob("*.md"):
                try:
                    content = file_path.read_text(encoding="utf-8")
                    
                    # Check if file has pending status marker
                    if "⏳ Awaiting conversation paste" in content or "_Paste your conversation here_" in content:
                        pending_files.append({
                            "filename": file_path.name,
                            "path": str(file_path.relative_to(self.cortex_brain_path.parent)).replace("\\", "/"),
                            "created": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                            "size_bytes": file_path.stat().st_size
                        })
                except Exception as e:
                    logger.warning(f"Failed to read {file_path}: {e}")
                    continue
            
            # Sort by creation time (newest first)
            pending_files.sort(key=lambda x: x["created"], reverse=True)
            
            return {
                "success": True,
                "pending_files": pending_files,
                "count": len(pending_files),
                "captures_dir": str(self.captures_dir)
            }
            
        except Exception as e:
            logger.error(f"Failed to list pending captures: {e}", exc_info=True)
            return {
                "success": False,
                "error": "list_failed",
                "message": f"Failed to list pending captures: {str(e)}",
                "exception": str(e)
            }
