"""
Test Suite: Enterprise Documentation Enhancement
Tests the new documentation generation capabilities added in Phase 3.0
- CORTEX vs COPILOT comparison
- Architecture documentation
- Technical documentation
- Getting Started guide
- MkDocs configuration updates
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cortex_brain.admin.scripts.documentation.enterprise_documentation_orchestrator import (
    EnterpriseDocumentationOrchestrator
)


@pytest.fixture
def orchestrator():
    """Create orchestrator instance for testing"""
    workspace_path = Path(__file__).parent.parent
    return EnterpriseDocumentationOrchestrator(workspace_path)


@pytest.fixture
def mock_features():
    """Mock feature discovery data"""
    return {
        "features": [
            {
                "name": "Memory System",
                "description": "4-tier memory architecture",
                "tier": 1
            },
            {
                "name": "Agent Coordination",
                "description": "10-agent split-brain system",
                "tier": 2
            }
        ],
        "total_features": 2
    }


class TestCortexVsCopilot:
    """Test CORTEX vs COPILOT comparison generation"""
    
    def test_method_renamed(self, orchestrator):
        """Verify method was renamed from _generate_executive_summary"""
        assert hasattr(orchestrator, '_generate_cortex_vs_copilot')
        assert hasattr(orchestrator, '_write_cortex_vs_copilot_comparison')
    
    def test_comparison_content_generation(self, orchestrator, mock_features):
        """Test comparison content includes all required sections"""
        content = orchestrator._write_cortex_vs_copilot_comparison(mock_features)
        
        # Check YAML frontmatter
        assert "---" in content
        assert "title: CORTEX vs GitHub Copilot" in content
        
        # Check key sections exist
        assert "## Why Choose CORTEX?" in content
        assert "## Side-by-Side Comparison" in content
        assert "## 10 Ways CORTEX Beats Standalone Copilot" in content
        assert "## Real Cost Analysis" in content
        assert "## Use Cases" in content
        
        # Check comparison table
        assert "| Feature | GitHub Copilot | CORTEX |" in content
        assert "Memory" in content
        assert "4-tier persistent memory" in content
    
    def test_file_generation(self, orchestrator, mock_features):
        """Test file is created at correct path"""
        result = orchestrator._generate_cortex_vs_copilot(mock_features, dry_run=False)
        
        assert result["document_type"] == "cortex_vs_copilot"
        assert "CORTEX-VS-COPILOT.md" in result["file"]
        assert result["validation"]["file_created"] is True
        
        # Verify file exists
        file_path = Path(result["file"])
        assert file_path.exists()
        
        # Verify file size reasonable (should be >10KB for comprehensive comparison)
        assert file_path.stat().st_size > 10000


class TestArchitectureDoc:
    """Test Architecture documentation generation"""
    
    def test_method_exists(self, orchestrator):
        """Verify architecture generation method exists"""
        assert hasattr(orchestrator, '_generate_architecture_doc')
        assert hasattr(orchestrator, '_write_architecture_documentation')
    
    def test_architecture_content(self, orchestrator, mock_features):
        """Test architecture content includes all tiers and agents"""
        content = orchestrator._write_architecture_documentation(mock_features)
        
        # Check YAML frontmatter
        assert "title: CORTEX Architecture" in content
        
        # Check tier documentation
        assert "Tier 0: Brain Protection (SKULL)" in content
        assert "Tier 1: Working Memory" in content
        assert "Tier 2: Knowledge Graph" in content
        assert "Tier 3: Long-term Storage" in content
        
        # Check agent system
        assert "Left Hemisphere (5 Analytical Agents)" in content
        assert "Right Hemisphere (5 Creative Agents)" in content
        assert "Corpus Callosum" in content
        
        # Check for memory persistence
        assert "conversation-history.db" in content
        assert "knowledge-graph.yaml" in content
    
    def test_file_generation(self, orchestrator, mock_features):
        """Test architecture file is created"""
        result = orchestrator._generate_architecture_doc(mock_features, dry_run=False)
        
        assert result["document_type"] == "architecture"
        assert "ARCHITECTURE.md" in result["file"]
        assert result["validation"]["file_created"] is True
        
        # Verify file size (should be >15KB for comprehensive architecture)
        file_path = Path(result["file"])
        assert file_path.exists()
        assert file_path.stat().st_size > 15000


class TestTechnicalDocs:
    """Test Technical Documentation generation"""
    
    def test_method_exists(self, orchestrator):
        """Verify technical docs generation method exists"""
        assert hasattr(orchestrator, '_generate_technical_docs')
        assert hasattr(orchestrator, '_write_technical_documentation')
    
    def test_technical_content(self, orchestrator, mock_features):
        """Test technical documentation includes API reference"""
        content = orchestrator._write_technical_documentation(mock_features)
        
        # Check YAML frontmatter
        assert "title: CORTEX Technical Documentation" in content
        
        # Check API reference sections
        assert "## API Reference" in content
        assert "## Module Definitions" in content
        assert "## Configuration Reference" in content
        
        # Check for code examples
        assert "```python" in content or "```json" in content
    
    def test_file_generation(self, orchestrator, mock_features):
        """Test technical docs file is created"""
        result = orchestrator._generate_technical_docs(mock_features, dry_run=False)
        
        assert result["document_type"] == "technical_docs"
        assert "TECHNICAL-DOCUMENTATION.md" in result["file"]
        assert result["validation"]["file_created"] is True
        
        file_path = Path(result["file"])
        assert file_path.exists()


class TestGettingStarted:
    """Test Getting Started guide generation"""
    
    def test_method_exists(self, orchestrator):
        """Verify getting started generation method exists"""
        assert hasattr(orchestrator, '_generate_getting_started')
        assert hasattr(orchestrator, '_write_getting_started_guide')
    
    def test_getting_started_content(self, orchestrator, mock_features):
        """Test getting started content includes setup and onboarding"""
        content = orchestrator._write_getting_started_guide(mock_features)
        
        # Check YAML frontmatter
        assert "title: Getting Started with CORTEX" in content
        
        # Check required sections
        assert "## 🚀 Setup" in content
        assert "## 📚 Onboarding" in content
        assert "## 🎮 Demo" in content
        assert "## ⚡ First Steps" in content
        assert "## 🆘 Troubleshooting" in content
        
        # Check setup instructions
        assert "Prerequisites" in content
        assert "Installation" in content
        assert "python scripts/setup_cortex.py" in content
        
        # Check onboarding workflow
        assert "Step 1:" in content
        assert "GitHub Copilot" in content
    
    def test_file_generation(self, orchestrator, mock_features):
        """Test getting started file is created"""
        result = orchestrator._generate_getting_started(mock_features, dry_run=False)
        
        assert result["document_type"] == "getting_started"
        assert "GETTING-STARTED.md" in result["file"]
        assert result["validation"]["file_created"] is True
        
        # Verify file size (should be >8KB for comprehensive guide)
        file_path = Path(result["file"])
        assert file_path.exists()
        assert file_path.stat().st_size > 8000


class TestMkDocsIntegration:
    """Test MkDocs configuration updates"""
    
    def test_mkdocs_nav_updated(self, orchestrator):
        """Test MkDocs navigation includes new docs"""
        config = orchestrator._generate_mkdocs_config()
        
        # Check new documents in navigation
        assert "CORTEX-VS-COPILOT.md" in config
        assert "GETTING-STARTED.md" in config
        assert "ARCHITECTURE.md" in config
        assert "TECHNICAL-DOCUMENTATION.md" in config
        
        # Check navigation structure
        assert "- CORTEX vs COPILOT:" in config
        assert "- Getting Started:" in config
        assert "- Documentation:" in config
    
    def test_mkdocs_index_updated(self, orchestrator, mock_features):
        """Test MkDocs index page features CORTEX vs COPILOT"""
        index = orchestrator._generate_mkdocs_index(mock_features)
        
        # Check prominent placement
        assert "Why CORTEX?" in index
        assert "CORTEX-VS-COPILOT.md" in index
        assert "GETTING-STARTED.md" in index
        
        # Check comparison table
        assert "| Feature | GitHub Copilot | CORTEX |" in index
        
        # Check links to all new docs
        assert "[CORTEX vs COPILOT]" in index
        assert "[Getting Started]" in index
        assert "[Architecture]" in index
        assert "[Technical Documentation]" in index


class TestIntegration:
    """Integration tests for full pipeline"""
    
    def test_full_pipeline_dry_run(self, orchestrator):
        """Test full documentation pipeline in dry run mode"""
        result = orchestrator.execute(dry_run=True)
        
        assert result["status"] == "success"
        assert "phase_2" in result
        
        # Check all new phases present in dry run
        phase2_results = result["phase_2"]["results"]
        phase_types = [r["document_type"] for r in phase2_results if "document_type" in r]
        
        assert "cortex_vs_copilot" in phase_types
        assert "architecture" in phase_types
        assert "technical_docs" in phase_types
        assert "getting_started" in phase_types
    
    def test_all_files_created(self, orchestrator):
        """Test all new documentation files are created"""
        # Run orchestrator
        result = orchestrator.execute(dry_run=False)
        
        # Verify all files exist
        docs_path = Path(__file__).parent.parent / "docs"
        
        assert (docs_path / "CORTEX-VS-COPILOT.md").exists()
        assert (docs_path / "ARCHITECTURE.md").exists()
        assert (docs_path / "TECHNICAL-DOCUMENTATION.md").exists()
        assert (docs_path / "GETTING-STARTED.md").exists()
        
        # Verify file sizes reasonable
        assert (docs_path / "CORTEX-VS-COPILOT.md").stat().st_size > 10000
        assert (docs_path / "ARCHITECTURE.md").stat().st_size > 15000
        assert (docs_path / "TECHNICAL-DOCUMENTATION.md").stat().st_size > 5000
        assert (docs_path / "GETTING-STARTED.md").stat().st_size > 8000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
