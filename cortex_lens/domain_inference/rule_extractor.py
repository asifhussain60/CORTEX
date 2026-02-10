"""
Business Rule Extractor

Extracts validation logic, constraints, and business rules from code.

Author: CORTEX Architect
Phase: Phase 66 S3
"""

import logging
import re
import ast
from typing import List, Dict, Set, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class RuleExtractor:
    """
    Extracts business rules and validation logic from code.
    
    Capabilities:
    - Extract rules from @validator decorators (Pydantic)
    - Parse if/raise patterns for constraints
    - Identify business logic from method implementations
    - Detect class invariants
    - Categorize rules by type (format, range, business, etc.)
    
    Example:
        extractor = RuleExtractor()
        
        # Extract from validators
        rules = extractor.extract_from_validators(code)
        # Returns: [{"field": "email", "description": "Must contain @", ...}]
        
        # Extract from conditions
        rules = extractor.extract_from_conditions(code)
        # Returns: [{"description": "Minimum order value is $10", ...}]
    """
    
    def __init__(self):
        """Initialize rule extractor"""
        self.rule_patterns = {
            "format": r"(format|pattern|regex|contains|@|starts|ends|email|must contain)",
            "range": r"(min|max|between|greater|less|range|>=|<=|>|<)",
            "required": r"(required|mandatory|must have|cannot be empty)",
            "unique": r"(unique|duplicate|already exists)",
            "reference": r"(exist|valid|found|reference)"
        }
        logger.debug("Initialized RuleExtractor")
    
    def extract_from_validators(self, code: str) -> List[Dict[str, Any]]:
        """
        Extract rules from @validator decorators.
        
        Args:
            code: Python code containing validator decorators
        
        Returns:
            List of rule dictionaries
        
        Example:
            code = '''
            @validator('email')
            def validate_email(cls, v):
                if '@' not in v:
                    raise ValueError('Invalid email')
                return v
            '''
            Returns: [{"field": "email", "description": "Invalid email", ...}]
        """
        logger.debug("Extracting rules from validators")
        
        rules = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for @validator decorator
                    for decorator in node.decorator_list:
                        if self._is_validator_decorator(decorator):
                            field_name = self._extract_field_from_decorator(decorator)
                            
                            if field_name:
                                # Extract rule from function body
                                rule = self._extract_rule_from_function(node, field_name)
                                if rule:
                                    rules.append(rule)
        
        except SyntaxError as e:
            logger.warning(f"Failed to parse code: {e}")
        
        logger.debug(f"Extracted {len(rules)} validator rules")
        return rules
    
    def _is_validator_decorator(self, decorator: ast.expr) -> bool:
        """Check if decorator is a validator"""
        if isinstance(decorator, ast.Name):
            return decorator.id in ["validator", "field_validator"]
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id in ["validator", "field_validator"]
        return False
    
    def _extract_field_from_decorator(self, decorator: ast.expr) -> Optional[str]:
        """Extract field name from @validator('field_name')"""
        if isinstance(decorator, ast.Call):
            if decorator.args and len(decorator.args) > 0:
                arg = decorator.args[0]
                if isinstance(arg, ast.Constant):
                    return str(arg.value)
        return None
    
    def _extract_rule_from_function(
        self, 
        func: ast.FunctionDef, 
        field: str
    ) -> Optional[Dict[str, Any]]:
        """Extract rule description from validator function body"""
        rule = {
            "field": field,
            "rule_type": "validation",
            "description": "",
            "confidence": 0.7,
            "source": "validator_decorator"
        }
        
        # Look for raise statements with error messages
        for node in ast.walk(func):
            if isinstance(node, ast.Raise):
                if isinstance(node.exc, ast.Call):
                    # Get error message from ValueError('message')
                    if node.exc.args and len(node.exc.args) > 0:
                        arg = node.exc.args[0]
                        if isinstance(arg, ast.Constant):
                            rule["description"] = str(arg.value)
                            rule["confidence"] = 0.9
                            return rule
        
        # Fallback: use function docstring
        docstring = ast.get_docstring(func)
        if docstring:
            rule["description"] = docstring
            rule["confidence"] = 0.6
            return rule
        
        # Fallback: generic description
        rule["description"] = f"Validation rule for {field}"
        rule["confidence"] = 0.5
        return rule
    
    def extract_from_conditions(self, code: str) -> List[Dict[str, Any]]:
        """
        Extract constraints from if/raise patterns.
        
        Args:
            code: Python code with conditional validation
        
        Returns:
            List of constraint dictionaries
        
        Example:
            code = '''
            if order.total < 10:
                raise ValueError("Minimum order is $10")
            '''
            Returns: [{"description": "Minimum order is $10", ...}]
        """
        logger.debug("Extracting rules from conditions")
        
        rules = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    # Check if body contains raise statement
                    for stmt in node.body:
                        if isinstance(stmt, ast.Raise):
                            rule = self._extract_rule_from_if_raise(node, stmt)
                            if rule:
                                rules.append(rule)
        
        except SyntaxError as e:
            logger.warning(f"Failed to parse code: {e}")
        
        logger.debug(f"Extracted {len(rules)} condition rules")
        return rules
    
    def _extract_rule_from_if_raise(
        self, 
        if_node: ast.If, 
        raise_node: ast.Raise
    ) -> Optional[Dict[str, Any]]:
        """Extract rule from if/raise pattern"""
        rule = {
            "rule_type": "constraint",
            "description": "",
            "confidence": 0.7,
            "source": "if_raise_pattern"
        }
        
        # Extract error message
        if isinstance(raise_node.exc, ast.Call):
            if raise_node.exc.args and len(raise_node.exc.args) > 0:
                arg = raise_node.exc.args[0]
                if isinstance(arg, ast.Constant):
                    rule["description"] = str(arg.value)
                    rule["confidence"] = 0.8
                    
                    # Try to extract entity from condition
                    entity = self._extract_entity_from_condition(if_node.test)
                    if entity:
                        rule["entity"] = entity
                    
                    return rule
        
        return None
    
    def _extract_entity_from_condition(self, condition: ast.expr) -> Optional[str]:
        """Extract entity name from condition (e.g., 'order' from 'order.total')"""
        if isinstance(condition, ast.Compare):
            if isinstance(condition.left, ast.Attribute):
                if isinstance(condition.left.value, ast.Name):
                    # Capitalize first letter for entity name
                    return condition.left.value.id.capitalize()
        return None
    
    def extract_business_logic(self, code: str) -> List[Dict[str, Any]]:
        """
        Extract business logic from method implementations.
        
        Args:
            code: Python code with business logic
        
        Returns:
            List of business logic rules
        
        Example:
            code = '''
            def calculate_discount(self, order):
                if order.total > 1000:
                    return order.total * 0.15
            '''
            Returns: [{"description": "15% discount for orders > $1000", ...}]
        """
        logger.debug("Extracting business logic")
        
        rules = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Look for methods with business logic keywords
                    if any(keyword in node.name.lower() for keyword in ["calculate", "apply", "process", "determine"]):
                        rule = self._extract_logic_from_method(node)
                        if rule:
                            rules.append(rule)
        
        except SyntaxError as e:
            logger.warning(f"Failed to parse code: {e}")
        
        logger.debug(f"Extracted {len(rules)} business logic rules")
        return rules
    
    def _extract_logic_from_method(self, func: ast.FunctionDef) -> Optional[Dict[str, Any]]:
        """Extract business logic from method"""
        rule = {
            "rule_type": "business_logic",
            "description": "",
            "confidence": 0.6,
            "source": "method_implementation"
        }
        
        # Use docstring as description
        docstring = ast.get_docstring(func)
        if docstring:
            rule["description"] = docstring
            rule["confidence"] = 0.7
        else:
            # Generic description from method name
            rule["description"] = f"Business logic: {func.name.replace('_', ' ')}"
        
        # Try to extract entity from parameters
        if func.args.args and len(func.args.args) > 1:
            # Skip 'self' parameter
            param = func.args.args[1]
            if hasattr(param, 'arg'):
                rule["entity"] = param.arg.capitalize()
        
        return rule
    
    def extract_invariants(self, code: str) -> List[Dict[str, Any]]:
        """
        Detect class invariants from assertions and constraints.
        
        Args:
            code: Python code with class definitions
        
        Returns:
            List of invariant dictionaries
        
        Example:
            code = '''
            def __init__(self, balance):
                assert balance >= 0, "Balance cannot be negative"
            '''
            Returns: [{"description": "Balance cannot be negative", ...}]
        """
        logger.debug("Extracting invariants")
        
        invariants = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assert):
                    invariant = self._extract_invariant_from_assert(node)
                    if invariant:
                        invariants.append(invariant)
        
        except SyntaxError as e:
            logger.warning(f"Failed to parse code: {e}")
        
        logger.debug(f"Extracted {len(invariants)} invariants")
        return invariants
    
    def _extract_invariant_from_assert(self, assert_node: ast.Assert) -> Optional[Dict[str, Any]]:
        """Extract invariant from assert statement"""
        invariant = {
            "rule_type": "invariant",
            "description": "",
            "confidence": 0.8,
            "source": "assert_statement"
        }
        
        # Extract message from assert
        if assert_node.msg:
            if isinstance(assert_node.msg, ast.Constant):
                invariant["description"] = str(assert_node.msg.value)
                return invariant
        
        return None
    
    def categorize_rules(self, rules: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize rules by type based on description.
        
        Args:
            rules: List of rule dictionaries
        
        Returns:
            Dictionary mapping category to rules
        
        Example:
            Input: [{"description": "Email must contain @"}]
            Output: {"format": [{"description": "Email must contain @"}]}
        """
        logger.debug(f"Categorizing {len(rules)} rules")
        
        categorized: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        for rule in rules:
            description = rule.get("description", "").lower()
            
            # Check each category pattern
            category_found = False
            for category, pattern in self.rule_patterns.items():
                if re.search(pattern, description):
                    categorized[category].append(rule)
                    category_found = True
                    break
            
            # Default category
            if not category_found:
                categorized["general"].append(rule)
        
        logger.debug(f"Categorized into {len(categorized)} categories")
        return dict(categorized)
    
    def calculate_confidence(self, signals: Dict[str, Any]) -> float:
        """
        Calculate confidence score for extracted rule.
        
        Weighted signals:
        - Has decorator: 0.3
        - Has error message: 0.3
        - Has documentation: 0.2
        - Complexity (simple/complex): 0.2
        
        Args:
            signals: Dictionary of detection signals
        
        Returns:
            Confidence score in [0.0, 1.0]
        """
        score = 0.0
        
        # Decorator presence
        if signals.get("has_decorator"):
            score += 0.3
        
        # Error message
        if signals.get("has_error_message"):
            score += 0.3
        
        # Documentation
        if signals.get("has_documentation"):
            score += 0.2
        
        # Complexity
        complexity = signals.get("complexity", "medium")
        if complexity == "simple":
            score += 0.2
        elif complexity == "medium":
            score += 0.1
        
        # Clamp to [0.0, 1.0]
        confidence = max(0.0, min(1.0, score))
        
        logger.debug(f"Calculated confidence: {confidence:.2f}")
        return confidence
