# CORTEX Interactive Demo

**Operation:** `cortex_tutorial`  
**Category:** Onboarding  
**Status:** ✅ Ready (100% Complete)

## Overview

Hands-on walkthrough of CORTEX capabilities with live execution. The demo showcases core features through interactive modules that actually run real CORTEX operations.

## Natural Language Triggers

Use any of these phrases to run the demo:
- "demo"
- "show me what cortex can do"
- "walkthrough"
- "tutorial"
- "cortex demo"
- "interactive tutorial"
- "show demo"

## Demo Modules

The demo consists of 6 modules:

1. **demo_introduction** - Welcome message and CORTEX overview
2. **demo_help_system** - Interactive help command demonstration
3. **demo_story_refresh** - Story transformation showcase
4. **demo_cleanup** - Cleanup plugin demonstration
5. **demo_conversation** - Conversation memory showcase
6. **demo_completion** - Wrap-up and next steps

## Profiles

### Quick Profile (2 minutes)
Essential commands only for busy users.

**Modules:** introduction, help_system, story_refresh, completion

```bash
# Natural language
"run quick demo"
"quick tutorial"
```

### Standard Profile (3-4 minutes) ⭐ Recommended
Core capabilities with balanced coverage.

**Modules:** introduction, help_system, story_refresh, cleanup, completion

```bash
# Natural language
"demo"
"show me cortex"
```

### Comprehensive Profile (5-6 minutes)
Full walkthrough including all features.

**Modules:** All 6 modules

```bash
# Natural language  
"full demo"
"comprehensive tutorial"
"show everything"
```

## Implementation Details

### Status
- **Modules Implemented:** 6/6
- **Completion:** 100%
- **Development Hours:** 6 hours
- **Platforms:** ✅ Windows Track A, ✅ Mac Track B

### Module Distribution
- **Windows Track A:** intro, help, cleanup
- **Mac Track B:** story_refresh, conversation, completion

## Examples

### Running the Demo

```python
# Via entry point
/CORTEX demo

# Natural language
"Show me what CORTEX can do"
"Run the tutorial"
```

### Expected Output

The demo will:
1. Display CORTEX overview with ASCII art
2. Show interactive help system with table formatting
3. Demonstrate story refresh with narrator voice
4. Run cleanup plugin scan
5. Show conversation memory features
6. Provide next steps and documentation links

## Success Criteria

✅ All 6 modules execute without errors  
✅ Output formatted correctly (tables, colors, ASCII art)  
✅ Story refresh shows transformation  
✅ Help system displays command list  
✅ Cleanup scan completes  
✅ User receives next steps

## Related Documentation

- [Help Command](./help-command.md)
- [Story Refresh Operation](./refresh-cortex-story.md)
- [Cleanup Plugin Guide](../guides/cleanup-plugin-guide.md)
- [Getting Started](../getting-started/quick-start.md)

## Testing

Tested on:
- ✅ Windows 11 (Track A)
- ✅ macOS Sonoma (Track B)
- ✅ Both quick and comprehensive profiles
- ✅ All natural language triggers

## Notes

The demo is designed to be **non-destructive** - it only reads and displays information, never modifies files (except for story preview generation which is optional).

**Development Notes:**
- Windows Track A and Mac Track B implemented in parallel
- All modules tested independently and as complete operation
- Estimated 6 hours development time across both tracks
