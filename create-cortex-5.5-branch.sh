#!/bin/bash
# CORTEX-5.5 Branch Creation Script (macOS/Linux)
# Version: 1.0.0
# Created: 2026-01-06
# Purpose: Create clean CORTEX-5.5 branch with essential files only

set -e  # Exit on error

BRANCH_NAME="CORTEX-5.5"
SOURCE_BRANCH="CORTEX-5.0"
BASE_BRANCH="main"

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
echo "🚀 CORTEX-5.5 Clean Branch Migration"
echo "═══════════════════════════════════════════════════════"
echo ""

# Step 1: Validation
print_step 1 8 "Validating environment"
test_git_repository
test_clean_working_tree

if test_branch_exists "$BRANCH_NAME"; then
    print_warning "Branch $BRANCH_NAME already exists"
    read -p "Delete and recreate? (yes/no): " response
    if [ "$response" = "yes" ]; then
        print_info "Deleting existing branch..."
        git branch -D "$BRANCH_NAME"
        print_success "Branch deleted"
    else
        print_error "Migration cancelled by user"
        exit 1
    fi
fi

# Step 2: Fetch latest
print_step 2 8 "Fetching latest from remote"
git fetch origin
print_success "Fetched latest changes"

# Step 3: Create branch from main
print_step 3 8 "Creating branch from $BASE_BRANCH"
git checkout "$BASE_BRANCH"
git pull origin "$BASE_BRANCH"
git checkout -b "$BRANCH_NAME"
print_success "Created branch $BRANCH_NAME from $BASE_BRANCH"

# Step 4: Create directory structure
print_step 4 8 "Creating directory structure"

directories=(
    ".github/prompts/maintenance"
    "cortex-brain/tier0"
    "cortex-brain/tier1"
    "cortex-brain/tier2/company-knowledge/sample_company"
    "cortex-brain/config"
    "cortex-brain/manifests/orchestrators"
    "cortex-brain/documents/planning/active"
    "cortex-brain/documents/reports"
    "cortex-brain/documents/upgrades"
    "src/orchestrators/planning"
    "src/orchestrators/ado"
    "src/orchestrators/investigation"
    "src/knowledge"
    "src/config"
    "src/database"
    "src/response_templates"
    "src/logging"
    "src/diagnostics"
    "src/utils"
    "tests/unit"
    "tests/integration"
    "company_knowledge/sample_company/knowledge_graph"
    "company_knowledge/sample_company/orchestrators"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
done

print_success "Created ${#directories[@]} directories"

# Step 5: Copy essential files from CORTEX-5.0
print_step 5 8 "Copying essential files from $SOURCE_BRANCH"

essential_files=(
    ".gitignore"
    "requirements.txt"
    "pytest.ini"
    "mypy.ini"
    "README.md"
    "LICENSE"
    ".github/copilot-instructions.md"
    ".github/prompts/CORTEX.prompt.md"
    "cortex-brain/brain-protection-rules.yaml"
    "cortex-brain/response-templates-v4.yaml"
    "cortex-brain/capabilities.yaml"
    "cortex-brain/config/master-orchestrator.yaml"
    "cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml"
    "src/main.py"
    "src/__init__.py"
    "src/orchestrators/__init__.py"
    "src/orchestrators/master_orchestrator.py"
    "src/orchestrators/pattern_router.py"
    "src/orchestrators/planning/__init__.py"
    "src/orchestrators/planning/planning_orchestrator_v5.py"
    "src/database/planning_state_db.py"
    "src/config/__init__.py"
    "src/utils/__init__.py"
    "src/utils/logger.py"
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

# Step 6: Copy cortex5-enhancement-epic plan
print_step 6 8 "Copying cortex5-enhancement-epic plan"

plan_dir="cortex-brain/documents/planning/active/cortex5-enhancement-epic"
if git show "$SOURCE_BRANCH:$plan_dir" > /dev/null 2>&1; then
    mkdir -p "$plan_dir"
    # Copy entire plan directory
    git checkout "$SOURCE_BRANCH" -- "$plan_dir" 2>/dev/null || {
        print_warning "Could not copy plan directory, will continue"
    }
    print_success "Copied cortex5-enhancement-epic plan"
else
    print_warning "Plan directory not found in $SOURCE_BRANCH"
fi

# Step 7: Create Phase 1 scaffolding
print_step 7 8 "Creating Phase 1 scaffolding"

# Create company knowledge provider stub
cat > src/knowledge/company_knowledge_provider.py <<'EOF'
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
cat > company_knowledge/sample_company/knowledge_graph/architecture.yaml <<'EOF'
# Sample Company Knowledge Graph - Architecture
# This is a template - replace with actual company information

company:
  name: "Sample Company"
  domain: "sample.com"
  
architecture:
  style: "microservices"
  patterns:
    - "event-driven"
    - "api-gateway"
  
tech_stack:
  backend:
    - "Python 3.11"
    - "FastAPI"
  frontend:
    - "React"
    - "TypeScript"
  infrastructure:
    - "AWS"
    - "Docker"
    - "Kubernetes"
EOF

print_success "Created Phase 1 scaffolding"

# Step 8: Stage and summarize
print_step 8 8 "Staging changes"
git add .

file_count=$(git diff --cached --numstat | wc -l | tr -d ' ')
print_success "Staged $file_count files"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "🎉 CORTEX-5.5 Branch Created Successfully!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "📊 Summary:"
echo "  • Branch: $BRANCH_NAME"
echo "  • Base: $BASE_BRANCH"
echo "  • Files: $file_count"
echo "  • Directories: ${#directories[@]}"
echo ""
echo "📋 Next Steps:"
echo "  1. Review changes: git status"
echo "  2. Commit: git commit -m 'feat: Initialize CORTEX-5.5 clean branch'"
echo "  3. Push: git push -u origin $BRANCH_NAME"
echo ""
echo "📚 Documentation:"
echo "  • Migration guide: cortex-brain/documents/planning/active/cortex5-enhancement-epic/CORTEX-5.5-EXECUTION-GUIDE.md"
echo "  • Epic plan: cortex-brain/documents/planning/active/cortex5-enhancement-epic/00-cortex5-epic.md"
echo ""
