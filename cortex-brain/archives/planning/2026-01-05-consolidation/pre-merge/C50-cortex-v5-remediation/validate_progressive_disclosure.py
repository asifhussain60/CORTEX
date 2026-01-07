#!/usr/bin/env python3
"""
C50 Epic Progressive Disclosure Validation
Verifies that active work appears at top, completed at bottom
"""

import json
from pathlib import Path

def load_epic_data():
    """Load epic progress tracker"""
    tracker_path = Path(__file__).parent / "tracking" / "epic-progress-tracker.json"
    
    if not tracker_path.exists():
        print(f"⚠️  Tracker not found: {tracker_path}")
        return None
    
    with open(tracker_path) as f:
        return json.load(f)

def validate_sorting_logic():
    """Validate that sorting logic correctly prioritizes active work"""
    
    priority_map = {
        'in progress': 1,
        'blocked': 2,
        'pending': 3,
        'active': 4,
        'deferred': 5,
        'complete': 6,
        'completed': 6
    }
    
    test_plans = [
        {'id': 'C50-01', 'status': 'Complete', 'name': 'Should be last'},
        {'id': 'C50-02', 'status': 'In Progress', 'name': 'Should be first'},
        {'id': 'C50-03', 'status': 'Blocked', 'name': 'Should be second'},
        {'id': 'C50-04', 'status': 'Pending', 'name': 'Should be third'},
        {'id': 'C50-05', 'status': 'Completed', 'name': 'Should be last'},
    ]
    
    # Sort using priority map
    def get_priority(plan):
        status = plan['status'].lower()
        for key, value in priority_map.items():
            if key in status:
                return value
        return 999
    
    sorted_plans = sorted(test_plans, key=lambda p: (get_priority(p), p['id']))
    
    print("\n🧪 Sorting Logic Validation\n")
    print("Expected Order:")
    print("  1. In Progress (priority 1)")
    print("  2. Blocked (priority 2)")
    print("  3. Pending (priority 3)")
    print("  4. Complete/Completed (priority 6)")
    print("\nActual Sorted Order:")
    
    for i, plan in enumerate(sorted_plans, 1):
        priority = get_priority(plan)
        print(f"  {i}. {plan['status']} (priority {priority}) - {plan['name']}")
    
    # Validate
    expected_order = ['In Progress', 'Blocked', 'Pending', 'Complete', 'Completed']
    actual_order = [p['status'] for p in sorted_plans]
    
    if actual_order == expected_order:
        print("\n✅ Sorting logic is CORRECT")
        return True
    else:
        print(f"\n❌ Sorting logic FAILED")
        print(f"   Expected: {expected_order}")
        print(f"   Got: {actual_order}")
        return False

def analyze_actual_data():
    """Analyze actual C50 epic data"""
    
    data = load_epic_data()
    if not data:
        return
    
    print("\n📊 C50 Epic Data Analysis\n")
    
    # Group by status
    status_groups = {}
    for plan in data.get('child_plans', []):
        status = plan['status']
        if status not in status_groups:
            status_groups[status] = []
        status_groups[status].append(plan['id'])
    
    print("Status Distribution:")
    for status, plans in sorted(status_groups.items()):
        print(f"  {status}: {len(plans)} plans")
        print(f"    {', '.join(plans)}")
    
    # Show top 5 and bottom 5 after sorting
    priority_map = {
        'in progress': 1,
        'blocked': 2,
        'pending': 3,
        'active': 4,
        'deferred': 5,
        'complete': 6,
        'completed': 6
    }
    
    def get_priority(plan):
        status = plan['status'].lower()
        for key, value in priority_map.items():
            if key in status:
                return value
        return 999
    
    sorted_plans = sorted(
        data.get('child_plans', []),
        key=lambda p: (get_priority(p), p.get('order', p['id']))
    )
    
    print("\n🔝 Top 5 Plans (Should be active work):")
    for i, plan in enumerate(sorted_plans[:5], 1):
        print(f"  {i}. {plan['id']} - {plan['status']} - {plan['name']}")
    
    print("\n⬇️  Bottom 5 Plans (Should be completed):")
    for i, plan in enumerate(sorted_plans[-5:], 1):
        print(f"  {i}. {plan['id']} - {plan['status']} - {plan['name']}")

def main():
    print("=" * 60)
    print("C50 PROGRESSIVE DISCLOSURE VALIDATION")
    print("=" * 60)
    
    # Validate sorting logic
    logic_valid = validate_sorting_logic()
    
    # Analyze actual data
    analyze_actual_data()
    
    print("\n" + "=" * 60)
    if logic_valid:
        print("✅ VALIDATION PASSED")
    else:
        print("❌ VALIDATION FAILED")
    print("=" * 60)

if __name__ == '__main__':
    main()
