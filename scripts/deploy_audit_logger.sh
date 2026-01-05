#!/bin/bash
###############################################################################
# CORTEX Audit Logger Deployment Script
# Version: 1.0.0
# Purpose: Automated deployment with validation and safety checks
###############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Configuration
ENVIRONMENT="${CORTEX_ENV:-development}"
CONFIG_FILE="${PROJECT_ROOT}/cortex-brain/config/audit-logging-${ENVIRONMENT}.yaml"
LOG_BASE_PATH="${LOG_BASE_PATH:-logs/audit}"
DB_PATH="${DB_PATH:-cortex-brain/cortex-brain.db}"

# Flags
DRY_RUN=false
SKIP_VALIDATION=false
FORCE=false

###############################################################################
# Utility Functions
###############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "Required command '$1' not found"
        exit 1
    fi
}

###############################################################################
# Pre-Flight Checks
###############################################################################

pre_flight_checks() {
    log_info "Running pre-flight checks..."
    
    # Check required commands
    check_command "python3"
    check_command "yaml"
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    log_info "Python version: $PYTHON_VERSION"
    
    # Check project root
    if [ ! -d "$PROJECT_ROOT" ]; then
        log_error "Project root not found: $PROJECT_ROOT"
        exit 1
    fi
    
    # Check configuration file
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "Configuration file not found: $CONFIG_FILE"
        exit 1
    fi
    
    log_success "Pre-flight checks passed"
}

###############################################################################
# Configuration Validation
###############################################################################

validate_config() {
    log_info "Validating configuration..."
    
    if [ "$SKIP_VALIDATION" = true ]; then
        log_warning "Skipping configuration validation (--skip-validation)"
        return 0
    fi
    
    # Validate YAML syntax
    if ! python3 -c "import yaml; yaml.safe_load(open('$CONFIG_FILE'))" 2>/dev/null; then
        log_error "Invalid YAML syntax in configuration file"
        exit 1
    fi
    
    # Check required fields
    python3 <<EOF
import yaml
with open('$CONFIG_FILE', 'r') as f:
    config = yaml.safe_load(f)
    
required_fields = [
    'audit_logging.enabled',
    'audit_logging.environment',
    'audit_logging.log_level',
    'audit_logging.file.base_path'
]

def get_nested(data, path):
    keys = path.split('.')
    value = data
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value

missing = []
for field in required_fields:
    if get_nested(config, field) is None:
        missing.append(field)

if missing:
    print(f"Missing required fields: {', '.join(missing)}")
    exit(1)
EOF
    
    if [ $? -ne 0 ]; then
        log_error "Configuration validation failed"
        exit 1
    fi
    
    log_success "Configuration validation passed"
}

###############################################################################
# Directory Creation
###############################################################################

create_directories() {
    log_info "Creating log directories..."
    
    # Get base path from config
    BASE_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['audit_logging']['file']['base_path'])")
    
    # Create directory structure
    DIRS=(
        "$BASE_PATH"
        "$BASE_PATH/planning_v5"
        "$BASE_PATH/ado_v2"
        "$BASE_PATH/vacuum_v2"
        "$BASE_PATH/cleanup_v2"
        "$BASE_PATH/investigation_v2"
        "$BASE_PATH/tdd_v4"
        "$BASE_PATH/debug_v2"
        "$BASE_PATH/refinement_v2"
        "$BASE_PATH/maintenance_v2"
        "$BASE_PATH/sanitization_v2"
        "$BASE_PATH/master_orchestrator"
        "$BASE_PATH/archives"
    )
    
    for dir in "${DIRS[@]}"; do
        if [ "$DRY_RUN" = true ]; then
            log_info "[DRY RUN] Would create directory: $dir"
        else
            mkdir -p "$dir"
            log_success "Created directory: $dir"
        fi
    done
}

###############################################################################
# Permission Setup
###############################################################################

set_permissions() {
    log_info "Setting file permissions..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would set permissions on log directories"
        return 0
    fi
    
    BASE_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['audit_logging']['file']['base_path'])")
    
    # Set directory permissions (0750 = rwxr-x---)
    find "$BASE_PATH" -type d -exec chmod 0750 {} \;
    log_success "Set directory permissions: 0750"
    
    # Set file permissions for future files (0600 = rw-------)
    # This is handled by the audit logger at runtime
    log_info "File permissions (0600) will be set by audit logger at runtime"
}

###############################################################################
# Database Initialization
###############################################################################

init_database() {
    log_info "Initializing audit logger database..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would initialize database schema"
        return 0
    fi
    
    # Check if database exists
    if [ -f "$DB_PATH" ]; then
        log_warning "Database already exists: $DB_PATH"
        
        if [ "$FORCE" = false ]; then
            read -p "Reinitialize database? This will backup existing data (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Skipping database initialization"
                return 0
            fi
        fi
        
        # Backup existing database
        BACKUP_PATH="${DB_PATH}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$DB_PATH" "$BACKUP_PATH"
        log_success "Backed up database to: $BACKUP_PATH"
    fi
    
    # Run database migrations (if any)
    if [ -f "${PROJECT_ROOT}/cortex-brain/schema.sql" ]; then
        python3 <<EOF
import sqlite3
conn = sqlite3.connect('$DB_PATH')
with open('${PROJECT_ROOT}/cortex-brain/schema.sql', 'r') as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
print("Database schema initialized")
EOF
        log_success "Database schema initialized"
    else
        log_warning "No schema file found, skipping database initialization"
    fi
}

###############################################################################
# Dependency Check
###############################################################################

check_dependencies() {
    log_info "Checking Python dependencies..."
    
    REQUIRED_PACKAGES=(
        "yaml"
        "cryptography"
        "asyncio"
    )
    
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if ! python3 -c "import $package" 2>/dev/null; then
            log_error "Required Python package not found: $package"
            log_info "Install with: pip install $package"
            exit 1
        fi
    done
    
    log_success "All dependencies satisfied"
}

###############################################################################
# Service Restart (if applicable)
###############################################################################

restart_service() {
    log_info "Checking for service restart..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would restart CORTEX service"
        return 0
    fi
    
    # Check if systemd service exists
    if systemctl is-active --quiet cortex 2>/dev/null; then
        log_info "Restarting CORTEX service..."
        sudo systemctl restart cortex
        log_success "Service restarted"
    else
        log_warning "No systemd service found, skipping restart"
        log_info "Manual restart may be required"
    fi
}

###############################################################################
# Deployment Verification
###############################################################################

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check directories exist
    BASE_PATH=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['audit_logging']['file']['base_path'])")
    
    if [ ! -d "$BASE_PATH" ]; then
        log_error "Log directory not created: $BASE_PATH"
        return 1
    fi
    
    # Check permissions
    PERMS=$(stat -f "%OLp" "$BASE_PATH" 2>/dev/null || stat -c "%a" "$BASE_PATH")
    if [ "$PERMS" != "750" ]; then
        log_warning "Directory permissions unexpected: $PERMS (expected 750)"
    fi
    
    # Test write access
    TEST_FILE="${BASE_PATH}/.deployment_test"
    if touch "$TEST_FILE" 2>/dev/null; then
        rm "$TEST_FILE"
        log_success "Write access verified"
    else
        log_error "No write access to log directory"
        return 1
    fi
    
    log_success "Deployment verification passed"
}

###############################################################################
# Rollback
###############################################################################

rollback() {
    log_warning "Rolling back deployment..."
    
    # Restore database backup if exists
    LATEST_BACKUP=$(ls -t "${DB_PATH}.backup."* 2>/dev/null | head -n1)
    if [ -n "$LATEST_BACKUP" ]; then
        cp "$LATEST_BACKUP" "$DB_PATH"
        log_success "Restored database from backup: $LATEST_BACKUP"
    fi
    
    log_warning "Rollback complete"
    exit 1
}

###############################################################################
# Main Deployment
###############################################################################

deploy() {
    log_info "Starting CORTEX Audit Logger deployment..."
    log_info "Environment: $ENVIRONMENT"
    log_info "Configuration: $CONFIG_FILE"
    
    # Run deployment steps
    pre_flight_checks
    validate_config
    check_dependencies
    create_directories
    set_permissions
    init_database
    
    # Verify deployment
    if ! verify_deployment; then
        log_error "Deployment verification failed"
        if [ "$FORCE" = false ]; then
            rollback
        fi
    fi
    
    # Restart service if needed
    restart_service
    
    log_success "Deployment complete!"
    log_info "Audit logging is now configured for environment: $ENVIRONMENT"
}

###############################################################################
# CLI Arguments
###############################################################################

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Deploy CORTEX Audit Logger

Options:
    -e, --environment ENV    Deployment environment (dev|staging|prod) [default: development]
    -c, --config FILE        Configuration file path
    -d, --dry-run            Perform dry run without making changes
    -s, --skip-validation    Skip configuration validation
    -f, --force              Force deployment without prompts
    -h, --help               Show this help message

Examples:
    $0                                    # Deploy to development
    $0 --environment production           # Deploy to production
    $0 --dry-run                          # Dry run
    $0 --config custom-config.yaml        # Custom config

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            CONFIG_FILE="${PROJECT_ROOT}/cortex-brain/config/audit-logging-${ENVIRONMENT}.yaml"
            shift 2
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -s|--skip-validation)
            SKIP_VALIDATION=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

###############################################################################
# Execute Deployment
###############################################################################

# Trap errors and rollback
trap rollback ERR

# Run deployment
deploy

exit 0
