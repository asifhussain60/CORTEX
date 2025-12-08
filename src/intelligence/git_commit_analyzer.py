"""
Git Commit Pattern Analyzer

Analyzes git commit history to extract:
- Development themes (feature, bugfix, refactor, docs, test)
- Feature evolution patterns
- Active development areas
- Team velocity metrics

Includes knowledge graph integration to capture successful patterns.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
License: Proprietary - Source-Available
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import subprocess
import json


@dataclass
class CommitTheme:
    """Represents a development theme extracted from commits."""
    theme: str
    count: int
    percentage: float
    keywords: List[str]
    example_commits: List[str]


@dataclass
class FeatureEvolution:
    """Tracks evolution of a feature across commits."""
    feature_name: str
    stages: List[str]  # e.g., ["adding", "fixing", "optimizing"]
    commit_count: int
    first_commit_date: datetime
    last_commit_date: datetime
    files_touched: Set[str]


@dataclass
class DevelopmentNarrative:
    """Generated narrative about recent development activity."""
    summary: str
    top_themes: List[CommitTheme]
    active_areas: List[str]
    feature_evolutions: List[FeatureEvolution]
    velocity_metrics: Dict[str, int]
    time_period: str


class GitCommitAnalyzer:
    """Analyzes git commit patterns to extract development insights."""
    
    # Keyword patterns for theme classification
    THEME_PATTERNS = {
        'feature': [
            r'\b(add|implement|create|new|feature|introduce)\b',
            r'\b(feat|FT|FEAT)\b'
        ],
        'bugfix': [
            r'\b(fix|bug|issue|error|crash|resolve|patch)\b',
            r'\b(bug|BUG|FIX)\b'
        ],
        'refactor': [
            r'\b(refactor|improve|optimize|clean|restructure|simplify)\b',
            r'\b(refactor|REFACTOR)\b'
        ],
        'docs': [
            r'\b(doc|docs|documentation|readme|comment)\b',
            r'\b(docs|DOCS|DOC)\b'
        ],
        'test': [
            r'\b(test|tests|testing|spec|coverage|tdd)\b',
            r'\b(test|TEST|TDD)\b'
        ],
        'chore': [
            r'\b(chore|build|ci|cd|config|merge|update)\b',
            r'\b(chore|CHORE)\b'
        ]
    }
    
    # Feature evolution stage patterns
    EVOLUTION_STAGES = {
        'adding': [r'\b(add|implement|create|new|initial)\b'],
        'fixing': [r'\b(fix|bug|issue|resolve|patch)\b'],
        'optimizing': [r'(optimiz|improv|enhanc|refactor|performance)'],
        'deprecating': [r'\b(deprecate|remove|delete|obsolete)\b']
    }
    
    def __init__(self, repo_path: Path):
        """Initialize analyzer with repository path."""
        self.repo_path = Path(repo_path)
        self._validate_git_repo()
    
    def _validate_git_repo(self) -> None:
        """Validate that path is a git repository."""
        git_dir = self.repo_path / '.git'
        if not git_dir.exists():
            raise ValueError(f"Not a git repository: {self.repo_path}")
    
    def analyze(
        self,
        days: int = 90,
        limit: int = 100,
        branch: str = "HEAD"
    ) -> DevelopmentNarrative:
        """
        Analyze commit patterns over specified time period.
        
        Args:
            days: Number of days to look back (default: 90)
            limit: Maximum commits to analyze (default: 100)
            branch: Git branch to analyze (default: HEAD)
        
        Returns:
            DevelopmentNarrative with extracted insights
        """
        # Get commits from git log
        commits = self._get_commits(days, limit, branch)
        
        if not commits:
            return self._empty_narrative(days)
        
        # Extract themes from commit messages
        themes = self._extract_themes(commits)
        
        # Identify active development areas
        active_areas = self._identify_active_areas(commits)
        
        # Track feature evolutions
        evolutions = self._track_feature_evolutions(commits)
        
        # Calculate velocity metrics
        velocity = self._calculate_velocity(commits, days)
        
        # Generate narrative summary
        summary = self._generate_summary(themes, active_areas, evolutions, velocity, days)
        
        # Update knowledge graph with patterns
        self._update_knowledge_graph(commits, themes, evolutions, active_areas)
        
        return DevelopmentNarrative(
            summary=summary,
            top_themes=themes[:3],
            active_areas=active_areas[:5],
            feature_evolutions=evolutions[:5],
            velocity_metrics=velocity,
            time_period=f"last {days} days"
        )
    
    def _get_commits(self, days: int, limit: int, branch: str) -> List[Dict[str, str]]:
        """Fetch commit history from git log."""
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cmd = [
            'git', 'log',
            branch,
            f'--since={since_date}',
            f'--max-count={limit}',
            '--pretty=format:%H|%an|%ae|%ai|%s',
            '--name-only'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=True
            )
            
            return self._parse_git_log(result.stdout)
        
        except subprocess.CalledProcessError as e:
            print(f"Warning: Git log failed: {e}")
            return []
    
    def _parse_git_log(self, log_output: str) -> List[Dict[str, str]]:
        """Parse git log output into structured commit data."""
        commits = []
        current_commit = None
        files = []
        
        for line in log_output.split('\n'):
            line = line.strip()
            
            if '|' in line:
                # Commit header line
                if current_commit:
                    current_commit['files'] = files
                    commits.append(current_commit)
                    files = []
                
                parts = line.split('|')
                if len(parts) == 5:
                    current_commit = {
                        'hash': parts[0],
                        'author': parts[1],
                        'email': parts[2],
                        'date': parts[3],
                        'message': parts[4]
                    }
            elif line and current_commit:
                # File path line
                files.append(line)
        
        # Add last commit
        if current_commit:
            current_commit['files'] = files
            commits.append(current_commit)
        
        return commits
    
    def _extract_themes(self, commits: List[Dict[str, str]]) -> List[CommitTheme]:
        """Extract development themes from commit messages."""
        theme_counts = Counter()
        theme_examples = defaultdict(list)
        theme_keywords = defaultdict(set)
        
        for commit in commits:
            message = commit['message'].lower()
            matched = False
            
            for theme, patterns in self.THEME_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, message, re.IGNORECASE):
                        theme_counts[theme] += 1
                        if len(theme_examples[theme]) < 3:
                            theme_examples[theme].append(commit['message'][:80])
                        
                        # Extract keywords
                        words = re.findall(r'\b\w+\b', message)
                        theme_keywords[theme].update(words[:5])
                        matched = True
                        break
                
                if matched:
                    break
            
            if not matched:
                theme_counts['other'] += 1
        
        # Convert to CommitTheme objects
        total_commits = len(commits)
        themes = []
        
        for theme, count in theme_counts.most_common():
            themes.append(CommitTheme(
                theme=theme,
                count=count,
                percentage=round((count / total_commits) * 100, 1),
                keywords=list(theme_keywords.get(theme, []))[:5],
                example_commits=theme_examples.get(theme, [])
            ))
        
        return themes
    
    def _identify_active_areas(self, commits: List[Dict[str, str]]) -> List[str]:
        """Identify active development areas from changed files."""
        file_changes = Counter()
        
        for commit in commits:
            for file_path in commit.get('files', []):
                # Extract directory/module name
                parts = Path(file_path).parts
                if len(parts) > 1:
                    area = parts[0] if parts[0] != '.' else parts[1]
                    file_changes[area] += 1
        
        return [area for area, _ in file_changes.most_common(5)]
    
    def _track_feature_evolutions(self, commits: List[Dict[str, str]]) -> List[FeatureEvolution]:
        """Track evolution of features across commits."""
        feature_data = defaultdict(lambda: {
            'stages': [],
            'commits': 0,
            'first_date': None,
            'last_date': None,
            'files': set()
        })
        
        for commit in commits:
            message = commit['message'].lower()
            
            # Parse date from git format: "2025-12-08 05:57:37 -0500"
            try:
                date_str = commit['date'].split('.')[0]  # Remove microseconds if present
                date_str = date_str.split('+')[0].split('-0')[0].strip()  # Remove timezone
                date = datetime.fromisoformat(date_str)
            except (ValueError, IndexError) as e:
                # Fallback to current date if parsing fails
                date = datetime.now()
            
            # Extract feature name (simplified - could be more sophisticated)
            feature_match = re.search(r'\\b(feature|module|component|service)\\s+(\\w+)', message, re.IGNORECASE)
            if feature_match:
                feature_name = feature_match.group(2)
            else:
                # Look for capitalized words in original message (not lowercased)
                words = re.findall(r'\\b[A-Z][a-z]+\\b', commit['message'])
                # Filter out common words
                significant_words = [w for w in words if w not in ['Add', 'Fix', 'Update', 'Commit', 'New', 'The', 'A', 'An', 'Optimize']]
                feature_name = significant_words[0] if significant_words else None
            
            if not feature_name:
                continue
            
            # Determine stage
            for stage, patterns in self.EVOLUTION_STAGES.items():
                for pattern in patterns:
                    if re.search(pattern, message, re.IGNORECASE):
                        feature_data[feature_name]['stages'].append(stage)
                        break
            
            feature_data[feature_name]['commits'] += 1
            
            if not feature_data[feature_name]['first_date']:
                feature_data[feature_name]['first_date'] = date
            feature_data[feature_name]['last_date'] = date
            
            feature_data[feature_name]['files'].update(commit.get('files', []))
        
        # Convert to FeatureEvolution objects
        evolutions = []
        for feature_name, data in feature_data.items():
            if data['commits'] >= 2:  # Only features with multiple commits
                evolutions.append(FeatureEvolution(
                    feature_name=feature_name,
                    stages=list(dict.fromkeys(data['stages'])),  # Remove duplicates, preserve order
                    commit_count=data['commits'],
                    first_commit_date=data['first_date'],
                    last_commit_date=data['last_date'],
                    files_touched=data['files']
                ))
        
        # Sort by commit count
        evolutions.sort(key=lambda x: x.commit_count, reverse=True)
        
        return evolutions
    
    def _calculate_velocity(self, commits: List[Dict[str, str]], days: int) -> Dict[str, int]:
        """Calculate development velocity metrics."""
        theme_counts = Counter()
        
        for commit in commits:
            message = commit['message'].lower()
            for theme, patterns in self.THEME_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, message, re.IGNORECASE):
                        theme_counts[theme] += 1
                        break
        
        return {
            'total_commits': len(commits),
            'features_completed': theme_counts.get('feature', 0),
            'bugs_fixed': theme_counts.get('bugfix', 0),
            'refactors': theme_counts.get('refactor', 0),
            'commits_per_day': round(len(commits) / days, 1) if days > 0 else 0.0
        }
    
    def _generate_summary(
        self,
        themes: List[CommitTheme],
        active_areas: List[str],
        evolutions: List[FeatureEvolution],
        velocity: Dict[str, int],
        days: int
    ) -> str:
        """Generate human-readable narrative summary."""
        parts = []
        
        # Theme focus
        if themes:
            top_themes = [t.theme for t in themes[:3]]
            parts.append(f"Recent development focuses on {', '.join(top_themes)}")
        
        # Active areas
        if active_areas:
            parts.append(f"with active work in {', '.join(active_areas[:3])}")
        
        # Velocity
        if velocity['total_commits'] > 0:
            parts.append(
                f"Team has completed {velocity['features_completed']} features "
                f"and fixed {velocity['bugs_fixed']} bugs in the last {days} days"
            )
        
        return ". ".join(parts) + "."
    
    def _update_knowledge_graph(
        self,
        commits: List[Dict[str, str]],
        themes: List[CommitTheme],
        evolutions: List[FeatureEvolution],
        active_areas: List[str]
    ) -> None:
        """Update tier2 knowledge graph with commit pattern insights."""
        try:
            from src.tier2.knowledge_graph import KnowledgeGraph
            
            kg = KnowledgeGraph()
            
            # Store successful commit patterns
            for theme in themes:
                if theme.count >= 5:  # High-frequency theme
                    kg.add_pattern(
                        pattern_type='commit_theme',
                        pattern=theme.theme,
                        context={
                            'keywords': theme.keywords,
                            'examples': theme.example_commits,
                            'frequency': theme.count
                        },
                        confidence=min(theme.percentage / 100, 1.0)
                    )
            
            # Store feature evolution patterns
            for evolution in evolutions:
                if len(evolution.stages) >= 2:  # Multi-stage evolution
                    kg.add_pattern(
                        pattern_type='feature_evolution',
                        pattern=evolution.feature_name,
                        context={
                            'stages': evolution.stages,
                            'commits': evolution.commit_count,
                            'duration_days': (evolution.last_commit_date - evolution.first_commit_date).days
                        },
                        confidence=0.8
                    )
            
            # Store active development areas
            for area in active_areas[:3]:
                kg.add_pattern(
                    pattern_type='active_area',
                    pattern=area,
                    context={'commit_frequency': 'high'},
                    confidence=0.9
                )
            
            # Log lessons learned
            if len(commits) >= 10:
                kg.add_lesson_learned(
                    lesson_type='commit_analysis',
                    lesson=f"Successfully analyzed {len(commits)} commits, extracted {len(themes)} themes",
                    context={'repo_path': str(self.repo_path)},
                    success=True
                )
        
        except ImportError:
            # Knowledge graph not available - continue without it
            pass
        except Exception as e:
            print(f"Warning: Could not update knowledge graph: {e}")
    
    def _empty_narrative(self, days: int) -> DevelopmentNarrative:
        """Return empty narrative when no commits found."""
        return DevelopmentNarrative(
            summary=f"No commits found in the last {days} days.",
            top_themes=[],
            active_areas=[],
            feature_evolutions=[],
            velocity_metrics={
                'total_commits': 0,
                'features_completed': 0,
                'bugs_fixed': 0,
                'refactors': 0,
                'commits_per_day': 0.0
            },
            time_period=f"last {days} days"
        )
    
    def to_dict(self, narrative: DevelopmentNarrative) -> Dict:
        """Convert narrative to dictionary for serialization."""
        result = asdict(narrative)
        
        # Convert datetime objects to strings
        for evolution in result['feature_evolutions']:
            evolution['first_commit_date'] = evolution['first_commit_date'].isoformat()
            evolution['last_commit_date'] = evolution['last_commit_date'].isoformat()
            evolution['files_touched'] = list(evolution['files_touched'])
        
        return result
    
    def to_json(self, narrative: DevelopmentNarrative, indent: int = 2) -> str:
        """Convert narrative to JSON string."""
        return json.dumps(self.to_dict(narrative), indent=indent)
