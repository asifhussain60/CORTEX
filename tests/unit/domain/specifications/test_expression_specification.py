"""
Tests for expression-based specifications.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import pytest
from dataclasses import dataclass
from src.domain.specifications import ExpressionSpecification


@dataclass
class Product:
    """Test entity."""
    name: str
    price: float
    in_stock: bool = True


class TestExpressionSpecification:
    """Tests for expression-based specifications."""
    
    def test_simple_expression(self):
        """Test specification with simple lambda expression."""
        spec = ExpressionSpecification(lambda p: p.price > 100)
        
        product = Product("Laptop", 1200, True)
        assert spec.is_satisfied_by(product) is True
        
        product = Product("Mouse", 25, True)
        assert spec.is_satisfied_by(product) is False
    
    def test_expression_with_description(self):
        """Test specification with description."""
        spec = ExpressionSpecification(
            lambda p: p.price > 100,
            description="Expensive products"
        )
        
        assert "Expensive products" in repr(spec)
    
    def test_complex_expression(self):
        """Test specification with complex expression."""
        spec = ExpressionSpecification(
            lambda p: p.price > 50 and p.price < 500 and p.in_stock
        )
        
        # In range and in stock
        assert spec.is_satisfied_by(Product("Widget", 100, True)) is True
        
        # Too cheap
        assert spec.is_satisfied_by(Product("Cheap", 10, True)) is False
        
        # Too expensive
        assert spec.is_satisfied_by(Product("Expensive", 1000, True)) is False
        
        # Out of stock
        assert spec.is_satisfied_by(Product("Widget", 100, False)) is False
    
    def test_expression_with_exception(self):
        """Test specification handles exceptions gracefully."""
        spec = ExpressionSpecification(lambda p: p.nonexistent_field > 0)
        
        product = Product("Test", 100)
        # Should return False instead of raising exception
        assert spec.is_satisfied_by(product) is False
    
    def test_expression_composition(self):
        """Test expression specifications can be composed."""
        expensive = ExpressionSpecification(lambda p: p.price > 100)
        in_stock = ExpressionSpecification(lambda p: p.in_stock)
        
        spec = expensive & in_stock
        
        # Both conditions met
        assert spec.is_satisfied_by(Product("Laptop", 1200, True)) is True
        
        # Only first condition met
        assert spec.is_satisfied_by(Product("Laptop", 1200, False)) is False
        
        # Only second condition met
        assert spec.is_satisfied_by(Product("Mouse", 25, True)) is False
    
    def test_expression_with_string_operations(self):
        """Test expression with string operations."""
        spec = ExpressionSpecification(lambda p: "Laptop" in p.name)
        
        assert spec.is_satisfied_by(Product("Gaming Laptop", 1500)) is True
        assert spec.is_satisfied_by(Product("Mouse", 25)) is False
    
    def test_expression_with_multiple_conditions(self):
        """Test expression with multiple conditions using logical operators."""
        spec = ExpressionSpecification(
            lambda p: (p.price > 1000 or p.name.startswith("Premium")) and p.in_stock
        )
        
        # Expensive and in stock
        assert spec.is_satisfied_by(Product("Laptop", 1500, True)) is True
        
        # Premium name and in stock
        assert spec.is_satisfied_by(Product("Premium Mouse", 50, True)) is True
        
        # Expensive but out of stock
        assert spec.is_satisfied_by(Product("Laptop", 1500, False)) is False
        
        # Neither condition met
        assert spec.is_satisfied_by(Product("Mouse", 25, True)) is False
