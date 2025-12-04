/**
 * Test Fixtures - Mock Dashboard Data
 * 
 * Provides consistent test data for unit and integration tests.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 */

export const mockHealthData = {
    health_score: 87.5,
    total_files: 1248,
    total_lines_of_code: 45892,
    test_coverage: 78.3,
    code_quality_score: 85.2,
    security_score: 92.0,
    documentation_coverage: 68.5,
    last_updated: "2024-12-04T10:30:00Z",
    trends: {
        health_score_change: 2.3,
        test_coverage_change: 1.5,
        code_quality_change: -0.8
    }
};

export const mockTechStack = {
    languages: [
        { name: "Python", percentage: 68.5, files: 342, lines: 31420 },
        { name: "JavaScript", percentage: 18.2, files: 156, lines: 8356 },
        { name: "TypeScript", percentage: 8.3, files: 89, lines: 3812 },
        { name: "HTML/CSS", percentage: 5.0, files: 45, lines: 2304 }
    ],
    frameworks: [
        { name: "FastAPI", version: "0.104.1", files: 45 },
        { name: "React", version: "18.2.0", files: 82 },
        { name: "pytest", version: "7.4.3", files: 156 }
    ],
    dependencies: {
        total: 89,
        direct: 34,
        transitive: 55,
        outdated: 8
    }
};

export const mockSecurity = {
    overall_score: 92.0,
    vulnerabilities: {
        critical: 0,
        high: 2,
        medium: 5,
        low: 12,
        info: 24
    },
    last_scan: "2024-12-04T09:15:00Z",
    issues: [
        {
            id: "SEC-001",
            severity: "high",
            title: "Hardcoded API key in config",
            file: "src/config.py",
            line: 45,
            status: "open"
        },
        {
            id: "SEC-002",
            severity: "high",
            title: "SQL injection vulnerability",
            file: "src/database/queries.py",
            line: 128,
            status: "open"
        }
    ],
    compliance: {
        owasp_top_10: 8,
        pci_dss: true,
        gdpr: true
    }
};

export const mockArchitecture = {
    total_modules: 45,
    total_classes: 234,
    total_functions: 1456,
    dependencies: [
        { source: "tier1", target: "tier0", count: 12 },
        { source: "tier2", target: "tier1", count: 18 },
        { source: "tier3", target: "tier2", count: 15 },
        { source: "agents", target: "tier1", count: 25 }
    ],
    complexity: {
        average_cyclomatic: 4.2,
        max_cyclomatic: 18,
        average_cognitive: 6.8,
        max_cognitive: 24
    },
    layers: [
        { name: "Tier 0", modules: 5, files: 23 },
        { name: "Tier 1", modules: 8, files: 45 },
        { name: "Tier 2", modules: 12, files: 67 },
        { name: "Tier 3", modules: 10, files: 52 }
    ]
};

export const mockCodeOrganization = {
    total_directories: 156,
    total_files: 1248,
    file_size_stats: {
        average: 367,
        median: 245,
        largest: 2845,
        smallest: 12
    },
    module_structure: [
        { path: "src/tier0", files: 23, lines: 3456 },
        { path: "src/tier1", files: 45, lines: 8234 },
        { path: "src/tier2", files: 67, lines: 12456 },
        { path: "src/tier3", files: 52, lines: 9876 },
        { path: "src/cortex_agents", files: 89, lines: 15234 }
    ],
    code_metrics: {
        maintainability_index: 72.5,
        duplication_percentage: 3.2,
        comment_ratio: 18.5
    }
};

export const mockTeamMetrics = {
    total_contributors: 12,
    active_contributors: 8,
    total_commits: 2456,
    commits_last_30_days: 234,
    contributors: [
        {
            name: "Asif Hussain",
            commits: 1456,
            additions: 89234,
            deletions: 34567,
            files_changed: 892
        },
        {
            name: "Developer B",
            commits: 456,
            additions: 23456,
            deletions: 12345,
            files_changed: 234
        }
    ],
    activity_timeline: [
        { date: "2024-12-01", commits: 23 },
        { date: "2024-12-02", commits: 34 },
        { date: "2024-12-03", commits: 28 },
        { date: "2024-12-04", commits: 19 }
    ]
};

export const mockVendors = {
    total_vendors: 45,
    by_category: {
        "Cloud Services": 12,
        "Development Tools": 18,
        "Security": 8,
        "Monitoring": 7
    },
    vendors: [
        {
            name: "GitHub",
            category: "Development Tools",
            cost: 0,
            status: "active",
            last_used: "2024-12-04"
        },
        {
            name: "AWS",
            category: "Cloud Services",
            cost: 2450,
            status: "active",
            last_used: "2024-12-04"
        }
    ],
    total_monthly_cost: 8945
};

export const mockMetadata = {
    generated_at: "2024-12-04T10:30:00Z",
    version: "3.2.0",
    source: "mock",
    repository: "CORTEX",
    branch: "CORTEX-3.0"
};

export const mockFullDashboard = {
    metadata: mockMetadata,
    health: mockHealthData,
    tech_stack: mockTechStack,
    security: mockSecurity,
    architecture: mockArchitecture,
    code_organization: mockCodeOrganization,
    team_metrics: mockTeamMetrics,
    vendors: mockVendors
};
