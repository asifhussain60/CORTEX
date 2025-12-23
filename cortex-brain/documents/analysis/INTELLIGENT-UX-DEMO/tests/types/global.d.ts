/**
 * Global type definitions for dashboard data
 * Eliminates "Property 'dashboardData' does not exist on type 'Window'" errors
 */

declare global {
  interface Window {
    dashboardData: {
      metadata: {
        projectName: string;
        timestamp: string;
        fileCount: number;
        lineCount: number;
        language: string;
        version: string;
        analysisVersion: string;
        duration: number;
      };
      scores: {
        overall: number;
        quality: number;
        performance: number;
        security: number;
        architecture: number;
        maintainability: number;
        testCoverage: number;
      };
      summary: {
        text: string;
        quickWins: string[];
        criticalIssues: string[];
      };
      architecture: {
        components: Array<{
          id: string;
          name: string;
          size: number;
          color: string;
          description: string;
          complexity?: number;
          files?: number;
        }>;
        relationships: Array<{
          source: string;
          target: string;
        }>;
        issues: Array<{
          type: string;
          file: string;
          complexity?: number;
          severity?: string;
          recommendation?: string;
        }>;
        metrics?: {
          modularity: number;
          coupling: number;
          cohesion: number;
          abstractionLevel: number;
        };
      };
      quality: {
        codeSmells: Array<{
          file: string;
          type: string;
          count: number;
        }>;
        complexity: Array<{
          name: string;
          complexity: number;
          lines: number;
          file?: string;
        }>;
        maintainability: Array<{
          metric: string;
          value: number;
          target: number;
          unit?: string;
        }>;
        trends?: {
          qualityScoreChange: number;
          complexityTrend: string;
          testCoverageDelta: number;
        };
      };
      roadmap: {
        tasks: Array<{
          id: number;
          name: string;
          start: number;
          duration: number;
          priority: string;
          impact: number;
          effort: number;
          category?: string;
          assignee?: string | null;
        }>;
        dependencies: Array<{
          source: number;
          target: number;
        }>;
        milestones?: Array<{
          name: string;
          day: number;
        }>;
      };
      performance: {
        bottlenecks: Array<{
          function: string;
          time: number;
          calls: number;
          category?: string;
        }>;
        dataFlow: Array<{
          source: string;
          target: string;
          value: number;
        }>;
        metrics?: {
          avgResponseTime: number;
          p95ResponseTime: number;
          p99ResponseTime: number;
          errorRate: number;
        };
      };
      security: {
        vulnerabilities: {
          critical: number;
          high: number;
          medium: number;
          low: number;
        };
        issues: Array<{
          id?: string;
          type: string;
          severity: string;
          file: string;
          line: number;
          description?: string;
          recommendation?: string;
        }>;
        owasp: Array<{
          category: string;
          score: number;
          findings?: number;
        }>;
        riskScore: number;
        complianceStatus?: {
          OWASP_ASVS: string;
          CWE_Top25: string;
          GDPR: string;
          SOC2: string;
        };
      };
      discoveries?: Array<{
        id?: string;
        type: string;
        title: string;
        description: string;
        impact: string;
        effort: string;
        estimatedTime?: string;
        files?: string[];
      }>;
      testCoverage?: {
        overall: number;
        byModule: Record<string, number>;
        untested: string[];
      };
    } | null;
  }
}

export {};
