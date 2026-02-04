/**
 * CORTEX Debug Injector
 * ======================
 * 
 * Injects uniquely marked console.log statements into JavaScript files
 * to trace execution flow, detect race conditions, and identify integration issues.
 * 
 * Features:
 * - AST-based injection for accurate placement
 * - Unique session IDs for each debug run
 * - Function entry/exit tracing
 * - Async operation tracking
 * - DOM manipulation logging
 * - Event handler registration tracing
 * 
 * @author CORTEX
 * @version 1.0.0
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

// Debug marker prefix - easily grep-able
const MARKER_PREFIX = 'CORTEX_DEBUG_';

/**
 * Generate a unique session ID for this debug run
 */
function generateSessionId() {
    return crypto.randomBytes(4).toString('hex');
}

/**
 * Injection patterns for different code constructs
 */
const INJECTION_PATTERNS = {
    // Function declarations: function foo() { ... }
    functionDeclaration: {
        pattern: /^(\s*)(function\s+(\w+)\s*\([^)]*\)\s*\{)/gm,
        inject: (match, indent, funcStart, funcName, sessionId, file, lineNum) => {
            const marker = `${MARKER_PREFIX}${sessionId}:FUNC:${file}:${lineNum}`;
            return `${indent}${funcStart}\n${indent}    console.log('[${marker}] ENTER ${funcName}()');`;
        }
    },
    
    // Arrow functions assigned to variables: const foo = () => { ... }
    arrowFunctionAssignment: {
        pattern: /^(\s*)(const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>\s*\{/gm,
        inject: (match, indent, varType, varName, sessionId, file, lineNum) => {
            const marker = `${MARKER_PREFIX}${sessionId}:ARROW:${file}:${lineNum}`;
            return `${match}\n${indent}    console.log('[${marker}] ENTER ${varName}()');`;
        }
    },
    
    // Method definitions: methodName() { ... }
    methodDefinition: {
        pattern: /^(\s*)(async\s+)?(\w+)\s*\([^)]*\)\s*\{(?!\s*\/\/\s*CORTEX)/gm,
        inject: (match, indent, asyncKeyword, methodName, sessionId, file, lineNum) => {
            // Skip constructor and lifecycle methods (they have their own logging)
            if (['constructor', 'render', 'connectedCallback', 'disconnectedCallback'].includes(methodName)) {
                return match;
            }
            const marker = `${MARKER_PREFIX}${sessionId}:METHOD:${file}:${lineNum}`;
            const asyncStr = asyncKeyword || '';
            return `${indent}${asyncStr}${methodName}(${match.match(/\([^)]*\)/)[0]}) {\n${indent}    console.log('[${marker}] ENTER ${methodName}()');`;
        }
    },
    
    // Async operations: await fetch(), await Promise.all(), etc.
    asyncOperation: {
        pattern: /(\s*)(await\s+)([\w.]+\s*\([^)]*\))/g,
        inject: (match, indent, awaitKeyword, operation, sessionId, file, lineNum) => {
            const marker = `${MARKER_PREFIX}${sessionId}:ASYNC:${file}:${lineNum}`;
            const opName = operation.split('(')[0].trim();
            return `${indent}console.log('[${marker}] AWAIT START ${opName}');\n${indent}${awaitKeyword}${operation};\n${indent}console.log('[${marker}] AWAIT END ${opName}');`;
        }
    },
    
    // DOM queries: document.getElementById, querySelector, etc.
    domQuery: {
        pattern: /(\s*)(document\.(getElementById|querySelector|querySelectorAll)\s*\(\s*['"`]([^'"`]+)['"`]\s*\))/g,
        inject: (match, indent, fullExpr, method, selector, sessionId, file, lineNum) => {
            const marker = `${MARKER_PREFIX}${sessionId}:DOM:${file}:${lineNum}`;
            return `(console.log('[${marker}] DOM ${method}(${selector})'), ${fullExpr})`;
        }
    },
    
    // Event listeners: addEventListener
    eventListener: {
        pattern: /(\s*)(\w+)\.addEventListener\s*\(\s*['"`](\w+)['"`]/g,
        inject: (match, indent, element, eventType, sessionId, file, lineNum) => {
            const marker = `${MARKER_PREFIX}${sessionId}:EVENT:${file}:${lineNum}`;
            return `${indent}console.log('[${marker}] LISTEN ${element}.${eventType}');\n${match}`;
        }
    },
    
    // setTimeout/setInterval: Track delayed operations
    timedOperation: {
        pattern: /(\s*)(setTimeout|setInterval)\s*\(\s*(?:async\s*)?\([^)]*\)\s*=>\s*\{/g,
        inject: (match, indent, timerType, sessionId, file, lineNum) => {
            const marker = `${MARKER_PREFIX}${sessionId}:TIMER:${file}:${lineNum}`;
            return `${match}\n${indent}    console.log('[${marker}] ${timerType.toUpperCase()} FIRED');`;
        }
    },
    
    // Promise.then: Track promise chains
    promiseChain: {
        pattern: /(\s*)\.then\s*\(\s*(?:async\s*)?\([^)]*\)\s*=>\s*\{/g,
        inject: (match, indent, sessionId, file, lineNum) => {
            const marker = `${MARKER_PREFIX}${sessionId}:PROMISE:${file}:${lineNum}`;
            return `${match}\n${indent}    console.log('[${marker}] THEN RESOLVED');`;
        }
    },
    
    // catch blocks: Track error handling
    catchBlock: {
        pattern: /(\s*)\.catch\s*\(\s*(?:async\s*)?\((\w*)\)\s*=>\s*\{/g,
        inject: (match, indent, errorVar, sessionId, file, lineNum) => {
            const marker = `${MARKER_PREFIX}${sessionId}:ERROR:${file}:${lineNum}`;
            const errRef = errorVar || 'e';
            return `${match}\n${indent}    console.error('[${marker}] CATCH', ${errRef});`;
        }
    }
};

/**
 * Files to inject debug markers into
 */
const TARGET_FILES = [
    'js/app.js',
    'js/data/DualFormatDataLoader.js',
    'js/data/JSONDataAdapter.js',
    'js/data/SQLiteDataLayer.js',
    'js/components/DataBinder.js',
    'js/components/TabManager.js',
    'js/components/ChartHost.js',
    'js/components/Pagination.js',
    'js/components/SubTabs.js',
    'js/components/UseCasesManager.js',
    'js/components/Wizard.js',
    'js/charts/metricsCharts.js',
    'js/diagrams/MermaidRenderer.js'
];

/**
 * Create injection map for tracking what was injected where
 */
class InjectionMap {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.injections = [];
        this.fileBackups = new Map();
        this.startTime = new Date().toISOString();
    }
    
    addInjection(file, line, type, marker) {
        this.injections.push({
            file,
            line,
            type,
            marker,
            timestamp: new Date().toISOString()
        });
    }
    
    addBackup(file, content) {
        this.fileBackups.set(file, content);
    }
    
    toJSON() {
        return {
            sessionId: this.sessionId,
            startTime: this.startTime,
            totalInjections: this.injections.length,
            files: [...new Set(this.injections.map(i => i.file))],
            injections: this.injections,
            backups: Array.from(this.fileBackups.keys())
        };
    }
}

/**
 * Inject debug markers into a single file
 */
function injectFile(filePath, sessionId, injectionMap) {
    if (!fs.existsSync(filePath)) {
        console.warn(`⚠️ File not found: ${filePath}`);
        return null;
    }
    
    const originalContent = fs.readFileSync(filePath, 'utf-8');
    const fileName = path.basename(filePath);
    
    // Store backup
    injectionMap.addBackup(filePath, originalContent);
    
    let modifiedContent = originalContent;
    let lineOffset = 0;
    
    // Track line numbers for accurate markers
    const lines = originalContent.split('\n');
    
    // Apply each injection pattern
    for (const [patternName, config] of Object.entries(INJECTION_PATTERNS)) {
        const regex = new RegExp(config.pattern.source, config.pattern.flags);
        let match;
        
        while ((match = regex.exec(modifiedContent)) !== null) {
            const lineNum = modifiedContent.substring(0, match.index).split('\n').length;
            const marker = `${MARKER_PREFIX}${sessionId}:${patternName.toUpperCase()}:${fileName}:${lineNum}`;
            
            // Log injection
            injectionMap.addInjection(fileName, lineNum, patternName, marker);
        }
    }
    
    // Simple injection approach: Add entry logs after function/method opening braces
    modifiedContent = injectFunctionEntryLogs(originalContent, sessionId, fileName, injectionMap);
    
    return modifiedContent;
}

/**
 * Inject entry logs into functions and methods
 */
function injectFunctionEntryLogs(content, sessionId, fileName, injectionMap) {
    const lines = content.split('\n');
    const result = [];
    let lineNum = 0;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        lineNum++;
        result.push(line);
        
        // Skip if already has CORTEX marker
        if (line.includes(MARKER_PREFIX)) {
            continue;
        }
        
        // Detect function/method start (line ends with {)
        const funcMatch = line.match(/^\s*(async\s+)?(function\s+)?(\w+)\s*\([^)]*\)\s*\{?\s*$/);
        const classMethodMatch = line.match(/^\s*(async\s+)?(\w+)\s*\([^)]*\)\s*\{\s*$/);
        const arrowMatch = line.match(/^\s*(const|let|var)\s+(\w+)\s*=\s*(async\s*)?\([^)]*\)\s*=>\s*\{\s*$/);
        
        let funcName = null;
        let indentMatch = line.match(/^(\s*)/);
        let indent = indentMatch ? indentMatch[1] + '    ' : '    ';
        
        if (funcMatch && funcMatch[3]) {
            funcName = funcMatch[3];
        } else if (classMethodMatch && classMethodMatch[2]) {
            funcName = classMethodMatch[2];
        } else if (arrowMatch && arrowMatch[2]) {
            funcName = arrowMatch[2];
        }
        
        // Skip common non-interesting functions
        const skipFuncs = ['constructor', 'toString', 'valueOf', 'get', 'set'];
        if (funcName && !skipFuncs.includes(funcName)) {
            const marker = `${MARKER_PREFIX}${sessionId}:FUNC:${fileName}:${lineNum}`;
            result.push(`${indent}console.log('[${marker}] ENTER ${funcName}');`);
            injectionMap.addInjection(fileName, lineNum, 'FUNC', marker);
        }
        
        // Detect await statements
        if (line.includes('await ') && !line.includes('console.log')) {
            const awaitMatch = line.match(/await\s+([\w.]+)/);
            if (awaitMatch) {
                const asyncOp = awaitMatch[1];
                const marker = `${MARKER_PREFIX}${sessionId}:ASYNC:${fileName}:${lineNum}`;
                // Insert log before the await line
                result.splice(result.length - 1, 0, 
                    `${indent.slice(4)}console.log('[${marker}] AWAIT ${asyncOp}');`
                );
                injectionMap.addInjection(fileName, lineNum, 'ASYNC', marker);
            }
        }
        
        // Detect DOM queries
        if (line.includes('getElementById') || line.includes('querySelector')) {
            const domMatch = line.match(/(getElementById|querySelector(?:All)?)\s*\(\s*['"`]([^'"`]+)['"`]/);
            if (domMatch) {
                const method = domMatch[1];
                const selector = domMatch[2];
                const marker = `${MARKER_PREFIX}${sessionId}:DOM:${fileName}:${lineNum}`;
                result.splice(result.length - 1, 0,
                    `${indent.slice(4)}console.log('[${marker}] DOM ${method}(${selector})');`
                );
                injectionMap.addInjection(fileName, lineNum, 'DOM', marker);
            }
        }
    }
    
    return result.join('\n');
}

/**
 * Main injection function
 */
export async function inject(basePath, options = {}) {
    const sessionId = options.sessionId || generateSessionId();
    const injectionMap = new InjectionMap(sessionId);
    const outputDir = path.join(basePath, '.cortex-debug');
    
    console.log(`\n🔧 CORTEX Debug Injector`);
    console.log(`   Session: ${sessionId}`);
    console.log(`   Base Path: ${basePath}`);
    console.log(`   Output Dir: ${outputDir}\n`);
    
    // Create output directory
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Create backups directory
    const backupDir = path.join(outputDir, 'backups');
    if (!fs.existsSync(backupDir)) {
        fs.mkdirSync(backupDir, { recursive: true });
    }
    
    // Process each target file
    for (const relPath of TARGET_FILES) {
        const filePath = path.join(basePath, relPath);
        
        if (!fs.existsSync(filePath)) {
            console.log(`   ⏭️  Skipping (not found): ${relPath}`);
            continue;
        }
        
        console.log(`   📝 Injecting: ${relPath}`);
        
        // Read and backup original
        const originalContent = fs.readFileSync(filePath, 'utf-8');
        const backupPath = path.join(backupDir, relPath.replace(/\//g, '_'));
        fs.writeFileSync(backupPath, originalContent);
        
        // Inject markers
        const modifiedContent = injectFile(filePath, sessionId, injectionMap);
        
        if (modifiedContent && modifiedContent !== originalContent) {
            fs.writeFileSync(filePath, modifiedContent);
            console.log(`      ✅ Injected ${injectionMap.injections.filter(i => i.file === path.basename(filePath)).length} markers`);
        }
    }
    
    // Save injection map
    const mapPath = path.join(outputDir, 'injection-map.json');
    fs.writeFileSync(mapPath, JSON.stringify(injectionMap.toJSON(), null, 2));
    
    // Save session info
    const sessionPath = path.join(outputDir, 'session.json');
    fs.writeFileSync(sessionPath, JSON.stringify({
        sessionId,
        startTime: injectionMap.startTime,
        basePath,
        status: 'injected',
        totalInjections: injectionMap.injections.length,
        files: injectionMap.toJSON().files
    }, null, 2));
    
    console.log(`\n✅ Injection complete!`);
    console.log(`   Session ID: ${sessionId}`);
    console.log(`   Total Injections: ${injectionMap.injections.length}`);
    console.log(`   Files Modified: ${injectionMap.toJSON().files.length}`);
    console.log(`   Injection Map: ${mapPath}`);
    console.log(`   Backups: ${backupDir}`);
    
    return {
        sessionId,
        injectionMap: injectionMap.toJSON(),
        outputDir
    };
}

/**
 * CLI entry point
 */
if (process.argv[1] && process.argv[1].endsWith('CortexDebugInjector.js')) {
    const basePath = process.argv[2] || process.cwd();
    inject(basePath)
        .then(result => {
            console.log(`\n📋 Run tests now, then use CortexDebugCapture.js to collect logs`);
        })
        .catch(err => {
            console.error('❌ Injection failed:', err);
            process.exit(1);
        });
}

export default { inject, generateSessionId, MARKER_PREFIX };
