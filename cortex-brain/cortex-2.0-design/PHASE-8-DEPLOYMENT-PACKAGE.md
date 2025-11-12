# CORTEX 2.0 - Phase 8: Production Deployment Package

**Date:** 2025-11-12  
**Status:** 🟡 DESIGN COMPLETE - Implementation Pending  
**Type:** Production Packaging & Distribution System  
**Priority:** HIGH  
**Phase:** 8 - Migration & Deployment

---

## 📋 Executive Summary

**Purpose:** Create a production-ready deployment package that separates user-facing CORTEX features from admin/development tools, enabling clean distribution to end users.

**Key Innovation:** Two-tier distribution model:
- **User Package:** Clean, production-ready CORTEX for end users
- **Admin/Dev Tools:** Remain in development repository only

**Approach:** Automated packaging script that creates compressed deployment with setup automation.

---

## 🎯 Problem Statement

### Current State

**Repository Structure:**
- Mixed user-facing and admin/developer tools
- Development artifacts (tests, build scripts, admin plugins)
- Internal documentation and design documents
- Configuration examples and templates

**Pain Points:**
1. **Bloated Distribution:** Users get 200+ MB including tests, docs, admin tools
2. **Security Risk:** Admin tools and internal docs exposed to end users
3. **Complexity:** Users see development artifacts they don't need
4. **Configuration Confusion:** Multiple config templates, unclear which to use

### Desired State

**Clean User Distribution:**
- Only production-ready CORTEX features
- Minimal footprint (~20-30 MB)
- No admin tools or development artifacts
- Single, clear configuration process
- Automated setup with visual feedback

---

## 🏗️ Architecture Design

### Two-Tier Distribution Model

```
CORTEX Repository (Development)
├── src/                          → INCLUDE (production code)
├── prompts/shared/               → INCLUDE (user docs)
├── .github/prompts/              → INCLUDE (entry point)
├── cortex-brain/
│   ├── response-templates.yaml   → INCLUDE (production)
│   ├── brain-protection-rules.yaml → INCLUDE (production)
│   ├── knowledge-graph.yaml      → INCLUDE (production)
│   └── cortex-2.0-design/        → EXCLUDE (admin only)
├── tests/                        → EXCLUDE (dev only)
├── scripts/admin/                → EXCLUDE (admin only)
├── docs/development/             → EXCLUDE (dev only)
└── examples/                     → INCLUDE (user samples)

---

User Distribution Package (Clean)
├── cortex/
│   ├── src/                      ← Production code only
│   ├── prompts/                  ← User-facing docs
│   ├── .github/                  ← Copilot integration
│   ├── cortex-brain/             ← Essential brain files only
│   ├── examples/                 ← Getting started samples
│   ├── cortex.config.template.json
│   ├── requirements.txt
│   └── README.md
└── setup.ps1                     ← Automated installer
```

---

## 📦 Package Structure

### User Package Contents

**Root Structure:**
```
cortex-deployment-v2.0.zip
├── cortex/                       # Main application folder
│   ├── src/                      # Production source code
│   ├── prompts/
│   │   ├── shared/              # User documentation modules
│   │   └── user/                # User entry points
│   ├── .github/
│   │   ├── prompts/
│   │   │   └── CORTEX.prompt.md # Main entry point
│   │   └── copilot-instructions.md
│   ├── cortex-brain/
│   │   ├── response-templates.yaml
│   │   ├── brain-protection-rules.yaml
│   │   ├── knowledge-graph.yaml
│   │   ├── conversation-history.jsonl (empty template)
│   │   └── conversation-context.jsonl (empty template)
│   ├── examples/
│   │   ├── basic-usage/
│   │   ├── advanced-features/
│   │   └── integration-samples/
│   ├── cortex.config.template.json
│   ├── requirements.txt
│   ├── README.md                # Quick start guide
│   └── LICENSE
├── setup.ps1                     # Windows installer
├── setup.sh                      # Mac/Linux installer
└── INSTALLATION.md               # Installation guide
```

---

### Excluded Content (Admin/Dev Only)

**Development Artifacts:**
- `tests/` - Test suite (580+ tests, 15MB)
- `scripts/admin/` - Admin automation scripts
- `.pytest_cache/`, `.coverage*` - Test artifacts
- `.venv/`, `dist/`, `build/` - Build artifacts

**Admin Documentation:**
- `cortex-brain/cortex-2.0-design/` - Design documents (50+ files)
- `cortex-brain/archives/` - Historical documentation
- `docs/development/` - Developer guides
- `workflow_checkpoints/` - Development checkpoints

**Admin Plugins:**
- `src/plugins/design_sync_plugin.py` - Admin tool
- `src/plugins/cleanup_plugin.py` - Admin tool (aggressive mode)
- Development-only plugin features

**Configuration Examples:**
- `cortex.config.example.json` - Keep template only
- Multiple config variations - Consolidate to one

---

### Included Content (User Distribution)

**Production Code:**
- `src/tier0/` - Governance & brain protection
- `src/tier1/` - Conversation memory
- `src/tier2/` - Knowledge graph & learning
- `src/tier3/` - Development context
- `src/cortex_agents/` - 10 specialist agents
- `src/operations/` - Universal operations system
- `src/workflows/` - Workflow engine
- `src/plugins/` - User-facing plugins only

**User Plugins (Included):**
- Platform switch plugin
- Doc refresh plugin (user mode only)
- Response templates
- Context helper (when Phase 11.1 complete)

**User Documentation:**
- `prompts/shared/story.md` - The CORTEX story
- `prompts/shared/setup-guide.md` - Installation guide
- `prompts/shared/technical-reference.md` - API docs
- `prompts/shared/agents-guide.md` - Agent system explained
- `prompts/shared/tracking-guide.md` - Conversation tracking
- `prompts/shared/configuration-reference.md` - Config help

**Entry Points:**
- `.github/prompts/CORTEX.prompt.md` - Main entry point
- `.github/copilot-instructions.md` - Baseline context

**Brain Files:**
- `cortex-brain/response-templates.yaml` - Response templates
- `cortex-brain/brain-protection-rules.yaml` - SKULL rules
- `cortex-brain/knowledge-graph.yaml` - Learning patterns
- Empty conversation files (initialized on first use)

**Examples:**
- `examples/basic-usage/` - Getting started samples
- `examples/advanced-features/` - Advanced usage
- `examples/integration-samples/` - Integration examples

---

## 🔧 Deployment Automation

### Setup Script Design

**Windows: `setup.ps1`**

```powershell
# CORTEX 2.0 Production Deployment - Windows Setup Script
# © 2024-2025 Asif Hussain. All rights reserved.

param(
    [string]$InstallPath = "$env:USERPROFILE\CORTEX",
    [switch]$Force = $false
)

function Show-CORTEXHeader {
    $header = @"
================================================================================
                    CORTEX 2.0 Production Setup
================================================================================

Version:    2.0.0
Platform:   Windows
Author:     Asif Hussain
Copyright:  © 2024-2025 Asif Hussain. All rights reserved.
License:    Proprietary
Repository: https://github.com/asifhussain60/CORTEX

================================================================================
"@
    Write-Host $header -ForegroundColor Cyan
    Write-Host ""
}

function Test-Prerequisites {
    Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow
    
    # Check Python
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Python not found. Please install Python 3.10+ first." -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    
    # Check Git (optional but recommended)
    $gitVersion = git --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Git not found (optional but recommended)" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Git: $gitVersion" -ForegroundColor Green
    }
    
    Write-Host ""
}

function Expand-Package {
    param([string]$PackagePath, [string]$Destination)
    
    Write-Host "📦 Extracting CORTEX package..." -ForegroundColor Yellow
    
    # Find the cortex deployment zip
    $zipFile = Get-ChildItem -Path $PSScriptRoot -Filter "cortex-deployment-*.zip" | Select-Object -First 1
    
    if (-not $zipFile) {
        Write-Host "❌ Deployment package not found!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "   Source: $($zipFile.Name)" -ForegroundColor Gray
    Write-Host "   Destination: $Destination" -ForegroundColor Gray
    
    # Create destination if it doesn't exist
    if (-not (Test-Path $Destination)) {
        New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    }
    
    # Extract zip
    Expand-Archive -Path $zipFile.FullName -DestinationPath $Destination -Force
    
    Write-Host "✅ Package extracted successfully" -ForegroundColor Green
    Write-Host ""
}

function Initialize-Environment {
    param([string]$CortexPath)
    
    Write-Host "🔧 Initializing Python environment..." -ForegroundColor Yellow
    
    Push-Location $CortexPath
    
    try {
        # Create virtual environment
        Write-Host "   Creating virtual environment..." -ForegroundColor Gray
        python -m venv .venv
        
        # Activate and install dependencies
        Write-Host "   Installing dependencies..." -ForegroundColor Gray
        & ".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
        & ".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
        
        Write-Host "✅ Environment initialized" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Environment initialization failed: $_" -ForegroundColor Red
        exit 1
    }
    finally {
        Pop-Location
    }
    
    Write-Host ""
}

function Initialize-Configuration {
    param([string]$CortexPath)
    
    Write-Host "⚙️  Configuring CORTEX..." -ForegroundColor Yellow
    
    $configTemplate = Join-Path $CortexPath "cortex.config.template.json"
    $configFile = Join-Path $CortexPath "cortex.config.json"
    
    if (Test-Path $configFile) {
        Write-Host "   Configuration file already exists, skipping..." -ForegroundColor Gray
    } else {
        # Copy template to config
        Copy-Item $configTemplate $configFile
        
        # Update paths for Windows
        $config = Get-Content $configFile -Raw | ConvertFrom-Json
        $config.cortex_root = $CortexPath
        $config.brain_db_path = Join-Path $CortexPath "cortex-brain\cortex-brain.db"
        $config | ConvertTo-Json -Depth 10 | Set-Content $configFile
        
        Write-Host "✅ Configuration file created: cortex.config.json" -ForegroundColor Green
    }
    
    Write-Host ""
}

function Initialize-Brain {
    param([string]$CortexPath)
    
    Write-Host "🧠 Initializing CORTEX brain..." -ForegroundColor Yellow
    
    Push-Location $CortexPath
    
    try {
        # Initialize Tier 1 (conversation database)
        Write-Host "   Creating Tier 1 conversation database..." -ForegroundColor Gray
        & ".venv\Scripts\python.exe" -c "from src.tier1.conversation_tracker import ConversationTracker; ConversationTracker().initialize()"
        
        Write-Host "✅ Brain initialized" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  Brain initialization skipped (will initialize on first use)" -ForegroundColor Yellow
    }
    finally {
        Pop-Location
    }
    
    Write-Host ""
}

function Move-EntryPoint {
    param([string]$CortexPath, [string]$TargetGitHubPath)
    
    Write-Host "📝 Configuring GitHub Copilot integration..." -ForegroundColor Yellow
    
    # If user provides a target path (e.g., their application's .github folder)
    if ($TargetGitHubPath -and (Test-Path $TargetGitHubPath)) {
        $sourcePrompt = Join-Path $CortexPath ".github\prompts\CORTEX.prompt.md"
        $targetPromptDir = Join-Path $TargetGitHubPath "prompts"
        
        if (-not (Test-Path $targetPromptDir)) {
            New-Item -ItemType Directory -Path $targetPromptDir -Force | Out-Null
        }
        
        $targetPrompt = Join-Path $targetPromptDir "CORTEX.prompt.md"
        Copy-Item $sourcePrompt $targetPrompt -Force
        
        Write-Host "✅ Entry point copied to: $targetPrompt" -ForegroundColor Green
        Write-Host "   Use '/CORTEX' command in GitHub Copilot Chat" -ForegroundColor Gray
    } else {
        Write-Host "   Entry point location: $CortexPath\.github\prompts\CORTEX.prompt.md" -ForegroundColor Gray
        Write-Host "   To integrate with your project, copy to your .github/prompts/ folder" -ForegroundColor Gray
    }
    
    Write-Host ""
}

function Show-CompletionMessage {
    param([string]$InstallPath)
    
    $completion = @"
================================================================================
                    CORTEX 2.0 Installation Complete! 🎉
================================================================================

📁 Installation Path: $InstallPath

🚀 Quick Start:

1. Activate virtual environment:
   PS> cd $InstallPath
   PS> .\.venv\Scripts\Activate.ps1

2. Open VS Code with GitHub Copilot Chat

3. Use CORTEX:
   - Type '/CORTEX help' for available commands
   - Say 'setup environment' to complete setup
   - Say 'tell me the CORTEX story' to learn more

📚 Documentation:
   - Quick Start: $InstallPath\README.md
   - Full Guide: $InstallPath\prompts\shared\setup-guide.md
   - Entry Point: $InstallPath\.github\prompts\CORTEX.prompt.md

⚠️  Next Steps:
   1. Review $InstallPath\cortex.config.json
   2. Set up conversation tracking (see tracking-guide.md)
   3. Start using CORTEX in your projects!

================================================================================
"@
    
    Write-Host $completion -ForegroundColor Cyan
}

# ============================================================================
# Main Installation Flow
# ============================================================================

Show-CORTEXHeader
Test-Prerequisites

Write-Host "📍 Installation path: $InstallPath" -ForegroundColor Cyan
Write-Host ""

# Check if already installed
if ((Test-Path $InstallPath) -and -not $Force) {
    Write-Host "⚠️  CORTEX already installed at: $InstallPath" -ForegroundColor Yellow
    Write-Host "   Use -Force to reinstall" -ForegroundColor Gray
    Write-Host ""
    $response = Read-Host "Continue anyway? (y/N)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Host "Installation cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Run installation steps
Expand-Package -PackagePath $PSScriptRoot -Destination $InstallPath
Initialize-Environment -CortexPath (Join-Path $InstallPath "cortex")
Initialize-Configuration -CortexPath (Join-Path $InstallPath "cortex")
Initialize-Brain -CortexPath (Join-Path $InstallPath "cortex")
Move-EntryPoint -CortexPath (Join-Path $InstallPath "cortex")

Show-CompletionMessage -InstallPath (Join-Path $InstallPath "cortex")

# Optional: Add to PATH
Write-Host "💡 Tip: Add CORTEX to your PATH for easier access" -ForegroundColor Yellow
Write-Host "   [Environment]::SetEnvironmentVariable('CORTEX_ROOT', '$InstallPath\cortex', 'User')" -ForegroundColor Gray
Write-Host ""
```

---

**Mac/Linux: `setup.sh`**

```bash
#!/bin/bash
# CORTEX 2.0 Production Deployment - Mac/Linux Setup Script
# © 2024-2025 Asif Hussain. All rights reserved.

set -e

# Configuration
INSTALL_PATH="${HOME}/CORTEX"
FORCE_INSTALL=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --install-path)
            INSTALL_PATH="$2"
            shift 2
            ;;
        --force)
            FORCE_INSTALL=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

function show_cortex_header() {
    echo -e "${CYAN}================================================================================"
    echo "                    CORTEX 2.0 Production Setup"
    echo "================================================================================"
    echo ""
    echo "Version:    2.0.0"
    echo "Platform:   $(uname -s)"
    echo "Author:     Asif Hussain"
    echo "Copyright:  © 2024-2025 Asif Hussain. All rights reserved."
    echo "License:    Proprietary"
    echo "Repository: https://github.com/asifhussain60/CORTEX"
    echo ""
    echo -e "================================================================================${NC}"
    echo ""
}

function test_prerequisites() {
    echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo -e "${GREEN}✅ Python: ${PYTHON_VERSION}${NC}"
    else
        echo -e "${RED}❌ Python 3 not found. Please install Python 3.10+ first.${NC}"
        exit 1
    fi
    
    # Check Git (optional)
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        echo -e "${GREEN}✅ Git: ${GIT_VERSION}${NC}"
    else
        echo -e "${YELLOW}⚠️  Git not found (optional but recommended)${NC}"
    fi
    
    echo ""
}

function expand_package() {
    echo -e "${YELLOW}📦 Extracting CORTEX package...${NC}"
    
    # Find deployment zip
    ZIP_FILE=$(find "$(dirname "$0")" -name "cortex-deployment-*.zip" -type f | head -n 1)
    
    if [ -z "$ZIP_FILE" ]; then
        echo -e "${RED}❌ Deployment package not found!${NC}"
        exit 1
    fi
    
    echo -e "${GRAY}   Source: $(basename "$ZIP_FILE")${NC}"
    echo -e "${GRAY}   Destination: ${INSTALL_PATH}${NC}"
    
    # Create destination
    mkdir -p "$INSTALL_PATH"
    
    # Extract
    unzip -q "$ZIP_FILE" -d "$INSTALL_PATH"
    
    echo -e "${GREEN}✅ Package extracted successfully${NC}"
    echo ""
}

function initialize_environment() {
    local CORTEX_PATH="$1"
    
    echo -e "${YELLOW}🔧 Initializing Python environment...${NC}"
    
    cd "$CORTEX_PATH"
    
    # Create virtual environment
    echo -e "${GRAY}   Creating virtual environment...${NC}"
    python3 -m venv .venv
    
    # Activate and install dependencies
    echo -e "${GRAY}   Installing dependencies...${NC}"
    .venv/bin/pip install --upgrade pip --quiet
    .venv/bin/pip install -r requirements.txt --quiet
    
    echo -e "${GREEN}✅ Environment initialized${NC}"
    echo ""
}

function initialize_configuration() {
    local CORTEX_PATH="$1"
    
    echo -e "${YELLOW}⚙️  Configuring CORTEX...${NC}"
    
    local CONFIG_TEMPLATE="${CORTEX_PATH}/cortex.config.template.json"
    local CONFIG_FILE="${CORTEX_PATH}/cortex.config.json"
    
    if [ -f "$CONFIG_FILE" ]; then
        echo -e "${GRAY}   Configuration file already exists, skipping...${NC}"
    else
        # Copy template
        cp "$CONFIG_TEMPLATE" "$CONFIG_FILE"
        
        # Update paths (using sed for Mac/Linux)
        sed -i.bak "s|/path/to/cortex|${CORTEX_PATH}|g" "$CONFIG_FILE"
        rm "${CONFIG_FILE}.bak"
        
        echo -e "${GREEN}✅ Configuration file created: cortex.config.json${NC}"
    fi
    
    echo ""
}

function initialize_brain() {
    local CORTEX_PATH="$1"
    
    echo -e "${YELLOW}🧠 Initializing CORTEX brain...${NC}"
    
    cd "$CORTEX_PATH"
    
    # Initialize Tier 1
    echo -e "${GRAY}   Creating Tier 1 conversation database...${NC}"
    .venv/bin/python -c "from src.tier1.conversation_tracker import ConversationTracker; ConversationTracker().initialize()" || \
        echo -e "${YELLOW}⚠️  Brain initialization skipped (will initialize on first use)${NC}"
    
    echo -e "${GREEN}✅ Brain initialized${NC}"
    echo ""
}

function show_completion_message() {
    local INSTALL_PATH="$1"
    
    echo -e "${CYAN}================================================================================"
    echo "                    CORTEX 2.0 Installation Complete! 🎉"
    echo "================================================================================"
    echo ""
    echo "📁 Installation Path: ${INSTALL_PATH}"
    echo ""
    echo "🚀 Quick Start:"
    echo ""
    echo "1. Activate virtual environment:"
    echo "   \$ cd ${INSTALL_PATH}"
    echo "   \$ source .venv/bin/activate"
    echo ""
    echo "2. Open VS Code with GitHub Copilot Chat"
    echo ""
    echo "3. Use CORTEX:"
    echo "   - Type '/CORTEX help' for available commands"
    echo "   - Say 'setup environment' to complete setup"
    echo "   - Say 'tell me the CORTEX story' to learn more"
    echo ""
    echo "📚 Documentation:"
    echo "   - Quick Start: ${INSTALL_PATH}/README.md"
    echo "   - Full Guide: ${INSTALL_PATH}/prompts/shared/setup-guide.md"
    echo "   - Entry Point: ${INSTALL_PATH}/.github/prompts/CORTEX.prompt.md"
    echo ""
    echo "⚠️  Next Steps:"
    echo "   1. Review ${INSTALL_PATH}/cortex.config.json"
    echo "   2. Set up conversation tracking (see tracking-guide.md)"
    echo "   3. Start using CORTEX in your projects!"
    echo ""
    echo -e "================================================================================${NC}"
}

# ============================================================================
# Main Installation Flow
# ============================================================================

show_cortex_header
test_prerequisites

echo -e "${CYAN}📍 Installation path: ${INSTALL_PATH}${NC}"
echo ""

# Check if already installed
if [ -d "$INSTALL_PATH" ] && [ "$FORCE_INSTALL" = false ]; then
    echo -e "${YELLOW}⚠️  CORTEX already installed at: ${INSTALL_PATH}${NC}"
    echo -e "${GRAY}   Use --force to reinstall${NC}"
    echo ""
    read -p "Continue anyway? (y/N): " response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
fi

# Run installation steps
expand_package
CORTEX_DIR="${INSTALL_PATH}/cortex"
initialize_environment "$CORTEX_DIR"
initialize_configuration "$CORTEX_DIR"
initialize_brain "$CORTEX_DIR"

show_completion_message "$CORTEX_DIR"

echo -e "${YELLOW}💡 Tip: Add CORTEX to your PATH for easier access${NC}"
echo -e "${GRAY}   export CORTEX_ROOT='${CORTEX_DIR}'${NC}"
echo ""
```

---

## 🔧 Build Script

**PowerShell: `scripts/build-deployment-package.ps1`**

```powershell
# CORTEX 2.0 - Production Deployment Package Builder
# © 2024-2025 Asif Hussain. All rights reserved.

param(
    [string]$Version = "2.0.0",
    [string]$OutputDir = ".\Publish",
    [switch]$Clean = $false
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "▶ $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "   $Message" -ForegroundColor Gray
}

Write-Host @"
================================================================================
          CORTEX 2.0 Production Deployment Package Builder
================================================================================
Version: $Version
Output:  $OutputDir
Clean:   $Clean
================================================================================
"@ -ForegroundColor Cyan

# Clean output directory if requested
if ($Clean -and (Test-Path $OutputDir)) {
    Write-Step "Cleaning output directory..."
    Remove-Item $OutputDir -Recurse -Force
    Write-Success "Output directory cleaned"
}

# Create output structure
Write-Step "Creating package structure..."
$stagingDir = Join-Path $OutputDir "staging\cortex"
New-Item -ItemType Directory -Path $stagingDir -Force | Out-Null
Write-Success "Package structure created"

# Copy production source code
Write-Step "Copying production source code..."
$srcDirs = @("src", "prompts", ".github", "examples")
foreach ($dir in $srcDirs) {
    $source = Join-Path $PSScriptRoot "..\$dir"
    $dest = Join-Path $stagingDir $dir
    
    if (Test-Path $source) {
        Copy-Item $source $dest -Recurse -Force
        Write-Info "Copied: $dir"
    }
}
Write-Success "Source code copied"

# Copy brain files (selective)
Write-Step "Copying CORTEX brain files..."
$brainDir = Join-Path $stagingDir "cortex-brain"
New-Item -ItemType Directory -Path $brainDir -Force | Out-Null

$brainFiles = @(
    "response-templates.yaml",
    "brain-protection-rules.yaml",
    "knowledge-graph.yaml"
)

foreach ($file in $brainFiles) {
    $source = Join-Path $PSScriptRoot "..\cortex-brain\$file"
    if (Test-Path $source) {
        Copy-Item $source $brainDir -Force
        Write-Info "Copied: $file"
    }
}

# Create empty conversation files
New-Item (Join-Path $brainDir "conversation-history.jsonl") -ItemType File -Force | Out-Null
New-Item (Join-Path $brainDir "conversation-context.jsonl") -ItemType File -Force | Out-Null
Write-Success "Brain files copied"

# Copy configuration template
Write-Step "Copying configuration files..."
Copy-Item (Join-Path $PSScriptRoot "..\cortex.config.template.json") $stagingDir -Force
Copy-Item (Join-Path $PSScriptRoot "..\requirements.txt") $stagingDir -Force
Copy-Item (Join-Path $PSScriptRoot "..\LICENSE") $stagingDir -Force -ErrorAction SilentlyContinue
Write-Success "Configuration files copied"

# Create README for users
Write-Step "Generating user README..."
$readme = @"
# CORTEX 2.0 - Production Distribution

**Version:** $Version  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary

---

## Quick Start

1. Run the setup script:
   - Windows: ``.\setup.ps1``
   - Mac/Linux: ``./setup.sh``

2. Follow the installation prompts

3. Start using CORTEX in GitHub Copilot Chat:
   - Type ``/CORTEX help``
   - Say ``setup environment``
   - Say ``tell me the CORTEX story``

---

## Documentation

- **Installation Guide:** ``prompts/shared/setup-guide.md``
- **User Manual:** ``prompts/shared/story.md``
- **Technical Reference:** ``prompts/shared/technical-reference.md``
- **Entry Point:** ``.github/prompts/CORTEX.prompt.md``

---

## Support

- Repository: https://github.com/asifhussain60/CORTEX
- Documentation: See ``prompts/shared/`` directory
- Issues: Contact system administrator

---

**CORTEX 2.0** - Cognitive framework for GitHub Copilot with memory, learning, and strategic planning.
"@
Set-Content (Join-Path $stagingDir "README.md") $readme
Write-Success "README generated"

# Remove admin/dev content
Write-Step "Removing admin/development content..."
$excludePaths = @(
    "cortex-brain\cortex-2.0-design",
    "cortex-brain\archives",
    "tests",
    ".pytest_cache",
    ".coverage*",
    ".venv",
    "dist",
    "build",
    "__pycache__",
    "*.pyc"
)

foreach ($pattern in $excludePaths) {
    Get-ChildItem $stagingDir -Recurse -Filter $pattern -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
}
Write-Success "Admin content removed"

# Copy setup scripts
Write-Step "Copying setup scripts..."
Copy-Item (Join-Path $PSScriptRoot "setup.ps1") (Join-Path $OutputDir "staging\setup.ps1") -Force
Copy-Item (Join-Path $PSScriptRoot "setup.sh") (Join-Path $OutputDir "staging\setup.sh") -Force
Write-Success "Setup scripts copied"

# Create deployment package (zip)
Write-Step "Creating deployment package..."
$packageName = "cortex-deployment-v$Version.zip"
$packagePath = Join-Path $OutputDir $packageName

Compress-Archive -Path (Join-Path $OutputDir "staging\*") -DestinationPath $packagePath -Force
Write-Success "Deployment package created: $packageName"

# Calculate package size
$packageSize = (Get-Item $packagePath).Length / 1MB
Write-Info "Package size: $([math]::Round($packageSize, 2)) MB"

# Generate checksum
Write-Step "Generating checksums..."
$hash = Get-FileHash $packagePath -Algorithm SHA256
$checksumFile = Join-Path $OutputDir "cortex-deployment-v$Version.sha256"
"$($hash.Hash)  $packageName" | Set-Content $checksumFile
Write-Success "Checksum file created"

# Clean up staging
Write-Step "Cleaning up staging files..."
Remove-Item (Join-Path $OutputDir "staging") -Recurse -Force
Write-Success "Staging files removed"

# Summary
Write-Host @"

================================================================================
                    Package Build Complete! 🎉
================================================================================

📦 Package: $packagePath
📊 Size:    $([math]::Round($packageSize, 2)) MB
🔒 SHA256:  $checksumFile

📁 Output Structure:
   Publish/
   ├── cortex-deployment-v$Version.zip
   └── cortex-deployment-v$Version.sha256

🚀 Distribution:
   1. Distribute the .zip file to end users
   2. Users run setup.ps1 (Windows) or setup.sh (Mac/Linux)
   3. CORTEX installs to ~/CORTEX by default

================================================================================
"@ -ForegroundColor Cyan
```

---

## 📊 Package Metrics

### Size Estimates

**Full Development Repository:**
- Total size: ~200 MB
- Tests: ~15 MB
- Docs: ~30 MB
- Admin tools: ~10 MB
- Build artifacts: ~20 MB

**Clean User Package:**
- Production code: ~8 MB
- User docs: ~5 MB
- Brain files: ~2 MB
- Examples: ~3 MB
- Dependencies: ~12 MB (when installed)
- **Total compressed: ~20-25 MB**

### File Counts

**Development Repository:**
- Total files: ~1,200
- Python files: ~250
- Test files: ~150
- Documentation: ~100

**User Package:**
- Total files: ~400
- Python files: ~180 (production only)
- Documentation: ~20 (user-facing only)
- Examples: ~30

---

## 🎯 Success Metrics

**Package Quality:**
- ✅ No admin/dev tools in user package
- ✅ Package size < 30 MB compressed
- ✅ Setup completes in < 2 minutes
- ✅ Works offline (no internet after download)
- ✅ Cross-platform (Windows, Mac, Linux)

**User Experience:**
- ✅ One-click setup script
- ✅ Visual feedback during installation
- ✅ Clear success/error messages
- ✅ Automatic environment configuration
- ✅ Ready to use immediately after setup

---

## 🚀 Implementation Timeline

### Phase 8.1: Build Script (2 hours)
- [ ] Create `build-deployment-package.ps1` script
- [ ] Implement file selection logic (include/exclude)
- [ ] Add compression and checksums
- [ ] Test on Windows

### Phase 8.2: Setup Scripts (3 hours)
- [ ] Create `setup.ps1` (Windows installer)
- [ ] Create `setup.sh` (Mac/Linux installer)
- [ ] Implement CORTEX header display
- [ ] Add prerequisite checks
- [ ] Implement package extraction
- [ ] Add environment initialization
- [ ] Test on all platforms

### Phase 8.3: Documentation (1 hour)
- [ ] Create user-facing README
- [ ] Update INSTALLATION.md
- [ ] Create distribution guide
- [ ] Update status documents

### Phase 8.4: Testing & Validation (2 hours)
- [ ] Test full deployment on Windows
- [ ] Test full deployment on Mac
- [ ] Test full deployment on Linux
- [ ] Verify package contents
- [ ] Validate file exclusions

**Total Effort:** 8 hours

---

## 📚 Related Documents

- `CORTEX2-STATUS.MD` - Overall status (update Phase 8 progress)
- `CORTEX-2.0-IMPLEMENTATION-STATUS.md` - Implementation details
- `Phase-8.1-COMPLETE.md` - Code review plugin (archived)
- User docs: `prompts/shared/setup-guide.md` (existing)

---

## ✅ Acceptance Criteria

**Phase 8 Complete When:**
- [ ] Build script creates clean user package
- [ ] Setup scripts work on all 3 platforms
- [ ] Package size < 30 MB compressed
- [ ] No admin/dev files in package
- [ ] Setup completes successfully on test systems
- [ ] User can run `/CORTEX help` after setup
- [ ] Documentation complete and tested

---

**Status:** 🟡 DESIGN COMPLETE - Ready for Phase 8.1 implementation

**Next Step:** Implement `build-deployment-package.ps1` script

---

*© 2024-2025 Asif Hussain │ CORTEX 2.0 Phase 8 Design Document*
*Last Updated: 2025-11-12*
