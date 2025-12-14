# Executive Narrative Template

**Purpose:** Transform AST data into business-focused narrative for leadership

**Target Audience:** C-level executives, VPs, product managers, business stakeholders

**Tone:** Business-focused, non-technical, outcome-oriented

**Length:** 1,500-2,000 words (7-10 minutes read time)

---

## Section 1: What Is This Application?

**Goal:** Establish context - industry, problem space, solution overview

**Synthesis Prompt:**
```
From the AST data showing {entity_count} domain models and {service_count} business services,
explain what this application is in business terms. 

Include:
- Industry/domain (healthcare, finance, etc.)
- Primary business problem it solves
- Core value proposition
- Scale indicators (users, transactions, accounts)

Avoid: Technical implementation details, code structure, frameworks

Example opening: "The Reimbursement Accounts platform manages healthcare spending accounts
for employers and their employees..."
```

**Data Sources:**
- `business-value-scan.json` → Business keywords, domain services
- `complete-csharp-analysis.json` → Overall system metrics
- `batch-3-1-entities.json` → Domain model entities

**Expected Output:** 200-250 words

---

## Section 2: Who Uses It?

**Goal:** Identify stakeholders and their relationship to the system

**Synthesis Prompt:**
```
Based on entity names ({Member}, {Employer}, {Administrator}) and service operations,
describe the primary users and their roles.

Include:
- Primary user types (employees, employers, admins)
- What each user accomplishes with the system
- User journey touchpoints
- Stakeholder relationships

Example: "Employers sponsor reimbursement accounts for their employees, who submit claims
for qualified medical expenses..."
```

**Data Sources:**
- `batch-3-1-entities.json` → User-related entities
- `carryover-service-methods.json` → User-facing operations

**Expected Output:** 150-200 words

---

## Section 3: Key Capabilities

**Goal:** Enumerate what the system does (functional areas)

**Synthesis Prompt:**
```
From the {service_count} business services and {method_count} operations,
identify 8-12 key capabilities.

Group by:
- Account management (lifecycle operations)
- Financial operations (contributions, reimbursements)
- Compliance operations (regulatory requirements)
- Administrative operations (reporting, configuration)

For each capability:
- Name (Claims Processing, Year-End Carryover, etc.)
- Business purpose (why it exists)
- Volume/scale (if available from metrics)

Example: "**Claims Processing** - Manages medical expense reimbursement requests,
processing both manual submissions and automated provider claims..."
```

**Data Sources:**
- `business-value-scan.json` → Domain services with business keywords
- `carryover-service-methods.json` → Specific workflow operations
- `batch-3-1-entities.json` → Supporting domain models

**Expected Output:** 300-400 words (bullet list with explanations)

---

## Section 4: Core Workflows

**Goal:** Explain how the system works end-to-end (user perspective)

**Synthesis Prompt:**
```
Using method signatures from services like CarryoverDollarsDomainService,
ReimbursementAccountBalanceService, describe 3-5 primary workflows.

For each workflow:
- Trigger (what starts it)
- Steps (high-level, non-technical)
- Outcome (what value is delivered)
- Frequency (annual, daily, real-time)

Example workflow structure:
"**Year-End Carryover Processing** - Each December 31st, the system automatically
transfers eligible funds from expiring plan years to the next year, enforcing IRS
contribution limits..."
```

**Data Sources:**
- `carryover-service-methods.json` → Detailed method flows
- `business-value-scan.json` → Domain service responsibilities

**Expected Output:** 250-300 words

---

## Section 5: Regulatory Compliance

**Goal:** Explain compliance requirements and how system enforces them

**Synthesis Prompt:**
```
From entity names (BalanceChangeAudit, CarryoverTransferTracking, Card) and
business keywords (IRS, HIPAA, PCI-DSS, ERISA), describe regulatory scope.

Include:
- Regulatory bodies (IRS, HHS/HIPAA, PCI Council)
- Specific requirements (contribution limits, audit trails, data protection)
- Business impact of non-compliance (penalties, risk)
- How system enforces (automated validations, audit trails)

Example: "IRS Publication 969 limits FSA carryover to $640 per year. The system
automatically enforces this during year-end processing, preventing over-contribution
penalties of up to $2,000 per violation..."
```

**Data Sources:**
- `carryover-service-methods.json` → Compliance-related operations
- `batch-3-1-entities.json` → Audit and tracking entities
- Existing: `EXECUTIVE-SUMMARY-BATCHES-1-7.md` → P0 compliance gaps

**Expected Output:** 250-300 words

---

## Section 6: Technical Architecture (Business View)

**Goal:** High-level technical overview without implementation details

**Synthesis Prompt:**
```
From project structure ({project_count} projects) and integration patterns
(NServiceBus events, batch jobs), describe architecture at business level.

Include:
- System components (web portals, background processors, event system)
- Integration approach (real-time vs batch, event-driven)
- Scalability indicators (batch sizes, concurrency)
- Reliability mechanisms (transactions, audit trails, retries)

Avoid: Specific technologies, code patterns, infrastructure details

Example: "The platform uses event-driven architecture to notify downstream systems
when account balances change, ensuring statements and reports reflect current data..."
```

**Data Sources:**
- `complete-csharp-analysis.json` → Project inventory
- `carryover-service-methods.json` → Event publishing patterns
- Existing: `complete-architecture-guide.md` → Architecture overview

**Expected Output:** 200-250 words

---

## Section 7: Integration Ecosystem

**Goal:** Show how system connects to broader enterprise

**Synthesis Prompt:**
```
From NServiceBus event publishing (BalanceChangedEvent) and downstream references,
describe integration points.

Include:
- Internal integrations (member portal, admin portal, reporting)
- External integrations (third-party administrators, payment processors)
- Data flows (inbound contributions, outbound disbursements)
- Event-driven updates (statement generation, analytics)

Example: "When a year-end carryover completes, the system publishes events to 3 downstream
systems: member statement generation (PDF creation), reporting warehouse (BI updates),
and third-party administrator systems (data synchronization)..."
```

**Data Sources:**
- `carryover-service-methods.json` → PublishBalanceChangedById method
- Existing: `complete-architecture-guide.md` → Integration points section

**Expected Output:** 150-200 words

---

## Section 8: Developer Insights (NEW - With Comment Extraction)

**Goal:** Capture tribal knowledge from code comments - regulatory citations, business rules, design decisions

**Synthesis Prompt:**
```
Using developer comments from code ({regulatory_comment_count} regulatory refs, {business_comment_count} business rules),
extract insights that explain WHY certain decisions were made, not just WHAT the code does.

Include:
- Regulatory compliance context (IRS/HIPAA citations with business impact)
- Business rule rationale (why contribution limits exist, why grace periods matter)
- Known limitations (TODO/FIXME with business impact, not just technical debt)
- Design decisions (architectural choices explained in developer comments)

Example: "Developers note in comments that balance validation must occur before any distribution
to comply with IRS Publication 969 §223(d)(2), which prevents tax penalties for employers if 
accounts are improperly managed. This requirement explains why the system performs 3 separate
validation steps before approving reimbursements..."

Filter:
- Skip boilerplate comments (copyright, auto-generated)
- Focus on critical/high relevance comments only
- Link comments to business outcomes (not technical implementation)
- Prioritize regulatory and compliance references
```

**Data Sources:**
- `comment-extraction.json` → All developer comments with categorization
- `comment-statistics.json` → Regulatory keyword counts
- Filter: `business_relevance == 'critical' OR 'high'`
- Focus: Comments with `regulatory_keywords` or `business_keywords`

**Expected Output:** 250-300 words

---

## Assembly Instructions

1. **Generate each section** using synthesis prompts with actual data
2. **Sequence sections** in numbered order above (1-8)
3. **Add transitions** between sections for narrative flow
4. **Include metrics** from AST analysis (entity counts, service counts)
5. **Integrate comment insights** into Sections 3, 4, 5 (capabilities, workflows, compliance)
6. **Cite sources** at section end (JSON file references)
7. **Format** as markdown with H2 headers, bullets, emphasis
8. **Validate**:
   - Total word count 1,800-2,200 (increased with Section 8)
   - No technical jargon (unless defined)
   - Business outcomes emphasized
   - Real data included (not generic statements)
   - Developer insights add context, not noise

---

## Quality Checklist

- [ ] Non-technical language throughout
- [ ] Explains "what" and "why", not "how"
- [ ] Includes real metrics from AST data
- [ ] References regulatory requirements
- [ ] Shows business value/outcomes
- [ ] Target length achieved (1,800-2,200 words with Section 8)
- [ ] All 8 sections present (7 original + developer insights)
- [ ] Data sources cited
- [ ] Executive-appropriate tone
- [ ] Developer comments enhance business understanding (not technical details)
