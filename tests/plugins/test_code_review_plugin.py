"""
Unit tests for Code Review Plugin

Tests cover:
- SOLID principle violation detection
- Security vulnerability scanning
- Performance anti-pattern detection
- Overall code review workflow
- Score calculation
- Recommendation generation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

from plugins.code_review_plugin import (
    CodeReviewPlugin,
    SOLIDAnalyzer,
    SecurityScanner,
    PerformanceAnalyzer,
    ViolationType,
    ViolationSeverity,
    CodeViolation,
    ReviewResult
)


class TestSOLIDAnalyzer:
    """Test SOLID principle violation detection"""
    
    def setup_method(self):
        """Setup for each test"""
        self.analyzer = SOLIDAnalyzer()
    
    def test_detect_srp_violation_many_methods(self):
        """Test detection of SRP violation (too many methods)"""
        code = """
class UserManager:
    def create_user(self): pass
    def update_user(self): pass
    def delete_user(self): pass
    def authenticate(self): pass
    def send_email(self): pass
    def log_activity(self): pass
    def generate_report(self): pass
    def export_data(self): pass
    def import_data(self): pass
    def validate_data(self): pass
    def sync_with_api(self): pass
"""
        violations = self.analyzer.analyze("test.py", code, "python")
        
        srp_violations = [v for v in violations if v.type == ViolationType.SOLID_SRP]
        assert len(srp_violations) == 1
        assert srp_violations[0].severity == ViolationSeverity.HIGH
        assert "11 methods" in srp_violations[0].message
    
    def test_no_srp_violation_few_methods(self):
        """Test no SRP violation for class with few methods"""
        code = """
class User:
    def __init__(self): pass
    def validate(self): pass
    def save(self): pass
"""
        violations = self.analyzer.analyze("test.py", code, "python")
        
        srp_violations = [v for v in violations if v.type == ViolationType.SOLID_SRP]
        assert len(srp_violations) == 0
    
    def test_detect_dip_violation_direct_instantiation(self):
        """Test detection of DIP violation (direct instantiation)"""
        code = """
class OrderService:
    def process_order(self):
        repository = OrderRepository()  # Direct instantiation
        repository.save()
"""
        violations = self.analyzer.analyze("test.py", code, "python")
        
        dip_violations = [v for v in violations if v.type == ViolationType.SOLID_DIP]
        assert len(dip_violations) > 0
        assert any("OrderRepository" in v.message for v in dip_violations)
    
    def test_ignore_builtin_types(self):
        """Test that built-in types don't trigger DIP violations"""
        code = """
def process():
    data = dict()
    items = list()
    result = set()
"""
        violations = self.analyzer.analyze("test.py", code, "python")
        
        dip_violations = [v for v in violations if v.type == ViolationType.SOLID_DIP]
        assert len(dip_violations) == 0


class TestSecurityScanner:
    """Test security vulnerability scanning"""
    
    def setup_method(self):
        """Setup for each test"""
        self.scanner = SecurityScanner()
    
    def test_detect_hardcoded_password(self):
        """Test detection of hardcoded password"""
        code = """
def connect():
    password = "MySecretP@ssw0rd"
    db.connect(password=password)
"""
        violations = self.scanner.scan("test.py", code, "python")
        
        secret_violations = [
            v for v in violations
            if v.type == ViolationType.SECURITY_HARDCODED_SECRET
        ]
        assert len(secret_violations) == 1
        assert secret_violations[0].severity == ViolationSeverity.CRITICAL
        assert "password" in secret_violations[0].message.lower()
    
    def test_detect_hardcoded_api_key(self):
        """Test detection of hardcoded API key"""
        code = """
config = {
    'api_key': 'sk-1234567890abcdef',
    'endpoint': 'https://api.example.com'
}
"""
        violations = self.scanner.scan("test.py", code, "python")
        
        secret_violations = [
            v for v in violations
            if v.type == ViolationType.SECURITY_HARDCODED_SECRET
        ]
        assert len(secret_violations) == 1
        assert "api" in secret_violations[0].message.lower()
    
    def test_detect_sql_injection_concatenation(self):
        """Test detection of SQL injection via string concatenation"""
        code = """
def get_user(username):
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    return db.execute(query)
"""
        violations = self.scanner.scan("test.py", code, "python")
        
        sql_violations = [
            v for v in violations
            if v.type == ViolationType.SECURITY_SQL_INJECTION
        ]
        assert len(sql_violations) == 1
        assert sql_violations[0].severity == ViolationSeverity.CRITICAL
    
    def test_detect_sql_injection_fstring(self):
        """Test detection of SQL injection via f-string"""
        code = """
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.query(query)
"""
        violations = self.scanner.scan("test.py", code, "python")
        
        sql_violations = [
            v for v in violations
            if v.type == ViolationType.SECURITY_SQL_INJECTION
        ]
        assert len(sql_violations) == 1
    
    def test_detect_xss_innerHTML(self):
        """Test detection of XSS via innerHTML"""
        code = """
function updateContent(userInput) {
    document.getElementById('output').innerHTML = userInput;
}
"""
        violations = self.scanner.scan("test.js", code, "javascript")
        
        xss_violations = [
            v for v in violations
            if v.type == ViolationType.SECURITY_XSS
        ]
        assert len(xss_violations) == 1
        assert xss_violations[0].severity == ViolationSeverity.HIGH
        assert "innerHTML" in xss_violations[0].message
    
    def test_detect_xss_react_dangerous(self):
        """Test detection of XSS via dangerouslySetInnerHTML"""
        code = """
function MyComponent({ content }) {
    return <div dangerouslySetInnerHTML={{ __html: content }} />;
}
"""
        violations = self.scanner.scan("test.jsx", code, "javascript")
        
        xss_violations = [
            v for v in violations
            if v.type == ViolationType.SECURITY_XSS
        ]
        assert len(xss_violations) == 1
        assert "dangerouslySetInnerHTML" in xss_violations[0].message


class TestPerformanceAnalyzer:
    """Test performance anti-pattern detection"""
    
    def setup_method(self):
        """Setup for each test"""
        self.analyzer = PerformanceAnalyzer()
    
    def test_detect_n_plus_one_query(self):
        """Test detection of N+1 query problem"""
        code = """
async def get_users_with_posts():
    users = await User.query.all()
    for user in users:
        posts = await Post.query.filter(user_id=user.id).all()  # N+1!
        user.posts = posts
    return users
"""
        violations = self.analyzer.analyze("test.py", code, "python")
        
        n_plus_one = [
            v for v in violations
            if v.type == ViolationType.PERF_N_PLUS_ONE
        ]
        assert len(n_plus_one) == 1
        assert n_plus_one[0].severity == ViolationSeverity.HIGH
    
    def test_detect_blocking_sleep_in_async(self):
        """Test detection of blocking sleep in async function"""
        code = """
async def delayed_task():
    print("Starting")
    time.sleep(5)  # Blocking!
    print("Done")
"""
        violations = self.analyzer.analyze("test.py", code, "python")
        
        blocking = [
            v for v in violations
            if v.type == ViolationType.PERF_BLOCKING_IO
        ]
        assert len(blocking) == 1
        assert "time.sleep" in blocking[0].message
    
    def test_detect_blocking_requests_in_async(self):
        """Test detection of blocking requests in async function"""
        code = """
async def fetch_data():
    response = requests.get('https://api.example.com/data')  # Blocking!
    return response.json()
"""
        violations = self.analyzer.analyze("test.py", code, "python")
        
        blocking = [
            v for v in violations
            if v.type == ViolationType.PERF_BLOCKING_IO
        ]
        assert len(blocking) == 1
        assert "requests" in blocking[0].message
    
    def test_detect_inefficient_string_concat_in_loop(self):
        """Test detection of inefficient string concatenation in loop"""
        code = """
def build_html(items):
    html = ""
    for item in items:
        html += f"<li>{item}</li>"  # Inefficient!
    return html
"""
        violations = self.analyzer.analyze("test.py", code, "python")
        
        inefficient = [
            v for v in violations
            if v.type == ViolationType.PERF_INEFFICIENT_LOOP
        ]
        assert len(inefficient) == 1
        assert "concatenation" in inefficient[0].message.lower()


class TestCodeReviewPlugin:
    """Test overall code review plugin functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.plugin = CodeReviewPlugin({
            "min_confidence": 0.7,
            "max_violations_per_file": 50,
            "severity_threshold": "low"
        })
        self.plugin.initialize()
        
        # Create temp directory for test files
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup after each test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_plugin_initialization(self):
        """Test plugin initializes correctly"""
        assert self.plugin.metadata.plugin_id == "code_review"
        assert self.plugin.metadata.name == "Code Review Plugin"
        assert self.plugin.min_confidence == 0.7
    
    def test_detect_language_python(self):
        """Test language detection for Python files"""
        assert self.plugin._detect_language("test.py") == "python"
        assert self.plugin._detect_language("module.py") == "python"
    
    def test_detect_language_javascript(self):
        """Test language detection for JavaScript files"""
        assert self.plugin._detect_language("app.js") == "javascript"
        assert self.plugin._detect_language("component.jsx") == "javascript"
    
    def test_detect_language_typescript(self):
        """Test language detection for TypeScript files"""
        assert self.plugin._detect_language("app.ts") == "typescript"
        assert self.plugin._detect_language("component.tsx") == "typescript"
    
    def test_detect_language_csharp(self):
        """Test language detection for C# files"""
        assert self.plugin._detect_language("Program.cs") == "csharp"
    
    def test_calculate_score_no_violations(self):
        """Test score calculation with no violations"""
        score = self.plugin._calculate_score([], 100)
        assert score == 100.0
    
    def test_calculate_score_with_critical_violations(self):
        """Test score calculation with critical violations"""
        violations = [
            CodeViolation(
                type=ViolationType.SECURITY_HARDCODED_SECRET,
                severity=ViolationSeverity.CRITICAL,
                file_path="test.py",
                line_number=10,
                message="Critical issue"
            )
        ]
        score = self.plugin._calculate_score(violations, 100)
        assert score < 100.0
    
    def test_calculate_score_weighted_by_severity(self):
        """Test that score is weighted by severity"""
        critical_violations = [
            CodeViolation(
                type=ViolationType.SECURITY_SQL_INJECTION,
                severity=ViolationSeverity.CRITICAL,
                file_path="test.py",
                line_number=10,
                message="Critical"
            )
        ]
        
        low_violations = [
            CodeViolation(
                type=ViolationType.STYLE_NAMING,
                severity=ViolationSeverity.LOW,
                file_path="test.py",
                line_number=10,
                message="Low"
            )
        ]
        
        critical_score = self.plugin._calculate_score(critical_violations, 100)
        low_score = self.plugin._calculate_score(low_violations, 100)
        
        assert critical_score < low_score
    
    def test_generate_recommendations_for_secrets(self):
        """Test recommendation generation for hardcoded secrets"""
        violations = [
            CodeViolation(
                type=ViolationType.SECURITY_HARDCODED_SECRET,
                severity=ViolationSeverity.CRITICAL,
                file_path="test.py",
                line_number=10,
                message="Hardcoded password"
            )
        ]
        
        recommendations = self.plugin._generate_recommendations(violations)
        
        assert len(recommendations) > 0
        assert any("vault" in r.lower() for r in recommendations)
    
    def test_generate_recommendations_for_srp(self):
        """Test recommendation generation for SRP violations"""
        violations = [
            CodeViolation(
                type=ViolationType.SOLID_SRP,
                severity=ViolationSeverity.HIGH,
                file_path="test.py",
                line_number=10,
                message="Too many methods"
            )
        ]
        
        recommendations = self.plugin._generate_recommendations(violations)
        
        assert len(recommendations) > 0
        assert any("single responsibility" in r.lower() for r in recommendations)
    
    def test_generate_recommendations_for_sql_injection(self):
        """Test recommendation generation for SQL injection"""
        violations = [
            CodeViolation(
                type=ViolationType.SECURITY_SQL_INJECTION,
                severity=ViolationSeverity.CRITICAL,
                file_path="test.py",
                line_number=10,
                message="SQL injection"
            )
        ]
        
        recommendations = self.plugin._generate_recommendations(violations)
        
        assert len(recommendations) > 0
        assert any("parameterized" in r.lower() for r in recommendations)
        assert any("critical" in r.lower() for r in recommendations)
    
    def test_execute_review_with_violations(self):
        """Test executing review on file with violations"""
        # Create test file with violations
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("""
def login(username, password):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)
""")
        
        context = {
            "pr_id": "PR-123",
            "files": [{"path": "test.py"}],
            "repository_path": self.temp_dir
        }
        
        result = self.plugin.execute(context)
        
        assert result["success"] is True
        assert "result" in result
        review = result["result"]
        assert review["pr_id"] == "PR-123"
        assert review["files_reviewed"] == 1
        assert len(review["violations"]) > 0
    
    def test_execute_review_calculates_score(self):
        """Test that review calculates overall score"""
        # Create test file
        test_file = Path(self.temp_dir) / "clean.py"
        test_file.write_text("""
def add(a, b):
    return a + b
""")
        
        context = {
            "pr_id": "PR-456",
            "files": [{"path": "clean.py"}],
            "repository_path": self.temp_dir
        }
        
        result = self.plugin.execute(context)
        
        assert result["success"] is True
        review = result["result"]
        assert "overall_score" in review
        assert 0 <= review["overall_score"] <= 100
    
    def test_filter_by_confidence_threshold(self):
        """Test that violations below confidence threshold are filtered"""
        code = """
class Manager:
    def process(self):
        handler = Handler()  # Might be DIP violation
"""
        violations = self.plugin._analyze_file("test.py", code, "python")
        
        # All returned violations should meet confidence threshold
        for v in violations:
            assert v.confidence >= self.plugin.min_confidence
    
    def test_limit_violations_per_file(self):
        """Test that violations per file are limited"""
        # Create code with many violations
        code = "\n".join([
            f"password_{i} = 'secret{i}'"
            for i in range(100)
        ])
        
        violations = self.plugin._analyze_file("test.py", code, "python")
        
        # Should not exceed max_violations
        assert len(violations) <= self.plugin.max_violations
    
    def test_cleanup(self):
        """Test plugin cleanup"""
        # Add something to cache
        self.plugin.review_cache["test"] = Mock()
        
        success = self.plugin.cleanup()
        
        assert success is True
        assert len(self.plugin.review_cache) == 0


class TestReviewResult:
    """Test ReviewResult data class"""
    
    def test_count_violations_by_severity(self):
        """Test counting violations by severity"""
        violations = [
            CodeViolation(
                type=ViolationType.SECURITY_SQL_INJECTION,
                severity=ViolationSeverity.CRITICAL,
                file_path="test.py",
                line_number=10,
                message="Critical"
            ),
            CodeViolation(
                type=ViolationType.SOLID_SRP,
                severity=ViolationSeverity.HIGH,
                file_path="test.py",
                line_number=20,
                message="High"
            ),
            CodeViolation(
                type=ViolationType.PERF_INEFFICIENT_LOOP,
                severity=ViolationSeverity.MEDIUM,
                file_path="test.py",
                line_number=30,
                message="Medium"
            ),
            CodeViolation(
                type=ViolationType.STYLE_NAMING,
                severity=ViolationSeverity.LOW,
                file_path="test.py",
                line_number=40,
                message="Low"
            )
        ]
        
        result = ReviewResult(
            pr_id="PR-789",
            violations=violations,
            files_reviewed=1,
            lines_reviewed=100,
            review_time_seconds=2.5,
            overall_score=85.0,
            recommendations=[]
        )
        
        assert result.critical_count == 1
        assert result.high_count == 1
        assert result.medium_count == 1
        assert result.low_count == 1
    
    def test_to_dict_includes_all_fields(self):
        """Test that to_dict includes all required fields"""
        result = ReviewResult(
            pr_id="PR-999",
            violations=[],
            files_reviewed=5,
            lines_reviewed=500,
            review_time_seconds=10.0,
            overall_score=95.0,
            recommendations=["Good job!"]
        )
        
        result_dict = result.to_dict()
        
        assert "pr_id" in result_dict
        assert "violations" in result_dict
        assert "files_reviewed" in result_dict
        assert "lines_reviewed" in result_dict
        assert "review_time_seconds" in result_dict
        assert "overall_score" in result_dict
        assert "critical_count" in result_dict
        assert "high_count" in result_dict
        assert "medium_count" in result_dict
        assert "low_count" in result_dict
        assert "recommendations" in result_dict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
