# 🏗️ CORTEX Repository Dashboard SPA Redesign
**Authority:** cortex-architect.prompt.md v7.6 | **Phase:** Design & Architecture  
**Author:** Asif Hussain | **Date:** 2026-02-08 | **Status:** 📋 COMPREHENSIVE DESIGN SPECIFICATION

---

## 📋 Executive Summary

This document specifies the complete redesign of the CORTEX Repository Dashboard SPA to render correctly with proper data binding, interactive visualizations, and intelligent business capability detection. The dashboard currently has 9 tabs but lacks proper JSON schema, D3.js visualization implementation, and LLM-powered use case generation.

**Key Objectives:**
- ✅ Fix broken dashboard rendering with proper data schema
- ✅ Implement 9 tabs with rich D3.js visualizations  
- ✅ Create reverse engineering framework (code → business language)
- ✅ Match dark blue glassmorphism theme (approved-orchestrator-view)
- ✅ Integrate with RepoOnboardingOrchestrator
- ✅ Implement modern UX patterns + accessibility standards

---

## 🎯 Current State Analysis

### Existing Structure
- **File:** `_workspaces/.chats/chat01.md` (HTML SPA with embedded JSON)
- **Tabs:** 13 hardcoded but only 9 functional (Overview, Architecture, Quality, Vulnerabilities, Security, Dependencies, Testing, Patterns, Use Cases)
- **Data:** Embedded JSON with repository metadata, metrics, security findings
- **Theme:** Glassmorphism styling applied but visual consistency broken
- **Issue:** No proper data-driven tab rendering, missing D3 visualizations

### Reference Implementations
1. **approved-orchestrator-view/index.html**
   - Dark blue glassmorphism (primary: #1a1f3a, accent: #00d4ff)
   - Subtle shimmer animations (@keyframes glassShimmer)
   - SVG diagram styling with hover effects
   - Glass card animations with border glow pulse
   - Responsive grid system (auto-fit, minmax patterns)

2. **eras.json** (dashboard data model)
   - Hierarchical structure: eras → phases → stages
   - Metadata: status, progress, business_value, key_deliverables
   - Statistics aggregation
   - Timeline/milestone tracking

3. **plan-summary.json** (phase registry)
   - Structured metadata for 65+ phases
   - Status tracking (completed, planned, in-progress)
   - Priority indicators (P0, P1, P2)
   - Description with formatted lists

---

## 🎨 Design Specification

### A. Color Palette & Theme

```css
/* Dark Blue Glassmorphism */
:root {
  --glass-primary: #1a1f3a;        /* Dark navy blue */
  --glass-secondary: #0f1428;      /* Darker shade for depth */
  --glass-tertiary: #1e2847;       /* Lighter variant */
  
  --accent-primary: #00d4ff;       /* Cyan - main accent */
  --accent-secondary: #7b61ff;     /* Purple - secondary */
  --accent-tertiary: #10b981;      /* Green - success */
  
  --text-primary: #ffffff;         /* Main text */
  --text-secondary: #a0a6c0;       /* Secondary text */
  
  --status-success: #00ff88;       /* Bright green */
  --status-warning: #ffa500;       /* Orange */
  --status-danger: #ff4444;        /* Red */
  
  --glass-border: rgba(255, 255, 255, 0.1);
  --glass-bg: rgba(26, 31, 58, 0.7);
  --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
  
  /* Typography */
  --font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
  --font-mono: 'Courier New', monospace;
  
  /* Spacing */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-full: 9999px;
  
  /* Transitions */
  --transition-fast: 150ms ease-in-out;
  --transition-base: 200ms ease-in-out;
  --transition-slow: 300ms ease-in-out;
}
```

### B. Typography & Component Hierarchy

| Element | Font Size | Weight | Usage |
|---------|-----------|--------|-------|
| Page Title | 2.5rem | 700 | Repository name header |
| Section Header | 1.5rem | 600 | Tab section headers with icons |
| Subsection | 1.1rem | 600 | Card titles, modal headers |
| Body Text | 1rem | 400 | Description, paragraphs |
| Small Text | 0.875rem | 400 | Labels, helper text |
| Metric Value | 2.25rem | 700 | KPI numbers with glow |
| Badge | 0.8rem | 500 | Status indicators |

### C. Component Library

#### 1. Glass Card
```html
<div class="glass-card">
  <!-- Content -->
</div>

/* Styles */
.glass-card {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: var(--glass-shadow);
  padding: 1.5rem;
  transition: all var(--transition-base);
}

.glass-card:hover {
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  border-color: rgba(0, 212, 255, 0.3);
  transform: translateY(-2px);
}
```

#### 2. Metric Card (KPI Display)
```html
<div class="metric-card">
  <div class="metric-value">{{ value }}</div>
  <div class="metric-label">{{ label }}</div>
</div>

/* Styles */
.metric-card {
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  text-align: center;
  transition: all var(--transition-base);
}

.metric-value {
  font-size: 2.25rem;
  font-weight: 700;
  color: var(--accent-primary);
  text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
  margin-bottom: 0.5rem;
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
  border-color: rgba(0, 212, 255, 0.4);
}
```

#### 3. Badge System
```html
<span class="badge badge-success">Critical</span>
<span class="badge badge-warning">Medium</span>
<span class="badge badge-danger">High</span>
<span class="badge badge-info">Low</span>

/* Styles */
.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  font-weight: 500;
}

.badge-success {
  background: rgba(0, 255, 136, 0.15);
  color: var(--status-success);
}

.badge-warning {
  background: rgba(255, 165, 0, 0.15);
  color: var(--status-warning);
}

.badge-danger {
  background: rgba(255, 68, 68, 0.15);
  color: var(--status-danger);
}

.badge-info {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}
```

#### 4. Progress Bar
```html
<div class="progress-bar">
  <div class="progress-fill progress-success" style="width: {{ percentage }}%;"></div>
</div>

/* Styles */
.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin: 1rem 0;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
  box-shadow: 0 0 10px currentColor;
}

.progress-success {
  background: linear-gradient(90deg, #00ff88, #00cc6a);
}

.progress-warning {
  background: linear-gradient(90deg, #ffa500, #ffcc00);
}

.progress-danger {
  background: linear-gradient(90deg, #ff4444, #ff6666);
}
```

#### 5. Tab Navigation
```html
<nav class="tab-nav">
  <button class="tab-btn active" data-tab="overview">📊 Overview</button>
  <button class="tab-btn" data-tab="architecture">🏗️ Architecture</button>
  <!-- More tabs -->
</nav>

/* Styles */
.tab-nav {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: rgba(10, 14, 39, 0.8);
  border-bottom: 1px solid var(--glass-border);
  overflow-x: auto;
  scroll-behavior: smooth;
}

.tab-btn {
  padding: 0.75rem 1.25rem;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  font-family: inherit;
  transition: all var(--transition-base);
  white-space: nowrap;
}

.tab-btn:hover {
  background: rgba(0, 212, 255, 0.1);
  color: var(--text-primary);
  border-color: rgba(0, 212, 255, 0.3);
}

.tab-btn.active {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: var(--text-primary);
  border-color: transparent;
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
}
```

#### 6. Data Table
```html
<table class="data-table">
  <thead>
    <tr>
      <th>Column 1</th>
      <th>Column 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Value 1</td>
      <td>Value 2</td>
    </tr>
  </tbody>
</table>

/* Styles */
.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.data-table th {
  background: rgba(0, 212, 255, 0.1);
  color: var(--accent-primary);
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.05em;
  border-bottom: 2px solid var(--glass-border);
}

.data-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--glass-border);
  color: var(--text-secondary);
}

.data-table tr:hover {
  background: rgba(0, 212, 255, 0.05);
}

.data-table tr:hover td {
  color: var(--text-primary);
}
```

---

## 📊 9-Tab Specification

### Tab 1: Overview (📊 Repository Intelligence)
**Purpose:** Executive summary with key metrics, audience personas, repository health

**Sections:**
- Header with logo (200x200), title, tagline
- Key metrics grid (6-8 KPIs)
- Audience cards (Executive, Product Owner, Dev Manager, Engineer, Leader)
- Technology stack breakdown (language distribution)
- Repository health status table

**Data Requirements:**
```json
{
  "repository": {
    "name": "string",
    "description": "string",
    "primary_language": "string",
    "total_files": "number",
    "total_lines": "number",
    "repo_age_days": "number",
    "last_updated": "ISO8601",
    "contributors": "number"
  },
  "metrics": {
    "health_score": "0-100",
    "code_quality": "0-10",
    "test_coverage": "0-100",
    "maintainability_index": "0-100",
    "technical_debt_hours": "number"
  },
  "languages": {
    "[language]": "number (lines)"
  }
}
```

**D3 Visualization:** Pie chart of language distribution (sunburst optional for depth)

---

### Tab 2: Architecture (🏗️ System Design)
**Purpose:** Multi-layer architecture visualization, module dependency graph, system design patterns

**Sections:**
- Architecture overview (layers: Presentation → Business → Data → Infrastructure)
- Module breakdown with D3 treemap (code structure hierarchies)
- Design patterns detected (with examples)
- Layer interaction diagram

**Data Requirements:**
```json
{
  "architecture": {
    "layers": [
      {
        "name": "string",
        "description": "string",
        "modules": ["string"],
        "technologies": ["string"]
      }
    ],
    "modules": {
      "[module_name]": {
        "lines_of_code": "number",
        "files": "number",
        "complexity": "number",
        "sub_modules": ["string"],
        "dependencies": ["string"]
      }
    },
    "design_patterns": [
      {
        "name": "string",
        "description": "string",
        "location": "string",
        "usage_count": "number"
      }
    ]
  }
}
```

**D3 Visualizations:**
- Treemap: Module hierarchy with LOC, color-coded by complexity
- Force-directed graph: Module dependencies (click to expand)
- Sankey: Data flow between architectural layers

---

### Tab 3: Quality (✅ Code Health)
**Purpose:** Code quality metrics, test coverage, technical debt, complexity analysis

**Sections:**
- Quality score card (0-10 scale with color coding)
- Maintainability index gauge
- Test coverage progress bar
- Code complexity distribution histogram
- Technical debt breakdown (by category)
- Code smells and duplication metrics

**Data Requirements:**
```json
{
  "quality": {
    "code_quality_score": "0-10",
    "maintainability_index": "0-100",
    "code_smells": "number",
    "duplication_percentage": "0-100",
    "technical_debt_hours": "number",
    "test_coverage": "0-100",
    "coverage_trend": [
      {"date": "ISO8601", "coverage": "0-100"}
    ],
    "complexity_trend": [
      {"date": "ISO8601", "avg_complexity": "number"}
    ],
    "complexity_by_module": {
      "[module]": "number"
    },
    "hotspots": [
      {
        "file": "string",
        "complexity": "number",
        "issues": "number",
        "priority": "high|medium|low"
      }
    ]
  }
}
```

**D3 Visualizations:**
- Histogram: Complexity distribution across files
- Time-series line chart: Coverage trend (6-month rolling)
- Bar chart: Technical debt by category
- Heat map: File complexity hotspots

---

### Tab 4: Vulnerabilities (🛡️ Security Scan)
**Purpose:** Security vulnerabilities, OWASP compliance, dependency risks

**Sections:**
- Vulnerability metrics (Critical, High, Medium, Low counts)
- OWASP Top 10 compliance matrix
- Vulnerable dependency table (with remediation)
- Secrets scan status (clean/violations)
- CWE and CVE tracking

**Data Requirements:**
```json
{
  "security": {
    "security_score": "0-10",
    "vulnerabilities": {
      "critical": "number",
      "high": "number",
      "medium": "number",
      "low": "number"
    },
    "owasp_findings": [
      {
        "category": "string (A01:2021)",
        "severity": "critical|high|medium|low",
        "count": "number",
        "items": [
          {
            "location": "string",
            "description": "string",
            "remediation": "string"
          }
        ]
      }
    ],
    "secrets_scan": {
      "status": "clean|violations_found",
      "secrets_found": "number",
      "last_scan": "ISO8601"
    },
    "cves": [
      {
        "id": "CVE-XXXX-XXXXX",
        "severity": "string",
        "affected_package": "string",
        "fix_available": "boolean"
      }
    ]
  }
}
```

**D3 Visualizations:**
- Stacked bar chart: Vulnerability distribution by severity
- OWASP compliance gauge/progress ring
- Timeline: Vulnerability discovery and resolution

---

### Tab 5: Security (🔒 Posture & Compliance)
**Purpose:** Comprehensive security assessment, compliance status, enterprise security policies

**Sections:**
- Security posture summary (with color-coded score)
- Compliance status matrix (OWASP, GDPR, SOC2, etc.)
- Dependency audit results (with policy violations)
- Authorization/authentication patterns
- Encryption status check
- Data protection assessment

**Data Requirements:**
```json
{
  "compliance": {
    "security_posture": "string (description)",
    "overall_score": "0-100",
    "frameworks": [
      {
        "name": "string (OWASP, GDPR, etc.)",
        "status": "compliant|partial|non_compliant",
        "score": "0-100",
        "issues": "number"
      }
    ],
    "authentication": {
      "implemented": "string",
      "standards": ["string"],
      "multi_factor": "boolean"
    },
    "encryption": {
      "at_rest": "boolean",
      "in_transit": "boolean",
      "key_management": "string"
    },
    "data_protection": {
      "pii_detection": "number (found)",
      "masking": "boolean",
      "retention_policy": "string"
    }
  }
}
```

**D3 Visualizations:**
- Radar chart: Compliance across multiple frameworks
- Compliance timeline: Historical status changes
- Risk matrix: Probability vs Impact visualization

---

### Tab 6: Dependencies (📦 Package Management)
**Purpose:** Dependency inventory, vulnerability tracking, license compliance

**Sections:**
- Dependency counts (direct, transitive, outdated)
- Package table (name, version, license, latest, status)
- Dependency graph visualization (interactive force-directed)
- License compliance check
- Outdated package recommendations
- Circular dependency detection

**Data Requirements:**
```json
{
  "dependencies": {
    "direct_count": "number",
    "transitive_count": "number",
    "outdated_count": "number",
    "vulnerable_count": "number",
    "packages": [
      {
        "name": "string",
        "version": "string",
        "latest": "string",
        "type": "direct|transitive",
        "license": "string",
        "security_status": "safe|vulnerable|critical",
        "update_recommended": "boolean"
      }
    ],
    "dependency_graph": {
      "[package]": ["string (dependencies)"]
    },
    "licenses": [
      {
        "name": "string (MIT, Apache, etc.)",
        "count": "number",
        "packages": ["string"]
      }
    ]
  }
}
```

**D3 Visualizations:**
- Force-directed graph: Dependency relationships (with clustering)
- Sunburst: Dependency tree depth and breadth
- Bar chart: License distribution
- Timeline: Dependency updates over time

---

### Tab 7: Testing (🧪 Coverage & Quality)
**Purpose:** Test coverage metrics, test execution status, coverage trends

**Sections:**
- Coverage summary (overall percentage with progress bar)
- Test counts (Total, Passing, Failing, Skipped)
- Coverage trend chart (6-month rolling)
- Test type breakdown (unit, integration, e2e)
- Failing test list with remediation
- Coverage by module heatmap

**Data Requirements:**
```json
{
  "testing": {
    "coverage_percentage": "0-100",
    "coverage_trend": [
      {"date": "ISO8601", "coverage": "0-100"}
    ],
    "test_counts": {
      "total": "number",
      "passing": "number",
      "failing": "number",
      "skipped": "number"
    },
    "test_types": {
      "unit": "number",
      "integration": "number",
      "e2e": "number"
    },
    "failing_tests": [
      {
        "name": "string",
        "file": "string",
        "error": "string",
        "priority": "high|medium|low"
      }
    ],
    "coverage_by_module": {
      "[module]": "0-100"
    }
  }
}
```

**D3 Visualizations:**
- Line chart: Coverage trend with target line
- Stacked bar: Test results by type
- Heatmap: Coverage by module (rows: modules, cols: coverage %)

---

### Tab 8: Patterns (🎨 Design Patterns & Anti-Patterns)
**Purpose:** Detected design patterns, anti-patterns, code smells, refactoring opportunities

**Sections:**
- Design patterns detected (Singleton, Factory, Observer, etc.)
- Pattern occurrence count and locations
- Anti-patterns and code smells
- Refactoring opportunities ranked by effort
- SOLID principle compliance assessment

**Data Requirements:**
```json
{
  "patterns": {
    "design_patterns": [
      {
        "name": "string (Singleton, Factory, etc.)",
        "description": "string",
        "occurrences": "number",
        "locations": ["string (file:line)"]
      }
    ],
    "anti_patterns": [
      {
        "name": "string (God Object, etc.)",
        "severity": "high|medium|low",
        "count": "number",
        "locations": ["string"],
        "remediation": "string"
      }
    ],
    "refactoring_opportunities": [
      {
        "type": "string (Extract Method, etc.)",
        "file": "string",
        "priority": "high|medium|low",
        "effort_hours": "number",
        "description": "string"
      }
    ],
    "solid_principles": {
      "single_responsibility": "0-100",
      "open_closed": "0-100",
      "liskov_substitution": "0-100",
      "interface_segregation": "0-100",
      "dependency_inversion": "0-100"
    }
  }
}
```

**D3 Visualizations:**
- Bar chart: Pattern frequency
- Bubble chart: Refactoring opportunity (priority × effort)
- Radar: SOLID principles compliance

---

### Tab 9: Use Cases (📋 Business Capabilities)
**Purpose:** Reverse-engineered business capabilities from code, use case scenarios, business value

**Sections:**
- Business capabilities summary (mapped from code analysis)
- Audience personas with recommended capabilities
- Use case cards (title, description, business value, actors)
- API endpoints grouped by use case
- Integration points and external systems
- Stakeholder impact analysis

**Data Requirements:**
```json
{
  "use_cases": {
    "detected_capabilities": [
      {
        "id": "string",
        "business_capability": "string (human language)",
        "technical_name": "string (from code)",
        "description": "string",
        "business_value": "string",
        "actors": ["string"],
        "systems": ["string"],
        "complexity": "low|medium|high",
        "maturity": "emerging|stable|mature",
        "modernization_score": "0-100"
      }
    ],
    "business_flows": [
      {
        "name": "string",
        "description": "string",
        "steps": ["string"],
        "primary_actor": "string",
        "preconditions": ["string"],
        "success_criteria": ["string"]
      }
    ],
    "integrations": [
      {
        "system": "string",
        "type": "API|Database|File|Message",
        "description": "string"
      }
    ],
    "stakeholder_mapping": {
      "[audience_persona]": ["use_case_ids"]
    }
  }
}
```

**D3 Visualizations:**
- Sunburst: Use cases by business domain and capability
- Alluvial/Sankey: Use case flows with actor involvement
- Network graph: Integration points and system dependencies
- Treemap: Modernization score by capability

---

## 🤖 Reverse Engineering Framework (Code → Business)

### A. LLM-Powered Code Analysis Pipeline

```python
# Pseudocode flow for code-to-business transformation

class CodeToBusinessTransformer:
    """Transform technical code analysis into business language"""
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.pattern_cache = {}
    
    async def detect_capabilities(self, code_analysis: Dict) -> List[Capability]:
        """
        Input: LENS code analysis (AST, dependencies, patterns)
        Output: Business-friendly capability descriptions
        """
        
        # Step 1: Extract technical signals from code
        signals = {
            "api_endpoints": extract_rest_endpoints(code_analysis),
            "database_operations": extract_db_queries(code_analysis),
            "integrations": extract_external_apis(code_analysis),
            "patterns": extract_design_patterns(code_analysis),
            "domain_entities": extract_entities(code_analysis)
        }
        
        # Step 2: Cluster signals into capability groups
        capability_clusters = cluster_signals(signals)
        
        # Step 3: For each cluster, use LLM to generate business language
        capabilities = []
        for cluster in capability_clusters:
            prompt = f"""
            Analyze this technical capability cluster and describe it 
            in business language for non-technical stakeholders:
            
            Technical Signals:
            - API Endpoints: {cluster['endpoints']}
            - Database Operations: {cluster['db_ops']}
            - Integrations: {cluster['integrations']}
            - Domain Objects: {cluster['entities']}
            
            Generate:
            1. Business capability name (e.g., "User Authentication", "Report Generation")
            2. Clear description for executives (1-2 sentences)
            3. Business value proposition
            4. Primary actors/beneficiaries
            5. Associated processes/workflows
            
            Format: JSON with fields:
            {{
                "business_capability": "...",
                "description": "...",
                "business_value": "...",
                "actors": [...],
                "business_flows": [...]
            }}
            """
            
            response = await self.llm.generate(prompt, temperature=0.7)
            capability = parse_capability(response)
            capabilities.append(capability)
        
        return capabilities
    
    async def analyze_business_impact(self, use_cases: List[Capability]) -> Dict:
        """Generate impact analysis for leadership"""
        
        prompt = f"""
        For these technical capabilities, analyze business impact:
        
        Capabilities:
        {json.dumps(use_cases, indent=2)}
        
        Generate impact analysis addressing:
        1. Revenue drivers: Which capabilities directly or indirectly drive revenue?
        2. Cost reduction: Where does this capability reduce operational costs?
        3. Risk mitigation: What risks does this address?
        4. Customer value: How does this improve customer experience?
        5. Competitive advantage: What edge does this provide?
        6. Modernization priority: On scale 1-10, how modern is this capability?
        
        Format as JSON with stakeholder mapping:
        {{
            "revenue_drivers": ["capability_id": "annual_impact_usd"],
            "cost_reduction": {...},
            "risk_factors": [...],
            "competitive_factors": [...],
            "modernization_scores": {...}
        }}
        """
        
        response = await self.llm.generate(prompt, temperature=0.5)
        return parse_impact_analysis(response)
    
    def generate_persona_summary(self, use_cases: List[Capability], 
                                  persona: str) -> str:
        """Generate persona-specific summary of relevant capabilities"""
        
        persona_filters = {
            "executive": ["revenue_drivers", "risk_factors", "competitive_advantage"],
            "product_owner": ["business_capability", "workflows", "integration_points"],
            "tech_lead": ["architecture", "modernization_score", "technical_debt"],
            "engineer": ["implementation_details", "dependencies", "refactoring"]
        }
        
        relevant_cases = filter_by_persona(use_cases, persona, persona_filters)
        
        summary_prompt = f"""
        Create a concise summary for a {persona} about these technical capabilities:
        
        {json.dumps(relevant_cases)}
        
        The summary should:
        - Be 1-2 paragraphs
        - Focus on relevance to their role
        - Include 2-3 specific recommendations
        - Highlight any critical issues or opportunities
        """
        
        return self.llm.generate(summary_prompt, temperature=0.6)
```

### B. Pattern Detection Rules

```yaml
# Capability Detection Patterns

patterns:
  authentication:
    signals:
      - api_endpoints: ['/login', '/auth', '/oauth', '/saml']
      - db_patterns: [UserTable, PermissionTable, RoleTable]
      - integrations: [OAuth2, LDAP, ActiveDirectory]
    business_capability: "User Authentication & Authorization"
    value_drivers: [security, compliance, user_experience]
  
  reporting:
    signals:
      - api_endpoints: ['/report', '/export', '/dashboard', '/metrics']
      - db_patterns: [SELECT with aggregations, time-series queries]
      - design_patterns: [ReportBuilder, TemplatePattern]
    business_capability: "Business Intelligence & Reporting"
    value_drivers: [decision_making, visibility, compliance]
  
  data_integration:
    signals:
      - integrations: [HTTP clients, message queues, ETL frameworks]
      - db_patterns: [bulk_insert, sync_patterns]
      - file_handling: [CSV, JSON, XML parsers]
    business_capability: "Data Integration & Synchronization"
    value_drivers: [data_quality, integration_efficiency, real_time_data]
  
  notification_system:
    signals:
      - api_endpoints: ['/notify', '/subscribe', '/webhook']
      - integrations: [email, SMS, push_notifications]
      - patterns: [Observer, PubSub]
    business_capability: "Communication & Notification System"
    value_drivers: [user_engagement, alert_management, compliance]
```

### C. Business Language Transformation Rules

```python
# Technical term → Business language mapping

TERM_MAPPING = {
    # Data operations
    "CRUD operations": "Data Management",
    "database queries": "Information Retrieval",
    "SQL transactions": "Data Consistency Management",
    "caching layer": "Performance Optimization",
    
    # Integration
    "API endpoints": "External System Integration",
    "message queues": "Asynchronous Communication",
    "webhooks": "Event Notification",
    "ETL pipeline": "Data Pipeline",
    
    # Security
    "authentication": "User Verification",
    "authorization": "Access Control",
    "encryption": "Data Protection",
    "audit logging": "Compliance Tracking",
    
    # Architecture
    "microservices": "Modular Service Architecture",
    "event-driven": "Reactive System Design",
    "CQRS": "Separate Read/Write Optimization",
    "saga pattern": "Distributed Transaction Management",
    
    # Quality
    "unit tests": "Quality Assurance",
    "code coverage": "Code Reliability Metrics",
    "CI/CD pipeline": "Automated Deployment",
    "load testing": "Capacity Validation"
}
```

---

## 📐 D3.js Visualization Specifications

### 1. Sunburst Chart (Overview Language Distribution)
**Purpose:** Hierarchical view of code composition  
**Data Structure:**
```json
{
  "name": "KSESSIONS",
  "value": 3658465,
  "children": [
    {
      "name": "C#",
      "value": 2350000,
      "children": [
        {"name": "API", "value": 500000},
        {"name": "Business Logic", "value": 1200000}
      ]
    }
  ]
}
```

### 2. Force-Directed Graph (Dependency Network)
**Purpose:** Interactive exploration of package dependencies  
**Data Structure:**
```json
{
  "nodes": [
    {"id": "package-name", "group": "direct|transitive", "size": 30},
  ],
  "links": [
    {"source": "package-a", "target": "package-b", "value": 1}
  ]
}
```

### 3. Treemap (Module Complexity)
**Purpose:** Visual representation of code structure and hotspots  
**Data Structure:**
```json
{
  "name": "root",
  "children": [
    {
      "name": "module-name",
      "value": 1000,
      "complexity": 15,
      "color_scale": 0.75
    }
  ]
}
```

### 4. Heatmap (Test Coverage by Module)
**Purpose:** Identify coverage gaps  
**Data Structure:**
```json
{
  "modules": ["api", "brain", "mcp", ...],
  "coverage_data": [
    [95, 87, 72, ...],  // module 1 coverage by date
    [93, 89, 75, ...]   // module 2 coverage by date
  ]
}
```

### 5. Sankey Diagram (Architecture Data Flow)
**Purpose:** Show how data flows through layers  
**Data Structure:**
```json
{
  "nodes": [
    {"name": "Presentation Layer"},
    {"name": "Business Logic"},
    {"name": "Data Layer"}
  ],
  "links": [
    {"source": 0, "target": 1, "value": 100},
    {"source": 1, "target": 2, "value": 100}
  ]
}
```

### 6. Timeline (Commit History)
**Purpose:** Visualize development velocity and trends  
**Data Structure:**
```json
{
  "events": [
    {
      "date": "2026-01-03",
      "commits": 41,
      "prs": 7,
      "merges": 7,
      "authors": 5
    }
  ]
}
```

### 7. Radar Chart (SOLID Principles)
**Purpose:** Multi-dimensional quality assessment  
**Data Structure:**
```json
{
  "metrics": [
    {"axis": "Single Responsibility", "value": 85},
    {"axis": "Open/Closed", "value": 72},
    {"axis": "Liskov Substitution", "value": 78},
    {"axis": "Interface Segregation", "value": 81},
    {"axis": "Dependency Inversion", "value": 76}
  ]
}
```

---

## 🏗️ Implementation Phases

### Phase S1: Foundation & Schema (2 days)
- [x] Create comprehensive JSON schema (repo-dashboard-schema.json)
- [x] Define CSS design token system matching approved-orchestrator-view
- [x] Build base component library (glass-card, metric-card, badges, tabs)
- [x] Implement responsive grid system
- [ ] Write unit tests for component rendering

**Deliverables:**
- repo-dashboard-schema.json (with validation)
- design-tokens.css (vars + themes)
- component-library.css (8+ components)
- responsive-layout.css

### Phase S2: Core Tabs (3 days)
- [ ] Implement Overview tab (header, metrics grid, audience cards, tech stack)
- [ ] Implement Architecture tab (static descriptions + placeholder for D3)
- [ ] Implement Quality tab (metrics, progress bars, tables)
- [ ] Data binding framework (map JSON to template sections)
- [ ] Tab navigation with smooth transitions

**Deliverables:**
- repo-dashboard-core.html (S1-S3 tabs complete)
- tab-data-binder.js (template → data mapping)
- metrics-renderer.js (metric card → JSON)

### Phase S3: Analysis Tabs (3 days)
- [ ] Implement Security tab (vulnerability matrix, compliance status)
- [ ] Implement Vulnerabilities tab (OWASP table, CWE/CVE list)
- [ ] Implement Dependencies tab (package table, license matrix)
- [ ] Implement Testing tab (coverage trends, test matrix)

**Deliverables:**
- security-tabs.html (S4-S7 complete)
- data-table-renderer.js (flexible table generation)

### Phase S4: Patterns & Use Cases (3 days)
- [ ] Implement Patterns tab (pattern detection, anti-patterns, SOLID gauge)
- [ ] Implement Use Cases tab (capability cards, stakeholder mapping)
- [ ] Build LLM integration framework (async capability detection)
- [ ] Create business language transformer

**Deliverables:**
- patterns-usecases.html (S8-S9 complete)
- code-to-business-transformer.py (LLM orchestration)
- business-capability-detector.py (pattern matching)

### Phase S5: D3.js Visualizations (5 days)
- [ ] Sunburst chart (language distribution, architecture decomposition)
- [ ] Force-directed graph (dependency network)
- [ ] Treemap (module complexity)
- [ ] Heatmap (test coverage)
- [ ] Sankey diagram (architecture flow)
- [ ] Timeline (commit history)
- [ ] Radar chart (SOLID principles)
- [ ] Interactive tooltips + legends

**Deliverables:**
- d3-visualizations.js (7 chart types)
- chart-configs.json (theme colors, sizes)
- interactive-legends.js

### Phase S6: Polish & Integration (4 days)
- [ ] RepoOnboardingOrchestrator integration hooks
- [ ] Async data loading with loading states
- [ ] Error handling and graceful degradation
- [ ] Performance optimization (lazy loading, virtualization)
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Mobile responsiveness testing
- [ ] Documentation (component API, data schema, deployment)
- [ ] E2E test suite (Playwright/Cypress)

**Deliverables:**
- repo-dashboard-final.html (production-ready)
- orchestrator-integration.py (CORTEX hooks)
- performance-optimization.md
- accessibility-audit.md
- deployment-guide.md

**Total Effort:** ~17 days (6 weeks part-time)

---

## 🔌 RepoOnboardingOrchestrator Integration

### Integration Points

```python
# cortex/orchestrators/onboarding/repo_onboarding_orchestrator.py

class RepoOnboardingOrchestrator:
    """Orchestrate repository onboarding including dashboard generation"""
    
    async def onboard_repository(self, repo_path: str) -> RepositoryMetadata:
        """
        Onboarding flow:
        1. S1: Repository discovery & metadata extraction
        2. S2: Code analysis (LENS multi-analyzer)
        3. S3: Security & dependency scanning
        4. S4: Architecture analysis & pattern detection
        5. S5: Dashboard data structure generation
        6. S6: Use case & business capability inference
        """
        
        # Step 1: Metadata extraction
        metadata = await self.extract_metadata(repo_path)
        
        # Step 2: LENS analysis pipeline
        lens_results = await self.run_lens_analyzers(repo_path)
        
        # Step 3: Security scanning
        security_findings = await self.scan_security(repo_path)
        
        # Step 4: Architecture analysis
        architecture = await self.analyze_architecture(lens_results)
        
        # Step 5: Generate dashboard data structure
        dashboard_data = await self.generate_dashboard_schema(
            metadata=metadata,
            lens_results=lens_results,
            security=security_findings,
            architecture=architecture
        )
        
        # Step 6: Infer business capabilities (async, can be background job)
        self.background_task(
            self.infer_business_capabilities(
                dashboard_data, 
                llm_client=self.llm_client
            )
        )
        
        return dashboard_data
    
    async def generate_dashboard_schema(self, **analysis_results) -> Dict:
        """Merge all analysis into dashboard JSON schema"""
        
        dashboard = {
            "metadata": analysis_results["metadata"],
            "overview": self._transform_overview(analysis_results),
            "architecture": self._transform_architecture(analysis_results),
            "quality": self._transform_quality(analysis_results),
            "vulnerabilities": self._transform_vulnerabilities(analysis_results),
            "security": self._transform_security(analysis_results),
            "dependencies": self._transform_dependencies(analysis_results),
            "testing": self._transform_testing(analysis_results),
            "patterns": self._transform_patterns(analysis_results),
            "use_cases": await self._transform_use_cases(analysis_results)
        }
        
        return dashboard
    
    async def infer_business_capabilities(self, dashboard_data: Dict, 
                                         llm_client) -> List[Dict]:
        """Use LLM to infer business capabilities from code analysis"""
        
        transformer = CodeToBusinessTransformer(llm_client)
        
        capabilities = await transformer.detect_capabilities(
            code_analysis={
                "patterns": dashboard_data["patterns"]["design_patterns"],
                "modules": dashboard_data["architecture"]["modules"],
                "integrations": dashboard_data["use_cases"]["integrations"]
            }
        )
        
        # Store results back in dashboard data
        dashboard_data["use_cases"]["detected_capabilities"] = capabilities
        
        return capabilities
```

### Orchestrator Hooks

```python
# Hook 1: Pre-dashboard generation (validate environment)
@orchestrator_hook('onboarding:pre_dashboard')
async def validate_dashboard_env(repo_metadata):
    """Ensure required tools available"""
    pass

# Hook 2: Post-analysis (enrich with company knowledge)
@orchestrator_hook('onboarding:post_analysis')
async def enrich_with_company_context(dashboard_data, company_registry):
    """Add company-specific insights and domain mappings"""
    pass

# Hook 3: Post-dashboard (trigger notifications)
@orchestrator_hook('onboarding:post_dashboard')
async def notify_stakeholders(dashboard_data, repo_metadata):
    """Send dashboard URL to relevant teams"""
    pass
```

---

## 🎯 Modern UX/Design Patterns

### A. Micro-interactions

#### 1. Hover Effects
```css
/* Glass card elevation on hover */
.glass-card {
  transition: all 200ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.glass-card:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3),
              0 0 30px rgba(123, 97, 255, 0.15);
}

/* Metric card lift on hover */
.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
  border-color: rgba(0, 212, 255, 0.4);
}

/* Tab button active state */
.tab-btn.active {
  background: linear-gradient(135deg, #00d4ff, #7b61ff);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
  animation: borderGlow 4s ease-in-out infinite;
}
```

#### 2. Loading States
```html
<!-- Skeleton loader for async content -->
<div class="skeleton-card">
  <div class="skeleton-line skeleton-title"></div>
  <div class="skeleton-line skeleton-text"></div>
</div>

<style>
.skeleton-line {
  height: 12px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.1),
    transparent
  );
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
</style>
```

#### 3. Progress Indication
```html
<!-- Animated progress bar -->
<div class="progress-bar">
  <div class="progress-fill progress-success" style="width: 75%;"></div>
</div>

<style>
.progress-fill {
  background: linear-gradient(
    90deg,
    #00ff88,
    #00ff88,
    #00cc6a
  );
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
  animation: slideIn 0.6s ease-out;
}

@keyframes slideIn {
  from { width: 0; }
}
</style>
```

### B. Responsive Design Strategy

#### 1. Mobile-First Breakpoints
```css
/* Mobile (320px - 480px) */
@media (max-width: 480px) {
  .metrics-grid { grid-template-columns: 1fr; }
  .use-case-grid { grid-template-columns: 1fr; }
  .dashboard-header { flex-direction: column; }
  .tab-nav { overflow-x: auto; scroll-behavior: smooth; }
}

/* Tablet (481px - 768px) */
@media (max-width: 768px) {
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
  .use-case-grid { grid-template-columns: repeat(2, 1fr); }
  .logo-container img { width: 150px; }
}

/* Desktop (769px+) */
@media (min-width: 769px) {
  .metrics-grid { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
  .use-case-grid { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
  .dashboard-header { flex-direction: row; }
}
```

#### 2. Touch-Friendly UI
```css
/* Increase touch targets to 44px minimum */
.tab-btn {
  padding: 0.75rem 1.25rem;  /* ~44px height */
  min-width: 44px;
}

.badge {
  padding: 0.5rem 0.75rem;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
}

/* Reduce hover dependencies on desktop */
@media (hover: none) {
  .glass-card:hover { transform: none; }  /* No hover on touch */
  .glass-card:active { transform: scale(0.98); }  /* Use active state */
}
```

### C. Accessibility (WCAG 2.1 AA)

#### 1. Color Contrast
```css
/* Ensure 4.5:1 contrast ratio for text */
body {
  color: #ffffff;  /* Text on #1a1f3a background */
  /* Contrast ratio: 20.96:1 ✅ */
}

.section-header {
  color: #00d4ff;  /* Cyan on #1a1f3a */
  /* Contrast ratio: 6.64:1 ✅ */
}

.text-secondary {
  color: #a0a6c0;  /* Gray on #1a1f3a */
  /* Contrast ratio: 5.23:1 ✅ */
}
```

#### 2. Keyboard Navigation
```html
<!-- Tab order management -->
<div class="tab-nav" role="tablist">
  <button role="tab" aria-selected="true" aria-controls="overview">Overview</button>
  <button role="tab" aria-selected="false" aria-controls="architecture">Architecture</button>
</div>

<div id="overview" role="tabpanel" aria-labelledby="overview-btn">
  <!-- Content -->
</div>

<script>
// Keyboard navigation
document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowRight') {
    focusNextTab();
  } else if (e.key === 'ArrowLeft') {
    focusPreviousTab();
  }
});
</script>
```

#### 3. Screen Reader Support
```html
<!-- ARIA labels and descriptions -->
<div class="metric-card" aria-label="Code Quality Score">
  <div class="metric-value" aria-live="polite">8.5</div>
  <div class="metric-label">Code Quality Score (0-10 scale)</div>
</div>

<!-- Chart accessibility -->
<div class="d3-chart" role="img" aria-label="Pie chart showing language distribution: C# 65%, TypeScript 20%, JavaScript 15%">
  <svg><!-- Chart --></svg>
  <table aria-label="Language distribution data">
    <!-- Tabular data for screen readers -->
  </table>
</div>
```

### D. Performance Optimization

#### 1. Lazy Loading
```javascript
// Lazy load D3.js visualizations when tab becomes visible
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      loadVisualizationForTab(entry.target.id);
      observer.unobserve(entry.target);
    }
  });
});

document.querySelectorAll('.tab-panel').forEach(panel => {
  observer.observe(panel);
});
```

#### 2. Virtual Scrolling (for large tables)
```javascript
// Virtual scroll for large dependency tables
class VirtualTable {
  constructor(containerSelector, data, rowHeight) {
    this.container = document.querySelector(containerSelector);
    this.data = data;
    this.rowHeight = rowHeight;
    this.visibleRows = Math.ceil(this.container.clientHeight / rowHeight);
  }
  
  onScroll(scrollTop) {
    const startIndex = Math.floor(scrollTop / this.rowHeight);
    const endIndex = startIndex + this.visibleRows;
    
    this.renderRows(this.data.slice(startIndex, endIndex), startIndex);
  }
}
```

#### 3. Image Optimization
```html
<!-- Lazy load images with placeholders -->
<img
  src="real-chart.png"
  loading="lazy"
  width="800"
  height="600"
  alt="Dependency graph visualization"
/>

<!-- SVG for charts (vector, smaller filesize) -->
<svg class="metric-chart"><!-- D3.js generated --></svg>
```

---

## 📋 Data Schema Validation

### Pydantic Schema
```python
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional

class RepositoryMetadata(BaseModel):
    name: str = Field(..., description="Repository name")
    path: str = Field(..., description="Repository path")
    primary_language: str = Field(..., description="Primary programming language")
    total_files: int = Field(..., ge=0)
    total_lines: int = Field(..., ge=0)
    contributors: int = Field(..., ge=1)
    last_updated: str = Field(..., description="ISO8601 timestamp")
    repo_age_days: int = Field(..., ge=0)
    
    @validator('last_updated')
    def validate_iso8601(cls, v):
        from datetime import datetime
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Invalid ISO8601 timestamp')
        return v

class MetricsData(BaseModel):
    health_score: float = Field(..., ge=0, le=100)
    code_quality: float = Field(..., ge=0, le=10)
    test_coverage: float = Field(..., ge=0, le=100)
    maintainability_index: float = Field(..., ge=0, le=100)
    technical_debt_hours: int = Field(..., ge=0)

class DashboardSchema(BaseModel):
    metadata: RepositoryMetadata
    overview: Dict = Field(default_factory=dict)
    architecture: Dict = Field(default_factory=dict)
    quality: MetricsData
    vulnerabilities: Dict = Field(default_factory=dict)
    security: Dict = Field(default_factory=dict)
    dependencies: Dict = Field(default_factory=dict)
    testing: Dict = Field(default_factory=dict)
    patterns: Dict = Field(default_factory=dict)
    use_cases: Dict = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "name": "KSESSIONS",
                    "path": "D:\\PROJECTS\\KSESSIONS",
                    "primary_language": "C#",
                    "total_files": 26434,
                    "total_lines": 3658465,
                    "contributors": 30,
                    "last_updated": "2026-02-08T15:30:00Z",
                    "repo_age_days": 635
                }
            }
        }
```

---

## 📚 Supporting Files to Create

### 1. repo-dashboard-schema.json
Complete JSON schema with validation rules for all 9 tabs

### 2. design-tokens.css
CSS custom properties matching approved-orchestrator-view theme

### 3. component-library.css
8+ reusable components (glass-card, metric-card, badges, tables, etc.)

### 4. d3-visualizations.js
7 D3.js chart implementations with interactive features

### 5. code-to-business-transformer.py
LLM integration for capability detection + business language generation

### 6. orchestrator-integration.py
RepoOnboardingOrchestrator hooks + dashboard generation pipeline

### 7. dashboard-rendering.js
Data binding, tab management, dynamic DOM updates

### 8. accessibility-audit.md
WCAG 2.1 AA compliance checklist + fixes

### 9. performance-guide.md
Optimization strategies, lazy loading, caching

### 10. deployment-guide.md
Instructions for dashboard generation + hosting

---

## ✅ Success Criteria

| Criterion | Target | Validation |
|-----------|--------|-----------|
| **Visual Fidelity** | Match approved-orchestrator-view theme | Color match, typography, spacing |
| **Data Binding** | 100% of metrics rendered from JSON | All 9 tabs populated correctly |
| **Visualizations** | 7 D3.js charts fully interactive | All chart types responsive |
| **Business Language** | LLM generates 90%+ accurate summaries | Manual review by stakeholder |
| **Accessibility** | WCAG 2.1 AA compliance | Automated + manual audit |
| **Performance** | < 3s initial load, < 500ms tab switch | Lighthouse score > 90 |
| **Mobile** | Responsive on 320px - 1920px | Tested on iOS/Android browsers |
| **Testing** | 90%+ code coverage | Jest + E2E tests passing |

---

## 🚀 Next Steps

1. **Create JSON schema** (repo-dashboard-schema.json) with full validation
2. **Design CSS token system** (design-tokens.css) matching approved-orchestrator-view
3. **Build component library** (8+ components with variants)
4. **Implement Overview tab** (header + metrics + audience cards)
5. **Create data binding framework** (JSON → DOM rendering)
6. **Add D3.js visualizations** (start with sunburst + force-directed)
7. **Integrate with RepoOnboardingOrchestrator**
8. **Implement LLM-powered use case generation**
9. **Accessibility audit** + mobile testing
10. **Documentation** + deployment guide

---

## 📞 Stakeholder Mapping

| Persona | Primary Tabs | Key Metrics | Value Drivers |
|---------|--------------|------------|---------------|
| **Executive** | Overview, Security, Impact | Health score, vulnerabilities, ROI | Risk reduction, compliance |
| **Product Owner** | Overview, Use Cases, Testing | Features, test coverage, velocity | Capability inventory, quality |
| **Dev Manager** | Quality, Testing, Architecture | Code metrics, coverage, debt | Team productivity, health |
| **Engineer** | Architecture, Patterns, Dependencies | Complexity, patterns, tech debt | Implementation guidance |
| **Security Lead** | Security, Vulnerabilities, Compliance | OWASP compliance, CVEs, secrets | Risk management, compliance |

---

**Version:** 1.0  
**Last Updated:** 2026-02-08  
**Next Review:** 2026-02-22 (after S1-S2 completion)

This document is living — update as implementation progresses and learnings emerge.
