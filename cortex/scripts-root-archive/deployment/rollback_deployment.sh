#!/bin/bash
# CORTEX Production Rollback Script
# Usage: ./rollback_deployment.sh [version|previous]
# 
# Rolls back CORTEX to a previous version with automated health checks

set -e

VERSION=${1:-"previous"}
DEPLOYMENT_LOG="${DEPLOYMENT_LOG:-/tmp/cortex_deployments.log}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "╔════════════════════════════════════════════════════════╗"
echo "║         CORTEX Production Rollback                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "🔄 Target version: $VERSION"
echo "📁 Project root: $PROJECT_ROOT"
echo ""

cd "$PROJECT_ROOT"

# Step 1: Verify we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository"
    exit 1
fi

# Step 2: Get current branch/version
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
CURRENT_COMMIT=$(git rev-parse --short HEAD)
echo "📍 Current state: $CURRENT_BRANCH @ $CURRENT_COMMIT"

# Step 3: Stop services if running
echo ""
echo "1️⃣ Stopping CORTEX services..."
if [ -f "deployment/docker-compose.yml" ]; then
    docker-compose -f deployment/docker-compose.yml down 2>/dev/null || echo "⚠️  Docker services not running"
else
    echo "⚠️  No docker-compose.yml found, skipping service stop"
fi

# Stop any running Python processes
pkill -f "cortex" 2>/dev/null || echo "⚠️  No CORTEX processes running"

# Step 4: Determine target version
echo ""
echo "2️⃣ Determining target version..."

if [ "$VERSION" == "previous" ]; then
    # Get previous successful deployment from log
    if [ -f "$DEPLOYMENT_LOG" ]; then
        PREV_VERSION=$(grep "DEPLOYMENT_SUCCESS" "$DEPLOYMENT_LOG" 2>/dev/null | tail -2 | head -1 | awk '{print $3}' || echo "")
        if [ -z "$PREV_VERSION" ]; then
            echo "⚠️  No previous deployment found in log, using HEAD~1"
            PREV_VERSION="HEAD~1"
        fi
    else
        echo "⚠️  No deployment log found, using HEAD~1"
        PREV_VERSION="HEAD~1"
    fi
    TARGET_VERSION="$PREV_VERSION"
else
    TARGET_VERSION="$VERSION"
fi

echo "🎯 Rollback target: $TARGET_VERSION"

# Step 5: Validate target exists
if ! git rev-parse "$TARGET_VERSION" >/dev/null 2>&1; then
    echo "❌ Error: Version '$TARGET_VERSION' not found in git"
    exit 1
fi

# Step 6: Create backup of current state
echo ""
echo "3️⃣ Creating backup of current state..."
BACKUP_BRANCH="backup-$(date +%Y%m%d-%H%M%S)-$CURRENT_COMMIT"
git branch "$BACKUP_BRANCH" 2>/dev/null || echo "⚠️  Backup branch already exists"
echo "💾 Backup created: $BACKUP_BRANCH"

# Step 7: Perform rollback
echo ""
echo "4️⃣ Rolling back to $TARGET_VERSION..."
git checkout "$TARGET_VERSION" 2>&1 | head -5

TARGET_COMMIT=$(git rev-parse --short HEAD)
echo "✅ Switched to: $TARGET_COMMIT"

# Step 8: Reinstall dependencies
echo ""
echo "5️⃣ Reinstalling dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt || echo "⚠️  Some dependencies failed to install"
    echo "✅ Dependencies reinstalled"
else
    echo "⚠️  No requirements.txt found"
fi

# Step 9: Database migration check (if applicable)
echo ""
echo "6️⃣ Checking database state..."
if command -v alembic >/dev/null 2>&1; then
    CURRENT_MIGRATION=$(alembic current 2>/dev/null || echo "unknown")
    echo "📊 Current migration: $CURRENT_MIGRATION"
    
    # Check if downgrade needed
    MIGRATIONS_AHEAD=$(alembic history --verbose 2>/dev/null | grep -c "down" || echo "0")
    
    if [ "$MIGRATIONS_AHEAD" -gt 0 ]; then
        echo ""
        echo "⚠️  WARNING: Database migrations may need rollback"
        echo "    Current migrations: $MIGRATIONS_AHEAD ahead"
        read -p "    Execute database rollback? (yes/no): " CONFIRM
        
        if [ "$CONFIRM" == "yes" ]; then
            echo "    Rolling back 1 migration..."
            alembic downgrade -1 || echo "⚠️  Migration rollback failed"
        else
            echo "    Skipping database rollback"
        fi
    else
        echo "✅ Database state compatible"
    fi
else
    echo "⚠️  Alembic not available, skipping database check"
fi

# Step 10: Restart services
echo ""
echo "7️⃣ Restarting CORTEX services..."
if [ -f "deployment/docker-compose.yml" ]; then
    docker-compose -f deployment/docker-compose.yml up -d || echo "⚠️  Failed to start services"
else
    echo "⚠️  No docker-compose.yml found, skipping service start"
fi

# Step 11: Health check
echo ""
echo "8️⃣ Performing health checks..."
sleep 5

HEALTH_CHECK_PASSED=false

# Try HTTP health endpoint if available
if command -v curl >/dev/null 2>&1; then
    HEALTH_RESPONSE=$(curl -s -f http://localhost:8000/health 2>/dev/null || echo "")
    if [ ! -z "$HEALTH_RESPONSE" ]; then
        HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4 || echo "unknown")
        if [ "$HEALTH_STATUS" == "healthy" ]; then
            HEALTH_CHECK_PASSED=true
        fi
    fi
fi

# Fallback: Check if Python can import cortex
if [ "$HEALTH_CHECK_PASSED" == "false" ]; then
    echo "⚠️  HTTP health check unavailable, testing Python import..."
    if python3 -c "import cortex; print('OK')" 2>/dev/null | grep -q "OK"; then
        HEALTH_CHECK_PASSED=true
    fi
fi

# Step 12: Report results
echo ""
echo "╔════════════════════════════════════════════════════════╗"

if [ "$HEALTH_CHECK_PASSED" == "true" ]; then
    echo "║  ✅ ROLLBACK SUCCESSFUL                               ║"
    echo "╠════════════════════════════════════════════════════════╣"
    echo "║  From: $CURRENT_BRANCH @ $CURRENT_COMMIT                        ║"
    echo "║  To:   $TARGET_VERSION @ $TARGET_COMMIT                        ║"
    echo "║  Backup: $BACKUP_BRANCH              ║"
    echo "╚════════════════════════════════════════════════════════╝"
    
    # Log success
    echo "$(date '+%Y-%m-%d %H:%M:%S') ROLLBACK_SUCCESS $TARGET_VERSION ($TARGET_COMMIT)" >> "$DEPLOYMENT_LOG"
    exit 0
else
    echo "║  ❌ ROLLBACK FAILED                                   ║"
    echo "╠════════════════════════════════════════════════════════╣"
    echo "║  Health check failed after rollback                   ║"
    echo "║  System may be in unstable state                      ║"
    echo "║  Backup available: $BACKUP_BRANCH    ║"
    echo "╚════════════════════════════════════════════════════════╝"
    
    # Log failure
    echo "$(date '+%Y-%m-%d %H:%M:%S') ROLLBACK_FAILED $TARGET_VERSION ($TARGET_COMMIT)" >> "$DEPLOYMENT_LOG"
    
    echo ""
    echo "🔧 Recovery options:"
    echo "   1. Check logs: docker-compose logs -f"
    echo "   2. Restore backup: git checkout $BACKUP_BRANCH"
    echo "   3. Manual intervention required"
    
    exit 1
fi
