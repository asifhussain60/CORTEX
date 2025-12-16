"""
Dashboard Data Collection Script with Progress Feedback

Collects dashboard data for multiple repositories with real-time progress updates.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrators.dashboard_collector import DashboardDataCollector


def print_progress(message: str, prefix: str = "📊"):
    """Print progress message with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {prefix} {message}")


def collect_with_progress(repo_path: str, repo_name: str) -> bool:
    """
    Collect dashboard data with progress feedback.
    
    Args:
        repo_path: Path to repository
        repo_name: Display name for repository
    
    Returns:
        True if successful, False otherwise
    """
    print("\n" + "="*80)
    print(f"🚀 Starting data collection for: {repo_name}")
    print(f"📁 Path: {repo_path}")
    print("="*80 + "\n")
    
    start_time = time.time()
    
    try:
        # Initialize collector
        print_progress(f"Initializing collector for {repo_name}...", "🔧")
        collector = DashboardDataCollector(Path(repo_path))
        print_progress(f"Output directory: {collector.output_dir}", "📂")
        
        # Collect data
        print_progress("Starting parallel data collection...", "⚡")
        print_progress("This may take 2-5 minutes depending on repository size...", "⏳")
        
        results = collector.collect_all()
        
        collection_time = time.time() - start_time
        print_progress(f"Data collection completed in {collection_time:.1f} seconds", "✅")
        
        # Save results
        print_progress("Saving results to disk...", "💾")
        success = collector.save_results(results)
        
        if success:
            total_time = time.time() - start_time
            print("\n" + "="*80)
            print(f"✅ SUCCESS: {repo_name} data collection complete!")
            print(f"⏱️  Total time: {total_time:.1f} seconds")
            print(f"📂 Output: {collector.output_dir}")
            print("="*80 + "\n")
            return True
        else:
            print(f"\n❌ FAILED: Could not save results for {repo_name}\n")
            return False
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ ERROR after {elapsed:.1f} seconds: {str(e)}\n")
        return False


def main():
    """Main entry point - collect data for all target repositories."""
    
    print("\n" + "="*80)
    print("🧠 CORTEX Dashboard Data Collection Orchestrator")
    print("="*80 + "\n")
    
    # Define repositories to process
    repositories = [
        {
            "path": r"C:\PROJECTS\CORTEX\cortex-brain\dashboards\data\repos\v5-webservices-prevalidationws",
            "name": "v5-webservices-prevalidationws",
            "skip": True,  # Already has data
            "reason": "Data already exists (moved from old location)"
        },
        {
            "path": r"C:\PROJECTS\TCBULK",
            "name": "TCBULK",
            "skip": False
        },
        {
            "path": r"C:\PROJECTS\V5.ColdFusion",
            "name": "V5.ColdFusion",
            "skip": False
        }
    ]
    
    overall_start = time.time()
    results = {"success": [], "failed": [], "skipped": []}
    
    for i, repo in enumerate(repositories, 1):
        print(f"\n{'='*80}")
        print(f"Repository {i}/{len(repositories)}: {repo['name']}")
        print(f"{'='*80}")
        
        if repo.get("skip", False):
            reason = repo.get("reason", "Skipped by configuration")
            print(f"⏭️  SKIPPING: {reason}\n")
            results["skipped"].append(repo["name"])
            continue
        
        # Check if path exists
        if not Path(repo["path"]).exists():
            print(f"❌ ERROR: Repository path does not exist: {repo['path']}\n")
            results["failed"].append(repo["name"])
            continue
        
        # Collect data with progress
        success = collect_with_progress(repo["path"], repo["name"])
        
        if success:
            results["success"].append(repo["name"])
        else:
            results["failed"].append(repo["name"])
        
        # Brief pause between repositories
        if i < len(repositories):
            print_progress("Preparing for next repository...", "🔄")
            time.sleep(2)
    
    # Final summary
    total_time = time.time() - overall_start
    
    print("\n" + "="*80)
    print("📊 COLLECTION SUMMARY")
    print("="*80)
    print(f"\n✅ Successful: {len(results['success'])}")
    for name in results["success"]:
        print(f"   • {name}")
    
    if results["skipped"]:
        print(f"\n⏭️  Skipped: {len(results['skipped'])}")
        for name in results["skipped"]:
            print(f"   • {name}")
    
    if results["failed"]:
        print(f"\n❌ Failed: {len(results['failed'])}")
        for name in results["failed"]:
            print(f"   • {name}")
    
    print(f"\n⏱️  Total execution time: {total_time:.1f} seconds")
    print(f"\n🎯 Next steps:")
    print(f"   1. Launch dashboard: python -m src.orchestrators.dashboard_launcher")
    print(f"   2. Select repository from dropdown to view collected data")
    print(f"   3. Explore tech stack, architecture, and security insights")
    print("\n" + "="*80 + "\n")
    
    return 0 if not results["failed"] else 1


if __name__ == '__main__':
    sys.exit(main())
