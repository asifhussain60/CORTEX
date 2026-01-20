/**
 * Health Status Provider for CORTEX VS Code Extension
 *
 * Displays MCP hub connection status in sidebar panel.
 */

import * as vscode from "vscode";
import { MCPClient } from "./mcp_client";

/**
 * Tree data provider for health status sidebar.
 */
export class HealthStatusProvider
  implements vscode.TreeDataProvider<HealthStatusNode> {
  private mcpClient: MCPClient;
  private _onDidChangeTreeData = new vscode.EventEmitter<
    HealthStatusNode | undefined | null | void
  >();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  constructor(mcpClient: MCPClient) {
    this.mcpClient = mcpClient;
    
    // Refresh health status periodically
    setInterval(() => {
      this._onDidChangeTreeData.fire();
    }, 5000);
  }

  /**
   * Refresh health status.
   */
  async refresh(): Promise<void> {
    this._onDidChangeTreeData.fire();
  }

  /**
   * Get tree item for status.
   */
  getTreeItem(element: HealthStatusNode): vscode.TreeItem {
    const item = new vscode.TreeItem(element.label);
    item.description = element.description;
    item.collapsibleState = vscode.TreeItemCollapsibleState.None;
    
    // Set icon based on status
    if (element.status === "connected") {
      item.iconPath = new vscode.ThemeIcon("circle-filled", new vscode.ThemeColor("testing.runAction"));
    } else if (element.status === "disconnected") {
      item.iconPath = new vscode.ThemeIcon("circle-filled", new vscode.ThemeColor("errorForeground"));
    } else {
      item.iconPath = new vscode.ThemeIcon("circle-filled", new vscode.ThemeColor("activityBar.inactiveForeground"));
    }
    
    return item;
  }

  /**
   * Get children for status tree.
   */
  getChildren(element?: HealthStatusNode): HealthStatusNode[] {
    if (!element) {
      const health = this.mcpClient.getHealth();
      
      return [
        new HealthStatusNode(
          "Connection Status",
          health.connected ? "● Connected" : "● Disconnected",
          health.connected ? "connected" : "disconnected"
        ),
        new HealthStatusNode(
          "Hub Endpoint",
          health.endpoint,
          "info"
        ),
        new HealthStatusNode(
          "Response Time",
          health.responseTime ? `${health.responseTime}ms` : "N/A",
          "info"
        ),
        new HealthStatusNode(
          "Last Check",
          health.lastCheck
            ? new Date(health.lastCheck).toLocaleTimeString()
            : "Never",
          "info"
        ),
      ];
    }

    return [];
  }
}

/**
 * Health status tree node.
 */
class HealthStatusNode {
  constructor(
    public label: string,
    public description: string,
    public status: "connected" | "disconnected" | "info"
  ) {}
}
