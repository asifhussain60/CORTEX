# Production Deployment

**Status:** Production Ready | **Last Updated:** 2026-01-21

Deploy CORTEX to production environment.

## Overview

Production deployment requires careful planning and execution.

## Prerequisites

- Staging tests completed
- Production infrastructure ready
- Backup procedures tested
- Rollback plan documented

## Deployment Checklist

- [ ] Code review completed
- [ ] All tests passing
- [ ] Staging validation complete
- [ ] Backup scheduled
- [ ] Monitoring configured
- [ ] Alerting configured
- [ ] Runbooks prepared
- [ ] Team on call

## Deployment Steps

### 1. Pre-deployment

```bash
cortex pre-deploy-check --env production
```

### 2. Deploy Code

```bash
docker push cortex:production
cortex deploy --env production --version 1.0.0
```

### 3. Database Migration

```bash
cortex db migrate --env production
```

### 4. Health Checks

```bash
cortex health-check --env production
```

### 5. Monitoring

Monitor for:
- Error rates
- Response times
- Resource usage
- User experience

## Rollback Procedure

If issues detected:

```bash
cortex deploy rollback --env production
cortex db rollback --env production
```

## Post-deployment

- Monitor metrics closely
- Watch error logs
- Gather user feedback
- Document any issues

## Related Resources

- [Deployment Guide](0-overview.md)
- [Production Readiness](../../02-architecture/production-readiness.md)
