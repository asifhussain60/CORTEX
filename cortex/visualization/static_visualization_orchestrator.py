"""
Static Visualization Orchestrator (STATIC-VIZ-001).

Generates portfolio-level static HTML + JSON dashboards for multi-repository management.

Author: Asif Hussain
Phase: 17 Track B
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any
import json
from datetime import datetime


@dataclass
class DashboardOutput:
    """Output paths for generated dashboard files."""
    html_files: Dict[str, Path] = field(default_factory=dict)
    json_files: Dict[str, Path] = field(default_factory=dict)
    css_files: Dict[str, Path] = field(default_factory=dict)
    js_files: Dict[str, Path] = field(default_factory=dict)


class StaticVisualizationOrchestrator:
    """
    Portfolio-level static dashboard generator.
    
    Features:
    - Entry dashboard with tabs: Repositories | Domains | Quick Links
    - JSON export for external tools
    - Domain-level aggregation
    - Multi-repository navigation
    
    Output Structure:
        output_dir/
            index.html           # Entry dashboard
            portfolio.json       # Full portfolio data
            domains/             # Domain-specific dashboards (VIZ-003+)
            repositories/        # Repository dashboards (VIZ-004)
    """
    
    def __init__(self, output_dir: Path):
        """
        Initialize orchestrator.
        
        Args:
            output_dir: Root directory for generated dashboards
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_entry_dashboard(self, repositories: List[Dict[str, Any]]) -> DashboardOutput:
        """
        Generate entry-level portfolio dashboard.
        
        Args:
            repositories: List of repository dicts with keys:
                - name: Repository name
                - path: Repository path
                - domain: Domain classification
                - (optional) loc, files, authors, etc.
        
        Returns:
            DashboardOutput with generated file paths
        """
        output = DashboardOutput()
        
        # Group repositories by domain
        domains = self._group_by_domain(repositories)
        
        # Generate HTML
        html_content = self._generate_entry_html(repositories, domains)
        
        # Write index.html
        index_path = self.output_dir / "index.html"
        index_path.write_text(html_content)
        output.html_files["entry"] = index_path
        
        return output
    
    def export_portfolio_json(self, repositories: List[Dict[str, Any]]) -> DashboardOutput:
        """
        Export portfolio data as JSON.
        
        Args:
            repositories: List of repository dicts
        
        Returns:
            DashboardOutput with JSON file path
        """
        output = DashboardOutput()
        
        # Build portfolio data structure
        portfolio_data = {
            "generated_at": datetime.now().isoformat(),
            "repository_count": len(repositories),
            "repositories": repositories,
            "domains": self._aggregate_domains(repositories),
        }
        
        # Write portfolio.json
        json_path = self.output_dir / "portfolio.json"
        json_path.write_text(json.dumps(portfolio_data, indent=2))
        output.json_files["portfolio"] = json_path
        
        return output
    
    def _group_by_domain(self, repositories: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group repositories by domain."""
        domains: Dict[str, List[Dict[str, Any]]] = {}
        
        for repo in repositories:
            domain = repo.get("domain", "uncategorized")
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(repo)
        
        return domains
    
    def _aggregate_domains(self, repositories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate metrics by domain."""
        domains: Dict[str, Any] = {}
        
        for repo in repositories:
            domain = repo.get("domain", "uncategorized")
            
            if domain not in domains:
                domains[domain] = {
                    "repository_count": 0,
                    "total_loc": 0,
                    "total_files": 0,
                    "repositories": [],
                }
            
            domains[domain]["repository_count"] += 1
            domains[domain]["total_loc"] += repo.get("loc", 0)
            domains[domain]["total_files"] += repo.get("files", 0)
            domains[domain]["repositories"].append(repo["name"])
        
        return domains
    
    def _generate_entry_html(
        self,
        repositories: List[Dict[str, Any]],
        domains: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """Generate entry dashboard HTML."""
        
        # Build repository list HTML
        repo_list_html = ""
        for repo in repositories:
            repo_list_html += f"""
            <div class="repo-card">
                <h3>{repo['name']}</h3>
                <p>Domain: {repo.get('domain', 'N/A')}</p>
                <p>Path: {repo.get('path', 'N/A')}</p>
            </div>
            """
        
        # Build domain list HTML
        domain_list_html = ""
        for domain_name, domain_repos in domains.items():
            repo_count = len(domain_repos)
            domain_list_html += f"""
            <div class="domain-card">
                <h3>{domain_name}</h3>
                <p>{repo_count} repositor{"y" if repo_count == 1 else "ies"}</p>
                <ul>
                    {''.join(f'<li>{r["name"]}</li>' for r in domain_repos)}
                </ul>
            </div>
            """
        
        # Generate full HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio Dashboard - CORTEX</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .tabs {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .tab {{ padding: 10px 20px; background: #007bff; color: white; cursor: pointer; border-radius: 5px; }}
        .tab.active {{ background: #0056b3; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .repo-card, .domain-card {{ background: white; padding: 15px; margin-bottom: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .repo-card h3, .domain-card h3 {{ margin-top: 0; color: #007bff; }}
        ul {{ margin: 5px 0; padding-left: 20px; }}
    </style>
</head>
<body>
    <h1>CORTEX Portfolio Dashboard</h1>
    
    <div class="tabs">
        <div class="tab active" onclick="switchTab('repositories')">Repositories</div>
        <div class="tab" onclick="switchTab('domains')">Domains</div>
        <div class="tab" onclick="switchTab('quicklinks')">Quick Links</div>
    </div>
    
    <div id="repositories" class="tab-content active">
        <h2>All Repositories ({len(repositories)})</h2>
        {repo_list_html}
    </div>
    
    <div id="domains" class="tab-content">
        <h2>Domains ({len(domains)})</h2>
        {domain_list_html}
    </div>
    
    <div id="quicklinks" class="tab-content">
        <h2>Quick Links</h2>
        <ul>
            <li><a href="portfolio.json">Portfolio JSON Data</a></li>
            <li><a href="domains/">Domain Dashboards</a></li>
            <li><a href="repositories/">Repository Dashboards</a></li>
        </ul>
    </div>
    
    <script>
        function switchTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
        """
        
        return html.strip()
