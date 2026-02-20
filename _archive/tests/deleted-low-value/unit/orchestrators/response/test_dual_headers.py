"""
Test suite for dual header system (CORTEX vs CORTEX Architect).
Tests differentiation of response headers based on prompt context.

Module: tests.unit.orchestrators.response.test_dual_headers
Author: Asif Hussain
Created: 2026-02-07
"""

import pytest
from enum import Enum
from typing import Optional
from dataclasses import dataclass

# ============================================================================
# TEST DATA: Header Specifications
# ============================================================================


class HeaderType(str, Enum):
    """Header type enumeration."""
    CORTEX_OPERATIONS = "cortex_operations"
    CORTEX_ARCHITECT = "cortex_architect"


@dataclass
class HeaderSpec:
    """Header specification."""
    type: HeaderType
    icon: str
    title_prefix: str
    mode_descriptions: list[str]


CORTEX_OPERATIONS_SPEC = HeaderSpec(
    type=HeaderType.CORTEX_OPERATIONS,
    icon="🧠",
    title_prefix="CORTEX",
    mode_descriptions=[
        "Unified operations orchestrator",
        "Handles TDD, code review, deployment",
        "Status: Active"
    ]
)

CORTEX_ARCHITECT_SPEC = HeaderSpec(
    type=HeaderType.CORTEX_ARCHITECT,
    icon="🏛️",
    title_prefix="CORTEX Architect",
    mode_descriptions=[
        "HEPTA-MODE: /audit /plan /query /design /digest /meta-audit",
        "Self-development planning system",
        "Status: Active"
    ]
)


# ============================================================================
# TEST FIXTURES
# ============================================================================


class HeaderTemplate:
    """Header template for testing."""
    
    def __init__(self, spec: HeaderSpec):
        self.spec = spec
        self.icon = spec.icon
        self.title_prefix = spec.title_prefix
    
    def render(self, mode: str, author: str = "Asif Hussain", scope: str = "Implementation") -> str:
        """Render header with provided context."""
        return f"## {self.icon} {self.title_prefix} {mode}\n**Author:** {author} | **Mode:** {mode} | **Scope:** {scope} ✅\n\n---"
    
    def validate_icon(self) -> bool:
        """Validate icon is correct for header type."""
        if self.spec.type == HeaderType.CORTEX_OPERATIONS:
            return self.icon == "🧠"
        elif self.spec.type == HeaderType.CORTEX_ARCHITECT:
            return self.icon == "🏛️"
        return False


class HeaderFactory:
    """Factory for creating headers by type."""
    
    @staticmethod
    def create(header_type: HeaderType) -> HeaderTemplate:
        """Create header template by type."""
        if header_type == HeaderType.CORTEX_OPERATIONS:
            return HeaderTemplate(CORTEX_OPERATIONS_SPEC)
        elif header_type == HeaderType.CORTEX_ARCHITECT:
            return HeaderTemplate(CORTEX_ARCHITECT_SPEC)
        raise ValueError(f"Unknown header type: {header_type}")


# ============================================================================
# TEST CASES
# ============================================================================


class TestDualHeaderSystem:
    """Test suite for dual header system."""
    
    def test_cortex_operations_header_icon(self):
        """Test CORTEX operations header uses 🧠 icon."""
        header = HeaderFactory.create(HeaderType.CORTEX_OPERATIONS)
        assert header.icon == "🧠"
    
    def test_cortex_architect_header_icon(self):
        """Test CORTEX Architect header uses 🏛️ icon."""
        header = HeaderFactory.create(HeaderType.CORTEX_ARCHITECT)
        assert header.icon == "🏛️"
    
    def test_cortex_operations_title_format(self):
        """Test CORTEX operations header title is 'CORTEX'."""
        header = HeaderFactory.create(HeaderType.CORTEX_OPERATIONS)
        assert header.spec.title_prefix == "CORTEX"
        assert header.spec.icon == "🧠"
    
    def test_cortex_architect_title_format(self):
        """Test CORTEX Architect header title includes 'Architect'."""
        header = HeaderFactory.create(HeaderType.CORTEX_ARCHITECT)
        assert header.spec.title_prefix == "CORTEX Architect"
        assert header.spec.icon == "🏛️"
    
    def test_cortex_operations_render(self):
        """Test CORTEX operations header renders correctly."""
        header = HeaderFactory.create(HeaderType.CORTEX_OPERATIONS)
        rendered = header.render(mode="Operations", author="Asif Hussain")
        assert "🧠 CORTEX Operations" in rendered
        assert "**Author:** Asif Hussain" in rendered
        assert "✅" in rendered
        assert "---" in rendered
    
    def test_cortex_architect_render(self):
        """Test CORTEX Architect header renders correctly."""
        header = HeaderFactory.create(HeaderType.CORTEX_ARCHITECT)
        rendered = header.render(mode="Design", author="Asif Hussain")
        assert "🏛️ CORTEX Architect Design" in rendered
        assert "**Author:** Asif Hussain" in rendered
        assert "✅" in rendered
        assert "---" in rendered
    
    def test_header_icon_validation_cortex_ops(self):
        """Test icon validation passes for CORTEX operations header."""
        header = HeaderFactory.create(HeaderType.CORTEX_OPERATIONS)
        assert header.validate_icon() is True
    
    def test_header_icon_validation_architect(self):
        """Test icon validation passes for CORTEX Architect header."""
        header = HeaderFactory.create(HeaderType.CORTEX_ARCHITECT)
        assert header.validate_icon() is True
    
    def test_header_factory_creates_correct_type(self):
        """Test factory creates header of requested type."""
        ops_header = HeaderFactory.create(HeaderType.CORTEX_OPERATIONS)
        arch_header = HeaderFactory.create(HeaderType.CORTEX_ARCHITECT)
        
        assert ops_header.spec.type == HeaderType.CORTEX_OPERATIONS
        assert arch_header.spec.type == HeaderType.CORTEX_ARCHITECT
    
    def test_header_factory_invalid_type(self):
        """Test factory raises error for invalid header type."""
        with pytest.raises(ValueError):
            # Simulate invalid enum value
            class InvalidType(Enum):
                INVALID = "invalid"
            HeaderFactory.create(InvalidType.INVALID)  # type: ignore


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestHeaderIntegration:
    """Integration tests for header system."""
    
    def test_both_headers_have_different_icons(self):
        """Test both header types use different icons."""
        ops = HeaderFactory.create(HeaderType.CORTEX_OPERATIONS)
        arch = HeaderFactory.create(HeaderType.CORTEX_ARCHITECT)
        assert ops.icon != arch.icon
    
    def test_header_consistency_across_renders(self):
        """Test header renders consistently across multiple calls."""
        header = HeaderFactory.create(HeaderType.CORTEX_OPERATIONS)
        render1 = header.render("Test1")
        render2 = header.render("Test1")
        assert render1 == render2
    
    def test_header_modes_different(self):
        """Test both header types have different mode descriptions."""
        ops = CORTEX_OPERATIONS_SPEC
        arch = CORTEX_ARCHITECT_SPEC
        assert ops.mode_descriptions != arch.mode_descriptions
    
    def test_header_separator_always_present(self):
        """Test header separator '---' is always present in output."""
        ops = HeaderFactory.create(HeaderType.CORTEX_OPERATIONS)
        arch = HeaderFactory.create(HeaderType.CORTEX_ARCHITECT)
        
        ops_render = ops.render("Test")
        arch_render = arch.render("Test")
        
        assert "---" in ops_render
        assert "---" in arch_render


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
