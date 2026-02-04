/**
 * CORTEX Debug Language Adapters
 * ================================
 * 
 * Provides language-specific injection and cleanup adapters for:
 * - JavaScript/TypeScript (React, Angular, Vue, Vanilla)
 * - Python (Django, Flask, FastAPI)
 * - C# (.NET Core, ASP.NET, Blazor)
 * 
 * @author CORTEX
 * @version 1.0.0
 */

import fs from 'fs';
import path from 'path';

const MARKER_PREFIX = 'CORTEX_DEBUG_';

/**
 * Detect technology stack from project structure
 */
export function detectStack(basePath) {
    const indicators = {
        // JavaScript/TypeScript
        'package.json': 'javascript',
        'tsconfig.json': 'typescript',
        
        // React
        'src/App.jsx': 'react',
        'src/App.tsx': 'react-ts',
        
        // Angular
        'angular.json': 'angular',
        
        // Vue
        'vue.config.js': 'vue',
        'vite.config.ts': 'vue', // Could also be React/other
        
        // Python
        'requirements.txt': 'python',
        'pyproject.toml': 'python',
        'setup.py': 'python',
        
        // Django
        'manage.py': 'django',
        
        // Flask
        'app.py': 'flask',
        
        // FastAPI
        'main.py': 'fastapi',
        
        // C#/.NET
        '*.csproj': 'csharp',
        '*.sln': 'dotnet',
        
        // ASP.NET
        'Program.cs': 'aspnet',
        'Startup.cs': 'aspnet'
    };
    
    for (const [indicator, stack] of Object.entries(indicators)) {
        if (indicator.includes('*')) {
            // Glob pattern
            const ext = indicator.replace('*', '');
            const files = fs.readdirSync(basePath);
            if (files.some(f => f.endsWith(ext))) {
                return stack;
            }
        } else {
            const checkPath = path.join(basePath, indicator);
            if (fs.existsSync(checkPath)) {
                return stack;
            }
        }
    }
    
    return 'unknown';
}

/**
 * Base adapter class
 */
class BaseAdapter {
    constructor(options = {}) {
        this.sessionId = options.sessionId;
        this.basePath = options.basePath;
    }
    
    get markerPrefix() {
        return MARKER_PREFIX;
    }
    
    /**
     * Get files to inject
     * @returns {string[]} Array of file paths
     */
    getTargetFiles() {
        throw new Error('Not implemented');
    }
    
    /**
     * Inject markers into file content
     * @param {string} content - File content
     * @param {string} fileName - File name for markers
     * @returns {Object} { modified: string, injections: number }
     */
    injectFile(content, fileName) {
        throw new Error('Not implemented');
    }
    
    /**
     * Clean markers from file content
     * @param {string} content - File content
     * @returns {Object} { modified: string, removed: number }
     */
    cleanFile(content) {
        throw new Error('Not implemented');
    }
}

/**
 * JavaScript/TypeScript Adapter
 */
export class JavaScriptAdapter extends BaseAdapter {
    constructor(options = {}) {
        super(options);
        this.extensions = ['.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.vue', '.svelte'];
        this.excludeDirs = ['node_modules', 'dist', 'build', '.next', '.nuxt', 'vendor'];
    }
    
    getTargetFiles() {
        return this._findFiles(this.basePath);
    }
    
    _findFiles(dir, files = []) {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        
        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            
            if (entry.isDirectory()) {
                if (!this.excludeDirs.includes(entry.name) && !entry.name.startsWith('.')) {
                    this._findFiles(fullPath, files);
                }
            } else {
                if (this.extensions.includes(path.extname(entry.name).toLowerCase())) {
                    files.push(fullPath);
                }
            }
        }
        
        return files;
    }
    
    injectFile(content, fileName) {
        const lines = content.split('\n');
        const result = [];
        let injections = 0;
        let lineNum = 0;
        
        for (const line of lines) {
            lineNum++;
            result.push(line);
            
            // Skip if already has marker
            if (line.includes(this.markerPrefix)) continue;
            
            // Function/method start
            const funcMatch = line.match(/^\s*(async\s+)?(function\s+)?(\w+)\s*\([^)]*\)\s*\{?\s*$/);
            const arrowMatch = line.match(/^\s*(const|let|var)\s+(\w+)\s*=\s*(async\s*)?\([^)]*\)\s*=>\s*\{/);
            const methodMatch = line.match(/^\s*(async\s+)?(\w+)\s*\([^)]*\)\s*\{\s*$/);
            
            let funcName = null;
            if (funcMatch && funcMatch[3]) funcName = funcMatch[3];
            else if (arrowMatch && arrowMatch[2]) funcName = arrowMatch[2];
            else if (methodMatch && methodMatch[2]) funcName = methodMatch[2];
            
            // Skip common non-interesting functions
            const skipFuncs = ['constructor', 'toString', 'valueOf', 'get', 'set', 'if', 'for', 'while', 'switch'];
            
            if (funcName && !skipFuncs.includes(funcName)) {
                const indent = line.match(/^(\s*)/)[1] + '    ';
                const marker = `${this.markerPrefix}${this.sessionId}:FUNC:${fileName}:${lineNum}`;
                result.push(`${indent}console.log('[${marker}] ENTER ${funcName}');`);
                injections++;
            }
        }
        
        return { modified: result.join('\n'), injections };
    }
    
    cleanFile(content) {
        let modified = content;
        let removed = 0;
        
        const patterns = [
            /^\s*console\.(log|warn|error|info|debug)\s*\(\s*['"`]\[CORTEX_DEBUG_[^\]]+\][^'"`]*['"`][^)]*\);\s*\n?/gm
        ];
        
        for (const pattern of patterns) {
            const matches = modified.match(pattern);
            if (matches) removed += matches.length;
            modified = modified.replace(pattern, '');
        }
        
        return { modified, removed };
    }
}

/**
 * Python Adapter
 */
export class PythonAdapter extends BaseAdapter {
    constructor(options = {}) {
        super(options);
        this.extensions = ['.py'];
        this.excludeDirs = ['__pycache__', '.venv', 'venv', 'env', '.tox', 'dist', 'build', 'node_modules'];
    }
    
    getTargetFiles() {
        return this._findFiles(this.basePath);
    }
    
    _findFiles(dir, files = []) {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        
        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            
            if (entry.isDirectory()) {
                if (!this.excludeDirs.includes(entry.name) && !entry.name.startsWith('.')) {
                    this._findFiles(fullPath, files);
                }
            } else {
                if (this.extensions.includes(path.extname(entry.name).toLowerCase())) {
                    files.push(fullPath);
                }
            }
        }
        
        return files;
    }
    
    injectFile(content, fileName) {
        const lines = content.split('\n');
        const result = [];
        let injections = 0;
        let lineNum = 0;
        let inClass = false;
        let classIndent = 0;
        
        for (const line of lines) {
            lineNum++;
            result.push(line);
            
            // Skip if already has marker
            if (line.includes(this.markerPrefix)) continue;
            
            // Track class context
            const classMatch = line.match(/^(\s*)class\s+(\w+)/);
            if (classMatch) {
                inClass = true;
                classIndent = classMatch[1].length;
            }
            
            // Function/method definition
            const funcMatch = line.match(/^(\s*)(async\s+)?def\s+(\w+)\s*\([^)]*\)\s*(?:->.*)?:\s*$/);
            
            if (funcMatch) {
                const indent = funcMatch[1];
                const funcName = funcMatch[3];
                
                // Skip dunder methods
                if (funcName.startsWith('__') && funcName.endsWith('__')) continue;
                
                const marker = `${this.markerPrefix}${this.sessionId}:FUNC:${fileName}:${lineNum}`;
                result.push(`${indent}    print(f"[${marker}] ENTER ${funcName}")`);
                injections++;
            }
        }
        
        return { modified: result.join('\n'), injections };
    }
    
    cleanFile(content) {
        let modified = content;
        let removed = 0;
        
        const patterns = [
            /^\s*print\s*\(\s*f?['"`]\[CORTEX_DEBUG_[^\]]+\][^'"`]*['"`]\s*\)\s*\n?/gm,
            /^\s*(logging\.)?(debug|info|warning|error)\s*\(\s*f?['"`]\[CORTEX_DEBUG_[^\]]+\][^'"`]*['"`]\s*\)\s*\n?/gm
        ];
        
        for (const pattern of patterns) {
            const matches = modified.match(pattern);
            if (matches) removed += matches.length;
            modified = modified.replace(pattern, '');
        }
        
        return { modified, removed };
    }
}

/**
 * C#/.NET Adapter
 */
export class CSharpAdapter extends BaseAdapter {
    constructor(options = {}) {
        super(options);
        this.extensions = ['.cs'];
        this.excludeDirs = ['bin', 'obj', 'node_modules', 'packages', '.vs'];
    }
    
    getTargetFiles() {
        return this._findFiles(this.basePath);
    }
    
    _findFiles(dir, files = []) {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        
        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            
            if (entry.isDirectory()) {
                if (!this.excludeDirs.includes(entry.name) && !entry.name.startsWith('.')) {
                    this._findFiles(fullPath, files);
                }
            } else {
                if (this.extensions.includes(path.extname(entry.name).toLowerCase())) {
                    files.push(fullPath);
                }
            }
        }
        
        return files;
    }
    
    injectFile(content, fileName) {
        const lines = content.split('\n');
        const result = [];
        let injections = 0;
        let lineNum = 0;
        
        for (const line of lines) {
            lineNum++;
            result.push(line);
            
            // Skip if already has marker
            if (line.includes(this.markerPrefix)) continue;
            
            // Method definition (public/private/protected/internal, async, return type, name, params, {)
            const methodMatch = line.match(/^(\s*)(public|private|protected|internal)?\s*(static)?\s*(async)?\s*([\w<>\[\]]+)\s+(\w+)\s*\([^)]*\)\s*\{?\s*$/);
            
            if (methodMatch) {
                const indent = methodMatch[1];
                const methodName = methodMatch[6];
                
                // Skip common methods
                const skipMethods = ['Main', 'Dispose', 'ToString', 'GetHashCode', 'Equals'];
                if (skipMethods.includes(methodName)) continue;
                
                const marker = `${this.markerPrefix}${this.sessionId}:METHOD:${fileName}:${lineNum}`;
                result.push(`${indent}    System.Diagnostics.Debug.WriteLine($"[${marker}] ENTER ${methodName}");`);
                injections++;
            }
        }
        
        return { modified: result.join('\n'), injections };
    }
    
    cleanFile(content) {
        let modified = content;
        let removed = 0;
        
        const patterns = [
            /^\s*(System\.Diagnostics\.)?Debug\.WriteLine\s*\(\s*\$?"?\[CORTEX_DEBUG_[^\]]+\][^"]*"?\s*\);\s*\n?/gm,
            /^\s*Console\.WriteLine\s*\(\s*\$?"?\[CORTEX_DEBUG_[^\]]+\][^"]*"?\s*\);\s*\n?/gm
        ];
        
        for (const pattern of patterns) {
            const matches = modified.match(pattern);
            if (matches) removed += matches.length;
            modified = modified.replace(pattern, '');
        }
        
        return { modified, removed };
    }
}

/**
 * React-specific adapter (extends JavaScript)
 */
export class ReactAdapter extends JavaScriptAdapter {
    constructor(options = {}) {
        super(options);
        // Additional React-specific handling
    }
    
    injectFile(content, fileName) {
        // Call parent implementation
        let { modified, injections } = super.injectFile(content, fileName);
        
        // Add React-specific injections (useEffect, etc.)
        const lines = modified.split('\n');
        const result = [];
        let lineNum = 0;
        
        for (const line of lines) {
            lineNum++;
            result.push(line);
            
            // Skip if already has marker
            if (line.includes(this.markerPrefix)) continue;
            
            // useEffect hooks
            const effectMatch = line.match(/^\s*useEffect\s*\(\s*\(\s*\)\s*=>\s*\{/);
            if (effectMatch) {
                const indent = line.match(/^(\s*)/)[1] + '    ';
                const marker = `${this.markerPrefix}${this.sessionId}:EFFECT:${fileName}:${lineNum}`;
                result.push(`${indent}console.log('[${marker}] useEffect triggered');`);
                injections++;
            }
            
            // Component render
            const renderMatch = line.match(/^\s*return\s*\(\s*$/);
            if (renderMatch) {
                const indent = line.match(/^(\s*)/)[1];
                const marker = `${this.markerPrefix}${this.sessionId}:RENDER:${fileName}:${lineNum}`;
                // Insert before return
                result.splice(result.length - 1, 0, `${indent}console.log('[${marker}] Rendering component');`);
                injections++;
            }
        }
        
        return { modified: result.join('\n'), injections };
    }
}

/**
 * Angular-specific adapter
 */
export class AngularAdapter extends JavaScriptAdapter {
    constructor(options = {}) {
        super(options);
        this.extensions = ['.ts', '.js'];
    }
    
    injectFile(content, fileName) {
        let { modified, injections } = super.injectFile(content, fileName);
        
        const lines = modified.split('\n');
        const result = [];
        let lineNum = 0;
        
        for (const line of lines) {
            lineNum++;
            result.push(line);
            
            if (line.includes(this.markerPrefix)) continue;
            
            // Angular lifecycle hooks
            const lifecycleMatch = line.match(/^\s*(ngOnInit|ngOnDestroy|ngOnChanges|ngAfterViewInit|ngAfterContentInit)\s*\(\s*\)\s*\{/);
            if (lifecycleMatch) {
                const hookName = lifecycleMatch[1];
                const indent = line.match(/^(\s*)/)[1] + '    ';
                const marker = `${this.markerPrefix}${this.sessionId}:LIFECYCLE:${fileName}:${lineNum}`;
                result.push(`${indent}console.log('[${marker}] ${hookName}');`);
                injections++;
            }
        }
        
        return { modified: result.join('\n'), injections };
    }
}

/**
 * Get appropriate adapter for stack
 */
export function getAdapter(stack, options) {
    const adapters = {
        'javascript': JavaScriptAdapter,
        'typescript': JavaScriptAdapter,
        'react': ReactAdapter,
        'react-ts': ReactAdapter,
        'angular': AngularAdapter,
        'vue': JavaScriptAdapter,
        'python': PythonAdapter,
        'django': PythonAdapter,
        'flask': PythonAdapter,
        'fastapi': PythonAdapter,
        'csharp': CSharpAdapter,
        'dotnet': CSharpAdapter,
        'aspnet': CSharpAdapter
    };
    
    const AdapterClass = adapters[stack] || JavaScriptAdapter;
    return new AdapterClass(options);
}

export default {
    detectStack,
    getAdapter,
    JavaScriptAdapter,
    PythonAdapter,
    CSharpAdapter,
    ReactAdapter,
    AngularAdapter
};
