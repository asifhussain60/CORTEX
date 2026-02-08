"""
Dashboard File Protocol Test Utility

Generates a test dashboard HTML file and validates file:// protocol compatibility.
Tests asset loading, relative paths, and browser rendering before production deployment.

Author: Asif Hussain
Authority: CORE-008 (TDD), Phase 40
AC-ID: TEST-DASHBOARD-001

Usage:
    python cortex/visualization/scripts/test_dashboard_file_protocol.py
    python cortex/visualization/scripts/test_dashboard_file_protocol.py --repo cortex
    python cortex/visualization/scripts/test_dashboard_file_protocol.py --open
"""

import argparse
import json
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


def get_cortex_root() -> Path:
    """Get CORTEX root directory."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "cortex" / "__init__.py").exists():
            return parent
    return Path.cwd()


def check_asset_paths(cortex_root: Path) -> Dict[str, List[str]]:
    """
    Check for required assets for dashboard rendering.
    
    Returns:
        Dict with 'found' and 'missing' lists
    """
    required_assets = [
        "docs/assets/css/main.css",
        "docs/assets/css/glass-design-tokens.css",
        "docs/assets/css/glass-base-patterns.css",
        "docs/assets/css/glass-ui-components.css",
        "docs/assets/images/CORTEX-logo-200.png",
        "docs/assets/images/CORTEX-logo-64.png",
    ]
    
    found = []
    missing = []
    
    for asset in required_assets:
        asset_path = cortex_root / asset
        if asset_path.exists():
            found.append(asset)
        else:
            missing.append(asset)
    
    return {"found": found, "missing": missing}


def generate_test_dashboard(
    cortex_root: Path,
    repo_name: str = "test-repo",
    output_path: Path = None
) -> Path:
    """
    Generate a minimal test dashboard HTML file.
    
    Args:
        cortex_root: CORTEX root directory
        repo_name: Repository name for testing
        output_path: Output file path (default: test_dashboard_{timestamp}.html)
        
    Returns:
        Path to generated HTML file
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = cortex_root / f"test_dashboard_{repo_name}_{timestamp}.html"
    
    # Sample dashboard data
    dashboard_data = {
        "repository_name": repo_name.upper(),
        "repository_path": str(cortex_root),
        "analysis_timestamp": datetime.now().isoformat(),
        "overview": {
            "total_files": 1000,
            "total_lines": 50000,
            "languages": {"Python": 800, "JavaScript": 200},
            "primary_language": "Python"
        },
        "metrics": {
            "code_quality": 8.5,
            "test_coverage": 85.0,
            "maintainability_index": 70.0
        }
    }
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{repo_name.upper()} | CORTEX Dashboard Test</title>
    
    <!-- TEST UTILITY: Validate file:// Protocol Compatibility -->
    
    <!-- Favicon -->
    <link href="docs/assets/images/CORTEX-logo-64.png" rel="icon" type="image/png">
    
    <!-- CORTEX Glassmorphism Theme -->
    <link href="docs/assets/css/main.css" rel="stylesheet">
    <link href="docs/assets/css/glass-design-tokens.css" rel="stylesheet">
    <link href="docs/assets/css/glass-base-patterns.css" rel="stylesheet">
    <link href="docs/assets/css/glass-ui-components.css" rel="stylesheet">
    
    <!-- Font Awesome (CDN - for icons) -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet" crossorigin="anonymous">
    
    <style>
        .test-banner {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: linear-gradient(90deg, #ffc107 0%, #ff9800 100%);
            color: #000;
            padding: 1rem;
            text-align: center;
            font-weight: 700;
            z-index: 10000;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        
        body {{
            padding-top: 60px;
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0a1428 0%, #1a2a4a 100%);
            color: #ffffff;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .dashboard-header {{
            display: flex;
            align-items: center;
            gap: 2rem;
            padding: 2rem;
            background: rgba(26, 31, 58, 0.7);
            border-radius: 16px;
            margin-bottom: 2rem;
            backdrop-filter: blur(10px);
        }}
        
        .logo {{
            width: 120px;
            height: 120px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.3);
        }}
        
        .header-content h1 {{
            font-size: 2.5rem;
            color: #00d4ff;
            margin: 0 0 0.5rem 0;
        }}
        
        .header-content .subtitle {{
            color: #a0a6c0;
            font-size: 1.1rem;
        }}
        
        .diagnostics-panel {{
            background: rgba(26, 31, 58, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
        }}
        
        .diagnostics-panel h2 {{
            color: #00d4ff;
            margin-bottom: 1.5rem;
        }}
        
        .diagnostic-item {{
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            background: rgba(10, 14, 39, 0.5);
            border-radius: 8px;
            margin-bottom: 0.75rem;
        }}
        
        .diagnostic-item.success {{
            border-left: 4px solid #00ff88;
        }}
        
        .diagnostic-item.error {{
            border-left: 4px solid #ff4444;
        }}
        
        .diagnostic-item.warning {{
            border-left: 4px solid #ffa500;
        }}
        
        .status-icon {{
            font-size: 1.5rem;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .metric-card {{
            background: rgba(26, 31, 58, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: #00d4ff;
            margin-bottom: 0.5rem;
        }}
        
        .metric-label {{
            font-size: 0.875rem;
            color: #a0a6c0;
            text-transform: uppercase;
        }}
        
        .console-output {{
            background: #000;
            color: #0f0;
            padding: 1.5rem;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            max-height: 400px;
            overflow-y: auto;
        }}
        
        .console-output div {{
            margin-bottom: 0.5rem;
        }}
    </style>
</head>
<body>
    <!-- Test Banner -->
    <div class="test-banner">
        🧪 CORTEX DASHBOARD TEST UTILITY - File Protocol Validation - Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
    
    <div class="container">
        <!-- Header -->
        <header class="dashboard-header">
            <img 
                src="docs/assets/images/CORTEX-logo-200.png" 
                alt="CORTEX Logo" 
                class="logo"
                onerror="this.style.border='3px solid red'; this.alt='❌ Logo Load Failed'"
            >
            <div class="header-content">
                <h1>{repo_name.upper()}</h1>
                <p class="subtitle">Test Dashboard - File Protocol Validation</p>
            </div>
        </header>
        
        <!-- Diagnostics Panel -->
        <div class="diagnostics-panel">
            <h2><i class="fas fa-stethoscope"></i> Asset Loading Diagnostics</h2>
            <div id="diagnostics-output"></div>
        </div>
        
        <!-- Metrics Grid -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">1,000</div>
                <div class="metric-label">Files</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">50K</div>
                <div class="metric-label">Lines of Code</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">85%</div>
                <div class="metric-label">Test Coverage</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">8.5</div>
                <div class="metric-label">Quality Score</div>
            </div>
        </div>
        
        <!-- Console Output -->
        <div class="diagnostics-panel">
            <h2><i class="fas fa-terminal"></i> Console Output</h2>
            <div id="console-output" class="console-output"></div>
        </div>
    </div>
    
    <!-- Embedded Dashboard Data -->
    <script type="application/json" id="dashboard-data">
{json.dumps(dashboard_data, indent=2)}
    </script>
    
    <!-- Diagnostic Script -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('🔍 CORTEX Dashboard Test Utility - Starting Diagnostics...');
            console.log('📍 File Location:', window.location.href);
            console.log('📍 Protocol:', window.location.protocol);
            
            const diagnosticsOutput = document.getElementById('diagnostics-output');
            const consoleOutput = document.getElementById('console-output');
            const diagnostics = [];
            const logs = [];
            
            function log(message, type = 'info') {{
                console.log(message);
                logs.push(`[${{type.toUpperCase()}}] ${{message}}`);
            }}
            
            function addDiagnostic(status, icon, message) {{
                diagnostics.push({{
                    status: status,
                    icon: icon,
                    message: message
                }});
            }}
            
            // Test 1: Protocol Check
            log('Test 1: Protocol Check');
            const protocol = window.location.protocol;
            if (protocol === 'file:') {{
                addDiagnostic('success', '✅', `Protocol: ${{protocol}} (File Protocol Active)`);
                log('✅ File protocol detected', 'success');
            }} else if (protocol.startsWith('http')) {{
                addDiagnostic('warning', '⚠️', `Protocol: ${{protocol}} (HTTP/HTTPS - CDN assets will load)`);
                log('⚠️ HTTP protocol detected - CDN dependencies available', 'warning');
            }} else {{
                addDiagnostic('error', '❌', `Protocol: ${{protocol}} (Unknown)`);
                log('❌ Unknown protocol', 'error');
            }}
            
            // Test 2: CSS Loading
            log('Test 2: CSS Loading');
            const cssLinks = document.querySelectorAll('link[rel="stylesheet"]:not([href*="cdnjs"])');
            let cssLoaded = 0;
            let cssFailed = 0;
            
            cssLinks.forEach(link => {{
                if (link.sheet) {{
                    cssLoaded++;
                    log(`✅ CSS Loaded: ${{link.href}}`,'success');
                }} else {{
                    cssFailed++;
                    log(`❌ CSS Failed: ${{link.href}}`, 'error');
                }}
            }});
            
            if (cssFailed === 0) {{
                addDiagnostic('success', '✅', `CSS: ${{cssLoaded}}/${{cssLinks.length}} stylesheets loaded`);
            }} else {{
                addDiagnostic('error', '❌', `CSS: ${{cssFailed}}/${{cssLinks.length}} stylesheets failed`);
            }}
            
            // Test 3: Image Loading
            log('Test 3: Image Loading');
            const images = document.querySelectorAll('img');
            let imagesLoaded = 0;
            let imagesFailed = 0;
            
            setTimeout(() => {{
                images.forEach(img => {{
                    if (img.complete && img.naturalHeight !== 0) {{
                        imagesLoaded++;
                        log(`✅ Image Loaded: ${{img.src}} (${{img.naturalWidth}}x${{img.naturalHeight}}px)`, 'success');
                    }} else {{
                        imagesFailed++;
                        log(`❌ Image Failed: ${{img.src}}`, 'error');
                    }}
                }});
                
                if (imagesFailed === 0) {{
                    addDiagnostic('success', '✅', `Images: ${{imagesLoaded}}/${{images.length}} loaded`);
                }} else {{
                    addDiagnostic('error', '❌', `Images: ${{imagesFailed}}/${{images.length}} failed`);
                }}
                
                updateDiagnosticsDisplay();
            }}, 1000);
            
            // Test 4: Dashboard Data Loading
            log('Test 4: Dashboard Data Loading');
            const dataElement = document.getElementById('dashboard-data');
            if (dataElement) {{
                try {{
                    const data = JSON.parse(dataElement.textContent);
                    addDiagnostic('success', '✅', `Dashboard Data: Loaded (${{Object.keys(data).length}} keys)`);
                    log(`✅ Dashboard data loaded: ${{Object.keys(data).join(', ')}}`, 'success');
                    window.dashboardData = data;
                }} catch (e) {{
                    addDiagnostic('error', '❌', `Dashboard Data: Parse Error - ${{e.message}}`);
                    log(`❌ Dashboard data parse error: ${{e.message}}`, 'error');
                }}
            }} else {{
                addDiagnostic('error', '❌', 'Dashboard Data: Element not found');
                log('❌ Dashboard data element not found', 'error');
            }}
            
            // Test 5: External Dependencies (CDN)
            log('Test 5: External Dependencies');
            const cdnLinks = document.querySelectorAll('link[href*="cdnjs"], link[href*="d3js"], script[src*="cdnjs"], script[src*="d3js"]');
            if (protocol === 'file:') {{
                addDiagnostic('warning', '⚠️', `CDN Assets: ${{cdnLinks.length}} detected - Will NOT load with file:// protocol`);
                log(`⚠️ CDN dependencies detected: ${{cdnLinks.length}} - These require HTTP/HTTPS`, 'warning');
            }} else {{
                addDiagnostic('success', '✅', `CDN Assets: ${{cdnLinks.length}} detected - Available via HTTP`);
                log(`✅ CDN dependencies available: ${{cdnLinks.length}}`, 'success');
            }}
            
            function updateDiagnosticsDisplay() {{
                // Render diagnostics
                diagnosticsOutput.innerHTML = diagnostics.map(d => `
                    <div class="diagnostic-item ${{d.status}}">
                        <span class="status-icon">${{d.icon}}</span>
                        <span>${{d.message}}</span>
                    </div>
                `).join('');
                
                // Render console logs
                consoleOutput.innerHTML = logs.map(log => `<div>${{log}}</div>`).join('');
                
                // Final summary
                const successCount = diagnostics.filter(d => d.status === 'success').length;
                const errorCount = diagnostics.filter(d => d.status === 'error').length;
                const warningCount = diagnostics.filter(d => d.status === 'warning').length;
                
                log('');
                log('='.repeat(60));
                log('DIAGNOSTIC SUMMARY');
                log('='.repeat(60));
                log(`✅ Passed: ${{successCount}}`);
                log(`⚠️ Warnings: ${{warningCount}}`);
                log(`❌ Failed: ${{errorCount}}`);
                log('='.repeat(60));
                
                if (errorCount === 0 && warningCount === 0) {{
                    log('🎉 All tests passed! Dashboard ready for file:// protocol.', 'success');
                }} else if (errorCount === 0) {{
                    log('⚠️ Tests passed with warnings. Review CDN dependencies.', 'warning');
                }} else {{
                    log('❌ Tests failed. Fix asset paths before deployment.', 'error');
                }}
                
                consoleOutput.innerHTML = logs.map(log => `<div>${{log}}</div>`).join('');
            }}
            
            updateDiagnosticsDisplay();
        }});
    </script>
</body>
</html>'''
    
    output_path.write_text(html_content, encoding='utf-8')
    return output_path


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test dashboard file:// protocol compatibility'
    )
    parser.add_argument(
        '--repo',
        default='test-repo',
        help='Repository name for test dashboard (default: test-repo)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output file path (default: auto-generated)'
    )
    parser.add_argument(
        '--open',
        action='store_true',
        help='Open generated HTML in default browser'
    )
    parser.add_argument(
        '--check-assets',
        action='store_true',
        help='Check for required assets before generation'
    )
    
    args = parser.parse_args()
    
    cortex_root = get_cortex_root()
    print(f"📁 CORTEX Root: {cortex_root}")
    
    # Check assets if requested
    if args.check_assets:
        print("\n🔍 Checking for required assets...")
        asset_status = check_asset_paths(cortex_root)
        
        print(f"\n✅ Found: {len(asset_status['found'])} assets")
        for asset in asset_status['found']:
            print(f"  ✓ {asset}")
        
        if asset_status['missing']:
            print(f"\n❌ Missing: {len(asset_status['missing'])} assets")
            for asset in asset_status['missing']:
                print(f"  ✗ {asset}")
            print("\n⚠️ Some assets are missing. Dashboard may not render correctly.")
        else:
            print("\n✅ All required assets found!")
    
    # Generate test dashboard
    print(f"\n🔨 Generating test dashboard for '{args.repo}'...")
    output_path = generate_test_dashboard(
        cortex_root=cortex_root,
        repo_name=args.repo,
        output_path=args.output
    )
    
    print(f"\n✅ Test dashboard generated: {output_path}")
    print(f"\n📍 File URL: file:///{output_path.as_posix()}")
    
    # Open in browser if requested
    if args.open:
        print("\n🌐 Opening in default browser...")
        webbrowser.open(output_path.as_uri())
    
    print("\n" + "="*70)
    print("USAGE INSTRUCTIONS")
    print("="*70)
    print("1. Open the generated HTML file in a browser")
    print("2. Check the diagnostics panel for asset loading status")
    print("3. Open Developer Console (F12) to see detailed logs")
    print("4. Verify all assets load correctly with file:// protocol")
    print("="*70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
