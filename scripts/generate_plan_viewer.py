#!/usr/bin/env python3
"""
CORTEX Plan Viewer Generator
Generates interactive HTML viewer for YAML-based feature plans

Usage:
    python3 generate_plan_viewer.py <plan_directory>
    
Example:
    python3 generate_plan_viewer.py cortex-brain/documents/planning/active/c150-remediation-plan

Features:
- Auto-detects FEATURE mode (single YAML plan)
- Generates glassmorphism UI with CORTEX branding
- Real-time progress tracking (30s auto-refresh)
- Launcher script generation (HTTP server + browser)

Author: CORTEX Planning System v5
Date: 2026-01-04
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def load_progress_tracker(plan_path: Path) -> dict:
    """Load progress tracker JSON."""
    tracker_path = plan_path / "tracking" / "progress-tracker.json"
    
    if not tracker_path.exists():
        raise FileNotFoundError(f"Progress tracker not found: {tracker_path}")
    
    with open(tracker_path, 'r') as f:
        return json.load(f)


def generate_html_viewer(plan_path: Path, tracker_data: dict) -> Path:
    """Generate plan-viewer.html from template."""
    
    plan_name = tracker_data.get("plan_name", "Untitled Plan")
    plan_id = tracker_data.get("plan_id", "unknown")
    estimated_hours = tracker_data.get("estimated_total_hours", 0)
    status = tracker_data.get("status", "not_started")
    
    # Calculate phase statistics
    phases = tracker_data.get("phases", [])
    total_phases = len(phases)
    completed_phases = sum(1 for p in phases if p.get("status") == "complete")
    in_progress_phases = sum(1 for p in phases if p.get("status") == "in_progress")
    
    # Calculate overall progress
    if total_phases > 0:
        overall_progress = int((completed_phases / total_phases) * 100)
    else:
        overall_progress = 0
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{plan_name} - Plan Viewer</title>
    <style>
        :root {{
            --primary: #6D28D9;
            --primary-light: #7C3AED;
            --accent: #059669;
            --accent-light: #10B981;
            --warning: #D97706;
            --error: #DC2626;
            --bg-primary: rgba(30, 27, 75, 0.5);
            --bg-secondary: rgba(20, 18, 50, 0.6);
            --glass-blur: blur(12px);
            --glass-border: 1px solid rgba(255, 255, 255, 0.1);
            --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
            --text-primary: #D1D5DB;
            --text-secondary: #6B7280;
            --radius-lg: 16px;
            --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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

        .header {{
            padding: 40px 30px;
            margin-bottom: 20px;
        }}

        .header h1 {{
            color: white;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.6);
        }}

        .header .subtitle {{
            color: rgba(255, 255, 255, 0.75);
            font-size: 1.1em;
        }}

        .meta-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}

        .meta-item {{
            text-align: center;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
        }}

        .meta-label {{
            font-size: 0.9em;
            opacity: 0.7;
            margin-bottom: 8px;
            text-transform: uppercase;
        }}

        .meta-value {{
            font-size: 1.8em;
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
            font-weight: 600;
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
            background: linear-gradient(90deg, var(--accent) 0%, var(--primary-light) 100%);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            color: white;
            border-radius: 25px;
        }}

        .phases-container {{
            margin-top: 20px;
        }}

        .phase {{
            padding: 20px;
            margin-bottom: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .phase:hover {{
            transform: translateY(-2px);
            box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.6);
        }}

        .phase-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}

        .phase-title {{
            color: white;
            font-size: 1.2em;
            font-weight: 600;
        }}

        .status-badge {{
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 700;
            text-transform: uppercase;
        }}

        .status-complete {{
            background: linear-gradient(135deg, #059669 0%, #10B981 100%);
            color: white;
        }}

        .status-in-progress {{
            background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%);
            color: white;
        }}

        .status-not-started {{
            background: rgba(75, 85, 99, 0.8);
            color: white;
        }}

        .phase-meta {{
            display: flex;
            gap: 20px;
            font-size: 0.9em;
            color: rgba(255, 255, 255, 0.8);
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

        .loading {{
            text-align: center;
            color: white;
            padding: 50px;
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header glass">
            <h1>📋 {plan_name}</h1>
            <p class="subtitle">Plan ID: {plan_id}</p>
            <div class="meta-info">
                <div class="meta-item">
                    <div class="meta-label">Total Phases</div>
                    <div class="meta-value">{total_phases}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Completed</div>
                    <div class="meta-value">{completed_phases}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">In Progress</div>
                    <div class="meta-value">{in_progress_phases}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">Estimated Hours</div>
                    <div class="meta-value">{estimated_hours}</div>
                </div>
            </div>
        </div>

        <div class="overall-progress glass">
            <div class="progress-header">📊 Overall Progress</div>
            <div class="progress-bar-container">
                <div class="progress-bar" id="overall-progress-bar" style="width: {overall_progress}%">
                    <span id="overall-percentage">{overall_progress}%</span>
                </div>
            </div>
        </div>

        <div class="phases-container" id="phases-container">
            <div class="loading">Loading phases...</div>
        </div>
    </div>

    <div class="auto-refresh">
        <div class="refresh-dot"></div>
        <span>Auto-refresh: 30s | Last: <span id="last-update">--:--:--</span></span>
    </div>

    <script>
        const TRACKING_FILE = 'tracking/progress-tracker.json';
        const REFRESH_INTERVAL = 30000; // 30 seconds

        let planData = null;
        let autoRefreshTimer = null;

        document.addEventListener('DOMContentLoaded', () => {{
            loadPlanData();
            startAutoRefresh();
        }});

        async function loadPlanData() {{
            try {{
                const response = await fetch(TRACKING_FILE);
                if (!response.ok) throw new Error('Failed to load tracking data');
                
                planData = await response.json();
                renderPhases();
                updateTimestamp();
            }} catch (error) {{
                console.error('Error loading plan data:', error);
                document.getElementById('phases-container').innerHTML = 
                    '<div class="loading">Error loading plan data</div>';
            }}
        }}

        function renderPhases() {{
            if (!planData || !planData.phases) return;

            const container = document.getElementById('phases-container');
            container.innerHTML = '';

            planData.phases.forEach(phase => {{
                const phaseDiv = document.createElement('div');
                phaseDiv.className = 'phase glass';
                
                const statusClass = getStatusClass(phase.status);
                const estimatedHours = phase.estimated_hours || 0;
                const actualHours = phase.actual_hours || 0;
                
                phaseDiv.innerHTML = `
                    <div class="phase-header">
                        <div class="phase-title">Phase ${{phase.number}}: ${{phase.name}}</div>
                        <span class="status-badge status-${{phase.status}}">
                            ${{getStatusEmoji(phase.status)}} ${{phase.status.replace('_', ' ')}}
                        </span>
                    </div>
                    <div class="phase-meta">
                        <span>⏱️ Est: ${{estimatedHours}}h</span>
                        ${{actualHours > 0 ? `<span>✅ Actual: ${{actualHours}}h</span>` : ''}}
                        <span>📂 Outputs: ${{(phase.outputs || []).length}}</span>
                    </div>
                `;
                
                container.appendChild(phaseDiv);
            }});
        }}

        function getStatusClass(status) {{
            if (status === 'complete') return 'status-complete';
            if (status === 'in_progress') return 'status-in-progress';
            return 'status-not-started';
        }}

        function getStatusEmoji(status) {{
            if (status === 'complete') return '✅';
            if (status === 'in_progress') return '⏳';
            return '⏸️';
        }}

        function startAutoRefresh() {{
            autoRefreshTimer = setInterval(loadPlanData, REFRESH_INTERVAL);
        }}

        function updateTimestamp() {{
            const now = new Date();
            const timeStr = now.toLocaleTimeString();
            document.getElementById('last-update').textContent = timeStr;
        }}

        window.addEventListener('beforeunload', () => {{
            if (autoRefreshTimer) clearInterval(autoRefreshTimer);
        }});
    </script>
</body>
</html>'''
    
    output_path = plan_path / "plan-viewer.html"
    output_path.write_text(html_content)
    
    return output_path


def generate_launcher_script(plan_path: Path) -> Path:
    """Generate launch_plan_viewer.py script."""
    
    launcher_content = '''#!/usr/bin/env python3
"""
Plan Viewer Launcher
Auto-launches HTTP server and opens browser for plan-viewer.html
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path


def find_plan_root():
    """Find the plan root directory."""
    current = Path.cwd()
    
    # Check if we're already in plan root
    if (current / 'plan-viewer.html').exists():
        return current
    
    # Search parent directories
    for parent in current.parents:
        if (parent / 'plan-viewer.html').exists():
            return parent
    
    return None


def find_project_root(plan_root):
    """Find the CORTEX project root."""
    current = plan_root
    
    # Look for .git directory (project root indicator)
    for _ in range(10):  # Max 10 levels up
        if (current / '.git').exists():
            return current
        current = current.parent
        if current == current.parent:  # Reached filesystem root
            break
    
    return None


def main():
    print("🚀 CORTEX Plan Viewer Launcher")
    print("=" * 50)
    
    # Find plan root
    plan_root = find_plan_root()
    if not plan_root:
        print("❌ Cannot find plan-viewer.html")
        print("   Run this script from the plan directory or its subdirectories")
        return 1
    
    print(f"📂 Plan root: {plan_root}")
    
    # Find project root
    project_root = find_project_root(plan_root)
    if not project_root:
        print("❌ Cannot find CORTEX project root (.git directory)")
        return 1
    
    print(f"🏠 Project root: {project_root}")
    
    # Construct relative path
    try:
        rel_path = plan_root.relative_to(project_root)
    except ValueError:
        print("❌ Plan directory is not within project root")
        return 1
    
    viewer_url = f"http://localhost:8000/{rel_path}/plan-viewer.html"
    
    print(f"🌐 Viewer URL: {viewer_url}")
    print()
    
    # Check if server is already running
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        
        if result == 0:
            print("✅ HTTP server already running on port 8000")
            server_started = False
        else:
            # Start HTTP server (non-blocking)
            print("🔧 Starting HTTP server on port 8000...")
            subprocess.Popen(
                [sys.executable, "-m", "http.server", "8000"],
                cwd=project_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            server_started = True
            
            # Wait for server startup
            print("⏳ Waiting for server startup...")
            time.sleep(2)
    except Exception as e:
        print(f"⚠️  Error checking/starting server: {e}")
        return 1
    
    # Open browser
    print("🌐 Opening plan viewer in browser...")
    try:
        webbrowser.open(viewer_url)
        print()
        print("✅ Plan viewer opened successfully!")
        print()
        
        if server_started:
            print("💡 HTTP server is running in background")
            print("   To stop: kill the Python http.server process")
        
        print()
        print("📊 The plan viewer will auto-refresh every 30 seconds")
        print("   to show latest progress updates")
        
        return 0
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print(f"   Manually open: {viewer_url}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
'''
    
    output_path = plan_path / "launch_plan_viewer.py"
    output_path.write_text(launcher_content)
    output_path.chmod(0o755)  # Make executable
    
    return output_path


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python3 generate_plan_viewer.py <plan_directory>")
        print()
        print("Example:")
        print("  python3 generate_plan_viewer.py cortex-brain/documents/planning/active/c150-remediation-plan")
        sys.exit(1)
    
    plan_path = Path(sys.argv[1])
    
    if not plan_path.exists():
        print(f"❌ Plan directory not found: {plan_path}")
        sys.exit(1)
    
    if not plan_path.is_dir():
        print(f"❌ Not a directory: {plan_path}")
        sys.exit(1)
    
    print("🎨 CORTEX Plan Viewer Generator")
    print("=" * 60)
    print(f"📂 Plan: {plan_path.name}")
    print()
    
    try:
        # Load progress tracker
        print("📊 Loading progress tracker...")
        tracker_data = load_progress_tracker(plan_path)
        print(f"✅ Loaded: {tracker_data['plan_name']}")
        print()
        
        # Generate HTML viewer
        print("🎨 Generating plan-viewer.html...")
        viewer_path = generate_html_viewer(plan_path, tracker_data)
        file_size = viewer_path.stat().st_size
        print(f"✅ Generated: {viewer_path}")
        print(f"📁 File size: {file_size:,} bytes")
        print()
        
        # Generate launcher script
        print("🚀 Generating launch_plan_viewer.py...")
        launcher_path = generate_launcher_script(plan_path)
        print(f"✅ Generated: {launcher_path}")
        print()
        
        # Success summary
        print("=" * 60)
        print("🎉 Plan viewer generation complete!")
        print()
        print("🌐 To view the plan:")
        print(f"   cd {plan_path}")
        print("   python3 launch_plan_viewer.py")
        print()
        print("📊 Features:")
        print("   • Real-time progress tracking (30s auto-refresh)")
        print("   • Glassmorphism UI with CORTEX branding")
        print("   • Phase status indicators (⏸️/⏳/✅)")
        print("   • Auto HTTP server + browser launch")
        print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
