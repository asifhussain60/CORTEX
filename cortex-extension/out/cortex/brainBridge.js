"use strict";
/**
 * CORTEX Brain Bridge - Python ↔ TypeScript Communication
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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.BrainBridge = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const child_process_1 = require("child_process");
const axios_1 = __importDefault(require("axios"));
class BrainBridge {
    constructor(context) {
        this.pythonProcess = null;
        this.serverPort = 5555;
        this.isInitialized = false;
        this.context = context;
        this.httpClient = axios_1.default.create({
            baseURL: `http://localhost:${this.serverPort}`,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
    async initialize() {
        try {
            // Get configuration
            const config = vscode.workspace.getConfiguration('cortex');
            let pythonPath = config.get('pythonPath', '');
            const cortexRoot = config.get('cortexRoot', '') || this.detectCortexRoot();
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
        }
        catch (error) {
            console.error('Failed to initialize Brain Bridge:', error);
            throw new Error(`Brain Bridge initialization failed: ${error}`);
        }
    }
    async startPythonServer(pythonPath, cortexRoot) {
        // Bridge script is in the cortex-extension directory
        const bridgeScript = path.join(cortexRoot, 'cortex-extension', 'python', 'bridge_server.py');
        console.log(`Starting CORTEX Brain Bridge:`);
        console.log(`  Python: ${pythonPath}`);
        console.log(`  CORTEX Root: ${cortexRoot}`);
        console.log(`  Bridge Script: ${bridgeScript}`);
        console.log(`  Port: ${this.serverPort}`);
        this.pythonProcess = (0, child_process_1.spawn)(pythonPath, [bridgeScript, '--port', this.serverPort.toString()], {
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
    async waitForServer(maxRetries = 30) {
        for (let i = 0; i < maxRetries; i++) {
            try {
                await this.httpClient.get('/health');
                return;
            }
            catch (error) {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
        throw new Error('Python bridge server failed to start within timeout');
    }
    async detectPython() {
        // Try common Python paths
        const candidates = ['python', 'python3', 'py'];
        for (const candidate of candidates) {
            try {
                const result = await this.executePython(candidate, ['-c', 'print("ok")']);
                if (result.trim() === 'ok') {
                    return candidate;
                }
            }
            catch {
                continue;
            }
        }
        throw new Error('Could not find Python executable. Please configure cortex.pythonPath');
    }
    executePython(pythonPath, args) {
        return new Promise((resolve, reject) => {
            const proc = (0, child_process_1.spawn)(pythonPath, args);
            let output = '';
            proc.stdout.on('data', (data) => {
                output += data.toString();
            });
            proc.on('close', (code) => {
                if (code === 0) {
                    resolve(output);
                }
                else {
                    reject(new Error(`Python exited with code ${code}`));
                }
            });
            proc.on('error', reject);
        });
    }
    detectCortexRoot() {
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
    async captureMessage(message) {
        await this.httpClient.post('/capture/message', message);
    }
    async captureConversation(messages) {
        const response = await this.httpClient.post('/capture/conversation', { messages });
        return response.data.conversationId;
    }
    async getLastConversation() {
        const response = await this.httpClient.get('/conversation/last');
        return response.data.conversation || null;
    }
    async resumeConversation(conversationId) {
        const response = await this.httpClient.post('/conversation/resume', { conversationId });
        return response.data;
    }
    async createCheckpoint() {
        const response = await this.httpClient.post('/checkpoint/create');
        return response.data.checkpointId;
    }
    async getConversationHistory(limit = 20) {
        const response = await this.httpClient.get('/conversation/history', {
            params: { limit }
        });
        return response.data.conversations;
    }
    async getTokenMetrics() {
        const response = await this.httpClient.get('/metrics/tokens');
        return response.data;
    }
    async optimizeTokens() {
        const response = await this.httpClient.post('/optimize/tokens');
        return response.data;
    }
    async clearCache() {
        const response = await this.httpClient.post('/cache/clear');
        return response.data;
    }
    dispose() {
        if (this.pythonProcess) {
            this.pythonProcess.kill();
            this.pythonProcess = null;
        }
    }
}
exports.BrainBridge = BrainBridge;
//# sourceMappingURL=brainBridge.js.map