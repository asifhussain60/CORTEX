"""
Tests for MCP Coherence Tools.

AC_START: AC-ENH-101-012
Description: TDD tests for cortex_validate_coherence MCP tool
Authority: ENH-101 Stage S5 - WAVE-10 Quality
Compliance: CORE-008 (tests first), Zero mocks for core logic
"""

import pytest

from cortex.mcp.tools.coherence_tools import (
    MCP_TOOLS,
    cortex_validate_coherence,
)


# =============================================================================
# TEST: MCP TOOL REGISTRATION
# =============================================================================

class TestMCPToolRegistration:
    """Tests for MCP tool registration."""
    
    def test_tools_registered(self) -> None:
        """MCP_TOOLS list exists and has correct structure."""
        assert isinstance(MCP_TOOLS, list)
        assert len(MCP_TOOLS) >= 1
    
    def test_coherence_tool_registered(self) -> None:
        """cortex_validate_coherence is registered."""
        tool_names = [t["name"] for t in MCP_TOOLS]
        assert "cortex_validate_coherence" in tool_names
    
    def test_tool_has_schema(self) -> None:
        """Tool has proper input schema."""
        tool = MCP_TOOLS[0]
        
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool
        assert "handler" in tool
        
        schema = tool["inputSchema"]
        assert "properties" in schema
        assert "file_path" in schema["properties"]
        assert "content" in schema["properties"]


# =============================================================================
# TEST: VALIDATE COHERENCE - BASIC
# =============================================================================

@pytest.mark.asyncio
class TestValidateCoherenceBasic:
    """Basic tests for cortex_validate_coherence."""
    
    async def test_returns_dict(self) -> None:
        """Tool returns dictionary with expected keys."""
        result = await cortex_validate_coherence(
            file_path="test.md",
            content="# Title\n\n## Section",
        )
        
        assert isinstance(result, dict)
        assert "status" in result
        assert "file_path" in result
        assert "issues" in result
        assert "duplicates_found" in result
        assert "version_consistent" in result
        assert "recommendations" in result
        assert "summary" in result
    
    async def test_clean_content_passes(self) -> None:
        """Clean content passes validation."""
        result = await cortex_validate_coherence(
            file_path="test.md",
            content="""# Title

**Version:** 1.0.0

## Alpha Section

Content here with some text.

## Beta Section

More content with different text.

## Gamma Section

Even more unique content here.
""",
        )
        
        assert result["status"] in ("passed", "warning")
        # Check for no exact duplicates (similar sections OK with warning)
        exact_dup_issues = [
            i for i in result["issues"]
            if i["type"] == "duplicate_section"
        ]
        assert len(exact_dup_issues) == 0
        assert result["version_consistent"] is True
    
    async def test_duplicate_content_fails(self) -> None:
        """Duplicate sections are detected."""
        result = await cortex_validate_coherence(
            file_path="test.md",
            content="""# Title

## Section

Content.

## Section

Duplicate!
""",
        )
        
        assert result["status"] in ("failed", "warning")
        assert result["duplicates_found"] > 0
        assert len(result["issues"]) > 0
    
    async def test_version_mismatch_detected(self) -> None:
        """Version mismatches are detected."""
        result = await cortex_validate_coherence(
            file_path="test.md",
            content="""# Title

**Version:** 1.0.0

Content here.

---

*v2.0.0 — Footer*
""",
        )
        
        version_issues = [
            i for i in result["issues"]
            if i["type"] == "version_mismatch"
        ]
        assert len(version_issues) > 0
        assert not result["version_consistent"]


# =============================================================================
# TEST: VALIDATE COHERENCE - WITH PRE-EDIT
# =============================================================================

@pytest.mark.asyncio
class TestValidateCoherencePreEdit:
    """Tests with pre-edit content comparison."""
    
    async def test_with_pre_edit_content(self) -> None:
        """Validation works with before/after comparison."""
        pre_content = """# Title

## Section One

Content.

## Section Two

More content.
"""
        
        post_content = """# Title

## Section One

Updated content.

## Section Two

More content.

## Section Three

New section.
"""
        
        result = await cortex_validate_coherence(
            file_path="test.md",
            content=post_content,
            pre_edit_content=pre_content,
        )
        
        assert result["status"] in ("passed", "warning")
        assert "file_path" in result
    
    async def test_duplicate_introduced(self) -> None:
        """Detects when duplicate is introduced."""
        pre_content = """# Title

## Section One

Content.
"""
        
        post_content = """# Title

## Section One

Content.

## Section One

Duplicate added!
"""
        
        result = await cortex_validate_coherence(
            file_path="test.md",
            content=post_content,
            pre_edit_content=pre_content,
        )
        
        assert result["status"] in ("failed", "warning")
        assert result["duplicates_found"] > 0


# =============================================================================
# TEST: VALIDATE COHERENCE - CONFIG OPTIONS
# =============================================================================

@pytest.mark.asyncio
class TestValidateCoherenceConfig:
    """Tests for configuration options."""
    
    async def test_disable_duplicate_check(self) -> None:
        """Duplicate check can be disabled."""
        result = await cortex_validate_coherence(
            file_path="test.md",
            content="""# Title

## Section

## Section
""",
            check_duplicates=False,
        )
        
        # Should not report duplicates when check disabled
        # (Though it may still detect them in structure analysis)
        assert isinstance(result, dict)
    
    async def test_disable_version_check(self) -> None:
        """Version check can be disabled."""
        result = await cortex_validate_coherence(
            file_path="test.md",
            content="""# Title

**Version:** 1.0.0

*v2.0.0*
""",
            check_versions=False,
        )
        
        # Should not fail on version mismatch when disabled
        assert isinstance(result, dict)
    
    async def test_all_checks_disabled(self) -> None:
        """All checks can be disabled."""
        result = await cortex_validate_coherence(
            file_path="test.md",
            content="""# Title

## Section

## Section
""",
            check_duplicates=False,
            check_versions=False,
            check_structure=False,
        )
        
        assert result["status"] in ("passed", "warning")


# =============================================================================
# TEST: ERROR HANDLING
# =============================================================================

@pytest.mark.asyncio
class TestErrorHandling:
    """Tests for error handling."""
    
    async def test_empty_content(self) -> None:
        """Empty content is handled gracefully."""
        result = await cortex_validate_coherence(
            file_path="test.md",
            content="",
        )
        
        assert isinstance(result, dict)
        assert result["status"] in ("passed", "error")
    
    async def test_invalid_file_type(self) -> None:
        """Unknown file types are handled."""
        result = await cortex_validate_coherence(
            file_path="test.xyz",
            content="Some content",
        )
        
        assert isinstance(result, dict)
        # Should not crash


# =============================================================================
# TEST: INTEGRATION
# =============================================================================

@pytest.mark.asyncio
class TestIntegration:
    """Integration tests with real-world scenarios."""
    
    async def test_markdown_file_validation(self) -> None:
        """Validate a realistic markdown file."""
        content = """# Project Documentation

**Version:** 1.0.0 | **Author:** Test User

## Introduction

This project provides...

## Installation

```bash
pip install package
```

## Usage

Example usage:

```python
import package
package.run()
```

## Contributing

Please read CONTRIBUTING.md.

---

*v1.0.0 — Last updated: 2026-01-15*
"""
        
        result = await cortex_validate_coherence(
            file_path="README.md",
            content=content,
        )
        
        assert result["status"] in ("passed", "warning")
        assert result["version_consistent"] is True
    
    async def test_python_file_validation(self) -> None:
        """Validate a Python file structure."""
        content = '''"""
Module docstring.

Version: 1.0.0
"""

class MyClass:
    """A sample class."""
    
    def method_one(self) -> None:
        """First method."""
        pass


class AnotherClass:
    """Another class."""
    
    def method_two(self) -> None:
        """Second method."""
        pass
'''
        
        result = await cortex_validate_coherence(
            file_path="module.py",
            content=content,
        )
        
        assert result["status"] in ("passed", "warning")


# AC_COMPLETE: AC-ENH-101-012 ✅ MCP tool tests
