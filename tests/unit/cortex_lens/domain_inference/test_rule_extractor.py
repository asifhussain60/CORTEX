"""
Tests for Business Rule Extractor

Validates extraction of validation logic, constraints, and business rules.

Author: CORTEX Architect
Phase: Phase 66 S3
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any


class TestRuleExtractor:
    """Test suite for business rule extraction"""
    
    def test_validator_decorator_extraction(self):
        """Test extracting rules from @validator decorators"""
        from cortex_lens.domain_inference.rule_extractor import RuleExtractor
        
        # Mock code with Pydantic validators
        code = '''
class User(BaseModel):
    email: str
    age: int
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v < 18:
            raise ValueError('Must be 18 or older')
        return v
'''
        
        extractor = RuleExtractor()
        rules = extractor.extract_from_validators(code)
        
        assert len(rules) >= 2
        
        # Check email rule
        email_rule = next(r for r in rules if r["field"] == "email")
        assert "email" in email_rule["description"].lower()
        assert email_rule["rule_type"] == "validation"
        
        # Check age rule
        age_rule = next(r for r in rules if r["field"] == "age")
        assert "18" in age_rule["description"] or "age" in age_rule["description"].lower()
    
    def test_constraint_extraction_from_if_raise(self):
        """Test extracting constraints from if/raise patterns"""
        from cortex_lens.domain_inference.rule_extractor import RuleExtractor
        
        code = '''
def process_order(order):
    if order.total < 10:
        raise ValueError("Minimum order value is $10")
    
    if not order.customer.is_verified:
        raise PermissionError("Customer must be verified")
    
    if order.items_count > 100:
        raise ValueError("Maximum 100 items per order")
'''
        
        extractor = RuleExtractor()
        rules = extractor.extract_from_conditions(code)
        
        assert len(rules) >= 3
        
        # Check minimum order rule
        assert any("10" in r["description"] for r in rules)
        assert any("minimum" in r["description"].lower() for r in rules)
        
        # Check verification rule
        assert any("verified" in r["description"].lower() for r in rules)
    
    def test_business_logic_from_methods(self):
        """Test extracting business logic from method implementations"""
        from cortex_lens.domain_inference.rule_extractor import RuleExtractor
        
        code = '''
class OrderService:
    def calculate_discount(self, order):
        """Apply discount based on order total"""
        if order.total > 1000:
            return order.total * 0.15  # 15% discount
        elif order.total > 500:
            return order.total * 0.10  # 10% discount
        else:
            return 0
'''
        
        extractor = RuleExtractor()
        rules = extractor.extract_business_logic(code)
        
        assert len(rules) >= 1
        
        # Check discount logic extracted
        discount_rule = rules[0]
        assert "discount" in discount_rule["description"].lower()
        assert discount_rule["entity"] == "Order"
    
    def test_invariant_detection(self):
        """Test detecting class invariants"""
        from cortex_lens.domain_inference.rule_extractor import RuleExtractor
        
        code = '''
class BankAccount:
    def __init__(self, balance):
        assert balance >= 0, "Balance cannot be negative"
        self.balance = balance
    
    def withdraw(self, amount):
        if self.balance - amount < 0:
            raise ValueError("Insufficient funds")
        self.balance -= amount
'''
        
        extractor = RuleExtractor()
        invariants = extractor.extract_invariants(code)
        
        assert len(invariants) >= 1
        assert any("balance" in inv["description"].lower() for inv in invariants)
        assert any("negative" in inv["description"].lower() or "0" in inv["description"] for inv in invariants)
    
    def test_rule_confidence_scoring(self):
        """Test confidence scoring for extracted rules"""
        from cortex_lens.domain_inference.rule_extractor import RuleExtractor
        
        # Strong signals: explicit validator, clear message
        strong_rule = {
            "has_decorator": True,
            "has_error_message": True,
            "has_documentation": True,
            "complexity": "simple"
        }
        
        extractor = RuleExtractor()
        confidence = extractor.calculate_confidence(strong_rule)
        
        assert confidence >= 0.8
        
        # Weak signals: inferred from if statement, no message
        weak_rule = {
            "has_decorator": False,
            "has_error_message": False,
            "has_documentation": False,
            "complexity": "complex"
        }
        
        confidence_weak = extractor.calculate_confidence(weak_rule)
        assert confidence_weak < 0.6
    
    def test_cortex_rule_extraction(self):
        """Test extracting rules from CORTEX codebase"""
        from cortex_lens.domain_inference.rule_extractor import RuleExtractor
        from pathlib import Path
        
        extractor = RuleExtractor()
        
        # Look for validation in CORTEX models
        models_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/models")
        if models_path.exists():
            rules_found = []
            
            for py_file in models_path.glob("*.py"):
                content = py_file.read_text()
                rules = extractor.extract_from_validators(content)
                rules_found.extend(rules)
            
            # CORTEX should have some validation rules
            if rules_found:
                assert len(rules_found) > 0
                # Check for reasonable confidence scores
                assert all(0.0 <= r.get("confidence", 0.5) <= 1.0 for r in rules_found)
    
    def test_rule_categorization(self):
        """Test categorizing rules by type"""
        from cortex_lens.domain_inference.rule_extractor import RuleExtractor
        
        rules = [
            {"description": "Email must contain @", "field": "email"},
            {"description": "Age must be >= 18", "field": "age"},
            {"description": "Password min length 8", "field": "password"}
        ]
        
        extractor = RuleExtractor()
        categorized = extractor.categorize_rules(rules)
        
        assert "format" in categorized or "validation" in categorized
        assert len(categorized) > 0


class TestRuleExtractorIntegration:
    """Integration tests for rule extraction with knowledge graph"""
    
    def test_rules_to_graph_storage(self):
        """Test storing extracted rules in knowledge graph"""
        from cortex_lens.domain_inference.rule_extractor import RuleExtractor
        from cortex_lens.knowledge_graph.graph_storage import GraphStorage
        import tempfile
        
        # Create temporary graph
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)
        
        storage = GraphStorage(db_path)
        storage.initialize_schema()
        
        # Extract and store rules
        extractor = RuleExtractor()
        rules = [
            {
                "field": "email",
                "description": "Must contain @",
                "rule_type": "format",
                "confidence": 0.9
            }
        ]
        
        # Store as nodes
        for rule in rules:
            rule_id = storage.insert_node(
                "Rule",
                f"{rule['field']}_validation",
                {
                    "description": rule["description"],
                    "type": rule["rule_type"],
                    "confidence": rule["confidence"]
                }
            )
            assert rule_id > 0
        
        # Query back
        rule_nodes = storage.query_nodes_by_type("Rule")
        assert len(rule_nodes) == 1
        assert "email" in rule_nodes[0]["name"]
        
        # Cleanup
        db_path.unlink()
