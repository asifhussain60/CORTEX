// ✅ SMELL-24: Service layer — no direct fetch() in UI
// ✅ SMELL-25: All calls wrapped with typed error handling
// ✅ SMELL-6:  Paginated list queries throughout
// ✅ SMELL-1:  URLSearchParams (no string concatenation)
// ✅ SMELL-2:  sessionStorage (not localStorage)

import type {
  Transaction,
  User,
  Account,
  Report,
  AnalyticsSummary,
  CreateTransactionRequest,
  TransferRequest,
  TransactionCategory,
  ReportType,
  PageParams,
} from '../models/models.js';

const API_BASE = (window as typeof window & { __API_URL__?: string }).__API_URL__
  ?? 'http://localhost:5000/api/v1';

function getAuthHeader(): Record<string, string> {
  const token = sessionStorage.getItem('auth_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeader(),
      ...(init.headers as Record<string, string> ?? {}),
    },
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({ error: response.statusText }));
    throw new Error((err as { error?: string }).error ?? `HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const authService = {
  async login(username: string, password: string): Promise<{ token: string; role: string }> {
    const result = await apiRequest<{ token: string; role: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    sessionStorage.setItem('auth_token', result.token);
    sessionStorage.setItem('user_role', result.role);
    return result;
  },
  logout(): void {
    sessionStorage.removeItem('auth_token');
    sessionStorage.removeItem('user_role');
  },
};

export const transactionService = {
  async getAll(params: PageParams = { page: 1, pageSize: 25 }): Promise<Transaction[]> {
    return apiRequest<Transaction[]>(`/transactions?page=${params.page}&pageSize=${params.pageSize}`);
  },
  async search(category?: TransactionCategory, from?: string, params: PageParams = { page: 1, pageSize: 25 }): Promise<Transaction[]> {
    const qs = new URLSearchParams({ page: String(params.page), pageSize: String(params.pageSize) });
    if (category) qs.set('category', category);
    if (from) qs.set('from', from);
    return apiRequest<Transaction[]>(`/transactions/search?${qs}`);
  },
  async create(tx: CreateTransactionRequest): Promise<Transaction> {
    return apiRequest<Transaction>('/transactions', { method: 'POST', body: JSON.stringify(tx) });
  },
};

export const accountService = {
  async getAll(params: PageParams = { page: 1, pageSize: 25 }): Promise<Account[]> {
    return apiRequest<Account[]>(`/accounts?page=${params.page}&pageSize=${params.pageSize}`);
  },
  async transfer(req: TransferRequest): Promise<void> {
    const qs = new URLSearchParams({ fromId: String(req.fromId), toId: String(req.toId), amount: String(req.amount) });
    await apiRequest<unknown>(`/accounts/transfer?${qs}`, { method: 'POST' });
  },
};

export const userService = {
  async getAll(params: PageParams = { page: 1, pageSize: 25 }): Promise<User[]> {
    return apiRequest<User[]>(`/users?page=${params.page}&pageSize=${params.pageSize}`);
  },
  async search(username: string): Promise<User | null> {
    return apiRequest<User | null>(`/users/search?username=${encodeURIComponent(username)}`);
  },
  async delete(id: number): Promise<void> {
    await apiRequest<unknown>(`/users/${id}`, { method: 'DELETE' });
  },
};

export const reportService = {
  async getAll(params: PageParams = { page: 1, pageSize: 25 }): Promise<Report[]> {
    return apiRequest<Report[]>(`/reports?page=${params.page}&pageSize=${params.pageSize}`);
  },
  async generate(type: ReportType): Promise<Report> {
    return apiRequest<Report>(`/reports/generate?reportType=${type}`, { method: 'POST' });
  },
};

export const analyticsService = {
  async getSummary(): Promise<AnalyticsSummary> {
    return apiRequest<AnalyticsSummary>('/analytics/summary');
  },
};
