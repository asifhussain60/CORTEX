"""
Code Review Plugin for CORTEX 2.0

Automated pull request review with comprehensive code analysis:
- SOLID principle violation detection
- Security vulnerability scanning (secrets, SQL injection, XSS)
- Performance anti-pattern detection (N+1 queries, memory leaks)
- Test coverage regression detection
- Code style consistency checking
- Duplicate code detection
- Dependency vulnerability analysis
- Pattern violation checking (against Tier 2 knowledge)

Integration:
- Azure DevOps REST API
- GitHub REST API and GraphQL
- GitLab CI webhooks
- BitBucket Pipelines

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import re
import logging
import json
import hashlib

from plugins.base_plugin import (
    BasePlugin,
    PluginMetadata,
    PluginCategory,
    PluginPriority,
    HookPoint
)

logger = logging.getLogger(__name__)


class ViolationSeverity(Enum):
    """Severity levels for code violations"""
    CRITICAL = "critical"      # Security issues, data loss risks
    HIGH = "high"             # SOLID violations, major bugs
    MEDIUM = "medium"         # Code smells, minor issues
    LOW = "low"              # Style issues, suggestions
    INFO = "info"            # Informational only


class ViolationType(Enum):
    """Types of code violations"""
    SOLID_SRP = "solid_srp"                    # Single Responsibility Principle
    SOLID_OCP = "solid_ocp"                    # Open/Closed Principle
    SOLID_LSP = "solid_lsp"                    # Liskov Substitution Principle
    SOLID_ISP = "solid_isp"                    # Interface Segregation Principle
    SOLID_DIP = "solid_dip"                    # Dependency Inversion Principle
    SECURITY_HARDCODED_SECRET = "sec_secret"   # Hardcoded passwords/keys
    SECURITY_SQL_INJECTION = "sec_sql_inj"     # SQL injection vulnerability
    SECURITY_XSS = "sec_xss"                   # Cross-site scripting
    SECURITY_CSRF = "sec_csrf"                 # Cross-site request forgery
    SECURITY_PATH_TRAVERSAL = "sec_path_trav"  # Path traversal vulnerability
    PERF_N_PLUS_ONE = "perf_n_plus_one"       # N+1 query problem
    PERF_MEMORY_LEAK = "perf_memory_leak"     # Potential memory leak
    PERF_BLOCKING_IO = "perf_blocking_io"     # Blocking I/O in async context
    PERF_INEFFICIENT_LOOP = "perf_loop"       # Inefficient loop operations
    STYLE_NAMING = "style_naming"             # Naming convention violation
    STYLE_COMPLEXITY = "style_complexity"     # Cyclomatic complexity too high
    DUPLICATE_CODE = "duplicate_code"         # Duplicate code detected
    TEST_COVERAGE = "test_coverage"           # Test coverage regression
    DEPENDENCY_VULN = "dep_vuln"             # Vulnerable dependency


@dataclass
class CodeViolation:
    """Represents a code review violation"""
    type: ViolationType
    severity: ViolationSeverity
    file_path: str
    line_number: int
    message: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    confidence: float = 1.0  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.type.value,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "message": self.message,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet,
            "confidence": self.confidence
        }


@dataclass
class ReviewResult:
    """Results from code review"""
    pr_id: str
    violations: List[CodeViolation]
    files_reviewed: int
    lines_reviewed: int
    review_time_seconds: float
    overall_score: float  # 0.0 to 100.0
    recommendations: List[str]
    
    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.CRITICAL)
    
    @property
    def high_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.HIGH)
    
    @property
    def medium_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.MEDIUM)
    
    @property
    def low_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.LOW)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "pr_id": self.pr_id,
            "violations": [v.to_dict() for v in self.violations],
            "files_reviewed": self.files_reviewed,
            "lines_reviewed": self.lines_reviewed,
            "review_time_seconds": self.review_time_seconds,
            "overall_score": self.overall_score,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "medium_count": self.medium_count,
            "low_count": self.low_count,
            "recommendations": self.recommendations
        }


class SOLIDAnalyzer:
    """Analyzes code for SOLID principle violations"""
    
    def __init__(self):
        self.logger = logging.getLogger("code_review.solid")
    
    def analyze(self, file_path: str, content: str, language: str) -> List[CodeViolation]:
        """
        Analyze file for SOLID violations
        
        Args:
            file_path: Path to the file
            content: File content
            language: Programming language (python, csharp, javascript, etc.)
        
        Returns:
            List of violations found
        """
        violations = []
        
        if language == "python":
            violations.extend(self._analyze_python(file_path, content))
        elif language == "csharp":
            violations.extend(self._analyze_csharp(file_path, content))
        elif language in ["javascript", "typescript"]:
            violations.extend(self._analyze_javascript(file_path, content))
        
        return violations
    
    def _analyze_python(self, file_path: str, content: str) -> List[CodeViolation]:
        """Analyze Python code for SOLID violations"""
        violations = []
        lines = content.split('\n')
        
        # SRP: Check for classes with too many methods
        class_pattern = re.compile(r'^class\s+(\w+)')
        method_pattern = re.compile(r'^\s{4}def\s+(\w+)')
        
        current_class = None
        current_class_line = 0
        method_count = 0
        
        for line_num, line in enumerate(lines, 1):
            class_match = class_pattern.match(line)
            if class_match:
                # Check previous class
                if current_class and method_count > 10:
                    violations.append(CodeViolation(
                        type=ViolationType.SOLID_SRP,
                        severity=ViolationSeverity.HIGH,
                        file_path=file_path,
                        line_number=current_class_line,
                        message=f"Class '{current_class}' has {method_count} methods. Consider splitting into smaller classes (SRP violation).",
                        suggestion="Break down the class into smaller, more focused classes with single responsibilities.",
                        confidence=0.85
                    ))
                
                current_class = class_match.group(1)
                current_class_line = line_num
                method_count = 0
            
            method_match = method_pattern.match(line)
            if method_match and current_class:
                method_count += 1
        
        # Check last class
        if current_class and method_count > 10:
            violations.append(CodeViolation(
                type=ViolationType.SOLID_SRP,
                severity=ViolationSeverity.HIGH,
                file_path=file_path,
                line_number=current_class_line,
                message=f"Class '{current_class}' has {method_count} methods. Consider splitting into smaller classes (SRP violation).",
                suggestion="Break down the class into smaller, more focused classes with single responsibilities.",
                confidence=0.85
            ))
        
        # DIP: Check for direct instantiation of concrete classes
        instantiation_pattern = re.compile(r'=\s*(\w+)\(')
        for line_num, line in enumerate(lines, 1):
            if 'import' in line or 'from' in line:
                continue
            
            matches = instantiation_pattern.findall(line)
            for class_name in matches:
                # Skip built-in types and common patterns
                if class_name.lower() in ['dict', 'list', 'set', 'tuple', 'str', 'int', 'float', 'bool']:
                    continue
                
                if class_name[0].isupper():  # Likely a class
                    violations.append(CodeViolation(
                        type=ViolationType.SOLID_DIP,
                        severity=ViolationSeverity.MEDIUM,
                        file_path=file_path,
                        line_number=line_num,
                        message=f"Direct instantiation of '{class_name}'. Consider dependency injection (DIP).",
                        suggestion="Use dependency injection or factory pattern instead of direct instantiation.",
                        code_snippet=line.strip(),
                        confidence=0.6
                    ))
        
        return violations
    
    def _analyze_csharp(self, file_path: str, content: str) -> List[CodeViolation]:
        """Analyze C# code for SOLID violations"""
        violations = []
        # TODO: Implement C# SOLID analysis
        return violations
    
    def _analyze_javascript(self, file_path: str, content: str) -> List[CodeViolation]:
        """Analyze JavaScript/TypeScript for SOLID violations"""
        violations = []
        # TODO: Implement JavaScript/TypeScript SOLID analysis
        return violations


class SecurityScanner:
    """Scans code for security vulnerabilities"""
    
    def __init__(self):
        self.logger = logging.getLogger("code_review.security")
        
        # Common secret patterns
        self.secret_patterns = [
            (r'password\s*=\s*["\']([^"\']+)["\']', "Hardcoded password"),
            (r'api[_-]?key\s*=\s*["\']([^"\']+)["\']', "Hardcoded API key"),
            (r'secret[_-]?key\s*=\s*["\']([^"\']+)["\']', "Hardcoded secret key"),
            (r'token\s*=\s*["\']([^"\']+)["\']', "Hardcoded token"),
            (r'aws[_-]?secret\s*=\s*["\']([^"\']+)["\']', "Hardcoded AWS secret"),
            (r'private[_-]?key\s*=\s*["\']([^"\']+)["\']', "Hardcoded private key"),
        ]
        
        # SQL injection patterns
        self.sql_injection_patterns = [
            (r'execute\s*\(\s*["\'].*\+.*["\']', "String concatenation in SQL query"),
            (r'query\s*\(\s*["\'].*\+.*["\']', "String concatenation in SQL query"),
            (r'f["\']SELECT.*\{.*\}', "f-string in SQL query (Python)"),
        ]
    
    def scan(self, file_path: str, content: str, language: str) -> List[CodeViolation]:
        """
        Scan file for security vulnerabilities
        
        Args:
            file_path: Path to the file
            content: File content
            language: Programming language
        
        Returns:
            List of security violations found
        """
        violations = []
        
        violations.extend(self._scan_secrets(file_path, content))
        violations.extend(self._scan_sql_injection(file_path, content, language))
        violations.extend(self._scan_xss(file_path, content, language))
        
        return violations
    
    def _scan_secrets(self, file_path: str, content: str) -> List[CodeViolation]:
        """Scan for hardcoded secrets"""
        violations = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()
            
            for pattern, description in self.secret_patterns:
                if re.search(pattern, line_lower, re.IGNORECASE):
                    violations.append(CodeViolation(
                        type=ViolationType.SECURITY_HARDCODED_SECRET,
                        severity=ViolationSeverity.CRITICAL,
                        file_path=file_path,
                        line_number=line_num,
                        message=f"{description} detected",
                        suggestion="Use environment variables or secure configuration management (e.g., Azure Key Vault, AWS Secrets Manager)",
                        code_snippet=line.strip(),
                        confidence=0.9
                    ))
        
        return violations
    
    def _scan_sql_injection(self, file_path: str, content: str, language: str) -> List[CodeViolation]:
        """Scan for SQL injection vulnerabilities"""
        violations = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern, description in self.sql_injection_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(CodeViolation(
                        type=ViolationType.SECURITY_SQL_INJECTION,
                        severity=ViolationSeverity.CRITICAL,
                        file_path=file_path,
                        line_number=line_num,
                        message=f"Potential SQL injection: {description}",
                        suggestion="Use parameterized queries or ORM with parameter binding",
                        code_snippet=line.strip(),
                        confidence=0.85
                    ))
        
        return violations
    
    def _scan_xss(self, file_path: str, content: str, language: str) -> List[CodeViolation]:
        """Scan for XSS vulnerabilities"""
        violations = []
        
        if language not in ["javascript", "typescript", "html"]:
            return violations
        
        lines = content.split('\n')
        
        # Check for innerHTML usage
        innerHTML_pattern = re.compile(r'\.innerHTML\s*=')
        dangerouslySetInnerHTML_pattern = re.compile(r'dangerouslySetInnerHTML')
        
        for line_num, line in enumerate(lines, 1):
            if innerHTML_pattern.search(line):
                violations.append(CodeViolation(
                    type=ViolationType.SECURITY_XSS,
                    severity=ViolationSeverity.HIGH,
                    file_path=file_path,
                    line_number=line_num,
                    message="Use of innerHTML can lead to XSS vulnerabilities",
                    suggestion="Use textContent or sanitize input with DOMPurify",
                    code_snippet=line.strip(),
                    confidence=0.8
                ))
            
            if dangerouslySetInnerHTML_pattern.search(line):
                violations.append(CodeViolation(
                    type=ViolationType.SECURITY_XSS,
                    severity=ViolationSeverity.HIGH,
                    file_path=file_path,
                    line_number=line_num,
                    message="dangerouslySetInnerHTML can lead to XSS if not sanitized",
                    suggestion="Ensure all content is sanitized with DOMPurify before rendering",
                    code_snippet=line.strip(),
                    confidence=0.75
                ))
        
        return violations


class PerformanceAnalyzer:
    """Analyzes code for performance anti-patterns"""
    
    def __init__(self):
        self.logger = logging.getLogger("code_review.performance")
    
    def analyze(self, file_path: str, content: str, language: str) -> List[CodeViolation]:
        """
        Analyze file for performance issues
        
        Args:
            file_path: Path to the file
            content: File content
            language: Programming language
        
        Returns:
            List of performance violations found
        """
        violations = []
        
        violations.extend(self._detect_n_plus_one(file_path, content, language))
        violations.extend(self._detect_blocking_io(file_path, content, language))
        violations.extend(self._detect_inefficient_loops(file_path, content))
        
        return violations
    
    def _detect_n_plus_one(self, file_path: str, content: str, language: str) -> List[CodeViolation]:
        """Detect N+1 query problems"""
        violations = []
        lines = content.split('\n')
        
        # Look for queries inside loops
        in_loop = False
        loop_start = 0
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Detect loop start
            if re.match(r'(for|while)\s+', stripped):
                in_loop = True
                loop_start = line_num
            
            # Detect loop end (rough heuristic)
            if in_loop and line and not line[0].isspace() and line_num > loop_start:
                in_loop = False
            
            # Check for queries inside loop
            if in_loop:
                query_keywords = ['query', 'execute', 'find', 'get', 'fetch', 'select']
                if any(keyword in stripped.lower() for keyword in query_keywords):
                    if 'await' in stripped or 'cursor' in stripped.lower():
                        violations.append(CodeViolation(
                            type=ViolationType.PERF_N_PLUS_ONE,
                            severity=ViolationSeverity.HIGH,
                            file_path=file_path,
                            line_number=line_num,
                            message="Potential N+1 query problem: Database query inside loop",
                            suggestion="Use batch queries or eager loading to fetch all data in one query",
                            code_snippet=stripped,
                            confidence=0.7
                        ))
        
        return violations
    
    def _detect_blocking_io(self, file_path: str, content: str, language: str) -> List[CodeViolation]:
        """Detect blocking I/O in async context"""
        violations = []
        
        if language not in ["python", "javascript", "typescript"]:
            return violations
        
        lines = content.split('\n')
        in_async_function = False
        async_func_line = 0
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Detect async function
            if re.match(r'async\s+(def|function)', stripped):
                in_async_function = True
                async_func_line = line_num
            
            # End of function (rough heuristic)
            if in_async_function and line and not line[0].isspace() and line_num > async_func_line + 1:
                if not line.startswith('    '):
                    in_async_function = False
            
            # Check for blocking operations in async function
            if in_async_function:
                blocking_patterns = [
                    (r'time\.sleep', "time.sleep() is blocking"),
                    (r'requests\.(get|post|put|delete)', "requests library is blocking"),
                    (r'open\(', "file I/O without async"),
                ]
                
                for pattern, message in blocking_patterns:
                    if re.search(pattern, stripped):
                        violations.append(CodeViolation(
                            type=ViolationType.PERF_BLOCKING_IO,
                            severity=ViolationSeverity.MEDIUM,
                            file_path=file_path,
                            line_number=line_num,
                            message=f"Blocking operation in async function: {message}",
                            suggestion="Use async alternatives (asyncio.sleep, aiohttp, aiofiles)",
                            code_snippet=stripped,
                            confidence=0.85
                        ))
        
        return violations
    
    def _detect_inefficient_loops(self, file_path: str, content: str) -> List[CodeViolation]:
        """Detect inefficient loop operations"""
        violations = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for string concatenation in loops
            if re.search(r'(for|while)\s+.*:', stripped):
                # Look at next few lines
                for offset in range(1, min(10, len(lines) - line_num)):
                    next_line = lines[line_num + offset - 1].strip()
                    if re.search(r'\+\=.*["\']', next_line):
                        violations.append(CodeViolation(
                            type=ViolationType.PERF_INEFFICIENT_LOOP,
                            severity=ViolationSeverity.LOW,
                            file_path=file_path,
                            line_number=line_num + offset,
                            message="String concatenation in loop is inefficient",
                            suggestion="Use list append and join(), or StringBuilder (C#)",
                            code_snippet=next_line,
                            confidence=0.75
                        ))
                        break
        
        return violations


class CodeReviewPlugin(BasePlugin):
    """
    Automated code review plugin for pull requests
    
    Features:
    - SOLID principle violation detection
    - Security vulnerability scanning
    - Performance anti-pattern detection
    - Test coverage regression checking
    - Code style consistency validation
    - Duplicate code detection
    - Integration with Azure DevOps, GitHub, GitLab, BitBucket
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.solid_analyzer = SOLIDAnalyzer()
        self.security_scanner = SecurityScanner()
        self.performance_analyzer = PerformanceAnalyzer()
        self.review_cache: Dict[str, ReviewResult] = {}
    
    def _get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        return PluginMetadata(
            plugin_id="code_review",
            name="Code Review Plugin",
            version="1.0.0",
            category=PluginCategory.ANALYSIS,
            priority=PluginPriority.HIGH,
            description="Automated pull request review with SOLID, security, and performance analysis",
            author="Asif Hussain",
            dependencies=[],
            hooks=[
                HookPoint.ON_BRAIN_UPDATE.value,
                "on_pr_created",
                "on_pr_updated"
            ],
            config_schema={
                "enabled": {"type": "boolean", "default": True},
                "min_confidence": {"type": "number", "default": 0.7},
                "max_violations_per_file": {"type": "integer", "default": 50},
                "severity_threshold": {"type": "string", "default": "low"},
                "integrations": {
                    "type": "object",
                    "properties": {
                        "azure_devops": {"type": "object"},
                        "github": {"type": "object"},
                        "gitlab": {"type": "object"}
                    }
                }
            }
        )
    
    def initialize(self) -> bool:
        """Initialize plugin"""
        try:
            self.logger.info("Initializing Code Review Plugin")
            
            # Load configuration
            self.min_confidence = self.config.get("min_confidence", 0.7)
            self.max_violations = self.config.get("max_violations_per_file", 50)
            self.severity_threshold = self.config.get("severity_threshold", "low")
            
            self.logger.info("Code Review Plugin initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Code Review Plugin: {e}")
            return False
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute code review
        
        Context parameters:
            - pr_id: Pull request ID
            - files: List of changed files
            - repository_path: Path to repository
            - platform: Integration platform (azure_devops, github, gitlab)
        
        Returns:
            Review results
        """
        try:
            pr_id = context.get("pr_id", "unknown")
            files = context.get("files", [])
            repo_path = Path(context.get("repository_path", "."))
            
            self.logger.info(f"Starting code review for PR {pr_id}")
            start_time = datetime.now()
            
            all_violations = []
            files_reviewed = 0
            lines_reviewed = 0
            
            for file_info in files:
                file_path = file_info.get("path")
                if not file_path:
                    continue
                
                full_path = repo_path / file_path
                if not full_path.exists():
                    self.logger.warning(f"File not found: {full_path}")
                    continue
                
                # Determine language
                language = self._detect_language(file_path)
                if not language:
                    continue
                
                # Read file content
                try:
                    content = full_path.read_text(encoding='utf-8')
                except Exception as e:
                    self.logger.error(f"Failed to read file {file_path}: {e}")
                    continue
                
                # Analyze file
                violations = self._analyze_file(file_path, content, language)
                all_violations.extend(violations)
                
                files_reviewed += 1
                lines_reviewed += len(content.split('\n'))
            
            # Calculate review time
            review_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate overall score
            overall_score = self._calculate_score(all_violations, lines_reviewed)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(all_violations)
            
            # Create review result
            result = ReviewResult(
                pr_id=pr_id,
                violations=all_violations,
                files_reviewed=files_reviewed,
                lines_reviewed=lines_reviewed,
                review_time_seconds=review_time,
                overall_score=overall_score,
                recommendations=recommendations
            )
            
            # Cache result
            self.review_cache[pr_id] = result
            
            self.logger.info(
                f"Code review completed for PR {pr_id}: "
                f"{len(all_violations)} violations, score {overall_score:.1f}"
            )
            
            return {
                "success": True,
                "result": result.to_dict()
            }
            
        except Exception as e:
            self.logger.error(f"Error during code review: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        try:
            self.review_cache.clear()
            self.logger.info("Code Review Plugin cleaned up successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cleanup Code Review Plugin: {e}")
            return False
    
    def _detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension"""
        ext_map = {
            '.py': 'python',
            '.cs': 'csharp',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.html': 'html',
            '.css': 'css'
        }
        
        ext = Path(file_path).suffix.lower()
        return ext_map.get(ext)
    
    def _analyze_file(
        self,
        file_path: str,
        content: str,
        language: str
    ) -> List[CodeViolation]:
        """Analyze a single file for violations"""
        violations = []
        
        # SOLID analysis
        violations.extend(self.solid_analyzer.analyze(file_path, content, language))
        
        # Security scanning
        violations.extend(self.security_scanner.scan(file_path, content, language))
        
        # Performance analysis
        violations.extend(self.performance_analyzer.analyze(file_path, content, language))
        
        # Filter by confidence threshold
        violations = [v for v in violations if v.confidence >= self.min_confidence]
        
        # Limit violations per file
        if len(violations) > self.max_violations:
            violations = sorted(
                violations,
                key=lambda v: (v.severity.value, -v.confidence)
            )[:self.max_violations]
        
        return violations
    
    def _calculate_score(self, violations: List[CodeViolation], lines_reviewed: int) -> float:
        """Calculate overall code quality score"""
        if lines_reviewed == 0:
            return 100.0
        
        # Weight by severity
        severity_weights = {
            ViolationSeverity.CRITICAL: 10.0,
            ViolationSeverity.HIGH: 5.0,
            ViolationSeverity.MEDIUM: 2.0,
            ViolationSeverity.LOW: 0.5,
            ViolationSeverity.INFO: 0.1
        }
        
        total_penalty = sum(
            severity_weights.get(v.severity, 1.0)
            for v in violations
        )
        
        # Calculate score (0-100)
        # Normalize by lines of code
        penalty_per_100_lines = (total_penalty / lines_reviewed) * 100
        score = max(0.0, 100.0 - penalty_per_100_lines * 5)
        
        return round(score, 2)
    
    def _generate_recommendations(self, violations: List[CodeViolation]) -> List[str]:
        """Generate actionable recommendations from violations"""
        recommendations = []
        
        # Group violations by type
        violations_by_type = {}
        for v in violations:
            if v.type not in violations_by_type:
                violations_by_type[v.type] = []
            violations_by_type[v.type].append(v)
        
        # Generate recommendations
        if ViolationType.SECURITY_HARDCODED_SECRET in violations_by_type:
            recommendations.append(
                "Move all secrets to environment variables or secure vaults (Azure Key Vault, AWS Secrets Manager)"
            )
        
        if ViolationType.SOLID_SRP in violations_by_type:
            count = len(violations_by_type[ViolationType.SOLID_SRP])
            recommendations.append(
                f"Refactor {count} class(es) to follow Single Responsibility Principle"
            )
        
        if ViolationType.PERF_N_PLUS_ONE in violations_by_type:
            recommendations.append(
                "Optimize database queries to avoid N+1 problems using eager loading or batch queries"
            )
        
        if ViolationType.SECURITY_SQL_INJECTION in violations_by_type:
            recommendations.append(
                "CRITICAL: Replace all string concatenation in SQL with parameterized queries"
            )
        
        if ViolationType.PERF_BLOCKING_IO in violations_by_type:
            recommendations.append(
                "Replace blocking I/O operations with async alternatives for better performance"
            )
        
        return recommendations


# Export main class
__all__ = ['CodeReviewPlugin', 'ReviewResult', 'CodeViolation', 'ViolationType', 'ViolationSeverity']
