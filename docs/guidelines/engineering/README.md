# Engineering Best Practices Knowledge Library

**Version:** 1.0 | **Last Updated:** December 19, 2025  
**Author:** CORTEX Knowledge Library | **Source:** Machine-readable YAML guidelines

---

## Overview

This knowledge library contains comprehensive engineering best practices in **machine-readable YAML format** (primary source) for use by CORTEX AI agents. Human-readable Markdown documentation will be auto-generated in a future phase.

## Available Guidelines

### 1. Clean Code Principles (`clean-code.yaml`)

**Source:** Robert C. Martin's "Clean Code: A Handbook of Agile Software Craftsmanship" (2008)  
**Size:** 562 lines | **Status:** ✅ Complete

**Contents:**
- **Naming Conventions:** 8 rules (intention-revealing names, avoid disinformation, meaningful distinctions, pronounceable names, searchable names, avoid encodings, class=nouns, method=verbs)
- **Function Design:** 6 rules (small functions, SRP, one abstraction level, max 3 params, no side effects, command-query separation)
- **Error Handling:** 4 rules (exceptions not codes, try-catch-finally first, context with exceptions, don't return null)
- **Commenting:** 4 rules (don't comment bad code, explain in code not comments, good comments=legal/docstring/intent, bad comments=mumbling/redundant/misleading)
- **Formatting:** 3 rules (vertical openness, density, horizontal alignment)
- **SOLID Principles:** Integration examples (SRP, OCP)
- **Code Smells:** Detection mappings (Long Method, Long Parameter List, Mysterious Name, Comments, Dead Code)
- **Automation:** Tool coverage (pylint, flake8, mypy for Python; StyleCop, FxCop for C#; ESLint, TSLint for TypeScript)
- **Metrics:** Thresholds (function length ideal=10/warning=20/error=50, params ideal=2/warning=3/error=5, complexity ideal=3/warning=5/error=10)
- **CORTEX Integration:** Agent capabilities (code review validates rules via AST, generation uses defaults, refactoring triggers on rule violations)

**Access:** `cortex-brain/knowledge/engineering/clean-code.yaml`

---

### 2. Code Review Best Practices (`code-review.yaml`)

**Source:** Industry standards (OWASP, Google Code Review, Microsoft Code Review)  
**Size:** 750+ lines | **Status:** ✅ Complete

**Contents:**
- **Security Review:** 4 rules (input validation, authentication/authorization, sensitive data exposure, cryptography)
  - CRITICAL severity items: SQL injection prevention, PII masking, secure hashing (bcrypt/Argon2), no hardcoded secrets
- **Performance Review:** 3 rules (N+1 query detection, inefficient algorithms, resource leaks)
  - Detection tools: Django Silk, SQLAlchemy Echo, cProfile, memory_profiler
- **Readability Review:** 3 rules (naming clarity, function length/complexity, code duplication)
  - Metrics: Max 20 lines/function, max 3 parameters, cyclomatic complexity ≤ 10
- **Maintainability Review:** 3 rules (error handling, documentation, dependency management)
  - Tools: Pylint, Pydocstyle, Interrogate, Pydeps, Safety
- **Test Coverage Review:** 2 rules (coverage thresholds=85%, test quality with AAA pattern)
- **Architecture Review:** 2 rules (layer boundaries, SOLID principles)
- **Compliance Review:** 2 rules (license compliance, accessibility standards)
- **CORTEX Integration:** Automated PR review workflow with inline comments, quality gates, auto-fix capabilities

**Access:** `cortex-brain/knowledge/engineering/code-review.yaml`

---

### 3. Refactoring Catalog (`refactoring.yaml`)

**Source:** Martin Fowler's "Refactoring" (2nd Edition), Refactoring.Guru  
**Size:** 1,100+ lines | **Status:** ✅ Complete

**Contents:**
- **Code Smells:** 22 smells mapped to refactoring techniques
  - Bloaters: Long Method, Large Class, Primitive Obsession, Long Parameter List, Data Clumps
  - OO Abusers: Switch Statements, Temporary Field, Refused Bequest, Alternative Classes
  - Change Preventers: Divergent Change, Shotgun Surgery, Parallel Inheritance Hierarchies
  - Dispensables: Comments, Duplicate Code, Lazy Class, Dead Code, Speculative Generality
  - Couplers: Feature Envy, Inappropriate Intimacy, Message Chains, Middle Man

- **Composing Methods:** 9 refactorings
  - Extract Method, Inline Method, Extract Variable, Inline Temp, Replace Temp with Query, Split Temporary Variable, Remove Assignments to Parameters, Replace Method with Method Object, Substitute Algorithm

- **Moving Features:** 6 refactorings
  - Move Method, Move Field, Extract Class, Inline Class, Hide Delegate, Remove Middle Man

- **Organizing Data:** 3 refactorings
  - Replace Data Value with Object, Replace Type Code with Class, Encapsulate Field

- **Simplifying Conditionals:** 4 refactorings
  - Decompose Conditional, Consolidate Conditional Expression, Replace Conditional with Polymorphism, Introduce Null Object

- **Simplifying Method Calls:** 5 refactorings
  - Rename Method, Introduce Parameter Object, Preserve Whole Object, Replace Error Code with Exception

- **Dealing with Generalization:** 7 refactorings
  - Pull Up Field, Pull Up Method, Push Down Field, Push Down Method, Extract Subclass, Collapse Hierarchy

**Each refactoring includes:**
- ID, name, category
- Problem description
- Solution approach
- Step-by-step mechanics
- Before/after code examples

**CORTEX Integration:** Smell detection → Suggest refactoring → Apply with approval workflow

**Access:** `cortex-brain/knowledge/engineering/refactoring.yaml`

---

## How CORTEX Uses These Guidelines

### Code Review Agent
- **Input:** Pull request with code changes
- **Process:** 
  1. Load `code-review.yaml` rules
  2. Run AST analysis + detection patterns
  3. Generate inline comments for violations
  4. Create PR summary with severity breakdown
- **Output:** Automated code review with actionable feedback

### Code Generation Agent
- **Input:** User feature request
- **Process:**
  1. Load `clean-code.yaml` defaults
  2. Apply naming conventions (naming_001-008)
  3. Apply function design rules (function_001-006)
  4. Generate code with built-in quality
- **Output:** Clean, maintainable code by default

### Refactoring Agent
- **Input:** Existing codebase
- **Process:**
  1. Scan for code smells (`refactoring.yaml` detection patterns)
  2. Map smells → suggested refactorings
  3. Show before/after preview
  4. Apply with user approval
- **Output:** Improved code structure

---

## Future Enhancements

### Phase 10.1 (Week 22-25): Foundation Best Practices
- ✅ `clean-code.yaml` - Complete
- ✅ `code-review.yaml` - Complete
- ✅ `refactoring.yaml` - Complete
- ☐ Markdown generation (Week 23)
- ☐ Pydantic schemas for validation (Week 23-24)

### Phase 10.2 (Week 26-29): Specialized Domains
- ☐ `architecture-patterns.yaml` - DDD, Clean Architecture, Hexagonal
- ☐ `security-best-practices.yaml` - OWASP Top 10, secure coding
- ☐ `testing-strategies.yaml` - TDD, BDD, test patterns
- ☐ `performance-optimization.yaml` - Profiling, caching, async
- ☐ `devops-practices.yaml` - CI/CD, containerization, monitoring
- ☐ `api-design.yaml` - REST, GraphQL, versioning

### Phase 10.3 (Week 30-33): Domain Integration + RAG
- ☐ Vector embeddings for semantic search
- ☐ Domain-specific augmentation (company tech stacks, compliance)
- ☐ Contextual retrieval (universal + domain layers)

### Phase 10.4 (Week 34-37): Learning Agents Enhancement
- ☐ Pattern learning from best practices
- ☐ Domain-aware code review
- ☐ Compliance framework support
- ☐ Architecture recommendations

---

## Accessing the Guidelines

**Primary Source (Machine-Readable):**
```bash
cortex-brain/knowledge/engineering/
├── clean-code.yaml       # 562 lines, 30+ rules
├── code-review.yaml      # 750+ lines, 19 checklists
└── refactoring.yaml      # 1,100+ lines, 34 techniques
```

**For Agents (Programmatic Access):**
```python
import yaml
from pathlib import Path

# Load guideline
guideline_path = Path("cortex-brain/knowledge/engineering/clean-code.yaml")
with open(guideline_path) as f:
    guideline = yaml.safe_load(f)

# Access rules
naming_rules = guideline['naming_conventions']['rules']
for rule in naming_rules:
    print(f"{rule['id']}: {rule['name']} ({rule['severity']})")
```

**For Humans (Future):**
- Auto-generated Markdown: `docs/guidelines/engineering/*.md`
- Interactive web documentation (MkDocs)
- Quick reference cards

---

## Contributing

To add new guidelines:
1. Create YAML file in `cortex-brain/knowledge/{domain}/`
2. Follow existing structure (metadata, rules with IDs, examples, integration)
3. Run validation: `pydantic validate {guideline}.yaml`
4. Generate MD: `python scripts/yaml_to_md.py {guideline}.yaml`

---

**Last Generated:** December 19, 2025  
**YAML Files:** 3/24 (Week 22 complete, Phase 10.1 in progress)  
**Next Milestone:** Week 25 - Foundation complete (3 packages, 9 YAML files)
