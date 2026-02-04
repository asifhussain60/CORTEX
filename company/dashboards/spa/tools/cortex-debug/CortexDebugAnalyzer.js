/**
 * CORTEX Debug Analyzer
 * ======================
 * 
 * Analyzes captured console logs to identify:
 * - Race conditions (data accessed before load)
 * - Integration breakages (missing dependencies, DOM mismatches)
 * - Timing issues (async operations out of order)
 * - Error patterns and root causes
 * 
 * Generates comprehensive fix plans with prioritized recommendations.
 * 
 * @author CORTEX
 * @version 1.0.0
 */

import fs from 'fs';
import path from 'path';

const MARKER_PREFIX = 'CORTEX_DEBUG_';

/**
 * Analysis patterns for detecting issues
 */
const ANALYSIS_PATTERNS = {
    // Race condition: Data accessed before load complete
    raceCondition: {
        name: 'Race Condition',
        severity: 'HIGH',
        detect: (logs) => {
            const issues = [];
            const dataLoadMarkers = logs.filter(l => 
                l.parsedMarker?.phase === 'ASYNC' && 
                l.parsedMarker?.message?.includes('AWAIT')
            );
            const domAccessMarkers = logs.filter(l => 
                l.parsedMarker?.phase === 'DOM'
            );
            
            // Check if DOM accessed before async complete
            for (const domLog of domAccessMarkers) {
                const asyncBefore = dataLoadMarkers.filter(a => 
                    a.timestamp < domLog.timestamp &&
                    a.parsedMarker?.message?.includes('START')
                );
                const asyncComplete = dataLoadMarkers.filter(a => 
                    a.timestamp < domLog.timestamp &&
                    a.parsedMarker?.message?.includes('END')
                );
                
                if (asyncBefore.length > asyncComplete.length) {
                    issues.push({
                        type: 'RACE_CONDITION',
                        description: `DOM access (${domLog.parsedMarker?.message}) before async operation completed`,
                        file: domLog.parsedMarker?.file,
                        line: domLog.parsedMarker?.line,
                        timestamp: domLog.timestamp,
                        relatedLogs: [domLog, ...asyncBefore]
                    });
                }
            }
            return issues;
        }
    },
    
    // Missing dependency: Script/module not loaded
    missingDependency: {
        name: 'Missing Dependency',
        severity: 'CRITICAL',
        detect: (logs, errors) => {
            const issues = [];
            
            for (const error of errors) {
                const text = error.text.toLowerCase();
                
                if (text.includes('is not defined') || 
                    text.includes('is not a function') ||
                    text.includes('cannot read property') ||
                    text.includes('not loaded')) {
                    
                    // Extract the missing item name
                    const match = error.text.match(/(\w+)\s+is not (defined|a function)/i) ||
                                  error.text.match(/(\w+)\s+not loaded/i);
                    
                    issues.push({
                        type: 'MISSING_DEPENDENCY',
                        description: error.text,
                        missingItem: match ? match[1] : 'Unknown',
                        timestamp: error.timestamp,
                        suggestion: `Ensure ${match ? match[1] : 'dependency'} is loaded before dependent code`
                    });
                }
            }
            return issues;
        }
    },
    
    // DOM mismatch: Element not found
    domMismatch: {
        name: 'DOM Mismatch',
        severity: 'MEDIUM',
        detect: (logs, errors, warnings) => {
            const issues = [];
            
            // Check CORTEX logs for DOM issues
            const domLogs = logs.filter(l => l.parsedMarker?.phase === 'DOM');
            
            // Check warnings for container not found
            const containerWarnings = warnings.filter(w => 
                w.text.includes('not found') || 
                w.text.includes('Container')
            );
            
            for (const warn of containerWarnings) {
                const match = warn.text.match(/Container ['"`]?(\w+)['"`]?\s+not found/i) ||
                              warn.text.match(/['"`](\w+)['"`]\s+not found/i);
                
                issues.push({
                    type: 'DOM_MISMATCH',
                    description: warn.text,
                    elementId: match ? match[1] : 'Unknown',
                    timestamp: warn.timestamp,
                    suggestion: `Add element with id="${match ? match[1] : 'ID'}" to HTML or fix ID in JavaScript`
                });
            }
            
            return issues;
        }
    },
    
    // Async timing: Operations completing out of order
    asyncTiming: {
        name: 'Async Timing Issue',
        severity: 'MEDIUM',
        detect: (logs) => {
            const issues = [];
            const asyncLogs = logs.filter(l => 
                l.parsedMarker?.phase === 'ASYNC' ||
                l.parsedMarker?.phase === 'PROMISE'
            );
            
            // Group by file and check order
            const byFile = {};
            for (const log of asyncLogs) {
                const file = log.parsedMarker?.file;
                if (!byFile[file]) byFile[file] = [];
                byFile[file].push(log);
            }
            
            for (const [file, fileLogs] of Object.entries(byFile)) {
                // Check for START without corresponding END
                const starts = fileLogs.filter(l => l.parsedMarker?.message?.includes('START'));
                const ends = fileLogs.filter(l => l.parsedMarker?.message?.includes('END'));
                
                if (starts.length !== ends.length) {
                    issues.push({
                        type: 'ASYNC_TIMING',
                        description: `Async operations may not be completing properly in ${file}`,
                        file,
                        starts: starts.length,
                        ends: ends.length,
                        suggestion: 'Check for uncaught promise rejections or timeout issues'
                    });
                }
            }
            
            return issues;
        }
    },
    
    // Script loading order
    scriptLoadOrder: {
        name: 'Script Load Order Issue',
        severity: 'HIGH',
        detect: (logs, errors) => {
            const issues = [];
            
            // Check for "not loaded" errors
            const notLoadedErrors = errors.filter(e => 
                e.text.includes('not loaded') ||
                e.text.includes('Include')
            );
            
            for (const error of notLoadedErrors) {
                const match = error.text.match(/(\w+)\s+not loaded.*Include\s+(\w+\.js)/i);
                
                issues.push({
                    type: 'SCRIPT_LOAD_ORDER',
                    description: error.text,
                    missingScript: match ? match[2] : 'Unknown',
                    timestamp: error.timestamp,
                    suggestion: `Move ${match ? match[2] : 'script'} before dependent scripts in HTML`
                });
            }
            
            return issues;
        }
    },
    
    // 404 Resource not found
    resourceNotFound: {
        name: 'Resource Not Found',
        severity: 'HIGH',
        detect: (logs, errors, warnings, networkRequests) => {
            const issues = [];
            
            const failed = networkRequests.filter(r => r.status === 404);
            
            for (const req of failed) {
                issues.push({
                    type: 'RESOURCE_NOT_FOUND',
                    description: `404 Not Found: ${req.url}`,
                    url: req.url,
                    timestamp: req.timestamp,
                    suggestion: `Verify file exists at path or update path in code`
                });
            }
            
            return issues;
        }
    }
};

/**
 * Issue priority scoring
 */
const SEVERITY_SCORES = {
    'CRITICAL': 100,
    'HIGH': 75,
    'MEDIUM': 50,
    'LOW': 25
};

/**
 * Analyze captured logs
 */
export async function analyze(capturedLogsPath, options = {}) {
    const {
        outputDir = path.dirname(capturedLogsPath)
    } = options;
    
    console.log(`\n🔍 CORTEX Debug Analyzer`);
    console.log(`   Input: ${capturedLogsPath}\n`);
    
    if (!fs.existsSync(capturedLogsPath)) {
        throw new Error(`Captured logs not found: ${capturedLogsPath}`);
    }
    
    const capturedData = JSON.parse(fs.readFileSync(capturedLogsPath, 'utf-8'));
    
    const {
        sessionId,
        cortexLogs = [],
        errors = [],
        warnings = [],
        networkRequests = []
    } = capturedData;
    
    console.log(`   Session: ${sessionId}`);
    console.log(`   CORTEX Logs: ${cortexLogs.length}`);
    console.log(`   Errors: ${errors.length}`);
    console.log(`   Warnings: ${warnings.length}`);
    console.log(`   Network Requests: ${networkRequests.length}\n`);
    
    // Run all analysis patterns
    const allIssues = [];
    
    for (const [patternName, pattern] of Object.entries(ANALYSIS_PATTERNS)) {
        console.log(`   🔎 Checking: ${pattern.name}`);
        
        try {
            const issues = pattern.detect(cortexLogs, errors, warnings, networkRequests);
            
            for (const issue of issues) {
                allIssues.push({
                    ...issue,
                    pattern: patternName,
                    severity: pattern.severity,
                    score: SEVERITY_SCORES[pattern.severity]
                });
            }
            
            if (issues.length > 0) {
                console.log(`      Found ${issues.length} issues`);
            }
        } catch (err) {
            console.warn(`      ⚠️ Pattern failed: ${err.message}`);
        }
    }
    
    // Sort by severity score (highest first)
    allIssues.sort((a, b) => b.score - a.score);
    
    // Generate analysis report
    const report = {
        sessionId,
        analyzedAt: new Date().toISOString(),
        summary: {
            totalIssues: allIssues.length,
            critical: allIssues.filter(i => i.severity === 'CRITICAL').length,
            high: allIssues.filter(i => i.severity === 'HIGH').length,
            medium: allIssues.filter(i => i.severity === 'MEDIUM').length,
            low: allIssues.filter(i => i.severity === 'LOW').length
        },
        issues: allIssues,
        executionTrace: buildExecutionTrace(cortexLogs),
        fixPlan: generateFixPlan(allIssues)
    };
    
    // Save analysis report
    const reportPath = path.join(outputDir, 'analysis-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    // Generate human-readable fix plan
    const fixPlanMd = generateFixPlanMarkdown(report);
    const fixPlanPath = path.join(outputDir, 'fix-plan.md');
    fs.writeFileSync(fixPlanPath, fixPlanMd);
    
    // Update session status
    const sessionPath = path.join(outputDir, 'session.json');
    if (fs.existsSync(sessionPath)) {
        const sessionData = JSON.parse(fs.readFileSync(sessionPath, 'utf-8'));
        sessionData.status = 'analyzed';
        sessionData.analyzeTime = new Date().toISOString();
        sessionData.analysisResult = report.summary;
        fs.writeFileSync(sessionPath, JSON.stringify(sessionData, null, 2));
    }
    
    // Print summary
    console.log(`\n✅ Analysis complete!`);
    console.log(`   Total Issues: ${report.summary.totalIssues}`);
    console.log(`   🔴 Critical: ${report.summary.critical}`);
    console.log(`   🟠 High: ${report.summary.high}`);
    console.log(`   🟡 Medium: ${report.summary.medium}`);
    console.log(`   🟢 Low: ${report.summary.low}`);
    console.log(`   Report: ${reportPath}`);
    console.log(`   Fix Plan: ${fixPlanPath}`);
    
    return report;
}

/**
 * Build execution trace from CORTEX logs
 */
function buildExecutionTrace(cortexLogs) {
    const trace = [];
    
    for (const log of cortexLogs) {
        if (log.parsedMarker) {
            trace.push({
                timestamp: log.timestamp,
                phase: log.parsedMarker.phase,
                file: log.parsedMarker.file,
                line: log.parsedMarker.line,
                message: log.parsedMarker.message
            });
        }
    }
    
    return trace;
}

/**
 * Generate prioritized fix plan
 */
function generateFixPlan(issues) {
    const plan = {
        immediate: [],  // CRITICAL - Fix now
        priority: [],   // HIGH - Fix today
        scheduled: [],  // MEDIUM - Plan for next sprint
        backlog: []     // LOW - Nice to have
    };
    
    for (const issue of issues) {
        const step = {
            type: issue.type,
            description: issue.description,
            suggestion: issue.suggestion || 'Review and fix manually',
            file: issue.file,
            line: issue.line
        };
        
        switch (issue.severity) {
            case 'CRITICAL':
                plan.immediate.push(step);
                break;
            case 'HIGH':
                plan.priority.push(step);
                break;
            case 'MEDIUM':
                plan.scheduled.push(step);
                break;
            default:
                plan.backlog.push(step);
        }
    }
    
    return plan;
}

/**
 * Generate human-readable fix plan markdown
 */
function generateFixPlanMarkdown(report) {
    const lines = [
        '# CORTEX Debug Fix Plan',
        '',
        `**Session:** ${report.sessionId}`,
        `**Generated:** ${report.analyzedAt}`,
        '',
        '## Summary',
        '',
        `| Severity | Count |`,
        `|----------|-------|`,
        `| 🔴 Critical | ${report.summary.critical} |`,
        `| 🟠 High | ${report.summary.high} |`,
        `| 🟡 Medium | ${report.summary.medium} |`,
        `| 🟢 Low | ${report.summary.low} |`,
        `| **Total** | **${report.summary.totalIssues}** |`,
        ''
    ];
    
    // Immediate actions (Critical)
    if (report.fixPlan.immediate.length > 0) {
        lines.push('## 🔴 Immediate Actions (Critical)', '');
        lines.push('These issues are blocking and must be fixed immediately:', '');
        
        for (let i = 0; i < report.fixPlan.immediate.length; i++) {
            const step = report.fixPlan.immediate[i];
            lines.push(`### ${i + 1}. ${step.type}`, '');
            lines.push(`**Problem:** ${step.description}`, '');
            lines.push(`**Fix:** ${step.suggestion}`, '');
            if (step.file) lines.push(`**Location:** ${step.file}${step.line ? `:${step.line}` : ''}`, '');
            lines.push('');
        }
    }
    
    // Priority actions (High)
    if (report.fixPlan.priority.length > 0) {
        lines.push('## 🟠 Priority Actions (High)', '');
        lines.push('These issues should be fixed today:', '');
        
        for (let i = 0; i < report.fixPlan.priority.length; i++) {
            const step = report.fixPlan.priority[i];
            lines.push(`### ${i + 1}. ${step.type}`, '');
            lines.push(`**Problem:** ${step.description}`, '');
            lines.push(`**Fix:** ${step.suggestion}`, '');
            if (step.file) lines.push(`**Location:** ${step.file}${step.line ? `:${step.line}` : ''}`, '');
            lines.push('');
        }
    }
    
    // Scheduled actions (Medium)
    if (report.fixPlan.scheduled.length > 0) {
        lines.push('## 🟡 Scheduled Actions (Medium)', '');
        lines.push('Plan these for the next sprint:', '');
        
        for (const step of report.fixPlan.scheduled) {
            lines.push(`- **${step.type}:** ${step.description}`);
            lines.push(`  - Fix: ${step.suggestion}`);
        }
        lines.push('');
    }
    
    // Backlog (Low)
    if (report.fixPlan.backlog.length > 0) {
        lines.push('## 🟢 Backlog (Low)', '');
        lines.push('Nice to have improvements:', '');
        
        for (const step of report.fixPlan.backlog) {
            lines.push(`- ${step.type}: ${step.description}`);
        }
        lines.push('');
    }
    
    // Execution trace
    lines.push('## Execution Trace', '');
    lines.push('```');
    for (const entry of report.executionTrace.slice(0, 50)) {
        lines.push(`[${entry.phase}] ${entry.file}:${entry.line} - ${entry.message}`);
    }
    if (report.executionTrace.length > 50) {
        lines.push(`... and ${report.executionTrace.length - 50} more entries`);
    }
    lines.push('```', '');
    
    // Cleanup reminder
    lines.push('---', '');
    lines.push('## ⚠️ Cleanup Reminder', '');
    lines.push('After fixing all issues and verifying the application works:', '');
    lines.push('```bash');
    lines.push('node cortex-debug-orchestrator.js cleanup --confirm');
    lines.push('```');
    lines.push('');
    lines.push('This will remove all CORTEX_DEBUG markers from the codebase.');
    
    return lines.join('\n');
}

/**
 * CLI entry point
 */
if (process.argv[1] && process.argv[1].endsWith('CortexDebugAnalyzer.js')) {
    const capturedLogsPath = process.argv[2] || '.cortex-debug/captured-logs.json';
    
    analyze(capturedLogsPath)
        .then(report => {
            console.log(`\n📋 Review fix-plan.md then use CortexDebugCleanup.js to clean up`);
        })
        .catch(err => {
            console.error('❌ Analysis failed:', err);
            process.exit(1);
        });
}

export default { analyze, ANALYSIS_PATTERNS, SEVERITY_SCORES };
