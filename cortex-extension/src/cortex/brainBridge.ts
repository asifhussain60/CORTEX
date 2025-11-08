/**
 * CORTEX Brain Bridge - Python ↔ TypeScript Communication
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Proprietary - See LICENSE file for terms
 */

import * as vscode from 'vscode';
import * as path from 'path';
import { spawn, ChildProcess } from 'child_process';
import axios, { AxiosInstance } from 'axios';

export interface ConversationMessage {
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
}

export interface TokenMetrics {
    sessionTokens: number;
    totalTokens: number;
    costEstimate: number;
    optimizationRate: number;
    cacheStatus: 'OK' | 'WARNING' | 'CRITICAL';
    cacheSize: number;
    patternCount: number;
}

export class BrainBridge {
    private context: vscode.ExtensionContext;
    private pythonProcess: ChildProcess | null = null;
    private httpClient: AxiosInstance;
    private serverPort: number = 5555;
    private isInitialized: boolean = false;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.httpClient = axios.create({
            baseURL: `http://localhost:${this.serverPort}`,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    async initialize(): Promise<void> {
        try {
            // Get configuration
            const config = vscode.workspace.getConfiguration('cortex');
            let pythonPath = config.get<string>('pythonPath', '');
            const cortexRoot = config.get<string>('cortexRoot', '') || this.detectCortexRoot();

            // Auto-detect Python if not configured
            if (!pythonPath) {
                pythonPath = await this.detectPython();
            }

            // Start Python bridge server
            await this.startPythonServer(pythonPath, cortexRoot);

            // Wait for server to be ready
            await this.waitForServer();

            this.isInitialized = true;
            console.log('CORTEX Brain Bridge initialized successfully');
        } catch (error) {
            console.error('Failed to initialize Brain Bridge:', error);
            throw new Error(`Brain Bridge initialization failed: ${error}`);
        }
    }

    private async startPythonServer(pythonPath: string, cortexRoot: string): Promise<void> {
        // Bridge script is in the cortex-extension directory
        const bridgeScript = path.join(cortexRoot, 'cortex-extension', 'python', 'bridge_server.py');
        
        console.log(`Starting CORTEX Brain Bridge:`);
        console.log(`  Python: ${pythonPath}`);
        console.log(`  CORTEX Root: ${cortexRoot}`);
        console.log(`  Bridge Script: ${bridgeScript}`);
        console.log(`  Port: ${this.serverPort}`);
        
        this.pythonProcess = spawn(pythonPath, [bridgeScript, '--port', this.serverPort.toString()], {
            env: {
                ...process.env,
                CORTEX_ROOT: cortexRoot,
                PYTHONPATH: cortexRoot
            },
            cwd: cortexRoot
        });

        this.pythonProcess.stdout?.on('data', (data) => {
            console.log(`[CORTEX Bridge] ${data.toString().trim()}`);
        });

        this.pythonProcess.stderr?.on('data', (data) => {
            console.error(`[CORTEX Bridge Error] ${data.toString().trim()}`);
        });

        this.pythonProcess.on('close', (code) => {
            console.log(`CORTEX Bridge process exited with code ${code}`);
            this.pythonProcess = null;
        });
    }

    private async waitForServer(maxRetries: number = 30): Promise<void> {
        for (let i = 0; i < maxRetries; i++) {
            try {
                await this.httpClient.get('/health');
                return;
            } catch (error) {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
        throw new Error('Python bridge server failed to start within timeout');
    }

    private async detectPython(): Promise<string> {
        // Try common Python paths
        const candidates = ['python', 'python3', 'py'];
        
        for (const candidate of candidates) {
            try {
                const result = await this.executePython(candidate, ['-c', 'print("ok")']);
                if (result.trim() === 'ok') {
                    return candidate;
                }
            } catch {
                continue;
            }
        }
        
        throw new Error('Could not find Python executable. Please configure cortex.pythonPath');
    }

    private executePython(pythonPath: string, args: string[]): Promise<string> {
        return new Promise((resolve, reject) => {
            const proc = spawn(pythonPath, args);
            let output = '';
            
            proc.stdout.on('data', (data) => {
                output += data.toString();
            });
            
            proc.on('close', (code) => {
                if (code === 0) {
                    resolve(output);
                } else {
                    reject(new Error(`Python exited with code ${code}`));
                }
            });
            
            proc.on('error', reject);
        });
    }

    private detectCortexRoot(): string {
        // Try to find CORTEX root from environment or workspace
        const envRoot = process.env.CORTEX_ROOT;
        if (envRoot) {
            return envRoot;
        }

        // Look for src folder with CORTEX 2.0 structure in workspace
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders) {
            for (const folder of workspaceFolders) {
                const potentialRoot = folder.uri.fsPath;
                // Check if this looks like CORTEX root (has src/tier1, src/tier2, etc.)
                const srcPath = path.join(potentialRoot, 'src');
                const tier1Path = path.join(srcPath, 'tier1');
                if (require('fs').existsSync(srcPath) && require('fs').existsSync(tier1Path)) {
                    return potentialRoot;
                }
            }
        }

        throw new Error('Could not detect CORTEX root. Please configure cortex.cortexRoot setting or set CORTEX_ROOT environment variable');
    }

    // === Brain API Methods ===

    async captureMessage(message: ConversationMessage): Promise<void> {
        await this.httpClient.post('/capture/message', message);
    }

    async captureConversation(messages: ConversationMessage[]): Promise<string> {
        const response = await this.httpClient.post('/capture/conversation', { messages });
        return response.data.conversationId;
    }

    async getLastConversation(): Promise<{ id: string; topic: string; timestamp: string; messages: ConversationMessage[] } | null> {
        const response = await this.httpClient.get('/conversation/last');
        return response.data.conversation || null;
    }

    async resumeConversation(conversationId: string): Promise<{ messages: ConversationMessage[]; context: string }> {
        const response = await this.httpClient.post('/conversation/resume', { conversationId });
        return response.data;
    }

    async createCheckpoint(): Promise<string> {
        const response = await this.httpClient.post('/checkpoint/create');
        return response.data.checkpointId;
    }

    async getConversationHistory(limit: number = 20): Promise<any[]> {
        const response = await this.httpClient.get('/conversation/history', {
            params: { limit }
        });
        return response.data.conversations;
    }

    async getTokenMetrics(): Promise<TokenMetrics> {
        const response = await this.httpClient.get('/metrics/tokens');
        return response.data;
    }

    async optimizeTokens(): Promise<{ tokensReduced: number; percentageReduction: number }> {
        const response = await this.httpClient.post('/optimize/tokens');
        return response.data;
    }

    async clearCache(): Promise<{ conversationsRemoved: number; tokensFreed: number }> {
        const response = await this.httpClient.post('/cache/clear');
        return response.data;
    }

    dispose(): void {
        if (this.pythonProcess) {
            this.pythonProcess.kill();
            this.pythonProcess = null;
        }
    }
}
