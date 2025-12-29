import * as vscode from 'vscode';
import { registerCommands } from './commands';
import { OutputChannelManager } from './utils/outputChannel';

export function activate(context: vscode.ExtensionContext) {
    console.log('CORTEX extension is now active');

    // Initialize output channel
    const outputChannel = OutputChannelManager.getInstance();
    outputChannel.log('CORTEX 4.0 - AI Development Intelligence');
    outputChannel.log('Extension activated successfully');

    // Register all commands
    registerCommands(context);

    // Show welcome message on first activation
    const config = vscode.workspace.getConfiguration('cortex');
    const hasShownWelcome = context.globalState.get<boolean>('hasShownWelcome', false);
    
    if (!hasShownWelcome) {
        vscode.window.showInformationMessage(
            'Welcome to CORTEX! Use "CORTEX: Show Help" or @cortex in Copilot Chat to get started.',
            'Show Help'
        ).then(selection => {
            if (selection === 'Show Help') {
                vscode.commands.executeCommand('cortex.help');
            }
        });
        context.globalState.update('hasShownWelcome', true);
    }

    outputChannel.log('All commands registered');
}

export function deactivate() {
    console.log('CORTEX extension is now deactivated');
    OutputChannelManager.dispose();
}
