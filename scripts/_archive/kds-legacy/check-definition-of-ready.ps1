# Definition of READY Automation Script
# KDS/scripts/check-definition-of-ready.ps1

<#
.SYNOPSIS
    Validates Definition of READY for work items, PRs, and features

.DESCRIPTION
    RIGHT BRAIN agent tool that ensures work is ready before execution begins.
    Integrates with GitHub PRs and provides interactive DoR completion wizard.

.PARAMETER Source
    Source of work item: "PR", "Issue", "Manual"

.PARAMETER WorkItemId
    PR number, Issue number, or custom work item ID

.PARAMETER Interactive
    Enable interactive DoR completion wizard

.EXAMPLE
    pwsh check-definition-of-ready.ps1 -Source "PR" -WorkItemId 123
    
.EXAMPLE
    pwsh check-definition-of-ready.ps1 -Interactive
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("PR", "Issue", "Manual")]
    [string]$Source = "Manual",
    
    [Parameter(Mandatory=$false)]
    [string]$WorkItemId,
    
    [Parameter(Mandatory=$false)]
    [switch]$Interactive
)

$ErrorActionPreference = "Stop"

# ============================================================================
# DoR Validation Functions
# ============================================================================

function Test-AcceptanceCriteria {
    param(
        [Parameter(Mandatory)]
        [string]$Description
    )
    
    # Check for Given/When/Then patterns
    $hasGiven = $Description -match '\bgiven\b'
    $hasWhen = $Description -match '\bwhen\b'
    $hasThen = $Description -match '\bthen\b'
    
    # Check for scenario structure
    $hasScenario = $Description -match '\bscenario\b'
    
    # Check for user story format
    $hasUserStory = $Description -match 'as a.*i want.*so that'
    
    $score = 0
    if ($hasGiven) { $score++ }
    if ($hasWhen) { $score++ }
    if ($hasThen) { $score++ }
    if ($hasScenario) { $score++ }
    if ($hasUserStory) { $score++ }
    
    return @{
        HasCriteria = ($score -ge 3)
        Score = $score
        MaxScore = 5
        Suggestions = @(
            if (-not $hasUserStory) { "Add user story: 'As a [role], I want [goal], so that [benefit]'" }
            if (-not $hasScenario) { "Add scenarios with Given/When/Then format" }
            if (-not $hasGiven) { "Define preconditions with 'Given'" }
            if (-not $hasWhen) { "Define actions with 'When'" }
            if (-not $hasThen) { "Define expected outcomes with 'Then'" }
        )
    }
}

function Test-TestScenarios {
    param(
        [Parameter(Mandatory)]
        [string]$Description
    )
    
    # Check for test-related keywords
    $hasTestPlan = $Description -match '\btest\b'
    $hasTDD = $Description -match '\bred.*green.*refactor\b'
    $hasTestCases = $Description -match 'test case|test scenario'
    
    # Look for specific test names
    $testPattern = '\b\w+_Should_\w+_When\w+'
    $hasTestNames = $Description -match $testPattern
    
    return @{
        HasScenarios = ($hasTestPlan -or $hasTestCases -or $hasTestNames)
        HasTDDApproach = $hasTDD
        Suggestions = @(
            if (-not $hasTestCases) { "List test scenarios to cover" }
            if (-not $hasTDD) { "Define TDD approach: RED → GREEN → REFACTOR" }
            if (-not $hasTestNames) { "Suggest test method names (e.g., Component_Should_Behavior_WhenCondition)" }
        )
    }
}

function Test-TechnicalApproach {
    param(
        [Parameter(Mandatory)]
        [string]$Description,
        
        [Parameter(Mandatory=$false)]
        [string[]]$ChangedFiles = @()
    )
    
    $hasApproach = $Description -match 'approach|implementation|design|architecture'
    $hasComponents = $Description -match 'component|service|class|module'
    $hasPattern = $Description -match 'pattern|solid|mvc|repository'
    
    $identifiedFiles = $ChangedFiles.Count -gt 0
    
    return @{
        HasApproach = ($hasApproach -or $hasComponents)
        HasPattern = $hasPattern
        HasFiles = $identifiedFiles
        AffectedFiles = $ChangedFiles
        Suggestions = @(
            if (-not $hasApproach) { "Describe technical implementation approach" }
            if (-not $hasComponents) { "List affected components/services" }
            if (-not $hasPattern) { "Identify architectural patterns to use" }
            if (-not $identifiedFiles) { "List files that will change" }
        )
    }
}

function Test-Dependencies {
    param(
        [Parameter(Mandatory=$false)]
        [string]$Description = ""
    )
    
    $hasBlockers = $Description -match 'block|depend|require|prerequisite'
    $explicitlyNone = $Description -match 'no (dependencies|blockers)|none'
    
    return @{
        Acknowledged = ($hasBlockers -or $explicitlyNone)
        HasBlockers = $hasBlockers
        Suggestions = @(
            if (-not ($hasBlockers -or $explicitlyNone)) {
                "Identify dependencies or state 'None'"
            }
        )
    }
}

function Test-ScopeDefinition {
    param(
        [Parameter(Mandatory=$false)]
        [int]$EstimatedHours = 0,
        
        [Parameter(Mandatory=$false)]
        [string]$Description = ""
    )
    
    $hasEstimate = $EstimatedHours -gt 0 -or $Description -match '\d+\s*(hour|hr|h)\b'
    $withinRecommended = $EstimatedHours -le 4 -and $EstimatedHours -gt 0
    $hasBreakdown = $Description -match 'task|phase|step|subtask'
    
    return @{
        HasEstimate = $hasEstimate
        WithinRecommended = $withinRecommended
        EstimatedHours = $EstimatedHours
        HasBreakdown = $hasBreakdown
        Suggestions = @(
            if (-not $hasEstimate) { "Estimate effort in hours" }
            if ($EstimatedHours -gt 4) { 
                "Break down work into tasks <4 hours each (current: $EstimatedHours hours)"
            }
            if (-not $hasBreakdown) { "Create task breakdown" }
        )
    }
}

# ============================================================================
# PR Integration
# ============================================================================

function Get-PRDetails {
    param(
        [Parameter(Mandatory)]
        [int]$PRNumber
    )
    
    try {
        # Use GitHub CLI if available
        $prJson = gh pr view $PRNumber --json title,body,labels,files,url 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            $pr = $prJson | ConvertFrom-Json
            
            return @{
                Success = $true
                Title = $pr.title
                Description = $pr.body
                Files = $pr.files | ForEach-Object { $_.path }
                URL = $pr.url
                Labels = $pr.labels | ForEach-Object { $_.name }
            }
        }
    } catch {
        # Fallback: Manual input
    }
    
    # Fallback if gh CLI not available
    return @{
        Success = $false
        Error = "GitHub CLI not available. Use -Interactive mode for manual input."
    }
}

function Add-PRComment {
    param(
        [Parameter(Mandatory)]
        [int]$PRNumber,
        
        [Parameter(Mandatory)]
        [string]$Comment
    )
    
    try {
        gh pr comment $PRNumber --body $Comment
        return $true
    } catch {
        Write-Warning "Failed to add PR comment: $_"
        return $false
    }
}

# ============================================================================
# Interactive DoR Wizard
# ============================================================================

function Start-DoRWizard {
    param(
        [Parameter(Mandatory=$false)]
        [hashtable]$ExistingData
    )
    
    Write-Host "`n" -NoNewline
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  📋 DEFINITION OF READY - Interactive Wizard" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    
    $dor = @{
        Title = ""
        UserStory = @{
            Role = ""
            Goal = ""
            Benefit = ""
        }
        AcceptanceCriteria = @()
        TestScenarios = @()
        TechnicalApproach = ""
        Dependencies = @()
        EstimatedHours = 0
        TaskBreakdown = @()
    }
    
    # Step 1: Work Description
    Write-Host "STEP 1: Work Description" -ForegroundColor Yellow
    Write-Host "───────────────────────────────────────────────────────────" -ForegroundColor Gray
    
    if ($ExistingData -and $ExistingData.Title) {
        Write-Host "Current title: " -NoNewline
        Write-Host $ExistingData.Title -ForegroundColor White
        $useExisting = Read-Host "Use this title? (Y/N)"
        if ($useExisting -eq 'Y') {
            $dor.Title = $ExistingData.Title
        }
    }
    
    if (-not $dor.Title) {
        $dor.Title = Read-Host "What are you building/fixing?"
    }
    
    Write-Host ""
    
    # Step 2: User Story
    Write-Host "STEP 2: User Story" -ForegroundColor Yellow
    Write-Host "───────────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host "Format: As a [role], I want [goal], so that [benefit]" -ForegroundColor Gray
    Write-Host ""
    
    $dor.UserStory.Role = Read-Host "As a (user role)"
    $dor.UserStory.Goal = Read-Host "I want (what goal)"
    $dor.UserStory.Benefit = Read-Host "So that (what benefit)"
    
    Write-Host ""
    
    # Step 3: Acceptance Criteria
    Write-Host "STEP 3: Acceptance Criteria (Given/When/Then)" -ForegroundColor Yellow
    Write-Host "───────────────────────────────────────────────────────────" -ForegroundColor Gray
    
    $addMore = $true
    $scenarioNum = 1
    
    while ($addMore) {
        Write-Host "`nScenario $scenarioNum" -ForegroundColor Cyan
        $scenario = @{
            Name = Read-Host "  Scenario name"
            Given = Read-Host "  Given (precondition)"
            When = Read-Host "  When (action)"
            Then = Read-Host "  Then (expected outcome)"
        }
        $dor.AcceptanceCriteria += $scenario
        
        $response = Read-Host "`nAdd another scenario? (Y/N)"
        $addMore = ($response -eq 'Y')
        $scenarioNum++
    }
    
    Write-Host ""
    
    # Step 4: Test Strategy
    Write-Host "STEP 4: Test Strategy" -ForegroundColor Yellow
    Write-Host "───────────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host "Based on your acceptance criteria, I suggest these tests:" -ForegroundColor Gray
    Write-Host ""
    
    foreach ($scenario in $dor.AcceptanceCriteria) {
        $testName = "{0}_Should_{1}_When{2}" -f 
            ($dor.Title -replace '\s', ''),
            ($scenario.Then -replace '\s', '_' -replace '[^\w]', ''),
            ($scenario.Given -replace '\s', '_' -replace '[^\w]', '')
        
        Write-Host "  • $testName" -ForegroundColor Green
        $dor.TestScenarios += $testName
    }
    
    Write-Host ""
    $addCustomTests = Read-Host "Add custom test scenarios? (Y/N)"
    
    if ($addCustomTests -eq 'Y') {
        $addMore = $true
        while ($addMore) {
            $testName = Read-Host "  Test method name"
            $dor.TestScenarios += $testName
            $response = Read-Host "  Add another? (Y/N)"
            $addMore = ($response -eq 'Y')
        }
    }
    
    Write-Host ""
    
    # Step 5: Technical Approach
    Write-Host "STEP 5: Technical Approach" -ForegroundColor Yellow
    Write-Host "───────────────────────────────────────────────────────────" -ForegroundColor Gray
    
    $dor.TechnicalApproach = Read-Host "Describe implementation approach"
    
    Write-Host ""
    
    # Step 6: Dependencies
    Write-Host "STEP 6: Dependencies & Blockers" -ForegroundColor Yellow
    Write-Host "───────────────────────────────────────────────────────────" -ForegroundColor Gray
    
    $hasDeps = Read-Host "Are there any blockers or dependencies? (Y/N)"
    
    if ($hasDeps -eq 'Y') {
        $addMore = $true
        while ($addMore) {
            $dep = Read-Host "  Dependency/Blocker"
            $dor.Dependencies += $dep
            $response = Read-Host "  Add another? (Y/N)"
            $addMore = ($response -eq 'Y')
        }
    } else {
        $dor.Dependencies += "None"
    }
    
    Write-Host ""
    
    # Step 7: Effort Estimation
    Write-Host "STEP 7: Effort Estimation" -ForegroundColor Yellow
    Write-Host "───────────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host "Recommendation: Break work into tasks <4 hours each" -ForegroundColor Gray
    Write-Host ""
    
    $dor.EstimatedHours = [int](Read-Host "Estimated total effort (hours)")
    
    if ($dor.EstimatedHours -gt 4) {
        Write-Host ""
        Write-Host "⚠️  Estimated effort exceeds 4 hours" -ForegroundColor Yellow
        Write-Host "Let's break this down into smaller tasks..." -ForegroundColor Yellow
        Write-Host ""
        
        $numTasks = [Math]::Ceiling($dor.EstimatedHours / 4)
        Write-Host "Suggested: $numTasks tasks of ~$([Math]::Round($dor.EstimatedHours / $numTasks, 1)) hours each" -ForegroundColor Cyan
        Write-Host ""
        
        for ($i = 1; $i -le $numTasks; $i++) {
            $taskName = Read-Host "  Task $i name"
            $taskHours = Read-Host "  Task $i estimated hours"
            $dor.TaskBreakdown += @{
                Name = $taskName
                Hours = [int]$taskHours
            }
        }
    }
    
    return $dor
}

function Format-DoROutput {
    param(
        [Parameter(Mandatory)]
        [hashtable]$DoR
    )
    
    $output = @"

# $($DoR.Title)

## User Story

**As a** $($DoR.UserStory.Role)
**I want** $($DoR.UserStory.Goal)
**So that** $($DoR.UserStory.Benefit)

## Acceptance Criteria

"@

    foreach ($scenario in $DoR.AcceptanceCriteria) {
        $output += @"

### Scenario: $($scenario.Name)
- **Given** $($scenario.Given)
- **When** $($scenario.When)
- **Then** $($scenario.Then)

"@
    }

    $output += @"

## Test Strategy

**TDD Approach:** RED → GREEN → REFACTOR

**Test Scenarios:**
"@

    foreach ($test in $DoR.TestScenarios) {
        $output += "`n- $test"
    }

    $output += @"


## Technical Approach

$($DoR.TechnicalApproach)

## Dependencies

"@

    foreach ($dep in $DoR.Dependencies) {
        $output += "`n- $dep"
    }

    if ($DoR.TaskBreakdown.Count -gt 0) {
        $output += @"


## Task Breakdown

"@
        foreach ($task in $DoR.TaskBreakdown) {
            $output += "`n- **$($task.Name)** ($($task.Hours) hours)"
        }
    }

    $output += @"


## Definition of DONE

- [ ] Build succeeds (0 errors, 0 warnings)
- [ ] All tests passing
- [ ] TDD workflow followed
- [ ] Code reviewed
- [ ] Documentation updated

---

**Estimated Effort:** $($DoR.EstimatedHours) hours
**Status:** ✅ READY FOR EXECUTION

"@

    return $output
}

# ============================================================================
# Main Execution
# ============================================================================

function Invoke-DoRCheck {
    Write-Host "`n🔍 Running Definition of READY validation..." -ForegroundColor Cyan
    Write-Host ""
    
    $workItem = $null
    
    # Get work item data
    if ($Source -eq "PR" -and $WorkItemId) {
        Write-Host "Fetching PR #$WorkItemId..." -ForegroundColor Gray
        $pr = Get-PRDetails -PRNumber $WorkItemId
        
        if ($pr.Success) {
            $workItem = @{
                Title = $pr.Title
                Description = $pr.Description
                Files = $pr.Files
                URL = $pr.URL
            }
            Write-Host "✅ PR fetched: $($pr.Title)" -ForegroundColor Green
        } else {
            Write-Warning $pr.Error
            if ($Interactive) {
                Write-Host "Continuing in interactive mode..." -ForegroundColor Yellow
            } else {
                return
            }
        }
    }
    
    # Run DoR validation
    if ($workItem) {
        Write-Host "`n" -NoNewline
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host "  DoR Validation Results" -ForegroundColor Cyan
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host ""
        
        # Check each criterion
        $checks = @()
        
        # 1. Acceptance Criteria
        $acResult = Test-AcceptanceCriteria -Description $workItem.Description
        $checks += @{
            Name = "Acceptance Criteria"
            Pass = $acResult.HasCriteria
            Score = "$($acResult.Score)/$($acResult.MaxScore)"
            Suggestions = $acResult.Suggestions
        }
        
        # 2. Test Scenarios
        $testResult = Test-TestScenarios -Description $workItem.Description
        $checks += @{
            Name = "Test Scenarios"
            Pass = $testResult.HasScenarios
            Score = if ($testResult.HasScenarios) { "✓" } else { "✗" }
            Suggestions = $testResult.Suggestions
        }
        
        # 3. Technical Approach
        $techResult = Test-TechnicalApproach -Description $workItem.Description -ChangedFiles $workItem.Files
        $checks += @{
            Name = "Technical Approach"
            Pass = $techResult.HasApproach
            Score = if ($techResult.HasApproach) { "✓" } else { "✗" }
            Suggestions = $techResult.Suggestions
        }
        
        # 4. Dependencies
        $depResult = Test-Dependencies -Description $workItem.Description
        $checks += @{
            Name = "Dependencies Identified"
            Pass = $depResult.Acknowledged
            Score = if ($depResult.Acknowledged) { "✓" } else { "✗" }
            Suggestions = $depResult.Suggestions
        }
        
        # 5. Scope Definition
        $scopeResult = Test-ScopeDefinition -Description $workItem.Description
        $checks += @{
            Name = "Scope Defined"
            Pass = $scopeResult.HasEstimate
            Score = if ($scopeResult.HasEstimate) { "✓" } else { "✗" }
            Suggestions = $scopeResult.Suggestions
        }
        
        # Display results
        foreach ($check in $checks) {
            $status = if ($check.Pass) {
                Write-Host "  [" -NoNewline
                Write-Host "✅" -NoNewline -ForegroundColor Green
                Write-Host "] " -NoNewline
            } else {
                Write-Host "  [" -NoNewline
                Write-Host "❌" -NoNewline -ForegroundColor Red
                Write-Host "] " -NoNewline
            }
            
            Write-Host "$($check.Name) " -NoNewline
            Write-Host "($($check.Score))" -ForegroundColor Gray
            
            if (-not $check.Pass -and $check.Suggestions.Count -gt 0) {
                foreach ($suggestion in $check.Suggestions) {
                    Write-Host "      💡 $suggestion" -ForegroundColor Yellow
                }
            }
        }
        
        Write-Host ""
        
        # Overall status
        $passCount = ($checks | Where-Object { $_.Pass }).Count
        $totalCount = $checks.Count
        $percentage = [Math]::Round(($passCount / $totalCount) * 100, 1)
        
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        
        if ($passCount -eq $totalCount) {
            Write-Host "  ✅ DEFINITION OF READY: " -NoNewline -ForegroundColor Green
            Write-Host "COMPLETE" -ForegroundColor Green -BackgroundColor DarkGreen
            Write-Host "  Ready to begin execution!" -ForegroundColor Green
        } else {
            Write-Host "  ❌ DEFINITION OF READY: " -NoNewline -ForegroundColor Red
            Write-Host "INCOMPLETE" -ForegroundColor Red -BackgroundColor DarkRed
            Write-Host "  $passCount/$totalCount checks passed ($percentage%)" -ForegroundColor Yellow
        }
        
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host ""
        
        # Offer help if incomplete
        if ($passCount -lt $totalCount) {
            $helpResponse = Read-Host "Would you like me to help complete the DoR? (Y/N)"
            
            if ($helpResponse -eq 'Y') {
                $completedDoR = Start-DoRWizard -ExistingData $workItem
                $formatted = Format-DoROutput -DoR $completedDoR
                
                # Save to file
                $outputPath = "KDS/dor-$WorkItemId.md"
                $formatted | Out-File -FilePath $outputPath -Encoding UTF8
                
                Write-Host "`n✅ DoR saved to: $outputPath" -ForegroundColor Green
                
                # Add to PR if applicable
                if ($Source -eq "PR") {
                    $addToPR = Read-Host "Add DoR to PR #$WorkItemId as comment? (Y/N)"
                    if ($addToPR -eq 'Y') {
                        $success = Add-PRComment -PRNumber $WorkItemId -Comment $formatted
                        if ($success) {
                            Write-Host "✅ DoR added to PR #$WorkItemId" -ForegroundColor Green
                        }
                    }
                }
            }
        } else {
            # Create checkpoint if ready
            $createCheckpoint = Read-Host "DoR complete! Create checkpoint before starting? (Y/N)"
            if ($createCheckpoint -eq 'Y') {
                $feature = $workItem.Title -replace '\s+', '-' -replace '[^\w-]', ''
                $tag = "checkpoint-$feature-start"
                
                git tag -a $tag -m "[$($workItem.Title)] DoR complete, starting implementation"
                
                Write-Host "✅ Checkpoint created: $tag" -ForegroundColor Green
                Write-Host ""
                Write-Host "Ready to execute! Follow TDD: RED → GREEN → REFACTOR" -ForegroundColor Cyan
            }
        }
    }
    
    # Interactive mode without work item
    if ($Interactive -and -not $workItem) {
        $completedDoR = Start-DoRWizard
        $formatted = Format-DoROutput -DoR $completedDoR
        
        # Save to file
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $outputPath = "KDS/dor-$timestamp.md"
        $formatted | Out-File -FilePath $outputPath -Encoding UTF8
        
        Write-Host "`n✅ DoR saved to: $outputPath" -ForegroundColor Green
        Write-Host "`nNext steps:" -ForegroundColor Cyan
        Write-Host "  1. Review the DoR document" -ForegroundColor Gray
        Write-Host "  2. Create checkpoint: git tag checkpoint-[feature]-start" -ForegroundColor Gray
        Write-Host "  3. Begin execution with TDD: RED → GREEN → REFACTOR" -ForegroundColor Gray
    }
}

# Execute
Invoke-DoRCheck
