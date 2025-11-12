"""
ErrorCorrector Agent - Modular error correction with specialized parsers and strategies.

This module provides the ErrorCorrector agent that automatically detects, parses,
and corrects errors in code. The agent is organized into:

- Parsers: Extract structured error information from various error outputs
- Strategies: Apply specific fixes for different error types
- Validators: Ensure fixes are safe and paths are not protected

The agent only fixes TARGET APPLICATION code and never modifies CORTEX system files.
"""

from .agent import ErrorCorrector

__all__ = ["ErrorCorrector"]
