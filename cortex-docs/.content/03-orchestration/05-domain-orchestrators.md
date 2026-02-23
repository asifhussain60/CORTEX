# Domain Orchestrators

---
title: Domain Orchestrators — Business-Vertical Specialization
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-20
source_of_truth: cortex/orchestrators/domain/
order: 5
---

> **Brain analogy:** Domain orchestrators are **specialized brain regions** for specific types of knowledge — like the fusiform face area recognizes faces, and the parahippocampal place area recognizes places. Each domain orchestrator has deep knowledge of a specific business vertical.

## Domain Architecture

**Location:** `cortex/orchestrators/domain/` (30 files)

### Business Domain Orchestrators

| Orchestrator | Vertical | Capabilities |
|-------------|----------|-------------|
| **BusinessDomainOrchestrator** | Abstract base | Common domain patterns |
| **EcommerceOrchestrator** | Retail/ecommerce | Cart logic, payment flows, inventory |
| **FinancialOrchestrator** | Finance/banking | Transaction patterns, regulatory compliance |
| **HealthcareOrchestrator** | Healthcare | HIPAA patterns, patient data handling |
| **DomainOrchestrator** | General domain | Cross-vertical domain analysis |

### How Domain Routing Works

1. LENS Domain Analyzer detects business context
2. IntentRouter identifies domain-specific aspects
3. MasterOrchestrator delegates to the appropriate domain orchestrator
4. Domain orchestrator applies vertical-specific patterns and governance

**Practical Example:**
- "Implement payment processing" → Domain Analyzer detects financial context → FinancialOrchestrator applies PCI-DSS patterns + transaction integrity checks

---

*Verified against `cortex/orchestrators/domain/` · 20 February 2026*
