"""
Extension Scaffold Plugin for CORTEX 2.0

Generates complete VS Code extension project structure automatically.
This is the core implementation for Phase 3 (VS Code Extension).

Features:
- Complete TypeScript extension project generation
- Python ↔ TypeScript bridge setup
- package.json with all dependencies
- Chat participant (@cortex) implementation
- Lifecycle hooks (focus/blur, checkpoint)
- External monitoring (@copilot capture)
- Test infrastructure
- Build and package scripts

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import json
import logging
import os
from urllib.parse import urlunparse

from src.plugins.base_plugin import BasePlugin, PluginMetadata, PluginCategory, PluginPriority
from src.plugins.hooks import HookPoint

logger = logging.getLogger(__name__)


def _build_default_repository_url():
    """Build default repository URL using proper URL construction"""
    protocol = os.getenv('CORTEX_GITHUB_PROTOCOL', 'https')
    domain = os.getenv('CORTEX_GITHUB_DOMAIN', 'github.com')
    user = os.getenv('CORTEX_GITHUB_USER', 'asifhussain60')
    repo = os.getenv('CORTEX_REPO_NAME', 'CORTEX')
    
    # Use urlunparse for proper URL construction
    path = f"/{user}/{repo}"
    return urlunparse((protocol, domain, path, '', '', ''))


class Plugin(BasePlugin):
    """Extension Scaffold Plugin - Generates VS Code extension project"""
    
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="extension_scaffold",
            name="Extension Scaffold Generator",
            version="1.0.0",
            category=PluginCategory.EXTENSION,
            priority=PluginPriority.HIGH,
            description="Generates complete VS Code extension project structure",
            author="CORTEX Team",
            dependencies=[],
            hooks=[HookPoint.ON_EXTENSION_SCAFFOLD.value],
            config_schema={
                "type": "object",
                "properties": {
                    "extension_name": {
                        "type": "string",
                        "description": "Extension name (lowercase, hyphen-separated)",
                        "default": "cortex"
                    },
                    "display_name": {
                        "type": "string",
                        "description": "Display name for marketplace",
                        "default": "CORTEX - Cognitive Development Partner"
                    },
                    "publisher": {
                        "type": "string",
                        "description": "VS Code Marketplace publisher",
                        "default": "cortex-team"
                    },
                    "repository": {
                        "type": "string",
                        "description": "GitHub repository URL",
                        "default": os.getenv("CORTEX_DEFAULT_REPOSITORY", _build_default_repository_url())
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Output directory for extension",
                        "default": "cortex-extension"
                    },
                    "features": {
                        "type": "array",
                        "description": "Features to include",
                        "items": {
                            "enum": [
                                "chat_participant",
                                "conversation_capture",
                                "lifecycle_hooks",
                                "external_monitoring",
                                "resume_prompts",
                                "checkpoint_system",
                                "token_dashboard"
                            ]
                        },
                        "default": [
                            "chat_participant",
                            "conversation_capture",
                            "lifecycle_hooks",
                            "external_monitoring",
                            "resume_prompts",
                            "checkpoint_system",
                            "token_dashboard"
                        ]
                    }
                }
            }
        )
    
    def initialize(self) -> bool:
        """Initialize plugin - verify templates exist"""
        try:
            self.logger.info("Extension Scaffold Plugin initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize extension_scaffold: {e}")
            return False
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute extension scaffolding"""
        try:
            # Merge config with context
            config = {**self.config, **context}
            
            extension_name = config.get("extension_name", "cortex")
            display_name = config.get("display_name", "CORTEX - Cognitive Development Partner")
            publisher = config.get("publisher", "cortex-team")
            repository = config.get("repository", os.getenv("CORTEX_DEFAULT_REPOSITORY", _build_default_repository_url()))
            output_dir = config.get("output_dir", "cortex-extension")
            features = config.get("features", [
                "chat_participant",
                "conversation_capture",
                "lifecycle_hooks",
                "external_monitoring",
                "resume_prompts",
                "checkpoint_system",
                "token_dashboard"
            ])
            
            # Create output directory
            output_path = Path(output_dir)
            if output_path.exists():
                self.logger.warning(f"Output directory exists: {output_path}")
                return {
                    "success": False,
                    "error": f"Output directory already exists: {output_path}"
                }
            
            # Generate extension structure
            self.logger.info(f"Generating extension at: {output_path}")
            
            # 1. Create directory structure
            self._create_directory_structure(output_path)
            
            # 2. Generate package.json
            self._generate_package_json(
                output_path, extension_name, display_name, publisher, repository
            )
            
            # 3. Generate tsconfig.json
            self._generate_tsconfig(output_path)
            
            # 4. Generate TypeScript source files
            self._generate_typescript_files(output_path, features)
            
            # 5. Generate Python bridge
            self._generate_python_bridge(output_path)
            
            # 6. Generate tests
            self._generate_tests(output_path)
            
            # 7. Generate build/package scripts
            self._generate_scripts(output_path)
            
            # 8. Generate documentation
            self._generate_documentation(output_path, extension_name, display_name)
            
            # 9. Generate .vscodeignore
            self._generate_vscodeignore(output_path)
            
            # 10. Generate .gitignore
            self._generate_gitignore(output_path)
            
            return {
                "success": True,
                "output_dir": str(output_path.absolute()),
                "extension_name": extension_name,
                "features": features,
                "next_steps": [
                    f"cd {output_path}",
                    "npm install",
                    "npm run compile",
                    "Press F5 to debug in VS Code"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error scaffolding extension: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        return True
    
    def _create_directory_structure(self, output_path: Path) -> None:
        """Create extension directory structure"""
        directories = [
            output_path,
            output_path / "src",
            output_path / "src" / "cortex",
            output_path / "src" / "python",
            output_path / "src" / "test" / "suite",
            output_path / "out",
            output_path / ".vscode",
            output_path / "scripts",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Created directory: {directory}")
    
    def _generate_package_json(
        self,
        output_path: Path,
        extension_name: str,
        display_name: str,
        publisher: str,
        repository: str
    ) -> None:
        """Generate package.json with full VS Code extension configuration"""
        
        package_json = {
            "name": extension_name,
            "displayName": display_name,
            "description": "AI development assistant with persistent memory and context awareness",
            "version": "1.0.0",
            "author": "Asif Hussain",
            "publisher": publisher,
            "license": "SEE LICENSE IN LICENSE",
            "copyright": "Copyright (c) 2024-2025 Asif Hussain. All rights reserved.",
            "repository": {
                "type": "git",
                "url": repository
            },
            "engines": {
                "vscode": "^1.85.0"
            },
            "categories": [
                "AI",
                "Chat",
                "Programming Languages"
            ],
            "activationEvents": [
                "onStartupFinished"
            ],
            "main": "./out/extension.js",
            "contributes": {
                "chatParticipants": [
                    {
                        "id": "cortex",
                        "name": "CORTEX",
                        "description": "Cognitive development partner with memory",
                        "isSticky": True,
                        "commands": [
                            {
                                "name": "resume",
                                "description": "Resume last conversation"
                            },
                            {
                                "name": "checkpoint",
                                "description": "Save conversation checkpoint"
                            },
                            {
                                "name": "status",
                                "description": "Show current work status"
                            }
                        ]
                    }
                ],
                "commands": [
                    {
                        "command": "cortex.resume",
                        "title": "CORTEX: Resume Last Conversation"
                    },
                    {
                        "command": "cortex.checkpoint",
                        "title": "CORTEX: Save Checkpoint"
                    },
                    {
                        "command": "cortex.showHistory",
                        "title": "CORTEX: Show Conversation History"
                    },
                    {
                        "command": "cortex.clearHistory",
                        "title": "CORTEX: Clear Conversation History"
                    },
                    {
                        "command": "cortex.showTokenDashboard",
                        "title": "CORTEX: Show Token Dashboard"
                    }
                ],
                "viewsContainers": {
                    "activitybar": [
                        {
                            "id": "cortex",
                            "title": "CORTEX",
                            "icon": "resources/icon.svg"
                        }
                    ]
                },
                "views": {
                    "cortex": [
                        {
                            "id": "cortexTokenDashboard",
                            "name": "Token Dashboard"
                        },
                        {
                            "id": "cortexConversationHistory",
                            "name": "Conversation History"
                        }
                    ]
                },
                "configuration": {
                    "title": "CORTEX",
                    "properties": {
                        "cortex.autoCapture": {
                            "type": "boolean",
                            "default": True,
                            "description": "Automatically capture conversations"
                        },
                        "cortex.monitorCopilot": {
                            "type": "boolean",
                            "default": True,
                            "description": "Monitor GitHub Copilot conversations"
                        },
                        "cortex.autoCheckpoint": {
                            "type": "boolean",
                            "default": True,
                            "description": "Automatically checkpoint on focus loss"
                        },
                        "cortex.resumePrompt": {
                            "type": "boolean",
                            "default": True,
                            "description": "Show resume prompt on startup"
                        },
                        "cortex.pythonPath": {
                            "type": "string",
                            "default": "python",
                            "description": "Path to Python executable"
                        },
                        "cortex.brainPath": {
                            "type": "string",
                            "default": "",
                            "description": "Path to CORTEX brain directory (auto-detected if empty)"
                        }
                    }
                }
            },
            "scripts": {
                "vscode:prepublish": "npm run compile",
                "compile": "tsc -p ./",
                "watch": "tsc -watch -p ./",
                "pretest": "npm run compile",
                "test": "node ./out/test/runTest.js",
                "package": "vsce package",
                "publish": "vsce publish",
                "lint": "eslint src --ext ts",
                "format": "prettier --write \"src/**/*.ts\""
            },
            "devDependencies": {
                "@types/vscode": "^1.85.0",
                "@types/node": "^20.x",
                "@types/mocha": "^10.0.0",
                "@typescript-eslint/eslint-plugin": "^6.0.0",
                "@typescript-eslint/parser": "^6.0.0",
                "eslint": "^8.50.0",
                "prettier": "^3.0.0",
                "typescript": "^5.3.0",
                "@vscode/test-electron": "^2.3.0",
                "mocha": "^10.2.0",
                "@vscode/vsce": "^2.22.0"
            },
            "dependencies": {
                "node-ipc": "^11.1.0"
            }
        }
        
        package_path = output_path / "package.json"
        with open(package_path, "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2)
        
        self.logger.info(f"Generated package.json at: {package_path}")
    
    def _generate_tsconfig(self, output_path: Path) -> None:
        """Generate tsconfig.json for TypeScript compilation"""
        
        tsconfig = {
            "compilerOptions": {
                "module": "commonjs",
                "target": "ES2020",
                "outDir": "out",
                "lib": ["ES2020"],
                "sourceMap": True,
                "rootDir": "src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True
            },
            "exclude": ["node_modules", ".vscode-test"]
        }
        
        tsconfig_path = output_path / "tsconfig.json"
        with open(tsconfig_path, "w", encoding="utf-8") as f:
            json.dump(tsconfig, f, indent=2)
        
        self.logger.info(f"Generated tsconfig.json at: {tsconfig_path}")
    
    def _generate_typescript_files(self, output_path: Path, features: List[str]) -> None:
        """Generate all TypeScript source files"""
        
        # Generate extension.ts (main entry point)
        self._generate_extension_ts(output_path, features)
        
        # Generate chat participant
        if "chat_participant" in features:
            self._generate_chat_participant_ts(output_path)
        
        # Generate brain bridge
        self._generate_brain_bridge_ts(output_path)
        
        # Generate lifecycle manager
        if "lifecycle_hooks" in features:
            self._generate_lifecycle_manager_ts(output_path)
        
        # Generate checkpoint manager
        if "checkpoint_system" in features:
            self._generate_checkpoint_manager_ts(output_path)
        
        # Generate external monitor
        if "external_monitoring" in features:
            self._generate_external_monitor_ts(output_path)
        
        # Generate token dashboard provider
        if "token_dashboard" in features:
            self._generate_token_dashboard_ts(output_path)
    
    def _generate_extension_ts(self, output_path: Path, features: List[str]) -> None:
        """Generate extension.ts - main entry point"""
        
        content = '''// Extension entry point - auto-generated by ExtensionScaffoldPlugin
import * as vscode from 'vscode';
import { CortexChatParticipant } from './cortex/chatParticipant';
import { BrainBridge } from './cortex/brainBridge';
'''
        
        if "lifecycle_hooks" in features:
            content += "import { LifecycleManager } from './cortex/lifecycleManager';\n"
        if "checkpoint_system" in features:
            content += "import { CheckpointManager } from './cortex/checkpointManager';\n"
        if "external_monitoring" in features:
            content += "import { ExternalMonitor } from './cortex/externalMonitor';\n"
        if "token_dashboard" in features:
            content += "import { TokenDashboardProvider } from './cortex/tokenDashboard';\n"
        
        content += '''
export async function activate(context: vscode.ExtensionContext) {
    console.log('CORTEX extension activating...');
    
    try {
        // Initialize Python brain bridge
        const brainBridge = new BrainBridge(context);
        await brainBridge.initialize();
        
        // Register CORTEX chat participant
        const chatParticipant = new CortexChatParticipant(brainBridge);
        const participant = vscode.chat.createChatParticipant('cortex', async (request, context, stream, token) => {
            return await chatParticipant.handleRequest(request, context, stream, token);
        });
        
        participant.iconPath = vscode.Uri.joinPath(context.extensionUri, 'resources', 'icon.png');
        context.subscriptions.push(participant);
        
'''
        
        if "lifecycle_hooks" in features:
            content += '''        // Initialize lifecycle management
        const lifecycleManager = new LifecycleManager(brainBridge);
        lifecycleManager.setupHooks(context);
        
'''
        
        if "checkpoint_system" in features:
            content += '''        // Initialize checkpoint system
        const checkpointManager = new CheckpointManager(brainBridge);
        checkpointManager.startAutoCheckpoint();
        context.subscriptions.push(checkpointManager);
        
'''
        
        if "external_monitoring" in features:
            content += '''        // Initialize external monitoring
        const externalMonitor = new ExternalMonitor(brainBridge);
        externalMonitor.startMonitoring(context);
        
'''
        
        if "token_dashboard" in features:
            content += '''        // Register token dashboard
        const tokenDashboard = new TokenDashboardProvider(brainBridge);
        vscode.window.registerTreeDataProvider('cortexTokenDashboard', tokenDashboard);
        
'''
        
        content += '''        // Register commands
        context.subscriptions.push(
            vscode.commands.registerCommand('cortex.resume', async () => {
                await chatParticipant.resumeLastConversation();
            }),
            vscode.commands.registerCommand('cortex.checkpoint', async () => {
                await checkpointManager.createCheckpoint();
            }),
            vscode.commands.registerCommand('cortex.showHistory', async () => {
                await chatParticipant.showConversationHistory();
            }),
            vscode.commands.registerCommand('cortex.clearHistory', async () => {
                await brainBridge.clearHistory();
                vscode.window.showInformationMessage('Conversation history cleared');
            })
        );
        
        // Check for resume on startup
        const config = vscode.workspace.getConfiguration('cortex');
        if (config.get('resumePrompt')) {
            await chatParticipant.offerResume();
        }
        
        console.log('CORTEX extension activated successfully!');
    } catch (error) {
        console.error('Failed to activate CORTEX extension:', error);
        vscode.window.showErrorMessage(`CORTEX activation failed: ${error}`);
    }
}

export function deactivate() {
    console.log('CORTEX extension deactivating...');
}
'''
        
        extension_path = output_path / "src" / "extension.ts"
        with open(extension_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info(f"Generated extension.ts at: {extension_path}")
    
    def _generate_chat_participant_ts(self, output_path: Path) -> None:
        """Generate chatParticipant.ts - @cortex chat handler"""
        
        content = '''// Chat participant implementation - handles @cortex messages
import * as vscode from 'vscode';
import { BrainBridge } from './brainBridge';

export class CortexChatParticipant {
    constructor(private brainBridge: BrainBridge) {}
    
    async handleRequest(
        request: vscode.ChatRequest,
        context: vscode.ChatContext,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<vscode.ChatResult> {
        try {
            // Capture user message to Tier 1
            await this.brainBridge.captureMessage({
                user: request.prompt,
                timestamp: new Date().toISOString(),
                context: context.history.map(msg => ({
                    role: msg.participant,
                    content: msg.message
                }))
            });
            
            // Process through CORTEX router
            const response = await this.brainBridge.routeRequest(request.prompt, context);
            
            // Stream response
            stream.markdown(response.content);
            
            // Auto-save response to brain
            await this.brainBridge.captureResponse(response);
            
            return {
                metadata: {
                    conversationId: response.conversationId,
                    agent: response.agent
                }
            };
        } catch (error) {
            stream.markdown(`❌ Error: ${error}`);
            return { metadata: { error: String(error) } };
        }
    }
    
    async resumeLastConversation(): Promise<void> {
        const lastConv = await this.brainBridge.getLastActiveConversation();
        if (lastConv) {
            // Open chat with resume context
            const message = `Resume: ${lastConv.topic}\\n\\nLast activity: ${lastConv.lastActivity}\\n\\nProgress: ${lastConv.progress}`;
            vscode.window.showInformationMessage(message, 'Resume', 'Cancel').then(async (choice) => {
                if (choice === 'Resume') {
                    await this.brainBridge.resumeConversation(lastConv.id);
                }
            });
        } else {
            vscode.window.showInformationMessage('No active conversation to resume');
        }
    }
    
    async showConversationHistory(): Promise<void> {
        const history = await this.brainBridge.getConversationHistory();
        // TODO: Show in webview panel
        vscode.window.showInformationMessage(`${history.length} conversations in history`);
    }
    
    async offerResume(): Promise<void> {
        const lastConv = await this.brainBridge.getLastActiveConversation();
        if (lastConv && this._shouldOfferResume(lastConv)) {
            const message = `Resume: ${lastConv.topic}? (${this._formatTimeSince(lastConv.lastActivity)})`;
            vscode.window.showInformationMessage(message, 'Yes', 'No').then(async (choice) => {
                if (choice === 'Yes') {
                    await this.brainBridge.resumeConversation(lastConv.id);
                }
            });
        }
    }
    
    private _shouldOfferResume(conversation: any): boolean {
        // Offer resume if conversation was active within last 2 hours
        const twoHoursAgo = Date.now() - (2 * 60 * 60 * 1000);
        const lastActivity = new Date(conversation.lastActivity).getTime();
        return lastActivity > twoHoursAgo;
    }
    
    private _formatTimeSince(timestamp: string): string {
        const now = Date.now();
        const then = new Date(timestamp).getTime();
        const seconds = Math.floor((now - then) / 1000);
        
        if (seconds < 60) return `${seconds}s ago`;
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes}m ago`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours}h ago`;
        const days = Math.floor(hours / 24);
        return `${days}d ago`;
    }
}
'''
        
        file_path = output_path / "src" / "cortex" / "chatParticipant.ts"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info(f"Generated chatParticipant.ts")
    
    
    def _generate_brain_bridge_ts(self, output_path: Path) -> None:
        """Generate brainBridge.ts - Python ↔ TypeScript communication"""
        
        content = '''// Brain bridge - TypeScript ↔ Python IPC communication
import * as vscode from 'vscode';
import * as child_process from 'child_process';
import * as ipc from 'node-ipc';

export class BrainBridge {
    private pythonProcess: child_process.ChildProcess | null = null;
    private ipcClient: any = null;
    
    constructor(private context: vscode.ExtensionContext) {}
    
    async initialize(): Promise<void> {
        console.log('Initializing CORTEX brain bridge...');
        
        // Get Python path from configuration
        const config = vscode.workspace.getConfiguration('cortex');
        const pythonPath = config.get<string>('pythonPath', 'python');
        
        // Get CORTEX brain path
        const brainPath = config.get<string>('brainPath', '') || this._detectBrainPath();
        
        if (!brainPath) {
            throw new Error('CORTEX brain path not found. Please configure cortex.brainPath');
        }
        
        // Start Python IPC server
        const bridgeScript = `${brainPath}/src/plugins/extension_bridge.py`;
        this.pythonProcess = child_process.spawn(pythonPath, [bridgeScript]);
        
        // Setup IPC client
        ipc.config.id = 'cortex_extension';
        ipc.config.retry = 1500;
        ipc.config.silent = true;
        
        return new Promise((resolve, reject) => {
            ipc.connectTo('cortex_brain', () => {
                ipc.of.cortex_brain.on('connect', () => {
                    console.log('Connected to CORTEX brain');
                    this.ipcClient = ipc.of.cortex_brain;
                    resolve();
                });
                
                ipc.of.cortex_brain.on('error', (err: Error) => {
                    console.error('Brain bridge error:', err);
                    reject(err);
                });
            });
        });
    }
    
    async captureMessage(message: any): Promise<void> {
        return this._sendCommand('capture_message', message);
    }
    
    async captureResponse(response: any): Promise<void> {
        return this._sendCommand('capture_response', response);
    }
    
    async routeRequest(prompt: string, context: any): Promise<any> {
        return this._sendCommand('route_request', { prompt, context });
    }
    
    async getLastActiveConversation(): Promise<any> {
        return this._sendCommand('get_last_active_conversation', {});
    }
    
    async getConversationHistory(): Promise<any[]> {
        return this._sendCommand('get_conversation_history', {});
    }
    
    async resumeConversation(conversationId: string): Promise<void> {
        return this._sendCommand('resume_conversation', { conversationId });
    }
    
    async clearHistory(): Promise<void> {
        return this._sendCommand('clear_history', {});
    }
    
    async getTokenMetrics(): Promise<any> {
        return this._sendCommand('get_token_metrics', {});
    }
    
    dispose(): void {
        if (this.ipcClient) {
            ipc.disconnect('cortex_brain');
        }
        if (this.pythonProcess) {
            this.pythonProcess.kill();
        }
    }
    
    private _sendCommand(command: string, params: any): Promise<any> {
        return new Promise((resolve, reject) => {
            if (!this.ipcClient) {
                reject(new Error('Brain bridge not initialized'));
                return;
            }
            
            const requestId = Math.random().toString(36).substring(7);
            
            this.ipcClient.emit('command', {
                id: requestId,
                command,
                params
            });
            
            const timeout = setTimeout(() => {
                reject(new Error('Command timeout'));
            }, 30000);
            
            this.ipcClient.on(`response_${requestId}`, (response: any) => {
                clearTimeout(timeout);
                if (response.error) {
                    reject(new Error(response.error));
                } else {
                    resolve(response.result);
                }
            });
        });
    }
    
    private _detectBrainPath(): string {
        // Try to detect CORTEX brain path
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders && workspaceFolders.length > 0) {
            const rootPath = workspaceFolders[0].uri.fsPath;
            // Check if cortex-brain folder exists
            if (require('fs').existsSync(`${rootPath}/cortex-brain`)) {
                return rootPath;
            }
        }
        return '';
    }
}
'''
        
        file_path = output_path / "src" / "cortex" / "brainBridge.ts"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info("Generated brainBridge.ts")
    
    def _generate_lifecycle_manager_ts(self, output_path: Path) -> None:
        """Generate lifecycleManager.ts"""
        
        content = '''// Lifecycle manager - window state hooks
import * as vscode from 'vscode';
import { BrainBridge } from './brainBridge';

export class LifecycleManager {
    constructor(private brainBridge: BrainBridge) {}
    
    setupHooks(context: vscode.ExtensionContext): void {
        // Window focus/blur detection
        context.subscriptions.push(
            vscode.window.onDidChangeWindowState(async (state) => {
                if (!state.focused) {
                    console.log('Window losing focus - creating checkpoint');
                    // Auto-checkpoint on focus loss
                    const config = vscode.workspace.getConfiguration('cortex');
                    if (config.get('autoCheckpoint')) {
                        // Checkpoint will be handled by CheckpointManager
                    }
                }
            })
        );
    }
}
'''
        
        file_path = output_path / "src" / "cortex" / "lifecycleManager.ts"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info("Generated lifecycleManager.ts")
    
    def _generate_checkpoint_manager_ts(self, output_path: Path) -> None:
        """Generate checkpointManager.ts"""
        
        content = '''// Checkpoint manager - conversation state persistence
import * as vscode from 'vscode';
import { BrainBridge } from './brainBridge';

export class CheckpointManager implements vscode.Disposable {
    private checkpointInterval: NodeJS.Timeout | null = null;
    
    constructor(private brainBridge: BrainBridge) {}
    
    startAutoCheckpoint(): void {
        // Auto-checkpoint every 5 minutes
        this.checkpointInterval = setInterval(async () => {
            await this.createCheckpoint();
        }, 5 * 60 * 1000);
    }
    
    async createCheckpoint(): Promise<void> {
        try {
            await this.brainBridge._sendCommand('create_checkpoint', {});
            console.log('Checkpoint created');
        } catch (error) {
            console.error('Failed to create checkpoint:', error);
        }
    }
    
    dispose(): void {
        if (this.checkpointInterval) {
            clearInterval(this.checkpointInterval);
        }
    }
}
'''
        
        file_path = output_path / "src" / "cortex" / "checkpointManager.ts"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info("Generated checkpointManager.ts")
    
    def _generate_external_monitor_ts(self, output_path: Path) -> None:
        """Generate externalMonitor.ts - monitors @copilot chats"""
        
        content = '''// External monitor - capture @copilot conversations
import * as vscode from 'vscode';
import { BrainBridge } from './brainBridge';

export class ExternalMonitor {
    constructor(private brainBridge: BrainBridge) {}
    
    startMonitoring(context: vscode.ExtensionContext): void {
        // Monitor chat actions (proposed API - may need enablement)
        if (vscode.chat && 'onDidPerformChatAction' in vscode.chat) {
            context.subscriptions.push(
                (vscode.chat as any).onDidPerformChatAction(async (action: any) => {
                    if (action.participant?.id === 'copilot') {
                        // Capture Copilot chat to CORTEX brain
                        await this.brainBridge._sendCommand('capture_external_chat', {
                            participant: 'copilot',
                            message: action.message,
                            timestamp: new Date().toISOString()
                        });
                    }
                })
            );
        }
    }
}
'''
        
        file_path = output_path / "src" / "cortex" / "externalMonitor.ts"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info("Generated externalMonitor.ts")
    
    def _generate_token_dashboard_ts(self, output_path: Path) -> None:
        """Generate tokenDashboard.ts - real-time token metrics"""
        
        content = '''// Token dashboard provider - real-time metrics
import * as vscode from 'vscode';
import { BrainBridge } from './brainBridge';

export class TokenDashboardProvider implements vscode.TreeDataProvider<TokenMetricItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<TokenMetricItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;
    
    constructor(private brainBridge: BrainBridge) {
        // Refresh every 30 seconds
        setInterval(() => this.refresh(), 30000);
    }
    
    refresh(): void {
        this._onDidChangeTreeData.fire(undefined);
    }
    
    async getTreeItem(element: TokenMetricItem): Promise<vscode.TreeItem> {
        return element;
    }
    
    async getChildren(element?: TokenMetricItem): Promise<TokenMetricItem[]> {
        if (!element) {
            // Root level - show main metrics
            const metrics = await this.brainBridge.getTokenMetrics();
            return [
                new TokenMetricItem(
                    'Total Tokens',
                    metrics.totalTokens.toLocaleString(),
                    vscode.TreeItemCollapsibleState.None
                ),
                new TokenMetricItem(
                    'Saved by Optimization',
                    `${metrics.savedTokens.toLocaleString()} (${metrics.savingsPercent}%)`,
                    vscode.TreeItemCollapsibleState.None
                ),
                new TokenMetricItem(
                    'Active Conversations',
                    metrics.activeConversations.toString(),
                    vscode.TreeItemCollapsibleState.None
                ),
                new TokenMetricItem(
                    'Patterns Learned',
                    metrics.patternsCount.toString(),
                    vscode.TreeItemCollapsibleState.None
                )
            ];
        }
        return [];
    }
}

class TokenMetricItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        private value: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(label, collapsibleState);
        this.description = value;
    }
}
'''
        
        file_path = output_path / "src" / "cortex" / "tokenDashboard.ts"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info("Generated tokenDashboard.ts")
    
    def _generate_python_bridge(self, output_path: Path) -> None:
        """Generate Python IPC bridge server"""
        
        content = '''#!/usr/bin/env python3
"""
CORTEX Extension Bridge - Python IPC Server

Connects TypeScript extension to CORTEX Python brain.
Handles all communication via node-ipc protocol.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import json
import logging
from pathlib import Path

# Add CORTEX to path
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

from src.entry_point.cortex_entry import CortexEntry
from src.tier1.working_memory.conversation_manager import ConversationManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExtensionBridge:
    """IPC bridge between TypeScript extension and Python brain"""
    
    def __init__(self):
        self.cortex = CortexEntry()
        self.conversation_manager = ConversationManager()
    
    def handle_command(self, command: str, params: dict) -> dict:
        """Route command to appropriate handler"""
        
        handlers = {
            'capture_message': self._capture_message,
            'capture_response': self._capture_response,
            'route_request': self._route_request,
            'get_last_active_conversation': self._get_last_active_conversation,
            'get_conversation_history': self._get_conversation_history,
            'resume_conversation': self._resume_conversation,
            'clear_history': self._clear_history,
            'get_token_metrics': self._get_token_metrics,
            'capture_external_chat': self._capture_external_chat,
            'create_checkpoint': self._create_checkpoint
        }
        
        handler = handlers.get(command)
        if not handler:
            return {'error': f'Unknown command: {command}'}
        
        try:
            result = handler(params)
            return {'result': result}
        except Exception as e:
            logger.error(f'Error handling {command}: {e}')
            return {'error': str(e)}
    
    def _capture_message(self, params: dict) -> dict:
        """Capture user message to Tier 1"""
        # Implementation: Store message in Tier 1
        return {'success': True}
    
    def _capture_response(self, params: dict) -> dict:
        """Capture assistant response to Tier 1"""
        # Implementation: Store response in Tier 1
        return {'success': True}
    
    def _route_request(self, params: dict) -> dict:
        """Route request through CORTEX entry point"""
        prompt = params.get('prompt', '')
        result = self.cortex.process(prompt)
        return result
    
    def _get_last_active_conversation(self, params: dict) -> dict:
        """Get last active conversation"""
        # Implementation: Query Tier 1
        return {}
    
    def _get_conversation_history(self, params: dict) -> list:
        """Get conversation history"""
        # Implementation: Query Tier 1
        return []
    
    def _resume_conversation(self, params: dict) -> dict:
        """Resume conversation"""
        # Implementation: Load conversation state
        return {'success': True}
    
    def _clear_history(self, params: dict) -> dict:
        """Clear conversation history"""
        # Implementation: Clear Tier 1
        return {'success': True}
    
    def _get_token_metrics(self, params: dict) -> dict:
        """Get token usage metrics"""
        # Implementation: Query token dashboard data
        return {
            'totalTokens': 0,
            'savedTokens': 0,
            'savingsPercent': 0,
            'activeConversations': 0,
            'patternsCount': 0
        }
    
    def _capture_external_chat(self, params: dict) -> dict:
        """Capture external chat (e.g., @copilot)"""
        # Implementation: Store external conversation
        return {'success': True}
    
    def _create_checkpoint(self, params: dict) -> dict:
        """Create conversation checkpoint"""
        # Implementation: Checkpoint current state
        return {'success': True}
    
    def run(self):
        """Run IPC server"""
        logger.info('CORTEX Extension Bridge starting...')
        
        # Simple stdin/stdout protocol for now
        # TODO: Implement proper node-ipc server
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line)
                command_id = request.get('id')
                command = request.get('command')
                params = request.get('params', {})
                
                response = self.handle_command(command, params)
                response['id'] = command_id
                
                sys.stdout.write(json.dumps(response) + '\\n')
                sys.stdout.flush()
                
            except Exception as e:
                logger.error(f'Bridge error: {e}')
                break


if __name__ == '__main__':
    bridge = ExtensionBridge()
    bridge.run()
'''
        
        file_path = output_path / "src" / "python" / "extension_bridge.py"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info("Generated extension_bridge.py")
    
    def _generate_tests(self, output_path: Path) -> None:
        """Generate test files"""
        
        # runTest.ts
        content = '''import * as path from 'path';
import { runTests } from '@vscode/test-electron';

async function main() {
    try {
        const extensionDevelopmentPath = path.resolve(__dirname, '../../');
        const extensionTestsPath = path.resolve(__dirname, './suite/index');
        
        await runTests({ extensionDevelopmentPath, extensionTestsPath });
    } catch (err) {
        console.error('Failed to run tests:', err);
        process.exit(1);
    }
}

main();
'''
        
        file_path = output_path / "src" / "test" / "runTest.ts"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Test suite index
        content = '''import * as path from 'path';
import * as Mocha from 'mocha';
import * as glob from 'glob';

export function run(): Promise<void> {
    const mocha = new Mocha({
        ui: 'tdd',
        color: true
    });
    
    const testsRoot = path.resolve(__dirname, '.');
    
    return new Promise((resolve, reject) => {
        glob('**/**.test.js', { cwd: testsRoot }, (err, files) => {
            if (err) {
                return reject(err);
            }
            
            files.forEach(f => mocha.addFile(path.resolve(testsRoot, f)));
            
            try {
                mocha.run(failures => {
                    if (failures > 0) {
                        reject(new Error(`${failures} tests failed.`));
                    } else {
                        resolve();
                    }
                });
            } catch (err) {
                reject(err);
            }
        });
    });
}
'''
        
        file_path = output_path / "src" / "test" / "suite" / "index.ts"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Sample test
        content = '''import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Test Suite', () => {
    vscode.window.showInformationMessage('Running tests...');
    
    test('Extension should be present', () => {
        assert.ok(vscode.extensions.getExtension('cortex-team.cortex'));
    });
});
'''
        
        file_path = output_path / "src" / "test" / "suite" / "extension.test.ts"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info("Generated test files")
    
    def _generate_scripts(self, output_path: Path) -> None:
        """Generate build/package/publish scripts"""
        
        # build.sh (Linux/macOS)
        content = '''#!/bin/bash
# Build CORTEX extension

echo "Building CORTEX extension..."
npm run compile

echo "Build complete!"
'''
        
        file_path = output_path / "scripts" / "build.sh"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        file_path.chmod(0o755)
        
        # build.ps1 (Windows)
        content = '''# Build CORTEX extension

Write-Host "Building CORTEX extension..." -ForegroundColor Green
npm run compile

Write-Host "Build complete!" -ForegroundColor Green
'''
        
        file_path = output_path / "scripts" / "build.ps1"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # package.sh
        content = '''#!/bin/bash
# Package CORTEX extension as .vsix

echo "Packaging CORTEX extension..."
npm run compile
npm run package

echo "Package complete! Install with:"
echo "code --install-extension cortex-1.0.0.vsix"
'''
        
        file_path = output_path / "scripts" / "package.sh"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        file_path.chmod(0o755)
        
        self.logger.info("Generated build/package scripts")
    
    def _generate_documentation(self, output_path: Path, extension_name: str, display_name: str) -> None:
        """Generate README.md and CHANGELOG.md"""
        
        readme = f'''# {display_name}

AI development assistant with persistent memory and context awareness.

## Features

- **@cortex Chat Participant**: Natural conversation interface with memory
- **Persistent Memory**: Remembers across sessions (no amnesia!)
- **Auto-Capture**: Automatically captures all conversations
- **Resume Support**: Resume last conversation on startup
- **Token Dashboard**: Real-time token usage and optimization metrics
- **External Monitoring**: Captures @copilot conversations too

## Installation

1. Install from VS Code Marketplace (search "CORTEX")
2. Restart VS Code
3. Open Command Palette (Ctrl+Shift+P)
4. Type "CORTEX" to see available commands

## Usage

### Chat with CORTEX

Open any file and type `@cortex` in chat to start a conversation.

```
@cortex Add a purple button to the FAB
@cortex Continue working on the invoice feature
@cortex Resume last conversation
```

### Commands

- **CORTEX: Resume Last Conversation** - Continue where you left off
- **CORTEX: Save Checkpoint** - Manually save conversation state
- **CORTEX: Show Conversation History** - View past conversations
- **CORTEX: Show Token Dashboard** - View token metrics

## Configuration

Go to Settings > Extensions > CORTEX:

- `cortex.autoCapture`: Automatically capture conversations (default: true)
- `cortex.monitorCopilot`: Monitor @copilot conversations (default: true)
- `cortex.autoCheckpoint`: Auto-checkpoint on focus loss (default: true)
- `cortex.resumePrompt`: Show resume prompt on startup (default: true)
- `cortex.pythonPath`: Path to Python executable (default: "python")
- `cortex.brainPath`: Path to CORTEX brain (auto-detected)

## Requirements

- VS Code 1.85.0 or higher
- Python 3.8 or higher (for CORTEX brain)
- CORTEX brain installed (see main repo)

## Extension Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.

## Release Notes

### 1.0.0

Initial release:
- @cortex chat participant
- Automatic conversation capture
- Token dashboard
- Resume support
- External monitoring

## License

Copyright © 2024-2025 Asif Hussain. All rights reserved.

See LICENSE file for details.
'''
        
        readme_path = output_path / "README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme)
        
        changelog = f'''# Change Log

All notable changes to the "{extension_name}" extension will be documented in this file.

## [1.0.0] - {datetime.now().strftime("%Y-%m-%d")}

### Added
- Initial release
- @cortex chat participant with persistent memory
- Automatic conversation capture
- Token usage dashboard
- Resume last conversation feature
- External monitoring (@copilot capture)
- Lifecycle hooks (auto-checkpoint on focus loss)
- Configuration options

## [Unreleased]

- Additional agent integrations
- Advanced workflow orchestration
- Performance optimizations
'''
        
        changelog_path = output_path / "CHANGELOG.md"
        with open(changelog_path, "w", encoding="utf-8") as f:
            f.write(changelog)
        
        self.logger.info("Generated documentation")
    
    def _generate_vscodeignore(self, output_path: Path) -> None:
        """Generate .vscodeignore"""
        
        content = '''.vscode/**
.vscode-test/**
src/**
.gitignore
.yarnrc
vsc-extension-quickstart.md
**/tsconfig.json
**/.eslintrc.json
**/*.map
**/*.ts
!out/**/*.js
node_modules/**
scripts/**
.github/**
'''
        
        file_path = output_path / ".vscodeignore"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info("Generated .vscodeignore")
    
    def _generate_gitignore(self, output_path: Path) -> None:
        """Generate .gitignore"""
        
        content = '''node_modules/
out/
dist/
*.vsix
.vscode-test/
.DS_Store
'''
        
        file_path = output_path / ".gitignore"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.logger.info("Generated .gitignore")


def register():
    """Register the extension scaffold plugin"""
    return Plugin()
