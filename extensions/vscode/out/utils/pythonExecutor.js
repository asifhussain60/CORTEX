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
exports.PythonExecutor = void 0;
const vscode = __importStar(require("vscode"));
const cp = __importStar(require("child_process"));
const path = __importStar(require("path"));
const outputChannel_1 = require("./outputChannel");
const workspaceDetector_1 = require("./workspaceDetector");
/**
 * Manages Python execution for CORTEX backend operations
 */
class PythonExecutor {
    constructor() {
        this.outputChannel = outputChannel_1.OutputChannelManager.getInstance();
        this.workspaceDetector = workspaceDetector_1.WorkspaceDetector.getInstance();
        this.initializePaths();
    }
    static getInstance() {
        if (!PythonExecutor.instance) {
            PythonExecutor.instance = new PythonExecutor();
        }
        return PythonExecutor.instance;
    }
    /**
     * Initialize Python and CORTEX paths from configuration or environment
     */
    initializePaths() {
        // Get Python path from configuration or use default
        const config = vscode.workspace.getConfiguration('cortex');
        this.pythonPath = config.get('pythonPath') || 'python3';
        // Detect CORTEX installation path
        const cortexDetection = this.workspaceDetector.detectCortexInstallation();
        if (cortexDetection.isCortexRepo) {
            this.cortexPath = cortexDetection.workspacePath;
            this.outputChannel.log(`CORTEX installation detected at: ${this.cortexPath}`);
        }
        else {
            this.outputChannel.log('CORTEX installation not detected. User workspace mode.');
        }
    }
    /**
     * Execute a CORTEX Python command
     * @param command CORTEX command (e.g., 'plan', 'tdd', 'maintenance')
     * @param args Additional command arguments
     * @returns Promise resolving to command output
     */
    async executeCortexCommand(command, args = []) {
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
            const output = await this.executeWithTimeout(this.pythonPath, pythonArgs, { cwd: this.cortexPath }, 30000 // 30 second timeout
            );
            this.outputChannel.log(`Command completed successfully`);
            return { success: true, output };
        }
        catch (error) {
            const errorMsg = error instanceof Error ? error.message : String(error);
            this.outputChannel.log(`ERROR: Command failed: ${errorMsg}`);
            return { success: false, output: '', error: errorMsg };
        }
    }
    /**
     * Get the script path for a CORTEX command
     */
    getScriptPath(command) {
        const scriptMap = {
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
        return path.join(this.cortexPath, scriptPath);
    }
    /**
     * Execute a command with timeout
     */
    executeWithTimeout(command, args, options, timeout) {
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
            process.stdout?.on('data', (data) => {
                const text = data.toString();
                output += text;
                this.outputChannel.log(text);
            });
            // Collect stderr
            process.stderr?.on('data', (data) => {
                const text = data.toString();
                errorOutput += text;
                this.outputChannel.log(`STDERR: ${text}`);
            });
            // Handle completion
            process.on('close', (code) => {
                clearTimeout(timer);
                if (code === 0) {
                    resolve(output);
                }
                else {
                    reject(new Error(`Process exited with code ${code}: ${errorOutput}`));
                }
            });
            // Handle errors
            process.on('error', (error) => {
                clearTimeout(timer);
                reject(error);
            });
        });
    }
    /**
     * Validate Python installation
     */
    async validatePythonInstallation() {
        try {
            const result = await this.executeWithTimeout(this.pythonPath, ['--version'], {}, 5000);
            this.outputChannel.log(`Python validation: ${result}`);
            return true;
        }
        catch (error) {
            this.outputChannel.log(`ERROR: Python validation failed: ${error}`);
            return false;
        }
    }
    /**
     * Update configuration paths
     */
    updatePaths(pythonPath, cortexPath) {
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
    getConfiguration() {
        return {
            pythonPath: this.pythonPath,
            cortexPath: this.cortexPath
        };
    }
}
exports.PythonExecutor = PythonExecutor;
//# sourceMappingURL=pythonExecutor.js.map