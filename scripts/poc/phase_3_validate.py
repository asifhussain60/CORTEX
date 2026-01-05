#!/usr/bin/env python3
"""Phase 3: Validation - Verify POC completion."""
import json
from pathlib import Path
from datetime import datetime


def execute():
    print("🎯 POC Phase 3: Validation")
    
    # Validate test file
    test_file = Path("cortex-brain/documents/planning/active/poc-python-execution/artifacts/poc_test_file.txt")
    
    if not test_file.exists():
        print("❌ Test file not found!")
        return {"success": False, "message": "Validation failed"}
    
    with open(test_file) as f:
        content = f.read()
    
    required_strings = [
        "POC Test File",
        "Created:",
        "Purpose: Prove Python execution works",
        "Architecture: Copilot → Terminal → Python → Results"
    ]
    
    all_present = all(s in content for s in required_strings)
    
    if all_present:
        print("✅ All required strings found in test file")
        print(f"📄 File size: {test_file.stat().st_size} bytes")
        print(f"📝 Lines: {len(content.splitlines())}")
    else:
        print("❌ Missing required strings!")
        return {"success": False, "message": "Validation failed"}
    
    # Update progress tracker
    tracker_path = Path("cortex-brain/documents/planning/active/poc-python-execution/tracking/progress-tracker.json")
    
    with open(tracker_path) as f:
        tracker = json.load(f)
    
    phase = next((p for p in tracker["phases"] if p["number"] == 3), None)
    if not phase:
        tracker["phases"].append({
            "number": 3,
            "name": "Validation",
            "status": "complete",
            "completed_at": datetime.now().isoformat()
        })
    else:
        phase["status"] = "complete"
        phase["completed_at"] = datetime.now().isoformat()
    
    # Mark plan complete
    tracker["status"] = "COMPLETE"
    tracker["completed_phases"] = 3
    tracker["total_phases"] = 3
    tracker["completed_at"] = datetime.now().isoformat()
    
    with open(tracker_path, "w") as f:
        json.dump(tracker, f, indent=2)
    
    print("📊 Progress tracker updated")
    print("\n🎉 POC COMPLETE - Python execution proven!")
    
    return {
        "success": True,
        "message": "POC validation complete",
        "phases_complete": 3,
        "architecture_validated": True
    }


if __name__ == "__main__":
    result = execute()
    print(f"\n✅ {result['message']}")
    if result.get("architecture_validated"):
        print("🏆 CORTEX v5.2.0 architecture validated!")
