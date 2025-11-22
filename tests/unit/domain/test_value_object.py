"""Unit tests for ValueObject base class"""
import pytest
from dataclasses import dataclass
from typing import Tuple, Any
from src.domain.common.value_object import ValueObject


@dataclass(frozen=True)
class TestScore(ValueObject):
    """Test value object for unit tests"""
    value: float
    
    def get_equality_components(self) -> Tuple[Any, ...]:
        return (self.value,)


@dataclass(frozen=True)
class TestPerson(ValueObject):
    """Test value object with multiple components"""
    first_name: str
    last_name: str
    
    def get_equality_components(self) -> Tuple[Any, ...]:
        return (self.first_name, self.last_name)


class TestValueObject:
    """Test ValueObject base class"""
    
    def test_value_objects_equal_with_same_values(self):
        """Test value objects are equal when components match"""
        score1 = TestScore(0.85)
        score2 = TestScore(0.85)
        
        assert score1 == score2
    
    def test_value_objects_not_equal_with_different_values(self):
        """Test value objects are not equal when components differ"""
        score1 = TestScore(0.85)
        score2 = TestScore(0.90)
        
        assert score1 != score2
    
    def test_value_objects_equal_with_multiple_components(self):
        """Test equality with multiple components"""
        person1 = TestPerson("John", "Doe")
        person2 = TestPerson("John", "Doe")
        
        assert person1 == person2
    
    def test_value_objects_not_equal_with_different_components(self):
        """Test inequality when any component differs"""
        person1 = TestPerson("John", "Doe")
        person2 = TestPerson("Jane", "Doe")
        
        assert person1 != person2
    
    def test_value_objects_not_equal_to_different_types(self):
        """Test value objects not equal to different types"""
        score = TestScore(0.85)
        
        # Python's default equality allows comparison with different types
        # Value object should not equal primitives
        assert not (score == 0.85)
        assert not (score == "0.85")
        assert not (score == None)
    
    def test_value_objects_have_consistent_hash(self):
        """Test value objects with same values have same hash"""
        score1 = TestScore(0.85)
        score2 = TestScore(0.85)
        
        assert hash(score1) == hash(score2)
    
    def test_value_objects_can_be_used_in_sets(self):
        """Test value objects work correctly in sets"""
        scores = {
            TestScore(0.85),
            TestScore(0.90),
            TestScore(0.85),  # Duplicate
        }
        
        assert len(scores) == 2  # Duplicate removed
    
    def test_value_objects_can_be_used_as_dict_keys(self):
        """Test value objects work correctly as dict keys"""
        score_map = {
            TestScore(0.85): "High",
            TestScore(0.50): "Medium",
        }
        
        assert score_map[TestScore(0.85)] == "High"
        assert score_map[TestScore(0.50)] == "Medium"
    
    def test_value_objects_are_immutable(self):
        """Test value objects cannot be modified (frozen)"""
        score = TestScore(0.85)
        
        with pytest.raises(AttributeError):
            score.value = 0.90  # Should raise error
