"use strict";
/**
 * CORTEX Token Dashboard - Real-time Token Tracking UI
 *
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Proprietary - See LICENSE file for terms
 */
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
exports.TokenDashboardProvider = void 0;
const vscode = __importStar(require("vscode"));
class TokenDashboardProvider {
    constructor(extensionUri, brainBridge) {
        this.extensionUri = extensionUri;
        this.brainBridge = brainBridge;
    }
    resolveWebviewView(webviewView, context, _token) {
        this.view = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this.extensionUri]
        };
        webviewView.webview.html = this.getHtmlForWebview(webviewView.webview);
        // Start auto-refresh
        const config = vscode.workspace.getConfiguration('cortex');
        const refreshSeconds = config.get('tokenDashboard.refreshInterval', 10);
        this.refreshInterval = setInterval(() => {
            this.refresh();
        }, refreshSeconds * 1000);
        // Handle messages from webview
        webviewView.webview.onDidReceiveMessage(async (message) => {
            switch (message.command) {
                case 'optimize':
                    await this.brainBridge.optimizeTokens();
                    this.refresh();
                    vscode.window.showInformationMessage('Token optimization complete');
                    break;
                case 'clearCache':
                    await this.brainBridge.clearCache();
                    this.refresh();
                    vscode.window.showInformationMessage('Conversation cache cleared');
                    break;
                case 'refresh':
                    this.refresh();
                    break;
            }
        });
        // Initial refresh
        this.refresh();
    }
    async refresh() {
        if (!this.view) {
            return;
        }
        try {
            const metrics = await this.brainBridge.getTokenMetrics();
            this.view.webview.postMessage({
                command: 'update',
                metrics: metrics
            });
        }
        catch (error) {
            console.error('Failed to refresh token metrics:', error);
        }
    }
    getHtmlForWebview(webview) {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX Token Dashboard</title>
    <style>
        body {
            padding: 10px;
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
        }
        .metric-card {
            background-color: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            border: 1px solid var(--vscode-panel-border);
        }
        .metric-title {
            font-size: 12px;
            opacity: 0.8;
            margin-bottom: 4px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
        }
        .metric-sub {
            font-size: 11px;
            opacity: 0.7;
            margin-top: 4px;
        }
        .status-ok {
            color: var(--vscode-testing-iconPassed);
        }
        .status-warning {
            color: var(--vscode-editorWarning-foreground);
        }
        .status-critical {
            color: var(--vscode-editorError-foreground);
        }
        .button {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
            margin-bottom: 8px;
            font-size: 13px;
        }
        .button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        .button-secondary {
            background-color: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        .button-secondary:hover {
            background-color: var(--vscode-button-secondaryHoverBackground);
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background-color: var(--vscode-progressBar-background);
            border-radius: 4px;
            margin-top: 8px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background-color: var(--vscode-progressBar-background);
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <h2>Token Dashboard</h2>
    
    <div class="metric-card">
        <div class="metric-title">Session Tokens</div>
        <div class="metric-value" id="sessionTokens">-</div>
        <div class="metric-sub">Est. Cost: $<span id="costEstimate">0.00</span></div>
    </div>

    <div class="metric-card">
        <div class="metric-title">Cache Status</div>
        <div class="metric-value" id="cacheStatus">-</div>
        <div class="metric-sub"><span id="cacheSize">0</span> KB / <span id="patternCount">0</span> patterns</div>
        <div class="progress-bar">
            <div class="progress-fill" id="cacheProgress" style="width: 0%"></div>
        </div>
    </div>

    <div class="metric-card">
        <div class="metric-title">Optimization Rate</div>
        <div class="metric-value" id="optimizationRate">-</div>
        <div class="metric-sub">ML-powered context compression</div>
    </div>

    <div class="metric-card">
        <div class="metric-title">Total Tokens</div>
        <div class="metric-value" id="totalTokens">-</div>
        <div class="metric-sub">All conversations</div>
    </div>

    <button class="button" onclick="optimize()">🚀 Optimize Tokens</button>
    <button class="button button-secondary" onclick="clearCache()">🗑️ Clear Cache</button>
    <button class="button button-secondary" onclick="refresh()">🔄 Refresh</button>

    <script>
        const vscode = acquireVsCodeApi();

        function optimize() {
            vscode.postMessage({ command: 'optimize' });
        }

        function clearCache() {
            vscode.postMessage({ command: 'clearCache' });
        }

        function refresh() {
            vscode.postMessage({ command: 'refresh' });
        }

        window.addEventListener('message', event => {
            const message = event.data;
            if (message.command === 'update') {
                updateMetrics(message.metrics);
            }
        });

        function updateMetrics(metrics) {
            // Session tokens
            document.getElementById('sessionTokens').textContent = 
                metrics.sessionTokens.toLocaleString();
            document.getElementById('costEstimate').textContent = 
                metrics.costEstimate.toFixed(4);

            // Cache status
            const statusElement = document.getElementById('cacheStatus');
            statusElement.textContent = metrics.cacheStatus;
            statusElement.className = 'metric-value';
            
            if (metrics.cacheStatus === 'OK') {
                statusElement.classList.add('status-ok');
            } else if (metrics.cacheStatus === 'WARNING') {
                statusElement.classList.add('status-warning');
            } else if (metrics.cacheStatus === 'CRITICAL') {
                statusElement.classList.add('status-critical');
            }

            document.getElementById('cacheSize').textContent = 
                (metrics.cacheSize / 1024).toFixed(1);
            document.getElementById('patternCount').textContent = 
                metrics.patternCount;

            // Cache progress bar (40k soft limit, 50k hard limit)
            const cachePercentage = (metrics.sessionTokens / 50000) * 100;
            document.getElementById('cacheProgress').style.width = 
                Math.min(cachePercentage, 100) + '%';

            // Optimization rate
            document.getElementById('optimizationRate').textContent = 
                (metrics.optimizationRate * 100).toFixed(1) + '%';

            // Total tokens
            document.getElementById('totalTokens').textContent = 
                metrics.totalTokens.toLocaleString();
        }
    </script>
</body>
</html>`;
    }
    dispose() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}
exports.TokenDashboardProvider = TokenDashboardProvider;
//# sourceMappingURL=tokenDashboard.js.map