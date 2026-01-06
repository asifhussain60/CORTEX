# Company ABC - Architecture Guide

**Company:** ABC Corporation  
**Industry:** Enterprise Software  
**Architecture Style:** Microservices + Event-Driven  
**Last Updated:** 2026-01-06

---

## 🏗️ Architecture Principles

1. **API-First Design** - All services expose RESTful APIs
2. **Event-Driven Communication** - Services communicate via Azure Service Bus
3. **Database per Service** - Each microservice owns its data
4. **Cloud-Native** - Designed for Azure cloud platform
5. **Security by Default** - Zero-trust security model

---

## 🎯 Architectural Patterns

### Microservices Pattern
- **Gateway:** Azure API Management
- **Service Mesh:** Not used (direct service-to-service with retry policies)
- **Configuration:** Azure App Configuration
- **Secrets:** Azure Key Vault

### Event-Driven Architecture
- **Message Bus:** Azure Service Bus (topics + subscriptions)
- **Event Store:** Azure Event Hubs for event sourcing
- **Dead Letter Queue:** Automatic retry with exponential backoff

### Data Architecture
- **Primary Database:** Azure SQL Database
- **NoSQL:** Azure Cosmos DB (for high-throughput scenarios)
- **Cache:** Azure Redis Cache
- **Blob Storage:** Azure Blob Storage (documents, images)

---

## 🔐 Security Architecture

### Authentication & Authorization
- **Identity Provider:** Azure AD (Entra ID)
- **Protocol:** OAuth 2.0 + OpenID Connect
- **Token Type:** JWT (JSON Web Tokens)
- **API Security:** Bearer token authentication on all APIs

### Network Security
- **VNet Integration:** All services in private VNets
- **Service-to-Service:** Managed identities (no secrets)
- **External Access:** Azure Front Door + WAF

---

## 📊 Observability

### Logging
- **Platform:** Azure Application Insights
- **Format:** Structured JSON logs
- **Retention:** 90 days (production), 30 days (non-prod)

### Monitoring
- **APM:** Application Insights
- **Metrics:** Azure Monitor
- **Alerts:** Action Groups with PagerDuty integration

### Tracing
- **Distributed Tracing:** Application Insights correlation IDs
- **Telemetry:** OpenTelemetry SDK

---

## 🚀 Deployment Architecture

### Containerization
- **Runtime:** Docker containers
- **Orchestration:** Azure Kubernetes Service (AKS)
- **Registry:** Azure Container Registry (ACR)

### CI/CD
- **Platform:** Azure DevOps
- **Pipeline:** YAML-based pipelines
- **Deployment:** Blue-green deployments
- **Rollback:** Automatic on health check failure

---

## 📚 Reference Documentation

- **Internal Wiki:** https://wiki.company-abc.com/architecture
- **API Catalog:** See `api-catalog.json`
- **Tech Stack:** See `tech-stack.yaml`
- **Coding Standards:** See `coding-standards.md`
