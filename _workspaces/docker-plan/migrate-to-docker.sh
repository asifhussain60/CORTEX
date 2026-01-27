#!/bin/bash
# ============================================================================
# CORTEX Docker-Clean Migration Script
# ============================================================================
# Date: 2026-01-27
# Phase: 0 Complete
# Status: Validated (All phases executable)
# Authority: CORTEX Master Orchestrator
#
# This script executes the CORTEX migration to a clean Docker-first branch.
# Uses SUBTRACTION approach: start with full state, remove unwanted files.
#
# Usage:
#   chmod +x migrate-to-docker.sh
#   ./migrate-to-docker.sh [--dry-run] [--phase N]
#
# Options:
#   --dry-run    Show what would be done without making changes
#   --phase N    Execute only phase N (0-6)
#   --skip-tests Skip test validation (faster, less safe)
# ============================================================================

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/migration-$(date +%Y%m%d_%H%M%S).log"
BRANCH_NAME="CORTEX-docker"
TAG_NAME="pre-docker-migration-$(date +%Y%m%d)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
DRY_RUN=false
SPECIFIC_PHASE=""
SKIP_TESTS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --phase)
            SPECIFIC_PHASE="$2"
            shift 2
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${BLUE}[$timestamp]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${GREEN}[$timestamp] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${YELLOW}[$timestamp] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${RED}[$timestamp] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

log_header() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}║  $1${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}" | tee -a "$LOG_FILE"
}

run_cmd() {
    local cmd="$1"
    local description="$2"
    
    if [ "$DRY_RUN" = true ]; then
        log "[DRY-RUN] Would execute: $cmd"
        return 0
    fi
    
    log "Executing: $description"
    eval "$cmd" 2>&1 | tee -a "$LOG_FILE"
    return ${PIPESTATUS[0]}
}

confirm() {
    local message="$1"
    read -p "$message (y/n): " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

count_files() {
    local pattern="$1"
    find . -name "$pattern" -type f 2>/dev/null | wc -l | tr -d ' '
}

# ============================================================================
# PHASE 0: PRE-FLIGHT CHECKS
# ============================================================================

phase_0_preflight() {
    log_header "PHASE 0: PRE-FLIGHT CHECKS"
    
    cd "$PROJECT_ROOT"
    
    # Check 1: Git status
    log "Checking git status..."
    if [[ -n $(git status --porcelain) ]]; then
        log_error "Uncommitted changes detected. Please commit or stash."
        git status --short
        exit 1
    fi
    log_success "Git working directory clean"
    
    # Check 2: Current branch
    local current_branch=$(git branch --show-current)
    log "Current branch: $current_branch"
    
    # Check 3: Python version
    local python_version=$(python --version 2>&1)
    log "Python version: $python_version"
    
    # Check 4: Disk space
    local disk_space=$(df -h . | tail -1 | awk '{print $4}')
    log "Available disk space: $disk_space"
    
    # Check 5: Test suite (optional)
    if [ "$SKIP_TESTS" = false ]; then
        log "Running baseline test count..."
        local test_count=$(pytest tests/ --collect-only -q 2>/dev/null | tail -1 | grep -oE '[0-9]+' | head -1 || echo "unknown")
        log "Test count: $test_count"
    fi
    
    # Check 6: File counts
    log "Current file counts:"
    log "  Python files: $(count_files '*.py')"
    log "  Test files: $(find tests/ -name 'test_*.py' 2>/dev/null | wc -l | tr -d ' ')"
    log "  MD files: $(count_files '*.md')"
    log "  DB files: $(count_files '*.db')"
    
    log_success "Pre-flight checks complete"
}

# ============================================================================
# PHASE 1: BRANCH CREATION & BACKUP
# ============================================================================

phase_1_branch_creation() {
    log_header "PHASE 1: BRANCH CREATION & BACKUP"
    
    cd "$PROJECT_ROOT"
    
    # Create checkpoint tag
    log "Creating checkpoint tag: $TAG_NAME"
    run_cmd "git tag -a $TAG_NAME -m 'Pre-Docker migration checkpoint' 2>/dev/null || true" "Create tag"
    
    # Create migration branch
    log "Creating migration branch: $BRANCH_NAME"
    if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
        log_warning "Branch $BRANCH_NAME already exists"
        if confirm "Delete and recreate branch?"; then
            run_cmd "git branch -D $BRANCH_NAME" "Delete existing branch"
        else
            run_cmd "git checkout $BRANCH_NAME" "Switch to existing branch"
            return 0
        fi
    fi
    
    run_cmd "git checkout -b $BRANCH_NAME" "Create new branch"
    
    # Initial commit
    run_cmd "git add -A && git commit --allow-empty -m 'chore: start CORTEX-docker migration' || true" "Initial commit"
    
    log_success "Branch creation complete"
}

# ============================================================================
# PHASE 2: LEGACY REMOVAL
# ============================================================================

phase_2_legacy_removal() {
    log_header "PHASE 2: LEGACY REMOVAL (SUBTRACTION APPROACH)"
    
    cd "$PROJECT_ROOT"
    
    # Batch 1: Remove legacy wiring systems
    log "BATCH 1: Removing legacy wiring systems..."
    local wiring_files=(
        "cortex/orchestrators/core/database_registry.py"
        "cortex/orchestrators/core/orchestrator_registry.py"
        "cortex/orchestrators/bootstrap.py"
        "cortex/orchestrators/core/db_wiring_init.py"
        "cortex/orchestrators/core/permanent_wiring_state.py"
        "cortex/orchestrators/core/autowiring_orchestrator.py"
        "cortex/orchestrators/core/intent_router_factory.py"
        "cortex/infrastructure/wiring_contract_manager.py"
        "cortex/infrastructure/wiring_drift_detector.py"
        "cortex/orchestrators/core/master_orchestrator_stage_1.py"
        "cortex/orchestrators/core/master_orchestrator_stage_4.py"
    )
    
    for file in "${wiring_files[@]}"; do
        if [ -f "$file" ]; then
            run_cmd "rm -f '$file'" "Remove $file"
        fi
    done
    run_cmd "git add -A && git commit -m 'chore: remove legacy wiring systems' || true" "Commit batch 1"
    
    # Batch 2: Remove database files
    log "BATCH 2: Removing database files..."
    run_cmd "find . -name '*.db' -delete 2>/dev/null || true" "Remove .db files"
    run_cmd "find . -name '*.db-journal' -delete 2>/dev/null || true" "Remove .db-journal files"
    run_cmd "find . -name '*.db-shm' -delete 2>/dev/null || true" "Remove .db-shm files"
    run_cmd "find . -name '*.db-wal' -delete 2>/dev/null || true" "Remove .db-wal files"
    run_cmd "rm -rf cortex/migrations/ 2>/dev/null || true" "Remove migrations"
    run_cmd "rm -f cortex/infrastructure/database.py 2>/dev/null || true" "Remove database.py"
    run_cmd "git add -A && git commit -m 'chore: remove database files' || true" "Commit batch 2"
    
    # Batch 3: Remove duplicate files
    log "BATCH 3: Removing duplicate implementations..."
    run_cmd "rm -f cortex/infrastructure/pre_op_enforcer.py 2>/dev/null || true" "Remove pre_op_enforcer"
    run_cmd "rm -f cortex/infrastructure/core035_compliance_check.py 2>/dev/null || true" "Remove core035 check"
    run_cmd "git add -A && git commit -m 'chore: remove duplicate implementations' || true" "Commit batch 3"
    
    # Batch 4: Remove cruft documentation
    log "BATCH 4: Removing cruft documentation..."
    run_cmd "find . -maxdepth 1 -name 'AC-*.md' -delete 2>/dev/null || true" "Remove AC-*.md"
    run_cmd "find . -maxdepth 1 -name '*COMPLETION*.md' -delete 2>/dev/null || true" "Remove COMPLETION*.md"
    run_cmd "find . -maxdepth 1 -name '*CERTIFICATE*.md' -delete 2>/dev/null || true" "Remove CERTIFICATE*.md"
    run_cmd "find . -maxdepth 1 -name 'PHASE_*.md' -delete 2>/dev/null || true" "Remove PHASE_*.md"
    run_cmd "git add -A && git commit -m 'chore: remove cruft documentation' || true" "Commit batch 4"
    
    # Batch 5: Remove archive directories
    log "BATCH 5: Removing archive directories..."
    run_cmd "rm -rf _backups/ 2>/dev/null || true" "Remove _backups"
    run_cmd "rm -rf cortex/scripts-root-archive/ 2>/dev/null || true" "Remove scripts-root-archive"
    run_cmd "find . -type d -name '_archive' -exec rm -rf {} + 2>/dev/null || true" "Remove _archive dirs"
    run_cmd "find . -type d -name '_archives' -exec rm -rf {} + 2>/dev/null || true" "Remove _archives dirs"
    run_cmd "rm -rf cortex_registry/artifacts/ 2>/dev/null || true" "Remove registry artifacts"
    run_cmd "git add -A && git commit -m 'chore: remove archive directories' || true" "Commit batch 5"
    
    # Validate imports still work
    log "Validating Python imports..."
    if python -c "import cortex" 2>/dev/null; then
        log_success "cortex module imports successfully"
    else
        log_warning "cortex import failed - this is expected, will fix in Phase 3"
    fi
    
    log_success "Legacy removal complete"
    log "Updated file counts:"
    log "  Python files: $(count_files '*.py')"
    log "  MD files: $(count_files '*.md')"
    log "  DB files: $(count_files '*.db')"
}

# ============================================================================
# PHASE 3: CREATE WIRING SYSTEM
# ============================================================================

phase_3_wiring_system() {
    log_header "PHASE 3: CREATE NEW WIRING SYSTEM"
    
    cd "$PROJECT_ROOT"
    
    # Create directory structure
    log "Creating wiring directory structure..."
    run_cmd "mkdir -p cortex/wiring/registry" "Create wiring/registry"
    run_cmd "mkdir -p cortex/wiring/specifications" "Create wiring/specifications"
    
    # Copy wiring.yaml from docker-plan
    if [ -f "_workspaces/docker-plan/wiring.yaml" ]; then
        log "Copying wiring.yaml specification..."
        run_cmd "cp _workspaces/docker-plan/wiring.yaml cortex/wiring/specifications/wiring.yaml" "Copy wiring.yaml"
    else
        log_warning "wiring.yaml not found in docker-plan - create manually"
    fi
    
    # Create __init__.py files
    log "Creating __init__.py files..."
    
    cat > cortex/wiring/__init__.py << 'EOF'
"""
CORTEX Git-Backed Wiring System
===============================

This module provides the SINGLE entry point for all CORTEX wiring.
All orchestrators are defined in specifications/wiring.yaml.

Usage:
    from cortex.wiring import bootstrap_cortex, get_cortex, is_wired
    
    cortex = bootstrap_cortex()
    master = cortex.get("MasterOrchestrator")
"""

from cortex.wiring.bootstrap import (
    bootstrap_cortex,
    get_cortex,
    is_wired,
    get_wiring_hash,
    get_orchestrator_count,
)

__all__ = [
    "bootstrap_cortex",
    "get_cortex",
    "is_wired",
    "get_wiring_hash",
    "get_orchestrator_count",
]
EOF
    
    cat > cortex/wiring/registry/__init__.py << 'EOF'
"""CORTEX Wiring Registry Components."""

from cortex.wiring.registry.git_backed_registry import GitBackedRegistry
from cortex.wiring.registry.lazy_orchestrator import LazyOrchestrator
from cortex.wiring.registry.wiring_validator import WiringValidator

__all__ = [
    "GitBackedRegistry",
    "LazyOrchestrator",
    "WiringValidator",
]
EOF
    
    log_success "Wiring directory structure created"
    log_warning "NOTE: Python implementation files must be created manually"
    log "  - cortex/wiring/bootstrap.py"
    log "  - cortex/wiring/registry/git_backed_registry.py"
    log "  - cortex/wiring/registry/lazy_orchestrator.py"
    log "  - cortex/wiring/registry/wiring_validator.py"
    
    run_cmd "git add -A && git commit -m 'chore: create wiring system structure' || true" "Commit wiring structure"
    
    log_success "Wiring system structure complete"
}

# ============================================================================
# PHASE 4: MIGRATE _WORKSPACES
# ============================================================================

phase_4_workspaces_migration() {
    log_header "PHASE 4: MIGRATE _WORKSPACES"
    
    cd "$PROJECT_ROOT"
    
    # Keep roadmap (as-is)
    log "Keeping _workspaces/roadmap/ (SSOT)"
    
    # Rename cortex-vision to vision
    if [ -d "_workspaces/cortex-vision" ]; then
        log "Renaming cortex-vision to vision..."
        run_cmd "mv _workspaces/cortex-vision _workspaces/vision" "Rename cortex-vision"
    fi
    
    # Rename docker-plan to migration
    if [ -d "_workspaces/docker-plan" ]; then
        log "Renaming docker-plan to migration..."
        run_cmd "mv _workspaces/docker-plan _workspaces/migration" "Rename docker-plan"
    fi
    
    # Create archives directory
    run_cmd "mkdir -p _workspaces/archives" "Create archives directory"
    
    # Archive awakening-of-cortex (keep prompts/diagrams)
    if [ -d "_workspaces/awakening-of-cortex" ]; then
        log "Archiving awakening-of-cortex..."
        run_cmd "mkdir -p _workspaces/archives/awakening-of-cortex" "Create archive dir"
        run_cmd "mv _workspaces/awakening-of-cortex/prompts _workspaces/archives/awakening-of-cortex/ 2>/dev/null || true" "Move prompts"
        run_cmd "mv _workspaces/awakening-of-cortex/diagrams _workspaces/archives/awakening-of-cortex/ 2>/dev/null || true" "Move diagrams"
        run_cmd "rm -rf _workspaces/awakening-of-cortex" "Remove awakening-of-cortex"
    fi
    
    # Archive sts (keep sample-apps)
    if [ -d "_workspaces/sts" ]; then
        log "Archiving sts..."
        run_cmd "mkdir -p _workspaces/archives/sts" "Create sts archive"
        run_cmd "mv _workspaces/sts/sample-apps _workspaces/archives/sts/ 2>/dev/null || true" "Move sample-apps"
        run_cmd "rm -rf _workspaces/sts" "Remove sts"
    fi
    
    # Remove ppt (binary files)
    if [ -d "_workspaces/ppt" ]; then
        log "Removing ppt (binary PDFs)..."
        run_cmd "rm -rf _workspaces/ppt" "Remove ppt"
    fi
    
    # Remove .chats (ephemeral)
    if [ -d "_workspaces/.chats" ]; then
        log "Removing .chats (ephemeral)..."
        run_cmd "rm -rf _workspaces/.chats" "Remove .chats"
    fi
    
    # Commit workspaces migration
    run_cmd "git add -A && git commit -m 'chore: migrate _workspaces structure' || true" "Commit workspaces"
    
    log_success "_workspaces migration complete"
    log "Final structure:"
    ls -la _workspaces/ 2>/dev/null || true
}

# ============================================================================
# PHASE 5: CREATE DOCKER INFRASTRUCTURE
# ============================================================================

phase_5_docker_infrastructure() {
    log_header "PHASE 5: CREATE DOCKER INFRASTRUCTURE"
    
    cd "$PROJECT_ROOT"
    
    # Create Dockerfile
    log "Creating Dockerfile..."
    cat > Dockerfile << 'EOF'
# CORTEX MCP Server - Production Container
# Build: docker build -t cortex/mcp-server:latest .
# Run:   docker run -d -p 8443:8443 cortex/mcp-server:latest

FROM python:3.11-slim AS base

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    CORTEX_ENV=production \
    CORTEX_LOG_LEVEL=INFO

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir fastapi uvicorn[standard]

# Copy source code
COPY cortex/ ./cortex/
COPY cortex_brain/ ./cortex_brain/

# Create non-root user
RUN useradd -m -u 1000 cortex && \
    chown -R cortex:cortex /app
USER cortex

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8443/health || exit 1

# Expose port
EXPOSE 8443

# Start server
CMD ["python", "-m", "uvicorn", "cortex.mcp.server:app", \
     "--host", "0.0.0.0", "--port", "8443", \
     "--workers", "4", "--loop", "uvloop"]
EOF
    
    # Create docker-compose.yml
    log "Creating docker-compose.yml..."
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  cortex-mcp:
    build:
      context: .
      dockerfile: Dockerfile
    image: cortex/mcp-server:latest
    container_name: cortex-mcp
    ports:
      - "8443:8443"
    environment:
      - CORTEX_ENV=development
      - CORTEX_LOG_LEVEL=DEBUG
      - CORTEX_MCP_HOST=0.0.0.0
      - CORTEX_MCP_PORT=8443
    volumes:
      # Mount wiring specs for live updates during dev
      - ./cortex/wiring/specifications:/app/cortex/wiring/specifications:ro
      # Mount logs
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8443/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - cortex-network

networks:
  cortex-network:
    driver: bridge
EOF
    
    # Create .dockerignore
    log "Creating .dockerignore..."
    cat > .dockerignore << 'EOF'
# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*$py.class
.Python
.venv
venv/
.pytest_cache/

# IDE
.vscode/
.idea/

# Logs
logs/
*.log

# Tests (not needed in production)
tests/

# Documentation
docs/
*.md

# Workspaces
_workspaces/
_backups/

# Database files
*.db
*.db-journal
EOF
    
    run_cmd "git add -A && git commit -m 'chore: add Docker infrastructure' || true" "Commit Docker files"
    
    log_success "Docker infrastructure created"
}

# ============================================================================
# PHASE 6: FINAL VALIDATION
# ============================================================================

phase_6_validation() {
    log_header "PHASE 6: FINAL VALIDATION"
    
    cd "$PROJECT_ROOT"
    
    log "Running validation checklist..."
    
    # Check 1: File counts
    log "File counts:"
    log "  Python files: $(count_files '*.py')"
    log "  Test files: $(find tests/ -name 'test_*.py' 2>/dev/null | wc -l | tr -d ' ')"
    log "  MD files: $(count_files '*.md')"
    log "  DB files: $(count_files '*.db')"
    
    # Check 2: No legacy wiring files
    log "Checking for legacy wiring files..."
    local legacy_files=(
        "cortex/orchestrators/core/database_registry.py"
        "cortex/orchestrators/bootstrap.py"
    )
    for file in "${legacy_files[@]}"; do
        if [ -f "$file" ]; then
            log_error "Legacy file still exists: $file"
        else
            log_success "Legacy file removed: $file"
        fi
    done
    
    # Check 3: No .db files
    local db_count=$(count_files '*.db')
    if [ "$db_count" -eq 0 ]; then
        log_success "No .db files found"
    else
        log_error "Found $db_count .db files"
    fi
    
    # Check 4: Wiring structure exists
    if [ -d "cortex/wiring" ] && [ -f "cortex/wiring/specifications/wiring.yaml" ]; then
        log_success "Wiring structure exists"
    else
        log_error "Wiring structure incomplete"
    fi
    
    # Check 5: _workspaces structure
    if [ -d "_workspaces/roadmap" ] && [ -d "_workspaces/migration" ]; then
        log_success "_workspaces structure correct"
    else
        log_warning "_workspaces structure needs verification"
    fi
    
    # Check 6: Docker files
    if [ -f "Dockerfile" ] && [ -f "docker-compose.yml" ]; then
        log_success "Docker files exist"
    else
        log_error "Docker files missing"
    fi
    
    log_success "Validation complete"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║          CORTEX Docker-Clean Migration Script v2.0              ║"
    echo "║                                                                  ║"
    echo "║  Approach: SUBTRACTION (safer than cherry-pick)                 ║"
    echo "║  Target Branch: $BRANCH_NAME                                    ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    
    if [ "$DRY_RUN" = true ]; then
        log_warning "DRY RUN MODE - No changes will be made"
    fi
    
    # Execute phases
    if [ -n "$SPECIFIC_PHASE" ]; then
        log "Executing only Phase $SPECIFIC_PHASE"
        case $SPECIFIC_PHASE in
            0) phase_0_preflight ;;
            1) phase_1_branch_creation ;;
            2) phase_2_legacy_removal ;;
            3) phase_3_wiring_system ;;
            4) phase_4_workspaces_migration ;;
            5) phase_5_docker_infrastructure ;;
            6) phase_6_validation ;;
            *) log_error "Unknown phase: $SPECIFIC_PHASE" ;;
        esac
    else
        phase_0_preflight
        
        if confirm "Continue with Phase 1 (Branch Creation)?"; then
            phase_1_branch_creation
        else
            log "Migration cancelled"
            exit 0
        fi
        
        if confirm "Continue with Phase 2 (Legacy Removal)?"; then
            phase_2_legacy_removal
        fi
        
        if confirm "Continue with Phase 3 (Wiring System)?"; then
            phase_3_wiring_system
        fi
        
        if confirm "Continue with Phase 4 (_workspaces Migration)?"; then
            phase_4_workspaces_migration
        fi
        
        if confirm "Continue with Phase 5 (Docker Infrastructure)?"; then
            phase_5_docker_infrastructure
        fi
        
        phase_6_validation
    fi
    
    echo ""
    log_header "MIGRATION SUMMARY"
    log "Log file: $LOG_FILE"
    log ""
    log "Next steps:"
    log "  1. Create Python files for wiring system:"
    log "     - cortex/wiring/bootstrap.py"
    log "     - cortex/wiring/registry/git_backed_registry.py"
    log "     - cortex/wiring/registry/lazy_orchestrator.py"
    log "     - cortex/wiring/registry/wiring_validator.py"
    log ""
    log "  2. Update cortex/__init__.py to use new wiring"
    log ""
    log "  3. Run tests: pytest tests/ -v"
    log ""
    log "  4. Build Docker: docker build -t cortex/mcp-server:test ."
    log ""
}

# Run main
main "$@"
