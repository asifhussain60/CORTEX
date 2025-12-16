# PowerShell deployment script for PaymentProcessor Transaction Invoices Azure infrastructure
# Prerequisites: Azure CLI, Azure PowerShell module, Bicep CLI

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('dev', 'staging', 'prod')]
    [string]$Environment,
    
    [Parameter(Mandatory=$false)]
    [string]$Location = 'eastus2',
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "rg-ra-transaction-invoices-$Environment",
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipConfirmation
)

# Error handling
$ErrorActionPreference = 'Stop'

# Colors for output
function Write-Success { param([string]$Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param([string]$Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param([string]$Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message) Write-Host "❌ $Message" -ForegroundColor Red }

# Banner
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║  PaymentProcessor Transaction Invoices - Azure Infrastructure Deployment         ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

# Deployment parameters
$deploymentName = "ra-transaction-invoices-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$bicepFilePath = Join-Path $PSScriptRoot "deploy-azure-resources.bicep"

Write-Info "Environment: $Environment"
Write-Info "Location: $Location"
Write-Info "Resource Group: $ResourceGroupName"
Write-Info "Deployment Name: $deploymentName"
Write-Host ""

# Validate prerequisites
Write-Info "Validating prerequisites..."

# Check Azure CLI
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Success "Azure CLI version: $($azVersion.'azure-cli')"
} catch {
    Write-Error "Azure CLI not found. Install from: https://aka.ms/installazurecli"
    exit 1
}

# Check if logged in
$account = az account show --output json 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Warning "Not logged in to Azure. Running 'az login'..."
    az login
    $account = az account show --output json | ConvertFrom-Json
}

Write-Success "Logged in as: $($account.user.name)"
Write-Success "Subscription: $($account.name) ($($account.id))"
Write-Host ""

# Confirm deployment (unless SkipConfirmation)
if (-not $SkipConfirmation -and -not $WhatIf) {
    Write-Warning "This will deploy Azure resources to environment: $Environment"
    $confirmation = Read-Host "Continue? (yes/no)"
    if ($confirmation -ne 'yes') {
        Write-Info "Deployment cancelled by user."
        exit 0
    }
}

# Create resource group if it doesn't exist
Write-Info "Checking resource group..."
$rg = az group show --name $ResourceGroupName --output json 2>$null | ConvertFrom-Json
if (-not $rg) {
    Write-Info "Creating resource group: $ResourceGroupName"
    az group create --name $ResourceGroupName --location $Location --output none
    Write-Success "Resource group created"
} else {
    Write-Success "Resource group exists: $ResourceGroupName"
}
Write-Host ""

# Validate Bicep template
Write-Info "Validating Bicep template..."
try {
    az deployment group validate `
        --resource-group $ResourceGroupName `
        --template-file $bicepFilePath `
        --parameters environment=$Environment location=$Location `
        --output none
    Write-Success "Bicep template validation passed"
} catch {
    Write-Error "Bicep template validation failed: $_"
    exit 1
}
Write-Host ""

# Deploy or preview
if ($WhatIf) {
    Write-Info "Running What-If analysis..."
    az deployment group what-if `
        --resource-group $ResourceGroupName `
        --template-file $bicepFilePath `
        --parameters environment=$Environment location=$Location `
        --name $deploymentName
    Write-Host ""
    Write-Info "What-If analysis complete. No resources were deployed."
    exit 0
}

# Deploy resources
Write-Info "Deploying Azure resources..."
Write-Host ""

$deployment = az deployment group create `
    --resource-group $ResourceGroupName `
    --template-file $bicepFilePath `
    --parameters environment=$Environment location=$Location `
    --name $deploymentName `
    --output json | ConvertFrom-Json

if ($LASTEXITCODE -ne 0) {
    Write-Error "Deployment failed. Check Azure Portal for details."
    exit 1
}

Write-Success "Deployment complete!"
Write-Host ""

# Display outputs
Write-Info "Deployment Outputs:"
Write-Host "───────────────────────────────────────────────────────────────" -ForegroundColor DarkGray

$outputs = $deployment.properties.outputs

Write-Host "App Configuration:" -ForegroundColor Yellow
Write-Host "  Name: $($outputs.appConfigurationName.value)" -ForegroundColor White
Write-Host "  Endpoint: $($outputs.appConfigurationEndpoint.value)" -ForegroundColor White
Write-Host ""

Write-Host "Application Insights:" -ForegroundColor Yellow
Write-Host "  Name: $($outputs.applicationInsightsName.value)" -ForegroundColor White
Write-Host "  Connection String: $($outputs.applicationInsightsConnectionString.value.Substring(0, 50))..." -ForegroundColor White
Write-Host ""

Write-Host "Key Vault:" -ForegroundColor Yellow
Write-Host "  Name: $($outputs.keyVaultName.value)" -ForegroundColor White
Write-Host "  URI: $($outputs.keyVaultUri.value)" -ForegroundColor White
Write-Host "  Encryption Key: $($outputs.encryptionKeyName.value)" -ForegroundColor White
Write-Host ""

# Save outputs to file
$outputFile = Join-Path $PSScriptRoot "deployment-outputs.$Environment.json"
$deployment.properties.outputs | ConvertTo-Json -Depth 10 | Out-File $outputFile -Encoding UTF8
Write-Success "Outputs saved to: $outputFile"
Write-Host ""

# Next steps
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  Next Steps                                                    ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "1. Update appsettings.$Environment.json with connection strings:" -ForegroundColor Cyan
Write-Host "   - AzureAppConfiguration:ConnectionString" -ForegroundColor White
Write-Host "   - ApplicationInsights:ConnectionString" -ForegroundColor White
Write-Host "   - AzureKeyVault:Url" -ForegroundColor White
Write-Host ""
Write-Host "2. Grant API managed identity access to Key Vault:" -ForegroundColor Cyan
Write-Host "   az role assignment create --role 'Key Vault Secrets User' \" -ForegroundColor White
Write-Host "     --assignee <API-MANAGED-IDENTITY-PRINCIPAL-ID> \" -ForegroundColor White
Write-Host "     --scope /subscriptions/<SUBSCRIPTION-ID>/resourceGroups/$ResourceGroupName/providers/Microsoft.KeyVault/vaults/$($outputs.keyVaultName.value)" -ForegroundColor White
Write-Host ""
Write-Host "3. Configure feature flags in App Configuration Portal" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Run gradual rollout script: .\gradual-rollout.ps1 -Environment $Environment" -ForegroundColor Cyan
Write-Host ""
