/**
 * Audit Trail Provider for CORTEX VS Code Extension
 *
 * Provides tree view of audit trail entries in sidebar panel.
 */

import * as vscode from "vscode";
import { MCPClient } from "./mcp_client";

interface AuditEntry {
  id: string;
  timestamp: string;
  operation: string;
  actor: string;
  repo_id: string;
  details: string;
}

/**
 * Tree data provider for audit trail sidebar.
 */
export class AuditTrailProvider
  implements vscode.TreeDataProvider<AuditEntryNode> {
  private mcpClient: MCPClient;
  private entries: AuditEntry[] = [];
  private _onDidChangeTreeData = new vscode.EventEmitter<
    AuditEntryNode | undefined | null | void
  >();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  constructor(mcpClient: MCPClient) {
    this.mcpClient = mcpClient;
    this.loadAuditTrail();
  }

  /**
   * Load audit trail from hub.
   */
  async loadAuditTrail(): Promise<void> {
    this.entries = await this.mcpClient.getAuditTrail(100);
    this._onDidChangeTreeData.fire();
  }

  /**
   * Refresh audit trail.
   */
  async refresh(): Promise<void> {
    await this.loadAuditTrail();
  }

  /**
   * Get tree item for entry.
   */
  getTreeItem(element: AuditEntryNode): vscode.TreeItem {
    const item = new vscode.TreeItem(element.label);
    item.description = element.description;
    item.collapsibleState = vscode.TreeItemCollapsibleState.None;
    item.iconPath = new vscode.ThemeIcon("clock");
    return item;
  }

  /**
   * Get children for entry.
   */
  getChildren(element?: AuditEntryNode): AuditEntryNode[] {
    if (!element) {
      // Root - show audit entries sorted by timestamp (newest first)
      return this.entries
        .sort(
          (a, b) =>
            new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        )
        .map(
          (entry) =>
            new AuditEntryNode(
              `${entry.operation} - ${entry.actor}`,
              `${entry.timestamp} (${entry.repo_id})`
            )
        );
    }

    return [];
  }
}

/**
 * Audit entry tree node.
 */
class AuditEntryNode {
  constructor(
    public label: string,
    public description: string
  ) {}
}
