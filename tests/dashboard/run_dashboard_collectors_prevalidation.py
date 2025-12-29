#!/usr/bin/env python3
"""
Execute Dashboard Collectors for V5.WebServices.PrevalidationWS

Runs the parallel dashboard collectors to generate dashboard data for the 
PrevalidationWS repository.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add CORTEX to path
cortex_root = Path(__file__).parent
sys.path.insert(0, str(cortex_root))
sys.path.insert(0, str(cortex_root / "src"))

def main():
    """Execute dashboard collectors for PrevalidationWS."""
    
    # Configuration
    target_repo = Path(r"C:\PROJECTS\V5.WebServices.PrevalidationWS")
    project_name = "V5-WebServices-PrevalidationWS"
    
    print("=" * 70)
    print("CORTEX Dashboard Data Collection")
    print("=" * 70)
    print(f"\nTarget Repository: {target_repo}")
    print(f"Project Name: {project_name}")
    
    if not target_repo.exists():
        print(f"\nERROR: Repository not found at {target_repo}")
        return 1
    
    print(f"Repository verified: OK")
    print("\nStarting parallel data collection...\n")
    
    try:
        # Import parallel collector orchestrator
        from dashboard.data.parallel_collector import ParallelCollectorOrchestrator
        
        # Output directory
        repo_slug = project_name.lower().replace(" ", "-")
        output_dir = cortex_root / "cortex-brain" / "dashboards" / repo_slug
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Output directory: {output_dir}")
        print("\n" + "-" * 70)
        
        # Execute collectors in parallel (6 threads)
        start_time = time.time()
        parallel_orchestrator = ParallelCollectorOrchestrator(target_repo)
        collected_data, collection_time = parallel_orchestrator.collect_all_parallel()
        
        print(f"\nAll collectors completed in {collection_time:.2f} seconds")
        print("\n" + "-" * 70)
        print("Collection Results:")
        print("-" * 70)
        
        # Display collection summary
        for filename, data in collected_data.items():
            size_kb = len(json.dumps(data)) / 1024
            print(f"  [OK] {filename:<30} {size_kb:>8.2f} KB")
        
        # Write collected data to files
        print("\n" + "-" * 70)
        print("Writing dashboard data files...")
        print("-" * 70)
        
        for filename, data in collected_data.items():
            try:
                file_path = output_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"  [OK] {filename}")
            except Exception as e:
                print(f"  [ERROR] {filename}: {e}")
        
        # Generate health-data.json (overview)
        print("\n  Generating health-data.json...")
        health_data = _calculate_health_metrics(collected_data)
        health_file = output_dir / "health-data.json"
        with open(health_file, 'w', encoding='utf-8') as f:
            json.dump(health_data, f, indent=2, ensure_ascii=False)
        print(f"  [OK] health-data.json")
        
        # Generate metadata.json
        metadata = {
            "app_name": project_name,
            "app_type": "external",
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "last_scan": datetime.now().isoformat(),
            "scan_duration_seconds": round(time.time() - start_time, 2),
            "collection_time_seconds": round(collection_time, 2),
            "parallel_execution": True,
            "collectors": 6
        }
        metadata_file = output_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"  [OK] metadata.json")
        
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 70)
        print("DASHBOARD DATA COLLECTION COMPLETE")
        print("=" * 70)
        print(f"\nTotal Time: {elapsed:.2f} seconds")
        print(f"Collection Time: {collection_time:.2f} seconds")
        print(f"Output Directory: {output_dir}")
        print(f"\nDashboard Files Generated:")
        for filename in sorted([f.name for f in output_dir.glob("*.json")]):
            print(f"  • {filename}")
        
        dashboard_url = f"cortex-brain/dashboards/ui/index.html?source={repo_slug}"
        print(f"\nDashboard URL: {dashboard_url}")
        
        print("\nNext Steps:")
        print("  1. Open the dashboard in a browser")
        print("  2. Review collected metrics and analysis")
        print("  3. Use data for project insights and planning")
        
        return 0
        
    except ImportError as e:
        print(f"\nERROR: Failed to import dashboard collectors: {e}")
        print("\nMake sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        return 1
    except KeyboardInterrupt:
        print("\n\nCollection interrupted by user")
        return 130
    except Exception as e:
        print(f"\nERROR: Collection failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def _calculate_health_metrics(collected_data: dict) -> dict:
    """Calculate overall health metrics from collected data."""
    
    # Extract metrics from collected data
    tech_stack = collected_data.get("tech-stack.json", {})
    security = collected_data.get("security.json", {})
    architecture = collected_data.get("architecture.json", {})
    code_org = collected_data.get("code-organization.json", {})
    team_metrics = collected_data.get("team-metrics.json", {})
    
    # Calculate component scores (0-100)
    scores = {
        "security": security.get("overall_score", 0),
        "architecture": _calculate_architecture_score(architecture),
        "code_quality": _calculate_code_quality_score(code_org),
        "team_health": _calculate_team_health_score(team_metrics),
        "tech_stack": _calculate_tech_stack_score(tech_stack)
    }
    
    # Overall health score (weighted average)
    weights = {"security": 0.25, "architecture": 0.20, "code_quality": 0.25, 
               "team_health": 0.15, "tech_stack": 0.15}
    overall_score = sum(scores[k] * weights[k] for k in scores)
    
    # Get file/line counts from tech stack if code org is empty
    total_files = code_org.get("total_files", 0)
    total_lines = code_org.get("total_lines", 0)
    if total_files == 0 and tech_stack.get("backend"):
        for tech in tech_stack.get("backend", []):
            if "metadata" in tech and "file_count" in tech["metadata"]:
                total_files += tech["metadata"]["file_count"]
            if "metadata" in tech and "lines_of_code" in tech["metadata"]:
                total_lines += tech["metadata"]["lines_of_code"]
    
    return {
        "overall_health_score": round(overall_score),
        "status": _get_health_status(overall_score).lower(),
        "last_scan": datetime.now().isoformat(),
        "summary": {
            "total_files": total_files,
            "total_loc": total_lines,
            "test_coverage": 0,
            "critical_issues": 0,
            "warnings": 0,
            "maintainability_index": round(overall_score)
        },
        "metrics": {
            "code_quality_score": round(scores["code_quality"]),
            "security_score": round(scores["security"]),
            "test_score": 0,
            "documentation_score": 50
        },
        "component_scores": scores,
        "health_status": _get_health_status(overall_score),
        "last_updated": datetime.now().isoformat(),
        "trends": {
            "health_trend": "stable",
            "velocity_trend": "stable",
            "quality_trend": "stable"
        }
    }


def _calculate_architecture_score(architecture: dict) -> float:
    """Calculate architecture health score."""
    components = architecture.get("components", [])
    layers = architecture.get("layers", 0)
    patterns = architecture.get("patterns", [])
    
    if not components:
        return 50.0  # Neutral score if no data
    
    score = 70.0  # Base score
    score += min(20, len(components) * 2)  # Bonus for components (max 20)
    score += min(10, layers * 2)  # Bonus for layering (max 10)
    
    return min(100.0, score)


def _calculate_code_quality_score(code_org: dict) -> float:
    """Calculate code quality score."""
    total_files = code_org.get("total_files", 0)
    hotspots = code_org.get("hotspots", [])
    
    if total_files == 0:
        return 50.0  # Neutral score if no data
    
    score = 85.0  # Base score
    
    # Penalize for high number of hotspots
    if total_files > 0:
        hotspot_ratio = len(hotspots) / total_files
        penalty = hotspot_ratio * 30  # Up to 30 point penalty
        score -= penalty
    
    return max(0.0, min(100.0, score))


def _calculate_team_health_score(team_metrics: dict) -> float:
    """Calculate team health score."""
    total_commits = team_metrics.get("total_commits", 0)
    contributor_count = team_metrics.get("contributor_count", 0)
    
    if total_commits == 0:
        return 50.0  # Neutral score if no data
    
    score = 60.0  # Base score
    
    # Bonus for multiple contributors
    score += min(20, contributor_count * 5)
    
    # Bonus for active development
    score += min(20, total_commits / 100)
    
    return min(100.0, score)


def _calculate_tech_stack_score(tech_stack: dict) -> float:
    """Calculate tech stack score."""
    languages = tech_stack.get("total_languages", 0)
    frameworks = tech_stack.get("total_frameworks", 0)
    
    score = 70.0  # Base score
    
    # Bonus for diverse tech stack (but not too diverse)
    if 1 <= languages <= 3:
        score += 15
    elif languages > 3:
        score += 5  # Slight bonus for polyglot
    
    score += min(15, frameworks * 3)  # Bonus for frameworks
    
    return min(100.0, score)


def _get_health_status(score: float) -> str:
    """Get health status label from score."""
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Fair"
    else:
        return "Needs Attention"


if __name__ == "__main__":
    sys.exit(main())
