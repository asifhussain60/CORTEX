import * as vscode from 'vscode';

/**
 * Singleton class to manage the CORTEX output channel
 */
export class OutputChannelManager {
    private static instance: OutputChannelManager;
    private outputChannel: vscode.OutputChannel;

    private constructor() {
        this.outputChannel = vscode.window.createOutputChannel('CORTEX');
    }

    public static getInstance(): OutputChannelManager {
        if (!OutputChannelManager.instance) {
            OutputChannelManager.instance = new OutputChannelManager();
        }
        return OutputChannelManager.instance;
    }

    public log(message: string): void {
        const timestamp = new Date().toLocaleTimeString();
        this.outputChannel.appendLine(`[${timestamp}] ${message}`);
    }

    public show(): void {
        this.outputChannel.show();
    }

    public static dispose(): void {
        if (OutputChannelManager.instance) {
            OutputChannelManager.instance.outputChannel.dispose();
        }
    }
}
