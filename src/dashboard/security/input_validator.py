"""
Input Validation Framework for Dashboard Security

OWASP A03 (Injection) mitigation with path traversal prevention,
file size limits, and extension validation.

Author: Asif Hussain
License: Source-Available
"""

import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation failures."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of input validation."""
    is_valid: bool
    message: str
    severity: ValidationSeverity
    sanitized_value: Optional[Any] = None
    details: Optional[Dict[str, Any]] = None


class InputValidator:
    """
    Security-focused input validation for dashboard operations.
    
    Prevents:
    - Path traversal attacks (../, ..\, absolute paths)
    - XSS via file names (<script>, HTML entities)
    - File size limit violations (>100MB default)
    - Unauthorized file extensions (.exe, .dll, etc.)
    
    Usage:
        validator = InputValidator()
        result = validator.validate_path("/safe/path/to/repo")
        if not result.is_valid:
            raise SecurityException(result.message)
    """
    
    # Allowed file extensions for analysis
    ALLOWED_EXTENSIONS = {
        '.py', '.pyw',  # Python
        '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',  # JavaScript/TypeScript
        '.cs', '.csx',  # C#
        '.java',  # Java
        '.rb',  # Ruby
        '.go',  # Go
        '.rs',  # Rust
        '.cpp', '.cc', '.cxx', '.c', '.h', '.hpp',  # C/C++
        '.php',  # PHP
        '.swift',  # Swift
        '.kt', '.kts',  # Kotlin
        '.scala',  # Scala
        '.r',  # R
        '.md', '.rst', '.txt',  # Documentation
        '.json', '.yaml', '.yml', '.toml', '.xml',  # Config
        '.html', '.htm', '.css', '.scss', '.sass',  # Web
        '.sql',  # Database
        '.sh', '.bash', '.zsh',  # Shell scripts
        '.ps1', '.psm1',  # PowerShell
    }
    
    # Dangerous file extensions (never analyze)
    FORBIDDEN_EXTENSIONS = {
        '.exe', '.dll', '.so', '.dylib',  # Binaries
        '.bat', '.cmd',  # Windows batch (XSS risk in output)
        '.vbs', '.wsf',  # Windows Script Host
        '.scr',  # Screensaver (executable)
        '.msi', '.msp',  # Windows Installer
        '.cpl',  # Control Panel extension
        '.jar', '.war',  # Java archives (could contain malicious code)
        '.zip', '.tar', '.gz', '.7z', '.rar',  # Archives (could contain path traversal)
        '.app', '.deb', '.rpm',  # Application packages
    }
    
    # Path traversal patterns (case-insensitive)
    PATH_TRAVERSAL_PATTERNS = [
        r'\.\.',  # ..
        r'\.\./',  # ../
        r'\.\.[/\\]',  # ..\ or ../
        r'[/\\]\.\.[/\\]',  # /../ or \..\
        r'%2e%2e',  # URL-encoded ..
        r'\.\.%2f',  # Mixed encoding
        r'%252e%252e',  # Double URL-encoded
    ]
    
    # XSS patterns in file paths/names
    XSS_PATTERNS = [
        r'<script',
        r'javascript:',
        r'onerror\s*=',
        r'onload\s*=',
        r'<iframe',
        r'<object',
        r'<embed',
        r'eval\(',
        r'alert\(',
    ]
    
    # Maximum file size for analysis (100MB default)
    MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024
    
    # Maximum path length (Windows: 260, Unix: 4096, use safe limit)
    MAX_PATH_LENGTH = 260
    
    def __init__(
        self,
        max_file_size: int = MAX_FILE_SIZE_BYTES,
        allowed_extensions: Optional[set] = None,
        forbidden_extensions: Optional[set] = None
    ):
        """
        Initialize input validator.
        
        Args:
            max_file_size: Maximum file size in bytes (default: 100MB)
            allowed_extensions: Override default allowed extensions
            forbidden_extensions: Override default forbidden extensions
        """
        self.max_file_size = max_file_size
        self.allowed_extensions = allowed_extensions or self.ALLOWED_EXTENSIONS
        self.forbidden_extensions = forbidden_extensions or self.FORBIDDEN_EXTENSIONS
        
        # Compile regex patterns for performance
        self._traversal_regex = re.compile(
            '|'.join(self.PATH_TRAVERSAL_PATTERNS),
            re.IGNORECASE
        )
        self._xss_regex = re.compile(
            '|'.join(self.XSS_PATTERNS),
            re.IGNORECASE
        )
    
    def validate_path(
        self,
        path: str,
        must_exist: bool = True,
        must_be_directory: bool = False,
        allowed_base_paths: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Validate file system path for security issues.
        
        Args:
            path: Path to validate
            must_exist: Require path to exist on filesystem
            must_be_directory: Require path to be a directory
            allowed_base_paths: List of allowed parent directories (chroot-style)
        
        Returns:
            ValidationResult with is_valid, message, and sanitized_value
        """
        # Null/empty check
        if not path or not isinstance(path, str):
            return ValidationResult(
                is_valid=False,
                message="Path is null or empty",
                severity=ValidationSeverity.HIGH,
                details={"input": path}
            )
        
        # Length check
        if len(path) > self.MAX_PATH_LENGTH:
            return ValidationResult(
                is_valid=False,
                message=f"Path exceeds maximum length ({self.MAX_PATH_LENGTH} chars)",
                severity=ValidationSeverity.MEDIUM,
                details={"length": len(path), "max": self.MAX_PATH_LENGTH}
            )
        
        # Path traversal check
        if self._traversal_regex.search(path):
            return ValidationResult(
                is_valid=False,
                message="Path contains traversal sequences (../, %2e%2e, etc.)",
                severity=ValidationSeverity.CRITICAL,
                details={"input": path, "attack_type": "path_traversal"}
            )
        
        # XSS pattern check
        if self._xss_regex.search(path):
            return ValidationResult(
                is_valid=False,
                message="Path contains XSS patterns (<script>, javascript:, etc.)",
                severity=ValidationSeverity.CRITICAL,
                details={"input": path, "attack_type": "xss"}
            )
        
        # Normalize path (resolve . and .., but safely)
        try:
            normalized_path = Path(path).resolve()
        except (ValueError, OSError) as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid path format: {e}",
                severity=ValidationSeverity.HIGH,
                details={"input": path, "error": str(e)}
            )
        
        # Chroot-style validation (ensure path within allowed bases)
        if allowed_base_paths:
            is_within_allowed = False
            for base in allowed_base_paths:
                try:
                    base_path = Path(base).resolve()
                    if normalized_path.is_relative_to(base_path):
                        is_within_allowed = True
                        break
                except (ValueError, AttributeError):
                    # Python 3.8 doesn't have is_relative_to, use string comparison
                    if str(normalized_path).startswith(str(Path(base).resolve())):
                        is_within_allowed = True
                        break
            
            if not is_within_allowed:
                return ValidationResult(
                    is_valid=False,
                    message="Path is outside allowed base directories",
                    severity=ValidationSeverity.CRITICAL,
                    details={
                        "input": path,
                        "normalized": str(normalized_path),
                        "allowed_bases": allowed_base_paths
                    }
                )
        
        # Existence check
        if must_exist and not normalized_path.exists():
            return ValidationResult(
                is_valid=False,
                message="Path does not exist",
                severity=ValidationSeverity.MEDIUM,
                details={"path": str(normalized_path)}
            )
        
        # Directory check
        if must_be_directory and normalized_path.exists() and not normalized_path.is_dir():
            return ValidationResult(
                is_valid=False,
                message="Path must be a directory",
                severity=ValidationSeverity.MEDIUM,
                details={"path": str(normalized_path)}
            )
        
        # Success
        return ValidationResult(
            is_valid=True,
            message="Path validation passed",
            severity=ValidationSeverity.LOW,
            sanitized_value=str(normalized_path),
            details={"normalized": str(normalized_path)}
        )
    
    def validate_file(
        self,
        file_path: str,
        check_extension: bool = True,
        check_size: bool = True
    ) -> ValidationResult:
        """
        Validate file for analysis (extension, size, existence).
        
        Args:
            file_path: Path to file
            check_extension: Validate file extension against whitelist
            check_size: Validate file size against limit
        
        Returns:
            ValidationResult with is_valid and details
        """
        # First, validate path security
        path_result = self.validate_path(file_path, must_exist=True, must_be_directory=False)
        if not path_result.is_valid:
            return path_result
        
        file = Path(path_result.sanitized_value)
        
        # Extension validation
        if check_extension:
            extension = file.suffix.lower()
            
            if extension in self.forbidden_extensions:
                return ValidationResult(
                    is_valid=False,
                    message=f"Forbidden file extension: {extension}",
                    severity=ValidationSeverity.CRITICAL,
                    details={
                        "file": str(file),
                        "extension": extension,
                        "reason": "Potentially dangerous file type"
                    }
                )
            
            if extension not in self.allowed_extensions:
                return ValidationResult(
                    is_valid=False,
                    message=f"Unsupported file extension: {extension}",
                    severity=ValidationSeverity.MEDIUM,
                    details={
                        "file": str(file),
                        "extension": extension,
                        "allowed": list(self.allowed_extensions)
                    }
                )
        
        # Size validation
        if check_size:
            try:
                file_size = file.stat().st_size
                if file_size > self.max_file_size:
                    return ValidationResult(
                        is_valid=False,
                        message=f"File exceeds size limit ({self.max_file_size} bytes)",
                        severity=ValidationSeverity.MEDIUM,
                        details={
                            "file": str(file),
                            "size": file_size,
                            "limit": self.max_file_size,
                            "size_mb": round(file_size / 1024 / 1024, 2),
                            "limit_mb": round(self.max_file_size / 1024 / 1024, 2)
                        }
                    )
            except OSError as e:
                return ValidationResult(
                    is_valid=False,
                    message=f"Cannot read file size: {e}",
                    severity=ValidationSeverity.HIGH,
                    details={"file": str(file), "error": str(e)}
                )
        
        # Success
        return ValidationResult(
            is_valid=True,
            message="File validation passed",
            severity=ValidationSeverity.LOW,
            sanitized_value=str(file),
            details={
                "file": str(file),
                "extension": file.suffix.lower(),
                "size": file.stat().st_size if file.exists() else 0
            }
        )
    
    def validate_string(
        self,
        value: str,
        max_length: int = 1000,
        allow_html: bool = False,
        pattern: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate string input for XSS and other attacks.
        
        Args:
            value: String to validate
            max_length: Maximum string length
            allow_html: Allow HTML tags (escaped)
            pattern: Optional regex pattern to match
        
        Returns:
            ValidationResult with sanitized string
        """
        # Null/empty check
        if value is None:
            return ValidationResult(
                is_valid=False,
                message="Value is null",
                severity=ValidationSeverity.HIGH
            )
        
        if not isinstance(value, str):
            return ValidationResult(
                is_valid=False,
                message=f"Value must be string, got {type(value).__name__}",
                severity=ValidationSeverity.HIGH,
                details={"type": type(value).__name__}
            )
        
        # Length check
        if len(value) > max_length:
            return ValidationResult(
                is_valid=False,
                message=f"String exceeds maximum length ({max_length} chars)",
                severity=ValidationSeverity.MEDIUM,
                details={"length": len(value), "max": max_length}
            )
        
        # XSS check (if HTML not allowed)
        if not allow_html and self._xss_regex.search(value):
            return ValidationResult(
                is_valid=False,
                message="String contains XSS patterns",
                severity=ValidationSeverity.CRITICAL,
                details={"input": value[:100], "attack_type": "xss"}
            )
        
        # Pattern validation
        if pattern:
            try:
                if not re.match(pattern, value):
                    return ValidationResult(
                        is_valid=False,
                        message=f"String does not match required pattern: {pattern}",
                        severity=ValidationSeverity.MEDIUM,
                        details={"input": value[:100], "pattern": pattern}
                    )
            except re.error as e:
                return ValidationResult(
                    is_valid=False,
                    message=f"Invalid regex pattern: {e}",
                    severity=ValidationSeverity.HIGH,
                    details={"pattern": pattern, "error": str(e)}
                )
        
        # Sanitize (escape HTML entities)
        sanitized = value
        if not allow_html:
            sanitized = (value
                        .replace('&', '&amp;')
                        .replace('<', '&lt;')
                        .replace('>', '&gt;')
                        .replace('"', '&quot;')
                        .replace("'", '&#x27;'))
        
        # Success
        return ValidationResult(
            is_valid=True,
            message="String validation passed",
            severity=ValidationSeverity.LOW,
            sanitized_value=sanitized,
            details={"original_length": len(value), "sanitized_length": len(sanitized)}
        )
    
    def validate_integer(
        self,
        value: Any,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ) -> ValidationResult:
        """
        Validate integer input with range checks.
        
        Args:
            value: Value to validate (will attempt int conversion)
            min_value: Minimum allowed value (inclusive)
            max_value: Maximum allowed value (inclusive)
        
        Returns:
            ValidationResult with validated integer
        """
        # Type conversion
        try:
            int_value = int(value)
        except (ValueError, TypeError) as e:
            return ValidationResult(
                is_valid=False,
                message=f"Cannot convert to integer: {e}",
                severity=ValidationSeverity.HIGH,
                details={"input": value, "type": type(value).__name__}
            )
        
        # Range validation
        if min_value is not None and int_value < min_value:
            return ValidationResult(
                is_valid=False,
                message=f"Value {int_value} is below minimum {min_value}",
                severity=ValidationSeverity.MEDIUM,
                details={"value": int_value, "min": min_value}
            )
        
        if max_value is not None and int_value > max_value:
            return ValidationResult(
                is_valid=False,
                message=f"Value {int_value} exceeds maximum {max_value}",
                severity=ValidationSeverity.MEDIUM,
                details={"value": int_value, "max": max_value}
            )
        
        # Success
        return ValidationResult(
            is_valid=True,
            message="Integer validation passed",
            severity=ValidationSeverity.LOW,
            sanitized_value=int_value,
            details={"value": int_value}
        )


class SecurityException(Exception):
    """Raised when security validation fails."""
    
    def __init__(self, validation_result: ValidationResult):
        self.result = validation_result
        super().__init__(validation_result.message)
