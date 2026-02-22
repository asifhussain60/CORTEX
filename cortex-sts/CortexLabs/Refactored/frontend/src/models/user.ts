/**
 * User model — typed replacement for `any` (SMELL-07 fix).
 * Password fields are never present in response DTOs.
 */
export interface User {
    id: number;
    username: string;
    email: string;
    role: UserRole;
    createdAt: string;
}

export type UserRole = 'Admin' | 'User';

export interface CreateUserRequest {
    username: string;
    email: string;
    password: string;
}

export interface LoginRequest {
    username: string;
    password: string;
}
