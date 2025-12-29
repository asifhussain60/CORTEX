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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const commands_1 = require("./commands");
const outputChannel_1 = require("./utils/outputChannel");
const copilotIntegration_1 = require("./utils/copilotIntegration");
function activate(context) {
    console.log('CORTEX extension is now active');
    // Initialize output channel
    const outputChannel = outputChannel_1.OutputChannelManager.getInstance();
    outputChannel.log('CORTEX 4.0 - AI Development Intelligence');
    outputChannel.log('Extension activated successfully');
    // Register all commands
    (0, commands_1.registerCommands)(context);
    // Initialize Copilot integration
    const copilotIntegration = copilotIntegration_1.CopilotIntegration.getInstance();
    copilotIntegration.registerContextProvider(context);
    outputChannel.log('Copilot integration initialized');
    // Show welcome message on first activation
    const config = vscode.workspace.getConfiguration('cortex');
    const hasShownWelcome = context.globalState.get('hasShownWelcome', false);
    if (!hasShownWelcome) {
        vscode.window.showInformationMessage('Welcome to CORTEX! Use "CORTEX: Show Help" or @github in Copilot Chat with CORTEX commands to get started.', 'Show Help', 'Show Dashboard').then(selection => {
            if (selection === 'Show Help') {
                vscode.commands.executeCommand('cortex.help');
            }
            else if (selection === 'Show Dashboard') {
                vscode.commands.executeCommand('cortex.showDashboard');
            }
        });
        context.globalState.update('hasShownWelcome', true);
    }
    outputChannel.log('All commands registered');
}
function deactivate() {
    console.log('CORTEX extension is now deactivated');
    outputChannel_1.OutputChannelManager.dispose();
}
//# sourceMappingURL=extension.js.map