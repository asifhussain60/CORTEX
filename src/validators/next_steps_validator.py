"""
Next Steps Formatting Validator

Validates "Next Steps" sections conform to CORTEX formatting standards:
- Simple Tasks: Numbered list (1, 2, 3)
- Complex Projects: Checkboxes with phases + "Ready to proceed" prompt
- Parallel Work: Track format + parallel indicators + choice prompt

Critical Rules Enforced:
- ❌ NEVER force singular choice when tasks can be done together
- ✅ ALWAYS use checkboxes for phases in complex work
- ✅ ALWAYS indicate parallel capability
- ✅ ALWAYS offer "all or specific" choice

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from enum import Enum


class NextStepsPattern(Enum):
    """Next Steps formatting patterns"""
    SIMPLE_TASKS = "simple_tasks"          # Numbered list (1, 2, 3)
    COMPLEX_PROJECTS = "complex_projects"  # Checkboxes with phases
    PARALLEL_WORK = "parallel_work"        # Track A/B/C format
    VIOLATION = "violation"                # Doesn't match any pattern


class NextStepsViolation:
    """Represents a Next Steps formatting violation"""
    
    def __init__(
        self,
        file_path: str,
        line_number: int,
        violation_type: str,
        detected_pattern: NextStepsPattern,
        expected_pattern: NextStepsPattern,
        actual_content: str,
        fix_suggestion: str
    ):
        self.file_path = file_path
        self.line_number = line_number
        self.violation_type = violation_type
        self.detected_pattern = detected_pattern
        self.expected_pattern = expected_pattern
        self.actual_content = actual_content
        self.fix_suggestion = fix_suggestion
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting"""
        return {
            "file": self.file_path,
            "line": self.line_number,
            "violation": self.violation_type,
            "detected_pattern": self.detected_pattern.value,
            "expected_pattern": self.expected_pattern.value,
            "actual_content": self.actual_content[:200],  # Truncate
            "fix_suggestion": self.fix_suggestion
        }


class NextStepsValidator:
    """
    Validates Next Steps formatting across CORTEX codebase.
    
    Patterns:
    1. Simple Tasks - Numbered list (1-5 items)
    2. Complex Projects - Checkboxes + phases + "Ready to proceed" prompt
    3. Parallel Work - Track A/B/C + parallel indicators + choice prompt
    """
    
    # Regex patterns for detection
    NEXT_STEPS_HEADER = re.compile(
        r'(?:🔍|\\U0001F50D)\s*\*?\*?Next Steps\*?\*?:?',
        re.IGNORECASE
    )
    
    # Simple tasks pattern: numbered list
    SIMPLE_TASK_PATTERN = re.compile(
        r'^\s*\d+\.\s+.+$',
        re.MULTILINE
    )
    
    # Complex projects pattern: checkbox
    CHECKBOX_PATTERN = re.compile(
        r'^\s*[☐☑✓✗]\s+Phase\s+\d+:',
        re.MULTILINE
    )
    
    # Parallel work pattern: Track A/B/C
    TRACK_PATTERN = re.compile(
        r'^\s*Track\s+[A-Z]:',
        re.MULTILINE
    )
    
    # Required prompts
    READY_PROMPT = re.compile(
        r'Ready to proceed with all (?:phases|tasks),?\s+or focus on a specific (?:phase|task)',
        re.IGNORECASE
    )
    
    PARALLEL_INDICATOR = re.compile(
        r'(?:These tracks are )?independent and can run in parallel',
        re.IGNORECASE
    )
    
    CHOICE_PROMPT = re.compile(
        r'Which track\(s\).+\(You can choose multiple or ALL\)',
        re.IGNORECASE
    )
    
    # Violation patterns
    FORCED_CHOICE = re.compile(
        r'(?:Choose|Select|Pick)\s+(?:one|1)(?:\s+of\s+the\s+following)?:',
        re.IGNORECASE
    )
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize validator.
        
        Args:
            project_root: Root directory of CORTEX project
        """
        self.project_root = project_root or Path.cwd()
        self.violations: List[NextStepsViolation] = []
    
    def validate_file(self, file_path: Path) -> List[NextStepsViolation]:
        """
        Validate Next Steps formatting in a single file.
        
        Args:
            file_path: Path to file to validate
        
        Returns:
            List of violations found
        """
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            # Skip files that can't be read
            return violations
        
        # Find all Next Steps sections
        for match in self.NEXT_STEPS_HEADER.finditer(content):
            start_pos = match.end()
            line_number = content[:start_pos].count('\n') + 1
            
            # Extract section content (next 500 chars or until next ## header)
            section_end = content.find('\n##', start_pos)
            if section_end == -1:
                section_end = start_pos + 500
            
            section_content = content[start_pos:section_end]
            
            # Detect pattern
            detected_pattern = self._detect_pattern(section_content)
            
            # Validate based on pattern
            section_violations = self._validate_section(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_number,
                section_content=section_content,
                detected_pattern=detected_pattern
            )
            
            violations.extend(section_violations)
        
        return violations
    
    def validate_directory(
        self,
        directory: Path,
        extensions: List[str] = ['.py', '.md']
    ) -> List[NextStepsViolation]:
        """
        Validate Next Steps formatting across directory.
        
        Args:
            directory: Directory to scan
            extensions: File extensions to check
        
        Returns:
            List of all violations found
        """
        violations = []
        
        for ext in extensions:
            for file_path in directory.rglob(f'*{ext}'):
                # Skip test files, archives, dist, publish
                if any(skip in str(file_path) for skip in [
                    '__pycache__', '.pytest_cache', 'archives',
                    'dist', 'publish', 'node_modules'
                ]):
                    continue
                
                file_violations = self.validate_file(file_path)
                violations.extend(file_violations)
        
        return violations
    
    def _detect_pattern(self, section_content: str) -> NextStepsPattern:
        """
        Detect which Next Steps pattern is used.
        
        Args:
            section_content: Content of Next Steps section
        
        Returns:
            Detected pattern type
        """
        # Check for checkbox pattern (Complex Projects)
        if self.CHECKBOX_PATTERN.search(section_content):
            return NextStepsPattern.COMPLEX_PROJECTS
        
        # Check for track pattern (Parallel Work)
        if self.TRACK_PATTERN.search(section_content):
            return NextStepsPattern.PARALLEL_WORK
        
        # Check for simple numbered list
        numbered_matches = self.SIMPLE_TASK_PATTERN.findall(section_content)
        if numbered_matches and len(numbered_matches) <= 5:
            return NextStepsPattern.SIMPLE_TASKS
        
        # Check for violations (numbered list in complex work)
        if numbered_matches and len(numbered_matches) > 5:
            return NextStepsPattern.VIOLATION
        
        return NextStepsPattern.VIOLATION
    
    def _validate_section(
        self,
        file_path: str,
        line_number: int,
        section_content: str,
        detected_pattern: NextStepsPattern
    ) -> List[NextStepsViolation]:
        """
        Validate a Next Steps section based on detected pattern.
        
        Args:
            file_path: File containing section
            line_number: Line number of section
            section_content: Section content
            detected_pattern: Detected pattern type
        
        Returns:
            List of violations
        """
        violations = []
        
        # Check for forced singular choice (always a violation)
        if self.FORCED_CHOICE.search(section_content):
            violations.append(NextStepsViolation(
                file_path=file_path,
                line_number=line_number,
                violation_type="FORCED_SINGULAR_CHOICE",
                detected_pattern=detected_pattern,
                expected_pattern=NextStepsPattern.PARALLEL_WORK,
                actual_content=section_content,
                fix_suggestion="Remove 'Choose one' language. Use 'Which track(s) shall I start with? (You can choose multiple or ALL)'"
            ))
        
        # Pattern-specific validations
        if detected_pattern == NextStepsPattern.COMPLEX_PROJECTS:
            violations.extend(self._validate_complex_project(
                file_path, line_number, section_content
            ))
        
        elif detected_pattern == NextStepsPattern.PARALLEL_WORK:
            violations.extend(self._validate_parallel_work(
                file_path, line_number, section_content
            ))
        
        elif detected_pattern == NextStepsPattern.SIMPLE_TASKS:
            # Simple tasks are valid if ≤5 items
            pass
        
        elif detected_pattern == NextStepsPattern.VIOLATION:
            # Check if it should be complex projects (>5 numbered items)
            numbered_matches = self.SIMPLE_TASK_PATTERN.findall(section_content)
            if len(numbered_matches) > 5:
                violations.append(NextStepsViolation(
                    file_path=file_path,
                    line_number=line_number,
                    violation_type="NUMBERED_LIST_IN_COMPLEX_WORK",
                    detected_pattern=NextStepsPattern.VIOLATION,
                    expected_pattern=NextStepsPattern.COMPLEX_PROJECTS,
                    actual_content=section_content,
                    fix_suggestion="Replace numbered list with checkboxes grouped into phases. Add 'Ready to proceed with all phases, or focus on a specific phase?' prompt."
                ))
        
        return violations
    
    def _validate_complex_project(
        self,
        file_path: str,
        line_number: int,
        section_content: str
    ) -> List[NextStepsViolation]:
        """Validate Complex Projects pattern"""
        violations = []
        
        # Check for "Ready to proceed" prompt
        if not self.READY_PROMPT.search(section_content):
            violations.append(NextStepsViolation(
                file_path=file_path,
                line_number=line_number,
                violation_type="MISSING_READY_PROMPT",
                detected_pattern=NextStepsPattern.COMPLEX_PROJECTS,
                expected_pattern=NextStepsPattern.COMPLEX_PROJECTS,
                actual_content=section_content,
                fix_suggestion="Add after checkboxes: 'Ready to proceed with all phases, or focus on a specific phase?'"
            ))
        
        return violations
    
    def _validate_parallel_work(
        self,
        file_path: str,
        line_number: int,
        section_content: str
    ) -> List[NextStepsViolation]:
        """Validate Parallel Work pattern"""
        violations = []
        
        # Check for parallel indicator
        if not self.PARALLEL_INDICATOR.search(section_content):
            violations.append(NextStepsViolation(
                file_path=file_path,
                line_number=line_number,
                violation_type="MISSING_PARALLEL_INDICATOR",
                detected_pattern=NextStepsPattern.PARALLEL_WORK,
                expected_pattern=NextStepsPattern.PARALLEL_WORK,
                actual_content=section_content,
                fix_suggestion="Add after tracks: 'These tracks are independent and can run in parallel.'"
            ))
        
        # Check for choice prompt
        if not self.CHOICE_PROMPT.search(section_content):
            violations.append(NextStepsViolation(
                file_path=file_path,
                line_number=line_number,
                violation_type="MISSING_CHOICE_PROMPT",
                detected_pattern=NextStepsPattern.PARALLEL_WORK,
                expected_pattern=NextStepsPattern.PARALLEL_WORK,
                actual_content=section_content,
                fix_suggestion="Add after parallel indicator: 'Which track(s) shall I start with? (You can choose multiple or ALL)'"
            ))
        
        return violations
    
    def generate_report(self, violations: List[NextStepsViolation]) -> str:
        """
        Generate human-readable violation report.
        
        Args:
            violations: List of violations
        
        Returns:
            Markdown-formatted report
        """
        if not violations:
            return "✅ No Next Steps formatting violations found!"
        
        report_lines = [
            "# Next Steps Formatting Violations Report",
            "",
            f"**Total Violations:** {len(violations)}",
            "",
            "## Violation Summary",
            ""
        ]
        
        # Group by violation type
        by_type: Dict[str, List[NextStepsViolation]] = {}
        for v in violations:
            if v.violation_type not in by_type:
                by_type[v.violation_type] = []
            by_type[v.violation_type].append(v)
        
        for vtype, vlist in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
            report_lines.append(f"### {vtype} ({len(vlist)} violations)")
            report_lines.append("")
            
            for v in vlist:
                report_lines.append(f"**{v.file_path}:{v.line_number}**")
                report_lines.append(f"- **Detected Pattern:** {v.detected_pattern.value}")
                report_lines.append(f"- **Expected Pattern:** {v.expected_pattern.value}")
                report_lines.append(f"- **Fix:** {v.fix_suggestion}")
                report_lines.append("")
        
        report_lines.extend([
            "",
            "## Pattern Reference",
            "",
            "### ✅ Pattern 1: Simple Tasks",
            "```markdown",
            "🔍 Next Steps:",
            "   1. First action",
            "   2. Second action",
            "   3. Third action",
            "```",
            "",
            "### ✅ Pattern 2: Complex Projects",
            "```markdown",
            "🔍 Next Steps:",
            "   ☐ Phase 1: Discovery (Tasks 1-3)",
            "   ☐ Phase 2: Implementation (Tasks 4-7)",
            "   ",
            "   Ready to proceed with all phases, or focus on a specific phase?",
            "```",
            "",
            "### ✅ Pattern 3: Parallel Work",
            "```markdown",
            "🔍 Next Steps:",
            "   Track A: Fix Python config (30 min)",
            "   Track B: Update documentation (45 min)",
            "   ",
            "   These tracks are independent and can run in parallel.",
            "   Which track(s) shall I start with? (You can choose multiple or ALL)",
            "```",
            "",
            "---",
            "",
            "**Reference:** `.github/prompts/modules/response-format.md`"
        ])
        
        return "\n".join(report_lines)


# Standalone CLI usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python next_steps_validator.py <project_root>")
        sys.exit(1)
    
    project_root = Path(sys.argv[1])
    validator = NextStepsValidator(project_root)
    
    print("🔍 Scanning for Next Steps violations...")
    violations = validator.validate_directory(project_root)
    
    print(f"\n✅ Scan complete: {len(violations)} violations found\n")
    
    if violations:
        report = validator.generate_report(violations)
        
        # Save report
        report_path = project_root / "cortex-brain" / "documents" / "reports" / "next-steps-violations.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Report saved to: {report_path}")
        print("\nFirst 10 violations:\n")
        for v in violations[:10]:
            print(f"  {v.file_path}:{v.line_number} - {v.violation_type}")
    
    sys.exit(0 if not violations else 1)
