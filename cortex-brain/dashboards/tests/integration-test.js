#!/usr/bin/env node

/**
 * Dashboard Integration Test Suite
 * 
 * Validates all file paths, imports, and dependencies are correct
 * relative to index.html in the dashboard UI.
 * 
 * Run: node tests/integration-test.js
 * 
 * Author: Asif Hussain
 * Date: December 7, 2025
 */

const fs = require('fs');
const path = require('path');

// ANSI color codes for output
const colors = {
    reset: '\x1b[0m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m'
};

// Test results tracker
const results = {
    passed: 0,
    failed: 0,
    warnings: 0,
    errors: []
};

// Base paths
const dashboardRoot = path.join(__dirname, '..');
const uiRoot = path.join(dashboardRoot, 'ui');
const dataRoot = path.join(dashboardRoot, 'data');

/**
 * Log test result
 */
function log(type, message, detail = '') {
    const icons = { pass: '✅', fail: '❌', warn: '⚠️ ', info: 'ℹ️ ' };
    const color = type === 'pass' ? colors.green : type === 'fail' ? colors.red : type === 'warn' ? colors.yellow : colors.cyan;
    
    console.log(`${color}${icons[type]} ${message}${colors.reset}`);
    if (detail) console.log(`   ${colors.cyan}→${colors.reset} ${detail}`);
}

/**
 * Test: Check if file exists
 */
function testFileExists(relativePath, basePath = uiRoot) {
    const fullPath = path.join(basePath, relativePath);
    const exists = fs.existsSync(fullPath);
    
    if (exists) {
        results.passed++;
        log('pass', `File exists: ${relativePath}`);
    } else {
        results.failed++;
        results.errors.push(`Missing file: ${relativePath}`);
        log('fail', `File missing: ${relativePath}`, fullPath);
    }
    
    return exists;
}

/**
 * Test: Extract script sources from HTML
 */
function extractScriptSources(htmlPath) {
    const content = fs.readFileSync(htmlPath, 'utf-8');
    const scriptRegex = /<script[^>]+src=["']([^"']+)["']/g;
    const moduleRegex = /<script[^>]+type=["']module["'][^>]+src=["']([^"']+)["']/g;
    
    const scripts = [];
    const modules = [];
    
    let match;
    while ((match = scriptRegex.exec(content)) !== null) {
        scripts.push(match[1]);
    }
    
    while ((match = moduleRegex.exec(content)) !== null) {
        modules.push(match[1]);
    }
    
    return { scripts, modules };
}

/**
 * Test: Extract container IDs from HTML
 */
function extractContainerIds(htmlPath) {
    const content = fs.readFileSync(htmlPath, 'utf-8');
    const idRegex = /id=["']([^"']+)["']/g;
    
    const ids = [];
    let match;
    while ((match = idRegex.exec(content)) !== null) {
        ids.push(match[1]);
    }
    
    return ids;
}

/**
 * Test: Parse ES6 imports from JS file
 */
function extractImports(jsPath) {
    if (!fs.existsSync(jsPath)) return [];
    
    const content = fs.readFileSync(jsPath, 'utf-8');
    const importRegex = /import\s+.*?\s+from\s+['"]([^'"]+)['"]/g;
    
    const imports = [];
    let match;
    while ((match = importRegex.exec(content)) !== null) {
        imports.push(match[1]);
    }
    
    return imports;
}

/**
 * Test: Validate import path resolution
 */
function testImportPath(importPath, sourceFile) {
    const sourceDir = path.dirname(sourceFile);
    const resolvedPath = path.resolve(sourceDir, importPath);
    
    // Try with .js extension if not present
    let finalPath = resolvedPath;
    if (!fs.existsSync(finalPath) && !resolvedPath.endsWith('.js')) {
        finalPath = `${resolvedPath}.js`;
    }
    
    const exists = fs.existsSync(finalPath);
    const relativePath = path.relative(uiRoot, finalPath);
    
    if (exists) {
        results.passed++;
        log('pass', `Import resolves: ${importPath}`, `from ${path.relative(uiRoot, sourceFile)}`);
    } else {
        results.failed++;
        results.errors.push(`Broken import: ${importPath} in ${path.relative(uiRoot, sourceFile)}`);
        log('fail', `Import broken: ${importPath}`, `from ${path.relative(uiRoot, sourceFile)}`);
    }
    
    return exists;
}

/**
 * Test: Check container IDs referenced in JS
 */
function extractGetElementById(jsPath) {
    if (!fs.existsSync(jsPath)) return [];
    
    const content = fs.readFileSync(jsPath, 'utf-8');
    const regex = /getElementById\(['"]([^'"]+)['"]\)/g;
    
    const ids = [];
    let match;
    while ((match = regex.exec(content)) !== null) {
        ids.push(match[1]);
    }
    
    return ids;
}

/**
 * Main test suite
 */
async function runTests() {
    console.log(`\n${colors.magenta}╔═══════════════════════════════════════════════════════╗${colors.reset}`);
    console.log(`${colors.magenta}║   CORTEX Dashboard Integration Test Suite           ║${colors.reset}`);
    console.log(`${colors.magenta}╚═══════════════════════════════════════════════════════╝${colors.reset}\n`);
    
    // Test 1: Core HTML file
    console.log(`\n${colors.blue}━━━ Test 1: Core HTML File ━━━${colors.reset}`);
    const indexPath = path.join(uiRoot, 'index.html');
    testFileExists('index.html');
    
    // Test 2: Extract and validate script sources
    console.log(`\n${colors.blue}━━━ Test 2: Script Sources ━━━${colors.reset}`);
    const { scripts, modules } = extractScriptSources(indexPath);
    
    console.log(`\n${colors.cyan}Found ${scripts.length} regular scripts, ${modules.length} ES6 modules${colors.reset}`);
    
    [...scripts, ...modules].forEach(src => {
        testFileExists(src);
    });
    
    // Test 3: Component files
    console.log(`\n${colors.blue}━━━ Test 3: Component Files ━━━${colors.reset}`);
    const componentFiles = [
        'components/executive-tab.js',
        'components/overview-tab-v3.js',
        'components/tech-stack-tab.js',
        'components/security-tab.js',
        'components/architecture-tab.js',
        'components/code-org-tab.js',
        'components/vendors-tab.js',
        'components/engineering-onboarding-tab.js'
    ];
    
    componentFiles.forEach(file => testFileExists(file));
    
    // Test 4: Check imports in app.js
    console.log(`\n${colors.blue}━━━ Test 4: App.js Imports ━━━${colors.reset}`);
    const appJsPath = path.join(uiRoot, 'app.js');
    if (fs.existsSync(appJsPath)) {
        const imports = extractImports(appJsPath);
        console.log(`\n${colors.cyan}Found ${imports.length} imports in app.js${colors.reset}`);
        imports.forEach(imp => testImportPath(imp, appJsPath));
    } else {
        results.failed++;
        log('fail', 'app.js not found');
    }
    
    // Test 5: Container IDs
    console.log(`\n${colors.blue}━━━ Test 5: Container IDs ━━━${colors.reset}`);
    const htmlContainerIds = extractContainerIds(indexPath);
    console.log(`\n${colors.cyan}Found ${htmlContainerIds.length} container IDs in HTML${colors.reset}`);
    
    const expectedContainers = [
        'executive-container',
        'overview-container',
        'tech-stack-container',
        'security-container',
        'architecture-container',
        'code-org-container',
        'vendors-container',
        'engineering-container',
        'engineering-onboarding-content'
    ];
    
    expectedContainers.forEach(id => {
        if (htmlContainerIds.includes(id)) {
            results.passed++;
            log('pass', `Container exists: #${id}`);
        } else {
            results.failed++;
            results.errors.push(`Missing container: #${id}`);
            log('fail', `Container missing: #${id}`);
        }
    });
    
    // Test 6: Check component imports
    console.log(`\n${colors.blue}━━━ Test 6: Component Imports ━━━${colors.reset}`);
    componentFiles.forEach(file => {
        const fullPath = path.join(uiRoot, file);
        if (fs.existsSync(fullPath)) {
            const imports = extractImports(fullPath);
            if (imports.length > 0) {
                console.log(`\n${colors.cyan}Checking ${imports.length} imports in ${file}${colors.reset}`);
                imports.forEach(imp => testImportPath(imp, fullPath));
            }
        }
    });
    
    // Test 7: Data files
    console.log(`\n${colors.blue}━━━ Test 7: Mock Data Files ━━━${colors.reset}`);
    const mockDataPath = path.join(dataRoot, 'mock');
    const expectedDataFiles = [
        'overview.json',
        'executive-summary.json',
        'tech-stack.json',
        'security.json',
        'architecture.json',
        'code-organization.json',
        'vendors.json',
        'engineering-onboarding.json'
    ];
    
    expectedDataFiles.forEach(file => {
        const fullPath = path.join(mockDataPath, file);
        const exists = fs.existsSync(fullPath);
        if (exists) {
            results.passed++;
            log('pass', `Data file exists: ${file}`);
        } else {
            results.warnings++;
            log('warn', `Data file missing: ${file}`, 'May cause runtime errors');
        }
    });
    
    // Test 8: Repository registry
    console.log(`\n${colors.blue}━━━ Test 8: Repository Registry ━━━${colors.reset}`);
    testFileExists('repository-registry.json', dataRoot);
    
    // Test 9: Check for getElementById mismatches
    console.log(`\n${colors.blue}━━━ Test 9: Container ID Mismatches ━━━${colors.reset}`);
    componentFiles.forEach(file => {
        const fullPath = path.join(uiRoot, file);
        if (fs.existsSync(fullPath)) {
            const referencedIds = extractGetElementById(fullPath);
            if (referencedIds.length > 0) {
                console.log(`\n${colors.cyan}${file} references ${referencedIds.length} container IDs${colors.reset}`);
                referencedIds.forEach(id => {
                    if (htmlContainerIds.includes(id)) {
                        results.passed++;
                        log('pass', `Container referenced correctly: #${id}`);
                    } else {
                        results.failed++;
                        results.errors.push(`Container #${id} referenced in ${file} but not in HTML`);
                        log('fail', `Container mismatch: #${id}`, `Referenced in ${file} but missing from HTML`);
                    }
                });
            }
        }
    });
    
    // Test 10: CSS files
    console.log(`\n${colors.blue}━━━ Test 10: CSS Files ━━━${colors.reset}`);
    const cssFiles = [
        'styles/global.css',
        'styles/dashboard.css',
        'styles/engineering-onboarding.css'
    ];
    
    cssFiles.forEach(file => testFileExists(file));
    
    // Print summary
    console.log(`\n${colors.magenta}╔═══════════════════════════════════════════════════════╗${colors.reset}`);
    console.log(`${colors.magenta}║   Test Summary                                        ║${colors.reset}`);
    console.log(`${colors.magenta}╚═══════════════════════════════════════════════════════╝${colors.reset}\n`);
    
    console.log(`${colors.green}✅ Passed:   ${results.passed}${colors.reset}`);
    console.log(`${colors.red}❌ Failed:   ${results.failed}${colors.reset}`);
    console.log(`${colors.yellow}⚠️  Warnings: ${results.warnings}${colors.reset}`);
    
    if (results.errors.length > 0) {
        console.log(`\n${colors.red}━━━ Errors ━━━${colors.reset}`);
        results.errors.forEach((err, i) => {
            console.log(`${colors.red}${i + 1}. ${err}${colors.reset}`);
        });
    }
    
    console.log(`\n${colors.magenta}═══════════════════════════════════════════════════════${colors.reset}\n`);
    
    // Exit with appropriate code
    process.exit(results.failed > 0 ? 1 : 0);
}

// Run tests
runTests().catch(err => {
    console.error(`${colors.red}Fatal error:${colors.reset}`, err);
    process.exit(1);
});
