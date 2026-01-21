# Azure Deployment

**Status:** Production Ready | **Last Updated:** 2026-01-21

Deploy CORTEX to Microsoft Azure cloud platform.

## Overview

Deploying CORTEX on Azure provides scalability and cloud-native features.

## Prerequisites

- Azure subscription
- Azure CLI installed
- Container registry access
- App Service plan

## Deployment Architecture

```
Azure Container Registry
    ↓
Azure App Service
    ↓
Azure Database for PostgreSQL
    ↓
Azure Application Insights
```

## Step 1: Prepare Image

```bash
# Build image
docker build -t cortex:latest .

# Tag for Azure
docker tag cortex:latest cortexregistry.azurecr.io/cortex:latest

# Push to registry
docker push cortexregistry.azurecr.io/cortex:latest
```

## Step 2: Create App Service

```bash
az appservice plan create \
  --name cortex-plan \
  --resource-group cortex-rg \
  --sku B3 \
  --is-linux

az webapp create \
  --name cortex-app \
  --plan cortex-plan \
  --resource-group cortex-rg \
  --deployment-container-image-name cortexregistry.azurecr.io/cortex:latest
```

## Step 3: Configure Database

```bash
az postgres server create \
  --name cortex-db \
  --resource-group cortex-rg \
  --admin-user dbadmin \
  --admin-password <password> \
  --sku-name B_Gen5_1
```

## Step 4: Environment Variables

```bash
az webapp config appsettings set \
  --name cortex-app \
  --resource-group cortex-rg \
  --settings \
    CORTEX_ENV=production \
    CORTEX_DATABASE_URL=postgresql://... \
    CORTEX_LOG_LEVEL=INFO
```

## Step 5: Deploy

```bash
az webapp deployment container config \
  --name cortex-app \
  --resource-group cortex-rg

az webapp restart --name cortex-app --resource-group cortex-rg
```

## Monitoring

```bash
# View logs
az webapp log tail --name cortex-app --resource-group cortex-rg

# Application Insights
az monitor metrics list \
  --resource /subscriptions/.../resourceGroups/cortex-rg/providers/Microsoft.Web/sites/cortex-app
```

## Related Resources

- [Production Deployment](3-production-deployment.md)
- [Deployment Guide](0-overview.md)
