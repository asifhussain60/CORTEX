import { ApiClient } from './api-client.js';
import { ApiResponse } from '../models/api-response.js';
import { Account, CreateAccountRequest } from '../models/account.js';

/**
 * Account service — extracted from God Component app.ts (SMELL-01 fix).
 * Single responsibility: account CRUD via typed API client.
 */
export class AccountService {
    private readonly client: ApiClient;

    constructor(client: ApiClient) {
        this.client = client;
    }

    async getAll(page: number = 1, pageSize: number = 20): Promise<ApiResponse<Account>> {
        return this.client.get<ApiResponse<Account>>(
            `/api/v1/accounts?page=${page}&pageSize=${pageSize}`
        );
    }

    async getByUserId(userId: number): Promise<Account[]> {
        return this.client.get<Account[]>(`/api/v1/accounts/user/${userId}`);
    }

    async create(request: CreateAccountRequest): Promise<Account> {
        return this.client.post<Account>('/api/v1/accounts', request);
    }

    async delete(id: number): Promise<void> {
        return this.client.delete(`/api/v1/accounts/${id}`);
    }
}
