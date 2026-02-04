"""
Contract Tests for Cross-Layer Alignment.

This package contains tests that validate alignment between different layers:
- Python ↔ JavaScript enum alignment
- Python ↔ JavaScript field naming
- Pydantic ↔ JSON Schema compatibility

These tests are critical for preventing schema misalignments discovered during
Phase 21 debugging (4+ hours of layer alignment issues).

Authority: CORTEX-SELF-IMPROVEMENT-SDLC.yaml
Created: 2026-02-04
"""
