# Extract Patterns from Events
# Week 4 Phase 1: Learning Pipeline
# Analyzes execution events to identify reusable patterns

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [array]$Events,
    
    [Parameter(Mandatory=$false)]
    [int]$MinimumFrequency = 2,
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

function Get-RecentEvents {
    param([int]$Days = 7)
    
    $eventsFile = "cortex-brain\left-hemisphere\execution-state.jsonl"
    
    if (-not (Test-Path $eventsFile)) {
        Write-Verbose "No events file found"
        return @()
    }
    
    $cutoffDate = (Get-Date).AddDays(-$Days)
    
    Get-Content $eventsFile |
        ForEach-Object { 
            try {
                $_ | ConvertFrom-Json 
            } catch {
                Write-Verbose "Skipping invalid JSON line: $_"
            }
        } |
        Where-Object { 
            $_.timestamp -and 
            (Get-Date $_.timestamp) -gt $cutoffDate 
        }
}

function Extract-FileRelationshipPatterns {
    param([array]$Events)
    
    if ($Events.Count -eq 0) {
        return @()
    }
    
    # Group events by session to find co-modified files
    $sessionGroups = $Events | 
        Where-Object { $_.type -eq "code_modified" -and $_.files_modified } |
        Group-Object { $_.session_id }
    
    $coModifications = @{}
    
    foreach ($session in $sessionGroups) {
        $filesInSession = $session.Group | 
            Select-Object -ExpandProperty files_modified -ErrorAction SilentlyContinue |
            Where-Object { $_ } |
            Sort-Object -Unique
        
        if ($filesInSession.Count -ge 2) {
            # Create unique key for file pair
            $fileKey = ($filesInSession | Sort-Object) -join "|"
            
            if (-not $coModifications.ContainsKey($fileKey)) {
                $coModifications[$fileKey] = @{
                    files = $filesInSession
                    frequency = 0
                    last_seen = $null
                }
            }
            
            $coModifications[$fileKey].frequency++
            
            # Update last seen
            $latestTimestamp = $session.Group | 
                Select-Object -ExpandProperty timestamp |
                Sort-Object -Descending |
                Select-Object -First 1
            
            $coModifications[$fileKey].last_seen = $latestTimestamp
        }
    }
    
    # Convert to pattern format
    $patterns = @()
    foreach ($key in $coModifications.Keys) {
        $data = $coModifications[$key]
        
        if ($data.frequency -ge $MinimumFrequency) {
            $patterns += @{
                pattern_type = "file_relationship"
                files = $data.files
                frequency = $data.frequency
                last_seen = $data.last_seen
                raw_confidence = [Math]::Min(0.95, 0.5 + ($data.frequency * 0.05))
            }
        }
    }
    
    return $patterns
}

function Extract-WorkflowSequencePatterns {
    param([array]$Events)
    
    if ($Events.Count -eq 0) {
        return @()
    }
    
    # Group by session and extract phase sequences
    $sessionGroups = $Events | 
        Where-Object { $_.type -eq "phase_complete" -and $_.phase_id } |
        Group-Object { $_.session_id }
    
    $workflowSequences = @{}
    
    foreach ($session in $sessionGroups) {
        $phases = $session.Group | 
            Sort-Object { $_.timestamp } |
            Select-Object -ExpandProperty phase_id
        
        if ($phases.Count -ge 2) {
            $sequenceKey = ($phases | Sort-Object) -join "->"
            
            if (-not $workflowSequences.ContainsKey($sequenceKey)) {
                $workflowSequences[$sequenceKey] = @{
                    phases = $phases
                    frequency = 0
                    success_count = 0
                    last_seen = $null
                }
            }
            
            $workflowSequences[$sequenceKey].frequency++
            
            # Check if session was successful
            $success = $session.Group | 
                Where-Object { $_.success -eq $true } |
                Measure-Object |
                Select-Object -ExpandProperty Count
            
            if ($success -gt 0) {
                $workflowSequences[$sequenceKey].success_count++
            }
            
            $latestTimestamp = $session.Group | 
                Select-Object -ExpandProperty timestamp |
                Sort-Object -Descending |
                Select-Object -First 1
            
            $workflowSequences[$sequenceKey].last_seen = $latestTimestamp
        }
    }
    
    # Convert to pattern format
    $patterns = @()
    foreach ($key in $workflowSequences.Keys) {
        $data = $workflowSequences[$key]
        
        if ($data.frequency -ge $MinimumFrequency) {
            $successRate = if ($data.frequency -gt 0) { 
                $data.success_count / $data.frequency 
            } else { 
                0 
            }
            
            $patterns += @{
                pattern_type = "workflow_sequence"
                phases = $data.phases
                frequency = $data.frequency
                success_rate = $successRate
                last_seen = $data.last_seen
                raw_confidence = [Math]::Min(0.95, 0.5 + ($successRate * 0.3) + ($data.frequency * 0.02))
            }
        }
    }
    
    return $patterns
}

function Extract-ComponentTypePatterns {
    param([array]$Events)
    
    if ($Events.Count -eq 0) {
        return @()
    }
    
    # Identify common file types/components created together
    $componentGroups = $Events | 
        Where-Object { $_.type -eq "file_created" -and $_.file_path } |
        Group-Object { $_.session_id }
    
    $componentPatterns = @{}
    
    foreach ($session in $componentGroups) {
        $fileTypes = $session.Group | 
            ForEach-Object { 
                $extension = [System.IO.Path]::GetExtension($_.file_path)
                if ($_.file_path -match "\.razor$") { "razor_component" }
                elseif ($_.file_path -match "\.cs$" -and $_.file_path -match "Service") { "service_class" }
                elseif ($_.file_path -match "\.cs$" -and $_.file_path -match "Controller") { "api_controller" }
                elseif ($_.file_path -match "\.spec\.ts$" -or $_.file_path -match "Tests\.cs$") { "test_file" }
                elseif ($extension) { $extension.TrimStart('.') }
                else { "unknown" }
            } |
            Where-Object { $_ -ne "unknown" } |
            Sort-Object -Unique
        
        if ($fileTypes.Count -ge 2) {
            $componentKey = ($fileTypes | Sort-Object) -join "+"
            
            if (-not $componentPatterns.ContainsKey($componentKey)) {
                $componentPatterns[$componentKey] = @{
                    component_types = $fileTypes
                    frequency = 0
                    last_seen = $null
                }
            }
            
            $componentPatterns[$componentKey].frequency++
            
            $latestTimestamp = $session.Group | 
                Select-Object -ExpandProperty timestamp |
                Sort-Object -Descending |
                Select-Object -First 1
            
            $componentPatterns[$componentKey].last_seen = $latestTimestamp
        }
    }
    
    # Convert to pattern format
    $patterns = @()
    foreach ($key in $componentPatterns.Keys) {
        $data = $componentPatterns[$key]
        
        if ($data.frequency -ge $MinimumFrequency) {
            $patterns += @{
                pattern_type = "component_structure"
                components = $data.component_types
                frequency = $data.frequency
                last_seen = $data.last_seen
                raw_confidence = [Math]::Min(0.90, 0.5 + ($data.frequency * 0.04))
            }
        }
    }
    
    return $patterns
}

# Main execution
try {
    Write-Verbose "Starting pattern extraction from events"
    
    if ($WhatIf) {
        Write-Host "⚙️  WhatIf mode: Would extract patterns from events" -ForegroundColor Yellow
        
        # Return mock patterns for testing
        return @{
            patterns_extracted = 3
            file_relationships = 1
            workflow_sequences = 1
            component_structures = 1
            patterns = @(
                @{pattern_type="file_relationship"; files=@("A.cs","B.cs"); frequency=3}
                @{pattern_type="workflow_sequence"; phases=@("phase_0","phase_1"); frequency=2}
                @{pattern_type="component_structure"; components=@("razor_component","service_class"); frequency=2}
            )
        }
    }
    
    # Get events (either provided or from recent history)
    if (-not $Events) {
        Write-Verbose "Loading recent events from execution state"
        $Events = Get-RecentEvents -Days 7
    }
    
    if ($Events.Count -eq 0) {
        Write-Warning "No events to process"
        return @{
            patterns_extracted = 0
            file_relationships = 0
            workflow_sequences = 0
            component_structures = 0
            patterns = @()
        }
    }
    
    Write-Verbose "Processing $($Events.Count) events"
    
    # Extract different pattern types
    $filePatterns = Extract-FileRelationshipPatterns -Events $Events
    $workflowPatterns = Extract-WorkflowSequencePatterns -Events $Events
    $componentPatterns = Extract-ComponentTypePatterns -Events $Events
    
    # Combine all patterns
    $allPatterns = @()
    $allPatterns += $filePatterns
    $allPatterns += $workflowPatterns
    $allPatterns += $componentPatterns
    
    Write-Verbose "Extracted $($allPatterns.Count) patterns"
    Write-Verbose "  File relationships: $($filePatterns.Count)"
    Write-Verbose "  Workflow sequences: $($workflowPatterns.Count)"
    Write-Verbose "  Component structures: $($componentPatterns.Count)"
    
    # Return results
    return @{
        patterns_extracted = $allPatterns.Count
        file_relationships = $filePatterns.Count
        workflow_sequences = $workflowPatterns.Count
        component_structures = $componentPatterns.Count
        patterns = $allPatterns
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    }
    
} catch {
    Write-Error "Pattern extraction failed: $_"
    throw
}
