/**
 * Mock Data Fixtures for Dashboard Tests
 * 
 * Comprehensive mock data representing all dashboard data structures.
 */

export const mockOverviewData = {
    project_name: "CORTEX",
    overall_health: {
        score: 92,
        status: "healthy",
        trend: "improving",
        last_scan: "2025-12-06T16:40:00.000000"
    },
    key_metrics: {
        total_files: 994,
        total_loc: 45678,
        test_coverage: 78.5,
        maintainability_index: 85,
        technical_debt_hours: 12.5
    },
    health_categories: [
        {
            name: "code_quality",
            score: 88,
            status: "healthy",
            trend: "improving",
            issues_count: 3,
            details: "3 minor code quality issues"
        },
        {
            name: "security",
            score: 96,
            status: "healthy",
            trend: "stable",
            issues_count: 0,
            details: "No security vulnerabilities"
        }
    ],
    composition: {
        languages: [
            { name: "Python", percentage: 55.2, loc: 25214 },
            { name: "JavaScript", percentage: 30.5, loc: 13932 },
            { name: "HTML", percentage: 10.3, loc: 4705 },
            { name: "CSS", percentage: 4.0, loc: 1827 }
        ]
    },
    critical_issues: []
};

export const mockTechStackData = {
    summary: {
        total_technologies: 45,
        active: 38,
        deprecated: 5,
        evaluation: 2
    },
    frontend: [
        {
            name: "React",
            version: "18.2.0",
            category: "framework",
            status: "active",
            adoption: "high",
            last_updated: "2024-11-15"
        }
    ],
    backend: [
        {
            name: "Flask",
            version: "3.0.0",
            category: "framework",
            status: "active",
            adoption: "high",
            last_updated: "2024-10-20"
        }
    ],
    database: [
        {
            name: "SQLite",
            version: "3.40.0",
            category: "database",
            status: "active",
            adoption: "high"
        }
    ]
};

export const mockSecurityData = {
    summary: {
        total_vulnerabilities: 0,
        critical: 0,
        high: 0,
        medium: 0,
        low: 0
    },
    vulnerabilities: [],
    owasp_compliance: {
        a01_broken_access_control: "compliant",
        a02_cryptographic_failures: "compliant",
        a03_injection: "compliant"
    }
};

export const mockArchitectureData = {
    components: [
        {
            name: "Brain System",
            type: "core",
            description: "4-tier memory architecture",
            health: 95
        }
    ],
    patterns: ["MVC", "Repository Pattern", "Factory Pattern"],
    dependencies: {
        internal: 12,
        external: 23,
        circular: 0
    }
};

export const mockCodeOrgData = {
    complexity: {
        average_complexity: 4.2,
        max_complexity: 15,
        high_complexity_files: 3
    },
    hotspots: [
        {
            file: "src/tier1/working_memory.py",
            complexity: 15,
            changes: 45,
            risk_score: 8.5
        }
    ],
    structure: {
        total_modules: 47,
        avg_lines_per_file: 235,
        duplicated_code_percentage: 2.1
    }
};

export const mockVendorsData = {
    services: [
        {
            name: "GitHub",
            category: "SCM",
            criticality: "high",
            status: "active",
            risk_level: "low"
        }
    ],
    total_services: 8,
    high_risk: 0,
    medium_risk: 1,
    low_risk: 7
};

export const mockExecutiveData = {
    project_name: "CORTEX",
    overall_health: {
        score: 92,
        status: "healthy"
    },
    executive_summary: "AI Assistant with comprehensive memory and TDD workflow",
    key_strengths: [
        "4-tier brain architecture",
        "TDD Mastery automation",
        "Strategic planning capabilities"
    ],
    areas_of_concern: [
        "Documentation coverage below target"
    ],
    recommendations: [
        "Increase documentation coverage to 80%+"
    ]
};

export const mockFullDashboard = {
    overview: mockOverviewData,
    techStack: mockTechStackData,
    security: mockSecurityData,
    architecture: mockArchitectureData,
    codeOrg: mockCodeOrgData,
    vendors: mockVendorsData,
    executive: mockExecutiveData
};

export const mockEmptyData = {
    overview: {
        project_name: "Test",
        overall_health: { score: 0, status: "unknown" },
        key_metrics: {},
        health_categories: [],
        composition: { languages: [] },
        critical_issues: []
    },
    techStack: {
        summary: { total_technologies: 0 },
        frontend: [],
        backend: [],
        database: []
    }
};

export const mockMalformedData = {
    overview: {
        // Missing required fields
        project_name: null,
        overall_health: null
    }
};
