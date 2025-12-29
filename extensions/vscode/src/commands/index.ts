import * as vscode from 'vscode';
import { OutputChannelManager } from '../utils/outputChannel';
import { PythonExecutor } from '../utils/pythonExecutor';
import { WorkspaceDetector } from '../utils/workspaceDetector';
import { DashboardProvider } from '../utils/dashboardProvider';

/**
 * Register all CORTEX commands
 */
export function registerCommands(context: vscode.ExtensionContext): void {
    const outputChannel = OutputChannelManager.getInstance();
    const pythonExecutor = PythonExecutor.getInstance();
    const workspaceDetector = WorkspaceDetector.getInstance();

    // CORTEX: Show Help
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.help', async () => {
            outputChannel.log('Executing command: cortex.help');
            
            const helpMessage = `
**CORTEX 4.0 - AI Development Intelligence**

Available Commands:
• Plan: Create planning folder with TDD
• TDD: RED→GREEN→REFACTOR workflow
• Maintenance: 6-phase health pipeline
• Sanitize: Remove company/PII data
• Refine: 7-phase system improvement
• Onboard: Interactive learning guide
• ADO Planning: Azure DevOps integration
• Dashboard: View brain health & metrics

Use @cortex in GitHub Copilot Chat for natural language interaction.
            `.trim();

            vscode.window.showInformationMessage(
                'CORTEX Help',
                { modal: true, detail: helpMessage },
                'Open Documentation'
            ).then(selection => {
                if (selection === 'Open Documentation') {
                    vscode.env.openExternal(vscode.Uri.parse('https://asifhussain60.github.io/CORTEX/'));
                }
            });
        })
    );

    // CORTEX: Create Planning Folder
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.plan', async () => {
            outputChannel.log('Executing command: cortex.plan');
            
            // Validate configuration
            const validation = await workspaceDetector.validateConfiguration();
            if (!validation.isValid) {
                vscode.window.showErrorMessage(
                    `CORTEX Configuration Error: ${validation.errors.join(', ')}`
                );
                return;
            }

            // Get plan name from user
            const planName = await vscode.window.showInputBox({
                prompt: 'Enter plan name (e.g., "user-authentication-feature")',
                placeHolder: 'feature-name',
                validateInput: (value) => {
                    if (!value || value.trim().length === 0) {
                        return 'Plan name cannot be empty';
                    }
                    if (!/^[a-z0-9-]+$/.test(value)) {
                        return 'Plan name must be lowercase with hyphens (e.g., my-feature)';
                    }
                    return null;
                }
            });

            if (!planName) {
                return; // User cancelled
            }

            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Creating planning folder structure...',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0, message: 'Executing CORTEX Planning System' });
                
                const result = await pythonExecutor.executeCortexCommand('plan', [planName]);
                
                if (result.success) {
                    progress.report({ increment: 100, message: 'Complete!' });
                    vscode.window.showInformationMessage(
                        `✅ Planning folder created: cortex-brain/documents/planning/active/${planName}/`
                    );
                    outputChannel.show();
                } else {
                    vscode.window.showErrorMessage(
                        `❌ Planning folder creation failed: ${result.error}`
                    );
                }
            });
        })
    );

    // CORTEX: Start TDD Workflow
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.startTdd', async () => {
            outputChannel.log('Executing command: cortex.startTdd');
            
            // Validate configuration
            const validation = await workspaceDetector.validateConfiguration();
            if (!validation.isValid) {
                vscode.window.showErrorMessage(
                    `CORTEX Configuration Error: ${validation.errors.join(', ')}`
                );
                return;
            }

            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Starting TDD workflow (RED → GREEN → REFACTOR)...',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0, message: 'Initializing TDD Orchestrator' });
                
                const result = await pythonExecutor.executeCortexCommand('tdd', ['--interactive']);
                
                if (result.success) {
                    progress.report({ increment: 100, message: 'TDD session started!' });
                    vscode.window.showInformationMessage(
                        '✅ TDD Orchestrator started. Check CORTEX output for instructions.'
                    );
                    outputChannel.show();
                } else {
                    vscode.window.showErrorMessage(
                        `❌ TDD workflow failed: ${result.error}`
                    );
                }
            });
        })
    );

    // CORTEX: Run System Maintenance
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.systemMaintenance', async () => {
            outputChannel.log('Executing command: cortex.systemMaintenance');
            
            // Validate configuration
            const validation = await workspaceDetector.validateConfiguration();
            if (!validation.isValid) {
                vscode.window.showErrorMessage(
                    `CORTEX Configuration Error: ${validation.errors.join(', ')}`
                );
                return;
            }

            // Confirm destructive operation
            const confirm = await vscode.window.showWarningMessage(
                'System Maintenance will analyze and optimize your codebase. Continue?',
                { modal: true },
                'Yes, Run Maintenance',
                'Cancel'
            );

            if (confirm !== 'Yes, Run Maintenance') {
                return;
            }

            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Running 6-phase system maintenance...',
                cancellable: false
            }, async (progress) => {
                const phases = [
                    'Pre-Healthcheck',
                    'Alignment',
                    'Cleanup',
                    'Optimization',
                    'Vacuum',
                    'Post-Healthcheck'
                ];

                for (let i = 0; i < phases.length; i++) {
                    progress.report({
                        increment: (i / phases.length) * 100,
                        message: `Phase ${i + 1}/6: ${phases[i]}`
                    });
                    await new Promise(resolve => setTimeout(resolve, 500));
                }

                const result = await pythonExecutor.executeCortexCommand('maintenance', ['--full']);
                
                if (result.success) {
                    progress.report({ increment: 100, message: 'Complete!' });
                    vscode.window.showInformationMessage(
                        '✅ System maintenance complete! Check CORTEX output for report.'
                    );
                    outputChannel.show();
                } else {
                    vscode.window.showErrorMessage(
                        `❌ System maintenance failed: ${result.error}`
                    );
                }
            });
        })
    );

    // CORTEX: Sanitize Code
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.sanitize', async () => {
            outputChannel.log('Executing command: cortex.sanitize');
            
            // Validate configuration
            const validation = await workspaceDetector.validateConfiguration();
            if (!validation.isValid) {
                vscode.window.showErrorMessage(
                    `CORTEX Configuration Error: ${validation.errors.join(', ')}`
                );
                return;
            }

            // Confirm destructive operation
            const confirm = await vscode.window.showWarningMessage(
                'Code Sanitization will remove company data and PII. This modifies files. Continue?',
                { modal: true },
                'Yes, Sanitize Code',
                'Cancel'
            );

            if (confirm !== 'Yes, Sanitize Code') {
                return;
            }

            // Get target directory
            const targetDir = await vscode.window.showInputBox({
                prompt: 'Enter directory to sanitize (relative to workspace root, or leave empty for entire workspace)',
                placeHolder: 'src/ or leave empty',
            });

            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Running 5-phase code sanitization...',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0, message: 'Scanning for sensitive data' });
                
                const args = targetDir ? ['--directory', targetDir] : [];
                const result = await pythonExecutor.executeCortexCommand('sanitize', args);
                
                if (result.success) {
                    progress.report({ increment: 100, message: 'Complete!' });
                    vscode.window.showInformationMessage(
                        '✅ Code sanitization complete! Review changes before committing.'
                    );
                    outputChannel.show();
                } else {
                    vscode.window.showErrorMessage(
                        `❌ Code sanitization failed: ${result.error}`
                    );
                }
            });
        })
    );

    // CORTEX: Run Refinement
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.refine', async () => {
            outputChannel.log('Executing command: cortex.refine');
            
            // Validate configuration
            const validation = await workspaceDetector.validateConfiguration();
            if (!validation.isValid) {
                vscode.window.showErrorMessage(
                    `CORTEX Configuration Error: ${validation.errors.join(', ')}`
                );
                return;
            }

            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Running 7-phase refinement process...',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0, message: 'Analyzing codebase quality' });
                
                const result = await pythonExecutor.executeCortexCommand('refine', ['--comprehensive']);
                
                if (result.success) {
                    progress.report({ increment: 100, message: 'Complete!' });
                    vscode.window.showInformationMessage(
                        '✅ System refinement complete! Check CORTEX output for recommendations.'
                    );
                    outputChannel.show();
                } else {
                    vscode.window.showErrorMessage(
                        `❌ System refinement failed: ${result.error}`
                    );
                }
            });
        })
    );

    // CORTEX: Interactive Onboarding
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.onboard', async () => {
            outputChannel.log('Executing command: cortex.onboard');
            
            // Validate configuration
            const validation = await workspaceDetector.validateConfiguration();
            if (!validation.isValid) {
                vscode.window.showErrorMessage(
                    `CORTEX Configuration Error: ${validation.errors.join(', ')}`
                );
                return;
            }

            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Starting interactive onboarding...',
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0, message: 'Launching onboarding guide' });
                
                const result = await pythonExecutor.executeCortexCommand('onboard');
                
                if (result.success) {
                    progress.report({ increment: 100, message: 'Complete!' });
                    vscode.window.showInformationMessage(
                        '✅ Onboarding started! Check CORTEX output for interactive guide.'
                    );
                    outputChannel.show();
                } else {
                    vscode.window.showErrorMessage(
                        `❌ Onboarding failed: ${result.error}`
                    );
                }
            });
        })
    );

    // CORTEX: ADO Planning
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.adoPlanning', async () => {
            outputChannel.log('Executing command: cortex.adoPlanning');
            
            // Validate configuration
            const validation = await workspaceDetector.validateConfiguration();
            if (!validation.isValid) {
                vscode.window.showErrorMessage(
                    `CORTEX Configuration Error: ${validation.errors.join(', ')}`
                );
                return;
            }

            // Get work item type
            const workItemType = await vscode.window.showQuickPick(
                ['Story', 'Feature', 'Task', 'Bug', 'Epic'],
                {
                    placeHolder: 'Select Azure DevOps work item type',
                    canPickMany: false
                }
            );

            if (!workItemType) {
                return; // User cancelled
            }

            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: `Creating ADO ${workItemType}...`,
                cancellable: false
            }, async (progress) => {
                progress.report({ increment: 0, message: 'Executing ADO Planning Orchestrator' });
                
                const result = await pythonExecutor.executeCortexCommand('ado', [
                    '--type', workItemType.toLowerCase()
                ]);
                
                if (result.success) {
                    progress.report({ increment: 100, message: 'Complete!' });
                    vscode.window.showInformationMessage(
                        `✅ ADO ${workItemType} created successfully!`
                    );
                    outputChannel.show();
                } else {
                    vscode.window.showErrorMessage(
                        `❌ ADO planning failed: ${result.error}`
                    );
                }
            });
        })
    );

    // CORTEX: Show Dashboard
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex.showDashboard', async () => {
            outputChannel.log('Executing command: cortex.showDashboard');
            
            // Initialize and show dashboard
            const dashboard = DashboardProvider.getInstance(context);
            dashboard.show();
        })
    );

    outputChannel.log('Registered 9 commands');
}

