"""
CORTEX Daily Brain Health Metrics Collector

Collects brain health metrics from all tiers and saves to git-tracked YAML.
Run daily via cron/Task Scheduler or GitHub Actions to build historical data.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import yaml
import json
import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def get_brain_path() -> Path:
    """Get cortex-brain directory path."""
    return project_root / "cortex-brain"


def collect_tier0_metrics() -> Dict[str, Any]:
    """Collect Tier 0 (Instinct/Governance) metrics."""
    brain_path = get_brain_path()
    rules_file = brain_path / "brain-protection-rules.yaml"
    
    metrics = {
        "rules_file_size_kb": 0,
        "total_rules": 0,
        "critical_paths": 0,
        "tier0_instincts": 0
    }
    
    if rules_file.exists():
        metrics["rules_file_size_kb"] = round(rules_file.stat().st_size / 1024, 2)
        
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
                if rules:
                    metrics["critical_paths"] = len(rules.get("critical_paths", []))
                    metrics["tier0_instincts"] = len(rules.get("tier0_instincts", []))
        except Exception as e:
            print(f"Warning: Could not parse brain-protection-rules.yaml: {e}")
    
    return metrics


def collect_tier1_metrics() -> Dict[str, Any]:
    """Collect Tier 1 (Working Memory) metrics."""
    brain_path = get_brain_path()
    
    metrics = {
        "conversations_jsonl": 0,
        "conversations_db": 0,
        "jsonl_size_kb": 0,
        "db_size_kb": 0,
        "last_activity": None,
        "utilization_percent": 0
    }
    
    # JSONL file
    jsonl_file = brain_path / "conversation-history.jsonl"
    if jsonl_file.exists():
        metrics["jsonl_size_kb"] = round(jsonl_file.stat().st_size / 1024, 2)
        metrics["last_activity"] = datetime.fromtimestamp(
            jsonl_file.stat().st_mtime
        ).isoformat()
        
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                metrics["conversations_jsonl"] = sum(1 for line in f if line.strip())
        except Exception as e:
            print(f"Warning: Could not count JSONL lines: {e}")
    
    # SQLite database
    db_file = brain_path / "conversation-history.db"
    if db_file.exists():
        metrics["db_size_kb"] = round(db_file.stat().st_size / 1024, 2)
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversations")
            metrics["conversations_db"] = cursor.fetchone()[0]
            conn.close()
        except Exception as e:
            print(f"Warning: Could not query conversation DB: {e}")
    
    # Calculate utilization (20 is FIFO capacity)
    count = max(metrics["conversations_jsonl"], metrics["conversations_db"])
    metrics["utilization_percent"] = round((count / 20) * 100, 1) if count else 0
    
    return metrics


def collect_tier2_metrics() -> Dict[str, Any]:
    """Collect Tier 2 (Knowledge Graph) metrics."""
    brain_path = get_brain_path()
    kg_file = brain_path / "knowledge-graph.yaml"
    
    metrics = {
        "file_size_kb": 0,
        "patterns_count": 0,
        "avg_confidence": 0,
        "last_learning": None,
        "patterns_by_impact": {}
    }
    
    if kg_file.exists():
        metrics["file_size_kb"] = round(kg_file.stat().st_size / 1024, 2)
        metrics["last_learning"] = datetime.fromtimestamp(
            kg_file.stat().st_mtime
        ).isoformat()
        
        try:
            with open(kg_file, 'r', encoding='utf-8') as f:
                kg = yaml.safe_load(f)
                
                if kg and "validation_insights" in kg:
                    patterns = kg["validation_insights"]
                    metrics["patterns_count"] = len(patterns)
                    
                    # Calculate average confidence
                    confidences = [p.get("confidence", 0) for p in patterns.values()]
                    if confidences:
                        metrics["avg_confidence"] = round(sum(confidences) / len(confidences), 3)
                    
                    # Count by impact
                    impacts = {}
                    for pattern in patterns.values():
                        impact = pattern.get("impact", "unknown")
                        impacts[impact] = impacts.get(impact, 0) + 1
                    metrics["patterns_by_impact"] = impacts
                    
        except Exception as e:
            print(f"Warning: Could not parse knowledge-graph.yaml: {e}")
    
    return metrics


def collect_tier3_metrics() -> Dict[str, Any]:
    """Collect Tier 3 (Context Intelligence) metrics."""
    brain_path = get_brain_path()
    
    metrics = {
        "architecture_file_kb": 0,
        "module_definitions_kb": 0,
        "session_summaries": 0
    }
    
    # Architecture file
    arch_file = brain_path / "CORTEX-UNIFIED-ARCHITECTURE.yaml"
    if arch_file.exists():
        metrics["architecture_file_kb"] = round(arch_file.stat().st_size / 1024, 2)
    
    # Module definitions
    mod_file = brain_path / "module-definitions.yaml"
    if mod_file.exists():
        metrics["module_definitions_kb"] = round(mod_file.stat().st_size / 1024, 2)
    
    # Count session summaries
    try:
        session_files = list(brain_path.glob("SESSION-*.md"))
        metrics["session_summaries"] = len(session_files)
    except Exception as e:
        print(f"Warning: Could not count session files: {e}")
    
    return metrics


def calculate_health_score(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall brain health score."""
    health = {
        "overall_status": "Unknown",
        "tier0_health": "Unknown",
        "tier1_health": "Unknown",
        "tier2_health": "Unknown",
        "tier3_health": "Unknown",
        "health_score": 0
    }
    
    points = 0
    max_points = 0
    
    # Tier 0 health (governance rules exist and not too large)
    max_points += 25
    if metrics["tier0"]["rules_file_size_kb"] > 0:
        if metrics["tier0"]["rules_file_size_kb"] < 50:  # Under 50KB is good
            points += 25
            health["tier0_health"] = "Healthy"
        else:
            points += 15
            health["tier0_health"] = "Acceptable"
    else:
        health["tier0_health"] = "Missing"
    
    # Tier 1 health (conversation tracking active)
    max_points += 25
    utilization = metrics["tier1"]["utilization_percent"]
    if 50 <= utilization <= 95:  # Good utilization range
        points += 25
        health["tier1_health"] = "Optimal"
    elif utilization > 0:
        points += 15
        health["tier1_health"] = "Active"
    else:
        health["tier1_health"] = "Inactive"
    
    # Tier 2 health (knowledge accumulation)
    max_points += 25
    if metrics["tier2"]["patterns_count"] >= 10:
        points += 25
        health["tier2_health"] = "Learning"
    elif metrics["tier2"]["patterns_count"] > 0:
        points += 15
        health["tier2_health"] = "Growing"
    else:
        health["tier2_health"] = "Empty"
    
    # Tier 3 health (context tracking)
    max_points += 25
    if metrics["tier3"]["session_summaries"] > 0:
        points += 25
        health["tier3_health"] = "Active"
    else:
        health["tier3_health"] = "Inactive"
    
    # Calculate overall score
    health["health_score"] = round((points / max_points) * 100, 1) if max_points else 0
    
    if health["health_score"] >= 80:
        health["overall_status"] = "Excellent"
    elif health["health_score"] >= 60:
        health["overall_status"] = "Good"
    elif health["health_score"] >= 40:
        health["overall_status"] = "Fair"
    else:
        health["overall_status"] = "Needs Attention"
    
    return health


def collect_all_metrics() -> Dict[str, Any]:
    """Collect metrics from all brain tiers."""
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
        "tier0": collect_tier0_metrics(),
        "tier1": collect_tier1_metrics(),
        "tier2": collect_tier2_metrics(),
        "tier3": collect_tier3_metrics()
    }


def save_metrics(metrics: Dict[str, Any], output_dir: Path) -> Path:
    """Save metrics to dated YAML file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Add health assessment
    health = calculate_health_score(metrics)
    metrics["health"] = health
    
    # Save to dated file
    date_str = metrics["date"]
    output_file = output_dir / f"{date_str}.yaml"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(metrics, f, default_flow_style=False, sort_keys=False)
    
    return output_file


def main():
    """Main entry point."""
    print("=" * 80)
    print("CORTEX Daily Brain Health Metrics Collector")
    print("=" * 80)
    print()
    
    try:
        # Collect metrics
        print("📊 Collecting metrics from all brain tiers...")
        metrics = collect_all_metrics()
        
        # Display summary
        print(f"✅ Tier 0: {metrics['tier0']['tier0_instincts']} instinct rules")
        print(f"✅ Tier 1: {metrics['tier1']['conversations_jsonl']} conversations " +
              f"({metrics['tier1']['utilization_percent']}% utilization)")
        print(f"✅ Tier 2: {metrics['tier2']['patterns_count']} patterns " +
              f"(avg confidence: {metrics['tier2']['avg_confidence']})")
        print(f"✅ Tier 3: {metrics['tier3']['session_summaries']} session summaries")
        print()
        
        # Save metrics
        brain_path = get_brain_path()
        metrics_dir = brain_path / "metrics-history"
        output_file = save_metrics(metrics, metrics_dir)
        
        print(f"💾 Metrics saved: {output_file.relative_to(project_root)}")
        print()
        
        # Display health assessment
        health = metrics["health"]
        print("🏥 Brain Health Assessment:")
        print(f"   Overall: {health['overall_status']} ({health['health_score']}%)")
        print(f"   Tier 0: {health['tier0_health']}")
        print(f"   Tier 1: {health['tier1_health']}")
        print(f"   Tier 2: {health['tier2_health']}")
        print(f"   Tier 3: {health['tier3_health']}")
        print()
        
        print("✅ Collection complete!")
        print()
        print("💡 Next steps:")
        print("   • Commit metrics to git: git add cortex-brain/metrics-history/")
        print("   • View trends: python scripts/visualize_brain_health.py")
        print("   • Automate: Set up GitHub Actions workflow")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
