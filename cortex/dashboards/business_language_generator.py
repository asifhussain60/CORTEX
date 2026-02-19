"""
Business Language Generator - AST to Plain English Conversion.

Converts code structure analysis into human-readable business descriptions:
- Extracts capabilities from function/class names
- Detects tech stack from imports
- Identifies architecture patterns
- Generates plain English summaries
- Assigns confidence scores

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-001
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class BusinessDescription:
    """
    Business-level description of repository.

    Attributes:
        summary: High-level summary (1-2 sentences)
        capabilities: List of capabilities (e.g., "User authentication")
        tech_stack: List of technologies (e.g., "Flask", "PostgreSQL")
        architecture_pattern: Detected pattern (e.g., "MVC")
        confidence_score: Confidence (0.0-1.0) based on documentation quality
        details: Extended description (optional)
    """
    summary: str
    capabilities: List[str]
    tech_stack: List[str]
    architecture_pattern: str
    confidence_score: float
    details: str = ""


class CapabilitySet:
    """Detects capabilities from code structure."""

    # Common capability patterns (verb + noun)
    CAPABILITY_PATTERNS = {
        "create": "Creation",
        "add": "Addition",
        "update": "Update",
        "edit": "Editing",
        "delete": "Deletion",
        "remove": "Removal",
        "get": "Retrieval",
        "fetch": "Fetching",
        "list": "Listing",
        "search": "Search",
        "find": "Finding",
        "validate": "Validation",
        "verify": "Verification",
        "authenticate": "Authentication",
        "authorize": "Authorization",
        "login": "Login",
        "logout": "Logout",
        "register": "Registration",
        "send": "Sending",
        "receive": "Receiving",
        "process": "Processing",
        "calculate": "Calculation",
        "compute": "Computation",
        "transform": "Transformation",
        "convert": "Conversion",
        "parse": "Parsing",
        "render": "Rendering",
        "display": "Display",
        "export": "Export",
        "import": "Import",
    }

    # Common nouns for capabilities
    ENTITY_PATTERNS = [
        "user", "customer", "account", "profile",
        "order", "payment", "transaction", "invoice",
        "product", "item", "inventory",
        "email", "notification", "message",
        "report", "dashboard", "analytics",
        "file", "document", "data",
        "token", "session", "auth",
    ]

    @classmethod
    def detect_capabilities(cls, functions: List[str] = None, classes: List[str] = None) -> List[str]:
        """
        Detect capabilities from function and class names.

        Args:
            functions: List of function names
            classes: List of class names

        Returns:
            List of capability descriptions (e.g., ["User authentication", "Data processing"])
        """
        capabilities = set()

        if functions:
            for func_name in functions:
                capability = cls._extract_capability(func_name)
                if capability:
                    capabilities.add(capability)

        if classes:
            for class_name in classes:
                capability = cls._extract_capability_from_class(class_name)
                if capability:
                    capabilities.add(capability)

        return sorted(capabilities)

    @classmethod
    def _extract_capability(cls, name: str) -> str:
        """Extract capability from function name."""
        # Convert camelCase/snake_case to words
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', name)
        if not words:
            words = name.split("_")

        words = [w.lower() for w in words]

        # Look for verb pattern
        for verb, action in cls.CAPABILITY_PATTERNS.items():
            if words and words[0] == verb:
                # Extract entity (noun)
                entity = " ".join(words[1:]) if len(words) > 1 else "resource"
                return f"{entity.capitalize()} {action.lower()}"

        # Fallback: look for entity in name
        for entity in cls.ENTITY_PATTERNS:
            if entity in words:
                return f"{entity.capitalize()} management"

        return ""

    @classmethod
    def _extract_capability_from_class(cls, name: str) -> str:
        """Extract capability from class name."""
        # Remove common suffixes
        clean_name = name
        for suffix in ["Controller", "Service", "Manager", "Handler", "Processor", "Repository"]:
            if name.endswith(suffix):
                clean_name = name[: -len(suffix)]
                break

        # Convert to words
        words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', clean_name)
        words = [w.lower() for w in words]

        if words:
            entity = " ".join(words)
            return f"{entity.capitalize()} management"

        return ""


class TechStackInfo:
    """Detects tech stack from imports."""

    # Technology mapping (import → business name)
    TECH_MAP = {
        # Web frameworks
        "flask": "Flask (Python web framework)",
        "django": "Django (Python web framework)",
        "fastapi": "FastAPI (Python web framework)",
        "express": "Express.js (Node.js web framework)",
        "react": "React (Frontend framework)",
        "vue": "Vue.js (Frontend framework)",

        # Databases & ORMs
        "sqlalchemy": "SQLAlchemy (Database ORM)",
        "django.db": "Django ORM",
        "psycopg2": "PostgreSQL",
        "pymongo": "MongoDB",
        "redis": "Redis (Cache/Message broker)",

        # Data science
        "pandas": "Pandas (Data analysis)",
        "numpy": "NumPy (Numerical computing)",
        "scikit-learn": "Scikit-learn (Machine learning)",
        "tensorflow": "TensorFlow (Deep learning)",
        "pytorch": "PyTorch (Deep learning)",
        "matplotlib": "Matplotlib (Data visualization)",

        # Async
        "asyncio": "Asyncio (Async programming)",
        "aiohttp": "AIOHTTP (Async HTTP)",
        "celery": "Celery (Task queue)",

        # Testing
        "pytest": "Pytest (Testing framework)",
        "unittest": "unittest (Testing framework)",

        # Serialization
        "marshmallow": "Marshmallow (Serialization)",
        "pydantic": "Pydantic (Validation)",

        # Authentication
        "jwt": "JWT (Authentication)",
        "oauth": "OAuth (Authorization)",
    }

    @classmethod
    def detect_tech_stack(cls, imports: List[str]) -> List[str]:
        """
        Detect tech stack from import statements.

        Args:
            imports: List of import module names

        Returns:
            List of technology descriptions
        """
        tech_stack = set()

        for imp in imports:
            # Normalize import (handle submodules)
            base_module = imp.split(".")[0]

            # Check direct match
            if base_module in cls.TECH_MAP:
                tech_stack.add(cls.TECH_MAP[base_module])
            elif imp in cls.TECH_MAP:
                tech_stack.add(cls.TECH_MAP[imp])

        return sorted(tech_stack)


class ArchitecturePattern:
    """Identifies architecture patterns from file structure."""

    @classmethod
    def detect_pattern(cls, files: List[str]) -> str:
        """
        Detect architecture pattern from file paths.

        Args:
            files: List of file paths

        Returns:
            Architecture pattern name
        """
        file_paths = [f.lower() for f in files]

        # MVC pattern
        if any("model" in f for f in file_paths) and \
           any("view" in f for f in file_paths) and \
           any("controller" in f for f in file_paths):
            return "MVC (Model-View-Controller)"

        # Layered architecture
        if any("domain" in f for f in file_paths) and \
           any("application" in f or "service" in f for f in file_paths) and \
           any("infrastructure" in f for f in file_paths):
            return "Layered Architecture (Domain-Driven Design)"

        # Microservices
        if sum("service" in f for f in file_paths) >= 2:
            return "Microservices Architecture"

        # Feature-based
        if any("features" in f or "modules" in f for f in file_paths):
            return "Feature-based Architecture"

        return "Custom Architecture"


class BusinessLanguageGenerator:
    """
    Generates business-level descriptions from code analysis.

    Converts AST analysis into plain English descriptions for non-technical stakeholders.

    Example:
        ```python
        generator = BusinessLanguageGenerator()

        ast_analysis = {
            "functions": [{"name": "create_user"}, {"name": "send_email"}],
            "classes": [{"name": "UserController"}],
            "imports": ["flask", "sqlalchemy"],
        }
        file_list = ["models/user.py", "views/user_view.py"]

        description = generator.generate_description(ast_analysis, file_list)
        print(description.summary)
        # "A Flask-based web application for user management and email notifications"
        ```
    """

    def generate_description(
        self,
        ast_analysis: Dict[str, Any],
        file_list: List[str],
    ) -> BusinessDescription:
        """
        Generate business description from AST analysis.

        Args:
            ast_analysis: AST analysis result from ASTAnalyzer
            file_list: List of file paths in repository

        Returns:
            BusinessDescription with summary, capabilities, tech stack, etc.
        """
        # Extract components
        function_names = [f.get("name", "") for f in ast_analysis.get("functions", [])]
        class_names = [c.get("name", "") for c in ast_analysis.get("classes", [])]
        imports = ast_analysis.get("imports", [])

        # Detect capabilities
        capabilities = CapabilitySet.detect_capabilities(
            functions=function_names,
            classes=class_names,
        )

        # Detect tech stack
        tech_stack = TechStackInfo.detect_tech_stack(imports)

        # Detect architecture pattern
        architecture_pattern = ArchitecturePattern.detect_pattern(file_list)

        # Generate summary
        summary = self._generate_summary(capabilities, tech_stack)

        # Calculate confidence
        confidence_score = self._calculate_confidence(ast_analysis)

        return BusinessDescription(
            summary=summary,
            capabilities=capabilities,
            tech_stack=tech_stack,
            architecture_pattern=architecture_pattern,
            confidence_score=confidence_score,
        )

    def _generate_summary(self, capabilities: List[str], tech_stack: List[str]) -> str:
        """
        Generate high-level summary.

        Args:
            capabilities: List of detected capabilities
            tech_stack: List of detected technologies

        Returns:
            Summary sentence
        """
        # Extract primary technology
        primary_tech = tech_stack[0] if tech_stack else "Python"

        # Extract primary capabilities (top 3)
        primary_capabilities = capabilities[:3] if capabilities else ["data processing"]

        # Format summary
        if len(primary_capabilities) == 1:
            capability_text = primary_capabilities[0].lower()
        elif len(primary_capabilities) == 2:
            capability_text = f"{primary_capabilities[0].lower()} and {primary_capabilities[1].lower()}"
        else:
            capability_text = ", ".join(c.lower() for c in primary_capabilities[:-1])
            capability_text += f", and {primary_capabilities[-1].lower()}"

        return f"A {primary_tech.split()[0]}-based application for {capability_text}."

    def _calculate_confidence(self, ast_analysis: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on documentation quality.

        Args:
            ast_analysis: AST analysis result

        Returns:
            Confidence score (0.0-1.0)
        """
        functions = ast_analysis.get("functions", [])
        classes = ast_analysis.get("classes", [])

        total_items = len(functions) + len(classes)
        if total_items == 0:
            return 0.5  # Neutral confidence

        # Count documented items
        documented_functions = sum(1 for f in functions if f.get("docstring"))
        documented_classes = sum(1 for c in classes if c.get("docstring"))
        documented_items = documented_functions + documented_classes

        # Calculate base confidence
        documentation_ratio = documented_items / total_items

        # Base confidence: 0.4 (low) to 1.0 (high)
        confidence = 0.4 + (documentation_ratio * 0.6)

        return round(confidence, 2)


def get_business_description(
    ast_analysis: Dict[str, Any],
    file_list: List[str],
) -> BusinessDescription:
    """
    Convenience function to get business description.

    Args:
        ast_analysis: AST analysis result from ASTAnalyzer
        file_list: List of file paths in repository

    Returns:
        BusinessDescription
    """
    generator = BusinessLanguageGenerator()
    return generator.generate_description(ast_analysis, file_list)
