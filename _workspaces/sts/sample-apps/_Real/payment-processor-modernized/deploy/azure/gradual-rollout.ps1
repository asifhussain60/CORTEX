# Gradual Rollout Orchestration Script for PaymentProcessor Transaction Invoices
# Automates 5-week traffic rollout: 0% → 10% → 25% → 50% → 75% → 100%

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('dev', 'staging', 'prod')]
    [string]$Environment,
    
    [Parameter(Mandatory=$true)]
    [ValidateSet(0, 10, 25, 50, 75, 100)]
    [int]$TargetPercentage,
    
    [Parameter(Mandatory=$false)]
    [int]$MonitoringDurationMinutes = 30,
    
    [Parameter(Mandatory=$false)]
    [switch]$AutoRollbackOnFailure,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipConfirmation
)

$ErrorActionPreference = 'Stop'

# Configuration
$appConfigName = "ra-transaction-invoices-config-$Environment"
$appInsightsName = "ra-transaction-invoices-insights-$Environment"
$featureFlagName = "DataLayerRollout"

# Rollback thresholds (from Phase 6 configuration)
$thresholds = @{
    ErrorRatePercent = 0.1
    LatencyMs = 200
    SuccessRatePercent = 99.9
}

# Colors
function Write-Success { param([string]$Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Info { param([string]$Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param([string]$Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Critical { param([string]$Message) Write-Host "🚨 $Message" -ForegroundColor Red -BackgroundColor Yellow }

# Banner
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║  PaymentProcessor Transaction Invoices - Gradual Rollout Orchestration           ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

Write-Info "Environment: $Environment"
Write-Info "Target Percentage: $TargetPercentage%"
Write-Info "Monitoring Duration: $MonitoringDurationMinutes minutes"
Write-Info "Auto-Rollback: $AutoRollbackOnFailure"
Write-Host ""

# Get current feature flag state
Write-Info "Checking current feature flag state..."
$currentState = az appconfig feature show `
    --name $appConfigName `
    --feature $featureFlagName `
    --output json 2>$null | ConvertFrom-Json

if (-not $currentState) {
    Write-Error "Feature flag '$featureFlagName' not found in App Configuration '$appConfigName'"
    exit 1
}

$currentPercentage = 0
if ($currentState.conditions.client_filters) {
    $percentageFilter = $currentState.conditions.client_filters | Where-Object { $_.name -eq 'Microsoft.Percentage' }
    if ($percentageFilter) {
        $currentPercentage = [int]$percentageFilter.parameters.Value
    }
}

Write-Success "Current traffic percentage: $currentPercentage%"
Write-Host ""

# Validate rollout direction (must be increasing)
if ($TargetPercentage -le $currentPercentage) {
    Write-Warning "Target percentage ($TargetPercentage%) is not greater than current ($currentPercentage%)."
    Write-Info "For rollback, use emergency rollback script: .\emergency-rollback.ps1"
    exit 0
}

# Confirmation
if (-not $SkipConfirmation) {
    Write-Warning "This will increase EF Core traffic from $currentPercentage% to $TargetPercentage%"
    $confirmation = Read-Host "Continue? (yes/no)"
    if ($confirmation -ne 'yes') {
        Write-Info "Rollout cancelled by user."
        exit 0
    }
}
Write-Host ""

# Update feature flag
Write-Info "Updating feature flag to $TargetPercentage%..."
az appconfig feature set `
    --name $appConfigName `
    --feature $featureFlagName `
    --yes `
    --output none `
    --query 'name' `
    -- `
    --label $null `
    --description "EF Core traffic rollout - automated update to $TargetPercentage%" `
    --conditions '{\"client_filters\":[{\"name\":\"Microsoft.Percentage\",\"parameters\":{\"Value\":' + $TargetPercentage + '}}]}'

if ($LASTEXITCODE -eq 0) {
    Write-Success "Feature flag updated to $TargetPercentage%"
} else {
    Write-Error "Failed to update feature flag. Check Azure CLI output."
    exit 1
}
Write-Host ""

# Wait for propagation (App Configuration cache is 30 seconds)
Write-Info "Waiting 60 seconds for feature flag propagation..."
Start-Sleep -Seconds 60
Write-Success "Feature flag propagated"
Write-Host ""

# Monitor metrics
Write-Info "Monitoring metrics for $MonitoringDurationMinutes minutes..."
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray

$monitoringEnd = (Get-Date).AddMinutes($MonitoringDurationMinutes)
$checkIntervalSeconds = 60
$checksPerformed = 0
$rollbackTriggered = $false

while ((Get-Date) -lt $monitoringEnd -and -not $rollbackTriggered) {
    $checksPerformed++
    $timeRemaining = ($monitoringEnd - (Get-Date)).TotalMinutes
    
    Write-Host ""
    Write-Info "Check #$checksPerformed ($('{0:N1}' -f $timeRemaining) minutes remaining)"
    
    # Query Application Insights for metrics (last 5 minutes)
    $query = @"
requests
| where timestamp > ago(5m)
| where cloud_RoleName == 'ra-transaction-invoices-api'
| summarize 
    TotalRequests = count(),
    SuccessfulRequests = countif(success == true),
    FailedRequests = countif(success == false),
    AvgDuration = avg(duration),
    P95Duration = percentile(duration, 95)
| extend 
    ErrorRatePercent = (FailedRequests * 100.0) / TotalRequests,
    SuccessRatePercent = (SuccessfulRequests * 100.0) / TotalRequests
"@

    try {
        $metrics = az monitor app-insights query `
            --app $appInsightsName `
            --analytics-query $query `
            --output json | ConvertFrom-Json
        
        if ($metrics.tables -and $metrics.tables[0].rows.Count -gt 0) {
            $row = $metrics.tables[0].rows[0]
            $totalRequests = $row[0]
            $successRequests = $row[1]
            $failedRequests = $row[2]
            $avgDuration = [math]::Round($row[3], 2)
            $p95Duration = [math]::Round($row[4], 2)
            $errorRate = [math]::Round($row[5], 2)
            $successRate = [math]::Round($row[6], 2)
            
            # Display metrics
            Write-Host "  Total Requests: $totalRequests" -ForegroundColor White
            Write-Host "  Success Rate: $successRate% (threshold: >$($thresholds.SuccessRatePercent)%)" -ForegroundColor $(if ($successRate -ge $thresholds.SuccessRatePercent) { 'Green' } else { 'Red' })
            Write-Host "  Error Rate: $errorRate% (threshold: <$($thresholds.ErrorRatePercent)%)" -ForegroundColor $(if ($errorRate -le $thresholds.ErrorRatePercent) { 'Green' } else { 'Red' })
            Write-Host "  Avg Latency: $avgDuration ms (threshold: <$($thresholds.LatencyMs)ms)" -ForegroundColor $(if ($avgDuration -le $thresholds.LatencyMs) { 'Green' } else { 'Red' })
            Write-Host "  P95 Latency: $p95Duration ms" -ForegroundColor White
            
            # Check thresholds
            $violations = @()
            if ($errorRate -gt $thresholds.ErrorRatePercent) {
                $violations += "Error rate ($errorRate%) exceeds threshold ($($thresholds.ErrorRatePercent)%)"
            }
            if ($avgDuration -gt $thresholds.LatencyMs) {
                $violations += "Latency ($avgDuration ms) exceeds threshold ($($thresholds.LatencyMs)ms)"
            }
            if ($successRate -lt $thresholds.SuccessRatePercent) {
                $violations += "Success rate ($successRate%) below threshold ($($thresholds.SuccessRatePercent)%)"
            }
            
            if ($violations.Count -gt 0) {
                Write-Host ""
                Write-Critical "THRESHOLD VIOLATIONS DETECTED!"
                foreach ($violation in $violations) {
                    Write-Error "  - $violation"
                }
                
                if ($AutoRollbackOnFailure) {
                    Write-Critical "AUTO-ROLLBACK TRIGGERED"
                    $rollbackTriggered = $true
                } else {
                    Write-Warning "Auto-rollback disabled. Manual intervention required."
                    $response = Read-Host "Trigger emergency rollback? (yes/no)"
                    if ($response -eq 'yes') {
                        $rollbackTriggered = $true
                    }
                }
            } else {
                Write-Success "  All metrics within healthy thresholds ✓"
            }
        } else {
            Write-Warning "  No metrics data available (API may not be receiving traffic)"
        }
    } catch {
        Write-Warning "  Failed to query Application Insights: $_"
    }
    
    if (-not $rollbackTriggered -and (Get-Date) -lt $monitoringEnd) {
        Write-Host ""
        Write-Info "Next check in $checkIntervalSeconds seconds..."
        Start-Sleep -Seconds $checkIntervalSeconds
    }
}

Write-Host ""
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host ""

# Handle rollback if triggered
if ($rollbackTriggered) {
    Write-Critical "EXECUTING EMERGENCY ROLLBACK TO 0%"
    Write-Host ""
    
    # Rollback feature flag
    az appconfig feature set `
        --name $appConfigName `
        --feature $featureFlagName `
        --yes `
        --output none `
        --query 'name' `
        -- `
        --label $null `
        --description "EMERGENCY ROLLBACK - metrics threshold violations" `
        --conditions '{\"client_filters\":[{\"name\":\"Microsoft.Percentage\",\"parameters\":{\"Value\":0}}]}'
    
    Write-Success "Feature flag rolled back to 0%"
    Write-Host ""
    Write-Critical "ROLLBACK COMPLETE - ALL TPaymentProcessorFFIC ROUTED TO MOCK DATA LAYER"
    Write-Host ""
    Write-Info "Next steps:"
    Write-Host "  1. Investigate root cause in Application Insights" -ForegroundColor White
    Write-Host "  2. Review error logs and traces" -ForegroundColor White
    Write-Host "  3. Fix underlying issues" -ForegroundColor White
    Write-Host "  4. Re-run rollout after validation" -ForegroundColor White
    Write-Host ""
    
    exit 1
}

# Success
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  Rollout Complete - Metrics Healthy                           ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Success "EF Core traffic successfully increased to $TargetPercentage%"
Write-Success "All metrics within healthy thresholds"
Write-Success "$checksPerformed monitoring checks performed"
Write-Host ""

# Next steps
$nextPercentages = @(10, 25, 50, 75, 100)
$nextPercentage = $nextPercentages | Where-Object { $_ -gt $TargetPercentage } | Select-Object -First 1

if ($nextPercentage) {
    Write-Info "Next rollout step:"
    Write-Host "  .\gradual-rollout.ps1 -Environment $Environment -TargetPercentage $nextPercentage -AutoRollbackOnFailure" -ForegroundColor Cyan
    Write-Host ""
    Write-Info "Recommended wait time before next rollout: 1 week"
} else {
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║  🎉 MIGPaymentProcessorTION COMPLETE - 100% EF CORE TPaymentProcessorFFIC                  ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
    Write-Success "Full migration to EF Core data layer complete!"
    Write-Info "Next steps:"
    Write-Host "  1. Continue monitoring for 1 week" -ForegroundColor White
    Write-Host "  2. Archive Mock data layer code" -ForegroundColor White
    Write-Host "  3. Update documentation" -ForegroundColor White
    Write-Host "  4. Generate completion report" -ForegroundColor White
}
Write-Host ""
