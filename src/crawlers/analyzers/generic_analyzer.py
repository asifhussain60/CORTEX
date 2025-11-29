"""
Generic Language Analyzer

Fallback analyzer for unsupported languages. Provides basic file metrics
without language-specific parsing (LOC, SLOC, comments, file size).

Author: CORTEX Application Health Dashboard
"""

import re
from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass
class GenericAnalysisResult:
    """Analysis result for generic files"""
    file_path: str
    language: str = "unknown"
    lines_of_code: int = 0
    source_lines: int = 0  # Non-blank, non-comment lines
    comment_lines: int = 0
    blank_lines: int = 0
    file_size_bytes: int = 0
    raw_metrics: Dict[str, Any] = field(default_factory=dict)


class GenericAnalyzer:
    """Fallback analyzer for unsupported languages - provides basic metrics"""
    
    # Comment patterns for common languages
    COMMENT_PATTERNS = {
        # Single-line comments
        'hash': re.compile(r'^\s*#'),  # Python, Ruby, Shell, YAML
        'slash': re.compile(r'^\s*//'),  # JavaScript, C#, Java, C++
        'dash': re.compile(r'^\s*--'),  # SQL, Lua, Ada
        'rem': re.compile(r'^\s*rem\s', re.IGNORECASE),  # Batch
        'semicolon': re.compile(r'^\s*;'),  # Lisp, Assembly
        
        # Multi-line comments (simplified detection)
        'c_style_start': re.compile(r'/\*'),  # /* ... */
        'c_style_end': re.compile(r'\*/'),
    }
    
    def __init__(self):
        """Initialize generic analyzer"""
        self.in_multiline_comment = False
    
    def analyze(self, file_path: str, content: str) -> GenericAnalysisResult:
        """
        Analyze file content with basic metrics
        
        Args:
            file_path: Path to the file
            content: File content as string
            
        Returns:
            GenericAnalysisResult with basic metrics
        """
        result = GenericAnalysisResult(file_path=file_path)
        
        # Detect language from extension
        result.language = self._detect_language(file_path)
        
        # File size
        result.file_size_bytes = len(content.encode('utf-8'))
        
        # Line-by-line analysis
        lines = content.split('\n')
        result.lines_of_code = len(lines)
        
        self.in_multiline_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            # Blank line
            if not stripped:
                result.blank_lines += 1
                continue
            
            # Check for multi-line comment transitions
            if self.COMMENT_PATTERNS['c_style_start'].search(line):
                self.in_multiline_comment = True
            
            if self.in_multiline_comment:
                result.comment_lines += 1
                if self.COMMENT_PATTERNS['c_style_end'].search(line):
                    self.in_multiline_comment = False
                continue
            
            # Check for single-line comments
            is_comment = False
            for pattern in [self.COMMENT_PATTERNS['hash'], 
                           self.COMMENT_PATTERNS['slash'],
                           self.COMMENT_PATTERNS['dash'],
                           self.COMMENT_PATTERNS['rem'],
                           self.COMMENT_PATTERNS['semicolon']]:
                if pattern.match(stripped):
                    result.comment_lines += 1
                    is_comment = True
                    break
            
            if not is_comment:
                result.source_lines += 1
        
        # Calculate raw metrics
        result.raw_metrics = {
            'total_lines': result.lines_of_code,
            'source_lines': result.source_lines,
            'comment_lines': result.comment_lines,
            'blank_lines': result.blank_lines,
            'comment_ratio': (result.comment_lines / result.lines_of_code 
                            if result.lines_of_code > 0 else 0),
            'code_density': (result.source_lines / result.lines_of_code 
                           if result.lines_of_code > 0 else 0),
            'file_size_kb': result.file_size_bytes / 1024
        }
        
        return result
    
    def can_analyze(self, file_path: str) -> bool:
        """
        Generic analyzer can handle any file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Always True (fallback analyzer)
        """
        return True
    
    def _detect_language(self, file_path: str) -> str:
        """
        Detect language from file extension
        
        Args:
            file_path: Path to the file
            
        Returns:
            Language name or "unknown"
        """
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.cs': 'csharp',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c_header',
            '.hpp': 'cpp_header',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.m': 'matlab',
            '.lua': 'lua',
            '.pl': 'perl',
            '.sh': 'shell',
            '.bat': 'batch',
            '.ps1': 'powershell',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.xml': 'xml',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.txt': 'text'
        }
        
        # Find extension
        for ext, lang in extension_map.items():
            if file_path.lower().endswith(ext):
                return lang
        
        return 'unknown'
