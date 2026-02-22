// ══════════════════════════════════════════════════════════════════════════════
// API Client — Centralized HTTP service with error handling
// ══════════════════════════════════════════════════════════════════════════════
// Fixes: SMELL-24 (no service layer → service abstraction)
//        SMELL-25 (no error handling → try/catch + typed errors)
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Custom API error class with HTTP status code
 */
export class ApiError extends Error {
  public readonly statusCode: number;

  constructor(message: string, statusCode: number) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
  }
}

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

/**
 * Centralized API client with error handling and type safety
 */
export class ApiClient {
  private readonly baseUrl: string;

  constructor(baseUrl: string = '/api/v1') {
    this.baseUrl = baseUrl;
  }

  /**
   * Generic GET request with typed response
   * @param endpoint - API endpoint (e.g., '/users')
   * @returns Promise with typed data or error
   */
  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new ApiError(
          `GET ${endpoint} failed: ${response.statusText}`,
          response.status
        );
      }

      const data = await response.json();
      return { data };
    } catch (error: unknown) {
      return {
        error: error instanceof ApiError ? error.message : 'Network error',
      };
    }
  }

  /**
   * Generic POST request with typed request/response
   * @param endpoint - API endpoint (e.g., '/users')
   * @param body - Request payload
   * @returns Promise with typed data or error
   */
  async post<TRequest, TResponse>(
    endpoint: string,
    body: TRequest
  ): Promise<ApiResponse<TResponse>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        throw new ApiError(
          `POST ${endpoint} failed: ${response.statusText}`,
          response.status
        );
      }

      const data = await response.json();
      return { data };
    } catch (error: unknown) {
      return {
        error: error instanceof ApiError ? error.message : 'Network error',
      };
    }
  }

  /**
   * Generic DELETE request
   * @param endpoint - API endpoint (e.g., '/users/123')
   * @returns Promise with success status or error
   */
  async delete(endpoint: string): Promise<ApiResponse<void>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new ApiError(
          `DELETE ${endpoint} failed: ${response.statusText}`,
          response.status
        );
      }

      return {};
    } catch (error: unknown) {
      return {
        error: error instanceof ApiError ? error.message : 'Network error',
      };
    }
  }
}

// Singleton instance
export const apiClient = new ApiClient();
