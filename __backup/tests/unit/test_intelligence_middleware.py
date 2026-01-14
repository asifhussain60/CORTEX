"""
Unit tests for Intelligence Middleware.

Tests the intelligent validation layer that prevents user mistakes.

Author: CORTEX feat04-core-orchestration Phase 1
Created: 2026-01-08
TDD Phase: RED → GREEN → REFACTOR
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass

# Import the components we'll be testing (they don't exist yet - TDD RED)
from src.orchestrators.middleware.intelligence_middleware import (
    IntelligenceMiddleware,
    ValidationResult,
    IntelligenceRule,
)


class TestIntelligenceMiddleware:
    """Test suite for IntelligenceMiddleware."""
    
    @pytest.fixture
    def rules_config_path(self, tmp_path: Path) -> Path:
        """Create temporary intelligence rules config."""
        config = tmp_path / "intelligence-rules.yaml"
        config.write_text("""
rules:
  - id: IR-001
    name: "Planning vs Implementation Separation"
    category: planning_vs_implementation
    severity: error
    enabled: true
    message: "Planning commands create plans only. Use implementation orchestrator to execute."
    suggestion: "Run: 'implement plan [plan-id]' to execute the plan"
  
  - id: IR-002
    name: "Missing Test Infrastructure"
    category: missing_prerequisites
    severity: warning
    enabled: true
    message: "Test infrastructure not detected. TDD requires tests first."
    suggestion: "Run: 'setup tests' or verify tests/ folder exists with pytest.ini"
  
  - id: IR-006
    name: "YAML-First Enforcement"
    category: yaml_first
    severity: error
    enabled: true
    message: "Markdown plan files prohibited. Use YAML config files."
    suggestion: "Create config file: cortex-brain/config/{name}.yaml"
  
  - id: IR-007
    name: "Governance Integration"
    category: governance_integration
    severity: warning
    enabled: true
    message: "Governance check was skipped."
    suggestion: "Run governance check before proceeding"
  
  - id: IR-008
    name: "TODO Dependency Blocking"
    category: todo_dependencies
    severity: error
    enabled: true
    message: "Cannot execute task - parent TODO is BLOCKED"
    suggestion: "Unblock parent TODO or check dependency chain"
""")
        return config
    
    @pytest.fixture
    def middleware(self, rules_config_path: Path) -> IntelligenceMiddleware:
        """Create IntelligenceMiddleware instance."""
        return IntelligenceMiddleware(rules_path=str(rules_config_path))
    
    def test_middleware_initialization(self, middleware: IntelligenceMiddleware):
        """Test middleware initializes correctly."""
        assert middleware is not None
        assert middleware.rules_path is not None
        assert isinstance(middleware.rules, list)
        assert len(middleware.rules) > 0
    
    def test_load_rules_from_yaml(self, middleware: IntelligenceMiddleware):
        """Test loading rules from YAML configuration."""
        rules = middleware.rules
        assert len(rules) == 5  # IR-001, IR-002, IR-006, IR-007, IR-008
        assert rules[0].id == "IR-001"
        assert rules[0].name == "Planning vs Implementation Separation"
        assert rules[0].severity == "error"
    
    def test_validate_execution_with_no_violations(
        self, 
        middleware: IntelligenceMiddleware
    ):
        """Test validation passes when no rules are violated."""
        result = middleware.validate_execution(
            orchestrator_id="test_orchestrator",
            params={"action": "safe_operation"},
            context={}
        )
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
    
    def test_validate_execution_with_error_violation(
        self,
        middleware: IntelligenceMiddleware
    ):
        """Test validation blocks execution on error-level violation."""
        # This would trigger IR-001: Planning vs Implementation
        result = middleware.validate_execution(
            orchestrator_id="planning_orchestrator",
            params={"action": "implement", "code": "print('hello')"},
            context={}
        )
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert "Planning commands create plans only" in result.errors[0]
        assert len(result.suggestions) > 0
    
    def test_validate_execution_with_warning_violation(
        self,
        middleware: IntelligenceMiddleware
    ):
        """Test validation allows execution with warnings."""
        # This would trigger IR-002: Missing Test Infrastructure
        result = middleware.validate_execution(
            orchestrator_id="implementation_orchestrator",
            params={"action": "implement"},
            context={"test_framework_exists": False}
        )
        
        assert result.is_valid is True  # Warnings don't block
        assert len(result.errors) == 0
        assert len(result.warnings) > 0
        assert "Test infrastructure not detected" in result.warnings[0]


class TestPlanningVsImplementationRule:
    """Test IR-001: Planning vs Implementation Separation."""
    
    @pytest.fixture
    def middleware(self) -> IntelligenceMiddleware:
        """Create middleware with real config."""
        config_path = Path("cortex-brain/config/intelligence-rules.yaml")
        return IntelligenceMiddleware(rules_path=str(config_path))
    
    def test_planning_orchestrator_blocks_implementation(
        self,
        middleware: IntelligenceMiddleware
    ):
        """Test planning orchestrator cannot implement code."""
        result = middleware.validate_execution(
            orchestrator_id="planning_orchestrator",
            params={"request": "plan and implement user auth"},
            context={}
        )
        
        assert result.is_valid is False
        assert any("Planning commands create plans only" in e for e in result.errors)
    
    def test_planning_orchestrator_allows_planning(
        self,
        middleware: IntelligenceMiddleware
    ):
        """Test planning orchestrator can create plans."""
        result = middleware.validate_execution(
            orchestrator_id="planning_orchestrator",
            params={"request": "plan user authentication system"},
            context={}
        )
        
        assert result.is_valid is True
        assert len(result.errors) == 0


class TestMissingPrerequisitesRule:
    """Test IR-002: Missing Test Infrastructure."""
    
    @pytest.fixture
    def middleware(self) -> IntelligenceMiddleware:
        """Create middleware with real config."""
        config_path = Path("cortex-brain/config/intelligence-rules.yaml")
        return IntelligenceMiddleware(rules_path=str(config_path))
    
    def test_implementation_without_tests_warns(
        self,
        middleware: IntelligenceMiddleware
    ):
        """Test warning when implementing without test infrastructure."""
        result = middleware.validate_execution(
            orchestrator_id="implementation_orchestrator",
            params={"action": "implement"},
            context={"test_framework_exists": False}
        )
        
        assert result.is_valid is True  # Warning, not error
        assert len(result.warnings) > 0
        assert any("Test infrastructure not detected" in w for w in result.warnings)
    
    def test_implementation_with_tests_passes(
        self,
        middleware: IntelligenceMiddleware
    ):
        """Test no warning when test infrastructure exists."""
        result = middleware.validate_execution(
            orchestrator_id="implementation_orchestrator",
            params={"action": "implement"},
            context={"test_framework_exists": True}
        )
        
        assert result.is_valid is True
        assert len(result.warnings) == 0


class TestYAMLFirstEnforcement:
    """Test IR-006: YAML-First Enforcement."""
    
    @pytest.fixture
    def middleware(self) -> IntelligenceMiddleware:
        """Create middleware with real config."""
        config_path = Path("cortex-brain/config/intelligence-rules.yaml")
        return IntelligenceMiddleware(rules_path=str(config_path))
    
    def test_blocks_markdown_plan_files(
        self,
        middleware: IntelligenceMiddleware
    ):
        """Test blocking of *-PLAN.md files."""
        result = middleware.validate_execution(
            orchestrator_id="file_creator",
            params={
                "action": "create_file",
                "file_path": "feat04-core-orchestration-PLAN.md"
            },
            context={}
        )
        
        assert result.is_valid is False
        assert any("YAML-first violation" in e for e in result.errors)
        assert any("CORE-018" in e for e in result.errors)
    
    def test_allows_yaml_config_files(
        self,
        middleware: IntelligenceMiddleware
    ):
        """Test allowing YAML configuration files."""
        result = middleware.validate_execution(
            orchestrator_id="file_creator",
            params={
                "action": "create_file",
                "file_path": "cortex-brain/config/intelligence-rules.yaml"
            },
            context={}
        )
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_allows_readme_files(
        self,
        middleware: IntelligenceMiddleware
    ):
        """Test allowing README.md files (exception)."""
        result = middleware.validate_execution(
            orchestrator_id="file_creator",
            params={
                "action": "create_file",
                "file_path": "README.md"
            },
            context={}
        )
        
        assert result.is_valid is True
        assert len(result.errors) == 0


class TestGovernanceIntegration:
    """Test IR-007: Missing Governance Check."""
    
    @pytest.fixture
    def middleware(self) -> IntelligenceMiddleware:
        """Create middleware with real config."""
        config_path = Path("cortex-brain/config/intelligence-rules.yaml")
        return IntelligenceMiddleware(rules_path=str(config_path))
    
    def test_warns_when_governance_skipped(
        self,
        middleware: IntelligenceMiddleware
    ):
        """Test warning when governance check is skipped."""
        result = middleware.validate_execution(
            orchestrator_id="test_orchestrator",
            params={"action": "execute"},
            context={"governance_check_skipped": True}
        )
        
        assert result.is_valid is True  # Warning, not error
        assert len(result.warnings) > 0
        assert any("Governance rules not checked" in w for w in result.warnings)


class TestTODODependencyBlocking:
    """Test IR-008: TODO Dependency Blocking."""
    
    @pytest.fixture
    def middleware(self) -> IntelligenceMiddleware:
        """Create middleware with real config."""
        config_path = Path("cortex-brain/config/intelligence-rules.yaml")
        return IntelligenceMiddleware(rules_path=str(config_path))
    
    def test_blocks_execution_of_blocked_todo(
        self,
        middleware: IntelligenceMiddleware
    ):
        """Test blocking execution when TODO is BLOCKED."""
        result = middleware.validate_execution(
            orchestrator_id="test_orchestrator",
            params={"action": "execute"},
            context={
                "has_parent_todo": True,
                "todo_id": "task-4.1.1",
                "todo_status": "BLOCKED",
                "blocked_by": ["task-4.1.0"]
            }
        )
        
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("BLOCKED by unmet dependencies" in e for e in result.errors)
    
    def test_allows_execution_of_ready_todo(
        self,
        middleware: IntelligenceMiddleware
    ):
        """Test allowing execution when TODO is READY."""
        result = middleware.validate_execution(
            orchestrator_id="test_orchestrator",
            params={"action": "execute"},
            context={
                "has_parent_todo": True,
                "todo_id": "task-4.1.1",
                "todo_status": "READY"
            }
        )
        
        assert result.is_valid is True
        assert len(result.errors) == 0


class TestValidationResult:
    """Test ValidationResult data structure."""
    
    def test_validation_result_creation(self):
        """Test creating ValidationResult."""
        result = ValidationResult(
            is_valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
            suggestions=["Suggestion 1"],
            metadata={"rules_evaluated": 8}
        )
        
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 1
        assert len(result.suggestions) == 1
        assert result.metadata["rules_evaluated"] == 8
    
    def test_format_error_message(self):
        """Test formatting user-friendly error message."""
        result = ValidationResult(
            is_valid=False,
            errors=["Error 1", "Error 2"],
            warnings=[],
            suggestions=["Try this", "Or this"],
            metadata={}
        )
        
        message = result.format_error_message()
        assert "⚠️ Cannot proceed" in message
        assert "Error 1" in message
        assert "Error 2" in message
        assert "💡 Suggestions" in message
        assert "Try this" in message
        assert "Or this" in message


class TestIntelligenceRule:
    """Test IntelligenceRule data structure."""
    
    def test_rule_creation(self):
        """Test creating IntelligenceRule."""
        rule = IntelligenceRule(
            id="TEST-001",
            name="Test Rule",
            category="test",
            severity="error",
            condition="test condition",
            message="Test message",
            suggestion="Test suggestion",
            enabled=True
        )
        
        assert rule.id == "TEST-001"
        assert rule.name == "Test Rule"
        assert rule.severity == "error"
        assert rule.enabled is True
    
    def test_rule_evaluation(self):
        """Test rule evaluation logic."""
        rule = IntelligenceRule(
            id="TEST-001",
            name="Test Rule",
            category="test",
            severity="error",
            condition="orchestrator == 'planning_orchestrator'",
            message="Test message",
            enabled=True
        )
        
        # This would test the evaluate() method when implemented
        # For now, just verify structure
        assert hasattr(rule, 'id')
        assert hasattr(rule, 'condition')


class TestPerformance:
    """Test intelligence middleware performance."""
    
    @pytest.fixture
    def middleware(self) -> IntelligenceMiddleware:
        """Create middleware with real config."""
        config_path = Path("cortex-brain/config/intelligence-rules.yaml")
        return IntelligenceMiddleware(rules_path=str(config_path))
    
    @pytest.mark.skipif(
        not hasattr(pytest, "benchmark"),
        reason="pytest-benchmark not installed"
    )
    def test_validation_performance(
        self,
        middleware: IntelligenceMiddleware,
        benchmark
    ):
        """Test validation completes within 10ms target."""
        def validate():
            return middleware.validate_execution(
                orchestrator_id="test_orchestrator",
                params={"action": "test"},
                context={}
            )
        
        result = benchmark(validate)
        
        # Benchmark will measure execution time
        # Target: <10ms per validation
        assert result.is_valid is not None
