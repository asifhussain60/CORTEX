/**
 * CORTEX 6.0 Audit Log Parser and Visualizer
 * Parses JSONL audit logs and displays with correlation chain tracing
 */

class AuditLogViewer {
    constructor(auditLogElement) {
        this.auditLogElement = auditLogElement;
        this.allLogs = [];
        this.filteredLogs = [];
        this.currentFilter = 'all';
    }
    
    /**
     * Parse JSONL audit log content
     */
    parseJSONL(content) {
        const lines = content.trim().split('\n');
        const logs = [];
        
        lines.forEach(line => {
            try {
                const entry = JSON.parse(line);
                logs.push(entry);
            } catch (error) {
                console.warn('Failed to parse log entry:', error);
            }
        });
        
        return logs;
    }
    
    /**
     * Load audit logs from file system (if accessible)
     */
    async loadAuditLogs() {
        try {
            // Try to load recent audit logs
            const logFiles = [
                '../../cortex-brain/audit-logs/20260110_130749_middleware.jsonl',
                '../../cortex-brain/audit-logs/20260110_130749_state_management.jsonl'
            ];
            
            for (const logFile of logFiles) {
                try {
                    const response = await fetch(logFile);
                    const content = await response.text();
                    const logs = this.parseJSONL(content);
                    this.allLogs.push(...logs);
                } catch (error) {
                    console.log(`Could not load ${logFile}:`, error.message);
                }
            }
            
            if (this.allLogs.length === 0) {
                // Use sample data if files not accessible
                this.useSampleData();
            } else {
                this.filteredLogs = [...this.allLogs];
                this.render();
            }
        } catch (error) {
            console.log('Using sample audit data');
            this.useSampleData();
        }
    }
    
    /**
     * Use sample audit data for demonstration
     */
    useSampleData() {
        this.allLogs = [
            {
                timestamp: "2026-01-10T23:50:00Z",
                level: "info",
                category: "INFRASTRUCTURE",
                component: "EnhancedAuditLogger",
                operation: "initialize",
                message: "EnhancedAuditLogger initialized with SQLite backend",
                correlation_id: "CORTEX-ABC123",
                ac_id: "AC-AUDIT-001"
            },
            {
                timestamp: "2026-01-10T23:51:00Z",
                level: "info",
                category: "GOVERNANCE",
                component: "GovernanceMerger",
                operation: "merge_rules",
                message: "4-Tier Governance Merger loaded 19 SKULL rules from Tier 0",
                correlation_id: "CORTEX-ABC123",
                ac_id: "AC-GOV-001",
                context: {
                    tier0_rules: 19,
                    tier1_rules: 5,
                    tier2_rules: 12,
                    tier3_rules: 8
                }
            },
            {
                timestamp: "2026-01-10T23:52:00Z",
                level: "info",
                category: "VALIDATION",
                component: "EvidenceBundler",
                operation: "validate_structure",
                message: "Evidence Bundle structure validated: 3-file format (manifest, test_results, audit_trace)",
                correlation_id: "CORTEX-ABC123",
                ac_id: "AC-EVIDENCE-001"
            },
            {
                timestamp: "2026-01-10T23:53:00Z",
                level: "info",
                category: "ORCHESTRATOR",
                component: "MasterOrchestrator",
                operation: "initialize",
                message: "MasterOrchestrator initialized with correlation_id: CORTEX-ABC123",
                correlation_id: "CORTEX-ABC123",
                ac_id: "AC-ORCH-001"
            },
            {
                timestamp: "2026-01-10T23:54:00Z",
                level: "info",
                category: "ORCHESTRATOR",
                component: "TodoManager",
                operation: "create_task",
                message: "Created task: Implement AC-AUDIT-007 (Hash Chain Audit Trail)",
                correlation_id: "CORTEX-ABC123",
                ac_id: "AC-TODO-001",
                context: {
                    task_id: "TASK-001",
                    priority: "HIGH"
                }
            },
            {
                timestamp: "2026-01-10T23:55:00Z",
                level: "warning",
                category: "GOVERNANCE",
                component: "GovernanceMerger",
                operation: "enforce_rule",
                message: "CORE-001 enforcement: Operation exceeds 500 lines, splitting into increments",
                correlation_id: "CORTEX-ABC123",
                ac_id: "AC-GOV-002",
                context: {
                    rule_id: "CORE-001",
                    lines_requested: 750,
                    increments_created: 2
                }
            },
            {
                timestamp: "2026-01-10T23:56:00Z",
                level: "info",
                category: "INFRASTRUCTURE",
                component: "StateManager",
                operation: "persist",
                message: "State persisted to progress-tracker.json with atomic write",
                correlation_id: "CORTEX-ABC123",
                ac_id: "AC-STATE-001"
            },
            {
                timestamp: "2026-01-10T23:57:00Z",
                level: "info",
                category: "ORCHESTRATOR",
                component: "TDD-Master",
                operation: "validate_tests",
                message: "Test validation passed: 15 tests, 100% coverage for AC-AUDIT-001",
                correlation_id: "CORTEX-ABC123",
                ac_id: "AC-TDD-001",
                context: {
                    tests_passed: 15,
                    coverage: 100
                }
            },
            {
                timestamp: "2026-01-10T23:58:00Z",
                level: "error",
                category: "ORCHESTRATOR",
                component: "PlanningOrchestrator",
                operation: "generate_plan",
                message: "Planning failed: Missing context from git history",
                correlation_id: "CORTEX-DEF456",
                ac_id: "AC-PLAN-001",
                context: {
                    error: "GitHistoryNotFound",
                    required_branches: ["CORTEX-5.5", "CORTEX-5.0"]
                }
            },
            {
                timestamp: "2026-01-10T23:59:00Z",
                level: "info",
                category: "VALIDATION",
                component: "EvidenceBundler",
                operation: "generate",
                message: "Evidence Bundle generated for TodoOrchestrator: 3 gates passed (test 85%, audit 100%, governance 100%)",
                correlation_id: "CORTEX-ABC123",
                ac_id: "AC-EVIDENCE-003",
                context: {
                    test_coverage: 85,
                    audit_completeness: 100,
                    governance_compliance: 100
                }
            }
        ];
        
        this.filteredLogs = [...this.allLogs];
        this.render();
    }
    
    /**
     * Filter logs by category
     */
    filterByCategory(category) {
        this.currentFilter = category;
        
        if (category === 'all') {
            this.filteredLogs = [...this.allLogs];
        } else {
            this.filteredLogs = this.allLogs.filter(log => 
                log.category === category
            );
        }
        
        this.render();
    }
    
    /**
     * Get CSS class for log level
     */
    getLevelClass(level) {
        const levelMap = {
            'error': 'danger',
            'warning': 'warning',
            'info': 'primary',
            'debug': 'secondary'
        };
        return levelMap[level] || 'primary';
    }
    
    /**
     * Format timestamp for display
     */
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('en-US', { 
            hour12: false, 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
        });
    }
    
    /**
     * Render audit logs to DOM
     */
    render() {
        this.auditLogElement.innerHTML = '';
        
        if (this.filteredLogs.length === 0) {
            this.auditLogElement.innerHTML = `
                <div style="text-align: center; padding: 40px; color: var(--text-secondary);">
                    No audit logs found for filter: ${this.currentFilter}
                </div>
            `;
            return;
        }
        
        this.filteredLogs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            
            // Add level-specific border color
            const levelClass = this.getLevelClass(log.level);
            if (levelClass === 'danger') {
                logEntry.style.borderLeftColor = 'var(--danger-color)';
            } else if (levelClass === 'warning') {
                logEntry.style.borderLeftColor = 'var(--warning-color)';
            } else {
                logEntry.style.borderLeftColor = 'var(--primary-color)';
            }
            
            let contextInfo = '';
            if (log.context && Object.keys(log.context).length > 0) {
                contextInfo = `<div style="margin-top: 5px; font-size: 0.85em; color: var(--text-secondary);">
                    ${Object.entries(log.context).map(([key, value]) => 
                        `${key}: ${JSON.stringify(value)}`
                    ).join(' | ')}
                </div>`;
            }
            
            logEntry.innerHTML = `
                <div class="log-timestamp">${this.formatTimestamp(log.timestamp)}</div>
                <div>
                    <span class="log-category">${log.category}</span> | 
                    <span style="color: var(--secondary-color); font-weight: 600;">${log.component}</span> | 
                    ${log.ac_id ? `<span style="color: var(--accent-color);">${log.ac_id}</span>` : ''}
                </div>
                <div class="log-message">${log.message}</div>
                ${contextInfo}
                ${log.correlation_id ? `<div style="margin-top: 5px; font-size: 0.8em; color: var(--text-secondary); font-family: monospace;">
                    correlation: ${log.correlation_id}
                </div>` : ''}
            `;
            
            this.auditLogElement.appendChild(logEntry);
        });
        
        // Update log count
        const logCountElement = document.getElementById('logCount');
        if (logCountElement) {
            logCountElement.textContent = `${this.filteredLogs.length} logs`;
        }
    }
    
    /**
     * Search logs by text
     */
    search(searchTerm) {
        if (!searchTerm) {
            this.filteredLogs = [...this.allLogs];
        } else {
            const term = searchTerm.toLowerCase();
            this.filteredLogs = this.allLogs.filter(log => 
                log.message.toLowerCase().includes(term) ||
                log.component.toLowerCase().includes(term) ||
                (log.ac_id && log.ac_id.toLowerCase().includes(term)) ||
                (log.correlation_id && log.correlation_id.toLowerCase().includes(term))
            );
        }
        
        this.render();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const auditLogElement = document.getElementById('auditLog');
    if (auditLogElement) {
        const viewer = new AuditLogViewer(auditLogElement);
        viewer.loadAuditLogs();
        
        // Setup filter buttons
        const filterButtons = document.querySelectorAll('.filter-btn');
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                const filter = button.getAttribute('data-filter');
                
                // Update active state
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Apply filter
                viewer.filterByCategory(filter);
            });
        });
        
        // Make viewer globally accessible for debugging
        window.auditViewer = viewer;
    }
});

export { AuditLogViewer };
