# CORTEX Quick Reference

**🎯 Single Entry Point for All AI Interactions**

---

## 🚀 How to Invoke CORTEX

### Method 1: In GitHub Copilot Chat (Recommended)

```
#file:/Users/asifhussain/PROJECTS/CORTEX/prompts/user/cortex.md

[Your request here]
```

**Examples:**
```
#file:/Users/asifhussain/PROJECTS/CORTEX/prompts/user/cortex.md

Add user authentication to the app
```

```
#file:/Users/asifhussain/PROJECTS/CORTEX/prompts/user/cortex.md

Continue where we left off
```

```
#file:/Users/asifhussain/PROJECTS/CORTEX/prompts/user/cortex.md

Test the login feature
```

### Method 2: Terminal Shortcuts

```bash
# Open CORTEX entry point in VS Code
cortex

# Navigate to CORTEX directory
cdcortex

# Run the launcher (displays help)
./run-cortex.sh

# Show CORTEX invocation help
cortex-invoke
```

---

## 📋 What Can You Ask CORTEX?

### Planning & Design
- "Add [feature name]" → CORTEX creates multi-phase plan
- "Design a solution for [problem]" → Strategic architecture planning
- "How should I implement [concept]?" → Best practices and patterns

### Execution
- "Continue" → Resumes automatically from last conversation
- "Implement [specific task]" → Tactical execution with TDD
- "Refactor [component]" → Safe refactoring with tests

### Testing & Validation
- "Test this feature" → Comprehensive test generation
- "Validate the code" → Health checks and error detection
- "Check for issues" → Quality analysis

### Context & Memory
- "Make it purple" → CORTEX remembers "it" from earlier
- "What did we discuss about [topic]?" → Searches conversation history
- "Show me similar patterns" → Retrieves learned knowledge

### Git & Commits
- "Commit these changes" → Smart commit with semantic messages
- "What's changed?" → Analyzes git diff and impact
- "Show commit history for [file]" → Development context analysis

---

## 🧠 CORTEX Capabilities

### 4-Tier Brain Architecture

**Tier 0: Instinct (Immutable Rules)**
- Definition of READY/DONE
- Test-Driven Development enforcement
- SOLID principles
- Challenge risky user requests

**Tier 1: Working Memory (Last 20 Conversations)**
- Recent conversation history
- Context continuity across sessions
- "Make it purple" reference resolution
- FIFO queue management

**Tier 2: Knowledge Graph (Learned Patterns)**
- Intent patterns ("add button" → PLAN)
- File relationships (co-modification tracking)
- Workflow templates
- Correction history (learn from mistakes)

**Tier 3: Development Context (Project Intelligence)**
- Git metrics (commits, authors, churn)
- Test activity patterns
- Build success rates
- Work pattern detection

### 10 Specialist Agents

**Right Brain (Strategic):**
1. **Intent Router** - Understands your natural language
2. **Work Planner** - Creates multi-phase strategic plans
3. **Screenshot Analyzer** - Extracts requirements from images
4. **Change Governor** - Protects system from degradation
5. **Brain Protector** - Challenges risky proposals with evidence

**Left Brain (Tactical):**
6. **Code Executor** - Implements with TDD precision
7. **Test Generator** - Creates comprehensive test suites
8. **Session Resumer** - Picks up where you left off
9. **Error Corrector** - Catches wrong-file mistakes instantly
10. **Health Validator** - Validates system health obsessively
11. **Commit Handler** - Semantic commits with precision

---

## 🎯 Best Practices

### Do's ✅
- **Always use the single entry point** - `cortex.md` handles routing
- **Be natural** - "Add login" works better than technical jargon
- **Trust the memory** - CORTEX remembers context across sessions
- **Use "continue"** - Let CORTEX resume automatically
- **Ask for help** - "What should I work on?" leverages pattern learning

### Don'ts ❌
- **Don't switch between multiple prompts** - One entry point for everything
- **Don't repeat yourself** - CORTEX remembers from earlier conversations
- **Don't skip planning** - Let CORTEX create strategic plans first
- **Don't ignore warnings** - Brain Protector challenges for good reasons
- **Don't manually edit brain files** - Let CORTEX manage its own memory

---

## 📊 Typical Workflows

### New Feature Workflow
```
You: #file:cortex.md
     Add invoice export feature

CORTEX: [Creates 3-phase plan with TDD approach]

You: Continue

CORTEX: [Executes Phase 1, writes tests first]

You: Continue

CORTEX: [Executes Phase 2, implements feature]

You: Test this

CORTEX: [Runs comprehensive tests, validates]

You: Commit

CORTEX: [Creates semantic commit message, pushes]
```

### Resume Work Workflow
```
You: #file:cortex.md
     Continue where we left off

CORTEX: [Checks Tier 1, finds last conversation]
        We were implementing invoice export, Phase 2 complete.
        Ready to start Phase 3: PDF generation?

You: Yes, continue

CORTEX: [Resumes automatically, maintains context]
```

### Context Reference Workflow
```
You: #file:cortex.md
     Add a fade animation to the FAB button

CORTEX: [Implements animation]

[Later in conversation]

You: Make it 300ms instead

CORTEX: [Checks Tier 1, finds "fade animation"]
        Updating animation duration to 300ms...

You: And make it purple

CORTEX: [Still remembers "FAB button"]
        Setting FAB button background to purple...
```

---

## 🔧 Shell Setup (One-Time)

If aliases aren't working, reload your shell config:

```bash
# Reload zsh configuration
source ~/.zshrc

# Test aliases
cortex-invoke
```

Or manually add to `~/.zshrc`:

```bash
# CORTEX Entry Point Shortcuts
alias cortex='code /Users/asifhussain/PROJECTS/CORTEX/prompts/user/cortex.md'
alias cortex-open='open -a "Visual Studio Code" /Users/asifhussain/PROJECTS/CORTEX/prompts/user/cortex.md'

# CORTEX Project Navigation
alias cdcortex='cd /Users/asifhussain/PROJECTS/CORTEX'

# CORTEX Quick Commands
cortex-invoke() {
    echo "# CORTEX Universal Entry Point"
    echo "#file:/Users/asifhussain/PROJECTS/CORTEX/prompts/user/cortex.md"
    echo ""
    echo "You can now use CORTEX for all AI assistant interactions!"
}
```

---

## 📚 More Information

- **Full Documentation:** `cortex-design/CORTEX-DNA.md`
- **Implementation Plan:** `cortex-design/IMPLEMENTATION-PLAN-V3.md`
- **Migration Guide:** `cortex-design/MIGRATION-STRATEGY.md`
- **Entry Point Details:** `prompts/user/cortex.md`

---

**Remember:** CORTEX assumes you're always invoking it. Just reference the entry point and make your request naturally!
