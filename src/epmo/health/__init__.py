"""
CORTEX 3.0 - EPMO Health Package
================================

Complete EPMO health validation, remediation, and monitoring system.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from .validation_suite import (
    EPMOHealthValidator,
    ValidationResult,
    HealthDimension,
    ValidationSeverity
)
from .auto_fix import AutoFixEngine
from .remediation_engine import RemediationEngine, RemediationAction
from .dashboard import HealthDashboard
from .integration import EPMOHealthSystem

# Import all validators
from .validators import (
    BaseValidator,
    CodeQualityValidator,
    DocumentationValidator,
    TestCoverageValidator,
    PerformanceValidator,
    ArchitectureValidator,
    MaintainabilityValidator
)

__all__ = [
    # Core validation
    'EPMOHealthValidator',
    'ValidationResult',
    'HealthDimension',
    'ValidationSeverity',
    
    # Remediation
    'AutoFixEngine',
    'RemediationEngine',
    'RemediationAction',
    
    # Dashboard and monitoring
    'HealthDashboard',
    'EPMOHealthSystem',
    
    # Validators
    'BaseValidator',
    'CodeQualityValidator',
    'DocumentationValidator',
    'TestCoverageValidator',
    'PerformanceValidator',
    'ArchitectureValidator',
    'MaintainabilityValidator'
]

# Package version
__version__ = '1.0.0'

# Quick access to main functionality
def validate_epmo(epmo_path, project_root=None):
    """Quick validation of an EPMO."""
    from pathlib import Path
    
    epmo_path = Path(epmo_path)
    if project_root is None:
        project_root = epmo_path.parent
    else:
        project_root = Path(project_root)
    
    validator = EPMOHealthValidator()
    return validator.validate_epmo_health(epmo_path, project_root)

def run_health_system(epmo_path, project_root=None):
    """Run complete health system on an EPMO."""
    from pathlib import Path
    
    epmo_path = Path(epmo_path)
    if project_root is None:
        project_root = epmo_path.parent
    else:
        project_root = Path(project_root)
    
    health_system = EPMOHealthSystem(project_root)
    return health_system.run_comprehensive_health_check(epmo_path)