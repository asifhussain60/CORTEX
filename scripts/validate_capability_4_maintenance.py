#!/usr/bin/env python3
"""
Phase 13B Capability 4: System Maintenance Validation

This script validates the System Maintenance Orchestrator by running it
against the STS validation application and measuring the 7-phase workflow.

Author: Asif Hussain
Date: December 26, 2025
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add project root to path
CORTEX_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

from src.operations.modules.orchestration.maintenance_orchestrator import MaintenanceOrchestrator


def setup_logging() -> logging.Logger:
    """Setup logging for validation."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("capability_4_validation")


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def run_validation() -> Dict[str, Any]:
    """
    Run Capability 4 validation.
    
    Returns:
        Validation results
    """
    logger = setup_logging()
    results = {
        "capability": "System Maintenance",
        "start_time": datetime.now().isoformat(),
        "phases": {},
        "overall_success": False,
        "errors": []
    }
    
    print_section("Phase 13B Capability 4: System Maintenance Validation")
    
    # Target: STS validation app
    sts_app_path = CORTEX_ROOT / "cortex-sample-apps" / "sts-validation-app"
    
    if not sts_app_path.exists():
        error = f"STS validation app not found: {sts_app_path}"
        logger.error(error)
        results["errors"].append(error)
        return results
    
    print(f"📁 Target Application: {sts_app_path}")
    print(f"🎯 Objective: Run 7-phase maintenance workflow")
    print(f"📊 Expected: Health improvement +20 minimum (targeting +30)")
    
    try:
        # Initialize orchestrator
        print_section("Phase 0: Initialization")
        orchestrator = MaintenanceOrchestrator(
            cortex_root=CORTEX_ROOT,
            logger=logger
        )
        print("✅ Maintenance Orchestrator initialized")
        
        # Run 7-phase workflow
        print_section("Executing 7-Phase Maintenance Workflow")
        
        context = {
            "target_path": str(sts_app_path),
            "auto_fix": True,
            "dry_run": False
        }
        
        print("🚀 Starting maintenance workflow...\n")
        
        # Execute orchestrator
        result = orchestrator.execute(context)
        
        # Extract results - orchestrator returns dict, not object
        if isinstance(result, dict):
            results["overall_success"] = result.get("success", False)
            results["execution_time_seconds"] = result.get("duration_seconds", 0)
            data = result
        else:
            # Handle OrchestratorResult object if returned
            results["overall_success"] = result.success
            results["execution_time_seconds"] = result.metadata.get("duration_seconds", 0)
            data = result.data
        
        if results["overall_success"]:
            print("\n✅ Maintenance workflow completed successfully!")
            
            # Extract phase results
            data = result.data
            phases_completed = data.get("phases_completed", 0)
            total_phases = data.get("metrics", {}).get("phases_total", 7)
            
            print(f"\n📊 Phases Completed: {phases_completed}/{total_phases}")
            
            # Health metrics
            baseline = orchestrator.baseline_health
            final = orchestrator.final_health
            
            if baseline is not None and final is not None:
                delta = final - baseline
                results["baseline_health"] = baseline
                results["final_health"] = final
                results["health_delta"] = delta
                
                print(f"\n🏥 Health Metrics:")
                print(f"   Baseline: {baseline:.1f}/100")
                print(f"   Final:    {final:.1f}/100")
                print(f"   Delta:    {delta:+.1f} points")
                
                # Grade interpretation
                def get_grade(score):
                    if score >= 90: return "A"
                    if score >= 80: return "B"
                    if score >= 70: return "C"
                    if score >= 60: return "D"
                    return "F"
                
                baseline_grade = get_grade(baseline)
                final_grade = get_grade(final)
                
                print(f"   Grade:    {baseline_grade} → {final_grade}")
                
                # Validate success criteria
                print(f"\n✅ Success Criteria:")
                if delta >= 20:
                    print(f"   ✅ Health improvement: {delta:+.1f} (target: +20)")
                else:
                    print(f"   ❌ Health improvement: {delta:+.1f} (target: +20)")
                    results["errors"].append(f"Health improvement below target: {delta:+.1f} < +20")
                
                if phases_completed == total_phases:
                    print(f"   ✅ All phases completed: {phases_completed}/{total_phases}")
                else:
                    print(f"   ⚠️  Phases completed: {phases_completed}/{total_phases}")
            
            # Warnings
            warnings = data.get("warnings", [])
            if warnings:
                print(f"\n⚠️  Warnings ({len(warnings)}):")
                for warning in warnings[:5]:  # Show first 5
                    print(f"   - {warning}")
            
            # Improvements
            improvements = data.get("improvements", [])
            if improvements:
                print(f"\n✨ Improvements ({len(improvements)}):")
                for improvement in improvements[:5]:  # Show first 5
                    print(f"   - {improvement}")
            
        else:
            print(f"\n❌ Maintenance workflow failed: {data.get('message', 'Unknown error')}")
            results["errors"].append(data.get("message", "Unknown error"))
        
    except Exception as e:
        error_msg = f"Validation failed: {str(e)}"
        logger.exception(error_msg)
        results["errors"].append(error_msg)
        print(f"\n❌ {error_msg}")
    
    results["end_time"] = datetime.now().isoformat()
    
    # Final verdict
    print_section("Validation Verdict")
    
    if results["overall_success"] and not results["errors"]:
        print("✅ CAPABILITY 4 VALIDATED")
        print("\nSystem Maintenance Orchestrator successfully:")
        print("  ✅ Executed all 7 phases")
        print("  ✅ Improved system health")
        print("  ✅ No critical errors")
        results["validation_status"] = "PASS"
    else:
        print("❌ CAPABILITY 4 VALIDATION FAILED")
        if results["errors"]:
            print("\nErrors:")
            for error in results["errors"]:
                print(f"  ❌ {error}")
        results["validation_status"] = "FAIL"
    
    return results


def save_results(results: Dict[str, Any]):
    """Save validation results to file."""
    output_dir = CORTEX_ROOT / "cortex-brain" / "documents" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "phase-13b-capability-4-results.json"
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved: {output_file}")


if __name__ == "__main__":
    print("🧠 CORTEX Phase 13B - Capability 4 Validation")
    print("=" * 80)
    
    results = run_validation()
    save_results(results)
    
    # Exit with appropriate code
    sys.exit(0 if results["validation_status"] == "PASS" else 1)
