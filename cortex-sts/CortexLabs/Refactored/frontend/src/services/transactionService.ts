import { apiClient } from '../api/apiClient';
import type { Transaction } from '../models';

export const transactionService = {
  list: (userId: number, page = 1, pageSize = 50) =>
    apiClient.get<Transaction[]>(`/transactions?userId=${userId}&page=${page}&pageSize=${pageSize}`),
  search: (category?: string, dateFrom?: string) => {
    const params = new URLSearchParams();
    if (category) params.set('category', category);
    if (dateFrom) params.set('dateFrom', dateFrom);
    return apiClient.get<Transaction[]>(`/transactions/search?${params}`);
  },
  create: (tx: Omit<Transaction, 'id'>) => apiClient.post<Transaction>('/transactions', tx),
};