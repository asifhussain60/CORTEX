import { ApiError } from '../models/api-response.js';

/**
 * Typed API client — fixes SMELL-06 (fetch without error handling),
 * SMELL-10 (empty catch blocks), SMELL-22 (console.log → structured errors).
 * Provides retry logic and typed error responses.
 */
export class ApiClient {
    private readonly baseUrl: string;
    private readonly maxRetries: number;

    constructor(baseUrl: string = 'http://localhost:5000', maxRetries: number = 2) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.maxRetries = maxRetries;
    }

    async get<T>(path: string): Promise<T> {
        return this.request<T>('GET', path);
    }

    async post<T>(path: string, body: unknown): Promise<T> {
        return this.request<T>('POST', path, body);
    }

    async delete(path: string): Promise<void> {
        await this.request<void>('DELETE', path);
    }

    private async request<T>(method: string, path: string, body?: unknown): Promise<T> {
        let lastError: Error | null = null;

        for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
            try {
                const response = await fetch(`${this.baseUrl}${path}`, {
                    method,
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                    },
                    body: body ? JSON.stringify(body) : undefined,
                });

                if (!response.ok) {
                    const error: ApiError = await response.json().catch(() => ({
                        type: 'unknown',
                        title: response.statusText,
                        status: response.status,
                        detail: `HTTP ${response.status}`,
                        traceId: '',
                    }));
                    throw new ApiRequestError(error.detail, response.status, error);
                }

                if (response.status === 204) {
                    return undefined as T;
                }

                return await response.json() as T;
            } catch (err) {
                lastError = err instanceof Error ? err : new Error(String(err));
                if (attempt < this.maxRetries && !(err instanceof ApiRequestError)) {
                    await this.delay(Math.pow(2, attempt) * 500);
                } else {
                    throw lastError;
                }
            }
        }

        throw lastError ?? new Error('Request failed');
    }

    private delay(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

/**
 * Typed API error — replaces raw string errors.
 */
export class ApiRequestError extends Error {
    readonly statusCode: number;
    readonly apiError: ApiError;

    constructor(message: string, statusCode: number, apiError: ApiError) {
        super(message);
        this.name = 'ApiRequestError';
        this.statusCode = statusCode;
        this.apiError = apiError;
    }
}
