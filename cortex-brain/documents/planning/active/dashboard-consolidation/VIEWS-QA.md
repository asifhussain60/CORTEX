# Dashboard Views Analysis - Questions & Answers

**Created:** December 4, 2025  
**Updated:** December 4, 2025 (Removed API Documentation - Current State Principle)  
**Reference:** dashboard-advanced-views-specification.md  
**Plan:** unified-dashboard-2025-12-04  
**Purpose:** Answer specific questions about dashboard capabilities and view types

**🎯 GUIDING PRINCIPLE:** Dashboard visualizes **CURRENT STATE ONLY** - actual runtime data from existing code, not aspirational features or desired capabilities.

---

## 📋 Your Questions Answered

### Q1: What kind of views can be generated based on Phase 1-2 data?

**Answer:** Based on the universal health data schema from Phase 1-2, we can generate **9 advanced view types** beyond the basic dashboard (reduced from 10 after removing API Documentation per Current State Principle):

#### ✅ Already in Schema (Core Views)
1. **Overview Dashboard** - Health score, key metrics, status indicators
2. **Metrics View** - Code metrics, activity, performance, LOC breakdown
3. **Code Quality View** - Complexity, maintainability, technical debt
4. **Dependencies View** - Dependency tree, vulnerabilities, outdated packages

#### 🎯 Require Schema Extensions (Advanced Views)
5. **Tech Stack View** - Technology inventory (answered below)
6. **Architecture View** - Tier diagrams, UML/ERD (answered below)
7. **Security View** - Multi-angle security analysis (answered below)
8. **Code Organization View** - Heatmaps, complexity hotspots
9. **Team Productivity View** - Contribution graphs, PR metrics (optional)

**Additional Views Possible:**
10. Test Coverage Map
11. Performance Insights
12. Change Impact Analysis
13. **Dependency Deep Dive** - Code dependencies + external vendor integrations (detailed below)
14. Knowledge Distribution Map

**⚠️ CRITICAL PRINCIPLE: CURRENT STATE ONLY**
- Dashboard visualizes **ACTUAL runtime state** of the application
- No aspirational features, planned capabilities, or desired state
- All metrics reflect real, measurable, existing data
- Views must query actual files, dependencies, code - not mock data

---

### Q2: Tech Stack View - Detailed Requirements

**Purpose:** List current technology stack across entire application (views, API, database), tools, libraries, utilities with version numbers and deprecation status.

#### What It Shows:

**A. Frontend Technologies**
```
┌─────────────────────────────────────────────────┐
│ Framework    │ Version  │ Status    │ EOL Date │
├──────────────┼──────────┼───────────┼──────────┤
│ React        │ 18.2.0   │ ✅ Current │ -        │
│ TypeScript   │ 5.3.0    │ ✅ Current │ -        │
│ Blazor       │ 7.0.14   │ ⚠️ Update  │ 2024-05  │
│ jQuery       │ 3.6.0    │ ⚠️ Legacy  │ 2024-03  │
└──────────────┴──────────┴───────────┴──────────┘
```

**B. Backend Technologies**
```
┌─────────────────────────────────────────────────┐
│ Runtime      │ Version  │ Status    │ EOL Date │
├──────────────┼──────────┼───────────┼──────────┤
│ Python       │ 3.11.5   │ ✅ Current │ 2027-10  │
│ .NET         │ 8.0      │ ✅ Current │ 2026-11  │
│ Node.js      │ 20.10.0  │ ✅ LTS     │ 2026-04  │
└──────────────┴──────────┴───────────┴──────────┘
```

**C. Database Technologies**
```
┌─────────────────────────────────────────────────┐
│ Database     │ Version  │ Status    │ Notes    │
├──────────────┼──────────┼───────────┼──────────┤
│ SQLite       │ 3.43.0   │ ✅ Current │ FTS5     │
│ PostgreSQL   │ 15.3     │ ✅ Current │ Primary  │
│ Redis        │ 7.2.3    │ ✅ Current │ Cache    │
│ SQL Server   │ 2019     │ ⚠️ Update  │ Legacy   │
└──────────────┴──────────┴───────────┴──────────┘
```

**D. DevOps & Tools**
```
┌─────────────────────────────────────────────────┐
│ Tool         │ Version  │ Status    │ Purpose  │
├──────────────┼──────────┼───────────┼──────────┤
│ Docker       │ 24.0.7   │ ✅ Current │ Container│
│ GitHub Actions│ N/A     │ ✅ Active  │ CI/CD    │
│ pytest       │ 8.4.0    │ ✅ Current │ Testing  │
│ Webpack      │ 5.89.0   │ ✅ Current │ Bundler  │
└──────────────┴──────────┴───────────┴──────────┘
```

#### Status Legend:
- ✅ **Current:** Latest stable version, actively maintained
- ⚠️ **Update Available:** Newer version exists, recommended upgrade
- ⚠️ **Legacy:** Old version, still supported but consider modernizing
- ❌ **Deprecated:** End-of-life reached, urgent migration needed
- 🔒 **Security Risk:** Known vulnerabilities, immediate action required

#### Interactive Features:
- Click tech name → Show all files using that technology
- Click version → Show upgrade path and breaking changes
- Filter by status (Current/Update/Legacy/Deprecated)
- Export tech stack to CSV/JSON for documentation

#### Data Requirements (Schema Extension):
```json
{
  "custom_metrics": {
    "tech_stack": {
      "frontend": [
        {"name": "React", "version": "18.2.0", "latest": "18.2.0", "status": "current", "eol_date": null, "cve_count": 0}
      ],
      "backend": [...],
      "database": [...],
      "devops": [...]
    }
  }
}
```

#### Professional Presentation:
- Color-coded badges (green=current, yellow=update, red=deprecated)
- Sortable tables
- Filterable by category and status
- Exportable to PDF/CSV for stakeholder reports
- Timeline view showing EOL dates

---

### Q3: Architecture View - Visual Structure

**Purpose:** Show application tiers (UI → API → Database), generate UML diagrams, ERD, component relationships.

#### What It Shows:

**A. 3-Tier Architecture Diagram**
```
┌───────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Blazor UI  │  │  React SPA   │  │  REST API    │  │
│  │   (C#)       │  │  (TypeScript)│  │  (Python)    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌───────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Business    │  │  Use Cases   │  │  Services    │  │
│  │  Logic       │  │  (Clean Arch)│  │  Layer       │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌───────────────────────────────────────────────────────────┐
│                     DATA LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  SQLite DB   │  │  PostgreSQL  │  │  Redis Cache │  │
│  │  (Brain)     │  │  (Main DB)   │  │  (Sessions)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└───────────────────────────────────────────────────────────┘
```

**B. UML Class Diagram (Auto-Generated)**
For Clean Architecture projects:
- Entity classes
- Use case interfaces
- Repository patterns
- Dependency injection flow

**C. ERD (Entity Relationship Diagram)**
For database-heavy projects:
- Tables and relationships
- Primary/foreign keys
- Cardinality (1:1, 1:N, N:N)
- Indexes and constraints

**D. Component Dependency Graph**
Shows which components depend on which:
```
UI Layer → Service Layer → Data Layer
  │            │              │
  └─ Feature A ┤              │
  └─ Feature B ┴─ Service 1 ──┤
  └─ Feature C ┬─ Service 2 ──┴─ Database
  └─ Feature D ┘
```

#### Interactive Features:
- Click component → Show files, dependencies, metrics
- Zoom in/out on diagrams
- Toggle layers (show/hide presentation, business, data)
- Export diagrams as PNG/SVG
- Generate PlantUML/Mermaid code

#### Data Requirements:
```json
{
  "custom_metrics": {
    "architecture": {
      "style": "clean_architecture",
      "tiers": ["presentation", "application", "data"],
      "components": [
        {
          "name": "UserFeature",
          "tier": "application",
          "loc": 1250,
          "dependencies": ["UserRepository", "ValidationService"]
        }
      ],
      "database_schema": {
        "tables": ["users", "sessions", "logs"],
        "relationships": [
          {"from": "sessions", "to": "users", "type": "many_to_one"}
        ]
      }
    }
  }
}
```

---

### Q4: Security View - Multi-Angle Analysis

**Purpose:** List vulnerabilities and overall security status checked against various angles.

#### What It Shows:

**A. Security Scorecard**
```
┌─────────────────────────────────────────────────────┐
│ Security Posture: 85/100 (Good)         ✅          │
├─────────────────────────────────────────────────────┤
│ Last Scan: 2025-12-04 09:00 EST                    │
│ Scanner: Snyk + OWASP ZAP + Custom                 │
└─────────────────────────────────────────────────────┘

┌───────────────┬────────┬────────┬────────┬─────────┐
│   Category    │ Score  │ Issues │ Status │ Trend   │
├───────────────┼────────┼────────┼────────┼─────────┤
│ Code Security │ 90/100 │   2    │   ✅   │    ↑    │
│ Dependencies  │ 75/100 │   8    │   ⚠️   │    →    │
│ Authentication│ 95/100 │   1    │   ✅   │    ↑    │
│ Authorization │ 88/100 │   3    │   ✅   │    →    │
│ Data Security │ 80/100 │   5    │   ⚠️   │    ↓    │
│ Network       │ 92/100 │   1    │   ✅   │    ↑    │
└───────────────┴────────┴────────┴────────┴─────────┘
```

**B. Vulnerability Breakdown**
```
┌─────────────────────────────────────────────────────┐
│ Vulnerabilities by Severity                         │
├─────────────────────────────────────────────────────┤
│ 🔴 Critical: 0  (Target: 0)                         │
│ 🟠 High:     2  (Target: ≤ 3)    ⚠️ Above Target   │
│ 🟡 Medium:   8  (Target: ≤ 10)   ✅ Within Target  │
│ 🟢 Low:      15 (Target: ≤ 20)   ✅ Within Target  │
├─────────────────────────────────────────────────────┤
│ Total: 25 vulnerabilities                           │
│ Remediation Est: 12 hours                           │
└─────────────────────────────────────────────────────┘
```

**C. OWASP Top 10 (2021) Compliance**
```
┌─────────────────────────────────────────────────────┐
│ OWASP Top 10 (2021) Compliance                      │
├──────────────────────────────────────┬──────┬───────┤
│ Risk                                 │ Status│ Score │
├──────────────────────────────────────┼──────┼───────┤
│ A01: Broken Access Control          │  ✅  │ 92/100│
│ A02: Cryptographic Failures          │  ✅  │ 88/100│
│ A03: Injection                       │  ✅  │ 95/100│
│ A04: Insecure Design                 │  ⚠️  │ 75/100│
│ A05: Security Misconfiguration       │  ✅  │ 90/100│
│ A06: Vulnerable Components           │  ⚠️  │ 70/100│
│ A07: Auth Failures                   │  ✅  │ 95/100│
│ A08: Data Integrity Failures         │  ✅  │ 85/100│
│ A09: Logging Failures                │  ⚠️  │ 78/100│
│ A10: Server-Side Request Forgery     │  ✅  │ 98/100│
└──────────────────────────────────────┴──────┴───────┘
```

**D. Compliance Checklist**
- GDPR (General Data Protection Regulation)
- SOC 2 (System and Organization Controls)
- HIPAA (Health Insurance Portability and Accountability Act)
- PCI DSS (Payment Card Industry Data Security Standard)

#### Multiple Scan Angles:
1. **Code Security:** Static analysis (SQL injection, XSS, etc.)
2. **Dependency Security:** Vulnerable packages (Snyk, npm audit)
3. **Authentication:** Password policies, MFA, session management
4. **Authorization:** Role-based access, privilege escalation
5. **Data Security:** Encryption at rest/transit, PII handling
6. **Network Security:** HTTPS, CORS, CSP headers
7. **Infrastructure:** Container security, cloud misconfigurations

---

### Q5: What else would be useful for engineers and managers unfamiliar with the code?

**Recommended Views:**

#### For Engineers (Technical Deep Dive)
1. **Code Organization Heatmap** - Where is complexity concentrated?
2. **Test Coverage Map** - Which areas lack tests?
3. **Dependency Graph** - How are modules connected?
4. **Technical Debt Tracker** - What needs refactoring?
5. **Performance Insights** - Build times, test times, bottlenecks

#### For Managers (High-Level Overview)
1. **Team Productivity** - Who's contributing? Velocity trends?
2. **Project Health Summary** - One-page executive view
3. **Risk Assessment** - Critical issues, security risks, technical debt
4. **Resource Allocation** - Time spent on features vs bugs vs tech debt
5. **Knowledge Distribution** - Who knows what? Bus factor analysis

#### For New Team Members
1. **Getting Started Guide** - Architecture overview, setup instructions
2. **Code Navigation** - Key files, common patterns, entry points
3. **Domain Model** - Business entities, relationships, workflows
4. **Testing Strategy** - How to run tests, where to add new tests
5. **Deployment Process** - CI/CD pipeline, environment stages

#### For Architects
1. **Component Relationships** - Coupling, cohesion, dependencies
2. **Technology Choices** - Why was X chosen? When to upgrade?
3. **Scalability Analysis** - Performance bottlenecks, growth projections
4. **Integration Points** - External APIs, third-party services
5. **Data Flow Diagrams** - How does data move through the system?

---

### Q5.1: Dependency Deep Dive - Comprehensive Tracking

**Purpose:** Track ALL dependencies - code-level packages AND external vendor integrations - to provide complete visibility into application dependencies.

#### What It Shows:

**A. Code-Level Dependencies (Package Managers)**
```
┌─────────────────────────────────────────────────────────────────┐
│ Python Dependencies (requirements.txt)                          │
├──────────────────┬──────────┬───────────┬────────────┬─────────┤
│ Package          │ Current  │ Latest    │ Status     │ CVEs    │
├──────────────────┼──────────┼───────────┼────────────┼─────────┤
│ requests         │ 2.31.0   │ 2.31.0    │ ✅ Current │ 0       │
│ django           │ 4.2.0    │ 4.2.8     │ ⚠️ Update  │ 2 (Low) │
│ sqlalchemy       │ 1.4.50   │ 2.0.23    │ ⚠️ Major   │ 0       │
│ pillow           │ 9.5.0    │ 10.1.0    │ 🔴 Update  │ 3 (High)│
└──────────────────┴──────────┴───────────┴────────────┴─────────┘

┌─────────────────────────────────────────────────────────────────┐
│ JavaScript Dependencies (package.json)                          │
├──────────────────┬──────────┬───────────┬────────────┬─────────┤
│ react            │ 18.2.0   │ 18.2.0    │ ✅ Current │ 0       │
│ axios            │ 1.5.0    │ 1.6.2     │ ⚠️ Update  │ 0       │
│ lodash           │ 4.17.15  │ 4.17.21   │ 🔴 Security│ 5 (Crit)│
└──────────────────┴──────────┴───────────┴────────────┴─────────┘
```

**B. External Vendor Integrations (Third-Party Services)**
```
┌─────────────────────────────────────────────────────────────────┐
│ External Vendors & SaaS Integrations                            │
├──────────────────┬──────────┬───────────┬────────────┬─────────┤
│ Vendor           │ Purpose  │ Config    │ Status     │ Cost    │
├──────────────────┼──────────┼───────────┼────────────┼─────────┤
│ Stripe           │ Payments │ ✅ Prod   │ ✅ Active  │ $$$     │
│ Auth0            │ Auth     │ ✅ Prod   │ ✅ Active  │ $$      │
│ SendGrid         │ Email    │ ✅ Prod   │ ✅ Active  │ $       │
│ AWS S3           │ Storage  │ ✅ Prod   │ ✅ Active  │ $$$$    │
│ Twilio           │ SMS      │ ⚠️ Staging│ ⚠️ Inactive│ $       │
│ Sentry           │ Errors   │ ✅ Prod   │ ✅ Active  │ $$      │
│ Datadog          │ Monitor  │ ✅ Prod   │ ✅ Active  │ $$$     │
│ GitHub API       │ CI/CD    │ ✅ Prod   │ ✅ Active  │ Free    │
│ Google Maps API  │ Geocode  │ ⚠️ Test   │ ❌ Unused  │ N/A     │
└──────────────────┴──────────┴───────────┴────────────┴─────────┘
```

**C. Vendor Detection Methods (Current State Analysis)**
Detect external vendors by analyzing actual code:

1. **Environment Variables:**
   ```python
   # Scan for .env, .env.production, config files
   STRIPE_API_KEY=sk_live_...
   AUTH0_DOMAIN=myapp.auth0.com
   SENDGRID_API_KEY=SG.xxx
   AWS_ACCESS_KEY_ID=AKIA...
   ```

2. **Configuration Files:**
   ```yaml
   # config/production.yaml
   payment_provider: stripe
   email_service: sendgrid
   storage: aws_s3
   monitoring: datadog
   ```

3. **API Endpoint Patterns in Code:**
   ```python
   # Grep for common vendor domains
   requests.post("https://api.stripe.com/v1/charges")
   auth0_client.authorize("auth0.com")
   s3_client.upload_file("s3.amazonaws.com")
   ```

4. **SDK/Client Imports:**
   ```python
   from stripe import Stripe
   from auth0.v3.authentication import GetToken
   from sendgrid import SendGridAPIClient
   import boto3  # AWS SDK
   ```

**D. Vendor Tracking Schema**
```json
{
  "external_vendors": [
    {
      "name": "Stripe",
      "category": "payment",
      "detection_method": "env_var",
      "config_location": ".env:STRIPE_API_KEY",
      "status": "configured_active",
      "endpoints": ["api.stripe.com/v1"],
      "sdk": "stripe==7.0.0",
      "cost_tier": "high",
      "usage_locations": [
        "src/payments/stripe_gateway.py:45",
        "src/api/checkout.py:120"
      ]
    },
    {
      "name": "Google Maps API",
      "category": "geocoding",
      "detection_method": "config_file",
      "config_location": "config/services.yaml:google_maps_key",
      "status": "configured_unused",
      "endpoints": ["maps.googleapis.com/maps/api"],
      "sdk": null,
      "cost_tier": "none",
      "usage_locations": []
    }
  ]
}
```

**E. Vendor Status Legend:**
- ✅ **Active:** Configured with valid credentials, actively used in code
- ⚠️ **Inactive:** Configured but not used in current codebase
- ❌ **Unused:** Config exists but credentials missing or invalid
- 🔒 **Credentials Expired:** Config present but credentials need refresh

**F. Interactive Features:**
- Click vendor → Show all code locations using that service
- Filter by category (payments, auth, email, storage, monitoring)
- Export vendor inventory to CSV/JSON for audit
- Cost analysis: Show total monthly SaaS spend estimate
- Security audit: Highlight vendors with hardcoded credentials

**G. Dependency Graph Visualization**
```
Application Core
    │
    ├─ Payments Module
    │   ├─ stripe (v7.0.0)
    │   └─ Stripe API (External)
    │
    ├─ Authentication
    │   ├─ auth0-python (v4.7.0)
    │   └─ Auth0 Service (External)
    │
    ├─ Email Service
    │   ├─ sendgrid (v6.11.0)
    │   └─ SendGrid API (External)
    │
    └─ File Storage
        ├─ boto3 (v1.34.0)
        └─ AWS S3 (External)
```

**H. Risk Assessment:**
- **High Risk:** External vendors with no fallback (single point of failure)
- **Medium Risk:** Vendors with outdated SDKs (security vulnerabilities)
- **Low Risk:** Well-maintained integrations with fallback mechanisms

#### Data Requirements (Schema Extension):
```json
{
  "custom_metrics": {
    "dependencies_extended": {
      "code_dependencies": {
        "python": [...],
        "javascript": [...],
        "dotnet": [...]
      },
      "external_vendors": [
        {
          "name": "Stripe",
          "category": "payment",
          "status": "configured_active",
          "detection_method": "env_var",
          "cost_tier": "high",
          "usage_count": 8
        }
      ],
      "dependency_graph": {
        "nodes": [...],
        "edges": [...]
      }
    }
  }
}
```

#### Professional Presentation:
- Two-column layout: Code dependencies (left), External vendors (right)
- Color-coded status badges
- Sortable/filterable tables
- Dependency graph with D3.js force-directed layout
- Export to CSV/PDF for stakeholder reports
- Security alert highlighting (critical CVEs, expired credentials)

#### Compliance & Security:
- Track API key locations (flag hardcoded keys as 🔴 CRITICAL)
- Monitor vendor credential expiration dates
- Audit trail: When was vendor added? Who configured it?
- GDPR compliance: Flag vendors handling PII
- SOC 2 audit: Export vendor list with security posture

---

### Q6: ~~How will the dashboard be created for API projects?~~

**❌ REMOVED:** API Documentation view removed per architectural principle.

**Reason:** Dashboard must show **CURRENT STATE** only. API documentation (Swagger UI, live endpoint testing) represents desired/aspirational features that may not exist in the scanned application. 

**If Application Has APIs:**
- Show existing endpoint files in Tech Stack view
- Display route definitions in Code Organization view
- Show API framework versions (FastAPI, Express, etc.)
- All data must come from actual code analysis, not assumed capabilities

**What's Excluded:**
- ❌ Embedded Swagger UI (not current state)
- ❌ Live API testing (not observability)
- ❌ Interactive API explorer (not dashboard purpose)
- ❌ Runtime API health metrics (requires instrumentation not guaranteed to exist)

---

## 📊 Implementation Summary

### Schema Extensions Required

All advanced views require `custom_metrics` extensions:

```json
{
  "custom_metrics": {
    "tech_stack": { /* Technology inventory */ },
    "architecture": { /* Tiers, components, diagrams */ },
    "security_extended": { /* OWASP, compliance */ },
    "code_organization": { /* Heatmap, hotspots */ },
    "team_metrics": { /* Contributions, velocity */ },
    "dependencies_extended": { /* Code deps + external vendors */ }
  }
}
```

**Note:** `api_spec` removed - API documentation is not "current state" visualization.

### Implementation Phases

**Phase 13:** Tech Stack & Security Views (90 minutes)  
**Phase 14:** Architecture & Code Organization Views (90 minutes)  
**Phase 15:** Dependency Deep Dive (External Vendors) (60 minutes)  
**Phase 16:** Team Productivity & Visual Polish (60 minutes)

**Total Time:** 5 hours for all advanced views + external vendor tracking

---

## ✅ Benefits Summary

### For Engineers
- Instant understanding of tech stack and architecture
- Security vulnerabilities prioritized and tracked
- Code quality hotspots identified for refactoring
- Code organization and complexity visualized
- **Complete dependency tracking: packages + external vendors**
- **Vendor integration audit trail and security posture**

### For Managers
- High-level project health at a glance
- Risk assessment (security, technical debt)
- Team productivity and velocity tracking
- Technology choices transparent and justified
- **External vendor cost tracking and risk analysis**
- **SaaS spend visibility and optimization opportunities**

### For New Team Members
- Architecture diagrams for quick onboarding
- Tech stack inventory with versions
- Code organization clear and navigable
- Testing strategy and coverage visible

### For Stakeholders
- Professional, exportable reports
- Compliance status (OWASP, GDPR, etc.)
- Security posture communicated clearly
- Technology modernization roadmap
- **Vendor dependency audit for SOC 2 compliance**
- **Third-party risk assessment and cost transparency**

---

**Document Status:** ✅ FINALIZED  
**All Questions Answered:** YES  
**API Documentation View:** ❌ REMOVED (Current State Principle)  
**Dependency Deep Dive:** ✅ ENHANCED (External Vendor Tracking Added)  
**Total Views:** 9 core + 5 additional = 14 view types  
**Plan Updated:** dashboard-consolidation-plan.md (FEAT 4: Phases 13-16)  
**Specification:** dashboard-advanced-views-specification.md (28 KB)  
**Last Updated:** December 4, 2025 - FINAL

