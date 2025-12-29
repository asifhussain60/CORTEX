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
exports.OutputChannelManager = void 0;
const vscode = __importStar(require("vscode"));
/**
 * Singleton class to manage the CORTEX output channel
 */
class OutputChannelManager {
    constructor() {
        this.outputChannel = vscode.window.createOutputChannel('CORTEX');
    }
    static getInstance() {
        if (!OutputChannelManager.instance) {
            OutputChannelManager.instance = new OutputChannelManager();
        }
        return OutputChannelManager.instance;
    }
    log(message) {
        const timestamp = new Date().toLocaleTimeString();
        this.outputChannel.appendLine(`[${timestamp}] ${message}`);
    }
    show() {
        this.outputChannel.show();
    }
    static dispose() {
        if (OutputChannelManager.instance) {
            OutputChannelManager.instance.outputChannel.dispose();
        }
    }
}
exports.OutputChannelManager = OutputChannelManager;
//# sourceMappingURL=outputChannel.js.map