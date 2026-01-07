# PaymentProcessor Transaction Invoices - Azure Resource Deployment Guide

**Version:** 1.0  
**Date:** December 12, 2025  
**Author:** Asif Hussain

---

## 📋 Overview

This guide covers deploying Azure infrastructure for PaymentProcessor Transaction Invoices modernization:
- **Azure App Configuration** - Feature flags and configuration management
- **Application Insights** - Monitoring and telemetry
- **Azure Key Vault** - Secrets and encryption key management

---

## 🛠️ Prerequisites

### Required Tools
- **Azure CLI** (v2.50+): https://aka.ms/installazurecli
- **Azure PowerShell** (optional): https://aka.ms/installazpowershell
- **Bicep CLI** (included with Azure CLI v2.20+)

### Verify Installation
```powershell
# Check Azure CLI
az version

# Check Bicep
az bicep version

# Login to Azure
az login
```

### Azure Permissions
- **Contributor** role on target subscription
- **User Access Administrator** (for RBAC assignments)

---

## 🚀 Quick Start

### 1. Deploy to Dev Environment
```powershell
cd deploy/azure
.\deploy.ps1 -Environment dev
```

### 2. Deploy to Staging
```powershell
.\deploy.ps1 -Environment staging
```

### 3. Deploy to Production (with confirmation)
```powershell
.\deploy.ps1 -Environment prod
```

### 4. Preview Changes (What-If)
```powershell
.\deploy.ps1 -Environment dev -WhatIf
```

---

## 📂 File Structure

```
deploy/azure/
├── deploy-azure-resources.bicep    # Main Bicep template
├── deploy.ps1                      # PowerShell deployment script
├── parameters.dev.json             # Dev environment parameters
├── parameters.staging.json         # Staging environment parameters
├── parameters.prod.json            # Production environment parameters
└── README.md                       # This file
```

---

## 🔧 Deployment Parameters

### Required Parameters
| Parameter | Description | Example |
|-----------|-------------|---------|
| `environment` | Environment name | `dev`, `staging`, `prod` |

### Optional Parameters
| Parameter | Description | Default |
|-----------|-------------|---------|
| `location` | Azure region | `eastus2` |
| `resourceGroupName` | Resource group name | `rg-ra-transaction-invoices-{env}` |
| `WhatIf` | Preview changes without deploying | `false` |
| `SkipConfirmation` | Skip confirmation prompt | `false` |

### Example with Custom Parameters
```powershell
.\deploy.ps1 `
    -Environment prod `
    -Location westus2 `
    -ResourceGroupName "rg-ra-custom" `
    -SkipConfirmation
```

---

## 📦 Resources Created

### 1. Azure App Configuration
**Name:** `ra-transaction-invoices-config-{env}`  
**SKU:** Standard (required for feature flags)  
**Features:**
- Feature flag: `DataLayerRollout` (starts disabled, 0% traffic)
- Configuration keys for fallback values
- Soft delete enabled (7-day retention in prod)
- System-assigned managed identity

### 2. Application Insights
**Name:** `ra-transaction-invoices-insights-{env}`  
**Features:**
- Connected to Log Analytics workspace
- 90-day retention
- 100% sampling (no data loss)
- IP masking enabled (GDPR compliance)
- Web application type

### 3. Azure Key Vault
**Name:** `ra-transaction-invoices-kv-{env}`  
**SKU:** Standard (Premium for HSM in production)  
**Features:**
- Soft delete enabled (90-day retention)
- Purge protection enabled (production only)
- RBAC authorization enabled
- Secrets stored:
  - `AppConfiguration--ConnectionString`
  - `ApplicationInsights--ConnectionString`
  - `ApplicationInsights--InstrumentationKey`
- Encryption key: `ra-transaction-encryption-key` (2048-bit RSA)

---

## 🔐 Post-Deployment Configuration

### 1. Grant API Managed Identity Access to Key Vault

#### Option A: Azure Portal
1. Navigate to Key Vault → Access control (IAM)
2. Click "Add role assignment"
3. Select role: **Key Vault Secrets User**
4. Select customer: Your API app service managed identity
5. Click "Review + assign"

#### Option B: Azure CLI
```bash
# Get API managed identity principal ID
APP_IDENTITY=$(az webapp identity show \
    --name ra-transaction-invoices-api-prod \
    --resource-group rg-ra-transaction-invoices-prod \
    --query principalId \
    --output tsv)

# Grant Key Vault Secrets User role
az role assignment create \
    --role "Key Vault Secrets User" \
    --assignee $APP_IDENTITY \
    --scope /subscriptions/{SUBSCRIPTION-ID}/resourceGroups/rg-ra-transaction-invoices-prod/providers/Microsoft.KeyVault/vaults/ra-transaction-invoices-kv-prod
```

### 2. Update Application Configuration

#### appsettings.Production.json
```json
{
  "AzureAppConfiguration": {
    "ConnectionString": "@Microsoft.KeyVault(SecretUri=https://ra-transaction-invoices-kv-prod.vault.azure.net/secrets/AppConfiguration--ConnectionString/)"
  },
  "ApplicationInsights": {
    "ConnectionString": "@Microsoft.KeyVault(SecretUri=https://ra-transaction-invoices-kv-prod.vault.azure.net/secrets/ApplicationInsights--ConnectionString/)"
  },
  "AzureKeyVault": {
    "Url": "https://ra-transaction-invoices-kv-prod.vault.azure.net/"
  }
}
```

### 3. Configure Feature Flags in App Configuration Portal

1. Navigate to Azure App Configuration → Feature manager
2. Find feature flag: `DataLayerRollout`
3. Configure initial state:
   - **Enabled:** `false` (start with feature off)
   - **Percentage filter:** `0%` (no EF Core traffic initially)
4. Save changes

---

## 📊 Monitoring & Validation

### Verify Resources Created
```bash
# List all resources in resource group
az resource list \
    --resource-group rg-ra-transaction-invoices-prod \
    --output table
```

### Test App Configuration Connection
```bash
# Get feature flag value
az appconfig feature show \
    --name ra-transaction-invoices-config-prod \
    --feature DataLayerRollout
```

### Test Key Vault Access
```bash
# Get secret (requires permissions)
az keyvault secret show \
    --vault-name ra-transaction-invoices-kv-prod \
    --name AppConfiguration--ConnectionString
```

### View Application Insights Metrics
1. Navigate to Application Insights → Live Metrics
2. Deploy API and verify telemetry appears
3. Check for connection errors

---

## 🔄 Gradual Rollout Process

### Week 1: 0% → 10%
```bash
# Update feature flag to 10%
az appconfig feature set \
    --name ra-transaction-invoices-config-prod \
    --feature DataLayerRollout \
    --percentage 10 \
    --yes
```

### Week 2: 10% → 25%
```bash
az appconfig feature set \
    --name ra-transaction-invoices-config-prod \
    --feature DataLayerRollout \
    --percentage 25 \
    --yes
```

### Continue incrementally through 50%, 75%, to 100%

**See:** `gradual-rollout.ps1` for automated rollout script.

---

## 🚨 Rollback Procedures

### Emergency Rollback to 0%
```bash
# Immediate rollback
az appconfig feature set \
    --name ra-transaction-invoices-config-prod \
    --feature DataLayerRollout \
    --percentage 0 \
    --yes
```

### Disable Feature Entirely
```bash
# Disable feature flag
az appconfig feature disable \
    --name ra-transaction-invoices-config-prod \
    --feature DataLayerRollout \
    --yes
```

---

## 🧹 Cleanup

### Delete Resource Group (All Resources)
```bash
az group delete \
    --name rg-ra-transaction-invoices-dev \
    --yes \
    --no-wait
```

### Delete Individual Resources
```bash
# Delete App Configuration
az appconfig delete \
    --name ra-transaction-invoices-config-dev \
    --resource-group rg-ra-transaction-invoices-dev \
    --yes

# Delete Application Insights
az monitor app-insights component delete \
    --app ra-transaction-invoices-insights-dev \
    --resource-group rg-ra-transaction-invoices-dev

# Delete Key Vault (with purge protection)
az keyvault delete \
    --name ra-transaction-invoices-kv-dev \
    --resource-group rg-ra-transaction-invoices-dev

# Purge Key Vault (permanent deletion)
az keyvault purge \
    --name ra-transaction-invoices-kv-dev \
    --location eastus2
```

---

## 📝 Troubleshooting

### Issue: "Resource group not found"
**Solution:** Resource group is created automatically by `deploy.ps1`. If using Azure CLI directly, create it first:
```bash
az group create --name rg-ra-transaction-invoices-dev --location eastus2
```

### Issue: "Key Vault name already exists"
**Solution:** Key Vault names are globally unique. Wait 90 days after deletion or use a different name.

### Issue: "Insufficient permissions"
**Solution:** Ensure you have **Contributor** role on subscription:
```bash
az role assignment list --assignee YOUR-EMAIL@domain.com
```

### Issue: "Bicep validation failed"
**Solution:** Update Azure CLI to latest version:
```bash
az upgrade
```

---

## 🔗 Additional Resources

- **Azure App Configuration Docs:** https://learn.microsoft.com/en-us/azure/azure-app-configuration/
- **Application Insights Docs:** https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview
- **Azure Key Vault Docs:** https://learn.microsoft.com/en-us/azure/key-vault/
- **Bicep Docs:** https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/

---

**Last Updated:** December 12, 2025  
**Maintained By:** Platform Engineering Team
