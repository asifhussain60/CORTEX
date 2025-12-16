// Bicep template for PaymentProcessor Transaction Invoices Azure infrastructure
// Deploys: App Configuration, Application Insights, Key Vault

@description('Environment name (dev, staging, prod)')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Application name prefix')
param appName string = 'ra-transaction-invoices'

@description('Tags for all resources')
param tags object = {
  Application: 'PaymentProcessor Transaction Invoices'
  Environment: environment
  ManagedBy: 'Bicep'
  CostCenter: 'Engineering'
  Project: 'PaymentProcessor Modernization'
}

// Variables
var appConfigName = '${appName}-config-${environment}'
var appInsightsName = '${appName}-insights-${environment}'
var keyVaultName = '${appName}-kv-${environment}'
var logAnalyticsName = '${appName}-logs-${environment}'

// Existing resources (must already exist)
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' existing = {
  name: logAnalyticsName
}

// ============================================================================
// Azure App Configuration
// ============================================================================
resource appConfiguration 'Microsoft.AppConfiguration/configurationStores@2023-03-01' = {
  name: appConfigName
  location: location
  tags: tags
  sku: {
    name: 'standard' // Required for feature flags
  }
  properties: {
    enablePurgeProtection: environment == 'prod' // Prevent accidental deletion in prod
    softDeleteRetentionInDays: environment == 'prod' ? 7 : 0
    disableLocalAuth: false // Enable connection string access
  }
  identity: {
    type: 'SystemAssigned'
  }
}

// Feature Flag: DataLayerRollout
resource featureFlagDataLayerRollout 'Microsoft.AppConfiguration/configurationStores/keyValues@2023-03-01' = {
  parent: appConfiguration
  name: '.appconfig.featureflag~2FDataLayerRollout' // URL-encoded: /DataLayerRollout
  properties: {
    value: string({
      id: 'DataLayerRollout'
      description: 'Controls EF Core vs Mock data layer traffic distribution'
      enabled: false // Start disabled
      conditions: {
        client_filters: [
          {
            name: 'Microsoft.Percentage'
            parameters: {
              Value: 0 // Start at 0%, gradually increase
            }
          }
        ]
      }
    })
    contentType: 'application/vnd.microsoft.appconfig.ff+json;charset=utf-8'
  }
}

// Configuration: EFCorePercentage (for fallback)
resource configEFCorePercentage 'Microsoft.AppConfiguration/configurationStores/keyValues@2023-03-01' = {
  parent: appConfiguration
  name: 'FeatureFlags:DataLayerRollout:EFCorePercentage'
  properties: {
    value: '0' // Start at 0%
    contentType: 'application/json'
  }
}

// Configuration: Enabled (for fallback)
resource configEnabled 'Microsoft.AppConfiguration/configurationStores/keyValues@2023-03-01' = {
  parent: appConfiguration
  name: 'FeatureFlags:DataLayerRollout:Enabled'
  properties: {
    value: 'false' // Start disabled
    contentType: 'application/json'
  }
}

// ============================================================================
// Application Insights
// ============================================================================
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
    RetentionInDays: 90 // 90-day retention
    SamplingPercentage: 100 // No sampling in production
    DisableIpMasking: false // Mask IP addresses (GDPR compliance)
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// ============================================================================
// Azure Key Vault
// ============================================================================
resource keyVault 'Microsoft.KeyVault/vaults@2023-02-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard' // Use 'premium' for HSM-backed keys in prod
    }
    tenantId: subscription().tenantId
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: environment == 'prod' // Prevent permanent deletion in prod
    enableRbacAuthorization: true // Use Azure RBAC (recommended)
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: true
    publicNetworkAccess: 'Enabled' // Change to 'Disabled' for private endpoints
    networkAcls: {
      defaultAction: 'Allow' // Change to 'Deny' for production with private endpoints
      bypass: 'AzureServices'
      ipRules: []
      virtualNetworkRules: []
    }
  }
}

// Create encryption key for data encryption
resource encryptionKey 'Microsoft.KeyVault/vaults/keys@2023-02-01' = {
  parent: keyVault
  name: 'ra-transaction-encryption-key'
  properties: {
    kty: 'RSA' // Key type: RSA
    keySize: 2048 // 2048-bit key (increase to 4096 for enhanced security)
    keyOps: [
      'encrypt'
      'decrypt'
      'wrapKey'
      'unwrapKey'
    ]
    attributes: {
      enabled: true
      exportable: false // Prevent key export
    }
  }
}

// Store App Configuration connection string in Key Vault
resource secretAppConfigConnectionString 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: keyVault
  name: 'AppConfiguration--ConnectionString'
  properties: {
    value: listKeys(appConfiguration.id, appConfiguration.apiVersion).value[0].connectionString
    contentType: 'text/plain'
    attributes: {
      enabled: true
    }
  }
}

// Store Application Insights connection string in Key Vault
resource secretAppInsightsConnectionString 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: keyVault
  name: 'ApplicationInsights--ConnectionString'
  properties: {
    value: applicationInsights.properties.ConnectionString
    contentType: 'text/plain'
    attributes: {
      enabled: true
    }
  }
}

// Store Application Insights instrumentation key in Key Vault
resource secretAppInsightsInstrumentationKey 'Microsoft.KeyVault/vaults/secrets@2023-02-01' = {
  parent: keyVault
  name: 'ApplicationInsights--InstrumentationKey'
  properties: {
    value: applicationInsights.properties.InstrumentationKey
    contentType: 'text/plain'
    attributes: {
      enabled: true
    }
  }
}

// ============================================================================
// Outputs
// ============================================================================
output appConfigurationName string = appConfiguration.name
output appConfigurationEndpoint string = appConfiguration.properties.endpoint
output appConfigurationConnectionString string = listKeys(appConfiguration.id, appConfiguration.apiVersion).value[0].connectionString

output applicationInsightsName string = applicationInsights.name
output applicationInsightsConnectionString string = applicationInsights.properties.ConnectionString
output applicationInsightsInstrumentationKey string = applicationInsights.properties.InstrumentationKey

output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
output encryptionKeyName string = encryptionKey.name
output encryptionKeyUri string = encryptionKey.properties.keyUri
