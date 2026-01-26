"""
Execution Specification Framework

AC-PERMANENT-FIX-010: Execution Specifications - Machine-Readable Configuration
Purpose: Replace hardcoded routing logic with declarative YAML specifications

Key Components:
- specs/: YAML specification files (routing, dispatch, governance, etc.)
- spec_registry.py: Load and cache specifications
- spec_validator.py: Validate specs against schema
- models/: Dataclasses for spec structures
- gateway.py: MasterGateway entry point (implemented in Phase 3)

Authority: cortex_brain/tier0/governance/core-040-execution-spec-mandate.yaml
"""

__version__ = "0.1.0"
__status__ = "PHASE_1_FOUNDATION"
