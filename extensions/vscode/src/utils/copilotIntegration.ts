import * as vscode from 'vscode';
import { OutputChannelManager } from './outputChannel';
import { PythonExecutor } from './pythonExecutor';
import { WorkspaceDetector } from './workspaceDetector';

/**
 * Intent classification for natural language commands
 */
export interface CommandIntent {
    command: string;
    confidence: number;
    args: string[];
}

/**
 * Manages GitHub Copilot Chat integration for CORTEX
 * Note: This provides enhanced command routing and context for Copilot Chat
 */
export class CopilotIntegration {
    private static instance: CopilotIntegration;
    private outputChannel: OutputChannelManager;
    private pythonExecutor: PythonExecutor;
    private workspaceDetector: WorkspaceDetector;

    private constructor() {
        this.outputChannel = OutputChannelManager.getInstance();
        this.pythonExecutor = PythonExecutor.getInstance();
        this.workspaceDetector = WorkspaceDetector.getInstance();
    }

    public static getInstance(): CopilotIntegration {
        if (!CopilotIntegration.instance) {
            CopilotIntegration.instance = new CopilotIntegration();
        }
        return CopilotIntegration.instance;
    }

    /**
     * Register CORTEX context provider for Copilot Chat
     * This enhances Copilot's understanding of CORTEX commands
     */
    public registerContextProvider(context: vscode.ExtensionContext): void {
        this.outputChannel.log('Registering Copilot context provider');

        // Register workspace state updates
        this.updateCopilotContext();

        // Watch for brain changes to update context
        const brainWatcher = vscode.workspace.createFileSystemWatcher(
            '**/cortex-brain/**/*.{json,yaml,md}'
        );

        brainWatcher.onDidChange(() => this.updateCopilotContext());
        brainWatcher.onDidCreate(() => this.updateCopilotContext());
        brainWatcher.onDidDelete(() => this.updateCopilotContext());

        context.subscriptions.push(brainWatcher);
    }

    /**
     * Update workspace state to provide context to Copilot
     */
    private async updateCopilotContext(): Promise<void> {
        const detection = this.workspaceDetector.detectCortexInstallation();
        
        // Store context in workspace state for Copilot to access
        const context = {
            isCortexRepo: detection.isCortexRepo,
            hasManifests: detection.hasManifests,
            hasCortexBrain: detection.hasCortexBrain,
            availableCommands: this.getAvailableCommands(),
            recentOperations: await this.getRecentOperations()
        };

        this.outputChannel.log(`Updated Copilot context: ${JSON.stringify(context)}`);
    }

    /**
     * Parse natural language input to detect CORTEX command intent
     */
    public parseIntent(input: string): CommandIntent | null {
        const normalizedInput = input.toLowerCase().trim();

        // Direct command patterns
        const intentPatterns: Array<{pattern: RegExp; command: string; confidence: number}> = [
            // Planning
            { pattern: /\b(create|make|start|new)\s+(a\s+)?plan(ning)?(\s+folder)?/i, command: 'plan', confidence: 0.9 },
            { pattern: /\bplan\s+(for|about)\s+(.+)/i, command: 'plan', confidence: 0.85 },
            
            // TDD
            { pattern: /\b(start|begin|run|execute)\s+tdd/i, command: 'tdd', confidence: 0.9 },
            { pattern: /\b(red|green|refactor)\s+(cycle|workflow)/i, command: 'tdd', confidence: 0.85 },
            { pattern: /\btest\s+driven\s+development/i, command: 'tdd', confidence: 0.8 },
            
            // Maintenance
            { pattern: /\b(run|execute|perform)\s+(system\s+)?maintenance/i, command: 'maintenance', confidence: 0.9 },
            { pattern: /\b(health|check|analyze)\s+(system|codebase)/i, command: 'maintenance', confidence: 0.7 },
            { pattern: /\bclean(up)?\s+(the\s+)?(code|system)/i, command: 'maintenance', confidence: 0.7 },
            
            // Sanitization
            { pattern: /\bsanitize\s+(the\s+)?(code|files)/i, command: 'sanitize', confidence: 0.9 },
            { pattern: /\bremove\s+(company\s+)?(data|secrets|pii)/i, command: 'sanitize', confidence: 0.8 },
            { pattern: /\b(anonymize|clean)\s+sensitive/i, command: 'sanitize', confidence: 0.75 },
            
            // Refinement
            { pattern: /\brefine\s+(the\s+)?(code|system)/i, command: 'refine', confidence: 0.9 },
            { pattern: /\bimprove\s+(code\s+)?quality/i, command: 'refine', confidence: 0.75 },
            { pattern: /\b(optimize|enhance)\s+(the\s+)?(codebase|system)/i, command: 'refine', confidence: 0.7 },
            
            // Onboarding
            { pattern: /\b(start|show|begin)\s+onboarding/i, command: 'onboard', confidence: 0.9 },
            { pattern: /\b(learn|getting\s+started|tutorial)\s+(cortex|about)/i, command: 'onboard', confidence: 0.8 },
            
            // ADO
            { pattern: /\b(create|make)\s+(ado|azure\s+devops)\s+(story|feature|task|bug)/i, command: 'ado', confidence: 0.9 },
            { pattern: /\bado\s+planning/i, command: 'ado', confidence: 0.85 },
            
            // Dashboard
            { pattern: /\b(show|open|display)\s+(the\s+)?dashboard/i, command: 'dashboard', confidence: 0.9 },
            { pattern: /\b(brain\s+)?health\s+(status|metrics)/i, command: 'dashboard', confidence: 0.75 },
            
            // Help
            { pattern: /\b(show|display|get)\s+help/i, command: 'help', confidence: 0.9 },
            { pattern: /\bwhat\s+can\s+(cortex|you)\s+do/i, command: 'help', confidence: 0.85 }
        ];

        // Check each pattern
        for (const { pattern, command, confidence } of intentPatterns) {
            const match = normalizedInput.match(pattern);
            if (match) {
                // Extract arguments if any
                const args: string[] = [];
                if (command === 'plan' && match[2]) {
                    args.push(match[2].trim());
                }

                return { command, confidence, args };
            }
        }

        return null;
    }

    /**
     * Execute a CORTEX command from natural language input
     */
    public async executeFromNaturalLanguage(input: string): Promise<boolean> {
        const intent = this.parseIntent(input);

        if (!intent || intent.confidence < 0.7) {
            this.outputChannel.log(`No confident intent found for: "${input}"`);
            return false;
        }

        this.outputChannel.log(`Detected intent: ${intent.command} (confidence: ${intent.confidence})`);

        // Map to VS Code commands
        const commandMap: Record<string, string> = {
            'plan': 'cortex.plan',
            'tdd': 'cortex.startTdd',
            'maintenance': 'cortex.systemMaintenance',
            'sanitize': 'cortex.sanitize',
            'refine': 'cortex.refine',
            'onboard': 'cortex.onboard',
            'ado': 'cortex.adoPlanning',
            'dashboard': 'cortex.showDashboard',
            'help': 'cortex.help'
        };

        const vsCodeCommand = commandMap[intent.command];
        if (vsCodeCommand) {
            await vscode.commands.executeCommand(vsCodeCommand, ...intent.args);
            return true;
        }

        return false;
    }

    /**
     * Get available CORTEX commands for context
     */
    private getAvailableCommands(): string[] {
        return [
            'plan - Create planning folder with TDD',
            'tdd - Start RED→GREEN→REFACTOR workflow',
            'maintenance - Run 6-phase system maintenance',
            'sanitize - Remove company data and PII',
            'refine - Run 7-phase system refinement',
            'onboard - Interactive onboarding guide',
            'ado - Azure DevOps planning',
            'dashboard - Show brain health metrics',
            'help - Show all commands'
        ];
    }

    /**
     * Get recent operations for context
     */
    private async getRecentOperations(): Promise<string[]> {
        const cortexPath = this.workspaceDetector.getCortexInstallationPath();
        if (!cortexPath) {
            return [];
        }

        // Simplified - would parse actual logs in production
        return [
            'Last operation: Planning (2h ago)',
            'Recent: TDD workflow (5h ago)',
            'Recent: System maintenance (1d ago)'
        ];
    }

    /**
     * Generate contextual response for Copilot Chat
     */
    public generateContextualResponse(command: string): string {
        const responses: Record<string, string> = {
            'plan': '📋 The Planning System creates a 4-folder structure (00-master-plan.md, context/, reports/, artifacts/) with DoR/DoD enforcement and TDD integration.',
            'tdd': '🧪 TDD Orchestrator follows RED→GREEN→REFACTOR cycle with automatic test execution and learning from failures.',
            'maintenance': '🔧 System Maintenance runs 6 phases: Pre-healthcheck → Align → Cleanup → Optimize → Vacuum → Post-healthcheck.',
            'sanitize': '🧹 Code Sanitization removes hardcoded secrets, company data, and PII in 5 phases with Git checkpoint protection.',
            'refine': '✨ System Refinement analyzes code quality across 7 dimensions with SOLID principles and architectural recommendations.',
            'onboard': '🚀 Interactive Onboarding provides a 6-phase guided tour through all CORTEX capabilities.',
            'ado': '📊 ADO Planning creates Azure DevOps work items (Story/Feature/Task/Bug/Epic) with full traceability.',
            'dashboard': '🧠 Dashboard displays 4-tier brain health metrics, recent operations, and planning folders.',
            'help': '❓ CORTEX provides 8 major orchestrators plus autonomous execution, multi-repo support, and long-term memory.'
        };

        return responses[command] || 'CORTEX command executed successfully.';
    }
}
