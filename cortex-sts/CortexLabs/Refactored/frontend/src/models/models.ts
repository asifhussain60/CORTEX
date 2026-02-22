// ✅ SMELL-22 FIXED: Typed interfaces replace 'any' everywhere
// ✅ SMELL-7 FIXED: Consistent camelCase throughout

/** Financial transaction from the API. */
export interface Transaction {
  id: number;
  description: string;
  amount: number;
  category: TransactionCategory;
  type: TransactionType;
  date: string;
  userId: number;
}

/** User account. */
export interface User {
  id: number;
  userName: string;
  email: string;
  role: string;
  isActive: boolean;
}

/** Financial account (checking, savings, etc.). */
export interface Account {
  id: number;
  name: string;
  balance: number;
  userId: number;
  type: AccountType;
}

/** Generated financial report. */
export interface Report {
  id: number;
  title: string;
  content: string;
  generatedBy: number;
  generatedAt: string;
  type: ReportType;
}

/** Analytics summary from the API. */
export interface AnalyticsSummary {
  totalIncome: number;
  totalExpenses: number;
  netPosition: number;
  averageTransaction: number;
  topCategory: string;
  healthScore: HealthScore;
  transactionCount: number;
}

/** Application UI state — immutable snapshot, never mutated in place. */
export interface AppState {
  transactions: Transaction[];
  users: User[];
  accounts: Account[];
  reports: Report[];
  summary: AnalyticsSummary | null;
  activeTab: TabName;
  isLoading: boolean;
  error: string | null;
}

// ✅ SMELL-15 FIXED: String literal union types instead of magic strings
export type TransactionType = 'Income' | 'Expense' | 'Transfer';
export type TransactionCategory =
  | 'Food' | 'Transport' | 'Entertainment'
  | 'LargePurchase' | 'MediumPurchase' | 'Utilities'
  | 'Healthcare' | 'Other';
export type AccountType = 'Checking' | 'Savings' | 'Investment' | 'Credit';
export type ReportType = 'Monthly' | 'Annual' | 'Tax' | 'Custom';
export type HealthScore = 'Healthy' | 'Warning' | 'Critical';
export type TabName = 'dashboard' | 'transactions' | 'accounts' | 'users' | 'reports';

/** Request body for creating a new transaction. */
export interface CreateTransactionRequest {
  description: string;
  amount: number;
  category: TransactionCategory;
  type: TransactionType;
  date: string;
  userId: number;
}

/** Request body for initiating a transfer. */
export interface TransferRequest {
  fromId: number;
  toId: number;
  amount: number;
}

/** Pagination parameters for list queries. */
export interface PageParams {
  page: number;
  pageSize: number;
}

/** Generic paginated API response. */
export interface ApiError {
  error: string;
}
