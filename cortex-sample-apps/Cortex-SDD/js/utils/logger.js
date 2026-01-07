/**
 * Logger Utility
 * Console logging with levels and formatting
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

import { AppConfig } from '../config.js';

/**
 * Logger class for consistent console logging
 */
export class Logger {
    constructor(context = 'App') {
        this.context = context;
        this.enabled = AppConfig.logging.enabled;
        this.level = AppConfig.logging.level;
        this.includeTimestamp = AppConfig.logging.includeTimestamp;
    }

    /**
     * Get formatted timestamp
     * @returns {string} Formatted timestamp
     */
    getTimestamp() {
        if (!this.includeTimestamp) return '';
        const now = new Date();
        return `[${now.toLocaleTimeString()}]`;
    }

    /**
     * Log debug message
     * @param {string} message - Message to log
     * @param {*} data - Optional data to log
     */
    debug(message, data = null) {
        if (!this.enabled || this.level === 'warn' || this.level === 'error') return;
        console.debug(`${this.getTimestamp()} [DEBUG] [${this.context}] ${message}`, data || '');
    }

    /**
     * Log info message
     * @param {string} message - Message to log
     * @param {*} data - Optional data to log
     */
    info(message, data = null) {
        if (!this.enabled || this.level === 'warn' || this.level === 'error') return;
        console.info(`${this.getTimestamp()} [INFO] [${this.context}] ${message}`, data || '');
    }

    /**
     * Log warning message
     * @param {string} message - Message to log
     * @param {*} data - Optional data to log
     */
    warn(message, data = null) {
        if (!this.enabled || this.level === 'error') return;
        console.warn(`${this.getTimestamp()} [WARN] [${this.context}] ${message}`, data || '');
    }

    /**
     * Log error message
     * @param {string} message - Message to log
     * @param {Error} error - Optional error object
     */
    error(message, error = null) {
        if (!this.enabled) return;
        console.error(`${this.getTimestamp()} [ERROR] [${this.context}] ${message}`, error || '');
        if (error && AppConfig.logging.includeStackTrace && error.stack) {
            console.error(error.stack);
        }
    }

    /**
     * Log group start
     * @param {string} label - Group label
     */
    group(label) {
        if (!this.enabled) return;
        console.group(`${this.getTimestamp()} [${this.context}] ${label}`);
    }

    /**
     * Log group end
     */
    groupEnd() {
        if (!this.enabled) return;
        console.groupEnd();
    }
}

// Export singleton instance
export const logger = new Logger('Cortex-SDD');

export default Logger;
