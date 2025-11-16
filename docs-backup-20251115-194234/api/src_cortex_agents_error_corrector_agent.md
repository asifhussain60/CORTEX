# src.cortex_agents.error_corrector.agent

ErrorCorrector Agent - Modular Version

Automatically detects, parses, and corrects errors in code.
This is the coordinator that delegates to specialized parsers, strategies, and validators.

ISOLATION NOTICE: This agent fixes errors in TARGET APPLICATION code only.
It NEVER modifies CORTEX/tests/ - those are protected system health tests.
