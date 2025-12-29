# Learning Library

**Purpose:** Structured knowledge repository capturing implementation decisions, architectural patterns, and lessons learned from CORTEX development.

**Structure:** Each topic organized in `{category}/{topic}/` with 6-file documentation set.

---

## 📂 Organization

```
learning/
├── architecture/          # System design patterns and decisions
├── implementation/        # Code implementation guides
├── testing/              # Test strategies and approaches
├── refactoring/          # Refactoring patterns and techniques  
├── performance/          # Performance optimization techniques
├── troubleshooting/      # Common issues and solutions
└── workflows/            # Development workflows and processes
```

---

## 📝 Documentation Standards

Each learning topic must include 6 files:

1. **README.md** - Overview, quickstart, key concepts
2. **context.md** - Problem statement, requirements, constraints
3. **architecture.md** - Design diagrams, components, data flow
4. **implementation-guide.md** - Code walkthrough, key algorithms, extension points
5. **test-strategy.md** - Test approach, coverage metrics, test files
6. **research-notes.md** - Design decisions, trade-offs, alternatives considered

---

## 🎯 Purpose

- **Preserve Knowledge:** Design decisions and rationale never lost
- **Accelerate Onboarding:** New developers understand "why" not just "what"
- **Prevent Repeated Research:** Solutions documented for reuse
- **Cross-Reference:** Linked to knowledge graph for discoverability
- **Continuous Learning:** Growing repository of best practices

---

## 📊 Quality Gates

✅ All 6 documentation files present  
✅ Each file has meaningful content (not placeholders)  
✅ Examples and code snippets included where applicable  
✅ Architecture diagrams present (ASCII or Mermaid)  
✅ Integration points documented  
✅ Common pitfalls captured  
✅ Cross-references valid  
✅ Knowledge graph updated  

---

## 🔗 Integration

- **Planning System:** Automatic learning library phase in all plans
- **SKULL Rule:** `LEARNING_LIBRARY_DOCUMENTATION_ENFORCEMENT` (Tier 0)
- **Knowledge Graph:** Auto-linked for semantic search
- **Brain Persistence:** Stored in cortex-brain for long-term memory

---

**Last Updated:** December 27, 2025  
**Enforcement:** MANDATORY (cannot be bypassed)
