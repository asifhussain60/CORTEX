"""
Test Multi-Persona HTML Generator (STATIC-VIZ-002).

Tests specialized dashboard generation for 5 personas:
- Developer: Technical details, APIs, dependencies
- Manager: Progress, velocity, blockers
- Executive: High-level metrics, ROI, strategic alignment
- Regulatory: Compliance, audit trails, security
- Product: Features, user impact, roadmap

AC Coverage:
- VIZ-002-AC01: Generate persona-specific HTML views
- VIZ-002-AC02: Persona filtering/highlighting logic
- VIZ-002-AC03: Subdirectory organization (personas/{persona}/)
"""

import pytest
from pathlib import Path
from cortex.visualization.multi_persona_generator import (
    MultiPersonaGenerator,
    Persona,
)


class TestPersonaDashboardGeneration:
    """Test persona-specific dashboard generation (VIZ-002-AC01)."""
    
    def test_generate_developer_dashboard(self, tmp_path):
        """Generate developer-focused dashboard."""
        generator = MultiPersonaGenerator(output_dir=tmp_path)
        
        repo_data = {
            "name": "cortex",
            "domain": "ai",
            "technical_stack": ["Python", "FastAPI", "Docker"],
            "api_endpoints": 25,
            "dependencies": 45,
        }
        
        result = generator.generate_persona_dashboard(
            persona=Persona.DEVELOPER,
            repository_data=repo_data
        )
        
        # Should create personas/developer/cortex.html
        dev_path = tmp_path / "personas" / "developer" / "cortex.html"
        assert dev_path.exists()
        
        html = dev_path.read_text()
        # Developer view should emphasize technical details
        assert "technical_stack" in html.lower() or "Python" in html
        assert "api" in html.lower() or "endpoint" in html.lower()
        assert "dependencies" in html.lower()
    
    def test_generate_manager_dashboard(self, tmp_path):
        """Generate manager-focused dashboard."""
        generator = MultiPersonaGenerator(output_dir=tmp_path)
        
        repo_data = {
            "name": "cortex",
            "velocity": {"last_sprint": 42, "average": 38},
            "blockers": ["Deploy automation", "Test coverage"],
            "completion_rate": 0.85,
        }
        
        result = generator.generate_persona_dashboard(
            persona=Persona.MANAGER,
            repository_data=repo_data
        )
        
        mgr_path = tmp_path / "personas" / "manager" / "cortex.html"
        assert mgr_path.exists()
        
        html = mgr_path.read_text()
        # Manager view should emphasize progress metrics
        assert "velocity" in html.lower() or "42" in html
        assert "blocker" in html.lower()
        assert "completion" in html.lower() or "85%" in html
    
    def test_generate_executive_dashboard(self, tmp_path):
        """Generate executive-focused dashboard."""
        generator = MultiPersonaGenerator(output_dir=tmp_path)
        
        repo_data = {
            "name": "cortex",
            "strategic_value": "High",
            "roi_estimate": "350%",
            "alignment": ["AI Strategy", "Innovation"],
        }
        
        result = generator.generate_persona_dashboard(
            persona=Persona.EXECUTIVE,
            repository_data=repo_data
        )
        
        exec_path = tmp_path / "personas" / "executive" / "cortex.html"
        assert exec_path.exists()
        
        html = exec_path.read_text()
        # Executive view should emphasize business value
        assert "strategic" in html.lower() or "High" in html
        assert "roi" in html.lower() or "350%" in html
    
    def test_generate_regulatory_dashboard(self, tmp_path):
        """Generate regulatory/compliance-focused dashboard."""
        generator = MultiPersonaGenerator(output_dir=tmp_path)
        
        repo_data = {
            "name": "cortex",
            "compliance_score": 92,
            "audit_trails": 1500,
            "security_scans": {"passed": 48, "failed": 2},
        }
        
        result = generator.generate_persona_dashboard(
            persona=Persona.REGULATORY,
            repository_data=repo_data
        )
        
        reg_path = tmp_path / "personas" / "regulatory" / "cortex.html"
        assert reg_path.exists()
        
        html = reg_path.read_text()
        # Regulatory view should emphasize compliance
        assert "compliance" in html.lower() or "92" in html
        assert "audit" in html.lower()
        assert "security" in html.lower()
    
    def test_generate_product_dashboard(self, tmp_path):
        """Generate product-focused dashboard."""
        generator = MultiPersonaGenerator(output_dir=tmp_path)
        
        repo_data = {
            "name": "cortex",
            "features": ["LENS Intelligence", "Multi-model estimation"],
            "user_impact": "500+ developers",
            "roadmap_items": 12,
        }
        
        result = generator.generate_persona_dashboard(
            persona=Persona.PRODUCT,
            repository_data=repo_data
        )
        
        prod_path = tmp_path / "personas" / "product" / "cortex.html"
        assert prod_path.exists()
        
        html = prod_path.read_text()
        # Product view should emphasize features and user impact
        assert "feature" in html.lower() or "LENS" in html
        assert "user" in html.lower() or "500+" in html
        assert "roadmap" in html.lower()


class TestPersonaFiltering:
    """Test persona-specific filtering logic (VIZ-002-AC02)."""
    
    def test_developer_filters_technical_data(self, tmp_path):
        """Developer persona should highlight technical metrics."""
        generator = MultiPersonaGenerator(output_dir=tmp_path)
        
        full_data = {
            "name": "cortex",
            "technical_stack": ["Python"],
            "strategic_value": "High",  # Not relevant for developers
            "compliance_score": 92,      # Not relevant for developers
        }
        
        filtered = generator.filter_for_persona(Persona.DEVELOPER, full_data)
        
        # Should include technical data
        assert "technical_stack" in filtered
        # Should exclude executive/regulatory data
        assert "strategic_value" not in filtered
        assert "compliance_score" not in filtered
    
    def test_executive_filters_strategic_data(self, tmp_path):
        """Executive persona should highlight strategic metrics."""
        generator = MultiPersonaGenerator(output_dir=tmp_path)
        
        full_data = {
            "name": "cortex",
            "technical_stack": ["Python"],   # Not relevant for executives
            "strategic_value": "High",
            "roi_estimate": "350%",
            "api_endpoints": 25,             # Too detailed for executives
        }
        
        filtered = generator.filter_for_persona(Persona.EXECUTIVE, full_data)
        
        # Should include strategic data
        assert "strategic_value" in filtered
        assert "roi_estimate" in filtered
        # Should exclude technical details
        assert "technical_stack" not in filtered
        assert "api_endpoints" not in filtered


class TestSubdirectoryOrganization:
    """Test subdirectory structure (VIZ-002-AC03)."""
    
    def test_creates_persona_subdirectories(self, tmp_path):
        """Should create personas/{persona}/ subdirectories."""
        generator = MultiPersonaGenerator(output_dir=tmp_path)
        
        repo_data = {"name": "cortex"}
        
        # Generate all persona dashboards
        for persona in Persona:
            generator.generate_persona_dashboard(persona, repo_data)
        
        # Should have subdirectory for each persona
        assert (tmp_path / "personas" / "developer").exists()
        assert (tmp_path / "personas" / "manager").exists()
        assert (tmp_path / "personas" / "executive").exists()
        assert (tmp_path / "personas" / "regulatory").exists()
        assert (tmp_path / "personas" / "product").exists()
    
    def test_generates_persona_index(self, tmp_path):
        """Should generate personas/index.html with links to all personas."""
        generator = MultiPersonaGenerator(output_dir=tmp_path)
        
        generator.generate_persona_index()
        
        index_path = tmp_path / "personas" / "index.html"
        assert index_path.exists()
        
        html = index_path.read_text()
        # Should link to all personas
        assert "developer" in html.lower()
        assert "manager" in html.lower()
        assert "executive" in html.lower()
        assert "regulatory" in html.lower()
        assert "product" in html.lower()
