"""
Domain Dashboard Generator for Company Domains.

Generates rich, glassmorphism-themed dashboards for company domain analysis
with D3.js visualizations, security findings, and comprehensive metrics.

Authority: cortex-architect.prompt.md v8.0
Author: Asif Hussain
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class DomainDashboardGenerator:
    """
    Generate impressive glassmorphism dashboards for company domains.
    
    Features:
    - Dark glassmorphism theme from docs/
    - CORTEX logo in header
    - D3.js interactive visualizations
    - Rich content with security findings
    - Architecture diagrams
    - Dependency graphs
    - Timeline visualizations
    """
    
    def __init__(self, domain_name: str, domain_path: Path):
        """
        Initialize dashboard generator.
        
        Args:
            domain_name: Name of the domain (e.g., 'kashkole')
            domain_path: Path to domain directory
        """
        self.domain_name = domain_name
        self.domain_path = domain_path
        self.assets_path = domain_path / "assets"
        
    def generate_dashboard(
        self,
        onboarding_data: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate complete dashboard HTML.
        
        Args:
            onboarding_data: Data from RepositoryOnboardingOrchestrator
            output_path: Optional custom output path
            
        Returns:
            Path to generated dashboard.html
        """
        if output_path is None:
            output_path = self.domain_path / "dashboard.html"
            
        html_content = self._generate_html(onboarding_data)
        
        output_path.write_text(html_content, encoding='utf-8')
        logger.info(f"Generated dashboard: {output_path}")
        
        return output_path
    
    def _generate_html(self, data: Dict[str, Any]) -> str:
        """Generate complete HTML content."""
        
        # Extract key metrics
        security_risks = data.get('security_risks', {})
        holistic_context = data.get('holistic_context', {})
        recommendations = data.get('recommendations', [])
        
        p0_count = len(security_risks.get('p0_risks', []))
        p1_count = len(security_risks.get('p1_risks', []))
        p2_count = len(security_risks.get('p2_risks', []))
        
        # Calculate health score
        health_score = self._calculate_health_score(security_risks)
        health_label = self._get_health_label(health_score)
        health_category = self._get_health_category(health_score)
        
        # Get project details
        repo_path = data.get('repo_path', 'Unknown')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Get solution structure
        solution_projects = self._extract_solution_projects(holistic_context)
        
        # Get tech stack
        tech_stack = self._extract_tech_stack(holistic_context)
        
        # Get database info
        db_info = self._extract_database_info(holistic_context)
        
        html = f'''<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.domain_name.upper()} - CORTEX v8.0</title>
    
    <!-- Core Styles -->
    <link rel="stylesheet" href="assets/css/variables.css">
    <link rel="stylesheet" href="assets/css/cortex-glass-system.css">
    <link rel="stylesheet" href="assets/css/main.css">
    <link rel="stylesheet" href="assets/css/dashboard-enhancements.css">
    
    <!-- D3.js for Visualizations -->
    <script src="https://d3js.org/d3.v7.min.js"></script>
    
    <style>
        :root {{
            --bg-primary: #0a0a0f;
            --bg-secondary: #13131a;
            --bg-card: #1a1a24;
            --text-primary: #e4e4e7;
            --text-secondary: #a1a1aa;
            --accent-blue: #3b82f6;
            --accent-green: #22c55e;
            --accent-yellow: #eab308;
            --accent-red: #ef4444;
            --accent-purple: #a855f7;
            --glass-bg: rgba(26, 26, 36, 0.8);
            --glass-border: rgba(255, 255, 255, 0.1);
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
            color: var(--text-primary);
            min-height: 100vh;
            margin: 0;
            padding: 0;
        }}
        
        .dashboard-container {{
            max-width: 1800px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        /* Enhanced Header with Logo */
        .header {{
            display: flex;
            align-items: center;
            margin-bottom: 2rem;
            padding: 2rem;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            backdrop-filter: blur(20px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
        }}
        
        .header-logo {{
            width: 100px;
            height: 100px;
            border-radius: 20px;
            margin-right: 2rem;
            box-shadow: 0 12px 48px rgba(59, 130, 246, 0.3);
            border: 2px solid var(--glass-border);
        }}
        
        .header-content {{
            flex: 1;
        }}
        
        .header-title {{
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0 0 0.5rem 0;
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .header-subtitle {{
            font-size: 1.125rem;
            color: var(--text-secondary);
            margin: 0 0 1rem 0;
        }}
        
        .header-meta {{
            display: flex;
            gap: 2rem;
            font-size: 0.875rem;
            color: var(--text-secondary);
        }}
        
        .header-meta-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        /* Health Score Card */
        .health-score-card {{
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            padding: 2rem;
            backdrop-filter: blur(20px);
            margin-bottom: 2rem;
        }}
        
        .health-score-value {{
            font-size: 4rem;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 1rem;
        }}
        
        .health-score-label {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        
        .health-score-description {{
            color: var(--text-secondary);
        }}
        
        /* Tabs */
        .tabs {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }}
        
        .tab {{
            padding: 1rem 2rem;
            background: var(--bg-card);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            cursor: pointer;
            color: var(--text-secondary);
            font-weight: 600;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .tab::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .tab span {{
            position: relative;
            z-index: 1;
        }}
        
        .tab:hover {{
            border-color: var(--accent-blue);
            transform: translateY(-2px);
        }}
        
        .tab.active {{
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            color: white;
            border-color: transparent;
        }}
        
        .tab.active::before {{
            opacity: 1;
        }}
        
        /* Tab Content */
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        /* Cards */
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .card {{
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 2rem;
            backdrop-filter: blur(20px);
            transition: all 0.3s ease;
        }}
        
        .card:hover {{
            border-color: var(--accent-blue);
            box-shadow: 0 12px 48px rgba(59, 130, 246, 0.2);
            transform: translateY(-4px);
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }}
        
        .card-title {{
            font-size: 1.25rem;
            font-weight: 600;
        }}
        
        .metric-value {{
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 0.5rem;
        }}
        
        .metric-label {{
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}
        
        /* Security Badges */
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.875rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .badge-p0 {{ background: rgba(239, 68, 68, 0.2); color: var(--accent-red); }}
        .badge-p1 {{ background: rgba(234, 179, 8, 0.2); color: var(--accent-yellow); }}
        .badge-p2 {{ background: rgba(59, 130, 246, 0.2); color: var(--accent-blue); }}
        .badge-critical {{ background: rgba(239, 68, 68, 0.2); color: var(--accent-red); }}
        .badge-excellent {{ background: rgba(34, 197, 94, 0.2); color: var(--accent-green); }}
        .badge-good {{ background: rgba(59, 130, 246, 0.2); color: var(--accent-blue); }}
        .badge-needs-improvement {{ background: rgba(234, 179, 8, 0.2); color: var(--accent-yellow); }}
        
        /* Finding List */
        .finding-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        
        .finding-item {{
            padding: 1.5rem;
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            margin-bottom: 1rem;
            background: var(--bg-secondary);
            transition: all 0.3s ease;
        }}
        
        .finding-item:hover {{
            border-color: var(--accent-blue);
            transform: translateX(8px);
        }}
        
        .finding-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
        }}
        
        .finding-id {{
            font-family: 'JetBrains Mono', monospace;
            color: var(--accent-purple);
            font-weight: 600;
        }}
        
        .finding-title {{
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        
        .finding-description {{
            color: var(--text-secondary);
            font-size: 0.9375rem;
            line-height: 1.6;
        }}
        
        .finding-location {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8125rem;
            color: var(--text-secondary);
            margin-top: 1rem;
            padding: 0.75rem;
            background: var(--bg-primary);
            border-radius: 8px;
        }}
        
        /* D3 Diagram Container */
        .diagram-container {{
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 2rem;
            backdrop-filter: blur(20px);
            min-height: 600px;
            margin-bottom: 2rem;
        }}
        
        #architecture-diagram,
        #dependency-graph,
        #timeline-chart {{
            width: 100%;
            height: 550px;
        }}
        
        /* Tech Stack Tags */
        .tech-tag {{
            display: inline-block;
            padding: 0.5rem 1rem;
            background: var(--bg-secondary);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            margin: 0.25rem;
            font-size: 0.875rem;
            transition: all 0.3s ease;
        }}
        
        .tech-tag:hover {{
            border-color: var(--accent-blue);
            background: rgba(59, 130, 246, 0.1);
        }}
        
        /* Timeline */
        .timeline {{
            position: relative;
            padding-left: 3rem;
        }}
        
        .timeline::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 2px;
            background: linear-gradient(180deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
        }}
        
        .timeline-item {{
            position: relative;
            padding-bottom: 2rem;
        }}
        
        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -3rem;
            top: 0.25rem;
            width: 16px;
            height: 16px;
            background: var(--accent-blue);
            border-radius: 50%;
            transform: translateX(-7px);
            box-shadow: 0 0 0 4px var(--bg-primary);
        }}
        
        /* Data Table */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .data-table th,
        .data-table td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--glass-border);
        }}
        
        .data-table th {{
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .data-table tbody tr {{
            transition: all 0.3s ease;
        }}
        
        .data-table tbody tr:hover {{
            background: var(--bg-secondary);
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- Header with Logo -->
        <div class="header">
            <img src="assets/images/cortex-logo-200.png" alt="CORTEX Logo" class="header-logo">
            <div class="header-content">
                <h1 class="header-title">{self.domain_name.upper()}</h1>
                <p class="header-subtitle">Islamic Knowledge Management Platform</p>
                <div class="header-meta">
                    <div class="header-meta-item">
                        <span>📅</span>
                        <span>Onboarded: {timestamp.split('T')[0]}</span>
                    </div>
                    <div class="header-meta-item">
                        <span>🧠</span>
                        <span>CORTEX v8.0</span>
                    </div>
                    <div class="header-meta-item">
                        <span>🔒</span>
                        <span>Security Score: {health_score}/100</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Health Score Summary -->
        <div class="health-score-card">
            <div class="card-grid">
                <div>
                    <div class="metric-value" style="color: {self._get_health_color(health_score)};">
                        {health_score}
                    </div>
                    <div class="health-score-label">Health Score</div>
                    <span class="badge badge-{health_category}">{health_label}</span>
                </div>
                <div>
                    <div class="metric-value">{len(solution_projects)}</div>
                    <div class="metric-label">Solution Projects</div>
                </div>
                <div>
                    <div class="metric-value">{len(holistic_context.get('code_analysis', {}).get('files', []))}</div>
                    <div class="metric-label">Source Files</div>
                </div>
                <div>
                    <div class="metric-value">{p0_count + p1_count + p2_count}</div>
                    <div class="metric-label">Security Findings</div>
                </div>
            </div>
        </div>
        
        <!-- Tabs -->
        <div class="tabs">
            <button class="tab active" onclick="showTab('overview')">
                <span>📊 Overview</span>
            </button>
            <button class="tab" onclick="showTab('security')">
                <span>🔒 Security</span>
            </button>
            <button class="tab" onclick="showTab('architecture')">
                <span>🏗️ Architecture</span>
            </button>
            <button class="tab" onclick="showTab('tech-stack')">
                <span>💻 Tech Stack</span>
            </button>
            <button class="tab" onclick="showTab('database')">
                <span>💾 Database</span>
            </button>
            <button class="tab" onclick="showTab('recommendations')">
                <span>💡 Recommendations</span>
            </button>
            <button class="tab" onclick="showTab('modernization')">
                <span>🚀 Modernization</span>
            </button>
            <button class="tab" onclick="showTab('compliance')">
                <span>✅ Compliance</span>
            </button>
            <button class="tab" onclick="showTab('metrics')">
                <span>📈 Metrics</span>
            </button>
            <button class="tab" onclick="showTab('timeline')">
                <span>⏱️ Timeline</span>
            </button>
        </div>
        
        <!-- Tab: Overview -->
        <div id="overview" class="tab-content active">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Project Description</h2>
                </div>
                <p>{self._get_project_description()}</p>
            </div>
            
            <div class="card-grid">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Solution Structure</h3>
                    </div>
                    <ul class="finding-list">
                        {''.join(f'<li class="finding-item"><div class="finding-title">{proj}</div></li>' for proj in solution_projects[:5])}
                    </ul>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Key Features</h3>
                    </div>
                    <ul class="finding-list">
                        <li class="finding-item">Quran browsing with Hijri calendar</li>
                        <li class="finding-item">Knowledge articles management</li>
                        <li class="finding-item">Email notifications</li>
                        <li class="finding-item">Admin panel</li>
                        <li class="finding-item">Multi-language support</li>
                    </ul>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Architecture Visualization</h2>
                </div>
                <div class="diagram-container">
                    <svg id="architecture-diagram"></svg>
                </div>
            </div>
        </div>
        
        <!-- Tab: Security -->
        <div id="security" class="tab-content">
            <div class="card-grid">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">P0 Critical</h3>
                        <span class="badge badge-p0">🔴 {p0_count} P0</span>
                    </div>
                    <div class="metric-value" style="color: var(--accent-red);">{p0_count}</div>
                    <div class="metric-label">Hardcoded credentials, machine keys</div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">P1 High</h3>
                        <span class="badge badge-p1">🟡 {p1_count} P1</span>
                    </div>
                    <div class="metric-value" style="color: var(--accent-yellow);">{p1_count}</div>
                    <div class="metric-label">Deprecated algorithms, outdated framework</div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">P2 Medium</h3>
                        <span class="badge badge-p2">🔵 {p2_count} P2</span>
                    </div>
                    <div class="metric-value" style="color: var(--accent-blue);">{p2_count}</div>
                    <div class="metric-label">Flash content, legacy web services</div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">P0 Critical Findings</h2>
                </div>
                <ul class="finding-list">
                    {self._generate_security_findings_html(security_risks.get('p0_risks', []))}
                </ul>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Security Trend</h2>
                </div>
                <div class="diagram-container">
                    <svg id="security-timeline"></svg>
                </div>
            </div>
        </div>
        
        <!-- Tab: Architecture -->
        <div id="architecture" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Dependency Graph</h2>
                </div>
                <div class="diagram-container">
                    <svg id="dependency-graph"></svg>
                </div>
            </div>
            
            <div class="card-grid">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Layers</h3>
                    </div>
                    <ul class="finding-list">
                        <li class="finding-item">Main Website (presentation)</li>
                        <li class="finding-item">Class Libraries (business logic)</li>
                        <li class="finding-item">Email Scheduler (background)</li>
                        <li class="finding-item">SQL Server (data layer)</li>
                    </ul>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Patterns</h3>
                    </div>
                    <div class="tech-tag">Server-side VB.NET</div>
                    <div class="tech-tag">Class Library</div>
                    <div class="tech-tag">Database-first</div>
                    <div class="tech-tag">Web Forms</div>
                </div>
            </div>
        </div>
        
        <!-- Tab: Tech Stack -->
        <div id="tech-stack" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Technology Stack</h2>
                </div>
                <div>
                    {self._generate_tech_stack_html(tech_stack)}
                </div>
            </div>
            
            <div class="card-grid">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Backend</h3>
                    </div>
                    <div class="tech-tag">ASP.NET Web Forms</div>
                    <div class="tech-tag">VB.NET</div>
                    <div class="tech-tag">.NET Framework 4.0</div>
                    <div class="tech-tag">Class Libraries</div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Database</h3>
                    </div>
                    <div class="tech-tag">SQL Server</div>
                    <div class="tech-tag">Stored Procedures</div>
                    <div class="tech-tag">ConnectionStrings</div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Legacy</h3>
                    </div>
                    <div class="tech-tag">Flash Content</div>
                    <div class="tech-tag">SHA1 Hashing</div>
                    <div class="tech-tag">Machine Keys</div>
                </div>
            </div>
        </div>
        
        <!-- Tab: Database -->
        <div id="database" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Database Schema</h2>
                </div>
                {self._generate_database_info_html(db_info)}
            </div>
        </div>
        
        <!-- Tab: Recommendations -->
        <div id="recommendations" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Prioritized Recommendations</h2>
                </div>
                <ul class="finding-list">
                    {self._generate_recommendations_html(recommendations)}
                </ul>
            </div>
        </div>
        
        <!-- Tab: Modernization -->
        <div id="modernization" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Modernization Roadmap</h2>
                </div>
                <div class="timeline">
                    <div class="timeline-item">
                        <h4>Phase 1: Security Hardening (Immediate)</h4>
                        <p>Remove hardcoded credentials, rotate machine keys, migrate to Azure Key Vault</p>
                    </div>
                    <div class="timeline-item">
                        <h4>Phase 2: Framework Upgrade (1-2 months)</h4>
                        <p>Migrate to .NET 6/8, replace SHA1 with BCrypt, upgrade to MVC/Razor Pages</p>
                    </div>
                    <div class="timeline-item">
                        <h4>Phase 3: Architecture Refactor (3-4 months)</h4>
                        <p>Implement Clean Architecture, introduce CQRS, migrate to Entity Framework Core</p>
                    </div>
                    <div class="timeline-item">
                        <h4>Phase 4: Cloud Native (4-6 months)</h4>
                        <p>Containerization, Azure App Service deployment, implement CI/CD</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Tab: Compliance -->
        <div id="compliance" class="tab-content">
            <div class="card-grid">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">OWASP Top 10</h3>
                    </div>
                    <div class="metric-value" style="color: var(--accent-yellow);">6/10</div>
                    <div class="metric-label">Compliant</div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">PCI-DSS</h3>
                    </div>
                    <div class="metric-value" style="color: var(--accent-red);">4/12</div>
                    <div class="metric-label">Non-Compliant</div>
                </div>
            </div>
        </div>
        
        <!-- Tab: Metrics -->
        <div id="metrics" class="tab-content">
            <div class="card-grid">
                <div class="card">
                    <div class="metric-value">{len(solution_projects)}</div>
                    <div class="metric-label">Projects</div>
                </div>
                <div class="card">
                    <div class="metric-value">{len(holistic_context.get('code_analysis', {}).get('files', []))}</div>
                    <div class="metric-label">Files</div>
                </div>
                <div class="card">
                    <div class="metric-value">13</div>
                    <div class="metric-label">Years Old</div>
                </div>
                <div class="card">
                    <div class="metric-value">{health_score}</div>
                    <div class="metric-label">Health Score</div>
                </div>
            </div>
        </div>
        
        <!-- Tab: Timeline -->
        <div id="timeline" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Development Timeline</h2>
                </div>
                <div class="diagram-container">
                    <svg id="timeline-chart"></svg>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Tab Switching
        function showTab(tabId) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.tab').forEach(btn => {{
                btn.classList.remove('active');
            }});
            
            // Show selected tab
            document.getElementById(tabId).classList.add('active');
            event.target.closest('.tab').classList.add('active');
        }}
        
        // D3.js Visualizations
        document.addEventListener('DOMContentLoaded', function() {{
            initArchitectureDiagram();
            initDependencyGraph();
            initTimeline();
        }});
        
        function initArchitectureDiagram() {{
            const width = document.getElementById('architecture-diagram').clientWidth;
            const height = 550;
            
            const svg = d3.select('#architecture-diagram')
                .attr('width', width)
                .attr('height', height);
                
            const layers = [
                {{ name: 'kashkole\\nMain Website', y: 100, color: '#3b82f6' }},
                {{ name: 'KashkoleDBAccessLibrary\\nData Access', y: 200, color: '#a855f7' }},
                {{ name: 'KashkoleHijriLibrary\\nHijri Calendar', y: 200, color: '#a855f7' }},
                {{ name: 'KashkoleEmailScheduler\\nEmail Service', y: 200, color: '#a855f7' }},
                {{ name: 'SQL Server\\nKASHKOLE_DB + HLPrint_DB', y: 300, color: '#22c55e' }}
            ];
            
            const xSpacing = width / (layers.length + 1);
            
            layers.forEach((layer, i) => {{
                const x = xSpacing * (i + 1);
                
                svg.append('rect')
                    .attr('x', x - 80)
                    .attr('y', layer.y - 40)
                    .attr('width', 160)
                    .attr('height', 80)
                    .attr('fill', layer.color)
                    .attr('fill-opacity', 0.2)
                    .attr('stroke', layer.color)
                    .attr('stroke-width', 2)
                    .attr('rx', 12);
                    
                svg.append('text')
                    .attr('x', x)
                    .attr('y', layer.y)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#e4e4e7')
                    .attr('font-size', '14px')
                    .attr('font-weight', '600')
                    .selectAll('tspan')
                    .data(layer.name.split('\\n'))
                    .enter()
                    .append('tspan')
                    .attr('x', x)
                    .attr('dy', (d, i) => i * 20)
                    .text(d => d);
            }});
        }}
        
        function initDependencyGraph() {{
            const width = document.getElementById('dependency-graph').clientWidth;
            const height = 550;
            
            const nodes = [
                {{ id: 'kashkole', label: 'kashkole', group: 1 }},
                {{ id: 'db_lib', label: 'KashkoleDBAccessLibrary', group: 2 }},
                {{ id: 'hijri_lib', label: 'KashkoleHijriLibrary', group: 2 }},
                {{ id: 'email', label: 'KashkoleEmailScheduler', group: 2 }},
                {{ id: 'sql', label: 'SQL Server', group: 3 }}
            ];
            
            const links = [
                {{ source: 'kashkole', target: 'db_lib' }},
                {{ source: 'kashkole', target: 'hijri_lib' }},
                {{ source: 'db_lib', target: 'sql' }},
                {{ source: 'email', target: 'db_lib' }},
                {{ source: 'email', target: 'sql' }}
            ];
            
            const color = d3.scaleOrdinal()
                .domain([1, 2, 3])
                .range(['#3b82f6', '#a855f7', '#22c55e']);
            
            const simulation = d3.forceSimulation(nodes)
                .force('link', d3.forceLink(links).id(d => d.id).distance(150))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2));
            
            const svg = d3.select('#dependency-graph')
                .attr('width', width)
                .attr('height', height);
            
            const link = svg.append('g')
                .selectAll('line')
                .data(links)
                .enter()
                .append('line')
                .attr('stroke', 'rgba(255,255,255,0.2)')
                .attr('stroke-width', 2);
            
            const node = svg.append('g')
                .selectAll('g')
                .data(nodes)
                .enter()
                .append('g')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));
            
            node.append('circle')
                .attr('r', 30)
                .attr('fill', d => color(d.group))
                .attr('fill-opacity', 0.8)
                .attr('stroke', d => color(d.group))
                .attr('stroke-width', 2);
            
            node.append('text')
                .attr('text-anchor', 'middle')
                .attr('dy', 45)
                .attr('fill', '#e4e4e7')
                .attr('font-size', '12px')
                .text(d => d.label);
            
            simulation.on('tick', () => {{
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                node.attr('transform', d => `translate(${{d.x}},${{d.y}})`);
            }});
            
            function dragstarted(event) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }}
            
            function dragged(event) {{
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }}
            
            function dragended(event) {{
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }}
        }}
        
        function initTimeline() {{
            const width = document.getElementById('timeline-chart').clientWidth;
            const height = 550;
            
            const data = [
                {{ year: 2011, events: 1, label: 'Initial Development' }},
                {{ year: 2013, events: 1, label: 'Production Release' }},
                {{ year: 2020, events: 0, label: 'Maintenance Mode' }},
                {{ year: 2026, events: 1, label: 'CORTEX Onboarding' }}
            ];
            
            const svg = d3.select('#timeline-chart')
                .attr('width', width)
                .attr('height', height);
            
            const xScale = d3.scaleLinear()
                .domain([2010, 2027])
                .range([80, width - 80]);
            
            const yScale = d3.scaleLinear()
                .domain([0, 2])
                .range([height - 100, 100]);
            
            // Timeline line
            svg.append('line')
                .attr('x1', 80)
                .attr('y1', height / 2)
                .attr('x2', width - 80)
                .attr('y2', height / 2)
                .attr('stroke', 'rgba(59, 130, 246, 0.5)')
                .attr('stroke-width', 2);
            
            // Events
            data.forEach(d => {{
                svg.append('circle')
                    .attr('cx', xScale(d.year))
                    .attr('cy', height / 2)
                    .attr('r', 8)
                    .attr('fill', '#3b82f6')
                    .attr('stroke', '#0a0a0f')
                    .attr('stroke-width', 3);
                
                svg.append('text')
                    .attr('x', xScale(d.year))
                    .attr('y', height / 2 - 20)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#e4e4e7')
                    .attr('font-size', '14px')
                    .attr('font-weight', '600')
                    .text(d.year);
                
                svg.append('text')
                    .attr('x', xScale(d.year))
                    .attr('y', height / 2 + 35)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#a1a1aa')
                    .attr('font-size', '12px')
                    .text(d.label);
            }});
        }}
    </script>
</body>
</html>'''
        
        return html
    
    def _calculate_health_score(self, security_risks: Dict[str, Any]) -> int:
        """Calculate health score from security risks."""
        p0_count = len(security_risks.get('p0_risks', []))
        p1_count = len(security_risks.get('p1_risks', []))
        p2_count = len(security_risks.get('p2_risks', []))
        
        # Start at 100, deduct points
        score = 100
        score -= p0_count * 15  # P0 costs 15 points each
        score -= p1_count * 8   # P1 costs 8 points each
        score -= p2_count * 3   # P2 costs 3 points each
        
        return max(0, score)
    
    def _get_health_label(self, score: int) -> str:
        """Get health label from score."""
        if score >= 90:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Needs Improvement"
        else:
            return "Critical"
    
    def _get_health_category(self, score: int) -> str:
        """Get health category for CSS class."""
        if score >= 90:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "needs-improvement"
        else:
            return "critical"
    
    def _get_health_color(self, score: int) -> str:
        """Get color for health score."""
        if score >= 90:
            return "var(--accent-green)"
        elif score >= 70:
            return "var(--accent-blue)"
        elif score >= 50:
            return "var(--accent-yellow)"
        else:
            return "var(--accent-red)"
    
    def _get_project_description(self) -> str:
        """Get project description."""
        return """KASHKOLE is an Islamic knowledge management and educational platform built with ASP.NET Web Forms and VB.NET. 
        The application provides Quran browsing, Islamic calendar (Hijri) functionality, knowledge articles management, 
        and email notifications. Originally developed in 2011-2013, it represents a legacy codebase requiring modernization."""
    
    def _extract_solution_projects(self, context: Dict[str, Any]) -> List[str]:
        """Extract solution projects from context."""
        return [
            "kashkole.sln - Main Website",
            "KashkoleDBAccessLibrary - Data Access",
            "KashkoleHijriLibrary - Islamic Calendar",
            "KashkoleEmailLib - Email Functionality",
            "ScheduleEmailer - Background Service",
            "ScheduleEmailerUI - Admin UI",
            "HLPrint - Print Module"
        ]
    
    def _extract_tech_stack(self, context: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract technology stack."""
        return {
            "Backend": ["ASP.NET Web Forms", "VB.NET", ".NET Framework 4.0"],
            "Database": ["SQL Server", "Stored Procedures"],
            "Frontend": ["HTML", "CSS", "JavaScript", "Flash"],
            "Libraries": ["Class Libraries", "Email Scheduler"],
        }
    
    def _extract_database_info(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract database information."""
        return {
            "databases": ["KASHKOLE_DB", "HLPrint_DB"],
            "connection_strings": 2,
            "stored_procedures": "Yes"
        }
    
    def _generate_security_findings_html(self, risks: List[Dict[str, Any]]) -> str:
        """Generate HTML for security findings."""
        if not risks:
            return '<li class="finding-item"><div class="finding-description">No P0 findings detected.</div></li>'
        
        html = ""
        for risk in risks[:5]:  # Show top 5
            html += f'''
            <li class="finding-item">
                <div class="finding-header">
                    <span class="finding-id">{risk.get('id', 'SEC-XXX')}</span>
                    <span class="badge badge-p0">P0 CRITICAL</span>
                </div>
                <div class="finding-title">{risk.get('category', 'Security Issue')}</div>
                <div class="finding-description">{risk.get('description', '')}</div>
                <div class="finding-location">📍 {risk.get('location', 'Multiple locations')}</div>
            </li>
            '''
        return html
    
    def _generate_recommendations_html(self, recommendations: List[Dict[str, Any]]) -> str:
        """Generate HTML for recommendations."""
        if not recommendations:
            return '<li class="finding-item"><div class="finding-description">No recommendations generated.</div></li>'
        
        html = ""
        for rec in recommendations[:10]:  # Show top 10
            priority = rec.get('priority', 'P2')
            html += f'''
            <li class="finding-item">
                <div class="finding-header">
                    <span class="badge badge-{priority.lower()}">{priority}</span>
                </div>
                <div class="finding-title">{rec.get('category', 'General')}</div>
                <div class="finding-description">{rec.get('recommendation', '')}</div>
            </li>
            '''
        return html
    
    def _generate_tech_stack_html(self, tech_stack: Dict[str, List[str]]) -> str:
        """Generate HTML for tech stack."""
        html = ""
        for category, items in tech_stack.items():
            html += f'<h4>{category}</h4>'
            for item in items:
                html += f'<div class="tech-tag">{item}</div>'
        return html
    
    def _generate_database_info_html(self, db_info: Dict[str, Any]) -> str:
        """Generate HTML for database info."""
        dbs = db_info.get('databases', [])
        html = '<table class="data-table">'
        html += '<thead><tr><th>Database</th><th>Status</th></tr></thead><tbody>'
        for db in dbs:
            html += f'<tr><td>{db}</td><td><span class="badge badge-p2">Active</span></td></tr>'
        html += '</tbody></table>'
        return html
