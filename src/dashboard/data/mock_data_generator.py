"""
Mock Data Generator

Generates realistic mock data for dashboard development and testing.

This generator wraps existing collectors' data structures, producing mock data
that matches the exact schema expected by dashboard visualizations without
requiring actual codebase scanning.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum


class HealthScenario(Enum):
    """Health scenario variants for mock data generation."""
    HEALTHY = "healthy"      # 90/100 health score
    WARNING = "warning"      # 60/100 health score
    CRITICAL = "critical"    # 30/100 health score


class MockDataGenerator:
    """
    Generates realistic mock data matching existing collector schemas.
    
    This class produces data structures identical to what real collectors return,
    enabling safe UI/UX iteration without scanning actual codebases.
    
    Data is based on patterns observed in:
    - CORTEX (Clean Architecture, Python/JavaScript, 994 files)
    - NOOR CANVAS (React frontend, .NET backend)
    - ALIST (Multi-language, microservices)
    - KSESSIONS (Session management, API-heavy)
    """
    
    def __init__(self, scenario: HealthScenario = HealthScenario.HEALTHY):
        """
        Initialize mock data generator.
        
        Args:
            scenario: Health scenario variant (HEALTHY, WARNING, CRITICAL)
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.scenario = scenario
        self.logger.info(f"MockDataGenerator initialized with scenario: {scenario.value}")
    
    def generate_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate all mock data files at once.
        
        Returns:
            Dict with keys: health_data, tech_stack, security, architecture,
                           code_organization, team_metrics, vendors
        """
        self.logger.info("Generating all mock data...")
        
        return {
            "health_data": self.generate_mock_health_data(),
            "tech_stack": self.generate_mock_tech_stack(),
            "security": self.generate_mock_security(),
            "architecture": self.generate_mock_architecture(),
            "code_organization": self.generate_mock_code_org(),
            "team_metrics": self.generate_mock_team_metrics(),
            "vendors": self.generate_mock_vendors()
        }
    
    def generate_mock_health_data(self) -> Dict[str, Any]:
        """
        Generate overall health data (overview tab).
        
        Schema matches: General dashboard overview metrics
        
        Returns:
            Dict with overall_health_score, status, key metrics
        """
        if self.scenario == HealthScenario.HEALTHY:
            health_score = 92
            status = "healthy"
            critical_issues = 0
            warnings = 3
        elif self.scenario == HealthScenario.WARNING:
            health_score = 65
            status = "warning"
            critical_issues = 2
            warnings = 12
        else:  # CRITICAL
            health_score = 35
            status = "critical"
            critical_issues = 8
            warnings = 24
        
        return {
            "overall_health_score": health_score,
            "status": status,
            "last_scan": datetime.now().isoformat(),
            "summary": {
                "total_files": 994,
                "total_loc": 45678,
                "test_coverage": 78.5 if self.scenario == HealthScenario.HEALTHY else 45.2,
                "critical_issues": critical_issues,
                "warnings": warnings,
                "maintainability_index": 85 if self.scenario == HealthScenario.HEALTHY else 58
            },
            "metrics": {
                "code_quality_score": 88 if self.scenario == HealthScenario.HEALTHY else 62,
                "security_score": 96 if self.scenario == HealthScenario.HEALTHY else 54,
                "test_score": 82 if self.scenario == HealthScenario.HEALTHY else 48,
                "documentation_score": 75
            },
            "trends": {
                "health_trend": "improving" if self.scenario == HealthScenario.HEALTHY else "declining",
                "velocity_trend": "stable",
                "quality_trend": "improving" if self.scenario == HealthScenario.HEALTHY else "declining"
            }
        }
    
    def generate_mock_tech_stack(self) -> Dict[str, Any]:
        """
        Generate technology stack data.
        
        Schema matches: TechStackCollector output
        
        Returns:
            Dict with frontend, backend, database, devops, summary
        """
        frontend_techs = [
            {
                "name": "React",
                "version": "18.2.0",
                "latest": "18.2.0",
                "status": "current",
                "category": "framework",
                "cve_count": 0,
                "eol_date": None
            },
            {
                "name": "TypeScript",
                "version": "5.2.2",
                "latest": "5.3.3",
                "status": "outdated",
                "category": "language",
                "cve_count": 0,
                "eol_date": None
            },
            {
                "name": "Vite",
                "version": "4.5.0",
                "latest": "5.0.0",
                "status": "outdated",
                "category": "build_tool",
                "cve_count": 0,
                "eol_date": None
            }
        ]
        
        backend_techs = [
            {
                "name": "Python",
                "version": "3.11.5",
                "latest": "3.12.0",
                "status": "current",
                "category": "language",
                "cve_count": 0,
                "eol_date": None
            },
            {
                "name": "FastAPI",
                "version": "0.104.1",
                "latest": "0.109.0",
                "status": "outdated",
                "category": "framework",
                "cve_count": 0,
                "eol_date": None
            },
            {
                "name": ".NET",
                "version": "8.0",
                "latest": "8.0",
                "status": "current",
                "category": "framework",
                "cve_count": 0,
                "eol_date": None
            }
        ]
        
        database_techs = [
            {
                "name": "SQLite",
                "version": "3.43.0",
                "latest": "3.44.0",
                "status": "current",
                "category": "database",
                "cve_count": 0,
                "eol_date": None
            },
            {
                "name": "PostgreSQL",
                "version": "15.4",
                "latest": "16.1",
                "status": "outdated",
                "category": "database",
                "cve_count": 0,
                "eol_date": None
            },
            {
                "name": "Redis",
                "version": "7.2.0",
                "latest": "7.2.3",
                "status": "current",
                "category": "cache",
                "cve_count": 0,
                "eol_date": None
            }
        ]
        
        devops_techs = [
            {
                "name": "Docker",
                "version": "24.0.6",
                "latest": "24.0.7",
                "status": "current",
                "category": "container",
                "cve_count": 0,
                "eol_date": None
            },
            {
                "name": "pytest",
                "version": "7.4.3",
                "latest": "7.4.4",
                "status": "current",
                "category": "testing",
                "cve_count": 0,
                "eol_date": None
            },
            {
                "name": "GitHub Actions",
                "version": "latest",
                "latest": "latest",
                "status": "current",
                "category": "ci_cd",
                "cve_count": 0,
                "eol_date": None
            }
        ]
        
        all_techs = frontend_techs + backend_techs + database_techs + devops_techs
        
        return {
            "frontend": frontend_techs,
            "backend": backend_techs,
            "database": database_techs,
            "devops": devops_techs,
            "summary": {
                "total_technologies": len(all_techs),
                "current_count": len([t for t in all_techs if t["status"] == "current"]),
                "outdated_count": len([t for t in all_techs if t["status"] == "outdated"]),
                "deprecated_count": len([t for t in all_techs if t["status"] == "deprecated"]),
                "last_scan": datetime.now().isoformat()
            }
        }
    
    def generate_mock_security(self) -> Dict[str, Any]:
        """
        Generate security scorecard data.
        
        Schema matches: SecurityCollector output
        
        Returns:
            Dict with overall_score, vulnerabilities, owasp_compliance, compliance
        """
        if self.scenario == HealthScenario.HEALTHY:
            overall_score = 96
            critical_vulns = 0
            high_vulns = 0
            medium_vulns = 2
            low_vulns = 5
            owasp_pass = 9
            owasp_warn = 1
            owasp_fail = 0
        elif self.scenario == HealthScenario.WARNING:
            overall_score = 72
            critical_vulns = 1
            high_vulns = 3
            medium_vulns = 8
            low_vulns = 12
            owasp_pass = 6
            owasp_warn = 3
            owasp_fail = 1
        else:  # CRITICAL
            overall_score = 42
            critical_vulns = 5
            high_vulns = 12
            medium_vulns = 18
            low_vulns = 24
            owasp_pass = 3
            owasp_warn = 4
            owasp_fail = 3
        
        return {
            "overall_score": overall_score,
            "last_scan": datetime.now().isoformat(),
            "vulnerabilities": {
                "total": critical_vulns + high_vulns + medium_vulns + low_vulns,
                "critical": critical_vulns,
                "high": high_vulns,
                "medium": medium_vulns,
                "low": low_vulns,
                "by_package": [
                    {"package": "lodash", "version": "4.17.19", "severity": "medium", "cve": "CVE-2020-8203"}
                ] if medium_vulns > 0 else []
            },
            "owasp_top_10": {
                "pass_count": owasp_pass,
                "warn_count": owasp_warn,
                "fail_count": owasp_fail,
                "categories": [
                    {"id": "A01", "name": "Broken Access Control", "status": "pass", "score": 95},
                    {"id": "A02", "name": "Cryptographic Failures", "status": "pass", "score": 92},
                    {"id": "A03", "name": "Injection", "status": "pass", "score": 98},
                    {"id": "A04", "name": "Insecure Design", "status": "pass", "score": 88},
                    {"id": "A05", "name": "Security Misconfiguration", "status": "warn" if owasp_warn > 0 else "pass", "score": 78},
                    {"id": "A06", "name": "Vulnerable Components", "status": "pass", "score": 90},
                    {"id": "A07", "name": "Authentication Failures", "status": "pass", "score": 94},
                    {"id": "A08", "name": "Data Integrity Failures", "status": "pass", "score": 96},
                    {"id": "A09", "name": "Logging Failures", "status": "pass", "score": 85},
                    {"id": "A10", "name": "SSRF", "status": "pass", "score": 100}
                ]
            },
            "compliance": {
                "gdpr_ready": overall_score >= 85,
                "soc2_ready": overall_score >= 90,
                "hipaa_ready": False,
                "pci_dss_ready": False
            },
            "summary": {
                "total_issues": critical_vulns + high_vulns + medium_vulns + low_vulns,
                "high_priority": critical_vulns + high_vulns,
                "hardcoded_secrets": 0 if self.scenario == HealthScenario.HEALTHY else 2,
                "weak_crypto": 0 if self.scenario == HealthScenario.HEALTHY else 1
            }
        }
    
    def generate_mock_architecture(self) -> Dict[str, Any]:
        """
        Generate architecture analysis data.
        
        Schema matches: ArchitectureCollector output
        
        Returns:
            Dict with style, tiers, components, database_schema, score
        """
        return {
            "style": "clean_architecture",
            "score": 100 if self.scenario == HealthScenario.HEALTHY else 75,
            "last_scan": datetime.now().isoformat(),
            "tiers": [
                {
                    "name": "presentation",
                    "component_count": 12,
                    "loc": 8450,
                    "description": "UI components, views, and user interaction"
                },
                {
                    "name": "application",
                    "component_count": 28,
                    "loc": 15230,
                    "description": "Business logic, use cases, orchestration"
                },
                {
                    "name": "domain",
                    "component_count": 8,
                    "loc": 4560,
                    "description": "Core entities, domain models, business rules"
                },
                {
                    "name": "infrastructure",
                    "component_count": 7,
                    "loc": 5890,
                    "description": "Data access, external services, persistence"
                }
            ],
            "components": [
                {
                    "name": "UserFeature",
                    "tier": "application",
                    "loc": 1250,
                    "complexity": 42,
                    "dependencies": ["UserRepository", "ValidationService", "EmailService"]
                },
                {
                    "name": "AuthenticationService",
                    "tier": "application",
                    "loc": 890,
                    "complexity": 38,
                    "dependencies": ["TokenService", "UserRepository", "PasswordHasher"]
                },
                {
                    "name": "UserRepository",
                    "tier": "infrastructure",
                    "loc": 645,
                    "complexity": 28,
                    "dependencies": ["DatabaseContext", "User"]
                },
                {
                    "name": "User",
                    "tier": "domain",
                    "loc": 320,
                    "complexity": 12,
                    "dependencies": []
                },
                {
                    "name": "ValidationService",
                    "tier": "application",
                    "loc": 450,
                    "complexity": 22,
                    "dependencies": ["ValidationRules"]
                }
            ],
            "database_schema": {
                "tables": [
                    {
                        "name": "users",
                        "columns": 12,
                        "relationships": [
                            {"table": "sessions", "type": "one_to_many"},
                            {"table": "user_roles", "type": "one_to_many"}
                        ]
                    },
                    {
                        "name": "sessions",
                        "columns": 8,
                        "relationships": [
                            {"table": "users", "type": "many_to_one"}
                        ]
                    },
                    {
                        "name": "user_roles",
                        "columns": 5,
                        "relationships": [
                            {"table": "users", "type": "many_to_one"},
                            {"table": "roles", "type": "many_to_one"}
                        ]
                    },
                    {
                        "name": "roles",
                        "columns": 6,
                        "relationships": [
                            {"table": "user_roles", "type": "one_to_many"}
                        ]
                    }
                ],
                "total_tables": 8,
                "total_relationships": 12
            },
            "summary": {
                "total_components": 55,
                "total_loc": 34130,
                "average_complexity": 27.3,
                "tier_count": 4,
                "high_coupling_components": 3 if self.scenario != HealthScenario.HEALTHY else 0
            }
        }
    
    def generate_mock_code_org(self) -> Dict[str, Any]:
        """
        Generate code organization/complexity data.
        
        Schema matches: CodeOrganizationCollector output
        
        Returns:
            Dict with heatmap, hotspots, complexity_distribution, summary
        """
        hotspots = [
            {
                "file": "src/entry_point/cortex_entry.py",
                "loc": 825,
                "complexity": 91,
                "change_frequency": 18,
                "risk_score": 100,
                "recommendation": "Split into multiple focused modules"
            },
            {
                "file": "src/entry_point/response_formatter.py",
                "loc": 625,
                "complexity": 163,
                "change_frequency": 15,
                "risk_score": 98,
                "recommendation": "Extract formatting strategies into separate classes"
            },
            {
                "file": "src/plugins/cleanup_plugin.py",
                "loc": 901,
                "complexity": 181,
                "change_frequency": 12,
                "risk_score": 95,
                "recommendation": "Refactor into cleanup orchestrator with smaller handlers"
            }
        ]
        
        if self.scenario != HealthScenario.HEALTHY:
            hotspots.extend([
                {
                    "file": "src/core/legacy_processor.py",
                    "loc": 1450,
                    "complexity": 245,
                    "change_frequency": 28,
                    "risk_score": 100,
                    "recommendation": "Critical refactoring required - legacy code"
                },
                {
                    "file": "src/utils/data_transformer.py",
                    "loc": 980,
                    "complexity": 198,
                    "change_frequency": 22,
                    "risk_score": 92,
                    "recommendation": "Break into smaller transformation utilities"
                }
            ])
        
        return {
            "heatmap": [
                {
                    "directory": "src/entry_point/",
                    "file_count": 8,
                    "total_loc": 3450,
                    "avg_complexity": 68,
                    "max_complexity": 163,
                    "files": [
                        {"name": "cortex_entry.py", "loc": 825, "complexity": 91},
                        {"name": "response_formatter.py", "loc": 625, "complexity": 163},
                        {"name": "intent_classifier.py", "loc": 445, "complexity": 42}
                    ]
                },
                {
                    "directory": "src/plugins/",
                    "file_count": 15,
                    "total_loc": 8920,
                    "avg_complexity": 48,
                    "max_complexity": 181,
                    "files": [
                        {"name": "cleanup_plugin.py", "loc": 901, "complexity": 181},
                        {"name": "validation_plugin.py", "loc": 567, "complexity": 54}
                    ]
                },
                {
                    "directory": "src/tier1/",
                    "file_count": 12,
                    "total_loc": 5680,
                    "avg_complexity": 28,
                    "max_complexity": 72,
                    "files": []
                }
            ],
            "hotspots": hotspots,
            "complexity_distribution": {
                "low": 526,       # Complexity 1-10
                "medium": 350,    # Complexity 11-20
                "high": 100,      # Complexity 21-50
                "very_high": 18   # Complexity 51+
            },
            "summary": {
                "total_files": 994,
                "total_loc": 45678,
                "avg_complexity": 27.3 if self.scenario == HealthScenario.HEALTHY else 42.8,
                "max_complexity": 181,
                "hotspots_count": len(hotspots),
                "high_complexity_files": 118 if self.scenario == HealthScenario.HEALTHY else 245,
                "last_scan": datetime.now().isoformat()
            }
        }
    
    def generate_mock_team_metrics(self) -> Dict[str, Any]:
        """
        Generate team productivity/contribution data.
        
        Schema matches: TeamMetricsCollector output
        
        Returns:
            Dict with contributors, velocity, commit_trends, summary
        """
        return {
            "contributors": [
                {
                    "name": "Asif Hussain",
                    "email": "asif@example.com",
                    "commits": 856,
                    "lines_added": 125430,
                    "lines_deleted": 45230,
                    "active_days": 145,
                    "first_commit": (datetime.now() - timedelta(days=180)).isoformat(),
                    "last_commit": datetime.now().isoformat()
                },
                {
                    "name": "Developer 2",
                    "email": "dev2@example.com",
                    "commits": 234,
                    "lines_added": 34560,
                    "lines_deleted": 12340,
                    "active_days": 98,
                    "first_commit": (datetime.now() - timedelta(days=120)).isoformat(),
                    "last_commit": (datetime.now() - timedelta(days=2)).isoformat()
                },
                {
                    "name": "Developer 3",
                    "email": "dev3@example.com",
                    "commits": 98,
                    "lines_added": 15670,
                    "lines_deleted": 5430,
                    "active_days": 45,
                    "first_commit": (datetime.now() - timedelta(days=60)).isoformat(),
                    "last_commit": (datetime.now() - timedelta(days=5)).isoformat()
                },
                {
                    "name": "Developer 4",
                    "email": "dev4@example.com",
                    "commits": 48,
                    "lines_added": 8920,
                    "lines_deleted": 2340,
                    "active_days": 28,
                    "first_commit": (datetime.now() - timedelta(days=45)).isoformat(),
                    "last_commit": (datetime.now() - timedelta(days=8)).isoformat()
                }
            ],
            "velocity": {
                "commits_per_week": [
                    {"week": "2025-W48", "commits": 42},
                    {"week": "2025-W47", "commits": 38},
                    {"week": "2025-W46", "commits": 45},
                    {"week": "2025-W45", "commits": 51},
                    {"week": "2025-W44", "commits": 39}
                ],
                "trend": "stable",
                "avg_commits_per_week": 43
            },
            "commit_trends": {
                "by_hour": {
                    "09": 45, "10": 78, "11": 92, "12": 34,
                    "13": 28, "14": 67, "15": 89, "16": 72,
                    "17": 45, "18": 23, "19": 12, "20": 8
                },
                "by_day": {
                    "Monday": 234,
                    "Tuesday": 267,
                    "Wednesday": 289,
                    "Thursday": 245,
                    "Friday": 201,
                    "Saturday": 0,
                    "Sunday": 0
                }
            },
            "summary": {
                "total_contributors": 4,
                "total_commits": 1236,
                "active_contributors": 4,
                "bus_factor": 1,  # Only 1 person with majority of commits
                "avg_commits_per_contributor": 309,
                "avg_commits_per_week": 43,
                "last_scan": datetime.now().isoformat()
            }
        }
    
    def generate_mock_vendors(self) -> Dict[str, Any]:
        """
        Generate external vendor/service detection data.
        
        Schema matches: VendorDetector output
        
        Returns:
            Dict with vendors, by_category, by_status, summary
        """
        vendors = [
            {
                "name": "Stripe",
                "category": "payment",
                "status": "active",
                "cost_tier": "$$$",
                "detection_method": "sdk_import",
                "files_using": ["src/payments/stripe_client.py", "src/api/checkout.py"],
                "env_vars": ["STRIPE_API_KEY", "STRIPE_WEBHOOK_SECRET"],
                "compliance": ["PCI_DSS", "GDPR"],
                "security_notes": "API keys properly stored in env vars"
            },
            {
                "name": "Auth0",
                "category": "authentication",
                "status": "active",
                "cost_tier": "$$",
                "detection_method": "sdk_import",
                "files_using": ["src/auth/auth0_client.py", "src/middleware/auth.py"],
                "env_vars": ["AUTH0_DOMAIN", "AUTH0_CLIENT_ID", "AUTH0_CLIENT_SECRET"],
                "compliance": ["SOC2", "GDPR"],
                "security_notes": "OAuth flow properly implemented"
            },
            {
                "name": "AWS S3",
                "category": "storage",
                "status": "active",
                "cost_tier": "$$",
                "detection_method": "sdk_import",
                "files_using": ["src/storage/s3_client.py", "src/services/file_upload.py"],
                "env_vars": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_BUCKET_NAME"],
                "compliance": ["SOC2", "HIPAA"],
                "security_notes": "IAM roles recommended over access keys"
            },
            {
                "name": "SendGrid",
                "category": "email",
                "status": "configured",
                "cost_tier": "$",
                "detection_method": "env_var",
                "files_using": ["src/services/email_service.py"],
                "env_vars": ["SENDGRID_API_KEY"],
                "compliance": ["GDPR"],
                "security_notes": "API key found, service configured"
            },
            {
                "name": "Sentry",
                "category": "monitoring",
                "status": "active",
                "cost_tier": "$",
                "detection_method": "sdk_import",
                "files_using": ["src/main.py", "src/middleware/error_handler.py"],
                "env_vars": ["SENTRY_DSN"],
                "compliance": ["SOC2"],
                "security_notes": "Error tracking properly configured"
            }
        ]
        
        return {
            "vendors": vendors,
            "by_category": {
                "payment": 1,
                "authentication": 1,
                "storage": 1,
                "email": 1,
                "monitoring": 1,
                "analytics": 0,
                "messaging": 0,
                "cdn": 0
            },
            "by_status": {
                "active": 4,
                "configured": 1,
                "inactive": 0,
                "expired": 0
            },
            "summary": {
                "total_vendors": len(vendors),
                "active_vendors": 4,
                "cost_estimate": "$$$",
                "compliance_flags": ["PCI_DSS", "GDPR", "SOC2", "HIPAA"],
                "security_warnings": 1,  # AWS access keys warning
                "last_scan": datetime.now().isoformat()
            }
        }


# Helper function for script usage
def generate_mock_data(scenario: str = "healthy") -> Dict[str, Dict[str, Any]]:
    """
    Generate all mock data files for specified scenario.
    
    Args:
        scenario: "healthy", "warning", or "critical"
        
    Returns:
        Dict containing all generated mock data
    """
    scenario_enum = HealthScenario(scenario.lower())
    generator = MockDataGenerator(scenario=scenario_enum)
    return generator.generate_all()
