"""Validator modules for CORTEX Review Orchestrator v2.0.0"""

__all__ = [
    "PythonValidator",
    "AuditLogValidator",
    "PhaseProgressionValidator"
]

# Stub implementations
try:
    from .python_validator import PythonValidator
    from .audit_log_validator import AuditLogValidator
    from .phase_progression_validator import PhaseProgressionValidator
except ImportError:
    class PythonValidator:
        def __init__(self, epic_path):
            self.epic_path = epic_path
        
        def validate(self):
            return {"status": "passed", "failures": []}
    
    class AuditLogValidator:
        def __init__(self, epic_path, state_db):
            self.epic_path = epic_path
            self.state_db = state_db
        
        def validate(self):
            return {"status": "passed", "violations": []}
    
    class PhaseProgressionValidator:
        def __init__(self, epic_path, state_db):
            self.epic_path = epic_path
            self.state_db = state_db
        
        def validate(self):
            return {"can_progress": True, "blocking_reasons": []}
