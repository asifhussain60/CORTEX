# src.cortex_agents.intent_router

IntentRouter Agent

Routes user requests to appropriate specialist agents based on intent analysis.
Uses Tier 2 Knowledge Graph to find similar past intents and improve routing decisions.

The IntentRouter is the entry point for all user requests - it analyzes the intent,
checks for patterns in past requests, and routes to the most appropriate specialist agent.
