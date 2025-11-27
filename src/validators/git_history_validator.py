"""
Git History Validator - Universal Rule Enforcement

Purpose: Ensures all requests check git history to build stronger context before analysis.
This validator enforces CORTEX's universal rule that git history must be consulted for
every request to identify patterns, security issues, and subject matter experts.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 1.0.0
"""

import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import yaml


@dataclass
class ValidationResult:
    """Result of git history validation"""
    status: str  # PASS, FAIL, WARNING, BLOCKED
    message: str
    required_actions: List[str]
    context_enrichment: Dict[str, any]
    quality_score: float  # 0-100%


class GitHistoryValidator:
    """
    Validates that git history has been checked before processing requests.
    
    Enforcement Level: BLOCKING (cannot proceed without git history context)
    
    Validation Checks:
    1. Recent Activity Analysis (6 months): Commit count, churn rate
    2. Security Pattern Detection (1 year): Security commits, hotfixes, CVE references
    3. Contributor Analysis: Top contributors, SME identification
    4. Related Work Discovery: PR references, issue tracker links
    5. Temporal Patterns: Change frequency, spike detection
    """
    
    def __init__(self, repo_path: Path, config_path: Optional[Path] = None):
        """
        Initialize validator with repository path and optional config.
        
        Args:
            repo_path: Path to git repository
            config_path: Path to git-history-rules.yaml (defaults to cortex-brain/config/)
        """
        self.repo_path = Path(repo_path)
        self.config = self._load_config(config_path)
        self.security_keywords = self.config.get('security_keywords', [
            'security', 'vulnerability', 'CVE', 'exploit', 'bypass',
            'injection', 'XSS', 'CSRF', 'authentication', 'authorization',
            'password', 'encryption', 'hotfix', 'rollback'
        ])
    
    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load configuration from YAML file"""
        if config_path is None:
            config_path = self.repo_path / 'cortex-brain' / 'config' / 'git-history-rules.yaml'
        
        if not config_path.exists():
            # Return defaults if config doesn't exist
            return {
                'enforcement_level': 'BLOCKING',
                'minimum_commits_analyzed': 5,
                'commit_lookback_months': 6,
                'security_lookback_months': 12,
                'security_keywords': [
                    'security', 'vulnerability', 'CVE', 'exploit', 'bypass',
                    'injection', 'XSS', 'CSRF', 'authentication', 'authorization',
                    'password', 'encryption', 'hotfix', 'rollback'
                ],
                'high_risk_indicators': {
                    'churn_threshold': 15,
                    'hotfix_count_threshold': 3,
                    'recent_security_fix_days': 30
                },
                'exemptions': ['*.md', '*.txt', '*.json', '*.yaml']
            }
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def validate_request(self, request_context: Dict) -> ValidationResult:
        """
        Validate that git history has been checked for the request.
        
        Args:
            request_context: Dictionary containing:
                - files: List of files being analyzed
                - operation: Type of operation (plan, execute, review, etc.)
                - has_git_history_context: Boolean indicating if git history was checked
        
        Returns:
            ValidationResult with status, message, required actions, and context enrichment
        """
        files = request_context.get('files', [])
        operation = request_context.get('operation', 'unknown')
        has_context = request_context.get('has_git_history_context', False)
        
        # Check exemptions (documentation files, configs)
        if self._is_exempt(files):
            return ValidationResult(
                status='PASS',
                message='Files exempt from git history requirement',
                required_actions=[],
                context_enrichment={},
                quality_score=100.0
            )
        
        # If git history context already provided, validate quality
        if has_context:
            return self._validate_context_quality(request_context)
        
        # Git history context missing - BLOCKING failure
        return ValidationResult(
            status='BLOCKED',
            message='Git history context required but not provided',
            required_actions=[
                'Run git history analysis before proceeding',
                'Check: git log --oneline [file] (recent activity)',
                'Check: git log --grep="security|vulnerability" (security patterns)',
                'Check: git shortlog -sn [file] (contributors)',
                'Check: git blame [file] (line-level history)'
            ],
            context_enrichment={},
            quality_score=0.0
        )
    
    def _is_exempt(self, files: List[str]) -> bool:
        """Check if files are exempt from git history requirement"""
        exemptions = self.config.get('exemptions', [])
        
        for file_path in files:
            # Check if any exemption pattern matches
            for pattern in exemptions:
                if re.match(pattern.replace('*', '.*'), file_path):
                    return True
        
        return False
    
    def _validate_context_quality(self, request_context: Dict) -> ValidationResult:
        """
        Validate the quality of provided git history context.
        
        Checks:
        - Minimum commits analyzed (default: 5)
        - Lookback period (default: 6 months)
        - Security pattern scan completed
        - Contributor analysis completed
        """
        git_context = request_context.get('git_history_context', {})
        
        # Extract metrics
        commits_analyzed = git_context.get('commits_analyzed', 0)
        lookback_months = git_context.get('lookback_months', 0)
        security_scan_done = git_context.get('security_scan_completed', False)
        contributor_analysis_done = git_context.get('contributor_analysis_completed', False)
        
        # Calculate quality score
        score = 0.0
        issues = []
        
        # Check commits analyzed (30 points)
        min_commits = self.config.get('minimum_commits_analyzed', 5)
        if commits_analyzed >= min_commits:
            score += 30.0
        else:
            issues.append(f'Only {commits_analyzed} commits analyzed (minimum: {min_commits})')
        
        # Check lookback period (25 points)
        min_lookback = self.config.get('commit_lookback_months', 6)
        if lookback_months >= min_lookback:
            score += 25.0
        else:
            issues.append(f'Only {lookback_months} months lookback (minimum: {min_lookback})')
        
        # Check security scan (25 points)
        if security_scan_done:
            score += 25.0
        else:
            issues.append('Security pattern scan not completed')
        
        # Check contributor analysis (20 points)
        if contributor_analysis_done:
            score += 20.0
        else:
            issues.append('Contributor analysis not completed')
        
        # Determine status based on score
        if score >= 90:
            status = 'PASS'
            message = 'Git history context quality: Excellent'
        elif score >= 70:
            status = 'PASS'
            message = 'Git history context quality: Good'
        elif score >= 50:
            status = 'WARNING'
            message = 'Git history context quality: Adequate (improvements recommended)'
        else:
            status = 'BLOCKED'
            message = 'Git history context quality: Insufficient'
        
        return ValidationResult(
            status=status,
            message=message,
            required_actions=issues if issues else [],
            context_enrichment=git_context,
            quality_score=score
        )
    
    def analyze_file_history(self, file_path: str) -> Dict:
        """
        Analyze git history for a specific file.
        
        Returns comprehensive context including:
        - Recent activity (6 months)
        - Security patterns (1 year)
        - Contributors (all time)
        - Related work (PR/issue references)
        - Temporal patterns (change frequency)
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'error': 'File not found',
                'commits_analyzed': 0,
                'quality_score': 0.0
            }
        
        context = {
            'file': str(file_path),
            'analyzed_at': datetime.now().isoformat(),
            'commits_analyzed': 0,
            'lookback_months': self.config.get('commit_lookback_months', 6),
            'security_scan_completed': False,
            'contributor_analysis_completed': False
        }
        
        # 1. Recent Activity Analysis (6 months)
        recent_activity = self._analyze_recent_activity(file_path)
        context.update(recent_activity)
        
        # 2. Security Pattern Detection (1 year)
        security_patterns = self._analyze_security_patterns(file_path)
        context.update(security_patterns)
        context['security_scan_completed'] = True
        
        # 3. Contributor Analysis
        contributors = self._analyze_contributors(file_path)
        context.update(contributors)
        context['contributor_analysis_completed'] = True
        
        # 4. Related Work Discovery
        related_work = self._discover_related_work(file_path)
        context.update(related_work)
        
        # 5. Temporal Patterns
        temporal = self._analyze_temporal_patterns(file_path)
        context.update(temporal)
        
        return context
    
    def _analyze_recent_activity(self, file_path: Path) -> Dict:
        """Analyze recent commits (6 months) for the file"""
        lookback_months = self.config.get('commit_lookback_months', 6)
        since_date = (datetime.now() - timedelta(days=lookback_months * 30)).strftime('%Y-%m-%d')
        
        try:
            # Get commit count
            result = subprocess.run(
                ['git', 'log', '--oneline', f'--since={since_date}', '--', str(file_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
            commit_count = len(commits)
            
            # Get churn rate (lines added/deleted)
            churn_result = subprocess.run(
                ['git', 'log', '--numstat', f'--since={since_date}', '--', str(file_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            # Parse numstat output
            lines_added = 0
            lines_deleted = 0
            for line in churn_result.stdout.split('\n'):
                if line and not line.startswith('commit'):
                    parts = line.split('\t')
                    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                        lines_added += int(parts[0])
                        lines_deleted += int(parts[1])
            
            churn_rate = lines_added + lines_deleted
            
            # Determine if high churn
            churn_threshold = self.config.get('high_risk_indicators', {}).get('churn_threshold', 15)
            is_high_churn = commit_count >= churn_threshold
            
            return {
                'recent_commits': commit_count,
                'commits_analyzed': commit_count,
                'lines_added': lines_added,
                'lines_deleted': lines_deleted,
                'churn_rate': churn_rate,
                'is_high_churn': is_high_churn,
                'high_churn_threshold': churn_threshold
            }
        
        except subprocess.CalledProcessError as e:
            return {
                'recent_commits': 0,
                'commits_analyzed': 0,
                'error': f'Git command failed: {e}'
            }
    
    def _analyze_security_patterns(self, file_path: Path) -> Dict:
        """Analyze security-related commits (1 year lookback)"""
        lookback_months = self.config.get('security_lookback_months', 12)
        since_date = (datetime.now() - timedelta(days=lookback_months * 30)).strftime('%Y-%m-%d')
        
        try:
            # Build grep pattern from security keywords
            pattern = '|'.join(self.security_keywords)
            
            result = subprocess.run(
                ['git', 'log', '--grep', pattern, '-i', '--oneline', f'--since={since_date}', '--', str(file_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            security_commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
            security_count = len([c for c in security_commits if c])
            
            # Count hotfixes specifically
            hotfix_result = subprocess.run(
                ['git', 'log', '--grep', 'hotfix', '-i', '--oneline', f'--since={since_date}', '--', str(file_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            hotfix_commits = hotfix_result.stdout.strip().split('\n') if hotfix_result.stdout.strip() else []
            hotfix_count = len([c for c in hotfix_commits if c])
            
            # Check for recent security fixes (30 days)
            recent_security_days = self.config.get('high_risk_indicators', {}).get('recent_security_fix_days', 30)
            recent_date = (datetime.now() - timedelta(days=recent_security_days)).strftime('%Y-%m-%d')
            
            recent_result = subprocess.run(
                ['git', 'log', '--grep', pattern, '-i', '--oneline', f'--since={recent_date}', '--', str(file_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            has_recent_security_fix = bool(recent_result.stdout.strip())
            
            return {
                'security_commits': security_count,
                'hotfix_commits': hotfix_count,
                'has_recent_security_fix': has_recent_security_fix,
                'security_keywords_checked': len(self.security_keywords),
                'is_security_sensitive': security_count >= 3 or has_recent_security_fix
            }
        
        except subprocess.CalledProcessError as e:
            return {
                'security_commits': 0,
                'error': f'Security scan failed: {e}'
            }
    
    def _analyze_contributors(self, file_path: Path) -> Dict:
        """Analyze contributors to the file"""
        try:
            # Get top contributors
            result = subprocess.run(
                ['git', 'shortlog', '-sn', '--', str(file_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            contributors = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        count = int(parts[0])
                        name = parts[1]
                        contributors.append({'name': name, 'commits': count})
            
            # Get recent contributors (last 3 months)
            recent_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            recent_result = subprocess.run(
                ['git', 'shortlog', '-sn', f'--since={recent_date}', '--', str(file_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            recent_contributors = []
            for line in recent_result.stdout.strip().split('\n'):
                if line:
                    parts = line.strip().split('\t')
                    if len(parts) == 2:
                        recent_contributors.append(parts[1])
            
            return {
                'total_contributors': len(contributors),
                'top_contributors': contributors[:3] if contributors else [],
                'recent_contributors': recent_contributors,
                'primary_maintainer': contributors[0]['name'] if contributors else None
            }
        
        except subprocess.CalledProcessError as e:
            return {
                'total_contributors': 0,
                'error': f'Contributor analysis failed: {e}'
            }
    
    def _discover_related_work(self, file_path: Path) -> Dict:
        """Discover related PRs, issues, and files"""
        try:
            # Search for PR references in commit messages
            result = subprocess.run(
                ['git', 'log', '--grep', '#[0-9]', '--oneline', '--', str(file_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            pr_references = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    # Extract PR numbers (e.g., #123)
                    matches = re.findall(r'#(\d+)', line)
                    pr_references.extend(matches)
            
            return {
                'related_prs': list(set(pr_references)),
                'pr_count': len(set(pr_references))
            }
        
        except subprocess.CalledProcessError as e:
            return {
                'related_prs': [],
                'error': f'Related work discovery failed: {e}'
            }
    
    def _analyze_temporal_patterns(self, file_path: Path) -> Dict:
        """Analyze change frequency and temporal patterns"""
        try:
            # Get commit dates for last 6 months
            lookback_months = self.config.get('commit_lookback_months', 6)
            since_date = (datetime.now() - timedelta(days=lookback_months * 30)).strftime('%Y-%m-%d')
            
            result = subprocess.run(
                ['git', 'log', '--format=%ad', '--date=short', f'--since={since_date}', '--', str(file_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            dates = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            
            if not dates:
                return {
                    'change_frequency': 'No recent changes',
                    'days_since_last_change': None
                }
            
            # Calculate days since last change
            last_change = datetime.strptime(dates[0], '%Y-%m-%d')
            days_since = (datetime.now() - last_change).days
            
            # Calculate average frequency
            total_days = (datetime.now() - datetime.strptime(since_date, '%Y-%m-%d')).days
            avg_days_between = total_days / len(dates) if dates else 0
            
            # Categorize frequency
            if avg_days_between < 7:
                frequency = 'Very High (multiple times per week)'
            elif avg_days_between < 30:
                frequency = 'High (weekly)'
            elif avg_days_between < 90:
                frequency = 'Medium (monthly)'
            else:
                frequency = 'Low (quarterly or less)'
            
            return {
                'change_frequency': frequency,
                'days_since_last_change': days_since,
                'avg_days_between_changes': round(avg_days_between, 1),
                'total_changes': len(dates)
            }
        
        except subprocess.CalledProcessError as e:
            return {
                'change_frequency': 'Unknown',
                'error': f'Temporal analysis failed: {e}'
            }


# Example usage for testing
if __name__ == '__main__':
    # Initialize validator
    validator = GitHistoryValidator(Path.cwd())
    
    # Test validation without context
    result = validator.validate_request({
        'files': ['src/auth.py'],
        'operation': 'security_review',
        'has_git_history_context': False
    })
    
    print(f"Status: {result.status}")
    print(f"Message: {result.message}")
    print(f"Quality Score: {result.quality_score}%")
    print(f"Required Actions: {result.required_actions}")
