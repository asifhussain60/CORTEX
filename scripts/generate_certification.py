#!/usr/bin/env python3
"""
STS Certification Report Generator
Generates production-ready certification reports from validation results

Usage:
    python scripts/generate_certification.py
    python scripts/generate_certification.py --results path/to/results.json
    python scripts/generate_certification.py --format html
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict

CORTEX_ROOT = Path(__file__).parent.parent
RESULTS_DIR = CORTEX_ROOT / "cortex-brain/sts-results"


class CertificationGenerator:
    """Generate STS certification reports"""
    
    def __init__(self, results: Dict):
        self.results = results
        self.summary = results.get('summary', {})
        self.capabilities = results.get('capabilities', [])
    
    def generate_markdown(self) -> str:
        """Generate markdown certification report"""
        passed = self.summary.get('passed', 0)
        total = self.summary.get('total', 0)
        confidence = self.summary.get('confidence', 0)
        overall = self.results.get('overall', 'UNKNOWN')
        
        # Determine certification status
        if passed == total and overall == 'PASS':
            status = "✅ CERTIFIED"
            status_desc = "PRODUCTION READY"
        elif passed >= total * 0.75:
            status = "⚠️ BETA"
            status_desc = "Beta Ready (Known Gaps)"
        else:
            status = "❌ FAILED"
            status_desc = "Not Production Ready"
        
        report = f"""# CORTEX 4.0 STS Certification Report

**Date:** {datetime.now().strftime('%B %d, %Y')}  
**Version:** 4.0.0  
**Status:** {status}  
**Confidence Level:** {confidence:.1f}%

---

## 📊 Executive Summary

This report certifies the production readiness of CORTEX 4.0 based on validation against the STS (Sharpen The Saw) template application across 8 critical capabilities.

**Verdict:** {status_desc}

**Summary:**
- **Total Capabilities:** {total}
- **Passed:** {passed}
- **Failed:** {total - passed}
- **Overall Status:** {overall}
- **Confidence:** {confidence:.1f}%

---

## 🎯 Critical Capabilities ({passed}/{total} Required)

"""
        
        # Add capability results
        for cap in self.capabilities:
            cap_name = cap.get('capability', 'Unknown')
            cap_status = cap.get('status', 'UNKNOWN')
            metrics = cap.get('metrics', {})
            issues = cap.get('issues', [])
            
            icon = "✅" if cap_status == 'PASS' else "❌"
            
            report += f"### {icon} {cap_name.replace('_', ' ').title()}\n\n"
            report += f"**Status:** {cap_status}\n\n"
            
            if metrics:
                report += "**Metrics:**\n"
                for metric_name, metric_value in metrics.items():
                    report += f"- {metric_name.replace('_', ' ').title()}: {metric_value}\n"
                report += "\n"
            
            if issues:
                report += "**Issues:**\n"
                for issue in issues:
                    report += f"- {issue}\n"
                report += "\n"
            
            report += "---\n\n"
        
        # Add confidence formula
        report += f"""## 📐 Confidence Formula

**Production Readiness Gate:**

```
Confidence = (Passed / Total) × 100%
           = ({passed} / {total}) × 100%
           = {confidence:.1f}%
```

**Thresholds:**
- ✅ **100% (8/8):** PRODUCTION READY - Full confidence
- ⚠️ **75-99% (6-7/8):** BETA READY - Known gaps, acceptable risks
- ❌ **<75% (<6/8):** NOT READY - Critical gaps present

**Current Status:** {status_desc} ({confidence:.1f}%)

---

## 🔍 Detailed Analysis

### What Was Validated

The STS template application contains 40 documented flaws across 6 categories:
- Security: 10 flaws (hardcoded secrets, SQL injection, weak auth)
- SOLID Violations: 8 flaws (god classes, tight coupling)
- Code Quality: 10 flaws (complexity, duplication, dead code)
- Performance: 6 flaws (N+1 queries, memory leaks)
- Testing: 4 gaps (placeholder tests, no mocking)
- Documentation: 2 issues (outdated, incomplete)

### Validation Scope

8 critical capabilities tested:
1. **Deployment Pipeline:** Build, install, publish, first-run
2. **Multi-Workspace:** VSCode, Visual Studio, GitHub Copilot detection
3. **Upgrade Path:** 3.0→4.0 migration with rollback
4. **End-to-End Workflows:** Multi-orchestrator chains
5. **Brain Persistence:** Failure recovery, integrity
6. **Agent Collaboration:** Handoffs, context preservation
7. **Performance Baseline:** Scale, latency, memory
8. **Regression Detection:** Baseline comparison

---

## ✅ Certification Decision

"""
        
        if passed == total:
            report += f"""**CERTIFIED FOR PRODUCTION**

All {total} critical capabilities passed validation. CORTEX 4.0 is ready for production deployment with full confidence.

**Recommended Actions:**
- ✅ Deploy to production environment
- ✅ Enable for all users
- ✅ Monitor initial usage for edge cases
- ✅ Run weekly regression validation

**Next Validation:** Run STS validation weekly or after major feature additions.
"""
        elif passed >= total * 0.75:
            report += f"""**BETA CERTIFICATION**

{passed}/{total} critical capabilities passed. System is beta-ready with known limitations.

**Known Gaps:**
"""
            failed_caps = [c for c in self.capabilities if c.get('status') != 'PASS']
            for cap in failed_caps:
                report += f"- {cap.get('capability', 'Unknown').replace('_', ' ').title()}\n"
            
            report += f"""
**Recommended Actions:**
- ⚠️ Deploy to beta/staging environment
- ⚠️ Enable for limited user group
- 🔧 Address failing capabilities
- 🔄 Re-run validation after fixes

**Production Gate:** All 8 capabilities must pass for production certification.
"""
        else:
            report += f"""**CERTIFICATION FAILED**

Only {passed}/{total} critical capabilities passed. System is not ready for production.

**Critical Gaps:**
"""
            failed_caps = [c for c in self.capabilities if c.get('status') != 'PASS']
            for cap in failed_caps:
                report += f"- {cap.get('capability', 'Unknown').replace('_', ' ').title()}\n"
                if cap.get('issues'):
                    for issue in cap['issues']:
                        report += f"  - {issue}\n"
            
            report += f"""
**Recommended Actions:**
- ❌ Do NOT deploy to production
- 🔧 Fix all failing capabilities
- 🔄 Re-run full validation
- 📊 Review architectural decisions

**Production Gate:** Minimum 6/8 capabilities required for beta, 8/8 for production.
"""
        
        report += f"""
---

**Report Generated:** {datetime.now().isoformat()}  
**Generator:** CORTEX STS Validation Framework  
**Contact:** Asif Hussain | GitHub: github.com/asifhussain60/CORTEX
"""
        
        return report
    
    def generate_html(self) -> str:
        """Generate HTML certification report (stub for now)"""
        # Week 1 Day 4 can implement this if time permits
        markdown = self.generate_markdown()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>CORTEX 4.0 STS Certification Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .status-pass {{ color: #27ae60; }}
        .status-fail {{ color: #e74c3c; }}
        .metric {{ background: #ecf0f1; padding: 10px; margin: 5px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <pre>{markdown}</pre>
</body>
</html>"""
        
        return html
    
    def save(self, output_path: Path, format: str = 'markdown'):
        """Save certification report"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'html':
            content = self.generate_html()
            suffix = '.html'
        else:
            content = self.generate_markdown()
            suffix = '.md'
        
        # Ensure correct suffix
        if not str(output_path).endswith(suffix):
            output_path = output_path.with_suffix(suffix)
        
        with open(output_path, 'w') as f:
            f.write(content)
        
        print(f"📄 Certification report saved: {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description='STS Certification Generator')
    parser.add_argument('--results', type=str,
                       help='Path to validation results JSON (default: latest)')
    parser.add_argument('--format', type=str, default='markdown',
                       choices=['markdown', 'html'],
                       help='Output format (default: markdown)')
    parser.add_argument('--output', type=str,
                       help='Output path for certification report')
    
    args = parser.parse_args()
    
    # Resolve results path
    if args.results:
        results_path = Path(args.results)
        if not results_path.is_absolute():
            results_path = CORTEX_ROOT / results_path
    else:
        # Use latest results
        if not RESULTS_DIR.exists():
            print(f"❌ Results directory not found: {RESULTS_DIR}")
            return 1
        
        results_files = sorted(RESULTS_DIR.glob('*.json'), reverse=True)
        if not results_files:
            print(f"❌ No results files found in {RESULTS_DIR}")
            return 1
        
        results_path = results_files[0]
        print(f"📄 Using latest results: {results_path.name}")
    
    # Load results
    try:
        with open(results_path, 'r') as f:
            results = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load results: {e}")
        return 1
    
    # Generate certification
    generator = CertificationGenerator(results)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = CORTEX_ROOT / output_path
    else:
        timestamp = datetime.now().strftime('%Y-%m-%d')
        suffix = '.html' if args.format == 'html' else '.md'
        output_path = RESULTS_DIR / f"certification-{timestamp}{suffix}"
    
    # Save report
    try:
        generator.save(output_path, args.format)
        print(f"\n✅ Certification report generated successfully")
        
        # Print summary
        summary = results.get('summary', {})
        print(f"\n📊 Summary:")
        print(f"  Status: {results.get('overall', 'UNKNOWN')}")
        print(f"  Passed: {summary.get('passed', 0)}/{summary.get('total', 0)}")
        print(f"  Confidence: {summary.get('confidence', 0):.1f}%")
        
        return 0
    except Exception as e:
        print(f"❌ Failed to generate report: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
