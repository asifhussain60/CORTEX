"""
Test KSESSIONS onboarding with enhanced LLM synthesis layer.

AC_START: AC-KSESSIONS-ONBOARD-001
"""

import json
from pathlib import Path
from cortex.orchestrators.support.unified_llm_synthesis_layer import (
    UnifiedLLMSynthesisLayer,
    LLMProvider
)

def test_ksessions_onboarding():
    """Test KSESSIONS onboarding with enhanced use case extraction."""
    
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📋 KSESSIONS Repository Onboarding Test")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    # Initialize synthesis layer
    synthesis_layer = UnifiedLLMSynthesisLayer(provider=LLMProvider.CLAUDE_SONNET)
    
    # Simulated synthesis input (would come from LENS + Git + Config analysis)
    synthesis_input = {
        "repository_name": "KSESSIONS",
        "repository_path": "D:\\PROJECTS\\KSESSIONS",
        "lens_analysis": {
            "patterns": [
                {"type": "api_endpoint", "path": "/api/session/create"},
                {"type": "api_endpoint", "path": "/api/session/refresh"},
                {"type": "service", "name": "SessionService"},
                {"type": "data_model", "name": "Session"},
            ],
            "api_contracts": [
                {"endpoint": "/api/session/create", "method": "POST"},
                {"endpoint": "/api/session/refresh", "method": "POST"},
            ],
        },
        "git_history": {
            "first_commit": "2023-06-15",
            "last_commit": "2026-02-08",
            "age_days": 968,
            "total_commits": 2453,
            "contributors": 8,
            "is_active": True,
            "recent_changes": [
                "feat: Add OAuth2 integration",
                "fix: Session timeout issue",
                "perf: Optimize Redis caching"
            ]
        },
        "config_analysis": {
            "tech_stack": {
                "languages": ["Python", "TypeScript", "C#"],
                "frameworks": ["Flask", "NestJS", "ASP.NET Core"],
            },
            "databases": ["PostgreSQL", "Redis"],
            "message_brokers": ["RabbitMQ"],
            "caching": ["Redis"],
            "monitoring": ["Prometheus", "Grafana"],
            "ci_cd_enabled": True,
            "containerized": True,
            "infrastructure_as_code": True,
        },
        "documentation": {
            "readme": "KSESSIONS is a multi-tenant session management platform..."
        }
    }
    
    # Run synthesis
    print("🔄 Running LLM synthesis...")
    result = synthesis_layer.synthesize(synthesis_input)
    
    # Display results
    print(f"\n✅ Synthesis Complete: {result.repository_name}")
    print(f"📅 Timestamp: {result.synthesis_timestamp}")
    
    print(f"\n📊 Executive Summary:")
    print(f"   Overview: {result.executive_summary.overview[:100]}...")
    print(f"   Purpose: {result.executive_summary.purpose[:80]}...")
    print(f"   Maturity: {result.executive_summary.maturity_level}")
    print(f"   Age: {result.executive_summary.repository_age}")
    print(f"   Capabilities: {len(result.executive_summary.key_capabilities)}")
    print(f"   Functionalities: {len(result.executive_summary.core_functionalities)}")
    
    print(f"\n🎯 Use Cases Extracted: {len(result.use_cases)}")
    for i, uc in enumerate(result.use_cases[:3], 1):
        print(f"\n   {i}. {uc.title} ({uc.category})")
        print(f"      Actors: {', '.join(uc.actors)}")
        print(f"      Confidence: {uc.confidence_score:.2f}")
        print(f"      Value: {uc.business_value[:60]}...")
    
    # Save to JSON
    output_file = Path("d:/PROJECTS/CORTEX/cortex_brain/onboarded_repos/ksessions_enhanced.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(result.to_dict(), f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"\n✅ KSESSIONS onboarding test complete!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    return result

if __name__ == "__main__":
    test_ksessions_onboarding()

# AC_COMPLETE: AC-KSESSIONS-ONBOARD-001 ✅
