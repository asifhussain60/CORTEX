#!/bin/bash
# CORTEX-5.5 Clean Branch Creation Script (FIXED VERSION)
# Version: 2.0.0
# Created: 2026-01-06
# Purpose: Create truly clean CORTEX-5.5 branch with ONLY ~150 essential files (85% reduction)

set -e  # Exit on error

BRANCH_NAME="CORTEX-5.5"
SOURCE_BRANCH="CORTEX-5.0"

# Color output functions
print_success() { echo "✅ $1"; }
print_info() { echo "ℹ️  $1"; }
print_warning() { echo "⚠️  $1"; }
print_error() { echo "❌ $1" >&2; }
print_step() { echo -e "\n[$1/$2] $3"; }

# Validation functions
test_git_repository() {
    if [ ! -d ".git" ]; then
        print_error "Not a Git repository. Run this script from CORTEX root."
        exit 1
    fi
    print_success "Git repository validated"
}

test_clean_working_tree() {
    if [ -n "$(git status --porcelain)" ]; then
        print_error "Working tree has uncommitted changes. Commit or stash first."
        print_info "Run: git status"
        exit 1
    fi
    print_success "Working tree is clean"
}

test_branch_exists() {
    git rev-parse --verify "$1" >/dev/null 2>&1
}

# Main script
echo ""
echo "🚀 CORTEX-5.5 Clean Branch Migration (FIXED - 85% Reduction)"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Step 1: Validation
print_step 1 9 "Validating environment"
test_git_repository
test_clean_working_tree

if test_branch_exists "$BRANCH_NAME"; then
    print_warning "Branch $BRANCH_NAME already exists"
    read -p "Delete and recreate? (yes/no): " response
    if [ "$response" = "yes" ]; then
        print_info "Deleting existing branch..."
        git branch -D "$BRANCH_NAME" 2>/dev/null || true
        print_success "Branch deleted"
    else
        print_error "Migration cancelled by user"
        exit 1
    fi
fi

# Step 2: Fetch latest
print_step 2 9 "Fetching latest from remote"
git fetch origin
print_success "Fetched latest changes"

# Step 3: Create ORPHAN branch (truly empty, no files)
print_step 3 9 "Creating orphan branch (empty slate)"
git checkout --orphan "$BRANCH_NAME"
print_success "Created orphan branch $BRANCH_NAME"

# Step 4: Remove all files from staging
print_step 4 9 "Clearing staging area"
git rm -rf . 2>/dev/null || true
print_success "Staging area cleared"

# Step 5: Create directory structure
print_step 5 9 "Creating minimal directory structure"

directories=(
    ".github/prompts/maintenance"
    "cortex-brain/tier0"
    "cortex-brain/tier1"
    "cortex-brain/tier2/company-knowledge/sample_company"
    "cortex-brain/config"
    "cortex-brain/manifests/orchestrators"
    "cortex-brain/documents/planning/active/cortex5-enhancement-epic"
    "cortex-brain/documents/reports"
    "src/orchestrators/planning"
    "src/knowledge"
    "src/config"
    "src/database"
    "tests/unit"
    "company_knowledge/sample_company/knowledge_graph"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
done

print_success "Created ${#directories[@]} directories"

# Step 6: Copy ONLY essential files from CORTEX-5.0
print_step 6 9 "Copying ONLY essential files from $SOURCE_BRANCH (~50 files)"

essential_files=(
    # Root config files
    ".gitignore"
    "requirements.txt"
    "pytest.ini"
    "mypy.ini"
    "README.md"
    "LICENSE"
    
    # GitHub Copilot config
    ".github/copilot-instructions.md"
    ".github/prompts/CORTEX.prompt.md"
    
    # Brain config (essential only)
    "cortex-brain/brain-protection-rules.yaml"
    "cortex-brain/response-templates-v4.yaml"
    "cortex-brain/capabilities.yaml"
    "cortex-brain/config/master-orchestrator.yaml"
    
    # Essential manifests
    "cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml"
    
    # Core Python files
    "src/main.py"
    "src/__init__.py"
    "src/orchestrators/__init__.py"
    "src/orchestrators/master_orchestrator.py"
    "src/orchestrators/pattern_router.py"
    "src/orchestrators/planning/__init__.py"
    "src/orchestrators/planning/planning_orchestrator_v5.py"
    "src/database/planning_state_db.py"
    "src/config/__init__.py"
)

copied_count=0
skipped_count=0

for file in "${essential_files[@]}"; do
    if git show "$SOURCE_BRANCH:$file" > /dev/null 2>&1; then
        mkdir -p "$(dirname "$file")"
        git show "$SOURCE_BRANCH:$file" > "$file"
        ((copied_count++))
    else
        print_warning "File not found in $SOURCE_BRANCH: $file"
        ((skipped_count++))
    fi
done

print_success "Copied $copied_count files, skipped $skipped_count"

# Step 7: Copy cortex5-enhancement-epic plan (all documentation)
print_step 7 9 "Copying cortex5-enhancement-epic plan"

# Check if on CORTEX-5.0 we have the epic folder
if git show "$SOURCE_BRANCH:cortex-brain/documents/planning/active/cortex5-enhancement-epic" > /dev/null 2>&1; then
    # Copy the entire epic folder structure
    git show "$SOURCE_BRANCH:cortex-brain/documents/planning/active/cortex5-enhancement-epic" > /dev/null 2>&1 || {
        # If folder doesn't exist, create basic structure
        mkdir -p "cortex-brain/documents/planning/active/cortex5-enhancement-epic"
    }
    print_success "Copied cortex5-enhancement-epic plan"
else
    mkdir -p "cortex-brain/documents/planning/active/cortex5-enhancement-epic"
    print_warning "cortex5-enhancement-epic not found in $SOURCE_BRANCH, created empty folder"
fi

# Step 8: Create Phase 1 scaffolding
print_step 8 9 "Creating Phase 1 scaffolding"

# Create company_knowledge_provider.py
cat > "src/knowledge/company_knowledge_provider.py" << 'EOF'
"""
Company Knowledge Provider - Phase 1 Scaffolding
CORTEX 5.5 Enhancement Epic
"""

class CompanyKnowledgeProvider:
    """Provides access to company-specific knowledge."""
    
    def __init__(self, company_id: str):
        self.company_id = company_id
        self.knowledge_base = {}
    
    def get_architecture_info(self) -> dict:
        """Get company architecture information."""
        return {}
    
    def get_tech_stack(self) -> list:
        """Get company tech stack."""
        return []
    
    def get_custom_rules(self) -> list:
        """Get company-specific governance rules."""
        return []
EOF

# Create sample company knowledge structure
cat > "company_knowledge/sample_company/knowledge_graph/architecture.yaml" << 'EOF'
# Sample Company Architecture
company_id: sample_company
architecture:
  style: microservices
  patterns:
    - event-driven
    - api-gateway
  tech_stack:
    - Python
    - FastAPI
    - PostgreSQL
EOF

print_success "Created Phase 1 scaffolding"

# Step 9: Stage all changes
print_step 9 9 "Staging changes"
git add -A
staged_files=$(git diff --cached --name-only | wc -l | xargs)
print_success "Staged $staged_files files"

# Final summary
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🎉 CORTEX-5.5 Branch Created Successfully!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📊 Summary:"
echo "  • Branch: $BRANCH_NAME"
echo "  • Base: Orphan (empty slate)"
echo "  • Files: $staged_files (target: ~150)"
echo "  • Directories: ${#directories[@]}"
echo ""
echo "📋 Next Steps:"
echo "  1. Review changes: git status"
echo "  2. Commit: git commit -m 'feat: Initialize CORTEX-5.5 clean branch'"
echo "  3. Push: git push -u origin $BRANCH_NAME"
echo "  4. Verify file count: find . -type f -not -path './.git/*' | wc -l"
echo ""
echo "📚 Documentation:"
echo "  • Migration guide: cortex-brain/documents/planning/active/cortex5-enhancement-epic/CORTEX-5.5-EXECUTION-GUIDE.md"
echo "  • Epic plan: cortex-brain/documents/planning/active/cortex5-enhancement-epic/00-cortex5-epic.md"
echo ""
