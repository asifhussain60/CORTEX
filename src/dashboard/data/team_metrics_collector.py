"""
Team Metrics Collector

Analyzes team productivity from git history.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict

from src.dashboard.data.base_collector import BaseDataCollector


class TeamMetricsCollector(BaseDataCollector):
    """
    Collects team productivity metrics from git history.
    
    Analyzes:
    - Contributor activity (commits, lines added/removed)
    - Pull request metrics (opened, merged, time-to-merge)
    - Velocity trends (sprint-over-sprint)
    - Knowledge distribution (file ownership)
    - Bus factor analysis
    
    Data Source: CURRENT STATE ONLY - Real git history analysis.
    """
    
    def collect(self) -> Optional[Dict[str, Any]]:
        """
        Collect team metrics data.
        
        Returns:
            Dict with keys: contributors, velocity, pr_metrics, knowledge_distribution, summary
        """
        self.logger.info("Collecting team metrics data...")
        
        # Check if git repository
        if not (self.project_root / ".git").exists():
            self.logger.warning("Not a git repository")
            return None
        
        # Collect contributor data
        contributors = self._collect_contributors()
        
        # Calculate velocity metrics
        velocity = self._calculate_velocity()
        
        # Analyze knowledge distribution
        knowledge_dist = self._analyze_knowledge_distribution()
        
        # Calculate bus factor
        bus_factor = self._calculate_bus_factor(contributors)
        
        team_metrics = {
            "contributors": contributors,
            "velocity": velocity,
            "knowledge_distribution": knowledge_dist,
            "bus_factor": bus_factor,
            "summary": {
                "total_contributors": len(contributors),
                "active_contributors": len([c for c in contributors if c["commits"] > 5]),
                "total_commits": sum(c["commits"] for c in contributors),
                "avg_commits_per_contributor": sum(c["commits"] for c in contributors) / len(contributors) if contributors else 0
            }
        }
        
        self.logger.info(f"Team metrics collection complete. {len(contributors)} contributors analyzed")
        return team_metrics
    
    def _collect_contributors(self) -> List[Dict[str, Any]]:
        """
        Collect contributor statistics from git history.
        
        Returns:
            List of contributor data
        """
        contributors = []
        
        try:
            # Get all contributors with commit counts
            result = subprocess.run(
                ["git", "shortlog", "-sn", "--all", "--no-merges"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.warning("Failed to get git contributors")
                return contributors
            
            # Parse output
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                
                # Format: "   123  Author Name"
                match = re.match(r'\s*(\d+)\s+(.+)', line)
                if match:
                    commits = int(match.group(1))
                    name = match.group(2)
                    
                    # Get detailed stats for this contributor
                    stats = self._get_contributor_stats(name)
                    
                    contributors.append({
                        "name": name,
                        "commits": commits,
                        "lines_added": stats["lines_added"],
                        "lines_removed": stats["lines_removed"],
                        "files_changed": stats["files_changed"],
                        "first_commit": stats["first_commit"],
                        "last_commit": stats["last_commit"]
                    })
            
        except (subprocess.TimeoutExpired, Exception) as e:
            self.logger.error(f"Error collecting contributors: {e}")
        
        return contributors
    
    def _get_contributor_stats(self, author: str) -> Dict[str, Any]:
        """
        Get detailed statistics for a contributor.
        
        Args:
            author: Author name
            
        Returns:
            Dict with lines_added, lines_removed, files_changed, first_commit, last_commit
        """
        stats = {
            "lines_added": 0,
            "lines_removed": 0,
            "files_changed": 0,
            "first_commit": "unknown",
            "last_commit": "unknown"
        }
        
        try:
            # DISABLED: --numstat on large repos causes 60+ second hangs per contributor
            # Use lightweight commit-count-only approach instead
            # Lines added/removed stats are too expensive for dashboard collection
            
            # Skip detailed file stats - too slow
            stats["lines_added"] = 0
            stats["lines_removed"] = 0
            stats["files_changed"] = 0
        
        except Exception as e:
            self.logger.debug(f"Error getting stats for {author}: {e}")
            
            # Get first commit date
            result = subprocess.run(
                ["git", "log", "--author", author, "--reverse", "--format=%ai", "-1"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                stats["first_commit"] = result.stdout.strip().split()[0]
            
            # Get last commit date
            result = subprocess.run(
                ["git", "log", "--author", author, "--format=%ai", "-1"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                stats["last_commit"] = result.stdout.strip().split()[0]
                
        except (subprocess.TimeoutExpired, Exception) as e:
            self.logger.debug(f"Error getting stats for {author}: {e}")
        
        return stats
    
    def _calculate_velocity(self) -> Dict[str, Any]:
        """
        Calculate velocity metrics.
        
        Returns:
            Dict with commits_per_week, trend, recent_activity
        """
        velocity = {
            "commits_per_week": 0,
            "trend": "stable",
            "recent_activity": []
        }
        
        try:
            # Get commits from last 12 weeks, grouped by week
            weeks_data = []
            
            for week in range(12):
                since = datetime.now() - timedelta(weeks=week+1)
                until = datetime.now() - timedelta(weeks=week)
                
                result = subprocess.run(
                    ["git", "rev-list", "--count", "--all", "--no-merges",
                     f"--since={since.isoformat()}", f"--until={until.isoformat()}"],
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    count = int(result.stdout.strip()) if result.stdout.strip() else 0
                    weeks_data.append(count)
            
            if weeks_data:
                velocity["commits_per_week"] = sum(weeks_data) / len(weeks_data)
                velocity["recent_activity"] = list(reversed(weeks_data))
                
                # Determine trend
                if len(weeks_data) >= 4:
                    recent_avg = sum(weeks_data[:4]) / 4
                    older_avg = sum(weeks_data[4:8]) / 4
                    
                    if recent_avg > older_avg * 1.2:
                        velocity["trend"] = "increasing"
                    elif recent_avg < older_avg * 0.8:
                        velocity["trend"] = "decreasing"
                    else:
                        velocity["trend"] = "stable"
                        
        except (subprocess.TimeoutExpired, Exception) as e:
            self.logger.error(f"Error calculating velocity: {e}")
        
        return velocity
    
    def _analyze_knowledge_distribution(self) -> Dict[str, Any]:
        """
        Analyze knowledge distribution across files.
        
        Returns:
            Dict with file ownership data
        """
        knowledge_dist = {
            "files": [],
            "concentration_score": 0
        }
        
        try:
            # Get file list
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return knowledge_dist
            
            files = [f for f in result.stdout.strip().split('\n') if f.endswith('.py')][:50]  # Limit to 50 Python files
            
            for file_path in files:
                # Get primary contributor for this file
                result = subprocess.run(
                    ["git", "log", "--format=%an", "--", file_path],
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    authors = result.stdout.strip().split('\n')
                    # Count author frequency
                    author_counts = defaultdict(int)
                    for author in authors:
                        author_counts[author] += 1
                    
                    if author_counts:
                        primary_author = max(author_counts, key=author_counts.get)
                        ownership_pct = (author_counts[primary_author] / len(authors)) * 100
                        
                        knowledge_dist["files"].append({
                            "file": file_path,
                            "primary_owner": primary_author,
                            "ownership_percentage": int(ownership_pct),
                            "total_commits": len(authors)
                        })
            
            # Calculate concentration score (0-100, higher = more concentrated)
            if knowledge_dist["files"]:
                avg_ownership = sum(f["ownership_percentage"] for f in knowledge_dist["files"]) / len(knowledge_dist["files"])
                knowledge_dist["concentration_score"] = int(avg_ownership)
                
        except (subprocess.TimeoutExpired, Exception) as e:
            self.logger.error(f"Error analyzing knowledge distribution: {e}")
        
        return knowledge_dist
    
    def _calculate_bus_factor(self, contributors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate bus factor (minimum number of contributors whose absence would cripple the project).
        
        Args:
            contributors: List of contributor data
            
        Returns:
            Dict with bus_factor number and risk level
        """
        if not contributors:
            return {"factor": 0, "risk": "unknown"}
        
        # Sort contributors by commit count
        sorted_contributors = sorted(contributors, key=lambda x: x["commits"], reverse=True)
        total_commits = sum(c["commits"] for c in contributors)
        
        # Find minimum number of contributors that account for 50% of commits
        cumulative = 0
        bus_factor = 0
        
        for contributor in sorted_contributors:
            cumulative += contributor["commits"]
            bus_factor += 1
            if cumulative >= total_commits * 0.5:
                break
        
        # Determine risk level
        if bus_factor == 1:
            risk = "critical"
        elif bus_factor == 2:
            risk = "high"
        elif bus_factor <= 3:
            risk = "medium"
        else:
            risk = "low"
        
        return {
            "factor": bus_factor,
            "risk": risk,
            "top_contributors": [c["name"] for c in sorted_contributors[:bus_factor]]
        }
