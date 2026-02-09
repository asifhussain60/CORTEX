"""
Phase 48-S2: SecurityReviewEngine

CWE (Common Weakness Enumeration) detection for code security vulnerabilities.
Integrates with CORTEX LENS for holistic security analysis.

AC_START: AC-PHASE48-S2-001
Description: SecurityReviewEngine with 7 CWE patterns (89, 94, 78, 327, 22, 79, 502)
Authority: Phase 48-S2 Stage 2
"""

import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

from cortex.orchestrators.code_review.core_review_engine import (
    ReviewSeverity,
    ReviewFinding,
    FileChange,
)


class CWEType(str, Enum):
    """Common Weakness Enumeration (CWE) types detected"""
    
    CWE_89 = "CWE-89"  # SQL Injection
    CWE_94 = "CWE-94"  # Code Injection
    CWE_78 = "CWE-78"  # Command Injection
    CWE_327 = "CWE-327"  # Weak Cryptography
    CWE_22 = "CWE-22"  # Path Traversal
    CWE_79 = "CWE-79"  # XSS (Cross-Site Scripting)
    CWE_502 = "CWE-502"  # Unsafe Deserialization


@dataclass
class SecurityFinding(ReviewFinding):
    """Security-specific finding with CWE reference"""
    
    cwe_type: Optional[CWEType] = None
    owasp_category: str = ""
    cvss_score: float = 0.0
    affected_language: str = "unknown"
    
    def __post_init__(self) -> None:
        """Validate security finding fields"""
        if self.cwe_type is not None and not isinstance(self.cwe_type, CWEType):
            raise ValueError(f"Invalid CWE type: {self.cwe_type}")
        if not 0 <= self.cvss_score <= 10:
            raise ValueError(f"CVSS score must be 0-10, got {self.cvss_score}")


class SecurityReviewEngine:
    """
    Security review engine for detecting CWE vulnerabilities.
    
    Supports 7 major CWE patterns:
    - CWE-89: SQL Injection
    - CWE-94: Code Injection
    - CWE-78: Command Injection
    - CWE-327: Weak Cryptography
    - CWE-22: Path Traversal
    - CWE-79: XSS
    - CWE-502: Unsafe Deserialization
    
    Target accuracy: 95%+ with minimal false positives
    """

    def __init__(self) -> None:
        """Initialize SecurityReviewEngine"""
        self.findings: List[SecurityFinding] = []
        self._detection_patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[CWEType, List[re.Pattern]]:
        """Initialize regex patterns for CWE detection"""
        return {
            CWEType.CWE_89: [
                re.compile(r'f["\'].*\{.*\}.*(?Union[SELECT, INSERT]|UPDATE|DELETE|DROP)["\']', re.IGNORECASE | re.MULTILINE),
                re.compile(r'(?Union[SELECT, INSERT]|UPDATE|DELETE|DROP).*["\'].*\+.*["\']', re.IGNORECASE | re.MULTILINE),
                re.compile(r'\.format\(.*\).*(?Union[SELECT, INSERT]|UPDATE|DELETE|DROP)', re.IGNORECASE | re.MULTILINE),
            ],
            CWEType.CWE_78: [
                re.compile(r'os\.system\s*\(\s*f["\']', re.MULTILINE),
                re.compile(r'subprocess\.(call|run|Popen)\s*\(\s*f["\']', re.MULTILINE),
                re.compile(r'shell\s*=\s*True.*os\.(getcwd|system|popen)', re.MULTILINE),
            ],
            CWEType.CWE_327: [
                re.compile(r'hashlib\.(md5|sha1)\s*\(', re.MULTILINE),
                re.compile(r'Crypto\.Cipher\.(DES|RC4|RC2)', re.MULTILINE),
                re.compile(r'cryptography.*algorithms\.(MD5|SHA1|DES|RC4)', re.MULTILINE),
            ],
            CWEType.CWE_22: [
                re.compile(r'os\.path\.join\s*\(\s*[^,]*,\s*(?Union[request, user]|input|args)', re.MULTILINE),
                re.compile(r'open\s*\(\s*(?Union[request, user]|input|args)(?:\.get)?\s*\(', re.MULTILINE),
            ],
            CWEType.CWE_79: [
                re.compile(r'\.innerHTML\s*=\s*(?Union[request, user]|input|args)', re.MULTILINE),
                re.compile(r'\.append\s*\(\s*(?Union[request, user]|input|args)', re.MULTILINE),
                re.compile(r'document\.write\s*\(\s*(?Union[request, user]|input|args)', re.MULTILINE),
            ],
            CWEType.CWE_502: [
                re.compile(r'pickle\.loads\s*\(\s*(?Union[request, user]|input|args|untrusted)', re.MULTILINE),
                re.compile(r'json\.loads\s*\(\s*(?Union[request, user]|input|args)', re.MULTILINE),
            ],
            CWEType.CWE_94: [
                re.compile(r'eval\s*\(\s*(?Union[request, user]|input|args)', re.MULTILINE),
                re.compile(r'exec\s*\(\s*f["\']', re.MULTILINE),
                re.compile(r'compile\s*\(\s*(?Union[request, user]|input|args)', re.MULTILINE),
            ],
        }

    def analyze_diff(
        self,
        changes: List[FileChange],
        code_content: Dict[str, str],
    ) -> List[ReviewFinding]:
        """
        Analyze file changes for security vulnerabilities.
        
        Args:
            changes: List of file changes from diff parser
            code_content: Dictionary mapping filepath to full content
            
        Returns:
            List of security findings with severity and fix suggestions
        """
        findings = []

        for change in changes:
            content = code_content.get(change.filepath, "")
            
            # Detect language from file extension
            language = self._detect_language(change.filepath)
            
            # Run all CWE detections
            findings.extend(self._check_cwe_89(change, content, language))
            findings.extend(self._check_cwe_78(change, content, language))
            findings.extend(self._check_cwe_327(change, content, language))
            findings.extend(self._check_cwe_22(change, content, language))
            findings.extend(self._check_cwe_79(change, content, language))
            findings.extend(self._check_cwe_502(change, content, language))
            findings.extend(self._check_cwe_94(change, content, language))
        
        return findings

    def _detect_language(self, filepath: str) -> str:
        """Detect programming language from file extension"""
        extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.sql': 'SQL',
            '.php': 'PHP',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
        }
        
        for ext, lang in extensions.items():
            if filepath.endswith(ext):
                return lang
        
        return 'unknown'

    def _check_cwe_89(self, change: FileChange, content: str, language: str) -> List[SecurityFinding]:
        """Detect CWE-89: SQL Injection"""
        findings = []
        
        # Skip if it's a parameterized query pattern
        if self._is_parameterized_query(content):
            return findings
        
        for pattern in self._detection_patterns[CWEType.CWE_89]:
            matches = pattern.finditer(content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                
                # Verify it's actually in the changed lines
                if not self._line_in_change(line_num, change):
                    continue
                
                findings.append(
                    ReviewFinding(
                        file=change.filepath,
                        line=line_num,
                        severity=ReviewSeverity.P0_CRITICAL,
                        title="CWE-89: SQL Injection Vulnerability",
                        description=f"SQL injection detected in {language} code. "
                                   f"User input is directly concatenated into SQL query. "
                                   f"Use parameterized queries or prepared statements.",
                        fix_suggestion="Use parameterized queries: query = 'SELECT * FROM users WHERE id = ?' "
                                      "and pass values separately: db.execute(query, (user_id,))",
                    )
                )
        
        return findings

    def _check_cwe_78(self, change: FileChange, content: str, language: str) -> List[SecurityFinding]:
        """Detect CWE-78: Command Injection"""
        findings = []
        
        for pattern in self._detection_patterns[CWEType.CWE_78]:
            matches = pattern.finditer(content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                
                if not self._line_in_change(line_num, change):
                    continue
                
                findings.append(
                    ReviewFinding(
                        file=change.filepath,
                        line=line_num,
                        severity=ReviewSeverity.P0_CRITICAL,
                        title="CWE-78: Command Injection Vulnerability",
                        description=f"Command injection detected. "
                                   f"User input is used in shell commands. "
                                   f"This allows arbitrary command execution.",
                        fix_suggestion="Use subprocess.run with list arguments and shell=False: "
                                      "subprocess.run(['ping', hostname], shell=False)",
                    )
                )
        
        return findings

    def _check_cwe_327(self, change: FileChange, content: str, language: str) -> List[SecurityFinding]:
        """Detect CWE-327: Weak Cryptography"""
        findings = []
        
        for pattern in self._detection_patterns[CWEType.CWE_327]:
            matches = pattern.finditer(content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                
                if not self._line_in_change(line_num, change):
                    continue
                
                weak_algo = match.group()
                findings.append(
                    ReviewFinding(
                        file=change.filepath,
                        line=line_num,
                        severity=ReviewSeverity.P1_HIGH,
                        title="CWE-327: Use of Weak Cryptographic Algorithm",
                        description=f"Weak cryptography algorithm detected: {weak_algo}. "
                                   f"MD5, SHA1, DES, and RC4 are cryptographically broken.",
                        fix_suggestion="Use strong algorithms: hashlib.sha256() or "
                                      "cryptography.hazmat.primitives.hashes.SHA256()",
                    )
                )
        
        return findings

    def _check_cwe_22(self, change: FileChange, content: str, language: str) -> List[SecurityFinding]:
        """Detect CWE-22: Path Traversal"""
        findings = []
        
        for pattern in self._detection_patterns[CWEType.CWE_22]:
            matches = pattern.finditer(content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                
                if not self._line_in_change(line_num, change):
                    continue
                
                findings.append(
                    ReviewFinding(
                        file=change.filepath,
                        line=line_num,
                        severity=ReviewSeverity.P0_CRITICAL,
                        title="CWE-22: Path Traversal Vulnerability",
                        description=f"Path traversal vulnerability detected. "
                                   f"User input is used to construct file paths. "
                                   f"This allows reading arbitrary files (e.g., '../../../etc/passwd').",
                        fix_suggestion="Validate and sanitize path input: "
                                      "safe_path = os.path.normpath(os.path.join(base_dir, user_path)); "
                                      "assert safe_path.startswith(base_dir)",
                    )
                )
        
        return findings

    def _check_cwe_79(self, change: FileChange, content: str, language: str) -> List[SecurityFinding]:
        """Detect CWE-79: Cross-Site Scripting (XSS)"""
        findings = []
        
        for pattern in self._detection_patterns[CWEType.CWE_79]:
            matches = pattern.finditer(content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                
                if not self._line_in_change(line_num, change):
                    continue
                
                findings.append(
                    ReviewFinding(
                        file=change.filepath,
                        line=line_num,
                        severity=ReviewSeverity.P0_CRITICAL,
                        title="CWE-79: Cross-Site Scripting (XSS) Vulnerability",
                        description=f"XSS vulnerability detected in {language}. "
                                   f"User input is directly injected into DOM without escaping. "
                                   f"This allows script injection and session hijacking.",
                        fix_suggestion="Use textContent instead of innerHTML, or sanitize input: "
                                      "element.textContent = userInput; "
                                      "or use DOMPurify.sanitize(userInput) for innerHTML",
                    )
                )
        
        return findings

    def _check_cwe_502(self, change: FileChange, content: str, language: str) -> List[SecurityFinding]:
        """Detect CWE-502: Unsafe Deserialization"""
        findings = []
        
        for pattern in self._detection_patterns[CWEType.CWE_502]:
            matches = pattern.finditer(content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                
                if not self._line_in_change(line_num, change):
                    continue
                
                findings.append(
                    ReviewFinding(
                        file=change.filepath,
                        line=line_num,
                        severity=ReviewSeverity.P0_CRITICAL,
                        title="CWE-502: Deserialization of Untrusted Data",
                        description=f"Unsafe deserialization detected. "
                                   f"Deserializing untrusted data can lead to RCE (Remote Code Execution). "
                                   f"pickle.loads() and similar functions can execute arbitrary code.",
                        fix_suggestion="Use safe alternatives: json.loads() for trusted JSON data, "
                                      "or use pickle.loads(data, restricted=True) with restrictions",
                    )
                )
        
        return findings

    def _check_cwe_94(self, change: FileChange, content: str, language: str) -> List[SecurityFinding]:
        """Detect CWE-94: Improper Control of Generation of Code"""
        findings = []
        
        for pattern in self._detection_patterns[CWEType.CWE_94]:
            matches = pattern.finditer(content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                
                if not self._line_in_change(line_num, change):
                    continue
                
                findings.append(
                    ReviewFinding(
                        file=change.filepath,
                        line=line_num,
                        severity=ReviewSeverity.P0_CRITICAL,
                        title="CWE-94: Code Injection Vulnerability",
                        description=f"Code injection vulnerability detected. "
                                   f"eval(), exec(), or compile() with user input "
                                   f"allows arbitrary code execution.",
                        fix_suggestion="Never use eval/exec with user input. "
                                      "Use json.loads() or ast.literal_eval() for safe data parsing",
                    )
                )
        
        return findings

    def _is_parameterized_query(self, content: str) -> bool:
        """Check if code uses parameterized queries (to reduce false positives)"""
        parameterized_patterns = [
            r'\?',  # ? placeholder
            r'%s',  # %s placeholder
            r'\$\d+',  # $1, $2 placeholders
            r':\w+',  # :name placeholders
            r'db\.execute\s*\([^,]*,\s*\[',  # positional args in list
        ]
        
        for pattern_str in parameterized_patterns:
            if re.search(pattern_str, content):
                return True
        
        return False

    def _line_in_change(self, line_num: int, change: FileChange) -> bool:
        """Check if line number is in the changed lines"""
        if not change.line_diffs:
            return True
        
        changed_lines = {d.get('line', 0) for d in change.line_diffs}
        return line_num in changed_lines or len(changed_lines) == 0


# AC_COMPLETE: AC-PHASE48-S2-001 (SecurityReviewEngine implemented)
# Features: 7 CWE patterns, pattern registry, language detection, finding generation
# Status: Ready for test execution and MCP integration
