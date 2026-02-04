/**
 * CORTEX Lens - Data Adapter
 * Loads and manages dashboard data from JSON file or inline script
 */

class DataAdapter {
    constructor() {
        this.data = null;
        this.loaded = false;
    }

    /**
     * Load data from inline script or external JSON
     */
    async load() {
        try {
            // Try to load from inline script first
            const dataScript = document.getElementById('dashboard-data');
            if (dataScript) {
                this.data = JSON.parse(dataScript.textContent);
                this.loaded = true;
                console.log('✅ Data loaded from inline script');
                return this.data;
            }

            // Try to load from external JSON file
            const response = await fetch('data/dashboard-data.json');
            if (response.ok) {
                this.data = await response.json();
                this.loaded = true;
                console.log('✅ Data loaded from external file');
                return this.data;
            }

            // Fallback to mock data
            this.data = this.getMockData();
            this.loaded = true;
            console.warn('⚠️ Using mock data');
            return this.data;
        } catch (error) {
            console.error('❌ Error loading data:', error);
            this.data = this.getMockData();
            this.loaded = true;
            return this.data;
        }
    }

    /**
     * Get mock data for demonstration
     */
    getMockData() {
        return {
            repo: {
                display_name: 'CORTEX',
                primary_language: 'Python',
                version: '1.0.0',
                last_analyzed_at: new Date().toISOString()
            },
            metrics: {
                health_score: 85,
                total_files: 450,
                lines_of_code: 45000,
                test_coverage: 78
            },
            executive: {
                health_status: 'Good',
                security_posture: 'Strong',
                tech_debt_hours: 120,
                test_pass_rate: 95,
                risk_summary: 'Low to moderate risk. Primary concerns are in dependency management and technical debt reduction.',
                recommendations: [
                    'Upgrade outdated dependencies (12 packages)',
                    'Reduce technical debt in core modules',
                    'Improve test coverage in API layer'
                ]
            },
            overview: {
                business_summary: 'CORTEX is an intelligent orchestration platform with strong architecture and good maintainability. The codebase demonstrates solid engineering practices with room for optimization in dependency management and test coverage.',
                health_metrics: {
                    maintainability: 85,
                    reliability: 90,
                    security: 80,
                    performance: 75,
                    testability: 78
                }
            },
            use_cases: [
                {
                    id: 'UC-001',
                    title: 'Code Analysis',
                    description: 'Analyze repository structure and quality metrics',
                    category: 'Analysis',
                    impacted_modules: ['cortex.brain', 'cortex.lens'],
                    priority: 'High'
                },
                {
                    id: 'UC-002',
                    title: 'Dependency Management',
                    description: 'Track and manage external dependencies',
                    category: 'Management',
                    impacted_modules: ['cortex.orchestrators'],
                    priority: 'Medium'
                }
            ],
            quality: {
                complexity_score: 7.5,
                duplication: 5.2,
                tech_debt_hours: 120,
                code_smells: 45
            },
            security: {
                total_count: 8,
                vulnerabilities: [
                    { severity: 'high', count: 2 },
                    { severity: 'medium', count: 4 },
                    { severity: 'low', count: 2 }
                ]
            }
        };
    }

    /**
     * Get data by path (e.g., 'metrics.health_score')
     */
    get(path, defaultValue = null) {
        if (!this.loaded || !this.data) {
            return defaultValue;
        }

        const keys = path.split('.');
        let value = this.data;

        for (const key of keys) {
            if (value && typeof value === 'object' && key in value) {
                value = value[key];
            } else {
                return defaultValue;
            }
        }

        return value;
    }

    /**
     * Check if data is loaded
     */
    isLoaded() {
        return this.loaded;
    }
}

// Global instance
const dataAdapter = new DataAdapter();
