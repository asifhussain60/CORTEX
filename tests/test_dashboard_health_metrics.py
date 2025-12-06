"""
Comprehensive Test Suite for Dashboard Health Metrics

CRITICAL: This dashboard drives LEADERSHIP DECISIONS - data CANNOT be wrong!

Tests cover:
1. Health metrics calculation with real data structures
2. Data validation and integrity checks
3. Edge cases (missing data, malformed JSON, zero values)
4. Parallel collector orchestration
5. Data structure conformance
6. Confirmation steps before writing critical metrics

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


class TestHealthMetricsCalculation:
    """Test health metrics calculation with real-world data structures."""
    
    @pytest.fixture
    def sample_code_organization_data(self):
        """Sample data matching actual code-organization.json structure."""
        return {
            "summary": {
                "total_files": 10391,
                "total_loc": 1246213,
                "maintainability_score": 77,
                "high_complexity_files": 480,
                "avg_complexity": 3.2,
                "code_smells": 1234
            },
            "hotspots": [
                {"file": "Controllers/HomeController.cs", "complexity": 45, "loc": 1200},
                {"file": "Services/DataService.cs", "complexity": 38, "loc": 950}
            ],
            "file_complexity": {},
            "module_structure": {}
        }
    
    @pytest.fixture
    def sample_security_data(self):
        """Sample data matching actual security.json structure."""
        return {
            "overall_score": 65,
            "last_scan": "2025-12-06T03:48:00",
            "vulnerabilities": [
                {"severity": "high", "type": "SQL Injection", "file": "Controllers/UserController.cs"},
                {"severity": "medium", "type": "XSS", "file": "Views/Home/Index.cshtml"},
                {"severity": "low", "type": "Missing HTTPS", "file": "Startup.cs"}
            ],
            "categories": {
                "injection": 5,
                "xss": 12,
                "configuration": 8
            }
        }
    
    @pytest.fixture
    def sample_tech_stack_data(self):
        """Sample data matching actual tech-stack.json structure."""
        return {
            "frontend": {
                "languages": ["JavaScript", "HTML", "CSS"],
                "frameworks": ["jQuery", "Bootstrap"]
            },
            "backend": {
                "languages": ["C#", "SQL"],
                "frameworks": ["ASP.NET MVC", "Entity Framework"]
            },
            "summary": {
                "total_technologies": 4,
                "current_count": 4,
                "outdated_count": 0,
                "deprecated_count": 0
            }
        }
    
    @pytest.fixture
    def sample_team_metrics_data(self):
        """Sample data matching actual team-metrics.json structure."""
        return {
            "contributors": [
                {"name": "Developer1", "commits": 523, "email": "dev1@example.com"},
                {"name": "Developer2", "commits": 412, "email": "dev2@example.com"}
            ],
            "summary": {
                "total_commits": 935,
                "total_contributors": 2,
                "active_contributors": 2,
                "last_commit_date": "2025-12-01"
            }
        }
    
    @pytest.fixture
    def sample_architecture_data(self):
        """Sample data matching actual architecture.json structure."""
        return {
            "components": [
                {"name": "Controllers", "type": "presentation", "file_count": 74},
                {"name": "Models", "type": "domain", "file_count": 120},
                {"name": "Services", "type": "business", "file_count": 45}
            ],
            "tiers": 6,
            "patterns": ["MVC", "Repository", "Dependency Injection"]
        }
    
    @pytest.fixture
    def sample_vendors_data(self):
        """Sample data matching actual vendors.json structure."""
        return {
            "external_vendors": [
                {"name": "Microsoft", "packages": ["EntityFramework", "AspNet"]},
                {"name": "jQuery", "packages": ["jquery"]}
            ],
            "code_dependencies": {
                "nuget": 25,
                "npm": 12
            }
        }
    
    @pytest.fixture
    def complete_collected_data(self, sample_code_organization_data, sample_security_data,
                                 sample_tech_stack_data, sample_team_metrics_data,
                                 sample_architecture_data, sample_vendors_data):
        """Complete collected data structure as returned by parallel_collector."""
        return {
            "code-organization.json": sample_code_organization_data,
            "security.json": sample_security_data,
            "tech-stack.json": sample_tech_stack_data,
            "team-metrics.json": sample_team_metrics_data,
            "architecture.json": sample_architecture_data,
            "vendors.json": sample_vendors_data
        }
    
    def test_health_metrics_with_complete_data(self, complete_collected_data):
        """Test health metrics calculation with complete, valid data."""
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        
        orchestrator = OnboardingOrchestrator(Path.cwd())
        health_data = orchestrator._calculate_health_metrics(complete_collected_data)
        
        # CRITICAL: No zeros allowed for existing data
        assert health_data["total_files"] == 10391, "Total files must match collected data"
        assert health_data["lines_of_code"] == 1246213, "Lines of code must match collected data"
        assert health_data["contributors"] == 2, "Contributors must match team metrics"
        assert health_data["languages"] > 0, "Languages count must be > 0"
        assert health_data["frameworks"] > 0, "Frameworks count must be > 0"
        assert health_data["security_score"] == 65, "Security score must match collected data"
        assert health_data["overall_health_score"] > 0, "Overall health score must be calculated"
        assert health_data["status"] in ["healthy", "warning", "critical"], "Status must be valid"
    
    def test_health_metrics_rejects_zero_total_files_when_data_exists(self, complete_collected_data):
        """Test that health metrics validation catches zero total_files when data clearly exists."""
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        
        orchestrator = OnboardingOrchestrator(Path.cwd())
        health_data = orchestrator._calculate_health_metrics(complete_collected_data)
        
        # If we have 10K+ files in source data, health_data CANNOT show 0
        source_files = complete_collected_data["code-organization.json"]["summary"]["total_files"]
        assert source_files > 0, "Source data has files"
        assert health_data["total_files"] == source_files, f"Health data shows 0 but source has {source_files} files - DATA INTEGRITY VIOLATION"
    
    def test_health_metrics_with_missing_summary(self, complete_collected_data):
        """Test health metrics gracefully handles missing summary section."""
        # Remove summary from code-organization
        del complete_collected_data["code-organization.json"]["summary"]
        
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        orchestrator = OnboardingOrchestrator(Path.cwd())
        health_data = orchestrator._calculate_health_metrics(complete_collected_data)
        
        # Should default to 0 but not crash
        assert health_data["total_files"] == 0
        assert health_data["lines_of_code"] == 0
        assert "overall_health_score" in health_data
    
    def test_health_metrics_with_empty_collectors(self):
        """Test health metrics with empty collector data."""
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        
        empty_data = {
            "code-organization.json": {},
            "security.json": {},
            "tech-stack.json": {},
            "team-metrics.json": {},
            "architecture.json": {},
            "vendors.json": {}
        }
        
        orchestrator = OnboardingOrchestrator(Path.cwd())
        health_data = orchestrator._calculate_health_metrics(empty_data)
        
        # All should be 0 for truly empty data
        assert health_data["total_files"] == 0
        assert health_data["lines_of_code"] == 0
        assert health_data["contributors"] == 0
        assert health_data["status"] == "critical"  # Empty project = critical
    
    def test_health_metrics_with_malformed_lists(self, complete_collected_data):
        """Test health metrics handles malformed list structures."""
        # Make contributors a string instead of list
        complete_collected_data["team-metrics.json"]["contributors"] = "not a list"
        
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        orchestrator = OnboardingOrchestrator(Path.cwd())
        health_data = orchestrator._calculate_health_metrics(complete_collected_data)
        
        # Should handle gracefully and default to 0
        assert health_data["contributors"] == 0
        assert "overall_health_score" in health_data


class TestDataValidation:
    """Test data validation and integrity checks."""
    
    def test_validate_collected_data_structure(self):
        """Test validation of collected data structure before processing."""
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        
        orchestrator = OnboardingOrchestrator(Path.cwd())
        
        # Valid structure
        valid_data = {
            "code-organization.json": {"summary": {"total_files": 100}},
            "security.json": {"overall_score": 50},
            "tech-stack.json": {"summary": {}},
            "team-metrics.json": {"contributors": []},
            "architecture.json": {"components": []},
            "vendors.json": {"external_vendors": []}
        }
        
        # This should exist and return True
        assert hasattr(orchestrator, '_validate_collected_data'), "Validation method must exist"
        result = orchestrator._validate_collected_data(valid_data)
        assert result is True, "Valid data should pass validation"
    
    def test_validate_rejects_missing_collectors(self):
        """Test validation rejects data with missing collectors."""
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        
        orchestrator = OnboardingOrchestrator(Path.cwd())
        
        # Missing security.json
        incomplete_data = {
            "code-organization.json": {"summary": {"total_files": 100}},
            "tech-stack.json": {"summary": {}}
        }
        
        result = orchestrator._validate_collected_data(incomplete_data)
        assert result is False, "Incomplete data should fail validation"
    
    def test_validate_checks_data_consistency(self):
        """Test validation checks data consistency (e.g., files count vs LOC)."""
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        
        orchestrator = OnboardingOrchestrator(Path.cwd())
        
        # Inconsistent: 10K files but 0 lines of code (impossible)
        inconsistent_data = {
            "code-organization.json": {
                "summary": {
                    "total_files": 10000,
                    "total_loc": 0  # Impossible if files exist
                }
            },
            "security.json": {"overall_score": 50},
            "tech-stack.json": {"summary": {}},
            "team-metrics.json": {"contributors": []},
            "architecture.json": {"components": []},
            "vendors.json": {"external_vendors": []}
        }
        
        warnings = orchestrator._check_data_consistency(inconsistent_data)
        assert len(warnings) > 0, "Should detect inconsistency"
        assert any("lines of code" in w.lower() for w in warnings), "Should warn about LOC inconsistency"


class TestHealthMetricsConfirmation:
    """Test confirmation steps before writing health-data.json."""
    
    def test_health_metrics_require_confirmation_before_write(self):
        """Test that health metrics are validated before writing to file."""
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        
        orchestrator = OnboardingOrchestrator(Path.cwd())
        
        # Health data with suspicious zeros
        suspicious_health_data = {
            "total_files": 0,
            "lines_of_code": 0,
            "contributors": 0,
            "overall_health_score": 0
        }
        
        # Source data that clearly has content
        source_data = {
            "code-organization.json": {
                "summary": {"total_files": 10000, "total_loc": 500000}
            }
        }
        
        # Should detect mismatch
        assert hasattr(orchestrator, '_confirm_health_data_valid'), "Confirmation method must exist"
        is_valid, issues = orchestrator._confirm_health_data_valid(suspicious_health_data, source_data)
        assert is_valid is False, "Should reject health data with zeros when source has data"
        assert len(issues) > 0, "Should list specific issues"
    
    def test_confirmation_passes_for_valid_data(self):
        """Test confirmation passes for valid, consistent health data."""
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        
        orchestrator = OnboardingOrchestrator(Path.cwd())
        
        health_data = {
            "total_files": 10000,
            "lines_of_code": 500000,
            "contributors": 5,
            "overall_health_score": 75
        }
        
        source_data = {
            "code-organization.json": {
                "summary": {"total_files": 10000, "total_loc": 500000}
            }
        }
        
        is_valid, issues = orchestrator._confirm_health_data_valid(health_data, source_data)
        assert is_valid is True, "Should accept valid health data"
        assert len(issues) == 0, "Should have no issues"


class TestParallelCollectorOrchestration:
    """Test parallel collector orchestration and error handling."""
    
    def test_parallel_collector_returns_correct_structure(self):
        """Test parallel collector returns data in expected format."""
        import sys
        sys.path.insert(0, str(Path.cwd() / "src"))
        from dashboard.data.parallel_collector import ParallelCollectorOrchestrator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            orchestrator = ParallelCollectorOrchestrator(project_path)
            collected_data, execution_time = orchestrator.collect_all_parallel()
            
            # Should return dict with .json filename keys
            assert isinstance(collected_data, dict), "Should return dict"
            assert "code-organization.json" in collected_data, "Should have code-organization data"
            assert "security.json" in collected_data, "Should have security data"
            assert execution_time > 0, "Should track execution time"
    
    def test_parallel_collector_handles_failed_collector(self):
        """Test parallel collector handles individual collector failures."""
        import sys
        sys.path.insert(0, str(Path.cwd() / "src"))
        from dashboard.data.parallel_collector import ParallelCollectorOrchestrator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            orchestrator = ParallelCollectorOrchestrator(project_path)
            
            # Mock one collector to fail
            with patch.object(orchestrator.collectors["security"], "collect", side_effect=Exception("Test failure")):
                collected_data, execution_time = orchestrator.collect_all_parallel()
            
            # Should still return data (minimal structure for failed collector)
            assert "security.json" in collected_data, "Should have fallback data for failed collector"
            assert collected_data["security.json"]["overall_score"] == 0, "Failed collector should return minimal structure"


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_health_calculation_with_none_values(self):
        """Test health calculation handles None values in data."""
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        
        data_with_nones = {
            "code-organization.json": {
                "summary": {
                    "total_files": None,
                    "total_loc": None,
                    "maintainability_score": None
                }
            },
            "security.json": {},
            "tech-stack.json": {},
            "team-metrics.json": {},
            "architecture.json": {},
            "vendors.json": {}
        }
        
        orchestrator = OnboardingOrchestrator(Path.cwd())
        health_data = orchestrator._calculate_health_metrics(data_with_nones)
        
        # Should convert None to 0
        assert health_data["total_files"] == 0
        assert health_data["lines_of_code"] == 0
    
    def test_health_calculation_with_negative_values(self):
        """Test health calculation rejects negative values."""
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        
        data_with_negatives = {
            "code-organization.json": {
                "summary": {
                    "total_files": -100,  # Invalid
                    "total_loc": -5000,   # Invalid
                    "maintainability_score": -50  # Invalid
                }
            },
            "security.json": {"overall_score": -10},  # Invalid
            "tech-stack.json": {},
            "team-metrics.json": {},
            "architecture.json": {},
            "vendors.json": {}
        }
        
        orchestrator = OnboardingOrchestrator(Path.cwd())
        health_data = orchestrator._calculate_health_metrics(data_with_negatives)
        
        # Should clamp to 0 or raise validation error
        assert health_data["total_files"] >= 0, "Negative values should be clamped/rejected"
        assert health_data["lines_of_code"] >= 0, "Negative values should be clamped/rejected"
    
    def test_dashboard_generation_rollback_on_validation_failure(self):
        """Test dashboard generation rolls back if validation fails."""
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            orchestrator = OnboardingOrchestrator(Path.cwd())
            
            # This should fail validation and not write corrupt data
            # Implementation should detect and prevent writing zeros when source has data
            # Test will verify rollback mechanism exists


class TestRealWorldScenarios:
    """Test real-world scenarios from Chat001.md."""
    
    def test_luum_fresh_scenario_actual_data_structure(self):
        """Test with actual luum-fresh data structure that caused the bug."""
        # This is the ACTUAL data structure that caused zeros in health-data.json
        actual_code_org_data = {
            "summary": {
                "total_files": 10391,
                "total_loc": 1246213,
                "maintainability_score": 77,
                "high_complexity_files": 480,
                "avg_complexity": 3.2,
                "technical_debt_hours": 523.5
            },
            "hotspots": [
                {"file": "Controllers/HomeController.cs", "complexity": 45}
            ],
            "heatmap": {},
            "file_complexity": {},
            "module_structure": {}
        }
        
        collected_data = {
            "code-organization.json": actual_code_org_data,
            "security.json": {"overall_score": 0, "vulnerabilities": []},
            "tech-stack.json": {"frontend": {}, "backend": {}, "summary": {"total_technologies": 4}},
            "team-metrics.json": {"contributors": [], "summary": {"total_commits": 0}},
            "architecture.json": {"components": []},
            "vendors.json": {"external_vendors": []}
        }
        
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        orchestrator = OnboardingOrchestrator(Path.cwd())
        health_data = orchestrator._calculate_health_metrics(collected_data)
        
        # THIS IS THE CRITICAL TEST - must match source data
        assert health_data["total_files"] == 10391, f"BUG REPRODUCED: Expected 10391 files, got {health_data['total_files']}"
        assert health_data["lines_of_code"] == 1246213, f"BUG REPRODUCED: Expected 1246213 LOC, got {health_data['lines_of_code']}"
    
    def test_list_object_has_no_get_attribute_error(self):
        """Test the specific error from logs: 'list' object has no attribute 'get'."""
        # This error occurred because code tried .get() on a list instead of dict
        
        malformed_data = {
            "code-organization.json": [  # This is a LIST, not a DICT!
                {"file": "test.cs", "loc": 100}
            ],
            "security.json": {},
            "tech-stack.json": {},
            "team-metrics.json": {},
            "architecture.json": {},
            "vendors.json": {}
        }
        
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        orchestrator = OnboardingOrchestrator(Path.cwd())
        
        # Should not crash, should handle gracefully
        try:
            health_data = orchestrator._calculate_health_metrics(malformed_data)
            # Should detect wrong structure and use defaults
            assert health_data["total_files"] == 0, "Should handle malformed structure"
        except AttributeError as e:
            pytest.fail(f"Should not raise AttributeError, got: {e}")


class TestDataIntegrityForLeadership:
    """CRITICAL: Tests ensuring data accuracy for leadership decisions."""
    
    def test_health_data_matches_source_data_exactly(self):
        """CRITICAL: Health data must exactly match source data - no information loss."""
        source_data = {
            "code-organization.json": {
                "summary": {
                    "total_files": 15234,
                    "total_loc": 2456789,
                    "maintainability_score": 82
                }
            },
            "security.json": {
                "overall_score": 72,
                "vulnerabilities": [{"severity": "high"}] * 23  # 23 vulnerabilities
            },
            "tech-stack.json": {
                "frontend": {"languages": ["JavaScript", "TypeScript"]},
                "backend": {"languages": ["C#"]},
                "summary": {"total_technologies": 5}
            },
            "team-metrics.json": {
                "contributors": [{"name": f"Dev{i}"} for i in range(12)],  # 12 contributors
                "summary": {"total_commits": 5678}
            },
            "architecture.json": {"components": [{}] * 45},  # 45 components
            "vendors.json": {"external_vendors": [{}] * 8}  # 8 vendors
        }
        
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        orchestrator = OnboardingOrchestrator(Path.cwd())
        health_data = orchestrator._calculate_health_metrics(source_data)
        
        # ZERO TOLERANCE for data loss
        assert health_data["total_files"] == 15234, "File count MUST match source"
        assert health_data["lines_of_code"] == 2456789, "LOC MUST match source"
        assert health_data["contributors"] == 12, "Contributors MUST match source"
        assert health_data["security_score"] == 72, "Security score MUST match source"
        assert health_data["security_issues"] == 23, "Vulnerability count MUST match source"
        assert health_data["architecture_components"] == 45, "Component count MUST match source"
        assert health_data["external_vendors"] == 8, "Vendor count MUST match source"
    
    def test_prevent_writing_zeros_when_data_exists(self):
        """CRITICAL: System must refuse to write zeros when source data clearly exists."""
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        
        orchestrator = OnboardingOrchestrator(Path.cwd())
        
        # Health data calculation that resulted in zeros (BUG)
        health_data_with_zeros = {
            "total_files": 0,
            "lines_of_code": 0,
            "contributors": 0
        }
        
        # But source data has clear values
        source_data = {
            "code-organization.json": {
                "summary": {"total_files": 10391, "total_loc": 1246213}
            }
        }
        
        # System MUST detect this mismatch and refuse to write
        is_valid, issues = orchestrator._confirm_health_data_valid(health_data_with_zeros, source_data)
        assert is_valid is False, "MUST reject health data with zeros when source has data"
        assert len(issues) > 0, "MUST report specific data integrity violations"
        assert any("10391" in str(issue) for issue in issues), "MUST mention actual file count from source"
    
    def test_data_quality_gates_before_leadership_reporting(self):
        """CRITICAL: Data must pass quality gates before being used for leadership reports."""
        from src.operations.onboarding_orchestrator import OnboardingOrchestrator
        
        orchestrator = OnboardingOrchestrator(Path.cwd())
        
        # Define acceptable ranges for leadership data
        health_data = {
            "total_files": 10000,
            "lines_of_code": 500000,
            "overall_health_score": 75,
            "security_score": 65,
            "contributors": 5
        }
        
        # Quality gates
        assert hasattr(orchestrator, '_validate_for_leadership_reporting'), "Quality gate method must exist"
        is_ready, warnings = orchestrator._validate_for_leadership_reporting(health_data)
        
        assert is_ready is True, "Valid data should pass quality gates"
        
        # Test with suspicious data
        suspicious_data = {
            "total_files": 5,  # Too few for a real project
            "lines_of_code": 100,  # Way too low
            "overall_health_score": 0,  # Suspicious
            "security_score": 0,
            "contributors": 0
        }
        
        is_ready, warnings = orchestrator._validate_for_leadership_reporting(suspicious_data)
        assert is_ready is False, "Suspicious data should fail quality gates"
        assert len(warnings) > 0, "Should explain why data failed quality gates"
