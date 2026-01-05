"""
CORTEX 5.0 HTML Plan Viewer Generator

Purpose: Generate static glassmorphism-styled HTML viewers for epic and feature plans
         with auto-refresh capability and real-time progress display.

Version: 5.0.0
Author: Asif Hussain
Created: January 4, 2026

Features:
- Glassmorphism UI design (follows design standards)
- Auto-refresh from JSON trackers
- Responsive layout
- Dependency visualization
- Progress animations
- WCAG AA accessibility
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ViewerConfig:
    """Configuration for HTML viewer generation."""
    plan_name: str
    plan_type: str  # "epic" or "feature"
    tracker_path: str  # Relative path to JSON tracker
    refresh_interval: int = 30  # seconds
    theme: str = "glassmorphism"
    enable_auto_refresh: bool = True
    enable_animations: bool = True


@dataclass
class ViewerStyle:
    """Glassmorphism styling configuration following design standards."""
    # Color scheme
    glass_bg: str = "rgba(15, 23, 42, 0.7)"
    glass_border: str = "rgba(255, 255, 255, 0.1)"
    progress_gradient: str = "linear-gradient(90deg, #00d4ff 0%, #a855f7 100%)"
    text_primary: str = "#e2e8f0"
    text_secondary: str = "#94a3b8"
    accent_blue: str = "#00d4ff"
    accent_purple: str = "#a855f7"
    
    # Effects
    blur_amount: str = "20px"
    transition_duration: str = "0.2s"
    hover_lift: str = "2px"
    
    # Typography
    font_family: str = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"


class HTMLViewerGenerator:
    """
    Generates static HTML plan viewers with glassmorphism styling.
    
    Follows CORTEX glassmorphism design standards for consistent UI.
    """
    
    def __init__(self, config: ViewerConfig, style: Optional[ViewerStyle] = None):
        """
        Initialize HTML viewer generator.
        
        Args:
            config: Viewer configuration
            style: Optional custom styling (defaults to standard glassmorphism)
        """
        self.config = config
        self.style = style or ViewerStyle()
    
    def generate(self, tracker_data: Dict, output_path: Path) -> None:
        """
        Generate HTML viewer and write to file.
        
        Args:
            tracker_data: Progress tracker data (epic or feature)
            output_path: Path to write HTML file
        """
        if self.config.plan_type == "epic":
            html = self._generate_epic_viewer(tracker_data)
        elif self.config.plan_type == "feature":
            html = self._generate_feature_viewer(tracker_data)
        else:
            raise ValueError(f"Unknown plan type: {self.config.plan_type}")
        
        # Write to file
        output_path.write_text(html, encoding='utf-8')
        logger.info(f"Generated HTML viewer: {output_path}")
    
    def _generate_epic_viewer(self, tracker_data: Dict) -> str:
        """Generate HTML for epic plan viewer."""
        plan_name = tracker_data.get("plan_name", "Epic Plan")
        plan_id = tracker_data.get("plan_id", "")
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{plan_name} - CORTEX Epic Plan Progress Viewer">
    <title>{plan_name} - Progress</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
{self._generate_css()}
    </style>
</head>
<body>
    <div class="epic-container">
        <!-- Header -->
        <header class="epic-header" role="banner">
            <h1 class="epic-title">🎯 {plan_name}</h1>
            <p class="epic-subtitle">Strategic Multi-Phase Epic Plan</p>
            <p class="epic-id" aria-label="Plan ID">Plan ID: {plan_id}</p>
        </header>
        
        <!-- Epic Stats -->
        <section class="glass-panel" aria-labelledby="stats-heading">
            <h2 id="stats-heading" class="sr-only">Epic Statistics</h2>
            <div class="epic-stats">
                <div class="stat-card">
                    <div class="stat-value" id="epic-progress" aria-label="Overall progress">0%</div>
                    <div class="stat-label">Overall Progress</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="child-plans-complete" aria-label="Plans complete">0/0</div>
                    <div class="stat-label">Plans Complete</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="total-phases" aria-label="Phases complete">0/0</div>
                    <div class="stat-label">Phases Complete</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="estimated-days" aria-label="Estimated duration">0d</div>
                    <div class="stat-label">Estimated Duration</div>
                </div>
            </div>
            
            <div class="progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" aria-label="Overall epic progress">
                <div class="progress-bar-fill" id="overall-progress-bar" style="width: 0%">
                    <span id="progress-text">0%</span>
                </div>
            </div>
        </section>
        
        <!-- Child Plans -->
        <section class="glass-panel" aria-labelledby="plans-heading">
            <h2 id="plans-heading">📋 Child Plans</h2>
            <div class="child-plans-grid" id="child-plans-container">
                <!-- Child plans populated by JavaScript -->
            </div>
        </section>
        
        <!-- Milestones -->
        <section class="glass-panel" aria-labelledby="milestones-heading">
            <h2 id="milestones-heading">🎯 Milestones</h2>
            <div class="milestones-list" id="milestones-container">
                <!-- Milestones populated by JavaScript -->
            </div>
        </section>
        
        <!-- Auto-refresh indicator -->
        <div class="auto-refresh-indicator pulse" role="status" aria-live="polite">
            <span class="refresh-icon">🔄</span>
            Auto-refreshing every {self.config.refresh_interval}s
        </div>
    </div>
    
    <script>
{self._generate_javascript()}
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_feature_viewer(self, tracker_data: Dict) -> str:
        """Generate HTML for feature plan viewer."""
        plan_name = tracker_data.get("plan_name", "Feature Plan")
        plan_id = tracker_data.get("plan_id", "")
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{plan_name} - CORTEX Feature Plan Progress Viewer">
    <title>{plan_name} - Progress</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
{self._generate_css()}
    </style>
</head>
<body>
    <div class="feature-container">
        <!-- Header -->
        <header class="feature-header" role="banner">
            <h1 class="feature-title">📋 {plan_name}</h1>
            <p class="feature-subtitle">Feature Plan Execution</p>
            <p class="feature-id" aria-label="Plan ID">Plan ID: {plan_id}</p>
        </header>
        
        <!-- Feature Stats -->
        <section class="glass-panel" aria-labelledby="stats-heading">
            <h2 id="stats-heading" class="sr-only">Feature Statistics</h2>
            <div class="feature-stats">
                <div class="stat-card">
                    <div class="stat-value" id="feature-progress" aria-label="Overall progress">0%</div>
                    <div class="stat-label">Overall Progress</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="phases-complete" aria-label="Phases complete">0/0</div>
                    <div class="stat-label">Phases Complete</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="current-phase" aria-label="Current phase">Phase -1</div>
                    <div class="stat-label">Current Phase</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="hours-spent" aria-label="Hours spent">0h</div>
                    <div class="stat-label">Hours Spent</div>
                </div>
            </div>
            
            <div class="progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" aria-label="Overall feature progress">
                <div class="progress-bar-fill" id="overall-progress-bar" style="width: 0%">
                    <span id="progress-text">0%</span>
                </div>
            </div>
        </section>
        
        <!-- Phases -->
        <section class="glass-panel" aria-labelledby="phases-heading">
            <h2 id="phases-heading">📊 Phases</h2>
            <div class="phases-list" id="phases-container">
                <!-- Phases populated by JavaScript -->
            </div>
        </section>
        
        <!-- Auto-refresh indicator -->
        <div class="auto-refresh-indicator pulse" role="status" aria-live="polite">
            <span class="refresh-icon">🔄</span>
            Auto-refreshing every {self.config.refresh_interval}s
        </div>
    </div>
    
    <script>
{self._generate_javascript()}
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_css(self) -> str:
        """Generate glassmorphism CSS styles following design standards."""
        return f"""/* CORTEX 5.0 Glassmorphism Plan Viewer Styles */

/* CSS Variables */
:root {{
    --glass-bg: {self.style.glass_bg};
    --glass-border: {self.style.glass_border};
    --progress-gradient: {self.style.progress_gradient};
    --text-primary: {self.style.text_primary};
    --text-secondary: {self.style.text_secondary};
    --accent-blue: {self.style.accent_blue};
    --accent-purple: {self.style.accent_purple};
    --blur-amount: {self.style.blur_amount};
    --transition: {self.style.transition_duration} ease;
}}

/* Base Styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: {self.style.font_family};
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: var(--text-primary);
    padding: 2rem;
    min-height: 100vh;
    line-height: 1.6;
}}

/* Screen reader only content */
.sr-only {{
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}}

/* Container */
.epic-container,
.feature-container {{
    max-width: 1400px;
    margin: 0 auto;
}}

/* Glass Panels */
.glass-panel {{
    background: var(--glass-bg);
    backdrop-filter: blur(var(--blur-amount));
    -webkit-backdrop-filter: blur(var(--blur-amount));
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    transition: transform var(--transition), box-shadow var(--transition);
}}

.glass-panel:hover {{
    transform: translateY(-{self.style.hover_lift});
    box-shadow: 0 8px 32px rgba(0, 212, 255, 0.15);
}}

/* Header */
.epic-header,
.feature-header {{
    text-align: center;
    margin-bottom: 3rem;
}}

.epic-title,
.feature-title {{
    font-size: clamp(2rem, 4cqi, 3rem);
    font-weight: 700;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
}}

.epic-subtitle,
.feature-subtitle {{
    font-size: 1.125rem;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
}}

.epic-id,
.feature-id {{
    font-size: 0.875rem;
    color: var(--text-secondary);
    font-family: 'Courier New', monospace;
}}

/* Stats Grid */
.epic-stats,
.feature-stats {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}}

.stat-card {{
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    transition: background var(--transition);
}}

.stat-card:hover {{
    background: rgba(255, 255, 255, 0.08);
}}

.stat-value {{
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--accent-blue);
    margin-bottom: 0.5rem;
}}

.stat-label {{
    font-size: 0.875rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

/* Progress Bar */
.progress-bar {{
    height: 40px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    overflow: hidden;
    position: relative;
    margin: 1rem 0;
}}

.progress-bar-fill {{
    height: 100%;
    background: var(--progress-gradient);
    border-radius: 20px;
    transition: width 0.5s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    position: relative;
    min-width: 60px;
}}

.progress-bar-fill::before {{
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
}}

@keyframes shimmer {{
    0% {{ transform: translateX(-100%); }}
    100% {{ transform: translateX(100%); }}
}}

/* Section Headings */
h2 {{
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--text-primary);
}}

/* Child Plans Grid */
.child-plans-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1rem;
}}

.child-plan-card {{
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all var(--transition);
    cursor: pointer;
}}

.child-plan-card:hover {{
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(0, 212, 255, 0.3);
    transform: translateY(-2px);
}}

.child-plan-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}}

.child-plan-order {{
    font-weight: 700;
    font-size: 1.125rem;
    color: var(--accent-blue);
}}

.child-plan-status {{
    font-size: 1.5rem;
}}

.child-plan-name {{
    font-size: 1.125rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}}

.child-plan-progress {{
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-bottom: 0.75rem;
}}

.dependency-tag {{
    display: inline-block;
    background: rgba(168, 85, 247, 0.2);
    color: #c084fc;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    margin-top: 0.5rem;
}}

/* Phases List */
.phases-list {{
    display: flex;
    flex-direction: column;
    gap: 1rem;
}}

.phase-card {{
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all var(--transition);
}}

.phase-card:hover {{
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(0, 212, 255, 0.2);
}}

.phase-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}}

.phase-number {{
    font-weight: 700;
    color: var(--accent-blue);
}}

.phase-name {{
    font-weight: 600;
    flex: 1;
    margin-left: 1rem;
}}

.phase-status {{
    font-size: 1.25rem;
}}

.phase-progress {{
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-bottom: 0.75rem;
}}

/* Status Badges */
.status-badge {{
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}}

.status-complete {{
    background: linear-gradient(135deg, #059669 0%, #10B981 100%);
    color: white;
}}

.status-in-progress {{
    background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%);
    color: white;
}}

.status-failed {{
    background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%);
    color: white;
}}

.status-not-started {{
    background: rgba(75, 85, 99, 0.8);
    color: rgba(255, 255, 255, 0.9);
}}

/* Milestones List */
.milestones-list {{
    display: flex;
    flex-direction: column;
    gap: 1rem;
}}

.milestone-item {{
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 8px;
}}

.milestone-status {{
    font-size: 1.5rem;
}}

.milestone-info {{
    flex: 1;
}}

.milestone-name {{
    font-weight: 600;
    margin-bottom: 0.25rem;
}}

.milestone-date {{
    font-size: 0.875rem;
    color: var(--text-secondary);
}}

/* Auto-refresh Indicator */
.auto-refresh-indicator {{
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
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}

.refresh-icon {{
    display: inline-block;
}}

.pulse {{
    animation: pulse 2s infinite;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
}}

/* Responsive Design */
@media (max-width: 768px) {{
    body {{
        padding: 1rem;
    }}
    
    .glass-panel {{
        padding: 1.5rem;
    }}
    
    .epic-stats,
    .feature-stats {{
        grid-template-columns: repeat(2, 1fr);
    }}
    
    .child-plans-grid {{
        grid-template-columns: 1fr;
    }}
    
    .auto-refresh-indicator {{
        bottom: 1rem;
        right: 1rem;
        font-size: 0.75rem;
        padding: 0.5rem 1rem;
    }}
}}

/* Print Styles */
@media print {{
    .auto-refresh-indicator {{
        display: none;
    }}
    
    .glass-panel {{
        break-inside: avoid;
    }}
}}"""
    
    def _generate_javascript(self) -> str:
        """Generate JavaScript for auto-refresh and data population."""
        return f"""// CORTEX 5.0 Plan Viewer - Auto-Refresh System

class PlanViewerAutoRefresh {{
    constructor(trackerPath, refreshInterval) {{
        this.trackerPath = trackerPath;
        this.refreshInterval = refreshInterval * 1000; // Convert to ms
        this.lastModified = null;
        this.planType = '{self.config.plan_type}';
    }}
    
    async fetchTrackerData() {{
        try {{
            const response = await fetch(this.trackerPath + '?t=' + Date.now());
            if (!response.ok) {{
                throw new Error(`HTTP error! status: ${{response.status}}`);
            }}
            return await response.json();
        }} catch (error) {{
            console.error('Failed to fetch tracker:', error);
            return null;
        }}
    }}
    
    async checkForUpdates() {{
        const data = await this.fetchTrackerData();
        if (!data) {{
            console.error('No data fetched from tracker');
            return;
        }}
        
        console.log('Tracker data loaded:', {{
            phases: data.phases?.length,
            updated_date: data.updated_date,
            plan_name: data.plan_name
        }});
        
        // Check if data has changed (use updated_date or last_updated)
        const lastUpdate = data.updated_date || data.last_updated;
        if (this.lastModified !== lastUpdate) {{
            console.log('Data changed, updating viewer');
            this.lastModified = lastUpdate;
            this.updateViewer(data);
        }} else {{
            console.log('No changes detected');
        }}
    }}
    
    updateViewer(data) {{
        if (this.planType === 'epic') {{
            this.updateEpicViewer(data);
        }} else if (this.planType === 'feature') {{
            this.updateFeatureViewer(data);
        }}
    }}
    
    updateEpicViewer(data) {{
        // Update stats
        document.getElementById('epic-progress').textContent = 
            Math.round(data.overall_progress) + '%';
        document.getElementById('child-plans-complete').textContent = 
            `${{data.completed_plans}}/${{data.total_plans}}`;
        document.getElementById('total-phases').textContent = 
            `${{data.completed_phases}}/${{data.total_phases}}`;
        document.getElementById('estimated-days').textContent = 
            data.estimated_days + 'd';
        
        // Update overall progress bar
        const progressBar = document.getElementById('overall-progress-bar');
        const progressText = document.getElementById('progress-text');
        const progress = Math.round(data.overall_progress);
        progressBar.style.width = progress + '%';
        progressBar.setAttribute('aria-valuenow', progress);
        progressText.textContent = progress + '%';
        
        // Update child plans
        this.updateChildPlans(data.child_plans);
        
        // Update milestones
        this.updateMilestones(data.milestones || []);
    }}
    
    updateFeatureViewer(data) {{
        // Calculate stats from phases array
        const phases = data.phases || [];
        const totalPhases = phases.length;
        const completedPhases = phases.filter(p => p.status === 'complete').length;
        const overallProgress = totalPhases > 0 ? (completedPhases / totalPhases * 100) : 0;
        const currentPhase = phases.find(p => p.status === 'in_progress')?.number || 
                           phases.find(p => p.status === 'not_started')?.number || 
                           totalPhases;
        const actualHours = phases.reduce((sum, p) => sum + (p.actual_hours || 0), 0);
        
        // Update stats
        document.getElementById('feature-progress').textContent = 
            Math.round(overallProgress) + '%';
        document.getElementById('phases-complete').textContent = 
            `${{completedPhases}}/${{totalPhases}}`;
        document.getElementById('current-phase').textContent = 
            `Phase ${{currentPhase}}`;
        document.getElementById('hours-spent').textContent = 
            Math.round(actualHours) + 'h';
        
        // Update overall progress bar
        const progressBar = document.getElementById('overall-progress-bar');
        const progressText = document.getElementById('progress-text');
        const progress = Math.round(overallProgress);
        progressBar.style.width = progress + '%';
        progressBar.setAttribute('aria-valuenow', progress);
        progressText.textContent = progress + '%';
        
        // Update phases
        this.updatePhases(data.phases);
    }}
    
    updateChildPlans(childPlans) {{
        const container = document.getElementById('child-plans-container');
        if (!container) return;
        
        container.innerHTML = '';
        
        childPlans.forEach(plan => {{
            const card = document.createElement('div');
            card.className = 'child-plan-card';
            card.innerHTML = `
                <div class="child-plan-header">
                    <span class="child-plan-order">${{plan.order}}</span>
                    <span class="child-plan-status" aria-label="${{plan.status}}">${{plan.status_emoji}}</span>
                </div>
                <div class="child-plan-name">${{plan.name}}</div>
                <div class="child-plan-progress">
                    Progress: ${{Math.round(plan.progress)}}% • 
                    Phases: ${{plan.phases_complete}}/${{plan.total_phases}}
                </div>
                <div class="progress-bar" style="height: 24px; margin-top: 0.5rem;">
                    <div class="progress-bar-fill" style="width: ${{plan.progress}}%; font-size: 0.75rem;">
                        ${{Math.round(plan.progress)}}%
                    </div>
                </div>
                ${{plan.dependencies.length > 0 ? 
                    `<div class="dependency-tag">Depends on: ${{plan.dependencies.join(', ')}}</div>` : 
                    ''}}
            `;
            container.appendChild(card);
        }});
    }}
    
    updatePhases(phases) {{
        const container = document.getElementById('phases-container');
        if (!container) {{
            console.error('phases-container not found!');
            return;
        }}
        
        console.log(`Updating ${{phases.length}} phase cards`);
        container.innerHTML = '';
        
        phases.forEach(phase => {{
            // Map status to emoji and label
            const statusMap = {{
                'complete': {{ emoji: '✅', label: 'Complete', class: 'status-complete' }},
                'in_progress': {{ emoji: '🔄', label: 'In Progress', class: 'status-in-progress' }},
                'failed': {{ emoji: '❌', label: 'Failed', class: 'status-failed' }},
                'not_started': {{ emoji: '🔲', label: 'Not Started', class: 'status-not-started' }}
            }};
            
            const statusInfo = statusMap[phase.status] || statusMap['not_started'];
            
            // Calculate progress (100% if complete, 50% if in progress, 0% otherwise)
            const progress = phase.status === 'complete' ? 100 : 
                           phase.status === 'in_progress' ? 50 : 0;
            
            const card = document.createElement('div');
            card.className = 'phase-card';
            card.innerHTML = `
                <div class="phase-header">
                    <span class="phase-number">Phase ${{phase.number}}</span>
                    <span class="phase-name">${{phase.name}}</span>
                    <span class="status-badge ${{statusInfo.class}}">${{statusInfo.emoji}} ${{statusInfo.label}}</span>
                </div>
                <div class="phase-progress">
                    Est: ${{phase.estimated_hours || 0}}h • 
                    Outputs: ${{(phase.outputs || []).length}}
                </div>
                <div class="progress-bar" style="height: 24px; margin-top: 0.5rem;">
                    <div class="progress-bar-fill" style="width: ${{progress}}%; font-size: 0.75rem;">
                        ${{Math.round(progress)}}%
                    </div>
                </div>
            `;
            container.appendChild(card);
        }});
        
        console.log(`✅ Rendered ${{phases.length}} phase cards`);
    }}
    
    updateMilestones(milestones) {{
        const container = document.getElementById('milestones-container');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (milestones.length === 0) {{
            container.innerHTML = '<p style="color: var(--text-secondary);">No milestones defined</p>';
            return;
        }}
        
        milestones.forEach(milestone => {{
            const item = document.createElement('div');
            item.className = 'milestone-item';
            const statusEmoji = milestone.status === 'complete' ? '✅' : 
                              milestone.status === 'in_progress' ? '🔄' : '⏳';
            item.innerHTML = `
                <span class="milestone-status" aria-label="${{milestone.status}}">${{statusEmoji}}</span>
                <div class="milestone-info">
                    <div class="milestone-name">${{milestone.name}}</div>
                    <div class="milestone-date">Target: ${{milestone.target_date}}</div>
                </div>
            `;
            container.appendChild(item);
        }});
    }}
    
    start() {{
        // Initial load
        this.checkForUpdates();
        
        // Set up periodic refresh
        setInterval(() => this.checkForUpdates(), this.refreshInterval);
        
        console.log('CORTEX Plan Viewer started - Refresh interval:', this.refreshInterval / 1000, 'seconds');
    }}
}}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {{
    const viewer = new PlanViewerAutoRefresh(
        '{self.config.tracker_path}',
        {self.config.refresh_interval}
    );
    viewer.start();
}});"""


# Export public API
__all__ = [
    "HTMLViewerGenerator",
    "ViewerConfig",
    "ViewerStyle"
]
