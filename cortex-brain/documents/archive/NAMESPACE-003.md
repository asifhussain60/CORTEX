NAMESPACE-003: No Namespace Mixing

Single Ownership Principle: Each pattern has ONE home.

Why Single Namespace:
1. Clear Ownership: No ambiguity about who maintains pattern
2. Clean Deletion: Removing workspace.* removes all patterns
3. No Orphans: Pattern lifecycle tied to single namespace
4. Simpler Queries: No multi-namespace resolution logic

Cross-Namespace References:
Use relationship links instead of multi-namespace patterns:

❌ BAD:
learn_pattern(
    ...,
    namespaces=["cortex.security", "workspace.myapp.security"]
)

✅ GOOD:
# Store in primary namespace
pattern_id = learn_pattern(
    ...,
    namespaces=["workspace.myapp.security"]
)

# Link to generic pattern
create_relationship(
    from_pattern="cortex.security_best_practices",
    to_pattern=pattern_id,
    relationship_type="implements"
)

This rule is BLOCKING severity - multi-namespace patterns rejected.
