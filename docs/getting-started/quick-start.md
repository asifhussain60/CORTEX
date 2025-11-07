# Quick Start

Get CORTEX up and running in 5 minutes.

## The Only Command You Need

```markdown
#file:prompts/user/cortex.md

[Tell CORTEX what you want in natural language]
```

That's it! CORTEX will automatically analyze your request, route it to the appropriate agent, and execute the workflow.

## Your First Interaction

1. **Open GitHub Copilot Chat**
2. **Type the magic command:**
   ```
   #file:prompts/user/cortex.md
   
   Add a purple button to my homepage
   ```
3. **Watch CORTEX work:**
   - ✅ Analyzes your request (intent detection)
   - ✅ Routes to the Planner (strategic planning)
   - ✅ Creates test-first implementation plan
   - ✅ Executes with the Builder agent
   - ✅ Validates with the Inspector
   - ✅ Commits with semantic message

## What Just Happened?

Behind the scenes, CORTEX:

1. **RIGHT BRAIN (Strategic):**
   - Analyzed your request as a PLAN intent
   - Queried Tier 2 for similar button patterns
   - Checked Tier 3 for file stability warnings
   - Created a 4-phase implementation plan

2. **LEFT BRAIN (Tactical):**
   - Created failing tests first (RED)
   - Implemented minimum code (GREEN)
   - Validated health checks (REFACTOR)
   - Committed with semantic message

3. **BRAIN LEARNING:**
   - Logged 5 events to event stream
   - Updated conversation history (Tier 1)
   - Reinforced button pattern (Tier 2)
   - Updated development metrics (Tier 3)

## Next Steps

- **[Installation](installation.md)** - Set up CORTEX in your project
- **[Your First Task](first-task.md)** - Walk through a complete workflow
- **[Configuration](configuration.md)** - Customize CORTEX for your needs

## What You Don't Need to Know

CORTEX handles all of this automatically:

- ❌ Which hemisphere should handle your request
- ❌ Which agent specializes in what
- ❌ What tier stores which knowledge
- ❌ How the corpus callosum coordinates
- ❌ When to trigger brain updates

Just talk naturally, and CORTEX figures out the rest.

## Common First Commands

```markdown
# Create a new feature
#file:prompts/user/cortex.md
Add invoice export to the billing module

# Fix an issue
#file:prompts/user/cortex.md
The login button isn't responding on mobile

# Resume after a break
#file:prompts/user/cortex.md
Where did I leave off?

# Understand the codebase
#file:prompts/user/cortex.md
What are the most unstable files in this project?
```

## The One Rule

**CORTEX follows Definition of DONE:**
- ✅ Zero errors
- ✅ Zero warnings  
- ✅ All tests pass
- ✅ Test-first development (RED → GREEN → REFACTOR)

This is a Tier 0 instinct and cannot be disabled. If you ask CORTEX to skip tests, it will challenge you with evidence and safer alternatives.

## Ready?

That's all you need to know to get started. Let's dive deeper:

→ **[Installation Guide](installation.md)**
