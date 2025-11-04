# workspace-resolver.ps1
# Dynamic workspace and path resolution utilities for KDS
# Provides zero hard-coded path resolution for cross-project portability
#
# Version: 1.0.0
# Purpose: Enable KDS to work in any project without hard-coded absolute paths
# Dependencies: None (PowerShell 5.1+ or PowerShell Core)

<#
.SYNOPSIS
    Gets the workspace root directory (git repository root or parent folder).

.DESCRIPTION
    Searches upward from current directory to find the git repository root.
    If no git repository is found, returns the parent folder of the current directory.
    This enables KDS to work in both git-tracked and non-tracked projects.

.EXAMPLE
    $workspaceRoot = Get-WorkspaceRoot
    # Returns: "D:\PROJECTS\KDS" (if running from KDS git repo)

.OUTPUTS
    System.String - Absolute path to workspace root
#>
function Get-WorkspaceRoot {
    [CmdletBinding()]
    [OutputType([string])]
    param()

    try {
        # Start from current directory
        $currentDir = Get-Location
        $searchDir = $currentDir.Path

        # Search upward for .git directory (indicates git root)
        while ($searchDir) {
            $gitDir = Join-Path $searchDir ".git"
            if (Test-Path $gitDir) {
                Write-Verbose "Found git repository root: $searchDir"
                return $searchDir
            }

            # Move to parent directory
            $parentDir = Split-Path $searchDir -Parent
            if ($parentDir -eq $searchDir) {
                # Reached filesystem root, no git repo found
                break
            }
            $searchDir = $parentDir
        }

        # No git repository found - return parent of current directory
        $fallback = (Get-Item $currentDir).Parent.FullName
        Write-Verbose "No git repository found. Using parent folder: $fallback"
        return $fallback
    }
    catch {
        Write-Error "Failed to determine workspace root: $_"
        throw
    }
}

<#
.SYNOPSIS
    Gets the absolute path to the KDS folder.

.DESCRIPTION
    Locates the KDS folder regardless of current working directory.
    Uses multiple strategies to find KDS:
    1. Check if current directory is KDS or contains KDS
    2. Search upward for KDS folder
    3. Search in workspace root
    
    This function is location-agnostic and works from anywhere.

.EXAMPLE
    $kdsRoot = Get-KdsRoot
    # Returns: "D:\PROJECTS\KDS" (absolute path)

.OUTPUTS
    System.String - Absolute path to KDS folder

.NOTES
    Throws an error if KDS folder cannot be found.
#>
function Get-KdsRoot {
    [CmdletBinding()]
    [OutputType([string])]
    param()

    try {
        # Strategy 1: Check if we're already in KDS folder
        $currentDir = Get-Location
        if ($currentDir.Path -match 'KDS$') {
            Write-Verbose "Already in KDS folder: $($currentDir.Path)"
            return $currentDir.Path
        }

        # Strategy 2: Check if current directory contains KDS folder
        $kdsInCurrent = Join-Path $currentDir.Path "KDS"
        if (Test-Path $kdsInCurrent) {
            Write-Verbose "Found KDS in current directory: $kdsInCurrent"
            return $kdsInCurrent
        }

        # Strategy 3: Search upward from current directory
        $searchDir = $currentDir.Path
        while ($searchDir) {
            # Check if this is the KDS folder
            if ($searchDir -match 'KDS$') {
                Write-Verbose "Found KDS folder in path: $searchDir"
                return $searchDir
            }

            # Check if KDS is a subdirectory here
            $kdsSubdir = Join-Path $searchDir "KDS"
            if (Test-Path $kdsSubdir) {
                Write-Verbose "Found KDS subdirectory: $kdsSubdir"
                return $kdsSubdir
            }

            # Move to parent directory
            $parentDir = Split-Path $searchDir -Parent
            if ($parentDir -eq $searchDir) {
                # Reached filesystem root
                break
            }
            $searchDir = $parentDir
        }

        # Strategy 4: Use PSScriptRoot if available (when sourced from KDS script)
        if ($PSScriptRoot) {
            $scriptKdsRoot = $PSScriptRoot
            while ($scriptKdsRoot -and $scriptKdsRoot -ne (Split-Path $scriptKdsRoot -Parent)) {
                if ($scriptKdsRoot -match 'KDS$') {
                    Write-Verbose "Found KDS from script location: $scriptKdsRoot"
                    return $scriptKdsRoot
                }
                $scriptKdsRoot = Split-Path $scriptKdsRoot -Parent
            }
        }

        # Strategy 5: Try workspace root
        $workspaceRoot = Get-WorkspaceRoot
        $kdsInWorkspace = Join-Path $workspaceRoot "KDS"
        if (Test-Path $kdsInWorkspace) {
            Write-Verbose "Found KDS in workspace root: $kdsInWorkspace"
            return $kdsInWorkspace
        }

        # KDS folder not found
        throw "KDS folder not found. Please ensure you're running from within a KDS-enabled project, or that KDS is in your workspace root. Current directory: $($currentDir.Path)"
    }
    catch {
        Write-Error "Failed to locate KDS folder: $_"
        throw
    }
}

<#
.SYNOPSIS
    Converts a relative path to an absolute path.

.DESCRIPTION
    Takes a relative path and converts it to an absolute path based on the provided
    base path or current directory. Handles parent directory references (..) and
    normalizes path separators for the current OS.

.PARAMETER Path
    The path to resolve (can be relative or absolute).

.PARAMETER BasePath
    The base path to resolve relative paths against. Defaults to current directory.

.EXAMPLE
    $absolutePath = Resolve-RelativePath -Path ".\kds-brain\events.jsonl" -BasePath (Get-KdsRoot)
    # Returns: "D:\PROJECTS\KDS\kds-brain\events.jsonl"

.EXAMPLE
    $absolutePath = Resolve-RelativePath -Path "..\..\..\README.md" -BasePath "D:\PROJECTS\KDS\scripts\lib"
    # Returns: "D:\PROJECTS\README.md"

.OUTPUTS
    System.String - Absolute path
#>
function Resolve-RelativePath {
    [CmdletBinding()]
    [OutputType([string])]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string]$Path,

        [Parameter(Mandatory = $false)]
        [string]$BasePath = (Get-Location).Path
    )

    try {
        # Validate inputs
        if ([string]::IsNullOrWhiteSpace($Path)) {
            throw "Path cannot be null or empty"
        }

        if ([string]::IsNullOrWhiteSpace($BasePath)) {
            throw "BasePath cannot be null or empty"
        }

        # If path is already absolute, return it (with normalization)
        if ([System.IO.Path]::IsPathRooted($Path)) {
            # Normalize path separators
            $normalized = $Path -replace '[/\\]', [System.IO.Path]::DirectorySeparatorChar
            Write-Verbose "Path is already absolute: $normalized"
            return $normalized
        }

        # Validate base path exists
        if (-not (Test-Path $BasePath)) {
            throw "BasePath does not exist: $BasePath"
        }

        # Normalize path separators in input path
        $normalizedPath = $Path -replace '[/\\]', [System.IO.Path]::DirectorySeparatorChar

        # Combine base path and relative path
        $combined = Join-Path $BasePath $normalizedPath

        # Resolve to absolute path (handles .. and .)
        $resolved = [System.IO.Path]::GetFullPath($combined)

        Write-Verbose "Resolved '$Path' to '$resolved'"
        return $resolved
    }
    catch {
        Write-Error "Failed to resolve path '$Path' with base '$BasePath': $_"
        throw
    }
}

<#
.SYNOPSIS
    Tests if a path exists and optionally throws an error if not.

.DESCRIPTION
    Validates that a file or directory exists. Can either return a boolean or
    throw a descriptive error. Useful for validating paths before use and
    providing better error messages.

.PARAMETER Path
    The path to test for existence.

.PARAMETER ThrowIfNotFound
    If specified, throws an error instead of returning false when path doesn't exist.

.EXAMPLE
    if (Test-PathExists -Path $configFile) {
        # Use config file
    }

.EXAMPLE
    Test-PathExists -Path $requiredFile -ThrowIfNotFound
    # Throws error with descriptive message if file doesn't exist

.OUTPUTS
    System.Boolean - True if path exists, False otherwise (unless ThrowIfNotFound is set)
#>
function Test-PathExists {
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string]$Path,

        [Parameter(Mandatory = $false)]
        [switch]$ThrowIfNotFound
    )

    try {
        $exists = Test-Path $Path

        if (-not $exists -and $ThrowIfNotFound) {
            throw "Required path does not exist: $Path"
        }

        Write-Verbose "Path exists check for '$Path': $exists"
        return $exists
    }
    catch {
        if ($ThrowIfNotFound) {
            Write-Error "Path validation failed: $_"
            throw
        }
        return $false
    }
}

# Export functions (for module-style usage) - only if running as a module
if ($MyInvocation.MyCommand.CommandType -eq 'ExternalScript' -and $MyInvocation.MyCommand.ScriptBlock.Module) {
    Export-ModuleMember -Function @(
        'Get-WorkspaceRoot',
        'Get-KdsRoot',
        'Resolve-RelativePath',
        'Test-PathExists'
    )
}

# Module metadata
$script:ModuleVersion = '1.0.0'
$script:ModuleName = 'KDS.WorkspaceResolver'

Write-Verbose "KDS Workspace Resolver loaded (v$script:ModuleVersion)"
