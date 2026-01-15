import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { execSync } from 'child_process';

/**
 * CORTEX Governance VS Code Extension
 * 
 * Provides real-time governance compliance diagnostics in the VS Code editor.
 * Shows governance violations inline with quick-fix suggestions.
 */

let diagnosticCollection: vscode.DiagnosticCollection;
let statusBarItem: vscode.StatusBarItem;

export function activate(context: vscode.ExtensionContext) {
    console.log('CORTEX Governance extension activated');

    // Create diagnostic collection
    diagnosticCollection = vscode.languages.createDiagnosticCollection('cortex-governance');
    context.subscriptions.push(diagnosticCollection);

    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'cortex-governance.showStatus';
    statusBarItem.text = '$(check) CORTEX';
    context.subscriptions.push(statusBarItem);
    statusBarItem.show();

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('cortex-governance.analyze', analyzeCurrentFile)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('cortex-governance.clearCache', clearCache)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('cortex-governance.showRules', showRules)
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('cortex-governance.showStatus', showStatus)
    );

    // Set up event listeners
    context.subscriptions.push(
        vscode.window.onDidOpenTextDocument(onDocumentOpen)
    );

    context.subscriptions.push(
        vscode.window.onDidSaveTextDocument(onDocumentSave)
    );

    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(onConfigurationChange)
    );

    // Analyze current file if any
    if (vscode.window.activeTextEditor) {
        analyzeFile(vscode.window.activeTextEditor.document);
    }

    // Register code actions for quick fixes
    context.subscriptions.push(
        vscode.languages.registerCodeActionsProvider(
            { language: 'python' },
            new GovernanceCodeActionProvider()
        )
    );

    updateStatusBar();
}

/**
 * Analyze the currently active file.
 */
async function analyzeCurrentFile(): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('No active editor');
        return;
    }

    await analyzeFile(editor.document);
}

/**
 * Analyze a specific document.
 */
async function analyzeFile(document: vscode.TextDocument): Promise<void> {
    if (document.languageId !== 'python') {
        return;
    }

    const config = vscode.workspace.getConfiguration('cortex-governance');
    if (!config.get<boolean>('enable')) {
        return;
    }

    try {
        const diagnostics = await getDiagnosticsForFile(document.uri.fsPath);
        diagnosticCollection.set(document.uri, diagnostics);
        updateStatusBar();
    } catch (error) {
        console.error('Error analyzing file:', error);
    }
}

/**
 * Get diagnostics for a file by running the governance CLI.
 */
async function getDiagnosticsForFile(filePath: string): Promise<vscode.Diagnostic[]> {
    try {
        const cliScript = path.join(
            vscode.workspace.workspaceFolders?.[0]?.uri?.fsPath || '.',
            'src/tools/governance-cli.py'
        );

        if (!fs.existsSync(cliScript)) {
            console.warn('Governance CLI script not found');
            return [];
        }

        // Run validation command
        const result = execSync(
            `python3 "${cliScript}" validate "${filePath}" --format json`,
            { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }
        );

        const data = JSON.parse(result);
        const violations = data.violations || [];

        // Convert violations to VSCode diagnostics
        const diagnostics: vscode.Diagnostic[] = violations.map((v: any) => {
            const line = (v.line || 1) - 1; // Convert to 0-indexed
            const range = new vscode.Range(line, 0, line, 1);

            let severity = vscode.DiagnosticSeverity.Warning;
            if (v.severity === 'blocked' || v.severity === 'error') {
                severity = vscode.DiagnosticSeverity.Error;
            } else if (v.severity === 'info') {
                severity = vscode.DiagnosticSeverity.Information;
            }

            const diagnostic = new vscode.Diagnostic(
                range,
                `[${v.rule_id}] ${v.message}`,
                severity
            );
            diagnostic.code = v.rule_id;
            diagnostic.source = 'cortex-governance';

            // Store fix suggestion for code actions
            if (v.fix_suggestion) {
                (diagnostic as any).fixSuggestion = v.fix_suggestion;
            }

            return diagnostic;
        });

        return diagnostics;

    } catch (error: any) {
        if (error.stderr) {
            console.log('Validation stderr:', error.stderr);
        }
        return [];
    }
}

/**
 * Called when a document is opened.
 */
function onDocumentOpen(document: vscode.TextDocument): void {
    const config = vscode.workspace.getConfiguration('cortex-governance');
    if (config.get<boolean>('validateOnOpen')) {
        analyzeFile(document);
    }
}

/**
 * Called when a document is saved.
 */
function onDocumentSave(document: vscode.TextDocument): void {
    const config = vscode.workspace.getConfiguration('cortex-governance');
    if (config.get<boolean>('autoAnalyze')) {
        analyzeFile(document);
    }
}

/**
 * Called when configuration changes.
 */
function onConfigurationChange(): void {
    // Re-analyze all open documents
    vscode.workspace.textDocuments.forEach(doc => {
        if (doc.languageId === 'python') {
            analyzeFile(doc);
        }
    });
}

/**
 * Clear the diagnostics cache.
 */
function clearCache(): void {
    diagnosticCollection.clear();
    vscode.window.showInformationMessage('CORTEX governance cache cleared');
    updateStatusBar();
}

/**
 * Show governance rules reference.
 */
async function showRules(): Promise<void> {
    const panel = vscode.window.createWebviewPanel(
        'cortexRules',
        'CORTEX Governance Rules',
        vscode.ViewColumn.Two,
        { enableScripts: true }
    );

    panel.webview.html = getRulesHtml();
}

/**
 * Show extension status.
 */
function showStatus(): void {
    const statusMessage = getDiagnosticsSummary();
    vscode.window.showInformationMessage(`CORTEX Governance: ${statusMessage}`);
}

/**
 * Get a summary of all diagnostics.
 */
function getDiagnosticsSummary(): string {
    let errors = 0, warnings = 0, infos = 0;

    diagnosticCollection.forEach((uri, diagnostics) => {
        diagnostics?.forEach(d => {
            if (d.severity === vscode.DiagnosticSeverity.Error) errors++;
            else if (d.severity === vscode.DiagnosticSeverity.Warning) warnings++;
            else if (d.severity === vscode.DiagnosticSeverity.Information) infos++;
        });
    });

    if (errors === 0 && warnings === 0 && infos === 0) {
        return 'No violations';
    }

    const parts = [];
    if (errors > 0) parts.push(`${errors} error${errors > 1 ? 's' : ''}`);
    if (warnings > 0) parts.push(`${warnings} warning${warnings > 1 ? 's' : ''}`);
    if (infos > 0) parts.push(`${infos} info`);

    return parts.join(', ');
}

/**
 * Update the status bar with diagnostic summary.
 */
function updateStatusBar(): void {
    const summary = getDiagnosticsSummary();
    statusBarItem.text = `$(check) CORTEX: ${summary}`;
}

/**
 * Generate HTML for rules panel.
 */
function getRulesHtml(): string {
    return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .rule { margin: 10px 0; padding: 10px; border-left: 3px solid #0066cc; }
        .rule-id { font-weight: bold; color: #0066cc; }
        .rule-description { margin-top: 5px; color: #666; }
    </style>
</head>
<body>
    <h1>CORTEX Governance Rules</h1>
    <p>Core rules enforced by CORTEX governance:</p>
    
    <div class="rule">
        <div class="rule-id">CORE-008: Test-Driven Development</div>
        <div class="rule-description">All new code must have tests before implementation</div>
    </div>
    
    <div class="rule">
        <div class="rule-id">CORE-011: Type Hints</div>
        <div class="rule-description">All functions must have type hints</div>
    </div>
    
    <div class="rule">
        <div class="rule-id">CORE-012: Docstrings</div>
        <div class="rule-description">All public APIs must have docstrings (Google style)</div>
    </div>
    
    <div class="rule">
        <div class="rule-id">CORE-013: Exception Handling</div>
        <div class="rule-description">No bare except clauses; use specific exception types</div>
    </div>
    
    <div class="rule">
        <div class="rule-id">CORE-028: Naming Conventions</div>
        <div class="rule-description">Use kebab-case for file names, max 25 characters</div>
    </div>
    
    <p><strong>For more rules, see:</strong> <code>cortex-brain/tier0/governance/core-rules.yaml</code></p>
</body>
</html>`;
}

/**
 * Code actions provider for quick fixes.
 */
class GovernanceCodeActionProvider implements vscode.CodeActionProvider {
    provideCodeActions(
        document: vscode.TextDocument,
        range: vscode.Range,
        context: vscode.CodeActionContext
    ): vscode.CodeAction[] {
        const actions: vscode.CodeAction[] = [];

        context.diagnostics
            .filter(d => d.source === 'cortex-governance')
            .forEach(diagnostic => {
                const suggestion = (diagnostic as any).fixSuggestion;
                if (suggestion) {
                    const action = new vscode.CodeAction(
                        `Fix: ${suggestion}`,
                        vscode.CodeActionKind.QuickFix
                    );
                    action.diagnostic = diagnostic;
                    action.command = {
                        command: 'cortex-governance.applySuggestion',
                        title: 'Apply fix suggestion',
                        arguments: [document.uri, diagnostic.code, suggestion]
                    };
                    actions.push(action);
                }
            });

        return actions;
    }
}

export function deactivate() {
    diagnosticCollection.dispose();
    statusBarItem.dispose();
}
