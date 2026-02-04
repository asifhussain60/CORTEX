#!/usr/bin/env python3
"""
Generate KSESSIONS dashboard matching KASHKOLE archived specifications.
9 tabs, logo left, title right, glassmorphism theme, self-contained.
"""

import json
from pathlib import Path
from datetime import datetime

def load_ksessions_data():
    """Load KSESSIONS data from current dashboard"""
    ksessions_html = Path("company/dashboards/repos/ksessions/index.html")
    with open(ksessions_html, 'r') as f:
        content = f.read()
    
    # Extract JSON data
    start = content.find('id="dashboard-data">')
    end = content.find('</script>', start)
    json_str = content[start+20:end].strip()
    return json.loads(json_str)

def load_logo_base64():
    """Load CORTEX logo as base64"""
    logo_path = Path("company/dashboards/assets/images/CORTEX-logo-200.png")
    if logo_path.exists():
        with open(logo_path, 'rb') as f:
            import base64
            return base64.b64encode(f.read()).decode('utf-8')
    return ""

def generate_dashboard(data, logo_base64):
    """Generate complete self-contained dashboard"""
    
    # Extract metrics
    health_score = data.get('metrics', {}).get('health_score', 0)
    total_files = data.get('overview', {}).get('total_files', 0)
    lines_of_code = data.get('overview', {}).get('lines_of_code', 0)
    classes = data.get('metrics', {}).get('total_classes', 0)
    functions = data.get('metrics', {}).get('total_functions', 0)
    security_issues = data.get('security', {}).get('total_count', 0)
    
    # Determine health badge
    if health_score >= 80:
        health_badge = f'✅ Health Score: {health_score}/100 - Excellent'
        health_color = '#22c55e'
    elif health_score >= 60:
        health_badge = f'⚠️ Health Score: {health_score}/100 - Needs Attention'
        health_color = '#f59e0b'
    else:
        health_badge = f'🔴 Health Score: {health_score}/100 - Critical'
        health_color = '#ef4444'
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KSESSIONS - Modern Dashboard | CORTEX v9.0</title>
    
    <!-- Preload Inter Font -->
    <link rel="preload" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" as="style">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        /* ===== CORTEX Glassmorphism Universal Dashboard Theme ===== */
        
        /* Root Variables */
        :root {{
            /* Typography Scale */
            --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            --font-size-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
            --font-size-sm: clamp(0.875rem, 0.825rem + 0.25vw, 1rem);
            --font-size-base: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);
            --font-size-lg: clamp(1.125rem, 1.05rem + 0.375vw, 1.25rem);
            --font-size-xl: clamp(1.25rem, 1.15rem + 0.5vw, 1.5rem);
            --font-size-2xl: clamp(1.5rem, 1.35rem + 0.75vw, 2rem);
            --font-size-3xl: clamp(1.875rem, 1.65rem + 1.125vw, 2.5rem);
            
            /* Font Weights */
            --font-weight-light: 300;
            --font-weight-normal: 400;
            --font-weight-medium: 500;
            --font-weight-semibold: 600;
            --font-weight-bold: 700;
            
            /* Line Heights */
            --line-height-tight: 1.25;
            --line-height-normal: 1.5;
            --line-height-relaxed: 1.75;
            
            /* Letter Spacing */
            --letter-spacing-tight: -0.025em;
            --letter-spacing-normal: 0;
            --letter-spacing-wide: 0.025em;
            
            /* Content Width */
            --content-width-narrow: 45ch;
            --content-width-normal: 65ch;
            --content-width-wide: 80ch;
            --content-width-full: 100%;
            
            /* Margins */
            --margin-xs: clamp(0.25rem, 0.2rem + 0.25vw, 0.5rem);
            --margin-sm: clamp(0.5rem, 0.45rem + 0.25vw, 0.75rem);
            --margin-md: clamp(0.75rem, 0.65rem + 0.5vw, 1.25rem);
            --margin-lg: clamp(1rem, 0.85rem + 0.75vw, 1.75rem);
            --margin-xl: clamp(1.5rem, 1.25rem + 1.25vw, 2.75rem);
            
            /* Color Palette - Dark Blue Glassmorphism */
            --bg-primary: #0a1428;
            --bg-secondary: #0d1a30;
            --bg-tertiary: #122038;
            
            /* Glassmorphism */
            --glass-bg: rgba(26, 31, 58, 0.7);
            --glass-border: rgba(255, 255, 255, 0.1);
            --glass-hover: rgba(26, 31, 58, 0.85);
            
            /* Text Colors */
            --text-primary: #ffffff;
            --text-secondary: #a0a6c0;
            --text-muted: #6b7280;
            
            /* Accent Colors */
            --accent-primary: #4d8cff;
            --accent-secondary: #7fb3ff;
            --accent-tertiary: #3b82f6;
            
            /* Status Colors */
            --color-success: #22c55e;
            --color-warning: #f59e0b;
            --color-error: #ef4444;
            --color-info: #06b6d4;
            
            /* Shadows */
            --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.15);
            --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.2);
            --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.3);
            --shadow-xl: 0 16px 64px rgba(0, 0, 0, 0.4);
            
            /* Border Radius */
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 24px;
            
            /* Transitions */
            --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
            --transition-base: 300ms cubic-bezier(0.4, 0, 0.2, 1);
            --transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
            
            /* Backdrop Blur */
            --blur-sm: blur(8px);
            --blur-md: blur(16px);
            --blur-lg: blur(24px);
        }}
        
        /* Global Styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: var(--font-family);
            font-size: var(--font-size-base);
            line-height: var(--line-height-normal);
            color: var(--text-primary);
            background: var(--bg-primary);
            background-image: 
                radial-gradient(at 0% 0%, rgba(77, 140, 255, 0.15) 0, transparent 50%),
                radial-gradient(at 100% 100%, rgba(127, 179, 255, 0.1) 0, transparent 50%);
            background-attachment: fixed;
            min-height: 100vh;
            overflow-x: hidden;
        }}
        
        /* Dashboard Container */
        .dashboard-container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 0;
        }}
        
        /* Header - Logo Left + Title Right */
        .dashboard-header {{
            display: flex;
            align-items: center;
            gap: 2rem;
            padding: 2rem;
            background: var(--glass-bg);
            border-bottom: 1px solid var(--glass-border);
            backdrop-filter: var(--blur-lg);
            -webkit-backdrop-filter: var(--blur-lg);
        }}
        
        .cortex-logo {{
            width: 200px;
            height: 200px;
            object-fit: contain;
            filter: drop-shadow(0 0 20px rgba(77, 140, 255, 0.4));
        }}
        
        .header-content {{
            flex: 1;
        }}
        
        .dashboard-title {{
            font-size: var(--font-size-3xl);
            font-weight: var(--font-weight-bold);
            color: var(--accent-primary);
            margin-bottom: 0.5rem;
            letter-spacing: var(--letter-spacing-tight);
            text-shadow: 0 0 30px rgba(77, 140, 255, 0.3);
        }}
        
        .dashboard-subtitle {{
            font-size: var(--font-size-lg);
            color: var(--text-secondary);
            margin-bottom: 1rem;
        }}
        
        .health-badge {{
            display: inline-block;
            padding: 0.5rem 1rem;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid {health_color};
            border-radius: var(--radius-md);
            color: {health_color};
            font-weight: var(--font-weight-semibold);
            font-size: var(--font-size-sm);
        }}
        
        /* Tabs */
        .tabs-container {{
            display: flex;
            gap: 0.5rem;
            padding: 1rem 2rem;
            background: var(--glass-bg);
            border-bottom: 1px solid var(--glass-border);
            backdrop-filter: var(--blur-md);
            -webkit-backdrop-filter: var(--blur-md);
            overflow-x: auto;
            scrollbar-width: thin;
            scrollbar-color: var(--accent-primary) var(--bg-secondary);
        }}
        
        .tabs-container::-webkit-scrollbar {{
            height: 6px;
        }}
        
        .tabs-container::-webkit-scrollbar-track {{
            background: var(--bg-secondary);
        }}
        
        .tabs-container::-webkit-scrollbar-thumb {{
            background: var(--accent-primary);
            border-radius: 3px;
        }}
        
        .tab-button {{
            padding: 0.75rem 1.5rem;
            background: transparent;
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            color: var(--text-secondary);
            font-size: var(--font-size-sm);
            font-weight: var(--font-weight-medium);
            cursor: pointer;
            transition: all var(--transition-base);
            white-space: nowrap;
        }}
        
        .tab-button:hover {{
            background: rgba(77, 140, 255, 0.1);
            border-color: var(--accent-primary);
            color: var(--accent-primary);
        }}
        
        .tab-button.active {{
            background: var(--accent-primary);
            border-color: var(--accent-primary);
            color: white;
            box-shadow: 0 0 20px rgba(77, 140, 255, 0.4);
        }}
        
        /* Tab Content */
        .tab-content {{
            display: none;
            padding: 2rem;
            animation: fadeIn var(--transition-base);
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        /* Section Panels */
        .section-panel {{
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-lg);
            padding: 2rem;
            margin-bottom: 2rem;
            backdrop-filter: var(--blur-md);
            -webkit-backdrop-filter: var(--blur-md);
            box-shadow: var(--shadow-md);
            transition: all var(--transition-base);
        }}
        
        .section-panel:hover {{
            border-color: rgba(77, 140, 255, 0.3);
            box-shadow: var(--shadow-lg);
        }}
        
        .section-title {{
            font-size: var(--font-size-xl);
            font-weight: var(--font-weight-bold);
            color: var(--accent-primary);
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid rgba(77, 140, 255, 0.2);
        }}
        
        /* Metrics Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .metric-card {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            padding: 1.5rem;
            text-align: center;
            transition: all var(--transition-base);
        }}
        
        .metric-card:hover {{
            background: rgba(255, 255, 255, 0.05);
            border-color: var(--accent-primary);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}
        
        .metric-value {{
            font-size: var(--font-size-2xl);
            font-weight: var(--font-weight-bold);
            color: var(--accent-primary);
            margin-bottom: 0.5rem;
        }}
        
        .metric-label {{
            font-size: var(--font-size-sm);
            color: var(--text-secondary);
        }}
        
        /* Interactive Cards */
        .interactive-card {{
            cursor: pointer;
        }}
        
        /* Project Description */
        .project-description {{
            color: var(--text-secondary);
            line-height: var(--line-height-relaxed);
            max-width: var(--content-width-wide);
        }}
        
        /* Footer */
        .dashboard-footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-muted);
            font-size: var(--font-size-sm);
            border-top: 1px solid var(--glass-border);
            background: var(--glass-bg);
            backdrop-filter: var(--blur-md);
            -webkit-backdrop-filter: var(--blur-md);
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .dashboard-header {{
                flex-direction: column;
                text-align: center;
            }}
            
            .cortex-logo {{
                width: 150px;
                height: 150px;
            }}
            
            .tabs-container {{
                padding: 1rem;
            }}
            
            .tab-content {{
                padding: 1rem;
            }}
            
            .section-panel {{
                padding: 1.5rem;
            }}
            
            .metrics-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- Compact Header -->
        <header class="dashboard-header">
            <img src="data:image/png;base64,{logo_base64}" alt="CORTEX Logo" class="cortex-logo">
            <div class="header-content">
                <h1 class="dashboard-title">KSESSIONS</h1>
                <p class="dashboard-subtitle">Enterprise Repository Intelligence Dashboard</p>
                <div class="health-badge">{health_badge}</div>
            </div>
        </header>

        <!-- Modern Tabs -->
        <nav class="tabs-container">
            <button class="tab-button active" onclick="switchTab('overview')">📊 Overview</button>
            <button class="tab-button" onclick="switchTab('dependencies')">🔗 Dependencies</button>
            <button class="tab-button" onclick="switchTab('timeline')">⏱️ Timeline</button>
            <button class="tab-button" onclick="switchTab('impact')">💥 Impact</button>
            <button class="tab-button" onclick="switchTab('security')">🔒 Security</button>
            <button class="tab-button" onclick="switchTab('techstack')">⚙️ Tech Stack</button>
            <button class="tab-button" onclick="switchTab('architecture')">🏗️ Architecture</button>
            <button class="tab-button" onclick="switchTab('quality')">✨ Quality</button>
            <button class="tab-button" onclick="switchTab('testing')">🧪 Testing</button>
        </nav>

        <!-- OVERVIEW TAB -->
        <div id="overview" class="tab-content active">
            <!-- Executive Summary -->
            <section class="section-panel" style="background: linear-gradient(135deg, rgba(77, 140, 255, 0.12) 0%, rgba(127, 179, 255, 0.05) 100%); border: 2px solid rgba(77, 140, 255, 0.4);">
                <h2 class="section-title" style="text-align: center;">📊 Executive Summary</h2>
                <div style="padding: 1.5rem; background: rgba(0,0,0,0.2); border-radius: 12px; line-height: 1.8;">
                    <p style="font-size: 1.1rem; color: var(--text-primary); margin: 0;">
                        <strong style="color: var(--accent-primary);">KSESSIONS</strong> is an enterprise repository with 
                        <strong style="color: #22c55e;">{total_files:,} files</strong> and <strong style="color: #22c55e;">{lines_of_code:,} LOC</strong>.
                        <br><br>
                        <strong style="color: {health_color};">Health Score: {health_score}/100</strong>
                        {' — Requires attention' if health_score < 80 else ' — Excellent condition'} with 
                        <strong style="color: #ef4444;">{security_issues} security issues</strong>.
                    </p>
                </div>
            </section>
            
            <!-- At-a-Glance Metrics -->
            <section class="section-panel">
                <h2 class="section-title">📈 At-a-Glance Metrics</h2>
                <div class="metrics-grid">
                    <div class="metric-card interactive-card" onclick="switchTab('dependencies')">
                        <div class="metric-value">{total_files:,}</div>
                        <div class="metric-label">Total Files</div>
                    </div>
                    <div class="metric-card interactive-card" onclick="switchTab('quality')">
                        <div class="metric-value">{classes}</div>
                        <div class="metric-label">Classes</div>
                    </div>
                    <div class="metric-card interactive-card" onclick="switchTab('quality')">
                        <div class="metric-value">{functions}</div>
                        <div class="metric-label">Functions</div>
                    </div>
                    <div class="metric-card interactive-card" onclick="switchTab('security')" style="background: rgba(239, 68, 68, 0.15);">
                        <div class="metric-value" style="color: #ef4444;">{security_issues}</div>
                        <div class="metric-label">Security Issues</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{lines_of_code:,}</div>
                        <div class="metric-label">Lines of Code</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{health_score}/100</div>
                        <div class="metric-label">Health Score</div>
                    </div>
                </div>
            </section>
        </div>

        <!-- DEPENDENCIES TAB -->
        <div id="dependencies" class="tab-content">
            <section class="section-panel">
                <h2 class="section-title">🔗 Dependencies</h2>
                <p class="project-description">Dependency analysis coming soon...</p>
            </section>
        </div>

        <!-- TIMELINE TAB -->
        <div id="timeline" class="tab-content">
            <section class="section-panel">
                <h2 class="section-title">⏱️ Timeline</h2>
                <p class="project-description">Timeline analysis coming soon...</p>
            </section>
        </div>

        <!-- IMPACT TAB -->
        <div id="impact" class="tab-content">
            <section class="section-panel">
                <h2 class="section-title">💥 Impact</h2>
                <p class="project-description">Impact analysis coming soon...</p>
            </section>
        </div>

        <!-- SECURITY TAB -->
        <div id="security" class="tab-content">
            <section class="section-panel">
                <h2 class="section-title">🔒 Security</h2>
                <p class="project-description">Security analysis coming soon...</p>
            </section>
        </div>

        <!-- TECH STACK TAB -->
        <div id="techstack" class="tab-content">
            <section class="section-panel">
                <h2 class="section-title">⚙️ Tech Stack</h2>
                <p class="project-description">Technology stack analysis coming soon...</p>
            </section>
        </div>

        <!-- ARCHITECTURE TAB -->
        <div id="architecture" class="tab-content">
            <section class="section-panel">
                <h2 class="section-title">🏗️ Architecture</h2>
                <p class="project-description">Architecture analysis coming soon...</p>
            </section>
        </div>

        <!-- QUALITY TAB -->
        <div id="quality" class="tab-content">
            <section class="section-panel">
                <h2 class="section-title">✨ Quality</h2>
                <p class="project-description">Quality metrics coming soon...</p>
            </section>
        </div>

        <!-- TESTING TAB -->
        <div id="testing" class="tab-content">
            <section class="section-panel">
                <h2 class="section-title">🧪 Testing</h2>
                <p class="project-description">Testing metrics coming soon...</p>
            </section>
        </div>

        <!-- Footer -->
        <footer class="dashboard-footer">
            <p>📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 📁 CORTEX Enterprise Dashboard v9.0</p>
            <p>Generated by CORTEX Intelligence Platform</p>
        </footer>
    </div>

    <!-- Embedded Data (for future use) -->
    <script id="dashboard-data" type="application/json">
{json.dumps(data, indent=2)}
    </script>

    <!-- Dashboard JavaScript -->
    <script>
        // Tab Switching
        function switchTab(tabName) {{
            // Hide all tabs
            const tabs = document.querySelectorAll('.tab-content');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Remove active from all buttons
            const buttons = document.querySelectorAll('.tab-button');
            buttons.forEach(btn => btn.classList.remove('active'));
            
            // Show selected tab
            const selectedTab = document.getElementById(tabName);
            if (selectedTab) {{
                selectedTab.classList.add('active');
            }}
            
            // Activate corresponding button
            const selectedButton = event.target;
            if (selectedButton && selectedButton.classList.contains('tab-button')) {{
                selectedButton.classList.add('active');
            }}
        }}
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {{
            console.log('KSESSIONS Dashboard v9.0 loaded');
            console.log('Health Score: {health_score}/100');
        }});
    </script>
</body>
</html>'''
    
    return html

def main():
    print("🚀 Generating KSESSIONS Dashboard v9.0")
    print("   Matching KASHKOLE archived specifications")
    print()
    
    # Load data
    print("📊 Loading KSESSIONS data...")
    data = load_ksessions_data()
    
    # Load logo
    print("🖼️  Loading CORTEX logo...")
    logo_base64 = load_logo_base64()
    
    # Generate dashboard
    print("🎨 Generating dashboard HTML...")
    html = generate_dashboard(data, logo_base64)
    
    # Save
    output_path = Path("company/dashboards/repos/ksessions/dashboard-v9.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"\n✅ Dashboard generated successfully!")
    print(f"   📁 Location: {output_path}")
    print(f"   📏 Size: {len(html):,} bytes ({len(html)/1024:.1f} KB)")
    print(f"   🏷️  9 tabs: Overview, Dependencies, Timeline, Impact, Security, Tech Stack, Architecture, Quality, Testing")
    print(f"   🎨 Theme: Glassmorphism with logo left, title right")
    print(f"   📦 Self-contained: All CSS/data embedded")

if __name__ == '__main__':
    main()
