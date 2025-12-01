NAMESPACE-002: Workspace Isolation

Each workspace (project) should have isolated knowledge.

Benefits:
1. Clean Separation: No cross-project contamination
2. Parallel Development: Multiple projects on same machine
3. Easier Cleanup: Delete workspace.projectA.* removes all traces
4. Privacy: Project A can't see Project B patterns

Example Structure:
- workspace.ksessions.* → KSESSIONS project patterns
- workspace.noor.* → NOOR Canvas project patterns
- workspace.cortex.* → CORTEX development patterns (meta!)

This rule is WARNING severity - allowed but discouraged.
