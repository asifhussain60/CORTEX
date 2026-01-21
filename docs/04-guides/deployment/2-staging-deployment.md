# Staging Deployment

**Status:** Production Ready | **Last Updated:** 2026-01-21

Deploy CORTEX to staging environment for testing before production.

## Overview

Staging deployment mirrors production setup for thorough testing.

## Prerequisites

- Production deployment setup completed
- Test data available
- Staging infrastructure provisioned

## Deployment Steps

### 1. Prepare Environment

```bash
export CORTEX_ENV=staging
export CORTEX_DATABASE_URL=postgresql://user:pass@staging-db:5432/cortex_staging
```

### 2. Deploy Code

```bash
git checkout main
git pull
docker build -t cortex:staging .
```

### 3. Run Migrations

```bash
cortex db migrate --env staging
```

### 4. Smoke Tests

```bash
cortex test --env staging --type smoke
```

### 5. Load Tests

```bash
cortex test --env staging --type load --users 100
```

## Monitoring

- Monitor error rates
- Check performance metrics
- Verify audit logs
- Test failover procedures

## Rollback Procedure

```bash
cortex deploy rollback --env staging --version previous
```

## Related Resources

- [Production Deployment](3-production-deployment.md)
- [Deployment Guide](0-overview.md)
