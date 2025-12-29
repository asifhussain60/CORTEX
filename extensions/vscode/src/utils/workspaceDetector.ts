import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';

/**
 * Detection result for CORTEX workspace
 */
export interface CortexDetectionResult {
    isCortexRepo: boolean;
    isUserWorkspace: boolean;
    workspacePath: string;
    hasManifests: boolean;
    hasCortexBrain: boolean;
}

/**
 * Detects and manages CORTEX workspace context
 */
export class WorkspaceDetector {
    private static instance: WorkspaceDetector;

    private constructor() {}

    public static getInstance(): WorkspaceDetector {
        if (!WorkspaceDetector.instance) {
            WorkspaceDetector.instance = new WorkspaceDetector();
        }
        return WorkspaceDetector.instance;
    }

    /**
     * Detect if current workspace is CORTEX repository or user workspace
     */
    public detectCortexInstallation(): CortexDetectionResult {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        
        if (!workspaceFolders || workspaceFolders.length === 0) {
            return {
                isCortexRepo: false,
                isUserWorkspace: false,
                workspacePath: '',
                hasManifests: false,
                hasCortexBrain: false
            };
        }

        const workspacePath = workspaceFolders[0].uri.fsPath;

        // Check for CORTEX repository markers
        const hasCortexBrain = this.directoryExists(path.join(workspacePath, 'cortex-brain'));
        const hasManifests = this.directoryExists(path.join(workspacePath, 'cortex-brain', 'manifests'));
        const hasSrcOrchestrators = this.directoryExists(path.join(workspacePath, 'src', 'orchestrators'));
        
        const isCortexRepo = hasCortexBrain && hasManifests && hasSrcOrchestrators;
        const isUserWorkspace = !isCortexRepo;

        return {
            isCortexRepo,
            isUserWorkspace,
            workspacePath,
            hasManifests,
            hasCortexBrain
        };
    }

    /**
     * Get CORTEX installation path from configuration or environment
     */
    public getCortexInstallationPath(): string | undefined {
        // 1. Check VS Code configuration
        const config = vscode.workspace.getConfiguration('cortex');
        const configPath = config.get<string>('installationPath');
        if (configPath && this.isValidCortexPath(configPath)) {
            return configPath;
        }

        // 2. Check environment variable
        const envPath = process.env.CORTEX_HOME;
        if (envPath && this.isValidCortexPath(envPath)) {
            return envPath;
        }

        // 3. Check if current workspace is CORTEX
        const detection = this.detectCortexInstallation();
        if (detection.isCortexRepo) {
            return detection.workspacePath;
        }

        // 4. Check common installation locations
        const commonPaths = [
            path.join(process.env.HOME || '', 'PROJECTS', 'CORTEX'),
            path.join(process.env.HOME || '', 'projects', 'cortex'),
            '/usr/local/cortex',
            'C:\\Program Files\\CORTEX'
        ];

        for (const commonPath of commonPaths) {
            if (this.isValidCortexPath(commonPath)) {
                return commonPath;
            }
        }

        return undefined;
    }

    /**
     * Validate if path is a valid CORTEX installation
     */
    private isValidCortexPath(cortexPath: string): boolean {
        try {
            const hasCortexBrain = this.directoryExists(path.join(cortexPath, 'cortex-brain'));
            const hasManifests = this.directoryExists(path.join(cortexPath, 'cortex-brain', 'manifests'));
            const hasSrc = this.directoryExists(path.join(cortexPath, 'src'));
            
            return hasCortexBrain && hasManifests && hasSrc;
        } catch {
            return false;
        }
    }

    /**
     * Check if directory exists
     */
    private directoryExists(dirPath: string): boolean {
        try {
            return fs.existsSync(dirPath) && fs.statSync(dirPath).isDirectory();
        } catch {
            return false;
        }
    }

    /**
     * Get workspace root path
     */
    public getWorkspaceRoot(): string | undefined {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        return workspaceFolders && workspaceFolders.length > 0 
            ? workspaceFolders[0].uri.fsPath 
            : undefined;
    }

    /**
     * Check if CORTEX is properly configured
     */
    public async validateConfiguration(): Promise<{
        isValid: boolean;
        errors: string[];
        warnings: string[];
    }> {
        const errors: string[] = [];
        const warnings: string[] = [];

        // Check workspace
        const workspaceRoot = this.getWorkspaceRoot();
        if (!workspaceRoot) {
            errors.push('No workspace folder open');
            return { isValid: false, errors, warnings };
        }

        // Check CORTEX installation
        const cortexPath = this.getCortexInstallationPath();
        if (!cortexPath) {
            errors.push('CORTEX installation not found. Please configure cortex.installationPath in settings.');
        }

        // Check Python
        const config = vscode.workspace.getConfiguration('cortex');
        const pythonPath = config.get<string>('pythonPath') || 'python3';
        try {
            // This is a simple check - actual validation happens in PythonExecutor
            if (!pythonPath) {
                warnings.push('Python path not configured, using default "python3"');
            }
        } catch {
            warnings.push('Could not validate Python installation');
        }

        return {
            isValid: errors.length === 0,
            errors,
            warnings
        };
    }
}
