/**
 * Storage Utility
 * LocalStorage wrapper with JSON serialization
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

import { Logger } from './logger.js';

const logger = new Logger('Storage');

/**
 * StorageManager class for localStorage operations
 */
export class StorageManager {
    /**
     * Set item in localStorage
     * @param {string} key - Storage key
     * @param {*} value - Value to store (will be JSON stringified)
     * @returns {boolean} Success status
     */
    static set(key, value) {
        try {
            const serialized = JSON.stringify(value);
            localStorage.setItem(key, serialized);
            logger.debug(`Storage set: ${key}`, value);
            return true;
        } catch (error) {
            logger.error(`Failed to set storage key: ${key}`, error);
            return false;
        }
    }

    /**
     * Get item from localStorage
     * @param {string} key - Storage key
     * @param {*} defaultValue - Default value if key doesn't exist
     * @returns {*} Parsed value or default value
     */
    static get(key, defaultValue = null) {
        try {
            const serialized = localStorage.getItem(key);
            if (serialized === null) {
                return defaultValue;
            }
            const value = JSON.parse(serialized);
            logger.debug(`Storage get: ${key}`, value);
            return value;
        } catch (error) {
            logger.error(`Failed to get storage key: ${key}`, error);
            return defaultValue;
        }
    }

    /**
     * Remove item from localStorage
     * @param {string} key - Storage key
     * @returns {boolean} Success status
     */
    static remove(key) {
        try {
            localStorage.removeItem(key);
            logger.debug(`Storage removed: ${key}`);
            return true;
        } catch (error) {
            logger.error(`Failed to remove storage key: ${key}`, error);
            return false;
        }
    }

    /**
     * Clear all items from localStorage
     * @returns {boolean} Success status
     */
    static clear() {
        try {
            localStorage.clear();
            logger.info('Storage cleared');
            return true;
        } catch (error) {
            logger.error('Failed to clear storage', error);
            return false;
        }
    }

    /**
     * Check if key exists in localStorage
     * @param {string} key - Storage key
     * @returns {boolean} Exists status
     */
    static has(key) {
        return localStorage.getItem(key) !== null;
    }

    /**
     * Get all keys from localStorage
     * @returns {string[]} Array of keys
     */
    static keys() {
        return Object.keys(localStorage);
    }

    /**
     * Get storage size in bytes
     * @returns {number} Size in bytes
     */
    static getSize() {
        let size = 0;
        for (let key in localStorage) {
            if (localStorage.hasOwnProperty(key)) {
                size += localStorage[key].length + key.length;
            }
        }
        return size;
    }

    /**
     * Get storage size in human-readable format
     * @returns {string} Size formatted (e.g., "1.5 KB")
     */
    static getSizeFormatted() {
        const bytes = this.getSize();
        if (bytes < 1024) return bytes + ' bytes';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    }
}

export default StorageManager;
