"""
STS Validation App - API Layer

This module contains deliberately flawed API endpoints for CORTEX 4.0 validation.

EDUCATIONAL PURPOSE:
===================
This code demonstrates common security vulnerabilities, SOLID violations, and anti-patterns
for validating CORTEX's detection capabilities. DO NOT use in production.

Knowledge Library Mappings:
- OWASP Top 10 vulnerabilities
- SOLID principle violations
- Anti-patterns from clean-code.yaml, anti-patterns.yaml
- Code smells from refactoring.yaml

Modules:
- auth.py: Authentication with security flaws (OWASP A02, A07)
- users.py: God class violating SRP (SOLID violations)
- products.py: SQL injection vulnerabilities (OWASP A03)
- orders.py: High complexity and code quality issues

Author: CORTEX Phase 13 - STS Validation App
Created: December 25, 2025
"""

__version__ = "1.0.0-flawed"
__all__ = ["auth", "users", "products", "orders"]
