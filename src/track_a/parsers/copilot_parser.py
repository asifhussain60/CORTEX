"""
GitHub Copilot Chat Parser
==========================

Purpose: Parse GitHub Copilot Chat conversations into normalized CORTEX format.
Handles both Markdown and JSON conversation formats.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import re
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class CopilotParserError(Exception):
    """Raised when parsing fails."""
    pass


class CopilotParser:
    """
    Parser for GitHub Copilot Chat conversation formats.
    
    Supported formats:
    - Markdown conversation captures (most common)
    - JSON exports from VS Code Copilot Chat
    - Plain text with conversation markers
    
    Output format:
    {
        "format": "markdown" | "json" | "text",
        "messages": [
            {
                "role": "user" | "assistant",
                "content": "message text",
                "timestamp": "ISO 8601 timestamp",
                "metadata": {}
            }
        ],
        "metadata": {
            "source": "copilot_chat",
            "parsed_at": "ISO 8601 timestamp",
            "message_count": int,
            "has_code_blocks": bool
        }
    }
    """
    
    def __init__(self):
        """Initialize CopilotParser."""
        # Regex patterns for different conversation markers
        # Support both plain and markdown bold format (**User:** or User:)
        self.user_patterns = [
            r"^\*\*User:\*\*",  # Markdown bold
            r"^User:",
            r"^\*\*You:\*\*",
            r"^You:",
            r"^\*\*Human:\*\*",
            r"^Human:",
            r"^👤",  # User emoji
        ]
        
        self.assistant_patterns = [
            r"^\*\*Assistant:\*\*",  # Markdown bold
            r"^Assistant:",
            r"^\*\*Copilot:\*\*",
            r"^Copilot:",
            r"^\*\*CORTEX:\*\*",
            r"^CORTEX:",
            r"^🧠",  # Brain emoji (CORTEX)
            r"^🤖",  # Robot emoji
        ]
        
        logger.info("CopilotParser initialized")
    
    def parse(self, content: str) -> Dict:
        """
        Parse conversation content into normalized format.
        
        Args:
            content: Raw conversation content
        
        Returns:
            Parsed conversation dictionary
        
        Raises:
            CopilotParserError: If parsing fails
        """
        if not content or not content.strip():
            # Return empty result for empty content (edge case)
            return {
                "format": "text",
                "messages": [],
                "metadata": {
                    "source": "copilot_chat",
                    "parsed_at": datetime.now().isoformat(),
                    "message_count": 0,
                    "has_code_blocks": False
                }
            }
        
        # Detect format
        format_type = self._detect_format(content)
        
        logger.info(f"Detected conversation format: {format_type}")
        
        # Parse based on format
        if format_type == "json":
            return self._parse_json(content)
        elif format_type == "markdown":
            return self._parse_markdown(content)
        else:
            return self._parse_text(content)
    
    def _detect_format(self, content: str) -> str:
        """
        Detect conversation format.
        
        Args:
            content: Raw content
        
        Returns:
            Format type: "json", "markdown", or "text"
        """
        content_stripped = content.strip()
        
        # Check JSON
        if content_stripped.startswith("{") and content_stripped.endswith("}"):
            try:
                json.loads(content)
                return "json"
            except:
                pass
        
        # Check Markdown (has ** bold markers or code blocks or headers)
        if "**" in content or "```" in content or re.search(r"^#+\s", content, re.MULTILINE):
            return "markdown"
        
        # Default to plain text
        return "text"
    
    def _parse_json(self, content: str) -> Dict:
        """
        Parse JSON format conversation.
        
        Expected JSON structure:
        {
            "messages": [
                {"role": "user", "content": "...", "timestamp": "..."},
                {"role": "assistant", "content": "...", "timestamp": "..."}
            ]
        }
        """
        try:
            data = json.loads(content)
            
            if "messages" not in data:
                raise CopilotParserError("JSON missing 'messages' field")
            
            messages = []
            for msg in data["messages"]:
                if "role" not in msg or "content" not in msg:
                    logger.warning("Skipping message missing role or content")
                    continue
                
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg.get("timestamp", datetime.now().isoformat()),
                    "metadata": msg.get("metadata", {})
                })
            
            return {
                "format": "json",
                "messages": messages,
                "metadata": {
                    "source": "copilot_chat",
                    "parsed_at": datetime.now().isoformat(),
                    "message_count": len(messages),
                    "has_code_blocks": any("```" in m["content"] for m in messages)
                }
            }
        
        except json.JSONDecodeError as e:
            raise CopilotParserError(f"Invalid JSON: {e}")
    
    def _parse_markdown(self, content: str) -> Dict:
        """
        Parse Markdown format conversation.
        
        Handles:
        - User: / Assistant: markers
        - Emoji markers (👤, 🧠, 🤖)
        - Code blocks
        - Timestamps
        """
        messages = []
        lines = content.split("\n")
        
        current_role = None
        current_content = []
        
        for line in lines:
            # Check for role markers
            is_user = any(re.match(pattern, line, re.IGNORECASE) for pattern in self.user_patterns)
            is_assistant = any(re.match(pattern, line, re.IGNORECASE) for pattern in self.assistant_patterns)
            
            if is_user or is_assistant:
                # Save previous message if exists
                if current_role and current_content:
                    messages.append({
                        "role": current_role,
                        "content": "\n".join(current_content).strip(),
                        "timestamp": datetime.now().isoformat(),
                        "metadata": {}
                    })
                
                # Start new message
                current_role = "user" if is_user else "assistant"
                current_content = []
                
                # Extract content after marker (handle both markdown bold and plain)
                content_after_marker = re.sub(
                    r"^(\*\*)?(User:|You:|Human:|Assistant:|Copilot:|CORTEX:|👤|🧠|🤖)(\*\*)?\s*",
                    "",
                    line,
                    flags=re.IGNORECASE
                ).strip()
                
                if content_after_marker:
                    current_content.append(content_after_marker)
            
            elif current_role:
                # Continue current message
                current_content.append(line)
        
        # Add last message
        if current_role and current_content:
            messages.append({
                "role": current_role,
                "content": "\n".join(current_content).strip(),
                "timestamp": datetime.now().isoformat(),
                "metadata": {}
            })
        
        if not messages:
            # Return empty result for content without role markers (edge case)
            return {
                "format": "markdown",
                "messages": [],
                "metadata": {
                    "source": "copilot_chat",
                    "parsed_at": datetime.now().isoformat(),
                    "message_count": 0,
                    "has_code_blocks": False,
                    "format": "markdown"
                }
            }
        
        return {
            "format": "markdown",
            "messages": messages,
            "metadata": {
                "source": "copilot_chat",
                "parsed_at": datetime.now().isoformat(),
                "message_count": len(messages),
                "has_code_blocks": any("```" in m["content"] for m in messages),
                "format": "markdown"
            }
        }
    
    def _parse_text(self, content: str) -> Dict:
        """
        Parse plain text conversation (fallback parser).
        
        Uses same logic as Markdown but more lenient.
        """
        # Use Markdown parser as fallback
        return self._parse_markdown(content)
    
    def extract_code_blocks(self, conversation: Dict) -> List[Dict]:
        """
        Extract code blocks from conversation messages.
        
        Args:
            conversation: Parsed conversation dictionary
        
        Returns:
            List of code blocks with language and content
        """
        code_blocks = []
        
        for msg in conversation.get("messages", []):
            content = msg["content"]
            
            # Find code blocks with language
            pattern = r"```(\w+)?\n(.*?)```"
            matches = re.findall(pattern, content, re.DOTALL)
            
            for language, code in matches:
                code_blocks.append({
                    "language": language or "unknown",
                    "code": code.strip(),
                    "message_role": msg["role"]
                })
        
        return code_blocks
