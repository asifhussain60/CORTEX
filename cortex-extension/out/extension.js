"use strict";
/**
 * CORTEX VS Code Extension - Main Entry Point
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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const brainBridge_1 = require("./cortex/brainBridge");
const chatParticipant_1 = require("./cortex/chatParticipant");
const conversationCapture_1 = require("./cortex/conversationCapture");
const lifecycleManager_1 = require("./cortex/lifecycleManager");
const checkpointManager_1 = require("./cortex/checkpointManager");
let brainBridge;
let chatParticipant;
let lifecycleManager;
let checkpointManager;
async function activate(context) {
    console.log('🚀 CORTEX extension activating...');
    // Show immediate activation feedback
    vscode.window.showInformationMessage('🧠 CORTEX extension activated!');
    try {
        // Initialize Brain Bridge (connects to Python backend)
        brainBridge = new brainBridge_1.BrainBridge(context);
        let isOnline = false;
        try {
            console.log('🔌 Attempting to connect to CORTEX Brain...');
            await brainBridge.initialize();
            console.log('✅ CORTEX Brain Bridge connected');
            isOnline = true;
            vscode.window.showInformationMessage('🧠 CORTEX Brain connected! Full features enabled.');
        }
        catch (error) {
            console.warn('⚠️  Brain Bridge initialization failed, running in offline mode:', error);
            vscode.window.showWarningMessage('⚠️  CORTEX: Offline mode. Configure cortex.cortexRoot in settings for full features.');
        }
        // Initialize conversation capture
        const conversationCapture = new conversationCapture_1.ConversationCapture(brainBridge);
        // Initialize chat participant
        chatParticipant = new chatParticipant_1.CortexChatParticipant(brainBridge, conversationCapture, isOnline);
        console.log('📝 Registering @cortex chat participant...');
        // Register chat participant with VS Code
        const participant = vscode.chat.createChatParticipant('cortex', async (request, contextChat, stream, token) => {
            console.log('💬 CORTEX chat participant invoked:', request.prompt);
            return await chatParticipant.handleRequest(request, contextChat, stream, token);
        });
        participant.iconPath = vscode.Uri.joinPath(context.extensionUri, 'resources', 'cortex-icon.png');
        context.subscriptions.push(participant);
        console.log('✅ @cortex chat participant registered successfully!');
        // Initialize lifecycle manager
        lifecycleManager = new lifecycleManager_1.LifecycleManager(brainBridge);
        lifecycleManager.setupHooks(context);
        // Initialize checkpoint manager
        checkpointManager = new checkpointManager_1.CheckpointManager(brainBridge);
        checkpointManager.startAutoCheckpoint(10); // Auto-checkpoint every 10 minutes
        // Register commands
        context.subscriptions.push(vscode.commands.registerCommand('cortex.resume', async () => {
            await chatParticipant.resumeLastConversation();
        }), vscode.commands.registerCommand('cortex.checkpoint', async () => {
            try {
                const checkpointId = await checkpointManager.createCheckpoint();
                vscode.window.showInformationMessage(`✅ Checkpoint created: ${checkpointId}`);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Failed to create checkpoint: ${error}`);
            }
        }), vscode.commands.registerCommand('cortex.showHistory', async () => {
            await chatParticipant.showConversationHistory();
        }), vscode.commands.registerCommand('cortex.optimize', async () => {
            try {
                const result = await brainBridge.optimizeTokens();
                vscode.window.showInformationMessage(`✅ Optimized! Reduced ${result.tokensReduced} tokens (${result.percentageReduction.toFixed(1)}%)`);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Optimization failed: ${error}`);
            }
        }), vscode.commands.registerCommand('cortex.showTokenDashboard', async () => {
            try {
                const metrics = await brainBridge.getTokenMetrics();
                vscode.window.showInformationMessage(`📊 Tokens: ${metrics.sessionTokens} session / ${metrics.totalTokens} total | Cache: ${metrics.cacheStatus}`);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Failed to fetch metrics: ${error}`);
            }
        }), vscode.commands.registerCommand('cortex.clearCache', async () => {
            try {
                const result = await brainBridge.clearCache();
                vscode.window.showInformationMessage(`✅ Cache cleared: ${result.conversationsRemoved} conversations, ${result.tokensFreed} tokens freed`);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Failed to clear cache: ${error}`);
            }
        }));
        console.log('✅ CORTEX extension activated successfully!');
        // Don't show duplicate welcome message since we already showed connection status above
        // Offer resume on startup (if configured and online)
        const config = vscode.workspace.getConfiguration('cortex');
        if (config.get('resumePrompt', true) && isOnline) {
            setTimeout(() => chatParticipant.offerResume(), 2000);
        }
    }
    catch (error) {
        console.error('CORTEX extension activation failed:', error);
        vscode.window.showErrorMessage(`CORTEX activation failed: ${error}`);
        throw error;
    }
}
function deactivate() {
    console.log('CORTEX extension deactivating...');
    // Stop auto-checkpoint
    if (checkpointManager) {
        checkpointManager.stopAutoCheckpoint();
    }
    // Dispose brain bridge
    if (brainBridge) {
        brainBridge.dispose();
    }
}
//# sourceMappingURL=extension.js.map