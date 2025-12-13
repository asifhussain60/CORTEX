# Phase 6: Deployment Automation

**Duration:** Week 11-12 | **Owner:** DevOps Lead

---

## 🎯 Objectives
- Azure DevOps CI/CD pipelines
- Bicep infrastructure templates
- Blue-green deployment strategy

---

## 🔧 Key Deliverables

### azure-pipelines.yml
```yaml
trigger:
  branches:
    include:
    - main
    - develop
  paths:
    include:
    - cortex/modernized/*

stages:
- stage: Build
  jobs:
  - job: BuildAndTest
    steps:
    - task: UseDotNet@2
      inputs:
        version: '8.0.x'
    - task: DotNetCoreCLI@2
      inputs:
        command: 'restore'
    - task: DotNetCoreCLI@2
      inputs:
        command: 'build'
        arguments: '--configuration Release'
    - task: DotNetCoreCLI@2
      inputs:
        command: 'test'
        arguments: '--collect:"XPlat Code Coverage"'
    - task: PublishCodeCoverageResults@1

- stage: Deploy_Test
  jobs:
  - deployment: DeployToTest
    environment: 'Test'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebApp@1
            inputs:
              azureSubscription: 'Azure-Subscription'
              appName: 'psf-prevalidation-api-test'
              package: '$(Pipeline.Workspace)/**/*.zip'
```

### Infrastructure (Bicep)
- App Service
- Azure SQL/Oracle connection
- Blob Storage
- Application Insights
- Key Vault

---

## ✅ Deliverables
- [x] CI/CD pipeline (build, test, deploy)
- [x] Bicep templates (infrastructure as code)
- [x] Deployment runbooks

---

## 📊 Update Master Plan Progress

**BEFORE proceeding to Phase 7:**

1. Update `MODERNIZATION-PLAN.md` progress tracker:
   ```
   PHASE 6: DEPLOYMENT & MONITORING [██████████] 100% ✅ Complete
   ```

2. Update Phase 6 checklist to all `[x]` completed

3. Update overall progress:
   ```
   OVERALL PROGRESS: ██████████████████████████░░░░ 9/11 Phases (82%)
   ```

4. Verify deployment artifacts:
   ```powershell
   # Bicep templates, CI/CD pipeline, monitoring dashboards
   ls deploy/azure/*.bicep
   ls .azure-pipelines/*.yml
   ```

5. Test emergency rollback:
   ```powershell
   # Verify rollback completes in <30 seconds
   Measure-Command { ./deploy/rollback.ps1 }
   ```

6. Create deployment runbook:
   ```powershell
   echo "Deployment procedures, rollback steps, monitoring" > docs/DEPLOYMENT-RUNBOOK.md
   ```

**Next:** [Phase 7: Production Rollout](phase-7-production-rollout.md)
