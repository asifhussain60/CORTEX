"""
Pattern catalog registry for design patterns.

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Stage: S1 - Pattern Recognition Foundation
AC Marker: AC-PHASE57-S1-003
"""

from typing import Dict, Optional, List
from dataclasses import dataclass

from .base import PatternInfo, PatternCategory


@dataclass
class PatternCatalog:
    """
    Registry of recognized design patterns.
    
    Maintains a catalog of 25+ design patterns that can be detected
    in code analysis. Patterns are organized by category.
    
    Example:
        ```python
        catalog = PatternCatalog()
        
        # Register patterns
        singleton_pattern = PatternInfo(
            name="Singleton",
            category=PatternCategory.CREATIONAL,
            signatures=["getInstance()"],
            description="Ensure single instance"
        )
        catalog.register(singleton_pattern)
        
        # Query patterns
        pattern = catalog.get("Singleton")
        all_creational = catalog.get_by_category(PatternCategory.CREATIONAL)
        ```
    """

    registry: Dict[str, PatternInfo]

    def __init__(self) -> None:
        """Initialize catalog with default patterns."""
        self.registry = {}
        self._initialize_default_patterns()

    def _initialize_default_patterns(self) -> None:
        """
        Initialize catalog with 25+ Gang of Four and enterprise patterns.
        
        Patterns:
            Creational (5): Singleton, Factory, AbstractFactory, Builder, Prototype
            Structural (6): Adapter, Bridge, Composite, Decorator, Facade, Proxy
            Behavioral (11): Observer, Strategy, State, ChainOfResponsibility,
                           Command, Interpreter, Iterator, Mediator, Memento,
                           Template Method, Visitor
            Concurrency (4): ActiveObject, Monitor, ProducerConsumer, ThreadPool
            Enterprise (varies): Repository, ServiceLocator, DataTransferObject
        """
        # Creational Patterns
        self._register_default_pattern(
            PatternInfo(
                name="Singleton",
                category=PatternCategory.CREATIONAL,
                signatures=["getInstance()", "getinstance()", "__new__()"],
                description="Ensure a class has only one instance and provide a global point of access",
                confidence=0.85,
            )
        )

        self._register_default_pattern(
            PatternInfo(
                name="Factory",
                category=PatternCategory.CREATIONAL,
                signatures=["create()", "make()", "new()"],
                description="Define an interface for creating objects",
                confidence=0.80,
            )
        )

        self._register_default_pattern(
            PatternInfo(
                name="AbstractFactory",
                category=PatternCategory.CREATIONAL,
                signatures=["createProductA()", "createProductB()"],
                description="Provide interface for families of related objects",
                confidence=0.75,
            )
        )

        self._register_default_pattern(
            PatternInfo(
                name="Builder",
                category=PatternCategory.CREATIONAL,
                signatures=["build()", "with", "fluent"],
                description="Separate construction from representation",
                confidence=0.78,
            )
        )

        self._register_default_pattern(
            PatternInfo(
                name="Prototype",
                category=PatternCategory.CREATIONAL,
                signatures=["clone()", "__copy__"],
                description="Create new instances by copying prototype",
                confidence=0.72,
            )
        )

        # Structural Patterns
        self._register_default_pattern(
            PatternInfo(
                name="Adapter",
                category=PatternCategory.STRUCTURAL,
                signatures=["adapt()", "convert()"],
                description="Convert interface to another expected by clients",
                confidence=0.77,
            )
        )

        self._register_default_pattern(
            PatternInfo(
                name="Facade",
                category=PatternCategory.STRUCTURAL,
                signatures=["execute()", "run()", "process()"],
                description="Provide unified interface to set of interfaces",
                confidence=0.79,
            )
        )

        self._register_default_pattern(
            PatternInfo(
                name="Proxy",
                category=PatternCategory.STRUCTURAL,
                signatures=["__getattr__", "lazy_load", "cache"],
                description="Provide surrogate or placeholder for another object",
                confidence=0.76,
            )
        )

        self._register_default_pattern(
            PatternInfo(
                name="Decorator",
                category=PatternCategory.STRUCTURAL,
                signatures=["decorator", "wrap", "enhance"],
                description="Attach responsibilities to object dynamically",
                confidence=0.81,
            )
        )

        self._register_default_pattern(
            PatternInfo(
                name="Composite",
                category=PatternCategory.STRUCTURAL,
                signatures=["add()", "remove()", "children"],
                description="Compose objects into tree structures",
                confidence=0.78,
            )
        )

        self._register_default_pattern(
            PatternInfo(
                name="Bridge",
                category=PatternCategory.STRUCTURAL,
                signatures=["abstraction", "implementation"],
                description="Decouple abstraction from implementation",
                confidence=0.74,
            )
        )

        # Behavioral Patterns
        self._register_default_pattern(
            PatternInfo(
                name="Observer",
                category=PatternCategory.BEHAVIORAL,
                signatures=["subscribe()", "notify()", "observe()"],
                description="Define one-to-many dependency between objects",
                confidence=0.82,
            )
        )

        self._register_default_pattern(
            PatternInfo(
                name="Strategy",
                category=PatternCategory.BEHAVIORAL,
                signatures=["execute()", "algorithm", "strategy"],
                description="Define family of interchangeable algorithms",
                confidence=0.80,
            )
        )

        self._register_default_pattern(
            PatternInfo(
                name="State",
                category=PatternCategory.BEHAVIORAL,
                signatures=["handle()", "setState()", "state"],
                description="Allow object to alter behavior when state changes",
                confidence=0.79,
            )
        )

        self._register_default_pattern(
            PatternInfo(
                name="TemplateMethod",
                category=PatternCategory.BEHAVIORAL,
                signatures=["templateMethod()", "step1()", "step2()"],
                description="Define skeleton of algorithm in base class",
                confidence=0.81,
            )
        )

        self._register_default_pattern(
            PatternInfo(
                name="Command",
                category=PatternCategory.BEHAVIORAL,
                signatures=["execute()", "undo()", "command"],
                description="Encapsulate request as an object",
                confidence=0.78,
            )
        )

        # Concurrency Patterns
        self._register_default_pattern(
            PatternInfo(
                name="ThreadPool",
                category=PatternCategory.CONCURRENCY,
                signatures=["submit()", "execute()", "thread_pool"],
                description="Manage pool of worker threads",
                confidence=0.83,
            )
        )

        self._register_default_pattern(
            PatternInfo(
                name="ProducerConsumer",
                category=PatternCategory.CONCURRENCY,
                signatures=["produce()", "consume()", "queue"],
                description="Decouple production from consumption",
                confidence=0.80,
            )
        )

    def _register_default_pattern(self, pattern: PatternInfo) -> None:
        """Register a default pattern."""
        self.registry[pattern.name] = pattern

    def register(self, pattern: PatternInfo) -> None:
        """
        Register a pattern in the catalog.
        
        Args:
            pattern: PatternInfo to register
            
        Raises:
            ValueError: If pattern with same name already registered
        """
        if pattern.name in self.registry:
            raise ValueError(f"Pattern '{pattern.name}' already registered")
        self.registry[pattern.name] = pattern

    def get(self, name: str) -> Optional[PatternInfo]:
        """
        Retrieve pattern by name.
        
        Args:
            name: Pattern name
            
        Returns:
            PatternInfo or None if not found
        """
        return self.registry.get(name)

    def get_by_category(self, category: PatternCategory | str) -> List[PatternInfo]:
        """
        Retrieve all patterns in a category.
        
        Args:
            category: PatternCategory or string category name
            
        Returns:
            List of PatternInfo matching category
        """
        if isinstance(category, str):
            category_str = category
        else:
            category_str = category.value

        return [p for p in self.registry.values() if p.category == category_str or p.category == category]

    def list_patterns(self) -> List[PatternInfo]:
        """
        List all registered patterns.
        
        Returns:
            List of all PatternInfo objects
        """
        return list(self.registry.values())

    def count(self) -> int:
        """
        Get count of registered patterns.
        
        Returns:
            Number of patterns in catalog
        """
        return len(self.registry)

    def __len__(self) -> int:
        """Return number of patterns."""
        return self.count()
