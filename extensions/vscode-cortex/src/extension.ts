/**
 * CORTEX VS Code Extension
 * AC-DEPLOY-ENHANCED-004-01
 *
 * Connects VS Code to CORTEX MCP hub for governance validation,
 * violation display, quick fixes, and audit trail viewing.
 */

import * as vscode from "vscode";
import * as path from "path";
import { MCPClient } from "./mcp_client";
import { DiagnosticsManager } from "./diagnostics";
import { AuditTrailProvider } from "./audit_trail";
import { HealthStatusProvider } from "./health_status";

// Global state
let diagnosticsManager: DiagnosticsManager;
let auditTrailProvider: AuditTrailProvider;
let healthStatusProvider: HealthStatusProvider;
let mcpClient: MCPClient;

/**
 * Extension activation - runs when extension loads.
 */
export async function activate(context: vscode.ExtensionContext) {
  console.log("CORTEX extension activating...");

  try {
    // Initialize MCP client
    mcpClient = new MCPClient(context);
    await mcpClient.initialize();

    // Initialize diagnostics manager
    diagnosticsManager = new DiagnosticsManager(mcpClient);
    context.subscriptions.push(diagnosticsManager);

    // Initialize audit trail viewer
    auditTrailProvider = new AuditTrailProvider(mcpClient);
    vscode.window.registerTreeDataProvider(
      "cortex-audit-trail",
      auditTrailProvider
    );
    context.subscriptions.push(
      vscode.commands.registerCommand("cortex.showAuditTrail", () =>
        auditTrailProvider.refresh()
      )
    );

    // Initialize health status
    healthStatusProvider = new HealthStatusProvider(mcpClient);
    vscode.window.registerTreeDataProvider(
      "cortex-health",
      healthStatusProvider
    );
    context.subscriptions.push(
      vscode.commands.registerCommand("cortex.showHealth", () =>
        healthStatusProvider.refresh()
      )
    );

    // Register commands
    context.subscriptions.push(
      vscode.commands.registerCommand("cortex.connectToHub", async () => {
        try {
          await mcpClient.connect();
          vscode.window.showInformationMessage(
            "✓ Connected to CORTEX hub"
          );
        } catch (error) {
          vscode.window.showErrorMessage(
            `✗ Failed to connect: ${error}`
          );
        }
      })
    );

    context.subscriptions.push(
      vscode.commands.registerCommand("cortex.showViolations", async () => {
        await diagnosticsManager.refresh();
        vscode.window.showInformationMessage(
          "✓ Violations refreshed"
        );
      })
    );

    context.subscriptions.push(
      vscode.commands.registerCommand("cortex.applyQuickFix", async () => {
        await diagnosticsManager.applyQuickFix();
      })
    );

    // Watch for configuration changes
    vscode.workspace.onDidChangeConfiguration(
      async (event) => {
        if (event.affectsConfiguration("cortex")) {
          await mcpClient.updateConfiguration();
          await diagnosticsManager.refresh();
        }
      },
      null,
      context.subscriptions
    );

    // Watch for file changes
    vscode.workspace.onDidChangeTextDocument(
      async (event) => {
        await diagnosticsManager.validateFile(event.document);
      },
      null,
      context.subscriptions
    );

    // Initial validation of open files
    for (const editor of vscode.window.visibleTextEditors) {
      await diagnosticsManager.validateFile(editor.document);
    }

    console.log("CORTEX extension activated successfully");
  } catch (error) {
    console.error("Failed to activate CORTEX extension:", error);
    vscode.window.showErrorMessage(
      `CORTEX extension failed to activate: ${error}`
    );
  }
}

/**
 * Extension deactivation - runs when extension unloads.
 */
export function deactivate() {
  console.log("CORTEX extension deactivating...");
  
  if (mcpClient) {
    mcpClient.disconnect();
  }
  
  if (diagnosticsManager) {
    diagnosticsManager.dispose();
  }
  
  console.log("CORTEX extension deactivated");
}
