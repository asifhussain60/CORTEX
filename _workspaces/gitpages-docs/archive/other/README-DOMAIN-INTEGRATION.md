# Domain Integration Guide

## Overview

This document provides guidance on integrating with CORTEX domains.

## All 16 CORTEX Domains

The framework includes the following core domains organized by Tier:

### Tier 0 - Core
- **governance**: Governance rules and policies
- **response_headers**: Response standardization
- **master_orchestrator**: Central orchestration
- **audit**: Audit logging and tracking

### Tier 1 - Essential
- **planning**: Planning and phase management
- **tdd**: Test-driven development
- **knowledge**: Knowledge management
- **intent_router**: Intent classification

### Tier 2 - Extended
- **domain_brain**: Domain modeling
- **testing**: Test execution
- **deployment**: Deployment management
- **ci_cd**: CI/CD pipelines

### Tier 3 - Knowledge
- **observability**: Monitoring and metrics
- **infrastructure**: Infrastructure as code
- **devx**: Developer experience
- **mcp**: MCP tool management

## Business Domain Integration

### Business Domain Schema
Business domains can be integrated using the standard domain interface.

To configure a business domain:
1. Create domain definition in domain-registry.yaml
2. Setup environment variables for endpoints
3. Register with DomainBrainAPI

### Environment Configuration
```bash
export CORTEX_DOMAIN_ENDPOINT=http://localhost:8000/domains
export DOMAIN_BRAIN_ENDPOINT=http://localhost:8001/brain
```

## Integration Endpoint

The domain integration endpoint is configurable:
- Default: `http://localhost:8000/domains`
- Environment variable: `CORTEX_DOMAIN_ENDPOINT`

## Query Patterns by Tier

### Tier 0 Queries
Core domain queries are cached and always available.

### Tier 1-2 Queries
Essential and extended domain queries with fallback support.

### Tier 3 Queries
Knowledge domain queries with optional caching.

## Fallback Guarantee

When a domain query fails, the system guarantees:
1. Graceful degradation to cached data (optional fallback)
2. Logging of failure for monitoring
3. Return of partial results where available

The fallback behavior is optional and can be configured per-domain.

## Examples

### Create Domain
```python
from cortex.domain_brain.api import DomainBrainAPI
from cortex.domain_brain.models import Domain

api = DomainBrainAPI()
domain = Domain(
    domain_id="my-domain",
    name="My Domain",
    description="Description"
)
api.upsert_domain(domain)
```

### Handle Conflicts
```python
conflicts = api.get_conflicts("domain-id")
for conflict in conflicts:
    api.resolve_conflict(conflict.conflict_id, resolved_value)
```

### Query Domain
```python
domain = api.query_domain("domain-id")
entities = api.search_entities("query")
```

### Extend with Business Domains
```python
# Configure business domain endpoint
business_domain = Domain(
    domain_id="sales",
    name="Sales Domain",
    description="Sales business domain"
)
api.upsert_domain(business_domain)
```
