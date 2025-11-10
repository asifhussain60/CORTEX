# src.operations.operations_orchestrator

Universal Operations Orchestrator - CORTEX 2.0

This orchestrator coordinates ALL CORTEX operations (setup, story refresh, cleanup, etc.)
by executing modules in dependency-resolved order across defined phases.

Design Principles:
    - Single orchestrator for all operations
    - YAML-driven operation definitions
    - Topological sort for dependency resolution
    - Phase-based execution with priorities
    - Comprehensive error handling and rollback

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)
