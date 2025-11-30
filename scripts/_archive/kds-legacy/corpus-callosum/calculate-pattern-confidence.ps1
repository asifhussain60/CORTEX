# Calculate Pattern Confidence
# Week 4 Phase 1: Learning Pipeline
# Assigns confidence scores to patterns based on multiple factors

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [hashtable]$Pattern,
    
    [Parameter(Mandatory=$false)]
    [array]$Patterns,
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

function Calculate-FrequencyScore {
    param(
        [int]$Frequency,
        [int]$MaxFrequency = 20
    )
    
    # Logarithmic scale: more frequent patterns get higher scores
    # But with diminishing returns after certain threshold
    
    if ($Frequency -le 0) { return 0.0 }
    if ($Frequency -ge $MaxFrequency) { return 0.30 }
    
    # Score from 0.0 to 0.30 based on frequency
    return [Math]::Min(0.30, ($Frequency / $MaxFrequency) * 0.30)
}

function Calculate-SuccessScore {
    param([double]$SuccessRate)
    
    # Success rate contributes significantly to confidence
    # 0% success = 0.0, 100% success = 0.40
    
    if ($SuccessRate -lt 0) { return 0.0 }
    if ($SuccessRate -gt 1) { return 0.40 }
    
    return $SuccessRate * 0.40
}

function Calculate-RecencyScore {
    param([string]$LastSeen)
    
    if (-not $LastSeen) { return 0.10 }
    
    try {
        $lastSeenDate = Get-Date $LastSeen
        $daysSince = ((Get-Date) - $lastSeenDate).TotalDays
        
        # More recent patterns get higher scores
        # 0 days = 0.20, 30+ days = 0.05
        
        if ($daysSince -le 0) { return 0.20 }
        if ($daysSince -ge 30) { return 0.05 }
        
        # Linear decay from 0.20 to 0.05 over 30 days
        $decay = (30 - $daysSince) / 30
        return 0.05 + ($decay * 0.15)
        
    } catch {
        Write-Verbose "Could not parse last_seen date: $LastSeen"
        return 0.10
    }
}

function Calculate-PatternTypeScore {
    param([string]$PatternType)
    
    # Different pattern types have different base confidence levels
    
    switch ($PatternType) {
        "file_relationship" { return 0.10 }  # Direct observation, reliable
        "workflow_sequence" { return 0.08 }  # Proven sequence, fairly reliable
        "component_structure" { return 0.06 }  # Structural pattern, less reliable
        default { return 0.05 }
    }
}

function Add-ConfidenceScore {
    param([hashtable]$Pattern)
    
    $patternCopy = $Pattern.Clone()
    
    # Calculate individual score components
    $frequencyScore = Calculate-FrequencyScore -Frequency ($Pattern.frequency ?? 0)
    $successScore = if ($Pattern.success_rate) { 
        Calculate-SuccessScore -SuccessRate $Pattern.success_rate 
    } else { 
        0.10  # Default if no success rate
    }
    $recencyScore = Calculate-RecencyScore -LastSeen ($Pattern.last_seen ?? "")
    $typeScore = Calculate-PatternTypeScore -PatternType ($Pattern.pattern_type ?? "unknown")
    
    # Calculate composite confidence score
    $confidence = $frequencyScore + $successScore + $recencyScore + $typeScore
    
    # Use raw_confidence if provided and higher
    if ($Pattern.raw_confidence -and $Pattern.raw_confidence -gt $confidence) {
        $confidence = $Pattern.raw_confidence
    }
    
    # Ensure confidence is in valid range [0.5, 1.0]
    $confidence = [Math]::Max(0.5, [Math]::Min(1.0, $confidence))
    
    # Add confidence and breakdown to pattern
    $patternCopy.confidence = [Math]::Round($confidence, 2)
    $patternCopy.confidence_breakdown = @{
        frequency_score = [Math]::Round($frequencyScore, 2)
        success_score = [Math]::Round($successScore, 2)
        recency_score = [Math]::Round($recencyScore, 2)
        type_score = [Math]::Round($typeScore, 2)
        total = [Math]::Round($confidence, 2)
    }
    
    return $patternCopy
}

# Main execution
try {
    Write-Verbose "Starting pattern confidence calculation"
    
    if ($WhatIf) {
        Write-Host "⚙️  WhatIf mode: Would calculate confidence scores" -ForegroundColor Yellow
        
        # Return mock pattern with confidence for testing
        $mockPattern = @{
            pattern_type = "file_relationship"
            files = @("A.cs", "B.cs")
            frequency = 3
            confidence = 0.75
        }
        
        return $mockPattern
    }
    
    # Handle single pattern or array
    if ($Pattern) {
        Write-Verbose "Calculating confidence for single pattern"
        $result = Add-ConfidenceScore -Pattern $Pattern
        
        Write-Verbose "Confidence score: $($result.confidence)"
        return $result
    }
    
    if ($Patterns) {
        Write-Verbose "Calculating confidence for $($Patterns.Count) patterns"
        
        $results = @()
        foreach ($p in $Patterns) {
            $results += Add-ConfidenceScore -Pattern $p
        }
        
        Write-Verbose "Processed $($results.Count) patterns"
        
        # Calculate average confidence
        $avgConfidence = ($results | 
            ForEach-Object { $_.confidence } | 
            Measure-Object -Average).Average
        
        Write-Verbose "Average confidence: $([Math]::Round($avgConfidence, 2))"
        
        return @{
            patterns = $results
            count = $results.Count
            average_confidence = [Math]::Round($avgConfidence, 2)
            timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        }
    }
    
    Write-Warning "No pattern or patterns provided"
    return $null
    
} catch {
    Write-Error "Confidence calculation failed: $_"
    throw
}
