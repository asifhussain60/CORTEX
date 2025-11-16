# src.cortex_agents.strategic.interactive_planner

Interactive Planner Agent (CORTEX 2.1)

Collaborative planning through guided dialogue. Asks clarifying questions
to resolve ambiguous requirements before creating implementation plans.

This agent implements confidence-based routing:
- High confidence (>85%): Execute immediately (no questions)
- Medium confidence (60-85%): Confirm plan with user
- Low confidence (<60%): Interactive questioning mode

Part of CORTEX 2.1 Interactive Planning enhancement.
