# Observability & Monitoring

> **Summary:** Distributed tracing, metrics, logging, and alerting  
> **Authority:** cortex/observability/ | **Last Updated:** 2026-01-22

---

## Overview

Comprehensive observability stack for production monitoring, performance analysis, and incident response.

**Components:**
- Distributed tracing with correlation IDs
- Prometheus metrics collection
- Structured logging to ELK stack
- Health check endpoints
- Alert routing

---

## Tracing Architecture

```mermaid
graph LR
  A["User Request<br/>correlation_id: xyz"] -->|trace| B["Intent Router"]
  B -->|trace| C["Master Orchestrator"]
  C -->|trace| D["Domain Orchestrator"]
  D -->|trace| E["Execution Engine"]
  E -->|trace| F["Audit Logger"]
  F -->|write| G["Trace Backend<br/>Jaeger/Datadog"]
  
  style A fill:#2196f3,stroke:#1565c0,color:#fff
  style G fill:#2196f3,stroke:#1565c0,color:#fff,stroke-width:2px
```

---

## See Also

- [Infrastructure & Resilience](12-infrastructure/00-infrastructure-index.md)
- [Source: cortex/observability/](../../../cortex/observability/)

---

**Author:** CORTEX Documentation Engine  
**Generated:** 2026-01-22
