#!/usr/bin/env python3
"""
CORTEX Production Readiness Validator

Comprehensive production readiness assessment for CORTEX deployment.
Validates all critical infrastructure components, security configurations,
and deployment capabilities.

Author: CORTEX Framework
Version: 1.0.0
"""

import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

# Configure logging  
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH" 
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class ValidationCheck:
    """Individual validation check result."""
    name: str
    passed: bool
    severity: Severity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    remediation: Optional[str] = None


@dataclass  
class ProductionReadinessReport:
    """Complete production readiness assessment."""
    overall_status: str
    readiness_score: float
    critical_issues: List[ValidationCheck]
    high_issues: List[ValidationCheck]
    medium_issues: List[ValidationCheck]
    low_issues: List[ValidationCheck]
    passed_checks: List[ValidationCheck]
    summary: Dict[str, Any]
    timestamp: str


class CORTEXProductionValidator:
    """Validates CORTEX production readiness."""
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize production validator.
        
        Args:
            workspace_root: Root of CORTEX workspace
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.checks: List[ValidationCheck] = []
        
    def run_full_assessment(self) -> ProductionReadinessReport:
        """Run complete production readiness assessment.
        
        Returns:
            ProductionReadinessReport with all findings
        """
        logger.info("🔍 Running CORTEX Production Readiness Assessment...")
        
        # Run all validation categories
        self._validate_infrastructure()
        self._validate_dependencies()
        self._validate_mcp_server()
        self._validate_docker_deployment()
        self._validate_security_configuration()
        self._validate_monitoring()
        self._validate_tests()
        
        # Analyze results
        return self._generate_report()
    
    def _validate_infrastructure(self) -> None:
        """Validate core infrastructure components."""
        logger.info("📋 Validating Infrastructure...")
        
        # Python version
        if sys.version_info >= (3, 9):
            self._add_check(
                "Python Version",
                True,
                Severity.INFO,
                f"Python {sys.version_info.major}.{sys.version_info.minor} (>= 3.9 required)"
            )
        else:
            self._add_check(
                "Python Version", 
                False,
                Severity.CRITICAL,
                f"Python {sys.version_info.major}.{sys.version_info.minor} < 3.9 required",
                remediation="Upgrade Python to 3.9+ for production deployment"
            )
        
        # Core directories
        required_dirs = [
            "cortex", "cortex_brain", "tests", "deployment"
        ]
        
        for dir_name in required_dirs:
            dir_path = self.workspace_root / dir_name
            if dir_path.exists():
                self._add_check(
                    f"Directory: {dir_name}",
                    True,
                    Severity.INFO,
                    f"Required directory exists: {dir_path}"
                )
            else:
                self._add_check(
                    f"Directory: {dir_name}",
                    False,
                    Severity.CRITICAL,
                    f"Missing required directory: {dir_path}",
                    remediation=f"Ensure {dir_name}/ directory exists with proper structure"
                )
    
    def _validate_dependencies(self) -> None:
        """Validate Python dependencies."""
        logger.info("📦 Validating Dependencies...")
        
        # Check requirements files
        req_files = [
            "requirements.txt",
            "deployment/requirements.txt"
        ]
        
        for req_file in req_files:
            req_path = self.workspace_root / req_file
            if req_path.exists():
                self._add_check(
                    f"Requirements: {req_file}",
                    True,
                    Severity.INFO,
                    f"Requirements file exists: {req_path}"
                )
            else:
                self._add_check(
                    f"Requirements: {req_file}",
                    False,
                    Severity.HIGH,
                    f"Missing requirements file: {req_path}",
                    remediation=f"Create {req_file} with required dependencies"
                )
        
        # Check critical imports
        critical_packages = [
            ("fastapi", "Web framework for MCP server"),
            ("uvicorn", "ASGI server for FastAPI"),
            ("pydantic", "Data validation"),
            ("pyyaml", "YAML configuration"),
        ]
        
        for package, description in critical_packages:
            try:
                __import__(package)
                self._add_check(
                    f"Package: {package}",
                    True,
                    Severity.INFO,
                    f"Critical package available: {package} ({description})"
                )
            except ImportError:
                self._add_check(
                    f"Package: {package}",
                    False,
                    Severity.CRITICAL,
                    f"Missing critical package: {package} ({description})",
                    remediation=f"Install package: pip install {package}"
                )
    
    def _validate_mcp_server(self) -> None:
        """Validate MCP server configuration."""
        logger.info("🔧 Validating MCP Server...")
        
        # MCP server module
        server_path = self.workspace_root / "cortex" / "mcp" / "server.py"
        if server_path.exists():
            self._add_check(
                "MCP Server Module",
                True,
                Severity.INFO,
                f"MCP server module exists: {server_path}"
            )
            
            # Try to import and validate tools
            try:
                sys.path.insert(0, str(self.workspace_root))
                from cortex.mcp.server import MCPServer
                
                server = MCPServer()
                tools = server.list_tools()
                
                # Check for core tools
                required_tools = [
                    "cortex_process_request",
                    "cortex_lens_analyze",
                    "cortex_challenge", 
                    "cortex_total_recall"
                ]
                
                available_tools = {tool['name'] for tool in tools}
                missing_tools = set(required_tools) - available_tools
                
                if not missing_tools:
                    self._add_check(
                        "MCP Core Tools",
                        True,
                        Severity.INFO,
                        f"All {len(required_tools)} core MCP tools available ({len(tools)} total)"
                    )
                else:
                    self._add_check(
                        "MCP Core Tools",
                        False,
                        Severity.CRITICAL,
                        f"Missing core MCP tools: {', '.join(missing_tools)}",
                        remediation="Ensure all core MCP tools are properly registered"
                    )
                    
            except Exception as e:
                self._add_check(
                    "MCP Server Import",
                    False,
                    Severity.CRITICAL,
                    f"Cannot import MCP server: {e}",
                    remediation="Fix MCP server import errors and dependencies"
                )
        else:
            self._add_check(
                "MCP Server Module",
                False,
                Severity.CRITICAL,
                f"MCP server module missing: {server_path}",
                remediation="Ensure cortex/mcp/server.py exists and is properly implemented"
            )
    
    def _validate_docker_deployment(self) -> None:
        """Validate Docker deployment configuration."""
        logger.info("🐳 Validating Docker Deployment...")
        
        # Docker files
        docker_files = [
            ("deployment/docker/Dockerfile", "Production container image"),
            ("deployment/docker/docker-compose.yml", "Development orchestration"),
            ("deployment/docker/docker-compose.prod.yml", "Production orchestration"),
            ("deployment/nginx.conf", "Load balancer configuration"),
            ("deployment/nginx.prod.conf", "Production load balancer"),
        ]
        
        for file_path, description in docker_files:
            full_path = self.workspace_root / file_path
            if full_path.exists():
                self._add_check(
                    f"Docker: {file_path.split('/')[-1]}",
                    True,
                    Severity.INFO,
                    f"{description}: {full_path}"
                )
            else:
                severity = Severity.HIGH if "prod" in file_path else Severity.MEDIUM
                self._add_check(
                    f"Docker: {file_path.split('/')[-1]}",
                    False,
                    severity,
                    f"Missing {description}: {full_path}",
                    remediation=f"Create {file_path} for proper deployment"
                )
    
    def _validate_security_configuration(self) -> None:
        """Validate security configurations."""
        logger.info("🔒 Validating Security Configuration...")
        
        # Security knowledge
        security_files = [
            "cortex/knowledge/best-practices/security/owasp-top-10.yaml",
            "cortex_brain/tier3/knowledge/SECURITY/owasp-top-10.yaml"
        ]
        
        security_docs_found = False
        for sec_file in security_files:
            sec_path = self.workspace_root / sec_file  
            if sec_path.exists():
                security_docs_found = True
                break
        
        if security_docs_found:
            self._add_check(
                "Security Documentation", 
                True,
                Severity.INFO,
                "OWASP Top 10 security guidelines documented"
            )
        else:
            self._add_check(
                "Security Documentation",
                False, 
                Severity.HIGH,
                "Missing OWASP security documentation",
                remediation="Ensure security best practices are documented"
            )
        
        # Environment variables (secrets management)
        if os.getenv("CORTEX_ENV"):
            self._add_check(
                "Environment Configuration",
                True,
                Severity.INFO,
                f"Environment configured: {os.getenv('CORTEX_ENV')}"
            )
        else:
            self._add_check(
                "Environment Configuration",
                False,
                Severity.MEDIUM,
                "CORTEX_ENV environment variable not set",
                remediation="Set CORTEX_ENV=production for production deployment"
            )
    
    def _validate_monitoring(self) -> None:
        """Validate monitoring and observability."""
        logger.info("📊 Validating Monitoring...")
        
        # Monitoring configuration files
        monitoring_files = [
            ("deployment/prometheus.yml", "Metrics collection"),
            ("deployment/prometheus.prod.yml", "Production metrics"),
            ("deployment/health_checks.yaml", "Health check definitions"),
        ]
        
        for file_path, description in monitoring_files:
            full_path = self.workspace_root / file_path
            if full_path.exists():
                self._add_check(
                    f"Monitoring: {file_path.split('/')[-1]}",
                    True,
                    Severity.INFO,
                    f"{description}: {full_path}"
                )
            else:
                self._add_check(
                    f"Monitoring: {file_path.split('/')[-1]}",
                    False,
                    Severity.HIGH if "prod" in file_path else Severity.MEDIUM,
                    f"Missing {description}: {full_path}",
                    remediation=f"Create {file_path} for proper monitoring"
                )
        
        # Health endpoint check
        health_modules = [
            "cortex/api/health_endpoints.py",
            "cortex/mcp/health_checker.py"
        ]
        
        health_found = any(
            (self.workspace_root / health_mod).exists()
            for health_mod in health_modules
        )
        
        if health_found:
            self._add_check(
                "Health Endpoints",
                True,
                Severity.INFO,
                "Health check endpoints implemented"
            )
        else:
            self._add_check(
                "Health Endpoints",
                False,
                Severity.HIGH,
                "Missing health check endpoints",
                remediation="Implement /health endpoints for monitoring"
            )
    
    def _validate_tests(self) -> None:
        """Validate test suite."""
        logger.info("🧪 Validating Tests...")
        
        # Test directories
        test_dirs = [
            "tests/unit",
            "tests/integration",
            "tests/mcp"
        ]
        
        test_dirs_found = 0
        for test_dir in test_dirs:
            test_path = self.workspace_root / test_dir
            if test_path.exists() and any(test_path.iterdir()):
                test_dirs_found += 1
                self._add_check(
                    f"Tests: {test_dir}",
                    True,
                    Severity.INFO,
                    f"Test directory exists with content: {test_path}"
                )
        
        if test_dirs_found >= 2:
            self._add_check(
                "Test Coverage",
                True,
                Severity.INFO,
                f"Multiple test categories found: {test_dirs_found}/3"
            )
        else:
            self._add_check(
                "Test Coverage", 
                False,
                Severity.HIGH,
                f"Insufficient test coverage: {test_dirs_found}/3 categories",
                remediation="Ensure unit, integration, and MCP tests exist"
            )
    
    def _add_check(
        self, 
        name: str, 
        passed: bool, 
        severity: Severity, 
        message: str,
        details: Optional[Dict[str, Any]] = None,
        remediation: Optional[str] = None
    ) -> None:
        """Add validation check result."""
        check = ValidationCheck(
            name=name,
            passed=passed,
            severity=severity,
            message=message,
            details=details or {},
            remediation=remediation
        )
        self.checks.append(check)
    
    def _generate_report(self) -> ProductionReadinessReport:
        """Generate comprehensive readiness report."""
        # Categorize issues
        critical_issues = [c for c in self.checks if not c.passed and c.severity == Severity.CRITICAL]
        high_issues = [c for c in self.checks if not c.passed and c.severity == Severity.HIGH]
        medium_issues = [c for c in self.checks if not c.passed and c.severity == Severity.MEDIUM]
        low_issues = [c for c in self.checks if not c.passed and c.severity == Severity.LOW]
        passed_checks = [c for c in self.checks if c.passed]
        
        # Calculate readiness score
        total_checks = len(self.checks)
        passed_count = len(passed_checks)
        critical_weight = len(critical_issues) * 0.4
        high_weight = len(high_issues) * 0.3
        medium_weight = len(medium_issues) * 0.2
        low_weight = len(low_issues) * 0.1
        
        # Score: 100% - weighted penalty
        penalty = (critical_weight + high_weight + medium_weight + low_weight)
        readiness_score = max(0, 100 - (penalty / total_checks) * 100) if total_checks > 0 else 0
        
        # Overall status
        if critical_issues:
            overall_status = "❌ NOT READY - CRITICAL ISSUES"
        elif high_issues:
            overall_status = "⚠️ NEEDS ATTENTION - HIGH PRIORITY ISSUES"
        elif medium_issues:
            overall_status = "🟡 MOSTLY READY - MEDIUM PRIORITY ISSUES"
        else:
            overall_status = "✅ PRODUCTION READY"
        
        # Summary stats
        summary = {
            "total_checks": total_checks,
            "passed_checks": passed_count,
            "failed_checks": total_checks - passed_count,
            "critical_issues": len(critical_issues),
            "high_issues": len(high_issues),
            "medium_issues": len(medium_issues),
            "low_issues": len(low_issues),
            "readiness_percentage": round(readiness_score, 1)
        }
        
        return ProductionReadinessReport(
            overall_status=overall_status,
            readiness_score=readiness_score,
            critical_issues=critical_issues,
            high_issues=high_issues,
            medium_issues=medium_issues,
            low_issues=low_issues,
            passed_checks=passed_checks,
            summary=summary,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def print_report(self, report: ProductionReadinessReport) -> None:
        """Print formatted readiness report."""
        print("━" * 80)
        print("🧠 CORTEX PRODUCTION READINESS ASSESSMENT")
        print("━" * 80)
        print(f"📊 Overall Status: {report.overall_status}")
        print(f"📈 Readiness Score: {report.readiness_score:.1f}%")
        print(f"📅 Assessment Date: {report.timestamp}")
        print()
        
        # Summary
        print("📋 SUMMARY:")
        for key, value in report.summary.items():
            formatted_key = key.replace('_', ' ').title()
            print(f"  • {formatted_key}: {value}")
        print()
        
        # Issues by severity
        if report.critical_issues:
            print("🔴 CRITICAL ISSUES (Must Fix):")
            for issue in report.critical_issues:
                print(f"  ❌ {issue.name}: {issue.message}")
                if issue.remediation:
                    print(f"     💡 Fix: {issue.remediation}")
            print()
        
        if report.high_issues:
            print("🟡 HIGH PRIORITY ISSUES:")
            for issue in report.high_issues:
                print(f"  ⚠️  {issue.name}: {issue.message}")
                if issue.remediation:
                    print(f"     💡 Fix: {issue.remediation}")
            print()
        
        if report.medium_issues:
            print("🔵 MEDIUM PRIORITY ISSUES:")
            for issue in report.medium_issues:
                print(f"  ℹ️  {issue.name}: {issue.message}")
            print()
        
        # Success summary
        print(f"✅ PASSED CHECKS ({len(report.passed_checks)}):")
        for check in report.passed_checks[:10]:  # Show first 10
            print(f"  ✅ {check.name}: {check.message}")
        
        if len(report.passed_checks) > 10:
            print(f"  ... and {len(report.passed_checks) - 10} more")
        
        print("━" * 80)


def main():
    """Main entry point."""
    print("🧠 CORTEX Production Readiness Validator")
    print("=" * 50)
    
    # Find workspace root
    workspace_root = Path.cwd()
    if not (workspace_root / "cortex" / "__init__.py").exists():
        print("❌ Not in CORTEX workspace. Run from project root.")
        sys.exit(1)
    
    # Run validation
    validator = CORTEXProductionValidator(workspace_root)
    report = validator.run_full_assessment()
    
    # Print results
    validator.print_report(report)
    
    # Export JSON report
    report_file = workspace_root / "production-readiness-report.json"
    try:
        report_data = {
            "overall_status": report.overall_status,
            "readiness_score": report.readiness_score,
            "summary": report.summary,
            "timestamp": report.timestamp,
            "critical_issues": [
                {
                    "name": issue.name,
                    "message": issue.message,
                    "remediation": issue.remediation
                }
                for issue in report.critical_issues
            ],
            "high_issues": [
                {
                    "name": issue.name,
                    "message": issue.message,
                    "remediation": issue.remediation
                }
                for issue in report.high_issues
            ]
        }
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved: {report_file}")
        
    except Exception as e:
        print(f"\n⚠️  Could not save report: {e}")
    
    # Exit with appropriate code
    if report.critical_issues:
        print("\n❌ Production deployment BLOCKED due to critical issues.")
        sys.exit(1)
    elif report.high_issues:
        print("\n⚠️  Production deployment not recommended due to high priority issues.")
        sys.exit(1) 
    else:
        print("\n✅ Production deployment ready!")
        sys.exit(0)


if __name__ == "__main__":
    main()