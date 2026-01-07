#!/usr/bin/env python3
"""
CORTEX Design Validator

Validates documentation pages against glassmorphism-design-standards-v2.md:
- Logo sizes (200x200 for Level 1, 150x150 for Level 2)
- Footer presence/absence (NO footer on Level 1/2)
- Breadcrumb presence (required on Level 1/2)
- Panel spacing CSS variables
- Mobile responsiveness meta tags

Author: Asif Hussain
Version: 1.0.0

Reference: cortex-brain/documents/archive/glassmorphism-design-standards-v2.md
"""

import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from html.parser import HTMLParser


class ViewLevel(Enum):
    """Documentation view hierarchy levels."""
    HOME = "home"
    LEVEL1 = "level1"
    LEVEL2 = "level2"
    UNKNOWN = "unknown"


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    check_name: str
    passed: bool
    expected: str
    actual: str
    severity: str = "error"  # error, warning, info
    line_number: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "check": self.check_name,
            "passed": self.passed,
            "expected": self.expected,
            "actual": self.actual,
            "severity": self.severity,
            "line": self.line_number
        }


@dataclass
class PageValidation:
    """Validation results for a single page."""
    path: str
    level: ViewLevel
    results: List[ValidationResult] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results if r.severity == "error")
        
    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if not r.passed and r.severity == "error")
        
    @property
    def warning_count(self) -> int:
        return sum(1 for r in self.results if not r.passed and r.severity == "warning")
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "level": self.level.value,
            "passed": self.passed,
            "errors": self.error_count,
            "warnings": self.warning_count,
            "checks": [r.to_dict() for r in self.results]
        }


class HTMLStructureParser(HTMLParser):
    """Parse HTML to extract structural elements for validation."""
    
    def __init__(self):
        super().__init__()
        self.has_breadcrumb = False
        self.has_footer = False
        self.logo_sizes: List[Tuple[int, int]] = []
        self.has_viewport_meta = False
        self.css_variables: List[str] = []
        self.current_line = 1
        self.in_style = False
        self.style_content = ""
        self.in_footer = False
        self.footer_line: Optional[int] = None
        self.breadcrumb_line: Optional[int] = None
        
    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        attrs_dict = dict(attrs)
        class_attr = attrs_dict.get("class", "")
        
        # Check for breadcrumb
        if "breadcrumb" in class_attr.lower() or tag == "nav" and "breadcrumb" in class_attr.lower():
            self.has_breadcrumb = True
            self.breadcrumb_line = self.getpos()[0]
            
        # Check for footer
        if tag == "footer":
            self.has_footer = True
            self.in_footer = True
            self.footer_line = self.getpos()[0]
            
        # Check for logo images
        if tag == "img":
            src = attrs_dict.get("src", "")
            if "logo" in src.lower() or "cortex" in src.lower():
                width = attrs_dict.get("width", "")
                height = attrs_dict.get("height", "")
                if width and height:
                    try:
                        self.logo_sizes.append((int(width), int(height)))
                    except ValueError:
                        pass
                        
        # Check for viewport meta
        if tag == "meta" and attrs_dict.get("name") == "viewport":
            self.has_viewport_meta = True
            
        # Track style tags
        if tag == "style":
            self.in_style = True
            self.style_content = ""
            
    def handle_endtag(self, tag: str) -> None:
        if tag == "footer":
            self.in_footer = False
            
        if tag == "style":
            self.in_style = False
            # Extract CSS variables from style content
            self._extract_css_variables()
            
    def handle_data(self, data: str) -> None:
        if self.in_style:
            self.style_content += data
            
    def _extract_css_variables(self) -> None:
        """Extract --panel-gap-* CSS variables from style content."""
        pattern = r'--panel-gap-[a-z]+\s*:'
        matches = re.findall(pattern, self.style_content)
        self.css_variables.extend([m.rstrip(':').strip() for m in matches])


class DesignValidator:
    """
    Validates documentation pages against glassmorphism design standards.
    
    Design Standards Reference:
    - Home page: Footer YES, Breadcrumb NO
    - Level 1: Logo 200x200, Footer NO, Breadcrumb YES
    - Level 2: Logo 150x150, Footer NO, Breadcrumb YES
    """
    
    # Expected CSS panel spacing variables
    EXPECTED_CSS_VARS = [
        "--panel-gap-xs",
        "--panel-gap-sm",
        "--panel-gap-md",
        "--panel-gap-lg",
        "--panel-gap-xl"
    ]
    
    # Logo size requirements by level
    LOGO_SIZES = {
        ViewLevel.HOME: None,  # No specific requirement
        ViewLevel.LEVEL1: (200, 200),
        ViewLevel.LEVEL2: (150, 150)
    }
    
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.docs_dir = project_root / "docs"
        
    def determine_level(self, html_path: Path) -> ViewLevel:
        """
        Determine the view level of a page based on its path.
        
        Rules:
        - docs/index.html → HOME
        - docs/{section}/index.html → LEVEL1
        - docs/{section}/{page}.html → LEVEL2
        """
        try:
            rel_path = html_path.relative_to(self.docs_dir)
        except ValueError:
            return ViewLevel.UNKNOWN
            
        parts = rel_path.parts
        
        if len(parts) == 1 and parts[0] == "index.html":
            return ViewLevel.HOME
        elif len(parts) == 2 and parts[1] == "index.html":
            return ViewLevel.LEVEL1
        elif len(parts) == 2 and parts[1].endswith(".html"):
            return ViewLevel.LEVEL2
        elif len(parts) >= 3:
            # Deeper nesting - treat as Level 2 but flag as potential violation
            return ViewLevel.LEVEL2
            
        return ViewLevel.UNKNOWN
        
    def validate_page(self, html_path: Path) -> PageValidation:
        """
        Validate a single HTML page against design standards.
        
        Args:
            html_path: Path to the HTML file
            
        Returns:
            PageValidation with all check results
        """
        level = self.determine_level(html_path)
        rel_path = str(html_path.relative_to(self.docs_dir)) if self.docs_dir in html_path.parents or html_path.parent == self.docs_dir else str(html_path)
        
        validation = PageValidation(path=rel_path, level=level)
        
        # Read and parse HTML
        try:
            content = html_path.read_text(encoding="utf-8")
        except Exception as e:
            validation.results.append(ValidationResult(
                check_name="file_readable",
                passed=False,
                expected="Readable HTML file",
                actual=f"Error: {e}",
                severity="error"
            ))
            return validation
            
        parser = HTMLStructureParser()
        try:
            parser.feed(content)
        except Exception as e:
            validation.results.append(ValidationResult(
                check_name="html_valid",
                passed=False,
                expected="Valid HTML",
                actual=f"Parse error: {e}",
                severity="error"
            ))
            return validation
            
        # Run validation checks based on level
        validation.results.extend(self._check_logo_size(parser, level))
        validation.results.extend(self._check_footer(parser, level))
        validation.results.extend(self._check_breadcrumb(parser, level))
        validation.results.extend(self._check_viewport(parser))
        validation.results.extend(self._check_css_variables(parser, level))
        validation.results.extend(self._check_hierarchy_depth(html_path))
        
        return validation
        
    def _check_logo_size(self, parser: HTMLStructureParser, level: ViewLevel) -> List[ValidationResult]:
        """Check logo size matches level requirements."""
        results = []
        expected_size = self.LOGO_SIZES.get(level)
        
        if expected_size is None:
            # No logo size requirement for home page
            return results
            
        if not parser.logo_sizes:
            results.append(ValidationResult(
                check_name="logo_present",
                passed=False,
                expected=f"Logo with size {expected_size[0]}x{expected_size[1]}",
                actual="No logo found with explicit dimensions",
                severity="warning"
            ))
        else:
            # Check if any logo matches expected size
            matched = any(size == expected_size for size in parser.logo_sizes)
            
            results.append(ValidationResult(
                check_name="logo_size",
                passed=matched,
                expected=f"{expected_size[0]}x{expected_size[1]}",
                actual=str(parser.logo_sizes[0]) if parser.logo_sizes else "None",
                severity="error" if not matched else "info"
            ))
            
        return results
        
    def _check_footer(self, parser: HTMLStructureParser, level: ViewLevel) -> List[ValidationResult]:
        """Check footer presence/absence based on level."""
        results = []
        
        # Home page should have footer, Level 1/2 should NOT
        if level == ViewLevel.HOME:
            results.append(ValidationResult(
                check_name="footer_presence",
                passed=parser.has_footer,
                expected="Footer present (home page)",
                actual="Footer found" if parser.has_footer else "No footer",
                severity="warning" if not parser.has_footer else "info",
                line_number=parser.footer_line
            ))
        else:
            # Level 1 and Level 2 should NOT have footer
            results.append(ValidationResult(
                check_name="footer_absence",
                passed=not parser.has_footer,
                expected="No footer (breadcrumbs provide navigation)",
                actual="Footer found" if parser.has_footer else "No footer",
                severity="error" if parser.has_footer else "info",
                line_number=parser.footer_line
            ))
            
        return results
        
    def _check_breadcrumb(self, parser: HTMLStructureParser, level: ViewLevel) -> List[ValidationResult]:
        """Check breadcrumb presence based on level."""
        results = []
        
        # Home page should NOT have breadcrumb, Level 1/2 should
        if level == ViewLevel.HOME:
            results.append(ValidationResult(
                check_name="breadcrumb_absence",
                passed=not parser.has_breadcrumb,
                expected="No breadcrumb (home page)",
                actual="Breadcrumb found" if parser.has_breadcrumb else "No breadcrumb",
                severity="warning" if parser.has_breadcrumb else "info",
                line_number=parser.breadcrumb_line
            ))
        else:
            results.append(ValidationResult(
                check_name="breadcrumb_presence",
                passed=parser.has_breadcrumb,
                expected="Breadcrumb present (required for navigation)",
                actual="Breadcrumb found" if parser.has_breadcrumb else "No breadcrumb",
                severity="error" if not parser.has_breadcrumb else "info",
                line_number=parser.breadcrumb_line
            ))
            
        return results
        
    def _check_viewport(self, parser: HTMLStructureParser) -> List[ValidationResult]:
        """Check for mobile viewport meta tag."""
        return [ValidationResult(
            check_name="viewport_meta",
            passed=parser.has_viewport_meta,
            expected="<meta name=\"viewport\" ...>",
            actual="Found" if parser.has_viewport_meta else "Missing",
            severity="warning" if not parser.has_viewport_meta else "info"
        )]
        
    def _check_css_variables(self, parser: HTMLStructureParser, level: ViewLevel) -> List[ValidationResult]:
        """Check for panel spacing CSS variables (optional for home)."""
        if level == ViewLevel.HOME:
            return []  # Not required for home page
            
        found_vars = set(parser.css_variables)
        expected_vars = set(self.EXPECTED_CSS_VARS)
        
        # Check if at least some spacing variables are used
        has_spacing = bool(found_vars & expected_vars)
        
        return [ValidationResult(
            check_name="panel_spacing_vars",
            passed=has_spacing,
            expected="Panel spacing CSS variables (--panel-gap-*)",
            actual=f"Found: {list(found_vars)}" if found_vars else "None found",
            severity="warning" if not has_spacing else "info"
        )]
        
    def _check_hierarchy_depth(self, html_path: Path) -> List[ValidationResult]:
        """Check that page doesn't exceed 2-level hierarchy."""
        try:
            rel_path = html_path.relative_to(self.docs_dir)
        except ValueError:
            return []
            
        depth = len(rel_path.parts)
        
        # Maximum depth is 2 (section/page.html)
        if depth > 2:
            return [ValidationResult(
                check_name="hierarchy_depth",
                passed=False,
                expected="Maximum 2 levels (section/page.html)",
                actual=f"Depth: {depth} ({rel_path})",
                severity="error"
            )]
            
        return [ValidationResult(
            check_name="hierarchy_depth",
            passed=True,
            expected="Maximum 2 levels",
            actual=f"Depth: {depth}",
            severity="info"
        )]
        
    def validate_directory(self, path: Optional[Path] = None) -> List[PageValidation]:
        """
        Validate all HTML files in a directory.
        
        Args:
            path: Directory to validate (default: docs/)
            
        Returns:
            List of PageValidation results
        """
        if path is None:
            path = self.docs_dir
            
        results = []
        
        for html_file in path.rglob("*.html"):
            validation = self.validate_page(html_file)
            results.append(validation)
            
        return results
        
    def generate_report(self, validations: List[PageValidation]) -> Dict[str, Any]:
        """Generate a validation report."""
        total_pages = len(validations)
        passed_pages = sum(1 for v in validations if v.passed)
        total_errors = sum(v.error_count for v in validations)
        total_warnings = sum(v.warning_count for v in validations)
        
        return {
            "version": "1.0",
            "generated": datetime.now().isoformat(),
            "generator": "design_validator.py",
            "summary": {
                "total_pages": total_pages,
                "passed_pages": passed_pages,
                "failed_pages": total_pages - passed_pages,
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "pass_rate": f"{(passed_pages / total_pages * 100):.1f}%" if total_pages > 0 else "N/A"
            },
            "pages": [v.to_dict() for v in validations]
        }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX Design Validator - Validate glassmorphism design standards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --path docs/
  %(prog)s --path docs/orchestrators/index.html --level 1
  %(prog)s --path docs/ --format json --output report.json
        """
    )
    
    parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="Path to HTML file or directory to validate"
    )
    
    parser.add_argument(
        "--level",
        type=int,
        choices=[1, 2],
        help="Override view level (1 or 2) - for single file validation"
    )
    
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (default: stdout)"
    )
    
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)"
    )
    
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error if any warnings found"
    )
    
    args = parser.parse_args()
    
    # Find project root
    project_root = args.project_root
    if not (project_root / "docs").exists():
        current = Path.cwd()
        while current != current.parent:
            if (current / "cortex-brain").exists():
                project_root = current
                break
            current = current.parent
                
    validator = DesignValidator(project_root)
    
    # Validate
    if args.path.is_file():
        validations = [validator.validate_page(args.path)]
    else:
        validations = validator.validate_directory(args.path)
        
    report = validator.generate_report(validations)
    
    # Output
    if args.format == "json":
        output = json.dumps(report, indent=2)
    else:
        # Text format
        lines = [
            "=" * 60,
            "CORTEX Design Validator Report",
            "=" * 60,
            f"\nGenerated: {report['generated']}",
            f"\nSummary:",
            f"  Total Pages: {report['summary']['total_pages']}",
            f"  Passed: {report['summary']['passed_pages']}",
            f"  Failed: {report['summary']['failed_pages']}",
            f"  Errors: {report['summary']['total_errors']}",
            f"  Warnings: {report['summary']['total_warnings']}",
            f"  Pass Rate: {report['summary']['pass_rate']}",
            ""
        ]
        
        for page in report["pages"]:
            status = "✅" if page["passed"] else "❌"
            lines.append(f"\n{status} {page['path']} (Level: {page['level']})")
            
            for check in page["checks"]:
                if not check["passed"]:
                    icon = "🔴" if check["severity"] == "error" else "🟡"
                    lines.append(f"  {icon} {check['check']}: Expected '{check['expected']}', got '{check['actual']}'")
                    
        output = "\n".join(lines)
        
    # Write output
    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"Report saved to: {args.output}")
    else:
        print(output)
        
    # Exit code
    if report["summary"]["total_errors"] > 0:
        sys.exit(1)
    elif args.strict and report["summary"]["total_warnings"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
