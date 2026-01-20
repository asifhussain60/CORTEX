/**
 * Diagnostics Manager for CORTEX VS Code Extension
 *
 * Manages inline display of governance violations as diagnostics,
 * quick fixes, and file validation.
 */

import * as vscode from "vscode";
import { MCPClient } from "./mcp_client";

interface QuickFixAction {
  title: string;
  edit: vscode.WorkspaceEdit;
}

/**
 * Manages diagnostics display and quick fixes.
 */
export class DiagnosticsManager implements vscode.Disposable {
  private collection: vscode.DiagnosticCollection;
  private mcpClient: MCPClient;

  constructor(mcpClient: MCPClient) {
    this.mcpClient = mcpClient;
    this.collection = vscode.languages.createDiagnosticCollection(
      "cortex"
    );
  }

  /**
   * Validate a file and update diagnostics.
   */
  async validateFile(document: vscode.TextDocument): Promise<void> {
    try {
      const violations = await this.mcpClient.getGovernanceRules(
        document.fileName
      );

      const diagnostics: vscode.Diagnostic[] = violations.map((violation) =>
        this.createDiagnostic(violation, document)
      );

      this.collection.set(document.uri, diagnostics);
    } catch (error) {
      console.error("Failed to validate file:", error);
    }
  }

  /**
   * Refresh all open files.
   */
  async refresh(): Promise<void> {
    for (const editor of vscode.window.visibleTextEditors) {
      await this.validateFile(editor.document);
    }
  }

  /**
   * Create a diagnostic for a violation.
   */
  private createDiagnostic(
    violation: any,
    document: vscode.TextDocument
  ): vscode.Diagnostic {
    const line = Math.max(0, violation.line - 1);
    const column = Math.max(0, violation.column - 1);
    const range = new vscode.Range(
      line,
      column,
      line,
      column + 1
    );

    const severity =
      violation.severity === "error"
        ? vscode.DiagnosticSeverity.Error
        : violation.severity === "warning"
        ? vscode.DiagnosticSeverity.Warning
        : vscode.DiagnosticSeverity.Information;

    const diagnostic = new vscode.Diagnostic(
      range,
      violation.message,
      severity
    );

    diagnostic.code = violation.rule;
    diagnostic.source = "CORTEX";

    // Add quick fix actions
    diagnostic.relatedInformation = [
      new vscode.DiagnosticRelatedInformation(
        new vscode.Location(document.uri, range),
        `Rule: ${violation.rule}`
      ),
    ];

    return diagnostic;
  }

  /**
   * Apply a quick fix.
   */
  async applyQuickFix(): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      return;
    }

    const diagnostics = this.collection.get(editor.document.uri) || [];
    if (diagnostics.length === 0) {
      vscode.window.showInformationMessage(
        "No violations to fix"
      );
      return;
    }

    // Get first violation for demo
    const diagnostic = diagnostics[0];
    const fixId = String(diagnostic.code);

    const success = await this.mcpClient.applyQuickFix(
      editor.document.fileName,
      fixId
    );

    if (success) {
      vscode.window.showInformationMessage(
        "✓ Quick fix applied"
      );
      await this.validateFile(editor.document);
    } else {
      vscode.window.showErrorMessage(
        "✗ Failed to apply quick fix"
      );
    }
  }

  /**
   * Dispose of resources.
   */
  dispose(): void {
    this.collection.dispose();
  }
}
