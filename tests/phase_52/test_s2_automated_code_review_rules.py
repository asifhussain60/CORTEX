"""
Phase 52 Stage 2: Automated Code Review Rules (TDD RED Phase)
AC-PHASE52-S2-001 through AC-PHASE52-S2-007: Security checks, standards validation, dependency analysis
"""

import pytest
from typing import Dict, List, Tuple
from dataclasses import dataclass
from unittest.mock import Mock, patch, MagicMock

# Import implementations
from cortex.orchestrators.review.s2_code_review_rules import (
    SecurityCheckFilter,
    CodeStandardsValidator,
    DependencyAnalyzer,
    ReviewCommentGenerator,
    ReviewRuleEngine,
)

# ============================================================================
# TEST INFRASTRUCTURE: Fixtures & Helpers
# ============================================================================

@dataclass
class DiffHunk:
    """Represents a single diff hunk from a GitHub PR"""
    filename: str
    additions: List[str]
    deletions: List[str]
    line_numbers: Dict[str, int]


@dataclass
class ReviewComment:
    """Represents a single review comment"""
    path: str
    line: int
    body: str
    severity: str  # "info", "warning", "error", "critical"


@pytest.fixture
def sample_pr_diff():
    """Sample PR diff for testing"""
    return {
        "files": [
            {
                "filename": "app/models/user.py",
                "patch": """@@ -10,6 +10,12 @@ class User(Base):
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
+   # Database connection string hardcoded ❌
+   DB_URL = "postgres://user:password@localhost:5432/mydb"
+   
+   # AWS credentials in code ❌
+   AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
+   AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
     @property""",
                "additions": [
                    '   DB_URL = "postgres://user:password@localhost:5432/mydb"',
                    '   AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"',
                    '   AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"',
                ],
                "deletions": []
            },
            {
                "filename": "requirements.txt",
                "patch": """@@ -5,3 +5,5 @@
    flask==2.0.1
    sqlalchemy==1.4.0
    requests==2.26.0
+   django==2.2.0
+   vulnerable-package==1.0.0""",
                "additions": [
                    "django==2.2.0",
                    "vulnerable-package==1.0.0"
                ],
                "deletions": []
            }
        ]
    }


@pytest.fixture
def sample_code_violations():
    """Code quality violations to test"""
    return {
        "secrets": [
            ("DB_URL", "postgres://user:password"),
            ("AWS_ACCESS_KEY", "AKIA"),
            ("PRIVATE_KEY", "-----BEGIN"),
        ],
        "style_issues": [
            ("variable_naming", "camelCase instead of snake_case"),
            ("function_length", ">20 lines without docstring"),
            ("import_sorting", "imports not alphabetized"),
        ],
        "security": [
            ("sql_injection", "raw SQL query without parameterization"),
            ("xss_vulnerability", "unsanitized HTML rendering"),
            ("weak_crypto", "MD5 hashing instead of bcrypt"),
        ]
    }


# ============================================================================
# AC-PHASE52-S2-001: Security Check Filter (Detect Secrets)
# ============================================================================

class TestSecurityCheckFilter:
    """Test secret and credential detection"""
    
    def test_detects_database_urls(self, sample_pr_diff):
        """AC-PHASE52-S2-001-A: Detect database connection strings"""
        # RED: Expect SecurityCheckFilter to find DB URL
        filter = SecurityCheckFilter()
        violations = filter.find_secrets(sample_pr_diff)
        
        assert len(violations) > 0
        assert any("postgres://" in str(v) for v in violations)
        assert violations[0]["severity"] == "critical"
    
    def test_detects_aws_credentials(self, sample_pr_diff):
        """AC-PHASE52-S2-001-B: Detect AWS access/secret keys"""
        filter = SecurityCheckFilter()
        violations = filter.find_secrets(sample_pr_diff)
        
        assert any("AKIA" in str(v) for v in violations)  # AWS key pattern
        assert any(v["severity"] == "critical" for v in violations)
    
    def test_detects_private_keys(self):
        """AC-PHASE52-S2-001-C: Detect private keys"""
        diff = {
            "files": [{
                "filename": "config/private_key.pem",
                "additions": [
                    "-----BEGIN RSA PRIVATE KEY-----",
                    "MIIEpQIBAAKCAQEA2...",
                    "-----END RSA PRIVATE KEY-----"
                ]
            }]
        }
        
        filter = SecurityCheckFilter()
        violations = filter.find_secrets(diff)
        
        assert len(violations) > 0
        assert any("PRIVATE KEY" in str(v) for v in violations)
    
    def test_detects_api_tokens(self):
        """AC-PHASE52-S2-001-D: Detect hardcoded API tokens"""
        diff = {
            "files": [{
                "filename": "app/config.py",
                "additions": [
                    'GITHUB_TOKEN = "ghp_1234567890abcdef1234567890"',
                    'SLACK_BOT_TOKEN = "xoxb-123456789012-123456789012-abcdefghij"'
                ]
            }]
        }
        
        filter = SecurityCheckFilter()
        violations = filter.find_secrets(diff)
        
        assert len(violations) >= 2
        assert all(v["severity"] == "critical" for v in violations)
    
    def test_no_false_positives(self):
        """AC-PHASE52-S2-001-E: Avoid false positives for legitimate URLs"""
        diff = {
            "files": [{
                "filename": "README.md",
                "additions": [
                    "Connect to https://example.com with port 5432",
                    "Use demo://localhost:5432/testdb"
                ]
            }]
        }
        
        filter = SecurityCheckFilter()
        violations = filter.find_secrets(diff)
        
        # Legitimate demo URLs should not trigger
        assert len(violations) == 0


# ============================================================================
# AC-PHASE52-S2-002: Code Standards Validator
# ============================================================================

class TestCodeStandardsValidator:
    """Test company code standards enforcement"""
    
    def test_validates_naming_conventions(self):
        """AC-PHASE52-S2-002-A: Enforce snake_case naming"""
        code = """
def myFunction():  # ❌ camelCase
    myVariable = 10  # ❌ camelCase
    result = compute()
    return result
"""
        
        validator = CodeStandardsValidator()
        violations = validator.validate(code, "python")
        
        assert len(violations) > 0
        assert any("snake_case" in str(v) for v in violations)
    
    def test_validates_function_docstrings(self):
        """AC-PHASE52-S2-002-B: Require docstrings for public functions"""
        code = """
def process_data(items):  # ❌ Missing docstring
    return [x * 2 for x in items]

def _helper():  # ✅ Private, optional
    pass
"""
        
        validator = CodeStandardsValidator()
        violations = validator.validate(code, "python")
        
        assert any("docstring" in str(v) for v in violations)
    
    def test_validates_type_hints(self):
        """AC-PHASE52-S2-002-C: Require type hints for functions"""
        code = """
def calculate(x, y):  # ❌ Missing type hints
    return x + y

def add_typed(x: int, y: int) -> int:  # ✅ Complete
    return x + y
"""
        
        validator = CodeStandardsValidator()
        violations = validator.validate(code, "python")
        
        assert any("type hint" in str(v) for v in violations)
    
    def test_validates_import_organization(self):
        """AC-PHASE52-S2-002-D: Enforce import organization"""
        code = """
import requests
import os
from typing import List
import sys
from dataclasses import dataclass
"""
        
        validator = CodeStandardsValidator()
        violations = validator.validate(code, "python")
        
        # Imports should be: stdlib, then 3rd-party, then local
        assert len(violations) > 0


# ============================================================================
# AC-PHASE52-S2-003: Dependency Analyzer (Vulnerable Packages)
# ============================================================================

class TestDependencyAnalyzer:
    """Test dependency vulnerability detection"""
    
    def test_detects_known_vulnerabilities(self):
        """AC-PHASE52-S2-003-A: Flag known vulnerable package versions"""
        requirements = [
            "django==2.2.0",  # ❌ Known vulnerabilities (EOL)
            "requests==2.26.0",  # ✅ Safe
        ]
        
        analyzer = DependencyAnalyzer()
        violations = analyzer.analyze(requirements)
        
        assert len(violations) > 0
        assert any("django" in str(v).lower() for v in violations)
        assert any("EOL" in str(v) or "security" in str(v).lower() for v in violations)
    
    def test_detects_unpinned_versions(self):
        """AC-PHASE52-S2-003-B: Warn on unpinned/loose version specs"""
        requirements = [
            "flask>=2.0",  # ⚠️ Loose spec
            "requests==2.26.0",  # ✅ Pinned
            "django",  # ❌ No version
        ]
        
        analyzer = DependencyAnalyzer()
        violations = analyzer.analyze(requirements)
        
        assert any("unpin" in str(v).lower() for v in violations)
    
    def test_detects_abandoned_packages(self):
        """AC-PHASE52-S2-003-C: Flag abandoned/unmaintained packages"""
        requirements = [
            "unmaintained-lib==1.0.0",
            "actively-maintained==2.0.0",
        ]
        
        analyzer = DependencyAnalyzer()
        # Mock package metadata
        analyzer._get_package_status = Mock(side_effect=lambda pkg: {
            "unmaintained-lib": {"status": "abandoned", "last_update": "2015-01-01"},
            "actively-maintained": {"status": "maintained", "last_update": "2026-02-01"},
        }.get(pkg, {}))
        
        violations = analyzer.analyze(requirements)
        assert any("unmaintained" in str(v).lower() or "abandoned" in str(v).lower() for v in violations)
    
    def test_detects_dependency_conflicts(self):
        """AC-PHASE52-S2-003-D: Detect version conflicts"""
        requirements = [
            "package-a==1.0 (requires package-b>=2.0)",
            "package-b==1.5",  # ❌ Conflicts with package-a requirement
        ]
        
        analyzer = DependencyAnalyzer()
        violations = analyzer.analyze(requirements)
        
        assert any("conflict" in str(v).lower() for v in violations)


# ============================================================================
# AC-PHASE52-S2-004: Review Comment Generator
# ============================================================================

class TestReviewCommentGenerator:
    """Test review comment generation"""
    
    def test_generates_security_comments(self):
        """AC-PHASE52-S2-004-A: Generate clear security violation comments"""
        violation = {
            "type": "hardcoded_secret",
            "path": "app/models/user.py",
            "line": 15,
            "description": "AWS access key detected",
            "severity": "critical"
        }
        
        generator = ReviewCommentGenerator()
        comment = generator.generate(violation)
        
        assert "AWS" in comment["body"]
        assert "secret" in comment["body"].lower()
        assert comment["severity"] == "critical"
        assert "🔴" in comment["body"] or "❌" in comment["body"]  # Visual indicator
    
    def test_generates_actionable_comments(self):
        """AC-PHASE52-S2-004-B: Include remediation steps"""
        violation = {
            "type": "style_violation",
            "path": "app/handlers.py",
            "line": 32,
            "description": "Function exceeds 20 lines without docstring",
            "severity": "warning"
        }
        
        generator = ReviewCommentGenerator()
        comment = generator.generate(violation)
        
        assert "how to fix" in comment["body"].lower() or "add" in comment["body"].lower()
        assert "docstring" in comment["body"].lower()
    
    def test_generates_company_standards_comments(self):
        """AC-PHASE52-S2-004-C: Reference company standards"""
        violation = {
            "type": "naming_convention",
            "path": "app/utils.py",
            "line": 10,
            "description": "Variable uses camelCase, expected snake_case",
            "severity": "info"
        }
        
        generator = ReviewCommentGenerator()
        comment = generator.generate(violation)
        
        assert "snake_case" in comment["body"]
        assert "standard" in comment["body"].lower() or "convention" in comment["body"].lower()
    
    def test_batches_related_comments(self):
        """AC-PHASE52-S2-004-D: Group related violations in single comment"""
        violations = [
            {"type": "naming", "path": "app.py", "line": 5},
            {"type": "naming", "path": "app.py", "line": 7},
            {"type": "naming", "path": "app.py", "line": 9},
        ]
        
        generator = ReviewCommentGenerator()
        comments = generator.batch_generate(violations)
        
        # Should combine related violations
        assert len(comments) < len(violations)


# ============================================================================
# AC-PHASE52-S2-005: Integration - Review Rule Engine
# ============================================================================

class TestReviewRuleEngine:
    """Test complete review rule processing"""
    
    def test_applies_all_checks(self, sample_pr_diff):
        """AC-PHASE52-S2-005-A: Execute security, standards, dependency checks"""
        engine = ReviewRuleEngine()
        issues = engine.analyze(sample_pr_diff)
        
        # Should find: secrets, dependency issues
        assert len(issues) > 0
        assert any(i["category"] == "security" for i in issues)
    
    def test_prioritizes_critical_issues(self, sample_pr_diff):
        """AC-PHASE52-S2-005-B: Critical issues appear first"""
        engine = ReviewRuleEngine()
        issues = engine.analyze(sample_pr_diff)
        
        if len(issues) > 1:
            critical_count = sum(1 for i in issues if i["severity"] == "critical")
            non_critical_count = sum(1 for i in issues if i["severity"] != "critical")
            
            # Critical should be listed first
            for i, issue in enumerate(issues[:critical_count]):
                assert issue["severity"] == "critical"
    
    def test_returns_structured_review(self, sample_pr_diff):
        """AC-PHASE52-S2-005-C: Return structured review object"""
        engine = ReviewRuleEngine()
        review = engine.review(sample_pr_diff)
        
        assert "summary" in review  # Overall summary
        assert "issues" in review  # Detailed issues
        assert "recommendation" in review  # Approve/request-changes
        assert "stats" in review  # Count by severity


# ============================================================================
# AC-PHASE52-S2-006: Configuration & Customization
# ============================================================================

class TestReviewConfiguration:
    """Test configuration of review rules"""
    
    def test_enables_disable_checks(self):
        """AC-PHASE52-S2-006-A: Allow enabling/disabling specific checks"""
        config = {
            "checks": {
                "secrets": {"enabled": True},
                "style": {"enabled": False},  # Disabled
                "dependencies": {"enabled": True},
            }
        }
        
        engine = ReviewRuleEngine(config)
        
        assert engine.is_check_enabled("secrets")
        assert not engine.is_check_enabled("style")
    
    def test_customizes_severity_levels(self):
        """AC-PHASE52-S2-006-B: Customize severity mapping"""
        config = {
            "severity_mapping": {
                "secrets": "critical",  # Always critical
                "style": "info",  # Downgraded from warning
            }
        }
        
        engine = ReviewRuleEngine(config)
        assert engine.get_severity("secrets") == "critical"
        assert engine.get_severity("style") == "info"


# ============================================================================
# AC-PHASE52-S2-007: Performance & Edge Cases
# ============================================================================

class TestReviewPerformance:
    """Test performance and edge cases"""
    
    def test_handles_large_diffs(self):
        """AC-PHASE52-S2-007-A: Process large PR diffs efficiently"""
        large_diff = {
            "files": [
                {
                    "filename": f"file{i}.py",
                    "additions": [f"line {j}" for j in range(1000)]
                }
                for i in range(100)
            ] + [
                {
                    "filename": "config.py",
                    "additions": ['API_KEY = "AKIAIOSFODNN7EXAMPLE"']
                }
            ]
        }
        
        engine = ReviewRuleEngine()
        
        import time
        start = time.time()
        issues = engine.analyze(large_diff)
        elapsed = time.time() - start
        
        # Should complete in <5 seconds
        assert elapsed < 5.0
        # Should find at least the API key violation
        assert len(issues) > 0
    
    def test_handles_empty_diffs(self):
        """AC-PHASE52-S2-007-B: Handle empty or minimal diffs"""
        empty_diff = {"files": []}
        
        engine = ReviewRuleEngine()
        issues = engine.analyze(empty_diff)
        
        assert issues == [] or len(issues) == 0
    
    def test_handles_binary_files(self):
        """AC-PHASE52-S2-007-C: Skip binary file analysis"""
        diff = {
            "files": [
                {"filename": "image.png", "binary": True, "additions": []},
                {"filename": "script.py", "additions": ["print('hello')"]}
            ]
        }
        
        engine = ReviewRuleEngine()
        issues = engine.analyze(diff)
        
        # Should skip binary, analyze Python
        paths = [i["path"] for i in issues]
        assert "image.png" not in paths

    def get_severity(self, check_name: str) -> str:
        """Get severity level for check"""
        raise NotImplementedError("RED: Implement severity mapping")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
