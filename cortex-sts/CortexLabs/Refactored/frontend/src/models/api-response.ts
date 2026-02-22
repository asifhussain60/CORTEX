/**
 * API response envelope — typed wrapper for paginated responses.
 * Replaces raw `any` parsing (SMELL-07 fix).
 */
export interface ApiResponse<T> {
    items: T[];
    page: number;
    pageSize: number;
    totalCount: number;
    totalPages: number;
    hasNextPage: boolean;
    hasPreviousPage: boolean;
}

export interface ApiError {
    type: string;
    title: string;
    status: number;
    detail: string;
    traceId: string;
}
