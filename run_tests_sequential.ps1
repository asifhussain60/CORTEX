# Sequential Test Runner for CORTEX (PowerShell)
# Runs each test file one at a time with immediate output display

param(
    [string]$TestDir = "tests",
    [string]$Pattern = "test_*.py",
    [switch]$StopOnFailure
)

$ErrorActionPreference = "Continue"

Write-Host "`n🧠 CORTEX Sequential Test Runner" -ForegroundColor Cyan
Write-Host ("="*80) -ForegroundColor Gray

# Find all test files
$testFiles = Get-ChildItem -Path $TestDir -Recurse -Filter $Pattern | Sort-Object FullName
$totalTests = $testFiles.Count

if ($totalTests -eq 0) {
    Write-Host "❌ No test files found in '$TestDir'" -ForegroundColor Red
    exit 1
}

Write-Host "Found $totalTests test files" -ForegroundColor Green
Write-Host "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ("="*80) -ForegroundColor Gray
Write-Host ""

# Track results
$results = @()
$passed = 0
$failed = 0
$startTime = Get-Date

# Run each test file
$index = 1
foreach ($testFile in $testFiles) {
    $relativePath = $testFile.FullName.Replace("$PWD\", "")
    
    Write-Host "`n$("="*80)" -ForegroundColor Gray
    Write-Host "TEST $index/$totalTests`: $relativePath" -ForegroundColor Cyan
    Write-Host ("="*80) -ForegroundColor Gray
    Write-Host "Started: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
    Write-Host ("-"*80) -ForegroundColor Gray
    Write-Host ""
    
    $testStartTime = Get-Date
    
    # Run pytest on single file WITHOUT coverage (much faster)
    $process = Start-Process -FilePath "python" `
        -ArgumentList "-m", "pytest", $testFile.FullName, "-v", "--tb=short", "--no-cov", "-m", "not slow", "--color=yes" `
        -NoNewWindow -Wait -PassThru
    
    $testEndTime = Get-Date
    $duration = ($testEndTime - $testStartTime).TotalSeconds
    
    Write-Host "`n$("-"*80)" -ForegroundColor Gray
    Write-Host "Completed: $(Get-Date -Format 'HH:mm:ss') | Duration: $($duration.ToString('F2'))s" -ForegroundColor Gray
    
    if ($process.ExitCode -eq 0) {
        Write-Host "✅ PASSED" -ForegroundColor Green
        $passed++
        $testPassed = $true
    } else {
        Write-Host "❌ FAILED (Exit Code: $($process.ExitCode))" -ForegroundColor Red
        $failed++
        $testPassed = $false
    }
    
    Write-Host ("="*80) -ForegroundColor Gray
    
    $results += [PSCustomObject]@{
        File = $relativePath
        Passed = $testPassed
        Duration = $duration
        ExitCode = $process.ExitCode
    }
    
    $index++
    
    # Stop on first failure if requested
    if ($StopOnFailure -and -not $testPassed) {
        Write-Host "`n⚠️  Stopping on first failure" -ForegroundColor Yellow
        break
    }
}

$endTime = Get-Date
$totalDuration = ($endTime - $startTime).TotalSeconds

# Summary Report
Write-Host "`n$("="*80)" -ForegroundColor Gray
Write-Host "📊 SUMMARY REPORT" -ForegroundColor Cyan
Write-Host ("="*80) -ForegroundColor Gray
Write-Host ""
Write-Host "Total Tests: $totalTests" -ForegroundColor White
Write-Host "✅ Passed: $passed" -ForegroundColor Green
Write-Host "❌ Failed: $failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Red" })
Write-Host "⏱️  Total Duration: $($totalDuration.ToString('F2'))s" -ForegroundColor Gray
Write-Host "📅 Completed: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

if ($failed -gt 0) {
    Write-Host "`n❌ Failed Tests:" -ForegroundColor Red
    $results | Where-Object { -not $_.Passed } | ForEach-Object {
        Write-Host "  - $($_.File) (exit code: $($_.ExitCode))" -ForegroundColor Red
    }
}

Write-Host "`n$("="*80)" -ForegroundColor Gray

# Save results to JSON
$resultsData = @{
    timestamp = $endTime.ToString("o")
    total_duration = $totalDuration
    total_tests = $totalTests
    passed = $passed
    failed = $failed
    results = $results
} | ConvertTo-Json -Depth 5

$resultsFile = "test_results_sequential.json"
$resultsData | Out-File -FilePath $resultsFile -Encoding UTF8

Write-Host "📄 Detailed results saved to: $resultsFile" -ForegroundColor Gray
Write-Host ""

# Exit with appropriate code
exit $(if ($failed -eq 0) { 0 } else { 1 })
