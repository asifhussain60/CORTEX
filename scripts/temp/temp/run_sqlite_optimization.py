#!/usr/bin/env python
"""
Run SQLite optimization across all CORTEX tier databases.
Generates comprehensive before/after report with space reclamation metrics.
"""
from pathlib import Path
from src.operations.modules.database.sqlite_optimizer import SQLiteOptimizer

def main():
    print("🔧 CORTEX SQLite Database Optimization")
    print("=" * 80)
    
    # Initialize optimizer
    optimizer = SQLiteOptimizer()
    
    # Run optimization on all tiers
    print("\n⚙️  Optimizing databases...")
    results = optimizer.optimize_all()
    
    # Display summary
    print("\n" + "=" * 80)
    print("📊 OPTIMIZATION RESULTS")
    print("=" * 80)
    
    summary = results['summary']
    print(f"\n✅ Databases Optimized: {summary['successful']}/{summary['total_databases']}")
    print(f"💾 Total Space Reclaimed: {summary['total_space_reclaimed']:,.0f} bytes")
    print(f"   ({summary['total_space_reclaimed'] / 1024 / 1024:.2f} MB)")
    
    # Per-tier details
    print("\n" + "-" * 80)
    print("PER-TIER BREAKDOWN")
    print("-" * 80)
    
    for tier_name, tier_data in results['databases'].items():
        if not tier_data['success']:
            print(f"\n❌ {tier_name.upper()}: FAILED")
            print(f"   Error: {tier_data.get('error', 'Unknown error')}")
            continue
        
        print(f"\n✅ {tier_name.upper()} Database:")
        print(f"   Initial Size: {tier_data['initial_size_mb']:.2f} MB")
        print(f"   Final Size: {tier_data['final_size_mb']:.2f} MB")
        print(f"   Space Reclaimed: {tier_data['space_reclaimed_mb']:.2f} MB ({tier_data['space_reclaimed_percent']:.1f}%)")
        
        integrity = tier_data.get('integrity_check', {})
        print(f"   Integrity Check: {'✅ Passed' if integrity.get('passed') else '❌ Failed'}")
        
        print(f"   VACUUM: {'✅ Completed' if tier_data.get('vacuum_completed') else '⏸️  Skipped'}")
        print(f"   ANALYZE: {'✅ Completed' if tier_data.get('analyze_completed') else '⏸️  Skipped'}")
        
        table_stats = tier_data.get('table_stats', [])
        print(f"   Tables: {len(table_stats)}")
        
        index_info = tier_data.get('index_analysis', {})
        print(f"   Indexes: {index_info.get('index_count', 0)}")
        
        if table_stats:
            print(f"\n   Table Statistics:")
            for table_stat in table_stats[:5]:  # Show first 5 tables
                print(f"      - {table_stat['table']}: {table_stat['rows']:,} rows")
            if len(table_stats) > 5:
                print(f"      ... ({len(table_stats) - 5} more tables)")
    
    # Generate detailed report file
    report_path = Path('cortex-brain/documents/reports/sqlite-optimization-report.txt')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 80)
    print(f"📄 Generating detailed report...")
    
    report_content = optimizer.generate_report(results, report_path)
    
    print(f"✅ Report saved: {report_path}")
    print(f"   ({report_path.stat().st_size:,} bytes)")
    
    # Also save JSON for programmatic access
    import json
    json_path = report_path.with_suffix('.json')
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"✅ JSON data saved: {json_path}")
    
    print("\n" + "=" * 80)
    print("🎉 Optimization Complete!")
    print("=" * 80)

if __name__ == '__main__':
    main()
