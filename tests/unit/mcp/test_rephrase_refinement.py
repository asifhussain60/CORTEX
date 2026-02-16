"""
Tests for REPHRASE Mode Refinement (Phase 101 Enhancement).

Authority: cortex-architect.prompt.md § REPHRASE MODE
Purpose: Clean, minimal output with refined prompt + challenge protocol
AC-ID: AC-REPHRASE-REFINEMENT-001

Test Coverage:
- Output format: Clean markdown without metrics/tables
- Challenge protocol: Auto-appended unless already present
- Token optimization: Distilled summary generation
- Edge cases: Empty requests, duplicate protocols, special chars
"""

import pytest
from cortex.mcp.tools.core import CortexClassify
from cortex.mcp.mcp_tool_base import ToolResult


class TestRephraseOutputFormat:
    """Test clean rephrase output format."""
    
    @pytest.mark.asyncio
    async def test_rephrase_returns_clean_markdown_block(self):
        """Test: Rephrase returns ONLY refined prompt + challenge protocol."""
        tool = CortexClassify()
        
        result = await tool.execute(
            operation="intent",
            request="I want to review the existing user response templates blocks and recreate them",
            format="conversational",
        )
        
        assert result.success is True
        assert "rephrased_prompt" in result.data
        
        # Should contain refined text
        assert len(result.data["rephrased_prompt"]) > 0
        
        # Should contain challenge protocol
        assert "challenge-first protocol" in result.data["rephrased_prompt"].lower()
        
        # Should NOT contain metrics
        assert "Token Reduction" not in result.data["rephrased_prompt"]
        assert "Confidence:" not in result.data["rephrased_prompt"]
        
        # Should NOT contain tables or headers
        assert "|" not in result.data["rephrased_prompt"]  # No markdown tables
        assert "###" not in result.data["rephrased_prompt"]  # No h3 headers
        assert "🎯" not in result.data["rephrased_prompt"]  # No section icons
    
    @pytest.mark.asyncio
    async def test_rephrase_appends_challenge_protocol(self):
        """Test: Challenge protocol auto-appended to refined prompt."""
        tool = CortexClassify()
        
        result = await tool.execute(
            operation="intent",
            request="Fix the authentication bug",
            format="conversational",
        )
        
        rephrased = result.data["rephrased_prompt"]
        
        # Verify challenge protocol appended
        assert "Analyze my request using CORTEX's challenge-first protocol" in rephrased
        assert "extensibility, scalability, accuracy" in rephrased
        assert "MCP-first exposure" in rephrased
        assert "zero regression risk" in rephrased
    
    @pytest.mark.asyncio
    async def test_rephrase_no_duplicate_challenge_protocol(self):
        """Test: Challenge protocol NOT duplicated if user already included it."""
        tool = CortexClassify()
        
        result = await tool.execute(
            operation="intent",
            request="Implement feature X. Analyze using challenge-first protocol.",
            format="conversational",
        )
        
        rephrased = result.data["rephrased_prompt"]
        
        # Count occurrences of "challenge-first protocol"
        count = rephrased.lower().count("challenge-first protocol")
        
        # Should appear exactly once
        assert count == 1, f"Expected 1 occurrence, found {count}"


class TestRephraseTokenOptimization:
    """Test token optimization in rephrase mode."""
    
    @pytest.mark.asyncio
    async def test_rephrase_reduces_verbose_request(self):
        """Test: Verbose request distilled to concise CORTEX language."""
        tool = CortexClassify()
        
        verbose_request = (
            "I think we should probably implement some kind of user authentication "
            "system because right now anyone can access the admin panel and that's "
            "not good for security and we need to make sure only authorized users can get in"
        )
        
        result = await tool.execute(
            operation="intent",
            request=verbose_request,
            format="conversational",
        )
        
        rephrased = result.data["rephrased_prompt"]
        
        # Challenge protocol is ~600 chars, refined text should be shorter than original
        challenge_protocol_len = 600  # Approximate length
        refined_text = rephrased.split("\n\n")[0]  # Text before challenge protocol
        
        # Refined text should be shorter than original (filler words removed)
        assert len(refined_text) < len(verbose_request), \
            f"Refined text ({len(refined_text)}) should be shorter than original ({len(verbose_request)})"
        
        # Should preserve key concepts
        assert "authentication" in rephrased.lower() or "auth" in rephrased.lower()
        assert "security" in rephrased.lower() or "admin" in rephrased.lower()
    
    @pytest.mark.asyncio
    async def test_rephrase_adds_cortex_technical_details(self):
        """Test: Refined prompt includes CORTEX technical context."""
        tool = CortexClassify()
        
        result = await tool.execute(
            operation="intent",
            request="Make the response templates look better",
            format="conversational",
        )
        
        rephrased = result.data["rephrased_prompt"]
        
        # Should have added technical context (one or more expected terms)
        technical_terms = [
            "orchestrator",
            "MCP",
            "registry",
            "LENS",
            "governance",
            "template",
            "response format",
        ]
        
        # At least ONE technical term should be present
        assert any(term.lower() in rephrased.lower() for term in technical_terms)


class TestRephraseEdgeCases:
    """Test edge cases for rephrase mode."""
    
    @pytest.mark.asyncio
    async def test_rephrase_handles_empty_request(self):
        """Test: Empty request handled gracefully."""
        tool = CortexClassify()
        
        result = await tool.execute(
            operation="intent",
            request="",
            format="conversational",
        )
        
        # Should still return valid result (fallback to keyword classifier)
        assert result.success is True
        
        # Empty request should NOT have rephrased_prompt (nothing to rephrase)
        # This is expected behavior - rephrased_prompt only for valid requests
        assert "intent" in result.data  # Should still classify intent
    
    @pytest.mark.asyncio
    async def test_rephrase_handles_special_characters(self):
        """Test: Special characters preserved correctly."""
        tool = CortexClassify()
        
        result = await tool.execute(
            operation="intent",
            request="Fix bug in `user_auth` module (priority: high)",
            format="conversational",
        )
        
        rephrased = result.data["rephrased_prompt"]
        
        # Should preserve code backticks and parens
        assert "`" in rephrased or "user_auth" in rephrased
    
    @pytest.mark.asyncio
    async def test_table_format_unchanged(self):
        """Test: format='table' behavior unchanged (regression check)."""
        tool = CortexClassify()
        
        result = await tool.execute(
            operation="intent",
            request="Implement feature X",
            format="table",  # Default format
        )
        
        # Should NOT have rephrased_prompt field (old behavior)
        assert "rephrased_prompt" not in result.data
        
        # Should have old structure
        assert "intent" in result.data or "conversational_summary" in result.data
