"""
Chat Response Policy for CORTEX.

Enforces 3-section business-friendly structure, suppresses tool narration,
and ensures single PROCEED directive for autonomous execution.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 29 specification (AC-29-F1, AC-29-F2, AC-29-F3, AC-29-F7)
"""

import re
from typing import List, Tuple
from dataclasses import dataclass


class ResponseStructureError(Exception):
    """Raised when response structure is invalid."""
    pass


class NarrationDetectedError(Exception):
    """Raised when tool narration is detected in response."""
    pass


@dataclass
class ChatResponsePolicy:
    """
    Policy enforcer for Copilot Chat responses.
    
    Enforces:
    - EXACTLY 3 sections (What was asked | What's recommended | Next steps)
    - NO tool narration ("Let me read...", "Perfect!", etc.)
    - Single "Next Step: PROCEED" directive (no preference questions)
    - Response header mandatory (CORE-029)
    
    Example:
        >>> policy = ChatResponsePolicy()
        >>> response = "..."  # Raw response
        >>> clean_response = policy.apply(response)
    """
    
    required_section_count: int = 3
    suppress_narration_enabled: bool = True
    enforce_proceed_enabled: bool = True
    
    # Tool narration patterns to suppress
    NARRATION_PATTERNS = [
        r"Let me (read|check|search|look|analyze|examine)",
        r"Perfect!",
        r"Great!",
        r"Excellent!",
        r"Looking at",
        r"I'll (search|read|check|analyze|examine)",
        r"I notice that",
        r"After reviewing",
        r"I can see",
        r"Now let's",
    ]
    
    # Preference question patterns to remove
    PREFERENCE_PATTERNS = [
        r"Which approach do you prefer\?",
        r"Please select.*",
        r"Choose (one|an option).*",
        r"[1-9]️⃣\s+Option [A-Z]",
        r"Option [A-Z]:",
        r"\d+️⃣.*?Option.*",
    ]
    
    def validate_response_structure(self, response: str) -> Tuple[bool, List[str]]:
        """
        Validate response has exactly 3 sections and mandatory header.
        
        Args:
            response: Response text to validate
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        if not response or not response.strip():
            errors.append("Response is empty")
            return False, errors
        
        # Check for header (CORE-029)
        header_pattern = r"^##\s+🧠\s+CORTEX"
        if not re.search(header_pattern, response, re.MULTILINE):
            errors.append("Response header missing (CORE-029 violation)")
        
        # Count sections (### headers)
        section_pattern = r"^###\s+"
        sections = re.findall(section_pattern, response, re.MULTILINE)
        section_count = len(sections)
        
        if section_count != self.required_section_count:
            errors.append(
                f"Expected exactly {self.required_section_count} sections, "
                f"found {section_count}"
            )
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def contains_tool_narration(self, text: str) -> bool:
        """
        Check if text contains tool narration phrases.
        
        Args:
            text: Text to check
            
        Returns:
            True if narration detected
        """
        for pattern in self.NARRATION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def suppress_narration(self, response: str) -> str:
        """
        Remove tool narration from response.
        
        Args:
            response: Response with potential narration
            
        Returns:
            Response with narration removed
        """
        if not self.suppress_narration_enabled:
            return response
        
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that are pure narration
            if self.contains_tool_narration(line):
                # Check if line has technical content after narration
                # e.g., "Perfect! The adapter uses JSON." -> keep "The adapter uses JSON."
                for pattern in self.NARRATION_PATTERNS:
                    line = re.sub(pattern, '', line, flags=re.IGNORECASE)
                
                # Only keep line if it has substantial content left
                if line.strip() and len(line.strip()) > 10:
                    cleaned_lines.append(line.strip())
            else:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def enforce_proceed_directive(self, response: str) -> str:
        """
        Ensure response ends with single 'Next Step: PROCEED' directive.
        
        Removes preference questions and forces single directive.
        
        Args:
            response: Response to enforce
            
        Returns:
            Response with PROCEED directive
        """
        if not self.enforce_proceed_enabled:
            return response
        
        # Remove preference questions
        for pattern in self.PREFERENCE_PATTERNS:
            response = re.sub(pattern, '', response, flags=re.MULTILINE)
        
        # Check if PROCEED already exists
        proceed_pattern = r"\*\*Next Step:\*\*\s+PROCEED"
        has_proceed = re.search(proceed_pattern, response)
        
        if not has_proceed:
            # Add PROCEED directive
            # Find the last section (### 3)
            last_section_match = re.search(
                r"(###\s+3[).\]]\s+[^\n]+.*?)$",
                response,
                re.DOTALL | re.MULTILINE
            )
            
            if last_section_match:
                # Append to last section
                response += "\n\n**Next Step:** PROCEED"
            else:
                # No section 3 found, append to end
                response += "\n\n### 3) Next steps\n\n**Next Step:** PROCEED"
        
        return response
    
    def apply(self, response: str) -> str:
        """
        Apply all policies to response.
        
        Args:
            response: Raw response
            
        Returns:
            Policy-compliant response
        """
        # 1. Suppress narration
        response = self.suppress_narration(response)
        
        # 2. Enforce PROCEED directive
        response = self.enforce_proceed_directive(response)
        
        return response
