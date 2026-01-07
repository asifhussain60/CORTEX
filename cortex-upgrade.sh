#!/bin/bash
# CORTEX Upgrade System - macOS/Linux Bash Script
# Version: 1.0.0 | Author: Asif Hussain | Date: January 6, 2026
# Purpose: Automated upgrade for CORTEX v5.0 on Unix-based systems

set -e  # Exit on error
set -u  # Exit on undefined variable

# Script configuration
readonly CORTEX_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
readonly UPGRADE_DIR="${CORTEX_ROOT}/cortex-brain/documents/upgrades/${TIMESTAMP}"
readonly BACKUP_DIR="${CORTEX_ROOT}/backups/upgrade-${TIMESTAMP}"
readonly LOG_FILE="${UPGRADE_DIR}/upgrade.log"

# Color codes
readonly COLOR_SUCCESS="\033[0;32m"
readonly COLOR_ERROR="\033[0;31m"
readonly COLOR_WARNING="\033[0;33m"
readonly COLOR_INFO="\033[0;36m"
readonly COLOR_HEADER="\033[0;35m"
readonly COLOR_RESET="\033[0m"

# Flags
DRY_RUN=false
AUTO_APPROVE=false
SKIP_BACKUP=false
ROLLBACK_TO=""

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

write_header() {
    echo -e "\n${COLOR_HEADER}$(printf '=%.0s' {1..80})${COLOR_RESET}"
    echo -e "${COLOR_HEADER}$1${COLOR_RESET}"
    echo -e "${COLOR_HEADER}$(printf '=%.0s' {1..80})${COLOR_RESET}\n"
}

write_phase() {
    echo -e "\n${COLOR_INFO}[PHASE $1]${COLOR_RESET} $2"
    echo -e "${COLOR_INFO}$(printf -- '-%.0s' {1..80})${COLOR_RESET}"
}

write_success() {
    echo -e "${COLOR_SUCCESS}✅ $1${COLOR_RESET}"
}

write_error() {
    echo -e "${COLOR_ERROR}❌ $1${COLOR_RESET}"
}

write_warning() {
    echo -e "${COLOR_WARNING}⚠️  $1${COLOR_RESET}"
}

write_info() {
    echo -e "${COLOR_INFO}ℹ️  $1${COLOR_RESET}"
}

write_log() {
    local level="${2:-INFO}"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    local log_entry="[${timestamp}] [${level}] $1"
    
    # Create log directory if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "$log_entry" >> "$LOG_FILE"
}

get_user_confirmation() {
    local message="$1"
    local default="${2:-n}"
    
    if [ "$AUTO_APPROVE" = true ]; then
        write_info "Auto-approved: $message"
        return 0
    fi
    
    if [ "$default" = "y" ]; then
        read -p "$message [Y/n] " -n 1 -r
    else
        read -p "$message [y/N] " -n 1 -r
    fi
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

# =============================================================================
# PRE-FLIGHT VALIDATION (Phase P01)
# =============================================================================

test_pre_flight_checks() {
    write_phase "P01" "Pre-Flight Validation"
    
    local checks=()
    
    # Check 1: Git working directory clean
    write_info "Checking git working directory..."
    if [ -n "$(git status --porcelain)" ]; then
        write_warning "Working directory has uncommitted changes:"
        git status --short
        checks+=("Git Status:false:Uncommitted changes detected")
        
        if ! get_user_confirmation "Continue despite uncommitted changes?"; then
            write_error "Aborted by user due to uncommitted changes"
            exit 1
        fi
    else
        write_success "Working directory clean"
        checks+=("Git Status:true")
    fi
    
    # Check 2: Current branch
    write_info "Checking current branch..."
    local current_branch=$(git branch --show-current)
    if [ "$current_branch" != "CORTEX-5.0" ]; then
        write_warning "Current branch: $current_branch (expected: CORTEX-5.0)"
        checks+=("Git Branch:false:Not on CORTEX-5.0 branch")
    else
        write_success "On CORTEX-5.0 branch"
        checks+=("Git Branch:true")
    fi
    
    # Check 3: Python version
    write_info "Checking Python version..."
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version 2>&1)
        if [[ $python_version =~ Python\ 3\.([1-9][1-9]|[2-9][0-9])\. ]]; then
            write_success "Python version: $python_version"
            checks+=("Python Version:true")
        else
            write_error "Python 3.11+ required (found: $python_version)"
            checks+=("Python Version:false:Python 3.11+ required")
            exit 1
        fi
    else
        write_error "python3 not found in PATH"
        exit 1
    fi
    
    # Check 4: Git version
    write_info "Checking Git version..."
    local git_version=$(git --version)
    write_success "Git version: $git_version"
    checks+=("Git Version:true")
    
    # Check 5: Disk space
    write_info "Checking disk space..."
    local free_space=$(df -m . | tail -1 | awk '{print $4}')
    if [ "$free_space" -lt 500 ]; then
        write_warning "Low disk space: ${free_space}MB free"
        checks+=("Disk Space:false:Less than 500MB free")
    else
        write_success "Disk space: ${free_space}MB free"
        checks+=("Disk Space:true")
    fi
    
    # Check 6: Network connectivity
    write_info "Checking network connectivity..."
    if git fetch --dry-run origin CORTEX-5.0 &> /dev/null; then
        write_success "Network connectivity OK"
        checks+=("Network:true")
    else
        write_error "Network connectivity failed"
        checks+=("Network:false:Cannot reach remote")
        exit 1
    fi
    
    # Save pre-flight report
    local report_path="${UPGRADE_DIR}/01-pre-flight-report.json"
    mkdir -p "$(dirname "$report_path")"
    
    echo "{\"checks\": [" > "$report_path"
    local first=true
    for check in "${checks[@]}"; do
        IFS=':' read -ra parts <<< "$check"
        [ "$first" = false ] && echo "," >> "$report_path"
        echo "  {\"name\": \"${parts[0]}\", \"passed\": ${parts[1]}, \"message\": \"${parts[2]:-}\"}" >> "$report_path"
        first=false
    done
    echo "]}" >> "$report_path"
    
    write_info "Pre-flight report saved: $report_path"
    write_success "Pre-flight validation complete"
}

# =============================================================================
# REMOTE ANALYSIS (Phase P02)
# =============================================================================

get_remote_analysis() {
    write_phase "P02" "Remote Analysis"
    
    # Fetch latest from remote
    write_info "Fetching latest changes from origin/CORTEX-5.0..."
    git fetch origin CORTEX-5.0
    write_success "Fetch complete"
    
    # Get commit diff
    write_info "Analyzing commit differences..."
    local commit_log=$(git log HEAD..origin/CORTEX-5.0 --oneline)
    local commit_count=$(echo "$commit_log" | wc -l | xargs)
    
    if [ "$commit_count" -eq 0 ]; then
        write_success "Already up to date with remote"
        echo "up_to_date"
        return 0
    fi
    
    write_info "Found $commit_count new commits:"
    echo "$commit_log" | sed 's/^/  /'
    
    # Get file diff
    write_info "Analyzing file changes..."
    git diff --stat HEAD..origin/CORTEX-5.0
    
    # Categorize changes by subsystem
    local changed_files=$(git diff --name-only HEAD..origin/CORTEX-5.0)
    
    write_info "Changes by subsystem:"
    echo "  orchestrators: $(echo "$changed_files" | grep "^src/orchestrators/" | wc -l | xargs) files"
    echo "  prompts: $(echo "$changed_files" | grep "^.github/prompts/" | wc -l | xargs) files"
    echo "  documentation: $(echo "$changed_files" | grep "^cortex-brain/documents/" | wc -l | xargs) files"
    echo "  audit_logging: $(echo "$changed_files" | grep "^src/logging/" | wc -l | xargs) files"
    echo "  tests: $(echo "$changed_files" | grep "^tests/" | wc -l | xargs) files"
    
    # Save analysis
    local analysis_path="${UPGRADE_DIR}/02-remote-analysis.json"
    cat > "$analysis_path" << EOF
{
  "up_to_date": false,
  "commit_count": $commit_count,
  "files_changed": $(echo "$changed_files" | wc -l | xargs),
  "timestamp": "$(date -Iseconds)"
}
EOF
    
    # Save diff summary
    local diff_path="${UPGRADE_DIR}/03-diff-summary.md"
    cat > "$diff_path" << EOF
# Remote Analysis - $TIMESTAMP

## Summary
- **Commits:** $commit_count
- **Files Changed:** $(echo "$changed_files" | wc -l | xargs)

## Commits
\`\`\`
$commit_log
\`\`\`

## File Changes
\`\`\`
$(git diff --stat HEAD..origin/CORTEX-5.0)
\`\`\`
EOF
    
    write_success "Remote analysis complete"
    echo "changes_found:$commit_count"
}

# =============================================================================
# BACKUP & ROLLBACK PREPARATION (Phase P03)
# =============================================================================

create_backup() {
    write_phase "P03" "Backup & Rollback Preparation"
    
    if [ "$SKIP_BACKUP" = true ]; then
        write_warning "Skipping backup (not recommended)"
        return
    fi
    
    write_info "Creating backup directory: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    
    # Backup critical files
    local backup_targets=(
        "cortex.config.json"
        ".github/prompts/CORTEX.prompt.md"
        ".github/copilot-instructions.md"
        "cortex-brain/config/master-orchestrator.yaml"
    )
    
    for target in "${backup_targets[@]}"; do
        local source_path="${CORTEX_ROOT}/${target}"
        local dest_path="${BACKUP_DIR}/$(basename "$target")"
        
        if [ -f "$source_path" ]; then
            write_info "Backing up: $target"
            cp "$source_path" "$dest_path"
        fi
    done
    
    # Backup active plans
    local active_plans_source="${CORTEX_ROOT}/cortex-brain/documents/planning/active"
    local active_plans_dest="${BACKUP_DIR}/active-plans"
    
    if [ -d "$active_plans_source" ]; then
        write_info "Backing up active plans..."
        cp -r "$active_plans_source" "$active_plans_dest"
    fi
    
    # Record current state
    local current_commit=$(git rev-parse HEAD)
    local current_branch=$(git branch --show-current)
    
    cat > "${BACKUP_DIR}/manifest.json" << EOF
{
  "timestamp": "$TIMESTAMP",
  "commit_sha": "$current_commit",
  "branch": "$current_branch",
  "python_version": "$(python3 --version 2>&1)",
  "backup_directory": "$BACKUP_DIR"
}
EOF
    
    # Create rollback script
    cat > "${BACKUP_DIR}/rollback.sh" << 'ROLLBACK_SCRIPT'
#!/bin/bash
# CORTEX Rollback Script - Generated TIMESTAMP_PLACEHOLDER
# Restores system to state before upgrade

set -e

CORTEX_ROOT="CORTEX_ROOT_PLACEHOLDER"
BACKUP_DIR="BACKUP_DIR_PLACEHOLDER"
COMMIT_SHA="COMMIT_SHA_PLACEHOLDER"

echo "Starting rollback to commit $COMMIT_SHA..."

# Reset git
echo "Resetting git to $COMMIT_SHA..."
cd "$CORTEX_ROOT"
git reset --hard "$COMMIT_SHA"

# Restore config files
echo "Restoring backed up files..."
cp "${BACKUP_DIR}/cortex.config.json" "${CORTEX_ROOT}/cortex.config.json"
cp "${BACKUP_DIR}/CORTEX.prompt.md" "${CORTEX_ROOT}/.github/prompts/CORTEX.prompt.md"
cp "${BACKUP_DIR}/copilot-instructions.md" "${CORTEX_ROOT}/.github/copilot-instructions.md"
cp "${BACKUP_DIR}/master-orchestrator.yaml" "${CORTEX_ROOT}/cortex-brain/config/master-orchestrator.yaml"

# Restore active plans
echo "Restoring active plans..."
rm -rf "${CORTEX_ROOT}/cortex-brain/documents/planning/active"/*
cp -r "${BACKUP_DIR}/active-plans/"* "${CORTEX_ROOT}/cortex-brain/documents/planning/active/"

# Verify
echo "Verifying rollback..."
python3 -m src.main "help" --format markdown

echo "Rollback complete!"
ROLLBACK_SCRIPT
    
    # Replace placeholders
    sed -i.bak "s|TIMESTAMP_PLACEHOLDER|$TIMESTAMP|g" "${BACKUP_DIR}/rollback.sh"
    sed -i.bak "s|CORTEX_ROOT_PLACEHOLDER|$CORTEX_ROOT|g" "${BACKUP_DIR}/rollback.sh"
    sed -i.bak "s|BACKUP_DIR_PLACEHOLDER|$BACKUP_DIR|g" "${BACKUP_DIR}/rollback.sh"
    sed -i.bak "s|COMMIT_SHA_PLACEHOLDER|$current_commit|g" "${BACKUP_DIR}/rollback.sh"
    rm "${BACKUP_DIR}/rollback.sh.bak"
    
    chmod +x "${BACKUP_DIR}/rollback.sh"
    
    write_success "Backup complete: $BACKUP_DIR"
    write_info "Rollback script: ${BACKUP_DIR}/rollback.sh"
}

# =============================================================================
# GIT PULL & MERGE (Phase P04)
# =============================================================================

invoke_git_pull() {
    local remote_status="$1"
    
    write_phase "P04" "Git Pull & Merge"
    
    if [[ "$remote_status" == "up_to_date" ]]; then
        write_success "Already up to date - skipping git pull"
        return
    fi
    
    local commit_count=$(echo "$remote_status" | cut -d: -f2)
    
    if ! get_user_confirmation "Ready to pull $commit_count commits. Proceed?"; then
        write_error "Aborted by user"
        exit 1
    fi
    
    write_info "Pulling with rebase strategy..."
    if git pull --rebase origin CORTEX-5.0 > "${UPGRADE_DIR}/04-git-pull-log.txt" 2>&1; then
        write_success "Git pull complete"
    else
        write_error "Git pull failed"
        
        # Check for conflicts
        local conflicts=$(git diff --name-only --diff-filter=U)
        if [ -n "$conflicts" ]; then
            write_warning "Merge conflicts detected in:"
            echo "$conflicts" | sed 's/^/  /'
            
            echo "{\"conflicts\": [" > "${UPGRADE_DIR}/05-conflicts.json"
            echo "$conflicts" | awk '{print "\"" $0 "\""}' | paste -sd, >> "${UPGRADE_DIR}/05-conflicts.json"
            echo "]}" >> "${UPGRADE_DIR}/05-conflicts.json"
            
            if get_user_confirmation "Resolve conflicts manually now?"; then
                write_info "Please resolve conflicts and run: git rebase --continue"
                write_info "Then re-run this script to continue upgrade"
                exit 1
            else
                write_info "Rolling back..."
                git rebase --abort
                exit 1
            fi
        fi
        
        exit 1
    fi
}

# =============================================================================
# DEPENDENCY SYNCHRONIZATION (Phase P05)
# =============================================================================

update_dependencies() {
    write_phase "P05" "Dependency Synchronization"
    
    write_info "Installing updated dependencies..."
    python3 -m pip install -r requirements.txt --upgrade > "${UPGRADE_DIR}/07-pip-install-log.txt" 2>&1
    
    # Verify critical packages
    write_info "Verifying critical packages..."
    local critical_packages=("pytest" "pydantic" "yaml" "jinja2" "watchdog" "requests")
    
    for pkg in "${critical_packages[@]}"; do
        if python3 -c "import ${pkg}" 2>/dev/null; then
            write_success "$pkg installed"
        else
            write_error "$pkg verification failed"
            exit 1
        fi
    done
    
    # Test audit logger import
    write_info "Testing audit logger import..."
    if python3 -c "from src.logging.audit_logger import AuditLogger" 2>/dev/null; then
        write_success "Audit logger import successful"
    else
        write_error "Audit logger import failed"
        exit 1
    fi
    
    write_success "Dependencies synchronized"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

start_upgrade() {
    write_header "🚀 CORTEX v5.0 Upgrade System - Unix/Linux"
    echo "Timestamp: $TIMESTAMP"
    echo "Cortex Root: $CORTEX_ROOT"
    
    if [ "$DRY_RUN" = true ]; then
        write_warning "DRY RUN MODE - No changes will be made"
    fi
    
    # Create upgrade directory
    mkdir -p "$UPGRADE_DIR"
    write_info "Upgrade directory: $UPGRADE_DIR"
    
    write_log "Upgrade started" "INFO"
    
    # Phase P01: Pre-Flight Validation
    test_pre_flight_checks
    
    # Phase P02: Remote Analysis
    local remote_analysis=$(get_remote_analysis)
    
    if [[ "$remote_analysis" == "up_to_date" ]]; then
        write_success "System is already up to date!"
        write_info "No upgrade needed."
        exit 0
    fi
    
    if [ "$DRY_RUN" = true ]; then
        write_info "Dry run complete - no changes made"
        write_info "Review analysis: $UPGRADE_DIR"
        exit 0
    fi
    
    # Phase P03: Backup & Rollback Preparation
    create_backup
    
    # Phase P04: Git Pull & Merge
    invoke_git_pull "$remote_analysis"
    
    # Phase P05: Dependency Synchronization
    update_dependencies
    
    # Phase P06-P12: Invoke Python orchestrator for remaining phases
    write_header "🛡️ Invoking Python Orchestrator for Advanced Phases"
    write_info "Phases P06-P12 will be executed by Python orchestrator..."
    
    local python_command="python3 -m src.main \"upgrade cortex phases 06-12\" --format markdown"
    write_info "Command: $python_command"
    
    eval "$python_command"
    
    write_header "🎉 CORTEX Upgrade Complete!"
    write_success "All phases executed successfully"
    write_info "Upgrade documentation: $UPGRADE_DIR"
    write_info "Backup location: $BACKUP_DIR"
    write_info "Executive summary: ${UPGRADE_DIR}/EXECUTIVE-SUMMARY.md"
    
    write_log "Upgrade completed successfully" "INFO"
}

# =============================================================================
# ROLLBACK EXECUTION
# =============================================================================

start_rollback() {
    local timestamp="$1"
    
    write_header "🔄 CORTEX Rollback System"
    
    local rollback_dir="${CORTEX_ROOT}/backups/upgrade-${timestamp}"
    
    if [ ! -d "$rollback_dir" ]; then
        write_error "Backup not found: $rollback_dir"
        exit 1
    fi
    
    local rollback_script="${rollback_dir}/rollback.sh"
    
    if [ ! -f "$rollback_script" ]; then
        write_error "Rollback script not found: $rollback_script"
        exit 1
    fi
    
    if get_user_confirmation "Execute rollback to $timestamp?"; then
        bash "$rollback_script"
    else
        write_info "Rollback cancelled"
    fi
}

# =============================================================================
# ARGUMENT PARSING & ENTRY POINT
# =============================================================================

show_usage() {
    cat << EOF
CORTEX Upgrade System - Unix/Linux

Usage: $0 [OPTIONS]

OPTIONS:
    --dry-run           Analyze changes without making modifications
    --auto-approve      Skip confirmation prompts (use with caution)
    --skip-backup       Skip backup creation (not recommended)
    --rollback-to TIME  Rollback to specific upgrade timestamp
    -h, --help          Show this help message

EXAMPLES:
    $0                          # Interactive upgrade
    $0 --dry-run                # Analyze without changes
    $0 --auto-approve           # Automated upgrade (CI/CD)
    $0 --rollback-to 20260106_143022  # Rollback
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --auto-approve)
            AUTO_APPROVE=true
            shift
            ;;
        --skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --rollback-to)
            ROLLBACK_TO="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Entry point
if [ -n "$ROLLBACK_TO" ]; then
    start_rollback "$ROLLBACK_TO"
else
    start_upgrade
fi
