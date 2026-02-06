"""Chat Response Policy - Enforce 3-Section Structure & Suppress Verbosity

Implements chat response formatting rules for Copilot Chat sessions:
1) Exactly 3 sections (What was asked, What's recommended, Next steps)
2) Concise, business-language bullets (role-inclusive)
3) Suppress narration ("Let me read...", "Perfect!", tool call logs)
4) Enforce "Next Step: PROCEED" (no options/choices)
5) Compact ASCII plan spines when progress shown

Authority: chat02.txt (Change Request)
Author: CORTEX Framework
Date: 2026-02-06
Version: 1.0.0
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from abc import ABC, abstractmethod


class SectionType(str, Enum):
    """Chat response section types"""
    WHAT_WAS_ASKED = "what_was_asked"
    WHATS_RECOMMENDED = "whats_recommended"
    NEXT_STEPS = "next_steps"


class VerbosityPattern(str, Enum):
    """Patterns to suppress from chat output"""
    
    # Narration patterns
    LET_ME_READ = r"\blet me read|reading\b"
    LET_ME_SEARCH = r"\blet me search|searching for|searched for\b"
    PERFECT = r"\bperfect!|great!|excellent!\b"
    NOW_I_WILL = r"\bnow i (will|can|can do|proceed)|now (i'll|we'll)\b"
    
    # Tool call narration
    READ_FILE = r"\bred file|read (lines|file|content)\b"
    SEARCHED_FOR = r"\bsearched for|search results for\b"
    USING_REPLACE = r"\busing (replace|edit) (string|file)\b"
    GREP_SEARCH = r"\bgrep.*search|pattern matching\b"
    
    # Verbose headers
    COMPREHENSIVE_SUMMARY = r"\bdue to (length|complexity).*comprehensive summary\b"
    SUMMARIZING = r"\bsummarizing (conversation|context)\b"
    
    # Verbose transitions
    VERBOSE_TRANSITIONS = r"\b(furthermore|moreover|additionally|in addition)\b"


@dataclass
class ChatSection:
    """Represents one section of a 3-section response"""
    
    type: SectionType
    title: str
    bullets: List[str] = field(default_factory=list)
    max_bullets: int = 7
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """Validate section constraints"""
        if not self.bullets:
            return False, f"Section '{self.title}' has no bullets"
        
        if len(self.bullets) > self.max_bullets:
            return False, f"Section '{self.title}' exceeds {self.max_bullets} bullets ({len(self.bullets)} found)"
        
        if self.type == SectionType.WHAT_WAS_ASKED and len(self.bullets) > 5:
            return False, "Section 1 (What was asked) limited to 5 bullets max"
        
        if self.type == SectionType.NEXT_STEPS:
            # Check that last bullet contains "Next Step: PROCEED"
            last_bullet = self.bullets[-1] if self.bullets else ""
            if "Next Step: PROCEED" not in last_bullet:
                return False, "Section 3 (Next steps) must end with 'Next Step: PROCEED'"
            
            # Check no options present
            options_pattern = r"\boption\s+\d+|option\s+[a-z]|which\s+do\s+you|choose\s+between"
            if re.search(options_pattern, " ".join(self.bullets), re.IGNORECASE):
                return False, "Section 3 must not contain options or choices"
        
        return True, None
    
    def to_markdown(self) -> str:
        """Render section to markdown"""
        lines = [f"\n## {self.title}"]
        lines.extend(f"- {bullet}" for bullet in self.bullets)
        return "\n".join(lines)


@dataclass
class PlanSpineProgress:
    """ASCII plan spine progress indicator"""
    
    phases: List[Tuple[str, str]] = field(default_factory=list)  # (name, status)
    
    # Status glyphs (strict set)
    GLYPH_COMPLETED = "[✓]"
    GLYPH_ACTIVE = "[→]"
    GLYPH_BLOCKED = "[!]"
    GLYPH_REVISITING = "[~]"
    GLYPH_NOT_STARTED = "[ ]"
    
    def add_phase(self, name: str, status: str) -> None:
        """Add phase to plan spine"""
        # Validate status is one of allowed glyphs
        allowed = [
            "completed", "active", "blocked", "revisiting", "not_started"
        ]
        if status not in allowed:
            raise ValueError(f"Invalid status: {status}. Must be one of {allowed}")
        
        self.phases.append((name, status))
    
    def to_ascii(self, max_lines: int = 8) -> str:
        """Render to compact ASCII (max 8 lines)"""
        if not self.phases:
            return ""
        
        lines = ["Plan Progress:"]
        
        # Limit phases to fit within max_lines constraint
        phases_to_show = self.phases[:max_lines - 1]
        remaining = len(self.phases) - len(phases_to_show)
        
        glyph_map = {
            "completed": self.GLYPH_COMPLETED,
            "active": self.GLYPH_ACTIVE,
            "blocked": self.GLYPH_BLOCKED,
            "revisiting": self.GLYPH_REVISITING,
            "not_started": self.GLYPH_NOT_STARTED,
        }
        
        for i, (name, status) in enumerate(phases_to_show):
            glyph = glyph_map.get(status, "[ ]")
            is_last = (i == len(phases_to_show) - 1) and remaining == 0
            connector = "└─" if is_last else "├─"
            lines.append(f"{connector} {glyph} {name}")
        
        if remaining > 0:
            lines.append(f"└─ [ ] +{remaining} phases remaining")
        
        return "\n".join(lines)
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """Validate plan spine"""
        allowed_statuses = {"completed", "active", "blocked", "revisiting", "not_started"}
        
        for name, status in self.phases:
            if status not in allowed_statuses:
                return False, f"Invalid phase status '{status}' for '{name}'"
        
        # At most one "active" phase
        active_count = sum(1 for _, status in self.phases if status == "active")
        if active_count > 1:
            return False, "At most one phase can be 'active' at a time"
        
        return True, None


class ChatResponsePolicyValidator:
    """Validates response structure against 3-section policy"""
    
    def __init__(self):
        """Initialize validator"""
        self.sections: List[ChatSection] = []
        self.plan_spine: Optional[PlanSpineProgress] = None
    
    def validate_full_response(
        self,
        response: str,
        allow_plan_spine: bool = True
    ) -> Tuple[bool, List[str]]:
        """
        Validate complete response structure
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check for verbosity patterns (suppress these)
        for pattern_name, pattern in VerbosityPattern.__members__.items():
            if re.search(pattern.value, response, re.IGNORECASE):
                errors.append(f"VERBOSITY: Found '{pattern_name}' pattern")
        
        # Check section count in response
        section_count = self._count_sections(response)
        if section_count < 3:
            errors.append(f"STRUCTURE: Expected 3 sections, found {section_count}")
        elif section_count > 3:
            errors.append(f"STRUCTURE: Expected 3 sections, found {section_count}")
        
        # Check for "Next Step: PROCEED" in last section
        if "Next Step: PROCEED" not in response:
            errors.append("REQUIRED: Missing 'Next Step: PROCEED' directive")
        
        # Check for options/choices
        if re.search(r"\boption\s+\d+|choose\s+between|which\s+do\s+you", response, re.IGNORECASE):
            errors.append("STRUCTURE: Response contains options/choices (not allowed)")
        
        # Check for plan spine if present
        if allow_plan_spine and "Plan Progress:" in response:
            plan_valid, plan_error = self._validate_plan_spine(response)
            if not plan_valid:
                errors.append(f"PLAN_SPINE: {plan_error}")
        
        return len(errors) == 0, errors
    
    def _count_sections(self, response: str) -> int:
        """Count ## headers in response"""
        return len(re.findall(r"^##\s+", response, re.MULTILINE))
    
    def _validate_plan_spine(self, response: str) -> Tuple[bool, Optional[str]]:
        """Validate plan spine formatting"""
        # Extract plan spine lines
        lines = response.split("\n")
        plan_start = None
        
        for i, line in enumerate(lines):
            if "Plan Progress:" in line:
                plan_start = i
                break
        
        if plan_start is None:
            return True, None
        
        # Check glyph usage only
        valid_glyphs = {
            "[✓]", "[→]", "[!]", "[~]", "[ ]"
        }
        
        for line in lines[plan_start:]:
            if line.strip() == "":
                break
            
            # Check for invalid emoji/banner patterns
            if re.search(r"█|▓|░|[🟢🔴🟡🔵🔻▲▼]", line):
                return False, "Invalid glyph in plan spine (use only [✓][→][!][~][ ])"
            
            # Check line length (max 60 chars for readability)
            if len(line) > 60:
                return False, f"Plan spine line too long ({len(line)} chars, max 60)"
        
        return True, None
    
    def extract_sections(self, response: str) -> List[Tuple[str, str]]:
        """Extract section titles and content from response"""
        sections = []
        lines = response.split("\n")
        current_section = None
        current_content = []
        
        for line in lines:
            match = re.match(r"^##\s+(.+)$", line)
            if match:
                # Save previous section
                if current_section:
                    sections.append((current_section, "\n".join(current_content)))
                    current_content = []
                
                current_section = match.group(1)
            elif current_section and line.strip():
                current_content.append(line)
        
        # Save last section
        if current_section:
            sections.append((current_section, "\n".join(current_content)))
        
        return sections


def suppress_verbosity(response: str) -> str:
    """
    Remove verbose patterns from response
    
    Suppressed patterns:
    - "Let me read...", "searching for...", "Perfect!"
    - Tool call narration ("Read file...", "Using Replace String...")
    - "Due to complexity, here is a comprehensive summary..."
    - Verbose transitions (furthermore, moreover)
    """
    result = response
    
    for pattern_name, pattern in VerbosityPattern.__members__.items():
        # Replace matching patterns with nothing
        result = re.sub(pattern.value, "", result, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    result = re.sub(r"\n\n\n+", "\n\n", result)
    
    return result.strip()


def inject_plan_spine(
    response: str,
    phases: List[Tuple[str, str]],
    section_index: int = 1
) -> str:
    """
    Inject compact ASCII plan spine into section 2 (What's recommended)
    
    Args:
        response: Response text
        phases: List of (phase_name, status) tuples
        section_index: Section index to inject into (0-based, default 1 = section 2)
    
    Returns:
        Response with plan spine injected
    """
    spine = PlanSpineProgress()
    for name, status in phases:
        spine.add_phase(name, status)
    
    is_valid, error = spine.validate()
    if not is_valid:
        # Silently fail - return response unchanged
        return response
    
    ascii_spine = spine.to_ascii()
    if not ascii_spine:
        return response
    
    # Find section 2 and inject as a bullet
    lines = response.split("\n")
    header_count = 0
    section_start = None
    
    for i, line in enumerate(lines):
        if re.match(r"^##\s+", line):
            if header_count == section_index:
                section_start = i
                break
            header_count += 1
    
    if section_start is None:
        # Can't find target section, return unchanged
        return response
    
    # Find first bullet after section
    bullet_start = None
    for i in range(section_start + 1, len(lines)):
        if lines[i].startswith("-"):
            bullet_start = i
            break
    
    if bullet_start is None:
        # No bullets found, append after header
        bullet_start = section_start + 1
    
    # Insert plan spine as indented bullet block
    spine_lines = ascii_spine.split("\n")
    spine_block = ["", "**Plan Progress:**"] + spine_lines + [""]
    
    lines = lines[:bullet_start] + spine_block + lines[bullet_start:]
    
    return "\n".join(lines)


def build_3_section_response(
    what_asked: List[str],
    what_recommended: List[str],
    next_steps: List[str]
) -> str:
    """
    Build a validated 3-section response
    
    Args:
        what_asked: 2-5 bullets for section 1
        what_recommended: 3-7 bullets for section 2
        next_steps: 1-4 bullets for section 3 (must end with "Next Step: PROCEED")
    
    Returns:
        Formatted 3-section response
    
    Raises:
        ValueError: If any section violates constraints
    """
    sections = [
        ChatSection(
            type=SectionType.WHAT_WAS_ASKED,
            title="1) What was asked",
            bullets=what_asked
        ),
        ChatSection(
            type=SectionType.WHATS_RECOMMENDED,
            title="2) What's recommended and why",
            bullets=what_recommended
        ),
        ChatSection(
            type=SectionType.NEXT_STEPS,
            title="3) Next steps",
            bullets=next_steps
        ),
    ]
    
    # Validate all sections
    for section in sections:
        is_valid, error = section.validate()
        if not is_valid:
            raise ValueError(f"Section validation failed: {error}")
    
    # Build response
    response_lines = []
    for section in sections:
        response_lines.append(section.to_markdown())
    
    return "\n".join(response_lines)


# Export public API
__all__ = [
    "ChatResponsePolicyValidator",
    "ChatSection",
    "SectionType",
    "PlanSpineProgress",
    "VerbosityPattern",
    "suppress_verbosity",
    "inject_plan_spine",
    "build_3_section_response",
]
