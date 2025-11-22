"""
Tests for base specification classes and composition.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import pytest
from dataclasses import dataclass
from src.domain.specifications import (
    ISpecification,
    Specification,
    AndSpecification,
    OrSpecification,
    NotSpecification,
)


@dataclass
class Person:
    """Test entity."""
    name: str
    age: int
    is_active: bool = True


class IsAdultSpec(Specification[Person]):
    """Specification for adults (age >= 18)."""
    
    def is_satisfied_by(self, candidate: Person) -> bool:
        return candidate.age >= 18


class IsActiveSpec(Specification[Person]):
    """Specification for active persons."""
    
    def is_satisfied_by(self, candidate: Person) -> bool:
        return candidate.is_active


class TestSpecificationBase:
    """Tests for base specification functionality."""
    
    def test_simple_specification_satisfied(self):
        """Test specification returns True for satisfied candidate."""
        spec = IsAdultSpec()
        person = Person(name="John", age=25)
        
        assert spec.is_satisfied_by(person) is True
    
    def test_simple_specification_not_satisfied(self):
        """Test specification returns False for unsatisfied candidate."""
        spec = IsAdultSpec()
        person = Person(name="Jane", age=15)
        
        assert spec.is_satisfied_by(person) is False
    
    def test_specification_with_boundary(self):
        """Test specification at boundary value."""
        spec = IsAdultSpec()
        person = Person(name="Alex", age=18)
        
        assert spec.is_satisfied_by(person) is True


class TestAndSpecification:
    """Tests for AND composition."""
    
    def test_and_both_satisfied(self):
        """Test AND returns True when both specifications are satisfied."""
        spec = IsAdultSpec().and_(IsActiveSpec())
        person = Person(name="John", age=25, is_active=True)
        
        assert spec.is_satisfied_by(person) is True
    
    def test_and_first_not_satisfied(self):
        """Test AND returns False when first specification fails."""
        spec = IsAdultSpec().and_(IsActiveSpec())
        person = Person(name="Jane", age=15, is_active=True)
        
        assert spec.is_satisfied_by(person) is False
    
    def test_and_second_not_satisfied(self):
        """Test AND returns False when second specification fails."""
        spec = IsAdultSpec().and_(IsActiveSpec())
        person = Person(name="Bob", age=25, is_active=False)
        
        assert spec.is_satisfied_by(person) is False
    
    def test_and_neither_satisfied(self):
        """Test AND returns False when neither specification is satisfied."""
        spec = IsAdultSpec().and_(IsActiveSpec())
        person = Person(name="Alice", age=15, is_active=False)
        
        assert spec.is_satisfied_by(person) is False
    
    def test_and_operator(self):
        """Test & operator works same as and_()."""
        spec1 = IsAdultSpec() & IsActiveSpec()
        spec2 = IsAdultSpec().and_(IsActiveSpec())
        person = Person(name="John", age=25, is_active=True)
        
        assert spec1.is_satisfied_by(person) == spec2.is_satisfied_by(person)


class TestOrSpecification:
    """Tests for OR composition."""
    
    def test_or_both_satisfied(self):
        """Test OR returns True when both specifications are satisfied."""
        spec = IsAdultSpec().or_(IsActiveSpec())
        person = Person(name="John", age=25, is_active=True)
        
        assert spec.is_satisfied_by(person) is True
    
    def test_or_first_satisfied(self):
        """Test OR returns True when only first specification is satisfied."""
        spec = IsAdultSpec().or_(IsActiveSpec())
        person = Person(name="Jane", age=25, is_active=False)
        
        assert spec.is_satisfied_by(person) is True
    
    def test_or_second_satisfied(self):
        """Test OR returns True when only second specification is satisfied."""
        spec = IsAdultSpec().or_(IsActiveSpec())
        person = Person(name="Bob", age=15, is_active=True)
        
        assert spec.is_satisfied_by(person) is True
    
    def test_or_neither_satisfied(self):
        """Test OR returns False when neither specification is satisfied."""
        spec = IsAdultSpec().or_(IsActiveSpec())
        person = Person(name="Alice", age=15, is_active=False)
        
        assert spec.is_satisfied_by(person) is False
    
    def test_or_operator(self):
        """Test | operator works same as or_()."""
        spec1 = IsAdultSpec() | IsActiveSpec()
        spec2 = IsAdultSpec().or_(IsActiveSpec())
        person = Person(name="John", age=25, is_active=True)
        
        assert spec1.is_satisfied_by(person) == spec2.is_satisfied_by(person)


class TestNotSpecification:
    """Tests for NOT negation."""
    
    def test_not_satisfied_becomes_not_satisfied(self):
        """Test NOT inverts satisfied specification."""
        spec = IsAdultSpec().not_()
        person = Person(name="John", age=25)
        
        assert spec.is_satisfied_by(person) is False
    
    def test_not_not_satisfied_becomes_satisfied(self):
        """Test NOT inverts unsatisfied specification."""
        spec = IsAdultSpec().not_()
        person = Person(name="Jane", age=15)
        
        assert spec.is_satisfied_by(person) is True
    
    def test_not_operator(self):
        """Test ~ operator works same as not_()."""
        spec1 = ~IsAdultSpec()
        spec2 = IsAdultSpec().not_()
        person = Person(name="John", age=25)
        
        assert spec1.is_satisfied_by(person) == spec2.is_satisfied_by(person)
    
    def test_double_negation(self):
        """Test double negation returns to original logic."""
        spec = IsAdultSpec().not_().not_()
        person = Person(name="John", age=25)
        
        assert spec.is_satisfied_by(person) is True


class TestComplexComposition:
    """Tests for complex specification compositions."""
    
    def test_complex_and_or_composition(self):
        """Test (Adult AND Active) OR (NOT Adult)."""
        spec = (IsAdultSpec() & IsActiveSpec()) | ~IsAdultSpec()
        
        # Adult and active -> True
        assert spec.is_satisfied_by(Person("John", 25, True)) is True
        
        # Adult but not active -> False
        assert spec.is_satisfied_by(Person("Jane", 25, False)) is False
        
        # Not adult but active -> True (because NOT adult)
        assert spec.is_satisfied_by(Person("Bob", 15, True)) is True
        
        # Not adult and not active -> True (because NOT adult)
        assert spec.is_satisfied_by(Person("Alice", 15, False)) is True
    
    def test_multiple_and_chaining(self):
        """Test chaining multiple AND specifications."""
        # Create a third spec
        class HasNameSpec(Specification[Person]):
            def is_satisfied_by(self, candidate: Person) -> bool:
                return len(candidate.name) > 0
        
        spec = IsAdultSpec() & IsActiveSpec() & HasNameSpec()
        
        # All conditions met
        assert spec.is_satisfied_by(Person("John", 25, True)) is True
        
        # One condition fails
        assert spec.is_satisfied_by(Person("", 25, True)) is False
    
    def test_specification_string_representation(self):
        """Test string representation of composite specifications."""
        spec = IsAdultSpec() & IsActiveSpec()
        assert "AND" in repr(spec)
        
        spec = IsAdultSpec() | IsActiveSpec()
        assert "OR" in repr(spec)
        
        spec = ~IsAdultSpec()
        assert "NOT" in repr(spec)
