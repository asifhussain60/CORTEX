"""
TDD Tests for Business Language Generator.

Tests AST-to-plain-English conversion for Repository Overview tab:
- Capability extraction from code structure
- Tech stack detection from imports
- Architecture pattern recognition
- Business language template mapping
- Confidence scoring

Authority: CORE-008 (TDD First)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-001
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cortex.visualization.business_language_generator import (
    BusinessLanguageGenerator,
    BusinessDescription,
    CapabilitySet,
    TechStackInfo,
    ArchitecturePattern,
    get_business_description,
)


class TestBusinessDescription:
    """Test BusinessDescription dataclass."""
    
    def test_create_business_description(self):
        """Test creating business description with all fields."""
        desc = BusinessDescription(
            summary="A Flask-based REST API for user management",
            capabilities=["User authentication", "Database access", "Email notifications"],
            tech_stack=["Python", "Flask", "SQLAlchemy", "PostgreSQL"],
            architecture_pattern="MVC (Model-View-Controller)",
            confidence_score=0.85,
            details="This application provides user registration, login, and profile management.",
        )
        
        assert "Flask" in desc.summary
        assert len(desc.capabilities) == 3
        assert "Python" in desc.tech_stack
        assert desc.architecture_pattern == "MVC (Model-View-Controller)"
        assert desc.confidence_score == 0.85


class TestCapabilitySet:
    """Test CapabilitySet detection."""
    
    def test_detect_capabilities_from_function_names(self):
        """Test extracting capabilities from function names."""
        functions = ["create_user", "authenticate_user", "send_email", "validate_token"]
        
        capabilities = CapabilitySet.detect_capabilities(functions=functions)
        
        assert "User creation" in capabilities or "Create user" in capabilities
        assert any("authentication" in cap.lower() for cap in capabilities)
        assert any("email" in cap.lower() for cap in capabilities)
    
    def test_detect_capabilities_from_class_names(self):
        """Test extracting capabilities from class names."""
        classes = ["UserController", "AuthService", "EmailNotifier", "PaymentProcessor"]
        
        capabilities = CapabilitySet.detect_capabilities(classes=classes)
        
        assert any("user" in cap.lower() for cap in capabilities)
        assert any("auth" in cap.lower() for cap in capabilities)
        assert any("email" in cap.lower() or "notification" in cap.lower() for cap in capabilities)
        assert any("payment" in cap.lower() for cap in capabilities)


class TestTechStackInfo:
    """Test TechStackInfo detection."""
    
    def test_detect_python_web_frameworks(self):
        """Test detecting web frameworks from imports."""
        imports = ["flask", "sqlalchemy", "marshmallow", "redis"]
        
        tech_stack = TechStackInfo.detect_tech_stack(imports)
        
        assert "Flask" in tech_stack or "Python web framework" in " ".join(tech_stack)
        assert any("database" in tech.lower() or "sqlalchemy" in tech.lower() for tech in tech_stack)
    
    def test_detect_data_science_stack(self):
        """Test detecting data science libraries."""
        imports = ["pandas", "numpy", "scikit-learn", "matplotlib"]
        
        tech_stack = TechStackInfo.detect_tech_stack(imports)
        
        assert any("pandas" in tech.lower() or "data analysis" in tech.lower() for tech in tech_stack)
        assert any("numpy" in tech.lower() or "numerical" in tech.lower() for tech in tech_stack)
        assert any("machine learning" in tech.lower() or "scikit" in tech.lower() for tech in tech_stack)
    
    def test_detect_async_frameworks(self):
        """Test detecting async frameworks."""
        imports = ["asyncio", "aiohttp", "uvloop"]
        
        tech_stack = TechStackInfo.detect_tech_stack(imports)
        
        assert any("async" in tech.lower() for tech in tech_stack)


class TestArchitecturePattern:
    """Test ArchitecturePattern recognition."""
    
    def test_detect_mvc_pattern(self):
        """Test detecting MVC pattern from file structure."""
        files = ["models/user.py", "views/user_view.py", "controllers/user_controller.py"]
        
        pattern = ArchitecturePattern.detect_pattern(files)
        
        assert "MVC" in pattern or "Model-View-Controller" in pattern
    
    def test_detect_layered_architecture(self):
        """Test detecting layered architecture."""
        files = ["domain/entities.py", "application/services.py", "infrastructure/database.py"]
        
        pattern = ArchitecturePattern.detect_pattern(files)
        
        assert "Layered" in pattern or "Domain-Driven" in pattern
    
    def test_detect_microservices_pattern(self):
        """Test detecting microservices pattern."""
        files = ["services/auth_service/", "services/payment_service/", "services/notification_service/"]
        
        pattern = ArchitecturePattern.detect_pattern(files)
        
        assert "Microservices" in pattern or "Service-Oriented" in pattern
    
    def test_detect_unknown_pattern(self):
        """Test fallback for unknown pattern."""
        files = ["random.py", "stuff.py"]
        
        pattern = ArchitecturePattern.detect_pattern(files)
        
        assert "Custom" in pattern or "Unknown" in pattern


class TestBusinessLanguageGenerator:
    """Test BusinessLanguageGenerator main class."""
    
    def test_generate_description_from_ast_analysis(self):
        """Test generating business description from AST analysis."""
        generator = BusinessLanguageGenerator()
        
        # Mock AST analysis result
        ast_analysis = {
            "functions": [
                {"name": "create_user"},
                {"name": "authenticate_user"},
                {"name": "send_email"},
            ],
            "classes": [
                {"name": "UserController"},
                {"name": "AuthService"},
            ],
            "imports": ["flask", "sqlalchemy", "marshmallow"],
        }
        
        file_list = ["models/user.py", "views/user_view.py", "controllers/user_controller.py"]
        
        description = generator.generate_description(ast_analysis, file_list)
        
        assert isinstance(description, BusinessDescription)
        assert description.summary  # Non-empty summary
        assert len(description.capabilities) > 0
        assert len(description.tech_stack) > 0
        assert description.architecture_pattern
        assert 0.0 <= description.confidence_score <= 1.0
    
    def test_generate_summary_from_capabilities(self):
        """Test summary generation from capabilities."""
        generator = BusinessLanguageGenerator()
        
        capabilities = ["User authentication", "Database access", "Email notifications"]
        tech_stack = ["Python", "Flask", "SQLAlchemy"]
        
        summary = generator._generate_summary(capabilities, tech_stack)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        # Should mention key technologies
        assert any(tech.lower() in summary.lower() for tech in tech_stack)
    
    def test_calculate_confidence_high(self):
        """Test high confidence score with good docstrings."""
        generator = BusinessLanguageGenerator()
        
        # Mock AST with good documentation
        ast_analysis = {
            "functions": [
                {"name": "create_user", "docstring": "Creates a new user account."},
                {"name": "authenticate", "docstring": "Authenticates user credentials."},
            ],
            "classes": [
                {"name": "UserController", "docstring": "Handles user-related HTTP requests."},
            ],
        }
        
        confidence = generator._calculate_confidence(ast_analysis)
        
        assert confidence >= 0.7  # High confidence
    
    def test_calculate_confidence_low(self):
        """Test low confidence score without docstrings."""
        generator = BusinessLanguageGenerator()
        
        # Mock AST without documentation
        ast_analysis = {
            "functions": [
                {"name": "func1"},
                {"name": "func2"},
            ],
            "classes": [
                {"name": "Class1"},
            ],
        }
        
        confidence = generator._calculate_confidence(ast_analysis)
        
        assert confidence < 0.7  # Lower confidence
    
    def test_convenience_function_get_business_description(self):
        """Test convenience function."""
        ast_analysis = {
            "functions": [{"name": "process_data"}],
            "classes": [{"name": "DataProcessor"}],
            "imports": ["pandas", "numpy"],
        }
        file_list = ["processors/data_processor.py"]
        
        description = get_business_description(ast_analysis, file_list)
        
        assert isinstance(description, BusinessDescription)
        assert description.tech_stack  # Should detect pandas/numpy
