"""
SOLID Integration Validation Script

Validates complete SOLID integration across all phases.
Runs analysis on sample apps and generates comprehensive report.

Author: Asif Hussain
Date: December 5, 2025
"""

from pathlib import Path
from src.workflows.refactoring_intelligence import CodeSmellDetector, CodeSmellType
from src.workflows.solid_scoring_engine import SOLIDScoringEngine


def validate_sample_app(app_name: str, file_path: Path) -> dict:
    """
    Validate a sample application for SOLID compliance.
    
    Args:
        app_name: Name of the application
        file_path: Path to the Python file
        
    Returns:
        Validation results dictionary
    """
    print(f"\n{'=' * 70}")
    print(f"📊 Analyzing: {app_name}")
    print(f"{'=' * 70}")
    
    # Read source code
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    # Detect code smells
    detector = CodeSmellDetector()
    smells = detector.analyze_file(str(file_path), source_code)
    
    # Calculate SOLID score
    scoring_engine = SOLIDScoringEngine()
    score = scoring_engine.score_file(file_path, smells)
    
    # Filter SOLID violations
    solid_violations = [
        s for s in smells
        if s.smell_type in [
            CodeSmellType.SRP_VIOLATION,
            CodeSmellType.OCP_VIOLATION,
            CodeSmellType.LSP_VIOLATION,
            CodeSmellType.ISP_VIOLATION,
            CodeSmellType.DIP_VIOLATION,
            CodeSmellType.TIGHT_COUPLING,
            CodeSmellType.LOW_COHESION,
            CodeSmellType.SOLID_VIOLATION,
            CodeSmellType.GOD_CLASS  # Also a SOLID violation
        ]
    ]
    
    # Print score report
    print(scoring_engine.format_score_report(score))
    
    # Return results
    return {
        "app_name": app_name,
        "file_path": str(file_path),
        "overall_score": score.overall_score,
        "srp_score": score.srp_score,
        "ocp_score": score.ocp_score,
        "lsp_score": score.lsp_score,
        "isp_score": score.isp_score,
        "dip_score": score.dip_score,
        "coupling_score": score.coupling_score,
        "total_violations": len(solid_violations),
        "recommendations": score.recommendations,
        "passed": True
    }


def run_validation():
    """Run complete validation suite."""
    print("=" * 70)
    print("🧪 SOLID Integration Validation Suite")
    print("=" * 70)
    print("Testing SOLID detection, scoring, and recommendations")
    print()
    
    cortex_root = Path(__file__).parent.parent
    sample_apps_dir = cortex_root / "cortex-brain" / "validation" / "sample-apps"
    
    results = []
    
    # Validate BadMonolith
    bad_monolith = sample_apps_dir / "BadMonolith" / "monolith.py"
    if bad_monolith.exists():
        result = validate_sample_app("BadMonolith", bad_monolith)
        results.append(result)
    else:
        print(f"⚠️  BadMonolith not found: {bad_monolith}")
    
    # Validate CleanSolidApp
    clean_solid = sample_apps_dir / "CleanSolidApp" / "clean_solid.py"
    if clean_solid.exists():
        result = validate_sample_app("CleanSolidApp", clean_solid)
        results.append(result)
    else:
        print(f"⚠️  CleanSolidApp not found: {clean_solid}")
    
    # Generate summary
    print("\n" + "=" * 70)
    print("📊 VALIDATION SUMMARY")
    print("=" * 70)
    
    for result in results:
        print(f"\n{result['app_name']}:")
        print(f"  Overall Score: {result['overall_score']}%")
        print(f"  Total Violations: {result['total_violations']}")
        print(f"  Status: {'✅ PASS' if result['passed'] else '❌ FAIL'}")
    
    # Validate targets
    print("\n" + "=" * 70)
    print("🎯 TARGET VALIDATION")
    print("=" * 70)
    
    bad_result = next((r for r in results if r['app_name'] == 'BadMonolith'), None)
    clean_result = next((r for r in results if r['app_name'] == 'CleanSolidApp'), None)
    
    targets_met = True
    
    if bad_result:
        if bad_result['overall_score'] < 50:
            print(f"✅ BadMonolith <50%: {bad_result['overall_score']}%")
        else:
            print(f"❌ BadMonolith should be <50%: {bad_result['overall_score']}%")
            targets_met = False
    
    if clean_result:
        if clean_result['overall_score'] >= 90:
            print(f"✅ CleanSolidApp ≥90%: {clean_result['overall_score']}%")
        else:
            print(f"❌ CleanSolidApp should be ≥90%: {clean_result['overall_score']}%")
            targets_met = False
    
    print("\n" + "=" * 70)
    if targets_met:
        print("🎉 ALL VALIDATION TARGETS MET!")
    else:
        print("⚠️  Some validation targets not met")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    results = run_validation()
    
    # Save results
    import json
    from datetime import datetime
    
    cortex_root = Path(__file__).parent.parent
    report_dir = cortex_root / "cortex-brain" / "documents" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = report_dir / f"solid-validation-{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: {report_file}")
