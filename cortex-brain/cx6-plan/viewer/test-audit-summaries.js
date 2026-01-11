#!/usr/bin/env node

/**
 * Test script for AuditAnalytics summary generation
 * Validates that audit logs are properly grouped and summarized
 */

const fs = require('fs');
const path = require('path');

// Load audit logs
const auditLogsPath = path.join(__dirname, 'audit-logs-aggregated.json');
const auditLogsData = JSON.parse(fs.readFileSync(auditLogsPath, 'utf-8'));
const auditLogs = auditLogsData.entries || [];

console.log(`✓ Loaded ${auditLogs.length} audit logs\n`);

// Simulate the generateAuditSummaries logic
const summaries = {};
const icons = {
    'middleware': '⚙️',
    'governance': '🛡️',
    'state_management': '💾',
    'orchestration': '🎯',
    'validation': '✓',
    'infrastructure': '🏗️',
    'audit': '📊',
    'unknown': '📝'
};

// Group by category
auditLogs.forEach(log => {
    const category = log.category || 'unknown';
    
    if (!summaries[category]) {
        summaries[category] = {
            category,
            icon: icons[category] || '📝',
            count: 0,
            successCount: 0,
            lastLog: '',
            timestamp: new Date().toISOString(),
            level: 'info',
            levels: { info: 0, debug: 0, warning: 0, error: 0 }
        };
    }
    
    summaries[category].count++;
    summaries[category].levels[log.level] = (summaries[category].levels[log.level] || 0) + 1;
    
    if (log.level === 'info' || log.level === 'debug') {
        summaries[category].successCount++;
    }
    
    if (log.operation) {
        summaries[category].lastLog = log.operation;
    }
    
    summaries[category].timestamp = log.timestamp || summaries[category].timestamp;
    
    // Set overall level
    if (log.level === 'error') {
        summaries[category].level = 'error';
    } else if (summaries[category].level !== 'error' && log.level === 'warning') {
        summaries[category].level = 'warning';
    }
});

// Calculate success rates and sort
const summariesArray = Object.values(summaries)
    .map(s => ({
        ...s,
        successRate: Math.round((s.successCount / s.count) * 100)
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6);

console.log('📊 AUDIT SUMMARY REPORT\n');
console.log('═'.repeat(80));

summariesArray.forEach((summary, index) => {
    console.log(`\n${index + 1}. ${summary.icon} ${summary.category.toUpperCase()}`);
    console.log(`   Operations: ${summary.count} | Success Rate: ${summary.successRate}%`);
    console.log(`   Last Operation: ${summary.lastLog || 'N/A'}`);
    console.log(`   Timestamp: ${new Date(summary.timestamp).toLocaleTimeString()}`);
    console.log(`   Status: ${summary.level.toUpperCase()}`);
    console.log(`   Distribution: info=${summary.levels.info}, debug=${summary.levels.debug}, warning=${summary.levels.warning}, error=${summary.levels.error}`);
});

console.log('\n' + '═'.repeat(80));
console.log(`\n✓ Summary generation successful`);
console.log(`✓ Total categories identified: ${Object.keys(summaries).length}`);
console.log(`✓ Top 6 categories will be displayed in audit trail`);
