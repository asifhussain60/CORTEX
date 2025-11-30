# Workflow Template Validator Script
# Purpose: Validate workflow template structure
# Part of: Right Brain Pattern Recognition (Week 3)

param(
    [Parameter(Mandatory=$true)]
    [string]$TemplateFile,
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Validate required fields
function Test-RequiredFields {
    param([string]$Content)
    
    $requiredFields = @(
        "template_id",
        "pattern_id",
        "workflow_name",
        "tdd_required",
        "phases"
    )
    
    foreach ($field in $requiredFields) {
        if ($Content -notmatch "$field\s*:") {
            return $false
        }
    }
    
    return $true
}

# Check TDD compliance
function Test-TDDCompliance {
    param([string]$Content)
    
    $hasTDDPhases = $Content -match "tdd_phase.*RED" -and
                    $Content -match "tdd_phase.*GREEN" -and
                    $Content -match "tdd_phase.*REFACTOR"
    
    $isTDDRequired = $Content -match "tdd_required:\s*true"
    
    return $isTDDRequired -and $hasTDDPhases
}

# In DryRun mode, simulate validation
if ($DryRun) {
    if ($env:KDS_VERBOSE) {
        Write-Host "`n✅ Validating Workflow Template (DRY RUN)" -ForegroundColor Cyan
        Write-Host "  Template File: $TemplateFile" -ForegroundColor Yellow
    }
    
    return @{
        validation_passed = $true
        tdd_compliant = $true
        has_required_fields = $true
        dry_run = $true
    }
}

# Real execution: Validate template
try {
    Write-Host "`n✅ Validating workflow template: $TemplateFile" -ForegroundColor Cyan
    
    if (-not (Test-Path $TemplateFile)) {
        throw "Template file not found: $TemplateFile"
    }
    
    $content = Get-Content $TemplateFile -Raw
    
    # Check required fields
    $hasRequiredFields = Test-RequiredFields -Content $content
    Write-Host "  Required Fields: $(if ($hasRequiredFields) { '✅' } else { '❌' })" -ForegroundColor $(if ($hasRequiredFields) { "Green" } else { "Red" })
    
    # Check TDD compliance
    $isTDDCompliant = Test-TDDCompliance -Content $content
    Write-Host "  TDD Compliance: $(if ($isTDDCompliant) { '✅' } else { '❌' })" -ForegroundColor $(if ($isTDDCompliant) { "Green" } else { "Red" })
    
    $validationPassed = $hasRequiredFields -and $isTDDCompliant
    
    if ($validationPassed) {
        Write-Host "`n  ✅ Template validation PASSED" -ForegroundColor Green
    } else {
        Write-Host "`n  ❌ Template validation FAILED" -ForegroundColor Red
    }
    
    return @{
        validation_passed = $validationPassed
        tdd_compliant = $isTDDCompliant
        has_required_fields = $hasRequiredFields
        template_file = $TemplateFile
    }
    
} catch {
    Write-Host "  ❌ Validation error: $($_.Exception.Message)" -ForegroundColor Red
    
    return @{
        validation_passed = $false
        tdd_compliant = $false
        has_required_fields = $false
        error = $_.Exception.Message
    }
}
