"""
Tests for Test Gap Prioritization Matrix

Validates P0/P1/P2/P3 classification of untested code by:
- Business criticality
- Risk scoring (complexity, change frequency, bug history)
- Pattern detection (API endpoints, auth, money, security)

Author: Asif Hussain
Created: 2025-12-08
Phase: Dashboard Code Intelligence - Phase 2.5.3 (RED)
"""

import pytest
from pathlib import Path
import tempfile
import json

# RED phase - import will fail until GREEN phase implementation
try:
    from src.intelligence.gap_prioritization_matrix import (
        GapPrioritizer,
        Priority,
        TestGap,
        RiskFactors,
        CodePattern
    )
    IMPLEMENTATION_EXISTS = True
except ImportError:
    IMPLEMENTATION_EXISTS = False


@pytest.fixture
def temp_project():
    """Create temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_coverage_data():
    """Sample coverage baseline for testing."""
    return {
        "overall_coverage": 45.2,
        "files": [
            {
                "file": "src/api/UserController.cs",
                "coverage": 0.0,
                "complexity": 12,
                "loc": 234
            },
            {
                "file": "src/services/PayrollCalculator.cs",
                "coverage": 15.3,
                "complexity": 18,
                "loc": 456
            },
            {
                "file": "src/utils/StringHelper.cs",
                "coverage": 85.7,
                "complexity": 3,
                "loc": 89
            },
            {
                "file": "src/models/UserDto.cs",
                "coverage": 0.0,
                "complexity": 1,
                "loc": 45
            }
        ]
    }


@pytest.fixture
def sample_git_history():
    """Sample git commit history for change frequency analysis."""
    return [
        {"file": "src/api/UserController.cs", "commits": 15, "bugs": 5},
        {"file": "src/services/PayrollCalculator.cs", "commits": 8, "bugs": 3},
        {"file": "src/utils/StringHelper.cs", "commits": 2, "bugs": 0},
        {"file": "src/models/UserDto.cs", "commits": 1, "bugs": 0}
    ]


class TestPriorityClassification:
    """Test P0/P1/P2/P3 classification logic."""
    
    def test_p0_critical_api_endpoint_no_coverage(self, temp_project, sample_coverage_data):
        """P0: API endpoint with 0% coverage should be critical."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        # Create API controller file
        api_file = temp_project / "src" / "api" / "UserController.cs"
        api_file.parent.mkdir(parents=True, exist_ok=True)
        api_file.write_text("""
        [ApiController]
        [Route("api/users")]
        public class UserController {
            [HttpGet]
            public IActionResult GetUsers() {
                return Ok(_service.GetAll());
            }
        }
        """)
        
        gaps = prioritizer.analyze_gaps(sample_coverage_data)
        
        p0_gaps = [g for g in gaps if g.priority == Priority.P0_CRITICAL]
        assert len(p0_gaps) > 0
        
        user_controller_gap = next((g for g in p0_gaps if "UserController" in g.file_path), None)
        assert user_controller_gap is not None
        assert user_controller_gap.reason.lower().find("api") >= 0 or \
               user_controller_gap.reason.lower().find("endpoint") >= 0
    
    def test_p0_critical_financial_calculation(self, temp_project, sample_coverage_data):
        """P0: Financial calculation with low coverage should be critical."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        # Create payroll calculator
        calc_file = temp_project / "src" / "services" / "PayrollCalculator.cs"
        calc_file.parent.mkdir(parents=True, exist_ok=True)
        calc_file.write_text("""
        public class PayrollCalculator {
            public decimal CalculateNetPay(decimal gross, decimal tax) {
                return gross - tax;
            }
        }
        """)
        
        gaps = prioritizer.analyze_gaps(sample_coverage_data)
        
        p0_gaps = [g for g in gaps if g.priority == Priority.P0_CRITICAL]
        payroll_gap = next((g for g in p0_gaps if "PayrollCalculator" in g.file_path), None)
        
        assert payroll_gap is not None
        assert payroll_gap.current_coverage < 30.0
    
    def test_p1_high_business_logic(self, temp_project):
        """P1: Business logic services with medium coverage should be high priority."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        # Create service with business logic
        service_file = temp_project / "src" / "services" / "OrderService.cs"
        service_file.parent.mkdir(parents=True, exist_ok=True)
        service_file.write_text("""
        public class OrderService {
            public Order ProcessOrder(OrderRequest request) {
                // Business logic here
                return new Order();
            }
        }
        """)
        
        coverage_data = {
            "files": [{
                "file": "src/services/OrderService.cs",
                "coverage": 45.0,
                "complexity": 8,
                "loc": 156
            }]
        }
        
        gaps = prioritizer.analyze_gaps(coverage_data)
        
        p1_gaps = [g for g in gaps if g.priority == Priority.P1_HIGH]
        order_gap = next((g for g in p1_gaps if "OrderService" in g.file_path), None)
        
        assert order_gap is not None
    
    def test_p2_medium_utility_functions(self, temp_project, sample_coverage_data):
        """P2: Utility functions with high coverage should be medium priority."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        # Create utility helper
        util_file = temp_project / "src" / "utils" / "StringHelper.cs"
        util_file.parent.mkdir(parents=True, exist_ok=True)
        util_file.write_text("""
        public static class StringHelper {
            public static string Capitalize(string input) {
                return char.ToUpper(input[0]) + input.Substring(1);
            }
        }
        """)
        
        gaps = prioritizer.analyze_gaps(sample_coverage_data)
        
        p2_gaps = [g for g in gaps if g.priority == Priority.P2_MEDIUM]
        util_gap = next((g for g in p2_gaps if "StringHelper" in g.file_path), None)
        
        # Utilities with high coverage should be P2 or lower
        assert util_gap is not None or \
               any(g.file_path.find("StringHelper") >= 0 for g in gaps if g.priority == Priority.P3_LOW)
    
    def test_p3_low_dto_classes(self, temp_project, sample_coverage_data):
        """P3: Simple DTOs should be low priority."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        # Create DTO
        dto_file = temp_project / "src" / "models" / "UserDto.cs"
        dto_file.parent.mkdir(parents=True, exist_ok=True)
        dto_file.write_text("""
        public class UserDto {
            public int Id { get; set; }
            public string Name { get; set; }
            public string Email { get; set; }
        }
        """)
        
        gaps = prioritizer.analyze_gaps(sample_coverage_data)
        
        p3_gaps = [g for g in gaps if g.priority == Priority.P3_LOW]
        dto_gap = next((g for g in p3_gaps if "UserDto" in g.file_path), None)
        
        assert dto_gap is not None
        assert dto_gap.complexity <= 3


class TestPatternDetection:
    """Test detection of API endpoints, auth, money, security patterns."""
    
    def test_detect_api_endpoints_http_attributes(self, temp_project):
        """Detect C# API endpoints via HTTP attributes."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        code = """
        [HttpGet]
        [HttpPost]
        [Route("api/users/{id}")]
        public class UserController { }
        """
        
        patterns = prioritizer.detect_patterns(code, "UserController.cs")
        
        assert CodePattern.API_ENDPOINT in patterns
    
    def test_detect_api_endpoints_flask_decorator(self, temp_project):
        """Detect Python Flask API endpoints."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        code = """
        @app.route('/api/users', methods=['GET', 'POST'])
        def get_users():
            return jsonify(users)
        """
        
        patterns = prioritizer.detect_patterns(code, "app.py")
        
        assert CodePattern.API_ENDPOINT in patterns
    
    def test_detect_authentication_keywords(self, temp_project):
        """Detect authentication/authorization code by keywords."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        code = """
        public class AuthService {
            public bool Authenticate(string username, string password) {
                var user = _repository.GetByUsername(username);
                return _hasher.Verify(password, user.PasswordHash);
            }
        }
        """
        
        patterns = prioritizer.detect_patterns(code, "AuthService.cs")
        
        assert CodePattern.AUTHENTICATION in patterns
    
    def test_detect_money_operations(self, temp_project):
        """Detect financial/money operations."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        code = """
        public decimal CalculateTax(decimal amount) {
            return amount * 0.08M;
        }
        
        public Money ConvertCurrency(Money amount, Currency to) {
            return amount * _rate;
        }
        """
        
        patterns = prioritizer.detect_patterns(code, "TaxCalculator.cs")
        
        assert CodePattern.MONEY_OPERATION in patterns
    
    def test_detect_security_operations(self, temp_project):
        """Detect security-sensitive code."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        code = """
        public string Encrypt(string data, string key) {
            return _cipher.Encrypt(data, key);
        }
        
        public string Sanitize(string input) {
            return _validator.Escape(input);
        }
        """
        
        patterns = prioritizer.detect_patterns(code, "SecurityHelper.cs")
        
        assert CodePattern.SECURITY in patterns


class TestRiskScoring:
    """Test risk factor calculations."""
    
    def test_complexity_risk_high(self, temp_project):
        """High cyclomatic complexity increases risk score."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        factors = RiskFactors(
            complexity=18,
            change_frequency=5,
            bug_count=2,
            dependency_count=3
        )
        
        risk_score = prioritizer.calculate_risk_score(factors)
        
        assert risk_score > 65  # High complexity should yield high risk
    
    def test_change_frequency_risk(self, temp_project, sample_git_history):
        """Frequent changes increase risk score."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        # File with 15 commits in 90 days
        factors = RiskFactors(
            complexity=8,
            change_frequency=15,
            bug_count=1,
            dependency_count=2
        )
        
        risk_score = prioritizer.calculate_risk_score(factors)
        
        assert risk_score > 50
    
    def test_bug_history_risk(self, temp_project):
        """Bug history increases risk score."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        # File with 5 bugs in last 6 months
        factors = RiskFactors(
            complexity=10,
            change_frequency=8,
            bug_count=5,
            dependency_count=4
        )
        
        risk_score = prioritizer.calculate_risk_score(factors)
        
        assert risk_score > 60  # High bug count should significantly increase risk
    
    def test_low_risk_stable_code(self, temp_project):
        """Stable, simple code has low risk score."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        factors = RiskFactors(
            complexity=2,
            change_frequency=1,
            bug_count=0,
            dependency_count=1
        )
        
        risk_score = prioritizer.calculate_risk_score(factors)
        
        assert risk_score < 30


class TestEffortEstimation:
    """Test effort hour calculations."""
    
    def test_effort_based_on_complexity(self, temp_project):
        """Effort estimates should scale with complexity."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        simple_gap = TestGap(
            file_path="simple.py",
            priority=Priority.P1_HIGH,
            complexity=3,
            loc=50,
            current_coverage=0.0
        )
        
        complex_gap = TestGap(
            file_path="complex.py",
            priority=Priority.P1_HIGH,
            complexity=18,
            loc=50,
            current_coverage=0.0
        )
        
        simple_effort = prioritizer.estimate_effort(simple_gap)
        complex_effort = prioritizer.estimate_effort(complex_gap)
        
        assert complex_effort > simple_effort
    
    def test_effort_based_on_priority(self, temp_project):
        """P0 critical items may require more thorough testing."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        p0_gap = TestGap(
            file_path="critical.py",
            priority=Priority.P0_CRITICAL,
            complexity=10,
            loc=100,
            current_coverage=0.0
        )
        
        p2_gap = TestGap(
            file_path="medium.py",
            priority=Priority.P2_MEDIUM,
            complexity=10,
            loc=100,
            current_coverage=0.0
        )
        
        p0_effort = prioritizer.estimate_effort(p0_gap)
        p2_effort = prioritizer.estimate_effort(p2_gap)
        
        # P0 may require more effort due to higher testing standards
        assert p0_effort >= p2_effort


class TestOutputFormat:
    """Test JSON output structure."""
    
    def test_output_json_structure(self, temp_project, sample_coverage_data):
        """Output should have P0/P1/P2/P3 sections with examples."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        prioritizer = GapPrioritizer(temp_project)
        
        # Create sample files
        (temp_project / "src" / "api").mkdir(parents=True, exist_ok=True)
        (temp_project / "src" / "api" / "UserController.cs").write_text("[HttpGet] class UserController {}")
        
        gaps = prioritizer.analyze_gaps(sample_coverage_data)
        output = prioritizer.generate_report(gaps)
        
        # Verify structure
        assert "p0_critical" in output
        assert "p1_high" in output
        assert "p2_medium" in output
        assert "p3_low" in output
        assert "summary" in output
        
        # Verify P0 structure
        assert "count" in output["p0_critical"]
        assert "total_loc" in output["p0_critical"]
        assert "estimated_hours" in output["p0_critical"]
        assert "examples" in output["p0_critical"]
        
        # Verify summary
        assert "total_untested_methods" in output["summary"]
        assert "total_effort_hours" in output["summary"]


class TestPerformance:
    """Test performance requirements."""
    
    def test_large_codebase_performance(self, temp_project):
        """Should analyze 500 files in <10 seconds."""
        if not IMPLEMENTATION_EXISTS:
            pytest.skip("GapPrioritizer not implemented yet (RED phase)")
        
        import time
        
        prioritizer = GapPrioritizer(temp_project)
        
        # Create 500 files with coverage data
        coverage_data = {"files": []}
        for i in range(500):
            file_path = temp_project / f"src/module{i}/file{i}.py"
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(f"def function{i}(): pass")
            
            coverage_data["files"].append({
                "file": f"src/module{i}/file{i}.py",
                "coverage": 50.0,
                "complexity": 5,
                "loc": 100
            })
        
        start = time.time()
        gaps = prioritizer.analyze_gaps(coverage_data)
        elapsed = time.time() - start
        
        assert elapsed < 10.0, f"Analysis took {elapsed:.2f}s, expected <10s"
        assert len(gaps) > 0
