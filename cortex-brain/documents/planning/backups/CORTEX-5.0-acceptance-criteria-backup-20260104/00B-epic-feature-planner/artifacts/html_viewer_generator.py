"""
HTML Plan Viewer Generator for Epic & Feature Planning System.

Generates static glassmorphism-styled HTML viewers for epic and feature plans
with real-time progress tracking via JSON polling.

Author: Asif Hussain
Created: January 4, 2026
Part of: CORTEX-5.0 Sub-Plan 00B Phase 00
"""

from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ViewerConfig:
    """Configuration for HTML viewer generation."""
    plan_id: str
    plan_name: str
    plan_type: str  # "epic" or "feature"
    tracking_file: str  # Relative path to JSON tracker
    refresh_interval_ms: int = 5000  # Auto-refresh interval


class HTMLViewerGenerator:
    """
    Generate static HTML plan viewers with glassmorphism styling.
    
    Generates self-contained HTML files that:
    - Auto-refresh progress from JSON tracker every 5 seconds
    - Use glassmorphism design standard (T1 - subtle animation)
    - Are mobile-friendly and WCAG AA accessible
    - Require no external dependencies (embedded CSS/JS)
    
    Examples:
        >>> generator = HTMLViewerGenerator()
        >>> config = ViewerConfig(
        ...     plan_id="cortex-v5-gap-remediation",
        ...     plan_name="CORTEX v5 Gap Remediation",
        ...     plan_type="epic",
        ...     tracking_file="tracking/epic-progress-tracker.json"
        ... )
        >>> html = generator.generate_epic_viewer(config)
        >>> Path("CORTEX-5.0-plan-viewer.html").write_text(html)
    """
    
    def generate_epic_viewer(self, config: ViewerConfig) -> str:
        """
        Generate HTML for epic plan viewer.
        
        Args:
            config: Viewer configuration
            
        Returns:
            Complete HTML document as string
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.plan_name} - Epic Progress</title>
    {self._get_glassmorphism_styles()}
</head>
<body>
    <div class="epic-container">
        <!-- Epic Header -->
        <div class="epic-header">
            <h1 class="epic-title">🎯 {config.plan_name}</h1>
            <p class="epic-subtitle">Strategic Multi-Phase Epic Plan</p>
        </div>
        
        <!-- Epic Stats -->
        <div class="glass-panel">
            <div class="epic-stats">
                <div class="stat-card">
                    <div class="stat-value" id="epic-progress">0%</div>
                    <div class="stat-label">Overall Progress</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="child-plans-complete">0/0</div>
                    <div class="stat-label">Plans Complete</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="total-phases">0/0</div>
                    <div class="stat-label">Phases Complete</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="estimated-days">0d</div>
                    <div class="stat-label">Estimated Duration</div>
                </div>
            </div>
            
            <!-- Overall Progress Bar -->
            <div class="progress-bar">
                <div class="progress-bar-fill" id="epic-progress-bar" style="width: 0%">
                    <span id="epic-progress-text">0% Complete</span>
                </div>
            </div>
        </div>
        
        <!-- Child Plans Grid -->
        <div class="glass-panel">
            <h2>📋 Child Feature Plans</h2>
            <div class="child-plans-grid" id="child-plans-container">
                <!-- Child plan cards dynamically populated -->
            </div>
        </div>
    </div>
    
    <!-- Auto-Refresh Indicator -->
    <div class="auto-refresh-indicator pulse">
        🔄 Auto-refreshing every {config.refresh_interval_ms // 1000}s
    </div>
    
    {self._get_epic_javascript(config)}
</body>
</html>"""
    
    def generate_feature_viewer(self, config: ViewerConfig) -> str:
        """
        Generate HTML for feature plan viewer.
        
        Args:
            config: Viewer configuration
            
        Returns:
            Complete HTML document as string
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.plan_name} - Feature Progress</title>
    {self._get_glassmorphism_styles()}
</head>
<body>
    <div class="feature-container">
        <!-- Feature Header -->
        <div class="feature-header">
            <h1 class="feature-title">📋 {config.plan_name}</h1>
            <div class="feature-meta">
                <span class="meta-item" id="feature-status">⏳ Not Started</span>
                <span class="meta-item" id="feature-duration">Duration: TBD</span>
            </div>
        </div>
        
        <!-- Feature Stats -->
        <div class="glass-panel">
            <div class="feature-stats">
                <div class="stat-card">
                    <div class="stat-value" id="feature-progress">0%</div>
                    <div class="stat-label">Progress</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="phases-complete">0/0</div>
                    <div class="stat-label">Phases Complete</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="tasks-complete">0/0</div>
                    <div class="stat-label">Tasks Complete</div>
                </div>
            </div>
            
            <!-- Overall Progress Bar -->
            <div class="progress-bar">
                <div class="progress-bar-fill" id="feature-progress-bar" style="width: 0%">
                    <span id="feature-progress-text">0% Complete</span>
                </div>
            </div>
        </div>
        
        <!-- Phases List -->
        <div class="glass-panel">
            <h2>🔄 Phases</h2>
            <div class="phases-list" id="phases-container">
                <!-- Phase cards dynamically populated -->
            </div>
        </div>
        
        <!-- Artifacts & Reports -->
        <div class="glass-panel">
            <h2>📁 Artifacts & Reports</h2>
            <div class="artifacts-grid">
                <a href="context/" class="artifact-link">📖 Context</a>
                <a href="artifacts/" class="artifact-link">🔧 Artifacts</a>
                <a href="reports/" class="artifact-link">📊 Reports</a>
                <a href="tracking/" class="artifact-link">📈 Tracking</a>
            </div>
        </div>
    </div>
    
    <!-- Auto-Refresh Indicator -->
    <div class="auto-refresh-indicator pulse">
        🔄 Auto-refreshing every {config.refresh_interval_ms // 1000}s
    </div>
    
    {self._get_feature_javascript(config)}
</body>
</html>"""
    
    def _get_glassmorphism_styles(self) -> str:
        """Get embedded CSS styles (glassmorphism T1 standard)."""
        return """<style>
        /* Glassmorphism Design Standard - Tier 1 (Subtle Animation) */
        :root {
            --glass-bg: rgba(15, 23, 42, 0.7);
            --glass-border: rgba(255, 255, 255, 0.1);
            --progress-gradient: linear-gradient(90deg, #00d4ff 0%, #a855f7 100%);
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: var(--text-primary);
            padding: 2rem;
            min-height: 100vh;
            line-height: 1.6;
        }
        
        .epic-container, .feature-container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .glass-panel {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .glass-panel:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);
        }
        
        .epic-header, .feature-header {
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .epic-title, .feature-title {
            font-size: clamp(2rem, 5vw, 3rem);
            font-weight: 700;
            background: linear-gradient(90deg, #00d4ff, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }
        
        .epic-subtitle {
            font-size: 1.125rem;
            color: var(--text-secondary);
        }
        
        .feature-meta {
            display: flex;
            gap: 1.5rem;
            justify-content: center;
            margin-top: 1rem;
            flex-wrap: wrap;
        }
        
        .meta-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.875rem;
        }
        
        .epic-stats, .feature-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            transition: background 0.2s ease;
        }
        
        .stat-card:hover {
            background: rgba(255, 255, 255, 0.08);
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 0.25rem;
        }
        
        .stat-label {
            font-size: 0.875rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .progress-bar {
            height: 40px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            overflow: hidden;
            position: relative;
            margin: 1rem 0;
        }
        
        .progress-bar-fill {
            height: 100%;
            background: var(--progress-gradient);
            border-radius: 20px;
            transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            position: relative;
            min-width: 60px;
        }
        
        .progress-bar-fill::before {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255, 255, 255, 0.3),
                transparent
            );
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        .child-plans-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1rem;
        }
        
        .child-plan-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 1.5rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .child-plan-card:hover {
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(0, 212, 255, 0.3);
            transform: translateY(-2px);
        }
        
        .child-plan-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }
        
        .child-plan-header h3 {
            font-size: 1.125rem;
            margin: 0;
        }
        
        .child-plan-status {
            font-size: 1.5rem;
        }
        
        .child-plan-meta {
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin: 0.5rem 0;
        }
        
        .dependency-tag {
            display: inline-block;
            background: rgba(168, 85, 247, 0.2);
            color: #c084fc;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            margin-top: 0.5rem;
        }
        
        .phases-list {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .phase-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.2s ease;
        }
        
        .phase-card:hover {
            background: rgba(255, 255, 255, 0.06);
        }
        
        .phase-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }
        
        .phase-number {
            font-size: 1.5rem;
            font-weight: 700;
            color: #00d4ff;
        }
        
        .phase-status-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status-complete { background: rgba(16, 185, 129, 0.2); color: var(--success-color); }
        .status-in-progress { background: rgba(0, 212, 255, 0.2); color: #00d4ff; }
        .status-not-started { background: rgba(148, 163, 184, 0.2); color: var(--text-secondary); }
        .status-blocked { background: rgba(239, 68, 68, 0.2); color: var(--error-color); }
        
        .artifacts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }
        
        .artifact-link {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            background: rgba(255, 255, 255, 0.05);
            padding: 1rem;
            border-radius: 12px;
            text-decoration: none;
            color: var(--text-primary);
            transition: all 0.2s ease;
            font-weight: 500;
        }
        
        .artifact-link:hover {
            background: rgba(0, 212, 255, 0.1);
            transform: translateY(-2px);
        }
        
        .auto-refresh-indicator {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: rgba(0, 212, 255, 0.2);
            border: 1px solid rgba(0, 212, 255, 0.4);
            border-radius: 24px;
            padding: 0.75rem 1.5rem;
            font-size: 0.875rem;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }
            
            .glass-panel {
                padding: 1.5rem;
            }
            
            .child-plans-grid {
                grid-template-columns: 1fr;
            }
            
            .auto-refresh-indicator {
                bottom: 1rem;
                right: 1rem;
                padding: 0.5rem 1rem;
            }
        }
        
        /* Accessibility */
        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
    </style>"""
    
    def _get_epic_javascript(self, config: ViewerConfig) -> str:
        """Get embedded JavaScript for epic viewer."""
        return f"""<script>
        // Epic Plan Viewer - Auto-Refresh System
        const TRACKING_FILE = '{config.tracking_file}';
        const REFRESH_INTERVAL = {config.refresh_interval_ms};
        
        async function loadEpicProgress() {{
            try {{
                const response = await fetch(TRACKING_FILE + '?t=' + Date.now());
                const data = await response.json();
                
                // Update epic stats
                document.getElementById('epic-progress').textContent = 
                    Math.round(data.overall_progress) + '%';
                document.getElementById('child-plans-complete').textContent = 
                    `${{data.completed_plans}}/${{data.total_plans}}`;
                document.getElementById('total-phases').textContent = 
                    `${{data.completed_phases}}/${{data.total_phases}}`;
                document.getElementById('estimated-days').textContent = 
                    data.estimated_days + 'd';
                
                // Update progress bar
                const progressBar = document.getElementById('epic-progress-bar');
                progressBar.style.width = data.overall_progress + '%';
                document.getElementById('epic-progress-text').textContent = 
                    Math.round(data.overall_progress) + '% Complete';
                
                // Render child plans
                renderChildPlans(data.child_plans || []);
                
            }} catch (error) {{
                console.error('Failed to load epic progress:', error);
            }}
        }}
        
        function renderChildPlans(childPlans) {{
            const container = document.getElementById('child-plans-container');
            container.innerHTML = '';
            
            childPlans.forEach(plan => {{
                const card = document.createElement('div');
                card.className = 'child-plan-card';
                card.onclick = () => openChildPlanViewer(plan.viewer_url);
                
                const dependencies = (plan.dependencies || []).join(', ');
                
                card.innerHTML = `
                    <div class="child-plan-header">
                        <h3>${{plan.order}}. ${{plan.name}}</h3>
                        <span class="child-plan-status">${{plan.status_emoji || '⏳'}}</span>
                    </div>
                    <div class="progress-bar" style="height: 20px; margin: 1rem 0;">
                        <div class="progress-bar-fill" style="width: ${{plan.progress || 0}}%; font-size: 0.75rem;">
                            ${{Math.round(plan.progress || 0)}}%
                        </div>
                    </div>
                    <p class="child-plan-meta">
                        ${{plan.phases_complete || 0}}/${{plan.total_phases || 0}} phases • ${{plan.duration || 'TBD'}}
                    </p>
                    ${{dependencies ? `<div class="dependency-tag">Depends on: ${{dependencies}}</div>` : ''}}
                `;
                
                container.appendChild(card);
            }});
        }}
        
        function openChildPlanViewer(viewerUrl) {{
            if (viewerUrl) {{
                window.open(viewerUrl, '_blank');
            }}
        }}
        
        // Auto-refresh
        setInterval(loadEpicProgress, REFRESH_INTERVAL);
        
        // Initial load
        loadEpicProgress();
    </script>"""
    
    def _get_feature_javascript(self, config: ViewerConfig) -> str:
        """Get embedded JavaScript for feature viewer."""
        return f"""<script>
        // Feature Plan Viewer - Auto-Refresh System
        const TRACKING_FILE = '{config.tracking_file}';
        const REFRESH_INTERVAL = {config.refresh_interval_ms};
        
        async function loadFeatureProgress() {{
            try {{
                const response = await fetch(TRACKING_FILE + '?t=' + Date.now());
                const data = await response.json();
                
                // Update feature stats
                document.getElementById('feature-progress').textContent = 
                    Math.round(data.progress || 0) + '%';
                document.getElementById('phases-complete').textContent = 
                    `${{data.completed_phases || 0}}/${{data.total_phases || 0}}`;
                
                // Calculate total tasks
                const phases = data.phases || [];
                const totalTasks = phases.reduce((sum, p) => sum + (p.tasks?.length || 0), 0);
                const completeTasks = phases.reduce((sum, p) => 
                    sum + (p.tasks?.filter(t => t.status === 'complete').length || 0), 0);
                document.getElementById('tasks-complete').textContent = 
                    `${{completeTasks}}/${{totalTasks}}`;
                
                // Update progress bar
                const progressBar = document.getElementById('feature-progress-bar');
                progressBar.style.width = (data.progress || 0) + '%';
                document.getElementById('feature-progress-text').textContent = 
                    Math.round(data.progress || 0) + '% Complete';
                
                // Update status
                document.getElementById('feature-status').textContent = 
                    getStatusText(data.status);
                
                // Render phases
                renderPhases(phases);
                
            }} catch (error) {{
                console.error('Failed to load feature progress:', error);
            }}
        }}
        
        function getStatusText(status) {{
            const statusMap = {{
                'not_started': '⏳ Not Started',
                'in_progress': '🔄 In Progress',
                'blocked': '🔒 Blocked',
                'complete': '✅ Complete',
                'failed': '❌ Failed'
            }};
            return statusMap[status] || '⏳ Not Started';
        }}
        
        function renderPhases(phases) {{
            const container = document.getElementById('phases-container');
            container.innerHTML = '';
            
            phases.forEach(phase => {{
                const card = document.createElement('div');
                card.className = 'phase-card';
                
                const statusClass = `status-${{(phase.status || 'not_started').replace('_', '-')}}`;
                
                card.innerHTML = `
                    <div class="phase-header">
                        <div>
                            <span class="phase-number">Phase ${{phase.number}}</span>
                            <span> - ${{phase.name}}</span>
                        </div>
                        <span class="phase-status-badge ${{statusClass}}">${{phase.status || 'not started'}}</span>
                    </div>
                    <div class="progress-bar" style="height: 24px; margin: 1rem 0;">
                        <div class="progress-bar-fill" style="width: ${{phase.progress || 0}}%;">
                            ${{Math.round(phase.progress || 0)}}%
                        </div>
                    </div>
                    <p style="color: var(--text-secondary); font-size: 0.875rem;">
                        ${{phase.description || ''}}
                    </p>
                `;
                
                container.appendChild(card);
            }});
        }}
        
        // Auto-refresh
        setInterval(loadFeatureProgress, REFRESH_INTERVAL);
        
        // Initial load
        loadFeatureProgress();
    </script>"""


# Convenience functions
def generate_epic_viewer(
    plan_id: str,
    plan_name: str,
    output_path: Path,
    tracking_file: str = "tracking/epic-progress-tracker.json"
) -> Path:
    """
    Generate and save epic viewer HTML.
    
    Args:
        plan_id: Plan identifier
        plan_name: Display name
        output_path: Where to save HTML file
        tracking_file: Relative path to JSON tracker
        
    Returns:
        Path to generated HTML file
    """
    generator = HTMLViewerGenerator()
    config = ViewerConfig(
        plan_id=plan_id,
        plan_name=plan_name,
        plan_type="epic",
        tracking_file=tracking_file
    )
    html = generator.generate_epic_viewer(config)
    output_path.write_text(html)
    return output_path


def generate_feature_viewer(
    plan_id: str,
    plan_name: str,
    output_path: Path,
    tracking_file: str = "tracking/progress-tracker.json"
) -> Path:
    """
    Generate and save feature viewer HTML.
    
    Args:
        plan_id: Plan identifier
        plan_name: Display name
        output_path: Where to save HTML file
        tracking_file: Relative path to JSON tracker
        
    Returns:
        Path to generated HTML file
    """
    generator = HTMLViewerGenerator()
    config = ViewerConfig(
        plan_id=plan_id,
        plan_name=plan_name,
        plan_type="feature",
        tracking_file=tracking_file
    )
    html = generator.generate_feature_viewer(config)
    output_path.write_text(html)
    return output_path


if __name__ == "__main__":
    # Demo usage
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python html_viewer_generator.py <type> <plan_id> <plan_name> [output_path]")
        print("  type: 'epic' or 'feature'")
        sys.exit(1)
    
    viewer_type = sys.argv[1]
    plan_id = sys.argv[2]
    plan_name = sys.argv[3]
    output_path = Path(sys.argv[4]) if len(sys.argv) > 4 else Path(f"{plan_id}-plan-viewer.html")
    
    if viewer_type == "epic":
        result = generate_epic_viewer(plan_id, plan_name, output_path)
        print(f"✅ Generated epic viewer: {result}")
    elif viewer_type == "feature":
        result = generate_feature_viewer(plan_id, plan_name, output_path)
        print(f"✅ Generated feature viewer: {result}")
    else:
        print(f"❌ Invalid type: {viewer_type} (must be 'epic' or 'feature')")
        sys.exit(1)
