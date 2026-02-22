// ✅ CORTEX Refactored — TypeScript Models
// ✅ SMELL-22 RESOLVED: Strict types, no 'any'

/**
 * Transaction entity
 */
export interface Transaction {
    id: number;
    description: string;
    amount: number;
    category: string;
    type: TransactionType;
    date: string;
    userId: number;
}

/**
 * Transaction type enum — replaces magic strings
 */
export type TransactionType = 'income' | 'expense';

/**
 * Create transaction DTO
 */
export interface CreateTransactionDto {
    description: string;
    amount: number;
    category: string;
    type: TransactionType;
    userId: number;
}

/**
 * User entity
 */
export interface User {
    id: number;
    userName: string;
    email: string;
    role: UserRole;
    isActive: boolean;
}

/**
 * User role enum
 */
export type UserRole = 'user' | 'admin' | 'moderator';

/**
 * Create user DTO
 */
export interface CreateUserDto {
    userName: string;
    email: string;
    password: string;
    role?: UserRole;
}

/**
 * Account entity
 */
export interface Account {
    id: number;
    name: string;
    balance: number;
    userId: number;
    accountType: AccountType;
}

/**
 * Account type enum
 */
export type AccountType = 'checking' | 'savings' | 'investment';

/**
 * Dashboard summary
 */
export interface DashboardSummary {
    totalIncome: number;
    totalExpenses: number;
    netPosition: number;
    healthScore: HealthScore;
    categories: CategoryBreakdown[];
}

/**
 * Health score enum
 */
export type HealthScore = 'Healthy' | 'Warning' | 'Critical';

/**
 * Category breakdown for dashboard
 */
export interface CategoryBreakdown {
    name: string;
    amount: number;
    percentage: number;
}

/**
 * API error response
 */
export interface ApiError {
    message: string;
    statusCode: number;
    errors?: string[];
}

/**
 * Pagination parameters
 */
export interface PaginationParams {
    page: number;
    pageSize: number;
}

/**
 * API response wrapper
 */
export interface ApiResponse<T> {
    data: T | null;
    error: ApiError | null;
    loading: boolean;
}
