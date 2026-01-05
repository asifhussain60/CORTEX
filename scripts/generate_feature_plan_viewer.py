#!/usr/bin/env python3
"""
CORTEX Planning System v5 - Feature Plan Viewer Generator
Generates interactive HTML viewer for FEATURE-mode plans (single-plan execution)

Purpose: Create real-time progress tracking UI for feature plans
Author: CORTEX AI Assistant
Created: January 4, 2026
Version: 1.0.0

Usage:
    python3 generate_feature_plan_viewer.py <plan_directory>
    
Example:
    python3 generate_feature_plan_viewer.py cortex-brain/documents/planning/active/c150-remediation-plan
    
Features:
    - Auto-detects FEATURE mode from folder structure
    - Generates glassmorphism UI matching CORTEX brand
    - Real-time progress tracking (auto-refresh 30s)
    - Phase status indicators (⏳ in_progress, ✅ complete, ❌ failed)
    - HTTP server auto-launch with browser integration
"""

import json
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional


def validate_feature_plan(plan_path: Path) -> tuple[bool, str]:
    """
    Validate that directory is a FEATURE-mode plan.
    
    Args:
        plan_path: Path to plan directory
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not plan_path.exists():
        return False, f"Path does not exist: {plan_path}"
    
    if not plan_path.is_dir():
        return False, f"Path is not a directory: {plan_path}"
    
    # Check for required structure
    tracking_dir = plan_path / "tracking"
    progress_tracker = tracking_dir / "progress-tracker.json"
    
    if not tracking_dir.exists():
        return False, "Missing tracking/ directory (required for FEATURE mode)"
    
    if not progress_tracker.exists():
        return False, "Missing tracking/progress-tracker.json (required for FEATURE mode)"
    
    # Check for plan file (YAML or MD)
    plan_files = list(plan_path.glob("00-*.yaml")) + list(plan_path.glob("00-*.md"))
    if not plan_files:
        return False, "Missing master plan file (00-*.yaml or 00-*.md)"
    
    return True, ""


def load_progress_tracker(plan_path: Path) -> Dict:
    """Load progress tracker JSON."""
    tracker_path = plan_path / "tracking/progress-tracker.json"
    with open(tracker_path, 'r') as f:
        return json.load(f)


def generate_html_viewer(plan_path: Path, tracker_data: Dict) -> Path:
    """
    Generate HTML viewer for FEATURE-mode plan.
    
    Args:
        plan_path: Path to plan directory
        tracker_data: Progress tracker data from JSON
        
    Returns:
        Path to generated plan-viewer.html
    """
    plan_name = tracker_data.get("plan_name", "Untitled Plan")
    plan_id = tracker_data.get("plan_id", "unknown")
    status = tracker_data.get("status", "not_started")
    estimated_hours = tracker_data.get("estimated_total_hours", 0)
    actual_hours = tracker_data.get("actual_total_hours") or 0
    
    # Calculate progress
    phases = tracker_data.get("phases", [])
    total_phases = len(phases)
    completed_phases = len([p for p in phases if p.get("status") == "complete"])
    in_progress_phases = len([p for p in phases if p.get("status") == "in_progress"])
    failed_phases = len([p for p in phases if p.get("status") == "failed"])
    not_started_phases = total_phases - completed_phases - in_progress_phases - failed_phases
    
    overall_progress = (completed_phases / total_phases * 100) if total_phases > 0 else 0
    
    # Generate phases HTML with modal data
    phases_html = ""
    for phase in phases:
        phase_num = phase.get("number", "?")
        phase_name = phase.get("name", "Untitled Phase")
        phase_status = phase.get("status", "not_started")
        phase_estimated = phase.get("estimated_hours", 0)
        phase_actual = phase.get("actual_hours") or 0
        phase_outputs = phase.get("outputs", [])
        phase_description = phase.get("description", "No description available")
        phase_validation = phase.get("validation_criteria", [])
        phase_dependencies = phase.get("dependencies", [])
        phase_python_executor = phase.get("python_executor", "N/A")
        phase_start = phase.get("start_time", "Not started")
        phase_end = phase.get("end_time", "Not completed")
        
        # Status badge
        status_icon = "⏳" if phase_status == "in_progress" else ("✅" if phase_status == "complete" else ("❌" if phase_status == "failed" else "🔲"))
        status_class = f"status-{phase_status.replace('_', '-')}"
        
        # Build outputs list for modal
        outputs_html = ""
        if phase_outputs:
            outputs_html = "<ul>"
            for output in phase_outputs:
                outputs_html += f"<li>📄 {output}</li>"
            outputs_html += "</ul>"
        else:
            outputs_html = "<p style='color: rgba(255,255,255,0.5); font-style: italic;'>No outputs yet</p>"
        
        # Calculate progress indicator
        if phase_status == "complete":
            progress_emoji = "✅"
            progress_color = "var(--accent)"
        elif phase_status == "in_progress":
            progress_emoji = "⏳"
            progress_color = "var(--warning)"
        elif phase_status == "failed":
            progress_emoji = "❌"
            progress_color = "var(--error)"
        else:
            progress_emoji = "🔲"
            progress_color = "rgba(75, 85, 99, 0.8)"
        
        phases_html += f'''
        <div class="phase-card glass" id="phase-{phase_num}" data-phase-id="phase-{phase_num}" onclick="openPhaseModal('phase-{phase_num}')">
            <div class="phase-header">
                <div class="phase-title">
                    <span class="phase-number">Phase {phase_num}</span>
                    <span class="phase-name">{phase_name}</span>
                </div>
                <span class="status-badge {status_class}">{status_icon} {phase_status.replace('_', ' ').title()}</span>
            </div>
            <div class="phase-meta">
                <span>⏱️ Est: {phase_estimated}h</span>
                {f'<span>📊 Actual: {phase_actual}h</span>' if phase_actual > 0 else ''}
                <span>📁 Outputs: {len(phase_outputs)}</span>
            </div>
        </div>
        
        <!-- Modal for Phase {phase_num} -->
        <div class="glass-modal-overlay" id="modal-phase-{phase_num}" onclick="closePhaseModal('phase-{phase_num}', event)">
            <div class="glass-modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h2>{progress_emoji} Phase {phase_num}: {phase_name}</h2>
                    <button class="modal-close" onclick="closePhaseModal('phase-{phase_num}', event)">✕</button>
                </div>
                <div class="modal-content">
                    
                    <div class="modal-section">
                        <h3>⏱️ Time & Progress</h3>
                        <div class="modal-stats-grid">
                            <div class="modal-stat-tile">
                                <div class="modal-stat-label">⏳ Estimated</div>
                                <div class="modal-stat-value">{phase_estimated}h</div>
                            </div>
                            <div class="modal-stat-tile">
                                <div class="modal-stat-label">📊 Actual</div>
                                <div class="modal-stat-value">{phase_actual}h</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="modal-section">
                        <h3>📦 Deliverables ({len(phase_outputs)})</h3>
                        {outputs_html}
                    </div>
                    
                    <div class="modal-section" style="border-left: 4px solid {progress_color};">
                        <h3>📋 Status</h3>
                        <p style="font-size: 1.1em; font-weight: 600; color: white;">
                            {progress_emoji} {phase_status.replace('_', ' ').title()}
                        </p>
                        {f'<p style="color: rgba(255,255,255,0.7); font-size: 0.9em; margin-top: 0.5rem;">⏰ Started: {phase_start}</p>' if phase_start not in ["Not started", "None", None] else ''}
                        {f'<p style="color: rgba(255,255,255,0.7); font-size: 0.9em;">🏁 Completed: {phase_end}</p>' if phase_end not in ["Not completed", "None", None] else ''}
                    </div>
                    
                </div>
            </div>
        </div>
        '''
    
    # HTML template
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{plan_name} - Plan Viewer</title>
    <style>
        /* CORTEX Plan Viewer - Glassmorphism Theme */
        :root {{
            --primary: #6D28D9;
            --primary-light: #7C3AED;
            --accent: #059669;
            --accent-light: #10B981;
            --warning: #D97706;
            --error: #DC2626;
            --bg-primary: rgba(30, 27, 75, 0.5);
            --bg-secondary: rgba(20, 18, 50, 0.6);
            --bg-hover: rgba(40, 35, 90, 0.55);
            --glass-blur: blur(12px);
            --glass-border: 1px solid rgba(255, 255, 255, 0.1);
            --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
            --text-primary: #D1D5DB;
            --text-secondary: #6B7280;
            --radius-lg: 16px;
            --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: var(--font-family);
            background: linear-gradient(135deg, #0f0e1f 0%, #1a1640 50%, #0f1f3f 100%);
            background-attachment: fixed;
            min-height: 100vh;
            padding: 20px;
            color: var(--text-primary);
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .glass {{
            background: var(--bg-primary);
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
            border: var(--glass-border);
            box-shadow: var(--glass-shadow);
            border-radius: var(--radius-lg);
            transition: all 0.3s ease;
        }}

        .glass:hover {{
            background: var(--bg-hover);
            transform: translateY(-2px);
        }}

        .header {{
            padding: 40px 30px;
            margin-bottom: 20px;
        }}
        
        .header-brand {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .header-logo {{
            width: 200px;
            height: 200px;
            object-fit: contain;
        }}
        
        .header-title-group {{
            flex: 1;
        }}

        .header h1 {{
            color: white;
            font-size: 2.5em;
            margin-bottom: 5px;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.6);
        }}

        .header .subtitle {{
            color: rgba(255, 255, 255, 0.75);
            font-size: 1.2em;
        }}

        .meta-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-top: 25px;
        }}

        .meta-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 18px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .meta-label {{
            font-size: 0.85em;
            opacity: 0.7;
            margin-bottom: 8px;
            text-transform: uppercase;
        }}

        .meta-value {{
            font-size: 1.5em;
            font-weight: 700;
            color: white;
        }}

        .overall-progress {{
            padding: 30px;
            margin-bottom: 20px;
        }}

        .progress-header {{
            color: white;
            font-size: 1.5em;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .progress-bar-container {{
            width: 100%;
            height: 45px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 25px;
            overflow: hidden;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .progress-bar {{
            height: 100%;
            background: linear-gradient(90deg, var(--accent) 0%, var(--accent-light) 50%, var(--primary-light) 100%);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.1em;
            color: white;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.6);
        }}

        .progress-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }}

        .stat-item {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 12px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            font-weight: 500;
            color: white;
        }}

        .stat-item span:last-child {{
            font-weight: 700;
            font-size: 1.2em;
        }}

        .phases-container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .phase-card {{
            padding: 25px;
        }}

        .phase-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}

        .phase-title {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}

        .phase-number {{
            color: var(--accent-light);
            font-weight: 700;
            font-size: 0.9em;
        }}

        .phase-name {{
            color: white;
            font-size: 1.1em;
            font-weight: 600;
        }}

        .phase-meta {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            font-size: 0.9em;
            color: rgba(255, 255, 255, 0.8);
        }}

        .status-badge {{
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 0.85em;
            font-weight: 700;
            text-transform: uppercase;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
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
            color: white;
        }}

        .auto-refresh {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 0.9em;
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 1000;
        }}

        .refresh-dot {{
            width: 10px;
            height: 10px;
            background: var(--accent);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.5; transform: scale(1.2); }}
        }}
        
        /* Modal Styles - Glassmorphism Design */
        .glass-modal-overlay {{
            position: fixed;
            inset: 0;
            background: rgba(10, 14, 39, 0.8);
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            z-index: 9999;
            display: none;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.3s ease;
        }}
        
        .glass-modal-overlay.open {{
            display: flex;
        }}
        
        .glass-modal {{
            background: rgba(26, 31, 58, 0.95);
            backdrop-filter: blur(30px);
            -webkit-backdrop-filter: blur(30px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 24px;
            padding: 2rem;
            max-width: 600px;
            max-height: 80vh;
            width: 90%;
            overflow-y: auto;
            box-shadow: 
                0 30px 80px rgba(0, 0, 0, 0.6),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
            animation: modalSlideUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        @keyframes modalSlideUp {{
            from {{
                opacity: 0;
                transform: translateY(50px) scale(0.9);
            }}
            to {{
                opacity: 1;
                transform: translateY(0) scale(1);
            }}
        }}
        
        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid rgba(5, 150, 105, 0.3);
        }}
        
        .modal-header h2 {{
            color: white;
            font-size: 1.5em;
            margin: 0;
        }}
        
        .modal-close {{
            background: rgba(220, 38, 38, 0.2);
            border: 1px solid rgba(220, 38, 38, 0.5);
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-size: 1.5em;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }}
        
        .modal-close:hover {{
            background: rgba(220, 38, 38, 0.4);
            transform: scale(1.1);
        }}
        
        .modal-content {{
            color: var(--text-primary);
        }}
        
        .modal-section {{
            margin-bottom: 1.25rem;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 1.25rem;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }}
        
        .modal-section:hover {{
            background: rgba(255, 255, 255, 0.05);
            transform: translateX(4px);
            border-color: rgba(255, 255, 255, 0.15);
        }}
        
        .modal-section h3 {{
            color: var(--accent-light);
            font-size: 0.95em;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid rgba(16, 185, 129, 0.2);
        }}
        
        .modal-section p {{
            line-height: 1.8;
            margin-bottom: 0.5rem;
            color: rgba(255, 255, 255, 0.9);
        }}
        
        .modal-section ul {{
            list-style: none;
            padding-left: 0;
            display: grid;
            gap: 0.75rem;
        }}
        
        .modal-section li {{
            padding: 0.75rem 1rem;
            background: linear-gradient(135deg, rgba(109, 40, 217, 0.08) 0%, rgba(5, 150, 105, 0.08) 100%);
            border-radius: 8px;
            border-left: 3px solid var(--accent);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            position: relative;
            overflow: hidden;
            font-size: 0.9em;
        }}
        
        .modal-section li::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .modal-section li:hover {{
            transform: translateX(6px) scale(1.01);
            box-shadow: 0 4px 16px rgba(5, 150, 105, 0.3);
            border-left-width: 4px;
        }}
        
        .modal-section li:hover::before {{
            opacity: 1;
        }}
        
        .modal-section code {{
            background: rgba(0, 0, 0, 0.4);
            padding: 4px 12px;
            border-radius: 6px;
            color: var(--accent-light);
            font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Courier New', monospace;
            font-size: 0.9em;
            border: 1px solid rgba(5, 150, 105, 0.3);
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .modal-stats-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.75rem;
            margin-top: 0.5rem;
        }}
        
        .modal-stat-tile {{
            background: rgba(109, 40, 217, 0.15);
            border: 1px solid rgba(124, 58, 237, 0.3);
            border-radius: 10px;
            padding: 0.75rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        .modal-stat-tile:hover {{
            background: rgba(109, 40, 217, 0.25);
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(109, 40, 217, 0.3);
        }}
        
        .modal-stat-label {{
            font-size: 0.7em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: rgba(255, 255, 255, 0.6);
            margin-bottom: 0.4rem;
            font-weight: 600;
        }}
        
        .modal-stat-value {{
            font-size: 1.3em;
            font-weight: 700;
            color: var(--accent-light);
            text-shadow: 0 2px 8px rgba(5, 150, 105, 0.5);
        }}
        
        .phase-card {{
            cursor: pointer;
        }}

        @media (max-width: 768px) {{
            .phases-container {{
                grid-template-columns: 1fr;
            }}
            
            .glass-modal {{
                width: 95%;
                padding: 2rem;
                max-height: 90vh;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header glass">
            <div class="header-brand">
                <img src="../../../../../docs/assets/images/CORTEX-logo.png" alt="CORTEX Logo" class="header-logo">
                <div class="header-title-group">
                    <h1>{plan_name}</h1>
                    <p class="subtitle">Feature Plan Progress Tracker</p>
                </div>
            </div>
            <div class="meta-info">
                <div class="meta-item">
                    <span class="meta-label">Plan ID</span>
                    <span class="meta-value">{plan_id}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Status</span>
                    <span class="meta-value">{status.replace('_', ' ').title()}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Total Phases</span>
                    <span class="meta-value">{total_phases}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Estimated Hours</span>
                    <span class="meta-value">{estimated_hours}h</span>
                </div>
                {f'<div class="meta-item"><span class="meta-label">Actual Hours</span><span class="meta-value">{actual_hours}h</span></div>' if actual_hours > 0 else ''}
            </div>
        </div>

        <div class="overall-progress glass">
            <div class="progress-header">
                📊 Overall Progress
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar" id="overall-progress-bar" style="width: {overall_progress}%">
                    <span id="overall-percentage">{overall_progress:.1f}%</span>
                </div>
            </div>
            <div class="progress-stats">
                <div class="stat-item">
                    <span>✅ Complete:</span>
                    <span id="complete-count">{completed_phases}</span>
                </div>
                <div class="stat-item">
                    <span>⏳ In Progress:</span>
                    <span id="inprogress-count">{in_progress_phases}</span>
                </div>
                <div class="stat-item">
                    <span>❌ Failed:</span>
                    <span id="failed-count">{failed_phases}</span>
                </div>
                <div class="stat-item">
                    <span>🔲 Not Started:</span>
                    <span id="notstarted-count">{not_started_phases}</span>
                </div>
            </div>
        </div>

        <div class="phases-container" id="phases-container">
            {phases_html}
        </div>
    </div>

    <div class="auto-refresh">
        <div class="refresh-dot"></div>
        <span>Auto-refresh: 60s | Last: <span id="last-update">--:--:--</span></span>
    </div>

    <script>
        const TRACKING_FILE = 'tracking/progress-tracker.json';
        const REFRESH_INTERVAL = 60000; // 60 seconds (1 minute)

        function updateTimestamp() {{
            const now = new Date();
            const timeStr = now.toLocaleTimeString();
            document.getElementById('last-update').textContent = timeStr;
        }}

        async function loadProgress() {{
            try {{
                const response = await fetch(TRACKING_FILE + '?t=' + Date.now());
                const data = await response.json();
                
                // Update progress bar
                const phases = data.phases || [];
                const total = phases.length;
                const complete = phases.filter(p => p.status === 'complete').length;
                const progress = (complete / total * 100).toFixed(1);
                
                document.getElementById('overall-progress-bar').style.width = progress + '%';
                document.getElementById('overall-percentage').textContent = progress + '%';
                
                // Update stats
                document.getElementById('complete-count').textContent = complete;
                document.getElementById('inprogress-count').textContent = 
                    phases.filter(p => p.status === 'in_progress').length;
                document.getElementById('failed-count').textContent = 
                    phases.filter(p => p.status === 'failed').length;
                document.getElementById('notstarted-count').textContent = 
                    phases.filter(p => p.status === 'not_started').length;
                
                updateTimestamp();
            }} catch (error) {{
                console.error('Failed to load progress:', error);
            }}
        }}
        
        // Modal functions
        function openPhaseModal(phaseId) {{
            const modal = document.getElementById('modal-' + phaseId);
            if (modal) {{
                modal.classList.add('open');
                // Prevent body scroll when modal is open
                document.body.style.overflow = 'hidden';
            }}
        }}
        
        function closePhaseModal(phaseId, event) {{
            if (event) {{
                event.stopPropagation();
            }}
            const modal = document.getElementById('modal-' + phaseId);
            if (modal) {{
                modal.classList.remove('open');
                // Restore body scroll
                document.body.style.overflow = 'auto';
            }}
        }}
        
        // Close modal on ESC key
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                const openModals = document.querySelectorAll('.glass-modal-overlay.open');
                openModals.forEach(modal => {{
                    modal.classList.remove('open');
                }});
                document.body.style.overflow = 'auto';
            }}
        }});

        // Initial load
        loadProgress();
        updateTimestamp();
        
        // Auto-refresh
        setInterval(loadProgress, REFRESH_INTERVAL);
    </script>
</body>
</html>
'''
    
    # Write HTML file
    output_path = plan_path / "plan-viewer.html"
    output_path.write_text(html_content, encoding='utf-8')
    
    return output_path


def generate_launcher_script(plan_path: Path) -> Path:
    """Generate launch_plan_viewer.py script."""
    launcher_content = '''#!/usr/bin/env python3
"""
Plan Viewer Server Launcher
Auto-launches HTTP server and opens browser for plan-viewer.html
"""

import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def find_plan_root():
    """Find plan root directory containing plan-viewer.html"""
    current = Path.cwd()
    
    # Check if we're in plan root
    if (current / 'plan-viewer.html').exists():
        return current
    
    # Check if script is in plan directory
    script_dir = Path(__file__).parent
    if (script_dir / 'plan-viewer.html').exists():
        return script_dir
    
    # Search parent directories
    for parent in current.parents:
        if (parent / 'plan-viewer.html').exists():
            return parent
    
    return None


def find_project_root(plan_root):
    """Find CORTEX project root (where HTTP server should run from)"""
    current = plan_root
    
    # Look for .git directory (project root indicator)
    for _ in range(10):  # Max 10 levels up
        if (current / '.git').exists():
            return current
        if current.parent == current:  # Reached filesystem root
            break
        current = current.parent
    
    return None


def main():
    """Launch HTTP server and open plan viewer in browser"""
    print("🚀 CORTEX Plan Viewer Launcher")
    print("=" * 50)
    
    # Find plan root
    plan_root = find_plan_root()
    if not plan_root:
        print("❌ Error: Cannot find plan-viewer.html")
        print("   Make sure you're in the plan directory or a subdirectory")
        return 1
    
    print(f"📁 Plan root: {plan_root}")
    
    # Find project root
    project_root = find_project_root(plan_root)
    if not project_root:
        print("❌ Error: Cannot find CORTEX project root (.git directory)")
        print("   HTTP server needs to run from project root")
        return 1
    
    print(f"🏠 Project root: {project_root}")
    
    # Construct relative path from project root to plan viewer
    try:
        rel_path = plan_root.relative_to(project_root)
        viewer_url = f"http://localhost:8000/{rel_path}/plan-viewer.html"
    except ValueError:
        print(f"❌ Error: Plan directory not under project root")
        return 1
    
    print(f"🌐 Viewer URL: {viewer_url}")
    print()
    
    # Check if server is already running
    try:
        import urllib.request
        urllib.request.urlopen('http://localhost:8000', timeout=1)
        server_running = True
        print("✅ HTTP server already running on port 8000")
    except:
        server_running = False
    
    # Start HTTP server if not running
    if not server_running:
        print("🔧 Starting HTTP server on port 8000...")
        try:
            subprocess.Popen(
                [sys.executable, "-m", "http.server", "8000"],
                cwd=project_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("✅ HTTP server started")
            
            # Wait for server to start
            print("⏳ Waiting for server startup...")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Failed to start HTTP server: {e}")
            return 1
    
    # Open browser
    print("🌐 Opening browser...")
    try:
        webbrowser.open(viewer_url)
        print("✅ Plan viewer opened in browser")
        print()
        print("📊 Real-time progress tracking enabled (30s refresh)")
        print("🛑 To stop server: Press Ctrl+C in terminal where server is running")
        return 0
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print(f"   Please manually open: {viewer_url}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
'''
    
    launcher_path = plan_path / "launch_plan_viewer.py"
    launcher_path.write_text(launcher_content, encoding='utf-8')
    launcher_path.chmod(0o755)  # Make executable
    
    return launcher_path


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python3 generate_feature_plan_viewer.py <plan_directory>")
        print()
        print("Example:")
        print("  python3 generate_feature_plan_viewer.py cortex-brain/documents/planning/active/c150-remediation-plan")
        return 1
    
    plan_path = Path(sys.argv[1])
    
    print("🧠 CORTEX Feature Plan Viewer Generator")
    print("=" * 60)
    print()
    
    # Validate plan
    print("🔍 Validating plan structure...")
    is_valid, error_msg = validate_feature_plan(plan_path)
    if not is_valid:
        print(f"❌ Validation failed: {error_msg}")
        return 1
    print("✅ Plan structure validated")
    print()
    
    # Load progress tracker
    print("📊 Loading progress tracker...")
    try:
        tracker_data = load_progress_tracker(plan_path)
        print(f"✅ Loaded: {tracker_data.get('plan_name', 'Untitled Plan')}")
        print(f"   Phases: {len(tracker_data.get('phases', []))}")
        print()
    except Exception as e:
        print(f"❌ Failed to load progress tracker: {e}")
        return 1
    
    # Generate HTML viewer
    print("🎨 Generating plan-viewer.html...")
    try:
        viewer_path = generate_html_viewer(plan_path, tracker_data)
        print(f"✅ Generated: {viewer_path}")
        print(f"   File size: {viewer_path.stat().st_size:,} bytes")
        print()
    except Exception as e:
        print(f"❌ Failed to generate HTML viewer: {e}")
        return 1
    
    # Generate launcher script
    print("🚀 Generating launch_plan_viewer.py...")
    try:
        launcher_path = generate_launcher_script(plan_path)
        print(f"✅ Generated: {launcher_path}")
        print()
    except Exception as e:
        print(f"❌ Failed to generate launcher script: {e}")
        return 1
    
    # Success summary
    print("=" * 60)
    print("🎉 Plan viewer generation complete!")
    print()
    print("📁 Generated files:")
    print(f"   • {viewer_path.relative_to(Path.cwd())}")
    print(f"   • {launcher_path.relative_to(Path.cwd())}")
    print()
    print("🌐 To view:")
    print(f"   python3 {launcher_path.relative_to(Path.cwd())}")
    print()
    print("✨ Features:")
    print("   • Real-time progress tracking (auto-refresh 30s)")
    print("   • Glassmorphism UI (CORTEX brand colors)")
    print("   • Phase status indicators (⏳/✅/❌)")
    print("   • HTTP server auto-launch with browser integration")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
