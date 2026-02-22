import { ApiClient } from './api-client.js';
import { ApiResponse } from '../models/api-response.js';
import { User, CreateUserRequest, LoginRequest } from '../models/user.js';

/**
 * User service — extracted from God Component app.ts (SMELL-01 fix).
 * Single responsibility: user CRUD + auth via typed API client.
 */
export class UserService {
    private readonly client: ApiClient;

    constructor(client: ApiClient) {
        this.client = client;
    }

    async getAll(page: number = 1, pageSize: number = 20): Promise<ApiResponse<User>> {
        return this.client.get<ApiResponse<User>>(
            `/api/v1/users?page=${page}&pageSize=${pageSize}`
        );
    }

    async getById(id: number): Promise<User> {
        return this.client.get<User>(`/api/v1/users/${id}`);
    }

    async create(request: CreateUserRequest): Promise<User> {
        return this.client.post<User>('/api/v1/users', request);
    }

    async login(request: LoginRequest): Promise<User> {
        return this.client.post<User>('/api/v1/users/login', request);
    }

    async delete(id: number): Promise<void> {
        return this.client.delete(`/api/v1/users/${id}`);
    }
}
