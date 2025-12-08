"""
Business Capability Detector - Phase 7.4.1
Generates business narratives from code without documentation

Features:
- Entity extraction from class names (domain models)
- Pattern detection for business capabilities
- Confidence scoring (🟢 High 90%+, 🟡 Medium 60-89%, 🔴 Low 30-59%)
- Multi-language support (Python, C#, TypeScript, SQL, ColdFusion)
"""

import ast
import re
from typing import Dict, List, Set, Any
from collections import defaultdict


class BusinessCapabilityDetector:
    """Detects business capabilities from code using AST and pattern matching"""
    
    # Business pattern keywords
    BUSINESS_PATTERNS = {
        'authentication': ['login', 'authenticate', 'signin', 'authorize', 'jwt', 'token', 'auth', 'session'],
        'payment': ['payment', 'charge', 'invoice', 'billing', 'transaction', 'stripe', 'paypal', 'credit', 'checkout'],
        'reporting': ['report', 'analytics', 'dashboard', 'export', 'pdf', 'excel', 'chart', 'graph'],
        'email': ['email', 'notification', 'sendgrid', 'smtp', 'mailgun', 'mail', 'message'],
        'file_upload': ['upload', 'file', 'attachment', 's3', 'blob', 'storage', 'download'],
        'api': ['api', 'endpoint', 'rest', 'graphql', 'controller', 'route'],
        'database': ['database', 'sql', 'query', 'repository', 'dao', 'orm'],
        'security': ['security', 'encrypt', 'decrypt', 'hash', 'csrf', 'xss'],
    }
    
    # Domain entity keywords
    DOMAIN_ENTITIES = ['user', 'product', 'order', 'payment', 'customer', 'invoice', 
                      'account', 'transaction', 'item', 'cart', 'session']
    
    # Business value mapping
    VALUE_KEYWORDS = {
        'critical': ['payment', 'auth', 'security', 'checkout', 'transaction'],
        'high': ['order', 'user', 'customer', 'invoice', 'billing'],
        'medium': ['report', 'notification', 'email', 'file'],
        'low': ['log', 'utility', 'helper']
    }
    
    def __init__(self):
        """Initialize detector"""
        pass
    
    def extract_entities(self, code: str, language: str = 'python') -> List[str]:
        """
        Extract domain entities from class names
        
        Args:
            code: Source code string
            language: Programming language (python, csharp, typescript, sql, coldfusion)
            
        Returns:
            List of entity names
        """
        entities = set()
        
        if language == 'python':
            entities = self._extract_python_entities(code)
        elif language == 'csharp':
            entities = self._extract_csharp_entities(code)
        elif language == 'typescript':
            entities = self._extract_typescript_entities(code)
        elif language == 'sql':
            entities = self._extract_sql_entities(code)
        elif language == 'coldfusion':
            entities = self._extract_coldfusion_entities(code)
        
        return list(entities)
    
    def _extract_python_entities(self, code: str) -> Set[str]:
        """Extract entities from Python code using AST"""
        entities = set()
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Extract base class name (remove Service, Controller, etc.)
                    name = node.name
                    base_name = re.sub(r'(Service|Controller|Manager|Handler|Repository|Dao)$', '', name)
                    if base_name:
                        entities.add(base_name)
                    else:
                        entities.add(name)
        except SyntaxError:
            pass
        
        return entities
    
    def _extract_csharp_entities(self, code: str) -> Set[str]:
        """Extract entities from C# code using regex"""
        entities = set()
        
        # Match: public class ClassName
        pattern = r'(?:public|private|internal)?\s+class\s+(\w+)'
        matches = re.finditer(pattern, code)
        
        for match in matches:
            name = match.group(1)
            base_name = re.sub(r'(Service|Controller|Manager|Handler|Repository)$', '', name)
            if base_name:
                entities.add(base_name)
            else:
                entities.add(name)
        
        return entities
    
    def _extract_typescript_entities(self, code: str) -> Set[str]:
        """Extract entities from TypeScript code"""
        entities = set()
        
        # Match: class ClassName, export class ClassName
        pattern = r'(?:export\s+)?class\s+(\w+)'
        matches = re.finditer(pattern, code)
        
        for match in matches:
            name = match.group(1)
            base_name = re.sub(r'(Service|Controller|Manager|Handler|Repository)$', '', name)
            if base_name:
                entities.add(base_name)
            else:
                entities.add(name)
        
        return entities
    
    def _extract_sql_entities(self, code: str) -> Set[str]:
        """Extract entities from SQL table names"""
        entities = set()
        
        # Match: FROM TableName, JOIN TableName, UPDATE TableName, INSERT INTO TableName
        patterns = [
            r'FROM\s+(\w+)',
            r'JOIN\s+(\w+)',
            r'UPDATE\s+(\w+)',
            r'INSERT\s+INTO\s+(\w+)',
            r'CREATE\s+TABLE\s+(\w+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                entities.add(match.group(1))
        
        return entities
    
    def _extract_coldfusion_entities(self, code: str) -> Set[str]:
        """Extract entities from ColdFusion components"""
        entities = set()
        
        # Match: <cfcomponent name="ComponentName">
        pattern = r'<cfcomponent\s+name="(\w+)"'
        matches = re.finditer(pattern, code, re.IGNORECASE)
        
        for match in matches:
            name = match.group(1)
            base_name = re.sub(r'(Service|Controller|Manager|Handler)$', '', name)
            if base_name:
                entities.add(base_name)
            else:
                entities.add(name)
        
        return entities
    
    def detect_patterns(self, code: str, language: str = 'python') -> Dict[str, List[str]]:
        """
        Detect business capability patterns in code
        
        Args:
            code: Source code string
            language: Programming language
            
        Returns:
            Dict mapping pattern names to evidence list
        """
        patterns = defaultdict(list)
        code_lower = code.lower()
        
        # Extract method/function names
        methods = self._extract_methods(code, language)
        
        # Check each pattern
        for pattern_name, keywords in self.BUSINESS_PATTERNS.items():
            for keyword in keywords:
                # Check in code
                if keyword in code_lower:
                    patterns[pattern_name].append(keyword)
                
                # Check in method names
                for method in methods:
                    if keyword in method.lower():
                        patterns[pattern_name].append(method)
        
        # Remove duplicates
        return {k: list(set(v)) for k, v in patterns.items() if v}
    
    def _extract_methods(self, code: str, language: str) -> List[str]:
        """Extract method/function names from code"""
        methods = []
        
        if language == 'python':
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        methods.append(node.name)
            except SyntaxError:
                pass
        
        elif language in ['csharp', 'typescript']:
            # Match: void MethodName(), public string MethodName()
            pattern = r'(?:public|private|protected)?\s*(?:\w+\s+)?(\w+)\s*\([^)]*\)\s*\{'
            matches = re.finditer(pattern, code)
            for match in matches:
                methods.append(match.group(1))
        
        elif language == 'sql':
            # Match: CREATE PROCEDURE ProcedureName
            pattern = r'CREATE\s+PROCEDURE\s+(\w+)'
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                methods.append(match.group(1))
        
        elif language == 'coldfusion':
            # Match: <cffunction name="FunctionName">
            pattern = r'<cffunction\s+name="(\w+)"'
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                methods.append(match.group(1))
        
        return methods
    
    def calculate_confidence(self, evidence: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on evidence strength
        
        Args:
            evidence: Dict with entities, methods, patterns, endpoints
            
        Returns:
            Confidence score 0-100
        """
        score = 31.0  # Base score to ensure minimum 30 for any evidence
        
        # Entity evidence (30 points max)
        entity_count = len(evidence.get('entities', []))
        score += min(entity_count * 10, 30)
        
        # Method evidence (28 points max)
        method_count = len(evidence.get('methods', []))
        score += min(method_count * 7, 28)
        
        # Pattern evidence (10 points max)
        pattern_count = len(evidence.get('patterns', []))
        score += min(pattern_count * 5, 10)
        
        # Endpoint evidence (1 point max)
        endpoint_count = len(evidence.get('endpoints', []))
        score += min(endpoint_count * 0.5, 1)
        
        return min(score, 100.0)
    
    def get_confidence_emoji(self, confidence: float) -> str:
        """
        Get emoji indicator for confidence level
        
        Args:
            confidence: Confidence score 0-100
            
        Returns:
            Emoji string (🟢/🟡/🔴)
        """
        if confidence >= 90:
            return '🟢'  # High
        elif confidence >= 60:
            return '🟡'  # Medium
        else:
            return '🔴'  # Low
    
    def _determine_business_value(self, patterns: List[str], entities: List[str]) -> str:
        """Determine business value level based on patterns and entities"""
        all_text = ' '.join(patterns + entities).lower()
        
        # Check critical first
        for keyword in self.VALUE_KEYWORDS['critical']:
            if keyword in all_text:
                return 'critical'
        
        # Then high
        for keyword in self.VALUE_KEYWORDS['high']:
            if keyword in all_text:
                return 'high'
        
        # Then medium
        for keyword in self.VALUE_KEYWORDS['medium']:
            if keyword in all_text:
                return 'medium'
        
        # Default low
        return 'low'
    
    def analyze(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """
        Complete business capability analysis
        
        Args:
            code: Source code string
            language: Programming language
            
        Returns:
            Dict with capabilities and summary
        """
        if not code or not code.strip():
            return {
                'capabilities': [],
                'summary': {
                    'total_capabilities': 0,
                    'high_confidence': 0,
                    'domain_models': []
                }
            }
        
        # Extract data
        entities = self.extract_entities(code, language)
        patterns = self.detect_patterns(code, language)
        methods = self._extract_methods(code, language)
        
        # Build capabilities
        capabilities = []
        
        # Group by pattern
        for pattern_name, pattern_evidence in patterns.items():
            evidence = {
                'entities': entities,
                'methods': [m for m in methods if any(kw in m.lower() for kw in pattern_evidence)],
                'patterns': [pattern_name],
                'endpoints': []  # Would be extracted from route decorators/annotations
            }
            
            confidence = self.calculate_confidence(evidence)
            
            capability = {
                'name': pattern_name.replace('_', ' ').title(),
                'confidence': round(confidence, 1),
                'evidence': pattern_evidence[:5],  # Top 5 evidence items
                'patterns': [pattern_name],
                'entities': entities[:3] if entities else [],  # Top 3 entities
                'business_value': self._determine_business_value([pattern_name], entities)
            }
            
            if confidence >= 30:  # Only include if at least low confidence
                capabilities.append(capability)
        
        # Calculate summary
        high_confidence = sum(1 for c in capabilities if c['confidence'] >= 90)
        
        return {
            'capabilities': capabilities,
            'summary': {
                'total_capabilities': len(capabilities),
                'high_confidence': high_confidence,
                'domain_models': entities
            }
        }
