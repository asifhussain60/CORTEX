# Learning Library

**Purpose:** Repository-specific knowledge base capturing implementation decisions, architectural patterns, and lessons learned across multiple projects.

**Structure:** Each repository has isolated folders: `library/{repo_name}/{category}/{topic}/` with 6-file documentation set.

---

## 📂 Organization

```
library/
├── CORTEX/                # CORTEX project knowledge
│   ├── architecture/      # System design patterns and decisions
│   ├── implementation/    # Code implementation guides
│   ├── testing/          # Test strategies and approaches
│   ├── refactoring/      # Refactoring patterns and techniques  
│   ├── performance/      # Performance optimization techniques
│   ├── troubleshooting/  # Common issues and solutions
│   └── workflows/        # Development workflows and processes
│
├── UserRepo1/            # User repository 1 knowledge
│   ├── architecture/
│   ├── implementation/
│   └── ...
│
└── UserRepo2/            # User repository 2 knowledge
    ├── architecture/
    ├── implementation/
    └── ...
```

**Multi-Repo Support:** Each repository maintains separate knowledge to prevent mixing across projects. Repository name auto-detected from workspace context.

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

- **Preserve Knowledge:** Design decisions and rationale never lost per repository
- **Accelerate Onboarding:** New developers understand "why" not just "what"
- **Prevent Repeated Research:** Solutions documented for reuse
- **Repository Isolation:** Multi-project support without knowledge mixing
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
✅ Repository name correctly detected and used  

---

## 🔗 Integration

- **Planning System:** Automatic learning library phase in all plans
- **SKULL Rule:** `LEARNING_LIBRARY_DOCUMENTATION_ENFORCEMENT` (Tier 0)
- **Knowledge Graph:** Auto-linked for semantic search
- **Brain Persistence:** Stored in cortex-brain for long-term memory
- **Workspace Detection:** Auto-detects repository name from workspace context
- **Multi-Repo:** Supports working across multiple repositories simultaneously

---

**Path Format:** `cortex-brain/documents/library/{repo_name}/{category}/{topic}/`  
**Last Updated:** December 27, 2025  
**Enforcement:** MANDATORY (cannot be bypassed)
