# Emergency Rollback Script for PaymentProcessor Transaction Invoices
# Immediately sets feature flag to 0% (100% Mock traffic)

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('dev', 'staging', 'prod')]
    [string]$Environment,
    
    [Parameter(Mandatory=$true)]
    [string]$Reason,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipConfirmation
)

$ErrorActionPreference = 'Stop'

# Configuration
$appConfigName = "ra-transaction-invoices-config-$Environment"
$featureFlagName = "DataLayerRollout"

# Colors
function Write-Success { param([string]$Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param([string]$Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Critical { param([string]$Message) Write-Host "🚨 $Message" -ForegroundColor Red -BackgroundColor Yellow }

# Banner
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Red
Write-Host "║  🚨 EMERGENCY ROLLBACK - PaymentProcessor TPaymentProcessorNSACTION INVOICES                   ║" -ForegroundColor Red
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Red
Write-Host ""

Write-Critical "Environment: $Environment"
Write-Critical "Reason: $Reason"
Write-Host ""

# Confirmation
if (-not $SkipConfirmation) {
    Write-Critical "This will IMMEDIATELY route 100% of traffic to Mock data layer"
    $confirmation = Read-Host "Continue with emergency rollback? (yes/no)"
    if ($confirmation -ne 'yes') {
        Write-Info "Rollback cancelled by user."
        exit 0
    }
}
Write-Host ""

# Execute rollback
Write-Critical "EXECUTING EMERGENCY ROLLBACK..."

az appconfig feature set `
    --name $appConfigName `
    --feature $featureFlagName `
    --yes `
    --output none `
    -- `
    --description "EMERGENCY ROLLBACK: $Reason" `
    --conditions '{\"client_filters\":[{\"name\":\"Microsoft.Percentage\",\"parameters\":{\"Value\":0}}]}'

if ($LASTEXITCODE -eq 0) {
    Write-Success "Feature flag rolled back to 0%"
} else {
    Write-Critical "ROLLBACK FAILED - MANUAL INTERVENTION REQUIRED"
    Write-Host ""
    Write-Info "Manual rollback via Azure Portal:"
    Write-Host "  1. Navigate to Azure App Configuration: $appConfigName" -ForegroundColor White
    Write-Host "  2. Open Feature Manager" -ForegroundColor White
    Write-Host "  3. Find feature: $featureFlagName" -ForegroundColor White
    Write-Host "  4. Set percentage to 0% or disable feature" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ROLLBACK COMPLETE                                             ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Success "100% of traffic now routed to Mock data layer"
Write-Success "System operating in safe mode"
Write-Host ""

# Log incident
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$logEntry = @"
[$timestamp] EMERGENCY ROLLBACK - $Environment
Reason: $Reason
Action: Feature flag '$featureFlagName' set to 0%
Status: SUCCESS
"@

$logFile = Join-Path $PSScriptRoot "rollback-incidents.log"
Add-Content -Path $logFile -Value $logEntry
Write-Info "Incident logged to: $logFile"
Write-Host ""

# Next steps
Write-Info "Next steps:"
Write-Host "  1. Investigate root cause in Application Insights" -ForegroundColor White
Write-Host "  2. Review error logs and exception traces" -ForegroundColor White
Write-Host "  3. Identify and fix underlying issues" -ForegroundColor White
Write-Host "  4. Test fixes in dev/staging environments" -ForegroundColor White
Write-Host "  5. Schedule re-deployment after validation" -ForegroundColor White
Write-Host ""
