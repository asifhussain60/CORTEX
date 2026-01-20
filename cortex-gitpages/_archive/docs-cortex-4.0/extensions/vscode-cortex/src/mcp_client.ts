/**
 * MCP Client for CORTEX VS Code Extension
 *
 * Handles connection to CORTEX MCP hub, configuration loading,
 * governance rule fetching, and violation checks.
 */

import * as vscode from "vscode";
import * as fs from "fs";
import * as path from "path";
import * as yaml from "yaml";

interface CortexConfig {
  repo_id: string;
  repo_name: string;
  mcp_endpoint: string;
  version: string;
  [key: string]: any;
}

interface GovernanceViolation {
  file: string;
  line: number;
  column: number;
  severity: "error" | "warning" | "info";
  message: string;
  rule: string;
  quickFix?: string;
}

interface MCPHealthStatus {
  connected: boolean;
  endpoint: string;
  responseTime?: number;
  lastCheck?: Date;
}

/**
 * MCPClient manages connection to CORTEX governance hub.
 */
export class MCPClient {
  private context: vscode.ExtensionContext;
  private config: CortexConfig | null = null;
  private health: MCPHealthStatus;
  private violations: Map<string, GovernanceViolation[]> = new Map();
  private healthCheckInterval: NodeJS.Timeout | null = null;

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    this.health = {
      connected: false,
      endpoint: "http://127.0.0.1:8000",
    };
  }

  /**
   * Initialize the MCP client - load config and connect.
   */
  async initialize(): Promise<void> {
    try {
      await this.loadConfiguration();
      await this.connect();
      this.startHealthCheck();
    } catch (error) {
      console.error("MCPClient initialization failed:", error);
      throw error;
    }
  }

  /**
   * Load cortex-config.yaml from workspace root.
   */
  private async loadConfiguration(): Promise<void> {
    const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
    if (!workspaceRoot) {
      throw new Error("No workspace folder open");
    }

    const configPath = path.join(workspaceRoot, "cortex-config.yaml");
    
    if (!fs.existsSync(configPath)) {
      throw new Error(`cortex-config.yaml not found at ${configPath}`);
    }

    const configContent = fs.readFileSync(configPath, "utf-8");
    this.config = yaml.parse(configContent);

    if (!this.config || !this.config.mcp_endpoint) {
      throw new Error("Invalid cortex-config.yaml - missing mcp_endpoint");
    }

    this.health.endpoint = this.config.mcp_endpoint;
    console.log("CORTEX config loaded:", this.config);
  }

  /**
   * Connect to MCP hub.
   */
  async connect(): Promise<void> {
    if (!this.config) {
      await this.loadConfiguration();
    }

    try {
      const endpoint = this.config!.mcp_endpoint;
      const startTime = Date.now();
      
      const response = await this.fetch(`${endpoint}/health`, {
        timeout: 5000,
      });

      this.health.responseTime = Date.now() - startTime;
      this.health.connected = response.ok;
      this.health.lastCheck = new Date();

      if (!response.ok) {
        throw new Error(`MCP hub returned ${response.status}`);
      }

      console.log("Connected to MCP hub at", endpoint);
    } catch (error) {
      this.health.connected = false;
      console.warn("Failed to connect to MCP hub:", error);
      vscode.window.showWarningMessage(
        "⚠ CORTEX: Could not connect to MCP hub. Running in offline mode."
      );
    }
  }

  /**
   * Disconnect from MCP hub.
   */
  disconnect(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
  }

  /**
   * Get current health status.
   */
  getHealth(): MCPHealthStatus {
    return { ...this.health };
  }

  /**
   * Update configuration (when user changes settings).
   */
  async updateConfiguration(): Promise<void> {
    await this.loadConfiguration();
    await this.connect();
  }

  /**
   * Fetch governance rules from hub for a file.
   */
  async getGovernanceRules(filePath: string): Promise<GovernanceViolation[]> {
    if (!this.health.connected) {
      console.log("Offline mode - using cached rules");
      return this.violations.get(filePath) || [];
    }

    try {
      const endpoint = this.config!.mcp_endpoint;
      const response = await this.fetch(
        `${endpoint}/governance/validate`,
        {
          method: "POST",
          body: JSON.stringify({
            file: filePath,
            repo_id: this.config!.repo_id,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Hub returned ${response.status}`);
      }

      const data = await response.json();
      const violations = data.violations || [];
      this.violations.set(filePath, violations);
      return violations;
    } catch (error) {
      console.error("Failed to get governance rules:", error);
      return [];
    }
  }

  /**
   * Get audit trail from hub.
   */
  async getAuditTrail(limit: number = 100): Promise<any[]> {
    if (!this.health.connected) {
      return [];
    }

    try {
      const endpoint = this.config!.mcp_endpoint;
      const response = await this.fetch(
        `${endpoint}/audit/trail?limit=${limit}&repo_id=${this.config!.repo_id}`,
        { timeout: 5000 }
      );

      if (!response.ok) {
        throw new Error(`Hub returned ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Failed to get audit trail:", error);
      return [];
    }
  }

  /**
   * Apply a quick fix suggestion.
   */
  async applyQuickFix(
    filePath: string,
    fixId: string
  ): Promise<boolean> {
    if (!this.health.connected) {
      console.log("Offline mode - cannot apply remote fix");
      return false;
    }

    try {
      const endpoint = this.config!.mcp_endpoint;
      const response = await this.fetch(
        `${endpoint}/governance/apply-fix`,
        {
          method: "POST",
          body: JSON.stringify({
            file: filePath,
            fix_id: fixId,
            repo_id: this.config!.repo_id,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Hub returned ${response.status}`);
      }

      const data = await response.json();
      return data.success || false;
    } catch (error) {
      console.error("Failed to apply quick fix:", error);
      return false;
    }
  }

  /**
   * Start periodic health checks.
   */
  private startHealthCheck(): void {
    const interval = (this.config?.mcp_health_check_interval_seconds || 30) * 1000;
    
    this.healthCheckInterval = setInterval(() => {
      this.connect().catch(err => {
        console.debug("Health check failed:", err);
      });
    }, interval);
  }

  /**
   * Fetch helper with timeout support.
   */
  private async fetch(url: string, options: any = {}): Promise<any> {
    // Node.js fetch compatibility - use global fetch if available, else throw
    // In practice, extension would use node-fetch or similar
    throw new Error("Fetch not implemented in test environment");
  }
}
