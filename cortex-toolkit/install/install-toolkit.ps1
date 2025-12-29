# CORTEX Toolkit Installation Script (PowerShell)
# Installs toolkit for Windows with global command integration

param(
    [switch]$Global,
    [switch]$UserProfile,
    [switch]$SkipVerify
)

$ErrorActionPreference = "Stop"

Write-Host "=== CORTEX Toolkit Installer (Windows) ===" -ForegroundColor Cyan
Write-Host ""

# Discover toolkit root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ToolkitRoot = Split-Path -Parent $ScriptDir

Write-Host "Toolkit Root: $ToolkitRoot" -ForegroundColor Green

# 1. Set environment variable
Write-Host "`n[1/5] Setting environment variable..." -ForegroundColor Yellow

if ($Global) {
    [System.Environment]::SetEnvironmentVariable(
        "CORTEX_TOOLKIT_ROOT", 
        $ToolkitRoot, 
        [System.EnvironmentVariableTarget]::Machine
    )
    Write-Host "  ✓ Set CORTEX_TOOLKIT_ROOT (System-wide)" -ForegroundColor Green
} else {
    [System.Environment]::SetEnvironmentVariable(
        "CORTEX_TOOLKIT_ROOT", 
        $ToolkitRoot, 
        [System.EnvironmentVariableTarget]::User
    )
    Write-Host "  ✓ Set CORTEX_TOOLKIT_ROOT (User)" -ForegroundColor Green
}

$env:CORTEX_TOOLKIT_ROOT = $ToolkitRoot

# 2. Add to PATH
Write-Host "`n[2/5] Adding to PATH..." -ForegroundColor Yellow

$CliPath = Join-Path $ToolkitRoot "cli"

if ($Global) {
    $CurrentPath = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::Machine)
    if ($CurrentPath -notlike "*$CliPath*") {
        [System.Environment]::SetEnvironmentVariable(
            "Path",
            "$CurrentPath;$CliPath",
            [System.EnvironmentVariableTarget]::Machine
        )
        Write-Host "  ✓ Added to System PATH" -ForegroundColor Green
    } else {
        Write-Host "  ℹ Already in System PATH" -ForegroundColor Gray
    }
} else {
    $CurrentPath = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::User)
    if ($CurrentPath -notlike "*$CliPath*") {
        [System.Environment]::SetEnvironmentVariable(
            "Path",
            "$CurrentPath;$CliPath",
            [System.EnvironmentVariableTarget]::User
        )
        Write-Host "  ✓ Added to User PATH" -ForegroundColor Green
    } else {
        Write-Host "  ℹ Already in User PATH" -ForegroundColor Gray
    }
}

# 3. Create user config directory
Write-Host "`n[3/5] Creating user config..." -ForegroundColor Yellow

$UserConfigDir = Join-Path $env:USERPROFILE ".cortex"
$UserConfigFile = Join-Path $UserConfigDir "config.yaml"

if (-not (Test-Path $UserConfigDir)) {
    New-Item -ItemType Directory -Path $UserConfigDir -Force | Out-Null
    Write-Host "  ✓ Created $UserConfigDir" -ForegroundColor Green
}

if (-not (Test-Path $UserConfigFile)) {
    $ConfigContent = @"
# CORTEX User Configuration
cortex_toolkit_root: $ToolkitRoot
python_path: python
"@
    $ConfigContent | Out-File -FilePath $UserConfigFile -Encoding UTF8
    Write-Host "  ✓ Created $UserConfigFile" -ForegroundColor Green
} else {
    Write-Host "  ℹ Config already exists" -ForegroundColor Gray
}

# 4. Setup PowerShell profile integration (optional)
if ($UserProfile) {
    Write-Host "`n[4/5] Setting up PowerShell profile..." -ForegroundColor Yellow
    
    $ProfilePath = $PROFILE.CurrentUserAllHosts
    $ProfileDir = Split-Path -Parent $ProfilePath
    
    if (-not (Test-Path $ProfileDir)) {
        New-Item -ItemType Directory -Path $ProfileDir -Force | Out-Null
    }
    
    $ProfileSnippet = @"

# CORTEX Toolkit Integration
`$env:CORTEX_TOOLKIT_ROOT = "$ToolkitRoot"

# Load global commands (optional)
# . "`$env:CORTEX_TOOLKIT_ROOT\install\setup-global-commands.ps1"
"@
    
    if (Test-Path $ProfilePath) {
        $ProfileContent = Get-Content $ProfilePath -Raw
        if ($ProfileContent -notlike "*CORTEX Toolkit Integration*") {
            Add-Content -Path $ProfilePath -Value $ProfileSnippet
            Write-Host "  ✓ Added to PowerShell profile" -ForegroundColor Green
        } else {
            Write-Host "  ℹ Already in PowerShell profile" -ForegroundColor Gray
        }
    } else {
        $ProfileSnippet | Out-File -FilePath $ProfilePath -Encoding UTF8
        Write-Host "  ✓ Created PowerShell profile" -ForegroundColor Green
    }
} else {
    Write-Host "`n[4/5] Skipping PowerShell profile (use -UserProfile)" -ForegroundColor Gray
}

# 5. Verify installation
if (-not $SkipVerify) {
    Write-Host "`n[5/5] Verifying installation..." -ForegroundColor Yellow
    
    # Check Python
    try {
        $PythonVersion = python --version 2>&1
        Write-Host "  ✓ Python: $PythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠ Python not found in PATH" -ForegroundColor Yellow
    }
    
    # Check toolkit registry
    $RegistryScript = Join-Path $ToolkitRoot "shared\toolkit_registry.py"
    if (Test-Path $RegistryScript) {
        try {
            $RegistryOutput = python $RegistryScript version 2>&1
            Write-Host "  ✓ Toolkit Registry: $RegistryOutput" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠ Cannot execute toolkit registry" -ForegroundColor Yellow
        }
    }
    
    # Check manifest
    $ManifestPath = Join-Path $ToolkitRoot "toolkit-manifest.yaml"
    if (Test-Path $ManifestPath) {
        Write-Host "  ✓ Manifest: Found" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Manifest: Missing" -ForegroundColor Red
    }
} else {
    Write-Host "`n[5/5] Skipping verification (use without -SkipVerify)" -ForegroundColor Gray
}

# Summary
Write-Host "`n=== Installation Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Restart your terminal to load environment variables"
Write-Host "  2. Test installation: python `"$ToolkitRoot\shared\toolkit_registry.py`" list"
Write-Host "  3. View all tools: python `"$ToolkitRoot\shared\toolkit_registry.py`" list"
Write-Host ""
Write-Host "Environment:" -ForegroundColor Yellow
Write-Host "  CORTEX_TOOLKIT_ROOT = $ToolkitRoot"
Write-Host "  PATH += $CliPath"
Write-Host ""
Write-Host "Documentation: $ToolkitRoot\README.md" -ForegroundColor Gray
