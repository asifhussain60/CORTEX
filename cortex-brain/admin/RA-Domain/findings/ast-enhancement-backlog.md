# AST Enhancement Backlog: Multi-Language Support Roadmap

**Current State:** Python-only AST analysis  
**Target State:** Multi-language support (C#, Java, TypeScript, Go)  
**Analysis Date:** December 11, 2025  
**Source:** RA Domain C# analysis gaps + future requirements

---

## 🎯 Executive Summary

The current CORTEX AST analysis toolkit is **Python-specific** using the `ast` module. The Reimbursement Accounts (RA) domain analysis revealed the need for **C# AST capabilities** to analyze .NET codebases. This document outlines **52+ enhancements** needed to support multi-language analysis.

**Business Drivers:**
1. **RA Domain is C#/.NET** - Current analysis is incomplete (missing properties, methods, relationships)
2. **Enterprise Diversity** - Real-world codebases use C#, Java, TypeScript, Go
3. **Competitive Advantage** - Multi-language support differentiates CORTEX from Python-only tools

---

## 📊 Current Limitations (C# Analysis)

### What We Successfully Extracted
✅ **Entity Names** - All 30 entities discovered  
✅ **Namespaces** - Fully qualified names  
✅ **File Paths** - Complete file structure  
✅ **Line Numbers** - Class declarations  
✅ **Service Methods** - Method signatures from CarryoverDollarsDomainService  
✅ **XML Documentation** - Where present (e.g., BalanceChangeAudit)

### What We Could NOT Extract
❌ **Entity Properties** - All entities show `"properties": []`  
❌ **Navigation Properties** - All entities show `"navigation_properties": []`  
❌ **Attributes** - All entities show `"attributes": []`  
❌ **Base Classes** - All entities show `"inherits": []`  
❌ **Method Bodies** - Business logic inaccessible  
❌ **Type Inference** - Property types unknown  
❌ **Relationship Mapping** - Foreign keys, 1:N, N:M unknown  
❌ **Enum Values** - Enumeration members missing

**Impact:** 70% of domain model details are missing, requiring manual inference

---

## 🚀 Enhancement Backlog (52+ Items)

### Phase 1: C# AST Foundation (8 enhancements)

#### ENH-001: Integrate Roslyn C# Parser
**Priority:** CRITICAL  
**Effort:** 40 hours  
**Complexity:** High

**Description:**
Replace regex-based C# parsing with **Roslyn** (official C# compiler platform from Microsoft).

**Implementation:**
- Install `Microsoft.CodeAnalysis.CSharp` NuGet package
- Create Python wrapper using `pythonnet` or subprocess calls
- Parse `.cs` files into Roslyn `SyntaxTree`
- Extract semantic model for type information

**Benefits:**
- 100% accurate parsing (same parser as Visual Studio)
- Access to semantic analysis (type resolution, inheritance chains)
- Support for latest C# language features (C# 12)

**Alternatives:**
- `Tree-sitter` (fast but less semantic analysis)
- `srcML` (XML-based, cross-language)

---

#### ENH-002: Extract C# Entity Properties
**Priority:** CRITICAL  
**Effort:** 16 hours  
**Complexity:** Medium

**Description:**
Extract all properties from C# entities with full metadata.

**Required Fields:**
- `property_name` (e.g., "EmployerId")
- `property_type` (e.g., "string", "Guid", "decimal")
- `is_nullable` (bool)
- `default_value` (if present)
- `attributes` (e.g., `[Required]`, `[MaxLength(50)]`)
- `xml_doc` (documentation comments)

**Example Output:**
```json
{
  "name": "Employer",
  "properties": [
    {
      "name": "EmployerId",
      "type": "Guid",
      "is_nullable": false,
      "attributes": ["Key", "Required"],
      "xml_doc": "Unique identifier for employer"
    },
    {
      "name": "CompanyName",
      "type": "string",
      "is_nullable": false,
      "attributes": ["Required", "MaxLength(200)"],
      "xml_doc": "Legal entity name"
    }
  ]
}
```

---

#### ENH-003: Extract C# Navigation Properties
**Priority:** CRITICAL  
**Effort:** 16 hours  
**Complexity:** Medium

**Description:**
Identify navigation properties (Entity Framework relationships).

**Detection Logic:**
- Properties of type `ICollection<T>` (One-to-Many)
- Properties of reference types with `virtual` keyword (Lazy loading)
- Properties with `[ForeignKey]` attribute

**Example Output:**
```json
{
  "name": "Employer",
  "navigation_properties": [
    {
      "name": "Members",
      "type": "ICollection<Member>",
      "relationship": "OneToMany",
      "inverse_property": "Employer"
    },
    {
      "name": "ReimbursementPlans",
      "type": "ICollection<ReimbursementPlan>",
      "relationship": "OneToMany",
      "inverse_property": "Employer"
    }
  ]
}
```

---

#### ENH-004: Extract C# Attributes
**Priority:** HIGH  
**Effort:** 12 hours  
**Complexity:** Medium

**Description:**
Parse attributes (annotations) on classes, properties, methods.

**Attribute Categories:**
- **Data Annotations:** `[Required]`, `[MaxLength]`, `[Range]`
- **Entity Framework:** `[Key]`, `[ForeignKey]`, `[Index]`
- **Validation:** `[EmailAddress]`, `[CreditCard]`
- **Custom:** Project-specific attributes

**Example Output:**
```json
{
  "property": "Email",
  "attributes": [
    {
      "name": "Required",
      "arguments": []
    },
    {
      "name": "EmailAddress",
      "arguments": []
    },
    {
      "name": "MaxLength",
      "arguments": [100]
    }
  ]
}
```

---

#### ENH-005: Extract Inheritance Chains
**Priority:** HIGH  
**Effort:** 12 hours  
**Complexity:** Medium

**Description:**
Identify base classes and interfaces.

**Example Output:**
```json
{
  "name": "ReimbursementAccount",
  "inherits": ["BaseEntity", "IAuditable"],
  "inheritance_chain": [
    "ReimbursementAccount",
    "BaseEntity",
    "object"
  ]
}
```

---

#### ENH-006: Extract Method Bodies (Business Logic)
**Priority:** HIGH  
**Effort:** 24 hours  
**Complexity:** High

**Description:**
Parse method implementations to extract business rules.

**Extraction Targets:**
- Conditional statements (`if`, `switch`)
- Loop structures (`for`, `foreach`, `while`)
- LINQ queries
- Exception handling (`try-catch`)
- Return statements

**Use Case:** Extract IRS carryover calculation logic from `CalculateCarryoverAmountAllowedAtPlanYearEnd`

---

#### ENH-007: Type Inference and Resolution
**Priority:** HIGH  
**Effort:** 20 hours  
**Complexity:** High

**Description:**
Resolve types for properties, method parameters, return values.

**Challenges:**
- Generic types (`List<T>`, `IEnumerable<T>`)
- Nullable reference types (`string?`)
- Implicit types (`var`)
- Type aliases (`using Money = System.Decimal`)

---

#### ENH-008: Enum Value Extraction
**Priority:** MEDIUM  
**Effort:** 8 hours  
**Complexity:** Low

**Description:**
Extract enum members with values.

**Example Output:**
```json
{
  "name": "PlanType",
  "type": "enum",
  "members": [
    {"name": "FSA", "value": 0},
    {"name": "HSA", "value": 1},
    {"name": "HRA", "value": 2},
    {"name": "DependentCare", "value": 3}
  ]
}
```

---

### Phase 2: Advanced C# Analysis (12 enhancements)

#### ENH-009: LINQ Query Analysis
Extract LINQ queries to understand data access patterns.

#### ENH-010: Entity Framework Mapping
Infer database schema from Entity Framework configurations.

#### ENH-011: Dependency Injection Analysis
Map constructor injection dependencies.

#### ENH-012: Async/Await Pattern Detection
Identify asynchronous code paths.

#### ENH-013: Exception Handling Extraction
Catalog try-catch blocks and exception types.

#### ENH-014: NuGet Dependency Analysis
Parse `.csproj` files for package references.

#### ENH-015: XML Documentation Parsing
Extract all `<summary>`, `<param>`, `<returns>` tags.

#### ENH-016: Code Metrics Calculation
Cyclomatic complexity, lines of code, nesting depth.

#### ENH-017: Design Pattern Detection
Identify Repository, Factory, Strategy patterns.

#### ENH-018: SOLID Violation Detection
Flag SRP, OCP, LSP, ISP, DIP violations.

#### ENH-019: Performance Anti-Pattern Detection
N+1 queries, synchronous I/O, excessive allocations.

#### ENH-020: Security Vulnerability Scanning
SQL injection, XSS, CSRF risks.

---

### Phase 3: Java Support (10 enhancements)

#### ENH-021: Java AST Parser Integration
Use `javalang` or Eclipse JDT for parsing.

#### ENH-022: Java Annotation Extraction
Spring annotations (`@Entity`, `@Service`, `@Autowired`).

#### ENH-023: Spring Framework Analysis
Dependency injection, bean lifecycle, AOP.

#### ENH-024: Hibernate ORM Mapping
Extract JPA entities and relationships.

#### ENH-025: Maven/Gradle Dependency Analysis
Parse `pom.xml` and `build.gradle`.

#### ENH-026-030: (5 more Java-specific enhancements)

---

### Phase 4: TypeScript Support (10 enhancements)

#### ENH-031: TypeScript AST Parser Integration
Use `ts-morph` or TypeScript Compiler API.

#### ENH-032: Interface Extraction
TypeScript interfaces and type aliases.

#### ENH-033: Decorator Analysis
Angular/NestJS decorators (`@Component`, `@Injectable`).

#### ENH-034: React Component Analysis
Props, state, hooks extraction.

#### ENH-035: Node.js Module System
CommonJS vs ES Modules.

#### ENH-036-040: (5 more TypeScript-specific enhancements)

---

### Phase 5: Go Support (8 enhancements)

#### ENH-041: Go AST Parser Integration
Use `go/ast` package.

#### ENH-042: Struct Field Extraction
Equivalent to C# properties.

#### ENH-043: Interface Analysis
Go interfaces and implementations.

#### ENH-044: Goroutine Detection
Concurrency patterns.

#### ENH-045-048: (4 more Go-specific enhancements)

---

### Phase 6: Cross-Language Analysis (4 enhancements)

#### ENH-049: Multi-Language Relationship Mapping
Map C# backend → TypeScript frontend.

#### ENH-050: API Contract Extraction
REST/GraphQL endpoint documentation.

#### ENH-051: Cross-Language Dependency Graph
Service-to-service communication.

#### ENH-052: Unified Reporting Format
Language-agnostic JSON schema.

---

## 🛠️ Implementation Roadmap

### Q1 2026: C# Foundation (Phase 1)
**Focus:** Make C# analysis complete  
**Enhancements:** ENH-001 through ENH-008  
**Effort:** 148 hours (4 weeks FTE)  
**Deliverable:** 100% complete C# entity extraction

### Q2 2026: C# Advanced (Phase 2)
**Focus:** Business logic, patterns, metrics  
**Enhancements:** ENH-009 through ENH-020  
**Effort:** 200 hours (5 weeks FTE)  
**Deliverable:** Deep C# analysis (LINQ, EF, DI, patterns)

### Q3 2026: Java Support (Phase 3)
**Focus:** Enterprise Java applications  
**Enhancements:** ENH-021 through ENH-030  
**Effort:** 160 hours (4 weeks FTE)  
**Deliverable:** Spring Boot analysis

### Q4 2026: TypeScript + Go (Phases 4-5)
**Focus:** Frontend and microservices  
**Enhancements:** ENH-031 through ENH-048  
**Effort:** 240 hours (6 weeks FTE)  
**Deliverable:** Full-stack analysis

### Q1 2027: Cross-Language (Phase 6)
**Focus:** End-to-end system understanding  
**Enhancements:** ENH-049 through ENH-052  
**Effort:** 80 hours (2 weeks FTE)  
**Deliverable:** Unified multi-language reports

---

## 📈 Success Metrics

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| **C# Entity Properties** | 0% | 100% | Q1 2026 |
| **C# Navigation Props** | 0% | 100% | Q1 2026 |
| **C# Method Bodies** | 30% | 100% | Q2 2026 |
| **Languages Supported** | 1 (Python) | 5 (Py, C#, Java, TS, Go) | Q1 2027 |
| **Analysis Accuracy** | 70% | 95% | Q2 2026 |

---

## 💰 Business Value

**Current Limitation Cost:**
- **RA Domain Analysis:** 50+ hours manual inference (properties, relationships)
- **Enterprise Sales:** Cannot analyze C#/Java codebases (lost opportunities)

**Post-Enhancement Value:**
- **Time Savings:** 90% reduction in manual analysis (5 hours vs 50 hours)
- **Market Expansion:** Support 90% of enterprise codebases (C#, Java, TypeScript)
- **Competitive Edge:** Only tool supporting C# DDD analysis at this depth

---

## 📁 References

**Current Implementation:**
- `cortex-brain/admin/RA-Domain/scripts/analyze_ra_domain.py` - Python AST toolkit
- `ast-outputs/complete-csharp-analysis.json` - Partial C# analysis

**Target Libraries:**
- **C#:** Roslyn (`Microsoft.CodeAnalysis.CSharp`)
- **Java:** Eclipse JDT (`org.eclipse.jdt.core`)
- **TypeScript:** ts-morph (`ts-morph` npm package)
- **Go:** go/ast (built-in)

---

**Document Version:** 1.0  
**Last Updated:** December 11, 2025  
**Prepared By:** CORTEX AST Deep Analysis | Author: Asif Hussain  
**Copyright © 2025 Asif Hussain. All rights reserved.**
