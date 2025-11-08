/**
 * CORTEX VS Code Extension - Main Entry Point
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Proprietary - See LICENSE file for terms
 */

import * as vscode from 'vscode';
import { BrainBridge } from './cortex/brainBridge';
import { CortexChatParticipant } from './cortex/chatParticipant';
import { ConversationCapture } from './cortex/conversationCapture';
import { LifecycleManager } from './cortex/lifecycleManager';
import { CheckpointManager } from './cortex/checkpointManager';

let brainBridge: BrainBridge;
let chatParticipant: CortexChatParticipant;
let lifecycleManager: LifecycleManager;
let checkpointManager: CheckpointManager;

export async function activate(context: vscode.ExtensionContext) {
    console.log('🚀 CORTEX extension activating...');
    
    // Show immediate activation feedback
    vscode.window.showInformationMessage('🧠 CORTEX extension activated!');
    
    try {
        // Initialize Brain Bridge (connects to Python backend)
        brainBridge = new BrainBridge(context);
        let isOnline = false;
        
        try {
            console.log('🔌 Attempting to connect to CORTEX Brain...');
            await brainBridge.initialize();
            console.log('✅ CORTEX Brain Bridge connected');
            isOnline = true;
            vscode.window.showInformationMessage(
                '🧠 CORTEX Brain connected! Full features enabled.'
            );
        } catch (error) {
            console.warn('⚠️  Brain Bridge initialization failed, running in offline mode:', error);
            vscode.window.showWarningMessage(
                '⚠️  CORTEX: Offline mode. Configure cortex.cortexRoot in settings for full features.'
            );
        }
        
        // Initialize conversation capture
        const conversationCapture = new ConversationCapture(brainBridge);
        
        // Initialize chat participant
        chatParticipant = new CortexChatParticipant(brainBridge, conversationCapture, isOnline);
        
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
        lifecycleManager = new LifecycleManager(brainBridge);
        lifecycleManager.setupHooks(context);
        
        // Initialize checkpoint manager
        checkpointManager = new CheckpointManager(brainBridge);
        checkpointManager.startAutoCheckpoint(10); // Auto-checkpoint every 10 minutes
        
        // Register commands
        context.subscriptions.push(
            vscode.commands.registerCommand('cortex.resume', async () => {
                await chatParticipant.resumeLastConversation();
            }),
            vscode.commands.registerCommand('cortex.checkpoint', async () => {
                try {
                    const checkpointId = await checkpointManager.createCheckpoint();
                    vscode.window.showInformationMessage(`✅ Checkpoint created: ${checkpointId}`);
                } catch (error) {
                    vscode.window.showErrorMessage(`Failed to create checkpoint: ${error}`);
                }
            }),
            vscode.commands.registerCommand('cortex.showHistory', async () => {
                await chatParticipant.showConversationHistory();
            }),
            vscode.commands.registerCommand('cortex.optimize', async () => {
                try {
                    const result = await brainBridge.optimizeTokens();
                    vscode.window.showInformationMessage(
                        `✅ Optimized! Reduced ${result.tokensReduced} tokens (${result.percentageReduction.toFixed(1)}%)`
                    );
                } catch (error) {
                    vscode.window.showErrorMessage(`Optimization failed: ${error}`);
                }
            }),
            vscode.commands.registerCommand('cortex.showTokenDashboard', async () => {
                try {
                    const metrics = await brainBridge.getTokenMetrics();
                    vscode.window.showInformationMessage(
                        `📊 Tokens: ${metrics.sessionTokens} session / ${metrics.totalTokens} total | Cache: ${metrics.cacheStatus}`
                    );
                } catch (error) {
                    vscode.window.showErrorMessage(`Failed to fetch metrics: ${error}`);
                }
            }),
            vscode.commands.registerCommand('cortex.clearCache', async () => {
                try {
                    const result = await brainBridge.clearCache();
                    vscode.window.showInformationMessage(
                        `✅ Cache cleared: ${result.conversationsRemoved} conversations, ${result.tokensFreed} tokens freed`
                    );
                } catch (error) {
                    vscode.window.showErrorMessage(`Failed to clear cache: ${error}`);
                }
            })
        );
        
        console.log('✅ CORTEX extension activated successfully!');
        
        // Don't show duplicate welcome message since we already showed connection status above
        
        // Offer resume on startup (if configured and online)
        const config = vscode.workspace.getConfiguration('cortex');
        if (config.get('resumePrompt', true) && isOnline) {
            setTimeout(() => chatParticipant.offerResume(), 2000);
        }
        
    } catch (error) {
        console.error('CORTEX extension activation failed:', error);
        vscode.window.showErrorMessage(`CORTEX activation failed: ${error}`);
        throw error;
    }
}

export function deactivate() {
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
