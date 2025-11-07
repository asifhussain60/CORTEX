<#
.SYNOPSIS
    CORTEX configuration template engine with variable substitution support.

.DESCRIPTION
    Provides template expansion functionality for CORTEX configuration files.
    Supports variable substitution in JSON, YAML, and Markdown templates.
    
    Variable Syntax:
    - {{VARIABLE}}         - Required variable (error if missing)
    - {{VARIABLE:default}} - Optional variable with default value
    
    Built-in Variables:
    - PROJECT_ROOT   - Git workspace root directory
    - PROJECT_NAME   - Project folder name
    - GIT_BRANCH     - Current git branch
    - TIMESTAMP      - ISO 8601 timestamp (YYYY-MM-DDTHH:MM:SSZ)
    - KDS_ROOT       - CORTEX installation directory

.PARAMETER TemplatePath
    Path to template file (relative or absolute).

.PARAMETER TemplateContent
    Template content as string (alternative to TemplatePath).

.PARAMETER Variables
    Hashtable of custom variables for substitution.

.PARAMETER OutputPath
    Optional output file path. If not specified, returns string.

.PARAMETER Force
    Overwrite existing output file without prompting.

.EXAMPLE
    Expand-ConfigTemplate -TemplatePath "cortex.config.template.json" -OutputPath "cortex.config.json"
    
    Expands template using built-in variables only.

.EXAMPLE
    $vars = @{ 
        API_URL = "https://api.example.com"
        TIMEOUT = "30"
    }
    Expand-ConfigTemplate -TemplatePath "config.template.json" -Variables $vars -OutputPath "config.json"
    
    Expands template with custom variables.

.EXAMPLE
    $template = 'Project: {{PROJECT_NAME}} at {{PROJECT_ROOT}}'
    Expand-ConfigTemplate -TemplateContent $template
    
    Returns expanded string without writing file.

.NOTES
    Part of KDS Independence Project - Phase 3: Task 3.1
    Created: 2025-11-06
    Dependencies: workspace-resolver.ps1 (for PROJECT_ROOT, KDS_ROOT)
#>

#Requires -Version 5.1

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Import workspace resolver for built-in variables
$resolverPath = Join-Path $PSScriptRoot "workspace-resolver.ps1"
if (Test-Path $resolverPath) {
    . $resolverPath
}

<#
.SYNOPSIS
    Expands template with variable substitution.
#>
function Expand-ConfigTemplate {
    [CmdletBinding(DefaultParameterSetName = 'FromFile')]
    param(
        [Parameter(Mandatory = $true, ParameterSetName = 'FromFile')]
        [string]$TemplatePath,
        
        [Parameter(Mandatory = $true, ParameterSetName = 'FromString')]
        [string]$TemplateContent,
        
        [Parameter(Mandatory = $false)]
        [hashtable]$Variables = @{},
        
        [Parameter(Mandatory = $false)]
        [string]$OutputPath,
        
        [Parameter(Mandatory = $false)]
        [switch]$Force
    )
    
    # Load template content
    $content = if ($PSCmdlet.ParameterSetName -eq 'FromFile') {
        if (-not (Test-Path $TemplatePath)) {
            throw "Template file not found: $TemplatePath"
        }
        Get-Content -Path $TemplatePath -Raw
    } else {
        $TemplateContent
    }
    
    # Build variable dictionary (custom + built-in)
    $allVars = Get-BuiltInVariables
    foreach ($key in $Variables.Keys) {
        $allVars[$key] = $Variables[$key]
    }
    
    # Expand all variables
    $expanded = Expand-Variables -Content $content -Variables $allVars
    
    # Write to file or return string
    if ($OutputPath) {
        if ((Test-Path $OutputPath) -and -not $Force) {
            $confirm = Read-Host "File exists: $OutputPath. Overwrite? (y/N)"
            if ($confirm -ne 'y') {
                Write-Warning "Cancelled by user"
                return $null
            }
        }
        
        $outputDir = Split-Path $OutputPath -Parent
        if ($outputDir -and -not (Test-Path $outputDir)) {
            New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
        }
        
        Set-Content -Path $OutputPath -Value $expanded -NoNewline
        Write-Host "✅ Template expanded: $OutputPath" -ForegroundColor Green
        return $OutputPath
    } else {
        return $expanded
    }
}

<#
.SYNOPSIS
    Gets built-in template variables.
#>
function Get-BuiltInVariables {
    $vars = @{}
    
    # PROJECT_ROOT - Git workspace root
    if (Get-Command Get-WorkspaceRoot -ErrorAction SilentlyContinue) {
        try {
            $vars['PROJECT_ROOT'] = Get-WorkspaceRoot
        } catch {
            Write-Verbose "Could not determine PROJECT_ROOT: $_"
        }
    }
    
    # KDS_ROOT - CORTEX installation directory
    if (Get-Command Get-KdsRoot -ErrorAction SilentlyContinue) {
        try {
            $vars['KDS_ROOT'] = Get-KdsRoot
        } catch {
            Write-Verbose "Could not determine KDS_ROOT: $_"
        }
    }
    
    # PROJECT_NAME - Project folder name
    if ($vars.ContainsKey('PROJECT_ROOT')) {
        $vars['PROJECT_NAME'] = Split-Path $vars['PROJECT_ROOT'] -Leaf
    }
    
    # GIT_BRANCH - Current git branch
    try {
        $branch = git rev-parse --abbrev-ref HEAD 2>$null
        if ($LASTEXITCODE -eq 0) {
            $vars['GIT_BRANCH'] = $branch.Trim()
        }
    } catch {
        Write-Verbose "Could not determine GIT_BRANCH: $_"
    }
    
    # TIMESTAMP - ISO 8601 timestamp
    $vars['TIMESTAMP'] = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    
    return $vars
}

<#
.SYNOPSIS
    Expands variables in template content.
#>
function Expand-Variables {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Content,
        
        [Parameter(Mandatory = $true)]
        [hashtable]$Variables
    )
    
    # Regex pattern for {{VARIABLE}} or {{VARIABLE:default}}
    $pattern = '\{\{([A-Z_][A-Z0-9_]*)(?::([^}]*))?\}\}'
    
    $result = [regex]::Replace($Content, $pattern, {
        param($match)
        
        $varName = $match.Groups[1].Value
        $defaultValue = if ($match.Groups[2].Success) { $match.Groups[2].Value } else { $null }
        
        if ($Variables.ContainsKey($varName)) {
            # Variable found - use its value
            return $Variables[$varName]
        } elseif ($null -ne $defaultValue) {
            # Variable not found but has default - use default
            Write-Verbose "Using default for $varName`: $defaultValue"
            return $defaultValue
        } else {
            # Variable required but missing - error
            throw "Required variable not found: $varName (use {{$varName:default}} for optional)"
        }
    })
    
    return $result
}

<#
.SYNOPSIS
    Tests if template has all required variables.
#>
function Test-TemplateVariables {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$TemplatePath,
        
        [Parameter(Mandatory = $false)]
        [hashtable]$Variables = @{}
    )
    
    if (-not (Test-Path $TemplatePath)) {
        throw "Template file not found: $TemplatePath"
    }
    
    $content = Get-Content -Path $TemplatePath -Raw
    
    # Get all variables (custom + built-in)
    $allVars = Get-BuiltInVariables
    foreach ($key in $Variables.Keys) {
        $allVars[$key] = $Variables[$key]
    }
    
    # Find all required variables (those without defaults)
    $pattern = '\{\{([A-Z_][A-Z0-9_]*)(?::([^}]*))?\}\}'
    $matches = [regex]::Matches($content, $pattern)
    
    $missing = @()
    foreach ($match in $matches) {
        $varName = $match.Groups[1].Value
        $hasDefault = $match.Groups[2].Success
        
        if (-not $hasDefault -and -not $allVars.ContainsKey($varName)) {
            $missing += $varName
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-Warning "Missing required variables: $($missing -join ', ')"
        return $false
    }
    
    Write-Host "✅ All required variables available" -ForegroundColor Green
    return $true
}

# If script is not being dot-sourced, export functions for module use
if ($MyInvocation.InvocationName -ne '.') {
    Export-ModuleMember -Function @(
        'Expand-ConfigTemplate',
        'Get-BuiltInVariables',
        'Test-TemplateVariables'
    )
}
