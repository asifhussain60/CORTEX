# Architecture Tooling and Agent Index

**Purpose:** Quick reference for all architecture-related tools and agents  
**Updated:** December 15, 2025

---

## 🛠️ Validation Tools

### domain_boundary_checker.py

**Location:** `scripts/architecture/domain_boundary_checker.py`

**Purpose:** Detect Clean Architecture boundary violations

**Checks:**
- ❌ Entity exposure (domain entities in API responses)
- ❌ Cross-domain entity usage (RA using Employer/Plan/Member)
- ❌ Layer dependency violations (Domain → Infrastructure)

**Usage:**
```bash
# Check single file
python scripts/architecture/domain_boundary_checker.py --file Controllers/FundingInvoiceController.cs

# Check project
python scripts/architecture/domain_boundary_checker.py --project RA.Api.Host

# Check solution (filter by domain)
python scripts/architecture/domain_boundary_checker.py --solution Platform.Classic.sln --domain RA

# Save report
python scripts/architecture/domain_boundary_checker.py --project RA.Api.Host --output boundary-report.txt
```

**Exit Codes:**
- `0` - No violations
- `1` - Violations found

---

### project_reference_validator.py

**Location:** `scripts/architecture/project_reference_validator.py`

**Purpose:** Validate .csproj references match Clean Architecture rules

**Checks:**
- ✅ Domain has NO references
- ✅ UseCase references Domain ONLY
- ✅ Infrastructure references Domain ONLY (Internal) or UseCase+Domain (External)
- ⚠️  Presentation references Infrastructure (DI setup warning)

**Usage:**
```bash
# Check single project
python scripts/architecture/project_reference_validator.py --project RA.DomainCore/RA.DomainCore.csproj

# Check solution
python scripts/architecture/project_reference_validator.py --solution Platform.Classic.sln

# Filter by domain
python scripts/architecture/project_reference_validator.py --solution Platform.Classic.sln --domain RA

# Save report
python scripts/architecture/project_reference_validator.py --solution Platform.Classic.sln --output reference-report.txt
```

**Output:**
- Validation report with compliance score
- Errors (must fix)
- Warnings (DI-only usage)
- Valid references summary

**Exit Codes:**
- `0` - All references valid
- `1` - Invalid references found

---

## 🤖 Architecture Agents

### legacy-specification-generator

**Location:** `cortex-brain/agents/architecture/legacy-specification-generator-agent.md`

**Purpose:** Reverse engineer legacy WCF code into business specifications

**Input:**
- Legacy WCF transaction files (XAdd*, XUpdate*, XClose*)
- Context from similar APIs

**Output:**
- `business-spec.md` - Human-readable specification
- `data-flow.mmd` - Mermaid diagram
- `layer-mapping.md` - Domain/UseCase/Infrastructure classification
- `review-checklist.md` - PM/BA validation questions

**Invocation:**
```
plan ado ra-api Segment4/HETransactions/XAddFundingInvoice.cs
```

**Key Features:**
- Extracts business rules from code
- Plain English descriptions
- PM/BA friendly format
- Layer mapping for Clean Architecture

---

### modern-architecture-designer

**Location:** `cortex-brain/agents/architecture/modern-architecture-designer-agent.md`

**Purpose:** Design Clean Architecture implementations from specifications

**Input:**
- Approved business specification
- Architecture guidelines
- Similar API designs

**Output:**
- `technical-design.md` - 5-layer project structure
- `project-structure.txt` - Folder tree
- `architecture.mmd` - Sequence diagrams
- `dependency-matrix.md` - Project reference validation
- `traceability-template.csv` - Spec-to-code mapping template

**Invocation:**
```
design ra-api cortex-brain/documents/api-specifications/ra-domain/funding-invoice/business-spec.md
```

**Key Features:**
- Enforces Clean Architecture layers
- Validates project references
- Creates DTO wrappers
- OOB .NET framework usage

---

### tdd-implementation-orchestrator

**Location:** `cortex-brain/agents/architecture/tdd-implementation-orchestrator-agent.md` (referenced in plan)

**Purpose:** Implement specifications using TDD (RED→GREEN→REFACTOR)

**Input:**
- Approved technical design
- Business specification
- TDD enforcement rules

**Output:**
- Domain layer (entities, validators, interfaces)
- UseCase layer (orchestration)
- Infrastructure layers (repositories, clients)
- Presentation layer (controllers, DTOs)
- Test projects (unit + integration)
- `traceability.csv` (final with code references)

**Invocation:**
```
implement ra-api cortex-brain/documents/api-specifications/ra-domain/funding-invoice/technical-design.md
```

**Key Features:**
- RED phase (failing tests first)
- GREEN phase (minimal implementation)
- REFACTOR phase (Clean Architecture compliance)
- Layer-by-layer implementation
- Continuous validation

---

## 📚 Guidelines Documentation

### Clean Architecture Layer Definitions

**Location:** `cortex-brain/documents/guidelines/architecture/clean-architecture-layer-definitions.md`

**Content:**
- 5-layer definitions (Domain, UseCase, Internal/External Infrastructure, Presentation)
- Dependency rules
- Port interface patterns
- Prohibited vs correct patterns
- Project reference matrix

**Use When:** All architecture design, code review, migration planning

---

### Architecture Diagrams and Patterns

**Location:** `cortex-brain/documents/guidelines/architecture/architecture-diagrams-and-patterns.md`

**Content:**
- Layer dependency graph
- Project reference graph
- Application dependency graph
- Fee calculation example (complex logic)
- Cancel membership example (cross-domain)
- Pattern selection guide

**Use When:** Designing complex workflows, cross-domain integrations

---

### RA Domain Standards

**Location:** `Platform.Classic/.github/instructions/ra-domain-standards.md`

**Content:**
- RA-specific project naming (HealthEquity.RA.*)
- Prohibited cross-domain entities
- Repository patterns
- UseCase conventions
- API design standards
- Validation standards
- Security/logging standards

**Use When:** All RA domain development

---

## 🗂️ Folder Structure

```
CORTEX/
├── scripts/architecture/
│   ├── domain_boundary_checker.py
│   └── project_reference_validator.py
│
├── cortex-brain/
│   ├── agents/architecture/
│   │   ├── legacy-specification-generator-agent.md
│   │   └── modern-architecture-designer-agent.md
│   │
│   ├── documents/
│   │   ├── guidelines/architecture/
│   │   │   ├── README.md (index)
│   │   │   ├── clean-architecture-layer-definitions.md
│   │   │   ├── architecture-diagrams-and-patterns.md
│   │   │   └── diagrams/ (images)
│   │   │
│   │   ├── planning/
│   │   │   └── legacy-api-specification-generation-plan.md
│   │   │
│   │   └── pilot-projects/
│   │       └── xupdatefundingbatch-pilot-plan.md
│   │
│   └── knowledge-graph/ra-domain/
│       └── domain-patterns.yaml
│
Platform.Classic/
└── .github/instructions/
    └── ra-domain-standards.md
```

---

## 🚀 Quick Start Workflow

### New Legacy API Migration

1. **Generate Specification:**
   ```
   plan ado ra-api <legacy-file>
   ```
   Uses: `legacy-specification-generator`
   
2. **Get PM/BA Approval:**
   Review `business-spec.md` with stakeholders

3. **Design Architecture:**
   ```
   design ra-api <business-spec>
   ```
   Uses: `modern-architecture-designer`
   
4. **Validate Design:**
   ```bash
   python scripts/architecture/project_reference_validator.py --project <design-output>
   ```

5. **Implement with TDD:**
   ```
   implement ra-api <technical-design>
   ```
   Uses: `tdd-implementation-orchestrator`

6. **Validate Implementation:**
   ```bash
   python scripts/architecture/domain_boundary_checker.py --project <implementation>
   ```

7. **Run Tests & Deploy**

---

## 🔍 Troubleshooting

**Issue:** Domain boundary violations detected

**Solution:**
1. Run `domain_boundary_checker.py` with `--output` to save report
2. Review violations section
3. Apply suggested fixes (create DTOs, remove cross-domain references)
4. Re-run checker until clean

---

**Issue:** Invalid project references

**Solution:**
1. Run `project_reference_validator.py` on solution
2. Review ERROR sections (must fix)
3. Remove invalid references from .csproj files
4. Add interfaces/abstractions as needed
5. Re-run validator until compliance score 100%

---

**Issue:** Agent not following Clean Architecture

**Solution:**
1. Ensure agent has access to guidelines in context
2. Check agent prompt references correct files
3. Verify validation tools are available
4. Review agent output for layer mapping section

---

## 📊 Integration with CORTEX

**Planning System 2.0:**
- Architecture agents integrated via `copilot_chat` execution method
- Validation tools called during REFACTOR phase
- Guidelines referenced in agent context

**ADO Operations:**
- Architecture design included in ADO work item creation
- Traceability matrix links to ADO tasks
- Technical design attached to features/stories

**TDD Mastery:**
- Architecture layer compliance checked in REFACTOR phase
- Test structure follows layer separation
- Coverage reports per layer

---

**Maintained By:** Architecture Team + CORTEX Maintainers  
**Last Updated:** December 15, 2025
