#!/usr/bin/env python3
"""
CORTEX Review CLI Wrapper

Command-line interface for CORTEX architectural review.

Features:
- Comprehensive architecture analysis
- Code quality assessment
- Security and risk evaluation
- Performance and scalability review
- Maintainability and technical debt analysis
- Context-aware scope filtering

Usage:
    python scripts/cli_wrappers/review_wrapper.py
    python scripts/cli_wrappers/review_wrapper.py --scope auth api
    python scripts/cli_wrappers/review_wrapper.py --output json

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import sys
from pathlib import Path
import argparse

# Add CORTEX root to path
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

from .base_wrapper import BaseCLIWrapper, main_template
from src.operations.modules.architectural.review_orchestrator import ReviewOrchestrator


class ReviewWrapper(BaseCLIWrapper):
    """CLI wrapper for CORTEX architectural review."""
    
    def get_orchestrator(self):
        """Get review orchestrator."""
        return ReviewOrchestrator()
    
    def get_operation_name(self) -> str:
        """Get operation name."""
        return "CORTEX Architectural Review"
    
    def setup_argparse(self, parser: argparse.ArgumentParser) -> None:
        """Configure command-line arguments."""
        super().setup_argparse(parser)
        
        parser.add_argument(
            '--scope',
            nargs='+',
            help='Scope filter keywords (e.g., auth api security)'
        )
        parser.add_argument(
            '--context',
            type=str,
            help='Request context for contextual analysis'
        )
    
    def build_context(self):
        """Build context for review."""
        from typing import Dict, Any
        context = super().build_context()
        
        if hasattr(self.args, 'scope') and self.args.scope:
            context['scope_filter'] = self.args.scope
        
        if hasattr(self.args, 'context') and self.args.context:
            context['request_context'] = self.args.context
        
        context['path'] = Path(self.args.project_root).resolve()
        return context
    
    def format_text_output(self, result) -> str:
        """Format review result as human-readable text."""
        from src.operations.base_operation_module import OperationStatus
        
        lines = []
        lines.append(f"\n{'='*70}")
        lines.append(f"  📋 CORTEX Architectural Review")
        lines.append(f"{'='*70}\n")
        
        # Status
        if result.status == OperationStatus.SUCCESS:
            lines.append("Status: ✓ SUCCESS")
        else:
            lines.append("Status: ✗ FAILED")
        
        # Overall Score
        if result.data and 'overall_score' in result.data:
            score = result.data['overall_score']
            lines.append(f"Overall Score: {score}/100")
            
            # Rating
            if score >= 90:
                lines.append("Rating: 🟢 EXCELLENT")
            elif score >= 75:
                lines.append("Rating: 🟡 GOOD")
            elif score >= 50:
                lines.append("Rating: 🟠 FAIR")
            else:
                lines.append("Rating: 🔴 NEEDS IMPROVEMENT")
        
        # Sections
        if result.data and 'sections' in result.data:
            lines.append("\n" + "="*70)
            lines.append("REVIEW SECTIONS")
            lines.append("="*70)
            
            for section in result.data['sections']:
                if isinstance(section, dict):
                    name = section.get('name', 'Unknown')
                    score = section.get('score', 0)
                    findings_count = len(section.get('findings', []))
                    
                    lines.append(f"\n{name} - {score}/100")
                    lines.append(f"  Findings: {findings_count}")
                    
                    # Show findings summary
                    findings = section.get('findings', [])
                    if findings:
                        severity_counts = {}
                        for finding in findings:
                            if isinstance(finding, dict):
                                severity = finding.get('severity', 'UNKNOWN')
                                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                        
                        if severity_counts:
                            lines.append("  Severity breakdown:")
                            for severity, count in severity_counts.items():
                                lines.append(f"    {severity}: {count}")
        
        # Findings
        if result.data and 'findings' in result.data:
            findings = result.data['findings']
            if findings:
                lines.append("\n" + "="*70)
                lines.append(f"KEY FINDINGS ({len(findings)})")
                lines.append("="*70)
                
                # Group by severity
                critical = [f for f in findings if isinstance(f, dict) and f.get('severity') == 'CRITICAL']
                high = [f for f in findings if isinstance(f, dict) and f.get('severity') == 'HIGH']
                
                if critical:
                    lines.append(f"\n🔴 CRITICAL ({len(critical)}):")
                    for finding in critical[:5]:  # Show top 5
                        title = finding.get('title', 'Unknown')
                        lines.append(f"  - {title}")
                
                if high:
                    lines.append(f"\n🟠 HIGH ({len(high)}):")
                    for finding in high[:5]:  # Show top 5
                        title = finding.get('title', 'Unknown')
                        lines.append(f"  - {title}")
        
        # Recommendations
        if result.data and 'recommendations' in result.data:
            recommendations = result.data['recommendations']
            if recommendations:
                lines.append("\n" + "="*70)
                lines.append(f"💡 RECOMMENDATIONS ({len(recommendations)})")
                lines.append("="*70)
                for i, rec in enumerate(recommendations[:10], 1):  # Show top 10
                    if isinstance(rec, str):
                        lines.append(f"  {i}. {rec}")
                    elif isinstance(rec, dict):
                        lines.append(f"  {i}. {rec.get('recommendation', 'Unknown')}")
        
        # Warnings
        if result.warnings:
            lines.append("\n" + "="*70)
            lines.append(f"⚠️  WARNINGS ({len(result.warnings)})")
            lines.append("="*70)
            for warning in result.warnings:
                lines.append(f"  {warning}")
        
        # Errors
        if result.errors:
            lines.append("\n" + "="*70)
            lines.append(f"❌ ERRORS ({len(result.errors)})")
            lines.append("="*70)
            for error in result.errors:
                lines.append(f"  {error}")
        
        lines.append(f"\n{'='*70}\n")
        return '\n'.join(lines)


if __name__ == '__main__':
    sys.exit(main_template(ReviewWrapper))
