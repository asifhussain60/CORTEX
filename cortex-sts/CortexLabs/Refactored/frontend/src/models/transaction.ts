/**
 * Transaction model — typed replacement for `any` (SMELL-07 fix).
 * Matches backend TransactionDto exactly.
 */
export interface Transaction {
    id: number;
    userId: number;
    amount: number;
    type: TransactionType;
    category: TransactionCategory;
    description: string;
    date: string;
    createdAt: string;
}

export type TransactionType = 'Income' | 'Expense';

export type TransactionCategory =
    | 'Food'
    | 'Transport'
    | 'Entertainment'
    | 'LargePurchase'
    | 'MediumPurchase'
    | 'Other';

export interface CreateTransactionRequest {
    userId: number;
    amount: number;
    type: TransactionType;
    category?: TransactionCategory;
    description?: string;
    date?: string;
}
