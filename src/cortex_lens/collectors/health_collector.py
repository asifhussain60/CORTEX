"""
Health Collector

Collects basic repository health metrics: file count, LOC, language distribution.
"""

import logging
from pathlib import Path
from typing import Dict, Any
from collections import defaultdict
from .base import BaseCollector

logger = logging.getLogger(__name__)


class HealthCollector(BaseCollector):
    """
    Collect repository health metrics
    
    Metrics:
    - Total file count
    - Lines of code (LOC)
    - Language distribution
    - File type breakdown
    - Directory structure depth
    """
    
    # Language detection by extension
    LANGUAGE_MAP = {
        '.py': 'Python',
        '.pyw': 'Python',
        '.cs': 'C#',
        '.js': 'JavaScript',
        '.jsx': 'JavaScript',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript',
        '.sql': 'SQL',
        '.html': 'HTML',
        '.htm': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.sass': 'SASS',
        '.json': 'JSON',
        '.xml': 'XML',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.md': 'Markdown',
        '.txt': 'Text',
        '.sh': 'Shell',
        '.ps1': 'PowerShell',
        '.bat': 'Batch',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.h': 'C/C++ Header',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP'
    }
    
    def _scan_files(
        self,
        repo_path: Path,
        extensions: list[str] = None
    ) -> list[Path]:
        """
        Recursively scan repository for files with specified extensions.
        
        Args:
            repo_path: Repository root path
            extensions: List of file extensions to include (e.g., ['.py', '.cs'])
                       If None, includes all files
        
        Returns:
            List of Path objects for matching files
        """
        files = []
        
        # Directories to exclude
        exclude_dirs = {
            '.git', '.svn', '.hg',  # VCS
            '__pycache__', '.pytest_cache', '.mypy_cache',  # Python caches
            'node_modules', 'bower_components',  # JavaScript
            'bin', 'obj',  # .NET
            'target',  # Java/Rust
            'build', 'dist', '.egg-info',  # Build artifacts
            'venv', 'env', '.env', '.venv',  # Virtual environments
        }
        
        try:
            for file_path in repo_path.rglob('*'):
                # Skip if in excluded directory
                if any(excluded in file_path.parts for excluded in exclude_dirs):
                    continue
                
                # Skip if not a file
                if not file_path.is_file():
                    continue
                
                # Check extension filter
                if extensions is not None:
                    if file_path.suffix.lower() not in extensions:
                        continue
                
                files.append(file_path)
        except Exception as e:
            logger.warning(f"Error scanning {repo_path}: {e}")
        
        return files
    
    def collect(
        self,
        repo_path: Path,
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Collect health metrics
        
        Args:
            repo_path: Repository root
            classification: Classification results
            
        Returns:
            {
                'total_files': int,
                'total_loc': int,
                'languages': {...},
                'file_types': {...},
                'directory_depth': int,
                'largest_files': [...],
                'health_score': float
            }
        """
        logger.info("Collecting repository health metrics...")
        
        # Scan files
        files = self._scan_files(
            repo_path,
            extensions=list(self.LANGUAGE_MAP.keys())
        )
        
        total_files = len(files)
        total_loc = 0
        language_stats = defaultdict(lambda: {'files': 0, 'loc': 0})
        file_type_stats = defaultdict(int)
        file_sizes = []
        max_depth = 0
        
        for file_path in files:
            # Language detection
            ext = file_path.suffix.lower()
            language = self.LANGUAGE_MAP.get(ext, 'Other')
            
            # Count lines
            try:
                with file_path.open('r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    total_loc += lines
                    language_stats[language]['files'] += 1
                    language_stats[language]['loc'] += lines
                    
                    file_sizes.append({
                        'file': str(file_path.relative_to(repo_path)),
                        'loc': lines,
                        'language': language
                    })
            except Exception as e:
                logger.debug(f"Error reading {file_path}: {e}")
            
            # File type stats
            file_type_stats[ext] += 1
            
            # Directory depth
            depth = len(file_path.relative_to(repo_path).parts) - 1
            max_depth = max(max_depth, depth)
        
        # Sort files by size
        largest_files = sorted(file_sizes, key=lambda x: x['loc'], reverse=True)[:10]
        
        # Calculate health score (0-100)
        health_score = self._calculate_health_score(
            total_files,
            total_loc,
            language_stats,
            max_depth
        )
        
        # Convert language stats to percentages
        language_percentages = {}
        for lang, stats in language_stats.items():
            language_percentages[lang] = {
                'files': stats['files'],
                'loc': stats['loc'],
                'percentage': (stats['loc'] / total_loc * 100) if total_loc > 0 else 0
            }
        
        result = {
            'total_files': total_files,
            'total_loc': total_loc,
            'languages': dict(language_percentages),
            'file_types': dict(file_type_stats),
            'directory_depth': max_depth,
            'largest_files': largest_files,
            'health_score': health_score,
            'health_grade': self._score_to_grade(health_score),
            'metrics': {
                'avg_file_size': total_loc // total_files if total_files > 0 else 0,
                'code_density': self._calculate_code_density(total_loc, total_files)
            }
        }
        
        logger.info(f"✅ Health metrics collected: {total_files} files, "
                   f"{total_loc} LOC, health score: {health_score:.1f}")
        
        return result
    
    def _calculate_health_score(
        self,
        total_files: int,
        total_loc: int,
        language_stats: Dict,
        max_depth: int
    ) -> float:
        """
        Calculate overall repository health score (0-100)
        
        Factors:
        - File count (ideal: 50-500 files)
        - LOC (ideal: 5K-50K)
        - Language diversity (penalty for too many languages)
        - Directory depth (penalty for excessive nesting)
        """
        score = 100.0
        
        # File count scoring
        if total_files < 10:
            score -= 20
        elif total_files > 1000:
            score -= 10
        
        # LOC scoring
        if total_loc < 1000:
            score -= 15
        elif total_loc > 100000:
            score -= 10
        
        # Language diversity (penalty if >5 languages)
        if len(language_stats) > 5:
            score -= (len(language_stats) - 5) * 5
        
        # Directory depth (penalty if >6 levels)
        if max_depth > 6:
            score -= (max_depth - 6) * 3
        
        return max(0.0, min(100.0, score))
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return 'A - Excellent'
        elif score >= 80:
            return 'B - Good'
        elif score >= 70:
            return 'C - Fair'
        elif score >= 60:
            return 'D - Poor'
        else:
            return 'F - Critical'
    
    def _calculate_code_density(self, total_loc: int, total_files: int) -> str:
        """Calculate code density classification"""
        if total_files == 0:
            return 'N/A'
        
        avg_size = total_loc // total_files
        
        if avg_size < 100:
            return 'Low (Small files)'
        elif avg_size < 300:
            return 'Medium (Moderate files)'
        elif avg_size < 500:
            return 'High (Large files)'
        else:
            return 'Very High (Very large files)'
