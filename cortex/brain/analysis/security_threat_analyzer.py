"""
SecurityThreatAnalyzer - AST-based CWE/threat detection for LENS (Phase 8.2).

Provides the 4th pillar of LENS intelligence:
- Language → Examination → Navigation → Synthesis → **Security Threat Analysis**

Detects dangerous patterns in Python code and maps to CWE IDs:
- CWE-94: Code Injection (eval, exec)
- CWE-95: Deserialization (pickle, marshal)
- CWE-78: Command Injection (os.system, subprocess)
- CWE-89: SQL Injection (string concatenation)
- CWE-327: Weak Cryptography (MD5, DES, weak hash)
- CWE-22: Path Traversal (unsafe file operations)

Integrates with:
- ASTAnalyzer (pattern detection from AST)
- GitHistoryAnalyzer (blame tracking for threats)
- ChallengeEngine (hard gate on CRITICAL/HIGH threats)

AC-ID: AC-SECURITY-FRAMEWORK-001
Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import ast
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)


class ThreatSeverity(Enum):
    """Threat severity levels (CVSS-inspired)."""
    CRITICAL = 5  # Requires immediate action
    HIGH = 4      # Serious risk
    MEDIUM = 3    # Moderate risk
    LOW = 2       # Low risk
    INFO = 1      # Informational
    
    def __ge__(self, other: 'ThreatSeverity') -> bool:
        """Support >= comparison between severity levels."""
        if not isinstance(other, ThreatSeverity):
            return NotImplemented
        return self.value >= other.value
    
    def __gt__(self, other: 'ThreatSeverity') -> bool:
        """Support > comparison between severity levels."""
        if not isinstance(other, ThreatSeverity):
            return NotImplemented
        return self.value > other.value
    
    def __le__(self, other: 'ThreatSeverity') -> bool:
        """Support <= comparison between severity levels."""
        if not isinstance(other, ThreatSeverity):
            return NotImplemented
        return self.value <= other.value
    
    def __lt__(self, other: 'ThreatSeverity') -> bool:
        """Support < comparison between severity levels."""
        if not isinstance(other, ThreatSeverity):
            return NotImplemented
        return self.value < other.value


@dataclass
class ThreatFinding:
    """
    Represents a single security threat found in code.
    
    Attributes:
        cwe_id: CWE identifier (e.g., "CWE-94")
        severity: ThreatSeverity level
        line_number: Line number where threat occurs
        pattern_name: Name of pattern detected (e.g., "eval_usage")
        description: Human-readable description of threat
        recommendation: Recommended remediation
        file_path: Path to file containing threat
        code_snippet: The actual code causing the threat
        context: Additional context about the threat
    """
    cwe_id: str
    severity: ThreatSeverity
    line_number: int
    pattern_name: str
    description: str
    recommendation: str
    file_path: str
    code_snippet: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityAnalysisResult:
    """
    Result of security threat analysis.
    
    Attributes:
        success: Whether analysis succeeded
        threat_findings: List of threats found
        error: Error message if analysis failed
        analysis_time_ms: Time taken to analyze
        file_path: Path analyzed
        patterns_checked: Number of patterns checked
    """
    success: bool
    threat_findings: List[ThreatFinding] = field(default_factory=list)
    error: str = ""
    analysis_time_ms: float = 0.0
    file_path: str = ""
    patterns_checked: int = 0


class SecurityThreatAnalyzer:
    """
    Analyzes Python code for security threats and CWE vulnerabilities.
    
    Combines AST inspection with regex pattern matching to detect:
    - Dangerous built-in functions (eval, exec, compile, __import__)
    - Unsafe deserialization (pickle, marshal)
    - Command injection vulnerabilities
    - SQL injection patterns
    - Weak cryptography
    - Path traversal issues
    
    Integrates into LENS analysis pipeline (Phase 8.2):
    1. GitHistoryAnalyzer → commit history
    2. ASTAnalyzer → code structure
    3. CommentExtractor → intent hints
    4. **SecurityThreatAnalyzer** → CWE threats (NEW)
    """
    
    def __init__(self) -> None:
        """Initialize SecurityThreatAnalyzer with CWE pattern library."""
        self._init_threat_patterns()
    
    def _init_threat_patterns(self) -> None:
        """Initialize threat detection patterns."""
        # CWE-94: Code Injection (eval, exec, compile)
        self._cwe94_patterns = [
            r'\beval\s*\(',
            r'\bexec\s*\(',
            r'\bcompile\s*\(',
            r'__import__\s*\(',
        ]
        
        # CWE-95: Deserialization (pickle, marshal)
        self._cwe95_patterns = [
            r'pickle\.loads\s*\(',
            r'pickle\.load\s*\(',
            r'marshal\.loads\s*\(',
            r'marshal\.load\s*\(',
            r'dill\.loads\s*\(',
        ]
        
        # CWE-78: Command Injection (os.system, subprocess with shell=True)
        self._cwe78_patterns = [
            r'os\.system\s*\(',
            r'os\.popen\s*\(',
            r'subprocess\.call.*shell\s*=\s*True',
            r'subprocess\.run.*shell\s*=\s*True',
            r'subprocess\.Popen.*shell\s*=\s*True',
        ]
        
        # CWE-89: SQL Injection (string concatenation in SQL)
        self._cwe89_patterns = [
            r'(?Union[SELECT, INSERT]|UPDATE|DELETE).*[f"\'].*{',
            r'db\.execute\s*\(\s*f["\']',
            r'cursor\.execute\s*\(\s*f["\']',
            r'connection\.execute\s*\(\s*f["\']',
        ]
        
        # CWE-327: Weak Cryptography (MD5, DES, weak hashes)
        self._cwe327_patterns = [
            r'hashlib\.md5\s*\(',
            r'hashlib\.sha1\s*\(',
            r'DES\s*\(',
            r'Blowfish\s*\(',
            r'RC4\s*\(',
        ]
        
        # CWE-22: Path Traversal (unsafe file operations)
        self._cwe22_patterns = [
            r'open\s*\(\s*f["\'].*{',
            r'open\s*\(\s*["\'].*\s*\+\s*',
            r'pathlib\.Path\s*\(\s*f["\'].*{',
        ]
    
    def analyze_code(
        self, 
        code: str, 
        file_path: str = "unknown.py"
    ) -> SecurityAnalysisResult:
        """
        Analyze Python code for security threats.
        
        Args:
            code: Python source code to analyze
            file_path: Path to the file (for reporting)
            
        Returns:
            SecurityAnalysisResult with threat findings
        """
        start_time = time.time()
        findings: List[ThreatFinding] = []
        
        try:
            if not code.strip():
                return SecurityAnalysisResult(
                    success=True,
                    file_path=file_path,
                    analysis_time_ms=0.0,
                    patterns_checked=6,
                )
            
            # Parse code into AST
            tree = ast.parse(code)
            lines = code.split('\n')
            
            # Check each threat pattern category
            findings.extend(self._check_cwe94(code, lines, file_path))
            findings.extend(self._check_cwe95(code, lines, file_path))
            findings.extend(self._check_cwe78(code, lines, file_path))
            findings.extend(self._check_cwe89(code, lines, file_path))
            findings.extend(self._check_cwe327(code, lines, file_path))
            findings.extend(self._check_cwe22(code, lines, file_path))
            
            analysis_time = (time.time() - start_time) * 1000
            
            return SecurityAnalysisResult(
                success=True,
                threat_findings=findings,
                file_path=file_path,
                analysis_time_ms=analysis_time,
                patterns_checked=6,
            )
            
        except SyntaxError as e:
            analysis_time = (time.time() - start_time) * 1000
            return SecurityAnalysisResult(
                success=False,
                error=f"Syntax error: {str(e)}",
                file_path=file_path,
                analysis_time_ms=analysis_time,
                patterns_checked=0,
            )
        except Exception as e:
            analysis_time = (time.time() - start_time) * 1000
            logger.error(f"SecurityThreatAnalyzer error in {file_path}: {str(e)}")
            return SecurityAnalysisResult(
                success=False,
                error=f"Analysis error: {str(e)}",
                file_path=file_path,
                analysis_time_ms=analysis_time,
                patterns_checked=0,
            )
    
    def _check_cwe94(
        self, 
        code: str, 
        lines: List[str], 
        file_path: str
    ) -> List[ThreatFinding]:
        """Check for CWE-94 (Code Injection) vulnerabilities."""
        findings = []
        
        for pattern in self._cwe94_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    finding = ThreatFinding(
                        cwe_id="CWE-94",
                        severity=ThreatSeverity.CRITICAL,
                        line_number=line_num,
                        pattern_name=pattern.replace('\\', ''),
                        description="Code injection vulnerability: eval/exec/compile allow execution of arbitrary code",
                        recommendation="Use ast.literal_eval() for safe parsing, avoid eval/exec entirely",
                        file_path=file_path,
                        code_snippet=line.strip(),
                        context={"function": self._extract_function_name(line_num, lines)},
                    )
                    findings.append(finding)
        
        return findings
    
    def _check_cwe95(
        self, 
        code: str, 
        lines: List[str], 
        file_path: str
    ) -> List[ThreatFinding]:
        """Check for CWE-95 (Deserialization of Untrusted Data) vulnerabilities."""
        findings = []
        
        for pattern in self._cwe95_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    finding = ThreatFinding(
                        cwe_id="CWE-95",
                        severity=ThreatSeverity.CRITICAL,
                        line_number=line_num,
                        pattern_name="unsafe_deserialization",
                        description="Unsafe deserialization: pickle/marshal can execute arbitrary code during unpickling",
                        recommendation="Use json or msgpack for untrusted data. For Python objects, use pickle with restricted unpickler",
                        file_path=file_path,
                        code_snippet=line.strip(),
                        context={"function": self._extract_function_name(line_num, lines)},
                    )
                    findings.append(finding)
        
        return findings
    
    def _check_cwe78(
        self, 
        code: str, 
        lines: List[str], 
        file_path: str
    ) -> List[ThreatFinding]:
        """Check for CWE-78 (Command Injection) vulnerabilities."""
        findings = []
        
        for pattern in self._cwe78_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    finding = ThreatFinding(
                        cwe_id="CWE-78",
                        severity=ThreatSeverity.CRITICAL,
                        line_number=line_num,
                        pattern_name="command_injection",
                        description="Command injection: os.system() and shell=True allow arbitrary command execution",
                        recommendation="Use subprocess.run(shell=False) with list arguments, or use shlex.split()",
                        file_path=file_path,
                        code_snippet=line.strip(),
                        context={"function": self._extract_function_name(line_num, lines)},
                    )
                    findings.append(finding)
        
        return findings
    
    def _check_cwe89(
        self, 
        code: str, 
        lines: List[str], 
        file_path: str
    ) -> List[ThreatFinding]:
        """Check for CWE-89 (SQL Injection) vulnerabilities."""
        findings = []
        
        for pattern in self._cwe89_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    finding = ThreatFinding(
                        cwe_id="CWE-89",
                        severity=ThreatSeverity.HIGH,
                        line_number=line_num,
                        pattern_name="sql_injection",
                        description="SQL injection: String interpolation in SQL queries can allow SQL injection attacks",
                        recommendation="Use parameterized queries with ? placeholders and pass parameters separately",
                        file_path=file_path,
                        code_snippet=line.strip(),
                        context={"function": self._extract_function_name(line_num, lines)},
                    )
                    findings.append(finding)
        
        return findings
    
    def _check_cwe327(
        self, 
        code: str, 
        lines: List[str], 
        file_path: str
    ) -> List[ThreatFinding]:
        """Check for CWE-327 (Use of a Broken or Risky Cryptographic Algorithm) vulnerabilities."""
        findings = []
        
        for pattern in self._cwe327_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    finding = ThreatFinding(
                        cwe_id="CWE-327",
                        severity=ThreatSeverity.MEDIUM,
                        line_number=line_num,
                        pattern_name="weak_crypto",
                        description="Weak cryptography: MD5, SHA1, DES, Blowfish are cryptographically broken",
                        recommendation="Use SHA-256, SHA-3, or bcrypt for hashing. Use AES-256 for encryption",
                        file_path=file_path,
                        code_snippet=line.strip(),
                        context={"function": self._extract_function_name(line_num, lines)},
                    )
                    findings.append(finding)
        
        return findings
    
    def _check_cwe22(
        self, 
        code: str, 
        lines: List[str], 
        file_path: str
    ) -> List[ThreatFinding]:
        """Check for CWE-22 (Path Traversal) vulnerabilities."""
        findings = []
        
        for pattern in self._cwe22_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    finding = ThreatFinding(
                        cwe_id="CWE-22",
                        severity=ThreatSeverity.HIGH,
                        line_number=line_num,
                        pattern_name="path_traversal",
                        description="Path traversal: Unsanitized file paths can allow access to unintended files",
                        recommendation="Validate file paths using pathlib.Path.resolve() and ensure within base directory",
                        file_path=file_path,
                        code_snippet=line.strip(),
                        context={"function": self._extract_function_name(line_num, lines)},
                    )
                    findings.append(finding)
        
        return findings
    
    def _extract_function_name(self, line_num: int, lines: List[str]) -> Optional[str]:
        """
        Extract function name from line context.
        
        Args:
            line_num: Current line number
            lines: All lines of code
            
        Returns:
            Function name if found, None otherwise
        """
        # Search backwards for function definition
        for i in range(line_num - 1, -1, -1):
            line = lines[i]
            match = re.match(r'\s*def\s+(\w+)\s*\(', line)
            if match:
                return match.group(1)
        return None


def get_security_threat_analyzer() -> SecurityThreatAnalyzer:
    """
    Factory function for SecurityThreatAnalyzer singleton.
    
    Returns:
        SecurityThreatAnalyzer instance
    """
    return SecurityThreatAnalyzer()
