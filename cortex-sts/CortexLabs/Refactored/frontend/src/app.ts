/**
 * FinTrack App — thin entry point (SMELL-01 fix: 466 LOC God Component → ~100 LOC).
 * Delegates all domain logic to typed services.
 * Delegates formatting to utils.
 * No `any` types (SMELL-07 fix, ADR-004).
 */
import { ApiClient } from './services/api-client.js';
import { UserService } from './services/user-service.js';
import { TransactionService } from './services/transaction-service.js';
import { AccountService } from './services/account-service.js';
import { formatCurrency, formatDate } from './utils/currency-formatter.js';
import { escapeHtml } from './utils/validators.js';
import { User } from './models/user.js';
import { Transaction, TransactionType } from './models/transaction.js';
import { Account } from './models/account.js';

// --- Bootstrap ---
const client = new ApiClient('http://localhost:5000');
const userService = new UserService(client);
const transactionService = new TransactionService(client);
const accountService = new AccountService(client);

// --- DOM references ---
const usersTable = document.getElementById('users-table') as HTMLTableSectionElement;
const transactionsTable = document.getElementById('transactions-table') as HTMLTableSectionElement;
const accountsTable = document.getElementById('accounts-table') as HTMLTableSectionElement;
const errorBanner = document.getElementById('error-banner') as HTMLDivElement;
const transactionForm = document.getElementById('transaction-form') as HTMLFormElement;

// --- Error display ---
function showError(message: string): void {
    errorBanner.textContent = message;
    errorBanner.style.display = 'block';
    setTimeout(() => { errorBanner.style.display = 'none'; }, 5000);
}

// --- Render helpers ---
function renderUsers(users: User[]): void {
    usersTable.innerHTML = users.map(u =>
        `<tr>
            <td>${u.id}</td>
            <td>${escapeHtml(u.username)}</td>
            <td>${escapeHtml(u.email)}</td>
            <td>${escapeHtml(u.role)}</td>
        </tr>`
    ).join('');
}

function renderTransactions(transactions: Transaction[]): void {
    transactionsTable.innerHTML = transactions.map(t =>
        `<tr>
            <td>${t.id}</td>
            <td>${formatCurrency(t.amount)}</td>
            <td>${escapeHtml(t.type)}</td>
            <td>${escapeHtml(t.category)}</td>
        </tr>`
    ).join('');
}

function renderAccounts(accounts: Account[]): void {
    accountsTable.innerHTML = accounts.map(a =>
        `<tr>
            <td>${a.id}</td>
            <td>${escapeHtml(a.name)}</td>
            <td>${escapeHtml(a.type)}</td>
            <td>${formatCurrency(a.balance, a.currency)}</td>
            <td>${escapeHtml(a.currency)}</td>
        </tr>`
    ).join('');
}

// --- Data loading ---
async function loadAll(): Promise<void> {
    try {
        const [usersRes, txnRes, acctRes] = await Promise.all([
            userService.getAll(),
            transactionService.getAll(),
            accountService.getAll(),
        ]);
        renderUsers(usersRes.items);
        renderTransactions(txnRes.items);
        renderAccounts(acctRes.items);
    } catch (err) {
        showError(err instanceof Error ? err.message : 'Failed to load data');
    }
}

// --- Form handler ---
transactionForm?.addEventListener('submit', async (e: Event) => {
    e.preventDefault();

    const userId = parseInt((document.getElementById('txn-user-id') as HTMLInputElement).value);
    const amount = parseFloat((document.getElementById('txn-amount') as HTMLInputElement).value);
    const type = (document.getElementById('txn-type') as HTMLSelectElement).value as TransactionType;
    const description = (document.getElementById('txn-desc') as HTMLInputElement).value;

    try {
        await transactionService.create({ userId, amount, type, description });
        transactionForm.reset();
        await loadAll();
    } catch (err) {
        showError(err instanceof Error ? err.message : 'Failed to create transaction');
    }
});

// --- Init ---
loadAll();
