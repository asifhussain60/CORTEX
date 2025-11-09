# CORTEX Rules (Plain English)

**Quick Reference** | Updated: Nov 9, 2025

CORTEX's operating principles - the rules that keep it smart and reliable.

---

## 🎯 The 6 Protection Layers

Think of these as security checkpoints that keep CORTEX working correctly:

1. **Core Instincts** - Cannot be bypassed (DNA-level rules)
2. **Tier Boundaries** - Right information in right place
3. **SOLID Principles** - Clean, maintainable code
4. **Brain Separation** - Strategy vs. execution
5. **Knowledge Quality** - Accurate patterns and learning
6. **Commit Integrity** - Clean codebase

---

## Layer 1: Core Instincts (Cannot Be Broken)

### Rule 1: Test-First (TDD)
- Write failing test first
- Make it pass
- Clean up code
- **Example:** Want purple button? Test "button exists?" (fails) → create button (passes) → clean code

### Rule 2: Definition of DONE
Work complete only when:
- ✅ Zero errors
- ✅ Zero warnings  
- ✅ All tests pass
- ✅ Code formatted
- ✅ Docs updated
- ✅ App runs

### Rule 3: Definition of READY
Can't start until you have:
- ✅ Clear requirements
- ✅ Acceptance criteria
- ✅ Known files to modify
- ✅ No blockers

### Rule 4: Brain Protection Tests Always Pass
- Sacred tests for brain health
- Verify memory, paths, rules, tracking
- If these fail, EVERYTHING stops

### Rule 5: Use Right Format
- **YAML/JSON:** Config, rules, metrics, data
- **Markdown:** Stories, guides, tutorials
- **Code files:** Examples, patterns
- **Why:** 60% more efficient, prevents errors

---

## Layer 2: Tier Boundaries

### Rule 6: Tier 0 is Read-Only
- Instinct layer (these rules)
- Never modified during execution
- Only changed through deliberate updates

### Rule 7: Tier Isolation
- **Tier 1:** Working memory (current task)
- **Tier 2:** Knowledge graph (patterns)
- **Tier 3:** Dev context (git, files)
- **Tier 4:** Event stream (history)
- Each tier separate = performance & clarity

### Rule 8: No Cross-Tier Pollution
- Tier 1 can't leak into Tier 2
- Keeps memory organized
- Prevents confusion

---

## Layer 3: SOLID Principles

### Rule 9: Single Responsibility
- Each module does ONE thing well
- Example: `test_generator.py` only generates tests

### Rule 10: Open/Closed
- Open for extension (plugins)
- Closed for modification (core stays stable)

### Rule 11: Liskov Substitution
- Subclasses work like parent classes
- No surprises when swapping implementations

### Rule 12: Interface Segregation
- Small, focused interfaces
- No "god objects"

### Rule 13: Dependency Inversion
- Depend on abstractions, not concrete implementations
- Makes code flexible

---

## Layer 4: Brain Hemisphere Separation

### Rule 14: LEFT = Tactical (Doing)
- Code execution
- Test generation
- Error fixing
- File operations
- Commits

### Rule 15: RIGHT = Strategic (Planning)
- Work planning
- Risk assessment
- Pattern analysis
- Decision making
- Coordination

### Rule 16: Corpus Callosum = Communication
- Message queue between hemispheres
- Asynchronous messaging
- No direct coupling

---

## Layer 5: Knowledge Quality

### Rule 17: Patterns Need 3+ Examples
- Don't create pattern from 1 example
- Need 3+ instances to be confident
- **Example:** Seeing "async/await" once ≠ project pattern

### Rule 18: Pattern Validation
- Test patterns before using
- Verify they actually work
- Update if project changes

### Rule 19: Knowledge Expiry
- Old patterns expire (90 days)
- Re-validate before using
- Keep knowledge fresh

### Rule 20: Source Truth Priority
- Code > Docs > Comments
- If conflict, code wins
- Docs explain, code defines

---

## Layer 6: Commit Integrity

### Rule 21: Atomic Commits
- One logical change per commit
- **Good:** "Add user login endpoint"
- **Bad:** "Fix stuff"

### Rule 22: Commit Message Format
```
type(scope): description

- Bullet points for details
- Link to issue if exists
```

### Rule 23: No Broken Commits
- All tests must pass before commit
- No "fix later" commits
- Each commit is deployable

### Rule 24: Branch Strategy
- `main` = production-ready
- `CORTEX-2.0` = development
- Feature branches for new work

---

## Additional Rules

### Rule 25: Path Management
- Use relative paths, not absolute
- Cross-platform compatible
- Environment-specific via config

### Rule 26: Modular File Structure
- Files under 500 lines (target: 200-300)
- Split large files into focused modules
- Clear naming

### Rule 27: Hemisphere Separation (Strict)
- LEFT brain files in `src/agents/left/`
- RIGHT brain files in `src/agents/right/`
- Shared code in `src/shared/`

### Rule 28: Plugin Architecture
- Core features can't be plugins
- Extensions should be plugins
- Plugin discovery automatic

### Rule 29: Conversation State
- Always persist conversation state
- Enable resume after interruptions
- Track task progress

### Rule 30: Knowledge Boundaries
- Core CORTEX knowledge separate from project knowledge
- Enforce boundaries programmatically
- Validate on startup

### Rule 31: Documentation Ratio
- Technical docs: 5% technical, 95% story
- Human-readable format
- Examples over explanations

---

## 🔒 How Rules Are Enforced

### Prevention (Before Execution)
- Request Validator checks rules
- Brain Protector challenges violations
- Change Governor reviews proposals

### Detection (During Execution)
- Real-time monitoring
- Rule compliance checks
- Automated alerts

### Correction (After Detection)
- Auto-fix where possible
- Manual review for complex cases
- Learn from violations

---

## ⚠️ What Happens When Rules Break

### WARNING (Can Continue)
- Logged for review
- Suggestion provided
- Execution continues

### ERROR (Must Fix)
- Execution stops
- Clear error message
- Fix required before continuing

### CRITICAL (System Protection)
- Immediate halt
- Brain protection activated
- Manual intervention required

---

## 📊 Rule Compliance Stats

- **43 brain protection tests** (100% passing)
- **31 rules** enforced
- **6 protection layers** active
- **100% test coverage** for rule validation

---

## 💡 For Users

You don't need to memorize these rules. CORTEX follows them automatically. But knowing them helps you understand:

- Why CORTEX writes tests first
- Why it challenges risky changes
- Why it organizes code certain ways
- Why it keeps things modular

---

## 🗂️ Learn More

**Technical details:** `cortex-brain/brain-protection-rules.yaml`  
**Test implementation:** `tests/tier0/test_brain_protector*.py`  
**Design decisions:** `cortex-brain/cortex-2.0-design/`

---

**Folder:** `docs/human-readable/`  
**Purpose:** Plain English rule explanations  
**Target audience:** Everyone (technical background optional)
