# Request Validator & Enhancer Examples

This directory contains executable Python implementation examples for the CORTEX 2.0 Request Validator & Enhancer system.

## Overview

The Request Validator & Enhancer analyzes user requests before routing to specialist agents, providing:

- **Viability Analysis**: Technical feasibility checks
- **Historical Patterns**: Success rate analysis from past similar requests
- **Enhancement Suggestions**: Intelligent improvements based on learned patterns

## Files

### Core Implementation

- `request_validator.py` - Main validator orchestrator
- `viability_analyzer.py` - Technical viability analysis
- `historical_analyzer.py` - Historical pattern analysis
- `enhancement_analyzer.py` - Enhancement suggestion engine

### Usage Example

```python
from examples.request_validator.request_validator import RequestValidator, ValidationDecision

# Initialize with CORTEX tiers
validator = RequestValidator(tier1_api, tier2_kg, tier3_context)

# Validate a request
result = validator.validate_and_enhance(
    request=user_request,
    conversation_id="conv-123"
)

# Handle result
if result.decision == ValidationDecision.CHALLENGE:
    print(f"⚠️ Critical issues: {result.message}")
    print(f"Alternatives: {result.alternatives}")
elif result.decision == ValidationDecision.ENHANCE:
    print(f"✨ Enhancements available:")
    for enhancement in result.enhancements:
        print(f"  - {enhancement['title']} (value: {enhancement['value']})")
elif result.decision == ValidationDecision.APPROVE:
    print("✅ Request approved, proceeding...")
```

## Validation Decisions

1. **APPROVE**: Request is viable, proceed immediately
2. **ENHANCE**: Request is good but can be improved
3. **ADVISE**: Consider alternative approach based on historical success
4. **CHALLENGE**: Critical issues detected, requires user clarification

## Integration

To integrate into CORTEX:

1. Copy files to `src/entry_point/`
2. Import in universal entry point
3. Add validation step before agent routing
4. Connect to Tier 1, 2, and 3 APIs

## Development Status

- ✅ Core structure implemented
- ⏳ Viability analyzer - stub (TODO)
- ⏳ Historical analyzer - stub (TODO)
- ⏳ Enhancement analyzer - stub (TODO)
- ⏳ Tests - not yet created

## Next Steps

1. Implement viability analysis logic
2. Implement historical pattern matching
3. Implement enhancement suggestion rules
4. Add comprehensive test suite
5. Performance optimization
6. Integration testing with CORTEX agents

## Related Documentation

- Design: `cortex-brain/cortex-2.0-design/22-request-validator-enhancer.md`
- Visual Architecture: `cortex-brain/REQUEST-VALIDATOR-VISUAL-ARCHITECTURE.md`
