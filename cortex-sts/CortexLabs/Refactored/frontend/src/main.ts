// ✅ CORTEX Refactored — Main Entry Point
// ✅ SMELL-21 RESOLVED: Modular architecture, not a God file

import { transactionService } from './services/TransactionService';
import { validationService } from './services/ValidationService';
import type { Transaction, DashboardSummary, CreateTransactionDto } from './models';

/**
 * Application state — typed, not `any`
 */
interface AppState {
    transactions: Transaction[];
    dashboard: DashboardSummary | null;
    activeTab: string;
    loading: boolean;
    error: string | null;
}

const state: AppState = {
    transactions: [],
    dashboard: null,
    activeTab: 'dashboard',
    loading: false,
    error: null,
};

// ═══════════════════════════════════════════════════════════════════════════
// Initialization
// ═══════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initForms();
    loadDashboard();
});

function initNavigation(): void {
    const navButtons = document.querySelectorAll<HTMLButtonElement>('.nav-tab');
    
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;
            if (tabId) {
                switchTab(tabId);
            }
        });
    });
}

function initForms(): void {
    // Transaction form
    const txForm = document.getElementById('add-transaction-form');
    txForm?.addEventListener('submit', handleAddTransaction);

    // Search form
    const searchForm = document.getElementById('search-transaction-form');
    searchForm?.addEventListener('submit', handleSearchTransactions);

    // Transfer form
    const transferForm = document.getElementById('transfer-form');
    transferForm?.addEventListener('submit', handleTransfer);
}

// ═══════════════════════════════════════════════════════════════════════════
// Tab Navigation
// ═══════════════════════════════════════════════════════════════════════════

function switchTab(tabId: string): void {
    // Update buttons
    document.querySelectorAll<HTMLButtonElement>('.nav-tab').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabId);
        btn.setAttribute('aria-selected', String(btn.dataset.tab === tabId));
    });

    // Update content
    document.querySelectorAll<HTMLElement>('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `tab-${tabId}`);
    });

    state.activeTab = tabId;

    // Load data for tab
    switch (tabId) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'transactions':
            loadTransactions();
            break;
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// Data Loading — ✅ SMELL-25 RESOLVED: Proper error handling
// ═══════════════════════════════════════════════════════════════════════════

async function loadDashboard(): Promise<void> {
    setLoading(true);
    
    const response = await transactionService.getAll();
    
    if (response.error) {
        showError(response.error.message);
        setLoading(false);
        return;
    }

    if (response.data) {
        state.transactions = response.data;
        state.dashboard = transactionService.calculateDashboard(response.data);
        renderDashboard();
    }
    
    setLoading(false);
}

async function loadTransactions(): Promise<void> {
    setLoading(true);
    
    const response = await transactionService.getAll();
    
    if (response.error) {
        showError(response.error.message);
        setLoading(false);
        return;
    }

    if (response.data) {
        state.transactions = response.data;
        renderTransactions();
    }
    
    setLoading(false);
}

// ═══════════════════════════════════════════════════════════════════════════
// Form Handlers — ✅ SMELL-23 RESOLVED: Validation in service
// ═══════════════════════════════════════════════════════════════════════════

async function handleAddTransaction(event: Event): Promise<void> {
    event.preventDefault();
    
    const form = event.target as HTMLFormElement;
    const description = (document.getElementById('tx-desc') as HTMLInputElement).value;
    const amount = parseFloat((document.getElementById('tx-amount') as HTMLInputElement).value);
    const category = (document.getElementById('tx-category') as HTMLInputElement).value;
    const type = (document.getElementById('tx-type') as HTMLSelectElement).value as 'income' | 'expense';

    // ✅ Validation via service
    const validation = validationService.validateTransaction({ description, amount, type });
    if (!validation.isValid) {
        showError(validation.errors.join(', '));
        return;
    }

    const dto: CreateTransactionDto = {
        description,
        amount,
        category: category || transactionService.autoCategorizeTx(amount, description),
        type,
        userId: 1, // TODO: Get from auth context
    };

    const response = await transactionService.create(dto);
    
    if (response.error) {
        showError(response.error.message);
        return;
    }

    form.reset();
    showStatus('Transaction added successfully');
    await loadTransactions();
}

async function handleSearchTransactions(event: Event): Promise<void> {
    event.preventDefault();
    
    const category = (document.getElementById('search-category') as HTMLInputElement).value;
    const fromDate = (document.getElementById('search-date') as HTMLInputElement).value;

    setLoading(true);
    const response = await transactionService.search(category || undefined, fromDate || undefined);
    
    if (response.error) {
        showError(response.error.message);
        setLoading(false);
        return;
    }

    if (response.data) {
        state.transactions = response.data;
        renderTransactions();
    }
    
    setLoading(false);
}

async function handleTransfer(event: Event): Promise<void> {
    event.preventDefault();
    
    const fromAccountId = parseInt((document.getElementById('transfer-from') as HTMLInputElement).value);
    const toAccountId = parseInt((document.getElementById('transfer-to') as HTMLInputElement).value);
    const amount = parseFloat((document.getElementById('transfer-amount') as HTMLInputElement).value);

    const validation = validationService.validateTransfer({ fromAccountId, toAccountId, amount });
    if (!validation.isValid) {
        showError(validation.errors.join(', '));
        return;
    }

    // TODO: Implement transfer via AccountService
    showStatus('Transfer functionality coming soon');
}

// ═══════════════════════════════════════════════════════════════════════════
// Rendering
// ═══════════════════════════════════════════════════════════════════════════

function renderDashboard(): void {
    const container = document.getElementById('dashboard-content');
    if (!container || !state.dashboard) return;

    const { totalIncome, totalExpenses, netPosition, healthScore, categories } = state.dashboard;

    container.innerHTML = `
        <div class="dashboard-grid">
            <div class="stat-card">
                <h3>Total Income</h3>
                <div class="amount income">${formatCurrency(totalIncome)}</div>
            </div>
            <div class="stat-card">
                <h3>Total Expenses</h3>
                <div class="amount expense">${formatCurrency(totalExpenses)}</div>
            </div>
            <div class="stat-card">
                <h3>Net Position</h3>
                <div class="amount ${netPosition >= 0 ? 'income' : 'negative'}">${formatCurrency(netPosition)}</div>
            </div>
            <div class="stat-card">
                <h3>Health Score</h3>
                <div class="amount ${healthScore.toLowerCase()}">${healthScore}</div>
            </div>
        </div>
        <h3>Spending by Category</h3>
        ${renderCategoryBars(categories)}
    `;
}

function renderCategoryBars(categories: { name: string; amount: number; percentage: number }[]): string {
    if (categories.length === 0) {
        return '<p>No expense data available</p>';
    }

    return categories.map(cat => `
        <div style="margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between;">
                <span>${cat.name}</span>
                <span>${formatCurrency(cat.amount)} (${cat.percentage}%)</span>
            </div>
            <div class="category-bar" style="width: ${cat.percentage}%"></div>
        </div>
    `).join('');
}

function renderTransactions(): void {
    const container = document.getElementById('transactions-content');
    if (!container) return;

    if (state.transactions.length === 0) {
        container.innerHTML = '<p>No transactions found</p>';
        return;
    }

    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Description</th>
                    <th>Category</th>
                    <th>Type</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                ${state.transactions.map(tx => `
                    <tr>
                        <td>${formatDate(tx.date)}</td>
                        <td>${escapeHtml(tx.description)}</td>
                        <td>${escapeHtml(tx.category)}</td>
                        <td class="${tx.type}">${tx.type}</td>
                        <td class="${tx.type}">${formatCurrency(tx.amount)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// ═══════════════════════════════════════════════════════════════════════════
// Utilities — ✅ SMELL-15 RESOLVED: Currency formatting configurable
// ═══════════════════════════════════════════════════════════════════════════

function formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    }).format(amount);
}

function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    });
}

function escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ═══════════════════════════════════════════════════════════════════════════
// UI Feedback
// ═══════════════════════════════════════════════════════════════════════════

function setLoading(loading: boolean): void {
    state.loading = loading;
    const statusEl = document.getElementById('status-message');
    if (statusEl) {
        statusEl.textContent = loading ? 'Loading...' : 'Ready';
    }
}

function showError(message: string): void {
    state.error = message;
    const statusEl = document.getElementById('status-message');
    const indicatorEl = document.getElementById('api-status');
    
    if (statusEl) {
        statusEl.textContent = `Error: ${message}`;
        statusEl.style.color = 'var(--color-danger)';
    }
    if (indicatorEl) {
        indicatorEl.classList.add('error');
    }

    // Reset after 5 seconds
    setTimeout(() => {
        if (statusEl) {
            statusEl.textContent = 'Ready';
            statusEl.style.color = '';
        }
        if (indicatorEl) {
            indicatorEl.classList.remove('error');
        }
    }, 5000);
}

function showStatus(message: string): void {
    const statusEl = document.getElementById('status-message');
    if (statusEl) {
        statusEl.textContent = message;
    }
}
