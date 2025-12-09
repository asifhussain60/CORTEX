"""
Phase 1 Task 1.3 - Business Domain Inference Analysis
Analyze all 4 target repositories
"""
from pathlib import Path
from src.intelligence.business_domain_inference import analyze_repository
import json

repos = {
    'TCBULK': Path('C:/PROJECTS/TCBULK'),
    'V5.ColdFusion': Path('C:/PROJECTS/V5.ColdFusion'),
    'V5.WebServices.PrevalidationWS': Path('C:/PROJECTS/V5.WebServices.PrevalidationWS'),
    'V5.CommuterOpsWeb': Path('C:/PROJECTS/V5.CommuterOpsWeb')
}

all_results = {}

for repo_name, repo_path in repos.items():
    if repo_path.exists():
        print(f"\n{'='*80}")
        print(f"Analyzing: {repo_name}")
        print(f"Path: {repo_path}")
        print('='*80)
        
        try:
            result = analyze_repository(repo_path)
            all_results[repo_name] = result
            
            print(f"\n📊 Statistics:")
            print(f"  Total domains: {result['statistics']['total_domains']}")
            print(f"  High confidence: {result['statistics']['high_confidence']}")
            print(f"  Medium confidence: {result['statistics']['medium_confidence']}")
            print(f"  Low confidence: {result['statistics']['low_confidence']}")
            
            print(f"\n📝 Summary:")
            print(f"  {result['summary']}")
            
            print(f"\n🎯 Top 10 Domains:")
            for i, d in enumerate(result['domains'][:10], 1):
                sources_str = ', '.join(d['sources'])
                print(f"  {i}. {d['name']} ({d['confidence']})")
                print(f"     Frequency: {d['frequency']} | Sources: {sources_str}")
                if d['capabilities']:
                    print(f"     Capability: {d['capabilities'][0]}")
        
        except Exception as e:
            print(f"❌ Error analyzing {repo_name}: {e}")
            all_results[repo_name] = {'error': str(e)}
    else:
        print(f"\n⚠️  Repository not found: {repo_name} at {repo_path}")
        all_results[repo_name] = {'error': 'Repository not found'}

# Save consolidated results
output_file = Path('cortex-brain/documents/analysis/business-domain-inference-results-4-repos.json')
output_file.parent.mkdir(parents=True, exist_ok=True)
with open(output_file, 'w') as f:
    json.dump(all_results, f, indent=2)

print(f"\n{'='*80}")
print(f"✅ Analysis complete!")
print(f"📄 Results saved to: {output_file}")
print('='*80)

# Summary statistics
total_domains = sum(r['statistics']['total_domains'] for r in all_results.values() if 'statistics' in r)
total_high = sum(r['statistics']['high_confidence'] for r in all_results.values() if 'statistics' in r)
total_medium = sum(r['statistics']['medium_confidence'] for r in all_results.values() if 'statistics' in r)

print(f"\n🎯 AGGREGATE STATISTICS:")
print(f"  Total domains across all repos: {total_domains}")
print(f"  High confidence domains: {total_high}")
print(f"  Medium confidence domains: {total_medium}")
print(f"  Repositories analyzed: {len([r for r in all_results.values() if 'statistics' in r])}/4")
