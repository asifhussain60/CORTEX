# Operations Reports
**Purpose:** Operational and deployment reports  
**Authority:** AC-REPORTS-CONSOLIDATION-001

## Report Types
- Deployment logs and status
- Incident response reports
- Health check results
- Performance and monitoring data
- Operational SLA tracking

## Naming Pattern
`{category}-{description}-{date}.{md|yaml}`

**Examples:**
- `deployment-cortex-6.0-prod-2026-01-25.md`
- `incident-registry-database-failure-2026-01-25.md`
- `health-check-daily-2026-01-25.yaml`
- `performance-monitoring-weekly-2026-01-25.md`
- `sla-tracking-q1-2026.yaml`

## Format Guide
- Use **Markdown (.md)** for incident reports and deployment narratives
- Use **YAML (.yaml)** for health checks and metrics

## Operational Contacts
- **Infrastructure:** See deployment/
- **Monitoring:** See health_checks.yaml
- **Incidents:** Report with incident-*.md

---

See `reports/README.md` for complete guidelines.
