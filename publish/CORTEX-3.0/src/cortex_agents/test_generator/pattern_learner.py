"""
Pattern Learning System

Extracts business logic patterns from existing test suites and classifies them
for intelligent test generation.

Copyright (c) 2024-2025 Asif Hussain. All rights reserved.
"""

import ast
import re
from typing import List, Dict, Set, Optional, Any
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import logging

from .tier2_pattern_store import BusinessPattern, Tier2PatternStore


@dataclass
class ExtractedPattern:
    """Pattern extracted from existing tests"""
    domain: str
    operation: str
    pattern_type: str
    description: str
    assertion_template: str
    source_file: str
    source_function: str


class PatternLearner:
    """
    Learns business logic patterns from existing test suites.
    
    Features:
    - AST-based test analysis
    - Domain classification
    - Assertion extraction
    - Confidence scoring
    - Legacy Tier 2 KG compatibility
    """
    
    # Domain keywords for classification
    DOMAIN_KEYWORDS = {
        'authentication': {'login', 'logout', 'auth', 'token', 'session', 'password', 'user', 'signin', 'signout'},
        'validation': {'validate', 'check', 'verify', 'ensure', 'sanitize', 'clean', 'format'},
        'calculation': {'calculate', 'compute', 'sum', 'total', 'average', 'count', 'multiply', 'divide'},
        'data_access': {'get', 'fetch', 'load', 'retrieve', 'query', 'find', 'search'},
        'data_mutation': {'create', 'update', 'delete', 'insert', 'modify', 'save', 'store'},
        'authorization': {'permit', 'allow', 'deny', 'grant', 'revoke', 'access', 'permission', 'role'},
        'notification': {'send', 'notify', 'email', 'alert', 'message', 'publish'},
        'file_operations': {'read', 'write', 'file', 'path', 'directory', 'upload', 'download'}
    }
    
    def __init__(self, pattern_store: Optional[Tier2PatternStore] = None, tier2_kg=None):
        """
        Initialize pattern learner.
        
        Args:
            pattern_store: Tier 2 pattern storage (new system)
            tier2_kg: Legacy Tier 2 knowledge graph (backward compatibility)
        """
        self.pattern_store = pattern_store
        self.tier2 = tier2_kg
        self.logger = logging.getLogger(__name__)
    
    def learn_from_test_file(self, test_file_path: str) -> List[ExtractedPattern]:
        """
        Extract patterns from a test file.
        
        Args:
            test_file_path: Path to test file
            
        Returns:
            List of extracted patterns
        """
        with open(test_file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []
        
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                extracted = self._extract_patterns_from_test(node, test_file_path)
                patterns.extend(extracted)
        
        return patterns
    
    def _extract_patterns_from_test(
        self,
        test_func: ast.FunctionDef,
        source_file: str
    ) -> List[ExtractedPattern]:
        """
        Extract patterns from a test function.
        
        Args:
            test_func: Test function AST node
            source_file: Source file path
            
        Returns:
            List of extracted patterns
        """
        patterns = []
        
        # Infer domain from test name
        domain = self._infer_domain(test_func.name)
        
        # Extract operation from test name
        # e.g., test_user_login -> login
        operation = self._extract_operation(test_func.name)
        
        # Extract assertions
        assertions = self._extract_assertions(test_func)
        
        for assertion in assertions:
            pattern = ExtractedPattern(
                domain=domain,
                operation=operation,
                pattern_type=assertion['type'],
                description=assertion['description'],
                assertion_template=assertion['template'],
                source_file=source_file,
                source_function=test_func.name
            )
            patterns.append(pattern)
        
        return patterns
    
    def _infer_domain(self, test_name: str) -> str:
        """
        Infer domain from test name using keyword matching.
        
        Args:
            test_name: Test function name
            
        Returns:
            Domain name (or 'general' if no match)
        """
        test_name_lower = test_name.lower()
        
        scores = {}
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in test_name_lower)
            if score > 0:
                scores[domain] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return 'general'
    
    def _extract_operation(self, test_name: str) -> str:
        """
        Extract operation name from test name.
        
        Args:
            test_name: Test function name (e.g., test_user_login_success)
            
        Returns:
            Operation name (e.g., login)
        """
        # Remove 'test_' prefix
        name = test_name.replace('test_', '')
        
        # Extract main operation (usually first or second word)
        words = re.findall(r'[a-z]+', name.lower())
        
        if len(words) >= 2:
            # Skip generic first words
            if words[0] in {'user', 'admin', 'system', 'data'}:
                return words[1]
            return words[0]
        elif words:
            return words[0]
        
        return 'unknown'
    
    def _extract_assertions(self, test_func: ast.FunctionDef) -> List[Dict]:
        """
        Extract assertion patterns from test function.
        
        Args:
            test_func: Test function AST node
            
        Returns:
            List of assertion patterns
        """
        assertions = []
        
        for node in ast.walk(test_func):
            # assert statements
            if isinstance(node, ast.Assert):
                assertion = self._analyze_assertion(node)
                if assertion:
                    assertions.append(assertion)
            
            # pytest.raises
            elif isinstance(node, ast.With):
                for item in node.items:
                    if isinstance(item.context_expr, ast.Call):
                        if self._is_pytest_raises(item.context_expr):
                            assertions.append({
                                'type': 'exception',
                                'description': 'Expects specific exception',
                                'template': 'with pytest.raises(ExceptionType):'
                            })
        
        return assertions
    
    def _analyze_assertion(self, assert_node: ast.Assert) -> Optional[Dict]:
        """
        Analyze an assert statement.
        
        Args:
            assert_node: Assert AST node
            
        Returns:
            Assertion pattern or None
        """
        test = assert_node.test
        
        # assert result == expected
        if isinstance(test, ast.Compare):
            if isinstance(test.ops[0], ast.Eq):
                return {
                    'type': 'equality',
                    'description': 'Checks exact equality',
                    'template': 'assert result == expected'
                }
            elif isinstance(test.ops[0], (ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
                return {
                    'type': 'range',
                    'description': 'Checks value within range',
                    'template': 'assert value >= min_value'
                }
            elif isinstance(test.ops[0], ast.In):
                return {
                    'type': 'membership',
                    'description': 'Checks membership in collection',
                    'template': 'assert item in collection'
                }
            elif isinstance(test.ops[0], ast.Is):
                return {
                    'type': 'identity',
                    'description': 'Checks object identity',
                    'template': 'assert result is not None'
                }
        
        # assert result (truthy check)
        elif isinstance(test, ast.Name):
            return {
                'type': 'truthy',
                'description': 'Checks truthy value',
                'template': 'assert result'
            }
        
        # assert not result
        elif isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            return {
                'type': 'falsy',
                'description': 'Checks falsy value',
                'template': 'assert not result'
            }
        
        # assert isinstance(result, Type)
        elif isinstance(test, ast.Call):
            if isinstance(test.func, ast.Name) and test.func.id == 'isinstance':
                return {
                    'type': 'type_check',
                    'description': 'Checks type of result',
                    'template': 'assert isinstance(result, ExpectedType)'
                }
        
        return None
    
    def _is_pytest_raises(self, call_node: ast.Call) -> bool:
        """Check if call is pytest.raises"""
        if isinstance(call_node.func, ast.Attribute):
            if call_node.func.attr == 'raises':
                if isinstance(call_node.func.value, ast.Name):
                    return call_node.func.value.id == 'pytest'
        return False
    
    def store_learned_patterns(
        self,
        extracted_patterns: List[ExtractedPattern],
        initial_confidence: float = 0.5
    ) -> int:
        """
        Store learned patterns in Tier 2 storage.
        
        Args:
            extracted_patterns: Patterns to store
            initial_confidence: Initial confidence score
            
        Returns:
            Number of patterns stored
        """
        if not self.pattern_store:
            return 0
        
        stored = 0
        
        for pattern in extracted_patterns:
            business_pattern = BusinessPattern(
                pattern_id=None,
                domain=pattern.domain,
                operation=pattern.operation,
                pattern_type=pattern.pattern_type,
                description=pattern.description,
                assertion_template=pattern.assertion_template,
                confidence=initial_confidence,
                usage_count=0,
                success_count=0,
                created_at=datetime.now().isoformat(),
                last_used=None,
                metadata={
                    'source_file': pattern.source_file,
                    'source_function': pattern.source_function,
                    'learned': True
                }
            )
            
            self.pattern_store.store_pattern(business_pattern)
            stored += 1
        
        return stored
    
    def learn_from_directory(
        self,
        test_dir: str,
        pattern: str = "test_*.py"
    ) -> Dict:
        """
        Learn patterns from all test files in a directory.
        
        Args:
            test_dir: Directory containing tests
            pattern: File pattern to match
            
        Returns:
            Learning statistics
        """
        test_dir_path = Path(test_dir)
        test_files = list(test_dir_path.rglob(pattern))
        
        total_patterns = 0
        patterns_by_domain = {}
        
        for test_file in test_files:
            extracted = self.learn_from_test_file(str(test_file))
            
            for pattern in extracted:
                domain = pattern.domain
                patterns_by_domain[domain] = patterns_by_domain.get(domain, 0) + 1
            
            stored = self.store_learned_patterns(extracted)
            total_patterns += stored
        
        return {
            'files_processed': len(test_files),
            'patterns_learned': total_patterns,
            'patterns_by_domain': patterns_by_domain
        }
    
    # Legacy methods for backward compatibility
    def find_similar_patterns(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Legacy method for Tier 2 KG compatibility"""
        if not self.tier2:
            return []
        
        try:
            patterns = []
            for func in analysis.get("functions", []):
                query = f"test pattern for function with {func['arg_count']} arguments"
            return patterns
        except Exception as e:
            self.logger.error(f"Failed to search test patterns: {str(e)}")
            return []
    
    def store_pattern(self, analysis: Dict[str, Any], test_code: str, test_count: int) -> None:
        """Legacy method for Tier 2 KG compatibility"""
        if not self.tier2:
            return
        
        try:
            pattern_data = {
                "type": "test_generation",
                "functions": len(analysis.get("functions", [])),
                "classes": len(analysis.get("classes", [])),
                "test_count": test_count,
                "scenarios": analysis.get("scenarios", []),
                "timestamp": datetime.now().isoformat()
            }
            self.logger.debug(f"Storing test pattern: {pattern_data}")
        except Exception as e:
            self.logger.error(f"Failed to store pattern: {str(e)}")
