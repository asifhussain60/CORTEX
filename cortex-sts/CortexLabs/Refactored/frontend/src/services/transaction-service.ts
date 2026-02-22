import { ApiClient } from './api-client.js';
import { ApiResponse } from '../models/api-response.js';
import { Transaction, CreateTransactionRequest } from '../models/transaction.js';

/**
 * Transaction service — extracted from God Component app.ts (SMELL-01 fix).
 * Single responsibility: transaction CRUD via typed API client.
 */
export class TransactionService {
    private readonly client: ApiClient;

    constructor(client: ApiClient) {
        this.client = client;
    }

    async getAll(page: number = 1, pageSize: number = 20): Promise<ApiResponse<Transaction>> {
        return this.client.get<ApiResponse<Transaction>>(
            `/api/v1/transactions?page=${page}&pageSize=${pageSize}`
        );
    }

    async getByUserId(userId: number, page: number = 1): Promise<ApiResponse<Transaction>> {
        return this.client.get<ApiResponse<Transaction>>(
            `/api/v1/transactions/user/${userId}?page=${page}`
        );
    }

    async create(request: CreateTransactionRequest): Promise<Transaction> {
        return this.client.post<Transaction>('/api/v1/transactions', request);
    }

    async delete(id: number): Promise<void> {
        return this.client.delete(`/api/v1/transactions/${id}`);
    }

    async getTotal(userId: number): Promise<{ userId: number; total: number }> {
        return this.client.get(`/api/v1/transactions/user/${userId}/total`);
    }
}
