#!/usr/bin/env python3
"""
Regenerate CORTEX Dashboard Data

Runs collectors to generate fresh dashboard data for CORTEX.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add CORTEX to path
cortex_root = Path(__file__).parent
sys.path.insert(0, str(cortex_root))
sys.path.insert(0, str(cortex_root / "src"))

def main():
    """Execute dashboard collectors for CORTEX."""
    
    # Configuration
    target_repo = cortex_root
    project_name = "CORTEX"
    
    print("=" * 70)
    print("CORTEX Dashboard Data Regeneration")
    print("=" * 70)
    print(f"\nTarget Repository: {target_repo}")
    print(f"Project Name: {project_name}")
    
    if not target_repo.exists():
        print(f"\nERROR: Repository not found at {target_repo}")
        return 1
    
    print(f"Repository verified: OK")
    print("\nStarting parallel data collection...\n")
    
    try:
        # Import parallel collector orchestrator
        from dashboard.data.parallel_collector import ParallelCollectorOrchestrator
        
        # Output directory
        repo_slug = project_name.lower().replace(" ", "-")
        output_dir = cortex_root / "cortex-brain" / "dashboards" / repo_slug
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Output directory: {output_dir}")
        print("\n" + "-" * 70)
        
        # Execute collectors in parallel (6 threads)
        start_time = time.time()
        parallel_orchestrator = ParallelCollectorOrchestrator(target_repo)
        collected_data, collection_time = parallel_orchestrator.collect_all_parallel()
        
        print(f"\nAll collectors completed in {collection_time:.2f} seconds")
        print("\n" + "-" * 70)
        print("Collection Results:")
        print("-" * 70)
        
        # Display collection summary
        for filename, data in collected_data.items():
            size_kb = len(json.dumps(data)) / 1024
            print(f"  [OK] {filename:<30} {size_kb:>8.2f} KB")
        
        # Write collected data to files
        print("\n" + "-" * 70)
        print("Writing dashboard data files...")
        print("-" * 70)
        
        for filename, data in collected_data.items():
            try:
                file_path = output_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"  [OK] {filename}")
            except Exception as e:
                print(f"  [ERROR] {filename}: {e}")
        
        # Write metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "project": project_name,
            "project_root": str(target_repo),
            "collection_time_seconds": collection_time
        }
        
        metadata_path = output_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        print(f"  [OK] metadata.json")
        
        total_time = time.time() - start_time
        print("\n" + "=" * 70)
        print(f"✅ Dashboard data generation complete in {total_time:.2f}s")
        print(f"📂 Output: {output_dir}")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
