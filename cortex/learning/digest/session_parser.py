"""
Chat Session Parser for DIGEST Mode.

Detects GitHub Copilot chat sessions and extracts conversation structure.

AC_START: AC-PHASE41-002
Author: Asif Hussain
Date: 2026-02-07
Phase: 41 Stage 1 (ENH-053)
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass, field


@dataclass
class ChatSession:
    """
    Parsed chat session data.
    
    Attributes:
        is_chat_session: Whether content is a Copilot chat
        chat_score: Confidence score (0-10) based on marker count
        user_prompts: List of user prompts extracted
        copilot_responses: List of Copilot responses
        tool_invocations: List of tool calls
        markers_detected: Count of each marker type
    """
    is_chat_session: bool
    chat_score: int
    user_prompts: List[str] = field(default_factory=list)
    copilot_responses: List[str] = field(default_factory=list)
    tool_invocations: List[str] = field(default_factory=list)
    markers_detected: Dict[str, int] = field(default_factory=dict)


class SessionParser:
    """
    Parse chat session content and detect conversation markers.
    
    Detection Strategy:
    - Score based on presence of 6 marker types
    - Threshold: score ≥ 5 = chat session
    - Markers: User:, GitHub Copilot:, [Tool call:, # Drift, # Pattern, # Efficiency
    
    Usage:
        parser = SessionParser()
        session = parser.parse(content)
        if session.is_chat_session:
            print(f"Detected chat with score {session.chat_score}")
    """
    
    def __init__(self, detection_threshold: int = 5):
        """
        Initialize parser.
        
        Args:
            detection_threshold: Minimum score to classify as chat (default: 5)
        """
        self.detection_threshold = detection_threshold
        
        # Chat markers and their weights
        self.markers = {
            "user_prompt": (r"^User:", 2),  # Strong indicator
            "copilot_response": (r"^GitHub Copilot:", 2),  # Strong indicator
            "tool_call": (r"\[Tool call:", 1),
            "drift_comment": (r"# Drift", 1),
            "pattern_comment": (r"# Pattern", 1),
            "efficiency_comment": (r"# Efficiency:", 1)
        }
    
    def parse(self, content: str) -> ChatSession:
        """
        Parse content and detect chat session.
        
        Args:
            content: Text content to analyze
        
        Returns:
            ChatSession with detection results and extracted data
        """
        if not content:
            return ChatSession(
                is_chat_session=False,
                chat_score=0,
                markers_detected={}
            )
        
        # Detect markers
        markers_detected = self._detect_markers(content)
        
        # Calculate chat score
        chat_score = sum(markers_detected.values())
        is_chat = chat_score >= self.detection_threshold
        
        # Extract conversation elements
        user_prompts = self._extract_user_prompts(content) if is_chat else []
        copilot_responses = self._extract_copilot_responses(content) if is_chat else []
        tool_invocations = self._extract_tool_invocations(content) if is_chat else []
        
        return ChatSession(
            is_chat_session=is_chat,
            chat_score=chat_score,
            user_prompts=user_prompts,
            copilot_responses=copilot_responses,
            tool_invocations=tool_invocations,
            markers_detected=markers_detected
        )
    
    def _detect_markers(self, content: str) -> Dict[str, int]:
        """
        Detect presence of chat markers.
        
        Args:
            content: Text to scan
        
        Returns:
            Dict mapping marker name to weight (0 if absent)
        """
        detected = {}
        
        for marker_name, (pattern, weight) in self.markers.items():
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                detected[marker_name] = weight
            else:
                detected[marker_name] = 0
        
        return detected
    
    def _extract_user_prompts(self, content: str) -> List[str]:
        """Extract user prompts from chat."""
        prompts = []
        lines = content.split("\n")
        
        current_prompt = []
        in_user_section = False
        
        for line in lines:
            if line.strip().startswith("User:"):
                # Start new user prompt
                if current_prompt and in_user_section:
                    prompts.append("\n".join(current_prompt))
                current_prompt = [line.replace("User:", "").strip()]
                in_user_section = True
            elif line.strip().startswith("GitHub Copilot:"):
                # End user section
                if current_prompt and in_user_section:
                    prompts.append("\n".join(current_prompt))
                current_prompt = []
                in_user_section = False
            elif in_user_section and line.strip():
                current_prompt.append(line.strip())
        
        # Add last prompt if exists
        if current_prompt and in_user_section:
            prompts.append("\n".join(current_prompt))
        
        return prompts
    
    def _extract_copilot_responses(self, content: str) -> List[str]:
        """Extract Copilot responses from chat."""
        responses = []
        lines = content.split("\n")
        
        current_response = []
        in_copilot_section = False
        
        for line in lines:
            if line.strip().startswith("GitHub Copilot:"):
                # Start new response
                if current_response and in_copilot_section:
                    responses.append("\n".join(current_response))
                current_response = [line.replace("GitHub Copilot:", "").strip()]
                in_copilot_section = True
            elif line.strip().startswith("User:"):
                # End Copilot section
                if current_response and in_copilot_section:
                    responses.append("\n".join(current_response))
                current_response = []
                in_copilot_section = False
            elif in_copilot_section and line.strip():
                current_response.append(line.strip())
        
        # Add last response if exists
        if current_response and in_copilot_section:
            responses.append("\n".join(current_response))
        
        return responses
    
    def _extract_tool_invocations(self, content: str) -> List[str]:
        """Extract tool call mentions from chat."""
        tools = []
        
        # Pattern: [Tool call: tool_name]
        pattern = r"\[Tool call:\s*(\w+)\]"
        matches = re.findall(pattern, content, re.IGNORECASE)
        tools.extend(matches)
        
        # Also look for tool mentions in results
        # Pattern: Result: ... or Command: ...
        result_pattern = r"(Result|Command):\s*(.+?)(?:\n|$)"
        result_matches = re.findall(result_pattern, content, re.IGNORECASE)
        for _, tool_mention in result_matches:
            if tool_mention.strip():
                tools.append(tool_mention.strip()[:50])  # Truncate long commands
        
        return tools


# AC_COMPLETE: AC-PHASE41-002 ✅ Chat session parsing extracts all categories
