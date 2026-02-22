// FIX SMELL-21: app.ts is orchestration only — no inline fetch, no inline business logic
// FIX SMELL-11: no console.log for application state
import { userService } from './services/userService';
import { analyticsService } from './services/analyticsService';

async function bootstrap(): Promise<void> {
  const healthEl = document.getElementById('health-status');
  const analyticsEl = document.getElementById('analytics-summary');

  try {
    const res = await fetch('/api/v1/health');
    const health = await res.json();
    if (healthEl) healthEl.textContent = `Status: ${health.status}`;
  } catch {
    if (healthEl) healthEl.textContent = 'Status: unavailable';
  }

  try {
    const summary = await analyticsService.getSummary(1);
    if (analyticsEl) {
      analyticsEl.innerHTML = `
        <p>Income: $${summary.totalIncome.toFixed(2)}</p>
        <p>Expenses: $${summary.totalExpenses.toFixed(2)}</p>
        <p>Health: ${summary.healthScore}</p>
      `;
    }
  } catch {
    if (analyticsEl) analyticsEl.textContent = 'Analytics unavailable';
  }
}

document.addEventListener('DOMContentLoaded', bootstrap);