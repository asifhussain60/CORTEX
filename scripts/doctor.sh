#!/bin/bash
# CORTEX System Doctor - Quick Commands
# 
# Usage: ./scripts/doctor.sh [command]
#
# Commands:
#   quick     - Quick health check (default)
#   full      - Full diagnostic (dry-run)
#   scan      - Scan for issues only
#   cleanup   - Execute cleanup (with confirmation)
#   report    - Generate health report
#
# Author: Asif Hussain
# Copyright: © 2024-2025 Asif Hussain. All rights reserved.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default command
COMMAND="${1:-quick}"

cd "$PROJECT_ROOT"

case "$COMMAND" in
    quick)
        echo -e "${GREEN}🩺 Running quick health check...${NC}"
        python3 scripts/cortex_system_doctor.py --quick
        ;;
    
    full)
        echo -e "${GREEN}🩺 Running full diagnostic (dry-run)...${NC}"
        python3 scripts/cortex_system_doctor.py
        ;;
    
    scan)
        echo -e "${GREEN}🔍 Scanning for issues...${NC}"
        python3 scripts/cortex_system_doctor.py --phase diagnose --phase scan
        ;;
    
    cleanup)
        echo -e "${YELLOW}⚠️  WARNING: This will execute cleanup operations!${NC}"
        echo ""
        read -p "Are you sure you want to proceed? (y/N) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${GREEN}🧹 Executing cleanup...${NC}"
            python3 scripts/cortex_system_doctor.py --phase cleanup --execute
        else
            echo "Cancelled."
        fi
        ;;
    
    report)
        echo -e "${GREEN}📊 Generating health report...${NC}"
        python3 scripts/cortex_system_doctor.py --phase report
        ;;
    
    validate)
        echo -e "${GREEN}✅ Running validation...${NC}"
        python3 scripts/cortex_system_doctor.py --phase validate
        ;;
    
    help|--help|-h)
        echo "CORTEX System Doctor - Quick Commands"
        echo ""
        echo "Usage: ./scripts/doctor.sh [command]"
        echo ""
        echo "Commands:"
        echo "  quick     - Quick health check (default)"
        echo "  full      - Full diagnostic (dry-run)"
        echo "  scan      - Scan for issues only"
        echo "  cleanup   - Execute cleanup (with confirmation)"
        echo "  validate  - Run validation checks"
        echo "  report    - Generate health report"
        echo "  help      - Show this help message"
        ;;
    
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo "Run './scripts/doctor.sh help' for usage."
        exit 1
        ;;
esac
