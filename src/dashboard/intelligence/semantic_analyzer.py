"""
Semantic Analyzer - Phase 7.4.2
Generates human-readable narratives from business capabilities

Features:
- Method intent analysis (CRUD operations)
- Parameter analysis for business context
- Return type analysis for data flow
- Template-based narrative generation
- Multi-language support
"""

import ast
import re
from typing import Dict, List, Any


class SemanticAnalyzer:
    """Analyzes code semantics and generates business narratives"""
    
    # Method intent keywords
    INTENT_KEYWORDS = {
        'create': ['create', 'add', 'insert', 'new', 'register', 'signup'],
        'read': ['get', 'find', 'search', 'query', 'fetch', 'retrieve', 'select', 'list'],
        'update': ['update', 'edit', 'modify', 'change', 'set', 'put', 'patch'],
        'delete': ['delete', 'remove', 'destroy', 'drop', 'clear'],
        'financial_transaction': ['payment', 'charge', 'transaction', 'invoice', 'billing'],
    }
    
    # Parameter context keywords
    PARAMETER_CONTEXTS = {
        'financial': ['amount', 'price', 'cost', 'fee', 'total', 'currency', 'payment'],
        'communication': ['email', 'message', 'subject', 'body', 'recipient', 'notification'],
        'authentication': ['password', 'token', 'credential', 'auth', 'session'],
        'user': ['user', 'username', 'userid', 'account'],
    }
    
    # Narrative templates by capability
    NARRATIVE_TEMPLATES = {
        'authentication': {
            'high': "🟢 **User Authentication** ({confidence}% confidence)\n   - Robust authentication system detected\n   - Evidence: {evidence}\n   - Entities: {entities}",
            'medium': "🟡 **User Authentication** ({confidence}% confidence)\n   - Authentication capabilities present\n   - Evidence: {evidence}",
            'low': "🔴 **User Authentication** ({confidence}% confidence)\n   - Inferred authentication functionality\n   - Evidence: {evidence}"
        },
        'payment': {
            'high': "🟢 **Payment Processing** ({confidence}% confidence)\n   - Complete payment integration detected\n   - Evidence: {evidence}\n   - Entities: {entities}",
            'medium': "🟡 **Payment Processing** ({confidence}% confidence)\n   - Payment capabilities present\n   - Evidence: {evidence}",
            'low': "🔴 **Payment Processing** ({confidence}% confidence)\n   - Appears to handle payment processing\n   - Evidence: {evidence}"
        },
        'reporting': {
            'high': "🟢 **Reporting & Analytics** ({confidence}% confidence)\n   - Comprehensive reporting system\n   - Evidence: {evidence}",
            'medium': "🟡 **Reporting & Analytics** ({confidence}% confidence)\n   - Reporting capabilities detected\n   - Evidence: {evidence}",
            'low': "🔴 **Reporting & Analytics** ({confidence}% confidence)\n   - Inferred reporting functionality\n   - Evidence: {evidence}"
        },
        'email': {
            'high': "🟢 **Email Notifications** ({confidence}% confidence)\n   - Email notification system detected\n   - Evidence: {evidence}",
            'medium': "🟡 **Email Notifications** ({confidence}% confidence)\n   - Email capabilities present\n   - Evidence: {evidence}",
            'low': "🔴 **Email Notifications** ({confidence}% confidence)\n   - Appears to send emails\n   - Evidence: {evidence}"
        },
        'file_upload': {
            'high': "🟢 **File Management** ({confidence}% confidence)\n   - File upload/download system detected\n   - Evidence: {evidence}",
            'medium': "🟡 **File Management** ({confidence}% confidence)\n   - File handling capabilities\n   - Evidence: {evidence}",
            'low': "🔴 **File Management** ({confidence}% confidence)\n   - Inferred file operations\n   - Evidence: {evidence}"
        },
        'default': {
            'high': "🟢 **{name}** ({confidence}% confidence)\n   - {name} capability detected\n   - Evidence: {evidence}",
            'medium': "🟡 **{name}** ({confidence}% confidence)\n   - {name} functionality present\n   - Evidence: {evidence}",
            'low': "🔴 **{name}** ({confidence}% confidence)\n   - Inferred {name} capability\n   - Evidence: {evidence}"
        }
    }
    
    def __init__(self):
        """Initialize semantic analyzer"""
        pass
    
    def analyze_method_intent(self, method_name: str, parameters: List[str], 
                              return_type: str) -> Dict[str, Any]:
        """
        Analyze method intent from signature
        
        Args:
            method_name: Name of the method
            parameters: List of parameter names
            return_type: Return type annotation
            
        Returns:
            Dict with intent and confidence score
        """
        score = 0
        intent = "unknown"
        method_lower = method_name.lower()
        
        # Check method name against intent keywords
        for intent_type, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in method_lower:
                    intent = intent_type
                    score += 30
                    break
            if intent != "unknown":
                break
        
        # Check parameters for financial transaction indicators
        param_lower = [p.lower() for p in parameters]
        if any(p in param_lower for p in ['amount', 'price', 'payment']):
            if intent == "unknown":
                intent = "financial_transaction"
            score += 40
        
        # Check return type
        if return_type:
            if return_type.lower() in ['bool', 'boolean', 'task<bool>']:
                score += 10
            elif return_type.lower() not in ['void', 'none']:
                score += 5
        
        return {
            'intent': intent,
            'confidence': min(score, 100)
        }
    
    def analyze_parameters(self, parameters: List[str]) -> Dict[str, Any]:
        """
        Analyze parameters for business context
        
        Args:
            parameters: List of parameter names
            
        Returns:
            Dict with categories and confidence
        """
        categories = []
        confidence = 0
        param_lower = [p.lower() for p in parameters]
        
        for context, keywords in self.PARAMETER_CONTEXTS.items():
            for keyword in keywords:
                if any(keyword in p for p in param_lower):
                    if context not in categories:
                        categories.append(context)
                        confidence += 20
        
        return {
            'categories': categories,
            'confidence': min(confidence, 100)
        }
    
    def analyze_return_type(self, return_type: str) -> Dict[str, str]:
        """
        Analyze return type for data flow
        
        Args:
            return_type: Return type string
            
        Returns:
            Dict with category and entity info
        """
        if not return_type or return_type.lower() in ['void', 'none']:
            return {'category': 'void', 'entity_type': None}
        
        rt_lower = return_type.lower()
        
        # Boolean indicates success/failure
        if rt_lower in ['bool', 'boolean', 'task<bool>']:
            return {'category': 'success_indicator', 'confidence': 10}
        
        # Collection types
        if any(x in rt_lower for x in ['list', 'array', 'collection', 'ienumerable']):
            # Extract entity type from generic
            match = re.search(r'<(\w+)>', return_type)
            entity = match.group(1) if match else 'items'
            return {'category': 'collection', 'entity_type': entity}
        
        # Single entity
        return {'category': 'entity', 'entity_type': return_type}
    
    def get_confidence_level(self, confidence: float) -> str:
        """
        Categorize confidence score
        
        Args:
            confidence: Confidence score 0-100
            
        Returns:
            Level string (high/medium/low)
        """
        if confidence >= 90:
            return 'high'
        elif confidence >= 60:
            return 'medium'
        else:
            return 'low'
    
    def generate_narrative(self, capability: Dict[str, Any], 
                          include_files: bool = False) -> str:
        """
        Generate human-readable narrative from capability
        
        Args:
            capability: Capability dict with name, confidence, evidence, entities
            include_files: Whether to include file references
            
        Returns:
            Formatted narrative string
        """
        if not capability:
            return "No capability data available."
        
        # Extract data
        name = capability.get('name', 'Unknown')
        confidence = capability.get('confidence', 0)
        evidence = capability.get('evidence', [])
        entities = capability.get('entities', [])
        
        # Determine confidence level
        level = self.get_confidence_level(confidence)
        
        # Get template
        name_lower = name.lower().replace(' ', '_')
        templates = self.NARRATIVE_TEMPLATES.get(name_lower, self.NARRATIVE_TEMPLATES['default'])
        template = templates[level]
        
        # Format evidence
        if include_files:
            evidence_str = ', '.join(evidence[:5])  # Top 5
        else:
            evidence_str = ', '.join([e for e in evidence[:5] if not '.' in e or len(e) < 15])
        
        # Format entities
        entities_str = ', '.join(entities[:3]) if entities else 'N/A'
        
        # Substitute template variables
        narrative = template.format(
            name=name,
            confidence=int(confidence),
            evidence=evidence_str if evidence_str else 'code analysis',
            entities=entities_str
        )
        
        return narrative
    
    def generate_executive_summary(self, capabilities: List[Dict[str, Any]]) -> str:
        """
        Generate complete executive summary from capabilities
        
        Args:
            capabilities: List of capability dicts
            
        Returns:
            Complete formatted summary
        """
        if not capabilities:
            return "No capabilities detected. This may be a new project or require more code analysis."
        
        # Sort by confidence
        sorted_caps = sorted(capabilities, key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Build summary
        lines = ["This application has the following core capabilities:\n"]
        
        for cap in sorted_caps[:10]:  # Top 10 capabilities
            narrative = self.generate_narrative(cap)
            lines.append(narrative)
            lines.append("")  # Blank line
        
        # Add statistics
        high_conf = sum(1 for c in capabilities if c.get('confidence', 0) >= 90)
        medium_conf = sum(1 for c in capabilities if 60 <= c.get('confidence', 0) < 90)
        low_conf = sum(1 for c in capabilities if c.get('confidence', 0) < 60)
        
        lines.append(f"\n**Analysis Summary:**")
        lines.append(f"- Total capabilities: {len(capabilities)}")
        lines.append(f"- High confidence (🟢): {high_conf}")
        lines.append(f"- Medium confidence (🟡): {medium_conf}")
        lines.append(f"- Low confidence (🔴): {low_conf}")
        
        return '\n'.join(lines)
    
    def extract_method_signatures(self, code: str, language: str = 'python') -> List[Dict[str, Any]]:
        """
        Extract method signatures from code
        
        Args:
            code: Source code string
            language: Programming language
            
        Returns:
            List of signature dicts with name, parameters, return_type
        """
        signatures = []
        
        if language == 'python':
            signatures = self._extract_python_signatures(code)
        elif language == 'csharp':
            signatures = self._extract_csharp_signatures(code)
        elif language == 'typescript':
            signatures = self._extract_typescript_signatures(code)
        
        return signatures
    
    def _extract_python_signatures(self, code: str) -> List[Dict[str, Any]]:
        """Extract method signatures from Python using AST"""
        signatures = []
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Extract parameters
                    params = [arg.arg for arg in node.args.args if arg.arg != 'self']
                    
                    # Extract return type
                    return_type = None
                    if node.returns:
                        if isinstance(node.returns, ast.Name):
                            return_type = node.returns.id
                        elif isinstance(node.returns, ast.Constant):
                            return_type = str(node.returns.value)
                    
                    signatures.append({
                        'name': node.name,
                        'parameters': params,
                        'return_type': return_type
                    })
        except SyntaxError:
            pass
        
        return signatures
    
    def _extract_csharp_signatures(self, code: str) -> List[Dict[str, Any]]:
        """Extract method signatures from C# using regex"""
        signatures = []
        
        # Match: public ReturnType MethodName(Type param1, Type param2)
        pattern = r'(?:public|private|protected)?\s+(\w+)\s+(\w+)\s*\(([^)]*)\)'
        matches = re.finditer(pattern, code)
        
        for match in matches:
            return_type = match.group(1)
            method_name = match.group(2)
            params_str = match.group(3)
            
            # Parse parameters
            params = []
            if params_str.strip():
                for param in params_str.split(','):
                    parts = param.strip().split()
                    if len(parts) >= 2:
                        params.append(parts[1])  # Parameter name
            
            signatures.append({
                'name': method_name,
                'parameters': params,
                'return_type': return_type if return_type != 'void' else None
            })
        
        return signatures
    
    def _extract_typescript_signatures(self, code: str) -> List[Dict[str, Any]]:
        """Extract method signatures from TypeScript"""
        signatures = []
        
        # Match: methodName(param1: Type, param2: Type): ReturnType
        pattern = r'(\w+)\s*\(([^)]*)\)\s*:\s*(\w+)'
        matches = re.finditer(pattern, code)
        
        for match in matches:
            method_name = match.group(1)
            params_str = match.group(2)
            return_type = match.group(3)
            
            # Parse parameters
            params = []
            if params_str.strip():
                for param in params_str.split(','):
                    parts = param.strip().split(':')
                    if parts:
                        params.append(parts[0].strip())
            
            signatures.append({
                'name': method_name,
                'parameters': params,
                'return_type': return_type if return_type != 'void' else None
            })
        
        return signatures
