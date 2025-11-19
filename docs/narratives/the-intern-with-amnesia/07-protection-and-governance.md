# Chapter 07: Protection & Governance

*Part of The Intern with Amnesia - The CORTEX Story*  
*Author: Asif Hussain | © 2024-2025*  
*Generated: November 19, 2025*

---

## Overview

**Concept:** Rules that prevent self-sabotage  
**Technical Mapping:** Brain Protection Rules (SKULL governance)

---

## The Story

Like your brain's instinctive reflexes that you can't override (breathing, blinking), Tier 0 contains **immutable core principles** that define CORTEX's fundamental behavior. These are the "DNA" of the system that **never changes**.

**What's in Tier 0:**
- **Definition of READY** - Work must have clear, actionable requirements before starting (RIGHT BRAIN enforces)
- **Test-Driven Development** - Always RED → GREEN → REFACTOR, no exceptions (LEFT BRAIN enforces)
- **Definition of DONE** - Zero errors, zero warnings, all tests passing (LEFT BRAIN validates)
- **Challenge User Changes** - If you propose risky changes to the brain, CORTEX MUST challenge you (BRAIN PROTECTOR enforces)
- **SOLID Principles** - Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **Local-First Architecture** - Zero external dependencies, works completely offline, fully portable
- **Incremental File Creation** - Large files (>100 lines) created in small increments to prevent "response length limit" errors

**Storage:** `governance/rules.md` (never moves, never expires, never changes)  
**Protection:** Cannot be modified without explicit Brain Protector challenge and approval

---

---

## Technical Deep Dive

### Brain Protection Rules (SKULL governance)


**Brain Protection System:**
- 22 SKULL rules across 6 protection layers
- Source: `cortex-brain/brain-protection-rules.yaml`
- Automated enforcement via Brain Protector agent
- Challenge mechanism for risky changes
- Multi-layer defense architecture

**Tier 0 Instincts (Immutable):**
- Test-Driven Development
- Definition of Ready/Done
- SOLID Principles
- Local-First Architecture
- Challenge User Changes (Rule #22)
- Incremental File Creation


---

## Key Takeaways

- 22 SKULL rules protect architectural integrity
- 6 protection layers provide comprehensive defense
- Brain Protector challenges risky changes automatically
- Governance prevents degradation over time


---

## Next Chapter

**[Chapter 08: Integration & Extensibility](./08-integration-and-extensibility.md)**

*Connecting to external tools and services*
