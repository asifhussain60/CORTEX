"""
CORTEX Phase 3.3 - Scope Validator Tests (TDD RED Phase)

Purpose: Validate scope boundaries and identify missing elements for clarification
Target: Confidence scoring + validation rules + gap detection
Status: RED - Tests should fail until implementation complete

Test Coverage:
- Confidence threshold validation (<0.70 triggers clarification)
- Missing element detection (tables, files, dependencies)
- Scope completeness checks (DoR requirements satisfied)
- Edge cases (empty scope, over-limit scope, enterprise monolith)
"""

import pytest
from dataclasses import dataclass
from typing import List

# Dependencies
from src.agents.estimation.scope_inference_engine import (
    ScopeEntities,
    ScopeBoundary
)

# Module under test (doesn't exist yet - TDD RED)
from src.agents.estimation.scope_validator import (
    ScopeValidator,
    ValidationResult,
    ValidationRule
)


class TestScopeValidation:
    """Test scope boundary validation logic"""
    
    def test_high_confidence_scope_passes_validation(self):
        """Scope with >70% confidence should pass validation"""
        validator = ScopeValidator()
        boundary = ScopeBoundary(
            table_count=5,
            file_count=8,
            service_count=2,
            dependency_depth=1,
            estimated_complexity=45.0,
            confidence=0.75,
            gaps=[]
        )
        
        result = validator.validate_scope(boundary)
        
        assert result.is_valid is True
        assert result.requires_clarification is False
        assert len(result.validation_errors) == 0
    
    def test_low_confidence_scope_fails_validation(self):
        """Scope with <70% confidence should require clarification"""
        validator = ScopeValidator()
        boundary = ScopeBoundary(
            table_count=1,
            file_count=0,
            service_count=0,
            dependency_depth=1,
            estimated_complexity=5.0,
            confidence=0.25,
            gaps=["No code files mentioned"]
        )
        
        result = validator.validate_scope(boundary)
        
        assert result.is_valid is False
        assert result.requires_clarification is True
        assert len(result.validation_errors) > 0
    
    def test_validation_identifies_missing_tables(self):
        """Should detect when no tables are mentioned"""
        validator = ScopeValidator()
        boundary = ScopeBoundary(
            table_count=0,
            file_count=3,
            service_count=1,
            dependency_depth=1,
            estimated_complexity=15.0,
            confidence=0.45,
            gaps=["No database tables mentioned"]
        )
        
        result = validator.validate_scope(boundary)
        
        assert "tables" in result.missing_elements
        assert any("table" in err.lower() for err in result.validation_errors)
    
    def test_validation_identifies_missing_files(self):
        """Should detect when no code files are mentioned"""
        validator = ScopeValidator()
        boundary = ScopeBoundary(
            table_count=2,
            file_count=0,
            service_count=0,
            dependency_depth=1,
            estimated_complexity=10.0,
            confidence=0.35,
            gaps=["No code files mentioned"]
        )
        
        result = validator.validate_scope(boundary)
        
        assert "files" in result.missing_elements
        assert any("file" in err.lower() or "code" in err.lower() for err in result.validation_errors)
    
    def test_validation_passes_without_external_services(self):
        """Should allow scope with no external services (not all features need them)"""
        validator = ScopeValidator()
        boundary = ScopeBoundary(
            table_count=3,
            file_count=5,
            service_count=0,
            dependency_depth=1,
            estimated_complexity=30.0,
            confidence=0.72,
            gaps=[]
        )
        
        result = validator.validate_scope(boundary)
        
        assert result.is_valid is True
        assert "services" not in result.missing_elements


class TestValidationRules:
    """Test validation rule engine"""
    
    def test_table_count_rule(self):
        """Should validate table count within reasonable bounds"""
        validator = ScopeValidator()
        
        # No tables - warning
        boundary_no_tables = ScopeBoundary(
            table_count=0, file_count=5, service_count=0,
            dependency_depth=1, estimated_complexity=20.0,
            confidence=0.60, gaps=[]
        )
        result = validator.validate_scope(boundary_no_tables)
        assert len(result.warnings) > 0
        
        # Reasonable tables - pass
        boundary_reasonable = ScopeBoundary(
            table_count=8, file_count=12, service_count=1,
            dependency_depth=1, estimated_complexity=40.0,
            confidence=0.75, gaps=[]
        )
        result = validator.validate_scope(boundary_reasonable)
        assert len(result.warnings) == 0
        
        # Over limit - error
        boundary_over_limit = ScopeBoundary(
            table_count=60, file_count=150, service_count=5,
            dependency_depth=3, estimated_complexity=95.0,
            confidence=0.80, gaps=["Scope exceeds limits"]
        )
        result = validator.validate_scope(boundary_over_limit)
        assert len(result.validation_errors) > 0
    
    def test_complexity_scoring_rule(self):
        """Should flag high complexity scope for review"""
        validator = ScopeValidator()
        
        # High complexity (>70) should trigger warning
        boundary = ScopeBoundary(
            table_count=30,
            file_count=60,
            service_count=4,
            dependency_depth=2,
            estimated_complexity=85.0,
            confidence=0.78,
            gaps=[]
        )
        
        result = validator.validate_scope(boundary)
        
        assert len(result.warnings) > 0
        assert any("complex" in w.lower() for w in result.warnings)


class TestClarificationQuestions:
    """Test clarification question generation"""
    
    def test_generates_questions_for_missing_tables(self):
        """Should ask about database tables if none mentioned"""
        validator = ScopeValidator()
        boundary = ScopeBoundary(
            table_count=0, file_count=3, service_count=1,
            dependency_depth=1, estimated_complexity=15.0,
            confidence=0.45, gaps=["No database tables mentioned"]
        )
        
        result = validator.validate_scope(boundary)
        questions = validator.generate_clarification_questions(result, boundary)
        
        assert len(questions) > 0
        assert any("table" in q.lower() or "database" in q.lower() for q in questions)
    
    def test_generates_questions_for_missing_files(self):
        """Should ask about code files if none mentioned"""
        validator = ScopeValidator()
        boundary = ScopeBoundary(
            table_count=2, file_count=0, service_count=0,
            dependency_depth=1, estimated_complexity=10.0,
            confidence=0.35, gaps=["No code files mentioned"]
        )
        
        result = validator.validate_scope(boundary)
        questions = validator.generate_clarification_questions(result, boundary)
        
        assert len(questions) > 0
        assert any("file" in q.lower() or "code" in q.lower() or "class" in q.lower() for q in questions)
    
    def test_no_questions_for_valid_scope(self):
        """Should not generate questions for high-confidence valid scope"""
        validator = ScopeValidator()
        boundary = ScopeBoundary(
            table_count=5, file_count=8, service_count=2,
            dependency_depth=1, estimated_complexity=45.0,
            confidence=0.75, gaps=[]
        )
        
        result = validator.validate_scope(boundary)
        questions = validator.generate_clarification_questions(result, boundary)
        
        assert len(questions) == 0


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_handles_zero_confidence_scope(self):
        """Should handle scope with zero confidence gracefully"""
        validator = ScopeValidator()
        boundary = ScopeBoundary(
            table_count=0, file_count=0, service_count=0,
            dependency_depth=0, estimated_complexity=0.0,
            confidence=0.0, gaps=["Empty scope"]
        )
        
        result = validator.validate_scope(boundary)
        
        assert result.is_valid is False
        assert result.requires_clarification is True
        assert len(result.validation_errors) > 0
    
    def test_handles_enterprise_monolith_scope(self):
        """Should flag enterprise monolith scope (>50 tables, >100 files)"""
        validator = ScopeValidator()
        boundary = ScopeBoundary(
            table_count=50,
            file_count=100,
            service_count=3,
            dependency_depth=2,
            estimated_complexity=100.0,
            confidence=0.85,
            gaps=[]
        )
        
        result = validator.validate_scope(boundary)
        
        # Should pass but with warnings
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any("large" in w.lower() or "complex" in w.lower() for w in result.warnings)
    
    def test_handles_gaps_from_inference_engine(self):
        """Should use gaps from inference engine in validation"""
        validator = ScopeValidator()
        boundary = ScopeBoundary(
            table_count=2, file_count=1, service_count=0,
            dependency_depth=1, estimated_complexity=12.0,
            confidence=0.55,
            gaps=[
                "No external dependencies mentioned",
                "Only 2 tables identified - scope may be incomplete"
            ]
        )
        
        result = validator.validate_scope(boundary)
        questions = validator.generate_clarification_questions(result, boundary)
        
        # Should incorporate gaps into questions
        assert len(questions) > 0
