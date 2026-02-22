/**
 * Account model — typed replacement for `any` (SMELL-07 fix).
 */
export interface Account {
    id: number;
    userId: number;
    name: string;
    type: AccountType;
    balance: number;
    currency: string;
    createdAt: string;
}

export type AccountType = 'Checking' | 'Savings' | 'Investment';

export interface CreateAccountRequest {
    userId: number;
    name: string;
    type: AccountType;
    currency?: string;
    initialBalance?: number;
}
