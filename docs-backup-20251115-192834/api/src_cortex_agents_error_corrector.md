# src.cortex_agents.error_corrector

ErrorCorrector Agent

Automatically detects, parses, and corrects errors in code.

ISOLATION NOTICE: This agent fixes errors in TARGET APPLICATION code only.
It NEVER modifies CORTEX/tests/ - those are protected system health tests.

Handles:
- Pytest errors (assertion failures, import errors, type errors)
- Linter errors (undefined names, unused imports, formatting)
- Runtime errors (NameError, AttributeError, TypeError)
- Syntax errors (indentation, missing colons, invalid syntax)
- Import errors (missing modules, circular imports)

Uses Tier 2 knowledge base for known fix patterns.
