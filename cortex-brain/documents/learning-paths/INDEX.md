# 📚 CORTEX Learning Paths Index

**Purpose:** Curated educational resources for understanding code patterns, principles, and practices used in CORTEX

**Target Audience:** Junior and Mid-level developers

**Last Updated:** December 6, 2025  
**Last Reviewed:** December 6, 2025

---

## 🎯 Quick Navigation

| Learning Path | Topics Covered | Est. Time | Difficulty |
|---------------|----------------|-----------|------------|
| [SOLID Principles](./solid-principles.md) | SRP, OCP, LSP, ISP, DIP | 20 min | Beginner |
| [Dependency Injection](./dependency-injection.md) | Constructor injection, Service lifetimes, Testing | 15 min | Beginner |
| [TDD Workflow](./tdd-workflow.md) | RED-GREEN-REFACTOR, Test-first development | 25 min | Intermediate |
| [Async Patterns](./async-patterns.md) | async/await, Threading, Progress monitoring | 20 min | Intermediate |
| [Testing Strategies](./testing-strategies.md) | Unit, Integration, E2E, Mocking | 30 min | Intermediate |

---

## 🚀 Getting Started

### For Junior Developers
**Recommended Path:**
1. Start with [SOLID Principles](./solid-principles.md) - Foundation for clean code
2. Learn [Dependency Injection](./dependency-injection.md) - Essential pattern in CORTEX
3. Practice [TDD Workflow](./tdd-workflow.md) - How CORTEX enforces quality
4. Explore [Testing Strategies](./testing-strategies.md) - Different test types

### For Mid-Level Developers
**Recommended Path:**
1. Review [SOLID Principles](./solid-principles.md) - Ensure solid foundation
2. Deep dive [Async Patterns](./async-patterns.md) - Performance optimization
3. Master [TDD Workflow](./tdd-workflow.md) - Advanced refactoring
4. Study [Testing Strategies](./testing-strategies.md) - Test architecture

---

## 🎯 How CORTEX Uses These Patterns

### When You See This Code...
```python
class ProfileAgent(BaseAgent):
    def __init__(self, name: str, db_path: Optional[str] = None):
        super().__init__(name)
        self.profile_manager = UserProfileManager(db_path)
```

### ...It Demonstrates:
- **SOLID:** Single Responsibility (ProfileAgent only routes, UserProfileManager handles storage)
- **Dependency Injection:** ProfileAgent receives dependencies via constructor
- **TDD:** Tests can inject mock UserProfileManager for isolation

**Learn More:** [Dependency Injection](./dependency-injection.md) | [SOLID Principles](./solid-principles.md)

---

## 🎥 Video Resources

### General Programming
- [SOLID Principles (10 min)](https://www.youtube.com/watch?v=pTB30aXS77U) - Fireship
- [Design Patterns (8 min)](https://www.youtube.com/watch?v=tv-_1er1mWI) - Fireship
- [Clean Code (45 min)](https://www.youtube.com/watch?v=7EmboKQH8lM) - Uncle Bob

### Python-Specific
- [Python Best Practices (30 min)](https://www.youtube.com/watch?v=Eun4SBk88w0) - Corey Schafer
- [Python Testing (20 min)](https://www.youtube.com/watch?v=6tNS--WetLI) - Corey Schafer
- [Async Python (25 min)](https://www.youtube.com/watch?v=t5Bo1Je9EmE) - mCoding

---

## 📖 External References

### Documentation
- [Python Official Docs](https://docs.python.org/3/)
- [pytest Documentation](https://docs.pytest.org/)
- [SQLite Python Tutorial](https://docs.python.org/3/library/sqlite3.html)

### Books (Free Online)
- [Clean Code JavaScript](https://github.com/ryanmcdermott/clean-code-javascript) - Principles apply to Python
- [Python Testing with pytest](https://pragprog.com/titles/bopytest/python-testing-with-pytest/) - Sample chapters
- [Refactoring Guru](https://refactoring.guru/design-patterns/python) - Design patterns catalog

### Interactive Learning
- [Python Tutor](http://pythontutor.com/) - Visualize code execution
- [Exercism Python Track](https://exercism.org/tracks/python) - Practice with mentorship
- [Real Python](https://realpython.com/) - Comprehensive tutorials

---

## 🔧 CORTEX-Specific Patterns

### Brain Tier Architecture
When you see `tier1_api`, `tier2_kg`, `tier3_context` parameters:
- **Learn:** [CORTEX Architecture Overview](../implementation-guides/brain-architecture.md)

### Agent Pattern
When you see `BaseAgent`, `AgentRequest`, `AgentResponse`:
- **Learn:** [src/cortex_agents/README.md](../../../src/cortex_agents/README.md)

### Progress Monitoring
When you see `@with_progress` decorator:
- **Learn:** [../implementation-guides/progress-monitoring-quick-start.md](../implementation-guides/progress-monitoring-quick-start.md)

---

## 💡 How to Use This Index

### During Code Review
1. CORTEX generates code with inline comments
2. Inline comments reference specific learning paths (e.g., `# Reference: learning-paths/solid-principles.md`)
3. Click the reference to learn the underlying pattern

### For Self-Study
1. Pick a learning path from the table above
2. Read the document (10-30 min)
3. Watch the linked videos for visual learning
4. Practice by examining CORTEX code examples

### When Stuck
1. Check inline comments in the generated code
2. Follow the reference link to the learning path
3. Watch the recommended video
4. Ask CORTEX: "explain this code" for custom explanation

---

## 🔄 Continuous Learning

### Daily Practice
- Review one learning path per day
- Study code CORTEX generates for you
- Ask "why did you use this pattern?" when curious

### Weekly Goals
- Complete one full learning path per week
- Implement a small feature using learned patterns
- Refactor old code applying new knowledge

### Monthly Milestones
- Complete all 5 core learning paths
- Read one external book/resource
- Contribute improvements to CORTEX

---

## 📊 Progress Tracking

Mark your progress as you complete each learning path:

- [ ] SOLID Principles
- [ ] Dependency Injection
- [ ] TDD Workflow
- [ ] Async Patterns
- [ ] Testing Strategies

---

**Questions?** Ask CORTEX: `"explain [pattern name]"` for custom explanations with examples from your codebase.

**Feedback?** Use: `cortex feedback` to suggest improvements to learning paths.
