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

Authority: cortex/intelligence/tier0/governance/core-040-execution-spec-mandate.yaml
"""

