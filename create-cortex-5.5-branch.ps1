#!/usr/bin/env pwsh
# CORTEX-5.5 Branch Creation Script
# Version: 1.0.0
# Created: 2026-01-06
# Purpose: Create clean CORTEX-5.5 branch with essential files only

# Script configuration
$ErrorActionPreference = "Stop"
$BRANCH_NAME = "CORTEX-5.5"
$SOURCE_BRANCH = "CORTEX-5.0"
$BASE_BRANCH = "main"

# Color output functions
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Step { param($step, $total, $msg) Write-Host "`n[$step/$total] $msg" -ForegroundColor Magenta }

# Validation functions
function Test-GitRepository {
    if (-not (Test-Path ".git")) {
        Write-Error "Not a Git repository. Run this script from CORTEX root."
        exit 1
    }
    Write-Success "Git repository validated"
}

function Test-BranchExists {
    param($branchName)
    $branches = git branch --list $branchName
    return ($null -ne $branches -and $branches.Length -gt 0)
}

function Test-CleanWorkingTree {
    $status = git status --porcelain
    if ($status) {
        Write-Error "Working tree has uncommitted changes. Commit or stash first."
        Write-Info "Run: git status"
        exit 1
    }
    Write-Success "Working tree is clean"
}

# Main script
Write-Host "`n🚀 CORTEX-5.5 Clean Branch Migration" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Step 1: Validation
Write-Step 1 8 "Validating environment"
Test-GitRepository
Test-CleanWorkingTree

if (Test-BranchExists $BRANCH_NAME) {
    Write-Warning "Branch $BRANCH_NAME already exists"
    $response = Read-Host "Delete and recreate? (yes/no)"
    if ($response -eq "yes") {
        Write-Info "Deleting existing branch..."
        git branch -D $BRANCH_NAME
        Write-Success "Branch deleted"
    } else {
        Write-Error "Migration cancelled by user"
        exit 1
    }
}

# Step 2: Fetch latest
Write-Step 2 8 "Fetching latest from remote"
git fetch origin
Write-Success "Fetched latest changes"

# Step 3: Create branch from main
Write-Step 3 8 "Creating branch from $BASE_BRANCH"
git checkout $BASE_BRANCH
git pull origin $BASE_BRANCH
git checkout -b $BRANCH_NAME
Write-Success "Created branch $BRANCH_NAME from $BASE_BRANCH"

# Step 4: Create directory structure
Write-Step 4 8 "Creating directory structure"

$directories = @(
    ".github/prompts/maintenance",
    "cortex-brain/tier0",
    "cortex-brain/tier1",
    "cortex-brain/tier2/company-knowledge/sample_company",
    "cortex-brain/config",
    "cortex-brain/manifests/orchestrators",
    "cortex-brain/documents/planning/active",
    "src/orchestrators/planning",
    "src/orchestrators/ado",
    "src/orchestrators/investigation",
    "src/knowledge",
    "src/config",
    "src/database",
    "src/response_templates",
    "src/logging",
    "src/diagnostics",
    "src/utils",
    "tests/unit",
    "tests/integration"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}
Write-Success "Created $($directories.Count) directories"

# Step 5: Copy essential files from CORTEX-5.0
Write-Step 5 8 "Copying essential files from $SOURCE_BRANCH"

# Define essential files
$essentialFiles = @(
    # Root configuration (7 files)
    ".gitignore",
    "requirements.txt",
    "pytest.ini",
    "mypy.ini",
    "README.md",
    "LICENSE",
    "cortex.config.template.json",
    
    # GitHub Prompts (3 files)
    ".github/copilot-instructions.md",
    ".github/prompts/CORTEX.prompt.md",
    ".github/prompts/maintenance/index.prompt.md",
    
    # Tier 0 Governance (5 files)
    "cortex-brain/brain-protection-rules.yaml",
    "cortex-brain/response-templates-v4.yaml",
    "cortex-brain/TRUTH-SOURCES.yaml",
    "cortex-brain/capabilities.yaml",
    "cortex-brain/tier0/governance-schema.sql",
    
    # Tier 2 Schema
    "cortex-brain/tier2/schema.sql",
    
    # Configuration (8 files)
    "cortex-brain/config/master-orchestrator.yaml",
    "cortex-brain/config/orchestrator-registry.json",
    "cortex-brain/config/planning-v5-default.yaml",
    "cortex-brain/config/ado-v2-default.yaml",
    "cortex-brain/config/cleanup-v2-default.yaml",
    "cortex-brain/config/intent-classification-rules.yaml",
    "cortex-brain/config/plan-schema.yaml",
    "cortex-brain/config/shared.config.json",
    
    # Manifests (11 files)
    "cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml",
    "cortex-brain/manifests/orchestrators/ado-orchestrator-v2.yaml",
    "cortex-brain/manifests/orchestrators/vacuum-orchestrator-v2.yaml",
    "cortex-brain/manifests/orchestrators/cleanup-orchestrator-v2.yaml",
    "cortex-brain/manifests/orchestrators/investigation-orchestrator-v2.yaml",
    "cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml",
    "cortex-brain/manifests/orchestrators/sanitization-orchestrator-v2.yaml",
    "cortex-brain/manifests/orchestrators/debug-orchestrator-manifest.yaml",
    "cortex-brain/manifests/orchestrators/refinement-orchestrator-manifest.yaml",
    "cortex-brain/manifests/orchestrators/holistic-review-orchestrator.yaml",
    "cortex-brain/manifests/orchestrators/manifest-schema.yaml"
)

# Copy files
$copiedCount = 0
$skippedCount = 0

foreach ($file in $essentialFiles) {
    try {
        git checkout $SOURCE_BRANCH -- $file 2>$null
        if ($LASTEXITCODE -eq 0) {
            $copiedCount++
            Write-Host "  ✓ $file" -ForegroundColor Gray
        } else {
            Write-Host "  ⊘ $file (not found in $SOURCE_BRANCH)" -ForegroundColor DarkGray
            $skippedCount++
        }
    } catch {
        Write-Host "  ⊘ $file (error: $_)" -ForegroundColor DarkGray
        $skippedCount++
    }
}

Write-Success "Copied $copiedCount files, skipped $skippedCount"

# Step 6: Copy cortex5-enhancement-epic folder
Write-Step 6 8 "Copying cortex5-enhancement-epic plan"
try {
    git checkout $SOURCE_BRANCH -- "cortex-brain/documents/planning/active/cortex5-enhancement-epic/" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Copied cortex5-enhancement-epic plan"
    } else {
        Write-Warning "cortex5-enhancement-epic not found in $SOURCE_BRANCH"
    }
} catch {
    Write-Warning "Failed to copy epic: $_"
}

# Copy orchestrator docs
git checkout $SOURCE_BRANCH -- "cortex-brain/documents/orchestrators-quick-ref.md" 2>$null
git checkout $SOURCE_BRANCH -- "cortex-brain/documents/cortex-architecture-quick-ref.md" 2>$null

# Step 7: Copy source code (directories)
Write-Step 7 8 "Copying source code modules"

$sourceModules = @(
    "src/main.py",
    "src/__init__.py",
    "src/orchestrators/master_orchestrator.py",
    "src/orchestrators/pattern_router.py",
    "src/orchestrators/state_manager.py",
    "src/orchestrators/execution_engine.py",
    "src/orchestrators/__init__.py"
)

foreach ($module in $sourceModules) {
    git checkout $SOURCE_BRANCH -- $module 2>$null
}

# Copy orchestrator directories (planning, ado, investigation)
git checkout $SOURCE_BRANCH -- "src/orchestrators/planning/" 2>$null
git checkout $SOURCE_BRANCH -- "src/orchestrators/ado/" 2>$null
git checkout $SOURCE_BRANCH -- "src/orchestrators/investigation/" 2>$null

# Copy core systems
git checkout $SOURCE_BRANCH -- "src/config/" 2>$null
git checkout $SOURCE_BRANCH -- "src/database/" 2>$null
git checkout $SOURCE_BRANCH -- "src/response_templates/" 2>$null
git checkout $SOURCE_BRANCH -- "src/logging/" 2>$null
git checkout $SOURCE_BRANCH -- "src/diagnostics/" 2>$null
git checkout $SOURCE_BRANCH -- "src/utils/" 2>$null

# Copy minimal tests
git checkout $SOURCE_BRANCH -- "tests/conftest.py" 2>$null
git checkout $SOURCE_BRANCH -- "tests/__init__.py" 2>$null
git checkout $SOURCE_BRANCH -- "tests/unit/test_master_orchestrator.py" 2>$null
git checkout $SOURCE_BRANCH -- "tests/unit/test_pattern_router.py" 2>$null
git checkout $SOURCE_BRANCH -- "tests/integration/test_orchestrator_routing.py" 2>$null

Write-Success "Copied source code modules"

# Step 8: Create Phase 1 scaffolding
Write-Step 8 8 "Creating Phase 1 scaffolding"

# Create knowledge module files
@"
"""CORTEX Knowledge Extension Layer - Company Knowledge Provider

Phase 1 Deliverable: Enable company-specific knowledge integration
"""

from typing import Dict, Optional, List
from pathlib import Path
import yaml
import json

class CompanyKnowledgeProvider:
    """Queries company-specific knowledge libraries"""
    
    def __init__(self, company_id: str, base_path: Path):
        self.company_id = company_id
        self.base_path = base_path / company_id
        
    def query_architecture(self, topic: str) -> Dict:
        """Query company architecture patterns"""
        # TODO: Implement in Phase 1
        raise NotImplementedError("Phase 1 implementation pending")
        
    def query_tech_stack(self) -> Dict:
        """Query company technology stack"""
        # TODO: Implement in Phase 1
        raise NotImplementedError("Phase 1 implementation pending")
        
    def query_api_catalog(self, api_name: Optional[str] = None) -> List[Dict]:
        """Query company API catalog"""
        # TODO: Implement in Phase 1
        raise NotImplementedError("Phase 1 implementation pending")
        
    def query_coding_standards(self, language: str) -> Dict:
        """Query company coding standards"""
        # TODO: Implement in Phase 1
        raise NotImplementedError("Phase 1 implementation pending")
"@ | Out-File -FilePath "src/knowledge/company_knowledge_provider.py" -Encoding UTF8

@"
"""CORTEX Knowledge Extension Layer - Knowledge Merger

Phase 1 Deliverable: Merge CORTEX core knowledge with company overrides
"""

from typing import Dict

class KnowledgeMerger:
    """Merges CORTEX knowledge with company knowledge"""
    
    def merge_with_cortex_knowledge(self, 
                                    cortex_knowledge: Dict, 
                                    company_knowledge: Dict) -> Dict:
        """Merge company knowledge over CORTEX defaults"""
        # TODO: Implement priority-based merge in Phase 1
        raise NotImplementedError("Phase 1 implementation pending")
"@ | Out-File -FilePath "src/knowledge/knowledge_merger.py" -Encoding UTF8

"# CORTEX Knowledge Module" | Out-File -FilePath "src/knowledge/__init__.py" -Encoding UTF8

# Create sample company knowledge structure
@"
# Sample Company Architecture Guide

**Company ID:** sample_company  
**Tech Stack:** .NET, Azure, SQL Server  
**Architecture Style:** Microservices

## Principles

1. **API-First:** All services expose REST APIs
2. **Event-Driven:** Use Azure Service Bus for async communication
3. **Security:** OAuth2 + Azure AD integration required

## Patterns

- **Repository Pattern:** All data access via repositories
- **CQRS:** Command-query separation for complex domains
- **Circuit Breaker:** Polly for resilience
"@ | Out-File -FilePath "cortex-brain/tier2/company-knowledge/sample_company/architecture.md" -Encoding UTF8

@"
# Sample Company Tech Stack

languages:
  primary: csharp
  secondary: typescript
  
frameworks:
  backend: aspnetcore
  frontend: react
  
cloud:
  provider: azure
  services:
    - app_service
    - sql_database
    - service_bus
    - key_vault
    
databases:
  primary: sql_server
  cache: redis
"@ | Out-File -FilePath "cortex-brain/tier2/company-knowledge/sample_company/tech-stack.yaml" -Encoding UTF8

Write-Success "Created Phase 1 scaffolding"

# Final summary
Write-Host "`n═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🎉 CORTEX-5.5 Branch Created Successfully!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════`n" -ForegroundColor Cyan

Write-Info "Branch: $BRANCH_NAME"
Write-Info "Source: $SOURCE_BRANCH"
Write-Info "Files: ~$copiedCount essential files"
Write-Info "Epic: cortex5-enhancement-epic ready for Phase 1"

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. Review migration: git status" -ForegroundColor White
Write-Host "  2. Commit changes: git add . && git commit -m 'feat: Initialize CORTEX-5.5 clean branch'" -ForegroundColor White
Write-Host "  3. Push to remote: git push -u origin $BRANCH_NAME" -ForegroundColor White
Write-Host "  4. Start Phase 1: Open cortex-brain/documents/planning/active/cortex5-enhancement-epic/phases/phase-01-knowledge-extension.md" -ForegroundColor White
Write-Host ""
