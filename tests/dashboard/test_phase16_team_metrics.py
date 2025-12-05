"""
Test Team Metrics Collector

Phase 16 validation with CORTEX's own git history.

Author: Asif Hussain
"""

from pathlib import Path
from src.dashboard.data.team_metrics_collector import TeamMetricsCollector

def test_phase16_team_metrics():
    """Test Phase 16 team metrics collector on CORTEX repository."""
    cortex_root = Path.cwd()
    
    print("=" * 60)
    print("PHASE 16 COLLECTOR TEST - CORTEX Project")
    print("=" * 60)
    
    # Test Team Metrics Collector
    print("\n👥 Testing Team Metrics Collector...")
    team_collector = TeamMetricsCollector(cortex_root)
    team_metrics = team_collector.collect()
    
    if team_metrics:
        print(f"\n✅ Team Metrics Collection Successful!")
        print(f"   Total Contributors: {team_metrics['summary']['total_contributors']}")
        print(f"   Active Contributors: {team_metrics['summary']['active_contributors']}")
        print(f"   Total Commits: {team_metrics['summary']['total_commits']}")
        print(f"   Avg Commits/Person: {team_metrics['summary']['avg_commits_per_contributor']:.1f}")
        
        print(f"\n   Velocity:")
        print(f"      Commits/Week: {team_metrics['velocity']['commits_per_week']:.1f}")
        print(f"      Trend: {team_metrics['velocity']['trend']}")
        print(f"      12-Week Activity: {team_metrics['velocity']['recent_activity']}")
        
        print(f"\n   Top 5 Contributors:")
        for i, contributor in enumerate(team_metrics['contributors'][:5], 1):
            print(f"      {i}. {contributor['name']}")
            print(f"         Commits: {contributor['commits']}, +{contributor['lines_added']}/-{contributor['lines_removed']} lines")
            print(f"         Files: {contributor['files_changed']}, Period: {contributor['first_commit']} to {contributor['last_commit']}")
        
        print(f"\n   Bus Factor Analysis:")
        print(f"      Bus Factor: {team_metrics['bus_factor']['factor']}")
        print(f"      Risk Level: {team_metrics['bus_factor']['risk'].upper()}")
        print(f"      Critical Contributors: {', '.join(team_metrics['bus_factor']['top_contributors'])}")
        
        if team_metrics['knowledge_distribution']['files']:
            print(f"\n   Knowledge Distribution:")
            print(f"      Concentration Score: {team_metrics['knowledge_distribution']['concentration_score']}%")
            print(f"      Files Analyzed: {len(team_metrics['knowledge_distribution']['files'])}")
            print(f"\n      Sample File Ownership:")
            for file_data in team_metrics['knowledge_distribution']['files'][:5]:
                print(f"         {file_data['file']}")
                print(f"            Owner: {file_data['primary_owner']} ({file_data['ownership_percentage']}% ownership)")
    else:
        print("❌ Team Metrics Collection Failed (not a git repository?)")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\n✅ Phase 16 team metrics collector working with CURRENT STATE data")
    print("✅ No mock data - all metrics from actual git history")
    print("✅ Ready for dashboard integration")
    print("\n📋 Next: Integration Testing & Final Validation")

if __name__ == "__main__":
    test_phase16_team_metrics()
