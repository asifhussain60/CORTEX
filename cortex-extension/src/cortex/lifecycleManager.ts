/**
 * CORTEX Lifecycle Manager - Window State Monitoring
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Proprietary - See LICENSE file for terms
 */

import * as vscode from 'vscode';
import { BrainBridge } from './brainBridge';

export class LifecycleManager {
    private brainBridge: BrainBridge;
    private lastFocusTime: number = Date.now();

    constructor(brainBridge: BrainBridge) {
        this.brainBridge = brainBridge;
    }

    setupHooks(context: vscode.ExtensionContext): void {
        // Window state monitoring
        context.subscriptions.push(
            vscode.window.onDidChangeWindowState(async (state) => {
                if (!state.focused) {
                    await this.onWindowBlur();
                } else {
                    await this.onWindowFocus();
                }
            })
        );
    }

    private async onWindowBlur(): Promise<void> {
        console.log('Window lost focus - creating checkpoint...');
        
        // Auto-checkpoint if enabled
        const config = vscode.workspace.getConfiguration('cortex');
        if (config.get('autoCheckpoint', true)) {
            try {
                await this.brainBridge.createCheckpoint();
                console.log('Checkpoint created successfully');
            } catch (error) {
                console.error('Failed to create checkpoint:', error);
            }
        }
        
        this.lastFocusTime = Date.now();
    }

    private async onWindowFocus(): Promise<void> {
        const idleTime = Date.now() - this.lastFocusTime;
        const idleMinutes = idleTime / (1000 * 60);
        
        console.log(`Window gained focus after ${idleMinutes.toFixed(1)} minutes`);
        
        // Offer resume if idle > 30 minutes
        if (idleMinutes > 30) {
            const config = vscode.workspace.getConfiguration('cortex');
            if (config.get('resumePrompt', true)) {
                vscode.window.showInformationMessage(
                    `CORTEX: Resume your last conversation?`,
                    'Resume',
                    'Start New'
                ).then(async (choice) => {
                    if (choice === 'Resume') {
                        vscode.commands.executeCommand('cortex.resume');
                    }
                });
            }
        }
    }
}
