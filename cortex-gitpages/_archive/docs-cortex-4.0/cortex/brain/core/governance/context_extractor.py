"""
Context Extractor for Governance Rules

Extracts file context to enable situational rule application.

AC-GOV-CTX-001-01: Context extraction identifies file type, operation type, 
development phase, and code classification
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional


@dataclass
class GovernanceContext:
    """
    Context information for governance rule evaluation.
    
    Attributes:
        file_path: Path to the file being evaluated
        file_type: Type of file (python, yaml, json, markdown, etc.)
        operation_type: Type of operation (implement, fix, refactor, discovery, validation)
        development_phase: Development phase (production, development, exploration, testing)
        code_classification: Code classification (production, internal, generated, test)
        handler_name: Optional name of handler performing operation
    """
    file_path: str
    file_type: str
    operation_type: str
    development_phase: str
    code_classification: str
    handler_name: Optional[str] = None


class ContextExtractor:
    """
    Extracts context from file paths and operation metadata.
    
    AC-GOV-CTX-001-01: Provides context for situational rule application
    """
    
    def extract_context(
        self,
        file_path: str,
        operation_context: Dict[str, Any]
    ) -> GovernanceContext:
        """
        Extract governance context from file and operation.
        
        Args:
            file_path: Path to file being evaluated
            operation_context: Operation metadata (operation type, handler, etc.)
            
        Returns:
            GovernanceContext with extracted information
        """
        file_type = self.detect_file_type(file_path)
        code_classification = self.detect_code_classification(file_path)
        operation_type = self.extract_operation_type(operation_context)
        development_phase = self._infer_development_phase(
            code_classification, 
            operation_type
        )
        handler_name = operation_context.get("handler")
        
        return GovernanceContext(
            file_path=file_path,
            file_type=file_type,
            operation_type=operation_type,
            development_phase=development_phase,
            code_classification=code_classification,
            handler_name=handler_name
        )
    
    def detect_file_type(self, file_path: str) -> str:
        """
        Detect file type from file extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            File type identifier
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        type_map = {
            ".py": "python",
            ".pyx": "python",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".md": "markdown",
            ".txt": "text",
            ".toml": "toml",
            ".ini": "ini",
            ".cfg": "config",
        }
        
        return type_map.get(extension, "unknown")
    
    def detect_code_classification(self, file_path: str) -> str:
        """
        Classify code based on file path patterns.
        
        Args:
            file_path: Path to file
            
        Returns:
            Code classification (production, internal, generated, test)
        """
        path_lower = file_path.lower()
        
        # Test code
        if any(marker in path_lower for marker in ["tests/", "test_", "fixtures/"]):
            return "test"
        
        # Generated code
        if any(marker in path_lower for marker in ["generated/", "build/", "__pycache__/"]):
            return "generated"
        
        # Internal scripts and utilities
        if any(marker in path_lower for marker in ["scripts/", "tools/", "utilities/"]):
            return "internal"
        
        # Production code (cortex/, cortex_brain/)
        if any(marker in path_lower for marker in ["cortex/", "cortex_brain/"]):
            return "production"
        
        return "production"  # Default to production for safety
    
    def extract_operation_type(self, operation_context: Dict[str, Any]) -> str:
        """
        Extract operation type from context.
        
        Args:
            operation_context: Operation metadata
            
        Returns:
            Operation type identifier
        """
        return operation_context.get("operation", "implement")
    
    def _infer_development_phase(
        self,
        code_classification: str,
        operation_type: str
    ) -> str:
        """
        Infer development phase from classification and operation.
        
        Args:
            code_classification: Code classification
            operation_type: Operation type
            
        Returns:
            Development phase identifier
        """
        # Test code is always in testing phase
        if code_classification == "test":
            return "testing"
        
        # Internal/utility code in development phase
        if code_classification == "internal":
            return "development"
        
        # Discovery operations are exploration phase
        if operation_type == "discovery":
            return "exploration"
        
        # Production code in production phase
        if code_classification == "production":
            return "production"
        
        return "development"  # Default
