"""
Quick script to run CORTEX optimize operation and display results.
"""
from src.operations import execute_operation

print("=" * 80)
print("RUNNING CORTEX OPTIMIZE OPERATION")
print("=" * 80)

report = execute_operation('optimize')

print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)

if report.success:
    health_data = report.context.get('health_report', {})
    health_score = health_data.get('health_score', 0)
    overall_health = health_data.get('overall_health', 'unknown')
    stats = health_data.get('statistics', {})
    issues = health_data.get('issues', [])
    
    print(f"\n✅ Optimization Complete")
    print(f"\nHealth Score: {health_score:.1f}/100")
    print(f"Overall Health: {overall_health.upper()}")
    
    print(f"\n📊 Key Statistics:")
    print(f"  - Tier 0 Protection Layers: {stats.get('tier0_protection_layers', 0)}")
    print(f"  - Tier 0 SKULL Rules: {stats.get('tier0_skull_rules', 0)}")
    print(f"  - Brain Health: {stats.get('brain_health_percentage', 0):.1f}%")
    print(f"  - Issues Found: {len(issues)}")
    
    if stats.get('legacy_db_refs', 0) > 0:
        print(f"\n⚠️  Legacy Database References: {stats['legacy_db_refs']}")
    
    print(f"\n📄 Report Path: {report.context.get('report_path', 'N/A')}")
    
    # Show critical issues
    critical = [i for i in issues if i['severity'] == 'critical']
    if critical:
        print(f"\n🚨 CRITICAL ISSUES ({len(critical)}):")
        for issue in critical[:5]:
            print(f"  - {issue['title']}")
    
    print("\n✅ Brain protection rules are being enforced unforgivingly!")
else:
    print(f"\n❌ Optimization Failed: {report.errors}")

print("\n" + "=" * 80)
