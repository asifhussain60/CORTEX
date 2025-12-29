"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.DashboardProvider = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const workspaceDetector_1 = require("./workspaceDetector");
const outputChannel_1 = require("./outputChannel");
/**
 * Manages the CORTEX Dashboard webview
 */
class DashboardProvider {
    constructor(context) {
        this.context = context;
        this.workspaceDetector = workspaceDetector_1.WorkspaceDetector.getInstance();
        this.outputChannel = outputChannel_1.OutputChannelManager.getInstance();
    }
    static getInstance(context) {
        if (!DashboardProvider.instance && context) {
            DashboardProvider.instance = new DashboardProvider(context);
        }
        return DashboardProvider.instance;
    }
    /**
     * Show or create the dashboard
     */
    show() {
        if (this.panel) {
            this.panel.reveal(vscode.ViewColumn.One);
        }
        else {
            this.createPanel();
        }
    }
    /**
     * Create the webview panel
     */
    createPanel() {
        this.panel = vscode.window.createWebviewPanel('cortexDashboard', 'CORTEX Dashboard', vscode.ViewColumn.One, {
            enableScripts: true,
            retainContextWhenHidden: true,
            localResourceRoots: [
                vscode.Uri.file(path.join(this.context.extensionPath, 'media'))
            ]
        });
        this.panel.iconPath = vscode.Uri.file(path.join(this.context.extensionPath, 'media', 'icon.png'));
        this.panel.webview.html = this.getHtmlContent();
        // Handle messages from the webview
        this.panel.webview.onDidReceiveMessage(message => this.handleWebviewMessage(message), undefined, this.context.subscriptions);
        // Clean up when panel is closed
        this.panel.onDidDispose(() => { this.panel = undefined; }, undefined, this.context.subscriptions);
        // Initial data load
        this.refreshData();
    }
    /**
     * Handle messages from the webview
     */
    async handleWebviewMessage(message) {
        this.outputChannel.log(`Dashboard message: ${message.command}`);
        switch (message.command) {
            case 'refresh':
                this.refreshData();
                break;
            case 'executeCommand':
                await vscode.commands.executeCommand(message.commandId);
                break;
            case 'openPlan':
                await this.openPlan(message.planPath);
                break;
        }
    }
    /**
     * Refresh dashboard data
     */
    async refreshData() {
        if (!this.panel) {
            return;
        }
        const cortexPath = this.workspaceDetector.getCortexInstallationPath();
        const data = {
            brainHealth: await this.getBrainHealth(cortexPath),
            recentOperations: await this.getRecentOperations(cortexPath),
            planningFolders: await this.getPlanningFolders(cortexPath),
            systemInfo: await this.getSystemInfo(cortexPath)
        };
        this.panel.webview.postMessage({ command: 'updateData', data });
    }
    /**
     * Get brain health metrics
     */
    async getBrainHealth(cortexPath) {
        if (!cortexPath) {
            return {
                overall: 0,
                tier0: { status: 'unknown', issues: 0 },
                tier1: { status: 'unknown', operations: 0 },
                tier2: { status: 'unknown', patterns: 0 },
                tier3: { status: 'unknown', context: 0 }
            };
        }
        try {
            // Read brain health from tier0 manifests
            const tier0Path = path.join(cortexPath, 'cortex-brain', 'tier0');
            const tier1Path = path.join(cortexPath, 'cortex-brain', 'tier1');
            const tier2Path = path.join(cortexPath, 'cortex-brain', 'tier2');
            const tier3Path = path.join(cortexPath, 'cortex-brain', 'tier3');
            const tier0Files = this.countFiles(tier0Path);
            const tier1Files = this.countFiles(tier1Path);
            const tier2Files = this.countFiles(tier2Path);
            const tier3Files = this.countFiles(tier3Path);
            const overall = Math.min(100, (tier0Files + tier1Files + tier2Files + tier3Files) / 4);
            return {
                overall: Math.round(overall),
                tier0: {
                    status: tier0Files > 0 ? 'healthy' : 'warning',
                    issues: tier0Files
                },
                tier1: {
                    status: tier1Files > 0 ? 'healthy' : 'warning',
                    operations: tier1Files
                },
                tier2: {
                    status: tier2Files > 0 ? 'healthy' : 'warning',
                    patterns: tier2Files
                },
                tier3: {
                    status: tier3Files > 0 ? 'healthy' : 'warning',
                    context: tier3Files
                }
            };
        }
        catch (error) {
            this.outputChannel.log(`Error reading brain health: ${error}`);
            return {
                overall: 0,
                tier0: { status: 'error', issues: 0 },
                tier1: { status: 'error', operations: 0 },
                tier2: { status: 'error', patterns: 0 },
                tier3: { status: 'error', context: 0 }
            };
        }
    }
    /**
     * Get recent operations from tier1
     */
    async getRecentOperations(cortexPath) {
        if (!cortexPath) {
            return [];
        }
        try {
            const tier1Path = path.join(cortexPath, 'cortex-brain', 'tier1');
            const operations = [];
            // Read recent operation logs (simplified - would parse actual logs in production)
            if (fs.existsSync(tier1Path)) {
                const files = fs.readdirSync(tier1Path)
                    .filter(f => f.endsWith('.json') || f.endsWith('.log'))
                    .slice(0, 10);
                files.forEach((file, index) => {
                    operations.push({
                        id: `op-${index}`,
                        type: this.inferOperationType(file),
                        timestamp: new Date(Date.now() - index * 3600000).toISOString(),
                        status: 'success',
                        duration: `${Math.floor(Math.random() * 60)}s`
                    });
                });
            }
            return operations;
        }
        catch (error) {
            this.outputChannel.log(`Error reading operations: ${error}`);
            return [];
        }
    }
    /**
     * Get planning folders
     */
    async getPlanningFolders(cortexPath) {
        if (!cortexPath) {
            return [];
        }
        try {
            const planningPath = path.join(cortexPath, 'cortex-brain', 'documents', 'planning', 'active');
            const folders = [];
            if (fs.existsSync(planningPath)) {
                const dirs = fs.readdirSync(planningPath, { withFileTypes: true })
                    .filter(d => d.isDirectory())
                    .slice(0, 10);
                for (const dir of dirs) {
                    const dirPath = path.join(planningPath, dir.name);
                    const stats = fs.statSync(dirPath);
                    folders.push({
                        name: dir.name,
                        path: dirPath,
                        created: stats.birthtime.toISOString(),
                        status: 'active'
                    });
                }
            }
            return folders;
        }
        catch (error) {
            this.outputChannel.log(`Error reading planning folders: ${error}`);
            return [];
        }
    }
    /**
     * Get system info
     */
    async getSystemInfo(cortexPath) {
        const detection = this.workspaceDetector.detectCortexInstallation();
        return {
            cortexInstalled: !!cortexPath,
            cortexPath: cortexPath || 'Not found',
            workspaceType: detection.isCortexRepo ? 'CORTEX Repository' : 'User Workspace',
            hasManifests: detection.hasManifests,
            hasCortexBrain: detection.hasCortexBrain
        };
    }
    /**
     * Open a planning folder
     */
    async openPlan(planPath) {
        const uri = vscode.Uri.file(planPath);
        await vscode.commands.executeCommand('vscode.openFolder', uri, { forceNewWindow: false });
    }
    /**
     * Count files in directory
     */
    countFiles(dirPath) {
        try {
            if (!fs.existsSync(dirPath)) {
                return 0;
            }
            return fs.readdirSync(dirPath).length;
        }
        catch {
            return 0;
        }
    }
    /**
     * Infer operation type from filename
     */
    inferOperationType(filename) {
        if (filename.includes('plan'))
            return 'Planning';
        if (filename.includes('tdd'))
            return 'TDD';
        if (filename.includes('maintenance'))
            return 'Maintenance';
        if (filename.includes('sanitize'))
            return 'Sanitization';
        if (filename.includes('refine'))
            return 'Refinement';
        return 'Unknown';
    }
    /**
     * Get HTML content for the webview
     */
    getHtmlContent() {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            padding: 20px;
            line-height: 1.6;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--vscode-panel-border);
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: 600;
        }
        
        .header-actions {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }
        
        .btn:hover {
            background: var(--vscode-button-hoverBackground);
        }
        
        .btn-secondary {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        
        .btn-secondary:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: var(--vscode-sideBar-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            padding: 20px;
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .card-title {
            font-size: 18px;
            font-weight: 600;
        }
        
        .card-badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .badge-healthy {
            background: #4caf5022;
            color: #4caf50;
        }
        
        .badge-warning {
            background: #ff980022;
            color: #ff9800;
        }
        
        .badge-error {
            background: #f4433622;
            color: #f44336;
        }
        
        .health-score {
            font-size: 48px;
            font-weight: 700;
            text-align: center;
            margin: 20px 0;
            color: var(--vscode-textLink-foreground);
        }
        
        .health-metrics {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        
        .metric {
            padding: 12px;
            background: var(--vscode-editor-background);
            border-radius: 6px;
        }
        
        .metric-label {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 4px;
        }
        
        .metric-value {
            font-size: 20px;
            font-weight: 600;
        }
        
        .operations-list, .plans-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .operation-item, .plan-item {
            padding: 12px;
            margin-bottom: 8px;
            background: var(--vscode-editor-background);
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .operation-item:hover, .plan-item:hover {
            background: var(--vscode-list-hoverBackground);
        }
        
        .operation-header, .plan-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
        }
        
        .operation-type, .plan-name {
            font-weight: 600;
        }
        
        .operation-time, .plan-date {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }
        
        .quick-actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
        }
        
        .action-btn {
            padding: 16px;
            background: var(--vscode-button-secondaryBackground);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            cursor: pointer;
            text-align: center;
            transition: all 0.2s;
        }
        
        .action-btn:hover {
            background: var(--vscode-list-hoverBackground);
            transform: translateY(-2px);
        }
        
        .action-icon {
            font-size: 24px;
            margin-bottom: 8px;
        }
        
        .action-label {
            font-size: 14px;
            font-weight: 500;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: var(--vscode-descriptionForeground);
        }
        
        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 6px;
        }
        
        .status-success { background: #4caf50; }
        .status-failed { background: #f44336; }
        .status-progress { background: #ff9800; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 CORTEX Dashboard</h1>
        <div class="header-actions">
            <button class="btn btn-secondary" onclick="refresh()">🔄 Refresh</button>
        </div>
    </div>
    
    <div class="dashboard-grid">
        <!-- Brain Health Card -->
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Brain Health</h2>
                <span class="card-badge badge-healthy" id="health-badge">Healthy</span>
            </div>
            <div class="health-score" id="health-score">--</div>
            <div class="health-metrics">
                <div class="metric">
                    <div class="metric-label">Tier 0 (Governance)</div>
                    <div class="metric-value" id="tier0-value">--</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Tier 1 (Working Memory)</div>
                    <div class="metric-value" id="tier1-value">--</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Tier 2 (Knowledge Graph)</div>
                    <div class="metric-value" id="tier2-value">--</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Tier 3 (Dev Context)</div>
                    <div class="metric-value" id="tier3-value">--</div>
                </div>
            </div>
        </div>
        
        <!-- Recent Operations Card -->
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">Recent Operations</h2>
            </div>
            <div class="operations-list" id="operations-list">
                <div class="empty-state">No recent operations</div>
            </div>
        </div>
    </div>
    
    <!-- Planning Folders Card -->
    <div class="card">
        <div class="card-header">
            <h2 class="card-title">Active Planning Folders</h2>
        </div>
        <div class="plans-list" id="plans-list">
            <div class="empty-state">No planning folders found</div>
        </div>
    </div>
    
    <!-- Quick Actions Card -->
    <div class="card" style="margin-top: 20px;">
        <div class="card-header">
            <h2 class="card-title">Quick Actions</h2>
        </div>
        <div class="quick-actions">
            <div class="action-btn" onclick="executeCommand('cortex.plan')">
                <div class="action-icon">📋</div>
                <div class="action-label">Create Plan</div>
            </div>
            <div class="action-btn" onclick="executeCommand('cortex.startTdd')">
                <div class="action-icon">🧪</div>
                <div class="action-label">Start TDD</div>
            </div>
            <div class="action-btn" onclick="executeCommand('cortex.systemMaintenance')">
                <div class="action-icon">🔧</div>
                <div class="action-label">Maintenance</div>
            </div>
            <div class="action-btn" onclick="executeCommand('cortex.sanitize')">
                <div class="action-icon">🧹</div>
                <div class="action-label">Sanitize</div>
            </div>
            <div class="action-btn" onclick="executeCommand('cortex.refine')">
                <div class="action-icon">✨</div>
                <div class="action-label">Refine</div>
            </div>
            <div class="action-btn" onclick="executeCommand('cortex.onboard')">
                <div class="action-icon">🚀</div>
                <div class="action-label">Onboard</div>
            </div>
        </div>
    </div>
    
    <script>
        const vscode = acquireVsCodeApi();
        
        // Request initial data
        window.addEventListener('load', () => {
            refresh();
        });
        
        // Handle messages from extension
        window.addEventListener('message', event => {
            const message = event.data;
            if (message.command === 'updateData') {
                updateDashboard(message.data);
            }
        });
        
        function refresh() {
            vscode.postMessage({ command: 'refresh' });
        }
        
        function executeCommand(commandId) {
            vscode.postMessage({ command: 'executeCommand', commandId });
        }
        
        function openPlan(planPath) {
            vscode.postMessage({ command: 'openPlan', planPath });
        }
        
        function updateDashboard(data) {
            // Update brain health
            if (data.brainHealth) {
                const health = data.brainHealth;
                document.getElementById('health-score').textContent = health.overall + '%';
                
                const badge = document.getElementById('health-badge');
                badge.textContent = health.overall >= 80 ? 'Healthy' : 
                                   health.overall >= 50 ? 'Warning' : 'Critical';
                badge.className = 'card-badge ' + 
                    (health.overall >= 80 ? 'badge-healthy' : 
                     health.overall >= 50 ? 'badge-warning' : 'badge-error');
                
                document.getElementById('tier0-value').textContent = health.tier0.issues;
                document.getElementById('tier1-value').textContent = health.tier1.operations;
                document.getElementById('tier2-value').textContent = health.tier2.patterns;
                document.getElementById('tier3-value').textContent = health.tier3.context;
            }
            
            // Update recent operations
            if (data.recentOperations) {
                const opsList = document.getElementById('operations-list');
                if (data.recentOperations.length === 0) {
                    opsList.innerHTML = '<div class="empty-state">No recent operations</div>';
                } else {
                    opsList.innerHTML = data.recentOperations.map(op => \`
                        <div class="operation-item">
                            <div class="operation-header">
                                <span class="operation-type">
                                    <span class="status-dot status-\${op.status}"></span>
                                    \${op.type}
                                </span>
                                <span class="operation-time">\${formatTime(op.timestamp)}</span>
                            </div>
                            <div class="operation-time">Duration: \${op.duration || 'N/A'}</div>
                        </div>
                    \`).join('');
                }
            }
            
            // Update planning folders
            if (data.planningFolders) {
                const plansList = document.getElementById('plans-list');
                if (data.planningFolders.length === 0) {
                    plansList.innerHTML = '<div class="empty-state">No planning folders found</div>';
                } else {
                    plansList.innerHTML = data.planningFolders.map(plan => \`
                        <div class="plan-item" onclick="openPlan('\${plan.path}')">
                            <div class="plan-header">
                                <span class="plan-name">📁 \${plan.name}</span>
                                <span class="plan-date">\${formatDate(plan.created)}</span>
                            </div>
                            <div class="operation-time">Status: \${plan.status}</div>
                        </div>
                    \`).join('');
                }
            }
        }
        
        function formatTime(timestamp) {
            const date = new Date(timestamp);
            const now = new Date();
            const diff = now.getTime() - date.getTime();
            const hours = Math.floor(diff / (1000 * 60 * 60));
            
            if (hours === 0) return 'Just now';
            if (hours < 24) return \`\${hours}h ago\`;
            return \`\${Math.floor(hours / 24)}d ago\`;
        }
        
        function formatDate(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric',
                year: 'numeric'
            });
        }
    </script>
</body>
</html>`;
    }
}
exports.DashboardProvider = DashboardProvider;
//# sourceMappingURL=dashboardProvider.js.map