# Sample Test File for TDD Cycle Validation
# Purpose: PowerShell-based tests for validating TDD automation

param(
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# Sample test functions that would be created during RED phase
function Test-SampleButtonInitialization {
    param([object]$Button)
    
    if ($Button.Label -ne "Click Me") {
        throw "Button label should be 'Click Me', got '$($Button.Label)'"
    }
    
    Write-Host "  ✅ Button initialized with correct label" -ForegroundColor Green
    return $true
}

function Test-SampleButtonNotClickedInitially {
    param([object]$Button)
    
    if ($Button.IsClicked -eq $true) {
        throw "Button should not be clicked initially"
    }
    
    Write-Host "  ✅ Button not clicked initially" -ForegroundColor Green
    return $true
}

function Test-SampleButtonClickedAfterClick {
    param([object]$Button)
    
    $Button.Click()
    
    if ($Button.IsClicked -ne $true) {
        throw "Button should be clicked after Click() method called"
    }
    
    Write-Host "  ✅ Button clicked after Click() method" -ForegroundColor Green
    return $true
}

# Execution
if ($PSBoundParameters.ContainsKey('Verbose')) {
    Write-Host "`n🧪 Running Sample Button Tests" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
}

try {
    # In RED phase, these tests would fail because implementation doesn't exist
    # In GREEN phase, they would pass
    # In REFACTOR phase, they should still pass
    
    # For this fixture, we simulate the button object
    $button = @{
        Label = "Click Me"
        IsClicked = $false
    }
    
    # Add Click method
    $button | Add-Member -MemberType ScriptMethod -Name "Click" -Value {
        $this.IsClicked = $true
    }
    
    Test-SampleButtonInitialization -Button $button
    Test-SampleButtonNotClickedInitially -Button $button
    Test-SampleButtonClickedAfterClick -Button $button
    
    Write-Host "`n✅ All tests passed" -ForegroundColor Green
    return @{
        total = 3
        passed = 3
        failed = 0
        status = "success"
    }
    
} catch {
    Write-Host "`n❌ Tests failed: $($_.Exception.Message)" -ForegroundColor Red
    return @{
        total = 3
        passed = 0
        failed = 3
        status = "failed"
        error = $_.Exception.Message
    }
}
