"""
Relationship Mapper - Extract entity relationship graphs from code

Builds graphs for:
- File→Function relationships (function definitions and calls)
- File→File relationships (imports and dependencies)
- Feature→File relationships (implementation spanning multiple files)

Author: Asif Hussain
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass


@dataclass
class CodeRelationship:
    """Represents a relationship between code entities"""
    source: str
    target: str
    relationship_type: str
    strength: float = 0.5
    context: str = ""


class RelationshipMapper:
    """Extract and store code entity relationships"""
    
    def __init__(self, knowledge_graph):
        """
        Initialize relationship mapper
        
        Args:
            knowledge_graph: Tier 2 KnowledgeGraph instance
        """
        self.knowledge_graph = knowledge_graph
    
    def extract_code_relationships(
        self,
        file_path: str,
        code_content: str
    ) -> List[Dict[str, Any]]:
        """
        Extract file→function relationships from Python code
        
        Args:
            file_path: Path to the file being analyzed
            code_content: Python source code
            
        Returns:
            List of relationship dicts with type, name, line number
        """
        relationships = []
        
        try:
            tree = ast.parse(code_content)
            
            # Extract function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    relationships.append({
                        'type': 'function_definition',
                        'source': file_path,
                        'target': node.name,
                        'line': node.lineno,
                        'context': f"Function {node.name} defined in {file_path}"
                    })
                    
                    # Extract function calls within this function
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name):
                                relationships.append({
                                    'type': 'function_call',
                                    'source': node.name,
                                    'target': child.func.id,
                                    'line': child.lineno,
                                    'context': f"{node.name} calls {child.func.id}"
                                })
                
                # Extract class definitions
                elif isinstance(node, ast.ClassDef):
                    relationships.append({
                        'type': 'class_definition',
                        'source': file_path,
                        'target': node.name,
                        'line': node.lineno,
                        'context': f"Class {node.name} defined in {file_path}"
                    })
        
        except SyntaxError:
            # Handle invalid Python code gracefully
            pass
        
        return relationships
    
    def extract_import_relationships(
        self,
        file_path: str,
        code_content: str
    ) -> List[Dict[str, Any]]:
        """
        Extract file→file import relationships
        
        Args:
            file_path: Path to the file being analyzed
            code_content: Python source code
            
        Returns:
            List of import relationship dicts
        """
        relationships = []
        
        try:
            tree = ast.parse(code_content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Filter internal imports (src.*)
                        if alias.name.startswith('src.'):
                            target = alias.name.replace('.', '/') + '.py'
                            relationships.append({
                                'source': file_path,
                                'target': target,
                                'type': 'import',
                                'line': node.lineno,
                                'context': f"{file_path} imports {alias.name}"
                            })
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith('src.'):
                        target = node.module.replace('.', '/') + '.py'
                        relationships.append({
                            'source': file_path,
                            'target': target,
                            'type': 'import_from',
                            'line': node.lineno,
                            'context': f"{file_path} imports from {node.module}"
                        })
        
        except SyntaxError:
            pass
        
        return relationships
    
    def build_feature_graph(
        self,
        feature_files: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """
        Build feature→file relationship graph
        
        Args:
            feature_files: Dict mapping feature names to file lists
            
        Returns:
            Feature graph dict
        """
        # Return as-is, it's already in the right format
        return feature_files
    
    def store_relationship(
        self,
        source: str,
        target: str,
        relationship_type: str,
        strength: float = 0.5,
        context: str = ""
    ) -> str:
        """
        Store relationship in Tier 2 knowledge graph
        
        Args:
            source: Source entity (file, function, class)
            target: Target entity
            relationship_type: Type of relationship
            strength: Relationship strength (0.0-1.0)
            context: Description of relationship
            
        Returns:
            Relationship ID
        """
        import hashlib
        import json
        
        # Generate relationship ID
        rel_data = f"{source}_{target}_{relationship_type}"
        rel_id = f"rel_{hashlib.md5(rel_data.encode()).hexdigest()[:12]}"
        
        # Store in relationships table via knowledge graph
        self.knowledge_graph.store_relationship(
            relationship_id=rel_id,
            file_a=source,
            file_b=target,
            relationship_type=relationship_type,
            strength=strength,
            context=context
        )
        
        return rel_id
    
    def get_related_files(
        self,
        file_path: str,
        relationship_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get files related to given file
        
        Args:
            file_path: Source file path
            relationship_type: Optional filter by relationship type
            
        Returns:
            List of related files with relationship info
        """
        return self.knowledge_graph.get_relationships(
            file_a=file_path,
            relationship_type=relationship_type
        )
