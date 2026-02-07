"""
AC_START: AC-PHASE37.5-001
Description: Phase 37 Stage 5 - Documentation validation tests

Tests verify that:
1. User-facing documentation exists and is comprehensive
2. Example workflows demonstrate all persona features
3. Prompt templates contain {{PERSONA_INJECTION_POINT}}
4. Integration examples show real-world usage
5. API documentation covers all MCP tools (when implemented)
6. README includes persona system overview
"""

import pytest
from pathlib import Path


class TestPersonaDocumentation:
    """Test suite for Phase 37 Stage 5 documentation requirements."""
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_persona_readme_exists(self):
        """Should have comprehensive README for persona system."""
        readme_path = Path("cortex/orchestrators/core/README-PERSONAS.md")
        assert readme_path.exists(), "README-PERSONAS.md must exist"
        
        content = readme_path.read_text()
        
        # Must include key sections
        assert "# Role-Adaptive Persona System" in content
        assert "## Overview" in content
        assert "## Quick Start" in content
        assert "## Available Personas" in content
        assert "## Commands" in content
        assert "## Examples" in content
        
        # Must document all 6 personas
        assert "business_leader" in content.lower()
        assert "product_owner" in content.lower()
        assert "scrum_master" in content.lower()
        assert "tech_lead" in content.lower()
        assert "engineer" in content.lower()
        
        # Should be substantial (at least 1KB)
        assert len(content) > 1000, "README should be comprehensive"
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_persona_examples_exist(self):
        """Should have example workflows demonstrating persona features."""
        examples_path = Path("cortex/orchestrators/core/PERSONA-EXAMPLES.md")
        assert examples_path.exists(), "PERSONA-EXAMPLES.md must exist"
        
        content = examples_path.read_text()
        
        # Example categories
        assert "Basic Persona Switching" in content
        assert "Depth Override" in content
        assert "Inference Workflow" in content
        assert "Session Persistence" in content
        
        # Should include code examples
        assert "/persona" in content
        assert "/detail" in content
        assert "PersonaOrchestrator" in content
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_prompt_templates_updated(self):
        """Should update .github/prompts/ with persona injection."""
        cortex_prompt = Path(".github/prompts/CORTEX.prompt.md")
        assert cortex_prompt.exists()
        
        content = cortex_prompt.read_text()
        
        # Should mention persona system
        assert "{{PERSONA_INJECTION_POINT}}" in content or "persona" in content.lower()
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_personas_yaml_documented(self):
        """Should document personas.yaml schema."""
        personas_yaml = Path("cortex/config/personas.yaml")
        assert personas_yaml.exists()
        
        content = personas_yaml.read_text()
        
        # Should have inline documentation
        assert "#" in content  # Has comments
        
        # Should document structure
        personas_readme = Path("cortex/orchestrators/core/README-PERSONAS.md")
        readme_content = personas_readme.read_text()
        assert "personas.yaml" in readme_content
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_api_documentation_complete(self):
        """Should document PersonaOrchestrator public API."""
        api_doc = Path("cortex/orchestrators/core/API-REFERENCE.md")
        assert api_doc.exists(), "API-REFERENCE.md must exist"
        
        content = api_doc.read_text()
        
        # All public methods documented
        assert "process_request" in content
        assert "style_response" in content
        assert "inject_persona_context" in content
        assert "execute_command" in content
        assert "get_current_state" in content
        assert "consume_turn" in content
        assert "serialize_state" in content
        assert "restore_state" in content
        
        # Should include examples
        assert "Example" in content or "```python" in content
    
    # @pytest.mark.skip(reason="GREEN phase")
    def test_integration_guide_exists(self):
        """Should have integration guide for using PersonaOrchestrator."""
        guide_path = Path("cortex/orchestrators/core/INTEGRATION-GUIDE.md")
        assert guide_path.exists(), "INTEGRATION-GUIDE.md must exist"
        
        content = guide_path.read_text()
        
        # Integration topics
        assert "Getting Started" in content
        assert "Basic Usage" in content
        assert "Advanced Features" in content
        assert "Error Handling" in content
        
        # Code examples
        assert "```python" in content
        assert "PersonaOrchestrator()" in content


# AC_COMPLETE: AC-PHASE37.5-001 ✅ 0/6 tests (skipped, RED phase)
