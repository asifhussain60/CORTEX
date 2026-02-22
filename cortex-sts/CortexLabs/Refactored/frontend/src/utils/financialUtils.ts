// ✅ SMELL-23 FIXED: Financial business logic extracted from UI into domain utilities
// ✅ SMELL-15 FIXED: Named constants replace magic numbers

import type { Transaction, HealthScore } from '../models/models.js';

// ✅ SMELL-15 FIXED: Named constants
const CRITICAL_EXPENSE_RATIO = 1.5;
const CURRENCY_LOCALE = 'en-US';
const CURRENCY_CODE = 'USD';

/**
 * Computes income, expenses, net position, and health score from a transaction list.
 * Previously embedded inline in UI render functions (SMELL-23 fix).
 */
export function computeDashboardSummary(transactions: Transaction[]): {
  totalIncome: number;
  totalExpenses: number;
  netPosition: number;
  healthScore: HealthScore;
} {
  let totalIncome = 0;
  let totalExpenses = 0;

  for (const tx of transactions) {
    if (tx.type === 'Income') totalIncome += tx.amount;
    else if (tx.type === 'Expense') totalExpenses += tx.amount;
  }

  const netPosition = totalIncome - totalExpenses;

  const healthScore: HealthScore =
    totalIncome > totalExpenses
      ? 'Healthy'
      : totalExpenses > totalIncome * CRITICAL_EXPENSE_RATIO
        ? 'Critical'
        : 'Warning';

  return { totalIncome, totalExpenses, netPosition, healthScore };
}

/**
 * Groups expense transactions by category and computes percentage breakdown.
 * Previously inline in renderDashboard (SMELL-23 fix).
 */
export function getCategoryBreakdown(
  transactions: Transaction[]
): Array<{ name: string; amount: number; percentage: string }> {
  const categories: Record<string, number> = {};

  for (const tx of transactions) {
    if (tx.type === 'Expense') {
      categories[tx.category] = (categories[tx.category] ?? 0) + tx.amount;
    }
  }

  const totalSpending = Object.values(categories).reduce((a, b) => a + b, 0) || 1;

  return Object.entries(categories).map(([name, amount]) => ({
    name,
    amount,
    percentage: ((amount / totalSpending) * 100).toFixed(1),
  }));
}

/**
 * Formats a number as a localised currency string.
 * Previously a scattered inline helper using hardcoded "$" (SMELL-15 fix).
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat(CURRENCY_LOCALE, {
    style: 'currency',
    currency: CURRENCY_CODE,
  }).format(amount);
}
