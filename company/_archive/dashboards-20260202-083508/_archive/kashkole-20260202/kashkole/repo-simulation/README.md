# KASHKOLE Repository Simulation Data

**Purpose:** Simulated repository data for testing the enterprise dashboard system at multiple scales.

**Generated:** 2026-02-01  
**Based On:** Real repository analysis (KSESSIONS, NOOR CANVAS, ALIST, KASHKOLE)

---

## 📊 Repository Tiers

| Tier | Name | Files | LOC | Classes | Services | Vulnerabilities | Tech Stack |
|------|------|-------|-----|---------|----------|-----------------|------------|
| **Small** | ContosoPOS | 89 | 8.5K | 32 | Monolith | 9 | ASP.NET Core 8, SQL Server |
| **Medium** | ContosoHR | 892 | 85K | 145 | SOA | 25 | ASP.NET Core 8, Angular 17, SQL Server, Redis |
| **Large** | ContosoECommerce | 8.5K | 450K | 485 | 10 μservices | 66 | ASP.NET Core 8, React 18, Next.js, Multi-DB |
| **XLarge** | ContosoFinancialPlatform | 35K | 1.85M | 1,850 | 6 domains | 188 | ASP.NET Core 8, Angular 17, React Native, Oracle, SQL Server |
| **Enterprise** | ContosoGlobalPlatform | 125K | 8.5M | 5,850 | 201 μservices | 618 | Multi-cloud (Azure/AWS/GCP), 12 regions, 10 domains |

---

## 📁 Data Files Available

Each tier includes the following JSON files:

### Core Files (All Tiers)
- ✅ `repo_metrics.json` - Repository statistics and overview
- ✅ `database_schema.json` - Database topology and schema information
- ✅ `vulnerabilities.json` - Security issues, anti-patterns, compliance findings

### Extended Files (Medium+)
- ✅ `directory_structure.json` - File system layout and architecture
- ✅ `dependencies.json` - Package dependencies and vulnerability data

### Small Tier Only
- ✅ `directory_structure.json` - Simplified for small repos

---

## 🗂️ Tier Details

### Small Tier (repo-S) - ContosoPOS
**Profile:** Small business point-of-sale system  
**Architecture:** Monolithic ASP.NET Core application  
**Database:** SQL Server (0.5GB)  
**Files:** 89 files across 15 directories  
**Notable:** Entry-level complexity, single deployment unit

**Files:**
- `repo_metrics.json`
- `directory_structure.json`
- `database_schema.json`
- `dependencies.json` (6 NuGet packages)
- `vulnerabilities.json` (9 issues)

---

### Medium Tier (repo-M) - ContosoHR
**Profile:** Enterprise HR management system  
**Architecture:** Service-Oriented Architecture (SOA)  
**Database:** SQL Server (25GB) + Redis  
**Files:** 892 files, Angular 17 SPA frontend  
**Notable:** REST APIs, microservice-ready design

**Files:**
- `repo_metrics.json`
- `directory_structure.json`
- `database_schema.json`
- `dependencies.json` (20 packages)
- `vulnerabilities.json` (25 issues)

---

### Large Tier (repo-L) - ContosoECommerce
**Profile:** Multi-tenant e-commerce platform  
**Architecture:** 10 microservices  
**Database:** SQL Server (850GB) + MongoDB + Redis + Elasticsearch  
**Files:** 8,523 files, React 18 + Next.js frontends  
**Notable:** Event-driven, distributed transactions

**Files:**
- `repo_metrics.json`
- `directory_structure.json`
- `database_schema.json`
- `dependencies.json` (185 packages)
- `vulnerabilities.json` (66 issues including Distributed Monolith)

---

### XLarge Tier (repo-XL) - ContosoFinancialPlatform
**Profile:** Financial services platform  
**Architecture:** Domain-Driven Design (6 bounded contexts)  
**Database:** SQL Server (4.5TB) + Oracle (2.8TB legacy) + Cosmos DB (1.2TB)  
**Files:** 35,248 files, Angular 17 + React Native  
**Notable:** PCI-DSS compliance, legacy migration, Saga patterns

**Files:**
- `repo_metrics.json`
- `directory_structure.json`
- `database_schema.json`
- `dependencies.json` (425 packages including legacy)
- `vulnerabilities.json` (188 issues including compliance violations)

---

### Enterprise Tier (repo-enterprise) - ContosoGlobalPlatform
**Profile:** Global multi-cloud platform  
**Architecture:** 201 microservices across 10 domains  
**Database:** 5.8PB total (SQL Server, Oracle, MongoDB, Cosmos DB, Cassandra, Elasticsearch, Snowflake)  
**Files:** 125,483 files across 12 regions  
**Notable:** Multi-cloud (Azure/AWS/GCP/Alibaba/IBM), 5.8B daily transactions, 2.5M req/sec peak

**Files:**
- `repo_metrics.json`
- `directory_structure.json`
- `database_schema.json`
- `dependencies.json` (1,250 packages, multi-cloud SDKs)
- `vulnerabilities.json` (618 issues including SOC2/ISO27001/GDPR/HIPAA/PCI-DSS/FedRAMP)

---

## 🔍 Vulnerability Categories

All `vulnerabilities.json` files follow the same structure:

```json
{
  "vulnerability_summary": { "total": N, "by_severity": {...} },
  "code_smells": [...],
  "anti_patterns": [...],
  "security_issues": [...],
  "compliance_issues": [...],
  "best_practice_violations": [...]
}
```

### Severity Levels
- **Critical:** Requires immediate action (e.g., hardcoded secrets, broken access control)
- **High:** Significant security risk (e.g., SQL injection, vulnerable dependencies)
- **Medium:** Code quality issues (e.g., code duplication, missing idempotency)
- **Low:** Documentation and consistency issues

### Referenced Best Practices
All vulnerabilities reference CORTEX knowledge YAMLs:
- `engineering-anti-patterns.yaml`
- `owasp-top-10.yaml`
- `secure-coding-practices.yaml`
- `microservices-resilience-patterns.yaml`
- `ddd-bounded-contexts.yaml`
- `rest-api-design.yaml`
- `clean-code.yaml`

---

## 🎯 Usage

### Testing Dashboard Generation
```bash
# Generate dashboard for specific tier
python company/dashboards/generate_complete_dashboard.py --repo repo-S
python company/dashboards/generate_complete_dashboard.py --repo repo-M
python company/dashboards/generate_complete_dashboard.py --repo repo-L
python company/dashboards/generate_complete_dashboard.py --repo repo-XL
python company/dashboards/generate_complete_dashboard.py --repo repo-enterprise
```

### Data Access Pattern
```python
import json
from pathlib import Path

# Load any tier's data
tier = "repo-enterprise"
base_path = Path(f"company/dashboards/kashkole/repo-simulation/{tier}")

metrics = json.loads((base_path / "repo_metrics.json").read_text())
vulnerabilities = json.loads((base_path / "vulnerabilities.json").read_text())
database = json.loads((base_path / "database_schema.json").read_text())
```

---

## 📈 Scale Progression

| Metric | Small | Medium | Large | XLarge | Enterprise |
|--------|-------|--------|-------|--------|------------|
| **Files** | 89 | 892 | 8.5K | 35K | 125K |
| **LOC** | 8.5K | 85K | 450K | 1.85M | 8.5M |
| **DB Size** | 0.5GB | 25GB | 850GB | 8.5TB | 5.8PB |
| **Services** | 1 | 3 | 10 | 23 | 201 |
| **Domains** | 1 | 1 | 1 | 6 | 10 |
| **Regions** | 1 | 1 | 2 | 3 | 12 |
| **Clouds** | 1 | 1 | 1 | 2 | 5 |

---

## 🔧 Maintenance

**To update simulation data:**
1. Analyze real repositories for current patterns
2. Update JSON files to reflect new tech stacks
3. Add new vulnerability types from CORTEX knowledge base
4. Ensure compliance requirements stay current (SOC2, GDPR, etc.)

**Data freshness:** Review quarterly to align with:
- New .NET versions
- OWASP Top 10 updates
- Framework version releases
- Cloud provider SDKs

---

## ✅ Validation Checklist

All simulation data has been validated for:
- [x] Realistic file counts and LOC
- [x] Accurate tech stack versions (as of 2026-02-01)
- [x] Microsoft tech stack focus (ASP.NET Core, C#, SQL Server, Azure)
- [x] Realistic vulnerability distribution
- [x] Compliance requirement accuracy
- [x] Database schema complexity
- [x] Dependency vulnerability data
- [x] Scale progression realism

---

## 📝 Notes

- **Mermaid Removed:** No Mermaid diagrams (doesn't work with `file://` protocol)
- **Single Template:** Dashboard uses one adaptive template, not per-tier templates
- **Real Repo Basis:** Data modeled from KSESSIONS (51K files), NOOR CANVAS (32K), ALIST (2.6K), KASHKOLE (6K)
- **Best Practices:** All vulnerability findings reference CORTEX knowledge YAMLs

---

**Generated by:** CORTEX Dashboard Simulation  
**Phase:** 18 (Enterprise Dashboard System)  
**Approved:** 2026-02-01
