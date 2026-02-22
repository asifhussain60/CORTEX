// ✅ CORTEX Refactored — ApiService
// ✅ SMELL-24 RESOLVED: Centralized API abstraction
// ✅ SMELL-25 RESOLVED: Proper error handling
// ✅ SMELL-14 RESOLVED: Retry logic and timeout

import type { ApiError, ApiResponse } from '../models';

/**
 * API configuration
 */
interface ApiConfig {
    baseUrl: string;
    timeout: number;
    maxRetries: number;
    retryDelay: number;
}

/**
 * Default configuration — configurable via environment
 */
const DEFAULT_CONFIG: ApiConfig = {
    baseUrl: import.meta.env.VITE_API_URL ?? 'http://localhost:5000/api/v1',
    timeout: 10000,  // ✅ SMELL-15 RESOLVED: Named constant
    maxRetries: 3,   // ✅ SMELL-14 RESOLVED: Retry logic
    retryDelay: 1000,
};

/**
 * Centralized API service — handles all HTTP communication
 * ✅ SMELL-24 RESOLVED: Single point for all fetch calls
 */
export class ApiService {
    private config: ApiConfig;

    constructor(config: Partial<ApiConfig> = {}) {
        this.config = { ...DEFAULT_CONFIG, ...config };
    }

    /**
     * Generic GET request with retry and error handling
     */
    async get<T>(endpoint: string, params?: Record<string, string | number>): Promise<ApiResponse<T>> {
        const url = this.buildUrl(endpoint, params);
        return this.request<T>('GET', url);
    }

    /**
     * Generic POST request
     */
    async post<T, D>(endpoint: string, data: D): Promise<ApiResponse<T>> {
        const url = this.buildUrl(endpoint);
        return this.request<T>('POST', url, data);
    }

    /**
     * Generic PUT request
     */
    async put<T, D>(endpoint: string, data: D): Promise<ApiResponse<T>> {
        const url = this.buildUrl(endpoint);
        return this.request<T>('PUT', url, data);
    }

    /**
     * Generic DELETE request
     */
    async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
        const url = this.buildUrl(endpoint);
        return this.request<T>('DELETE', url);
    }

    /**
     * Core request method with retry logic
     * ✅ SMELL-14 RESOLVED: Retry with exponential backoff
     * ✅ SMELL-25 RESOLVED: Comprehensive error handling
     */
    private async request<T>(
        method: string,
        url: string,
        data?: unknown,
        retryCount = 0
    ): Promise<ApiResponse<T>> {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

        try {
            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: data ? JSON.stringify(data) : undefined,
                signal: controller.signal,
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorData = await this.parseError(response);
                
                // ✅ Retry on server errors (5xx)
                if (response.status >= 500 && retryCount < this.config.maxRetries) {
                    await this.delay(this.config.retryDelay * Math.pow(2, retryCount));
                    return this.request<T>(method, url, data, retryCount + 1);
                }

                return {
                    data: null,
                    error: errorData,
                    loading: false,
                };
            }

            const responseData = await response.json() as T;
            return {
                data: responseData,
                error: null,
                loading: false,
            };
        } catch (error) {
            clearTimeout(timeoutId);

            // ✅ Handle abort (timeout)
            if (error instanceof DOMException && error.name === 'AbortError') {
                return {
                    data: null,
                    error: {
                        message: 'Request timed out',
                        statusCode: 408,
                    },
                    loading: false,
                };
            }

            // ✅ Handle network errors with retry
            if (error instanceof TypeError && retryCount < this.config.maxRetries) {
                await this.delay(this.config.retryDelay * Math.pow(2, retryCount));
                return this.request<T>(method, url, data, retryCount + 1);
            }

            // ✅ SMELL-25 RESOLVED: Structured error response
            return {
                data: null,
                error: {
                    message: error instanceof Error ? error.message : 'Unknown error occurred',
                    statusCode: 0,
                },
                loading: false,
            };
        }
    }

    /**
     * Build URL with query parameters
     */
    private buildUrl(endpoint: string, params?: Record<string, string | number>): string {
        const url = new URL(endpoint, this.config.baseUrl);
        
        if (params) {
            Object.entries(params).forEach(([key, value]) => {
                if (value !== undefined && value !== null) {
                    url.searchParams.append(key, String(value));
                }
            });
        }

        return url.toString();
    }

    /**
     * Parse error response
     */
    private async parseError(response: Response): Promise<ApiError> {
        try {
            const data = await response.json();
            return {
                message: data.message ?? response.statusText,
                statusCode: response.status,
                errors: data.errors,
            };
        } catch {
            return {
                message: response.statusText,
                statusCode: response.status,
            };
        }
    }

    /**
     * Delay helper for retry logic
     */
    private delay(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// ✅ Singleton instance for app-wide use
export const apiService = new ApiService();
