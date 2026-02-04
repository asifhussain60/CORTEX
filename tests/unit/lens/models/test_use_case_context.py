"""
Unit tests for UseCaseExtractionContext model (Phase 0).

Tests business narrative extraction context for use case identification
from codebases (API endpoints, CLI commands, database operations).

Author: Asif Hussain
Created: 2026-02-04
Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 0
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any

# Direct import to avoid circular dependency
import importlib.util

test_file = Path(__file__)
tests_dir = test_file.parent.parent.parent.parent
project_root = tests_dir.parent
context_file = project_root / "cortex" / "lens" / "models" / "use_case_context.py"

spec = importlib.util.spec_from_file_location("use_case_context", context_file)
context_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context_module)

UseCaseExtractionContext = context_module.UseCaseExtractionContext
UseCase = context_module.UseCase
UseCaseType = context_module.UseCaseType
Actor = context_module.Actor


class TestUseCaseType:
    """Test UseCaseType enum."""
    
    def test_all_use_case_types(self):
        """Test that all expected use case types exist."""
        assert hasattr(UseCaseType, "API")
        assert hasattr(UseCaseType, "CLI")
        assert hasattr(UseCaseType, "DATABASE")
        assert hasattr(UseCaseType, "UI")
        assert hasattr(UseCaseType, "BACKGROUND_JOB")
    
    def test_use_case_type_values(self):
        """Test use case type string values."""
        assert UseCaseType.API.value == "api"
        assert UseCaseType.CLI.value == "cli"
        assert UseCaseType.DATABASE.value == "database"
        assert UseCaseType.UI.value == "ui"
        assert UseCaseType.BACKGROUND_JOB.value == "background_job"


class TestActor:
    """Test Actor data class."""
    
    def test_create_actor(self):
        """Test creating an actor."""
        actor = Actor(
            name="Admin User",
            role="administrator",
            permissions=["read", "write", "delete"]
        )
        
        assert actor.name == "Admin User"
        assert actor.role == "administrator"
        assert len(actor.permissions) == 3
    
    def test_actor_without_permissions(self):
        """Test actor without explicit permissions."""
        actor = Actor(
            name="Guest",
            role="guest",
            permissions=[]
        )
        
        assert actor.name == "Guest"
        assert actor.permissions == []


class TestUseCase:
    """Test UseCase data class."""
    
    def test_create_api_use_case(self):
        """Test creating an API use case."""
        use_case = UseCase(
            use_case_type=UseCaseType.API,
            title="User Registration",
            description="Allows new users to register with email and password",
            actors=[Actor("User", "end_user", ["create_account"])],
            endpoints=["/api/register"],
            business_value="Onboard new users to platform"
        )
        
        assert use_case.use_case_type == UseCaseType.API
        assert use_case.title == "User Registration"
        assert len(use_case.actors) == 1
        assert "/api/register" in use_case.endpoints
        assert "Onboard" in use_case.business_value
    
    def test_create_cli_use_case(self):
        """Test creating a CLI use case."""
        use_case = UseCase(
            use_case_type=UseCaseType.CLI,
            title="Database Migration",
            description="Run database schema migrations",
            actors=[Actor("DevOps Engineer", "operator", ["manage_schema"])],
            endpoints=["migrate", "migrate:rollback"],
            business_value="Maintain database schema integrity"
        )
        
        assert use_case.use_case_type == UseCaseType.CLI
        assert "Migration" in use_case.title
        assert len(use_case.endpoints) == 2
    
    def test_create_database_use_case(self):
        """Test creating a database use case."""
        use_case = UseCase(
            use_case_type=UseCaseType.DATABASE,
            title="Order Fulfillment",
            description="Track order status from placement to delivery",
            actors=[Actor("System", "system", ["read", "write"])],
            endpoints=["orders", "order_items", "shipments"],
            business_value="Enable order tracking"
        )
        
        assert use_case.use_case_type == UseCaseType.DATABASE
        assert len(use_case.endpoints) == 3
    
    def test_use_case_to_dict(self):
        """Test use case serialization to dictionary."""
        actor = Actor("Admin", "admin", ["all"])
        use_case = UseCase(
            use_case_type=UseCaseType.UI,
            title="Dashboard View",
            description="Display system metrics",
            actors=[actor],
            endpoints=["/dashboard"],
            business_value="Monitor system health"
        )
        
        data = use_case.to_dict()
        
        assert data["use_case_type"] == "ui"
        assert data["title"] == "Dashboard View"
        assert len(data["actors"]) == 1
        assert data["actors"][0]["name"] == "Admin"


class TestUseCaseExtractionContext:
    """Test UseCaseExtractionContext main class."""
    
    def test_create_empty_context(self):
        """Test creating an empty extraction context."""
        context = UseCaseExtractionContext(
            repository_path=Path("/test/repo"),
            language="Python",
            use_cases=[],
            metadata={}
        )
        
        assert context.repository_path == Path("/test/repo")
        assert context.language == "Python"
        assert len(context.use_cases) == 0
    
    def test_context_with_multiple_use_cases(self):
        """Test context with multiple use cases."""
        api_use_case = UseCase(
            UseCaseType.API,
            "User Login",
            "Authenticate users",
            [Actor("User", "end_user", [])],
            ["/api/login"],
            "Secure access"
        )
        
        cli_use_case = UseCase(
            UseCaseType.CLI,
            "Export Data",
            "Export data to CSV",
            [Actor("Admin", "admin", [])],
            ["export"],
            "Data portability"
        )
        
        context = UseCaseExtractionContext(
            repository_path=Path("/project"),
            language="Java",
            use_cases=[api_use_case, cli_use_case],
            metadata={"framework": "Spring Boot"}
        )
        
        assert len(context.use_cases) == 2
        assert context.metadata["framework"] == "Spring Boot"
    
    def test_to_narrative_method(self):
        """Test generating business narrative from context."""
        use_cases = [
            UseCase(
                UseCaseType.API,
                "Create Order",
                "Place new orders",
                [Actor("Customer", "customer", [])],
                ["/api/orders"],
                "Enable purchases"
            ),
            UseCase(
                UseCaseType.DATABASE,
                "Inventory Management",
                "Track product stock",
                [Actor("System", "system", [])],
                ["inventory"],
                "Prevent stockouts"
            )
        ]
        
        context = UseCaseExtractionContext(
            repository_path=Path("/ecommerce"),
            language="C#",
            use_cases=use_cases,
            metadata={}
        )
        
        narrative = context.to_narrative()
        
        assert isinstance(narrative, str)
        assert "Create Order" in narrative
        assert "Inventory Management" in narrative
        assert "C#" in narrative
    
    def test_context_serialization(self):
        """Test context serialization to dictionary."""
        actor = Actor("User", "user", ["read"])
        use_case = UseCase(
            UseCaseType.API,
            "View Profile",
            "Display user profile",
            [actor],
            ["/api/profile"],
            "User engagement"
        )
        
        context = UseCaseExtractionContext(
            repository_path=Path("/app"),
            language="TypeScript",
            use_cases=[use_case],
            metadata={"framework": "NestJS"}
        )
        
        data = context.to_dict()
        
        assert data["repository_path"] == "/app"
        assert data["language"] == "TypeScript"
        assert len(data["use_cases"]) == 1
        assert data["metadata"]["framework"] == "NestJS"
    
    def test_filter_by_use_case_type(self):
        """Test filtering use cases by type."""
        use_cases = [
            UseCase(UseCaseType.API, "API 1", "desc", [], ["/api/1"], "value"),
            UseCase(UseCaseType.CLI, "CLI 1", "desc", [], ["cmd1"], "value"),
            UseCase(UseCaseType.API, "API 2", "desc", [], ["/api/2"], "value"),
        ]
        
        context = UseCaseExtractionContext(
            Path("/repo"),
            "Python",
            use_cases,
            {}
        )
        
        api_cases = context.filter_by_type(UseCaseType.API)
        cli_cases = context.filter_by_type(UseCaseType.CLI)
        
        assert len(api_cases) == 2
        assert len(cli_cases) == 1
        assert all(uc.use_case_type == UseCaseType.API for uc in api_cases)
    
    def test_get_all_actors(self):
        """Test extracting all unique actors."""
        actor1 = Actor("User", "user", [])
        actor2 = Actor("Admin", "admin", [])
        actor3 = Actor("User", "user", [])  # Duplicate
        
        use_cases = [
            UseCase(UseCaseType.API, "UC1", "desc", [actor1], [], "value"),
            UseCase(UseCaseType.CLI, "UC2", "desc", [actor2, actor3], [], "value"),
        ]
        
        context = UseCaseExtractionContext(Path("/repo"), "Java", use_cases, {})
        actors = context.get_all_actors()
        
        # Should deduplicate by name
        assert len(actors) == 2
        actor_names = [a.name for a in actors]
        assert "User" in actor_names
        assert "Admin" in actor_names


class TestBusinessNarrativeGeneration:
    """Test business narrative generation capabilities."""
    
    def test_narrative_includes_all_use_cases(self):
        """Test that narrative includes all use cases."""
        use_cases = [
            UseCase(UseCaseType.API, "Login", "Auth", [], ["/login"], "Security"),
            UseCase(UseCaseType.DATABASE, "Store Data", "Persist", [], ["users"], "Reliability"),
        ]
        
        context = UseCaseExtractionContext(Path("/app"), "Python", use_cases, {})
        narrative = context.to_narrative()
        
        assert "Login" in narrative
        assert "Store Data" in narrative
    
    def test_narrative_format(self):
        """Test narrative format and structure."""
        use_case = UseCase(
            UseCaseType.API,
            "Process Payment",
            "Handle credit card transactions",
            [Actor("Customer", "customer", [])],
            ["/api/payments"],
            "Revenue generation"
        )
        
        context = UseCaseExtractionContext(
            Path("/payment-service"),
            "Java",
            [use_case],
            {"framework": "Spring"}
        )
        
        narrative = context.to_narrative()
        
        # Check for structured narrative
        assert "Process Payment" in narrative
        assert "Java" in narrative
        assert "Customer" in narrative or "customer" in narrative.lower()
