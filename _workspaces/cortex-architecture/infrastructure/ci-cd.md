# CI/CD Pipeline

**Purpose:** Continuous Integration and Deployment for CORTEX  
**Audience:** DevOps, Developers  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Pipeline Architecture](#pipeline-architecture)
- [Continuous Integration](#continuous-integration)
- [Continuous Deployment](#continuous-deployment)
- [Quality Gates](#quality-gates)
- [Release Process](#release-process)
- [Related Documents](#related-documents)

---

## Overview

CORTEX uses GitHub Actions for CI/CD with automated testing, security scanning, and deployment.

```
┌─────────────────────────────────────────────────────────────────┐
│                    CI/CD PIPELINE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CONTINUOUS INTEGRATION                                   │  │
│  │                                                           │  │
│  │  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐  │  │
│  │  │ Lint │──▶│ Type │──▶│ Unit │──▶│Integ │──▶│ Sec  │  │  │
│  │  │      │   │Check │   │Tests │   │Tests │   │ Scan │  │  │
│  │  └──────┘   └──────┘   └──────┘   └──────┘   └──────┘  │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  BUILD                                                    │  │
│  │                                                           │  │
│  │  ┌──────┐   ┌──────┐   ┌──────┐                         │  │
│  │  │Docker│──▶│ Push │──▶│ Tag  │                         │  │
│  │  │Build │   │  ECR │   │Latest│                         │  │
│  │  └──────┘   └──────┘   └──────┘                         │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CONTINUOUS DEPLOYMENT                                    │  │
│  │                                                           │  │
│  │  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐             │  │
│  │  │Staging│──▶│Smoke │──▶│ Prod │──▶│Verify│             │  │
│  │  │Deploy│   │Tests │   │Deploy│   │      │             │  │
│  │  └──────┘   └──────┘   └──────┘   └──────┘             │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pipeline Architecture

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install ruff black isort
      - name: Run linters
        run: |
          ruff check cortex/
          black --check cortex/
          isort --check cortex/

  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install mypy types-redis
      - name: Type check
        run: mypy cortex/ --strict

  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      - name: Run tests
        run: pytest tests/unit/ --cov=cortex --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: coverage.xml

  integration-tests:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run integration tests
        env:
          REDIS_URL: redis://localhost:6379
        run: pytest tests/integration/ -v

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          format: 'sarif'
          output: 'trivy-results.sarif'
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  build:
    needs: [lint, type-check, unit-tests, integration-tests, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t cortex/mcp-server:${{ github.sha }} .
      - name: Login to ECR
        uses: aws-actions/amazon-ecr-login@v1
      - name: Push to ECR
        run: |
          docker tag cortex/mcp-server:${{ github.sha }} $ECR_REGISTRY/cortex:${{ github.sha }}
          docker tag cortex/mcp-server:${{ github.sha }} $ECR_REGISTRY/cortex:latest
          docker push $ECR_REGISTRY/cortex:${{ github.sha }}
          docker push $ECR_REGISTRY/cortex:latest
```

---

## Continuous Integration

### Test Strategy

```python
# Test categories
tests/
├── unit/                 # Fast, isolated tests
│   ├── test_mcp/
│   ├── test_lens/
│   └── test_orchestrators/
├── integration/          # Component integration
│   ├── test_mcp_redis/
│   └── test_lens_cache/
└── e2e/                  # End-to-end workflows
    ├── test_implement_flow/
    └── test_analyze_flow/
```

### Coverage Requirements

| Component | Minimum Coverage |
|-----------|-----------------|
| Core (mcp, orchestrators) | 90% |
| LENS | 85% |
| Tools | 80% |
| Overall | 85% |

### Pre-Commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.0.280
    hooks:
      - id: ruff
        args: [--fix]
  
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest tests/unit/ -x -q
        language: system
        pass_filenames: false
        always_run: true
```

---

## Continuous Deployment

### Deployment Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to staging
        uses: azure/k8s-deploy@v4
        with:
          manifests: |
            deployment/k8s/staging/
          images: |
            ${{ env.ECR_REGISTRY }}/cortex:${{ github.sha }}
          namespace: cortex-staging
      
      - name: Run smoke tests
        run: |
          sleep 30
          curl -f http://staging.cortex.example.com/health
          pytest tests/smoke/ --env=staging

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to production
        uses: azure/k8s-deploy@v4
        with:
          manifests: |
            deployment/k8s/production/
          images: |
            ${{ env.ECR_REGISTRY }}/cortex:${{ github.ref_name }}
          namespace: cortex-production
          strategy: canary
          percentage: 10
      
      - name: Verify deployment
        run: |
          sleep 60
          pytest tests/smoke/ --env=production
      
      - name: Promote to full rollout
        run: |
          kubectl rollout resume deployment/cortex-mcp -n cortex-production
```

### Canary Deployment

```yaml
# Canary configuration
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: cortex-mcp
  namespace: cortex-production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: cortex-mcp
  progressDeadlineSeconds: 600
  service:
    port: 8000
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
      - name: request-success-rate
        thresholdRange:
          min: 99
        interval: 1m
      - name: request-duration
        thresholdRange:
          max: 500
        interval: 1m
```

---

## Quality Gates

### Gate Checklist

| Gate | Criteria | Action if Failed |
|------|----------|------------------|
| Lint | Zero errors | Block PR |
| Type Check | No type errors | Block PR |
| Unit Tests | 100% pass | Block PR |
| Coverage | ≥85% | Block PR |
| Integration Tests | 100% pass | Block PR |
| Security Scan | No critical/high | Block PR |
| Performance | P95 < 500ms | Warning |

### Branch Protection

```yaml
# Branch protection rules (GitHub settings)
main:
  required_status_checks:
    strict: true
    contexts:
      - lint
      - type-check
      - unit-tests
      - integration-tests
      - security-scan
  required_pull_request_reviews:
    required_approving_review_count: 1
    dismiss_stale_reviews: true
  enforce_admins: true
```

---

## Release Process

### Semantic Versioning

```
v{major}.{minor}.{patch}

Examples:
- v1.0.0 - Major release
- v1.1.0 - Feature release
- v1.1.1 - Bug fix
```

### Release Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Generate changelog
        id: changelog
        uses: mikepenz/release-changelog-builder-action@v3
        with:
          configuration: ".github/changelog-config.json"
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          body: ${{ steps.changelog.outputs.changelog }}
          draft: false
          prerelease: ${{ contains(github.ref, '-rc') }}
      
      - name: Build and push Docker image
        run: |
          VERSION=${GITHUB_REF#refs/tags/}
          docker build -t cortex/mcp-server:$VERSION .
          docker push cortex/mcp-server:$VERSION
      
      - name: Deploy to production
        if: "!contains(github.ref, '-rc')"
        run: |
          kubectl set image deployment/cortex-mcp \
            mcp=cortex/mcp-server:$VERSION \
            -n cortex-production
```

### Release Checklist

- [ ] All tests passing
- [ ] Coverage meets threshold
- [ ] No security vulnerabilities
- [ ] Changelog updated
- [ ] Documentation updated
- [ ] Version bumped
- [ ] Tag created
- [ ] Staging deployment verified
- [ ] Production deployment completed
- [ ] Post-deployment smoke tests passed

---

## Related Documents

- [Infrastructure Overview](overview.md) — Architecture
- [Deployment](deployment.md) — Deployment
- [Observability](observability.md) — Monitoring

---

*Part of CORTEX Architecture Documentation*
