import * as vscode from 'vscode';
import * as path from 'path';
import { WorkspaceDetector } from './workspaceDetector';
import { PythonExecutor } from './pythonExecutor';
import { OutputChannelManager } from './outputChannel';

/**
 * Configuration data structure
 */
export interface CortexConfiguration {
    pythonPath: string;
    cortexPath: string;
    enableCopilotIntegration: boolean;
    autoRefreshDashboard: boolean;
}

/**
 * Manages the CORTEX Configuration UI
 */
export class ConfigurationProvider {
    private static instance: ConfigurationProvider;
    private panel: vscode.WebviewPanel | undefined;
    private workspaceDetector: WorkspaceDetector;
    private pythonExecutor: PythonExecutor;
    private outputChannel: OutputChannelManager;

    private constructor(private context: vscode.ExtensionContext) {
        this.workspaceDetector = WorkspaceDetector.getInstance();
        this.pythonExecutor = PythonExecutor.getInstance();
        this.outputChannel = OutputChannelManager.getInstance();
    }

    public static getInstance(context?: vscode.ExtensionContext): ConfigurationProvider {
        if (!ConfigurationProvider.instance && context) {
            ConfigurationProvider.instance = new ConfigurationProvider(context);
        }
        return ConfigurationProvider.instance;
    }

    /**
     * Show or create the configuration panel
     */
    public show(): void {
        if (this.panel) {
            this.panel.reveal(vscode.ViewColumn.One);
        } else {
            this.createPanel();
        }
    }

    /**
     * Create the webview panel
     */
    private createPanel(): void {
        this.panel = vscode.window.createWebviewPanel(
            'cortexConfiguration',
            'CORTEX Configuration',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.file(path.join(this.context.extensionPath, 'media'))
                ]
            }
        );

        this.panel.iconPath = vscode.Uri.file(
            path.join(this.context.extensionPath, 'media', 'icon.png')
        );

        this.panel.webview.html = this.getHtmlContent();

        // Handle messages from the webview
        this.panel.webview.onDidReceiveMessage(
            message => this.handleWebviewMessage(message),
            undefined,
            this.context.subscriptions
        );

        // Clean up when panel is closed
        this.panel.onDidDispose(
            () => { this.panel = undefined; },
            undefined,
            this.context.subscriptions
        );

        // Load current configuration
        this.loadConfiguration();
    }

    /**
     * Handle messages from the webview
     */
    private async handleWebviewMessage(message: any): Promise<void> {
        this.outputChannel.log(`Configuration message: ${message.command}`);

        switch (message.command) {
            case 'load':
                this.loadConfiguration();
                break;
            case 'save':
                await this.saveConfiguration(message.config);
                break;
            case 'detect':
                await this.autoDetectPaths();
                break;
            case 'validate':
                await this.validateConfiguration(message.config);
                break;
            case 'reset':
                await this.resetConfiguration();
                break;
        }
    }

    /**
     * Load current configuration
     */
    private loadConfiguration(): void {
        if (!this.panel) {
            return;
        }

        const config = vscode.workspace.getConfiguration('cortex');
        const detection = this.workspaceDetector.detectCortexInstallation();

        const currentConfig: CortexConfiguration = {
            pythonPath: config.get<string>('pythonPath') || '',
            cortexPath: config.get<string>('cortexPath') || '',
            enableCopilotIntegration: config.get<boolean>('enableCopilotIntegration') ?? true,
            autoRefreshDashboard: config.get<boolean>('autoRefreshDashboard') ?? true
        };

        this.panel.webview.postMessage({
            command: 'configLoaded',
            config: currentConfig,
            detection: {
                isCortexRepo: detection.isCortexRepo,
                workspacePath: detection.workspacePath,
                hasManifests: detection.hasManifests,
                hasCortexBrain: detection.hasCortexBrain
            }
        });
    }

    /**
     * Save configuration
     */
    private async saveConfiguration(config: CortexConfiguration): Promise<void> {
        try {
            const vsConfig = vscode.workspace.getConfiguration('cortex');

            await vsConfig.update('pythonPath', config.pythonPath, vscode.ConfigurationTarget.Global);
            await vsConfig.update('cortexPath', config.cortexPath, vscode.ConfigurationTarget.Global);
            await vsConfig.update('enableCopilotIntegration', config.enableCopilotIntegration, vscode.ConfigurationTarget.Global);
            await vsConfig.update('autoRefreshDashboard', config.autoRefreshDashboard, vscode.ConfigurationTarget.Global);

            // Update runtime paths
            this.pythonExecutor.updatePaths(config.pythonPath, config.cortexPath);

            this.outputChannel.log('Configuration saved successfully');

            if (this.panel) {
                this.panel.webview.postMessage({
                    command: 'saveSuccess',
                    message: 'Configuration saved successfully!'
                });
            }

            vscode.window.showInformationMessage('CORTEX configuration saved successfully!');

        } catch (error) {
            const errorMsg = error instanceof Error ? error.message : String(error);
            this.outputChannel.log(`Error saving configuration: ${errorMsg}`);

            if (this.panel) {
                this.panel.webview.postMessage({
                    command: 'saveError',
                    message: `Failed to save: ${errorMsg}`
                });
            }
        }
    }

    /**
     * Auto-detect Python and CORTEX paths
     */
    private async autoDetectPaths(): Promise<void> {
        this.outputChannel.log('Auto-detecting paths...');

        // Detect CORTEX path
        const cortexPath = this.workspaceDetector.getCortexInstallationPath();

        // Detect Python path (simplified - would use more sophisticated detection)
        const pythonPath = 'python3'; // Default, could be enhanced

        if (this.panel) {
            this.panel.webview.postMessage({
                command: 'pathsDetected',
                paths: {
                    pythonPath,
                    cortexPath: cortexPath || ''
                }
            });
        }

        this.outputChannel.log(`Detected paths - Python: ${pythonPath}, CORTEX: ${cortexPath || 'not found'}`);
    }

    /**
     * Validate configuration
     */
    private async validateConfiguration(config: CortexConfiguration): Promise<void> {
        const errors: string[] = [];
        const warnings: string[] = [];

        // Validate Python path
        if (config.pythonPath) {
            const pythonValid = await this.pythonExecutor.validatePythonInstallation();
            if (!pythonValid) {
                errors.push('Python executable not found or not working');
            }
        } else {
            warnings.push('Python path not configured (will use default "python3")');
        }

        // Validate CORTEX path
        if (config.cortexPath) {
            const detection = this.workspaceDetector.detectCortexInstallation();
            if (!detection.isCortexRepo && !detection.hasCortexBrain) {
                errors.push('CORTEX installation not found at specified path');
            }
        } else {
            warnings.push('CORTEX path not configured (auto-detection will be used)');
        }

        if (this.panel) {
            this.panel.webview.postMessage({
                command: 'validationResult',
                isValid: errors.length === 0,
                errors,
                warnings
            });
        }

        this.outputChannel.log(`Validation complete - Errors: ${errors.length}, Warnings: ${warnings.length}`);
    }

    /**
     * Reset configuration to defaults
     */
    private async resetConfiguration(): Promise<void> {
        try {
            const vsConfig = vscode.workspace.getConfiguration('cortex');

            await vsConfig.update('pythonPath', '', vscode.ConfigurationTarget.Global);
            await vsConfig.update('cortexPath', '', vscode.ConfigurationTarget.Global);
            await vsConfig.update('enableCopilotIntegration', true, vscode.ConfigurationTarget.Global);
            await vsConfig.update('autoRefreshDashboard', true, vscode.ConfigurationTarget.Global);

            this.outputChannel.log('Configuration reset to defaults');

            if (this.panel) {
                this.panel.webview.postMessage({
                    command: 'resetSuccess',
                    message: 'Configuration reset to defaults'
                });
            }

            // Reload configuration
            this.loadConfiguration();

        } catch (error) {
            const errorMsg = error instanceof Error ? error.message : String(error);
            this.outputChannel.log(`Error resetting configuration: ${errorMsg}`);
        }
    }

    /**
     * Get HTML content for the webview
     */
    private getHtmlContent(): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX Configuration</title>
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
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--vscode-panel-border);
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .header p {
            color: var(--vscode-descriptionForeground);
        }
        
        .section {
            background: var(--vscode-sideBar-background);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 20px;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            font-weight: 500;
            margin-bottom: 8px;
        }
        
        .form-description {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 8px;
        }
        
        .input-group {
            display: flex;
            gap: 8px;
        }
        
        .form-input {
            flex: 1;
            padding: 8px 12px;
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            font-family: inherit;
            font-size: 14px;
        }
        
        .form-input:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .checkbox-group input[type="checkbox"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
        }
        
        .btn {
            padding: 8px 16px;
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-family: inherit;
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
        
        .btn-small {
            padding: 6px 12px;
            font-size: 12px;
        }
        
        .actions {
            display: flex;
            gap: 12px;
            margin-top: 24px;
        }
        
        .status-box {
            padding: 12px;
            border-radius: 6px;
            margin-top: 12px;
            display: none;
        }
        
        .status-box.success {
            background: #4caf5022;
            color: #4caf50;
            border: 1px solid #4caf5044;
        }
        
        .status-box.error {
            background: #f4433622;
            color: #f44336;
            border: 1px solid #f4433644;
        }
        
        .status-box.warning {
            background: #ff980022;
            color: #ff9800;
            border: 1px solid #ff980044;
        }
        
        .status-box.info {
            background: #2196f322;
            color: #2196f3;
            border: 1px solid #2196f344;
        }
        
        .detection-info {
            background: var(--vscode-editor-background);
            padding: 12px;
            border-radius: 6px;
            margin-top: 12px;
            font-size: 13px;
        }
        
        .detection-row {
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
        }
        
        .detection-label {
            color: var(--vscode-descriptionForeground);
        }
        
        .detection-value {
            font-weight: 500;
        }
        
        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
        }
        
        .badge-success {
            background: #4caf5022;
            color: #4caf50;
        }
        
        .badge-error {
            background: #f4433622;
            color: #f44336;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚙️ CORTEX Configuration</h1>
        <p>Configure Python path, CORTEX installation, and extension settings</p>
    </div>
    
    <!-- Paths Section -->
    <div class="section">
        <div class="section-title">📁 Paths</div>
        
        <div class="form-group">
            <label class="form-label">Python Executable Path</label>
            <div class="form-description">
                Path to Python 3.8+ executable. Leave empty for auto-detection (uses "python3").
            </div>
            <div class="input-group">
                <input type="text" class="form-input" id="pythonPath" placeholder="/usr/bin/python3 or python3">
                <button class="btn btn-secondary btn-small" onclick="detectPaths()">Auto-Detect</button>
            </div>
        </div>
        
        <div class="form-group">
            <label class="form-label">CORTEX Installation Path</label>
            <div class="form-description">
                Path to CORTEX repository. Leave empty for auto-detection.
            </div>
            <input type="text" class="form-input" id="cortexPath" placeholder="/Users/you/PROJECTS/CORTEX">
        </div>
        
        <div class="detection-info" id="detectionInfo">
            <div class="detection-row">
                <span class="detection-label">Workspace Type:</span>
                <span class="detection-value" id="workspaceType">-</span>
            </div>
            <div class="detection-row">
                <span class="detection-label">CORTEX Brain:</span>
                <span class="detection-value" id="cortexBrain">-</span>
            </div>
            <div class="detection-row">
                <span class="detection-label">Manifests:</span>
                <span class="detection-value" id="manifests">-</span>
            </div>
        </div>
    </div>
    
    <!-- Features Section -->
    <div class="section">
        <div class="section-title">✨ Features</div>
        
        <div class="form-group">
            <div class="checkbox-group">
                <input type="checkbox" id="enableCopilotIntegration" checked>
                <label class="form-label" style="margin: 0;">Enable GitHub Copilot Integration</label>
            </div>
            <div class="form-description" style="margin-left: 26px;">
                Provide CORTEX context to GitHub Copilot Chat for natural language commands.
            </div>
        </div>
        
        <div class="form-group">
            <div class="checkbox-group">
                <input type="checkbox" id="autoRefreshDashboard" checked>
                <label class="form-label" style="margin: 0;">Auto-Refresh Dashboard</label>
            </div>
            <div class="form-description" style="margin-left: 26px;">
                Automatically update dashboard when brain data changes.
            </div>
        </div>
    </div>
    
    <!-- Status Messages -->
    <div class="status-box" id="statusBox"></div>
    
    <!-- Actions -->
    <div class="actions">
        <button class="btn" onclick="saveConfiguration()">💾 Save Configuration</button>
        <button class="btn btn-secondary" onclick="validateConfiguration()">✓ Validate</button>
        <button class="btn btn-secondary" onclick="resetConfiguration()">↺ Reset to Defaults</button>
    </div>
    
    <script>
        const vscode = acquireVsCodeApi();
        
        // Request initial configuration on load
        window.addEventListener('load', () => {
            vscode.postMessage({ command: 'load' });
        });
        
        // Handle messages from extension
        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.command) {
                case 'configLoaded':
                    loadConfig(message.config, message.detection);
                    break;
                case 'saveSuccess':
                    showStatus('success', message.message);
                    break;
                case 'saveError':
                    showStatus('error', message.message);
                    break;
                case 'pathsDetected':
                    document.getElementById('pythonPath').value = message.paths.pythonPath;
                    document.getElementById('cortexPath').value = message.paths.cortexPath;
                    showStatus('info', 'Paths auto-detected. Review and save if correct.');
                    break;
                case 'validationResult':
                    showValidationResult(message);
                    break;
                case 'resetSuccess':
                    showStatus('success', message.message);
                    break;
            }
        });
        
        function loadConfig(config, detection) {
            document.getElementById('pythonPath').value = config.pythonPath || '';
            document.getElementById('cortexPath').value = config.cortexPath || '';
            document.getElementById('enableCopilotIntegration').checked = config.enableCopilotIntegration;
            document.getElementById('autoRefreshDashboard').checked = config.autoRefreshDashboard;
            
            // Update detection info
            document.getElementById('workspaceType').textContent = 
                detection.isCortexRepo ? 'CORTEX Repository' : 'User Workspace';
            document.getElementById('cortexBrain').innerHTML = 
                detection.hasCortexBrain 
                    ? '<span class="badge badge-success">Found</span>' 
                    : '<span class="badge badge-error">Not Found</span>';
            document.getElementById('manifests').innerHTML = 
                detection.hasManifests 
                    ? '<span class="badge badge-success">Found</span>' 
                    : '<span class="badge badge-error">Not Found</span>';
        }
        
        function saveConfiguration() {
            const config = {
                pythonPath: document.getElementById('pythonPath').value.trim(),
                cortexPath: document.getElementById('cortexPath').value.trim(),
                enableCopilotIntegration: document.getElementById('enableCopilotIntegration').checked,
                autoRefreshDashboard: document.getElementById('autoRefreshDashboard').checked
            };
            
            vscode.postMessage({ command: 'save', config });
        }
        
        function detectPaths() {
            vscode.postMessage({ command: 'detect' });
            showStatus('info', 'Detecting paths...');
        }
        
        function validateConfiguration() {
            const config = {
                pythonPath: document.getElementById('pythonPath').value.trim(),
                cortexPath: document.getElementById('cortexPath').value.trim(),
                enableCopilotIntegration: document.getElementById('enableCopilotIntegration').checked,
                autoRefreshDashboard: document.getElementById('autoRefreshDashboard').checked
            };
            
            vscode.postMessage({ command: 'validate', config });
            showStatus('info', 'Validating configuration...');
        }
        
        function resetConfiguration() {
            if (confirm('Reset all settings to defaults?')) {
                vscode.postMessage({ command: 'reset' });
            }
        }
        
        function showStatus(type, message) {
            const statusBox = document.getElementById('statusBox');
            statusBox.className = 'status-box ' + type;
            statusBox.textContent = message;
            statusBox.style.display = 'block';
            
            setTimeout(() => {
                statusBox.style.display = 'none';
            }, 5000);
        }
        
        function showValidationResult(result) {
            let message = '';
            let type = 'success';
            
            if (result.isValid) {
                message = '✓ Configuration is valid!';
                if (result.warnings.length > 0) {
                    message += '\\n\\nWarnings:\\n• ' + result.warnings.join('\\n• ');
                    type = 'warning';
                }
            } else {
                message = '✗ Configuration has errors:\\n• ' + result.errors.join('\\n• ');
                if (result.warnings.length > 0) {
                    message += '\\n\\nWarnings:\\n• ' + result.warnings.join('\\n• ');
                }
                type = 'error';
            }
            
            showStatus(type, message);
        }
    </script>
</body>
</html>`;
    }
}
