"""Quick test of business domain inference"""
from pathlib import Path
from src.intelligence.business_domain_inference import analyze_repository

# Test on CORTEX itself
tcbulk_path = Path('C:/PROJECTS/CORTEX/src')
if tcbulk_path.exists():
    print(f"Analyzing {tcbulk_path}...")
    result = analyze_repository(tcbulk_path)
    
    print(f"\nDomains found: {result['statistics']['total_domains']}")
    print(f"High confidence: {result['statistics']['high_confidence']}")
    print(f"Medium confidence: {result['statistics']['medium_confidence']}")
    print(f"\nSummary: {result['summary']}")
    
    print("\nTop 10 domains:")
    for d in result['domains'][:10]:
        print(f"  {d['name']}: {d['confidence']} confidence, {d['frequency']} occurrences")
        print(f"    Sources: {', '.join(d['sources'])}")
        print(f"    Capabilities: {d['capabilities'][0] if d['capabilities'] else 'N/A'}")
else:
    print(f"Repository not found: {tcbulk_path}")
