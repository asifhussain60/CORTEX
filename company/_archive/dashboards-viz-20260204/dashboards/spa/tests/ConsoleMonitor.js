/**
 * Playwright Console Assertion Framework
 * 
 * Filters and validates browser console messages to detect:
 * - CORTEX-specific errors (not third-party noise)
 * - Missing container warnings
 * - Data loading failures
 * - Unexpected JavaScript errors
 * 
 * Usage in E2E tests:
 *   const consoleMonitor = new ConsoleMonitor(page);
 *   await consoleMonitor.start();
 *   // ... test actions ...
 *   consoleMonitor.assertNoErrors();
 */

export class ConsoleMonitor {
  constructor(page, options = {}) {
    this.page = page;
    this.options = {
      // Filter out known third-party noise
      ignorePatterns: [
        /Grammarly/i,
        /WAX.*initialized/i,
        /DEFAULT.*root logger/i,
        /ContentIsolatedWorld/i,
        /Chrome extension/i,
        ...( options.ignorePatterns || [])
      ],
      
      // Only capture messages containing these patterns (CORTEX-specific)
      capturePatterns: [
        /CORTEX/i,
        /\[SPA\]/,
        /\[TRACE\]/,
        /DeferredRenderer/,
        /Dashboard/,
        ...( options.capturePatterns || [])
      ],
      
      // Error severity levels to capture
      captureLevels: options.captureLevels || ['error', 'warning'],
      
      // Maximum console messages to store
      maxMessages: options.maxMessages || 100,
      
      ...options
    };
    
    this.messages = {
      error: [],
      warning: [],
      info: [],
      log: []
    };
    
    this.rawMessages = []; // All messages for debugging
  }
  
  /**
   * Start monitoring console messages
   */
  async start() {
    this.page.on('console', (msg) => this._handleConsoleMessage(msg));
    
    // Also capture page errors (unhandled exceptions)
    this.page.on('pageerror', (error) => {
      this.messages.error.push({
        type: 'exception',
        text: error.message,
        stack: error.stack,
        timestamp: Date.now()
      });
    });
  }
  
  /**
   * Stop monitoring (cleanup)
   */
  stop() {
    this.page.removeAllListeners('console');
    this.page.removeAllListeners('pageerror');
  }
  
  /**
   * Handle console message with filtering
   */
  _handleConsoleMessage(msg) {
    const type = msg.type();
    const text = msg.text();
    
    // Store raw message
    if (this.rawMessages.length < this.options.maxMessages) {
      this.rawMessages.push({ type, text, timestamp: Date.now() });
    }
    
    // Apply ignore filter
    if (this._shouldIgnore(text)) {
      return;
    }
    
    // Apply capture filter (only store CORTEX-specific messages)
    if (!this._shouldCapture(text)) {
      return;
    }
    
    // Store filtered message
    if (this.options.captureLevels.includes(type)) {
      if (!this.messages[type]) {
        this.messages[type] = [];
      }
      
      if (this.messages[type].length < this.options.maxMessages) {
        this.messages[type].push({
          text,
          timestamp: Date.now(),
          location: msg.location()
        });
      }
    }
  }
  
  /**
   * Check if message should be ignored (third-party noise)
   */
  _shouldIgnore(text) {
    return this.options.ignorePatterns.some(pattern => pattern.test(text));
  }
  
  /**
   * Check if message should be captured (CORTEX-specific)
   */
  _shouldCapture(text) {
    // If no capture patterns specified, capture everything (except ignored)
    if (this.options.capturePatterns.length === 0) {
      return true;
    }
    
    return this.options.capturePatterns.some(pattern => pattern.test(text));
  }
  
  /**
   * Get all captured errors
   */
  getErrors() {
    return this.messages.error || [];
  }
  
  /**
   * Get all captured warnings
   */
  getWarnings() {
    return this.messages.warning || [];
  }
  
  /**
   * Assert no CORTEX-specific errors occurred
   */
  assertNoErrors(customMessage = '') {
    const errors = this.getErrors();
    
    if (errors.length > 0) {
      const errorList = errors.map((e, i) => 
        `  ${i + 1}. ${e.text}\n     at ${e.location?.url || 'unknown'}:${e.location?.lineNumber || '?'}`
      ).join('\n');
      
      throw new Error(
        `${customMessage || 'Console errors detected'} (${errors.length} errors):\n${errorList}`
      );
    }
  }
  
  /**
   * Assert no critical warnings occurred
   */
  assertNoWarnings(patterns = [/not found/i, /failed/i, /missing/i]) {
    const warnings = this.getWarnings().filter(w => 
      patterns.some(p => p.test(w.text))
    );
    
    if (warnings.length > 0) {
      const warningList = warnings.map((w, i) => 
        `  ${i + 1}. ${w.text}`
      ).join('\n');
      
      throw new Error(
        `Critical console warnings detected (${warnings.length}):\n${warningList}`
      );
    }
  }
  
  /**
   * Assert specific message was logged
   */
  assertMessageLogged(pattern, type = 'log') {
    const allMessages = this.rawMessages.filter(m => m.type === type);
    const found = allMessages.some(m => pattern.test(m.text));
    
    if (!found) {
      throw new Error(
        `Expected console.${type} message matching: ${pattern}\n` +
        `Captured ${allMessages.length} ${type} messages`
      );
    }
  }
  
  /**
   * Get summary of console activity
   */
  getSummary() {
    return {
      errors: this.messages.error?.length || 0,
      warnings: this.messages.warning?.length || 0,
      info: this.messages.info?.length || 0,
      total: this.rawMessages.length,
      ignored: this.rawMessages.length - Object.values(this.messages).flat().length
    };
  }
  
  /**
   * Print diagnostic report
   */
  printReport() {
    const summary = this.getSummary();
    
    console.log('\n📊 Console Monitor Report:');
    console.log(`   Total messages: ${summary.total}`);
    console.log(`   Captured: ${summary.total - summary.ignored}`);
    console.log(`   Filtered (noise): ${summary.ignored}`);
    console.log(`   Errors: ${summary.errors} 🔴`);
    console.log(`   Warnings: ${summary.warnings} 🟡`);
    
    if (summary.errors > 0) {
      console.log('\n🔴 Errors:');
      this.getErrors().forEach((e, i) => {
        console.log(`   ${i + 1}. ${e.text}`);
      });
    }
    
    if (summary.warnings > 0) {
      console.log('\n🟡 Warnings:');
      this.getWarnings().forEach((w, i) => {
        console.log(`   ${i + 1}. ${w.text}`);
      });
    }
  }
}

/**
 * Convenience function for use in Playwright tests
 */
export async function withConsoleMonitoring(page, testFn, options = {}) {
  const monitor = new ConsoleMonitor(page, options);
  await monitor.start();
  
  try {
    await testFn(monitor);
  } finally {
    if (options.printReport !== false) {
      monitor.printReport();
    }
    monitor.stop();
  }
  
  return monitor;
}
