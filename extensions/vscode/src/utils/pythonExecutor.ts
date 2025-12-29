import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';
import { OutputChannelManager } from './outputChannel';
import { WorkspaceDetector } from './workspaceDetector';

/**
 * Manages Python execution for CORTEX backend operations
 */
export class PythonExecutor {
    private static instance: PythonExecutor;
    private pythonPath: string | undefined;
    private cortexPath: string | undefined;
    private outputChannel: OutputChannelManager;
    private workspaceDetector: WorkspaceDetector;

    private constructor() {
        this.outputChannel = OutputChannelManager.getInstance();
        this.workspaceDetector = WorkspaceDetector.getInstance();
        this.initializePaths();
    }

    public static getInstance(): PythonExecutor {
        if (!PythonExecutor.instance) {
            PythonExecutor.instance = new PythonExecutor();
        }
        return PythonExecutor.instance;
    }

    /**
     * Initialize Python and CORTEX paths from configuration or environment
     */
    private initializePaths(): void {
        // Get Python path from configuration or use default
        const config = vscode.workspace.getConfiguration('cortex');
        this.pythonPath = config.get<string>('pythonPath') || 'python3';

        // Detect CORTEX installation path
        const cortexDetection = this.workspaceDetector.detectCortexInstallation();
        if (cortexDetection.isCortexRepo) {
            this.cortexPath = cortexDetection.workspacePath;
            this.outputChannel.log(`CORTEX installation detected at: ${this.cortexPath}`);
        } else {
            this.outputChannel.log('CORTEX installation not detected. User workspace mode.');
        }
    }

    /**
     * Execute a CORTEX Python command
     * @param command CORTEX command (e.g., 'plan', 'tdd', 'maintenance')
     * @param args Additional command arguments
     * @returns Promise resolving to command output
     */
    public async executeCortexCommand(
        command: string,
        args: string[] = []
    ): Promise<{ success: boolean; output: string; error?: string }> {
        try {
            this.outputChannel.log(`Executing CORTEX command: ${command} ${args.join(' ')}`);

            // Validate CORTEX installation
            if (!this.cortexPath) {
                throw new Error('CORTEX installation not found. Please install CORTEX first.');
            }

            // Build Python command
            const scriptPath = this.getScriptPath(command);
            const pythonArgs = [scriptPath, ...args];

            // Execute with timeout
            const output = await this.executeWithTimeout(
                this.pythonPath!,
                pythonArgs,
                { cwd: this.cortexPath },
                30000 // 30 second timeout
            );

            this.outputChannel.log(`Command completed successfully`);
            return { success: true, output };

        } catch (error) {
            const errorMsg = error instanceof Error ? error.message : String(error);
            this.outputChannel.log(`ERROR: Command failed: ${errorMsg}`);
            return { success: false, output: '', error: errorMsg };
        }
    }

    /**
     * Get the script path for a CORTEX command
     */
    private getScriptPath(command: string): string {
        const scriptMap: Record<string, string> = {
            'plan': 'src/orchestrators/planning_orchestrator_4.0.py',
            'tdd': 'src/orchestrators/tdd_orchestrator_v4.py',
            'maintenance': 'scripts/maintenance.py',
            'sanitize': 'src/orchestrators/sanitization_orchestrator.py',
            'refine': 'src/orchestrators/refinement_orchestrator.py',
            'onboard': 'src/onboarding_interactive.py',
            'ado': 'src/orchestrators/ado_planning_orchestrator.py',
        };

        const scriptPath = scriptMap[command];
        if (!scriptPath) {
            throw new Error(`Unknown command: ${command}`);
        }

        return path.join(this.cortexPath!, scriptPath);
    }

    /**
     * Execute a command with timeout
     */
    private executeWithTimeout(
        command: string,
        args: string[],
        options: cp.SpawnOptions,
        timeout: number
    ): Promise<string> {
        return new Promise((resolve, reject) => {
            let output = '';
            let errorOutput = '';

            const process = cp.spawn(command, args, options);

            // Set timeout
            const timer = setTimeout(() => {
                process.kill();
                reject(new Error(`Command timed out after ${timeout}ms`));
            }, timeout);

            // Collect stdout
            process.stdout?.on('data', (data: Buffer) => {
                const text = data.toString();
                output += text;
                this.outputChannel.log(text);
            });

            // Collect stderr
            process.stderr?.on('data', (data: Buffer) => {
                const text = data.toString();
                errorOutput += text;
                this.outputChannel.log(`STDERR: ${text}`);
            });

            // Handle completion
            process.on('close', (code: number | null) => {
                clearTimeout(timer);
                if (code === 0) {
                    resolve(output);
                } else {
                    reject(new Error(`Process exited with code ${code}: ${errorOutput}`));
                }
            });

            // Handle errors
            process.on('error', (error: Error) => {
                clearTimeout(timer);
                reject(error);
            });
        });
    }

    /**
     * Validate Python installation
     */
    public async validatePythonInstallation(): Promise<boolean> {
        try {
            const result = await this.executeWithTimeout(
                this.pythonPath!,
                ['--version'],
                {},
                5000
            );
            this.outputChannel.log(`Python validation: ${result}`);
            return true;
        } catch (error) {
            this.outputChannel.log(`ERROR: Python validation failed: ${error}`);
            return false;
        }
    }

    /**
     * Update configuration paths
     */
    public updatePaths(pythonPath?: string, cortexPath?: string): void {
        if (pythonPath) {
            this.pythonPath = pythonPath;
        }
        if (cortexPath) {
            this.cortexPath = cortexPath;
        }
        this.outputChannel.log(`Paths updated: Python=${this.pythonPath}, CORTEX=${this.cortexPath}`);
    }

    /**
     * Get current configuration
     */
    public getConfiguration(): { pythonPath?: string; cortexPath?: string } {
        return {
            pythonPath: this.pythonPath,
            cortexPath: this.cortexPath
        };
    }
}
