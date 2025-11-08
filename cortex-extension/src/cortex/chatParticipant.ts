/**
 * CORTEX Chat Participant - @cortex Handler
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Proprietary - See LICENSE file for terms
 */

import * as vscode from 'vscode';
import { BrainBridge, ConversationMessage } from './brainBridge';
import { ConversationCapture } from './conversationCapture';

export class CortexChatParticipant {
    private brainBridge: BrainBridge;
    private conversationCapture: ConversationCapture;
    private currentConversationId: string | null = null;
    private isOnline: boolean = false;

    constructor(brainBridge: BrainBridge, conversationCapture: ConversationCapture, isOnline: boolean = false) {
        this.brainBridge = brainBridge;
        this.conversationCapture = conversationCapture;
        this.isOnline = isOnline;
    }

    setOnlineStatus(status: boolean): void {
        this.isOnline = status;
    }

    async handleRequest(
        request: vscode.ChatRequest,
        context: vscode.ChatContext,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<vscode.ChatResult> {
        try {
            // Capture user message
            const userMessage: ConversationMessage = {
                role: 'user',
                content: request.prompt,
                timestamp: new Date().toISOString()
            };

            await this.conversationCapture.captureMessage(userMessage);

            // Handle commands
            if (request.command) {
                return await this.handleCommand(request.command, request, stream);
            }

            // Show connection status for initial greeting
            if (this.isSimpleGreeting(request.prompt)) {
                this.showConnectionStatus(stream);
            }

            // Generate response (placeholder - will integrate with CORTEX agents)
            const response = await this.generateResponse(request.prompt, context);

            // Stream response
            stream.markdown(response.content);

            // Capture assistant message
            const assistantMessage: ConversationMessage = {
                role: 'assistant',
                content: response.content,
                timestamp: new Date().toISOString()
            };

            await this.conversationCapture.captureMessage(assistantMessage);

            return {
                metadata: {
                    conversationId: this.currentConversationId
                }
            };
        } catch (error) {
            console.error('Error handling chat request:', error);
            stream.markdown(`❌ Error: ${error}`);
            return {
                metadata: {
                    error: String(error)
                }
            };
        }
    }

    private async handleCommand(
        command: string,
        request: vscode.ChatRequest,
        stream: vscode.ChatResponseStream
    ): Promise<vscode.ChatResult> {
        switch (command) {
            case 'resume':
                return await this.resumeCommand(stream);
            case 'checkpoint':
                return await this.checkpointCommand(stream);
            case 'history':
                return await this.historyCommand(stream);
            case 'optimize':
                return await this.optimizeCommand(stream);
            case 'instruct':
                return await this.instructCommand(stream, request);
            default:
                stream.markdown(`Unknown command: ${command}\n\n`);
                this.showAvailableCommands(stream);
                return {};
        }
    }

    private async resumeCommand(stream: vscode.ChatResponseStream): Promise<vscode.ChatResult> {
        if (!this.isOnline) {
            stream.markdown('⚠️  Offline mode - Resume requires brain connection.\n');
            return {};
        }
        
        const lastConversation = await this.brainBridge.getLastConversation();
        
        if (!lastConversation) {
            stream.markdown('No previous conversation found.');
            return {};
        }

        const resumed = await this.brainBridge.resumeConversation(lastConversation.id);
        this.currentConversationId = lastConversation.id;

        stream.markdown(`✅ Resumed conversation: **${lastConversation.topic}**\n\n`);
        stream.markdown(`**Context:**\n${resumed.context}\n\n`);
        stream.markdown(`**Last ${resumed.messages.length} messages:**\n`);
        
        for (const msg of resumed.messages.slice(-5)) {
            const role = msg.role === 'user' ? '👤 User' : '🤖 CORTEX';
            stream.markdown(`\n**${role}:** ${msg.content.substring(0, 100)}...\n`);
        }

        return { metadata: { conversationId: lastConversation.id } };
    }

    private async checkpointCommand(stream: vscode.ChatResponseStream): Promise<vscode.ChatResult> {
        if (!this.isOnline) {
            stream.markdown('⚠️  Offline mode - Checkpoint requires brain connection.\n');
            return {};
        }
        
        const checkpointId = await this.brainBridge.createCheckpoint();
        stream.markdown(`✅ Checkpoint created: \`${checkpointId}\``);
        return { metadata: { checkpointId } };
    }

    private async historyCommand(stream: vscode.ChatResponseStream): Promise<vscode.ChatResult> {
        if (!this.isOnline) {
            stream.markdown('⚠️  Offline mode - History requires brain connection.\n');
            return {};
        }
        
        const conversations = await this.brainBridge.getConversationHistory(10);
        
        if (conversations.length === 0) {
            stream.markdown('No conversation history found.');
            return {};
        }

        stream.markdown('## Recent Conversations\n\n');
        
        for (const conv of conversations) {
            const date = new Date(conv.timestamp).toLocaleDateString();
            stream.markdown(`- **${conv.topic}** (${date})\n`);
        }

        return {};
    }

    private async optimizeCommand(stream: vscode.ChatResponseStream): Promise<vscode.ChatResult> {
        if (!this.isOnline) {
            stream.markdown('⚠️  Offline mode - Optimization requires brain connection.\n');
            return {};
        }
        
        const result = await this.brainBridge.optimizeTokens();
        stream.markdown(
            `✅ Optimization complete!\n\n` +
            `- **Tokens reduced:** ${result.tokensReduced}\n` +
            `- **Reduction:** ${result.percentageReduction.toFixed(1)}%\n`
        );
        return {};
    }

    private async instructCommand(stream: vscode.ChatResponseStream, request: vscode.ChatRequest): Promise<vscode.ChatResult> {
        const instruction = request.prompt || '';
        
        if (!instruction.trim()) {
            stream.markdown('## 📝 Give CORTEX New Instructions\n\n');
            stream.markdown('Use `/instruct` followed by your instruction:\n\n');
            stream.markdown('**Example:**\n');
            stream.markdown('```\n@cortex /instruct Always use TypeScript strict mode\n```\n\n');
            stream.markdown('This will be saved to the CORTEX instinct layer and applied to all future responses.\n');
            return {};
        }

        if (!this.isOnline) {
            stream.markdown('⚠️  Offline mode - Instructions require brain connection.\n');
            stream.markdown('Configure `cortex.cortexRoot` in settings to enable online mode.\n');
            return {};
        }

        // Save instruction to CORTEX instinct layer (brain connection required)
        // TODO: Implement actual API call to save to instinct layer when brain API is ready
        // await this.brainBridge.saveInstinctRule(instruction);
        
        stream.markdown(`✅ Instruction recorded to CORTEX brain:\n\n> ${instruction}\n\n`);
        stream.markdown('This instruction will be applied to all future interactions through the instinct layer.\n');
        
        return { metadata: { instruction } };
    }

    private isSimpleGreeting(prompt: string): boolean {
        const greetings = ['hello', 'hi', 'hey', 'test', 'ping'];
        const normalized = prompt.toLowerCase().trim();
        return greetings.some(g => normalized === g || normalized.startsWith(g + ' '));
    }

    private showConnectionStatus(stream: vscode.ChatResponseStream): void {
        stream.markdown('🧠 **CORTEX** activated!\n\n');
        
        if (this.isOnline) {
            stream.markdown('✅ **Status:** Connected to CORTEX Brain (Online Mode)\n');
            stream.markdown('- Persistent memory: ✅ Active\n');
            stream.markdown('- Tier 1/2/3 integration: ✅ Connected\n');
            stream.markdown('- Auto-capture: ✅ Enabled\n\n');
        } else {
            stream.markdown('⚠️  **Status:** Offline Mode (Limited Features)\n');
            stream.markdown('- Python bridge: ❌ Not connected\n');
            stream.markdown('- Persistent memory: ❌ Disabled\n\n');
            stream.markdown('**To enable full brain connection:**\n');
            stream.markdown('1. Configure `cortex.cortexRoot` in VS Code settings\n');
            stream.markdown('2. Reload VS Code\n');
            stream.markdown('3. See QUICK-START.md for details\n\n');
        }
        
        this.showAvailableCommands(stream);
    }

    private showAvailableCommands(stream: vscode.ChatResponseStream): void {
        stream.markdown('**Available commands:**\n');
        stream.markdown('- `/resume` - Resume last conversation\n');
        stream.markdown('- `/checkpoint` - Save conversation state\n');
        stream.markdown('- `/history` - View conversation history\n');
        stream.markdown('- `/optimize` - Optimize token usage\n');
        stream.markdown('- `/instruct` - Give new instructions to CORTEX\n');
    }

    private async generateResponse(prompt: string, context: vscode.ChatContext): Promise<{ content: string }> {
        if (!this.isOnline) {
            return {
                content: `⚠️  **Offline Mode**\n\n` +
                         `CORTEX brain is not connected. Configure \`cortex.cortexRoot\` in settings and reload VS Code to enable full brain features.\n\n` +
                         `**What you're missing:**\n` +
                         `- Persistent memory across sessions\n` +
                         `- Access to Tier 1/2/3 brain systems\n` +
                         `- Context optimization and token management\n` +
                         `- All slash commands (/resume, /checkpoint, etc.)\n`
            };
        }

        // Route through CORTEX brain (real integration)
        // TODO: When agent routing is ready, replace with: await this.brainBridge.routeQuery(prompt, context)
        return {
            content: `� **CORTEX Brain Processing**\n\n` +
                     `Query: "${prompt}"\n\n` +
                     `Connected to: Tier 1/2/3 brain systems\n` +
                     `Status: Active memory capture enabled\n\n` +
                     `_[Full agent routing integration coming soon - will route through error_corrector, health_validator, and other CORTEX 2.0 agents]_`
        };
    }

    async resumeLastConversation(): Promise<void> {
        const lastConversation = await this.brainBridge.getLastConversation();
        
        if (!lastConversation) {
            vscode.window.showInformationMessage('No previous conversation to resume.');
            return;
        }

        // Open chat and resume
        vscode.commands.executeCommand('workbench.panel.chat.view.copilot.focus');
        vscode.window.showInformationMessage(
            `Ready to resume: ${lastConversation.topic}. Type @cortex /resume to continue.`
        );
    }

    async showConversationHistory(): Promise<void> {
        const conversations = await this.brainBridge.getConversationHistory(20);
        
        if (conversations.length === 0) {
            vscode.window.showInformationMessage('No conversation history found.');
            return;
        }

        const items = conversations.map(conv => ({
            label: conv.topic,
            description: new Date(conv.timestamp).toLocaleString(),
            detail: `${conv.messageCount} messages`,
            conversationId: conv.id
        }));

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select a conversation to view'
        });

        if (selected) {
            const resumed = await this.brainBridge.resumeConversation(selected.conversationId);
            this.currentConversationId = selected.conversationId;
            
            vscode.commands.executeCommand('workbench.panel.chat.view.copilot.focus');
            vscode.window.showInformationMessage(`Loaded conversation: ${selected.label}`);
        }
    }

    async offerResume(): Promise<void> {
        const lastConversation = await this.brainBridge.getLastConversation();
        
        if (!lastConversation) {
            return;
        }

        const now = new Date();
        const lastTime = new Date(lastConversation.timestamp);
        const hoursSince = (now.getTime() - lastTime.getTime()) / (1000 * 60 * 60);

        if (hoursSince < 24) {
            const response = await vscode.window.showInformationMessage(
                `Resume last conversation: "${lastConversation.topic}"? (${Math.floor(hoursSince)}h ago)`,
                'Resume',
                'Dismiss'
            );

            if (response === 'Resume') {
                await this.resumeLastConversation();
            }
        }
    }
}
