/**
 * HTTP Client Utility
 * Mock HTTP client for API simulation
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

import { AppConfig } from '../config.js';
import { Logger } from './logger.js';

const logger = new Logger('HttpClient');

/**
 * HttpClient class for simulated API calls
 */
export class HttpClient {
    /**
     * Simulate network delay
     * @returns {Promise<void>}
     */
    static async simulateDelay() {
        return new Promise(resolve => {
            setTimeout(resolve, AppConfig.api.simulatedDelay);
        });
    }

    /**
     * Simulate GET request
     * @param {string} url - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response object
     */
    static async get(url, options = {}) {
        logger.debug(`GET ${url}`, options);
        await this.simulateDelay();
        
        return {
            status: 200,
            ok: true,
            data: options.mockData || null,
            headers: { 'Content-Type': 'application/json' }
        };
    }

    /**
     * Simulate POST request
     * @param {string} url - API endpoint
     * @param {*} data - Request body
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response object
     */
    static async post(url, data, options = {}) {
        logger.debug(`POST ${url}`, data);
        await this.simulateDelay();
        
        return {
            status: 201,
            ok: true,
            data: options.mockResponse || data,
            headers: { 'Content-Type': 'application/json' }
        };
    }

    /**
     * Simulate PUT request
     * @param {string} url - API endpoint
     * @param {*} data - Request body
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response object
     */
    static async put(url, data, options = {}) {
        logger.debug(`PUT ${url}`, data);
        await this.simulateDelay();
        
        return {
            status: 200,
            ok: true,
            data: options.mockResponse || data,
            headers: { 'Content-Type': 'application/json' }
        };
    }

    /**
     * Simulate DELETE request
     * @param {string} url - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response object
     */
    static async delete(url, options = {}) {
        logger.debug(`DELETE ${url}`, options);
        await this.simulateDelay();
        
        return {
            status: 204,
            ok: true,
            data: null,
            headers: { 'Content-Type': 'application/json' }
        };
    }

    /**
     * Add authorization header to options
     * @param {Object} options - Request options
     * @param {string} token - Auth token
     * @returns {Object} Updated options
     */
    static withAuth(options = {}, token) {
        return {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${token}`
            }
        };
    }
}

export default HttpClient;
