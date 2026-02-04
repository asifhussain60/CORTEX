#!/usr/bin/env node
/**
 * CORTEX Debug Orchestrator
 * ==========================
 * 
 * Main CLI that coordinates all debugging phases:
 * 1. INJECT - Add CORTEX_DEBUG markers to codebase
 * 2. CAPTURE - Run application and collect console logs
 * 3. ANALYZE - Trace logs to identify issues
 * 4. FIX-PLAN - Generate prioritized fix recommendations
 * 5. CLEANUP - Remove markers when done
 * 
 * Supports multiple technology stacks:
 * - JavaScript/TypeScript (Vanilla, React, Angular, Vue)
 * - Python (Django, Flask, FastAPI)
 * - C# (.NET Core, ASP.NET, Blazor)
 * 
 * @author CORTEX
 * @version 1.0.0
 */

import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';

// Import debug tools
import { inject, generateSessionId, MARKER_PREFIX } from './CortexDebugInjector.js';
import { capture } from './CortexDebugCapture.js';
import { analyze } from './CortexDebugAnalyzer.js';
import { cleanup } from './CortexDebugCleanup.js';

// Import language adapters
import { detectStack, getAdapter } from './adapters/index.js';

const VERSION = '1.0.0';
const HELP = `
CORTEX Debug Orchestrator v${VERSION}
=====================================

A comprehensive debugging tool that traces execution flow across your codebase
to identify race conditions, integration breakages, and timing issues.

USAGE:
  cortex-debug <command> [options]

COMMANDS:
  run         Full debug cycle: inject → capture → analyze
  inject      Inject CORTEX_DEBUG markers into codebase
  capture     Run application and capture console logs
  analyze     Analyze captured logs for issues
  cleanup     Remove all CORTEX_DEBUG markers
  status      Show current debug session status

OPTIONS:
  --path, -p        Base path to project (default: current directory)
  --url, -u         URL to capture (for web applications)
  --stack, -s       Force technology stack (js|ts|python|csharp|auto)
  --headless        Run browser in headless mode (default: false)
  --confirm         Confirm cleanup (required for cleanup command)
  --dry-run         Preview changes without applying
  --verbose, -v     Verbose output
  --help, -h        Show this help message

EXAMPLES:
  # Full debug cycle for a web app
  cortex-debug run --url http://localhost:8888/dashboard.html

  # Inject markers only
  cortex-debug inject --path ./src

  # Capture logs from running app
  cortex-debug capture --url http://localhost:3000

  # Analyze captured logs
  cortex-debug analyze

  # Clean up after debugging
  cortex-debug cleanup --confirm

SUPPORTED STACKS:
  - JavaScript/TypeScript (React, Angular, Vue, Vanilla)
  - Python (Django, Flask, FastAPI)
  - C# (.NET Core, ASP.NET, Blazor)

For more information, see: docs/tools/cortex-debug-orchestrator.md
`;

/**
 * Parse command line arguments
 */
function parseArgs(args) {
    const options = {
        command: null,
        path: process.cwd(),
        url: null,
        stack: 'auto',
        headless: false,
        confirm: false,
        dryRun: false,
        verbose: false,
        help: false
    };
    
    let i = 0;
    while (i < args.length) {
        const arg = args[i];
        
        switch (arg) {
            case 'run':
            case 'inject':
            case 'capture':
            case 'analyze':
            case 'cleanup':
            case 'status':
                options.command = arg;
                break;
            case '--path':
            case '-p':
                options.path = args[++i];
                break;
            case '--url':
            case '-u':
                options.url = args[++i];
                break;
            case '--stack':
            case '-s':
                options.stack = args[++i];
                break;
            case '--headless':
                options.headless = true;
                break;
            case '--confirm':
                options.confirm = true;
                break;
            case '--dry-run':
                options.dryRun = true;
                break;
            case '--verbose':
            case '-v':
                options.verbose = true;
                break;
            case '--help':
            case '-h':
                options.help = true;
                break;
        }
        i++;
    }
    
    return options;
}

/**
 * Show session status
 */
function showStatus(basePath) {
    const outputDir = path.join(basePath, '.cortex-debug');
    const sessionPath = path.join(outputDir, 'session.json');
    
    console.log(`\n📊 CORTEX Debug Session Status`);
    console.log(`   Base Path: ${basePath}\n`);
    
    if (!fs.existsSync(sessionPath)) {
        console.log(`   ❌ No active debug session`);
        console.log(`   Run 'cortex-debug inject' to start a new session`);
        return;
    }
    
    const session = JSON.parse(fs.readFileSync(sessionPath, 'utf-8'));
    
    console.log(`   Session ID: ${session.sessionId}`);
    console.log(`   Status: ${session.status}`);
    console.log(`   Started: ${session.startTime}`);
    
    if (session.totalInjections) {
        console.log(`   Injections: ${session.totalInjections}`);
        console.log(`   Files: ${session.files?.length || 0}`);
    }
    
    if (session.captureSummary) {
        console.log(`\n   Capture Summary:`);
        console.log(`      CORTEX Logs: ${session.captureSummary.cortexLogs}`);
        console.log(`      Errors: ${session.captureSummary.errors}`);
        console.log(`      Warnings: ${session.captureSummary.warnings}`);
    }
    
    if (session.analysisResult) {
        console.log(`\n   Analysis Result:`);
        console.log(`      Total Issues: ${session.analysisResult.totalIssues}`);
        console.log(`      Critical: ${session.analysisResult.critical}`);
        console.log(`      High: ${session.analysisResult.high}`);
    }
    
    // Show available files
    console.log(`\n   Available Files:`);
    const files = [
        { name: 'injection-map.json', desc: 'Injection locations' },
        { name: 'captured-logs.json', desc: 'Console output' },
        { name: 'analysis-report.json', desc: 'Issue analysis' },
        { name: 'fix-plan.md', desc: 'Fix recommendations' }
    ];
    
    for (const file of files) {
        const filePath = path.join(outputDir, file.name);
        const exists = fs.existsSync(filePath);
        console.log(`      ${exists ? '✅' : '❌'} ${file.name} - ${file.desc}`);
    }
}

/**
 * Run full debug cycle
 */
async function runFullCycle(options) {
    console.log(`\n🚀 CORTEX Debug Orchestrator - Full Cycle`);
    console.log(`   Path: ${options.path}`);
    console.log(`   URL: ${options.url || 'Not specified'}\n`);
    
    // Detect technology stack
    const stack = options.stack === 'auto' ? detectStack(options.path) : options.stack;
    console.log(`   Detected Stack: ${stack}`);
    
    // Phase 1: Inject
    console.log(`\n${'='.repeat(50)}`);
    console.log(`   PHASE 1: INJECT`);
    console.log(`${'='.repeat(50)}`);
    
    const injectResult = await inject(options.path, { stack });
    
    // Phase 2: Capture
    if (options.url) {
        console.log(`\n${'='.repeat(50)}`);
        console.log(`   PHASE 2: CAPTURE`);
        console.log(`${'='.repeat(50)}`);
        
        await capture(options.url, {
            sessionId: injectResult.sessionId,
            outputDir: injectResult.outputDir,
            headless: options.headless
        });
    } else {
        console.log(`\n⚠️ No URL specified. Skipping capture phase.`);
        console.log(`   Run your application manually, then use 'cortex-debug capture --url <url>'`);
    }
    
    // Phase 3: Analyze
    const capturedLogsPath = path.join(injectResult.outputDir, 'captured-logs.json');
    
    if (fs.existsSync(capturedLogsPath)) {
        console.log(`\n${'='.repeat(50)}`);
        console.log(`   PHASE 3: ANALYZE`);
        console.log(`${'='.repeat(50)}`);
        
        await analyze(capturedLogsPath);
    }
    
    // Show fix plan
    const fixPlanPath = path.join(injectResult.outputDir, 'fix-plan.md');
    if (fs.existsSync(fixPlanPath)) {
        console.log(`\n${'='.repeat(50)}`);
        console.log(`   FIX PLAN GENERATED`);
        console.log(`${'='.repeat(50)}`);
        console.log(`   Review: ${fixPlanPath}`);
    }
    
    console.log(`\n${'='.repeat(50)}`);
    console.log(`   NEXT STEPS`);
    console.log(`${'='.repeat(50)}`);
    console.log(`   1. Review fix-plan.md for issues and recommendations`);
    console.log(`   2. Apply fixes to your codebase`);
    console.log(`   3. Test the application`);
    console.log(`   4. When satisfied, run: cortex-debug cleanup --confirm`);
}

/**
 * Main entry point
 */
async function main() {
    const args = process.argv.slice(2);
    const options = parseArgs(args);
    
    if (options.help || !options.command) {
        console.log(HELP);
        return;
    }
    
    try {
        switch (options.command) {
            case 'run':
                await runFullCycle(options);
                break;
                
            case 'inject':
                await inject(options.path, { stack: options.stack });
                break;
                
            case 'capture':
                if (!options.url) {
                    console.error('❌ URL required for capture. Use --url <url>');
                    process.exit(1);
                }
                await capture(options.url, {
                    outputDir: path.join(options.path, '.cortex-debug'),
                    headless: options.headless
                });
                break;
                
            case 'analyze':
                const logsPath = path.join(options.path, '.cortex-debug', 'captured-logs.json');
                await analyze(logsPath);
                break;
                
            case 'cleanup':
                await cleanup(options.path, {
                    dryRun: !options.confirm,
                    verify: true
                });
                break;
                
            case 'status':
                showStatus(options.path);
                break;
                
            default:
                console.error(`❌ Unknown command: ${options.command}`);
                console.log(HELP);
                process.exit(1);
        }
    } catch (err) {
        console.error(`❌ Error: ${err.message}`);
        if (options.verbose) {
            console.error(err.stack);
        }
        process.exit(1);
    }
}

main();
