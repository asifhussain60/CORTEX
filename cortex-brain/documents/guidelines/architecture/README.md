# Architecture Guidelines Index

**Version:** 1.0  
**Author:** Asif Hussain  
**Date:** December 15, 2025  
**Purpose:** Central index for all architecture guidelines and patterns

---

## 📚 Guidelines Catalog

### Core Architecture

1. **[Clean Architecture Layer Definitions](./clean-architecture-layer-definitions.md)**
   - **Purpose:** Defines the 5 layers of Clean Architecture with dependency rules
   - **Audience:** All agents, architects, developers
   - **Key Content:**
     - Domain, Use Case, Internal Infrastructure, External Infrastructure, Presentation layers
     - Compiler-enforced boundaries via project separation
     - Port interface patterns
     - Prohibited patterns and violations
   - **When to Use:** Every architecture design, code review, legacy API modernization

2. **[Architecture Diagrams and Patterns](./architecture-diagrams-and-patterns.md)**
   - **Purpose:** Visual references and sequence diagrams for common patterns
   - **Audience:** All agents, architects
   - **Key Content:**
     - Layer dependency graph
     - Project reference graph
     - Application dependency graph (multi-app isolation)
     - Fee calculation example (complex repository usage)
     - Cancel membership example (cross-domain communication)
   - **When to Use:** Designing complex workflows, cross-domain integrations, multi-repository orchestrations

---

## 🎯 Usage by Workflow

### Legacy API Specification Generation

**Phase 1: Reverse Engineering**
- Reference: Clean Architecture Layer Definitions
- Goal: Identify which legacy classes belong in which layer
- Output: Business specification with layer mapping

**Phase 2: Technical Design**
- Reference: Both documents
- Goal: Design modern architecture with proper project separation
- Output: Technical design with project structure and dependency validation

**Phase 3: TDD Implementation**
- Reference: Clean Architecture Layer Definitions (validation)
- Goal: Implement in correct layers with proper dependencies
- Output: Code in separate projects with compiler-enforced boundaries

### Planning System 2.0

- Reference: Architecture Diagrams and Patterns (for sequence diagrams)
- Goal: Design complex multi-step workflows
- Output: Implementation plans with proper layer orchestration

### Code Review

- Reference: Clean Architecture Layer Definitions (prohibited patterns)
- Goal: Validate layer boundaries and project references
- Output: Compliance report with violations flagged

---

## 🔧 Validation Tools

### domain_boundary_checker.py

**Purpose:** Detect entity exposure violations and layer dependency issues

**Checks:**
- ❌ Controllers returning domain entities directly
- ❌ Domain layer referencing infrastructure
- ❌ Use Case layer referencing concrete infrastructure
- ❌ Cross-domain entity exposure

**Usage:**
```bash
python scripts/domain_boundary_checker.py --project RA.Api.Host
```

### project_reference_validator.py

**Purpose:** Validate .csproj references match Clean Architecture rules

**Checks:**
- ✅ Domain has NO references
- ✅ Use Case references Domain ONLY
- ✅ Infrastructure references Domain ONLY (Internal) or Use Case + Domain (External)
- ✅ Presentation references Domain + Use Case (code), ALL (DI)

**Usage:**
```bash
python scripts/project_reference_validator.py --solution Platform.Classic.sln
```

---

## 📊 Diagram Storage

**Location:** `cortex-brain/documents/guidelines/architecture/diagrams/`

**Files:**
- `layer-dependency-graph.png` - High-level layer relationships
- `project-reference-graph.png` - Concrete .csproj structure
- `application-dependency-graph.png` - Multi-app isolation pattern
- `fee-calculation-example.png` - Complex repository pattern dependencies
- `fee-calculation-sequence.png` - Sequence diagram for fee calculation
- `cancel-membership-example.png` - Cross-domain client pattern dependencies
- `cancel-membership-sequence.png` - Sequence diagram for cross-domain call

**Source:** Extracted from Platform.Classic Vision API documentation

---

## 🔄 Update Process

**When to Update:**
- New architectural patterns emerge from implementation
- Domain-specific variations discovered
- Anti-patterns identified and documented
- Vision API documentation updates

**How to Update:**
1. Identify new pattern or clarification needed
2. Update appropriate guideline document
3. Add example if applicable
4. Update this index
5. Notify agents via knowledge base refresh

**Ownership:** Architecture team + CORTEX maintainers

---

## 🚀 Quick Reference

| Scenario | Document | Section |
|----------|----------|---------|
| **What layer does X belong in?** | Clean Architecture Layer Definitions | Layer Definitions § 1-5 |
| **Can layer A reference layer B?** | Clean Architecture Layer Definitions | Project Reference Matrix |
| **How to call another domain?** | Architecture Diagrams and Patterns | Cancel Membership Example |
| **Complex multi-repository logic?** | Architecture Diagrams and Patterns | Fee Calculation Example |
| **Project structure example?** | Clean Architecture Layer Definitions | Compiler-Enforced Boundaries |
| **Prohibited patterns?** | Clean Architecture Layer Definitions | Prohibited Patterns |

---

## 📝 Related Documentation

**CORTEX Planning:**
- `cortex-brain/documents/planning/legacy-api-specification-generation-plan.md`

**Platform.Classic Standards:**
- `Platform.Classic/.github/instructions/ra-domain-standards.md` (to be created)
- `Platform.Classic/.github/instructions/databricks-sql.instructions.md`
- `Platform.Classic/.github/instructions/sql-server-sql.instructions.md`

**Framework Documentation:**
- DomainFramework (internal link)
- ClassicModernization (internal link)

---

**Last Updated:** December 15, 2025  
**Next Review:** Quarterly or as needed based on implementation feedback
