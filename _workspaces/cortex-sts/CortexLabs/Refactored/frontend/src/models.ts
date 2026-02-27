// FIX SMELL-7: PascalCase enum names, consistent property casing
export enum TransactionType { Income = 'Income', Expense = 'Expense', Transfer = 'Transfer' }
export enum AccountType { Checking = 'Checking', Savings = 'Savings', Investment = 'Investment', Credit = 'Credit' }

export interface User {
  id: number;
  userName: string;
  email: string;
  role: string;
  isActive: boolean;
}

export interface Transaction {
  id: number;
  description: string;
  amount: number;
  categoryName: string;
  type: TransactionType;
  date: string;
  userId: number;
}

export interface Account {
  id: number;
  accountName: string;
  balance: number;
  userId: number;
  accountType: AccountType;
}

export interface AnalyticsSummary {
  totalIncome: number;
  totalExpenses: number;
  netPosition: number;
  averageTransaction: number;
  topCategory: string;
  healthScore: string;
  transactionCount: number;
}