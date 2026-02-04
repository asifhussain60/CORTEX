/**
 * CORTEX Debug Capture
 * =====================
 * 
 * Playwright-based console log capture that collects all CORTEX_DEBUG markers
 * during browser execution and saves them for analysis.
 * 
 * Features:
 * - Captures all console.log/warn/error messages
 * - Filters CORTEX_DEBUG markers from noise
 * - Records timestamps and execution order
 * - Supports interactive tab navigation
 * - Generates detailed capture report
 * 
 * @author CORTEX
 * @version 1.0.0
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const MARKER_PREFIX = 'CORTEX_DEBUG_';

/**
 * Third-party noise patterns to filter
 */
const NOISE_PATTERNS = [
    /grammarly/i,
    /wax/i,
    /contentisolated/i,
    /extension/i,
    /devtools/i,
    /chrome-extension/i,
    /moz-extension/i,
    /localhost:\d+\/favicon/i
];

/**
 * Log entry structure
 */
class LogEntry {
    constructor(type, text, timestamp, location = null) {
        this.type = type;           // 'log', 'warn', 'error', 'info', 'debug'
        this.text = text;
        this.timestamp = timestamp;
        this.location = location;   // Source file and line if available
        this.isCortexMarker = text.includes(MARKER_PREFIX);
        this.parsedMarker = this.isCortexMarker ? this.parseMarker(text) : null;
    }
    
    parseMarker(text) {
        // [CORTEX_DEBUG_abc123:FUNC:app.js:97] ENTER init
        const match = text.match(/\[CORTEX_DEBUG_(\w+):(\w+):([^:]+):(\d+)\]\s*(.*)/);
        if (match) {
            return {
                sessionId: match[1],
                phase: match[2],
                file: match[3],
                line: parseInt(match[4]),
                message: match[5]
            };
        }
        return null;
    }
    
    isNoise() {
        return NOISE_PATTERNS.some(pattern => pattern.test(this.text));
    }
}

/**
 * Capture session manager
 */
class CaptureSession {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.startTime = null;
        this.endTime = null;
        this.logs = [];
        this.cortexLogs = [];
        this.errors = [];
        this.warnings = [];
        this.tabsVisited = [];
        this.networkRequests = [];
    }
    
    start() {
        this.startTime = Date.now();
    }
    
    end() {
        this.endTime = Date.now();
    }
    
    addLog(entry) {
        this.logs.push(entry);
        
        if (entry.isCortexMarker) {
            this.cortexLogs.push(entry);
        }
        
        if (entry.type === 'error' && !entry.isNoise()) {
            this.errors.push(entry);
        }
        
        if (entry.type === 'warn' && !entry.isNoise()) {
            this.warnings.push(entry);
        }
    }
    
    addTabVisit(tabName) {
        this.tabsVisited.push({
            tab: tabName,
            timestamp: Date.now()
        });
    }
    
    addNetworkRequest(url, status, duration) {
        this.networkRequests.push({
            url,
            status,
            duration,
            timestamp: Date.now()
        });
    }
    
    getDuration() {
        return this.endTime - this.startTime;
    }
    
    getSummary() {
        return {
            sessionId: this.sessionId,
            duration: this.getDuration(),
            totalLogs: this.logs.length,
            cortexLogs: this.cortexLogs.length,
            errors: this.errors.length,
            warnings: this.warnings.length,
            tabsVisited: this.tabsVisited.length,
            networkRequests: this.networkRequests.length
        };
    }
    
    toJSON() {
        return {
            sessionId: this.sessionId,
            startTime: new Date(this.startTime).toISOString(),
            endTime: new Date(this.endTime).toISOString(),
            duration: this.getDuration(),
            summary: this.getSummary(),
            cortexLogs: this.cortexLogs.map(l => ({
                type: l.type,
                text: l.text,
                timestamp: l.timestamp,
                parsedMarker: l.parsedMarker
            })),
            errors: this.errors.map(l => ({
                type: l.type,
                text: l.text,
                timestamp: l.timestamp
            })),
            warnings: this.warnings.map(l => ({
                type: l.type,
                text: l.text,
                timestamp: l.timestamp
            })),
            tabsVisited: this.tabsVisited,
            networkRequests: this.networkRequests.slice(0, 50) // Limit to avoid huge files
        };
    }
}

/**
 * Main capture function
 */
export async function capture(url, options = {}) {
    const {
        sessionId,
        outputDir = '.cortex-debug',
        headless = true,
        timeout = 60000,
        clickTabs = true,
        waitForData = true
    } = options;
    
    // Load session info if available
    let session;
    const sessionPath = path.join(outputDir, 'session.json');
    if (fs.existsSync(sessionPath)) {
        const savedSession = JSON.parse(fs.readFileSync(sessionPath, 'utf-8'));
        session = new CaptureSession(savedSession.sessionId);
    } else {
        session = new CaptureSession(sessionId || 'unknown');
    }
    
    console.log(`\n📸 CORTEX Debug Capture`);
    console.log(`   Session: ${session.sessionId}`);
    console.log(`   URL: ${url}`);
    console.log(`   Headless: ${headless}`);
    console.log(`   Tab Navigation: ${clickTabs}\n`);
    
    const browser = await chromium.launch({ headless });
    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 }
    });
    const page = await context.newPage();
    
    session.start();
    
    // Capture console messages
    page.on('console', msg => {
        const entry = new LogEntry(
            msg.type(),
            msg.text(),
            Date.now(),
            msg.location()
        );
        
        if (!entry.isNoise()) {
            session.addLog(entry);
            
            // Real-time output for CORTEX markers
            if (entry.isCortexMarker) {
                const marker = entry.parsedMarker;
                if (marker) {
                    console.log(`   📍 [${marker.phase}] ${marker.file}:${marker.line} - ${marker.message}`);
                }
            } else if (entry.type === 'error') {
                console.log(`   ❌ ERROR: ${entry.text.slice(0, 100)}`);
            }
        }
    });
    
    // Capture network requests
    page.on('response', response => {
        const url = response.url();
        if (url.includes('dashboard') || url.includes('.json') || url.includes('.sqlite')) {
            session.addNetworkRequest(
                url,
                response.status(),
                0 // Duration would need request timing
            );
        }
    });
    
    // Navigate to dashboard
    console.log(`   🌐 Loading: ${url}`);
    try {
        await page.goto(url, { waitUntil: 'networkidle', timeout });
    } catch (err) {
        console.warn(`   ⚠️ Navigation timeout, continuing with capture...`);
    }
    
    // Wait for dashboard initialization
    if (waitForData) {
        console.log(`   ⏳ Waiting for dashboard initialization...`);
        try {
            await page.waitForFunction(() => {
                return window.cortexDashboard?.initialized || 
                       document.querySelector('[data-dashboard-ready="true"]') ||
                       document.querySelector('.metric-card__value:not(:empty)');
            }, { timeout: 10000 });
            console.log(`   ✅ Dashboard initialized`);
        } catch (err) {
            console.warn(`   ⚠️ Dashboard initialization check timed out`);
        }
    }
    
    // Click through all tabs
    if (clickTabs) {
        console.log(`\n   🔄 Navigating through tabs...`);
        
        const tabButtons = await page.$$('.tab-button');
        console.log(`   Found ${tabButtons.length} tabs`);
        
        for (let i = 0; i < tabButtons.length; i++) {
            const tabButton = tabButtons[i];
            const tabName = await tabButton.textContent();
            const cleanName = tabName.trim().replace(/\s+/g, ' ');
            
            try {
                console.log(`   📑 Tab ${i + 1}/${tabButtons.length}: ${cleanName}`);
                await tabButton.click();
                session.addTabVisit(cleanName);
                
                // Wait for tab content to render
                await page.waitForTimeout(500);
                
                // Check for sub-tabs and click them too
                const subTabs = await page.$$('.sub-tab');
                if (subTabs.length > 0) {
                    console.log(`      Found ${subTabs.length} sub-tabs`);
                    for (const subTab of subTabs) {
                        const subName = await subTab.textContent();
                        await subTab.click();
                        await page.waitForTimeout(300);
                        session.addTabVisit(`${cleanName} > ${subName.trim()}`);
                    }
                }
            } catch (err) {
                console.warn(`      ⚠️ Tab click failed: ${cleanName}`);
            }
        }
    }
    
    // Wait a bit more for any delayed renders
    await page.waitForTimeout(2000);
    
    session.end();
    
    // Close browser
    await browser.close();
    
    // Save captured logs
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }
    
    const capturedLogsPath = path.join(outputDir, 'captured-logs.json');
    fs.writeFileSync(capturedLogsPath, JSON.stringify(session.toJSON(), null, 2));
    
    // Update session status
    if (fs.existsSync(sessionPath)) {
        const sessionData = JSON.parse(fs.readFileSync(sessionPath, 'utf-8'));
        sessionData.status = 'captured';
        sessionData.captureTime = new Date().toISOString();
        sessionData.captureSummary = session.getSummary();
        fs.writeFileSync(sessionPath, JSON.stringify(sessionData, null, 2));
    }
    
    // Print summary
    const summary = session.getSummary();
    console.log(`\n✅ Capture complete!`);
    console.log(`   Duration: ${summary.duration}ms`);
    console.log(`   Total Logs: ${summary.totalLogs}`);
    console.log(`   CORTEX Markers: ${summary.cortexLogs}`);
    console.log(`   Errors: ${summary.errors}`);
    console.log(`   Warnings: ${summary.warnings}`);
    console.log(`   Tabs Visited: ${summary.tabsVisited}`);
    console.log(`   Output: ${capturedLogsPath}`);
    
    return {
        session: session.toJSON(),
        outputPath: capturedLogsPath
    };
}

/**
 * CLI entry point
 */
if (process.argv[1] && process.argv[1].endsWith('CortexDebugCapture.js')) {
    const url = process.argv[2] || 'http://localhost:8888/dashboard.html?repo=KSESSIONS';
    const outputDir = process.argv[3] || '.cortex-debug';
    
    capture(url, { outputDir, headless: false })
        .then(result => {
            console.log(`\n📋 Run CortexDebugAnalyzer.js to analyze the captured logs`);
        })
        .catch(err => {
            console.error('❌ Capture failed:', err);
            process.exit(1);
        });
}

export default { capture, CaptureSession, LogEntry, MARKER_PREFIX };
