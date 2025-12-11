"""
Copilot Instructions Merger - Intelligent Markdown Section Merging

Merges CORTEX enhancements into existing copilot-instructions.md files while
preserving 100% of user customizations.

**Merge Strategy:**
- Parse both files into sections (## headers)
- Classify sections: CORTEX-managed, user-owned, hybrid
- Preserve ALL user content (user wins on conflicts)
- Inject CORTEX sections if missing
- Update CORTEX sections if stale

**Three Scenarios:**
1. **New file:** Generate CORTEX-enhanced template
2. **Generic existing:** Merge CORTEX sections + preserve user content
3. **CORTEX existing:** Update CORTEX sections + preserve user content

Part of CORTEX 3.9.0 - AST-Powered Copilot Instructions Enhancement
Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import re
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


# ========================================
# Data Classes
# ========================================

@dataclass
class MergeResult:
    """Result of merge operation."""
    content: str
    action: str  # "created", "merged", "updated"
    user_sections_preserved: int
    cortex_sections_updated: int
    patterns_injected: int
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for reporting."""
        return {
            "content": self.content,
            "action": self.action,
            "user_sections_preserved": self.user_sections_preserved,
            "cortex_sections_updated": self.cortex_sections_updated,
            "patterns_injected": self.patterns_injected,
            "warnings": self.warnings
        }


# ========================================
# Section Classification
# ========================================

def is_cortex_managed_section(header: str, content: str) -> bool:
    """
    Check if section is CORTEX-managed (safe to update).
    
    A section is CORTEX-managed if:
    - Header starts with 🧠 or 🎯
    - Content contains CORTEX-specific markers
    
    Args:
        header: Section header (e.g., "## 🧠 CORTEX Integration")
        content: Section content
    
    Returns:
        True if CORTEX-managed, False if user-owned
    
    Example:
        >>> is_cortex_managed_section("## 🧠 CORTEX Integration", "Planning System 2.0...")
        True
        >>> is_cortex_managed_section("## Custom Notes", "My notes...")
        False
    """
    # Check header for CORTEX emojis
    if re.match(r'^##\s+[🧠🎯]', header):
        return True
    
    # Check for CORTEX-specific content markers
    cortex_markers = [
        "Planning System 2.0",
        "TDD Mastery",
        "CORTEX Integration",
        "Entry Point",
        "github.com/asifhussain60/CORTEX"
    ]
    
    for marker in cortex_markers:
        if marker in content:
            return True
    
    return False


def classify_section(header: str, content: str) -> str:
    """
    Classify section ownership.
    
    Returns:
        - "cortex_managed": CORTEX owns this section (safe to update)
        - "user_owned": User owns this section (preserve verbatim)
        - "hybrid": Shared section (inject CORTEX as subsection)
    
    Example:
        >>> classify_section("## 🧠 CORTEX Integration", "...")
        'cortex_managed'
        >>> classify_section("## Team Guidelines", "...")
        'user_owned'
        >>> classify_section("## Development Guidelines", "...")
        'hybrid'
    """
    if is_cortex_managed_section(header, content):
        return "cortex_managed"
    
    # Hybrid sections: Common headers that might contain both user + CORTEX content
    hybrid_headers = [
        "Development Guidelines",
        "Architecture",
        "Best Practices",
        "Conventions"
    ]
    
    for hybrid in hybrid_headers:
        if hybrid in header:
            return "hybrid"
    
    return "user_owned"


# ========================================
# Markdown Section Parser
# ========================================

def parse_markdown_sections(content: str) -> Dict[str, str]:
    """
    Parse markdown into sections by ## headers.
    
    Args:
        content: Markdown content
    
    Returns:
        Dictionary mapping header → content
    
    Example:
        >>> content = "## Section 1\\nContent 1\\n## Section 2\\nContent 2"
        >>> parse_markdown_sections(content)
        {'## Section 1': 'Content 1\\n', '## Section 2': 'Content 2'}
    """
    sections = {}
    
    # Split by ## headers
    parts = re.split(r'^(##\s+.+?)$', content, flags=re.MULTILINE)
    
    # First part is preamble (before first ##)
    if parts and not parts[0].startswith('##'):
        preamble = parts[0].strip()
        if preamble:
            sections["__preamble__"] = preamble
        parts = parts[1:]
    
    # Parse header/content pairs
    for i in range(0, len(parts), 2):
        if i + 1 < len(parts):
            header = parts[i].strip()
            content = parts[i + 1].strip()
            sections[header] = content
    
    return sections


def render_markdown(sections: Dict[str, str]) -> str:
    """
    Render sections back to markdown.
    
    Args:
        sections: Dictionary mapping header → content
    
    Returns:
        Rendered markdown string
    
    Example:
        >>> sections = {'## Section 1': 'Content 1', '## Section 2': 'Content 2'}
        >>> render_markdown(sections)
        '## Section 1\\n\\nContent 1\\n\\n## Section 2\\n\\nContent 2'
    """
    lines = []
    
    # Handle preamble first
    if "__preamble__" in sections:
        lines.append(sections["__preamble__"])
        lines.append("")
    
    # Render sections in order (preserve order where possible)
    for header, content in sections.items():
        if header == "__preamble__":
            continue
        
        lines.append(header)
        lines.append("")
        lines.append(content)
        lines.append("")
    
    return "\n".join(lines).strip() + "\n"


# ========================================
# CORTEX Section Generation
# ========================================

def generate_cortex_sections(
    project_name: str,
    language: str,
    framework: str,
    domain_patterns: Optional[object] = None
) -> Dict[str, str]:
    """
    Generate CORTEX-managed sections with detected patterns.
    
    Args:
        project_name: Project name
        language: Primary language
        framework: Framework name
        domain_patterns: DomainPatterns from code_pattern_detector (optional)
    
    Returns:
        Dictionary of CORTEX sections (header → content)
    """
    sections = {}
    
    # Entry Point section
    sections["## 🎯 Entry Point"] = f"""**Primary prompt:** `.github/prompts/CORTEX.prompt.md` - Load this for full CORTEX capabilities

**Project:** {project_name}  
**Language:** {language}  
**Framework:** {framework}

Users interact via natural language. No slash commands needed."""
    
    # CORTEX Integration section
    cortex_section = """This project uses **CORTEX** - an AI assistant enhancement system.

**Available Capabilities:**
- **Planning System 2.0:** Vision API, DoR/DoD enforcement, file-based planning
- **TDD Mastery:** RED→GREEN→REFACTOR automation with auto-debug
- **View Discovery:** Auto-extract UI element IDs for testing
- **Progress Monitoring:** Real-time feedback for long operations
- **Feedback System:** Structured issue reporting with privacy protection

**Quick Commands:**
- `plan [feature]` - Create feature plan with DoR/DoD
- `start tdd` - Begin TDD workflow for current task
- `discover views` - Extract UI element IDs for testing
- `feedback` - Report issues or suggest improvements
- `help` - Show all available commands"""
    
    sections["## 🧠 CORTEX Integration"] = cortex_section
    
    # Development Guidelines (with detected patterns)
    if domain_patterns:
        dev_guidelines = "### 🧠 CORTEX-Detected Patterns\n\n"
        
        # Architecture patterns
        if domain_patterns.architecture:
            dev_guidelines += "**Architecture:**\n"
            for pattern in domain_patterns.architecture:
                dev_guidelines += f"- {pattern}\n"
            dev_guidelines += "\n"
        
        # API style
        if domain_patterns.api_style:
            dev_guidelines += f"**API Style:** {domain_patterns.api_style}\n\n"
        
        # Authentication
        if domain_patterns.auth_method:
            dev_guidelines += f"**Authentication:** {domain_patterns.auth_method}\n\n"
        
        # Data access
        if domain_patterns.data_access:
            dev_guidelines += f"**Data Access:** {domain_patterns.data_access}\n\n"
        
        # Testing
        if domain_patterns.testing_patterns:
            dev_guidelines += "**Testing:**\n"
            for pattern in domain_patterns.testing_patterns:
                dev_guidelines += f"- {pattern}\n"
            dev_guidelines += "\n"
        
        sections["## Development Guidelines"] = dev_guidelines.strip()
    
    return sections


# ========================================
# Merge Engine
# ========================================

def merge_with_existing(
    existing_path: Path,
    project_name: str,
    language: str,
    framework: str,
    domain_patterns: Optional[object] = None
) -> MergeResult:
    """
    Merge CORTEX enhancements with existing copilot-instructions.md.
    
    Args:
        existing_path: Path to existing copilot-instructions.md
        project_name: Project name
        language: Primary language
        framework: Framework name
        domain_patterns: Detected patterns (optional)
    
    Returns:
        MergeResult with merged content and metadata
    
    Example:
        >>> result = merge_with_existing(
        ...     Path(".github/copilot-instructions.md"),
        ...     "my-project",
        ...     "Python",
        ...     "FastAPI",
        ...     patterns
        ... )
        >>> result.action
        'merged'
    """
    # Parse existing file
    existing_content = existing_path.read_text(encoding='utf-8')
    existing_sections = parse_markdown_sections(existing_content)
    
    # Generate CORTEX sections
    cortex_sections = generate_cortex_sections(
        project_name,
        language,
        framework,
        domain_patterns
    )
    
    # Merge sections
    merged = {}
    user_preserved = 0
    cortex_updated = 0
    warnings = []
    
    # Step 1: Preserve all existing sections
    for header, content in existing_sections.items():
        classification = classify_section(header, content)
        
        if classification == "user_owned":
            # Preserve user section verbatim
            merged[header] = content
            user_preserved += 1
            logger.debug(f"Preserved user section: {header}")
        
        elif classification == "cortex_managed":
            # Check if we have updated CORTEX content
            if header in cortex_sections:
                merged[header] = cortex_sections[header]
                cortex_updated += 1
                logger.debug(f"Updated CORTEX section: {header}")
            else:
                # CORTEX section but we don't have update (keep existing)
                merged[header] = content
                warnings.append(f"Kept existing CORTEX section: {header}")
        
        elif classification == "hybrid":
            # Hybrid: Check if CORTEX patterns already present
            if "🧠 CORTEX-Detected Patterns" in content:
                # Already has CORTEX subsection, update it
                if header in cortex_sections:
                    # Replace CORTEX subsection while preserving user content
                    merged[header] = _merge_hybrid_section(content, cortex_sections[header])
                    cortex_updated += 1
                else:
                    merged[header] = content
            else:
                # No CORTEX subsection yet, inject it
                if header in cortex_sections:
                    merged[header] = content + "\n\n" + cortex_sections[header]
                    cortex_updated += 1
                else:
                    merged[header] = content
                    user_preserved += 1
    
    # Step 2: Add missing CORTEX sections
    for header, content in cortex_sections.items():
        if header not in merged:
            merged[header] = content
            cortex_updated += 1
            logger.debug(f"Added new CORTEX section: {header}")
    
    # Render final content
    final_content = render_markdown(merged)
    
    # Determine action
    is_cortex_file = any("CORTEX Integration" in s for s in existing_sections.values())
    action = "updated" if is_cortex_file else "merged"
    
    return MergeResult(
        content=final_content,
        action=action,
        user_sections_preserved=user_preserved,
        cortex_sections_updated=cortex_updated,
        patterns_injected=len(domain_patterns.architecture) if domain_patterns else 0,
        warnings=warnings
    )


def _merge_hybrid_section(existing_content: str, cortex_content: str) -> str:
    """
    Merge hybrid section: Replace CORTEX subsection while preserving user content.
    
    Args:
        existing_content: Existing section content with CORTEX subsection
        cortex_content: New CORTEX subsection content
    
    Returns:
        Merged content with updated CORTEX subsection
    """
    # Find CORTEX subsection marker
    pattern = r'###\s+🧠\s+CORTEX-Detected Patterns.*?(?=\n###|\Z)'
    
    # Check if CORTEX subsection exists
    if re.search(pattern, existing_content, re.DOTALL):
        # Replace CORTEX subsection
        merged = re.sub(pattern, cortex_content, existing_content, flags=re.DOTALL)
        return merged
    else:
        # No CORTEX subsection found, append it
        return existing_content + "\n\n" + cortex_content


# ========================================
# Template Generation (for new files)
# ========================================

def generate_new_instructions(
    project_name: str,
    language: str,
    framework: str,
    build_system: str,
    test_framework: str,
    domain_patterns: Optional[object] = None
) -> str:
    """
    Generate new copilot-instructions.md from scratch.
    
    Args:
        project_name: Project name
        language: Primary language
        framework: Framework name
        build_system: Build system
        test_framework: Test framework
        domain_patterns: Detected patterns (optional)
    
    Returns:
        Complete markdown content
    """
    sections = {}
    
    # Preamble
    sections["__preamble__"] = f"""# GitHub Copilot Instructions for {project_name}

**Auto-generated by CORTEX** | **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Learning Progress:** Starting... (CORTEX will learn as you work)"""
    
    # Entry Point
    sections["## 🎯 Entry Point"] = f"""**Primary prompt:** `.github/prompts/CORTEX.prompt.md` - Load this for full CORTEX capabilities

**Project:** {project_name}  
**Language:** {language}  
**Framework:** {framework}  
**Build System:** {build_system}  
**Test Framework:** {test_framework}

Users interact via natural language. No slash commands needed."""
    
    # CORTEX Integration
    sections["## 🧠 CORTEX Integration"] = """This project uses **CORTEX** - an AI assistant enhancement system.

**Available Capabilities:**
- **Planning System 2.0:** Vision API, DoR/DoD enforcement, file-based planning
- **TDD Mastery:** RED→GREEN→REFACTOR automation with auto-debug
- **View Discovery:** Auto-extract UI element IDs for testing
- **Progress Monitoring:** Real-time feedback for long operations
- **Feedback System:** Structured issue reporting with privacy protection

**Quick Commands:**
- `plan [feature]` - Create feature plan with DoR/DoD
- `start tdd` - Begin TDD workflow for current task
- `discover views` - Extract UI element IDs for testing
- `feedback` - Report issues or suggest improvements
- `help` - Show all available commands"""
    
    # Development Guidelines (with detected patterns)
    if domain_patterns and domain_patterns.pattern_count() > 0:
        dev_guidelines = f"""### Code Style
- Follow {language} best practices and idioms
- Use type hints/annotations where supported
- Write self-documenting code with clear variable names

### 🧠 CORTEX-Detected Patterns

"""
        
        # Architecture patterns
        if domain_patterns.architecture:
            dev_guidelines += "**Architecture:**\n"
            for pattern in domain_patterns.architecture:
                dev_guidelines += f"- {pattern}\n"
            dev_guidelines += "\n"
        
        # API style
        if domain_patterns.api_style:
            dev_guidelines += f"**API Style:** {domain_patterns.api_style}\n\n"
        
        # Authentication
        if domain_patterns.auth_method:
            dev_guidelines += f"**Authentication:** {domain_patterns.auth_method}\n\n"
        
        # Data access
        if domain_patterns.data_access:
            dev_guidelines += f"**Data Access:** {domain_patterns.data_access}\n\n"
        
        # Testing
        if domain_patterns.testing_patterns:
            dev_guidelines += "**Testing:**\n"
            for pattern in domain_patterns.testing_patterns:
                dev_guidelines += f"- {pattern}\n"
            dev_guidelines += "\n"
        
        # Framework specifics
        if domain_patterns.framework_specifics:
            dev_guidelines += "**Framework-Specific:**\n"
            for key, value in domain_patterns.framework_specifics.items():
                dev_guidelines += f"- {value}\n"
        
        sections["## Development Guidelines"] = dev_guidelines.strip()
    else:
        # No patterns detected, use generic guidelines
        sections["## Development Guidelines"] = f"""### Code Style
- Follow {language} best practices and idioms
- Use type hints/annotations where supported
- Write self-documenting code with clear variable names

### Testing
- Test framework: {test_framework}
- Write tests FIRST (TDD workflow)
- Aim for 80%+ code coverage

### Documentation
- Document public APIs and complex logic
- Keep README.md updated
- Add inline comments for non-obvious code"""
    
    # Footer
    sections["__footer__"] = f"""---

*Generated by CORTEX Master Setup v3.9.0*  
*Last updated: {datetime.now().strftime("%Y-%m-%d")}*"""
    
    # Render
    return render_markdown(sections)


# ========================================
# Self-Test
# ========================================

if __name__ == "__main__":
    print("🧪 Copilot Instructions Merger - Self Test")
    print("=" * 70)
    
    # Test 1: Section parser
    print("\n1️⃣  Testing section parser...")
    test_md = """# Title

Preamble content

## Section 1

Content 1

## Section 2

Content 2"""
    
    sections = parse_markdown_sections(test_md)
    print(f"   Parsed {len(sections)} sections")
    assert "__preamble__" in sections
    assert "## Section 1" in sections
    print("   ✅ Parser works")
    
    # Test 2: Section classification
    print("\n2️⃣  Testing section classification...")
    assert classify_section("## 🧠 CORTEX Integration", "Planning...") == "cortex_managed"
    assert classify_section("## Custom Notes", "My notes") == "user_owned"
    assert classify_section("## Development Guidelines", "Code style") == "hybrid"
    print("   ✅ Classification works")
    
    # Test 3: Markdown rendering
    print("\n3️⃣  Testing markdown rendering...")
    rendered = render_markdown(sections)
    assert "## Section 1" in rendered
    assert "## Section 2" in rendered
    print("   ✅ Rendering works")
    
    # Test 4: CORTEX section generation
    print("\n4️⃣  Testing CORTEX section generation...")
    cortex_sections = generate_cortex_sections("test-project", "Python", "FastAPI")
    assert "## 🎯 Entry Point" in cortex_sections
    assert "## 🧠 CORTEX Integration" in cortex_sections
    print(f"   Generated {len(cortex_sections)} CORTEX sections")
    print("   ✅ Generation works")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print(f"📊 Module size: {len(open(__file__, encoding='utf-8').readlines())} lines")
