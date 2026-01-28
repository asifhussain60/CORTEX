"""
RemoteSecurityThreatAnalyzer - Remote GitHub code analysis (Phase 8.5).

Extends SecurityThreatAnalyzer to analyze code from remote GitHub repositories
without cloning, using GitHistoryAnalyzer's RemoteGitAdapter capabilities.

Phase 8.5: LENS Remote Intelligence
Authority: AC-SECURITY-FRAMEWORK-001 (Phase 8.5 Extension)
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
import logging

from cortex.brain.analysis.security_threat_analyzer import (
    SecurityThreatAnalyzer,
    ThreatFinding,
    ThreatSeverity,
    SecurityAnalysisResult,
)
from cortex.brain.analysis.remote_git_adapter import (
    RemoteGitAdapter,
    RemoteFile,
)

logger = logging.getLogger(__name__)


@dataclass
class RemoteSecurityAnalysisResult(SecurityAnalysisResult):
    """
    Result of remote security analysis with GitHub metadata.
    
    Extends SecurityAnalysisResult with remote source info.
    """
    github_repo: str = ""
    github_branch: str = "main"
    remote_file_url: str = ""
    commit_hash: str = ""
    file_author: str = ""
    last_modified: str = ""
    risk_score: float = 0.0  # 0-10 scale


class RemoteSecurityThreatAnalyzer(SecurityThreatAnalyzer):
    """
    Analyzes security threats in remote GitHub repositories (Phase 8.5).
    
    Extends SecurityThreatAnalyzer to:
    1. Fetch code from GitHub without cloning
    2. Correlate threats with git blame (who introduced vulnerability)
    3. Calculate risk scores based on file history
    4. Generate comprehensive security reports
    
    Uses RemoteGitAdapter for efficient remote analysis.
    
    Example:
        >>> analyzer = RemoteSecurityThreatAnalyzer()
        >>> result = analyzer.analyze_remote_file(
        ...     repo="myorg/myrepo",
        ...     file_path="src/handlers.py",
        ...     branch="main"
        ... )
        >>> print(f"Threats: {len(result.threat_findings)}")
        >>> print(f"Risk Score: {result.risk_score}/10")
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize RemoteSecurityThreatAnalyzer.
        
        Args:
            github_token: GitHub API token (optional, for private repos)
        """
        super().__init__()
        self.remote_adapter = RemoteGitAdapter(github_token=github_token)
        logger.info("RemoteSecurityThreatAnalyzer initialized (Phase 8.5)")
    
    def analyze_remote_file(
        self,
        repo: str,
        file_path: str,
        branch: str = "main",
    ) -> RemoteSecurityAnalysisResult:
        """
        Analyze a file from a remote GitHub repository.
        
        Phase 8.5: Remote LENS Intelligence
        
        Args:
            repo: Repository (e.g., "cortex-ai/cortex")
            file_path: Path to file in repo (e.g., "src/handlers.py")
            branch: Git branch (default: "main")
            
        Returns:
            RemoteSecurityAnalysisResult with threats and metadata
        """
        logger.info(f"Analyzing remote file: {repo}/{file_path} on {branch}")
        
        try:
            # Fetch remote file
            remote_file: RemoteFile = self.remote_adapter.get_file(
                repo=repo,
                path=file_path,
                ref=branch
            )
            
            if not remote_file:
                return RemoteSecurityAnalysisResult(
                    success=False,
                    error=f"Failed to fetch {file_path} from {repo}:{branch}"
                )
            
            # Analyze code using parent class
            analysis_result = self.analyze_code(
                remote_file.content,
                file_path
            )
            
            # Enhance with remote metadata
            blame_info = self.remote_adapter.get_blame(
                repo=repo,
                path=file_path,
                ref=branch
            )
            
            # Build comprehensive result
            result = RemoteSecurityAnalysisResult(
                success=analysis_result.success,
                threat_findings=analysis_result.threat_findings,
                error=analysis_result.error,
                analysis_time_ms=analysis_result.analysis_time_ms,
                file_path=file_path,
                patterns_checked=analysis_result.patterns_checked,
                github_repo=repo,
                github_branch=branch,
                remote_file_url=f"https://github.com/{repo}/blob/{branch}/{file_path}",
                commit_hash=remote_file.commit_hash,
                file_author=remote_file.author,
                last_modified=str(remote_file.last_modified),
                risk_score=self._calculate_risk_score(
                    analysis_result.threat_findings,
                    blame_info
                ),
            )
            
            # Log findings
            logger.info(
                f"Remote analysis complete: {repo}/{file_path} - "
                f"{len(result.threat_findings)} threats, risk={result.risk_score:.1f}/10"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Remote analysis failed: {str(e)}")
            return RemoteSecurityAnalysisResult(
                success=False,
                error=str(e),
                github_repo=repo,
                github_branch=branch,
            )
    
    def analyze_remote_repo(
        self,
        repo: str,
        branch: str = "main",
        patterns: Optional[List[str]] = None,
    ) -> Dict[str, RemoteSecurityAnalysisResult]:
        """
        Analyze multiple files in a remote repository.
        
        Phase 8.5: Repository-wide security scan
        
        Args:
            repo: Repository (e.g., "cortex-ai/cortex")
            branch: Git branch to analyze
            patterns: Optional glob patterns to match (e.g., ["*.py", "src/**/*.py"])
            
        Returns:
            Dict mapping file paths to analysis results
        """
        logger.info(f"Starting repository scan: {repo} on {branch}")
        
        results: Dict[str, RemoteSecurityAnalysisResult] = {}
        
        try:
            # List files in repo
            files = self.remote_adapter.list_files(
                repo=repo,
                ref=branch,
                patterns=patterns or ["*.py"]
            )
            
            logger.info(f"Found {len(files)} Python files to analyze")
            
            # Analyze each file
            for file_path in files:
                result = self.analyze_remote_file(repo, file_path, branch)
                results[file_path] = result
            
            return results
            
        except Exception as e:
            logger.error(f"Repository scan failed: {str(e)}")
            return {}
    
    def _calculate_risk_score(
        self,
        threats: List[ThreatFinding],
        blame_info: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Calculate composite risk score (0-10 scale).
        
        Phase 8.5: Risk scoring based on threat severity and ownership
        
        Args:
            threats: List of detected threats
            blame_info: Optional blame metadata
            
        Returns:
            Risk score 0-10
        """
        if not threats:
            return 0.0
        
        # Base score on threat count and severity
        severity_scores = {
            ThreatSeverity.CRITICAL: 10,
            ThreatSeverity.HIGH: 7,
            ThreatSeverity.MEDIUM: 4,
            ThreatSeverity.LOW: 2,
            ThreatSeverity.INFO: 1,
        }
        
        # Calculate average severity
        total_score = sum(
            severity_scores.get(t.severity, 0)
            for t in threats
        )
        
        avg_severity = total_score / len(threats) if threats else 0
        
        # Adjust for threat count (more threats = higher risk)
        threat_multiplier = min(1.0 + (len(threats) - 1) * 0.1, 2.0)
        
        risk_score = avg_severity * threat_multiplier
        
        # Cap at 10
        return min(risk_score, 10.0)


def get_remote_security_threat_analyzer(
    github_token: Optional[str] = None,
) -> RemoteSecurityThreatAnalyzer:
    """
    Factory function for RemoteSecurityThreatAnalyzer.
    
    Args:
        github_token: GitHub API token (optional)
        
    Returns:
        RemoteSecurityThreatAnalyzer instance
    """
    return RemoteSecurityThreatAnalyzer(github_token=github_token)
