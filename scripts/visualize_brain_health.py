"""
CORTEX Brain Health Trend Visualization

Generates charts from historical brain metrics for trend analysis.
Creates graphs showing knowledge growth, SKULL triggers, and health trends.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import yaml
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def load_metrics_history(metrics_dir: Path) -> List[Dict[str, Any]]:
    """Load all historical metrics files."""
    metrics_files = sorted(metrics_dir.glob("*.yaml"))
    metrics_history = []
    
    for file in metrics_files:
        if file.name == ".gitkeep":
            continue
            
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data:
                    metrics_history.append(data)
        except Exception as e:
            print(f"Warning: Could not load {file.name}: {e}")
    
    return metrics_history


def plot_knowledge_growth(metrics_history: List[Dict], output_dir: Path):
    """Plot knowledge graph pattern growth over time."""
    dates = [datetime.fromisoformat(m["timestamp"]) for m in metrics_history]
    patterns = [m["tier2"]["patterns_count"] for m in metrics_history]
    confidence = [m["tier2"]["avg_confidence"] for m in metrics_history]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Patterns count
    ax1.plot(dates, patterns, marker='o', linewidth=2, color='#4ec9b0')
    ax1.set_title('Knowledge Graph Growth', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Pattern Count', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Average confidence
    ax2.plot(dates, confidence, marker='s', linewidth=2, color='#ce9178')
    ax2.set_title('Pattern Confidence', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Avg Confidence', fontsize=12)
    ax2.set_ylim([0, 1.0])
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    output_file = output_dir / "knowledge-growth.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"   📈 {output_file.name}")
    return output_file


def plot_conversation_utilization(metrics_history: List[Dict], output_dir: Path):
    """Plot Tier 1 conversation memory utilization."""
    dates = [datetime.fromisoformat(m["timestamp"]) for m in metrics_history]
    utilization = [m["tier1"]["utilization_percent"] for m in metrics_history]
    conversations = [m["tier1"]["conversations_jsonl"] for m in metrics_history]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Utilization percentage
    ax1.plot(dates, utilization, marker='o', linewidth=2, color='#569cd6')
    ax1.axhline(y=80, color='#ce9178', linestyle='--', alpha=0.5, label='High Utilization')
    ax1.set_title('Tier 1 Memory Utilization', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Utilization %', fontsize=12)
    ax1.set_ylim([0, 100])
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # Conversation count
    ax2.plot(dates, conversations, marker='s', linewidth=2, color='#9cdcfe')
    ax2.axhline(y=20, color='#f48771', linestyle='--', alpha=0.5, label='FIFO Capacity')
    ax2.set_title('Conversation Count', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Count', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    output_file = output_dir / "conversation-utilization.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"   📊 {output_file.name}")
    return output_file


def plot_brain_health_score(metrics_history: List[Dict], output_dir: Path):
    """Plot overall brain health score over time."""
    dates = [datetime.fromisoformat(m["timestamp"]) for m in metrics_history]
    scores = [m["health"]["health_score"] for m in metrics_history]
    
    # Color code by health status
    colors = []
    for score in scores:
        if score >= 80:
            colors.append('#4ec9b0')  # Excellent - green
        elif score >= 60:
            colors.append('#569cd6')  # Good - blue
        elif score >= 40:
            colors.append('#ce9178')  # Fair - orange
        else:
            colors.append('#f48771')  # Needs Attention - red
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(dates, scores, marker='o', linewidth=2.5, color='#569cd6', alpha=0.7)
    ax.scatter(dates, scores, c=colors, s=100, zorder=5, edgecolors='white', linewidth=2)
    
    # Health thresholds
    ax.axhline(y=80, color='#4ec9b0', linestyle='--', alpha=0.3, label='Excellent')
    ax.axhline(y=60, color='#569cd6', linestyle='--', alpha=0.3, label='Good')
    ax.axhline(y=40, color='#ce9178', linestyle='--', alpha=0.3, label='Fair')
    
    ax.set_title('CORTEX Brain Health Score Over Time', fontsize=16, fontweight='bold')
    ax.set_ylabel('Health Score', fontsize=12)
    ax.set_ylim([0, 100])
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    output_file = output_dir / "brain-health-score.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"   🏥 {output_file.name}")
    return output_file


def plot_tier_sizes(metrics_history: List[Dict], output_dir: Path):
    """Plot storage sizes for each tier."""
    dates = [datetime.fromisoformat(m["timestamp"]) for m in metrics_history]
    tier0_sizes = [m["tier0"]["rules_file_size_kb"] for m in metrics_history]
    tier1_sizes = [m["tier1"]["jsonl_size_kb"] for m in metrics_history]
    tier2_sizes = [m["tier2"]["file_size_kb"] for m in metrics_history]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(dates, tier0_sizes, marker='o', linewidth=2, label='Tier 0 (Governance)', color='#f48771')
    ax.plot(dates, tier1_sizes, marker='s', linewidth=2, label='Tier 1 (Memory)', color='#569cd6')
    ax.plot(dates, tier2_sizes, marker='^', linewidth=2, label='Tier 2 (Knowledge)', color='#4ec9b0')
    
    ax.set_title('Brain Tier Storage Sizes', fontsize=14, fontweight='bold')
    ax.set_ylabel('Size (KB)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    output_file = output_dir / "tier-storage-sizes.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"   💾 {output_file.name}")
    return output_file


def generate_html_dashboard(metrics_history: List[Dict], graphs_dir: Path, output_file: Path):
    """Generate HTML dashboard with embedded graphs."""
    latest = metrics_history[-1] if metrics_history else None
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX Brain Health Trends</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #1e1e1e;
            color: #d4d4d4;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            color: #4ec9b0;
            border-bottom: 2px solid #569cd6;
            padding-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: #2d2d30;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #569cd6;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #4ec9b0;
        }}
        .stat-label {{
            color: #9cdcfe;
            font-size: 14px;
            text-transform: uppercase;
        }}
        .graph {{
            background: #2d2d30;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .graph img {{
            width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #3e3e42;
            color: #808080;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 CORTEX Brain Health Trends</h1>
        <p>Historical metrics tracking CORTEX intelligence growth and health</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Overall Health</div>
                <div class="stat-value">{latest['health']['overall_status'] if latest else 'N/A'}</div>
                <small>{latest['health']['health_score'] if latest else 0}% score</small>
            </div>
            <div class="stat-card">
                <div class="stat-label">Knowledge Patterns</div>
                <div class="stat-value">{latest['tier2']['patterns_count'] if latest else 0}</div>
                <small>Avg confidence: {latest['tier2']['avg_confidence'] if latest else 0}</small>
            </div>
            <div class="stat-card">
                <div class="stat-label">Conversations Tracked</div>
                <div class="stat-value">{latest['tier1']['conversations_jsonl'] if latest else 0}</div>
                <small>{latest['tier1']['utilization_percent'] if latest else 0}% utilization</small>
            </div>
            <div class="stat-card">
                <div class="stat-label">Data Points</div>
                <div class="stat-value">{len(metrics_history)}</div>
                <small>Historical snapshots</small>
            </div>
        </div>
        
        <div class="graph">
            <h2>📈 Brain Health Score</h2>
            <img src="brain-health-score.png" alt="Brain Health Score">
        </div>
        
        <div class="graph">
            <h2>🧠 Knowledge Graph Growth</h2>
            <img src="knowledge-growth.png" alt="Knowledge Growth">
        </div>
        
        <div class="graph">
            <h2>💬 Conversation Memory Utilization</h2>
            <img src="conversation-utilization.png" alt="Conversation Utilization">
        </div>
        
        <div class="graph">
            <h2>💾 Tier Storage Sizes</h2>
            <img src="tier-storage-sizes.png" alt="Storage Sizes">
        </div>
        
        <div class="footer">
            <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>© 2024-2025 Asif Hussain | CORTEX Brain Health Monitoring</p>
        </div>
    </div>
</body>
</html>"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"   🌐 {output_file.name}")
    return output_file


def main():
    """Main entry point."""
    print("=" * 80)
    print("CORTEX Brain Health Trend Visualization")
    print("=" * 80)
    print()
    
    try:
        # Check for matplotlib
        try:
            import matplotlib
        except ImportError:
            print("❌ Error: matplotlib not installed")
            print("   Install with: pip install matplotlib")
            return 1
        
        # Load historical data
        brain_path = project_root / "cortex-brain"
        metrics_dir = brain_path / "metrics-history"
        
        if not metrics_dir.exists():
            print(f"❌ Error: No metrics history found at {metrics_dir}")
            print("   Run collect_daily_metrics.py first to generate data")
            return 1
        
        print("📊 Loading historical metrics...")
        metrics_history = load_metrics_history(metrics_dir)
        
        if not metrics_history:
            print("❌ Error: No metrics data files found")
            print("   Run collect_daily_metrics.py first to generate data")
            return 1
        
        print(f"✅ Loaded {len(metrics_history)} data points")
        print()
        
        # Create output directory
        graphs_dir = brain_path / "graphs"
        graphs_dir.mkdir(exist_ok=True)
        
        # Generate all visualizations
        print("📈 Generating visualizations...")
        plot_brain_health_score(metrics_history, graphs_dir)
        plot_knowledge_growth(metrics_history, graphs_dir)
        plot_conversation_utilization(metrics_history, graphs_dir)
        plot_tier_sizes(metrics_history, graphs_dir)
        
        # Generate HTML dashboard
        print()
        print("🌐 Generating HTML dashboard...")
        html_file = brain_path / "health-trends.html"
        generate_html_dashboard(metrics_history, graphs_dir, html_file)
        
        print()
        print("✅ Visualization complete!")
        print()
        print(f"📂 Output:")
        print(f"   Graphs: {graphs_dir.relative_to(project_root)}/")
        print(f"   Dashboard: {html_file.relative_to(project_root)}")
        print()
        print("💡 Open health-trends.html in your browser to view the dashboard!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
