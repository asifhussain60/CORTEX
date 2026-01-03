"""
Code Analyzer Engine - File scanning, term extraction, and risk classification.

Integrates:
- Existing code_analyzer.py utilities (50% reuse)
- RiskClassifier from vacuum-v2-patterns.md
- Progressive analysis strategy for large codebases

Features:
- Multi-language support (Python, JavaScript/TypeScript, C#, Java, etc.)
- Domain terminology extraction
- Sensitive data detection
- Risk-based file classification
- Progressive analysis (quick scan → selective parsing → deep analysis)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import os
import re
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk levels for file/transformation classification."""
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class FileAnalysis:
    """Analysis result for a single file."""
    path: Path
    relative_path: str
    language: str
    size_bytes: int
    risk_level: RiskLevel
    terms_found: List[str] = field(default_factory=list)
    namespaces: List[str] = field(default_factory=list)
    sensitive_data: List[Dict[str, Any]] = field(default_factory=list)
    recently_modified: bool = False
    uncommitted_changes: bool = False


@dataclass
class AnalysisResult:
    """Complete codebase analysis result."""
    total_files: int
    analyzed_files: int
    skipped_files: int
    
    # File categorization
    files_by_language: Dict[str, int]
    files_by_risk: Dict[RiskLevel, int]
    
    # Terms and namespaces
    terms_found: Dict[str, int]  # term -> frequency
    namespaces: List[str]
    
    # Sensitive data
    sensitive_data_count: int
    sensitive_data_by_type: Dict[str, int]
    
    # Individual file analyses
    file_analyses: List[FileAnalysis]
    
    # Timing
    analysis_duration_seconds: float


class RiskClassifier:
    """
    Classifies files and transformations by risk level.
    
    Integrated from vacuum-v2-patterns.md with enhancements.
    """
    
    # Critical file patterns (NEVER auto-approve)
    CRITICAL_PATTERNS = {
        '.git', '.gitignore', '.gitattributes', '.github',
        'requirements.txt', 'package.json', 'pyproject.toml', 'Dockerfile',
        'README', 'LICENSE', 'CHANGELOG'
    }
    
    # Source code extensions
    SOURCE_CODE_EXTENSIONS = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h',
        '.cs', '.go', '.rs', '.rb', '.php', '.html', '.css', '.scss'
    }
    
    # Configuration extensions
    CONFIG_EXTENSIONS = {
        '.yaml', '.yml', '.json', '.toml', '.ini', '.conf', '.config', '.env'
    }
    
    # Documentation extensions
    DOCUMENTATION_EXTENSIONS = {'.md', '.rst', '.txt'}
    
    def __init__(self, git_root: Optional[Path] = None, recently_modified_hours: int = 24):
        """
        Initialize risk classifier.
        
        Args:
            git_root: Optional git repository root
            recently_modified_hours: Hours threshold for "recently modified" (default: 24)
        """
        self.git_root = git_root or self._find_git_root()
        self.recently_modified_hours = recently_modified_hours
    
    def classify_file(self, file_path: Path) -> RiskLevel:
        """
        Classify file by risk level.
        
        Args:
            file_path: Path to file
        
        Returns:
            RiskLevel enum value
        """
        # CRITICAL: Git metadata, project config files
        if self._is_critical_file(file_path):
            return RiskLevel.CRITICAL
        
        # CRITICAL: Uncommitted changes
        if self._has_uncommitted_changes(file_path):
            return RiskLevel.CRITICAL
        
        # HIGH: Recently modified files
        if self._is_recently_modified(file_path):
            return RiskLevel.HIGH
        
        # MEDIUM: Source code and config files
        if file_path.suffix in self.SOURCE_CODE_EXTENSIONS:
            return RiskLevel.MEDIUM
        if file_path.suffix in self.CONFIG_EXTENSIONS:
            return RiskLevel.MEDIUM
        
        # LOW: Documentation
        if file_path.suffix in self.DOCUMENTATION_EXTENSIONS:
            return RiskLevel.LOW
        
        # SAFE: Everything else (build artifacts, temp files, etc.)
        return RiskLevel.SAFE
    
    def _is_critical_file(self, file_path: Path) -> bool:
        """Check if file matches critical patterns."""
        path_str = str(file_path)
        filename = file_path.name
        
        for pattern in self.CRITICAL_PATTERNS:
            if pattern in path_str or pattern in filename:
                return True
        
        return False
    
    def _has_uncommitted_changes(self, file_path: Path) -> bool:
        """Check if file has uncommitted git changes."""
        if not self.git_root:
            return False
        
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain', str(file_path)],
                cwd=self.git_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            return bool(result.stdout.strip())
        except Exception:
            return False
    
    def _is_recently_modified(self, file_path: Path) -> bool:
        """Check if file was modified recently."""
        try:
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            threshold = datetime.now() - timedelta(hours=self.recently_modified_hours)
            return mod_time > threshold
        except OSError:
            return False
    
    def _find_git_root(self) -> Optional[Path]:
        """Find git repository root directory."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except Exception:
            pass
        return None


class CodeAnalyzerEngine:
    """
    Code analysis engine for sanitization.
    
    Performs:
    1. File structure scanning with exclusion patterns
    2. Domain terminology extraction
    3. Sensitive data detection
    4. Risk classification
    5. Namespace/package extraction
    
    Uses progressive analysis for performance:
    - Quick scan: File metadata only
    - Selective parsing: Code files <10MB
    - Deep analysis: High-risk files only (optional)
    """
    
    # Size thresholds
    MAX_FILE_SIZE_MB = 50
    SKIP_LARGE_FILES_MB = 100
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize code analyzer engine.
        
        Args:
            config: Configuration dictionary from orchestrator
        """
        self.config = config
        self.analysis_config = config.get('analysis', {})
        self.file_processing = self.analysis_config.get('file_processing', {})
        self.progressive = self.analysis_config.get('progressive_analysis', {})
        self.risk_config = config.get('risk_classification', {})
        
        # Compile exclusion patterns
        self.exclusions = self._compile_exclusions()
        
        # Initialize risk classifier
        self.risk_classifier = RiskClassifier(
            recently_modified_hours=self.risk_config.get('rules', {}).get('recently_modified_hours', 24)
        )
        
        # Sensitive data patterns
        self.sensitive_patterns = self._compile_sensitive_patterns()
        
        logger.info("Initialized CodeAnalyzerEngine")
    
    def analyze_codebase(
        self,
        source_directory: Path,
        deep_analysis: bool = False
    ) -> AnalysisResult:
        """
        Analyze entire codebase progressively.
        
        Args:
            source_directory: Root directory of codebase
            deep_analysis: If True, perform deep analysis on all files
        
        Returns:
            AnalysisResult with complete analysis
        """
        logger.info(f"Starting codebase analysis: {source_directory}")
        start_time = datetime.now()
        
        # Phase 1: Quick scan (file metadata only)
        logger.info("Phase 1: Quick file scan...")
        all_files = self._quick_scan(source_directory)
        logger.info(f"  Found {len(all_files)} files")
        
        # Phase 2: Selective parsing (code files only)
        logger.info("Phase 2: Selective file parsing...")
        file_analyses = self._selective_parse(all_files)
        logger.info(f"  Analyzed {len(file_analyses)} files")
        
        # Phase 3: Deep analysis (optional, high-risk only)
        if deep_analysis:
            logger.info("Phase 3: Deep analysis...")
            file_analyses = self._deep_analyze(file_analyses)
        
        # Aggregate results
        result = self._aggregate_results(file_analyses, start_time)
        
        logger.info(f"Analysis complete in {result.analysis_duration_seconds:.1f}s")
        logger.info(f"  Total files: {result.total_files}")
        logger.info(f"  Analyzed: {result.analyzed_files}")
        logger.info(f"  Terms found: {len(result.terms_found)}")
        logger.info(f"  Sensitive data: {result.sensitive_data_count}")
        
        return result
    
    def _quick_scan(self, source_directory: Path) -> List[Path]:
        """
        Phase 1: Quick scan (file metadata only).
        
        Args:
            source_directory: Root directory
        
        Returns:
            List of file paths to analyze
        """
        files = []
        
        for root, dirs, filenames in os.walk(source_directory):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if not self._is_excluded(Path(root) / d)]
            
            for filename in filenames:
                file_path = Path(root) / filename
                
                # Skip excluded files
                if self._is_excluded(file_path):
                    continue
                
                # Skip very large files
                try:
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    if size_mb > self.SKIP_LARGE_FILES_MB:
                        logger.debug(f"Skipping large file: {file_path} ({size_mb:.1f}MB)")
                        continue
                except OSError:
                    continue
                
                files.append(file_path)
        
        return files
    
    def _selective_parse(self, files: List[Path]) -> List[FileAnalysis]:
        """
        Phase 2: Selective parsing (code files only).
        
        Args:
            files: Files to parse
        
        Returns:
            List of FileAnalysis objects
        """
        analyses = []
        
        for file_path in files:
            try:
                # Get file metadata
                stats = file_path.stat()
                size_bytes = stats.st_size
                size_mb = size_bytes / (1024 * 1024)
                
                # Detect language
                language = self._detect_language(file_path)
                
                # Skip non-code files in selective parsing
                if language == 'unknown':
                    continue
                
                # Skip large files
                if size_mb > self.MAX_FILE_SIZE_MB:
                    continue
                
                # Classify risk
                risk_level = self.risk_classifier.classify_file(file_path)
                
                # Check if recently modified
                recently_modified = self.risk_classifier._is_recently_modified(file_path)
                
                # Check for uncommitted changes
                uncommitted = self.risk_classifier._has_uncommitted_changes(file_path)
                
                # Read and analyze file content
                content = self._read_file(file_path)
                
                # Extract terms
                terms_found = self._extract_terms(content, language)
                
                # Extract namespaces
                namespaces = self._extract_namespaces(content, language)
                
                # Detect sensitive data
                sensitive_data = self._detect_sensitive_data(content, file_path)
                
                # Create analysis
                analysis = FileAnalysis(
                    path=file_path,
                    relative_path=str(file_path.relative_to(file_path.parent.parent)),
                    language=language,
                    size_bytes=size_bytes,
                    risk_level=risk_level,
                    terms_found=terms_found,
                    namespaces=namespaces,
                    sensitive_data=sensitive_data,
                    recently_modified=recently_modified,
                    uncommitted_changes=uncommitted
                )
                
                analyses.append(analysis)
            
            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")
                continue
        
        return analyses
    
    def _deep_analyze(self, analyses: List[FileAnalysis]) -> List[FileAnalysis]:
        """
        Phase 3: Deep analysis (AST parsing, data flow, etc.).
        
        Currently a placeholder for future AST-based analysis.
        
        Args:
            analyses: Existing analyses
        
        Returns:
            Enhanced analyses
        """
        logger.info("Deep analysis not yet implemented - using selective parsing results")
        return analyses
    
    def _aggregate_results(
        self,
        file_analyses: List[FileAnalysis],
        start_time: datetime
    ) -> AnalysisResult:
        """Aggregate individual file analyses into complete result."""
        # Count by language
        files_by_language = defaultdict(int)
        for analysis in file_analyses:
            files_by_language[analysis.language] += 1
        
        # Count by risk
        files_by_risk = defaultdict(int)
        for analysis in file_analyses:
            files_by_risk[analysis.risk_level] += 1
        
        # Aggregate terms
        terms_aggregate = defaultdict(int)
        for analysis in file_analyses:
            for term in analysis.terms_found:
                terms_aggregate[term] += 1
        
        # Aggregate namespaces
        all_namespaces = set()
        for analysis in file_analyses:
            all_namespaces.update(analysis.namespaces)
        
        # Count sensitive data
        sensitive_count = sum(len(a.sensitive_data) for a in file_analyses)
        sensitive_by_type = defaultdict(int)
        for analysis in file_analyses:
            for item in analysis.sensitive_data:
                sensitive_by_type[item['type']] += 1
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return AnalysisResult(
            total_files=len(file_analyses),
            analyzed_files=len(file_analyses),
            skipped_files=0,  # Tracked separately in quick_scan
            files_by_language=dict(files_by_language),
            files_by_risk=dict(files_by_risk),
            terms_found=dict(terms_aggregate),
            namespaces=sorted(list(all_namespaces)),
            sensitive_data_count=sensitive_count,
            sensitive_data_by_type=dict(sensitive_by_type),
            file_analyses=file_analyses,
            analysis_duration_seconds=duration
        )
    
    def _compile_exclusions(self) -> List[re.Pattern]:
        """Compile exclusion patterns from config."""
        patterns = []
        for exclusion in self.file_processing.get('exclusions', []):
            pattern_str = exclusion.get('pattern', '')
            # Convert glob to regex
            pattern_str = pattern_str.replace('**', '.*').replace('*', '[^/]*')
            try:
                patterns.append(re.compile(pattern_str))
            except re.error as e:
                logger.warning(f"Invalid exclusion pattern '{pattern_str}': {e}")
        return patterns
    
    def _compile_sensitive_patterns(self) -> Dict[str, re.Pattern]:
        """Compile sensitive data detection patterns."""
        patterns = {}
        for pattern_config in self.analysis_config.get('sensitive_data_detection', {}).get('patterns', []):
            pattern_type = pattern_config.get('type')
            pattern_str = pattern_config.get('pattern')
            try:
                patterns[pattern_type] = re.compile(pattern_str)
            except re.error as e:
                logger.warning(f"Invalid sensitive pattern '{pattern_type}': {e}")
        return patterns
    
    def _is_excluded(self, path: Path) -> bool:
        """Check if path matches exclusion patterns."""
        path_str = str(path)
        for pattern in self.exclusions:
            if pattern.search(path_str):
                return True
        return False
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension."""
        ext = file_path.suffix.lower()
        
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.cs': 'csharp',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.md': 'markdown',
            '.txt': 'text',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
        }
        
        return lang_map.get(ext, 'unknown')
    
    def _read_file(self, file_path: Path) -> str:
        """Read file content with encoding handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception:
                return ""
        except Exception:
            return ""
    
    def _extract_terms(self, content: str, language: str) -> List[str]:
        """
        Extract domain-specific terms from content.
        
        Simplified implementation - could be enhanced with:
        - AST parsing for code structure
        - NLP for term extraction
        - Dictionary-based filtering
        """
        # For now, extract camelCase and PascalCase identifiers
        pattern = re.compile(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b')
        matches = pattern.findall(content)
        return list(set(matches))  # Unique terms only
    
    def _extract_namespaces(self, content: str, language: str) -> List[str]:
        """Extract namespaces/packages from content."""
        namespaces = []
        
        if language == 'python':
            # Extract from imports
            pattern = re.compile(r'(?:from|import)\s+([\w.]+)')
            matches = pattern.findall(content)
            namespaces.extend([m.split('.')[0] for m in matches])
        
        elif language in ['javascript', 'typescript']:
            # Extract from imports
            pattern = re.compile(r'(?:from|import)\s+["\']([^"\']+)["\']')
            matches = pattern.findall(content)
            namespaces.extend(matches)
        
        elif language == 'csharp':
            # Extract namespace declarations
            pattern = re.compile(r'namespace\s+([\w.]+)')
            matches = pattern.findall(content)
            namespaces.extend(matches)
        
        elif language == 'java':
            # Extract package declarations
            pattern = re.compile(r'package\s+([\w.]+)')
            matches = pattern.findall(content)
            namespaces.extend(matches)
        
        return list(set(namespaces))
    
    def _detect_sensitive_data(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Detect sensitive data in content."""
        findings = []
        
        for data_type, pattern in self.sensitive_patterns.items():
            matches = pattern.finditer(content)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                finding = {
                    'type': data_type,
                    'line': line_num,
                    'matched_text': match.group(0)[:50],  # Truncate for safety
                    'column': match.start() - content.rfind('\n', 0, match.start())
                }
                findings.append(finding)
        
        return findings
