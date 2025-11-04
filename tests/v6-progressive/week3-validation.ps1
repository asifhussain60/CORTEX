# KDS v6.0 Week 3 Validation Test Suite
# Purpose: Validate Right Brain Pattern Matching & Recognition
#
# Tests MUST fail until Week 3 implementation is complete
# These tests define the acceptance criteria for Week 3

$ErrorActionPreference = "Stop"
$script:TestsRun = 0
$script:TestsPassed = 0
$script:TestsFailed = 0

function Test-Assert {
    param(
        [string]$TestName,
        [bool]$Condition,
        [string]$ErrorMessage = "Test failed"
    )
    
    $script:TestsRun++
    
    if ($Condition) {
        Write-Host "  ✅ $TestName" -ForegroundColor Green
        $script:TestsPassed++
    } else {
        Write-Host "  ❌ $TestName - $ErrorMessage" -ForegroundColor Red
        $script:TestsFailed++
    }
}

Write-Host "`n🧪 KDS v6.0 Week 3 Validation Test Suite" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Testing: Right Brain Pattern Matching & Recognition" -ForegroundColor Yellow
Write-Host ""

$workspaceRoot = "D:\PROJECTS\KDS"

# ============================================================================
# TEST GROUP 1: Pattern Library Infrastructure (7 tests)
# ============================================================================
Write-Host "`n📚 Test Group 1: Pattern Library Infrastructure (7 tests)" -ForegroundColor Cyan

Test-Assert `
    -TestName "Week 3 validation test suite exists" `
    -Condition (Test-Path "$workspaceRoot\tests\v6-progressive\week3-validation.ps1") `
    -ErrorMessage "This file should exist"

Test-Assert `
    -TestName "Pattern library directory exists" `
    -Condition (Test-Path "$workspaceRoot\kds-brain\right-hemisphere\patterns") `
    -ErrorMessage "Pattern library directory missing"

Test-Assert `
    -TestName "Pattern schema exists" `
    -Condition (Test-Path "$workspaceRoot\kds-brain\right-hemisphere\schemas\pattern.schema.json") `
    -ErrorMessage "Pattern schema missing"

Test-Assert `
    -TestName "Workflow template directory exists" `
    -Condition (Test-Path "$workspaceRoot\kds-brain\right-hemisphere\workflow-templates") `
    -ErrorMessage "Workflow template directory missing"

Test-Assert `
    -TestName "Pattern fixtures exist for testing" `
    -Condition (Test-Path "$workspaceRoot\tests\fixtures\patterns\sample-export-pattern.yaml") `
    -ErrorMessage "Sample pattern fixture missing"

# Validate pattern schema structure
if (Test-Path "$workspaceRoot\kds-brain\right-hemisphere\schemas\pattern.schema.json") {
    $schema = Get-Content "$workspaceRoot\kds-brain\right-hemisphere\schemas\pattern.schema.json" -Raw | ConvertFrom-Json
    
    Test-Assert `
        -TestName "Pattern schema defines required fields" `
        -Condition ($schema.required -contains "pattern_id" -and $schema.required -contains "similarity_threshold") `
        -ErrorMessage "Schema must define pattern_id and similarity_threshold"
    
    Test-Assert `
        -TestName "Pattern schema includes feature_components array" `
        -Condition ($schema.properties.PSObject.Properties.Name -contains "feature_components") `
        -ErrorMessage "Schema must define feature_components"
} else {
    Test-Assert -TestName "Pattern schema defines required fields" -Condition $false -ErrorMessage "Schema file missing"
    Test-Assert -TestName "Pattern schema includes feature_components array" -Condition $false -ErrorMessage "Schema file missing"
}

# ============================================================================
# TEST GROUP 2: Pattern Matching Scripts (8 tests)
# ============================================================================
Write-Host "`n🔍 Test Group 2: Pattern Matching Scripts (8 tests)" -ForegroundColor Cyan

Test-Assert `
    -TestName "Pattern matcher script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\right-brain\match-pattern.ps1") `
    -ErrorMessage "match-pattern.ps1 missing"

Test-Assert `
    -TestName "Pattern creator script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\right-brain\create-pattern.ps1") `
    -ErrorMessage "create-pattern.ps1 missing"

Test-Assert `
    -TestName "Similarity analyzer script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\right-brain\analyze-similarity.ps1") `
    -ErrorMessage "analyze-similarity.ps1 missing"

# Test pattern matching functionality (if scripts exist)
if ((Test-Path "$workspaceRoot\scripts\right-brain\match-pattern.ps1") -and
    (Test-Path "$workspaceRoot\tests\fixtures\patterns\sample-export-pattern.yaml")) {
    
    try {
        $matchResult = & "$workspaceRoot\scripts\right-brain\match-pattern.ps1" `
            -Query "I want to add invoice export" `
            -DryRun 2>$null
        
        Test-Assert `
            -TestName "Pattern matcher can find similar patterns" `
            -Condition ($matchResult.matches_found -eq $true) `
            -ErrorMessage "Pattern matcher should find matches"
        
        Test-Assert `
            -TestName "Pattern matcher returns similarity score" `
            -Condition ($matchResult.similarity_score -is [double] -and $matchResult.similarity_score -ge 0 -and $matchResult.similarity_score -le 1) `
            -ErrorMessage "Should return similarity score 0.0-1.0"
        
        Test-Assert `
            -TestName "Pattern matcher suggests workflow template" `
            -Condition ($null -ne $matchResult.workflow_template) `
            -ErrorMessage "Should suggest workflow template"
        
    } catch {
        Test-Assert -TestName "Pattern matcher can find similar patterns" -Condition $false -ErrorMessage $_.Exception.Message
        Test-Assert -TestName "Pattern matcher returns similarity score" -Condition $false -ErrorMessage "Script execution failed"
        Test-Assert -TestName "Pattern matcher suggests workflow template" -Condition $false -ErrorMessage "Script execution failed"
    }
} else {
    Test-Assert -TestName "Pattern matcher can find similar patterns" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Pattern matcher returns similarity score" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Pattern matcher suggests workflow template" -Condition $false -ErrorMessage "Prerequisites missing"
}

# Test similarity analyzer
if (Test-Path "$workspaceRoot\scripts\right-brain\analyze-similarity.ps1") {
    try {
        $similarityResult = & "$workspaceRoot\scripts\right-brain\analyze-similarity.ps1" `
            -Query1 "add invoice export" `
            -Query2 "add PDF export" `
            -DryRun 2>$null
        
        Test-Assert `
            -TestName "Similarity analyzer calculates semantic similarity" `
            -Condition ($similarityResult.semantic_similarity -is [double]) `
            -ErrorMessage "Should calculate semantic similarity"
        
        Test-Assert `
            -TestName "Similarity analyzer identifies common components" `
            -Condition ($similarityResult.common_components.Count -gt 0) `
            -ErrorMessage "Should identify common components"
        
    } catch {
        Test-Assert -TestName "Similarity analyzer calculates semantic similarity" -Condition $false -ErrorMessage $_.Exception.Message
        Test-Assert -TestName "Similarity analyzer identifies common components" -Condition $false -ErrorMessage "Script execution failed"
    }
} else {
    Test-Assert -TestName "Similarity analyzer calculates semantic similarity" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Similarity analyzer identifies common components" -Condition $false -ErrorMessage "Prerequisites missing"
}

# ============================================================================
# TEST GROUP 3: Workflow Template Generation (7 tests)
# ============================================================================
Write-Host "`n📋 Test Group 3: Workflow Template Generation (7 tests)" -ForegroundColor Cyan

Test-Assert `
    -TestName "Template generator script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\right-brain\generate-workflow-template.ps1") `
    -ErrorMessage "generate-workflow-template.ps1 missing"

Test-Assert `
    -TestName "Template validator script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\right-brain\validate-workflow-template.ps1") `
    -ErrorMessage "validate-workflow-template.ps1 missing"

# Test workflow template generation
if (Test-Path "$workspaceRoot\scripts\right-brain\generate-workflow-template.ps1") {
    try {
        $templateResult = & "$workspaceRoot\scripts\right-brain\generate-workflow-template.ps1" `
            -PatternId "export_feature" `
            -DryRun 2>$null
        
        Test-Assert `
            -TestName "Template generator creates workflow phases" `
            -Condition ($templateResult.phases.Count -gt 0) `
            -ErrorMessage "Should create workflow phases"
        
        Test-Assert `
            -TestName "Template includes TDD instructions" `
            -Condition ($templateResult.includes_tdd -eq $true) `
            -ErrorMessage "Template should include TDD workflow"
        
        Test-Assert `
            -TestName "Template includes risk assessment" `
            -Condition ($templateResult.includes_risk_assessment -eq $true) `
            -ErrorMessage "Template should include risk assessment"
        
        Test-Assert `
            -TestName "Template includes architectural guidance" `
            -Condition ($templateResult.includes_architectural_guidance -eq $true) `
            -ErrorMessage "Template should include architectural guidance"
        
    } catch {
        Test-Assert -TestName "Template generator creates workflow phases" -Condition $false -ErrorMessage $_.Exception.Message
        Test-Assert -TestName "Template includes TDD instructions" -Condition $false -ErrorMessage "Script execution failed"
        Test-Assert -TestName "Template includes risk assessment" -Condition $false -ErrorMessage "Script execution failed"
        Test-Assert -TestName "Template includes architectural guidance" -Condition $false -ErrorMessage "Script execution failed"
    }
} else {
    Test-Assert -TestName "Template generator creates workflow phases" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Template includes TDD instructions" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Template includes risk assessment" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Template includes architectural guidance" -Condition $false -ErrorMessage "Prerequisites missing"
}

# Test template validator
if ((Test-Path "$workspaceRoot\scripts\right-brain\validate-workflow-template.ps1") -and
    (Test-Path "$workspaceRoot\tests\fixtures\patterns\sample-workflow-template.yaml")) {
    
    try {
        $validationResult = & "$workspaceRoot\scripts\right-brain\validate-workflow-template.ps1" `
            -TemplateFile "$workspaceRoot\tests\fixtures\patterns\sample-workflow-template.yaml" `
            -DryRun 2>$null
        
        Test-Assert `
            -TestName "Template validator checks required fields" `
            -Condition ($validationResult.validation_passed -eq $true) `
            -ErrorMessage "Should validate required fields"
        
        Test-Assert `
            -TestName "Template validator verifies TDD compliance" `
            -Condition ($validationResult.tdd_compliant -eq $true) `
            -ErrorMessage "Should verify TDD compliance"
        
    } catch {
        Test-Assert -TestName "Template validator checks required fields" -Condition $false -ErrorMessage $_.Exception.Message
        Test-Assert -TestName "Template validator verifies TDD compliance" -Condition $false -ErrorMessage "Script execution failed"
    }
} else {
    Test-Assert -TestName "Template validator checks required fields" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Template validator verifies TDD compliance" -Condition $false -ErrorMessage "Prerequisites missing"
}

# ============================================================================
# TEST GROUP 4: Pattern Learning & Storage (6 tests)
# ============================================================================
Write-Host "`n📖 Test Group 4: Pattern Learning & Storage (6 tests)" -ForegroundColor Cyan

Test-Assert `
    -TestName "Pattern extractor script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\right-brain\extract-pattern.ps1") `
    -ErrorMessage "extract-pattern.ps1 missing"

Test-Assert `
    -TestName "Pattern storage updater script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\right-brain\update-pattern-library.ps1") `
    -ErrorMessage "update-pattern-library.ps1 missing"

# Test pattern extraction from completed work
if (Test-Path "$workspaceRoot\scripts\right-brain\extract-pattern.ps1") {
    try {
        $extractResult = & "$workspaceRoot\scripts\right-brain\extract-pattern.ps1" `
            -SessionId "test-session-123" `
            -DryRun 2>$null
        
        Test-Assert `
            -TestName "Pattern extractor analyzes completed work" `
            -Condition ($extractResult.pattern_extracted -eq $true) `
            -ErrorMessage "Should extract patterns from completed work"
        
        Test-Assert `
            -TestName "Pattern extractor identifies reusable components" `
            -Condition ($extractResult.reusable_components.Count -gt 0) `
            -ErrorMessage "Should identify reusable components"
        
        Test-Assert `
            -TestName "Pattern extractor generates pattern metadata" `
            -Condition ($null -ne $extractResult.metadata) `
            -ErrorMessage "Should generate pattern metadata"
        
    } catch {
        Test-Assert -TestName "Pattern extractor analyzes completed work" -Condition $false -ErrorMessage $_.Exception.Message
        Test-Assert -TestName "Pattern extractor identifies reusable components" -Condition $false -ErrorMessage "Script execution failed"
        Test-Assert -TestName "Pattern extractor generates pattern metadata" -Condition $false -ErrorMessage "Script execution failed"
    }
} else {
    Test-Assert -TestName "Pattern extractor analyzes completed work" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Pattern extractor identifies reusable components" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Pattern extractor generates pattern metadata" -Condition $false -ErrorMessage "Prerequisites missing"
}

# Test pattern storage
if (Test-Path "$workspaceRoot\scripts\right-brain\update-pattern-library.ps1") {
    try {
        $storageResult = & "$workspaceRoot\scripts\right-brain\update-pattern-library.ps1" `
            -PatternFile "$workspaceRoot\tests\fixtures\patterns\sample-export-pattern.yaml" `
            -DryRun 2>$null
        
        Test-Assert `
            -TestName "Pattern storage validates before storing" `
            -Condition ($storageResult.validated -eq $true) `
            -ErrorMessage "Should validate patterns before storage"
        
        Test-Assert `
            -TestName "Pattern storage updates knowledge graph" `
            -Condition ($storageResult.knowledge_graph_updated -eq $true) `
            -ErrorMessage "Should update knowledge graph"
        
        Test-Assert `
            -TestName "Pattern storage logs to right-hemisphere state" `
            -Condition ($storageResult.logged_to_hemisphere_state -eq $true) `
            -ErrorMessage "Should log to hemisphere state"
        
    } catch {
        Test-Assert -TestName "Pattern storage validates before storing" -Condition $false -ErrorMessage $_.Exception.Message
        Test-Assert -TestName "Pattern storage updates knowledge graph" -Condition $false -ErrorMessage "Script execution failed"
        Test-Assert -TestName "Pattern storage logs to right-hemisphere state" -Condition $false -ErrorMessage "Script execution failed"
    }
} else {
    Test-Assert -TestName "Pattern storage validates before storing" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Pattern storage updates knowledge graph" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Pattern storage logs to right-hemisphere state" -Condition $false -ErrorMessage "Script execution failed"
}

# ============================================================================
# TEST GROUP 5: Work Planner Integration (7 tests)
# ============================================================================
Write-Host "`n🧠 Test Group 5: Work Planner Integration (7 tests)" -ForegroundColor Cyan

# Test work-planner.md has pattern matching integration
if (Test-Path "$workspaceRoot\prompts\internal\work-planner.md") {
    $workPlanner = Get-Content "$workspaceRoot\prompts\internal\work-planner.md" -Raw
    
    Test-Assert `
        -TestName "work-planner.md queries pattern library" `
        -Condition ($workPlanner -match "pattern|match-pattern") `
        -ErrorMessage "work-planner should query pattern library"
    
    Test-Assert `
        -TestName "work-planner.md uses workflow templates" `
        -Condition ($workPlanner -match "workflow.*template|template.*workflow") `
        -ErrorMessage "Should use workflow templates"
    
    Test-Assert `
        -TestName "work-planner.md performs similarity matching" `
        -Condition ($workPlanner -match "similarity|similar") `
        -ErrorMessage "Should perform similarity matching"
    
    Test-Assert `
        -TestName "work-planner.md stores active plan in right-hemisphere" `
        -Condition ($workPlanner -match "right-hemisphere.*active-plan") `
        -ErrorMessage "Should store active plan in right-hemisphere"
    
    Test-Assert `
        -TestName "work-planner.md sends coordination messages" `
        -Condition ($workPlanner -match "corpus-callosum|coordination") `
        -ErrorMessage "Should send coordination messages"
    
    Test-Assert `
        -TestName "work-planner.md learns from execution feedback" `
        -Condition ($workPlanner -match "feedback|learn.*execution") `
        -ErrorMessage "Should learn from execution feedback"
    
    Test-Assert `
        -TestName "work-planner.md adapts plans based on patterns" `
        -Condition ($workPlanner -match "adapt.*pattern|pattern.*adapt") `
        -ErrorMessage "Should adapt plans based on patterns"
    
} else {
    Test-Assert -TestName "work-planner.md queries pattern library" -Condition $false -ErrorMessage "work-planner.md missing"
    Test-Assert -TestName "work-planner.md uses workflow templates" -Condition $false -ErrorMessage "work-planner.md missing"
    Test-Assert -TestName "work-planner.md performs similarity matching" -Condition $false -ErrorMessage "work-planner.md missing"
    Test-Assert -TestName "work-planner.md stores active plan in right-hemisphere" -Condition $false -ErrorMessage "work-planner.md missing"
    Test-Assert -TestName "work-planner.md sends coordination messages" -Condition $false -ErrorMessage "work-planner.md missing"
    Test-Assert -TestName "work-planner.md learns from execution feedback" -Condition $false -ErrorMessage "work-planner.md missing"
    Test-Assert -TestName "work-planner.md adapts plans based on patterns" -Condition $false -ErrorMessage "work-planner.md missing"
}

# ============================================================================
# TEST GROUP 6: Corpus Callosum Coordination (6 tests)
# ============================================================================
Write-Host "`n🔗 Test Group 6: Corpus Callosum Coordination (6 tests)" -ForegroundColor Cyan

Test-Assert `
    -TestName "Coordination queue exists" `
    -Condition (Test-Path "$workspaceRoot\kds-brain\corpus-callosum\coordination-queue.jsonl") `
    -ErrorMessage "Coordination queue missing"

Test-Assert `
    -TestName "Message schema exists" `
    -Condition (Test-Path "$workspaceRoot\kds-brain\corpus-callosum\schemas\coordination-message.schema.json") `
    -ErrorMessage "Coordination message schema missing"

Test-Assert `
    -TestName "Coordination processor script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\corpus-callosum\process-coordination.ps1") `
    -ErrorMessage "process-coordination.ps1 missing"

# Test coordination message processing
if (Test-Path "$workspaceRoot\scripts\corpus-callosum\process-coordination.ps1") {
    try {
        $coordResult = & "$workspaceRoot\scripts\corpus-callosum\process-coordination.ps1" `
            -DryRun 2>$null
        
        Test-Assert `
            -TestName "Coordination processor routes messages between hemispheres" `
            -Condition ($coordResult.routes_messages -eq $true) `
            -ErrorMessage "Should route messages between hemispheres"
        
        Test-Assert `
            -TestName "Coordination processor validates message format" `
            -Condition ($coordResult.validates_format -eq $true) `
            -ErrorMessage "Should validate message format"
        
        Test-Assert `
            -TestName "Coordination processor logs all exchanges" `
            -Condition ($coordResult.logs_exchanges -eq $true) `
            -ErrorMessage "Should log all exchanges"
        
    } catch {
        Test-Assert -TestName "Coordination processor routes messages between hemispheres" -Condition $false -ErrorMessage $_.Exception.Message
        Test-Assert -TestName "Coordination processor validates message format" -Condition $false -ErrorMessage "Script execution failed"
        Test-Assert -TestName "Coordination processor logs all exchanges" -Condition $false -ErrorMessage "Script execution failed"
    }
} else {
    Test-Assert -TestName "Coordination processor routes messages between hemispheres" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Coordination processor validates message format" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Coordination processor logs all exchanges" -Condition $false -ErrorMessage "Prerequisites missing"
}

# ============================================================================
# TEST GROUP 7: Week 3 Capability Validation (5 tests)
# ============================================================================
Write-Host "`n🎯 Test Group 7: Week 3 Capability Validation (5 tests)" -ForegroundColor Cyan

# Test 1: Right brain can match patterns
$canMatchPatterns = $false
if ((Test-Path "$workspaceRoot\scripts\right-brain\match-pattern.ps1") -and
    (Test-Path "$workspaceRoot\kds-brain\right-hemisphere\patterns")) {
    try {
        $matchTest = & "$workspaceRoot\scripts\right-brain\match-pattern.ps1" `
            -Query "I want to add invoice export" `
            -DryRun 2>$null
        
        $canMatchPatterns = ($matchTest.matches_found -eq $true) -and
                           ($matchTest.similarity_score -is [double])
    } catch {
        $canMatchPatterns = $false
    }
}

Test-Assert `
    -TestName "Right brain can match patterns from queries" `
    -Condition $canMatchPatterns `
    -ErrorMessage "Pattern matching not operational"

# Test 2: Right brain can generate workflow templates
$canGenerateTemplates = $false
if (Test-Path "$workspaceRoot\scripts\right-brain\generate-workflow-template.ps1") {
    try {
        $templateTest = & "$workspaceRoot\scripts\right-brain\generate-workflow-template.ps1" `
            -PatternId "export_feature" `
            -DryRun 2>$null
        
        $canGenerateTemplates = ($templateTest.phases.Count -gt 0) -and
                               ($templateTest.includes_tdd -eq $true)
    } catch {
        $canGenerateTemplates = $false
    }
}

Test-Assert `
    -TestName "Right brain can generate workflow templates" `
    -Condition $canGenerateTemplates `
    -ErrorMessage "Template generation not operational"

# Test 3: Right brain can learn new patterns
$canLearnPatterns = $false
if (Test-Path "$workspaceRoot\scripts\right-brain\extract-pattern.ps1") {
    try {
        $learnTest = & "$workspaceRoot\scripts\right-brain\extract-pattern.ps1" `
            -SessionId "test-session-123" `
            -DryRun 2>$null
        
        $canLearnPatterns = ($learnTest.pattern_extracted -eq $true) -and
                           ($learnTest.reusable_components.Count -gt 0)
    } catch {
        $canLearnPatterns = $false
    }
}

Test-Assert `
    -TestName "Right brain can learn new patterns from completed work" `
    -Condition $canLearnPatterns `
    -ErrorMessage "Pattern learning not operational"

# Test 4: Hemispheres can coordinate
$canCoordinate = $false
if ((Test-Path "$workspaceRoot\kds-brain\corpus-callosum\coordination-queue.jsonl") -and
    (Test-Path "$workspaceRoot\scripts\corpus-callosum\process-coordination.ps1")) {
    try {
        $coordTest = & "$workspaceRoot\scripts\corpus-callosum\process-coordination.ps1" `
            -DryRun 2>$null
        
        $canCoordinate = ($coordTest.routes_messages -eq $true) -and
                        ($coordTest.validates_format -eq $true)
    } catch {
        $canCoordinate = $false
    }
}

Test-Assert `
    -TestName "Brain hemispheres can coordinate via corpus callosum" `
    -Condition $canCoordinate `
    -ErrorMessage "Hemisphere coordination not operational"

# Test 5: Full pattern-based planning works
$patternBasedPlanningWorks = $false

# Check all Week 3 components operational
$week3Complete = (Test-Path "$workspaceRoot\scripts\right-brain\match-pattern.ps1") -and
                 (Test-Path "$workspaceRoot\scripts\right-brain\generate-workflow-template.ps1") -and
                 (Test-Path "$workspaceRoot\scripts\right-brain\extract-pattern.ps1") -and
                 (Test-Path "$workspaceRoot\kds-brain\corpus-callosum\coordination-queue.jsonl") -and
                 $canMatchPatterns -and
                 $canGenerateTemplates -and
                 $canLearnPatterns -and
                 $canCoordinate

# Check work-planner integration
$plannerIntegrated = $false
if (Test-Path "$workspaceRoot\prompts\internal\work-planner.md") {
    $workPlanner = Get-Content "$workspaceRoot\prompts\internal\work-planner.md" -Raw
    $plannerIntegrated = ($workPlanner -match "pattern|match-pattern") -and
                        ($workPlanner -match "workflow.*template") -and
                        ($workPlanner -match "corpus-callosum|coordination")
}

$patternBasedPlanningWorks = $week3Complete -and $plannerIntegrated

Test-Assert `
    -TestName "Brain can use patterns to create better plans" `
    -Condition $patternBasedPlanningWorks `
    -ErrorMessage "Week 3 infrastructure not complete for pattern-based planning"

# ============================================================================
# RESULTS SUMMARY
# ============================================================================
Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "📊 WEEK 3 VALIDATION TEST RESULTS" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""
Write-Host "Total Tests Run:    $script:TestsRun" -ForegroundColor White
Write-Host "Tests Passed:       $script:TestsPassed" -ForegroundColor Green
Write-Host "Tests Failed:       $script:TestsFailed" -ForegroundColor Red
Write-Host ""

$passRate = if ($script:TestsRun -gt 0) { 
    [math]::Round(($script:TestsPassed / $script:TestsRun) * 100, 1) 
} else { 
    0 
}

Write-Host "Pass Rate:          $passRate%" -ForegroundColor $(if ($passRate -eq 100) { "Green" } else { "Yellow" })
Write-Host ""

if ($script:TestsFailed -eq 0) {
    Write-Host "✅ ALL WEEK 3 TESTS PASSING - Week 3 Implementation Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 Week 3 Capabilities Validated:" -ForegroundColor Cyan
    Write-Host "  - Pattern matching and recognition" -ForegroundColor Green
    Write-Host "  - Workflow template generation" -ForegroundColor Green
    Write-Host "  - Pattern learning from completed work" -ForegroundColor Green
    Write-Host "  - Hemisphere coordination via corpus callosum" -ForegroundColor Green
    Write-Host "  - Pattern-based planning integration" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Ready for Week 4: Cross-Hemisphere Learning" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  WEEK 3 IMPLEMENTATION IN PROGRESS" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Expected: Tests will fail until Week 3 is complete" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Create pattern library infrastructure" -ForegroundColor White
    Write-Host "  2. Implement pattern matching algorithm" -ForegroundColor White
    Write-Host "  3. Build workflow template generator" -ForegroundColor White
    Write-Host "  4. Create pattern learning system" -ForegroundColor White
    Write-Host "  5. Integrate with work-planner.md" -ForegroundColor White
    Write-Host "  6. Set up corpus callosum coordination" -ForegroundColor White
    Write-Host "  7. Re-run this test suite" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Use Week 2 TDD automation to build Week 3!" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}
