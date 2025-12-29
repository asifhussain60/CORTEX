#!/bin/bash

# CORTEX Intelligent UX Dashboard - Setup Script
# Installs dependencies and prepares test environment

set -e

echo "🧠 CORTEX Intelligent UX Dashboard - Setup"
echo "=========================================="
echo ""

# Check Node.js installation
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "   Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "⚠️  Node.js version 18+ required (found: $(node -v))"
    echo "   Please upgrade Node.js from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"
echo ""

# Install npm dependencies
echo "📦 Installing npm dependencies..."
npm install

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
npx playwright install

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Start local server:  npm run serve"
echo "   2. Run tests:           npm test"
echo "   3. Test UI mode:        npm run test:ui"
echo ""
echo "🎯 Dashboard: http://localhost:8080/dashboard.html"
echo ""
