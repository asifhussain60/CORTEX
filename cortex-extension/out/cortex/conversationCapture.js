"use strict";
/**
 * CORTEX Conversation Capture - Automatic Message Recording
 *
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Proprietary - See LICENSE file for terms
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ConversationCapture = void 0;
class ConversationCapture {
    constructor(brainBridge) {
        this.messageBuffer = [];
        this.conversationId = null;
        this.brainBridge = brainBridge;
    }
    async captureMessage(message) {
        // Add to buffer
        this.messageBuffer.push(message);
        // Immediate capture to Tier 1
        await this.brainBridge.captureMessage(message);
    }
    async startNewConversation() {
        if (this.messageBuffer.length > 0) {
            this.conversationId = await this.brainBridge.captureConversation(this.messageBuffer);
            this.messageBuffer = [];
        }
        return this.conversationId || '';
    }
    async flush() {
        if (this.messageBuffer.length > 0) {
            await this.brainBridge.captureConversation(this.messageBuffer);
            this.messageBuffer = [];
        }
    }
    getBufferedMessageCount() {
        return this.messageBuffer.length;
    }
}
exports.ConversationCapture = ConversationCapture;
//# sourceMappingURL=conversationCapture.js.map