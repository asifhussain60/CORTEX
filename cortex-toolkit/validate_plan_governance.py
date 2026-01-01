"""
Plan Governance Validator - Automated SKULL rule compliance check

Validates planning documents against CORTEX governance requirements:
- Phase -1 (Knowledge Library Consultation) present
- Phase 10+ (Comprehensive REFACTOR) has ≥15 tasks across 5 categories
- copilot_instructions block includes knowledge library references

Author: CORTEX Governance Team
Version: 1.0.0
Date: January 1, 2026
"""

from pathlib import Path
import yaml
import re
from typing import Dict, List, Tuple, Optional


class PlanGovernanceValidator:
    """Validates planning documents against CORTEX governance standards."""
    
    def __init__(self, plan_path: Path):
        """Initialize validator with plan file path."""
        self.plan_path = plan_path
        self.plan_content = plan_path.read_text(encoding='utf-8')
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validation checks."""
        self.validate_phase_minus_one()
        self.validate_refactor_phase()
        self.validate_copilot_instructions()
        self.validate_knowledge_library_references()
        self.validate_micro_batch_strategy()
        
        passed = len(self.errors) == 0
        return passed, self.errors, self.warnings
    
    def validate_phase_minus_one(self):
        """Check for Phase -1 (Knowledge Library Consultation)."""
        phase_minus_one_patterns = [
            r'Phase -1:',
            r'Phase -1\.',
            r'###\s+Phase -1',
            r'Knowledge Library Consultation'
        ]
        
        found = any(re.search(pattern, self.plan_content) for pattern in phase_minus_one_patterns)
        
        if not found:
            self.errors.append(
                "❌ CRITICAL: Phase -1 (Knowledge Library Consultation) missing\n"
                "   SKULL Rule: KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT\n"
                "   Required: Query knowledge library before Phase 0\n"
                "   Fix: Add Phase -1 with 4-5 knowledge scan tasks\n"
                "   Reference: cortex-brain/brain-protection-rules.yaml:2485"
            )
    
    def validate_refactor_phase(self):
        """Check REFACTOR phase comprehensiveness (≥15 tasks)."""
        refactor_match = re.search(
            r'Phase (\d+):.*REFACTOR.*?(?=Phase \d+:|##\s+|$)',
            self.plan_content,
            re.DOTALL | re.IGNORECASE
        )
        
        if not refactor_match:
            self.errors.append(
                "❌ CRITICAL: REFACTOR phase missing\n"
                "   SKULL Rule: REFACTOR_CODE_CLEANUP_ENFORCEMENT\n"
                "   Required: Final phase for comprehensive code cleanup\n"
                "   Reference: cortex-brain/brain-protection-rules.yaml:319"
            )
            return
        
        refactor_section = refactor_match.group(0)
        
        # Count tasks (patterns like "#### 10.1:", "- 10.1:", "| 10.1 |")
        task_patterns = [
            r'####\s+\d+\.\d+:',  # Markdown headers
            r'^\s*-\s+\d+\.\d+:',  # List items
            r'^\|\s*\d+\.\d+\s*\|',  # Table rows
        ]
        
        task_count = 0
        for pattern in task_patterns:
            task_count += len(re.findall(pattern, refactor_section, re.MULTILINE))
        
        if task_count < 15:
            self.errors.append(
                f"❌ CRITICAL: REFACTOR phase incomplete ({task_count} tasks, need ≥15)\n"
                f"   SKULL Rule: REFACTOR_CODE_CLEANUP_ENFORCEMENT\n"
                f"   Required Categories (minimum tasks):\n"
                f"   - Orphaned code removal (3+ tasks)\n"
                f"   - Code duplication elimination (4+ tasks)\n"
                f"   - Dead code removal (3+ tasks)\n"
                f"   - Formatting standardization (3+ tasks)\n"
                f"   - Documentation cleanup (2+ tasks)\n"
                f"   Reference: cortex-brain/brain-protection-rules.yaml:319-418"
            )
        
        # Check for required categories
        required_categories = [
            ('orphaned code', r'orphaned.*code|unused.*code|dead.*functions'),
            ('duplication', r'duplicat|duplicate|consolidat|DRY'),
            ('dead code', r'dead.*code|commented.*code|TODO'),
            ('formatting', r'format|indent|style|prettier'),
            ('documentation', r'document|comment|accessibility')
        ]
        
        missing_categories = []
        for category_name, pattern in required_categories:
            if not re.search(pattern, refactor_section, re.IGNORECASE):
                missing_categories.append(category_name)
        
        if missing_categories:
            self.warnings.append(
                f"⚠️  WARNING: REFACTOR phase may be missing categories:\n"
                f"   Missing: {', '.join(missing_categories)}\n"
                f"   Verify all 5 categories are covered"
            )
    
    def validate_copilot_instructions(self):
        """Check copilot_instructions block completeness."""
        copilot_match = re.search(
            r'##\s+copilot_instructions(.*?)(?=\n##|\Z)',
            self.plan_content,
            re.DOTALL
        )
        
        if not copilot_match:
            self.warnings.append(
                "⚠️  WARNING: copilot_instructions block missing\n"
                "   Recommended: Add YAML block with governance reminders\n"
                "   Reference: response-templates-v4.yaml (autonomous_execution_progress)"
            )
            return
        
        copilot_block = copilot_match.group(1)
        
        required_fields = {
            'knowledge_library_consultation': 'Phase -1 enforcement',
            'knowledge_library_references': 'Knowledge library metadata',
            'refactor_comprehensiveness': 'REFACTOR phase validation',
            'micro_batch_size': 'Length limit prevention'
        }
        
        for field, purpose in required_fields.items():
            if field not in copilot_block:
                self.warnings.append(
                    f"⚠️  WARNING: copilot_instructions missing '{field}'\n"
                    f"   Purpose: {purpose}\n"
                    f"   Add to copilot_instructions YAML block"
                )
    
    def validate_knowledge_library_references(self):
        """Check for knowledge library references section."""
        kl_patterns = [
            r'Knowledge Library',
            r'knowledge_library',
            r'Phase -1',
            r'context/.*\.md'
        ]
        
        found = any(re.search(pattern, self.plan_content, re.IGNORECASE) 
                   for pattern in kl_patterns)
        
        if not found:
            self.errors.append(
                "❌ CRITICAL: Knowledge library references missing\n"
                "   SKULL Rule: KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT\n"
                "   Required: Document knowledge library consultation results\n"
                "   Example: '### 📚 Knowledge Library References' section\n"
                "   Or: Phase -1 with context/ outputs"
            )
    
    def validate_micro_batch_strategy(self):
        """Check for micro-batch strategy to prevent length limit errors."""
        batch_patterns = [
            r'micro.?batch',
            r'batch.*2-3.*files',
            r'2-3\s+files.*batch',
            r'prevent.*length.*limit',
            r'Sorry.*can\'t.*assist'
        ]
        
        found = any(re.search(pattern, self.plan_content, re.IGNORECASE) 
                   for pattern in batch_patterns)
        
        if not found:
            self.warnings.append(
                "⚠️  WARNING: Micro-batch strategy not documented\n"
                "   Purpose: Prevent 'Sorry, I can't assist' length limit errors\n"
                "   Recommended: Document 2-3 files per batch with validation gates\n"
                "   Reference: planning-governance-gap-analysis.md (line 34)"
            )


def calculate_compliance_score(errors: List[str], warnings: List[str]) -> float:
    """Calculate governance compliance score (0-10 scale)."""
    # Start at 10, deduct points for issues
    score = 10.0
    
    # Critical errors: -2.5 points each
    score -= len(errors) * 2.5
    
    # Warnings: -0.5 points each
    score -= len(warnings) * 0.5
    
    return max(0.0, score)


def format_validation_report(
    plan_path: Path,
    passed: bool,
    errors: List[str],
    warnings: List[str],
    score: float
) -> str:
    """Format validation results as readable report."""
    
    status_emoji = "✅" if passed else "❌"
    score_emoji = "✅" if score >= 8.0 else ("⚠️" if score >= 6.0 else "❌")
    
    report = f"""
{'='*70}
PLAN GOVERNANCE VALIDATION: {plan_path.name}
{'='*70}

Status: {status_emoji} {'PASSED' if passed else 'FAILED'}
Compliance Score: {score_emoji} {score:.1f}/10.0 (Threshold: ≥8.0)

"""
    
    if errors:
        report += "🔴 ERRORS (Must Fix):\n\n"
        for i, error in enumerate(errors, 1):
            report += f"{i}. {error}\n\n"
    
    if warnings:
        report += "🟡 WARNINGS (Should Fix):\n\n"
        for i, warning in enumerate(warnings, 1):
            report += f"{i}. {warning}\n\n"
    
    if passed and not warnings:
        report += "✅ All governance checks passed!\n"
        report += "   • Phase -1 (Knowledge Library Consultation) present\n"
        report += "   • Phase 10+ (Comprehensive REFACTOR) has ≥15 tasks\n"
        report += "   • copilot_instructions block complete\n"
        report += "   • Knowledge library references documented\n"
    
    report += f"\n{'='*70}\n"
    
    if not passed:
        report += f"\nFix {len(errors)} error(s) to meet governance standards.\n"
        report += "Reference: .asif/backlog/planning-governance-gap-analysis-2026-01-01.md\n"
    
    return report


def validate_plan(plan_path: str) -> int:
    """CLI entry point for plan validation."""
    plan = Path(plan_path)
    
    if not plan.exists():
        print(f"❌ Plan not found: {plan_path}")
        return 1
    
    if not plan.suffix == '.md':
        print(f"⚠️  Warning: Expected .md file, got {plan.suffix}")
    
    validator = PlanGovernanceValidator(plan)
    passed, errors, warnings = validator.validate_all()
    score = calculate_compliance_score(errors, warnings)
    
    report = format_validation_report(plan, passed, errors, warnings, score)
    
    # Use UTF-8 encoding for console output (Windows compatibility)
    import sys
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    print(report)
    
    return 0 if passed else 1


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python validate_plan_governance.py <plan_path>")
        print("\nExample:")
        print("  python validate_plan_governance.py cortex-brain/documents/planning/active/feature-x/00-master-plan.md")
        sys.exit(1)
    
    sys.exit(validate_plan(sys.argv[1]))
