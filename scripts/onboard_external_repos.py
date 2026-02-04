"""
Repository Onboarding Script
Onboards external repositories using RepositoryOnboardingOrchestrator.

Enhanced with progress feedback and time estimates.

Author: Asif Hussain
Date: 2026-02-03
AC-ID: AC-ONBOARD-EXTERNAL-001
"""

import sys
from pathlib import Path
from datetime import datetime

# Add CORTEX to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cortex.orchestrators.support.repository_onboarding_orchestrator import (
    get_repository_onboarding_orchestrator
)
from cortex.common.progress_reporter import ProgressStyle


def onboard_repository(repo_path: str, show_progress: bool = True) -> None:
    """
    Onboard a single repository with progress feedback.
    
    Args:
        repo_path: Path to repository
        show_progress: Whether to show progress feedback
    """
    print(f"\n{'='*80}")
    print(f"🚀 ONBOARDING: {repo_path}")
    print(f"{'='*80}\n")
    
    try:
        orchestrator = get_repository_onboarding_orchestrator()
        result = orchestrator.onboard_repository(
            repo_path=Path(repo_path),
            include_dashboard=False,  # Disabled due to missing dashboard_asset_manager
            update_company_domain=True,
            show_progress=show_progress,
            progress_style=ProgressStyle.DETAILED,
        )
        
        if result.success:
            print(f"\n✅ SUCCESS: {result.repo_path}")
            print(f"   Timestamp: {result.timestamp}")
            
            # Security risks
            p0_count = len(result.security_risks.get("p0_risks", []))
            p1_count = len(result.security_risks.get("p1_risks", []))
            p2_count = len(result.security_risks.get("p2_risks", []))
            
            print(f"\n📊 Security Analysis:")
            print(f"   P0 (Critical): {p0_count}")
            print(f"   P1 (High):     {p1_count}")
            print(f"   P2 (Medium):   {p2_count}")
            
            # Recommendations
            rec_count = len(result.recommendations)
            print(f"\n💡 Recommendations: {rec_count}")
            
            if result.dashboard_path:
                print(f"\n📈 Dashboard: {result.dashboard_path}")
            
            print(f"\n{'─'*80}\n")
            
        else:
            print(f"❌ FAILED: {result.error}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main onboarding function."""
    repos = [
        r"D:\PROJECTS\ALIST",
        r"D:\PROJECTS\KASHKOLE",
        r"D:\PROJECTS\KSESSIONS",
        r"D:\PROJECTS\NOOR CANVAS",
    ]
    
    print("\n" + "="*80)
    print("🧠 CORTEX Repository Onboarding")
    print("="*80)
    print(f"Author: Asif Hussain")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Repositories: {len(repos)}")
    
    # Estimate total time
    estimated_per_repo = 80  # ~80 seconds per repo based on default estimates
    total_estimated = estimated_per_repo * len([r for r in repos if Path(r).exists()])
    total_mins = total_estimated // 60
    total_secs = total_estimated % 60
    print(f"Estimated Time: ~{total_mins}m {total_secs}s total")
    print("="*80)
    
    for idx, repo in enumerate(repos, 1):
        if Path(repo).exists():
            print(f"\n[Repository {idx}/{len(repos)}]")
            onboard_repository(repo, show_progress=True)
        else:
            print(f"\n⚠️  SKIPPING: {repo} (does not exist)")
    
    print("\n" + "="*80)
    print("✅ ONBOARDING COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
