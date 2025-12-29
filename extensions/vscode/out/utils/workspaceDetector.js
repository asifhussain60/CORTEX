"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.WorkspaceDetector = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
/**
 * Detects and manages CORTEX workspace context
 */
class WorkspaceDetector {
    constructor() { }
    static getInstance() {
        if (!WorkspaceDetector.instance) {
            WorkspaceDetector.instance = new WorkspaceDetector();
        }
        return WorkspaceDetector.instance;
    }
    /**
     * Detect if current workspace is CORTEX repository or user workspace
     */
    detectCortexInstallation() {
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
    getCortexInstallationPath() {
        // 1. Check VS Code configuration
        const config = vscode.workspace.getConfiguration('cortex');
        const configPath = config.get('installationPath');
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
    isValidCortexPath(cortexPath) {
        try {
            const hasCortexBrain = this.directoryExists(path.join(cortexPath, 'cortex-brain'));
            const hasManifests = this.directoryExists(path.join(cortexPath, 'cortex-brain', 'manifests'));
            const hasSrc = this.directoryExists(path.join(cortexPath, 'src'));
            return hasCortexBrain && hasManifests && hasSrc;
        }
        catch {
            return false;
        }
    }
    /**
     * Check if directory exists
     */
    directoryExists(dirPath) {
        try {
            return fs.existsSync(dirPath) && fs.statSync(dirPath).isDirectory();
        }
        catch {
            return false;
        }
    }
    /**
     * Get workspace root path
     */
    getWorkspaceRoot() {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        return workspaceFolders && workspaceFolders.length > 0
            ? workspaceFolders[0].uri.fsPath
            : undefined;
    }
    /**
     * Check if CORTEX is properly configured
     */
    async validateConfiguration() {
        const errors = [];
        const warnings = [];
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
        const pythonPath = config.get('pythonPath') || 'python3';
        try {
            // This is a simple check - actual validation happens in PythonExecutor
            if (!pythonPath) {
                warnings.push('Python path not configured, using default "python3"');
            }
        }
        catch {
            warnings.push('Could not validate Python installation');
        }
        return {
            isValid: errors.length === 0,
            errors,
            warnings
        };
    }
}
exports.WorkspaceDetector = WorkspaceDetector;
//# sourceMappingURL=workspaceDetector.js.map