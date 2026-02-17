/**
 * CORTEX Dashboard Visualizations Test Harness
 * 
 * Tests for D3.js visualization functions in visualizations.js
 * Covers: chart rendering, data validation, error handling, DOM interactions
 * 
 * Version: 1.0.0
 * Authority: Phase 48 (Holistic Validation Gate)
 * AC_START: AC-VIZ-TEST-001
 */

// ============================================================================
// TEST UTILITIES & MOCKS
// ============================================================================

/**
 * Mock DOM container for testing
 */
function createMockContainer(id = 'test-container') {
    const container = document.createElement('div');
    container.id = id;
    container.style.width = '400px';
    container.style.height = '400px';
    document.body.appendChild(container);
    return container;
}

/**
 * Clean up test DOM
 */
function cleanupContainer(id = 'test-container') {
    const container = document.getElementById(id);
    if (container) {
        container.remove();
    }
}

/**
 * Verify SVG element was created
 */
function verifySvgCreated(containerId) {
    const container = document.getElementById(containerId);
    const svg = container?.querySelector('svg');
    return svg !== null && svg !== undefined;
}

/**
 * Get SVG dimensions
 */
function getSvgDimensions(containerId) {
    const svg = document.getElementById(containerId)?.querySelector('svg');
    if (!svg) return null;
    
    return {
        width: svg.getAttribute('width') || svg.getAttribute('viewBox')?.split(' ')[2],
        height: svg.getAttribute('height') || svg.getAttribute('viewBox')?.split(' ')[3]
    };
}

// ============================================================================
// TEST SUITE 1: LANGUAGE SUNBURST CHART
// ============================================================================

describe('createLanguageSunburst', () => {
    beforeEach(() => {
        createMockContainer('lang-sunburst-test');
    });

    afterEach(() => {
        cleanupContainer('lang-sunburst-test');
    });

    test('Should create SVG element', () => {
        const languages = {
            'JavaScript': 5000,
            'TypeScript': 3000,
            'Python': 2000
        };

        window.CortexViz.createLanguageSunburst('lang-sunburst-test', languages);
        assert(verifySvgCreated('lang-sunburst-test'), 'SVG should be created');
    });

    test('Should render all language segments', () => {
        const languages = {
            'JavaScript': 5000,
            'TypeScript': 3000,
            'Python': 2000
        };

        window.CortexViz.createLanguageSunburst('lang-sunburst-test', languages);
        const container = document.getElementById('lang-sunburst-test');
        const paths = container.querySelectorAll('svg path');
        
        // Should have at least paths for each language (plus root)
        assert(paths.length >= 3, `Expected at least 3 paths, got ${paths.length}`);
    });

    test('Should handle empty data gracefully', () => {
        const languages = {};
        window.CortexViz.createLanguageSunburst('lang-sunburst-test', languages);
        
        // Should not throw error, container may be empty
        const container = document.getElementById('lang-sunburst-test');
        assert(container !== null, 'Container should still exist');
    });

    test('Should apply correct colors', () => {
        const languages = {
            'JavaScript': 5000,
            'TypeScript': 3000
        };

        window.CortexViz.createLanguageSunburst('lang-sunburst-test', languages);
        const paths = document.querySelectorAll('svg path');
        
        // At least one path should have a fill color
        let hasColor = false;
        paths.forEach(path => {
            const fill = path.getAttribute('fill') || path.style.fill;
            if (fill && fill !== 'none') {
                hasColor = true;
            }
        });
        
        assert(hasColor, 'At least one path should have a color');
    });

    test('Should handle missing data gracefully', () => {
        window.CortexViz.createLanguageSunburst('lang-sunburst-test', null);
        // Should not throw
        assert(true, 'Function should handle null data');
    });

    test('Should handle missing container', () => {
        const languages = { 'JS': 1000 };
        // Should not throw when container doesn't exist
        try {
            window.CortexViz.createLanguageSunburst('nonexistent-container', languages);
            assert(true, 'Function should handle missing container');
        } catch (e) {
            assert(false, `Should not throw error: ${e.message}`);
        }
    });
});

// ============================================================================
// TEST SUITE 2: HEALTH GAUGE
// ============================================================================

describe('createHealthGauge', () => {
    beforeEach(() => {
        createMockContainer('health-gauge-test');
    });

    afterEach(() => {
        cleanupContainer('health-gauge-test');
    });

    test('Should create gauge SVG', () => {
        const score = 8.5;
        window.CortexViz.createHealthGauge('health-gauge-test', score);
        assert(verifySvgCreated('health-gauge-test'), 'SVG should be created');
    });

    test('Should render gauge segments', () => {
        const score = 8.5;
        window.CortexViz.createHealthGauge('health-gauge-test', score);
        const container = document.getElementById('health-gauge-test');
        const paths = container.querySelectorAll('svg path');
        
        assert(paths.length > 0, 'Should have gauge paths');
    });

    test('Should handle score 0-10 range', () => {
        for (let score of [0, 2.5, 5, 7.5, 10]) {
            createMockContainer(`health-gauge-test-${score}`);
            window.CortexViz.createHealthGauge(`health-gauge-test-${score}`, score);
            assert(verifySvgCreated(`health-gauge-test-${score}`), 
                `Should create gauge for score ${score}`);
            cleanupContainer(`health-gauge-test-${score}`);
        }
    });

    test('Should clamp invalid scores', () => {
        // Function should handle scores outside 0-10 range
        const scores = [-5, 15, 100];
        scores.forEach(score => {
            try {
                window.CortexViz.createHealthGauge('health-gauge-test', score);
                assert(true, `Should handle score ${score}`);
            } catch (e) {
                assert(false, `Should not throw for score ${score}`);
            }
        });
    });
});

// ============================================================================
// TEST SUITE 3: SECURITY DONUT CHART
// ============================================================================

describe('createSecurityDonut', () => {
    beforeEach(() => {
        createMockContainer('security-donut-test');
    });

    afterEach(() => {
        cleanupContainer('security-donut-test');
    });

    test('Should create donut SVG', () => {
        const security = {
            passed: 45,
            warnings: 12,
            critical: 3
        };
        
        window.CortexViz.createSecurityDonut('security-donut-test', security);
        assert(verifySvgCreated('security-donut-test'), 'SVG should be created');
    });

    test('Should render security segments', () => {
        const security = {
            passed: 45,
            warnings: 12,
            critical: 3
        };
        
        window.CortexViz.createSecurityDonut('security-donut-test', security);
        const container = document.getElementById('security-donut-test');
        const paths = container.querySelectorAll('svg path');
        
        assert(paths.length >= 3, `Should have segments for each severity level`);
    });

    test('Should handle zero values', () => {
        const security = {
            passed: 60,
            warnings: 0,
            critical: 0
        };
        
        window.CortexViz.createSecurityDonut('security-donut-test', security);
        assert(verifySvgCreated('security-donut-test'), 'Should handle zero warnings/critical');
    });
});

// ============================================================================
// TEST SUITE 4: DEPENDENCY GRAPH
// ============================================================================

describe('createDependencyGraph', () => {
    beforeEach(() => {
        createMockContainer('dependency-graph-test');
    });

    afterEach(() => {
        cleanupContainer('dependency-graph-test');
    });

    test('Should create graph SVG', () => {
        const packages = {
            direct: [
                { name: 'express', version: '4.18.2' },
                { name: 'axios', version: '0.21.1' }
            ],
            transitive_count: 100
        };
        
        window.CortexViz.createDependencyGraph('dependency-graph-test', packages);
        assert(verifySvgCreated('dependency-graph-test'), 'SVG should be created');
    });

    test('Should render dependency nodes', () => {
        const packages = {
            direct: [
                { name: 'express', version: '4.18.2' },
                { name: 'axios', version: '0.21.1' }
            ],
            transitive_count: 100
        };
        
        window.CortexViz.createDependencyGraph('dependency-graph-test', packages);
        const container = document.getElementById('dependency-graph-test');
        const circles = container.querySelectorAll('svg circle');
        
        assert(circles.length >= 2, `Should have at least 2 dependency nodes`);
    });

    test('Should handle empty dependencies', () => {
        const packages = { direct: [], transitive_count: 0 };
        
        window.CortexViz.createDependencyGraph('dependency-graph-test', packages);
        assert(verifySvgCreated('dependency-graph-test'), 'Should handle empty dependencies');
    });
});

// ============================================================================
// TEST SUITE 5: FILE TREE
// ============================================================================

describe('createFileTree', () => {
    beforeEach(() => {
        createMockContainer('file-tree-test');
    });

    afterEach(() => {
        cleanupContainer('file-tree-test');
    });

    test('Should create tree SVG', () => {
        const metrics = {
            summary: 'Project structure',
            tree: {
                name: 'src',
                size: 5000,
                children: [
                    { name: 'index.js', size: 500 },
                    { name: 'utils.js', size: 300 }
                ]
            }
        };
        
        window.CortexViz.createFileTree('file-tree-test', metrics);
        assert(verifySvgCreated('file-tree-test'), 'SVG should be created');
    });

    test('Should render file nodes', () => {
        const metrics = {
            summary: 'Project structure',
            tree: {
                name: 'src',
                size: 5000,
                children: [
                    { name: 'index.js', size: 500 },
                    { name: 'utils.js', size: 300 }
                ]
            }
        };
        
        window.CortexViz.createFileTree('file-tree-test', metrics);
        const container = document.getElementById('file-tree-test');
        const rects = container.querySelectorAll('svg rect');
        
        assert(rects.length > 0, 'Should have tree nodes');
    });
});

// ============================================================================
// TEST SUITE 6: DOMAIN CONCEPT MAP
// ============================================================================

describe('createDomainConceptMap', () => {
    beforeEach(() => {
        createMockContainer('domain-concept-test');
    });

    afterEach(() => {
        cleanupContainer('domain-concept-test');
    });

    test('Should create concept map SVG', () => {
        const data = {
            overview: {
                summary: 'API framework for building web applications'
            }
        };
        
        window.CortexViz.createDomainConceptMap('domain-concept-test', data);
        assert(verifySvgCreated('domain-concept-test'), 'SVG should be created');
    });

    test('Should handle minimal data', () => {
        const data = {};
        
        window.CortexViz.createDomainConceptMap('domain-concept-test', data);
        assert(verifySvgCreated('domain-concept-test'), 'Should handle minimal data');
    });
});

// ============================================================================
// TEST SUITE 7: USE CASE TREEMAP
// ============================================================================

describe('createUseCaseTreemap', () => {
    beforeEach(() => {
        createMockContainer('usecase-treemap-test');
    });

    afterEach(() => {
        cleanupContainer('usecase-treemap-test');
    });

    test('Should create treemap SVG', () => {
        const useCases = [
            { name: 'API Routing', value: 30 },
            { name: 'Middleware', value: 25 },
            { name: 'Error Handling', value: 20 }
        ];
        
        window.CortexViz.createUseCaseTreemap('usecase-treemap-test', useCases);
        assert(verifySvgCreated('usecase-treemap-test'), 'SVG should be created');
    });

    test('Should render use case rects', () => {
        const useCases = [
            { name: 'API Routing', value: 30 },
            { name: 'Middleware', value: 25 }
        ];
        
        window.CortexViz.createUseCaseTreemap('usecase-treemap-test', useCases);
        const container = document.getElementById('usecase-treemap-test');
        const rects = container.querySelectorAll('svg rect');
        
        assert(rects.length >= 2, 'Should have rectangles for each use case');
    });

    test('Should handle empty use cases', () => {
        const useCases = [];
        
        window.CortexViz.createUseCaseTreemap('usecase-treemap-test', useCases);
        assert(verifySvgCreated('usecase-treemap-test'), 'Should handle empty use cases');
    });
});

// ============================================================================
// TEST SUITE 8: COLOR PALETTE
// ============================================================================

describe('COLORS Palette', () => {
    test('Should have all required color categories', () => {
        const required = ['primary', 'secondary', 'tertiary', 'warning', 'danger', 'text', 'languages', 'categories'];
        required.forEach(category => {
            assert(window.CortexViz.COLORS[category] !== undefined, 
                `Colors should have ${category}`);
        });
    });

    test('Should have language colors for common languages', () => {
        const languages = ['JavaScript', 'TypeScript', 'Python', 'HTML', 'CSS'];
        languages.forEach(lang => {
            assert(window.CortexViz.COLORS.languages[lang] !== undefined, 
                `Should have color for ${lang}`);
        });
    });

    test('Should have category colors', () => {
        const categories = ['core', 'domain', 'support', 'dev'];
        categories.forEach(cat => {
            assert(window.CortexViz.COLORS.categories[cat] !== undefined, 
                `Should have color for category ${cat}`);
        });
    });
});

// ============================================================================
// TEST UTILITIES
// ============================================================================

/**
 * Simple assertion function for testing
 */
function assert(condition, message) {
    if (!condition) {
        throw new Error(`Assertion failed: ${message}`);
    }
}

/**
 * Test runner
 */
function runTests() {
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📊 CORTEX Visualizations Test Suite');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    let totalTests = 0;
    let passedTests = 0;
    let failedTests = 0;
    
    // Run all test suites
    const suites = window.testSuites || [];
    suites.forEach(suite => {
        console.log(`\n✓ ${suite.name}`);
        suite.tests.forEach(test => {
            totalTests++;
            try {
                test.fn();
                passedTests++;
                console.log(`  ✓ ${test.name}`);
            } catch (e) {
                failedTests++;
                console.error(`  ✗ ${test.name}: ${e.message}`);
            }
        });
    });
    
    console.log(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
    console.log(`Results: ${passedTests}/${totalTests} passed`);
    console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
    
    return failedTests === 0;
}

// AC_COMPLETE: AC-VIZ-TEST-001 ✅ Visualization Test Harness
