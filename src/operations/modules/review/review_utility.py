"""
Code Review Utility

Fast, lightweight code review management.
Replaces heavy orchestrator (1,029 lines) with focused utility (~600 lines).

Core Operations:
- Create review session
- Analyze file/changes
- Generate review report
- Check quality metrics
- List reviews

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import yaml
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import CORTEX config
try:
    from src.config import config
    CORTEX_ROOT = Path(config.root_path)
except ImportError:
    CORTEX_ROOT = Path(__file__).resolve().parents[4]


# ===== ENUMS & DATACLASSES =====

class ReviewDepth(Enum):
    """Analysis depth options."""
    QUICK = "quick"        # Critical issues only
    STANDARD = "standard"  # + Best practices
    DEEP = "deep"         # + Security + Performance


class ReviewStatus(Enum):
    """Review status states."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"


@dataclass
class CodeIssue:
    """Single code issue."""
    severity: str  # critical, high, medium, low
    category: str  # security, performance, maintainability, tests, architecture
    description: str
    file: str = ""
    line: int = 0
    suggestion: str = ""


@dataclass
class QualityMetrics:
    """Code quality metrics."""
    risk_score: int = 0  # 0-100
    complexity_score: int = 0  # 0-100
    test_coverage: float = 0.0  # 0-100%
    lines_of_code: int = 0
    files_analyzed: int = 0
    issues_count: Dict[str, int] = field(default_factory=lambda: {
        "critical": 0, "high": 0, "medium": 0, "low": 0
    })


@dataclass
class ReviewSession:
    """Code review session."""
    review_id: str
    title: str
    description: str
    status: ReviewStatus
    depth: ReviewDepth
    
    # Files
    files_reviewed: List[str] = field(default_factory=list)
    
    # Issues
    issues: List[CodeIssue] = field(default_factory=list)
    
    # Metrics
    metrics: Optional[QualityMetrics] = None
    
    # Metadata
    reviewer: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


@dataclass
class ReviewResult:
    """Result of review operation."""
    success: bool
    message: str
    review_id: Optional[str] = None
    session: Optional[ReviewSession] = None
    report_path: Optional[Path] = None
    errors: List[str] = field(default_factory=list)


# ===== DIRECTORY MANAGEMENT =====

def _get_review_dirs() -> Dict[str, Path]:
    """Get review directory paths."""
    base_dir = CORTEX_ROOT / "cortex-brain" / "documents" / "reviews"
    
    dirs = {
        "base": base_dir,
        "draft": base_dir / "draft",
        "in_progress": base_dir / "in_progress",
        "completed": base_dir / "completed",
        "approved": base_dir / "approved",
        "reports": CORTEX_ROOT / "cortex-brain" / "documents" / "reports" / "reviews"
    }
    
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return dirs


def _get_status_dir(status: ReviewStatus) -> Path:
    """Get directory for review status."""
    dirs = _get_review_dirs()
    return dirs[status.value.replace("_", "_")]


def _slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


# ===== CORE OPERATION 1: CREATE REVIEW =====

def create_review(
    title: str,
    description: str,
    depth: ReviewDepth = ReviewDepth.STANDARD,
    **kwargs
) -> ReviewResult:
    """
    Create new code review session.
    
    Args:
        title: Review title
        description: Review description
        depth: Analysis depth
        **kwargs: Additional session fields
        
    Returns:
        ReviewResult with creation outcome
    """
    logger.info(f"📝 Creating review: {title}")
    
    try:
        # Generate review ID
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        slug = _slugify(title)[:30]
        review_id = f"review-{timestamp}-{slug}"
        
        # Create session
        session = ReviewSession(
            review_id=review_id,
            title=title,
            description=description,
            status=ReviewStatus.DRAFT,
            depth=depth,
            reviewer=kwargs.get('reviewer', 'CORTEX')
        )
        
        # Save to file
        file_path = _get_status_dir(ReviewStatus.DRAFT) / f"{review_id}.yaml"
        _save_session(session, file_path)
        
        return ReviewResult(
            success=True,
            message=f"Review created: {review_id}",
            review_id=review_id,
            session=session
        )
        
    except Exception as e:
        return ReviewResult(
            success=False,
            message=f"Failed to create review: {str(e)}",
            errors=[str(e)]
        )


def _save_session(session: ReviewSession, file_path: Path):
    """Save session to YAML file."""
    data = {
        "review_id": session.review_id,
        "title": session.title,
        "description": session.description,
        "status": session.status.value,
        "depth": session.depth.value,
        "files_reviewed": session.files_reviewed,
        "issues": [
            {
                "severity": issue.severity,
                "category": issue.category,
                "description": issue.description,
                "file": issue.file,
                "line": issue.line,
                "suggestion": issue.suggestion
            }
            for issue in session.issues
        ],
        "metrics": {
            "risk_score": session.metrics.risk_score,
            "complexity_score": session.metrics.complexity_score,
            "test_coverage": session.metrics.test_coverage,
            "lines_of_code": session.metrics.lines_of_code,
            "files_analyzed": session.metrics.files_analyzed,
            "issues_count": session.metrics.issues_count
        } if session.metrics else None,
        "reviewer": session.reviewer,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "completed_at": session.completed_at
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


# ===== CORE OPERATION 2: LOAD REVIEW =====

def load_review(review_id: str) -> ReviewResult:
    """
    Load existing review session.
    
    Args:
        review_id: Review identifier
        
    Returns:
        ReviewResult with loaded session
    """
    logger.info(f"📂 Loading review: {review_id}")
    
    try:
        # Search for review across all status directories
        dirs = _get_review_dirs()
        yaml_path = None
        
        for status_name in ["draft", "in_progress", "completed", "approved"]:
            potential_path = dirs[status_name] / f"{review_id}.yaml"
            if potential_path.exists():
                yaml_path = potential_path
                break
        
        if not yaml_path:
            return ReviewResult(
                success=False,
                message=f"Review not found: {review_id}",
                errors=[f"No file found for {review_id}"]
            )
        
        # Load YAML
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Reconstruct session
        issues = [
            CodeIssue(**issue_data)
            for issue_data in data.get("issues", [])
        ]
        
        metrics = None
        if data.get("metrics"):
            metrics = QualityMetrics(**data["metrics"])
        
        session = ReviewSession(
            review_id=data["review_id"],
            title=data["title"],
            description=data["description"],
            status=ReviewStatus(data["status"]),
            depth=ReviewDepth(data["depth"]),
            files_reviewed=data.get("files_reviewed", []),
            issues=issues,
            metrics=metrics,
            reviewer=data.get("reviewer", ""),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            completed_at=data.get("completed_at")
        )
        
        return ReviewResult(
            success=True,
            message=f"Review loaded: {review_id}",
            review_id=review_id,
            session=session
        )
        
    except Exception as e:
        return ReviewResult(
            success=False,
            message=f"Failed to load review: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 3: ANALYZE FILE =====

def analyze_file(
    review_id: str,
    file_path: Path,
    content: Optional[str] = None
) -> ReviewResult:
    """
    Analyze single file for code quality issues.
    
    Args:
        review_id: Review identifier
        file_path: Path to file being analyzed
        content: File content (optional, will read if not provided)
        
    Returns:
        ReviewResult with analysis outcome
    """
    logger.info(f"🔍 Analyzing file: {file_path.name}")
    
    try:
        # Load review
        load_result = load_review(review_id)
        if not load_result.success:
            return load_result
        
        session = load_result.session
        
        # Read file content if not provided
        if content is None:
            if not file_path.exists():
                return ReviewResult(
                    success=False,
                    message=f"File not found: {file_path}",
                    errors=[f"File does not exist: {file_path}"]
                )
            content = file_path.read_text(encoding='utf-8')
        
        # Perform basic analysis
        issues = _analyze_content(content, str(file_path), session.depth)
        
        # Add issues to session
        session.issues.extend(issues)
        
        # Add file to reviewed list
        if str(file_path) not in session.files_reviewed:
            session.files_reviewed.append(str(file_path))
        
        # Update metrics
        session.metrics = _calculate_metrics(session)
        session.updated_at = datetime.now().isoformat()
        
        # Save
        file_path_yaml = _get_status_dir(session.status) / f"{review_id}.yaml"
        _save_session(session, file_path_yaml)
        
        return ReviewResult(
            success=True,
            message=f"File analyzed: {file_path.name} ({len(issues)} issues found)",
            review_id=review_id,
            session=session
        )
        
    except Exception as e:
        return ReviewResult(
            success=False,
            message=f"Failed to analyze file: {str(e)}",
            errors=[str(e)]
        )


def _analyze_content(content: str, file_path: str, depth: ReviewDepth) -> List[CodeIssue]:
    """Analyze file content for issues."""
    issues = []
    lines = content.split('\n')
    
    # Quick checks (always run)
    for i, line in enumerate(lines, 1):
        # Check for TODO/FIXME
        if 'TODO' in line or 'FIXME' in line:
            issues.append(CodeIssue(
                severity="low",
                category="maintainability",
                description="TODO/FIXME comment found - consider addressing",
                file=file_path,
                line=i,
                suggestion="Complete the TODO or create a work item to track it"
            ))
        
        # Check for print statements (potential debug code)
        if re.search(r'\bprint\s*\(', line) and not line.strip().startswith('#'):
            issues.append(CodeIssue(
                severity="medium",
                category="maintainability",
                description="Print statement found - may be debug code",
                file=file_path,
                line=i,
                suggestion="Use logging instead of print statements"
            ))
        
        # Check for long lines
        if len(line) > 120:
            issues.append(CodeIssue(
                severity="low",
                category="maintainability",
                description=f"Line too long ({len(line)} chars > 120)",
                file=file_path,
                line=i,
                suggestion="Break long lines for better readability"
            ))
    
    # Standard/Deep checks
    if depth in [ReviewDepth.STANDARD, ReviewDepth.DEEP]:
        # Check for missing docstrings
        if 'def ' in content or 'class ' in content:
            if '"""' not in content and "'''" not in content:
                issues.append(CodeIssue(
                    severity="medium",
                    category="maintainability",
                    description="Missing docstrings for functions/classes",
                    file=file_path,
                    line=1,
                    suggestion="Add docstrings to document code purpose and usage"
                ))
        
        # Check for complex conditions
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('if ') or line.strip().startswith('elif '):
                if line.count(' and ') + line.count(' or ') > 2:
                    issues.append(CodeIssue(
                        severity="medium",
                        category="maintainability",
                        description="Complex conditional logic",
                        file=file_path,
                        line=i,
                        suggestion="Extract complex conditions into named variables"
                    ))
    
    # Deep checks (security, performance)
    if depth == ReviewDepth.DEEP:
        for i, line in enumerate(lines, 1):
            # Security: Check for SQL injection risks
            if 'execute(' in line and '+' in line:
                issues.append(CodeIssue(
                    severity="critical",
                    category="security",
                    description="Potential SQL injection vulnerability",
                    file=file_path,
                    line=i,
                    suggestion="Use parameterized queries instead of string concatenation"
                ))
            
            # Performance: Check for inefficient list comprehensions
            if '[' in line and 'for' in line and 'if' in line and 'in' in line:
                if line.count('for') > 1:
                    issues.append(CodeIssue(
                        severity="medium",
                        category="performance",
                        description="Nested list comprehension - may impact performance",
                        file=file_path,
                        line=i,
                        suggestion="Consider using generator expressions or breaking into multiple steps"
                    ))
    
    return issues


def _calculate_metrics(session: ReviewSession) -> QualityMetrics:
    """Calculate quality metrics for session."""
    issues_count = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    for issue in session.issues:
        severity = issue.severity.lower()
        if severity in issues_count:
            issues_count[severity] += 1
    
    # Calculate risk score (0-100)
    risk_score = min(100, (
        issues_count["critical"] * 25 +
        issues_count["high"] * 10 +
        issues_count["medium"] * 3 +
        issues_count["low"] * 1
    ))
    
    # Estimate complexity (placeholder)
    complexity_score = min(100, len(session.issues) * 2)
    
    return QualityMetrics(
        risk_score=risk_score,
        complexity_score=complexity_score,
        files_analyzed=len(session.files_reviewed),
        issues_count=issues_count
    )


# ===== CORE OPERATION 4: GENERATE REPORT =====

def generate_report(review_id: str) -> ReviewResult:
    """
    Generate code review report.
    
    Args:
        review_id: Review identifier
        
    Returns:
        ReviewResult with report path
    """
    logger.info(f"📄 Generating review report: {review_id}")
    
    try:
        # Load review
        load_result = load_review(review_id)
        if not load_result.success:
            return load_result
        
        session = load_result.session
        
        # Generate report markdown
        report_content = _generate_report_markdown(session)
        
        # Save report
        dirs = _get_review_dirs()
        report_path = dirs["reports"] / f"{review_id}-report.md"
        report_path.write_text(report_content, encoding='utf-8')
        
        return ReviewResult(
            success=True,
            message=f"Report generated: {review_id}",
            review_id=review_id,
            session=session,
            report_path=report_path
        )
        
    except Exception as e:
        return ReviewResult(
            success=False,
            message=f"Failed to generate report: {str(e)}",
            errors=[str(e)]
        )


def _generate_report_markdown(session: ReviewSession) -> str:
    """Generate markdown report for code review."""
    risk_icons = {0: "🟢", 25: "🟡", 50: "🟠", 75: "🔴"}
    risk_icon = risk_icons.get(min([k for k in risk_icons.keys() if k <= session.metrics.risk_score], default=0), "⚪") if session.metrics else "⚪"
    
    content = f"""# Code Review Report

**Review ID:** {session.review_id}  
**Date:** {session.created_at}  
**Reviewer:** {session.reviewer}  
**Status:** {session.status.value.upper()}  
**Depth:** {session.depth.value.upper()}

---

## Executive Summary

{risk_icon} **Risk Score:** {session.metrics.risk_score if session.metrics else 0}/100

**Files Analyzed:** {len(session.files_reviewed)}  
**Issues Found:** {len(session.issues)}

"""
    
    if session.metrics and session.metrics.issues_count:
        content += "**Issue Breakdown:**\n"
        content += f"- 🔴 Critical: {session.metrics.issues_count['critical']}\n"
        content += f"- 🟠 High: {session.metrics.issues_count['high']}\n"
        content += f"- 🟡 Medium: {session.metrics.issues_count['medium']}\n"
        content += f"- 🟢 Low: {session.metrics.issues_count['low']}\n"
    
    content += "\n---\n\n## Review Details\n\n"
    content += f"**Title:** {session.title}\n\n"
    content += f"**Description:**\n{session.description}\n\n"
    
    content += "---\n\n## Files Reviewed\n\n"
    if session.files_reviewed:
        for file in session.files_reviewed:
            content += f"- `{file}`\n"
    else:
        content += "(No files reviewed yet)\n"
    
    content += "\n---\n\n## Issues Found\n\n"
    
    if session.issues:
        # Group by severity
        by_severity = {"critical": [], "high": [], "medium": [], "low": []}
        for issue in session.issues:
            severity = issue.severity.lower()
            if severity in by_severity:
                by_severity[severity].append(issue)
        
        for severity in ["critical", "high", "medium", "low"]:
            issues_list = by_severity[severity]
            if not issues_list:
                continue
            
            severity_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
            icon = severity_icons.get(severity, "⚪")
            
            content += f"### {icon} {severity.upper()} Issues ({len(issues_list)})\n\n"
            
            for i, issue in enumerate(issues_list, 1):
                content += f"#### {i}. {issue.description}\n\n"
                content += f"**Category:** {issue.category}\n"
                if issue.file:
                    content += f"**File:** `{issue.file}`"
                    if issue.line > 0:
                        content += f" (line {issue.line})"
                    content += "\n"
                if issue.suggestion:
                    content += f"\n💡 **Suggestion:** {issue.suggestion}\n"
                content += "\n"
    else:
        content += "(No issues found)\n"
    
    content += f"\n---\n\n**Report Generated:** {datetime.now().isoformat()}\n"
    
    return content


# ===== CORE OPERATION 5: LIST REVIEWS =====

def list_reviews(status: Optional[ReviewStatus] = None) -> ReviewResult:
    """
    List code reviews by status.
    
    Args:
        status: Filter by status (None = all)
        
    Returns:
        ReviewResult with list of reviews
    """
    logger.info(f"📋 Listing reviews (status: {status.value if status else 'all'})")
    
    try:
        reviews = []
        dirs = _get_review_dirs()
        
        # Determine which directories to search
        if status:
            search_dirs = {status.value: _get_status_dir(status)}
        else:
            search_dirs = {
                "draft": dirs["draft"],
                "in_progress": dirs["in_progress"],
                "completed": dirs["completed"],
                "approved": dirs["approved"]
            }
        
        # Scan directories
        for status_name, dir_path in search_dirs.items():
            for yaml_path in dir_path.glob("*.yaml"):
                try:
                    with open(yaml_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                    
                    session = ReviewSession(
                        review_id=data["review_id"],
                        title=data["title"],
                        description=data["description"],
                        status=ReviewStatus(data["status"]),
                        depth=ReviewDepth(data["depth"]),
                        reviewer=data.get("reviewer", ""),
                        created_at=data["created_at"],
                        updated_at=data["updated_at"]
                    )
                    reviews.append(session)
                except Exception as e:
                    logger.warning(f"Failed to load {yaml_path.name}: {e}")
        
        # Sort by updated date
        reviews.sort(key=lambda x: x.updated_at, reverse=True)
        
        message = f"Found {len(reviews)} review(s)"
        if status:
            message += f" with status '{status.value}'"
        
        return ReviewResult(
            success=True,
            message=message,
            session=reviews[0] if reviews else None
        )
        
    except Exception as e:
        return ReviewResult(
            success=False,
            message=f"Failed to list reviews: {str(e)}",
            errors=[str(e)]
        )


# ===== CLI TEST EXECUTION =====

if __name__ == "__main__":
    print("=" * 60)
    print("Code Review Utility - Direct Test")
    print("=" * 60)
    
    # Test 1: Create review
    print("\n[Test 1] Create review...")
    result = create_review(
        title="Test Code Review",
        description="Testing code review utility",
        depth=ReviewDepth.STANDARD,
        reviewer="CORTEX Test"
    )
    
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    print(f"Review ID: {result.review_id}")
    
    if not result.success:
        print("❌ Creation failed")
        exit(1)
    
    review_id = result.review_id
    
    # Test 2: Analyze test file (create temporary)
    print("\n" + "=" * 60)
    print("[Test 2] Analyze file...")
    
    test_content = '''
def test_function():
    # TODO: Add more tests
    print("Debug message")
    x = 1
    if x == 1 and y == 2 and z == 3 and a == 4:
        pass
    result = execute("SELECT * FROM users WHERE id = " + user_id)
    return result
'''
    
    analyze_result = analyze_file(
        review_id,
        Path("test_file.py"),
        content=test_content
    )
    
    print(f"Success: {analyze_result.success}")
    print(f"Message: {analyze_result.message}")
    if analyze_result.session:
        print(f"Issues found: {len(analyze_result.session.issues)}")
    
    # Test 3: Generate report
    print("\n" + "=" * 60)
    print("[Test 3] Generate report...")
    report_result = generate_report(review_id)
    
    print(f"Success: {report_result.success}")
    print(f"Message: {report_result.message}")
    if report_result.report_path:
        print(f"Report: {report_result.report_path}")
    
    # Test 4: List reviews
    print("\n" + "=" * 60)
    print("[Test 4] List reviews...")
    list_result = list_reviews(status=ReviewStatus.DRAFT)
    
    print(f"Success: {list_result.success}")
    print(f"Message: {list_result.message}")
    
    # Cleanup
    print("\n" + "=" * 60)
    print("[Cleanup] Removing test review...")
    yaml_path = _get_status_dir(ReviewStatus.DRAFT) / f"{review_id}.yaml"
    report_path = _get_review_dirs()["reports"] / f"{review_id}-report.md"
    
    if yaml_path.exists():
        yaml_path.unlink()
    if report_path.exists():
        report_path.unlink()
    print("✅ Test review removed")
    
    print("\n" + "=" * 60)
    print("✅ Utility tests complete")
    print("=" * 60)
