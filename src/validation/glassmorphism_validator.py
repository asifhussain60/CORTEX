"""
Glassmorphism Design Standard Validator
Enforces glassmorphism-design-standard.md v4.0.0 compliance across all HTML views.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import html.parser


class ViewLevel(Enum):
    """View hierarchy levels."""
    LEVEL_0 = "Level 0"  # Home page (docs/index.html)
    LEVEL_1 = "Level 1"  # Hub pages (13 expected)
    LEVEL_2 = "Level 2"  # Detail pages (137 expected)
    LEVEL_3 = "Level 3"  # FORBIDDEN
    UNKNOWN = "Unknown"


class ValidationSeverity(Enum):
    """Validation error severity levels."""
    CRITICAL = "CRITICAL"  # Blocks deployment
    ERROR = "ERROR"       # Must fix before commit
    WARNING = "WARNING"   # Should fix, not blocking
    INFO = "INFO"         # Informational only


@dataclass
class ValidationIssue:
    """Single validation issue."""
    severity: ValidationSeverity
    rule_id: str
    rule_name: str
    file_path: Path
    line_number: Optional[int]
    message: str
    fix_suggestion: Optional[str] = None


@dataclass
class ValidationReport:
    """Comprehensive validation report."""
    total_files_scanned: int = 0
    passed_files: int = 0
    failed_files: int = 0
    
    issues: List[ValidationIssue] = field(default_factory=list)
    
    # Rule-specific counters
    inline_style_count: int = 0
    level3_link_count: int = 0
    missing_header_count: int = 0
    missing_footer_count: int = 0
    t3_animation_violations: int = 0
    
    # File categorization
    level0_files: List[Path] = field(default_factory=list)
    level1_files: List[Path] = field(default_factory=list)
    level2_files: List[Path] = field(default_factory=list)
    level3_files: List[Path] = field(default_factory=list)  # Should be empty!
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no CRITICAL or ERROR issues)."""
        return not any(
            issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]
            for issue in self.issues
        )
    
    @property
    def critical_count(self) -> int:
        """Count of CRITICAL issues."""
        return sum(1 for issue in self.issues if issue.severity == ValidationSeverity.CRITICAL)
    
    @property
    def error_count(self) -> int:
        """Count of ERROR issues."""
        return sum(1 for issue in self.issues if issue.severity == ValidationSeverity.ERROR)
    
    @property
    def warning_count(self) -> int:
        """Count of WARNING issues."""
        return sum(1 for issue in self.issues if issue.severity == ValidationSeverity.WARNING)


class HTMLStructureParser(html.parser.HTMLParser):
    """Parse HTML to extract structural information."""
    
    def __init__(self):
        super().__init__()
        self.has_header = False
        self.has_footer = False
        self.inline_styles: List[Tuple[int, str]] = []
        self.level3_links: List[Tuple[int, str]] = []
        self.t3_animations: List[Tuple[int, str]] = []
        self.current_line = 1
        
    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]):
        """Handle opening tags."""
        attrs_dict = dict(attrs)
        
        # Check for header
        if tag == "header" and attrs_dict.get("class", "").find("glass-header") >= 0:
            self.has_header = True
        
        # Check for footer
        if tag == "footer" and attrs_dict.get("class", "").find("glass-footer") >= 0:
            self.has_footer = True
        
        # Check for inline styles
        if "style" in attrs_dict:
            self.inline_styles.append((self.current_line, attrs_dict["style"]))
        
        # Check for Level 3 navigation (detect deep nesting patterns)
        if tag == "a":
            href = attrs_dict.get("href", "")
            # Pattern: /domain/category/subcategory/detail.html (too deep)
            if href.count("/") > 3 and not href.startswith("http"):
                self.level3_links.append((self.current_line, href))
        
        # Check for T3 dramatic animations in class names
        class_attr = attrs_dict.get("class", "")
        if any(anim in class_attr for anim in [
            "borderGlowSweep", "blobMorph", "lightLeakPrimary", 
            "glowPulse", "dramatic-", "hero-animation"
        ]):
            self.t3_animations.append((self.current_line, class_attr))


class GlassmorphismValidator:
    """
    Validates HTML files against glassmorphism-design-standard.md v4.0.0.
    
    Enforces:
    1. NO inline styles (style="" attributes)
    2. NO Level 3 navigation links
    3. Standardized header/footer on appropriate levels
    4. T1 animations only (except Level 0 hero)
    5. Production-ready file naming (no *-new.html, *-v2.html)
    6. Responsive breakpoints present
    """
    
    LEVEL_0_PATTERN = re.compile(r"docs[/\\]index\.html$")
    LEVEL_1_PATTERN = re.compile(r"docs[/\\][\w-]+[/\\]index\.html$")
    LEVEL_2_PATTERN = re.compile(r"docs[/\\][\w-]+[/\\][\w-]+\.html$")
    LEVEL_3_PATTERN = re.compile(r"docs[/\\][\w-]+[/\\][\w-]+[/\\][\w-]+\.html$")
    
    # Forbidden file name patterns
    FORBIDDEN_PATTERNS = [
        r"-new\.html$", r"-v\d+\.html$", r"-backup\.html$",
        r"-old\.html$", r"-temp\.html$", r"-test\.html$",
        r"-draft\.html$", r"-enhanced\.html$", r"-updated\.html$"
    ]
    
    def __init__(self, docs_root: Path):
        """
        Initialize validator.
        
        Args:
            docs_root: Path to docs/ directory
        """
        self.docs_root = Path(docs_root)
        self.report = ValidationReport()
    
    def classify_view_level(self, file_path: Path) -> ViewLevel:
        """Determine view hierarchy level from file path."""
        path_str = str(file_path).replace("\\", "/")
        
        if self.LEVEL_0_PATTERN.search(path_str):
            return ViewLevel.LEVEL_0
        elif self.LEVEL_1_PATTERN.search(path_str):
            return ViewLevel.LEVEL_1
        elif self.LEVEL_2_PATTERN.search(path_str):
            return ViewLevel.LEVEL_2
        elif self.LEVEL_3_PATTERN.search(path_str):
            return ViewLevel.LEVEL_3
        else:
            return ViewLevel.UNKNOWN
    
    def validate_file_naming(self, file_path: Path) -> List[ValidationIssue]:
        """
        RULE: PRODUCTION_FILE_NAMING
        Ensure no temporary/versioned file names exist.
        """
        issues = []
        file_name = file_path.name
        
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, file_name):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    rule_id="PRODUCTION_FILE_NAMING",
                    rule_name="Production File Naming",
                    file_path=file_path,
                    line_number=None,
                    message=f"Forbidden file name pattern: {file_name}",
                    fix_suggestion=(
                        f"Rename to production name (e.g., {file_name.split('-')[0]}.html). "
                        "Delete old file and use SAME production name."
                    )
                ))
        
        return issues
    
    def validate_inline_styles(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """
        RULE: NO_INLINE_STYLES
        Ensure ZERO inline style="" attributes exist.
        """
        issues = []
        
        # Pattern 1: Standard style="" attribute
        pattern1 = re.compile(r'\bstyle\s*=\s*["\']', re.IGNORECASE)
        
        for line_num, line in enumerate(content.splitlines(), start=1):
            if pattern1.search(line):
                self.report.inline_style_count += 1
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    rule_id="NO_INLINE_STYLES",
                    rule_name="No Inline Styles",
                    file_path=file_path,
                    line_number=line_num,
                    message=f"Inline style attribute found: {line.strip()[:100]}",
                    fix_suggestion=(
                        "Extract to CSS class in glassmorphism.css. "
                        "Use existing utility classes or create new semantic class."
                    )
                ))
        
        return issues
    
    def validate_header_footer(
        self, 
        file_path: Path, 
        level: ViewLevel,
        parser: HTMLStructureParser
    ) -> List[ValidationIssue]:
        """
        RULE: HEADER_FOOTER_STANDARD
        Ensure proper header/footer based on view level.
        
        - Level 0: Footer required, header NOT required
        - Level 1: Header AND footer required
        - Level 2: Header AND footer required
        """
        issues = []
        
        if level == ViewLevel.LEVEL_0:
            if not parser.has_footer:
                self.report.missing_footer_count += 1
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    rule_id="HEADER_FOOTER_STANDARD",
                    rule_name="Header/Footer Standardization",
                    file_path=file_path,
                    line_number=None,
                    message="Level 0 missing standardized footer (header not required)",
                    fix_suggestion="Add <footer class='glass-footer'> from glassmorphism-design-standard.md"
                ))
        
        elif level in [ViewLevel.LEVEL_1, ViewLevel.LEVEL_2]:
            if not parser.has_header:
                self.report.missing_header_count += 1
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    rule_id="HEADER_FOOTER_STANDARD",
                    rule_name="Header/Footer Standardization",
                    file_path=file_path,
                    line_number=None,
                    message=f"{level.value} missing standardized header",
                    fix_suggestion="Add <header class='glass-header'> from glassmorphism-design-standard.md"
                ))
            
            if not parser.has_footer:
                self.report.missing_footer_count += 1
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    rule_id="HEADER_FOOTER_STANDARD",
                    rule_name="Header/Footer Standardization",
                    file_path=file_path,
                    line_number=None,
                    message=f"{level.value} missing standardized footer",
                    fix_suggestion="Add <footer class='glass-footer'> from glassmorphism-design-standard.md"
                ))
        
        return issues
    
    def validate_level3_prohibition(
        self, 
        file_path: Path,
        level: ViewLevel,
        parser: HTMLStructureParser
    ) -> List[ValidationIssue]:
        """
        RULE: NO_LEVEL_3
        Ensure NO Level 3 navigation exists. All navigation stops at Level 2.
        """
        issues = []
        
        # Check if file itself is Level 3 (FORBIDDEN)
        if level == ViewLevel.LEVEL_3:
            self.report.level3_link_count += 1
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                rule_id="NO_LEVEL_3",
                rule_name="No Level 3 Views",
                file_path=file_path,
                line_number=None,
                message="Level 3 view detected - FORBIDDEN by design standard",
                fix_suggestion=(
                    "Consolidate content into parent Level 2 page using tabs/accordions. "
                    "Delete this Level 3 file."
                )
            ))
        
        # Check for links pointing to Level 3 paths
        for line_num, href in parser.level3_links:
            self.report.level3_link_count += 1
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                rule_id="NO_LEVEL_3",
                rule_name="No Level 3 Navigation",
                file_path=file_path,
                line_number=line_num,
                message=f"Level 3 navigation link detected: {href}",
                fix_suggestion="Remove link or consolidate target into Level 2 page with tabs/accordions"
            ))
        
        return issues
    
    def validate_animation_tier(
        self,
        file_path: Path,
        level: ViewLevel,
        content: str,
        parser: HTMLStructureParser
    ) -> List[ValidationIssue]:
        """
        RULE: T1_ANIMATIONS_ONLY
        Ensure only T1 (subtle) animations on Level 1 & Level 2.
        T3 dramatic animations ONLY allowed on Level 0 hero.
        """
        issues = []
        
        # T3 dramatic animations forbidden on Level 1 & Level 2
        if level in [ViewLevel.LEVEL_1, ViewLevel.LEVEL_2]:
            # Check CSS for T3 keyframes
            t3_keyframes = [
                "borderGlowSweep", "blobMorph", "lightLeakPrimary",
                "glowPulse", "particleFloat", "waveDistortion"
            ]
            
            for line_num, line in enumerate(content.splitlines(), start=1):
                for keyframe in t3_keyframes:
                    if keyframe in line:
                        self.report.t3_animation_violations += 1
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            rule_id="T1_ANIMATIONS_ONLY",
                            rule_name="T1 Subtle Animations Only",
                            file_path=file_path,
                            line_number=line_num,
                            message=f"T3 dramatic animation '{keyframe}' forbidden on {level.value}",
                            fix_suggestion=(
                                "Replace with T1 subtle animation (0.2-0.3s transitions). "
                                "See glassmorphism-design-standard.md T1 section."
                            )
                        ))
            
            # Check HTML for T3 animation classes
            for line_num, class_attr in parser.t3_animations:
                self.report.t3_animation_violations += 1
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    rule_id="T1_ANIMATIONS_ONLY",
                    rule_name="T1 Subtle Animations Only",
                    file_path=file_path,
                    line_number=line_num,
                    message=f"T3 animation class found on {level.value}: {class_attr}",
                    fix_suggestion="Remove T3 animation classes, use T1 transition classes"
                ))
        
        return issues
    
    def validate_responsive_breakpoints(
        self,
        file_path: Path,
        content: str
    ) -> List[ValidationIssue]:
        """
        RULE: RESPONSIVE_MANDATORY
        Ensure responsive breakpoints (375px, 768px, 1440px) are present.
        """
        issues = []
        
        # Check for media queries
        has_mobile = bool(re.search(r'@media.*\(.*width.*375px\)', content, re.IGNORECASE))
        has_tablet = bool(re.search(r'@media.*\(.*width.*768px\)', content, re.IGNORECASE))
        has_desktop = bool(re.search(r'@media.*\(.*width.*1440px\)', content, re.IGNORECASE))
        
        # Also check for linked CSS (glassmorphism.css should have breakpoints)
        has_glass_css = "glassmorphism.css" in content
        
        if not (has_mobile or has_tablet or has_desktop or has_glass_css):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                rule_id="RESPONSIVE_MANDATORY",
                rule_name="Responsive Breakpoints Required",
                file_path=file_path,
                line_number=None,
                message="No responsive breakpoints detected (375px, 768px, 1440px)",
                fix_suggestion=(
                    "Link glassmorphism.css or add media queries for mobile/tablet/desktop. "
                    "See glassmorphism-design-standard.md responsive section."
                )
            ))
        
        return issues
    
    def validate_file(self, file_path: Path) -> List[ValidationIssue]:
        """Validate a single HTML file against all rules."""
        issues = []
        
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                rule_id="FILE_READ_ERROR",
                rule_name="File Read Error",
                file_path=file_path,
                line_number=None,
                message=f"Failed to read file: {e}",
                fix_suggestion="Check file permissions and encoding"
            ))
            return issues
        
        # Classify view level
        level = self.classify_view_level(file_path)
        
        # Categorize file
        if level == ViewLevel.LEVEL_0:
            self.report.level0_files.append(file_path)
        elif level == ViewLevel.LEVEL_1:
            self.report.level1_files.append(file_path)
        elif level == ViewLevel.LEVEL_2:
            self.report.level2_files.append(file_path)
        elif level == ViewLevel.LEVEL_3:
            self.report.level3_files.append(file_path)
        
        # Parse HTML structure
        parser = HTMLStructureParser()
        try:
            parser.feed(content)
        except Exception as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                rule_id="HTML_PARSE_ERROR",
                rule_name="HTML Parse Error",
                file_path=file_path,
                line_number=None,
                message=f"Failed to parse HTML: {e}",
                fix_suggestion="Check HTML syntax"
            ))
        
        # Run all validation rules
        issues.extend(self.validate_file_naming(file_path))
        issues.extend(self.validate_inline_styles(file_path, content))
        issues.extend(self.validate_header_footer(file_path, level, parser))
        issues.extend(self.validate_level3_prohibition(file_path, level, parser))
        issues.extend(self.validate_animation_tier(file_path, level, content, parser))
        issues.extend(self.validate_responsive_breakpoints(file_path, content))
        
        return issues
    
    def validate_all(self) -> ValidationReport:
        """
        Validate all HTML files in docs/ directory.
        
        Returns:
            ValidationReport with all issues found
        """
        html_files = list(self.docs_root.rglob("*.html"))
        self.report.total_files_scanned = len(html_files)
        
        for file_path in html_files:
            issues = self.validate_file(file_path)
            self.report.issues.extend(issues)
            
            if issues:
                self.report.failed_files += 1
            else:
                self.report.passed_files += 1
        
        return self.report
    
    def generate_report_markdown(self) -> str:
        """Generate human-readable markdown report."""
        lines = [
            "# 🎨 Glassmorphism Design Standard Validation Report",
            "",
            f"**Generated:** {Path.cwd()}",
            f"**Docs Root:** {self.docs_root}",
            f"**Standard Version:** glassmorphism-design-standard.md v4.0.0",
            "",
            "---",
            "",
            "## 📊 Summary",
            "",
            f"- **Total Files Scanned:** {self.report.total_files_scanned}",
            f"- **Passed:** {self.report.passed_files} ✅",
            f"- **Failed:** {self.report.failed_files} ❌",
            f"- **Overall Status:** {'✅ PASS' if self.report.is_valid else '❌ FAIL'}",
            "",
            "### Issue Counts by Severity",
            "",
            f"- **CRITICAL:** {self.report.critical_count} 🔴",
            f"- **ERROR:** {self.report.error_count} 🟠",
            f"- **WARNING:** {self.report.warning_count} 🟡",
            f"- **INFO:** {len([i for i in self.report.issues if i.severity == ValidationSeverity.INFO])} 🔵",
            "",
            "### Rule Violation Summary",
            "",
            f"- **Inline Styles (style=\"\"):** {self.report.inline_style_count}",
            f"- **Level 3 Navigation:** {self.report.level3_link_count}",
            f"- **Missing Headers:** {self.report.missing_header_count}",
            f"- **Missing Footers:** {self.report.missing_footer_count}",
            f"- **T3 Animation Violations:** {self.report.t3_animation_violations}",
            "",
            "### View Hierarchy Breakdown",
            "",
            f"- **Level 0 (Home):** {len(self.report.level0_files)} files",
            f"- **Level 1 (Hubs):** {len(self.report.level1_files)} files (expected: 13)",
            f"- **Level 2 (Details):** {len(self.report.level2_files)} files (expected: 137)",
            f"- **Level 3 (FORBIDDEN):** {len(self.report.level3_files)} files ⚠️",
            "",
        ]
        
        if self.report.level3_files:
            lines.extend([
                "#### ⛔ Level 3 Files Detected (MUST BE CONSOLIDATED)",
                "",
            ])
            for file_path in self.report.level3_files:
                lines.append(f"- `{file_path}`")
            lines.append("")
        
        # Group issues by severity
        if self.report.issues:
            lines.extend([
                "---",
                "",
                "## 🔍 Detailed Issues",
                "",
            ])
            
            for severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR, 
                           ValidationSeverity.WARNING, ValidationSeverity.INFO]:
                severity_issues = [i for i in self.report.issues if i.severity == severity]
                
                if severity_issues:
                    emoji = {"CRITICAL": "🔴", "ERROR": "🟠", "WARNING": "🟡", "INFO": "🔵"}
                    lines.extend([
                        f"### {emoji[severity.value]} {severity.value} Issues ({len(severity_issues)})",
                        "",
                    ])
                    
                    # Group by rule_id
                    by_rule: Dict[str, List[ValidationIssue]] = {}
                    for issue in severity_issues:
                        by_rule.setdefault(issue.rule_id, []).append(issue)
                    
                    for rule_id, rule_issues in by_rule.items():
                        lines.extend([
                            f"#### {rule_issues[0].rule_name} ({len(rule_issues)} occurrences)",
                            "",
                        ])
                        
                        for issue in rule_issues[:10]:  # Limit to first 10
                            line_ref = f" (line {issue.line_number})" if issue.line_number else ""
                            lines.append(f"- **File:** `{issue.file_path}`{line_ref}")
                            lines.append(f"  - **Issue:** {issue.message}")
                            if issue.fix_suggestion:
                                lines.append(f"  - **Fix:** {issue.fix_suggestion}")
                            lines.append("")
                        
                        if len(rule_issues) > 10:
                            lines.append(f"*... and {len(rule_issues) - 10} more*")
                            lines.append("")
        else:
            lines.extend([
                "---",
                "",
                "## ✅ All Checks Passed",
                "",
                "No issues detected. All files comply with glassmorphism-design-standard.md v4.0.0.",
                "",
            ])
        
        lines.extend([
            "---",
            "",
            "## 📖 Reference",
            "",
            "- **Design Standard:** `cortex-brain/documents/standards/glassmorphism-design-standard.md` v4.0.0",
            "- **Master Plan:** `cortex-brain/documents/planning/active/level-2-glassmorphism-standardization/00-master-plan.md`",
            "- **Validator:** `src/validation/glassmorphism_validator.py` v1.0.0",
            "",
        ])
        
        return "\n".join(lines)


def main():
    """CLI entry point."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate HTML files against glassmorphism-design-standard.md v4.0.0"
    )
    parser.add_argument(
        "docs_root",
        type=Path,
        nargs="?",
        default=Path("docs"),
        help="Path to docs/ directory (default: docs)"
    )
    parser.add_argument(
        "--report-file",
        type=Path,
        help="Output report to file (markdown)"
    )
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Exit with error code if warnings present"
    )
    
    args = parser.parse_args()
    
    # Run validation
    validator = GlassmorphismValidator(args.docs_root)
    report = validator.validate_all()
    
    # Generate report
    markdown_report = validator.generate_report_markdown()
    
    # Output
    if args.report_file:
        args.report_file.write_text(markdown_report, encoding="utf-8")
        print(f"✅ Report written to: {args.report_file}")
    else:
        print(markdown_report)
    
    # Exit code
    if not report.is_valid:
        sys.exit(1)
    elif args.fail_on_warnings and report.warning_count > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
