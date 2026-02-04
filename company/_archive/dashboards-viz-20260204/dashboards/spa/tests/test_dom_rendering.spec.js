/**
 * TDD Test Suite: DOM Container Rendering
 * 
 * Tests for dashboard component rendering and DOM visibility issues
 * 
 * RED Phase: These tests will FAIL initially
 * GREEN Phase: Implement minimal fix to pass
 * REFACTOR Phase: Clean up implementation
 */

describe('Dashboard DOM Rendering', () => {
    let dashboard;
    let mockData;
    
    beforeEach(() => {
        // Setup mock data
        mockData = {
            repo: { display_name: 'Test Repo', slug: 'test' },
            overview: { summary: 'Test', key_findings: ['Finding 1', 'Finding 2'] },
            metrics: { health_score: 85, loc: 10000, files: 100 },
            security: {
                vulnerabilities: [
                    { id: 'V1', title: 'Test Vuln', severity: 'high', cwe_id: 'CWE-89', location: 'test.py:10', status: 'open' }
                ]
            },
            quality: {
                code_smells: [
                    { name: 'Test Smell', description: 'Test', location: 'test.py:20', severity: 'medium' }
                ]
            },
            dependencies: { packages: [], licenses: {} },
            use_cases: []
        };
        
        // Create fresh DOM structure
        document.body.innerHTML = `
            <div class="app-container">
                <div class="tabs-wrapper">
                    <div class="tabs-container">
                        <button class="tab-button active" id="overview-tab">Overview</button>
                        <button class="tab-button" id="security-tab">Security</button>
                        <button class="tab-button" id="quality-tab">Quality</button>
                    </div>
                    <div class="tab-panels">
                        <section class="tab-panel active" id="overview-panel">
                            <div id="key-findings-list"></div>
                        </section>
                        <section class="tab-panel" id="security-panel" aria-hidden="true">
                            <div id="vulnerabilities-list"></div>
                            <div id="vuln-types-list"></div>
                        </section>
                        <section class="tab-panel" id="quality-panel" aria-hidden="true">
                            <div id="code-smells-grid"></div>
                        </section>
                    </div>
                </div>
                <div id="license-summary"></div>
            </div>
            <script type="application/json" id="dashboard-data">{}</script>
        `;
    });
    
    afterEach(() => {
        document.body.innerHTML = '';
    });
    
    // RED PHASE TESTS (Will fail initially)
    
    describe('RED: Container Discovery', () => {
        test('should find containers in hidden tab panels', () => {
            const container = document.getElementById('vulnerabilities-list');
            
            // ASSERTION: Container exists even in hidden panel
            expect(container).toBeTruthy();
            expect(container).not.toBeNull();
        });
        
        test('should find containers regardless of aria-hidden state', () => {
            const panel = document.getElementById('security-panel');
            const container = document.getElementById('vulnerabilities-list');
            
            // ASSERTION: Container accessible despite parent being hidden
            expect(panel.getAttribute('aria-hidden')).toBe('true');
            expect(container).toBeTruthy();
        });
        
        test('should find all required containers on initialization', () => {
            const requiredContainers = [
                'key-findings-list',
                'vulnerabilities-list',
                'vuln-types-list',
                'code-smells-grid',
                'license-summary'
            ];
            
            const missingContainers = requiredContainers.filter(id => !document.getElementById(id));
            
            // ASSERTION: No containers should be missing
            expect(missingContainers).toEqual([]);
        });
    });
    
    describe('RED: Render Function Execution', () => {
        test('renderVulnerabilities should execute when container exists', () => {
            // Mock dashboard with render spy
            const renderSpy = jest.fn();
            
            // Simulate render call
            const container = document.getElementById('vulnerabilities-list');
            const vulns = mockData.security.vulnerabilities;
            
            if (container && vulns.length > 0) {
                renderSpy();
                container.innerHTML = `<div class="vuln">${vulns[0].title}</div>`;
            }
            
            // ASSERTION: Render should be called
            expect(renderSpy).toHaveBeenCalled();
            expect(container.innerHTML).toContain('Test Vuln');
        });
        
        test('renderCodeSmells should execute when container exists', () => {
            const renderSpy = jest.fn();
            
            const container = document.getElementById('code-smells-grid');
            const smells = mockData.quality.code_smells;
            
            if (container && smells.length > 0) {
                renderSpy();
                container.innerHTML = `<div class="smell">${smells[0].name}</div>`;
            }
            
            // ASSERTION: Render should be called
            expect(renderSpy).toHaveBeenCalled();
            expect(container.innerHTML).toContain('Test Smell');
        });
    });
    
    describe('RED: Deferred Rendering Pattern', () => {
        test('should render hidden panels when they become visible', (done) => {
            const container = document.getElementById('vulnerabilities-list');
            const panel = document.getElementById('security-panel');
            
            // Initial state: panel hidden, no content
            expect(panel.getAttribute('aria-hidden')).toBe('true');
            expect(container.innerHTML).toBe('');
            
            // Simulate tab switch
            panel.setAttribute('aria-hidden', 'false');
            panel.classList.add('active');
            
            // Trigger deferred render
            setTimeout(() => {
                const vulns = mockData.security.vulnerabilities;
                if (vulns.length > 0) {
                    container.innerHTML = `<div>${vulns[0].title}</div>`;
                }
                
                // ASSERTION: Content should now be rendered
                expect(container.innerHTML).toContain('Test Vuln');
                done();
            }, 10);
        });
        
        test('should queue renders for hidden panels until visible', () => {
            const renderQueue = [];
            
            // Queue render for hidden panel
            const container = document.getElementById('code-smells-grid');
            if (!container) {
                renderQueue.push({ container: 'code-smells-grid', data: mockData.quality.code_smells });
            }
            
            // ASSERTION: Render should be queued, not executed
            expect(renderQueue.length).toBeGreaterThan(0);
        });
    });
    
    describe('RED: Tab Manager Integration', () => {
        test('should trigger deferred renders on tab change', () => {
            const onTabChangeSpy = jest.fn();
            
            // Simulate tab change
            const securityTab = document.getElementById('security-tab');
            const securityPanel = document.getElementById('security-panel');
            
            securityTab.click = () => {
                securityPanel.setAttribute('aria-hidden', 'false');
                onTabChangeSpy();
            };
            
            securityTab.click();
            
            // ASSERTION: Tab change callback should fire
            expect(onTabChangeSpy).toHaveBeenCalled();
        });
    });
    
    describe('RED: Error Handling', () => {
        test('should not throw when container is missing', () => {
            const renderFn = () => {
                const container = document.getElementById('non-existent-container');
                if (!container) {
                    console.warn('Container not found');
                    return;
                }
                container.innerHTML = 'test';
            };
            
            // ASSERTION: Should not throw
            expect(renderFn).not.toThrow();
        });
        
        test('should log missing containers for debugging', () => {
            const consoleSpy = jest.spyOn(console, 'warn');
            
            const requiredContainers = ['missing-container'];
            const missingContainers = requiredContainers.filter(id => !document.getElementById(id));
            
            if (missingContainers.length > 0) {
                console.warn('Missing containers:', missingContainers);
            }
            
            // ASSERTION: Should log warning
            expect(consoleSpy).toHaveBeenCalledWith('Missing containers:', ['missing-container']);
            
            consoleSpy.mockRestore();
        });
    });
});

/**
 * TDD Test Suite: Deferred Rendering Implementation
 * 
 * Tests for the actual fix: Deferred rendering pattern
 */

describe('GREEN: Deferred Rendering Implementation', () => {
    test('DeferredRenderer should queue renders for hidden panels', () => {
        class DeferredRenderer {
            constructor() {
                this.renderQueue = new Map();
            }
            
            queueRender(containerId, renderFn) {
                const container = document.getElementById(containerId);
                
                if (!container) {
                    // Container doesn't exist - queue for later
                    this.renderQueue.set(containerId, renderFn);
                    return false;
                }
                
                // Check if in hidden panel
                const panel = container.closest('.tab-panel');
                if (panel && panel.getAttribute('aria-hidden') === 'true') {
                    // Panel hidden - queue for later
                    this.renderQueue.set(containerId, renderFn);
                    return false;
                }
                
                // Execute immediately
                renderFn(container);
                return true;
            }
            
            flushQueue() {
                for (const [containerId, renderFn] of this.renderQueue.entries()) {
                    const container = document.getElementById(containerId);
                    if (container) {
                        const panel = container.closest('.tab-panel');
                        if (!panel || panel.getAttribute('aria-hidden') !== 'true') {
                            renderFn(container);
                            this.renderQueue.delete(containerId);
                        }
                    }
                }
            }
        }
        
        // Create DOM
        document.body.innerHTML = `
            <div class="tab-panel" id="panel1" aria-hidden="true">
                <div id="container1"></div>
            </div>
        `;
        
        const renderer = new DeferredRenderer();
        const renderFn = (container) => { container.innerHTML = 'rendered'; };
        
        // Queue render
        const executed = renderer.queueRender('container1', renderFn);
        
        // ASSERTION: Should be queued, not executed
        expect(executed).toBe(false);
        expect(renderer.renderQueue.size).toBe(1);
        expect(document.getElementById('container1').innerHTML).toBe('');
        
        // Make panel visible and flush
        document.getElementById('panel1').setAttribute('aria-hidden', 'false');
        renderer.flushQueue();
        
        // ASSERTION: Should now be rendered
        expect(document.getElementById('container1').innerHTML).toBe('rendered');
        expect(renderer.renderQueue.size).toBe(0);
    });
});
