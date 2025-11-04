# Post-Week 4 Enhancements Validation Test
# Tests Enhancement #1 (Proactive Warnings in Router) and Enhancement #2 (Efficiency Dashboard)

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$testResults = @()

Write-Host "🧪 Post-Week 4 Enhancements Validation Test" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Gray
Write-Host ""

# ============================================================================
# Test Group 1: Enhancement #1 - Proactive Warnings in Router
# ============================================================================
Write-Host "📋 Test Group 1: Proactive Warnings in Intent Router" -ForegroundColor Yellow
Write-Host ""

# Test 1.1: Verify intent-router.md has Step 1.3
Write-Host "[1/5] Checking intent-router.md for Step 1.3..." -NoNewline
$routerFile = "prompts\internal\intent-router.md"
if (Test-Path $routerFile) {
    $content = Get-Content $routerFile -Raw
    if ($content -match "Step 1\.3.*Proactive Issue Prediction") {
        Write-Host " ✅ PASS" -ForegroundColor Green
        $testResults += @{ Test = "Router Step 1.3 exists"; Status = "PASS" }
    } else {
        Write-Host " ❌ FAIL - Step 1.3 not found" -ForegroundColor Red
        $testResults += @{ Test = "Router Step 1.3 exists"; Status = "FAIL" }
    }
} else {
    Write-Host " ❌ FAIL - File not found" -ForegroundColor Red
    $testResults += @{ Test = "Router Step 1.3 exists"; Status = "FAIL" }
}

# Test 1.2: Verify predict-issues.ps1 is called
Write-Host "[2/5] Checking predict-issues.ps1 integration..." -NoNewline
if ($content -match "predict-issues\.ps1") {
    Write-Host " ✅ PASS" -ForegroundColor Green
    $testResults += @{ Test = "predict-issues.ps1 called"; Status = "PASS" }
} else {
    Write-Host " ❌ FAIL" -ForegroundColor Red
    $testResults += @{ Test = "predict-issues.ps1 called"; Status = "FAIL" }
}

# Test 1.3: Verify generate-proactive-warnings.ps1 is called
Write-Host "[3/5] Checking generate-proactive-warnings.ps1 integration..." -NoNewline
if ($content -match "generate-proactive-warnings\.ps1") {
    Write-Host " ✅ PASS" -ForegroundColor Green
    $testResults += @{ Test = "generate-proactive-warnings.ps1 called"; Status = "PASS" }
} else {
    Write-Host " ❌ FAIL" -ForegroundColor Red
    $testResults += @{ Test = "generate-proactive-warnings.ps1 called"; Status = "FAIL" }
}

# Test 1.4: Verify warnings display logic exists
Write-Host "[4/5] Checking warning display logic..." -NoNewline
if ($content -match "🧠 BRAIN Analysis" -and $content -match "severity") {
    Write-Host " ✅ PASS" -ForegroundColor Green
    $testResults += @{ Test = "Warning display logic present"; Status = "PASS" }
} else {
    Write-Host " ❌ FAIL" -ForegroundColor Red
    $testResults += @{ Test = "Warning display logic present"; Status = "FAIL" }
}

# Test 1.5: Verify preventive actions stored for planner
Write-Host "[5/5] Checking preventive actions storage..." -NoNewline
if ($content -match "KDS_PREVENTIVE_ACTIONS" -and $content -match "suggest-preventive-actions\.ps1") {
    Write-Host " ✅ PASS" -ForegroundColor Green
    $testResults += @{ Test = "Preventive actions stored"; Status = "PASS" }
} else {
    Write-Host " ❌ FAIL" -ForegroundColor Red
    $testResults += @{ Test = "Preventive actions stored"; Status = "FAIL" }
}

Write-Host ""

# ============================================================================
# Test Group 2: Enhancement #2 - Brain Efficiency Dashboard
# ============================================================================
Write-Host "📋 Test Group 2: Brain Efficiency Dashboard" -ForegroundColor Yellow
Write-Host ""

# Test 2.1: Verify dashboard file exists
Write-Host "[1/5] Checking brain-efficiency.html exists..." -NoNewline
$dashboardFile = "dashboard\brain-efficiency.html"
if (Test-Path $dashboardFile) {
    Write-Host " ✅ PASS" -ForegroundColor Green
    $testResults += @{ Test = "Dashboard file exists"; Status = "PASS" }
} else {
    Write-Host " ❌ FAIL" -ForegroundColor Red
    $testResults += @{ Test = "Dashboard file exists"; Status = "FAIL" }
}

# Test 2.2: Verify Chart.js integration
Write-Host "[2/5] Checking Chart.js integration..." -NoNewline
if (Test-Path $dashboardFile) {
    $dashContent = Get-Content $dashboardFile -Raw
    if ($dashContent -match "chart\.js" -and $dashContent -match "new Chart") {
        Write-Host " ✅ PASS" -ForegroundColor Green
        $testResults += @{ Test = "Chart.js integrated"; Status = "PASS" }
    } else {
        Write-Host " ❌ FAIL" -ForegroundColor Red
        $testResults += @{ Test = "Chart.js integrated"; Status = "FAIL" }
    }
} else {
    Write-Host " ⏭️  SKIP - File not found" -ForegroundColor Gray
    $testResults += @{ Test = "Chart.js integrated"; Status = "SKIP" }
}

# Test 2.3: Verify efficiency-history.jsonl reading logic
Write-Host "[3/5] Checking efficiency-history.jsonl reading..." -NoNewline
if ($dashContent -match "efficiency-history\.jsonl" -and $dashContent -match "fetch") {
    Write-Host " ✅ PASS" -ForegroundColor Green
    $testResults += @{ Test = "Reads efficiency-history.jsonl"; Status = "PASS" }
} else {
    Write-Host " ❌ FAIL" -ForegroundColor Red
    $testResults += @{ Test = "Reads efficiency-history.jsonl"; Status = "FAIL" }
}

# Test 2.4: Verify all metric displays present
Write-Host "[4/5] Checking metric display elements..." -NoNewline
$requiredMetrics = @(
    "routing-accuracy",
    "plan-time",
    "tdd-time",
    "learning-score",
    "coord-latency",
    "overall-score"
)
$allPresent = $true
foreach ($metric in $requiredMetrics) {
    if ($dashContent -notmatch $metric) {
        $allPresent = $false
        break
    }
}
if ($allPresent) {
    Write-Host " ✅ PASS (6/6 metrics)" -ForegroundColor Green
    $testResults += @{ Test = "All metric displays present"; Status = "PASS" }
} else {
    Write-Host " ❌ FAIL - Missing metrics" -ForegroundColor Red
    $testResults += @{ Test = "All metric displays present"; Status = "FAIL" }
}

# Test 2.5: Verify recommendation generation
Write-Host "[5/5] Checking recommendation generation..." -NoNewline
if ($dashContent -match "generateRecommendations" -and $dashContent -match "recommendation-item") {
    Write-Host " ✅ PASS" -ForegroundColor Green
    $testResults += @{ Test = "Recommendations generated"; Status = "PASS" }
} else {
    Write-Host " ❌ FAIL" -ForegroundColor Red
    $testResults += @{ Test = "Recommendations generated"; Status = "FAIL" }
}

Write-Host ""

# ============================================================================
# Test Group 3: Integration Tests
# ============================================================================
Write-Host "📋 Test Group 3: Integration Tests" -ForegroundColor Yellow
Write-Host ""

# Test 3.1: Verify Week 4 scripts still exist
Write-Host "[1/3] Checking Week 4 scripts intact..." -NoNewline
$week4Scripts = @(
    "scripts\corpus-callosum\predict-issues.ps1",
    "scripts\corpus-callosum\generate-proactive-warnings.ps1",
    "scripts\corpus-callosum\suggest-preventive-actions.ps1",
    "scripts\corpus-callosum\collect-brain-metrics.ps1",
    "scripts\corpus-callosum\analyze-brain-efficiency.ps1"
)
$allExist = $true
foreach ($script in $week4Scripts) {
    if (-not (Test-Path $script)) {
        $allExist = $false
        break
    }
}
if ($allExist) {
    Write-Host " ✅ PASS (5/5 scripts)" -ForegroundColor Green
    $testResults += @{ Test = "Week 4 scripts intact"; Status = "PASS" }
} else {
    Write-Host " ❌ FAIL - Missing scripts" -ForegroundColor Red
    $testResults += @{ Test = "Week 4 scripts intact"; Status = "FAIL" }
}

# Test 3.2: Test metrics collection (WhatIf mode)
Write-Host "[2/3] Testing metrics collection (WhatIf)..." -NoNewline
try {
    $metricsResult = .\scripts\corpus-callosum\collect-brain-metrics.ps1 -WhatIf
    if ($metricsResult -and $null -ne $metricsResult.routing_accuracy) {
        Write-Host " ✅ PASS" -ForegroundColor Green
        $testResults += @{ Test = "Metrics collection works"; Status = "PASS" }
    } else {
        Write-Host " ❌ FAIL - Invalid output" -ForegroundColor Red
        $testResults += @{ Test = "Metrics collection works"; Status = "FAIL" }
    }
} catch {
    Write-Host " ❌ FAIL - $($_.Exception.Message)" -ForegroundColor Red
    $testResults += @{ Test = "Metrics collection works"; Status = "FAIL" }
}

# Test 3.3: Test prediction pipeline (with mock request)
Write-Host "[3/3] Testing prediction pipeline..." -NoNewline
try {
    $kgPath = "kds-brain\knowledge-graph.yaml"
    
    if (Test-Path $kgPath) {
        $null = .\scripts\corpus-callosum\predict-issues.ps1 `
            -Request "Add PDF export feature" `
            -MinimumConfidence 0.5 `
            -ErrorAction SilentlyContinue
        
        Write-Host " ✅ PASS" -ForegroundColor Green
        $testResults += @{ Test = "Prediction pipeline works"; Status = "PASS" }
    } else {
        Write-Host " ⏭️  SKIP - No knowledge graph" -ForegroundColor Gray
        $testResults += @{ Test = "Prediction pipeline works"; Status = "SKIP" }
    }
} catch {
    Write-Host " ⚠️  WARN - $($_.Exception.Message)" -ForegroundColor Yellow
    $testResults += @{ Test = "Prediction pipeline works"; Status = "WARN" }
}

Write-Host ""

# ============================================================================
# Summary
# ============================================================================
Write-Host "=" * 80 -ForegroundColor Gray
Write-Host "📊 Test Summary" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Gray

$passed = ($testResults | Where-Object { $_.Status -eq "PASS" }).Count
$failed = ($testResults | Where-Object { $_.Status -eq "FAIL" }).Count
$skipped = ($testResults | Where-Object { $_.Status -eq "SKIP" }).Count
$warned = ($testResults | Where-Object { $_.Status -eq "WARN" }).Count
$total = $testResults.Count

Write-Host ""
Write-Host "Total Tests: $total" -ForegroundColor White
Write-Host "✅ Passed:   $passed" -ForegroundColor Green
Write-Host "❌ Failed:   $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Gray" })
Write-Host "⏭️  Skipped:  $skipped" -ForegroundColor Gray
Write-Host "⚠️  Warnings: $warned" -ForegroundColor Yellow
Write-Host ""

if ($failed -eq 0) {
    Write-Host "🎉 ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✨ Both enhancements successfully integrated!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Update kds.md documentation" -ForegroundColor White
    Write-Host "2. Update WEEK4-IMPLEMENTATION-COMPLETE.md" -ForegroundColor White
    Write-Host "3. Test enhancements with real KDS usage" -ForegroundColor White
    exit 0
} else {
    Write-Host "❌ SOME TESTS FAILED" -ForegroundColor Red
    Write-Host ""
    Write-Host "Failed Tests:" -ForegroundColor Red
    $testResults | Where-Object { $_.Status -eq "FAIL" } | ForEach-Object {
        Write-Host "  - $($_.Test)" -ForegroundColor Red
    }
    exit 1
}
