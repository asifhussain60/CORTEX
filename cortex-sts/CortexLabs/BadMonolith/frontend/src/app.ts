// ❌ SMELL-21: God file — ALL application logic in ONE file (dashboard, transactions,
//    accounts, users, reports, admin — 6 domains crammed into a single TypeScript file)
// ❌ SMELL-22: 'any' types everywhere — no TypeScript safety
// ❌ SMELL-23: Business logic (calculations, validation, formatting) mixed into UI code
// ❌ SMELL-24: Direct fetch() calls everywhere — no service layer, no API abstraction
// ❌ SMELL-25: No error handling on API calls — silent failures everywhere

// ❌ SMELL-15: Hardcoded API URL — should come from environment config
const API_URL = "http://localhost:5000/api";
const MAX_RETRIES = 0;          // ❌ SMELL-14: No retry logic at all
const CACHE_TTL = 999999999;    // ❌ SMELL-15: Magic number — effectively infinite cache

// ❌ SMELL-16: Global mutable state — any function can mutate these
let transactions: any[] = [];
let users: any[] = [];
let accounts: any[] = [];
let reports: any[] = [];
let adminStats: any = {};
let apiCallCount = 0;
let lastError: string = "";
let totalIncome = 0;
let totalExpenses = 0;
let netPosition = 0;
let healthScore = "unknown";
let activeTab = "dashboard";

// ══════════════════════════════════════════════════════════════════════════════
// DATA LOADING — ❌ SMELL-24: Direct fetch in UI code, no service layer
// ══════════════════════════════════════════════════════════════════════════════

// ❌ SMELL-25: No error handling — if API is down, page silently breaks
// ❌ SMELL-6: No pagination parameter — loads ALL data
async function loadTransactions(): Promise<void> {
    const response = await fetch(`${API_URL}/transactions`);
    transactions = await response.json();
    apiCallCount++;
    calculateDashboard(); // ❌ SMELL-23: Business logic triggered from data load
    renderTransactions();
}

async function loadUsers(): Promise<void> {
    const response = await fetch(`${API_URL}/users`);
    users = await response.json();
    apiCallCount++;
    renderUsers();
}

async function loadAccounts(): Promise<void> {
    const response = await fetch(`${API_URL}/accounts`);
    accounts = await response.json();
    apiCallCount++;
    renderAccounts();
}

async function loadReports(): Promise<void> {
    const response = await fetch(`${API_URL}/reports`);
    reports = await response.json();
    apiCallCount++;
    renderReports();
}

// ❌ SMELL-18: Fetching admin stats (with secrets!) with no authentication
async function loadAdminStats(): Promise<void> {
    const response = await fetch(`${API_URL}/admin/stats`);
    adminStats = await response.json();
    apiCallCount++;
    renderAdmin();
}

// ❌ SMELL-25: No error handling, no loading states, no timeout
async function loadAllData(): Promise<void> {
    loadTransactions();  // ❌ SMELL-25: Not awaited — race conditions possible
    loadUsers();
    loadAccounts();
    loadReports();
    updateStatusBar();
}

// ══════════════════════════════════════════════════════════════════════════════
// BUSINESS LOGIC — ❌ SMELL-23: Should be in a separate service/domain layer
// ══════════════════════════════════════════════════════════════════════════════

// ❌ SMELL-23: Financial calculations in UI code — belongs in domain service
function calculateDashboard(): void {
    totalIncome = 0;
    totalExpenses = 0;

    for (const tx of transactions) {
        if (tx.Type === "income") {
            totalIncome += tx.Amount;
        } else if (tx.Type === "expense") {
            totalExpenses += tx.Amount;
        }
    }

    netPosition = totalIncome - totalExpenses;

    // ❌ SMELL-15: Magic number 1.5 for health threshold
    if (totalIncome > totalExpenses) {
        healthScore = "Healthy";
    } else if (totalExpenses > totalIncome * 1.5) {
        healthScore = "Critical";
    } else {
        healthScore = "Warning";
    }
}

// ❌ SMELL-23: Category breakdown — business analytics in UI layer
function getCategoryBreakdown(): any[] {
    const categories: any = {}; // ❌ SMELL-22: any type
    for (const tx of transactions) {
        if (tx.Type === "expense") {
            if (!categories[tx.category_name]) categories[tx.category_name] = 0;
            categories[tx.category_name] += tx.Amount;
        }
    }

    const result: any[] = [];
    const totalSpending = totalExpenses || 1; // ❌ SMELL-15: Magic number 1 to avoid div-by-zero
    for (const cat in categories) {
        result.push({
            name: cat,
            amount: categories[cat],
            percentage: ((categories[cat] / totalSpending) * 100).toFixed(1)
        });
    }
    return result;
}

// ❌ SMELL-10: Duplicate validation — same logic exists in backend UserService
// ❌ SMELL-23: Validation logic in UI code
function validateEmail(email: string): boolean {
    if (!email) return false;
    if (!email.includes("@")) return false;
    if (email.length < 5) return false;   // ❌ SMELL-15: Magic number
    if (email.length > 100) return false;  // ❌ SMELL-15: Magic number
    return true;
}

// ❌ SMELL-23: Currency formatting in UI — should be a shared utility
function formatCurrency(amount: any): string { // ❌ SMELL-22: any param
    return "$" + Number(amount).toFixed(2);     // ❌ SMELL-15: Hardcoded USD
}

// ❌ SMELL-8: Dead code — function defined but never called
function calculateCompoundInterest(principal: any, rate: any, years: any): any {
    return principal * Math.pow((1 + rate), years);
}

// ❌ SMELL-8: Another dead function
function generatePdfReport(data: any): void {
    console.log("PDF generation not implemented"); // ❌ SMELL-11: console.log
}

// ❌ SMELL-8: Dead function — was planned for "Phase 2"
function exportToExcel(data: any[]): any {
    // TODO: implement Excel export (this TODO has been here since 2023)
    return null;
}

// ══════════════════════════════════════════════════════════════════════════════
// API ACTIONS — ❌ SMELL-24: Direct fetch, no service abstraction
// ══════════════════════════════════════════════════════════════════════════════

// ❌ SMELL-24: Direct fetch call
// ❌ SMELL-25: No error handling
// ❌ SMELL-23: Input validation mixed into action handler
async function addTransaction(): Promise<void> {
    const descEl = document.getElementById("tx-desc") as HTMLInputElement;
    const amountEl = document.getElementById("tx-amount") as HTMLInputElement;
    const categoryEl = document.getElementById("tx-category") as HTMLInputElement;
    const typeEl = document.getElementById("tx-type") as HTMLSelectElement;

    const description = descEl?.value || "";
    const amount = parseFloat(amountEl?.value || "0");
    const category = categoryEl?.value || "";
    const type = typeEl?.value || "expense";

    // ❌ SMELL-23: Validation in UI action handler
    if (!description || description.length < 1) {
        alert("Description required");  // ❌ SMELL-21: alert() instead of proper UI feedback
        return;
    }
    if (amount <= 0) {
        alert("Amount must be positive");
        return;
    }

    const tx = {
        description: description,
        Amount: amount,
        category_name: category,
        Type: type,
        Date: new Date().toISOString().split("T")[0],
        UserId: 1  // ❌ SMELL-15: Hardcoded user ID
    };

    // ❌ SMELL-25: No try/catch — will silently fail
    await fetch(`${API_URL}/transactions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(tx)
    });
    apiCallCount++;
    loadAllData();  // ❌ Reloads ALL data instead of just updating local state
}

// ❌ SMELL-1: User input passed directly to query string — enables SQL injection via API
async function searchTransactions(): Promise<void> {
    const catEl = document.getElementById("search-category") as HTMLInputElement;
    const dateEl = document.getElementById("search-date") as HTMLInputElement;
    const category = catEl?.value || "";
    const dateFrom = dateEl?.value || "";

    // ❌ SMELL-25: No error handling
    // ❌ SMELL-1: Unsanitized user input goes straight to query params (API does SQL injection)
    const response = await fetch(`${API_URL}/transactions/search?category=${category}&dateFrom=${dateFrom}`);
    transactions = await response.json();
    apiCallCount++;
    renderTransactions();
}

// ❌ SMELL-25: No confirmation dialog before delete — no error handling
async function deleteUser(id: number): Promise<void> {
    await fetch(`${API_URL}/admin/users/${id}`, { method: "DELETE" });
    apiCallCount++;
    loadAllData();
}

async function searchUsers(): Promise<void> {
    const el = document.getElementById("search-username") as HTMLInputElement;
    const username = el?.value || "";
    // ❌ SMELL-1: Unsanitized input
    const response = await fetch(`${API_URL}/users/search?username=${username}`);
    users = await response.json();
    apiCallCount++;
    renderUsers();
}

// ❌ SMELL-19: No validation on transfer — allows negative amounts, self-transfers
async function transferMoney(): Promise<void> {
    const fromEl = document.getElementById("transfer-from") as HTMLInputElement;
    const toEl = document.getElementById("transfer-to") as HTMLInputElement;
    const amtEl = document.getElementById("transfer-amount") as HTMLInputElement;

    const fromId = parseInt(fromEl?.value || "0");
    const toId = parseInt(toEl?.value || "0");
    const amount = parseFloat(amtEl?.value || "0");

    // ❌ SMELL-25: No error handling, no confirmation
    await fetch(`${API_URL}/accounts/transfer?fromId=${fromId}&toId=${toId}&amount=${amount}`, {
        method: "POST"
    });
    apiCallCount++;
    loadAllData();
}

async function generateReport(): Promise<void> {
    const typeEl = document.getElementById("report-type") as HTMLSelectElement;
    const reportType = typeEl?.value || "monthly";

    await fetch(`${API_URL}/reports/generate?reportType=${reportType}&userId=1`, {
        method: "POST"
    });
    apiCallCount++;
    loadReports();
}

// ❌ SMELL-18: Login with no security — sends credentials in query params!
async function login(): Promise<void> {
    const userEl = document.getElementById("login-user") as HTMLInputElement;
    const passEl = document.getElementById("login-pass") as HTMLInputElement;
    const username = userEl?.value || "";
    const password = passEl?.value || "";

    // ❌ SMELL-18: Credentials in POST body but no HTTPS enforcement
    const response = await fetch(`${API_URL}/auth/login?username=${username}&password=${password}`, {
        method: "POST"
    });
    const data = await response.json();

    if (data.Token) {
        // ❌ SMELL-2: Storing token in localStorage — vulnerable to XSS
        localStorage.setItem("auth_token", data.Token);
        localStorage.setItem("user_role", data.Role);
        console.log("Login successful:", data); // ❌ SMELL-11: Logging sensitive data to console
        alert("Login successful!");
    } else {
        alert("Login failed");
    }
}

// ══════════════════════════════════════════════════════════════════════════════
// RENDERING — ❌ SMELL-21: All rendering logic in one file, no components
// ══════════════════════════════════════════════════════════════════════════════

// ❌ SMELL-21: Monolithic render function for dashboard
function renderDashboard(): void {
    const container = document.getElementById("dashboard-content");
    if (!container) return;

    const categories = getCategoryBreakdown();
    // ❌ SMELL-18: innerHTML with no sanitization — XSS vulnerable
    container.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Income</h3>
                <p class="amount">${formatCurrency(totalIncome)}</p>
            </div>
            <div class="stat-card">
                <h3>Total Expenses</h3>
                <p class="amount expense">${formatCurrency(totalExpenses)}</p>
            </div>
            <div class="stat-card">
                <h3>Net Position</h3>
                <p class="amount ${netPosition < 0 ? "negative" : ""}">${formatCurrency(netPosition)}</p>
            </div>
            <div class="stat-card">
                <h3>Health Score</h3>
                <p class="${healthScore.toLowerCase()}">${healthScore}</p>
            </div>
        </div>
        <h3>Spending by Category</h3>
        ${categories.map(c => `
            <div>${c.name}: ${c.percentage}%
                <div class="bar" style="width: ${c.percentage}%"></div>
            </div>
        `).join("")}
    `;
}

// ❌ SMELL-21: Monolithic render for transactions table
function renderTransactions(): void {
    const container = document.getElementById("transactions-content");
    if (!container) return;

    // ❌ SMELL-18: innerHTML — XSS risk if transaction descriptions contain scripts
    container.innerHTML = `
        <table>
            <tr><th>ID</th><th>Description</th><th>Amount</th><th>Category</th><th>Type</th><th>Date</th></tr>
            ${transactions.map((tx: any) => `
                <tr>
                    <td>${tx.Id}</td>
                    <td>${tx.description}</td>
                    <td class="${tx.Type === "expense" ? "negative" : ""}">${formatCurrency(tx.Amount)}</td>
                    <td>${tx.category_name}</td>
                    <td>${tx.Type}</td>
                    <td>${tx.Date}</td>
                </tr>
            `).join("")}
        </table>
    `;
}

function renderUsers(): void {
    const container = document.getElementById("users-content");
    if (!container) return;

    container.innerHTML = `
        <table>
            <tr><th>ID</th><th>Username</th><th>Email</th><th>Role</th><th>Active</th><th>Actions</th></tr>
            ${users.map((u: any) => `
                <tr>
                    <td>${u.Id}</td>
                    <td>${u.UserName}</td>
                    <td>${u.Email}</td>
                    <td>${u.Role}</td>
                    <td>${u.IsActive}</td>
                    <td><button onclick="deleteUser(${u.Id})">Delete</button></td>
                </tr>
            `).join("")}
        </table>
    `;
}

function renderAccounts(): void {
    const container = document.getElementById("accounts-content");
    if (!container) return;

    container.innerHTML = `
        <table>
            <tr><th>ID</th><th>Name</th><th>Balance</th><th>Type</th></tr>
            ${accounts.map((a: any) => `
                <tr>
                    <td>${a.Id}</td>
                    <td>${a.Name}</td>
                    <td>${formatCurrency(a.Balance)}</td>
                    <td>${a.Type}</td>
                </tr>
            `).join("")}
        </table>
    `;
}

function renderReports(): void {
    const container = document.getElementById("reports-content");
    if (!container) return;

    container.innerHTML = reports.map((r: any) => `
        <div class="report-card">
            <h4>${r.Title}</h4>
            <p>${r.Content}</p>
            <small>Generated: ${r.GeneratedAt}</small>
        </div>
    `).join("");
}

function renderAdmin(): void {
    const container = document.getElementById("admin-content");
    if (!container) return;

    // ❌ SMELL-2: Displaying secrets (JWT, SMTP password, connection string) in admin UI
    container.innerHTML = `<pre>${JSON.stringify(adminStats, null, 2)}</pre>`;
}

function updateStatusBar(): void {
    const bar = document.getElementById("status-bar");
    if (bar) {
        bar.innerHTML = `Last updated: ${new Date().toLocaleString()} | API calls: ${apiCallCount}`;
    }
}

// ══════════════════════════════════════════════════════════════════════════════
// TAB NAVIGATION — ❌ SMELL-21: Manual tab management instead of router
// ══════════════════════════════════════════════════════════════════════════════

function switchTab(tab: string): void {
    activeTab = tab;
    const tabs = document.querySelectorAll(".tab-content");
    tabs.forEach(t => (t as HTMLElement).style.display = "none");

    const activePanel = document.getElementById(`tab-${tab}`);
    if (activePanel) activePanel.style.display = "block";

    const buttons = document.querySelectorAll(".nav-tabs button");
    buttons.forEach(b => b.classList.remove("active"));

    const activeButton = document.querySelector(`[data-tab="${tab}"]`);
    if (activeButton) activeButton.classList.add("active");

    // ❌ SMELL-24: Reload data on every tab switch — wasteful
    if (tab === "dashboard") { renderDashboard(); }
    if (tab === "admin") { loadAdminStats(); }
}

// ══════════════════════════════════════════════════════════════════════════════
// INITIALIZATION — ❌ SMELL-21: Everything bootstrapped from one place
// ══════════════════════════════════════════════════════════════════════════════

// ❌ SMELL-25: No DOMContentLoaded guard — script may run before DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    loadAllData();
    switchTab("dashboard");
});

// ❌ SMELL-16: Exposing functions to global scope for onclick handlers
(window as any).addTransaction = addTransaction;
(window as any).searchTransactions = searchTransactions;
(window as any).deleteUser = deleteUser;
(window as any).searchUsers = searchUsers;
(window as any).transferMoney = transferMoney;
(window as any).generateReport = generateReport;
(window as any).login = login;
(window as any).switchTab = switchTab;
(window as any).loadAdminStats = loadAdminStats;
