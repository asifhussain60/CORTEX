// ✅ CORTEX Refactored — TransactionService
// ✅ SMELL-23 RESOLVED: Business logic in service layer, not UI
// ✅ SMELL-24 RESOLVED: Uses ApiService, no direct fetch()

import { apiService } from './ApiService';
import type { 
    Transaction, 
    CreateTransactionDto, 
    DashboardSummary, 
    ApiResponse,
    CategoryBreakdown,
    HealthScore
} from '../models';

/**
 * Transaction threshold constants
 * ✅ SMELL-15 RESOLVED: No magic numbers
 */
const THRESHOLDS = {
    LARGE_PURCHASE: 10000,
    MEDIUM_PURCHASE: 1000,
    HEALTHY_RATIO: 1.0,
    CRITICAL_RATIO: 1.5,
} as const;

/**
 * Transaction service — handles transaction operations and business logic
 */
export class TransactionService {
    private readonly basePath = '/transactions';

    /**
     * Get all transactions with pagination
     * ✅ SMELL-6 RESOLVED: Pagination support
     */
    async getAll(page = 1, pageSize = 50): Promise<ApiResponse<Transaction[]>> {
        return apiService.get<Transaction[]>(this.basePath, { page, pageSize });
    }

    /**
     * Get transaction by ID
     */
    async getById(id: number): Promise<ApiResponse<Transaction>> {
        return apiService.get<Transaction>(`${this.basePath}/${id}`);
    }

    /**
     * Search transactions
     * ✅ SMELL-1 RESOLVED: Parameterized via API service
     */
    async search(category?: string, fromDate?: string): Promise<ApiResponse<Transaction[]>> {
        const params: Record<string, string> = {};
        if (category) params.category = category;
        if (fromDate) params.fromDate = fromDate;
        
        return apiService.get<Transaction[]>(`${this.basePath}/search`, params);
    }

    /**
     * Create transaction
     */
    async create(dto: CreateTransactionDto): Promise<ApiResponse<Transaction>> {
        return apiService.post<Transaction, CreateTransactionDto>(this.basePath, dto);
    }

    /**
     * Delete transaction
     */
    async delete(id: number): Promise<ApiResponse<void>> {
        return apiService.delete<void>(`${this.basePath}/${id}`);
    }

    /**
     * Get dashboard summary from API
     */
    async getDashboardSummary(userId: number): Promise<ApiResponse<DashboardSummary>> {
        return apiService.get<DashboardSummary>(`${this.basePath}/dashboard/${userId}`);
    }

    /**
     * Calculate dashboard locally from transactions
     * ✅ SMELL-23 RESOLVED: Business logic in service
     */
    calculateDashboard(transactions: Transaction[]): DashboardSummary {
        const totalIncome = transactions
            .filter(t => t.type === 'income')
            .reduce((sum, t) => sum + t.amount, 0);

        const totalExpenses = transactions
            .filter(t => t.type === 'expense')
            .reduce((sum, t) => sum + t.amount, 0);

        const netPosition = totalIncome - totalExpenses;
        const healthScore = this.calculateHealthScore(totalIncome, totalExpenses);
        const categories = this.getCategoryBreakdown(transactions, totalExpenses);

        return {
            totalIncome,
            totalExpenses,
            netPosition,
            healthScore,
            categories,
        };
    }

    /**
     * Calculate health score
     * ✅ SMELL-15 RESOLVED: Constants instead of magic numbers
     */
    private calculateHealthScore(income: number, expenses: number): HealthScore {
        if (income > expenses * THRESHOLDS.HEALTHY_RATIO) {
            return 'Healthy';
        }
        if (expenses > income * THRESHOLDS.CRITICAL_RATIO) {
            return 'Critical';
        }
        return 'Warning';
    }

    /**
     * Get category breakdown for expenses
     */
    private getCategoryBreakdown(transactions: Transaction[], totalExpenses: number): CategoryBreakdown[] {
        const categoryMap = new Map<string, number>();

        for (const tx of transactions) {
            if (tx.type === 'expense') {
                const current = categoryMap.get(tx.category) ?? 0;
                categoryMap.set(tx.category, current + tx.amount);
            }
        }

        const result: CategoryBreakdown[] = [];
        for (const [name, amount] of categoryMap) {
            result.push({
                name,
                amount,
                percentage: totalExpenses > 0 
                    ? Math.round((amount / totalExpenses) * 1000) / 10 
                    : 0,
            });
        }

        return result.sort((a, b) => b.amount - a.amount);
    }

    /**
     * Auto-categorize transaction based on amount and description
     * ✅ SMELL-4 RESOLVED: Categorization logic in service
     */
    autoCategorizeTx(amount: number, description: string): string {
        if (amount >= THRESHOLDS.LARGE_PURCHASE) return 'large_purchase';
        if (amount >= THRESHOLDS.MEDIUM_PURCHASE) return 'medium_purchase';

        const lowerDesc = description.toLowerCase();
        if (lowerDesc.includes('grocery') || lowerDesc.includes('food')) return 'food';
        if (lowerDesc.includes('gas') || lowerDesc.includes('fuel')) return 'transport';
        if (lowerDesc.includes('netflix') || lowerDesc.includes('spotify')) return 'entertainment';

        return 'other';
    }
}

// ✅ Singleton instance
export const transactionService = new TransactionService();
