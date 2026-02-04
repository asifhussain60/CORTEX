/**
 * CORTEX Debug Cleanup
 * =====================
 * 
 * Efficiently removes ALL CORTEX_DEBUG markers from codebase,
 * leaving code production-ready.
 * 
 * Features:
 * - Restores from backups (if available)
 * - Pattern-based cleanup (if no backups)
 * - Verification that no markers remain
 * - Safe mode with dry-run support
 * 
 * @author CORTEX
 * @version 1.0.0
 */

import fs from 'fs';
import path from 'path';

const MARKER_PREFIX = 'CORTEX_DEBUG_';

/**
 * Cleanup patterns for different languages
 */
const CLEANUP_PATTERNS = {
    // JavaScript/TypeScript console.log with CORTEX marker
    javascript: {
        extensions: ['.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'],
        patterns: [
            // Full line: console.log('[CORTEX_DEBUG_...] ...');
            /^\s*console\.(log|warn|error|info|debug)\s*\(\s*['"`]\[CORTEX_DEBUG_[^\]]+\][^'"`]*['"`][^)]*\);\s*\n?/gm,
            // Comma expression: (console.log('[CORTEX_DEBUG_...]'), expr)
            /\(console\.(log|warn|error)\s*\(\s*['"`]\[CORTEX_DEBUG_[^\]]+\][^'"`]*['"`]\s*\),\s*/g,
            // Inline marker comment
            /\/\/\s*CORTEX_DEBUG_\w+.*\n?/g
        ]
    },
    
    // Python logging with CORTEX marker
    python: {
        extensions: ['.py'],
        patterns: [
            // logging.debug/info/warning/error
            /^\s*(logging\.)?(debug|info|warning|error|critical)\s*\(\s*['"`]\[CORTEX_DEBUG_[^\]]+\][^'"`]*['"`]\s*\)\s*\n?/gm,
            // print with CORTEX marker
            /^\s*print\s*\(\s*f?['"`]\[CORTEX_DEBUG_[^\]]+\][^'"`]*['"`]\s*\)\s*\n?/gm,
            // Comment marker
            /^\s*#\s*CORTEX_DEBUG_\w+.*\n?/gm
        ]
    },
    
    // C# Debug/Trace with CORTEX marker
    csharp: {
        extensions: ['.cs'],
        patterns: [
            // Debug.WriteLine/Console.WriteLine
            /^\s*(Debug|Console|Trace)\.(WriteLine|Write)\s*\(\s*\$?"?\[CORTEX_DEBUG_[^\]]+\][^"]*"?\s*\);\s*\n?/gm,
            // Logger calls
            /^\s*_?[Ll]ogger\.(Log|Debug|Info|Warning|Error)\s*\(\s*\$?"?\[CORTEX_DEBUG_[^\]]+\][^"]*"?\s*\);\s*\n?/gm,
            // Comment marker
            /^\s*\/\/\s*CORTEX_DEBUG_\w+.*\n?/gm
        ]
    },
    
    // HTML/Vue/Svelte
    html: {
        extensions: ['.html', '.htm', '.vue', '.svelte'],
        patterns: [
            // Script tags with CORTEX marker console.log
            /^\s*console\.(log|warn|error)\s*\(\s*['"`]\[CORTEX_DEBUG_[^\]]+\][^'"`]*['"`][^)]*\);\s*\n?/gm,
            // Comment markers
            /<!--\s*CORTEX_DEBUG_\w+[^>]*-->\s*\n?/g
        ]
    }
};

/**
 * Cleanup statistics
 */
class CleanupStats {
    constructor() {
        this.filesProcessed = 0;
        this.filesModified = 0;
        this.markersRemoved = 0;
        this.errors = [];
        this.restoredFromBackup = 0;
    }
    
    toJSON() {
        return {
            filesProcessed: this.filesProcessed,
            filesModified: this.filesModified,
            markersRemoved: this.markersRemoved,
            restoredFromBackup: this.restoredFromBackup,
            errors: this.errors
        };
    }
}

/**
 * Get language config for file
 */
function getLanguageConfig(filePath) {
    const ext = path.extname(filePath).toLowerCase();
    
    for (const [lang, config] of Object.entries(CLEANUP_PATTERNS)) {
        if (config.extensions.includes(ext)) {
            return { lang, ...config };
        }
    }
    
    return null;
}

/**
 * Remove markers from file content
 */
function removeMarkers(content, patterns) {
    let modified = content;
    let count = 0;
    
    for (const pattern of patterns) {
        const matches = modified.match(pattern);
        if (matches) {
            count += matches.length;
        }
        modified = modified.replace(pattern, '');
    }
    
    // Clean up empty lines left behind (max 2 consecutive)
    modified = modified.replace(/\n{3,}/g, '\n\n');
    
    return { modified, count };
}

/**
 * Verify no markers remain in content
 */
function verifyClean(content) {
    return !content.includes(MARKER_PREFIX);
}

/**
 * Clean a single file
 */
function cleanFile(filePath, stats, dryRun = false) {
    const langConfig = getLanguageConfig(filePath);
    
    if (!langConfig) {
        return false; // Skip unsupported file types
    }
    
    stats.filesProcessed++;
    
    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        
        // Skip if no markers present
        if (!content.includes(MARKER_PREFIX)) {
            return false;
        }
        
        const { modified, count } = removeMarkers(content, langConfig.patterns);
        
        if (count > 0) {
            stats.markersRemoved += count;
            stats.filesModified++;
            
            if (!dryRun) {
                fs.writeFileSync(filePath, modified);
            }
            
            // Verify clean
            if (!verifyClean(modified)) {
                stats.errors.push({
                    file: filePath,
                    error: 'Markers still present after cleanup'
                });
            }
            
            return true;
        }
    } catch (err) {
        stats.errors.push({
            file: filePath,
            error: err.message
        });
    }
    
    return false;
}

/**
 * Restore files from backup
 */
function restoreFromBackups(backupDir, basePath, stats) {
    if (!fs.existsSync(backupDir)) {
        return false;
    }
    
    const backupFiles = fs.readdirSync(backupDir);
    
    for (const backupFile of backupFiles) {
        const backupPath = path.join(backupDir, backupFile);
        
        // Convert backup filename back to original path
        // js_app.js -> js/app.js
        const originalRelPath = backupFile.replace(/_/g, '/');
        const originalPath = path.join(basePath, originalRelPath);
        
        try {
            const backupContent = fs.readFileSync(backupPath, 'utf-8');
            fs.writeFileSync(originalPath, backupContent);
            stats.restoredFromBackup++;
            console.log(`   ✅ Restored: ${originalRelPath}`);
        } catch (err) {
            stats.errors.push({
                file: originalPath,
                error: `Restore failed: ${err.message}`
            });
        }
    }
    
    return stats.restoredFromBackup > 0;
}

/**
 * Recursively find files to clean
 */
function findFilesToClean(dir, files = []) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    
    for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        
        // Skip node_modules, .git, .cortex-debug
        if (entry.isDirectory()) {
            if (!['node_modules', '.git', '.cortex-debug', 'vendor', 'dist', 'build'].includes(entry.name)) {
                findFilesToClean(fullPath, files);
            }
        } else {
            const langConfig = getLanguageConfig(fullPath);
            if (langConfig) {
                files.push(fullPath);
            }
        }
    }
    
    return files;
}

/**
 * Main cleanup function
 */
export async function cleanup(basePath, options = {}) {
    const {
        dryRun = false,
        useBackups = true,
        verify = true
    } = options;
    
    const outputDir = path.join(basePath, '.cortex-debug');
    const backupDir = path.join(outputDir, 'backups');
    const stats = new CleanupStats();
    
    console.log(`\n🧹 CORTEX Debug Cleanup`);
    console.log(`   Base Path: ${basePath}`);
    console.log(`   Dry Run: ${dryRun}`);
    console.log(`   Use Backups: ${useBackups}\n`);
    
    // Try restoring from backups first
    if (useBackups && fs.existsSync(backupDir)) {
        console.log(`   📦 Restoring from backups...`);
        const restored = restoreFromBackups(backupDir, basePath, stats);
        
        if (restored) {
            console.log(`   ✅ Restored ${stats.restoredFromBackup} files from backup`);
        }
    }
    
    // If no backups or restore failed, use pattern-based cleanup
    if (stats.restoredFromBackup === 0) {
        console.log(`   🔍 Pattern-based cleanup...`);
        
        const filesToClean = findFilesToClean(basePath);
        console.log(`   Found ${filesToClean.length} files to check`);
        
        for (const filePath of filesToClean) {
            const cleaned = cleanFile(filePath, stats, dryRun);
            if (cleaned) {
                const relPath = path.relative(basePath, filePath);
                console.log(`   ${dryRun ? '🔍' : '✅'} ${relPath}`);
            }
        }
    }
    
    // Verification pass
    if (verify && !dryRun) {
        console.log(`\n   🔬 Verification pass...`);
        const filesToVerify = findFilesToClean(basePath);
        let markersFound = 0;
        
        for (const filePath of filesToVerify) {
            const content = fs.readFileSync(filePath, 'utf-8');
            if (content.includes(MARKER_PREFIX)) {
                markersFound++;
                const relPath = path.relative(basePath, filePath);
                console.log(`   ⚠️ Markers still present: ${relPath}`);
            }
        }
        
        if (markersFound === 0) {
            console.log(`   ✅ Verification passed: No markers found`);
        } else {
            stats.errors.push({
                file: 'verification',
                error: `${markersFound} files still contain markers`
            });
        }
    }
    
    // Clean up debug directory
    if (!dryRun && stats.errors.length === 0) {
        console.log(`\n   🗑️  Cleaning up debug artifacts...`);
        
        if (fs.existsSync(outputDir)) {
            // Keep session.json for reference, remove everything else
            const sessionPath = path.join(outputDir, 'session.json');
            if (fs.existsSync(sessionPath)) {
                const sessionData = JSON.parse(fs.readFileSync(sessionPath, 'utf-8'));
                sessionData.status = 'cleaned';
                sessionData.cleanupTime = new Date().toISOString();
                sessionData.cleanupStats = stats.toJSON();
                fs.writeFileSync(sessionPath, JSON.stringify(sessionData, null, 2));
            }
            
            // Remove backup directory
            if (fs.existsSync(backupDir)) {
                fs.rmSync(backupDir, { recursive: true });
                console.log(`   ✅ Removed backups directory`);
            }
        }
    }
    
    // Print summary
    console.log(`\n✅ Cleanup complete!`);
    console.log(`   Files Processed: ${stats.filesProcessed}`);
    console.log(`   Files Modified: ${stats.filesModified}`);
    console.log(`   Markers Removed: ${stats.markersRemoved}`);
    console.log(`   Restored from Backup: ${stats.restoredFromBackup}`);
    
    if (stats.errors.length > 0) {
        console.log(`   ⚠️ Errors: ${stats.errors.length}`);
        for (const err of stats.errors) {
            console.log(`      - ${err.file}: ${err.error}`);
        }
    }
    
    if (dryRun) {
        console.log(`\n   ℹ️  This was a dry run. Run with --confirm to apply changes.`);
    }
    
    return stats;
}

/**
 * CLI entry point
 */
if (process.argv[1] && process.argv[1].endsWith('CortexDebugCleanup.js')) {
    const basePath = process.argv[2] || process.cwd();
    const dryRun = !process.argv.includes('--confirm');
    
    cleanup(basePath, { dryRun })
        .then(stats => {
            if (stats.errors.length === 0) {
                console.log(`\n✅ Codebase is production-ready!`);
            }
        })
        .catch(err => {
            console.error('❌ Cleanup failed:', err);
            process.exit(1);
        });
}

export default { cleanup, CLEANUP_PATTERNS, MARKER_PREFIX };
