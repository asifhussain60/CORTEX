"""
CORTEX Post-Upgrade Smoke Tests
================================

Fast smoke tests that run immediately after upgrade to verify CORTEX is functional.
These tests are designed to catch critical issues quickly (< 30 seconds execution).

Test Categories:
1. Critical Imports - Core modules loadable
2. Entry Points - Help command works
3. Database Connectivity - Can connect to Tier 2
4. Template Loading - Response templates load
5. Configuration - Config files valid

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sys
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestCriticalImports:
    """Verify core modules can be imported"""
    
    def test_import_feedback_agent(self):
        """FeedbackAgent can be imported"""
        from agents.feedback_agent import FeedbackAgent
        assert FeedbackAgent is not None
    
    def test_import_view_discovery_agent(self):
        """ViewDiscoveryAgent can be imported"""
        from agents.view_discovery_agent import ViewDiscoveryAgent
        assert ViewDiscoveryAgent is not None
    
    def test_import_tdd_workflow_integrator(self):
        """TDDWorkflowIntegrator can be imported"""
        from workflows.tdd_workflow_integrator import TDDWorkflowIntegrator
        assert TDDWorkflowIntegrator is not None


class TestEntryPoints:
    """Verify entry points accessible"""
    
    def test_cortex_prompt_exists(self):
        """CORTEX.prompt.md exists"""
        path = Path(__file__).parent.parent / '.github' / 'prompts' / 'CORTEX.prompt.md'
        assert path.exists(), "Entry point file missing"
    
    def test_cortex_prompt_has_help(self):
        """CORTEX.prompt.md documents help command"""
        path = Path(__file__).parent.parent / '.github' / 'prompts' / 'CORTEX.prompt.md'
        content = path.read_text(encoding='utf-8')
        assert 'help' in content.lower(), "Help command not documented"


class TestDatabaseConnectivity:
    """Verify database is accessible"""
    
    def test_tier2_database_exists(self):
        """Tier 2 database file exists"""
        path = Path(__file__).parent.parent / 'cortex-brain' / 'tier2' / 'knowledge_graph.db'
        assert path.exists(), "Tier 2 database missing"
    
    def test_tier2_database_connectable(self):
        """Can connect to Tier 2 database"""
        import sqlite3
        path = Path(__file__).parent.parent / 'cortex-brain' / 'tier2' / 'knowledge_graph.db'
        
        conn = sqlite3.connect(str(path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None, "Database appears empty"


class TestTemplateLoading:
    """Verify response templates load"""
    
    def test_response_templates_exist(self):
        """response-templates.yaml exists"""
        path = Path(__file__).parent.parent / 'cortex-brain' / 'response-templates.yaml'
        assert path.exists(), "Response templates file missing"
    
    def test_response_templates_loadable(self):
        """response-templates.yaml can be loaded"""
        import yaml
        path = Path(__file__).parent.parent / 'cortex-brain' / 'response-templates.yaml'
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        assert data is not None, "Templates file empty"
        assert 'templates' in data, "Templates key missing"


class TestConfiguration:
    """Verify configuration files valid"""
    
    def test_capabilities_yaml_exists(self):
        """capabilities.yaml exists"""
        path = Path(__file__).parent.parent / 'cortex-brain' / 'capabilities.yaml'
        assert path.exists(), "capabilities.yaml missing"
    
    def test_capabilities_yaml_loadable(self):
        """capabilities.yaml can be loaded"""
        import yaml
        path = Path(__file__).parent.parent / 'cortex-brain' / 'capabilities.yaml'
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        assert data is not None, "capabilities.yaml empty"
    
    def test_brain_protection_rules_exist(self):
        """brain-protection-rules.yaml exists"""
        path = Path(__file__).parent.parent / 'cortex-brain' / 'brain-protection-rules.yaml'
        assert path.exists(), "brain-protection-rules.yaml missing"
    
    def test_brain_protection_rules_loadable(self):
        """brain-protection-rules.yaml can be loaded"""
        import yaml
        path = Path(__file__).parent.parent / 'cortex-brain' / 'brain-protection-rules.yaml'
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        assert data is not None, "brain-protection-rules.yaml empty"


class TestVersionCompatibility:
    """Verify version information"""
    
    def test_version_file_exists(self):
        """VERSION file exists"""
        path = Path(__file__).parent.parent / 'VERSION'
        assert path.exists(), "VERSION file missing"
    
    def test_version_format_valid(self):
        """VERSION file has valid format"""
        path = Path(__file__).parent.parent / 'VERSION'
        content = path.read_text().strip()
        
        # Should be v3.x.x or 3.x.x format
        assert len(content) > 0, "VERSION file empty"
        assert '.' in content or 'v' in content.lower(), f"Invalid version format: {content}"


if __name__ == '__main__':
    # Run smoke tests with minimal output
    pytest.main([__file__, '-v', '--tb=line', '-x'])
