"""
Repository Onboarding Script
Onboards external repositories using RepositoryOnboardingOrchestrator.

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


def onboard_repository(repo_path: str) -> None:
    """
    Onboard a single repository.
    
    Args:
        repo_path: Path to repository
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
        )
        
        if result.success:
            print(f"✅ SUCCESS: {result.repo_path}")
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
    print("="*80)
    
    for repo in repos:
        if Path(repo).exists():
            onboard_repository(repo)
        else:
            print(f"\n⚠️  SKIPPING: {repo} (does not exist)")
    
    print("\n" + "="*80)
    print("✅ ONBOARDING COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
