"""
Post-Session Markdown Generation Auditor

Detects CORE-002 violations in recent commits and suggests remediation.

Authority: CORE-002 (No Markdown Report Generation)
Version: 6.2
Date: 2026-01-27
"""

import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple, Optional


@dataclass
class MarkdownViolation:
    """Represents a CORE-002 violation."""
    file_path: str
    commit_hash: str
    commit_message: str
    author: str
    timestamp: datetime
    violation_type: str  # 'REPORT', 'COMPLETION', 'STATUS', 'SUMMARY'
    
    def __str__(self) -> str:
        return (
            f"🚨 VIOLATION: {self.file_path}\n"
            f"   Commit: {self.commit_hash[:8]}\n"
            f"   Type: {self.violation_type}\n"
            f"   Author: {self.author}\n"
            f"   Time: {self.timestamp.isoformat()}"
        )


BLOCKED_PATTERNS = [
    (r".*-REPORT\.md$", "REPORT"),
    (r".*-COMPLETION.*\.md$", "COMPLETION"),
    (r".*-STATUS\.md$", "STATUS"),
    (r".*-SUMMARY\.md$", "SUMMARY"),
    (r"PHASE-.*-REPORT\.md$", "REPORT"),
]

# CORE-002 COMPLIANCE: Only these locations allow markdown files
ALLOWED_LOCATIONS = [".github/prompts/", ".github/agents/", "README.md"]


def is_violation(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Check if file path is a CORE-002 violation.
    
    Args:
        file_path: Relative file path from repo root
        
    Returns:
        (is_violation, violation_type) tuple
    """
    # Check if in allowed location
    for allowed in ALLOWED_LOCATIONS:
        if file_path.startswith(allowed):
            return False, None
    
    # Check patterns
    filename = Path(file_path).name
    for pattern, vtype in BLOCKED_PATTERNS:
        if re.match(pattern, filename, re.IGNORECASE):
            return True, vtype
    
    return False, None


def get_recent_commits(since_minutes: int = 60) -> List[str]:
    """
    Get commit hashes from recent commits.
    
    Args:
        since_minutes: How far back to look
        
    Returns:
        List of commit hashes
    """
    since_time = datetime.now() - timedelta(minutes=since_minutes)
    since_str = since_time.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        result = subprocess.run(
            ['git', 'log', f'--since={since_str}', '--format=%H'],
            capture_output=True,
            text=True,
            check=True
        )
        return [h for h in result.stdout.strip().split('\n') if h]
    except subprocess.CalledProcessError:
        return []


def get_files_in_commit(commit_hash: str) -> List[str]:
    """
    Get files added/modified in a commit.
    
    Args:
        commit_hash: Git commit hash
        
    Returns:
        List of file paths
    """
    try:
        result = subprocess.run(
            ['git', 'show', '--name-only', '--format=', commit_hash],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().split('\n')
        return [f for f in files if f.endswith('.md') and f]
    except subprocess.CalledProcessError:
        return []


def get_commit_info(commit_hash: str) -> Tuple[str, str, str]:
    """
    Get commit metadata.
    
    Args:
        commit_hash: Git commit hash
        
    Returns:
        (message, author, timestamp) tuple
    """
    try:
        result = subprocess.run(
            ['git', 'show', '-s', '--format=%s|%an|%ai', commit_hash],
            capture_output=True,
            text=True,
            check=True
        )
        parts = result.stdout.strip().split('|')
        if len(parts) == 3:
            return parts[0], parts[1], parts[2]
        return "", "", ""
    except subprocess.CalledProcessError:
        return "", "", ""


def audit_recent_commits(since_minutes: int = 60) -> List[MarkdownViolation]:
    """
    Audit recent commits for CORE-002 violations.
    
    Args:
        since_minutes: How far back to scan
        
    Returns:
        List of violations found
    """
    violations = []
    commits = get_recent_commits(since_minutes)
    
    for commit_hash in commits:
        files = get_files_in_commit(commit_hash)
        message, author, timestamp_str = get_commit_info(commit_hash)
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace(' ', 'T'))
        except ValueError:
            timestamp = datetime.now()
        
        for file_path in files:
            is_viol, vtype = is_violation(file_path)
            if is_viol and vtype:
                violations.append(MarkdownViolation(
                    file_path=file_path,
                    commit_hash=commit_hash,
                    commit_message=message,
                    author=author,
                    timestamp=timestamp,
                    violation_type=vtype
                ))
    
    return violations


def generate_violation_report(violations: List[MarkdownViolation]) -> str:
    """
    Generate inline chat report of violations.
    
    Args:
        violations: List of detected violations
        
    Returns:
        Formatted markdown report string
    """
    if not violations:
        return "✅ No CORE-002 violations detected in recent commits"
    
    report = [
        "## 🚨 CORE-002 Violations Detected",
        "",
        f"**Total Violations:** {len(violations)}",
        f"**Scan Time:** {datetime.now().isoformat()}",
        "",
        "### Violations:",
        ""
    ]
    
    for v in violations:
        report.append(f"#### {v.file_path}")
        report.append(f"- **Commit:** `{v.commit_hash[:8]}`")
        report.append(f"- **Type:** {v.violation_type}")
        report.append(f"- **Message:** {v.commit_message}")
        report.append(f"- **Author:** {v.author}")
        report.append(f"- **Time:** {v.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
    
    report.extend([
        "### 🔧 Remediation Steps:",
        "",
        "1. **Delete violation files:**",
        "   ```bash",
    ])
    
    for v in violations:
        report.append(f"   rm {v.file_path}")
    
    report.extend([
        "   ```",
        "",
        "2. **Amend last commit (if violations in HEAD):**",
        "   ```bash",
        "   git add -u",
        "   git commit --amend --no-edit",
        "   ```",
        "",
        "3. **Update workflow:**",
        "   - Use inline chat responses instead of files",
        "   - Only create .md files in .github/prompts/ or .github/agents/",
        "",
        "4. **Verify fix:**",
        "   ```bash",
        "   python -m cortex.tools.audit_md_generation",
        "   ```",
    ])
    
    return "\n".join(report)


def main() -> int:
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Audit recent commits for CORE-002 markdown generation violations"
    )
    parser.add_argument(
        '--since',
        type=int,
        default=60,
        help="Minutes to look back (default: 60)"
    )
    parser.add_argument(
        '--format',
        choices=['inline', 'json'],
        default='inline',
        help="Output format (default: inline)"
    )
    
    args = parser.parse_args()
    
    violations = audit_recent_commits(since_minutes=args.since)
    
    if args.format == 'json':
        import json
        output = json.dumps([
            {
                'file': v.file_path,
                'commit': v.commit_hash,
                'type': v.violation_type,
                'author': v.author,
                'timestamp': v.timestamp.isoformat(),
            }
            for v in violations
        ], indent=2)
        print(output)
    else:
        report = generate_violation_report(violations)
        print(report)
    
    return 1 if violations else 0


if __name__ == "__main__":
    exit(main())
