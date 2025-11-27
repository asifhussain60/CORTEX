"""
Analysis Engine for Code Review Feature

Provides base classes and concrete analyzers for detecting issues in code reviews:
- Breaking changes detection
- Code smell analysis
- Best practices validation
- Security vulnerabilities
- Performance issues

Author: Asif Hussain
Date: November 26, 2025
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Set
from pathlib import Path
import re


class IssueSeverity(Enum):
    """Severity levels for code review issues."""
    CRITICAL = "critical"  # Must fix before merge
    WARNING = "warning"    # Should fix before merge
    SUGGESTION = "suggestion"  # Nice to have, optional


class IssueCategory(Enum):
    """Categories of code review issues."""
    BREAKING_CHANGE = "breaking_change"
    CODE_SMELL = "code_smell"
    BEST_PRACTICE = "best_practice"
    SECURITY = "security"
    PERFORMANCE = "performance"
    TDD_VIOLATION = "tdd_violation"


@dataclass
class IssueFinding:
    """Represents a single issue found during code review."""
    category: IssueCategory
    severity: IssueSeverity
    title: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    fix_suggestion: Optional[str] = None
    confidence_score: float = 0.85  # 0.0-1.0, default 85%
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for reporting."""
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "fix_suggestion": self.fix_suggestion,
            "confidence_score": self.confidence_score
        }


@dataclass
class AnalysisResult:
    """Results from running an analyzer."""
    analyzer_name: str
    findings: List[IssueFinding] = field(default_factory=list)
    execution_time_ms: float = 0.0
    files_analyzed: int = 0
    
    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == IssueSeverity.CRITICAL)
    
    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == IssueSeverity.WARNING)
    
    @property
    def suggestion_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == IssueSeverity.SUGGESTION)
    
    @property
    def average_confidence(self) -> float:
        if not self.findings:
            return 1.0
        return sum(f.confidence_score for f in self.findings) / len(self.findings)


class BaseAnalyzer(ABC):
    """Abstract base class for all code analyzers."""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the analyzer name."""
        pass
    
    @abstractmethod
    def analyze(self, file_paths: List[str], file_contents: Optional[Dict[str, str]] = None) -> AnalysisResult:
        """
        Analyze the given files and return findings.
        
        Args:
            file_paths: List of file paths to analyze
            file_contents: Optional dict of {file_path: content} for efficiency
            
        Returns:
            AnalysisResult containing all findings
        """
        pass
    
    def _read_file(self, file_path: str) -> Optional[str]:
        """Read file content, return None if file doesn't exist."""
        try:
            full_path = self.workspace_root / file_path if not Path(file_path).is_absolute() else Path(file_path)
            return full_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return None
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.cs': 'csharp',
            '.java': 'java',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp'
        }
        ext = Path(file_path).suffix.lower()
        return ext_map.get(ext, 'unknown')


class BreakingChangesAnalyzer(BaseAnalyzer):
    """Detects breaking changes in public APIs."""
    
    @property
    def name(self) -> str:
        return "Breaking Changes Detector"
    
    def analyze(self, file_paths: List[str], file_contents: Optional[Dict[str, str]] = None) -> AnalysisResult:
        """Detect breaking changes in public APIs."""
        import time
        start_time = time.time()
        
        result = AnalysisResult(analyzer_name=self.name)
        
        for file_path in file_paths:
            content = file_contents.get(file_path) if file_contents else self._read_file(file_path)
            if not content:
                continue
            
            result.files_analyzed += 1
            language = self._detect_language(file_path)
            
            # Detect breaking changes based on language
            if language == 'python':
                result.findings.extend(self._detect_python_breaking_changes(file_path, content))
            elif language in ['javascript', 'typescript']:
                result.findings.extend(self._detect_js_breaking_changes(file_path, content))
            elif language == 'csharp':
                result.findings.extend(self._detect_csharp_breaking_changes(file_path, content))
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    def _detect_python_breaking_changes(self, file_path: str, content: str) -> List[IssueFinding]:
        """Detect Python-specific breaking changes."""
        findings = []
        lines = content.split('\n')
        
        # Pattern 1: Public function/method signature changes (removed parameters)
        for i, line in enumerate(lines, 1):
            # Check for function definitions
            if re.match(r'^\s*def\s+[a-z_][a-z0-9_]*\s*\(', line) and not line.strip().startswith('_'):
                # Look for removed required parameters (heuristic: very few params)
                param_match = re.search(r'def\s+(\w+)\s*\((.*?)\)', line)
                if param_match:
                    func_name = param_match.group(1)
                    params = param_match.group(2)
                    
                    # If function has no params (might have had some before)
                    if not params.strip() or params.strip() == 'self':
                        findings.append(IssueFinding(
                            category=IssueCategory.BREAKING_CHANGE,
                            severity=IssueSeverity.WARNING,
                            title=f"Potential parameter removal in '{func_name}'",
                            description=f"Public function '{func_name}' has minimal parameters. If parameters were removed, this is a breaking change.",
                            file_path=file_path,
                            line_number=i,
                            code_snippet=line.strip(),
                            fix_suggestion="Add deprecated parameters with default values for backward compatibility.",
                            confidence_score=0.60  # Lower confidence (heuristic-based)
                        ))
        
        # Pattern 2: Class/interface removal (deleted public classes)
        class_pattern = re.compile(r'^\s*class\s+([A-Z][a-zA-Z0-9_]*)')
        for i, line in enumerate(lines, 1):
            if class_pattern.match(line):
                class_name = class_pattern.match(line).group(1)
                # Check if class is marked as deprecated
                if i > 1 and '@deprecated' in lines[i-2].lower():
                    findings.append(IssueFinding(
                        category=IssueCategory.BREAKING_CHANGE,
                        severity=IssueSeverity.CRITICAL,
                        title=f"Deprecated class '{class_name}' may be removed",
                        description=f"Class '{class_name}' is marked as deprecated. Removal would be a breaking change.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        fix_suggestion="Ensure deprecation warnings are in place for at least one version before removal.",
                        confidence_score=0.90
                    ))
        
        # Pattern 3: Return type changes (heuristic: changed return statements)
        return_pattern = re.compile(r'^\s*return\s+(.+)')
        for i, line in enumerate(lines, 1):
            if return_pattern.match(line):
                return_value = return_pattern.match(line).group(1).strip()
                # Check for type changes (None -> value or value -> None)
                if return_value == 'None' and i > 5:
                    # Check if this is inside a public function
                    for j in range(max(0, i-10), i):
                        if re.match(r'^\s*def\s+[a-z_][a-z0-9_]*', lines[j]) and not lines[j].strip().startswith('_'):
                            findings.append(IssueFinding(
                                category=IssueCategory.BREAKING_CHANGE,
                                severity=IssueSeverity.WARNING,
                                title="Return type may have changed to None",
                                description="Returning None where a value was expected is a breaking change for callers.",
                                file_path=file_path,
                                line_number=i,
                                code_snippet=line.strip(),
                                fix_suggestion="Use Optional[Type] type hints and document the change.",
                                confidence_score=0.65
                            ))
                            break
        
        return findings
    
    def _detect_js_breaking_changes(self, file_path: str, content: str) -> List[IssueFinding]:
        """Detect JavaScript/TypeScript-specific breaking changes."""
        findings = []
        lines = content.split('\n')
        
        # Pattern 1: Exported function signature changes
        export_func_pattern = re.compile(r'export\s+(async\s+)?function\s+(\w+)\s*\(([^)]*)\)')
        for i, line in enumerate(lines, 1):
            match = export_func_pattern.search(line)
            if match:
                func_name = match.group(2)
                params = match.group(3).strip()
                
                # Check for minimal parameters
                if not params or params.count(',') < 1:
                    findings.append(IssueFinding(
                        category=IssueCategory.BREAKING_CHANGE,
                        severity=IssueSeverity.WARNING,
                        title=f"Exported function '{func_name}' has minimal parameters",
                        description=f"If parameters were removed from '{func_name}', this breaks existing consumers.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        fix_suggestion="Use object parameters with defaults for backward compatibility.",
                        confidence_score=0.60
                    ))
        
        # Pattern 2: Interface changes (TypeScript)
        interface_pattern = re.compile(r'^\s*export\s+interface\s+(\w+)')
        for i, line in enumerate(lines, 1):
            if interface_pattern.match(line):
                interface_name = interface_pattern.match(line).group(1)
                # Check next 10 lines for required properties
                for j in range(i, min(i+10, len(lines))):
                    if re.search(r'^\s*(\w+)\s*:\s*', lines[j]) and '?' not in lines[j]:
                        findings.append(IssueFinding(
                            category=IssueCategory.BREAKING_CHANGE,
                            severity=IssueSeverity.CRITICAL,
                            title=f"Required property in interface '{interface_name}'",
                            description="Adding required properties to exported interfaces breaks existing implementations.",
                            file_path=file_path,
                            line_number=j+1,
                            code_snippet=lines[j].strip(),
                            fix_suggestion="Make new properties optional with '?' or provide default values.",
                            confidence_score=0.85
                        ))
                        break
        
        return findings
    
    def _detect_csharp_breaking_changes(self, file_path: str, content: str) -> List[IssueFinding]:
        """Detect C#-specific breaking changes."""
        findings = []
        lines = content.split('\n')
        
        # Pattern: Public method signature changes
        public_method_pattern = re.compile(r'^\s*public\s+\w+\s+(\w+)\s*\(([^)]*)\)')
        for i, line in enumerate(lines, 1):
            match = public_method_pattern.search(line)
            if match:
                method_name = match.group(1)
                params = match.group(2).strip()
                
                if not params:
                    findings.append(IssueFinding(
                        category=IssueCategory.BREAKING_CHANGE,
                        severity=IssueSeverity.WARNING,
                        title=f"Public method '{method_name}' has no parameters",
                        description=f"If parameters were removed from '{method_name}', this breaks callers.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip(),
                        fix_suggestion="Use method overloading to maintain backward compatibility.",
                        confidence_score=0.60
                    ))
        
        return findings


class CodeSmellAnalyzer(BaseAnalyzer):
    """Detects code smells using pattern matching."""
    
    @property
    def name(self) -> str:
        return "Code Smell Analyzer"
    
    def analyze(self, file_paths: List[str], file_contents: Optional[Dict[str, str]] = None) -> AnalysisResult:
        """Detect code smells."""
        import time
        start_time = time.time()
        
        result = AnalysisResult(analyzer_name=self.name)
        
        for file_path in file_paths:
            content = file_contents.get(file_path) if file_contents else self._read_file(file_path)
            if not content:
                continue
            
            result.files_analyzed += 1
            
            # Detect various code smells
            result.findings.extend(self._detect_long_methods(file_path, content))
            result.findings.extend(self._detect_large_classes(file_path, content))
            result.findings.extend(self._detect_duplicated_code(file_path, content))
            result.findings.extend(self._detect_complex_conditions(file_path, content))
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    def _detect_long_methods(self, file_path: str, content: str) -> List[IssueFinding]:
        """Detect methods that are too long."""
        findings = []
        lines = content.split('\n')
        
        # Find function/method definitions
        func_pattern = re.compile(r'^\s*(def|function|public|private|protected)\s+\w+')
        current_func = None
        func_start_line = 0
        indent_level = 0
        
        for i, line in enumerate(lines, 1):
            if func_pattern.search(line):
                # Save previous function if it was long
                if current_func and (i - func_start_line) > 50:
                    findings.append(IssueFinding(
                        category=IssueCategory.CODE_SMELL,
                        severity=IssueSeverity.SUGGESTION,
                        title=f"Long method: '{current_func}' ({i - func_start_line} lines)",
                        description=f"Method '{current_func}' is {i - func_start_line} lines long. Consider breaking it into smaller methods.",
                        file_path=file_path,
                        line_number=func_start_line,
                        fix_suggestion="Extract logical blocks into separate methods. Aim for <30 lines per method.",
                        confidence_score=0.90
                    ))
                
                # Start tracking new function
                func_match = re.search(r'(def|function)\s+(\w+)', line)
                if func_match:
                    current_func = func_match.group(2)
                    func_start_line = i
                    indent_level = len(line) - len(line.lstrip())
        
        # Check last function
        if current_func and (len(lines) - func_start_line) > 50:
            findings.append(IssueFinding(
                category=IssueCategory.CODE_SMELL,
                severity=IssueSeverity.SUGGESTION,
                title=f"Long method: '{current_func}' ({len(lines) - func_start_line} lines)",
                description=f"Method '{current_func}' is {len(lines) - func_start_line} lines long. Consider breaking it into smaller methods.",
                file_path=file_path,
                line_number=func_start_line,
                fix_suggestion="Extract logical blocks into separate methods. Aim for <30 lines per method.",
                confidence_score=0.90
            ))
        
        return findings
    
    def _detect_large_classes(self, file_path: str, content: str) -> List[IssueFinding]:
        """Detect classes that are too large."""
        findings = []
        lines = content.split('\n')
        
        # Count lines per class
        class_pattern = re.compile(r'^\s*class\s+(\w+)')
        current_class = None
        class_start_line = 0
        
        for i, line in enumerate(lines, 1):
            if class_pattern.match(line):
                # Check previous class
                if current_class and (i - class_start_line) > 300:
                    findings.append(IssueFinding(
                        category=IssueCategory.CODE_SMELL,
                        severity=IssueSeverity.WARNING,
                        title=f"Large class: '{current_class}' ({i - class_start_line} lines)",
                        description=f"Class '{current_class}' is {i - class_start_line} lines long. This violates Single Responsibility Principle.",
                        file_path=file_path,
                        line_number=class_start_line,
                        fix_suggestion="Split class into smaller classes with focused responsibilities. Aim for <200 lines per class.",
                        confidence_score=0.85
                    ))
                
                current_class = class_pattern.match(line).group(1)
                class_start_line = i
        
        # Check last class
        if current_class and (len(lines) - class_start_line) > 300:
            findings.append(IssueFinding(
                category=IssueCategory.CODE_SMELL,
                severity=IssueSeverity.WARNING,
                title=f"Large class: '{current_class}' ({len(lines) - class_start_line} lines)",
                description=f"Class '{current_class}' is {len(lines) - class_start_line} lines long. This violates Single Responsibility Principle.",
                file_path=file_path,
                line_number=class_start_line,
                fix_suggestion="Split class into smaller classes with focused responsibilities. Aim for <200 lines per class.",
                confidence_score=0.85
            ))
        
        return findings
    
    def _detect_duplicated_code(self, file_path: str, content: str) -> List[IssueFinding]:
        """Detect duplicated code blocks."""
        findings = []
        lines = content.split('\n')
        
        # Simple heuristic: Look for identical sequential lines (>5 lines)
        seen_blocks = {}
        block_size = 5
        
        for i in range(len(lines) - block_size):
            block = '\n'.join(lines[i:i+block_size]).strip()
            if block and len(block) > 50:  # Ignore small/empty blocks
                if block in seen_blocks:
                    findings.append(IssueFinding(
                        category=IssueCategory.CODE_SMELL,
                        severity=IssueSeverity.WARNING,
                        title=f"Duplicated code block at line {i+1}",
                        description=f"Code block at line {i+1} appears to be duplicated (also at line {seen_blocks[block]}).",
                        file_path=file_path,
                        line_number=i+1,
                        code_snippet=lines[i].strip()[:80] + "...",
                        fix_suggestion="Extract duplicated code into a reusable function/method.",
                        confidence_score=0.75
                    ))
                else:
                    seen_blocks[block] = i+1
        
        return findings
    
    def _detect_complex_conditions(self, file_path: str, content: str) -> List[IssueFinding]:
        """Detect overly complex conditional logic."""
        findings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Count logical operators
            and_count = line.count(' and ') + line.count(' && ')
            or_count = line.count(' or ') + line.count(' || ')
            
            if and_count + or_count >= 3:
                findings.append(IssueFinding(
                    category=IssueCategory.CODE_SMELL,
                    severity=IssueSeverity.SUGGESTION,
                    title=f"Complex condition at line {i}",
                    description=f"Conditional has {and_count + or_count} logical operators, making it hard to understand.",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip()[:80] + "...",
                    fix_suggestion="Extract complex conditions into well-named boolean variables or methods.",
                    confidence_score=0.80
                ))
        
        return findings


class BestPracticesAnalyzer(BaseAnalyzer):
    """Validates adherence to best practices."""
    
    @property
    def name(self) -> str:
        return "Best Practices Validator"
    
    def analyze(self, file_paths: List[str], file_contents: Optional[Dict[str, str]] = None) -> AnalysisResult:
        """Validate best practices."""
        import time
        start_time = time.time()
        
        result = AnalysisResult(analyzer_name=self.name)
        
        for file_path in file_paths:
            content = file_contents.get(file_path) if file_contents else self._read_file(file_path)
            if not content:
                continue
            
            result.files_analyzed += 1
            
            # Check various best practices
            result.findings.extend(self._check_error_handling(file_path, content))
            result.findings.extend(self._check_naming_conventions(file_path, content))
            result.findings.extend(self._check_magic_numbers(file_path, content))
            result.findings.extend(self._check_todo_comments(file_path, content))
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    def _check_error_handling(self, file_path: str, content: str) -> List[IssueFinding]:
        """Check for proper error handling."""
        findings = []
        lines = content.split('\n')
        
        # Pattern 1: Empty except blocks
        in_except = False
        except_line = 0
        
        for i, line in enumerate(lines, 1):
            if re.match(r'^\s*except', line):
                in_except = True
                except_line = i
            elif in_except:
                if line.strip() == 'pass' or line.strip() == '':
                    findings.append(IssueFinding(
                        category=IssueCategory.BEST_PRACTICE,
                        severity=IssueSeverity.WARNING,
                        title=f"Empty except block at line {except_line}",
                        description="Empty except blocks silently swallow errors, making debugging difficult.",
                        file_path=file_path,
                        line_number=except_line,
                        fix_suggestion="Log the error or re-raise with context. At minimum, add a comment explaining why ignoring is safe.",
                        confidence_score=0.90
                    ))
                in_except = False
        
        # Pattern 2: Bare except
        for i, line in enumerate(lines, 1):
            if re.match(r'^\s*except\s*:', line):
                findings.append(IssueFinding(
                    category=IssueCategory.BEST_PRACTICE,
                    severity=IssueSeverity.WARNING,
                    title=f"Bare except clause at line {i}",
                    description="Bare 'except:' catches all exceptions including KeyboardInterrupt and SystemExit.",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip(),
                    fix_suggestion="Specify exception type(s) to catch, or use 'except Exception:' at minimum.",
                    confidence_score=0.95
                ))
        
        return findings
    
    def _check_naming_conventions(self, file_path: str, content: str) -> List[IssueFinding]:
        """Check naming convention violations."""
        findings = []
        lines = content.split('\n')
        language = self._detect_language(file_path)
        
        if language == 'python':
            # Check for non-snake_case function names
            func_pattern = re.compile(r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)')
            for i, line in enumerate(lines, 1):
                match = func_pattern.match(line)
                if match:
                    func_name = match.group(1)
                    # Check for camelCase (should be snake_case in Python)
                    if re.search(r'[a-z][A-Z]', func_name) and not func_name.startswith('_'):
                        findings.append(IssueFinding(
                            category=IssueCategory.BEST_PRACTICE,
                            severity=IssueSeverity.SUGGESTION,
                            title=f"Non-standard function name: '{func_name}'",
                            description=f"Function '{func_name}' uses camelCase. PEP 8 recommends snake_case for functions.",
                            file_path=file_path,
                            line_number=i,
                            code_snippet=line.strip(),
                            fix_suggestion=f"Rename to '{self._to_snake_case(func_name)}'",
                            confidence_score=0.85
                        ))
        
        return findings
    
    def _to_snake_case(self, name: str) -> str:
        """Convert camelCase to snake_case."""
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    
    def _check_magic_numbers(self, file_path: str, content: str) -> List[IssueFinding]:
        """Check for magic numbers."""
        findings = []
        lines = content.split('\n')
        
        # Look for numeric literals (excluding 0, 1, -1 which are common)
        magic_number_pattern = re.compile(r'\b(\d{2,})\b')
        
        for i, line in enumerate(lines, 1):
            # Skip comments and strings
            if line.strip().startswith('#') or line.strip().startswith('//'):
                continue
            
            matches = magic_number_pattern.findall(line)
            for match in matches:
                if match not in ['10', '100', '1000']:  # Common powers of 10
                    findings.append(IssueFinding(
                        category=IssueCategory.BEST_PRACTICE,
                        severity=IssueSeverity.SUGGESTION,
                        title=f"Magic number '{match}' at line {i}",
                        description=f"Numeric literal '{match}' lacks context. Consider using a named constant.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip()[:80],
                        fix_suggestion=f"Define a constant: SOME_MEANINGFUL_NAME = {match}",
                        confidence_score=0.70
                    ))
                    break  # Only report one per line
        
        return findings
    
    def _check_todo_comments(self, file_path: str, content: str) -> List[IssueFinding]:
        """Check for TODO comments."""
        findings = []
        lines = content.split('\n')
        
        todo_pattern = re.compile(r'#\s*TODO|//\s*TODO', re.IGNORECASE)
        
        for i, line in enumerate(lines, 1):
            if todo_pattern.search(line):
                findings.append(IssueFinding(
                    category=IssueCategory.BEST_PRACTICE,
                    severity=IssueSeverity.SUGGESTION,
                    title=f"TODO comment at line {i}",
                    description="TODO comments indicate incomplete work. Consider completing or creating a tracking issue.",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip(),
                    fix_suggestion="Complete the TODO or create a GitHub issue and reference it in the comment.",
                    confidence_score=0.95
                ))
        
        return findings


class SecurityAnalyzer(BaseAnalyzer):
    """Detects security vulnerabilities."""
    
    @property
    def name(self) -> str:
        return "Security Scanner"
    
    def analyze(self, file_paths: List[str], file_contents: Optional[Dict[str, str]] = None) -> AnalysisResult:
        """Scan for security vulnerabilities."""
        import time
        start_time = time.time()
        
        result = AnalysisResult(analyzer_name=self.name)
        
        for file_path in file_paths:
            content = file_contents.get(file_path) if file_contents else self._read_file(file_path)
            if not content:
                continue
            
            result.files_analyzed += 1
            
            # Security checks
            result.findings.extend(self._detect_hardcoded_secrets(file_path, content))
            result.findings.extend(self._detect_sql_injection(file_path, content))
            result.findings.extend(self._detect_xss_vulnerabilities(file_path, content))
            result.findings.extend(self._detect_insecure_functions(file_path, content))
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    def _detect_hardcoded_secrets(self, file_path: str, content: str) -> List[IssueFinding]:
        """Detect hardcoded secrets."""
        findings = []
        lines = content.split('\n')
        
        # Patterns for common secret types
        secret_patterns = [
            (r'password\s*=\s*["\']([^"\']+)["\']', 'password'),
            (r'api[_-]?key\s*=\s*["\']([^"\']+)["\']', 'API key'),
            (r'secret\s*=\s*["\']([^"\']+)["\']', 'secret'),
            (r'token\s*=\s*["\']([^"\']+)["\']', 'token'),
            (r'aws[_-]?access[_-]?key\s*=\s*["\']([^"\']+)["\']', 'AWS key'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, secret_type in secret_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    value = match.group(1)
                    # Skip obvious placeholders
                    if value.lower() in ['', 'your_password', 'your_key', 'xxx', 'placeholder']:
                        continue
                    
                    findings.append(IssueFinding(
                        category=IssueCategory.SECURITY,
                        severity=IssueSeverity.CRITICAL,
                        title=f"Hardcoded {secret_type} at line {i}",
                        description=f"Detected hardcoded {secret_type}. Secrets should never be committed to source control.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip()[:50] + "...",
                        fix_suggestion=f"Use environment variables or a secrets manager. Remove the secret from git history.",
                        confidence_score=0.85
                    ))
        
        return findings
    
    def _detect_sql_injection(self, file_path: str, content: str) -> List[IssueFinding]:
        """Detect potential SQL injection vulnerabilities."""
        findings = []
        lines = content.split('\n')
        
        # Pattern: String concatenation in SQL queries
        sql_concat_patterns = [
            r'execute\s*\([^)]*\+',
            r'query\s*\([^)]*\+',
            r'SELECT.*\+.*FROM',
            r'INSERT.*\+.*INTO',
            r'UPDATE.*\+.*SET',
            r'DELETE.*\+.*FROM',
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in sql_concat_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(IssueFinding(
                        category=IssueCategory.SECURITY,
                        severity=IssueSeverity.CRITICAL,
                        title=f"Potential SQL injection at line {i}",
                        description="SQL query appears to use string concatenation, which is vulnerable to SQL injection.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip()[:80],
                        fix_suggestion="Use parameterized queries or an ORM. Never concatenate user input into SQL.",
                        confidence_score=0.80
                    ))
                    break
        
        return findings
    
    def _detect_xss_vulnerabilities(self, file_path: str, content: str) -> List[IssueFinding]:
        """Detect potential XSS vulnerabilities."""
        findings = []
        lines = content.split('\n')
        
        # Pattern: Unescaped HTML rendering
        xss_patterns = [
            r'innerHTML\s*=',
            r'dangerouslySetInnerHTML',
            r'document\.write\s*\(',
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in xss_patterns:
                if re.search(pattern, line):
                    findings.append(IssueFinding(
                        category=IssueCategory.SECURITY,
                        severity=IssueSeverity.CRITICAL,
                        title=f"Potential XSS vulnerability at line {i}",
                        description="Direct HTML injection without sanitization can lead to XSS attacks.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip()[:80],
                        fix_suggestion="Sanitize user input before rendering. Use textContent instead of innerHTML.",
                        confidence_score=0.75
                    ))
                    break
        
        return findings
    
    def _detect_insecure_functions(self, file_path: str, content: str) -> List[IssueFinding]:
        """Detect usage of insecure functions."""
        findings = []
        lines = content.split('\n')
        
        # Insecure functions by language
        insecure_funcs = {
            'eval(': 'Arbitrary code execution',
            'exec(': 'Arbitrary code execution',
            'pickle.loads(': 'Insecure deserialization',
            'yaml.load(': 'Insecure YAML parsing',
            'subprocess.call(': 'Command injection risk',
        }
        
        for i, line in enumerate(lines, 1):
            for func, risk in insecure_funcs.items():
                if func in line:
                    findings.append(IssueFinding(
                        category=IssueCategory.SECURITY,
                        severity=IssueSeverity.CRITICAL,
                        title=f"Insecure function '{func.rstrip('(')}' at line {i}",
                        description=f"Function '{func.rstrip('(')}' is insecure: {risk}.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip()[:80],
                        fix_suggestion=self._get_secure_alternative(func),
                        confidence_score=0.90
                    ))
        
        return findings
    
    def _get_secure_alternative(self, insecure_func: str) -> str:
        """Get secure alternative for insecure function."""
        alternatives = {
            'eval(': 'Avoid eval(). Use ast.literal_eval() for safe evaluation of literals.',
            'exec(': 'Avoid exec(). Refactor to use safe alternatives.',
            'pickle.loads(': 'Use json.loads() instead, or validate pickle data source.',
            'yaml.load(': 'Use yaml.safe_load() instead of yaml.load().',
            'subprocess.call(': 'Use subprocess.run() with shell=False and validate inputs.',
        }
        return alternatives.get(insecure_func, 'Find a secure alternative.')


class PerformanceAnalyzer(BaseAnalyzer):
    """Detects performance issues."""
    
    @property
    def name(self) -> str:
        return "Performance Profiler"
    
    def analyze(self, file_paths: List[str], file_contents: Optional[Dict[str, str]] = None) -> AnalysisResult:
        """Detect performance issues."""
        import time
        start_time = time.time()
        
        result = AnalysisResult(analyzer_name=self.name)
        
        for file_path in file_paths:
            content = file_contents.get(file_path) if file_contents else self._read_file(file_path)
            if not content:
                continue
            
            result.files_analyzed += 1
            
            # Performance checks
            result.findings.extend(self._detect_nested_loops(file_path, content))
            result.findings.extend(self._detect_n_plus_one_queries(file_path, content))
            result.findings.extend(self._detect_inefficient_operations(file_path, content))
        
        result.execution_time_ms = (time.time() - start_time) * 1000
        return result
    
    def _detect_nested_loops(self, file_path: str, content: str) -> List[IssueFinding]:
        """Detect nested loops (O(n²) or worse)."""
        findings = []
        lines = content.split('\n')
        
        loop_depth = 0
        loop_stack = []
        
        for i, line in enumerate(lines, 1):
            # Check for loop start
            if re.match(r'^\s*(for|while)\s+', line):
                loop_depth += 1
                loop_stack.append(i)
                
                if loop_depth >= 3:
                    findings.append(IssueFinding(
                        category=IssueCategory.PERFORMANCE,
                        severity=IssueSeverity.WARNING,
                        title=f"Deeply nested loop (depth {loop_depth}) at line {i}",
                        description=f"Loop nesting depth of {loop_depth} results in O(n^{loop_depth}) complexity.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip()[:80],
                        fix_suggestion="Consider using more efficient data structures (dict/set) or algorithms to reduce complexity.",
                        confidence_score=0.85
                    ))
            
            # Rough heuristic for loop end (dedent)
            if loop_depth > 0 and line.strip() and not line.startswith(' ' * (loop_depth * 4)):
                if loop_stack:
                    loop_stack.pop()
                loop_depth = max(0, loop_depth - 1)
        
        return findings
    
    def _detect_n_plus_one_queries(self, file_path: str, content: str) -> List[IssueFinding]:
        """Detect N+1 query patterns."""
        findings = []
        lines = content.split('\n')
        
        in_loop = False
        loop_line = 0
        
        for i, line in enumerate(lines, 1):
            if re.match(r'^\s*(for|while)\s+', line):
                in_loop = True
                loop_line = i
            elif in_loop:
                # Check for database queries inside loops
                if any(pattern in line.lower() for pattern in ['query', 'select', 'find', 'get', '.filter(']):
                    findings.append(IssueFinding(
                        category=IssueCategory.PERFORMANCE,
                        severity=IssueSeverity.WARNING,
                        title=f"Potential N+1 query at line {i}",
                        description="Database query inside a loop can cause N+1 query problem.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip()[:80],
                        fix_suggestion="Fetch all required data before the loop using joins or batch queries.",
                        confidence_score=0.70
                    ))
                    in_loop = False  # Only report once per loop
                
                # Exit loop detection on dedent
                if line.strip() and not line.startswith(' ' * 4):
                    in_loop = False
        
        return findings
    
    def _detect_inefficient_operations(self, file_path: str, content: str) -> List[IssueFinding]:
        """Detect inefficient operations."""
        findings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Pattern 1: List comprehension with append (should use list comp directly)
            if '.append(' in line and 'for' in line:
                findings.append(IssueFinding(
                    category=IssueCategory.PERFORMANCE,
                    severity=IssueSeverity.SUGGESTION,
                    title=f"Inefficient list building at line {i}",
                    description="Using append in a loop is less efficient than list comprehension.",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip()[:80],
                    fix_suggestion="Use list comprehension: result = [x for x in items]",
                    confidence_score=0.75
                ))
            
            # Pattern 2: String concatenation in loop
            if re.search(r'(\+=|=.*\+).*["\']', line) and i > 1:
                prev_line = lines[i-2] if i > 1 else ''
                if 'for' in prev_line or 'while' in prev_line:
                    findings.append(IssueFinding(
                        category=IssueCategory.PERFORMANCE,
                        severity=IssueSeverity.SUGGESTION,
                        title=f"String concatenation in loop at line {i}",
                        description="String concatenation in loops is inefficient due to string immutability.",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip()[:80],
                        fix_suggestion="Use list and ''.join() or io.StringIO for better performance.",
                        confidence_score=0.80
                    ))
        
        return findings
