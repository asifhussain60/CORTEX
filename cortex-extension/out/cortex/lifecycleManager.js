"use strict";
/**
 * CORTEX Lifecycle Manager - Window State Monitoring
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
exports.LifecycleManager = void 0;
const vscode = __importStar(require("vscode"));
class LifecycleManager {
    constructor(brainBridge) {
        this.lastFocusTime = Date.now();
        this.brainBridge = brainBridge;
    }
    setupHooks(context) {
        // Window state monitoring
        context.subscriptions.push(vscode.window.onDidChangeWindowState(async (state) => {
            if (!state.focused) {
                await this.onWindowBlur();
            }
            else {
                await this.onWindowFocus();
            }
        }));
    }
    async onWindowBlur() {
        console.log('Window lost focus - creating checkpoint...');
        // Auto-checkpoint if enabled
        const config = vscode.workspace.getConfiguration('cortex');
        if (config.get('autoCheckpoint', true)) {
            try {
                await this.brainBridge.createCheckpoint();
                console.log('Checkpoint created successfully');
            }
            catch (error) {
                console.error('Failed to create checkpoint:', error);
            }
        }
        this.lastFocusTime = Date.now();
    }
    async onWindowFocus() {
        const idleTime = Date.now() - this.lastFocusTime;
        const idleMinutes = idleTime / (1000 * 60);
        console.log(`Window gained focus after ${idleMinutes.toFixed(1)} minutes`);
        // Offer resume if idle > 30 minutes
        if (idleMinutes > 30) {
            const config = vscode.workspace.getConfiguration('cortex');
            if (config.get('resumePrompt', true)) {
                vscode.window.showInformationMessage(`CORTEX: Resume your last conversation?`, 'Resume', 'Start New').then(async (choice) => {
                    if (choice === 'Resume') {
                        vscode.commands.executeCommand('cortex.resume');
                    }
                });
            }
        }
    }
}
exports.LifecycleManager = LifecycleManager;
//# sourceMappingURL=lifecycleManager.js.map