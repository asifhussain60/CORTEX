import * as vscode from 'vscode';
import { OutputChannelManager } from '../utils/outputChannel';

/**
 * Register all CORTEX commands
 */
export function registerCommands(context: vscode.ExtensionContext): void {
    const outputChannel = OutputChannelManager.getInstance();

    // CORTEX: Show Help
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.help', async () => {
            outputChannel.log('Executing command: cortex.help');
            vscode.window.showInformationMessage(
                'CORTEX Help: Use @cortex in Copilot Chat or run "CORTEX: Create Planning Folder" to get started.'
            );
            // TODO: Show webview with comprehensive help documentation
        })
    );

    // CORTEX: Create Planning Folder
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.plan', async () => {
            outputChannel.log('Executing command: cortex.plan');
            vscode.window.showInformationMessage('Creating planning folder structure...');
            // TODO: Execute Python backend to create 4-folder planning structure
        })
    );

    // CORTEX: Start TDD Workflow
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.startTdd', async () => {
            outputChannel.log('Executing command: cortex.startTdd');
            vscode.window.showInformationMessage('Starting TDD workflow (RED → GREEN → REFACTOR)...');
            // TODO: Execute Python backend TDD orchestrator
        })
    );

    // CORTEX: Run System Maintenance
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.systemMaintenance', async () => {
            outputChannel.log('Executing command: cortex.systemMaintenance');
            vscode.window.showInformationMessage('Running 6-phase system maintenance...');
            // TODO: Execute Python backend maintenance orchestrator
        })
    );

    // CORTEX: Sanitize Code
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.sanitize', async () => {
            outputChannel.log('Executing command: cortex.sanitize');
            vscode.window.showInformationMessage('Starting 5-phase code sanitization...');
            // TODO: Execute Python backend sanitization orchestrator
        })
    );

    // CORTEX: Run Refinement
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.refine', async () => {
            outputChannel.log('Executing command: cortex.refine');
            vscode.window.showInformationMessage('Starting 7-phase refinement process...');
            // TODO: Execute Python backend refinement orchestrator
        })
    );

    // CORTEX: Interactive Onboarding
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.onboard', async () => {
            outputChannel.log('Executing command: cortex.onboard');
            vscode.window.showInformationMessage('Starting interactive onboarding...');
            // TODO: Execute Python backend onboarding orchestrator
        })
    );

    // CORTEX: ADO Planning
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.adoPlanning', async () => {
            outputChannel.log('Executing command: cortex.adoPlanning');
            vscode.window.showInformationMessage('Starting Azure DevOps planning workflow...');
            // TODO: Execute Python backend ADO orchestrator
        })
    );

    // CORTEX: Show Dashboard
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.showDashboard', async () => {
            outputChannel.log('Executing command: cortex.showDashboard');
            vscode.window.showInformationMessage('Opening CORTEX dashboard...');
            // TODO: Create webview panel with brain health metrics, recent plans, quick actions
        })
    );

    outputChannel.log('Registered 9 commands');
}
