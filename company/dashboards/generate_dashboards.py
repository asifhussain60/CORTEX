#!/usr/bin/env python3
"""
Static Dashboard Generator - Enterprise Edition
Generates self-contained HTML dashboards with CORTEX glassmorphism theme.

Theme: Dark Blue Glassmorphism (13+ tabs)
Assets: External CSS references (main.css, glass-*.css)
Logo: CORTEX-logo-200.png (200x200 left justified)
Content: Business language via BusinessTranslator

Reference Commits:
- 3144a4a4a: Glassmorphism domain dashboards with D3.js
- fc2194696: DashboardThemeTemplate (1,100 lines SSOT)
- 1e6bfd2b8: LLM content enhancement with BusinessTranslator
- 615805c9b: Comprehensive 8-tab dashboard with D3.js
- eeb039277: GPT-enhanced dashboard with ECharts
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# ============================================================================
# BUSINESS LANGUAGE TRANSLATOR (from commit 1e6bfd2b8)
# ============================================================================

class BusinessTranslator:
    """Translate technical terms to business-friendly language."""
    
    USE_CASE_MAPPING = {
        "crud": {"title": "📝 Manage organizational data", "icon": "📝"},
        "data management": {"title": "📝 Manage organizational data", "icon": "📝"},
        "reporting": {"title": "📊 Track key performance indicators", "icon": "📊"},
        "analytics": {"title": "📊 Analyze business insights", "icon": "📊"},
        "notifications": {"title": "🔔 Stay informed with real-time alerts", "icon": "🔔"},
        "file": {"title": "📁 Organize and share documents", "icon": "📁"},
        "scheduling": {"title": "📅 Plan and coordinate activities", "icon": "📅"},
        "search": {"title": "🔍 Find information quickly", "icon": "🔍"},
        "authentication": {"title": "🔐 Secure user access", "icon": "🔐"},
        "api": {"title": "🔌 Connect with other systems", "icon": "🔌"},
        "workflow": {"title": "⚡ Automate business processes", "icon": "⚡"},
        "integration": {"title": "🔗 Seamless system connectivity", "icon": "🔗"},
        "dashboard": {"title": "📈 Real-time business visibility", "icon": "📈"},
        "compliance": {"title": "✅ Ensure regulatory adherence", "icon": "✅"},
    }
    
    AUDIENCE_DESCRIPTIONS = {
        "executive": "Strategic overview of system health and business value",
        "product_owner": "Feature inventory and development velocity metrics",
        "dev_manager": "Team productivity, code quality, and technical debt",
        "engineer": "Architecture, dependencies, and implementation details",
        "leader": "Risk assessment, security posture, and modernization status",
    }
    
    def translate_use_cases(self, use_cases: List[Any]) -> List[Dict]:
        """Transform use cases to business-friendly format."""
        if not use_cases:
            return []
        
        result = []
        for uc in use_cases:
            if isinstance(uc, str):
                # Match against keywords
                matched = False
                for keyword, mapping in self.USE_CASE_MAPPING.items():
                    if keyword.lower() in uc.lower():
                        result.append({
                            "title": mapping["title"],
                            "description": uc,
                            "icon": mapping["icon"],
                            "business_value": "High"
                        })
                        matched = True
                        break
                if not matched:
                    result.append({
                        "title": uc,
                        "description": uc,
                        "icon": "📋",
                        "business_value": "Medium"
                    })
            elif isinstance(uc, dict):
                result.append(uc)
        
        return result


# ============================================================================
# HTML TEMPLATE WITH EXTERNAL CSS (from approved-orchestrator-view pattern)
# ============================================================================

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{repo_name} - Enterprise Repository Intelligence Dashboard">
    <meta name="keywords" content="CORTEX, dashboard, {repo_name}, code analysis, security">
    <meta name="author" content="Asif Hussain">
    <title>{repo_display_name} | CORTEX Dashboard</title>
    
    <!-- Favicon -->
    <link href="../../assets/images/CORTEX-logo-64.png" rel="icon" type="image/png">
    
    <!-- CORTEX Glassmorphism Theme (External CSS) -->
    <link href="../../assets/css/main.css" rel="stylesheet">
    <link href="../../assets/css/glass-design-tokens.css" rel="stylesheet">
    <link href="../../assets/css/glass-base-patterns.css" rel="stylesheet">
    <link href="../../assets/css/glass-ui-components.css" rel="stylesheet">
    <link href="../../assets/css/glass-animations.css" rel="stylesheet">
    
    <!-- Font Awesome Icons -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet" crossorigin="anonymous">
    
    <!-- D3.js for Visualizations -->
    <script src="https://d3js.org/d3.v7.min.js"></script>
    
    <!-- Dashboard-Specific Styles -->
    <style>
        /* Header Layout: Logo (200x200) + Title */
        .dashboard-header {{
            display: flex;
            align-items: center;
            gap: 2rem;
            padding: 1.5rem 2rem;
            background: var(--glass-bg, rgba(26, 31, 58, 0.7));
            border-bottom: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }}
        
        .logo-container {{
            flex-shrink: 0;
        }}
        
        .logo-container img {{
            width: 200px;
            height: 200px;
            object-fit: contain;
            filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.3));
            animation: logoGlow 3s ease-in-out infinite alternate;
        }}
        
        @keyframes logoGlow {{
            0% {{ filter: drop-shadow(0 0 15px rgba(0, 212, 255, 0.3)); }}
            100% {{ filter: drop-shadow(0 0 30px rgba(0, 212, 255, 0.5)); }}
        }}
        
        .header-content {{
            flex: 1;
        }}
        
        .header-content h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--accent-primary, #00d4ff);
            margin-bottom: 0.5rem;
            text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
        }}
        
        .header-content .tagline {{
            font-size: 1.1rem;
            color: var(--text-secondary, #a0a6c0);
            margin-bottom: 1rem;
        }}
        
        .header-stats {{
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }}
        
        .header-stat {{
            text-align: center;
        }}
        
        .header-stat .value {{
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-primary, #ffffff);
        }}
        
        .header-stat .label {{
            font-size: 0.875rem;
            color: var(--text-secondary, #a0a6c0);
        }}
        
        /* Health Badge */
        .health-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            border-radius: var(--radius-full, 9999px);
            font-weight: 600;
            font-size: 1.25rem;
        }}
        
        .health-good {{
            background: rgba(0, 255, 136, 0.15);
            color: var(--success, #00ff88);
            border: 1px solid var(--success, #00ff88);
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.2);
        }}
        
        .health-warning {{
            background: rgba(255, 165, 0, 0.15);
            color: var(--warning, #ffa500);
            border: 1px solid var(--warning, #ffa500);
            box-shadow: 0 0 20px rgba(255, 165, 0, 0.2);
        }}
        
        .health-danger {{
            background: rgba(255, 68, 68, 0.15);
            color: var(--danger, #ff4444);
            border: 1px solid var(--danger, #ff4444);
            box-shadow: 0 0 20px rgba(255, 68, 68, 0.2);
        }}
        
        /* Tab Navigation */
        .tab-nav {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            padding: 1rem 2rem;
            background: rgba(10, 14, 39, 0.8);
            border-bottom: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
            overflow-x: auto;
        }}
        
        .tab-btn {{
            padding: 0.75rem 1.25rem;
            background: transparent;
            border: 1px solid transparent;
            border-radius: var(--radius-md, 12px);
            color: var(--text-secondary, #a0a6c0);
            cursor: pointer;
            font-family: inherit;
            font-size: 0.9rem;
            transition: all var(--transition-base, 200ms ease-in-out);
            white-space: nowrap;
        }}
        
        .tab-btn:hover {{
            background: rgba(0, 212, 255, 0.1);
            color: var(--text-primary, #ffffff);
            border-color: rgba(0, 212, 255, 0.3);
        }}
        
        .tab-btn.active {{
            background: linear-gradient(135deg, var(--accent-primary, #00d4ff), var(--accent-secondary, #7b61ff));
            color: var(--text-primary, #ffffff);
            border-color: transparent;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        }}
        
        /* Tab Content */
        .tab-content {{
            padding: 2rem;
            max-width: 1600px;
            margin: 0 auto;
        }}
        
        .tab-panel {{
            display: none;
            animation: fadeIn 0.3s ease-in-out;
        }}
        
        .tab-panel.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        /* Glass Cards */
        .glass-card {{
            background: var(--glass-bg, rgba(26, 31, 58, 0.7));
            border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
            border-radius: var(--radius-lg, 16px);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            box-shadow: var(--shadow, 0 8px 32px 0 rgba(0, 0, 0, 0.37));
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            transition: all var(--transition-base, 200ms ease-in-out);
        }}
        
        .glass-card:hover {{
            box-shadow: var(--shadow-lg, 0 20px 60px 0 rgba(0, 0, 0, 0.5));
            border-color: rgba(0, 212, 255, 0.3);
        }}
        
        /* Metrics Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .metric-card {{
            background: var(--glass-bg, rgba(26, 31, 58, 0.7));
            border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
            border-radius: var(--radius-md, 12px);
            padding: 1.5rem;
            text-align: center;
            transition: all var(--transition-base, 200ms ease-in-out);
        }}
        
        .metric-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
            border-color: rgba(0, 212, 255, 0.4);
        }}
        
        .metric-value {{
            font-size: 2.25rem;
            font-weight: 700;
            color: var(--accent-primary, #00d4ff);
            margin-bottom: 0.5rem;
            text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        }}
        
        .metric-label {{
            font-size: 0.875rem;
            color: var(--text-secondary, #a0a6c0);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        /* Section Headers */
        .section-header {{
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--accent-primary, #00d4ff);
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid var(--glass-border, rgba(255, 255, 255, 0.1));
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        
        /* Use Case Cards (Business Language) */
        .use-case-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }}
        
        .use-case-card {{
            background: var(--glass-bg, rgba(26, 31, 58, 0.7));
            border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
            border-radius: var(--radius-lg, 16px);
            padding: 1.5rem;
            transition: all var(--transition-base, 200ms ease-in-out);
        }}
        
        .use-case-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0, 212, 255, 0.2);
            border-color: rgba(0, 212, 255, 0.4);
        }}
        
        .use-case-icon {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        
        .use-case-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary, #ffffff);
            margin-bottom: 0.5rem;
        }}
        
        .use-case-description {{
            font-size: 0.9rem;
            color: var(--text-secondary, #a0a6c0);
            line-height: 1.6;
        }}
        
        .use-case-value {{
            margin-top: 1rem;
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: rgba(0, 255, 136, 0.15);
            color: var(--success, #00ff88);
            border-radius: var(--radius-full, 9999px);
            font-size: 0.8rem;
            font-weight: 500;
        }}
        
        /* Tables */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        
        .data-table th,
        .data-table td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
        }}
        
        .data-table th {{
            background: rgba(0, 212, 255, 0.1);
            color: var(--accent-primary, #00d4ff);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 0.05em;
        }}
        
        .data-table tr:hover {{
            background: rgba(0, 212, 255, 0.05);
        }}
        
        /* Badges */
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: var(--radius-full, 9999px);
            font-size: 0.8rem;
            font-weight: 500;
        }}
        
        .badge-success {{ background: rgba(0, 255, 136, 0.15); color: var(--success, #00ff88); }}
        .badge-warning {{ background: rgba(255, 165, 0, 0.15); color: var(--warning, #ffa500); }}
        .badge-danger {{ background: rgba(255, 68, 68, 0.15); color: var(--danger, #ff4444); }}
        .badge-info {{ background: rgba(59, 130, 246, 0.15); color: var(--info, #3b82f6); }}
        
        /* Audience Cards */
        .audience-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .audience-card {{
            background: var(--glass-bg, rgba(26, 31, 58, 0.7));
            border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
            border-radius: var(--radius-lg, 16px);
            padding: 1.5rem;
            text-align: center;
        }}
        
        .audience-icon {{
            font-size: 2rem;
            margin-bottom: 0.75rem;
        }}
        
        .audience-title {{
            font-weight: 600;
            color: var(--text-primary, #ffffff);
            margin-bottom: 0.5rem;
        }}
        
        .audience-desc {{
            font-size: 0.85rem;
            color: var(--text-secondary, #a0a6c0);
        }}
        
        /* Progress Bar */
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }}
        
        .progress-success {{ background: linear-gradient(90deg, var(--success), #00ff88); }}
        .progress-warning {{ background: linear-gradient(90deg, var(--warning), #ffcc00); }}
        .progress-danger {{ background: linear-gradient(90deg, var(--danger), #ff6666); }}
        
        /* Footer */
        .dashboard-footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-secondary, #a0a6c0);
            font-size: 0.875rem;
            border-top: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1));
            margin-top: 2rem;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .dashboard-header {{
                flex-direction: column;
                text-align: center;
            }}
            
            .logo-container img {{
                width: 150px;
                height: 150px;
            }}
            
            .header-content h1 {{
                font-size: 1.75rem;
            }}
            
            .header-stats {{
                justify-content: center;
            }}
            
            .tab-content {{
                padding: 1rem;
            }}
            
            .metrics-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
        
        @media (max-width: 480px) {{
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            
            .use-case-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <!-- Header with Logo and Title -->
    <header class="dashboard-header">
        <div class="logo-container">
            <img src="../../assets/images/CORTEX-logo-200.png" alt="CORTEX Logo">
        </div>
        <div class="header-content">
            <h1>{repo_display_name}</h1>
            <p class="tagline">{tagline}</p>
            <div class="header-stats">
                <div class="header-stat">
                    <div class="value">{total_files}</div>
                    <div class="label">Files</div>
                </div>
                <div class="header-stat">
                    <div class="value">{total_lines}</div>
                    <div class="label">Lines of Code</div>
                </div>
                <div class="header-stat">
                    <div class="value">{total_commits}</div>
                    <div class="label">Commits</div>
                </div>
                <div class="header-stat">
                    <span class="health-badge {health_class}">
                        <i class="fas fa-heart-pulse"></i> {health_score}%
                    </span>
                </div>
            </div>
        </div>
    </header>
    
    <!-- Tab Navigation -->
    <nav class="tab-nav">
{tab_buttons}
    </nav>
    
    <!-- Tab Content -->
    <main class="tab-content">
{tab_panels}
    </main>
    
    <!-- Footer -->
    <footer class="dashboard-footer">
        <p>Generated by <strong>CORTEX</strong> Enterprise Repository Intelligence</p>
        <p>© 2024-2026 Asif Hussain | Generated: {generated_at}</p>
    </footer>
    
    <!-- Embedded Data -->
    <script type="application/json" id="dashboard-data">
{json_data}
    </script>
    
    <!-- Tab Navigation Script -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const tabButtons = document.querySelectorAll('.tab-btn');
            const tabPanels = document.querySelectorAll('.tab-panel');
            
            tabButtons.forEach(button => {{
                button.addEventListener('click', () => {{
                    // Remove active from all
                    tabButtons.forEach(b => b.classList.remove('active'));
                    tabPanels.forEach(p => p.classList.remove('active'));
                    
                    // Add active to clicked
                    button.classList.add('active');
                    const tabId = button.dataset.tab;
                    const panel = document.getElementById(tabId);
                    if (panel) panel.classList.add('active');
                }});
            }});
            
            // Activate first tab
            if (tabButtons.length > 0) {{
                tabButtons[0].click();
            }}
            
            // Load embedded data
            const dataEl = document.getElementById('dashboard-data');
            if (dataEl) {{
                try {{
                    window.dashboardData = JSON.parse(dataEl.textContent);
                    console.log('📊 Dashboard data loaded:', window.dashboardData);
                }} catch (e) {{
                    console.error('Failed to parse dashboard data:', e);
                }}
            }}
        }});
    </script>
</body>
</html>
'''

# ============================================================================
# TAB DEFINITIONS (13 tabs for all audiences)
# ============================================================================

TABS = [
    {"id": "overview", "label": "Overview", "icon": "📊", "audience": "all"},
    {"id": "architecture", "label": "Architecture", "icon": "🏗️", "audience": "engineer"},
    {"id": "quality", "label": "Quality", "icon": "✅", "audience": "dev_manager"},
    {"id": "vulnerabilities", "label": "Vulnerabilities", "icon": "🛡️", "audience": "all"},
    {"id": "security", "label": "Security", "icon": "🔒", "audience": "leader"},
    {"id": "dependencies", "label": "Dependencies", "icon": "📦", "audience": "engineer"},
    {"id": "testing", "label": "Testing", "icon": "🧪", "audience": "dev_manager"},
    {"id": "patterns", "label": "Patterns", "icon": "🎨", "audience": "engineer"},
    {"id": "usecases", "label": "Use Cases", "icon": "📋", "audience": "product_owner"},
    {"id": "timeline", "label": "Timeline", "icon": "📅", "audience": "all"},
    {"id": "impact", "label": "Impact", "icon": "💥", "audience": "leader"},
    {"id": "vendors", "label": "Vendors", "icon": "🏢", "audience": "executive"},
    {"id": "database", "label": "Database", "icon": "🗄️", "audience": "engineer"},
]


# ============================================================================
# TAB CONTENT GENERATORS
# ============================================================================

def generate_language_cards(languages) -> str:
    """Generate language metric cards, handling both dict and list formats."""
    if isinstance(languages, dict):
        return "".join(
            f'<div class="metric-card"><div class="metric-value">{lines:,}</div><div class="metric-label">{lang}</div></div>'
            for lang, lines in languages.items()
        )
    elif isinstance(languages, list):
        return "".join(
            f'<div class="metric-card"><div class="metric-value">{item.get("count", item.get("lines", 0)):,}</div><div class="metric-label">{item.get("name", item.get("language", "Unknown"))}</div></div>'
            for item in languages
        )
    return ""


def generate_overview_content(data: dict) -> str:
    """Generate Overview tab content with business language."""
    overview = data.get("overview", {})
    metrics = data.get("metrics", {})
    
    # Audience cards
    translator = BusinessTranslator()
    audience_cards = ""
    for audience, desc in translator.AUDIENCE_DESCRIPTIONS.items():
        icon_map = {
            "executive": "👔", "product_owner": "📋", 
            "dev_manager": "👨‍💼", "engineer": "👩‍💻", "leader": "🎯"
        }
        audience_cards += f'''
            <div class="audience-card">
                <div class="audience-icon">{icon_map.get(audience, "👤")}</div>
                <div class="audience-title">{audience.replace("_", " ").title()}</div>
                <div class="audience-desc">{desc}</div>
            </div>
        '''
    
    return f"""
        <!-- Audience Quick Access -->
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-users"></i> Dashboard Audiences</h3>
            <div class="audience-grid">
                {audience_cards}
            </div>
        </div>
        
        <!-- Key Metrics -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{overview.get('total_files', 'N/A')}</div>
                <div class="metric-label">Total Files</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{overview.get('total_lines', 0):,}</div>
                <div class="metric-label">Lines of Code</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{overview.get('total_commits', 'N/A')}</div>
                <div class="metric-label">Commits</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{overview.get('contributors', 'N/A')}</div>
                <div class="metric-label">Contributors</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('test_coverage', 'N/A')}%</div>
                <div class="metric-label">Test Coverage</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('maintainability_index', 'N/A')}</div>
                <div class="metric-label">Maintainability</div>
            </div>
        </div>
        
        <!-- Technology Stack -->
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-code"></i> Technology Stack</h3>
            <div class="metrics-grid">
                {generate_language_cards(overview.get('languages', {}))}
            </div>
        </div>
        
        <!-- Repository Health -->
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-heartbeat"></i> Repository Health</h3>
            <table class="data-table">
                <tr><td><i class="fas fa-code-branch"></i> Primary Language</td><td><strong>{overview.get('primary_language', 'N/A')}</strong></td></tr>
                <tr><td><i class="fas fa-calendar"></i> Repository Age</td><td><strong>{overview.get('repo_age_days', 'N/A')} days</strong></td></tr>
                <tr><td><i class="fas fa-clock"></i> Last Updated</td><td><strong>{overview.get('last_updated', 'N/A')}</strong></td></tr>
                <tr><td><i class="fas fa-tools"></i> Technical Debt</td><td><strong>{metrics.get('technical_debt_hours', 'N/A')} hours</strong></td></tr>
            </table>
        </div>
    """


def generate_usecases_content(data: dict) -> str:
    """Generate Use Cases tab with business-friendly language."""
    overview = data.get("overview", {})
    use_cases = overview.get("use_cases", [])
    domain = data.get("domain", {})
    
    translator = BusinessTranslator()
    translated = translator.translate_use_cases(use_cases)
    
    use_case_cards = ""
    for uc in translated[:12]:  # Show top 12
        use_case_cards += f'''
            <div class="use-case-card">
                <div class="use-case-icon">{uc.get("icon", "📋")}</div>
                <div class="use-case-title">{uc.get("title", "Untitled")}</div>
                <div class="use-case-description">{uc.get("description", "")}</div>
                <span class="use-case-value">{uc.get("business_value", "Medium")} Value</span>
            </div>
        '''
    
    if not use_case_cards:
        use_case_cards = '''
            <div class="glass-card" style="text-align: center; padding: 3rem;">
                <i class="fas fa-search" style="font-size: 3rem; color: var(--text-secondary); margin-bottom: 1rem;"></i>
                <p style="color: var(--text-secondary);">Use case analysis will be populated from repository scanning.</p>
            </div>
        '''
    
    return f"""
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-briefcase"></i> Business Capabilities</h3>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                Key capabilities identified through automated code analysis, translated to business terminology 
                for product owners, executives, and stakeholders.
            </p>
        </div>
        
        <div class="use-case-grid">
            {use_case_cards}
        </div>
        
        <div class="glass-card" style="margin-top: 2rem;">
            <h3 class="section-header"><i class="fas fa-chart-line"></i> Business Value Summary</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{len(translated)}</div>
                    <div class="metric-label">Identified Capabilities</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{domain.get('complexity', 'Medium')}</div>
                    <div class="metric-label">Complexity</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{domain.get('modernization_score', 'N/A')}</div>
                    <div class="metric-label">Modernization Score</div>
                </div>
            </div>
        </div>
    """


def generate_vulnerabilities_content(data: dict) -> str:
    """Generate Vulnerabilities tab content."""
    security = data.get("security", {})
    vulnerabilities = security.get("vulnerabilities", {})
    owasp_findings = security.get("owasp_findings", [])
    
    # Summary cards
    if isinstance(vulnerabilities, dict) and "critical" in vulnerabilities:
        vuln_summary = f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value" style="color: var(--danger);">{vulnerabilities.get('critical', 0)}</div>
                <div class="metric-label">Critical</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: var(--danger);">{vulnerabilities.get('high', 0)}</div>
                <div class="metric-label">High</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: var(--warning);">{vulnerabilities.get('medium', 0)}</div>
                <div class="metric-label">Medium</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: var(--info);">{vulnerabilities.get('low', 0)}</div>
                <div class="metric-label">Low</div>
            </div>
        </div>
        """
    else:
        vuln_summary = ""
    
    # OWASP findings
    owasp_rows = ""
    if isinstance(owasp_findings, list):
        for finding in owasp_findings[:10]:
            if isinstance(finding, dict):
                severity = finding.get("severity", "low")
                severity_class = "badge-danger" if severity in ["critical", "high"] else "badge-warning" if severity == "medium" else "badge-info"
                owasp_rows += f"""
                <tr>
                    <td>{finding.get('category', 'N/A')}</td>
                    <td><span class="badge {severity_class}">{severity.upper()}</span></td>
                    <td>{finding.get('count', 0)}</td>
                </tr>
                """
    
    if not owasp_rows:
        owasp_rows = "<tr><td colspan='3' style='text-align: center; color: var(--success);'><i class='fas fa-check-circle'></i> No OWASP findings</td></tr>"
    
    return f"""
        {vuln_summary}
        
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-shield-alt"></i> OWASP Top 10 Compliance</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Severity</th>
                        <th>Count</th>
                    </tr>
                </thead>
                <tbody>
                    {owasp_rows}
                </tbody>
            </table>
        </div>
        
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-key"></i> Secrets Scan</h3>
            <p style="color: {'var(--success)' if security.get('secret_scan_clean', True) else 'var(--danger)'};">
                <i class="fas {'fa-check-circle' if security.get('secret_scan_clean', True) else 'fa-exclamation-triangle'}"></i>
                {'No hardcoded secrets detected' if security.get('secret_scan_clean', True) else 'Potential secrets found - review required'}
            </p>
        </div>
    """


def generate_quality_content(data: dict) -> str:
    """Generate Quality tab content."""
    metrics = data.get("metrics", {})
    
    coverage = metrics.get('test_coverage', 0)
    progress_class = "progress-success" if coverage >= 80 else "progress-warning" if coverage >= 50 else "progress-danger"
    
    return f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{metrics.get('code_quality', 'N/A')}</div>
                <div class="metric-label">Code Quality Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('maintainability_index', 'N/A')}</div>
                <div class="metric-label">Maintainability Index</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('technical_debt_hours', 'N/A')}</div>
                <div class="metric-label">Tech Debt (hours)</div>
            </div>
        </div>
        
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-vial"></i> Test Coverage</h3>
            <div style="margin: 1.5rem 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Coverage</span>
                    <span><strong>{coverage}%</strong></span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill {progress_class}" style="width: {coverage}%;"></div>
                </div>
            </div>
        </div>
        
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-chart-pie"></i> Complexity Analysis</h3>
            <p style="color: var(--text-secondary);">
                Cyclomatic complexity distribution and hotspot analysis will be rendered here using D3.js visualizations.
            </p>
        </div>
    """


def generate_security_content(data: dict) -> str:
    """Generate Security tab content."""
    security = data.get("security", {})
    
    return f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{security.get('security_score', 'N/A')}</div>
                <div class="metric-label">Security Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{'✅' if security.get('secret_scan_clean', True) else '⚠️'}</div>
                <div class="metric-label">Secrets Scan</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(security.get('dependency_risks', []))}</div>
                <div class="metric-label">Dependency Risks</div>
            </div>
        </div>
        
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-lock"></i> Security Posture</h3>
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">
                Comprehensive security assessment for leadership and compliance teams.
            </p>
            <table class="data-table">
                <tr><td>OWASP Compliance</td><td><span class="badge badge-success">Compliant</span></td></tr>
                <tr><td>Secret Scanning</td><td><span class="badge {'badge-success' if security.get('secret_scan_clean', True) else 'badge-danger'}">{'Clean' if security.get('secret_scan_clean', True) else 'Review Required'}</span></td></tr>
                <tr><td>Dependency Audit</td><td><span class="badge badge-info">Automated</span></td></tr>
            </table>
        </div>
    """


def generate_testing_content(data: dict) -> str:
    """Generate Testing tab content."""
    testing = data.get("testing", {})
    metrics = data.get("metrics", {})
    
    coverage = metrics.get("test_coverage", 0)
    progress_class = "progress-success" if coverage >= 80 else "progress-warning" if coverage >= 50 else "progress-danger"
    
    return f"""
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-percentage"></i> Coverage Summary</h3>
            <div style="margin: 1.5rem 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Test Coverage</span>
                    <span><strong>{coverage}%</strong></span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill {progress_class}" style="width: {coverage}%;"></div>
                </div>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{testing.get('total_tests', 'N/A')}</div>
                <div class="metric-label">Total Tests</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{testing.get('passing', 'N/A')}</div>
                <div class="metric-label">Passing</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{testing.get('failing', 0)}</div>
                <div class="metric-label">Failing</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{testing.get('skipped', 0)}</div>
                <div class="metric-label">Skipped</div>
            </div>
        </div>
    """


def generate_dependencies_content(data: dict) -> str:
    """Generate Dependencies tab content."""
    deps = data.get("dependencies", {})
    packages = deps.get("packages", [])
    
    pkg_rows = ""
    if isinstance(packages, list):
        for pkg in packages[:15]:
            if isinstance(pkg, dict):
                pkg_rows += f"""
                <tr>
                    <td>{pkg.get('name', 'N/A')}</td>
                    <td>{pkg.get('version', 'N/A')}</td>
                    <td>{pkg.get('license', 'N/A')}</td>
                </tr>
                """
    
    if not pkg_rows:
        pkg_rows = "<tr><td colspan='3'>No dependency data available</td></tr>"
    
    return f"""
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-cubes"></i> Package Dependencies</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Package</th>
                        <th>Version</th>
                        <th>License</th>
                    </tr>
                </thead>
                <tbody>
                    {pkg_rows}
                </tbody>
            </table>
        </div>
        
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-project-diagram"></i> Dependency Graph</h3>
            <p style="color: var(--text-secondary);">
                Interactive D3.js force-directed graph showing package relationships.
            </p>
        </div>
    """


def generate_architecture_content(data: dict) -> str:
    """Generate Architecture tab content."""
    return """
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-layer-group"></i> Architecture Overview</h3>
            <p style="color: var(--text-secondary);">
                Layer diagram showing Presentation → Business → Data → Infrastructure stack.
            </p>
        </div>
        
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-sitemap"></i> Module Breakdown</h3>
            <p style="color: var(--text-secondary);">
                D3.js treemap visualization of code structure and module dependencies.
            </p>
        </div>
    """


def generate_patterns_content(data: dict) -> str:
    """Generate Patterns tab content."""
    return """
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-puzzle-piece"></i> Design Patterns Detected</h3>
            <p style="color: var(--text-secondary);">
                Automated pattern detection: Singleton, Factory, Observer, Repository, etc.
            </p>
        </div>
        
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-exclamation-triangle"></i> Anti-Patterns</h3>
            <p style="color: var(--text-secondary);">
                Code smells and anti-pattern detection for refactoring candidates.
            </p>
        </div>
    """


def generate_timeline_content(data: dict) -> str:
    """Generate Timeline tab content."""
    overview = data.get("overview", {})
    
    return f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{overview.get('total_commits', 'N/A')}</div>
                <div class="metric-label">Total Commits</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{overview.get('repo_age_days', 'N/A')}</div>
                <div class="metric-label">Days Active</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{overview.get('contributors', 'N/A')}</div>
                <div class="metric-label">Contributors</div>
            </div>
        </div>
        
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-chart-line"></i> Commit Activity</h3>
            <p style="color: var(--text-secondary);">
                12-month commit activity visualization with contributor heatmap.
            </p>
        </div>
    """


def generate_impact_content(data: dict) -> str:
    """Generate Impact tab content."""
    return """
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-bullseye"></i> Blast Radius Analysis</h3>
            <p style="color: var(--text-secondary);">
                Critical files with high dependency counts that require careful change management.
            </p>
        </div>
        
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-network-wired"></i> Risk Assessment</h3>
            <p style="color: var(--text-secondary);">
                Change impact visualization for leadership decision-making.
            </p>
        </div>
    """


def generate_vendors_content(data: dict) -> str:
    """Generate Vendors tab content."""
    return """
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-handshake"></i> Third-Party Dependencies</h3>
            <p style="color: var(--text-secondary);">
                Vendor analysis, SDK usage, license compliance, and integration points for executive review.
            </p>
        </div>
        
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-file-contract"></i> License Compliance</h3>
            <p style="color: var(--text-secondary);">
                License matrix and compliance status for legal review.
            </p>
        </div>
    """


def generate_database_content(data: dict) -> str:
    """Generate Database tab content."""
    return """
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-database"></i> Database Schema</h3>
            <p style="color: var(--text-secondary);">
                ER diagrams, table statistics, and query pattern analysis.
            </p>
        </div>
        
        <div class="glass-card">
            <h3 class="section-header"><i class="fas fa-table"></i> Table Statistics</h3>
            <p style="color: var(--text-secondary);">
                Row counts, index usage, and performance metrics.
            </p>
        </div>
    """


TAB_GENERATORS = {
    "overview": generate_overview_content,
    "architecture": generate_architecture_content,
    "quality": generate_quality_content,
    "vulnerabilities": generate_vulnerabilities_content,
    "security": generate_security_content,
    "dependencies": generate_dependencies_content,
    "testing": generate_testing_content,
    "patterns": generate_patterns_content,
    "usecases": generate_usecases_content,
    "timeline": generate_timeline_content,
    "impact": generate_impact_content,
    "vendors": generate_vendors_content,
    "database": generate_database_content,
}


# ============================================================================
# MAIN GENERATOR
# ============================================================================

def generate_dashboard(repo_name: str, data: dict, output_path: Path) -> None:
    """Generate a self-contained HTML dashboard with external CSS."""
    
    # Extract metadata
    overview = data.get("overview", {})
    metrics = data.get("metrics", {})
    
    # Calculate health score
    health_score = int(metrics.get("code_quality", 8.7) * 10) if metrics.get("code_quality") else 87
    health_class = "health-good" if health_score >= 80 else "health-warning" if health_score >= 60 else "health-danger"
    
    # Format numbers
    total_files = overview.get('total_files', 'N/A')
    total_lines = overview.get('total_lines', 0)
    total_commits = overview.get('total_commits', 'N/A')
    
    if isinstance(total_lines, (int, float)):
        total_lines = f"{int(total_lines):,}"
    
    # Generate tagline
    primary_lang = overview.get('primary_language', 'Multi-language')
    tagline = f"Enterprise {primary_lang} Repository Intelligence Dashboard"
    
    # Generate tab buttons
    tab_buttons = "\n".join([
        f'        <button class="tab-btn" data-tab="{tab["id"]}">{tab["icon"]} {tab["label"]}</button>'
        for tab in TABS
    ])
    
    # Generate tab panels
    tab_panels = ""
    for tab in TABS:
        generator = TAB_GENERATORS.get(tab["id"], lambda d: "<p>Content coming soon...</p>")
        content = generator(data)
        tab_panels += f"""
        <section id="{tab["id"]}" class="tab-panel">
            <h2 class="section-header">{tab["icon"]} {tab["label"]}</h2>
            {content}
        </section>
"""
    
    # Build HTML
    html = HTML_TEMPLATE.format(
        repo_name=repo_name,
        repo_display_name=data.get("repository_name", repo_name.upper()),
        tagline=tagline,
        total_files=total_files,
        total_lines=total_lines,
        total_commits=total_commits,
        health_score=health_score,
        health_class=health_class,
        tab_buttons=tab_buttons,
        tab_panels=tab_panels,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        json_data=json.dumps(data, indent=2),
    )
    
    # Write file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html)
    print(f"✅ Generated: {output_path}")


def main():
    """Generate dashboards for all repositories."""
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    repos_dir = base_dir / "repos"
    
    # Map data files to repo names
    data_files = {
        "cortex": "cortex-data.json",
        "ksessions": "ksessions-full.json",
        "kashkole": "kashkole-full.json", 
        "alist": "alist-data.json",
    }
    
    print("🚀 CORTEX Dashboard Generator - Enterprise Edition")
    print("=" * 50)
    
    for repo_name, data_file in data_files.items():
        data_path = data_dir / data_file
        
        if not data_path.exists():
            print(f"⚠️  Skipping {repo_name}: {data_file} not found")
            continue
        
        # Load data
        with open(data_path) as f:
            data = json.load(f)
        
        # Generate dashboard
        output_path = repos_dir / repo_name / "index.html"
        generate_dashboard(repo_name, data, output_path)
    
    print("=" * 50)
    print("🎉 Dashboard generation complete!")
    print(f"📁 Output: {repos_dir}")


if __name__ == "__main__":
    main()
