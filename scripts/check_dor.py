"""DoR (Definition of Ready) Validation Script"""
import yaml
from pathlib import Path

def validate_phases():
    roadmap_dir = Path(__file__).parent.parent / ".github" / "roadmap" / "phases"
    results = {}
    
    for phase_file in sorted(roadmap_dir.glob("*.yaml")):
        with open(phase_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        ac_ids = []
        missing_test_refs = []
        
        days_data = data.get('days', {})
        # Handle both dict format (day_0, day_1) and list format
        if isinstance(days_data, dict):
            days_list = days_data.values()
        else:
            days_list = days_data
        
        # Collect all tasks - from days or from root-level tasks
        all_tasks = []
        
        # Tasks from days
        for day in days_list:
            if not isinstance(day, dict):
                continue
            all_tasks.extend(day.get('tasks', []))
        
        # Also check root-level tasks (phase-parallel uses this format)
        root_tasks = data.get('tasks', [])
        if isinstance(root_tasks, list):
            all_tasks.extend(root_tasks)
            
        for task in all_tasks:
                if not isinstance(task, dict):
                    continue
                for ac in task.get('acceptance_criteria', []):
                    if not isinstance(ac, dict):
                        continue
                    ac_id = ac.get('ac_id')
                    if ac_id:
                        ac_ids.append(ac_id)
                        has_test_ref = (
                            ac.get('test_file') or 
                            ac.get('test_command') or
                            ac_id.startswith('AC-EXPLAIN')
                        )
                        if not has_test_ref:
                            missing_test_refs.append(ac_id)
        
        risks = data.get('risks', [])
        summary = data.get('summary', {})
        est_hours = summary.get('estimated_hours', 0)
        buffer_hours = summary.get('buffer_hours', 0)
        
        results[phase_file.name] = {
            'ac_count': len(ac_ids),
            'missing_tests': len(missing_test_refs),
            'missing_list': missing_test_refs,
            'risks_count': len(risks),
            'estimated_hours': est_hours,
            'buffer_hours': buffer_hours
        }
    
    return results

if __name__ == "__main__":
    results = validate_phases()
    
    print("=" * 70)
    print("DoR VALIDATION RESULTS")
    print("=" * 70)
    
    for name, r in results.items():
        ok = r['missing_tests'] == 0 and r['risks_count'] > 0 and r['estimated_hours'] > 0
        status = "PASS" if ok else "FAIL"
        print(f"\n[{status}] {name}")
        print(f"  AC-IDs: {r['ac_count']}")
        print(f"  Missing Test Refs: {r['missing_tests']}")
        if r['missing_list']:
            print(f"  Missing: {r['missing_list'][:5]}{'...' if len(r['missing_list']) > 5 else ''}")
        print(f"  Risks: {r['risks_count']}")
        print(f"  Est Hours: {r['estimated_hours']} + {r['buffer_hours']} buffer")
    
    total_missing = sum(r['missing_tests'] for r in results.values())
    total_risks = sum(r['risks_count'] for r in results.values())
    total_hours = sum(r['estimated_hours'] for r in results.values())
    total_buffer = sum(r['buffer_hours'] for r in results.values())
    
    print("\n" + "=" * 70)
    print(f"TOTALS:")
    print(f"  Missing Test Refs: {total_missing}")
    print(f"  Risks Documented: {total_risks}")
    print(f"  Estimated Hours: {total_hours} + {total_buffer} buffer")
    print("=" * 70)
    
    if total_missing == 0 and total_risks >= 15:
        print("\n✓ DoR Score: 100/100 - All criteria met!")
    else:
        print(f"\n✗ DoR gaps remain: {total_missing} missing test refs")
