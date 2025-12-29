# Brain Ingestion Agent Guide

**Purpose:** Feature intelligence extraction and persistent brain storage  
**Version:** 1.0  
**Status:** ✅ Production Ready  
**Audience:** CORTEX Users building cross-session memory

---

## Overview

BrainIngestionAgent extracts feature intelligence from descriptions and implementation changes, then stores structured knowledge in CORTEX's Tier 2 Knowledge Graph and Tier 3 Context Intelligence for persistent cross-session memory.

**Key Capabilities:**
- 🧠 Feature intelligence extraction from natural language
- 📊 Entity recognition (files, classes, functions, concepts)
- 🔍 Implementation scanning (actual code changes)
- 💾 Tier 2 Knowledge Graph persistence
- 🎯 Pattern learning for future feature development
- 🔗 Relationship mapping between entities

---

## Quick Start

### Ingest Feature Intelligence

```
ingest to brain: "Added login authentication with JWT tokens in AuthService.cs"
```

or

```
learn this: I implemented user registration with email verification
```

**Result:**
- ✅ Entities extracted: AuthService, JWT, login, authentication
- ✅ Patterns stored: authentication implementation, token usage
- ✅ Context saved to Tier 2 Knowledge Graph
- ✅ Cross-session memory enabled for planning/TDD workflows

---

## Usage Scenarios

### Scenario 1: Feature Completion Intelligence

**User:** "ingest to brain: Completed payment processing integration with Stripe API. Created PaymentService.cs, added webhook handling, and implemented retry logic for failed transactions."

**BrainIngestionAgent:**
1. **Entity Extraction:**
   - Files: PaymentService.cs
   - Classes: PaymentService
   - Functions: webhook handling, retry logic
   - Concepts: payment processing, Stripe API, transactions

2. **Pattern Recognition:**
   - API Integration pattern detected (external service + webhooks)
   - Resilience pattern detected (retry logic)
   - Payment domain pattern detected

3. **Knowledge Graph Storage:**
   ```
   Namespace: payment_processing
   Entities:
     - PaymentService (class, confidence: 0.9)
     - Stripe API (concept, confidence: 0.8)
     - webhook handling (function, confidence: 0.7)
   
   Patterns:
     - API integration with webhooks (confidence: 0.85)
     - Retry pattern for failures (confidence: 0.8)
   
   Relationships:
     - PaymentService implements Stripe API integration
     - webhook handling uses retry logic
   ```

4. **Future Planning Impact:**
   - When user says "plan refund feature", CORTEX knows PaymentService exists
   - Planning system suggests webhook approach (learned pattern)
   - TDD workflow generates tests based on retry pattern

---

### Scenario 2: Architecture Decision Recording

**User:** "remember this: We decided to use Redis for session caching because SQL Server was too slow for 10,000 concurrent users. Session timeout is 30 minutes."

**BrainIngestionAgent:**
1. **Entity Extraction:**
   - Concepts: Redis, session caching, SQL Server, concurrent users
   - Decision: Redis over SQL Server for performance

2. **Context Intelligence:**
   ```
   Decision Record:
     Type: Architecture
     Problem: SQL Server too slow for session caching
     Solution: Redis for session caching
     Constraint: 10,000 concurrent users
     Configuration: 30-minute timeout
   ```

3. **Knowledge Graph Storage:**
   - Stores as architectural decision in `architecture_decisions` namespace
   - Cross-references with performance constraints
   - Links to session management patterns

4. **Future Impact:**
   - When planning similar caching features, suggests Redis
   - Remembers 30-minute timeout convention
   - Warns if SQL Server suggested for high-concurrency caching

---

### Scenario 3: Problem-Solution Learning

**User:** "learn this: We fixed the memory leak in DocumentParser by disposing the StreamReader in a using statement. Previously it was leaking 50MB per parse operation."

**BrainIngestionAgent:**
1. **Entity Extraction:**
   - Classes: DocumentParser
   - Functions: StreamReader disposal
   - Concepts: memory leak, resource management

2. **Pattern Recognition:**
   - Problem pattern: Memory leak from undisposed resources
   - Solution pattern: Using statement for IDisposable
   - Impact: 50MB leak per operation (quantified)

3. **Knowledge Graph Storage:**
   ```
   Problem-Solution Pair:
     Problem: Memory leak in DocumentParser (50MB/operation)
     Root Cause: StreamReader not disposed
     Solution: Using statement for automatic disposal
     Pattern: IDisposable resource management
     Severity: High (memory exhaustion risk)
   ```

4. **Future Impact:**
   - TDD workflow generates using statements for IDisposable
   - Code review suggests disposal checks
   - Planning system flags potential memory issues

---

## Entity Types & Confidence

**Entity Types:**

| Type | Description | Examples | Base Confidence |
|------|-------------|----------|----------------|
| **File** | Source code files | `AuthService.cs`, `login.component.ts` | 0.8 |
| **Class** | Classes/Services | `PaymentService`, `UserController` | 0.7 |
| **Function** | Methods/Functions | `authenticate()`, `processPayment()` | 0.6 |
| **Concept** | Abstract ideas | authentication, API, database | 0.5 |

**Confidence Boosters:**
- **Multiple mentions** (+0.05 per mention, max +0.2)
- **Implementation keywords** (+0.1 for "implement", "create", "add", "build")
- **Context relevance** (+0.1 for related terms nearby)

**Confidence Threshold:**
- **High (>0.8):** Strong entity, definitely related to feature
- **Medium (0.5-0.8):** Likely related, may need validation
- **Low (<0.5):** Weak signal, filtered out

---

## Brain Storage Tiers

### Tier 2: Knowledge Graph

**Structured storage for:**
- Feature patterns (authentication, API integration, caching)
- Entity relationships (PaymentService → Stripe API)
- Architecture decisions (Redis for caching)
- Problem-solution pairs (memory leak fixes)

**Namespace Convention:**
- Feature-based: `payment_processing`, `authentication`, `user_management`
- Decision-based: `architecture_decisions`, `performance_optimizations`
- Problem-based: `bug_fixes`, `refactoring_patterns`

**Retrieval:**
```
show context payment_processing
```

---

### Tier 3: Context Intelligence

**Time-series data for:**
- Implementation changes over time
- Pattern evolution (how authentication approach changed)
- Feature completion velocity (time to implement similar features)
- Decision impact tracking (did Redis solve the performance issue?)

**Auto-integration:**
- Planning system reads Tier 3 for similar feature estimates
- TDD workflow uses past test patterns
- Optimization suggests refactoring based on change frequency

---

## Configuration

**Ingestion Settings (cortex.config.json):**
```json
{
  "brain_ingestion": {
    "entity_confidence_threshold": 0.5,
    "max_entities_per_feature": 20,
    "enable_implementation_scan": true,
    "auto_namespace_detection": true,
    "pattern_matching": {
      "exact_match_weight": 0.9,
      "partial_match_weight": 0.7,
      "context_match_weight": 0.5,
      "keyword_match_weight": 0.3
    }
  }
}
```

**Entity Extraction Patterns:**
- Files: `filename.ext`, `path/to/file.ext`
- Classes: `XxxService`, `XxxController`, `XxxManager`, `XxxAgent`
- Functions: `functionName()`, `authenticate`, `process`, `validate`
- Concepts: authentication, API, database, testing, security

---

## Integration with CORTEX Workflows

### With Planning System

1. User says: "plan OAuth 2.0 authentication"
2. Planning system queries brain: "show context authentication"
3. BrainIngestionAgent returns: past authentication patterns, related services
4. Planning uses learned patterns to generate better estimates and suggestions

### With TDD Workflow

1. User says: "start tdd for PaymentService refund feature"
2. TDD workflow queries brain: "show context payment_processing"
3. BrainIngestionAgent returns: PaymentService structure, Stripe patterns, webhook examples
4. TDD generates tests based on existing payment patterns

### With Optimization

1. Optimization scans codebase for performance issues
2. Queries brain: "show context performance_optimizations"
3. BrainIngestionAgent returns: past optimizations (Redis caching decision)
4. Suggests similar solutions for new bottlenecks

---

## Advanced Features

### Automatic Implementation Scanning

BrainIngestionAgent can scan actual code changes to enrich ingestion:

```python
# Detects from git diff:
- Files changed: PaymentService.cs, StripeAdapter.cs
- Functions added: ProcessRefund(), ValidateWebhook()
- Dependencies added: Stripe.NET package
- Test coverage: 12 new tests in PaymentServiceTests.cs
```

**Storage:**
- Links entities to actual files (not just mentions)
- Tracks test coverage per feature
- Maps dependencies for impact analysis

---

### Pattern Learning

**Detected Patterns:**
- **API Integration:** External service + adapter + retry logic + webhooks
- **Authentication:** Token generation + validation + refresh + storage
- **CRUD Operations:** Create + Read + Update + Delete + validation
- **Caching:** Cache check + fetch + store + expiration + invalidation

**Pattern Reuse:**
When building new features, CORTEX suggests:
- "Use API integration pattern (from Stripe implementation)"
- "Apply authentication pattern (from JWT implementation)"
- "Implement caching pattern (from Redis decision)"

---

### Relationship Mapping

**Entity Relationships:**
```
PaymentService
  ├─ implements Stripe API integration
  ├─ uses webhook handling
  ├─ depends on retry logic
  └─ tested by PaymentServiceTests

Stripe API
  ├─ integrated by PaymentService
  ├─ requires webhook endpoint
  └─ documented in Stripe docs
```

**Impact Analysis:**
- "What depends on PaymentService?" → Refund feature, Invoice generator
- "What uses Stripe API?" → PaymentService, SubscriptionService
- "What features need retry logic?" → Payment processing, External API calls

---

## Troubleshooting

### Issue: "Low confidence entities extracted"

**Cause:** Vague feature description with few technical details

**Solution:** Provide more specific descriptions:
```
❌ "added payment stuff"
✅ "implemented Stripe payment processing in PaymentService with webhook handling and retry logic"
```

---

### Issue: "Namespace not auto-detected"

**Cause:** Feature description doesn't match domain patterns

**Solution:** Explicitly specify namespace:
```
ingest to brain [namespace: custom_domain]: "description..."
```

---

### Issue: "Entities not appearing in planning"

**Cause:** Knowledge Graph not queried or namespace mismatch

**Solution:** Verify storage:
```
show context [namespace]
```

If empty, re-ingest with explicit namespace.

---

## Best Practices

**DO:**
- ✅ Ingest immediately after feature completion (context is fresh)
- ✅ Use specific technical terms (class names, API names, patterns)
- ✅ Quantify when possible ("50MB leak", "10,000 users", "30-minute timeout")
- ✅ Record decisions and rationale ("Redis because SQL Server was slow")
- ✅ Include problem-solution pairs for future reference

**DON'T:**
- ❌ Use vague descriptions ("added stuff", "fixed things")
- ❌ Skip ingestion (breaks cross-session learning)
- ❌ Ingest partial work (wait until feature is complete)
- ❌ Forget to verify storage (`show context` after ingestion)

---

## Related Commands

- `show context [namespace]` - View stored brain data for a namespace
- `plan [feature]` - Planning uses brain data automatically
- `start tdd` - TDD workflow queries brain for patterns
- `optimize cortex` - Optimization suggests based on past decisions
- `architect` - Architectural analysis saves to brain automatically

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX

**Version:** 1.0  
**Last Updated:** November 25, 2025
