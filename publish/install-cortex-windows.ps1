<#
.SYNOPSIS
    CORTEX Bootstrap Installer for Windows
    
.DESCRIPTION
    Automated bootstrap installer that handles Python and Git installation,
    then runs the Python installer. Designed for VS Code terminal workflow.
    
.PARAMETER TargetPath
    Target repository path where CORTEX will be installed
    
.EXAMPLE
    .\install-cortex-windows.ps1 -TargetPath "C:\Users\YourName\Projects\KSESSIONS"
    
.NOTES
    Author: Asif Hussain
    Copyright: © 2024-2025 Asif Hussain. All rights reserved.
    License: Proprietary
    Version: 5.2.0
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$TargetPath
)

$ErrorActionPreference = "Stop"

# CORTEX Banner
Write-Host @"
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                   🧠 CORTEX Bootstrap Installer (Windows)                   ║
║                                                                              ║
║  Installing prerequisites and setting up CORTEX for your project            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Version:    5.2.0
Author:     Asif Hussain
Copyright:  © 2024-2025 Asif Hussain. All rights reserved.
License:    Proprietary
Platform:   Windows (PowerShell)

═══════════════════════════════════════════════════════════════════════════════
"@ -ForegroundColor Cyan

Write-Host ""

# Step 1: Check for Python
Write-Host "🔍 Checking for Python installation..." -ForegroundColor Yellow

$pythonCmd = $null
try {
    $pythonVersion = & python --version 2>&1
    if ($LASTEXITCODE -eq 0 -and $pythonVersion -match "Python 3\.([8-9]|1[0-9])") {
        $pythonCmd = "python"
        Write-Host "   ✅ Found: $pythonVersion" -ForegroundColor Green
    }
} catch {
    # Python not found
}

if (-not $pythonCmd) {
    # Try python3
    try {
        $pythonVersion = & python3 --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $pythonVersion -match "Python 3\.([8-9]|1[0-9])") {
            $pythonCmd = "python3"
            Write-Host "   ✅ Found: $pythonVersion" -ForegroundColor Green
        }
    } catch {
        # Python3 not found either
    }
}

if (-not $pythonCmd) {
    Write-Host "   ❌ Python 3.8+ not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 Installing Python..." -ForegroundColor Yellow
    
    # Download Python installer
    $pythonUrl = "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-installer.exe"
    
    Write-Host "   Downloading from python.org..." -ForegroundColor Gray
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller -UseBasicParsing
    
    Write-Host "   Running installer (this may take a few minutes)..." -ForegroundColor Gray
    Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_test=0" -Wait
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    # Verify installation
    try {
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = "python"
            Write-Host "   ✅ Python installed successfully: $pythonVersion" -ForegroundColor Green
        } else {
            throw "Python installation verification failed"
        }
    } catch {
        Write-Host "   ❌ Python installation failed" -ForegroundColor Red
        Write-Host "   Please install Python 3.8+ manually from python.org and re-run this script" -ForegroundColor Yellow
        exit 1
    }
}

# Step 2: Check for Git (optional but recommended)
Write-Host ""
Write-Host "🔍 Checking for Git installation..." -ForegroundColor Yellow

$gitInstalled = $false
try {
    $gitVersion = & git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $gitInstalled = $true
        Write-Host "   ✅ Found: $gitVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️  Git not found (optional but recommended)" -ForegroundColor Yellow
    
    # Ask user if they want to install Git
    $installGit = Read-Host "   Install Git now? (y/n)"
    if ($installGit -eq 'y' -or $installGit -eq 'Y') {
        Write-Host ""
        Write-Host "📥 Installing Git..." -ForegroundColor Yellow
        
        # Download Git installer
        $gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"
        $gitInstaller = "$env:TEMP\git-installer.exe"
        
        Write-Host "   Downloading from github.com..." -ForegroundColor Gray
        Invoke-WebRequest -Uri $gitUrl -OutFile $gitInstaller -UseBasicParsing
        
        Write-Host "   Running installer..." -ForegroundColor Gray
        Start-Process -FilePath $gitInstaller -ArgumentList "/VERYSILENT", "/NORESTART" -Wait
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        # Verify
        try {
            $gitVersion = & git --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $gitInstalled = $true
                Write-Host "   ✅ Git installed successfully: $gitVersion" -ForegroundColor Green
            }
        } catch {
            Write-Host "   ⚠️  Git installation failed (continuing anyway)" -ForegroundColor Yellow
        }
    }
}

# Step 3: Install Python dependencies
Write-Host ""
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow

$requirementsFile = Join-Path $PSScriptRoot "cortex-files\requirements.txt"
if (Test-Path $requirementsFile) {
    try {
        & $pythonCmd -m pip install --quiet --upgrade pip
        & $pythonCmd -m pip install --quiet -r $requirementsFile
        Write-Host "   ✅ Dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Some dependencies may have failed to install" -ForegroundColor Yellow
        Write-Host "   You can retry later with: pip install -r requirements.txt" -ForegroundColor Gray
    }
} else {
    Write-Host "   ⚠️  requirements.txt not found, skipping" -ForegroundColor Yellow
}

# Step 4: Get target path if not provided
if (-not $TargetPath) {
    Write-Host ""
    Write-Host "📁 Target Repository" -ForegroundColor Yellow
    Write-Host "   Where should CORTEX be installed?" -ForegroundColor Gray
    Write-Host "   (Press Enter for current directory)" -ForegroundColor Gray
    $TargetPath = Read-Host "   Path"
    
    if (-not $TargetPath) {
        $TargetPath = Get-Location
    }
}

# Step 5: Run Python installer
Write-Host ""
Write-Host "🚀 Running CORTEX installer..." -ForegroundColor Yellow

$pythonInstaller = Join-Path $PSScriptRoot "install_cortex.py"
if (-not (Test-Path $pythonInstaller)) {
    Write-Host "   ❌ install_cortex.py not found in package" -ForegroundColor Red
    Write-Host "   Please ensure you have the complete CORTEX installation package" -ForegroundColor Yellow
    exit 1
}

try {
    & $pythonCmd $pythonInstaller $TargetPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "╔══════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║                     ✅ Bootstrap Complete!                                    ║" -ForegroundColor Green
        Write-Host "╚══════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
        Write-Host "   1. Open your project in VS Code" -ForegroundColor White
        Write-Host "   2. Open GitHub Copilot Chat" -ForegroundColor White
        Write-Host "   3. Run: /CORTEX setup" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "📚 For help, type in Copilot Chat: /CORTEX help" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "❌ Installation failed. Check error messages above." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "❌ Installation failed: $_" -ForegroundColor Red
    exit 1
}
