"""
STS Test Logger - Simplified wrapper for test logging
"""

from pathlib import Path
from src.infrastructure.enhanced_audit_logger import EnhancedAuditLogger, AuditLevel, AuditCategory


class STSLogger:
    """Simplified audit logger for STS tests."""
    
    def __init__(self):
        self.logger = EnhancedAuditLogger()
    
    def log(self, level: str, message: str, category: str, metadata: dict = None):
        """
        Simplified log interface for STS tests.
        
        Maps to EnhancedAuditLogger.log() with required parameters.
        """
        # Map string levels to AuditLevel enum
        level_map = {
            "INFO": AuditLevel.INFO,
            "WARNING": AuditLevel.WARNING,
            "ERROR": AuditLevel.ERROR,
            "CRITICAL": AuditLevel.CRITICAL,
            "DEBUG": AuditLevel.DEBUG
        }
        
        # Map string categories to AuditCategory enum
        category_map = {
            "STS_VALIDATION": AuditCategory.VALIDATION,
            "SECURITY": AuditCategory.GOVERNANCE,
            "GOVERNANCE": AuditCategory.GOVERNANCE
        }
        
        audit_level = level_map.get(level, AuditLevel.INFO)
        audit_category = category_map.get(category, AuditCategory.INFRASTRUCTURE)
        
        # Extract component and operation from metadata or use defaults
        component = metadata.get('component', 'STS') if metadata else 'STS'
        operation = metadata.get('operation', 'test_validation') if metadata else 'test_validation'
        
        # Filter metadata to remove keys that aren't accepted by storage backend
        filtered_metadata = {}
        if metadata:
            # Remove 'intent' and other non-storage keys
            filtered_metadata = {k: v for k, v in metadata.items() 
                                 if k not in ('component', 'operation', 'intent')}
        
        self.logger.log(
            level=audit_level,
            category=audit_category,
            component=component,
            operation=operation,
            message=message,
            **filtered_metadata
        )
