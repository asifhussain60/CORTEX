<#
.SYNOPSIS
    BRAIN Feeder - Aggregates crawler results into KDS BRAIN storage

.DESCRIPTION
    Processes output from all area-specific crawlers and updates KDS BRAIN files:
    - file-relationships.yaml (from all crawlers)
    - test-patterns.yaml (from UI + Test crawlers)
    - architectural-patterns.yaml (from all crawlers)
    - knowledge-graph.yaml (consolidated patterns)
    
    Part of KDS v6.0 Multi-Threaded Crawler Architecture (Phase 2)

.PARAMETER WorkspaceRoot
    Absolute path to the project workspace root

.PARAMETER Results
    Hashtable of crawler results (from orchestrator)

.NOTES
    Version: 1.0.0
    Author: KDS Multi-Threaded Crawler System
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$WorkspaceRoot,
    
    [Parameter(Mandatory=$true)]
    [hashtable]$Results
)

Write-Host "🧠 BRAIN Feeder Started" -ForegroundColor Cyan
Write-Host "Workspace: $WorkspaceRoot" -ForegroundColor Gray
Write-Host ""

# Paths - detect KDS location
$normalizedRoot = $WorkspaceRoot.TrimEnd('\')
if ($normalizedRoot -match '\\KDS$') {
    # Workspace IS KDS
    $brainDir = "$normalizedRoot\kds-brain"
} else {
    # KDS is inside workspace
    $brainDir = "$normalizedRoot\KDS\kds-brain"
}

$crawlerTempDir = "$brainDir\crawler-temp"
$fileRelationshipsPath = "$brainDir\file-relationships.yaml"
$testPatternsPath = "$brainDir\test-patterns.yaml"
$architecturalPatternsPath = "$brainDir\architectural-patterns.yaml"
$knowledgeGraphPath = "$brainDir\knowledge-graph.yaml"

# Ensure BRAIN directory exists
if (-not (Test-Path $brainDir)) {
    New-Item -Path $brainDir -ItemType Directory -Force | Out-Null
}

# Helper: Load or create YAML structure
function Get-YamlContent {
    param([string]$Path, [hashtable]$Default)
    
    if (Test-Path $Path) {
        try {
            $content = Get-Content -Path $Path -Raw | ConvertFrom-Yaml -ErrorAction Stop
            return $content
        } catch {
            Write-Warning "Failed to parse $Path, using default structure"
            return $Default
        }
    }
    return $Default
}

# Helper: Save YAML content atomically
function Save-YamlContent {
    param([string]$Path, [object]$Content)
    
    $tempPath = "$Path.tmp"
    
    try {
        $Content | ConvertTo-Yaml | Set-Content -Path $tempPath -Encoding UTF8
        Move-Item -Path $tempPath -Destination $Path -Force
        return $true
    } catch {
        Write-Error "Failed to save $Path : $_"
        if (Test-Path $tempPath) {
            Remove-Item $tempPath -Force
        }
        return $false
    }
}

# Helper: Calculate confidence score
function Get-ConfidenceScore {
    param([string]$Source, [string]$Method)
    
    $baseConfidence = switch ($Source) {
        'direct-reference' { 0.95 }  # Explicit @inject, import
        'pattern-match' { 0.80 }     # Naming conventions, structure
        'statistical' { 0.65 }       # Co-occurrence
        default { 0.70 }
    }
    
    # Bonus for multiple sources
    if ($Method -eq 'multi-source') {
        $baseConfidence += 0.05
    }
    
    return [Math]::Min($baseConfidence, 0.98)  # Cap at 0.98
}

# Step 1: Process File Relationships
Write-Host "[1/4] Processing file relationships..." -ForegroundColor Yellow

$fileRelationships = @{
    last_updated = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    source = "multi-threaded-crawler"
    relationships = @()
}

# From UI crawler: Component dependencies
if ($Results.ContainsKey('UI')) {
    $uiData = $Results['UI']
    foreach ($component in $uiData.components) {
        foreach ($dep in $component.dependencies) {
            # Extract service name from "@inject Type Name"
            if ($dep -match '@inject\s+(\S+)\s+(\S+)') {
                $serviceType = $matches[1]
                
                $fileRelationships.relationships += @{
                    primary_file = $component.path
                    related_file = "Services/$serviceType.cs"  # Heuristic
                    relationship = "DI-injection"
                    confidence = Get-ConfidenceScore -Source 'direct-reference' -Method 'single'
                    source = "ui-crawler"
                }
            }
        }
    }
}

# From Test crawler: Test coverage
if ($Results.ContainsKey('Test')) {
    $testData = $Results['Test']
    foreach ($test in $testData.tests) {
        # Try to infer tested component from test path
        $testName = [System.IO.Path]::GetFileNameWithoutExtension($test.path)
        $componentName = $testName -replace '\.spec$|\.test$|Test$|Tests$', ''
        
        $fileRelationships.relationships += @{
            primary_file = $test.path
            related_file = "Components/**/$componentName.razor"  # Heuristic pattern
            relationship = "test-coverage"
            confidence = Get-ConfidenceScore -Source 'pattern-match' -Method 'single'
            source = "test-crawler"
        }
    }
}

Write-Host "  Found $($fileRelationships.relationships.Count) file relationships" -ForegroundColor Green

# Save file relationships
if (-not (Save-YamlContent -Path $fileRelationshipsPath -Content $fileRelationships)) {
    Write-Warning "  Failed to save file-relationships.yaml"
}

# Step 2: Process Test Patterns
Write-Host "`n[2/4] Processing test patterns..." -ForegroundColor Yellow

$testPatterns = @{
    last_updated = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    source = "multi-threaded-crawler"
    playwright = @{
        selector_strategy = "unknown"
        element_ids = @()
        test_data = @{}
    }
}

# From UI crawler: Element IDs
if ($Results.ContainsKey('UI')) {
    $uiData = $Results['UI']
    foreach ($component in $uiData.components) {
        foreach ($id in $component.element_ids) {
            $testPatterns.playwright.element_ids += @{
                id = $id
                component = $component.path
                purpose = "Unknown"  # Would need semantic analysis
                confidence = Get-ConfidenceScore -Source 'direct-reference' -Method 'single'
            }
        }
    }
}

# From Test crawler: Selector strategy and test data
if ($Results.ContainsKey('Test')) {
    $testData = $Results['Test']
    $testPatterns.playwright.selector_strategy = $testData.patterns.selector_strategy
    
    # Aggregate test data
    foreach ($test in $testData.tests) {
        foreach ($key in $test.test_data.Keys) {
            if (-not $testPatterns.playwright.test_data.ContainsKey($key)) {
                $testPatterns.playwright.test_data[$key] = $test.test_data[$key]
            }
        }
    }
}

Write-Host "  Found $($testPatterns.playwright.element_ids.Count) element IDs" -ForegroundColor Green
Write-Host "  Selector strategy: $($testPatterns.playwright.selector_strategy)" -ForegroundColor Green

# Save test patterns
if (-not (Save-YamlContent -Path $testPatternsPath -Content $testPatterns)) {
    Write-Warning "  Failed to save test-patterns.yaml"
}

# Step 3: Process Architectural Patterns
Write-Host "`n[3/4] Processing architectural patterns..." -ForegroundColor Yellow

$architecturalPatterns = @{
    last_updated = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    source = "multi-threaded-crawler"
    patterns = @{}
}

# Aggregate patterns from all crawlers
foreach ($area in $Results.Keys) {
    $data = $Results[$area]
    foreach ($key in $data.patterns.Keys) {
        $patternKey = "$($area.ToLower())_$key"
        $architecturalPatterns.patterns[$patternKey] = $data.patterns[$key]
    }
}

# Calculate overall confidence
$sourceCount = $Results.Count
$architecturalPatterns.confidence = Get-ConfidenceScore -Source 'pattern-match' -Method $(if ($sourceCount -gt 1) { 'multi-source' } else { 'single' })
$architecturalPatterns.sources = @($Results.Keys)

Write-Host "  Detected $($architecturalPatterns.patterns.Count) architectural patterns" -ForegroundColor Green

# Save architectural patterns
if (-not (Save-YamlContent -Path $architecturalPatternsPath -Content $architecturalPatterns)) {
    Write-Warning "  Failed to save architectural-patterns.yaml"
}

# Step 4: Update Knowledge Graph (consolidated)
Write-Host "`n[4/4] Updating knowledge graph..." -ForegroundColor Yellow

# Load existing knowledge graph
$knowledgeGraph = Get-YamlContent -Path $knowledgeGraphPath -Default @{
    last_updated = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    version = "6.0.0"
    intent_patterns = @{}
    file_relationships = @{}
    workflow_patterns = @{}
    validation_insights = @{}
    architectural_patterns = @{}
    test_patterns = @{}
}

# Merge architectural patterns
$knowledgeGraph.architectural_patterns = $architecturalPatterns.patterns

# Merge file relationships (indexed by primary file)
foreach ($rel in $fileRelationships.relationships) {
    $key = $rel.primary_file
    if (-not $knowledgeGraph.file_relationships.ContainsKey($key)) {
        $knowledgeGraph.file_relationships[$key] = @()
    }
    $knowledgeGraph.file_relationships[$key] += @{
        related_file = $rel.related_file
        relationship = $rel.relationship
        confidence = $rel.confidence
        source = $rel.source
    }
}

# Merge test patterns
$knowledgeGraph.test_patterns = $testPatterns.playwright

# Update metadata
$knowledgeGraph.last_updated = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")

Write-Host "  Knowledge graph updated with discoveries" -ForegroundColor Green

# Save knowledge graph
if (-not (Save-YamlContent -Path $knowledgeGraphPath -Content $knowledgeGraph)) {
    Write-Warning "  Failed to save knowledge-graph.yaml"
}

Write-Host ""
Write-Host "✅ BRAIN Feeding Complete!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Files updated:" -ForegroundColor Cyan
Write-Host "  - file-relationships.yaml ($($fileRelationships.relationships.Count) relationships)" -ForegroundColor White
Write-Host "  - test-patterns.yaml ($($testPatterns.playwright.element_ids.Count) element IDs)" -ForegroundColor White
Write-Host "  - architectural-patterns.yaml ($($architecturalPatterns.patterns.Count) patterns)" -ForegroundColor White
Write-Host "  - knowledge-graph.yaml (consolidated)" -ForegroundColor White
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
