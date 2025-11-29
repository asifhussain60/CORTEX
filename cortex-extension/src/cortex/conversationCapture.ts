/**
 * CORTEX Conversation Capture - Automatic Message Recording
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Proprietary - See LICENSE file for terms
 */

import { BrainBridge, ConversationMessage } from './brainBridge';

export class ConversationCapture {
    private brainBridge: BrainBridge;
    private messageBuffer: ConversationMessage[] = [];
    private conversationId: string | null = null;

    constructor(brainBridge: BrainBridge) {
        this.brainBridge = brainBridge;
    }

    async captureMessage(message: ConversationMessage): Promise<void> {
        // Add to buffer
        this.messageBuffer.push(message);

        // Immediate capture to Tier 1
        await this.brainBridge.captureMessage(message);
    }

    async startNewConversation(): Promise<string> {
        if (this.messageBuffer.length > 0) {
            this.conversationId = await this.brainBridge.captureConversation(this.messageBuffer);
            this.messageBuffer = [];
        }
        return this.conversationId || '';
    }

    async flush(): Promise<void> {
        if (this.messageBuffer.length > 0) {
            await this.brainBridge.captureConversation(this.messageBuffer);
            this.messageBuffer = [];
        }
    }

    getBufferedMessageCount(): number {
        return this.messageBuffer.length;
    }
}
