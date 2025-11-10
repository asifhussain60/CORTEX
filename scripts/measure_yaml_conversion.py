#!/usr/bin/env python3
"""
YAML Conversion Token Reduction Measurement

Measures token reduction from converting design documents to YAML format.
Phase 5.5 specific - validates 40-60% reduction target.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import yaml
from pathlib import Path
from typing import Dict
from datetime import datetime


def estimate_tokens(text: str) -> int:
    """Estimate token count (4 chars per token approximation)."""
    return len(text) // 4


def measure_yaml_conversion():
    """Measure token reduction from YAML conversion."""
    cortex_root = Path(__file__).parent.parent
    brain_path = cortex_root / "cortex-brain"
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "phase": "5.5 - YAML Conversion",
        "target": "40-60% reduction",
        "measurements": []
    }
    
    # Measure each YAML file
    yaml_files = [
        ("operations-config.yaml", cortex_root / "cortex-operations.yaml", 4.0),
        ("module-definitions.yaml", brain_path / "module-definitions.yaml", 3.5),
        ("design-metadata.yaml", brain_path / "cortex-2.0-design" / "design-metadata.yaml", 3.0),
        ("brain-protection-rules.yaml", brain_path / "brain-protection-rules.yaml", 4.0),  # Baseline
    ]
    
    total_yaml = 0
    total_estimated_md = 0
    
    print("=" * 80)
    print("PHASE 5.5: YAML CONVERSION TOKEN REDUCTION")
    print("=" * 80)
    print()
    
    for name, file_path, md_multiplier in yaml_files:
        if file_path.exists():
            yaml_tokens = estimate_tokens(file_path.read_text(encoding='utf-8'))
            estimated_md = int(yaml_tokens * md_multiplier)
            reduction = ((estimated_md - yaml_tokens) / estimated_md) * 100
            
            status = "✅" if reduction >= 40 else "⚠️"
            
            measurement = {
                "file": name,
                "yaml_tokens": yaml_tokens,
                "estimated_markdown_tokens": estimated_md,
                "reduction_percentage": round(reduction, 1),
                "target_met": reduction >= 40,
                "status": "PASS" if reduction >= 40 else "REVIEW"
            }
            
            results["measurements"].append(measurement)
            
            total_yaml += yaml_tokens
            total_estimated_md += estimated_md
            
            print(f"{status} {name}")
            print(f"   YAML tokens:       {yaml_tokens:,}")
            print(f"   Est. Markdown:     {estimated_md:,}")
            print(f"   Reduction:         {reduction:.1f}%")
            print()
    
    # Overall summary
    overall_reduction = ((total_estimated_md - total_yaml) / total_estimated_md) * 100
    
    results["summary"] = {
        "total_yaml_tokens": total_yaml,
        "estimated_markdown_tokens": total_estimated_md,
        "overall_reduction": round(overall_reduction, 1),
        "target_met": overall_reduction >= 40,
        "files_measured": len(results["measurements"]),
        "all_passed": all(m["target_met"] for m in results["measurements"])
    }
    
    print("=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    print(f"Total YAML tokens:       {total_yaml:,}")
    print(f"Est. Markdown tokens:    {total_estimated_md:,}")
    print(f"Overall reduction:       {overall_reduction:.1f}%")
    print(f"Target (40-60%):         {'✅ MET' if overall_reduction >= 40 else '❌ NOT MET'}")
    print(f"All files passed:        {'✅ YES' if results['summary']['all_passed'] else '⚠️ SOME FAILED'}")
    print("=" * 80)
    
    if overall_reduction >= 60:
        print("\n🎉 EXCELLENT! Exceeded 60% reduction target!")
    elif overall_reduction >= 40:
        print("\n✅ SUCCESS! Met 40-60% reduction target!")
    else:
        print("\n⚠️ REVIEW: Below 40% target")
    
    # Save report
    report_file = brain_path / "cortex-2.0-design" / "yaml-conversion-measurements.yaml"
    with open(report_file, 'w', encoding='utf-8') as f:
        yaml.dump(results, f, default_flow_style=False, sort_keys=False)
    
    print(f"\n📄 Report saved: {report_file}")
    print()
    
    return results


if __name__ == "__main__":
    measure_yaml_conversion()
