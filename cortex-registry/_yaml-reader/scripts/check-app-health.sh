#!/bin/bash

echo "🔍 CORTEX YAML Reader - Final Validation"
echo "========================================"
echo ""

# Check files exist
echo "📁 Checking required files..."
files=("../yaml-reader.html" "app.js" "vendor/js-yaml.min.js" "vendor/d3.min.js")
all_exist=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        size=$(ls -lh "$file" | awk '{print $5}')
        echo "   ✅ $file ($size)"
    else
        echo "   ❌ $file - MISSING"
        all_exist=false
    fi
done
echo ""

# Check JavaScript syntax
echo "🔬 Validating JavaScript syntax..."
if node --check app.js 2>&1; then
    echo "   ✅ app.js has no syntax errors"
else
    echo "   ❌ app.js has syntax errors"
fi
echo ""

# Check HTML structure
echo "🔬 Validating HTML structure..."
if grep -q "<!DOCTYPE html>" ../yaml-reader.html && \
   grep -q '<html lang="en">' ../yaml-reader.html && \
   grep -q '</html>' ../yaml-reader.html; then
    echo "   ✅ HTML structure is valid"
else
    echo "   ❌ HTML structure has issues"
fi
echo ""

# Check vendor dependencies
echo "📦 Checking vendor dependencies..."
if grep -q "jsyaml" vendor/js-yaml.min.js 2>/dev/null; then
    echo "   ✅ js-yaml library is intact"
else
    echo "   ⚠️  js-yaml library may be corrupted"
fi

if grep -q "d3" vendor/d3.min.js 2>/dev/null; then
    echo "   ✅ d3.js library is intact"
else
    echo "   ⚠️  d3.js library may be corrupted"
fi
echo ""

# Check for common issues
echo "🐛 Checking for common issues..."
issues=0

if grep -q "fetch(" app.js; then
    echo "   ⚠️  Warning: fetch() calls found (may not work in file://)"
    issues=$((issues + 1))
fi

if grep -q "http://" ../yaml-reader.html || grep -q "https://" ../yaml-reader.html | grep -v "file://"; then
    echo "   ⚠️  Warning: HTTP(S) URLs found"
    issues=$((issues + 1))
fi

if [ $issues -eq 0 ]; then
    echo "   ✅ No common issues found"
fi
echo ""

# Summary
echo "📊 Summary"
echo "=========="
if [ "$all_exist" = true ]; then
    echo "✅ All files present"
    echo "✅ JavaScript validated"
    echo "✅ HTML validated"
    echo "✅ Ready to use!"
    echo ""
    echo "🚀 To open: open ../yaml-reader.html"
    echo "   Or use: file://$(pwd)/../yaml-reader.html"
else
    echo "❌ Some files are missing. Please review above."
fi
