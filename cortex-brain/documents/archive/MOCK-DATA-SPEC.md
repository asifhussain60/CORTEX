# Mock Data Specification

**Version:** 1.0  
**Created:** November 26, 2025  
**Purpose:** Define data contracts for Intelligent UX Enhancement Dashboard

---

## Overview

This directory contains mock data for 3 quality scenarios representing different project health levels:
- **Problem Project (42%)** - Legacy codebase with significant technical debt
- **Average Project (73%)** - Typical production application with room for improvement
- **Excellent Project (92%)** - Well-architected system following best practices

---

## Data Files

### Core Data (All Tabs)

**`mock-metadata.json`** - Project metadata and analysis information
```json
{
  "scenarios": [ ... ],
  "analysis": {
    "project": "PaymentProcessor",
    "version": "2.4.1",
    "analyzedDate": "2025-11-26T10:30:00Z",
    "totalFiles": 847,
    "totalLines": 124589,
    "languages": [ ... ]
  },
  "tddMasteryIntegration": { ... }
}
```

**`mock-quality.json`** - Quality metrics and code smells (Tabs 1, 3)
```json
{
  "scenarios": {
    "problem": { "overallScore": 42, ... },
    "average": { "overallScore": 73, ... },
    "excellent": { "overallScore": 92, ... }
  },
  "industryBenchmarks": { ... },
  "trendData": { ... }
}
```

**`mock-architecture.json`** - Architecture components and relationships (Tab 2)
```json
{
  "scenarios": {
    "problem": {
      "components": [ ... ],
      "relationships": [ ... ],
      "issues": [ ... ]
    },
    ...
  },
  "proposedEnhancements": { ... }
}
```

**`mock-performance.json`** - Performance metrics and bottlenecks (Tab 3)
```json
{
  "scenarios": {
    "problem": {
      "endpoints": [ ... ],
      "bottlenecks": [ ... ],
      "flamegraphData": [ ... ]
    },
    ...
  },
  "performanceTargets": { ... },
  "optimizationRecommendations": { ... }
}
```

**`mock-security.json`** - Security vulnerabilities and compliance (Tab 6)
```json
{
  "scenarios": {
    "problem": {
      "owaspTop10": [ ... ],
      "vulnerabilities": { ... },
      "compliance": { ... },
      "criticalIssues": [ ... ]
    },
    ...
  },
  "securityRoadmap": { ... }
}
```

### Discovery System Data (Intelligent Guidance)

**`patterns/suggestion-patterns.json`** - Context-aware suggestion patterns
```json
{
  "patterns": {
    "basicAuth": {
      "keywords": [ ... ],
      "suggestions": [
        {
          "title": "Multi-Factor Authentication",
          "effort": { "min": 3, "max": 5, "unit": "days" },
          "impact": { "security": "+40%", ... }
        },
        ...
      ]
    },
    ...
  },
  "triggerThresholds": { ... }
}
```

**`patterns/question-trees.json`** - Progressive questioning flows
```json
{
  "questionFlows": {
    "authentication": {
      "entry": "clarify-priority",
      "nodes": {
        "clarify-priority": {
          "type": "multiple-choice",
          "question": "What matters most to you for authentication?",
          "options": [ ... ]
        },
        ...
      }
    },
    ...
  }
}
```

**`patterns/discovery-paths.json`** - Guided discovery journeys
```json
{
  "paths": {
    "security-focused": {
      "tabs": [ ... ],
      "expectedOutcome": "...",
      "nextActions": [ ... ]
    },
    ...
  },
  "pathRecommendations": { ... }
}
```

**`scenarios/auth-scenarios.json`** - "What if" authentication scenarios
```json
{
  "currentState": { ... },
  "scenarios": [
    {
      "name": "Multi-Factor Authentication (TOTP)",
      "security": 85,
      "userFriction": 55,
      "cost": 0,
      "pros": [ ... ],
      "cons": [ ... ]
    },
    ...
  ],
  "decisionMatrix": { ... }
}
```

---

## Data Contracts

### Quality Scenario Structure

Each scenario (problem, average, excellent) contains:

```typescript
interface QualityScenario {
  overallScore: number;          // 0-100
  metrics: {
    maintainability: number;     // 0-100
    reliability: number;         // 0-100
    security: number;            // 0-100
    performance: number;         // 0-100
    testCoverage: number;        // 0-100
  };
  codeSmells: {
    total: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
    breakdown: {
      longMethod: number;
      largeClass: number;
      complexMethod: number;
      duplicateCode: number;
      godClass: number;
      featureEnvy: number;
      dataClumps: number;
      primitiveObsession: number;
      switchStatements: number;
      speculativeGenerality: number;
      temporaryField: number;
    };
  };
  technicalDebt: {
    totalMinutes: number;
    estimatedCost: string;       // "$XX,XXX"
    remediationTime: string;     // "X.X weeks"
  };
}
```

### Architecture Component Structure

```typescript
interface ArchitectureComponent {
  id: string;                    // Unique identifier
  name: string;                  // Display name
  health: number;                // 0-100
  complexity: number;            // 0-100
  dependencies: number;          // Count
  type: 'security' | 'business' | 'infrastructure' | 'interface' | 'presentation';
}

interface ComponentRelationship {
  source: string;                // Component ID
  target: string;                // Component ID
  type: 'calls' | 'depends' | 'persists' | 'logs' | 'subscribes' | 'queries';
  strength: number;              // 0-1 (coupling strength)
}
```

### Performance Metrics Structure

```typescript
interface EndpointMetrics {
  name: string;                  // e.g., "POST /api/payment"
  avgLatency: number;            // Milliseconds
  p95Latency: number;            // 95th percentile
  p99Latency: number;            // 99th percentile
  errorRate: number;             // Percentage (0-100)
}

interface PerformanceBottleneck {
  location: string;              // Method/function name
  type: 'cpu' | 'io' | 'network' | 'database' | 'optimization';
  impact: 'critical' | 'high' | 'medium' | 'low';
  description: string;           // Human-readable explanation
}
```

### Security Vulnerability Structure

```typescript
interface OwaspVulnerability {
  id: string;                    // e.g., "A01"
  name: string;                  // e.g., "Broken Access Control"
  status: 'vulnerable' | 'at-risk' | 'protected';
  severity: 'critical' | 'high' | 'medium' | 'low' | 'none';
  instances: number;             // Count of occurrences
}

interface ComplianceStatus {
  SOC2: { status: string; coverage: number; };
  GDPR: { status: string; coverage: number; };
  PCIDSS: { status: string; coverage: number; };
  HIPAA: { status: string; coverage: number; };
}
```

### Discovery System Structures

```typescript
interface SuggestionPattern {
  keywords: string[];
  contextMatch: string[];
  suggestions: Suggestion[];
}

interface Suggestion {
  id: string;
  title: string;
  description: string;
  effort: { min: number; max: number; unit: string; };
  impact: Record<string, string>;
  visualExample: string;
  priority: 'high' | 'medium' | 'low';
  learnMoreUrl: string;
}

interface QuestionNode {
  type: 'multiple-choice' | 'single-choice' | 'range' | 'open-ended' | 'recommendation';
  question: string;
  options?: QuestionOption[];
  next?: string;
}

interface DiscoveryPath {
  id: string;
  name: string;
  description: string;
  estimatedDuration: string;
  tabs: PathTab[];
  expectedOutcome: string;
  nextActions: string[];
}
```

---

## Usage Example

### Loading Data

```javascript
// Load metadata
const metadata = await fetch('assets/data/mock-metadata.json').then(r => r.json());
const scenario = 'problem'; // or 'average', 'excellent'

// Load quality data
const qualityData = await fetch('assets/data/mock-quality.json').then(r => r.json());
const quality = qualityData.scenarios[scenario];

// Load architecture data
const archData = await fetch('assets/data/mock-architecture.json').then(r => r.json());
const architecture = archData.scenarios[scenario];

// Load discovery patterns
const patterns = await fetch('assets/data/patterns/suggestion-patterns.json').then(r => r.json());
```

### Generating Suggestions

```javascript
// Context-aware suggestions based on current view
function getSuggestions(currentTab, dataContext) {
  if (currentTab === 'security' && dataContext.security < 50) {
    // Load security patterns
    return patterns.patterns.securityVulnerability.suggestions;
  }
  
  if (currentTab === 'architecture' && dataContext.components.some(c => c.health < 40)) {
    // Load architecture patterns
    return patterns.patterns.complexCode.suggestions;
  }
  
  // ... pattern matching logic
}
```

---

## Data Generation Rules

### Scenario Relationships

**Problem → Average → Excellent progression:**
- Quality scores increase ~30-40 points per level
- Code smells decrease ~70% (problem → average) and ~85% (average → excellent)
- Technical debt decreases proportionally
- Latencies improve ~60-80% per level
- Vulnerabilities decrease dramatically

### Realistic Constraints

- Performance latencies follow realistic distribution (P95 ~2x average, P99 ~3x average)
- Error rates inversely proportional to quality scores
- Cost estimates based on $50/hour developer rate
- Compliance coverage aligns with security scores
- Component health correlates with code smell density

### Pattern Triggers

- Authentication patterns trigger when security < 60%
- Performance patterns trigger when latency > 1000ms
- Security patterns trigger when vulnerabilities > critical threshold
- Complexity patterns trigger when code smells > 100

---

## Validation

All data files validated against:
- ✅ JSON syntax (no errors)
- ✅ Required fields present
- ✅ Value ranges correct (0-100 for scores, positive numbers for counts)
- ✅ Scenario consistency (problem < average < excellent)
- ✅ Relationship integrity (source/target IDs exist in components)

---

**Last Updated:** November 26, 2025  
**Total Data Size:** ~150KB (compressed JSON)  
**Load Time:** <100ms (all files)
