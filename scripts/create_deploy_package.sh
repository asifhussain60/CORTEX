#!/usr/bin/env bash
#
# CORTEX Production Deploy Package Creator
#
# Creates a production-ready tarball with all necessary files,
# excluding development artifacts.
#
# Author: Asif Hussain
# Version: 3.0.0
# Date: December 3, 2025
#
# Usage:
#   ./scripts/create_deploy_package.sh [version]
#
# Example:
#   ./scripts/create_deploy_package.sh 3.0.0

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
CORTEX_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-$(cat VERSION 2>/dev/null || echo '3.0.0')}"
PACKAGE_NAME="cortex-${VERSION}-production"
OUTPUT_DIR="${CORTEX_ROOT}/deploy-packages"
PACKAGE_PATH="${OUTPUT_DIR}/${PACKAGE_NAME}.tar.gz"

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}📦 CORTEX Production Deploy Package Creator${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""
echo -e "${GREEN}Version:${NC}      ${VERSION}"
echo -e "${GREEN}Source:${NC}       ${CORTEX_ROOT}"
echo -e "${GREEN}Package:${NC}      ${PACKAGE_NAME}.tar.gz"
echo ""

# Step 1: Run Deploy Gate Validator
echo -e "${YELLOW}Step 1: Running Deploy Gate Validation...${NC}"
if python3 "${CORTEX_ROOT}/src/operations/modules/deploy/deploy_gate_validator.py"; then
    echo -e "${GREEN}✅ All deployment gates passed!${NC}"
    echo ""
else
    echo -e "${RED}❌ Deploy gate validation failed!${NC}"
    echo -e "${RED}Fix failed gates before creating deploy package.${NC}"
    exit 1
fi

# Step 2: Create output directory
echo -e "${YELLOW}Step 2: Creating output directory...${NC}"
mkdir -p "${OUTPUT_DIR}"
echo -e "${GREEN}✅ Output directory ready: ${OUTPUT_DIR}${NC}"
echo ""

# Step 3: Create temporary staging directory
echo -e "${YELLOW}Step 3: Creating staging directory...${NC}"
STAGING_DIR=$(mktemp -d)
STAGING_CORTEX="${STAGING_DIR}/${PACKAGE_NAME}"
mkdir -p "${STAGING_CORTEX}"
echo -e "${GREEN}✅ Staging directory: ${STAGING_DIR}${NC}"
echo ""

# Step 4: Copy production files
echo -e "${YELLOW}Step 4: Copying production files...${NC}"

# Core source code
echo "  📁 Copying src/..."
cp -r "${CORTEX_ROOT}/src" "${STAGING_CORTEX}/"

# Brain data and configuration
echo "  🧠 Copying cortex-brain/..."
mkdir -p "${STAGING_CORTEX}/cortex-brain"
cp "${CORTEX_ROOT}/cortex-brain/brain-protection-rules.yaml" "${STAGING_CORTEX}/cortex-brain/" 2>/dev/null || true
cp "${CORTEX_ROOT}/cortex-brain/response-templates.yaml" "${STAGING_CORTEX}/cortex-brain/" 2>/dev/null || true
cp "${CORTEX_ROOT}/cortex-brain/tier1-working-memory.db" "${STAGING_CORTEX}/cortex-brain/" 2>/dev/null || true
cp -r "${CORTEX_ROOT}/cortex-brain/admin" "${STAGING_CORTEX}/cortex-brain/" 2>/dev/null || true
cp -r "${CORTEX_ROOT}/cortex-brain/documents" "${STAGING_CORTEX}/cortex-brain/" 2>/dev/null || true
cp -r "${CORTEX_ROOT}/cortex-brain/operations" "${STAGING_CORTEX}/cortex-brain/" 2>/dev/null || true

# Configuration files
echo "  ⚙️  Copying configuration..."
cp "${CORTEX_ROOT}/requirements.txt" "${STAGING_CORTEX}/"
cp "${CORTEX_ROOT}/VERSION" "${STAGING_CORTEX}/"
cp "${CORTEX_ROOT}/cortex.config.template.json" "${STAGING_CORTEX}/"
cp "${CORTEX_ROOT}/README.md" "${STAGING_CORTEX}/" 2>/dev/null || true
cp "${CORTEX_ROOT}/LICENSE" "${STAGING_CORTEX}/" 2>/dev/null || true

# Deployment scripts
echo "  🚀 Copying deployment scripts..."
mkdir -p "${STAGING_CORTEX}/scripts"
cat > "${STAGING_CORTEX}/scripts/install.sh" << 'INSTALL_EOF'
#!/usr/bin/env bash
# CORTEX Production Installation Script

set -e

echo "🧠 CORTEX Production Installation"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "❌ Python 3 not found"; exit 1; }
echo "✅ Python 3 found"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Configure CORTEX
if [ ! -f cortex.config.json ]; then
    echo "Creating cortex.config.json from template..."
    cp cortex.config.template.json cortex.config.json
    echo "⚠️  IMPORTANT: Edit cortex.config.json with your production paths"
fi
echo ""

# Run deploy gate validation
echo "Running deployment validation..."
python3 src/operations/modules/deploy/deploy_gate_validator.py
echo ""

echo "🎉 CORTEX installation complete!"
echo ""
echo "Next steps:"
echo "  1. Edit cortex.config.json with your production paths"
echo "  2. Run: python3 -m src.operations.align"
echo "  3. Start using CORTEX!"
INSTALL_EOF

chmod +x "${STAGING_CORTEX}/scripts/install.sh"

echo -e "${GREEN}✅ Production files copied${NC}"
echo ""

# Step 5: Clean up development artifacts
echo -e "${YELLOW}Step 5: Cleaning development artifacts...${NC}"
find "${STAGING_CORTEX}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${STAGING_CORTEX}" -type f -name "*.pyc" -delete 2>/dev/null || true
find "${STAGING_CORTEX}" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find "${STAGING_CORTEX}" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
rm -rf "${STAGING_CORTEX}/cortex-brain/backups" 2>/dev/null || true
rm -rf "${STAGING_CORTEX}/cortex-brain/cache" 2>/dev/null || true
rm -rf "${STAGING_CORTEX}/cortex-brain/logs" 2>/dev/null || true
echo -e "${GREEN}✅ Development artifacts removed${NC}"
echo ""

# Step 6: Create tarball
echo -e "${YELLOW}Step 6: Creating deployment package...${NC}"
cd "${STAGING_DIR}"
tar -czf "${PACKAGE_PATH}" "${PACKAGE_NAME}"
cd "${CORTEX_ROOT}"
echo -e "${GREEN}✅ Package created: ${PACKAGE_PATH}${NC}"
echo ""

# Step 7: Generate checksums
echo -e "${YELLOW}Step 7: Generating checksums...${NC}"
if command -v sha256sum &> /dev/null; then
    sha256sum "${PACKAGE_PATH}" > "${PACKAGE_PATH}.sha256"
    echo -e "${GREEN}✅ SHA-256: $(cat ${PACKAGE_PATH}.sha256)${NC}"
elif command -v shasum &> /dev/null; then
    shasum -a 256 "${PACKAGE_PATH}" > "${PACKAGE_PATH}.sha256"
    echo -e "${GREEN}✅ SHA-256: $(cat ${PACKAGE_PATH}.sha256)${NC}"
fi
echo ""

# Step 8: Package info
echo -e "${YELLOW}Step 8: Generating package info...${NC}"
PACKAGE_SIZE=$(du -h "${PACKAGE_PATH}" | cut -f1)
cat > "${OUTPUT_DIR}/${PACKAGE_NAME}-info.txt" << INFO_EOF
CORTEX Production Deploy Package
Version: ${VERSION}
Created: $(date)
Package: ${PACKAGE_NAME}.tar.gz
Size: ${PACKAGE_SIZE}

Included Features:
✅ TDD Mastery (RED→GREEN→REFACTOR workflows)
✅ ADO Integration (Azure DevOps work items)
✅ Planning System (Vision API + DoR/DoD)
✅ RCA (Root Cause Analysis)
✅ SWAGGER Estimation (DoR-driven)
✅ Upgrade System (Brain-safe upgrades)
✅ Unified Entry Point (Universal routing)
✅ Git Checkpoint (Checkpoint management)
✅ Lint Validation (Code quality)

Installation:
1. Extract: tar -xzf ${PACKAGE_NAME}.tar.gz
2. Navigate: cd ${PACKAGE_NAME}
3. Run installer: ./scripts/install.sh
4. Configure: Edit cortex.config.json
5. Validate: python3 src/operations/modules/deploy/deploy_gate_validator.py
6. Start: python3 -m src.operations.align

System Requirements:
- Python 3.8+
- 2GB RAM minimum
- 500MB disk space
- Linux/macOS/Windows (with WSL)

Support:
- Documentation: README.md
- License: LICENSE
- Author: Asif Hussain
- GitHub: github.com/asifhussain60/CORTEX
INFO_EOF

echo -e "${GREEN}✅ Package info: ${OUTPUT_DIR}/${PACKAGE_NAME}-info.txt${NC}"
echo ""

# Step 9: Cleanup staging
echo -e "${YELLOW}Step 9: Cleaning up...${NC}"
rm -rf "${STAGING_DIR}"
echo -e "${GREEN}✅ Staging directory removed${NC}"
echo ""

# Summary
echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}📊 Package Creation Summary${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""
echo -e "${GREEN}✅ Package:${NC}     ${PACKAGE_PATH}"
echo -e "${GREEN}✅ Size:${NC}        ${PACKAGE_SIZE}"
echo -e "${GREEN}✅ SHA-256:${NC}     ${PACKAGE_PATH}.sha256"
echo -e "${GREEN}✅ Info:${NC}        ${OUTPUT_DIR}/${PACKAGE_NAME}-info.txt"
echo ""
echo -e "${BLUE}🎉 Production deploy package ready for distribution!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Verify package: tar -tzf ${PACKAGE_PATH} | head -20"
echo "  2. Test deployment in staging environment"
echo "  3. Transfer to production server"
echo "  4. Extract and run ./scripts/install.sh"
echo ""
