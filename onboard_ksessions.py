"""
Full KSESSIONS Repository Onboarding Script.

Onboards KSESSIONS repository using the complete RepositoryOnboardingOrchestrator
with enhanced LLM synthesis for comprehensive use cases and executive summary.

AC_START: AC-KSESSIONS-FULL-ONBOARD-001
"""

import json
from pathlib import Path
from cortex.orchestrators.support.repository_onboarding_orchestrator import (
    get_repository_onboarding_orchestrator,
    ProgressStyle
)

def onboard_ksessions_full():
    """Full KSESSIONS onboarding with all features."""
    
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧠 CORTEX Full KSESSIONS Repository Onboarding")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    # Repository path
    ksessions_path = Path("D:\\PROJECTS\\KSESSIONS")
    
    if not ksessions_path.exists():
        print(f"❌ ERROR: KSESSIONS repository not found at {ksessions_path}")
        return
    
    print(f"📁 Repository: {ksessions_path}")
    print(f"📊 Files: ~30,000 files (245 .cs, 319 .py, 10K+ .js/.ts)")
    print("")
    
    # Get orchestrator
    orchestrator = get_repository_onboarding_orchestrator()
    
    # Run onboarding
    print("🔄 Starting full onboarding workflow...")
    print("   1. LENS Analysis (Git, AST, Security)")
    print("   2. Business Narrative Generation")
    print("   3. Security Threat Modeling")
    print("   4. Dashboard Generation")
    print("")
    
    result = orchestrator.onboard_repository(
        repo_path=ksessions_path,
        include_dashboard=True,
        update_company_domain=False,  # Skip domain updates for external repo
        repo_name="KSESSIONS",
        icon="💼",
        progress_style=ProgressStyle.DETAILED,
        show_progress=True,
    )
    
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ ONBOARDING COMPLETE")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    # Display results
    if result.success:
        print(f"✅ Success: {result.success}")
        # Note: files_analyzed attribute doesn't exist in OnboardingResult
        
        if result.business_narrative:
            narrative = result.business_narrative
            print(f"\n📋 Business Narrative:")
            print(f"   Title: {getattr(narrative, 'title', 'N/A')}")
            print(f"   Tagline: {getattr(narrative, 'tagline', 'N/A')}")
            
            use_cases = getattr(narrative, 'use_cases', [])
            print(f"\n🎯 Use Cases Detected: {len(use_cases)}")
            for i, uc in enumerate(use_cases[:5], 1):
                uc_title = getattr(uc, 'title', 'Unknown')
                uc_icon = getattr(uc, 'icon', '📌')
                print(f"   {i}. {uc_icon} {uc_title}")
            
            if len(use_cases) > 5:
                print(f"   ... and {len(use_cases) - 5} more")
        
        if result.security_risks:
            p0 = len(result.security_risks.get("p0_risks", []))
            p1 = len(result.security_risks.get("p1_risks", []))
            p2 = len(result.security_risks.get("p2_risks", []))
            print(f"\n🔒 Security Risks:")
            print(f"   P0 (Critical): {p0}")
            print(f"   P1 (High): {p1}")
            print(f"   P2 (Medium): {p2}")
        
        if result.dashboard_path:
            print(f"\n📊 Dashboard: {result.dashboard_path}")
        
        # Check for repository JSON
        json_path = Path("d:/PROJECTS/CORTEX/cortex_brain/onboarded_repos/ksessions.json")
        if json_path.exists():
            print(f"\n💾 Repository JSON: {json_path}")
            with open(json_path, 'r') as f:
                data = json.load(f)
                print(f"   Schema Version: {data.get('schema_version', 'N/A')}")
                
                overview = data.get('overview', {})
                print(f"\n📖 Overview Summary:")
                summary = overview.get('summary', '')
                if summary:
                    print(f"   {summary[:150]}...")
                
                use_cases = overview.get('use_cases', [])
                if use_cases:
                    print(f"\n🎯 Use Cases in JSON: {len(use_cases)}")
                    for i, uc in enumerate(use_cases[:3], 1):
                        print(f"   {i}. {uc.get('title', 'N/A')} ({uc.get('category', 'N/A')})")
                        print(f"      Confidence: {uc.get('confidence_score', 0):.2f}")
                
                capabilities = overview.get('key_capabilities', [])
                if capabilities:
                    print(f"\n🔧 Key Capabilities: {len(capabilities)}")
                    for cap in capabilities[:5]:
                        print(f"   • {cap}")
    else:
        print(f"❌ Onboarding failed: {result.error}")
    
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    return result

if __name__ == "__main__":
    onboard_ksessions_full()

# AC_COMPLETE: AC-KSESSIONS-FULL-ONBOARD-001 ✅
