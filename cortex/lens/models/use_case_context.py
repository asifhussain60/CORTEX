"""
UseCaseExtractionContext for business narrative generation.

Extracts use cases from codebases by analyzing API endpoints, CLI commands,
database operations, and UI flows to generate business-facing documentation.

Author: Asif Hussain
Created: 2026-02-04
Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 0
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any


class UseCaseType(Enum):
    """
    Types of use cases that can be extracted from code.
    
    - API: REST/GraphQL endpoints, webhooks
    - CLI: Command-line commands, scripts
    - DATABASE: Database tables, stored procedures, triggers
    - UI: Web pages, forms, dashboards
    - BACKGROUND_JOB: Cron jobs, queues, scheduled tasks
    """
    API = "api"
    CLI = "cli"
    DATABASE = "database"
    UI = "ui"
    BACKGROUND_JOB = "background_job"


@dataclass
class Actor:
    """
    Actor in a use case (user, admin, system, external service).
    
    Attributes:
        name: Actor name (e.g., "Admin User", "Payment Gateway")
        role: Actor role (e.g., "administrator", "system", "external")
        permissions: List of permissions (e.g., ["read", "write"])
    
    Example:
        >>> actor = Actor(
        ...     name="Admin User",
        ...     role="administrator",
        ...     permissions=["read", "write", "delete"]
        ... )
    """
    name: str
    role: str
    permissions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize actor to dictionary."""
        return {
            "name": self.name,
            "role": self.role,
            "permissions": self.permissions
        }


@dataclass
class UseCase:
    """
    Business use case extracted from code.
    
    Attributes:
        use_case_type: Type of use case (API, CLI, DATABASE, UI, BACKGROUND_JOB)
        title: Use case title (e.g., "User Registration")
        description: Detailed description
        actors: List of actors involved
        endpoints: List of endpoints/commands/tables
        business_value: Business value statement
    
    Example:
        >>> use_case = UseCase(
        ...     use_case_type=UseCaseType.API,
        ...     title="User Registration",
        ...     description="Allows new users to register",
        ...     actors=[Actor("User", "end_user", ["create_account"])],
        ...     endpoints=["/api/register"],
        ...     business_value="Onboard new users"
        ... )
    
    Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 3
    """
    use_case_type: UseCaseType
    title: str
    description: str
    actors: List[Actor]
    endpoints: List[str]
    business_value: str
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize use case to dictionary.
        
        Returns:
            Dictionary with all use case fields
        """
        return {
            "use_case_type": self.use_case_type.value,
            "title": self.title,
            "description": self.description,
            "actors": [actor.to_dict() for actor in self.actors],
            "endpoints": self.endpoints,
            "business_value": self.business_value
        }


@dataclass
class UseCaseExtractionContext:
    """
    Context for use case extraction from codebase.
    
    Attributes:
        repository_path: Path to repository root
        language: Primary programming language
        use_cases: List of extracted use cases
        metadata: Additional metadata (framework, version, etc.)
    
    Methods:
        to_narrative(): Generate business narrative from use cases
        filter_by_type(): Filter use cases by type
        get_all_actors(): Get unique list of all actors
    
    Example:
        >>> context = UseCaseExtractionContext(
        ...     repository_path=Path("/project"),
        ...     language="Python",
        ...     use_cases=[...],
        ...     metadata={"framework": "FastAPI"}
        ... )
        >>> narrative = context.to_narrative()
        >>> print(narrative)
        "This Python application provides the following capabilities..."
    
    Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 3
    """
    repository_path: Path
    language: str
    use_cases: List[UseCase]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_narrative(self) -> str:
        """
        Generate business-facing narrative from use cases.
        
        Returns:
            Human-readable narrative describing system capabilities
        
        Example:
            >>> narrative = context.to_narrative()
            >>> print(narrative)
            "This Python application provides 3 capabilities:
            1. User Registration (API) - Onboard new users
            2. Export Data (CLI) - Data portability
            3. Order Tracking (DATABASE) - Monitor order status"
        """
        if not self.use_cases:
            return f"This {self.language} application has no extracted use cases yet."
        
        lines = [
            f"This {self.language} application provides {len(self.use_cases)} capabilities:\n"
        ]
        
        for idx, uc in enumerate(self.use_cases, 1):
            actor_names = ", ".join(actor.name for actor in uc.actors) if uc.actors else "System"
            lines.append(
                f"{idx}. {uc.title} ({uc.use_case_type.value.upper()}) - "
                f"{uc.business_value} [Actors: {actor_names}]"
            )
        
        return "\n".join(lines)
    
    def filter_by_type(self, use_case_type: UseCaseType) -> List[UseCase]:
        """
        Filter use cases by type.
        
        Args:
            use_case_type: Type to filter by
        
        Returns:
            List of use cases matching the type
        
        Example:
            >>> api_cases = context.filter_by_type(UseCaseType.API)
            >>> len(api_cases)
            5
        """
        return [uc for uc in self.use_cases if uc.use_case_type == use_case_type]
    
    def get_all_actors(self) -> List[Actor]:
        """
        Get unique list of all actors across use cases.
        
        Returns:
            Deduplicated list of actors
        
        Example:
            >>> actors = context.get_all_actors()
            >>> [a.name for a in actors]
            ['User', 'Admin', 'Payment Gateway']
        """
        seen_names = set()
        unique_actors = []
        
        for uc in self.use_cases:
            for actor in uc.actors:
                if actor.name not in seen_names:
                    seen_names.add(actor.name)
                    unique_actors.append(actor)
        
        return unique_actors
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize context to dictionary.
        
        Returns:
            Dictionary with all context fields
        """
        return {
            "repository_path": str(self.repository_path),
            "language": self.language,
            "use_cases": [uc.to_dict() for uc in self.use_cases],
            "metadata": self.metadata
        }
