# src.operations.base_operation_module

Base Operation Module - Universal Abstract Interface

This module provides the abstract base class that ALL operation modules inherit from,
whether for setup, story refresh, documentation updates, cleanup, or any other CORTEX command.

Design Principles (SOLID):
    - Single Responsibility: Each module does ONE thing
    - Open/Closed: Add new modules without modifying orchestrator
    - Liskov Substitution: All modules are interchangeable
    - Interface Segregation: Minimal required interface
    - Dependency Inversion: Depend on abstractions, not concrete implementations

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)
