# STS Before/After Diagram

---
title: Sharpen The Saw — Demo Repository Transformation
type: diagram
audience: [Software Developers, Product Owners]
last_verified: 2026-02-27
source_of_truth: cortex-sts/CortexLabs/
order: 15
---

> Side-by-side comparison of the BadMonolith demo repo before and after CORTEX transformation.

## STS Transformation

```
  BEFORE (BadMonolith)              AFTER (Refactored)
  ─────────────────────            ────────────────────
  ┌─────────────────────┐          ┌─────────────────────┐
  │ bad_monolith/       │          │ refactored/         │
  │ ├── giant_file.cs   │   ──▶    │ ├── Services/       │
  │ │   (2,000+ lines)  │          │ │   ├── AuthSvc.cs  │
  │ │   No patterns     │          │ │   ├── OrderSvc.cs │
  │ │   No tests        │          │ │   └── PaymentSvc  │
  │ │   No separation   │          │ ├── Models/         │
  │ └── app.config      │          │ ├── Interfaces/     │
  └─────────────────────┘          │ ├── Tests/          │
                                   │ └── appsettings.json│
  Issues:                          └─────────────────────┘
  • 0 tests
  • 0 interfaces                   Improvements:
  • 1 god class                    • Full test suite
  • No DI                          • Interface contracts
  • No error handling              • DI + IoC container
  • Hardcoded config               • Error handling
                                   • Configuration system

  Transformation Pipeline:
  /onboard → /digest → /challenge → SDLC 7-phase → CORTEX patterns
```

**Detailed diagram:** `flat-files/diagrams/diagram-20-sts-before-after.md`
**Full documentation:** `flat-files/15-sharpen-the-saw.md`

---

*Source: `cortex-sts/CortexLabs/BadMonolith/` · `cortex-sts/CortexLabs/Refactored/`*
