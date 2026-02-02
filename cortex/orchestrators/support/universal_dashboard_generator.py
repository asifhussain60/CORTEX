"""
Universal Domain Dashboard Generator.

Generates comprehensive, data-driven glassmorphism dashboards for any repository
with confidence scoring, collapsible references, and rich visualizations.

Authority: cortex-architect.prompt.md v8.0
Author: Asif Hussain
AC-ID: AC-UNIVERSAL-ONBOARD-004
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import html as html_module
import logging

logger = logging.getLogger(__name__)


class UniversalDashboardGenerator:
    """
    Generate comprehensive dashboards for any onboarded repository.
    
    Features:
    - Data-driven (no hardcoded content)
    - Confidence scoring with evidence
    - Collapsible file references
    - Rich use case cards
    - Industry-standard metrics
    - Glassmorphism dark theme
    
    Example:
        >>> generator = UniversalDashboardGenerator()
        >>> path = generator.generate_dashboard(
        ...     repo_name="kashkole",
        ...     narrative=business_narrative,
        ...     analysis_data=onboarding_data
        ... )
    """
    
    def __init__(self, dashboards_root: Optional[Path] = None):
        """
        Initialize Universal Dashboard Generator.
        
        Args:
            dashboards_root: Root path for dashboards output
        """
        cortex_root = Path(__file__).parent.parent.parent.parent
        self.dashboards_root = dashboards_root or cortex_root / "company" / "dashboards"
        logger.info(f"UniversalDashboardGenerator initialized. Dashboards root: {self.dashboards_root}")
    
    def generate_dashboard(
        self,
        repo_name: str,
        narrative: Any,  # BusinessNarrative
        analysis_data: Dict[str, Any],
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Generate dashboard by injecting data into HTML template.
        
        Approach: Embed all JSON data directly in the HTML file via window.dashboardData
        This eliminates need for HTTP server or fetch() calls.
        
        Args:
            repo_name: Repository identifier
            narrative: BusinessNarrative with use cases and confidence
            analysis_data: Full onboarding analysis data
            output_path: Optional custom output path
            
        Returns:
            Path to generated dashboard HTML
        """
        if output_path is None:
            output_path = self.dashboards_root / repo_name / "dashboard.html"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build all JSON data objects
        logger.info(f"🔵 Generating dashboard for {repo_name}...")
        
        # Extract metrics
        security = analysis_data.get('security_risks', {})
        p0_count = len(security.get('p0_risks', []))
        p1_count = len(security.get('p1_risks', []))
        p2_count = len(security.get('p2_risks', []))
        health_score = self._calculate_health_score(p0_count, p1_count, p2_count)
        
        # Build embedded JSON data
        overview_data = self._build_overview_json_object(narrative, p0_count, p1_count, p2_count, health_score, analysis_data.get('timestamp', datetime.now().isoformat()), analysis_data.get('repo_path', ''))
        security_data = self._build_security_json_object(security)
        tech_stack_data = self._build_tech_stack_json_object(narrative)
        
        # Generate HTML with embedded data
        html_content = self._generate_html_with_embedded_data(
            repo_name, 
            narrative, 
            overview_data, 
            security_data, 
            tech_stack_data
        )
        
        # Write to file
        output_path.write_text(html_content, encoding='utf-8')
        logger.info(f"✅ Generated dashboard: {output_path}")
        
        return output_path
    
    def _generate_overview_json(
        self,
        narrative: Any,
        analysis_data: Dict[str, Any],
        data_dir: Path
    ) -> None:
        """Generate overview.json with business narrative and metrics."""
        security = analysis_data.get('security_risks', {})
        context = analysis_data.get('holistic_context', {})
        timestamp = analysis_data.get('timestamp', datetime.now().isoformat())
        repo_path = analysis_data.get('repo_path', '')
        
        # Calculate health score
        p0_count = len(security.get('p0_risks', []))
        p1_count = len(security.get('p1_risks', []))
        p2_count = len(security.get('p2_risks', []))
        health_score = self._calculate_health_score(p0_count, p1_count, p2_count)
        health_label = self._get_health_label(health_score)
        
        # Extract file counts
        code_analysis = context.get('code_analysis', {})
        files = code_analysis.get('files', [])
        
        overview_data = {
            "metadata": {
                "generated_at": timestamp,
                "cortex_version": "8.0",
                "repo_name": narrative.name,
                "repo_path": repo_path
            },
            "health": {
                "score": health_score,
                "label": health_label,
                "category": health_label.lower().replace(' ', '-')
            },
            "metrics": {
                "technologies_detected": len(narrative.tech_stack),
                "use_cases_identified": len(narrative.use_cases),
                "security_findings": p0_count + p1_count + p2_count,
                "source_files": len(files)
            },
            "project": {
                "name": narrative.title,
                "tagline": narrative.tagline,
                "description": narrative.description,
                "architecture_summary": narrative.architecture_summary,
                "target_users": narrative.target_users,
                "confidence": {
                    "score": narrative.confidence.score,
                    "level": narrative.confidence.level,
                    "evidence": narrative.confidence.evidence,
                    "assumptions": narrative.confidence.assumptions
                }
            },
            "use_cases": [
                {
                    "title": uc.title,
                    "description": uc.description,
                    "icon": uc.icon,
                    "actors": uc.actors,
                    "confidence": {
                        "score": uc.confidence.score,
                        "level": uc.confidence.level
                    },
                    "evidence_files": uc.evidence_files[:5],
                    "evidence_file_count": len(uc.evidence_files)
                }
                for uc in narrative.use_cases
            ],
            "tech_stack": [
                {
                    "name": tech["name"],
                    "icon": tech["icon"],
                    "category": tech["category"],
                    "confidence": tech.get("confidence", "high"),
                    "evidence_files": tech.get("evidence_files", [])[:3]
                }
                for tech in narrative.tech_stack
            ]
        }
        
        # Save JSON
        overview_file = data_dir / "overview.json"
        with open(overview_file, 'w', encoding='utf-8') as f:
            json.dump(overview_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Generated overview.json with {len(narrative.use_cases)} use cases")
    
    def _generate_security_json(
        self,
        analysis_data: Dict[str, Any],
        data_dir: Path
    ) -> None:
        """Generate security.json with detailed findings."""
        security = analysis_data.get('security_risks', {})
        
        security_data = {
            "summary": {
                "p0_count": len(security.get('p0_risks', [])),
                "p1_count": len(security.get('p1_risks', [])),
                "p2_count": len(security.get('p2_risks', [])),
                "total_findings": sum([
                    len(security.get('p0_risks', [])),
                    len(security.get('p1_risks', [])),
                    len(security.get('p2_risks', []))
                ])
            },
            "findings": {
                "p0_risks": security.get('p0_risks', []),
                "p1_risks": security.get('p1_risks', []),
                "p2_risks": security.get('p2_risks', [])
            }
        }
        
        # Save JSON
        security_file = data_dir / "security.json"
        with open(security_file, 'w', encoding='utf-8') as f:
            json.dump(security_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Generated security.json with {security_data['summary']['total_findings']} findings")
    
    def _generate_tech_stack_json(
        self,
        narrative: Any,
        data_dir: Path
    ) -> None:
        """Generate tech_stack.json with technology analysis."""
        # Group technologies by category
        tech_by_category = {}
        for tech in narrative.tech_stack:
            category = tech["category"]
            if category not in tech_by_category:
                tech_by_category[category] = []
            tech_by_category[category].append(tech)
        
        tech_stack_data = {
            "technologies": narrative.tech_stack,
            "by_category": tech_by_category,
            "summary": {
                "total_technologies": len(narrative.tech_stack),
                "categories": list(tech_by_category.keys()),
                "high_confidence_count": len([t for t in narrative.tech_stack if t.get("confidence") == "high"])
            }
        }
        
        # Save JSON
        tech_file = data_dir / "tech_stack.json"
        with open(tech_file, 'w', encoding='utf-8') as f:
            json.dump(tech_stack_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Generated tech_stack.json with {len(narrative.tech_stack)} technologies")
    
    def _calculate_health_score(self, p0: int, p1: int, p2: int) -> int:
        """Calculate health score from security findings."""
        score = 100
        score -= p0 * 15
        score -= p1 * 8
        score -= p2 * 3
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
    
    def _generate_html_with_embedded_data(
        self,
        repo_name: str,
        narrative: Any,
        overview_data: Dict[str, Any],
        security_data: Dict[str, Any],
        tech_stack_data: Dict[str, Any]
    ) -> str:
        """
        Generate HTML with embedded JSON data.
        
        Injects data into window.dashboardData so it's available to JavaScript
        without needing fetch() or HTTP server.
        """
        # Convert data to JSON strings (properly escaped for JS)
        overview_json = json.dumps(overview_data, ensure_ascii=False, default=str)
        security_json = json.dumps(security_data, ensure_ascii=False, default=str)
        tech_stack_json = json.dumps(tech_stack_data, ensure_ascii=False, default=str)
        
        # Get template
        template_path = self.dashboards_root / repo_name / "dashboard.html"
        if not template_path.exists():
            logger.error(f"Dashboard template not found at {template_path}")
            return ""
        
        with open(template_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Replace the placeholder data section
        data_injection = f"""    <script>
        window.dashboardData = {{
            overview: {overview_json},
            security: {security_json},
            tech_stack: {tech_stack_json}
        }};
    </script>"""
        
        # Find and replace the embedded data section
        html = html.replace(
            "    <!-- Embedded Dashboard Data -->",
            ""
        )
        html = html.replace(
            """    <script>
        window.dashboardData = {""",
            data_injection.split('{')[0]
        )
        
        # Or just find the last <script> tag and replace the window.dashboardData definition
        # Better approach: use a regex or find the specific section
        import re
        pattern = r'window\.dashboardData = \{[^}]*\};'
        html = re.sub(pattern, "", html, flags=re.DOTALL)
        
        # Insert the data before the closing </body> tag
        html = html.replace(
            "</body>",
            data_injection + "\n</body>"
        )
        
        return html
    
    def _generate_complete_html(
        self,
        repo_name: str,
        narrative: Any,
        data: Dict[str, Any],
    ) -> str:
        """Generate complete HTML dashboard with embedded JSON data."""
        
        # Extract data
        security = data.get('security_risks', {})
        context = data.get('holistic_context', {})
        recommendations = data.get('recommendations', [])
        timestamp = data.get('timestamp', datetime.now().isoformat())
        repo_path = data.get('repo_path', '')
        
        # Calculate metrics
        p0_count = len(security.get('p0_risks', []))
        p1_count = len(security.get('p1_risks', []))
        p2_count = len(security.get('p2_risks', []))
        health_score = self._calculate_health_score(p0_count, p1_count, p2_count)
        health_category = self._get_health_category(health_score)
        
        # Get narrative data
        title = getattr(narrative, 'title', repo_name.upper())
        tagline = getattr(narrative, 'tagline', 'Software Application')
        description = getattr(narrative, 'description', 'No description available')
        use_cases = getattr(narrative, 'use_cases', [])
        tech_stack = getattr(narrative, 'tech_stack', [])
        overall_confidence = getattr(narrative, 'confidence', None)
        evidence_map = getattr(narrative, 'evidence_map', {})
        target_users = getattr(narrative, 'target_users', [])
        arch_summary = getattr(narrative, 'architecture_summary', '')
        
        # Get dependency analysis data (from holistic_context which contains lens results)
        dependency_analysis = context.get('dependency_analysis', {})
        
        # PHASE 3: Generate embedded JSON data for inline usage
        overview_data = self._build_overview_json_object(narrative, p0_count, p1_count, p2_count, health_score, timestamp, repo_path)
        security_data = self._build_security_json_object(security)
        tech_stack_data = self._build_tech_stack_json_object(narrative)
        
        # Convert to JSON strings for embedding in HTML
        overview_json_str = json.dumps(overview_data, ensure_ascii=False)
        security_json_str = json.dumps(security_data, ensure_ascii=False)
        tech_stack_json_str = json.dumps(tech_stack_data, ensure_ascii=False)
        
        # Format date
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_date = dt.strftime('%B %d, %Y')
        except (ValueError, AttributeError, TypeError) as e:
            logger.debug(f"Failed to parse timestamp '{timestamp}': {e}")
            formatted_date = timestamp[:10] if len(timestamp) >= 10 else timestamp
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{self._escape(tagline)} - CORTEX Security Analysis">
    <title>{self._escape(title)} - CORTEX Dashboard</title>
    
    <link rel="icon" type="image/png" href="../assets/images/CORTEX-logo-64.png">
    <link rel="stylesheet" href="../assets/css/dashboard-combined.css">
    
    <script src="https://d3js.org/d3.v7.min.js"></script>
    
    <style>
        /* Additional dashboard styles */
        .confidence-indicator {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: rgba(26, 31, 58, 0.6);
            border-radius: 8px;
            font-size: 0.875rem;
        }}
        
        .confidence-bar {{
            width: 100px;
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .confidence-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }}
        
        .confidence-fill.high {{ background: linear-gradient(90deg, #22c55e, #10b981); }}
        .confidence-fill.medium {{ background: linear-gradient(90deg, #eab308, #f59e0b); }}
        .confidence-fill.low {{ background: linear-gradient(90deg, #ef4444, #dc2626); }}
        
        .evidence-tag {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            background: rgba(34, 197, 94, 0.15);
            border: 1px solid rgba(34, 197, 94, 0.3);
            border-radius: 4px;
            font-size: 0.75rem;
            color: #22c55e;
            margin-right: 0.25rem;
            margin-bottom: 0.25rem;
        }}
        
        .assumption-tag {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 4px;
            font-size: 0.75rem;
            color: #ef4444;
            margin-right: 0.25rem;
            margin-bottom: 0.25rem;
        }}
        
        .back-link {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            transition: color 0.2s ease;
        }}
        
        .back-link:hover {{
            color: #00d4ff;
        }}
        
        .section-title {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        
        .section-title::after {{
            content: '';
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, rgba(255,255,255,0.2) 0%, transparent 100%);
        }}
        
        .health-ring-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem;
        }}
        
        .health-ring {{
            position: relative;
            width: 150px;
            height: 150px;
        }}
        
        .health-ring svg {{
            transform: rotate(-90deg);
            width: 150px;
            height: 150px;
        }}
        
        .health-ring .ring-bg {{
            fill: none;
            stroke: rgba(255, 255, 255, 0.1);
            stroke-width: 12;
        }}
        
        .health-ring .ring-progress {{
            fill: none;
            stroke-width: 12;
            stroke-linecap: round;
            transition: stroke-dashoffset 1s ease;
        }}
        
        .health-ring .ring-progress.critical {{ stroke: url(#gradientCritical); }}
        .health-ring .ring-progress.warning {{ stroke: url(#gradientWarning); }}
        .health-ring .ring-progress.good {{ stroke: url(#gradientGood); }}
        .health-ring .ring-progress.excellent {{ stroke: url(#gradientExcellent); }}
        
        .health-text {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }}
        
        .health-value {{
            font-size: 2.5rem;
            font-weight: 700;
            line-height: 1;
        }}
        
        .health-label {{
            font-size: 0.875rem;
            color: rgba(255, 255, 255, 0.6);
            margin-top: 0.25rem;
        }}
        
        .file-link {{
            font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
            font-size: 0.8rem;
            color: #00d4ff;
            text-decoration: none;
            padding: 0.25rem 0.5rem;
            background: rgba(0, 212, 255, 0.1);
            border-radius: 4px;
            display: inline-block;
            margin: 0.125rem;
            transition: all 0.2s ease;
        }}
        
        .file-link:hover {{
            background: rgba(0, 212, 255, 0.2);
            transform: translateX(2px);
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- Back to Hub -->
        <a href="../index.html" class="back-link">
            <span>←</span>
            <span>Back to Dashboard Hub</span>
        </a>
        
        <!-- Header -->
        <header class="dashboard-header">
            <img src="../assets/images/CORTEX-logo-128.png" 
                 alt="CORTEX Logo" 
                 class="dashboard-logo"
                 width="80" 
                 height="80">
            <div>
                <h1 class="dashboard-title">{self._escape(title)}</h1>
                <p class="dashboard-subtitle">{self._escape(tagline)}</p>
                <div style="display: flex; gap: 1.5rem; margin-top: 1rem; flex-wrap: wrap;">
                    <span style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">
                        📅 Onboarded: {formatted_date}
                    </span>
                    <span style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">
                        🧠 CORTEX v8.0
                    </span>
                    {self._generate_confidence_indicator(overall_confidence)}
                </div>
            </div>
        </header>
        
        <!-- Tabs Navigation -->
        <nav class="tabs-container" role="tablist" aria-label="Dashboard sections">
            <button class="tab-button active" data-tab="overview" role="tab" aria-selected="true">
                <span class="tab-icon">📊</span> Overview
            </button>
            <button class="tab-button" data-tab="security" role="tab" aria-selected="false">
                <span class="tab-icon">🔒</span> Security
            </button>
            <button class="tab-button" data-tab="architecture" role="tab" aria-selected="false">
                <span class="tab-icon">🏗️</span> Architecture
            </button>
            <button class="tab-button" data-tab="tech-stack" role="tab" aria-selected="false">
                <span class="tab-icon">💻</span> Tech Stack
            </button>
            <button class="tab-button" data-tab="database" role="tab" aria-selected="false">
                <span class="tab-icon">💾</span> Database
            </button>
            <button class="tab-button" data-tab="recommendations" role="tab" aria-selected="false">
                <span class="tab-icon">💡</span> Recommendations
            </button>
            <button class="tab-button" data-tab="modernization" role="tab" aria-selected="false">
                <span class="tab-icon">🚀</span> Modernization
            </button>
            <button class="tab-button" data-tab="compliance" role="tab" aria-selected="false">
                <span class="tab-icon">✅</span> Compliance
            </button>
            <button class="tab-button" data-tab="metrics" role="tab" aria-selected="false">
                <span class="tab-icon">📈</span> Metrics
            </button>
            <button class="tab-button" data-tab="timeline" role="tab" aria-selected="false">
                <span class="tab-icon">⏱️</span> Timeline
            </button>
        </nav>
        
        <!-- Tab: Overview -->
        <section id="tab-overview" class="tab-content active" role="tabpanel">
            <!-- Health Summary Row -->
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="health-ring-container">
                        <div class="health-ring">
                            <svg viewBox="0 0 150 150">
                                <defs>
                                    <linearGradient id="gradientCritical" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stop-color="#ef4444"/>
                                        <stop offset="100%" stop-color="#dc2626"/>
                                    </linearGradient>
                                    <linearGradient id="gradientWarning" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stop-color="#eab308"/>
                                        <stop offset="100%" stop-color="#f59e0b"/>
                                    </linearGradient>
                                    <linearGradient id="gradientGood" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stop-color="#3b82f6"/>
                                        <stop offset="100%" stop-color="#6366f1"/>
                                    </linearGradient>
                                    <linearGradient id="gradientExcellent" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stop-color="#22c55e"/>
                                        <stop offset="100%" stop-color="#10b981"/>
                                    </linearGradient>
                                </defs>
                                <circle class="ring-bg" cx="75" cy="75" r="60"/>
                                <circle class="ring-progress {health_category}" cx="75" cy="75" r="60"
                                        stroke-dasharray="377"
                                        stroke-dashoffset="{377 - (377 * health_score / 100)}"/>
                            </svg>
                            <div class="health-text">
                                <div class="health-value">{health_score}</div>
                                <div class="health-label">Health Score</div>
                            </div>
                        </div>
                        <span class="confidence-badge {health_category}" style="margin-top: 1rem;">
                            {self._get_health_label(health_score)}
                        </span>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{len(tech_stack)}</div>
                    <div class="metric-label">Technologies Detected</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{len(use_cases)}</div>
                    <div class="metric-label">Use Cases Identified</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{p0_count + p1_count + p2_count}</div>
                    <div class="metric-label">Security Findings</div>
                </div>
            </div>
            
            <!-- Project Description -->
            <div class="collapsible" style="margin-bottom: 2rem;">
                <div class="collapsible-header active" onclick="toggleCollapsible(this)">
                    <h2 class="section-title" style="margin: 0;">📋 Project Description</h2>
                    <span class="collapsible-icon">▼</span>
                </div>
                <div class="collapsible-content active">
                    <p style="font-size: 1.1rem; line-height: 1.8; color: rgba(255,255,255,0.9);">
                        {self._escape(description)}
                    </p>
                    {self._generate_confidence_details(overall_confidence)}
                </div>
            </div>
            
            <!-- Primary Use Cases -->
            <h2 class="section-title">🎯 Primary Use Cases</h2>
            <div class="use-case-grid">
                {self._generate_use_cases_html(use_cases)}
            </div>
            
            <!-- Target Users -->
            {self._generate_target_users_html(target_users)}
        </section>
        
        <!-- Tab: Security -->
        <section id="tab-security" class="tab-content" role="tabpanel">
            <h2 class="section-title">🔒 Security Summary</h2>
            
            <div class="metrics-grid">
                <div class="metric-card" style="border-left: 4px solid #ef4444;">
                    <div class="security-badge p0" style="margin-bottom: 1rem;">P0 CRITICAL</div>
                    <div class="metric-value" style="color: #ef4444;">{p0_count}</div>
                    <div class="metric-label">Critical issues requiring immediate attention</div>
                </div>
                <div class="metric-card" style="border-left: 4px solid #eab308;">
                    <div class="security-badge p1" style="margin-bottom: 1rem;">P1 HIGH</div>
                    <div class="metric-value" style="color: #eab308;">{p1_count}</div>
                    <div class="metric-label">High priority security concerns</div>
                </div>
                <div class="metric-card" style="border-left: 4px solid #3b82f6;">
                    <div class="security-badge p2" style="margin-bottom: 1rem;">P2 MEDIUM</div>
                    <div class="metric-value" style="color: #3b82f6;">{p2_count}</div>
                    <div class="metric-label">Medium priority improvements</div>
                </div>
            </div>
            
            {self._generate_security_findings_html(security)}
        </section>
        
        <!-- Tab: Architecture -->
        <section id="tab-architecture" class="tab-content" role="tabpanel">
            <h2 class="section-title">🏗️ Architecture Overview</h2>
            
            <div class="collapsible" style="margin-bottom: 2rem;">
                <div class="collapsible-header active" onclick="toggleCollapsible(this)">
                    <span>Architecture Summary</span>
                    <span class="collapsible-icon">▼</span>
                </div>
                <div class="collapsible-content active">
                    <p style="font-size: 1.1rem; line-height: 1.8;">
                        {self._escape(arch_summary) if arch_summary else 'Architecture analysis pending deeper code review.'}
                    </p>
                </div>
            </div>
            
            <div style="background: rgba(26, 31, 58, 0.6); border-radius: 16px; padding: 2rem; min-height: 400px;">
                <div id="architecture-diagram" style="width: 100%; height: 400px;"></div>
            </div>
        </section>
        
        <!-- Tab: Tech Stack -->
        <section id="tab-tech-stack" class="tab-content" role="tabpanel">
            <h2 class="section-title">💻 Technology Stack</h2>
            {self._generate_tech_stack_html(tech_stack, evidence_map)}
            
            <h2 class="section-title" style="margin-top: 3rem;">📦 Dependencies & Vulnerabilities</h2>
            {self._generate_dependencies_html(dependency_analysis)}
        </section>
        
        <!-- Tab: Database -->
        <section id="tab-database" class="tab-content" role="tabpanel">
            <h2 class="section-title">💾 Database Analysis</h2>
            {self._generate_database_html(context.get('database_analysis', {}))}
        </section>
        
        <!-- Tab: Recommendations -->
        <section id="tab-recommendations" class="tab-content" role="tabpanel">
            <h2 class="section-title">💡 Prioritized Recommendations</h2>
            {self._generate_recommendations_html(recommendations)}
        </section>
        
        <!-- Tab: Modernization -->
        <section id="tab-modernization" class="tab-content" role="tabpanel">
            <h2 class="section-title">🚀 Modernization Roadmap</h2>
            {self._generate_modernization_html(security, tech_stack)}
        </section>
        
        <!-- Tab: Compliance -->
        <section id="tab-compliance" class="tab-content" role="tabpanel">
            <h2 class="section-title">✅ Compliance Status</h2>
            {self._generate_compliance_html(security)}
        </section>
        
        <!-- Tab: Metrics -->
        <section id="tab-metrics" class="tab-content" role="tabpanel">
            <h2 class="section-title">📈 Code Metrics</h2>
            {self._generate_metrics_html(context)}
        </section>
        
        <!-- Tab: Timeline -->
        <section id="tab-timeline" class="tab-content" role="tabpanel">
            <h2 class="section-title">⏱️ Development Timeline</h2>
            <div style="background: rgba(26, 31, 58, 0.6); border-radius: 16px; padding: 2rem; min-height: 300px;">
                <div id="timeline-chart" style="width: 100%; height: 300px;"></div>
            </div>
        </section>
        
        <!-- Footer -->
        <footer style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.5); margin-top: 3rem;">
            <p>Generated by CORTEX v8.0 • {formatted_date}</p>
            <p style="font-size: 0.8rem; margin-top: 0.5rem;">
                Analysis confidence may vary. Review evidence and assumptions for accuracy.
            </p>
        </footer>
    </div>
    
    <script>
        // Tab switching
        document.querySelectorAll('.tab-button').forEach(button => {{
            button.addEventListener('click', () => {{
                // Update buttons
                document.querySelectorAll('.tab-button').forEach(b => {{
                    b.classList.remove('active');
                    b.setAttribute('aria-selected', 'false');
                }});
                button.classList.add('active');
                button.setAttribute('aria-selected', 'true');
                
                // Update content
                document.querySelectorAll('.tab-content').forEach(content => {{
                    content.classList.remove('active');
                }});
                const tabId = 'tab-' + button.dataset.tab;
                document.getElementById(tabId).classList.add('active');
            }});
        }});
        
        // Collapsible sections
        function toggleCollapsible(header) {{
            header.classList.toggle('active');
            const content = header.nextElementSibling;
            content.classList.toggle('active');
        }}
        
        // D3.js visualizations
        document.addEventListener('DOMContentLoaded', function() {{
            initArchitectureDiagram();
            initTimelineChart();
        }});
        
        function initArchitectureDiagram() {{
            const container = document.getElementById('architecture-diagram');
            if (!container) return;
            
            const width = container.clientWidth;
            const height = 400;
            
            const svg = d3.select('#architecture-diagram')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            // Simple architecture layers
            const layers = {self._get_architecture_layers_json(tech_stack)};
            
            if (layers.length === 0) {{
                svg.append('text')
                    .attr('x', width / 2)
                    .attr('y', height / 2)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#a1a1aa')
                    .text('Architecture visualization requires deeper analysis');
                return;
            }}
            
            const layerHeight = 60;
            const layerGap = 40;
            const startY = (height - (layers.length * layerHeight + (layers.length - 1) * layerGap)) / 2;
            
            layers.forEach((layer, i) => {{
                const y = startY + i * (layerHeight + layerGap);
                
                // Layer box
                svg.append('rect')
                    .attr('x', 100)
                    .attr('y', y)
                    .attr('width', width - 200)
                    .attr('height', layerHeight)
                    .attr('rx', 12)
                    .attr('fill', layer.color)
                    .attr('fill-opacity', 0.2)
                    .attr('stroke', layer.color)
                    .attr('stroke-width', 2);
                
                // Layer text
                svg.append('text')
                    .attr('x', width / 2)
                    .attr('y', y + layerHeight / 2 + 5)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#e4e4e7')
                    .attr('font-size', '14px')
                    .attr('font-weight', '600')
                    .text(layer.name);
                
                // Arrow to next layer
                if (i < layers.length - 1) {{
                    svg.append('path')
                        .attr('d', `M${{width/2}},${{y + layerHeight}} L${{width/2}},${{y + layerHeight + layerGap - 5}}`)
                        .attr('stroke', 'rgba(255,255,255,0.3)')
                        .attr('stroke-width', 2)
                        .attr('marker-end', 'url(#arrowhead)');
                }}
            }});
            
            // Arrow marker
            svg.append('defs').append('marker')
                .attr('id', 'arrowhead')
                .attr('markerWidth', 10)
                .attr('markerHeight', 7)
                .attr('refX', 9)
                .attr('refY', 3.5)
                .attr('orient', 'auto')
                .append('polygon')
                .attr('points', '0 0, 10 3.5, 0 7')
                .attr('fill', 'rgba(255,255,255,0.3)');
        }}
        
        function initTimelineChart() {{
            const container = document.getElementById('timeline-chart');
            if (!container) return;
            
            const width = container.clientWidth;
            const height = 300;
            
            const svg = d3.select('#timeline-chart')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            // Timeline line
            svg.append('line')
                .attr('x1', 50)
                .attr('y1', height / 2)
                .attr('x2', width - 50)
                .attr('y2', height / 2)
                .attr('stroke', 'rgba(59, 130, 246, 0.5)')
                .attr('stroke-width', 3);
            
            // Events
            const events = [
                {{ x: 100, label: 'Initial Dev', year: '?' }},
                {{ x: width / 2, label: 'Production', year: '?' }},
                {{ x: width - 100, label: 'CORTEX Analysis', year: '{datetime.now().year}' }}
            ];
            
            events.forEach(event => {{
                svg.append('circle')
                    .attr('cx', event.x)
                    .attr('cy', height / 2)
                    .attr('r', 10)
                    .attr('fill', '#3b82f6')
                    .attr('stroke', '#0a0a0f')
                    .attr('stroke-width', 3);
                
                svg.append('text')
                    .attr('x', event.x)
                    .attr('y', height / 2 - 25)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#e4e4e7')
                    .attr('font-size', '12px')
                    .text(event.label);
                
                svg.append('text')
                    .attr('x', event.x)
                    .attr('y', height / 2 + 35)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#a1a1aa')
                    .attr('font-size', '11px')
                    .text(event.year);
            }});
        }}
    </script>
</body>
</html>'''
    
    def _escape(self, text: str) -> str:
        """Escape HTML special characters."""
        return html_module.escape(str(text)) if text else ''
    
    def _calculate_health_score(self, p0: int, p1: int, p2: int) -> int:
        """Calculate health score."""
        score = 100
        score -= p0 * 15
        score -= p1 * 8
        score -= p2 * 3
        return max(0, min(100, score))
    
    def _get_health_category(self, score: int) -> str:
        """Get health category CSS class from score."""
        if score >= 90:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "warning"
        else:
            return "critical"
    
    def _build_overview_json_object(self, narrative, p0_count, p1_count, p2_count, health_score, timestamp, repo_path):
        """Build overview JSON object for embedding."""
        files = narrative.evidence_map if hasattr(narrative, 'evidence_map') else {}
        
        return {
            "metadata": {
                "generated_at": timestamp,
                "cortex_version": "8.0",
                "repo_name": narrative.name,
                "repo_path": repo_path
            },
            "health": {
                "score": health_score,
                "label": self._get_health_label(health_score),
                "category": self._get_health_category(health_score)
            },
            "metrics": {
                "technologies_detected": len(narrative.tech_stack),
                "use_cases_identified": len(narrative.use_cases),
                "security_findings": p0_count + p1_count + p2_count,
                "source_files": len(files)
            },
            "project": {
                "name": narrative.title,
                "tagline": narrative.tagline,
                "description": narrative.description,
                "architecture_summary": narrative.architecture_summary,
                "target_users": narrative.target_users,
                "confidence": {
                    "score": narrative.confidence.score,
                    "level": narrative.confidence.level,
                    "evidence": narrative.confidence.evidence,
                    "assumptions": narrative.confidence.assumptions
                }
            },
            "use_cases": [
                {
                    "title": uc.title,
                    "description": uc.description,
                    "icon": uc.icon,
                    "actors": uc.actors,
                    "confidence": {
                        "score": uc.confidence.score,
                        "level": uc.confidence.level
                    },
                    "evidence_files": uc.evidence_files[:5],
                    "evidence_file_count": len(uc.evidence_files)
                }
                for uc in narrative.use_cases
            ],
            "tech_stack": [
                {
                    "name": tech["name"],
                    "icon": tech["icon"],
                    "category": tech["category"],
                    "confidence": tech.get("confidence", "high"),
                    "evidence_files": tech.get("evidence_files", [])[:3]
                }
                for tech in narrative.tech_stack
            ]
        }
    
    def _build_security_json_object(self, security):
        """Build security JSON object for embedding."""
        return {
            "summary": {
                "p0_count": len(security.get('p0_risks', [])),
                "p1_count": len(security.get('p1_risks', [])),
                "p2_count": len(security.get('p2_risks', [])),
                "total_findings": sum([
                    len(security.get('p0_risks', [])),
                    len(security.get('p1_risks', [])),
                    len(security.get('p2_risks', []))
                ])
            },
            "findings": {
                "p0_risks": security.get('p0_risks', []),
                "p1_risks": security.get('p1_risks', []),
                "p2_risks": security.get('p2_risks', [])
            }
        }
    
    def _build_tech_stack_json_object(self, narrative):
        """Build tech stack JSON object for embedding."""
        tech_by_category = {}
        for tech in narrative.tech_stack:
            category = tech["category"]
            if category not in tech_by_category:
                tech_by_category[category] = []
            tech_by_category[category].append(tech)
        
        return {
            "technologies": narrative.tech_stack,
            "by_category": tech_by_category,
            "summary": {
                "total_technologies": len(narrative.tech_stack),
                "categories": list(tech_by_category.keys()),
                "high_confidence_count": len([t for t in narrative.tech_stack if t.get("confidence") == "high"])
            }
        }
    
    def _get_health_category(self, score: int) -> str:
        """Get health category."""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "warning"
        return "critical"
    
    def _get_health_label(self, score: int) -> str:
        """Get health label."""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Needs Improvement"
        return "Critical"
    
    def _generate_confidence_indicator(self, confidence) -> str:
        """Generate confidence indicator HTML."""
        if not confidence:
            return ''
        
        score = getattr(confidence, 'score', 0)
        level = getattr(confidence, 'level', 'low')
        
        return f'''
            <div class="confidence-indicator">
                <span>Confidence:</span>
                <div class="confidence-bar">
                    <div class="confidence-fill {level}" style="width: {score}%;"></div>
                </div>
                <span class="confidence-badge {level}">{score}%</span>
            </div>
        '''
    
    def _generate_confidence_details(self, confidence) -> str:
        """Generate confidence details HTML."""
        if not confidence:
            return ''
        
        evidence = getattr(confidence, 'evidence', [])
        assumptions = getattr(confidence, 'assumptions', [])
        
        html = '<div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.1);">'
        
        if evidence:
            html += '<div style="margin-bottom: 1rem;"><strong style="color: #22c55e;">📋 Evidence:</strong><br>'
            for e in evidence[:5]:
                html += f'<span class="evidence-tag">{self._escape(str(e))}</span>'
            html += '</div>'
        
        if assumptions:
            html += '<div><strong style="color: #ef4444;">⚠️ Assumptions:</strong><br>'
            for a in assumptions[:5]:
                html += f'<span class="assumption-tag">{self._escape(str(a))}</span>'
            html += '</div>'
        
        html += '</div>'
        return html
    
    def _generate_use_cases_html(self, use_cases: List) -> str:
        """Generate use cases grid HTML."""
        if not use_cases:
            return '<div class="metric-card"><p style="color: rgba(255,255,255,0.6);">No use cases identified. Deeper analysis may reveal application features.</p></div>'
        
        html = ''
        for uc in use_cases[:8]:
            title = getattr(uc, 'title', 'Unknown')
            description = getattr(uc, 'description', '')
            icon = getattr(uc, 'icon', '📋')
            confidence = getattr(uc, 'confidence', None)
            evidence_files = getattr(uc, 'evidence_files', [])
            
            conf_badge = ''
            if confidence:
                conf_level = getattr(confidence, 'level', 'low')
                conf_score = getattr(confidence, 'score', 0)
                conf_badge = f'<span class="confidence-badge {conf_level}">{conf_score}%</span>'
            
            files_html = ''
            if evidence_files:
                files_html = '<div style="margin-top: 1rem;">'
                for f in evidence_files[:3]:
                    files_html += f'<a href="#" class="file-link" onclick="return false;">{self._escape(f)}</a>'
                if len(evidence_files) > 3:
                    files_html += f'<span style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">+{len(evidence_files) - 3} more</span>'
                files_html += '</div>'
            
            html += f'''
                <div class="use-case-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <span class="use-case-icon">{icon}</span>
                        {conf_badge}
                    </div>
                    <h3 class="use-case-title">{self._escape(title)}</h3>
                    <p class="use-case-description">{self._escape(description)}</p>
                    {files_html}
                </div>
            '''
        
        return html
    
    def _generate_target_users_html(self, users: List[str]) -> str:
        """Generate target users section."""
        if not users:
            return ''
        
        tags = ''.join([f'<span style="display: inline-block; padding: 0.5rem 1rem; background: rgba(123, 97, 255, 0.2); border: 1px solid rgba(123, 97, 255, 0.4); border-radius: 20px; margin: 0.25rem; font-size: 0.9rem;">{self._escape(u)}</span>' for u in users])
        
        return f'''
            <div style="margin-top: 2rem;">
                <h2 class="section-title">👥 Target Users</h2>
                <div>{tags}</div>
            </div>
        '''
    
    def _generate_security_findings_html(self, security: Dict) -> str:
        """Generate security findings HTML."""
        html = ''
        
        for priority, label, color in [('p0_risks', 'P0 Critical', '#ef4444'), ('p1_risks', 'P1 High', '#eab308'), ('p2_risks', 'P2 Medium', '#3b82f6')]:
            risks = security.get(priority, [])
            if not risks:
                continue
            
            html += f'''
                <div class="collapsible" style="margin-top: 1.5rem;">
                    <div class="collapsible-header" onclick="toggleCollapsible(this)">
                        <span style="color: {color}; font-weight: 600;">{label} ({len(risks)} findings)</span>
                        <span class="collapsible-icon">▼</span>
                    </div>
                    <div class="collapsible-content">
            '''
            
            for risk in risks[:10]:
                cat = risk.get('category', 'Security Issue')
                desc = risk.get('description', 'No description')
                loc = risk.get('location', 'Unknown')
                rec = risk.get('recommendation', '')
                
                html += f'''
                    <div style="padding: 1rem; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; margin-bottom: 0.75rem;">
                        <div style="font-weight: 600; margin-bottom: 0.5rem;">{self._escape(cat)}</div>
                        <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">{self._escape(desc)}</div>
                        <div style="margin-top: 0.5rem;">
                            <a href="#" class="file-link" onclick="return false;">📍 {self._escape(str(loc))}</a>
                        </div>
                        {f'<div style="margin-top: 0.75rem; padding: 0.75rem; background: rgba(34, 197, 94, 0.1); border-radius: 6px; font-size: 0.85rem;"><strong>💡 Recommendation:</strong> {self._escape(rec)}</div>' if rec else ''}
                    </div>
                '''
            
            html += '</div></div>'
        
        if not html:
            html = '<div class="metric-card"><p style="color: #22c55e;">✅ No security findings detected. Great job!</p></div>'
        
        return html
    
    def _generate_tech_stack_html(self, tech_stack: List, evidence_map: Dict) -> str:
        """Generate tech stack HTML with evidence."""
        if not tech_stack:
            return '<div class="metric-card"><p style="color: rgba(255,255,255,0.6);">Technology stack analysis pending.</p></div>'
        
        # Group by category
        categories = {}
        for tech in tech_stack:
            cat = tech.get('category', 'other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(tech)
        
        html = '<div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));">'
        
        category_icons = {
            'language': '🔤',
            'framework': '🏗️',
            'database': '💾',
            'orm': '📊',
            'frontend': '🎨',
            'runtime': '⚙️',
            'other': '📦',
        }
        
        for cat, techs in categories.items():
            html += f'''
                <div class="metric-card">
                    <h3 style="margin-bottom: 1rem;">{category_icons.get(cat, '📦')} {cat.title()}</h3>
            '''
            
            for tech in techs:
                name = tech.get('name', 'Unknown')
                icon = tech.get('icon', '📦')
                conf = tech.get('confidence', 'low')
                files = tech.get('evidence_files', [])
                
                files_preview = ''
                if files:
                    files_preview = f'<div style="margin-top: 0.5rem; font-size: 0.75rem; color: rgba(255,255,255,0.5);">Evidence: {", ".join(files[:2])}{" ..." if len(files) > 2 else ""}</div>'
                
                html += f'''
                    <div style="padding: 0.75rem; background: rgba(255,255,255,0.05); border-radius: 8px; margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span>{icon} {self._escape(name)}</span>
                            <span class="confidence-badge {conf}" style="font-size: 0.7rem; padding: 0.15rem 0.5rem;">{conf}</span>
                        </div>
                        {files_preview}
                    </div>
                '''
            
            html += '</div>'
        
        html += '</div>'
        return html
    
    def _generate_dependencies_html(self, dep_data: Dict) -> str:
        """Generate beautiful dependency cards with vulnerability indicators."""
        if not dep_data or dep_data.get('error'):
            return '''
                <div class="metric-card">
                    <p style="color: rgba(255,255,255,0.6);">
                        Dependency analysis pending. Run with deep scan enabled.
                    </p>
                </div>
            '''
        
        packages = dep_data.get('packages', [])
        if not packages:
            # Show basic counts if no package details
            return f'''
                <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
                    <div class="metric-card" style="text-align: center;">
                        <div class="metric-value" style="font-size: 2.5rem; color: #8b5cf6;">
                            {dep_data.get('python_requirements', 0)}
                        </div>
                        <div class="metric-label">Python Requirements</div>
                    </div>
                    <div class="metric-card" style="text-align: center;">
                        <div class="metric-value" style="font-size: 2.5rem; color: #f59e0b;">
                            {dep_data.get('npm_packages', 0)}
                        </div>
                        <div class="metric-label">NPM Package Files</div>
                    </div>
                    <div class="metric-card" style="text-align: center;">
                        <div class="metric-value" style="font-size: 2.5rem; color: #3b82f6;">
                            {dep_data.get('dotnet_projects', 0)}
                        </div>
                        <div class="metric-label">.NET Projects</div>
                    </div>
                    <div class="metric-card" style="text-align: center;">
                        <div class="metric-value" style="font-size: 2.5rem; color: #10b981;">
                            {dep_data.get('nuget_packages', 0)}
                        </div>
                        <div class="metric-label">NuGet Config Files</div>
                    </div>
                </div>
            '''
        
        # Summary cards
        total = dep_data.get('total_packages', len(packages))
        outdated = dep_data.get('outdated_packages', 0)
        vulnerable = dep_data.get('vulnerable_packages', 0)
        critical = dep_data.get('critical_vulnerabilities', 0)
        high = dep_data.get('high_vulnerabilities', 0)
        medium = dep_data.get('medium_vulnerabilities', 0)
        
        html = f'''
            <!-- Dependency Summary Tiles -->
            <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); margin-bottom: 2rem;">
                <div class="metric-card" style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.3) 0%, rgba(139, 92, 246, 0.1) 100%); border: 1px solid rgba(139, 92, 246, 0.4);">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div style="font-size: 2.5rem;">📦</div>
                        <div>
                            <div style="font-size: 2rem; font-weight: 700; color: #a78bfa;">{total}</div>
                            <div style="font-size: 0.85rem; color: rgba(255,255,255,0.7);">Total Packages</div>
                        </div>
                    </div>
                </div>
                
                <div class="metric-card" style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.3) 0%, rgba(245, 158, 11, 0.1) 100%); border: 1px solid rgba(245, 158, 11, 0.4);">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div style="font-size: 2.5rem;">⏰</div>
                        <div>
                            <div style="font-size: 2rem; font-weight: 700; color: #fbbf24;">{outdated}</div>
                            <div style="font-size: 0.85rem; color: rgba(255,255,255,0.7);">Outdated</div>
                        </div>
                    </div>
                </div>
                
                <div class="metric-card" style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.3) 0%, rgba(239, 68, 68, 0.1) 100%); border: 1px solid rgba(239, 68, 68, 0.4);">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div style="font-size: 2.5rem;">🚨</div>
                        <div>
                            <div style="font-size: 2rem; font-weight: 700; color: #f87171;">{vulnerable}</div>
                            <div style="font-size: 0.85rem; color: rgba(255,255,255,0.7);">Vulnerable</div>
                        </div>
                    </div>
                </div>
                
                <div class="metric-card" style="background: linear-gradient(135deg, rgba(220, 38, 38, 0.3) 0%, rgba(220, 38, 38, 0.1) 100%); border: 1px solid rgba(220, 38, 38, 0.4);">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div style="font-size: 2.5rem;">💀</div>
                        <div>
                            <div style="font-size: 2rem; font-weight: 700; color: #ef4444;">{critical}</div>
                            <div style="font-size: 0.85rem; color: rgba(255,255,255,0.7);">Critical CVEs</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Package Cards Grid -->
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem;">
        '''
        
        # Group by type
        packages_by_type = {}
        for pkg in packages:
            pkg_type = pkg.get('type', 'unknown')
            if pkg_type not in packages_by_type:
                packages_by_type[pkg_type] = []
            packages_by_type[pkg_type].append(pkg)
        
        type_icons = {
            'python': '🐍',
            'nodejs': '⬢',
            'dotnet': '🔷',
            'unknown': '📦',
        }
        
        type_colors = {
            'python': '#3776ab',
            'nodejs': '#539e43',
            'dotnet': '#512bd4',
            'unknown': '#6b7280',
        }
        
        for pkg_type, type_packages in packages_by_type.items():
            icon = type_icons.get(pkg_type, '📦')
            color = type_colors.get(pkg_type, '#6b7280')
            
            for pkg in type_packages[:50]:  # Limit to 50 per type
                name = self._escape(pkg.get('name', 'Unknown'))
                version = self._escape(pkg.get('version', '?'))
                latest = pkg.get('latest_version', '')
                vulns = pkg.get('vulnerabilities', [])
                is_dev = pkg.get('is_dev', False)
                license_info = pkg.get('license', '')
                
                # Determine card status
                has_vulns = len(vulns) > 0
                is_outdated = latest and latest != version and latest != 'unknown'
                
                # Card border color based on status
                if has_vulns:
                    border_color = 'rgba(239, 68, 68, 0.6)'
                    bg_gradient = 'linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%)'
                elif is_outdated:
                    border_color = 'rgba(245, 158, 11, 0.5)'
                    bg_gradient = 'linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.02) 100%)'
                else:
                    border_color = 'rgba(255, 255, 255, 0.1)'
                    bg_gradient = 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)'
                
                # Build vulnerability badges
                vuln_badges = ''
                if vulns:
                    vuln_badges = '<div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.75rem;">'
                    for v in vulns[:3]:
                        severity = v.get('severity', 'medium').lower()
                        cve = v.get('cve_id', 'Unknown')
                        
                        sev_colors = {
                            'critical': '#dc2626',
                            'high': '#ef4444',
                            'medium': '#f59e0b',
                            'low': '#22c55e',
                        }
                        sev_color = sev_colors.get(severity, '#6b7280')
                        
                        vuln_badges += f'''
                            <span style="
                                display: inline-flex;
                                align-items: center;
                                gap: 0.25rem;
                                padding: 0.25rem 0.5rem;
                                background: rgba({self._hex_to_rgb(sev_color)}, 0.2);
                                border: 1px solid {sev_color};
                                border-radius: 6px;
                                font-size: 0.7rem;
                                font-weight: 600;
                                color: {sev_color};
                            ">
                                🔓 {cve}
                            </span>
                        '''
                    if len(vulns) > 3:
                        vuln_badges += f'<span style="font-size: 0.75rem; color: rgba(255,255,255,0.5);">+{len(vulns) - 3} more</span>'
                    vuln_badges += '</div>'
                
                # Status badges
                status_badges = '<div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">'
                if is_dev:
                    status_badges += '<span style="padding: 0.15rem 0.4rem; background: rgba(139, 92, 246, 0.2); border: 1px solid rgba(139, 92, 246, 0.4); border-radius: 4px; font-size: 0.65rem; color: #a78bfa;">DEV</span>'
                if is_outdated:
                    status_badges += '<span style="padding: 0.15rem 0.4rem; background: rgba(245, 158, 11, 0.2); border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 4px; font-size: 0.65rem; color: #fbbf24;">OUTDATED</span>'
                if has_vulns:
                    status_badges += '<span style="padding: 0.15rem 0.4rem; background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 4px; font-size: 0.65rem; color: #f87171;">VULNERABLE</span>'
                status_badges += '</div>'
                
                html += f'''
                    <div class="dependency-card" style="
                        background: {bg_gradient};
                        border: 1px solid {border_color};
                        border-radius: 12px;
                        padding: 1.25rem;
                        transition: all 0.3s ease;
                        position: relative;
                        overflow: hidden;
                    ">
                        <!-- Type indicator stripe -->
                        <div style="
                            position: absolute;
                            top: 0;
                            left: 0;
                            width: 4px;
                            height: 100%;
                            background: {color};
                        "></div>
                        
                        <!-- Header -->
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <span style="font-size: 1.25rem;">{icon}</span>
                                <span style="font-weight: 600; font-size: 1rem; color: #fff;">{name}</span>
                            </div>
                            {status_badges}
                        </div>
                        
                        <!-- Version info -->
                        <div style="display: flex; gap: 1rem; margin-bottom: 0.5rem; font-size: 0.85rem;">
                            <div>
                                <span style="color: rgba(255,255,255,0.5);">Current:</span>
                                <span style="color: #00d4ff; font-family: monospace;">{version}</span>
                            </div>
                            {"<div><span style='color: rgba(255,255,255,0.5);'>Latest:</span> <span style='color: #22c55e; font-family: monospace;'>" + self._escape(latest) + "</span></div>" if is_outdated else ""}
                        </div>
                        
                        <!-- License -->
                        {"<div style='font-size: 0.75rem; color: rgba(255,255,255,0.4);'>📜 " + self._escape(license_info) + "</div>" if license_info else ""}
                        
                        <!-- Vulnerabilities -->
                        {vuln_badges}
                    </div>
                '''
        
        html += '</div>'
        return html
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB string for rgba()."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            return f"{r}, {g}, {b}"
        return "128, 128, 128"
    
    def _generate_database_html(self, db_data: Dict) -> str:
        """Generate database analysis HTML."""
        if not db_data:
            return '<div class="metric-card"><p style="color: rgba(255,255,255,0.6);">Database analysis pending deeper inspection.</p></div>'
        
        return f'''
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{db_data.get('has_migrations', '?')}</div>
                    <div class="metric-label">Has Migrations</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">?</div>
                    <div class="metric-label">Tables Detected</div>
                </div>
            </div>
            <div class="metric-card" style="margin-top: 1.5rem;">
                <p style="color: rgba(255,255,255,0.6);">{db_data.get('note', 'Full database analysis requires additional tooling.')}</p>
            </div>
        '''
    
    def _generate_recommendations_html(self, recommendations: List) -> str:
        """Generate recommendations HTML."""
        if not recommendations:
            return '<div class="metric-card"><p style="color: rgba(255,255,255,0.6);">No recommendations generated. Repository appears healthy.</p></div>'
        
        html = ''
        for i, rec in enumerate(recommendations[:10], 1):
            priority = rec.get('priority', 'P2')
            cat = rec.get('category', 'General')
            desc = rec.get('description', '')
            recommendation = rec.get('recommendation', '')
            impact = rec.get('impact', 'MEDIUM')
            
            priority_color = {'P0': '#ef4444', 'P1': '#eab308', 'P2': '#3b82f6'}.get(priority, '#3b82f6')
            
            html += f'''
                <div style="padding: 1.5rem; background: rgba(26, 31, 58, 0.6); border-radius: 12px; margin-bottom: 1rem; border-left: 4px solid {priority_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                        <span style="font-weight: 700;">#{i} {self._escape(cat)}</span>
                        <div>
                            <span class="security-badge {priority.lower()}">{priority}</span>
                            <span style="margin-left: 0.5rem; font-size: 0.8rem; color: rgba(255,255,255,0.5);">{impact}</span>
                        </div>
                    </div>
                    {f'<p style="color: rgba(255,255,255,0.7); margin-bottom: 0.75rem;">{self._escape(desc)}</p>' if desc else ''}
                    {f'<div style="padding: 0.75rem; background: rgba(34, 197, 94, 0.1); border-radius: 6px;"><strong>💡</strong> {self._escape(recommendation)}</div>' if recommendation else ''}
                </div>
            '''
        
        return html
    
    def _generate_modernization_html(self, security: Dict, tech_stack: List) -> str:
        """Generate modernization roadmap HTML."""
        p0_count = len(security.get('p0_risks', []))
        
        phases = []
        
        if p0_count > 0:
            phases.append({
                'title': 'Phase 1: Security Hardening (Immediate)',
                'description': 'Address P0 critical security issues. Remove hardcoded credentials, rotate keys, implement proper secrets management.',
                'priority': 'critical'
            })
        
        phases.append({
            'title': 'Phase 2: Framework Updates (1-2 months)',
            'description': 'Update dependencies, migrate deprecated APIs, implement modern authentication patterns.',
            'priority': 'high'
        })
        
        phases.append({
            'title': 'Phase 3: Architecture Refactor (2-4 months)',
            'description': 'Implement Clean Architecture patterns, separate concerns, add comprehensive testing.',
            'priority': 'medium'
        })
        
        phases.append({
            'title': 'Phase 4: Cloud-Native Migration (4-6 months)',
            'description': 'Containerization, CI/CD pipelines, cloud deployment, monitoring and observability.',
            'priority': 'low'
        })
        
        html = '<div style="position: relative; padding-left: 2rem;">'
        html += '<div style="position: absolute; left: 0.5rem; top: 0; bottom: 0; width: 3px; background: linear-gradient(180deg, #ef4444 0%, #eab308 33%, #3b82f6 66%, #22c55e 100%); border-radius: 3px;"></div>'
        
        for phase in phases:
            color = {'critical': '#ef4444', 'high': '#eab308', 'medium': '#3b82f6', 'low': '#22c55e'}[phase['priority']]
            
            html += f'''
                <div style="position: relative; padding: 1.5rem; background: rgba(26, 31, 58, 0.6); border-radius: 12px; margin-bottom: 1rem; margin-left: 1.5rem;">
                    <div style="position: absolute; left: -2.15rem; top: 1.75rem; width: 12px; height: 12px; background: {color}; border-radius: 50%; border: 3px solid #0a0a0f;"></div>
                    <h4 style="margin-bottom: 0.5rem;">{self._escape(phase['title'])}</h4>
                    <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">{self._escape(phase['description'])}</p>
                </div>
            '''
        
        html += '</div>'
        return html
    
    def _generate_compliance_html(self, security: Dict) -> str:
        """Generate compliance status HTML."""
        p0 = len(security.get('p0_risks', []))
        p1 = len(security.get('p1_risks', []))
        
        owasp_score = max(0, 10 - p0 * 2 - p1)
        pci_score = max(0, 12 - p0 * 3 - p1 * 2)
        
        return f'''
            <div class="metrics-grid">
                <div class="metric-card">
                    <div style="font-size: 0.9rem; color: rgba(255,255,255,0.6); margin-bottom: 0.5rem;">OWASP Top 10</div>
                    <div class="metric-value" style="color: {'#22c55e' if owasp_score >= 7 else '#eab308' if owasp_score >= 5 else '#ef4444'};">{owasp_score}/10</div>
                    <div class="metric-label">Compliance Score</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 0.9rem; color: rgba(255,255,255,0.6); margin-bottom: 0.5rem;">PCI-DSS (if applicable)</div>
                    <div class="metric-value" style="color: {'#22c55e' if pci_score >= 9 else '#eab308' if pci_score >= 6 else '#ef4444'};">{pci_score}/12</div>
                    <div class="metric-label">Compliance Score</div>
                </div>
            </div>
            <div class="metric-card" style="margin-top: 1.5rem;">
                <p style="color: rgba(255,255,255,0.6);">
                    ⚠️ Compliance scores are estimates based on security findings. 
                    Full compliance audit requires dedicated security assessment.
                </p>
            </div>
        '''
    
    def _generate_metrics_html(self, context: Dict) -> str:
        """Generate code metrics HTML."""
        code = context.get('code_analysis', {})
        
        return f'''
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{code.get('total_python_files', '?')}</div>
                    <div class="metric-label">Python Files</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{code.get('analyzed_files', '?')}</div>
                    <div class="metric-label">Files Analyzed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">?</div>
                    <div class="metric-label">Lines of Code</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">?</div>
                    <div class="metric-label">Test Coverage</div>
                </div>
            </div>
            <div class="metric-card" style="margin-top: 1.5rem;">
                <p style="color: rgba(255,255,255,0.6);">
                    Detailed code metrics require integration with static analysis tools.
                    Consider running SonarQube, Pylint, or similar for comprehensive metrics.
                </p>
            </div>
        '''
    
    def _get_architecture_layers_json(self, tech_stack: List) -> str:
        """Generate JSON for architecture layers."""
        layers = []
        
        # Determine layers from tech stack
        has_frontend = any(t.get('category') == 'frontend' for t in tech_stack)
        has_api = any('api' in t.get('name', '').lower() or 'fastapi' in t.get('name', '').lower() for t in tech_stack)
        has_db = any(t.get('category') == 'database' for t in tech_stack)
        
        if has_frontend:
            layers.append({'name': 'Presentation Layer', 'color': '#3b82f6'})
        
        layers.append({'name': 'Application Layer', 'color': '#a855f7'})
        
        if has_api:
            layers.append({'name': 'API Layer', 'color': '#6366f1'})
        
        if has_db:
            layers.append({'name': 'Data Layer', 'color': '#22c55e'})
        
        if not layers:
            layers = [
                {'name': 'Application', 'color': '#3b82f6'},
                {'name': 'Data', 'color': '#22c55e'}
            ]
        
        return json.dumps(layers)


# Singleton
_universal_dashboard_generator = None


def get_universal_dashboard_generator() -> UniversalDashboardGenerator:
    """Get or create singleton."""
    global _universal_dashboard_generator
    if _universal_dashboard_generator is None:
        _universal_dashboard_generator = UniversalDashboardGenerator()
    return _universal_dashboard_generator
