"""
Generate Health Dashboard for KSESSIONS Repository

This script analyzes the KSESSIONS repository and generates an interactive
HTML health dashboard showing code quality, architecture, and metrics.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add CORTEX to path
cortex_root = Path(__file__).parent.parent
sys.path.insert(0, str(cortex_root))

from src.crawlers.application_scoped_crawler import ApplicationScopedCrawler, ApplicationContext
from src.crawlers.analyzers.python_analyzer import PythonAnalyzer
from src.crawlers.analyzers.javascript_analyzer import JavaScriptAnalyzer
from src.crawlers.analyzers.generic_analyzer import GenericAnalyzer


def analyze_ksessions(ksessions_path: Path, scan_level: str = "standard") -> dict:
    """
    Analyze KSESSIONS repository and collect metrics.
    
    Args:
        ksessions_path: Path to KSESSIONS repository
        scan_level: Scan depth - "overview", "standard", or "deep"
    
    Returns:
        Dictionary containing analysis results
    """
    print(f"🔍 Analyzing KSESSIONS at: {ksessions_path}")
    print(f"📊 Scan Level: {scan_level}")
    start_time = time.time()
    
    # Initialize analyzers
    python_analyzer = PythonAnalyzer()
    js_analyzer = JavaScriptAnalyzer()
    generic_analyzer = GenericAnalyzer()
    
    # Collect files
    python_files = list(ksessions_path.rglob("*.py"))
    js_files = list(ksessions_path.rglob("*.js")) + list(ksessions_path.rglob("*.ts"))
    all_files = list(ksessions_path.rglob("*.*"))
    
    print(f"  📁 Found {len(python_files)} Python files")
    print(f"  📁 Found {len(js_files)} JavaScript/TypeScript files")
    print(f"  📁 Found {len(all_files)} total files")
    
    # Analyze Python files
    python_metrics = {
        "total_files": len(python_files),
        "total_lines": 0,
        "total_functions": 0,
        "total_classes": 0,
        "complexity_scores": []
    }
    
    for py_file in python_files[:50 if scan_level == "standard" else len(python_files)]:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                metrics = python_analyzer.analyze(content, str(py_file))
                python_metrics["total_lines"] += metrics.get("lines_of_code", 0)
                python_metrics["total_functions"] += len(metrics.get("functions", []))
                python_metrics["total_classes"] += len(metrics.get("classes", []))
                if "complexity" in metrics:
                    python_metrics["complexity_scores"].append(metrics["complexity"])
        except Exception as e:
            print(f"    ⚠️ Error analyzing {py_file.name}: {e}")
    
    # Analyze JavaScript files
    js_metrics = {
        "total_files": len(js_files),
        "total_lines": 0,
        "estimated_components": 0
    }
    
    for js_file in js_files[:50 if scan_level == "standard" else len(js_files)]:
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
                js_metrics["total_lines"] += len(content.split('\n'))
                # Simple heuristic for components
                if 'class ' in content or 'function ' in content:
                    js_metrics["estimated_components"] += content.count('class ') + content.count('function ')
        except Exception as e:
            print(f"    ⚠️ Error analyzing {js_file.name}: {e}")
    
    # Calculate overall metrics
    avg_complexity = sum(python_metrics["complexity_scores"]) / len(python_metrics["complexity_scores"]) if python_metrics["complexity_scores"] else 0
    
    elapsed = time.time() - start_time
    print(f"✅ Analysis complete in {elapsed:.2f} seconds")
    
    return {
        "repository": str(ksessions_path),
        "scan_level": scan_level,
        "timestamp": datetime.now().isoformat(),
        "execution_time": elapsed,
        "python": python_metrics,
        "javascript": js_metrics,
        "overall": {
            "total_files": len(all_files),
            "total_python": len(python_files),
            "total_js": len(js_files),
            "avg_complexity": avg_complexity,
            "health_score": calculate_health_score(python_metrics, js_metrics, avg_complexity)
        }
    }


def calculate_health_score(python_metrics: dict, js_metrics: dict, avg_complexity: float) -> int:
    """Calculate overall health score (0-100)."""
    score = 100
    
    # Penalize high complexity
    if avg_complexity > 15:
        score -= 20
    elif avg_complexity > 10:
        score -= 10
    
    # Reward documentation (simple heuristic)
    if python_metrics["total_functions"] > 0:
        # Assume 70% documented for now
        score -= 10
    
    return max(0, min(100, score))


def generate_html_dashboard(analysis_results: dict, output_path: Path) -> None:
    """Generate interactive HTML dashboard."""
    print(f"📝 Generating dashboard: {output_path}")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KSESSIONS Health Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        header {{
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #888;
            font-size: 1.1em;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        .metric-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }}
        .health-score {{
            font-size: 4em;
            font-weight: bold;
            text-align: center;
            margin: 40px 0;
            color: {get_score_color(analysis_results['overall']['health_score'])};
        }}
        .section {{
            margin: 40px 0;
            padding: 30px;
            background: #f9f9f9;
            border-radius: 12px;
        }}
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        .detail-row {{
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #e0e0e0;
        }}
        .detail-label {{
            color: #666;
            font-weight: 500;
        }}
        .detail-value {{
            color: #333;
            font-weight: bold;
        }}
        .badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .badge-success {{
            background: #4caf50;
            color: white;
        }}
        .badge-warning {{
            background: #ff9800;
            color: white;
        }}
        .badge-info {{
            background: #2196f3;
            color: white;
        }}
        footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏥 KSESSIONS Health Dashboard</h1>
            <div class="subtitle">
                Generated: {analysis_results['timestamp']}<br>
                Scan Level: <span class="badge badge-info">{analysis_results['scan_level'].upper()}</span><br>
                Analysis Time: {analysis_results['execution_time']:.2f}s
            </div>
        </header>

        <div class="health-score">
            {analysis_results['overall']['health_score']}/100
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Files</div>
                <div class="metric-value">{analysis_results['overall']['total_files']:,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Python Files</div>
                <div class="metric-value">{analysis_results['overall']['total_python']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">JS/TS Files</div>
                <div class="metric-value">{analysis_results['overall']['total_js']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Complexity</div>
                <div class="metric-value">{analysis_results['overall']['avg_complexity']:.1f}</div>
            </div>
        </div>

        <div class="section">
            <h2>🐍 Python Analysis</h2>
            <div class="detail-row">
                <span class="detail-label">Total Python Files</span>
                <span class="detail-value">{analysis_results['python']['total_files']}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Total Lines of Code</span>
                <span class="detail-value">{analysis_results['python']['total_lines']:,}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Total Functions</span>
                <span class="detail-value">{analysis_results['python']['total_functions']}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Total Classes</span>
                <span class="detail-value">{analysis_results['python']['total_classes']}</span>
            </div>
        </div>

        <div class="section">
            <h2>⚛️ JavaScript/TypeScript Analysis</h2>
            <div class="detail-row">
                <span class="detail-label">Total JS/TS Files</span>
                <span class="detail-value">{analysis_results['javascript']['total_files']}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Total Lines of Code</span>
                <span class="detail-value">{analysis_results['javascript']['total_lines']:,}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Estimated Components</span>
                <span class="detail-value">{analysis_results['javascript']['estimated_components']}</span>
            </div>
        </div>

        <div class="section">
            <h2>📊 Quality Insights</h2>
            <div class="detail-row">
                <span class="detail-label">Code Health</span>
                <span class="detail-value">
                    <span class="badge {get_health_badge(analysis_results['overall']['health_score'])}">
                        {get_health_label(analysis_results['overall']['health_score'])}
                    </span>
                </span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Complexity Rating</span>
                <span class="detail-value">
                    <span class="badge {get_complexity_badge(analysis_results['overall']['avg_complexity'])}">
                        {get_complexity_label(analysis_results['overall']['avg_complexity'])}
                    </span>
                </span>
            </div>
        </div>

        <footer>
            <p><strong>CORTEX Application Health Dashboard</strong></p>
            <p>Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX</p>
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </footer>
    </div>
</body>
</html>
"""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard generated successfully!")
    print(f"   📂 Location: {output_path}")
    print(f"   🌐 Open in browser to view")


def get_score_color(score: int) -> str:
    """Get color based on health score."""
    if score >= 80:
        return "#4caf50"  # Green
    elif score >= 60:
        return "#ff9800"  # Orange
    else:
        return "#f44336"  # Red


def get_health_badge(score: int) -> str:
    """Get badge class for health score."""
    if score >= 80:
        return "badge-success"
    elif score >= 60:
        return "badge-warning"
    else:
        return "badge-danger"


def get_health_label(score: int) -> str:
    """Get label for health score."""
    if score >= 80:
        return "EXCELLENT"
    elif score >= 60:
        return "GOOD"
    else:
        return "NEEDS ATTENTION"


def get_complexity_badge(complexity: float) -> str:
    """Get badge class for complexity."""
    if complexity < 10:
        return "badge-success"
    elif complexity < 15:
        return "badge-warning"
    else:
        return "badge-danger"


def get_complexity_label(complexity: float) -> str:
    """Get label for complexity."""
    if complexity < 10:
        return "LOW"
    elif complexity < 15:
        return "MODERATE"
    else:
        return "HIGH"


def main():
    """Main execution."""
    print("\n" + "="*60)
    print("🧠 CORTEX Application Health Dashboard Generator")
    print("="*60 + "\n")
    
    # Paths
    ksessions_path = Path("D:/PROJECTS/KSESSIONS")
    output_path = Path("D:/PROJECTS/CORTEX/cortex-brain/dashboards/ksessions-health.html")
    
    # Validate KSESSIONS exists
    if not ksessions_path.exists():
        print(f"❌ ERROR: KSESSIONS not found at {ksessions_path}")
        print("   Please update the path in the script")
        return 1
    
    # Analyze repository
    try:
        analysis_results = analyze_ksessions(ksessions_path, scan_level="standard")
        
        # Generate dashboard
        generate_html_dashboard(analysis_results, output_path)
        
        print("\n" + "="*60)
        print("✅ SUCCESS: Health dashboard generated for KSESSIONS")
        print("="*60)
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
