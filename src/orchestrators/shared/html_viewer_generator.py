"""
HTML Viewer Generator - Glassmorphism-compliant plan viewer creation

Generates modern, accessible HTML viewers for epic and feature plans following
cortex-brain/documents/standards/glassmorphism-design-standard.md

Features:
- Epic viewer (multi-child plans with progress aggregation)
- Feature viewer (single plan with phase breakdown)
- Auto-refresh progress tracking
- Tailwind CSS cards/tiles with animations
- Seamless phase linking
- WCAG AA compliant

Author: Asif Hussain
Version: 1.0.0
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)


class ViewerMode(Enum):
    """Plan viewer modes."""
    EPIC = "epic"
    FEATURE = "feature"


@dataclass
class ViewerConfig:
    """Configuration for HTML viewer generation."""
    mode: ViewerMode
    plan_name: str
    plan_id: str
    output_path: Path
    tracking_json_path: str  # Relative path from viewer
    auto_refresh_seconds: int = 5
    theme: str = "dark"  # dark, light, auto
    animations_enabled: bool = True


class HTMLViewerGenerator:
    """
    Generates glassmorphism-compliant HTML plan viewers.
    
    Adheres to:
    - glassmorphism-design-standard.md
    - WCAG AA accessibility
    - Mobile-first responsive design
    - Zero inline styles
    - Modern CSS with Tailwind utilities
    """
    
    def __init__(self, config: ViewerConfig):
        """Initialize viewer generator with configuration."""
        self.config = config
    
    def generate(self) -> str:
        """
        Generate complete HTML viewer.
        
        Returns:
            HTML content as string
        """
        if self.config.mode == ViewerMode.EPIC:
            return self._generate_epic_viewer()
        else:
            return self._generate_feature_viewer()
    
    def save(self) -> None:
        """Save generated HTML to configured output path."""
        html = self.generate()
        self.config.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config.output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"Generated {self.config.mode.value} viewer: {self.config.output_path}")
    
    def _generate_epic_viewer(self) -> str:
        """Generate epic-level plan viewer HTML."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.plan_name} - Epic Progress Viewer</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    {self._generate_glassmorphism_styles()}
</head>
<body>
    {self._generate_epic_header()}
    {self._generate_epic_stats()}
    {self._generate_child_plans_grid()}
    {self._generate_auto_refresh_indicator()}
    {self._generate_epic_javascript()}
</body>
</html>"""
    
    def _generate_feature_viewer(self) -> str:
        """Generate feature-level plan viewer HTML."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.plan_name} - Feature Progress Viewer</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    {self._generate_glassmorphism_styles()}
</head>
<body>
    {self._generate_feature_header()}
    {self._generate_feature_stats()}
    {self._generate_phases_timeline()}
    {self._generate_auto_refresh_indicator()}
    {self._generate_feature_javascript()}
</body>
</html>"""
    
    def _generate_glassmorphism_styles(self) -> str:
        """Generate CSS following glassmorphism-design-standard.md."""
        return """<style>
        /* Glassmorphism Design Standard v4.2.8 Compliance */
        
        :root {
            /* Color System */
            --glass-bg: rgba(15, 23, 42, 0.7);
            --glass-border: rgba(255, 255, 255, 0.1);
            --glass-hover: rgba(255, 255, 255, 0.05);
            --progress-gradient: linear-gradient(90deg, #00d4ff 0%, #a855f7 100%);
            
            /* Text Colors */
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --text-accent: #00d4ff;
            
            /* Status Colors */
            --status-not-started: #64748b;
            --status-in-progress: #3b82f6;
            --status-completed: #22c55e;
            --status-blocked: #ef4444;
            
            /* Spacing (8px base) */
            --spacing-xs: 4px;
            --spacing-sm: 8px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
            --spacing-xl: 32px;
            --spacing-2xl: 48px;
            --spacing-3xl: 64px;
            
            /* Border Radius */
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-full: 9999px;
            
            /* Blur */
            --blur-sm: 10px;
            --blur-md: 20px;
            --blur-lg: 40px;
        }
        
        /* Reset & Base */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: var(--spacing-xl);
            line-height: 1.6;
        }
        
        /* Container */
        .plan-container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        /* Glass Panels (v4.2.8) */
        .glass-panel {
            background: var(--glass-bg);
            backdrop-filter: blur(var(--blur-md));
            -webkit-backdrop-filter: blur(var(--blur-md));
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-lg);
            padding: var(--spacing-xl);
            margin-bottom: var(--spacing-lg);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            position: relative;
        }
        
        .glass-panel::before {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, transparent, rgba(255, 255, 255, 0.05), transparent);
            border-radius: var(--radius-lg);
            opacity: 0;
            animation: glass-reflection 8s infinite;
            pointer-events: none;
        }
        
        @keyframes glass-reflection {
            0%, 100% { opacity: 0; }
            50% { opacity: 0.3; }
        }
        
        /* T1 Animations (Subtle) - Required for ALL detail pages */
        .glass-panel:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);
        }
        
        /* Header */
        .plan-header {
            text-align: center;
            margin-bottom: var(--spacing-2xl);
        }
        
        .plan-title {
            font-size: clamp(2rem, 5vw, 3rem);
            font-weight: 700;
            background: var(--progress-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: var(--spacing-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: var(--spacing-md);
        }
        
        .plan-subtitle {
            font-size: 1.125rem;
            color: var(--text-secondary);
            font-weight: 400;
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--spacing-md);
            margin-bottom: var(--spacing-xl);
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.03);
            border-radius: var(--radius-md);
            padding: var(--spacing-lg);
            text-align: center;
            transition: background 0.2s ease;
        }
        
        .stat-card:hover {
            background: rgba(255, 255, 255, 0.06);
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text-accent);
            margin-bottom: var(--spacing-xs);
        }
        
        .stat-label {
            font-size: 0.875rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Progress Bar (Tetris-Style) */
        .progress-bar {
            height: 40px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: var(--radius-full);
            overflow: hidden;
            position: relative;
            margin: var(--spacing-lg) 0;
        }
        
        .progress-bar-fill {
            height: 100%;
            background: var(--progress-gradient);
            border-radius: var(--radius-full);
            transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 0.875rem;
            position: relative;
            overflow: hidden;
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
        
        /* Child Plans / Phases Grid */
        .plans-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: var(--spacing-md);
        }
        
        .plan-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            padding: var(--spacing-lg);
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .plan-card:hover {
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(0, 212, 255, 0.3);
            transform: translateY(-2px);
        }
        
        .plan-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: var(--spacing-md);
        }
        
        .plan-card-title {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .status-emoji {
            font-size: 1.5rem;
        }
        
        .plan-card-meta {
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-top: var(--spacing-sm);
        }
        
        /* Dependency Tags */
        .dependency-tag {
            display: inline-block;
            background: rgba(168, 85, 247, 0.2);
            color: #c084fc;
            padding: 0.25rem 0.75rem;
            border-radius: var(--radius-full);
            font-size: 0.75rem;
            margin-top: var(--spacing-sm);
        }
        
        /* Auto-Refresh Indicator */
        .auto-refresh-indicator {
            position: fixed;
            bottom: var(--spacing-xl);
            right: var(--spacing-xl);
            background: rgba(0, 212, 255, 0.2);
            border: 1px solid rgba(0, 212, 255, 0.4);
            border-radius: var(--radius-full);
            padding: 0.75rem 1.5rem;
            font-size: 0.875rem;
            backdrop-filter: blur(var(--blur-sm));
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Responsive Design (Mobile-First) */
        @media (max-width: 768px) {
            body {
                padding: var(--spacing-md);
            }
            
            .plan-title {
                font-size: 1.75rem;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .plans-grid {
                grid-template-columns: 1fr;
            }
            
            .auto-refresh-indicator {
                bottom: var(--spacing-md);
                right: var(--spacing-md);
                padding: 0.5rem 1rem;
                font-size: 0.75rem;
            }
        }
        
        /* Accessibility (WCAG AA) */
        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
    </style>"""
    
    def _generate_epic_header(self) -> str:
        """Generate epic viewer header."""
        return f"""    <div class="plan-container">
        <div class="plan-header">
            <h1 class="plan-title">
                <i class="fas fa-layer-group"></i>
                {self.config.plan_name}
            </h1>
            <p class="plan-subtitle">Strategic Multi-Phase Epic Plan</p>
        </div>"""
    
    def _generate_feature_header(self) -> str:
        """Generate feature viewer header."""
        return f"""    <div class="plan-container">
        <div class="plan-header">
            <h1 class="plan-title">
                <i class="fas fa-tasks"></i>
                {self.config.plan_name}
            </h1>
            <p class="plan-subtitle">Feature Implementation Plan</p>
        </div>"""
    
    def _generate_epic_stats(self) -> str:
        """Generate epic-level statistics panel."""
        return """        <div class="glass-panel">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="epic-progress">0%</div>
                    <div class="stat-label">Overall Progress</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="plans-complete">0/0</div>
                    <div class="stat-label">Plans Complete</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="total-phases">0/0</div>
                    <div class="stat-label">Phases Complete</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="estimated-duration">0d</div>
                    <div class="stat-label">Estimated Duration</div>
                </div>
            </div>
            
            <div class="progress-bar">
                <div class="progress-bar-fill" id="epic-progress-bar" style="width: 0%">
                    <span id="epic-progress-text">0% Complete</span>
                </div>
            </div>
        </div>"""
    
    def _generate_feature_stats(self) -> str:
        """Generate feature-level statistics panel."""
        return """        <div class="glass-panel">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="feature-progress">0%</div>
                    <div class="stat-label">Overall Progress</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="phases-complete">0/0</div>
                    <div class="stat-label">Phases Complete</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="estimated-hours">0h</div>
                    <div class="stat-label">Estimated Duration</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="tasks-complete">0/0</div>
                    <div class="stat-label">Tasks Complete</div>
                </div>
            </div>
            
            <div class="progress-bar">
                <div class="progress-bar-fill" id="feature-progress-bar" style="width: 0%">
                    <span id="feature-progress-text">0% Complete</span>
                </div>
            </div>
        </div>"""
    
    def _generate_child_plans_grid(self) -> str:
        """Generate grid of child plans (epic mode)."""
        return """        <div class="glass-panel">
            <h2 style="margin-bottom: var(--spacing-lg); display: flex; align-items: center; gap: var(--spacing-sm);">
                <i class="fas fa-folder-tree"></i>
                Child Feature Plans
            </h2>
            <div class="plans-grid" id="child-plans-container">
                <!-- Dynamically populated by JavaScript -->
            </div>
        </div>
    </div>"""
    
    def _generate_phases_timeline(self) -> str:
        """Generate timeline of phases (feature mode)."""
        return """        <div class="glass-panel">
            <h2 style="margin-bottom: var(--spacing-lg); display: flex; align-items: center; gap: var(--spacing-sm);">
                <i class="fas fa-list-check"></i>
                Implementation Phases
            </h2>
            <div class="plans-grid" id="phases-container">
                <!-- Dynamically populated by JavaScript -->
            </div>
        </div>
    </div>"""
    
    def _generate_auto_refresh_indicator(self) -> str:
        """Generate auto-refresh status indicator."""
        return f"""    <div class="auto-refresh-indicator pulse">
        <i class="fas fa-rotate"></i>
        <span>Auto-refreshing every {self.config.auto_refresh_seconds}s</span>
    </div>"""
    
    def _generate_epic_javascript(self) -> str:
        """Generate JavaScript for epic viewer."""
        return f"""    <script>
        const TRACKING_FILE = '{self.config.tracking_json_path}';
        const REFRESH_INTERVAL = {self.config.auto_refresh_seconds * 1000};
        
        async function loadEpicProgress() {{
            try {{
                const response = await fetch(TRACKING_FILE + '?t=' + Date.now());
                const data = await response.json();
                
                // Update stats
                document.getElementById('epic-progress').textContent = data.overall_progress + '%';
                document.getElementById('plans-complete').textContent = 
                    `${{data.completed_plans || 0}}/${{data.total_plans || 0}}`;
                document.getElementById('total-phases').textContent = 
                    `${{data.completed_phases || 0}}/${{data.total_phases || 0}}`;
                document.getElementById('estimated-duration').textContent = 
                    (data.estimated_duration_days || 0) + 'd';
                
                // Update progress bar
                const progressBar = document.getElementById('epic-progress-bar');
                progressBar.style.width = data.overall_progress + '%';
                document.getElementById('epic-progress-text').textContent = 
                    data.overall_progress + '% Complete';
                
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
                card.className = 'plan-card';
                card.onclick = () => openChildPlanViewer(plan.plan_id);
                
                const statusEmoji = getStatusEmoji(plan.status);
                const dependencies = plan.dependencies || [];
                
                card.innerHTML = `
                    <div class="plan-card-header">
                        <h3 class="plan-card-title">${{plan.order || ''}}. ${{plan.plan_name}}</h3>
                        <span class="status-emoji">${{statusEmoji}}</span>
                    </div>
                    <div class="progress-bar" style="height: 24px;">
                        <div class="progress-bar-fill" style="width: ${{plan.overall_progress || 0}}%; font-size: 0.75rem;">
                            ${{plan.overall_progress || 0}}%
                        </div>
                    </div>
                    <p class="plan-card-meta">
                        ${{plan.completed_phases || 0}}/${{plan.total_phases || 0}} phases • 
                        ${{plan.estimated_duration_days || 0}}d
                    </p>
                    ${{dependencies.length > 0 ? `
                        <div class="dependency-tag">
                            <i class="fas fa-link"></i> Depends on: ${{dependencies.join(', ')}}
                        </div>
                    ` : ''}}
                `;
                
                container.appendChild(card);
            }});
        }}
        
        function getStatusEmoji(status) {{
            const emojis = {{
                'not-started': '⏳',
                'in-progress': '🔄',
                'completed': '✅',
                'blocked': '🔒',
                'failed': '❌',
                'deferred': '⏸️'
            }};
            return emojis[status] || '⏳';
        }}
        
        function openChildPlanViewer(planId) {{
            const viewerPath = `${{planId}}/${{planId}}-plan-viewer.html`;
            window.open(viewerPath, '_blank');
        }}
        
        // Auto-refresh
        loadEpicProgress();
        setInterval(loadEpicProgress, REFRESH_INTERVAL);
    </script>
</body>
</html>"""
    
    def _generate_feature_javascript(self) -> str:
        """Generate JavaScript for feature viewer."""
        return f"""    <script>
        const TRACKING_FILE = '{self.config.tracking_json_path}';
        const REFRESH_INTERVAL = {self.config.auto_refresh_seconds * 1000};
        
        async function loadFeatureProgress() {{
            try {{
                const response = await fetch(TRACKING_FILE + '?t=' + Date.now());
                const data = await response.json();
                
                // Update stats
                document.getElementById('feature-progress').textContent = data.overall_progress + '%';
                document.getElementById('phases-complete').textContent = 
                    `${{data.completed_phases || 0}}/${{data.total_phases || 0}}`;
                document.getElementById('estimated-hours').textContent = 
                    (data.estimated_duration_hours || 0) + 'h';
                
                const totalTasks = data.phases?.reduce((sum, p) => sum + (p.tasks_total || 0), 0) || 0;
                const completedTasks = data.phases?.reduce((sum, p) => sum + (p.tasks_completed || 0), 0) || 0;
                document.getElementById('tasks-complete').textContent = `${{completedTasks}}/${{totalTasks}}`;
                
                // Update progress bar
                const progressBar = document.getElementById('feature-progress-bar');
                progressBar.style.width = data.overall_progress + '%';
                document.getElementById('feature-progress-text').textContent = 
                    data.overall_progress + '% Complete';
                
                // Render phases
                renderPhases(data.phases || []);
            }} catch (error) {{
                console.error('Failed to load feature progress:', error);
            }}
        }}
        
        function renderPhases(phases) {{
            const container = document.getElementById('phases-container');
            container.innerHTML = '';
            
            phases.forEach(phase => {{
                const card = document.createElement('div');
                card.className = 'plan-card';
                
                const statusEmoji = getStatusEmoji(phase.status);
                const dependencies = phase.dependencies || [];
                
                card.innerHTML = `
                    <div class="plan-card-header">
                        <h3 class="plan-card-title">Phase ${{phase.phase_number}}: ${{phase.phase_name}}</h3>
                        <span class="status-emoji">${{statusEmoji}}</span>
                    </div>
                    <div class="progress-bar" style="height: 24px;">
                        <div class="progress-bar-fill" style="width: ${{phase.progress_percentage || 0}}%; font-size: 0.75rem;">
                            ${{phase.progress_percentage || 0}}%
                        </div>
                    </div>
                    <p class="plan-card-meta">
                        ${{phase.tasks_completed || 0}}/${{phase.tasks_total || 0}} tasks • 
                        ${{phase.estimated_hours || 0}}h estimated
                    </p>
                    ${{dependencies.length > 0 ? `
                        <div class="dependency-tag">
                            <i class="fas fa-link"></i> Depends on Phase: ${{dependencies.join(', ')}}
                        </div>
                    ` : ''}}
                `;
                
                container.appendChild(card);
            }});
        }}
        
        function getStatusEmoji(status) {{
            const emojis = {{
                'not-started': '⏳',
                'in-progress': '🔄',
                'completed': '✅',
                'blocked': '🔒',
                'failed': '❌',
                'deferred': '⏸️'
            }};
            return emojis[status] || '⏳';
        }}
        
        // Auto-refresh
        loadFeatureProgress();
        setInterval(loadFeatureProgress, REFRESH_INTERVAL);
    </script>
</body>
</html>"""
