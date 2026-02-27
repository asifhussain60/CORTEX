// ✅ SMELL-21 FIXED: Dashboard rendering extracted into own component module
// ✅ SMELL-18 FIXED: textContent used instead of innerHTML — XSS eliminated
// ✅ SMELL-23 FIXED: Calculations delegated to financialUtils

import type { AnalyticsSummary } from '../models/models.js';
import { formatCurrency } from '../utils/financialUtils.js';

/** Renders the dashboard summary statistics panel. */
export function renderDashboard(container: HTMLElement, summary: AnalyticsSummary): void {
  container.replaceChildren(); // ✅ SMELL-18 FIXED: no innerHTML

  const grid = createStatGrid([
    { label: 'Total Income', value: formatCurrency(summary.totalIncome) },
    { label: 'Total Expenses', value: formatCurrency(summary.totalExpenses), negative: summary.totalExpenses > summary.totalIncome },
    { label: 'Net Position', value: formatCurrency(summary.netPosition), negative: summary.netPosition < 0 },
    { label: 'Health Score', value: summary.healthScore, className: summary.healthScore.toLowerCase() },
  ]);

  container.appendChild(grid);

  if (summary.topCategory) {
    const heading = document.createElement('h3');
    heading.textContent = `Top Category: ${summary.topCategory}`;
    container.appendChild(heading);
  }

  const txCount = document.createElement('p');
  txCount.textContent = `Total transactions: ${summary.transactionCount}`;
  container.appendChild(txCount);
}

function createStatGrid(items: Array<{ label: string; value: string; negative?: boolean; className?: string }>): HTMLElement {
  const grid = document.createElement('div');
  grid.className = 'stats-grid';

  for (const item of items) {
    const card = document.createElement('div');
    card.className = 'stat-card';

    const title = document.createElement('h3');
    title.textContent = item.label;

    const value = document.createElement('p');
    value.className = ['amount', item.negative ? 'negative' : '', item.className ?? ''].filter(Boolean).join(' ');
    value.textContent = item.value;

    card.appendChild(title);
    card.appendChild(value);
    grid.appendChild(card);
  }

  return grid;
}
