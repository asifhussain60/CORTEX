"""
Multi-Persona HTML Generator (STATIC-VIZ-002).

Generates specialized dashboards for 5 personas with tailored content filtering.

Author: Asif Hussain
Phase: 17 Track B
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List
from enum import Enum


class Persona(Enum):
    """Dashboard personas with different focus areas."""
    DEVELOPER = "developer"
    MANAGER = "manager"
    EXECUTIVE = "executive"
    REGULATORY = "regulatory"
    PRODUCT = "product"


@dataclass
class PersonaDashboardConfig:
    """Configuration for persona-specific dashboards."""
    persona: Persona
    title: str
    description: str
    relevant_fields: List[str]  # Fields to include
    excluded_fields: List[str]  # Fields to exclude


# Persona configurations
PERSONA_CONFIGS = {
    Persona.DEVELOPER: PersonaDashboardConfig(
        persona=Persona.DEVELOPER,
        title="Developer Dashboard",
        description="Technical details, APIs, dependencies, and code metrics",
        relevant_fields=[
            "technical_stack", "api_endpoints", "dependencies", "code_quality",
            "test_coverage", "build_status", "deployment_frequency"
        ],
        excluded_fields=["strategic_value", "roi_estimate", "compliance_score", "roadmap_items"]
    ),
    Persona.MANAGER: PersonaDashboardConfig(
        persona=Persona.MANAGER,
        title="Manager Dashboard",
        description="Progress tracking, velocity, blockers, and team metrics",
        relevant_fields=[
            "velocity", "blockers", "completion_rate", "sprint_progress",
            "team_size", "burndown", "story_points"
        ],
        excluded_fields=["technical_stack", "strategic_value", "api_endpoints"]
    ),
    Persona.EXECUTIVE: PersonaDashboardConfig(
        persona=Persona.EXECUTIVE,
        title="Executive Dashboard",
        description="Strategic value, ROI, high-level metrics, and alignment",
        relevant_fields=[
            "strategic_value", "roi_estimate", "alignment", "business_impact",
            "market_position", "innovation_score"
        ],
        excluded_fields=["technical_stack", "api_endpoints", "dependencies", "test_coverage"]
    ),
    Persona.REGULATORY: PersonaDashboardConfig(
        persona=Persona.REGULATORY,
        title="Regulatory Dashboard",
        description="Compliance, audit trails, security, and governance",
        relevant_fields=[
            "compliance_score", "audit_trails", "security_scans", "vulnerabilities",
            "data_protection", "access_controls", "incident_reports"
        ],
        excluded_fields=["velocity", "roadmap_items", "technical_stack"]
    ),
    Persona.PRODUCT: PersonaDashboardConfig(
        persona=Persona.PRODUCT,
        title="Product Dashboard",
        description="Features, user impact, roadmap, and product metrics",
        relevant_fields=[
            "features", "user_impact", "roadmap_items", "adoption_rate",
            "customer_feedback", "feature_requests", "release_notes"
        ],
        excluded_fields=["technical_stack", "compliance_score", "api_endpoints"]
    ),
}


class MultiPersonaGenerator:
    """
    Generate specialized dashboards for different personas.
    
    Creates persona-specific HTML views with tailored content:
    - Developer: Technical focus (APIs, dependencies, code quality)
    - Manager: Progress focus (velocity, blockers, sprints)
    - Executive: Strategic focus (ROI, value, alignment)
    - Regulatory: Compliance focus (audits, security, governance)
    - Product: Feature focus (roadmap, users, adoption)
    
    Output Structure:
        output_dir/
            personas/
                index.html              # Persona selector
                developer/
                    {repo}.html
                manager/
                    {repo}.html
                executive/
                    {repo}.html
                regulatory/
                    {repo}.html
                product/
                    {repo}.html
    """
    
    def __init__(self, output_dir: Path):
        """
        Initialize generator.
        
        Args:
            output_dir: Root directory for persona dashboards
        """
        self.output_dir = Path(output_dir)
        self.personas_dir = self.output_dir / "personas"
        self.personas_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_persona_dashboard(
        self,
        persona: Persona,
        repository_data: Dict[str, Any]
    ) -> Path:
        """
        Generate dashboard for specific persona.
        
        Args:
            persona: Target persona
            repository_data: Repository data dict
        
        Returns:
            Path to generated HTML file
        """
        # Filter data for persona
        filtered_data = self.filter_for_persona(persona, repository_data)
        
        # Get persona config
        config = PERSONA_CONFIGS[persona]
        
        # Generate HTML
        html = self._generate_persona_html(config, filtered_data)
        
        # Create persona subdirectory
        persona_dir = self.personas_dir / persona.value
        persona_dir.mkdir(exist_ok=True)
        
        # Write HTML file
        repo_name = repository_data.get("name", "repository")
        html_path = persona_dir / f"{repo_name}.html"
        html_path.write_text(html)
        
        return html_path
    
    def filter_for_persona(
        self,
        persona: Persona,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Filter data for persona-specific view.
        
        Args:
            persona: Target persona
            data: Full repository data
        
        Returns:
            Filtered data dict with only relevant fields
        """
        config = PERSONA_CONFIGS[persona]
        
        # Start with name (always include)
        filtered = {"name": data.get("name", "Unknown")}
        
        # Include relevant fields
        for field in config.relevant_fields:
            if field in data:
                filtered[field] = data[field]
        
        # Explicitly exclude unwanted fields
        for field in config.excluded_fields:
            filtered.pop(field, None)
        
        return filtered
    
    def generate_persona_index(self) -> Path:
        """
        Generate personas/index.html with links to all personas.
        
        Returns:
            Path to generated index.html
        """
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Persona Dashboards - CORTEX</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        h1 { color: #333; }
        .persona-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }
        .persona-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); cursor: pointer; transition: transform 0.2s; }
        .persona-card:hover { transform: translateY(-5px); }
        .persona-card h2 { margin-top: 0; color: #007bff; }
        .persona-card p { color: #666; }
    </style>
</head>
<body>
    <h1>CORTEX Persona Dashboards</h1>
    <p>Select a persona to view tailored dashboard views:</p>
    
    <div class="persona-grid">
"""
        
        for persona_enum in Persona:
            config = PERSONA_CONFIGS[persona_enum]
            html += f"""
        <div class="persona-card" onclick="window.location='{persona_enum.value}/'">
            <h2>{config.title}</h2>
            <p>{config.description}</p>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
        """
        
        index_path = self.personas_dir / "index.html"
        index_path.write_text(html.strip())
        
        return index_path
    
    def _generate_persona_html(
        self,
        config: PersonaDashboardConfig,
        data: Dict[str, Any]
    ) -> str:
        """Generate HTML for persona dashboard."""
        
        # Build data section HTML
        data_html = ""
        for key, value in data.items():
            if key == "name":
                continue  # Name is in title
            
            # Format value
            if isinstance(value, list):
                value_str = "<ul>" + "".join(f"<li>{item}</li>" for item in value) + "</ul>"
            elif isinstance(value, dict):
                value_str = "<pre>" + str(value) + "</pre>"
            else:
                value_str = str(value)
            
            # Human-readable key
            key_display = key.replace("_", " ").title()
            
            data_html += f"""
        <div class="data-item">
            <strong>{key_display}:</strong>
            <div>{value_str}</div>
        </div>
            """
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.title} - {data.get('name', 'Repository')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .subtitle {{ color: #666; margin-bottom: 30px; }}
        .data-item {{ background: white; padding: 15px; margin-bottom: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .data-item strong {{ color: #007bff; }}
        ul {{ margin: 5px 0; padding-left: 20px; }}
        pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
        .back-link {{ display: inline-block; margin-bottom: 20px; color: #007bff; text-decoration: none; }}
        .back-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <a href="../index.html" class="back-link">← Back to Personas</a>
    
    <h1>{config.title}</h1>
    <p class="subtitle">{config.description}</p>
    
    <h2>{data.get('name', 'Repository')}</h2>
    
    <div class="data-section">
        {data_html}
    </div>
</body>
</html>
        """
        
        return html.strip()
