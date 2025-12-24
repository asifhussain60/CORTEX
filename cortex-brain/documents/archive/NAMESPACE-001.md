NAMESPACE-001: Protected CORTEX Namespace

Critical architectural boundary preventing knowledge contamination.

Why This Matters:
1. Framework Integrity: CORTEX patterns must remain pure
2. Multi-Project Support: Each workspace isolated
3. Knowledge Quality: No user app patterns in framework brain
4. Upgradability: CORTEX can update without breaking user data

Protected Namespaces:
- cortex.tier_architecture (4-tier brain system)
- cortex.agent_patterns (10 specialist agents)
- cortex.operations (universal operations)
- cortex.plugins (plugin system)

Allowed Namespaces:
- workspace.<project>.* (your application patterns)
- workspace.myapp.security (JWT, OAuth patterns)
- workspace.myapp.architecture (file structure, tech stack)

This rule is BLOCKING severity - violations stop execution immediately.
