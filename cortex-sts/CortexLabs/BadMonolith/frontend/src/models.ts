// ❌ SMELL-22: No interfaces, no typed models — everything is 'any'
// This file SHOULD define proper TypeScript interfaces but doesn't

// ❌ SMELL-22: Using 'any' instead of proper types
type Transaction = any;
type User = any;
type Account = any;
type FinReport = any; // ❌ SMELL-7: Inconsistent naming — 'FinReport' vs other types without prefix
type AdminStats = any;
type ApiResponse = any;

// ❌ SMELL-7: Mixed naming — some camelCase, some snake_case, some PascalCase
interface AppState {
    transactions: any[];
    users: any[];
    accounts: any[];
    reports: any[];
    admin_stats: any;          // ❌ SMELL-7: snake_case in TypeScript
    activeTab: string;
    TotalIncome: number;       // ❌ SMELL-7: PascalCase
    total_expenses: number;    // ❌ SMELL-7: snake_case
    netPosition: number;
    healthScore: string;
    api_call_count: number;    // ❌ SMELL-7: snake_case
}
