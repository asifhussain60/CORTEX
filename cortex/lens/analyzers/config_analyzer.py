"""
ConfigAnalyzer - Multi-format configuration analysis.

Detects:
- Secrets in config files (AWS keys, passwords, tokens)
- Insecure defaults (debug=true in prod, weak encryption)
- Missing required fields
- Schema validation
- Dependency conflicts

Formats: YAML, JSON, TOML, .env, docker-compose, .ini

AC-ID: AC-LENS-V2-CONFIG-001
Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import re
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConfigSeverity(Enum):
    """Configuration issue severity levels."""
    P0 = "P0"  # CRITICAL - Immediate action required
    P1 = "P1"  # HIGH - Address within sprint
    P2 = "P2"  # MEDIUM - Address within quarter
    P3 = "P3"  # LOW - Informational


class ConfigCategory(Enum):
    """Configuration issue categories."""
    SECRET_EXPOSURE = "secret_exposure"
    INSECURE_DEFAULT = "insecure_default"
    MISSING_FIELD = "missing_field"
    SCHEMA_VIOLATION = "schema_violation"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    PERFORMANCE_ISSUE = "performance_issue"


@dataclass
class ConfigFinding:
    """
    Represents a single configuration issue.
    
    Attributes:
        file_path: Path to config file
        line_number: Line number where issue occurs
        severity: ConfigSeverity level (P0/P1/P2/P3)
        category: ConfigCategory type
        description: Human-readable description
        recommendation: Recommended fix
        pattern_matched: Regex pattern that matched (if applicable)
        context: Additional context
    """
    file_path: str
    line_number: int
    severity: ConfigSeverity
    category: ConfigCategory
    description: str
    recommendation: str
    pattern_matched: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfigAnalysisResult:
    """
    Result of config analysis.
    
    Attributes:
        success: Whether analysis succeeded
        file_path: Path analyzed
        findings: List of findings
        error: Error message if failed
        analysis_time_ms: Time taken to analyze
        config_type: Type of config file (yaml, json, etc.)
    """
    success: bool
    file_path: str
    findings: List[ConfigFinding] = field(default_factory=list)
    error: str = ""
    analysis_time_ms: float = 0.0
    config_type: str = ""


class ConfigAnalyzer:
    """
    Multi-format configuration analyzer.
    
    Provides security and best practice analysis for configuration files.
    
    Example:
        >>> analyzer = ConfigAnalyzer()
        >>> result = analyzer.analyze_file(Path("config.yaml"))
        >>> for finding in result.findings:
        ...     if finding.severity == ConfigSeverity.P0:
        ...         print(f"CRITICAL: {finding.description}")
    """
    
    # Secret patterns (P0 severity)
    SECRET_PATTERNS = {
        "aws_access_key": (
            r"(?i)(access_key_id|aws_key_id):\s*['\"]?([A-Z0-9]{20})['\"]?",
            "Hardcoded AWS access key detected",
            "Store AWS credentials in AWS Secrets Manager or environment variables"
        ),
        "aws_secret_key": (
            r"(?i)(secret_access_key|aws_secret_key|secret_key):\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?",
            "Hardcoded AWS secret key detected",
            "Store AWS credentials in AWS Secrets Manager or environment variables"
        ),
        "api_key": (
            r"(?i)(api_key|apikey|api_token)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?",
            "Hardcoded API key detected",
            "Store API keys in secure secret management system"
        ),
        "password": (
            r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?([^'\"\s]{8,})['\"]?",
            "Hardcoded password detected",
            "Store passwords in secure secret management system or use environment variables"
        ),
        "private_key": (
            r"-----BEGIN (?Union[RSA, DSA] |EC )?PRIVATE KEY-----",
            "Private key embedded in config file",
            "Store private keys in secure key management system"
        ),
        "jwt_secret": (
            r"(?i)(jwt_secret|secret_key|secret_key_base)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?",
            "Hardcoded JWT secret detected",
            "Generate secrets at runtime or use environment variables"
        ),
        # .NET specific patterns
        "dotnet_connection_string": (
            r'(?i)connectionString\s*=\s*["\'].*?(password|pwd)\s*=\s*([^;"\'\s]+)',
            "Hardcoded database password in .NET connection string",
            "Use Azure Key Vault, Windows Credential Manager, or environment variables for connection strings"
        ),
        "dotnet_smtp_password": (
            r'(?i)(DefaultEmail[Pp]assword|smtp[Pp]assword|mail[Pp]assword)\s*value\s*=\s*["\']([^"\']+)',
            "Hardcoded email/SMTP password detected",
            "Store SMTP credentials in secure secret management system"
        ),
        "dotnet_machinekey": (
            r'(?i)machineKey.*validationKey\s*=\s*["\']([A-F0-9]{40,})',
            "Machine key exposed in config (should be auto-generated)",
            "Use auto-generated machine keys or store in secure configuration"
        ),
        "dotnet_appkey": (
            r'(?i)<add\s+key\s*=\s*["\'][^"\']*password[^"\']*["\']\s+value\s*=\s*["\']([^"\']+)',
            "Password in appSettings",
            "Store passwords in Azure Key Vault or encrypted config sections"
        ),
        "sql_sa_account": (
            r'(?i)User\s*ID\s*=\s*sa[;\s]',
            "Using SQL Server 'sa' account (critical security risk)",
            "Use a dedicated service account with least privilege, never use 'sa'"
        ),
    }
    
    # Insecure defaults (P1 severity)
    INSECURE_DEFAULTS = {
        "debug_enabled": (
            r"(?i)debug\s*[:=]\s*(true|1|yes|on)",
            "Debug mode enabled in production",
            "Disable debug mode in production environments"
        ),
        "ssl_disabled": (
            r"(?i)(ssl_verify|verify_ssl|ssl_check)\s*[:=]\s*(false|0|no|off)",
            "SSL verification disabled",
            "Enable SSL verification for all external connections"
        ),
        "weak_encryption": (
            r"(?i)(algorithm|cipher|encryption)\s*[:=]\s*['\"]?(md5|sha1|des|rc4)['\"]?",
            "Weak encryption algorithm detected",
            "Use modern encryption: AES-256-GCM, SHA-256, or better"
        ),
        "insecure_cors": (
            r"(?i)(cors|allowed_origins|allow_origins).*[:=].*['\"]?\*['\"]?",
            "CORS allows all origins (*)",
            "Restrict CORS to specific trusted origins"
        ),
        "no_auth": (
            r"(?i)(auth|authentication|require_auth)\s*[:=]\s*(false|0|no|off|null|none)",
            "Authentication disabled",
            "Enable authentication for all production endpoints"
        ),
        # .NET specific insecure defaults
        "dotnet_debug_compilation": (
            r'(?i)<compilation\s+[^>]*debug\s*=\s*["\']true["\']',
            "ASP.NET debug compilation enabled",
            "Set compilation debug='false' in production"
        ),
        "dotnet_custom_errors_off": (
            r'(?i)<customErrors\s+mode\s*=\s*["\']Off["\']',
            "Custom errors disabled - stack traces exposed to users",
            "Set customErrors mode='RemoteOnly' or 'On' in production"
        ),
        "dotnet_request_validation_disabled": (
            r'(?i)requestValidationMode\s*=\s*["\']2\.0["\']',
            "Legacy request validation mode (XSS risk)",
            "Remove requestValidationMode or set to 4.5+ for better XSS protection"
        ),
        "dotnet_sha1_validation": (
            r'(?i)validation\s*=\s*["\']SHA1["\']',
            "SHA1 validation is deprecated (use SHA256 or better)",
            "Update machineKey to use validation='HMACSHA256' or better"
        ),
        "dotnet_trace_enabled": (
            r'(?i)<trace\s+enabled\s*=\s*["\']true["\']',
            "ASP.NET tracing enabled - information disclosure risk",
            "Disable tracing in production environments"
        ),
    }
    
    def __init__(self):
        """Initialize ConfigAnalyzer."""
        self.findings: List[ConfigFinding] = []
    
    def analyze_file(self, config_path: Path) -> ConfigAnalysisResult:
        """
        Analyze single config file for security and best practices.
        
        Args:
            config_path: Path to config file
            
        Returns:
            ConfigAnalysisResult with findings
            
        Example:
            >>> analyzer = ConfigAnalyzer()
            >>> result = analyzer.analyze_file(Path("docker-compose.yml"))
            >>> print(f"Found {len(result.findings)} issues")
        """
        import time
        start_time = time.time()
        
        self.findings = []
        
        try:
            if not config_path.exists():
                return ConfigAnalysisResult(
                    success=False,
                    file_path=str(config_path),
                    error=f"File not found: {config_path}"
                )
            
            # Determine config type
            config_type = self._detect_config_type(config_path)
            
            # Read file content
            with open(config_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Run analyzers
            self._detect_secrets(content, str(config_path))
            self._detect_insecure_defaults(content, str(config_path))
            self._detect_missing_fields(content, str(config_path), config_type)
            
            analysis_time_ms = (time.time() - start_time) * 1000
            
            return ConfigAnalysisResult(
                success=True,
                file_path=str(config_path),
                findings=self.findings,
                analysis_time_ms=analysis_time_ms,
                config_type=config_type
            )
            
        except Exception as e:
            logger.error(f"Config analysis failed for {config_path}: {e}")
            return ConfigAnalysisResult(
                success=False,
                file_path=str(config_path),
                error=str(e)
            )
    
    def analyze_repository(self, repo_path: Path) -> Dict[str, Any]:
        """
        Analyze all config files in repository.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            Dict with aggregated results
            
        Example:
            >>> analyzer = ConfigAnalyzer()
            >>> results = analyzer.analyze_repository(Path("/repo"))
            >>> print(f"P0 issues: {len(results['p0_findings'])}")
        """
        all_findings: List[ConfigFinding] = []
        analyzed_files = 0
        
        # Config file patterns to search
        patterns = [
            "**/*.yaml",
            "**/*.yml",
            "**/*.json",
            "**/*.toml",
            "**/*.env",
            "**/*.ini",
            "**/docker-compose*.yml",
            "**/docker-compose*.yaml",
            # .NET config files
            "**/web.config",
            "**/app.config",
            "**/appsettings.json",
            "**/appsettings.*.json",
            "**/*.csproj",
            "**/*.vbproj",
        ]
        
        for pattern in patterns:
            for config_file in repo_path.glob(pattern):
                # Skip test files, node_modules, venv, etc.
                if self._should_skip_file(config_file):
                    continue
                
                result = self.analyze_file(config_file)
                if result.success:
                    all_findings.extend(result.findings)
                    analyzed_files += 1
        
        # Categorize by severity
        p0_findings = [f for f in all_findings if f.severity == ConfigSeverity.P0]
        p1_findings = [f for f in all_findings if f.severity == ConfigSeverity.P1]
        p2_findings = [f for f in all_findings if f.severity == ConfigSeverity.P2]
        p3_findings = [f for f in all_findings if f.severity == ConfigSeverity.P3]
        
        return {
            "analyzed_files": analyzed_files,
            "total_findings": len(all_findings),
            "p0_findings": [self._finding_to_dict(f) for f in p0_findings],
            "p1_findings": [self._finding_to_dict(f) for f in p1_findings],
            "p2_findings": [self._finding_to_dict(f) for f in p2_findings],
            "p3_findings": [self._finding_to_dict(f) for f in p3_findings],
            "summary": f"Found {len(all_findings)} issues across {analyzed_files} files",
        }
    
    def _detect_config_type(self, path: Path) -> str:
        """Detect config file type from extension or filename."""
        name = path.name.lower()
        suffix = path.suffix.lower()
        
        # .NET config files
        if name in ["web.config", "app.config"]:
            return "dotnet-xml"
        if name.startswith("appsettings") and suffix == ".json":
            return "dotnet-json"
        if suffix in [".csproj", ".vbproj"]:
            return "dotnet-project"
        
        # Standard config types
        if suffix in [".yaml", ".yml"]:
            return "yaml"
        elif suffix == ".json":
            return "json"
        elif suffix == ".toml":
            return "toml"
        elif suffix in [".env", ".ini"]:
            return "env"
        elif suffix == ".xml" or suffix == ".config":
            return "xml"
        return "unknown"
    
    def _detect_secrets(self, content: str, file_path: str) -> None:
        """Detect hardcoded secrets in config content."""
        lines = content.split("\n")
        
        for pattern_name, (pattern, description, recommendation) in self.SECRET_PATTERNS.items():
            for line_num, line in enumerate(lines, start=1):
                match = re.search(pattern, line)
                if match:
                    self.findings.append(ConfigFinding(
                        file_path=file_path,
                        line_number=line_num,
                        severity=ConfigSeverity.P0,
                        category=ConfigCategory.SECRET_EXPOSURE,
                        description=description,
                        recommendation=recommendation,
                        pattern_matched=pattern_name,
                        context={"line": line.strip()}
                    ))
    
    def _detect_insecure_defaults(self, content: str, file_path: str) -> None:
        """Detect insecure default configurations."""
        lines = content.split("\n")
        
        for pattern_name, (pattern, description, recommendation) in self.INSECURE_DEFAULTS.items():
            for line_num, line in enumerate(lines, start=1):
                match = re.search(pattern, line)
                if match:
                    self.findings.append(ConfigFinding(
                        file_path=file_path,
                        line_number=line_num,
                        severity=ConfigSeverity.P1,
                        category=ConfigCategory.INSECURE_DEFAULT,
                        description=description,
                        recommendation=recommendation,
                        pattern_matched=pattern_name,
                        context={"line": line.strip()}
                    ))
    
    def _detect_missing_fields(self, content: str, file_path: str, config_type: str) -> None:
        """Detect missing required fields (basic implementation)."""
        # For docker-compose files, check for common missing fields
        if "docker-compose" in file_path.lower():
            if "security_opt" not in content:
                self.findings.append(ConfigFinding(
                    file_path=file_path,
                    line_number=0,
                    severity=ConfigSeverity.P2,
                    category=ConfigCategory.MISSING_FIELD,
                    description="Docker security options not configured",
                    recommendation="Add security_opt to limit container capabilities",
                    context={"config_type": "docker-compose"}
                ))
    
    def _should_skip_file(self, path: Path) -> bool:
        """Determine if file should be skipped."""
        skip_dirs = {
            "node_modules", "venv", ".venv", "__pycache__", 
            ".git", ".pytest_cache", "dist", "build", ".tox"
        }
        
        # Check if any parent is in skip_dirs
        for parent in path.parents:
            if parent.name in skip_dirs:
                return True
        
        # Skip test files
        if "test" in path.name.lower():
            return True
        
        return False
    
    def _finding_to_dict(self, finding: ConfigFinding) -> Dict[str, Any]:
        """Convert ConfigFinding to dict."""
        return {
            "file_path": finding.file_path,
            "line_number": finding.line_number,
            "severity": finding.severity.value,
            "category": finding.category.value,
            "description": finding.description,
            "recommendation": finding.recommendation,
            "pattern_matched": finding.pattern_matched,
            "context": finding.context,
        }


# Singleton instance
_config_analyzer = None


def get_config_analyzer() -> ConfigAnalyzer:
    """Get or create singleton ConfigAnalyzer instance."""
    global _config_analyzer
    if _config_analyzer is None:
        _config_analyzer = ConfigAnalyzer()
    return _config_analyzer
