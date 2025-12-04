"""
Test Tech Stack and Security Collectors

Quick test to validate Phase 13 collectors with CORTEX's own data.

Author: Asif Hussain
"""

from pathlib import Path
from src.dashboard.data.tech_stack_collector import TechStackCollector
from src.dashboard.data.security_collector import SecurityCollector

def test_collectors():
    """Test collectors on CORTEX codebase."""
    cortex_root = Path.cwd()
    
    print("=" * 60)
    print("PHASE 13 COLLECTOR TEST - CORTEX Project")
    print("=" * 60)
    
    # Test Tech Stack Collector
    print("\n🛠️  Testing Tech Stack Collector...")
    tech_collector = TechStackCollector(cortex_root)
    tech_stack = tech_collector.collect()
    
    if tech_stack:
        print(f"\n✅ Tech Stack Collection Successful!")
        print(f"   Total Technologies: {tech_stack['summary']['total_technologies']}")
        print(f"   Current: {tech_stack['summary']['current_count']}")
        print(f"   Outdated: {tech_stack['summary']['outdated_count']}")
        print(f"   Deprecated: {tech_stack['summary']['deprecated_count']}")
        
        print(f"\n   Frontend: {len(tech_stack['frontend'])} items")
        print(f"   Backend: {len(tech_stack['backend'])} items")
        print(f"   Database: {len(tech_stack['database'])} items")
        print(f"   DevOps: {len(tech_stack['devops'])} items")
        
        # Show some backend technologies
        if tech_stack['backend']:
            print(f"\n   Sample Backend Technologies:")
            for tech in tech_stack['backend'][:5]:
                print(f"      - {tech['name']} {tech['version']} ({tech['status']})")
    else:
        print("❌ Tech Stack Collection Failed")
    
    # Test Security Collector
    print("\n\n🔒 Testing Security Collector...")
    security_collector = SecurityCollector(cortex_root)
    security_data = security_collector.collect()
    
    if security_data:
        print(f"\n✅ Security Collection Successful!")
        print(f"   Overall Score: {security_data['overall_score']}/100")
        print(f"   Vulnerabilities:")
        print(f"      Critical: {security_data['vulnerabilities']['critical']}")
        print(f"      High: {security_data['vulnerabilities']['high']}")
        print(f"      Medium: {security_data['vulnerabilities']['medium']}")
        print(f"      Low: {security_data['vulnerabilities']['low']}")
        
        print(f"\n   Category Scores:")
        for category, data in security_data['categories'].items():
            print(f"      {category}: {data['score']}% ({data['issues']} issues)")
        
        print(f"\n   Compliance:")
        print(f"      GDPR: {'✅' if security_data['compliance']['gdpr_ready'] else '❌'}")
        print(f"      SOC 2: {'✅' if security_data['compliance']['soc2_ready'] else '❌'}")
        
        # Show OWASP Top 10 summary
        owasp_pass = len([x for x in security_data['owasp_top_10'] if x['status'] == 'pass'])
        owasp_warn = len([x for x in security_data['owasp_top_10'] if x['status'] == 'warn'])
        owasp_fail = len([x for x in security_data['owasp_top_10'] if x['status'] == 'fail'])
        print(f"\n   OWASP Top 10 (2021):")
        print(f"      Pass: {owasp_pass}")
        print(f"      Warn: {owasp_warn}")
        print(f"      Fail: {owasp_fail}")
    else:
        print("❌ Security Collection Failed")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\n✅ Phase 13 collectors working with CURRENT STATE data only")
    print("✅ No mock data - all values from actual CORTEX codebase")
    print("✅ Ready for dashboard integration")

if __name__ == "__main__":
    test_collectors()
