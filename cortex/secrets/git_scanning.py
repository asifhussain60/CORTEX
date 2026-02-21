"""Git secrets scanning — detect secrets in git history and pre-commit hooks."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


# Patterns that indicate a secret
_SECRET_PATTERNS = [
    re.compile(r'(?i)(password|passwd|secret|token|api_key|apikey)\s*=\s*["\']?\S+'),
    re.compile(r'(?i)aws_access_key_id\s*=\s*[A-Z0-9]{20}'),
    re.compile(r'(?i)-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----'),
]


class SecretsScanner:
    """Base scanner — scans text content for secret patterns."""

    def scan_text(self, text: str) -> List[Dict[str, Any]]:
        """Scan text.
        
        Args:
            text: Parameter for text.
        
        Returns:
            List[Dict[str, Any]] result.
        """
        findings: List[Dict[str, Any]] = []
        for i, line in enumerate(text.splitlines(), 1):
            for pattern in _SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append({"line": i, "content": line.strip(), "pattern": pattern.pattern})
        return findings

    def scan_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan file.
        
        Args:
            file_path: Parameter for file path.
        
        Returns:
            List[Dict[str, Any]] result.
        """
        try:
            content = Path(file_path).read_text(errors="replace")
            findings = self.scan_text(content)
            for f in findings:
                f["file"] = file_path
            return findings
        except Exception:
            return []


class GitHistoryScanner(SecretsScanner):
    """Scans git history for accidentally committed secrets."""

    def __init__(self, repo_path: str = ".") -> None:
        self.repo_path = repo_path

    def scan_commits(self, max_commits: int = 100) -> List[Dict[str, Any]]:
        """Scan commits.
        
        Args:
            max_commits: Parameter for max commits.
        
        Returns:
            List[Dict[str, Any]] result.
        """
        try:
            result = subprocess.run(
                ["git", "log", f"-{max_commits}", "--patch", "--unified=0"],
                capture_output=True, text=True, cwd=self.repo_path, timeout=30,
            )
            return self.scan_text(result.stdout)
        except Exception:
            return []

    def scan_all_history(self) -> List[Dict[str, Any]]:
        """Scan all history.
        
        Returns:
            List[Dict[str, Any]] result.
        """
        return self.scan_commits(max_commits=500)


class GitHubActionsScanner(SecretsScanner):
    """Scans GitHub Actions workflow files for hardcoded secrets."""

    def scan_workflows(self, repo_path: str = ".") -> List[Dict[str, Any]]:
        """Scan workflows.
        
        Args:
            repo_path: Parameter for repo path.
        
        Returns:
            List[Dict[str, Any]] result.
        """
        findings: List[Dict[str, Any]] = []
        workflows_dir = Path(repo_path) / ".github" / "workflows"
        if workflows_dir.exists():
            for workflow in workflows_dir.rglob("*.yml"):
                findings.extend(self.scan_file(str(workflow)))
        return findings


class PreCommitHookScanner(SecretsScanner):
    """Installs and manages pre-commit hooks for secrets scanning."""

    def __init__(self, repo_path: str = ".") -> None:
        self.repo_path = repo_path

    def install_hook(self) -> bool:
        """Install hook.
        
        Returns:
            bool result.
        """
        hooks_dir = Path(self.repo_path) / ".git" / "hooks"
        if not hooks_dir.exists():
            return False
        hook_path = hooks_dir / "pre-commit"
        hook_content = "#!/bin/sh\npython3 -m cortex.secrets.git_scanning scan --pre-commit\n"
        hook_path.write_text(hook_content)
        hook_path.chmod(0o755)
        return True

    def is_installed(self) -> bool:
        """Is installed.
        
        Returns:
            bool result.
        """
        hook_path = Path(self.repo_path) / ".git" / "hooks" / "pre-commit"
        return hook_path.exists()


class SecretsRemediator:
    """Remediates detected secrets — rotates, redacts, or removes them."""

    def redact_file(self, file_path: str, findings: List[Dict[str, Any]]) -> bool:
        """Redact file.
        
        Args:
            file_path: Parameter for file path.
            findings: Parameter for findings.
        
        Returns:
            bool result.
        """
        path = Path(file_path)
        if not path.exists():
            return False
        content = path.read_text()
        for finding in findings:
            line_content = finding.get("content", "")
            if line_content:
                content = content.replace(line_content, "[REDACTED]")
        path.write_text(content)
        return True

    def generate_remediation_plan(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate remediation plan.
        
        Args:
            findings: Parameter for findings.
        
        Returns:
            List[Dict[str, Any]] result.
        """
        return [
            {
                "file": f.get("file", "unknown"),
                "line": f.get("line"),
                "action": "redact_and_rotate",
                "priority": "critical",
            }
            for f in findings
        ]
