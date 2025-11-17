"""
Tier 3: Context Intelligence Tests

Tests the context intelligence layer that provides development insights,
git analysis, file stability tracking, and proactive warnings.

Key Features Tested:
- Git repository analysis
- File stability and change patterns
- Session tracking and analytics
- Code health metrics
- Proactive warning generation
- Performance validation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# Mock Context Intelligence Implementation
# ============================================================================

class ChangeFrequency(Enum):
    """File change frequency categories"""
    STABLE = "stable"          # < 1 change/week
    MODERATE = "moderate"      # 1-5 changes/week
    VOLATILE = "volatile"      # > 5 changes/week
    HOT_SPOT = "hot_spot"      # > 10 changes/week


@dataclass
class GitCommit:
    """Represents a git commit"""
    commit_hash: str
    author: str
    timestamp: datetime
    message: str
    files_changed: List[str]
    lines_added: int
    lines_deleted: int


@dataclass
class FileStabilityMetrics:
    """Stability metrics for a file"""
    file_path: str
    total_changes: int
    change_frequency: ChangeFrequency
    last_modified: datetime
    avg_changes_per_week: float
    unique_authors: int
    bug_fix_count: int  # Commits with "fix" in message
    refactor_count: int  # Commits with "refactor" in message
    stability_score: float  # 0.0 (volatile) to 1.0 (stable)


@dataclass
class SessionMetrics:
    """Development session metrics"""
    session_id: str
    start_time: datetime
    end_time: datetime
    duration_minutes: float
    files_modified: List[str]
    commits_made: int
    tests_run: int
    tests_passed: int
    test_coverage_change: float  # +/- percentage
    focus_areas: List[str]  # e.g., ['authentication', 'api', 'tests']


@dataclass
class CodeHealthMetric:
    """Code health metric for a module or file"""
    target: str  # file or module path
    metric_type: str  # 'complexity', 'coverage', 'duplication', 'debt'
    current_value: float
    threshold: float
    status: str  # 'healthy', 'warning', 'critical'
    trend: str  # 'improving', 'stable', 'degrading'
    recommendation: Optional[str] = None


@dataclass
class ProactiveWarning:
    """Proactive warning about potential issues"""
    warning_id: str
    severity: str  # 'info', 'warning', 'critical'
    category: str  # 'stability', 'health', 'performance', 'security'
    title: str
    description: str
    affected_files: List[str]
    recommended_action: str
    confidence: float


class ContextIntelligence:
    """Mock context intelligence for testing Tier 3 functionality"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.git_commits: List[GitCommit] = []
        self.file_stability_cache: Dict[str, FileStabilityMetrics] = {}
        self.sessions: List[SessionMetrics] = []
        self.health_metrics: Dict[str, CodeHealthMetric] = {}
        self.warnings: List[ProactiveWarning] = []
    
    # ========================================================================
    # Git Analysis
    # ========================================================================
    
    def analyze_git_history(self, since_date: Optional[datetime] = None,
                           file_filter: Optional[str] = None) -> Dict[str, Any]:
        """Analyze git history for patterns and insights"""
        relevant_commits = self.git_commits
        
        # Filter by date
        if since_date:
            relevant_commits = [c for c in relevant_commits if c.timestamp >= since_date]
        
        # Filter by file
        if file_filter:
            relevant_commits = [c for c in relevant_commits 
                              if any(file_filter in f for f in c.files_changed)]
        
        if not relevant_commits:
            return {
                'total_commits': 0,
                'total_files_changed': 0,
                'total_lines_added': 0,
                'total_lines_deleted': 0,
                'unique_authors': 0,
                'most_changed_files': [],
                'busiest_days': []
            }
        
        # Calculate statistics
        all_files = []
        for commit in relevant_commits:
            all_files.extend(commit.files_changed)
        
        file_change_counts = {}
        for file in all_files:
            file_change_counts[file] = file_change_counts.get(file, 0) + 1
        
        most_changed = sorted(file_change_counts.items(), 
                             key=lambda x: x[1], reverse=True)[:10]
        
        unique_authors = len(set(c.author for c in relevant_commits))
        
        return {
            'total_commits': len(relevant_commits),
            'total_files_changed': len(set(all_files)),
            'total_lines_added': sum(c.lines_added for c in relevant_commits),
            'total_lines_deleted': sum(c.lines_deleted for c in relevant_commits),
            'unique_authors': unique_authors,
            'most_changed_files': most_changed,
            'commits_per_author': self._commits_per_author(relevant_commits)
        }
    
    def get_file_change_velocity(self, file_path: str, days: int = 30) -> float:
        """Calculate rate of change for a file (changes per day)"""
        since_date = datetime.now() - timedelta(days=days)
        
        relevant_commits = [c for c in self.git_commits 
                           if c.timestamp >= since_date 
                           and file_path in c.files_changed]
        
        if days == 0:
            return 0.0
        
        return len(relevant_commits) / days
    
    def identify_co_change_patterns(self, min_occurrences: int = 3) -> List[Tuple[str, str, int]]:
        """Identify files that frequently change together"""
        co_changes = {}
        
        for commit in self.git_commits:
            if len(commit.files_changed) > 1:
                # Sort to ensure consistent ordering
                files = sorted(commit.files_changed)
                for i in range(len(files)):
                    for j in range(i + 1, len(files)):
                        pair = (files[i], files[j])
                        co_changes[pair] = co_changes.get(pair, 0) + 1
        
        # Filter by minimum occurrences
        results = [(f1, f2, count) for (f1, f2), count in co_changes.items()
                   if count >= min_occurrences]
        
        # Sort by frequency descending
        results.sort(key=lambda x: x[2], reverse=True)
        
        return results
    
    # ========================================================================
    # File Stability Analysis
    # ========================================================================
    
    def calculate_file_stability(self, file_path: str) -> FileStabilityMetrics:
        """Calculate comprehensive stability metrics for a file"""
        # Check cache
        if file_path in self.file_stability_cache:
            return self.file_stability_cache[file_path]
        
        # Get commits affecting this file
        file_commits = [c for c in self.git_commits if file_path in c.files_changed]
        
        if not file_commits:
            # New or unchanged file
            metrics = FileStabilityMetrics(
                file_path=file_path,
                total_changes=0,
                change_frequency=ChangeFrequency.STABLE,
                last_modified=datetime.now(),
                avg_changes_per_week=0.0,
                unique_authors=0,
                bug_fix_count=0,
                refactor_count=0,
                stability_score=1.0
            )
            self.file_stability_cache[file_path] = metrics
            return metrics
        
        # Calculate metrics
        total_changes = len(file_commits)
        last_modified = max(c.timestamp for c in file_commits)
        unique_authors = len(set(c.author for c in file_commits))
        
        # Calculate average changes per week
        if file_commits:
            earliest = min(c.timestamp for c in file_commits)
            days_span = (datetime.now() - earliest).days
            weeks_span = max(days_span / 7, 1)
            avg_changes_per_week = total_changes / weeks_span
        else:
            avg_changes_per_week = 0.0
        
        # Classify change frequency
        if avg_changes_per_week > 10:
            frequency = ChangeFrequency.HOT_SPOT
        elif avg_changes_per_week > 5:
            frequency = ChangeFrequency.VOLATILE
        elif avg_changes_per_week > 1:
            frequency = ChangeFrequency.MODERATE
        else:
            frequency = ChangeFrequency.STABLE
        
        # Count bug fixes and refactors
        bug_fix_count = sum(1 for c in file_commits if 'fix' in c.message.lower())
        refactor_count = sum(1 for c in file_commits if 'refactor' in c.message.lower())
        
        # Calculate stability score (0.0 = volatile, 1.0 = stable)
        # Factors: low change frequency, few authors, few bug fixes
        stability_score = 1.0
        stability_score -= min(avg_changes_per_week / 20, 0.5)  # Frequency penalty
        stability_score -= min(unique_authors / 10, 0.2)  # Multiple authors penalty
        stability_score -= min(bug_fix_count / 10, 0.3)  # Bug fix penalty
        stability_score = max(0.0, min(1.0, stability_score))
        
        metrics = FileStabilityMetrics(
            file_path=file_path,
            total_changes=total_changes,
            change_frequency=frequency,
            last_modified=last_modified,
            avg_changes_per_week=avg_changes_per_week,
            unique_authors=unique_authors,
            bug_fix_count=bug_fix_count,
            refactor_count=refactor_count,
            stability_score=stability_score
        )
        
        self.file_stability_cache[file_path] = metrics
        return metrics
    
    def find_unstable_files(self, min_changes: int = 10) -> List[FileStabilityMetrics]:
        """Find files that are frequently changing (potential hot spots)"""
        all_files = set()
        for commit in self.git_commits:
            all_files.update(commit.files_changed)
        
        unstable = []
        for file_path in all_files:
            metrics = self.calculate_file_stability(file_path)
            if (metrics.total_changes >= min_changes and 
                metrics.change_frequency in [ChangeFrequency.VOLATILE, ChangeFrequency.HOT_SPOT]):
                unstable.append(metrics)
        
        # Sort by instability (lowest stability score first)
        unstable.sort(key=lambda m: m.stability_score)
        
        return unstable
    
    # ========================================================================
    # Session Tracking
    # ========================================================================
    
    def track_session(self, session: SessionMetrics) -> str:
        """Track a development session"""
        self.sessions.append(session)
        return session.session_id
    
    def get_session_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get analytics for recent sessions"""
        since_date = datetime.now() - timedelta(days=days)
        recent_sessions = [s for s in self.sessions if s.start_time >= since_date]
        
        if not recent_sessions:
            return {
                'total_sessions': 0,
                'total_duration_hours': 0.0,
                'avg_session_duration_minutes': 0.0,
                'total_commits': 0,
                'total_files_modified': 0,
                'test_success_rate': 0.0,
                'most_active_areas': []
            }
        
        total_duration = sum(s.duration_minutes for s in recent_sessions)
        total_commits = sum(s.commits_made for s in recent_sessions)
        
        all_files = []
        for session in recent_sessions:
            all_files.extend(session.files_modified)
        
        # Calculate test success rate
        total_tests = sum(s.tests_run for s in recent_sessions)
        passed_tests = sum(s.tests_passed for s in recent_sessions)
        test_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0.0
        
        # Find most active areas
        all_areas = []
        for session in recent_sessions:
            all_areas.extend(session.focus_areas)
        
        area_counts = {}
        for area in all_areas:
            area_counts[area] = area_counts.get(area, 0) + 1
        
        most_active = sorted(area_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_sessions': len(recent_sessions),
            'total_duration_hours': total_duration / 60,
            'avg_session_duration_minutes': total_duration / len(recent_sessions),
            'total_commits': total_commits,
            'total_files_modified': len(set(all_files)),
            'test_success_rate': test_success_rate,
            'most_active_areas': most_active
        }
    
    # ========================================================================
    # Code Health Metrics
    # ========================================================================
    
    def track_health_metric(self, metric: CodeHealthMetric) -> None:
        """Track a code health metric"""
        self.health_metrics[f"{metric.target}_{metric.metric_type}"] = metric
    
    def get_health_status(self, target: Optional[str] = None) -> Dict[str, Any]:
        """Get overall health status"""
        metrics = list(self.health_metrics.values())
        
        if target:
            metrics = [m for m in metrics if target in m.target]
        
        if not metrics:
            return {
                'status': 'unknown',
                'healthy_count': 0,
                'warning_count': 0,
                'critical_count': 0,
                'overall_score': 0.0
            }
        
        healthy = sum(1 for m in metrics if m.status == 'healthy')
        warning = sum(1 for m in metrics if m.status == 'warning')
        critical = sum(1 for m in metrics if m.status == 'critical')
        
        # Calculate overall score (0-100)
        total = len(metrics)
        score = (healthy * 100 + warning * 50 + critical * 0) / total if total > 0 else 0.0
        
        # Determine overall status
        if critical > 0:
            status = 'critical'
        elif warning > healthy:
            status = 'warning'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'healthy_count': healthy,
            'warning_count': warning,
            'critical_count': critical,
            'overall_score': score,
            'total_metrics': total
        }
    
    def find_degrading_metrics(self) -> List[CodeHealthMetric]:
        """Find metrics that are degrading"""
        return [m for m in self.health_metrics.values() if m.trend == 'degrading']
    
    # ========================================================================
    # Proactive Warnings
    # ========================================================================
    
    def generate_proactive_warnings(self) -> List[ProactiveWarning]:
        """Generate proactive warnings based on context analysis"""
        self.warnings = []
        
        # Warning 1: Check for hot spot files
        unstable = self.find_unstable_files(min_changes=15)
        if unstable:
            for file_metrics in unstable[:3]:  # Top 3 most unstable
                self.warnings.append(ProactiveWarning(
                    warning_id=f"hotspot_{file_metrics.file_path}",
                    severity='warning',
                    category='stability',
                    title=f"File Hot Spot: {file_metrics.file_path}",
                    description=f"File has {file_metrics.total_changes} changes with {file_metrics.bug_fix_count} bug fixes. Consider refactoring.",
                    affected_files=[file_metrics.file_path],
                    recommended_action="Review file for complexity issues, consider splitting into smaller modules",
                    confidence=0.85
                ))
        
        # Warning 2: Check for degrading health metrics
        degrading = self.find_degrading_metrics()
        if degrading:
            critical_degrading = [m for m in degrading if m.status == 'critical']
            if critical_degrading:
                self.warnings.append(ProactiveWarning(
                    warning_id="health_degrading",
                    severity='critical',
                    category='health',
                    title="Code Health Degradation Detected",
                    description=f"{len(critical_degrading)} critical metrics are degrading",
                    affected_files=[m.target for m in critical_degrading],
                    recommended_action="Address critical health issues before they worsen",
                    confidence=0.95
                ))
        
        # Warning 3: Check session test success rate
        recent_analytics = self.get_session_analytics(days=7)
        if recent_analytics['test_success_rate'] < 80:
            self.warnings.append(ProactiveWarning(
                warning_id="low_test_success",
                severity='warning',
                category='health',
                title="Low Test Success Rate",
                description=f"Test success rate is {recent_analytics['test_success_rate']:.1f}% (target: 95%)",
                affected_files=[],
                recommended_action="Review failing tests and fix underlying issues",
                confidence=0.90
            ))
        
        return self.warnings
    
    def get_warnings_by_severity(self, severity: str) -> List[ProactiveWarning]:
        """Get warnings filtered by severity"""
        return [w for w in self.warnings if w.severity == severity]
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def _commits_per_author(self, commits: List[GitCommit]) -> Dict[str, int]:
        """Count commits per author"""
        counts = {}
        for commit in commits:
            counts[commit.author] = counts.get(commit.author, 0) + 1
        return counts
    
    def add_git_commit(self, commit: GitCommit) -> None:
        """Add a git commit to the history"""
        self.git_commits.append(commit)


# ============================================================================
# Test: Git Analysis
# ============================================================================

class TestGitAnalysis:
    """Test git repository analysis functionality"""
    
    def test_analyze_git_history(self):
        """Should analyze git history and return statistics"""
        ci = ContextIntelligence()
        
        # Add some commits
        ci.add_git_commit(GitCommit(
            "abc123", "user1", datetime.now(), "feat: add feature",
            ["src/feature.py", "tests/test_feature.py"], 50, 10
        ))
        ci.add_git_commit(GitCommit(
            "def456", "user2", datetime.now(), "fix: bug fix",
            ["src/feature.py"], 5, 2
        ))
        
        analysis = ci.analyze_git_history()
        
        assert analysis['total_commits'] == 2
        assert analysis['total_files_changed'] == 2
        assert analysis['total_lines_added'] == 55
        assert analysis['total_lines_deleted'] == 12
        assert analysis['unique_authors'] == 2
    
    def test_analyze_git_history_with_date_filter(self):
        """Should filter commits by date"""
        ci = ContextIntelligence()
        
        old_commit = GitCommit(
            "old123", "user1", datetime.now() - timedelta(days=60),
            "old commit", ["old_file.py"], 10, 5
        )
        recent_commit = GitCommit(
            "new456", "user1", datetime.now(),
            "recent commit", ["new_file.py"], 20, 10
        )
        
        ci.add_git_commit(old_commit)
        ci.add_git_commit(recent_commit)
        
        # Analyze last 30 days
        since = datetime.now() - timedelta(days=30)
        analysis = ci.analyze_git_history(since_date=since)
        
        assert analysis['total_commits'] == 1
        assert "new_file.py" in [f for f, _ in analysis['most_changed_files']]
    
    def test_get_file_change_velocity(self):
        """Should calculate file change velocity"""
        ci = ContextIntelligence()
        
        # Add commits for a file over 30 days
        for i in range(15):
            ci.add_git_commit(GitCommit(
                f"commit{i}", "user1", 
                datetime.now() - timedelta(days=i*2),
                f"change {i}", ["volatile_file.py"], 10, 5
            ))
        
        velocity = ci.get_file_change_velocity("volatile_file.py", days=30)
        
        assert velocity == 15 / 30  # 0.5 changes per day
    
    def test_identify_co_change_patterns(self):
        """Should identify files that change together"""
        ci = ContextIntelligence()
        
        # Add commits where service and test change together
        for i in range(5):
            ci.add_git_commit(GitCommit(
                f"commit{i}", "user1", datetime.now(),
                f"update {i}", 
                ["src/service.py", "tests/test_service.py"], 
                10, 5
            ))
        
        patterns = ci.identify_co_change_patterns(min_occurrences=3)
        
        assert len(patterns) > 0
        assert patterns[0][0] == "src/service.py"
        assert patterns[0][1] == "tests/test_service.py"
        assert patterns[0][2] == 5  # Co-changed 5 times


# ============================================================================
# Test: File Stability
# ============================================================================

class TestFileStability:
    """Test file stability analysis"""
    
    def test_calculate_file_stability_stable(self):
        """Should identify stable files"""
        ci = ContextIntelligence()
        
        # Add few commits for a file
        ci.add_git_commit(GitCommit(
            "c1", "user1", datetime.now() - timedelta(days=90),
            "initial", ["stable_file.py"], 100, 0
        ))
        ci.add_git_commit(GitCommit(
            "c2", "user1", datetime.now() - timedelta(days=60),
            "minor update", ["stable_file.py"], 5, 2
        ))
        
        metrics = ci.calculate_file_stability("stable_file.py")
        
        assert metrics.change_frequency == ChangeFrequency.STABLE
        assert metrics.total_changes == 2
        assert metrics.stability_score > 0.7
    
    def test_calculate_file_stability_volatile(self):
        """Should identify volatile files"""
        ci = ContextIntelligence()
        
        # Add many commits for a file
        for i in range(20):
            ci.add_git_commit(GitCommit(
                f"c{i}", f"user{i%3}", 
                datetime.now() - timedelta(days=i),
                f"change {i}", ["volatile_file.py"], 10, 5
            ))
        
        metrics = ci.calculate_file_stability("volatile_file.py")
        
        assert metrics.change_frequency in [ChangeFrequency.VOLATILE, ChangeFrequency.HOT_SPOT]
        assert metrics.total_changes == 20
        assert metrics.stability_score < 0.5
    
    def test_bug_fix_count_affects_stability(self):
        """Should lower stability score for files with many bug fixes"""
        ci = ContextIntelligence()
        
        # Add commits with bug fixes
        for i in range(10):
            ci.add_git_commit(GitCommit(
                f"c{i}", "user1", datetime.now() - timedelta(days=i*7),
                f"fix: bug fix {i}", ["buggy_file.py"], 5, 3
            ))
        
        metrics = ci.calculate_file_stability("buggy_file.py")
        
        assert metrics.bug_fix_count == 10
        assert metrics.stability_score < 0.6  # Penalty for bug fixes
    
    def test_find_unstable_files(self):
        """Should find files that are frequently changing"""
        ci = ContextIntelligence()
        
        # Create stable file
        for i in range(5):
            ci.add_git_commit(GitCommit(
                f"s{i}", "user1", datetime.now() - timedelta(days=i*30),
                f"stable {i}", ["stable.py"], 5, 2
            ))
        
        # Create volatile file
        for i in range(20):
            ci.add_git_commit(GitCommit(
                f"v{i}", "user1", datetime.now() - timedelta(days=i),
                f"volatile {i}", ["volatile.py"], 10, 5
            ))
        
        unstable = ci.find_unstable_files(min_changes=10)
        
        assert len(unstable) == 1
        assert unstable[0].file_path == "volatile.py"


# ============================================================================
# Test: Session Tracking
# ============================================================================

class TestSessionTracking:
    """Test development session tracking"""
    
    def test_track_session(self):
        """Should track development sessions"""
        ci = ContextIntelligence()
        
        session = SessionMetrics(
            session_id="session_001",
            start_time=datetime.now() - timedelta(hours=2),
            end_time=datetime.now(),
            duration_minutes=120.0,
            files_modified=["src/feature.py", "tests/test_feature.py"],
            commits_made=3,
            tests_run=50,
            tests_passed=48,
            test_coverage_change=2.5,
            focus_areas=["authentication", "api"]
        )
        
        session_id = ci.track_session(session)
        
        assert session_id == "session_001"
        assert len(ci.sessions) == 1
    
    def test_get_session_analytics(self):
        """Should calculate session analytics"""
        ci = ContextIntelligence()
        
        # Add multiple sessions
        for i in range(3):
            ci.track_session(SessionMetrics(
                session_id=f"session_{i}",
                start_time=datetime.now() - timedelta(days=i),
                end_time=datetime.now() - timedelta(days=i) + timedelta(hours=1),
                duration_minutes=60.0,
                files_modified=[f"file_{i}.py"],
                commits_made=2,
                tests_run=20,
                tests_passed=19,
                test_coverage_change=1.0,
                focus_areas=["feature"]
            ))
        
        analytics = ci.get_session_analytics(days=7)
        
        assert analytics['total_sessions'] == 3
        assert analytics['total_duration_hours'] == 3.0
        assert analytics['avg_session_duration_minutes'] == 60.0
        assert analytics['total_commits'] == 6
        assert analytics['test_success_rate'] > 90.0
    
    def test_session_focus_areas(self):
        """Should identify most active focus areas"""
        ci = ContextIntelligence()
        
        ci.track_session(SessionMetrics(
            "s1", datetime.now(), datetime.now(), 60.0, [], 1, 10, 10, 0.0,
            focus_areas=["authentication", "api"]
        ))
        ci.track_session(SessionMetrics(
            "s2", datetime.now(), datetime.now(), 60.0, [], 1, 10, 10, 0.0,
            focus_areas=["authentication", "tests"]
        ))
        
        analytics = ci.get_session_analytics(days=7)
        
        assert len(analytics['most_active_areas']) > 0
        # Authentication should be most active (appears in both)
        assert analytics['most_active_areas'][0][0] == "authentication"
        assert analytics['most_active_areas'][0][1] == 2


# ============================================================================
# Test: Code Health Metrics
# ============================================================================

class TestCodeHealthMetrics:
    """Test code health tracking"""
    
    def test_track_health_metric(self):
        """Should track code health metrics"""
        ci = ContextIntelligence()
        
        metric = CodeHealthMetric(
            target="src/service.py",
            metric_type="complexity",
            current_value=12.5,
            threshold=10.0,
            status="warning",
            trend="stable",
            recommendation="Consider refactoring complex methods"
        )
        
        ci.track_health_metric(metric)
        
        assert len(ci.health_metrics) == 1
    
    def test_get_health_status_overall(self):
        """Should calculate overall health status"""
        ci = ContextIntelligence()
        
        ci.track_health_metric(CodeHealthMetric(
            "file1.py", "complexity", 5.0, 10.0, "healthy", "stable"
        ))
        ci.track_health_metric(CodeHealthMetric(
            "file2.py", "coverage", 75.0, 80.0, "warning", "stable"
        ))
        ci.track_health_metric(CodeHealthMetric(
            "file3.py", "duplication", 15.0, 5.0, "critical", "degrading"
        ))
        
        status = ci.get_health_status()
        
        assert status['healthy_count'] == 1
        assert status['warning_count'] == 1
        assert status['critical_count'] == 1
        assert status['status'] == 'critical'
    
    def test_find_degrading_metrics(self):
        """Should find metrics that are degrading"""
        ci = ContextIntelligence()
        
        ci.track_health_metric(CodeHealthMetric(
            "file1.py", "complexity", 15.0, 10.0, "warning", "degrading"
        ))
        ci.track_health_metric(CodeHealthMetric(
            "file2.py", "coverage", 85.0, 80.0, "healthy", "stable"
        ))
        
        degrading = ci.find_degrading_metrics()
        
        assert len(degrading) == 1
        assert degrading[0].target == "file1.py"


# ============================================================================
# Test: Proactive Warnings
# ============================================================================

class TestProactiveWarnings:
    """Test proactive warning generation"""
    
    def test_generate_warnings_for_hot_spots(self):
        """Should generate warnings for file hot spots"""
        ci = ContextIntelligence()
        
        # Create hot spot file
        for i in range(20):
            ci.add_git_commit(GitCommit(
                f"c{i}", "user1", datetime.now() - timedelta(days=i),
                f"fix: bug {i}", ["hotspot.py"], 10, 5
            ))
        
        warnings = ci.generate_proactive_warnings()
        
        assert len(warnings) > 0
        assert any(w.category == 'stability' for w in warnings)
        assert any('hotspot.py' in w.affected_files for w in warnings)
    
    def test_generate_warnings_for_degrading_health(self):
        """Should generate warnings for degrading health"""
        ci = ContextIntelligence()
        
        ci.track_health_metric(CodeHealthMetric(
            "bad_file.py", "complexity", 50.0, 10.0, "critical", "degrading"
        ))
        
        warnings = ci.generate_proactive_warnings()
        
        critical_warnings = [w for w in warnings if w.severity == 'critical']
        assert len(critical_warnings) > 0
    
    def test_generate_warnings_for_low_test_success(self):
        """Should generate warnings for low test success rate"""
        ci = ContextIntelligence()
        
        # Add sessions with low test success
        ci.track_session(SessionMetrics(
            "s1", datetime.now(), datetime.now(), 60.0, [], 1, 
            100, 60, 0.0, []  # Only 60% passed
        ))
        
        warnings = ci.generate_proactive_warnings()
        
        assert any(w.category == 'health' and 'Test' in w.title for w in warnings)
    
    def test_filter_warnings_by_severity(self):
        """Should filter warnings by severity"""
        ci = ContextIntelligence()
        
        ci.warnings = [
            ProactiveWarning("w1", "critical", "health", "Critical Issue", "", [], "", 0.9),
            ProactiveWarning("w2", "warning", "stability", "Warning Issue", "", [], "", 0.8),
            ProactiveWarning("w3", "info", "performance", "Info Issue", "", [], "", 0.7)
        ]
        
        critical = ci.get_warnings_by_severity("critical")
        
        assert len(critical) == 1
        assert critical[0].warning_id == "w1"


# ============================================================================
# Test: Performance
# ============================================================================

class TestPerformance:
    """Test performance of context intelligence operations"""
    
    def test_git_analysis_performance(self):
        """Should analyze 1000 commits quickly (<100ms)"""
        import time
        
        ci = ContextIntelligence()
        
        # Add 1000 commits
        for i in range(1000):
            ci.add_git_commit(GitCommit(
                f"commit{i}", f"user{i%10}", 
                datetime.now() - timedelta(days=i),
                f"message {i}", [f"file_{i%100}.py"], 10, 5
            ))
        
        start = time.time()
        analysis = ci.analyze_git_history()
        end = time.time()
        
        assert (end - start) * 1000 < 100  # Should be < 100ms
        assert analysis['total_commits'] == 1000
    
    def test_stability_calculation_performance(self):
        """Should calculate stability quickly"""
        import time
        
        ci = ContextIntelligence()
        
        # Add commits
        for i in range(100):
            ci.add_git_commit(GitCommit(
                f"c{i}", "user1", datetime.now() - timedelta(days=i),
                f"msg {i}", ["test_file.py"], 10, 5
            ))
        
        start = time.time()
        metrics = ci.calculate_file_stability("test_file.py")
        end = time.time()
        
        assert (end - start) * 1000 < 50  # Should be < 50ms


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
