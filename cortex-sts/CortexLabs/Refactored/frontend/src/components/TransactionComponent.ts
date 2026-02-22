// ✅ SMELL-21 FIXED: Transaction table extracted into own component
// ✅ SMELL-18 FIXED: textContent instead of innerHTML — XSS eliminated
// ✅ SMELL-22 FIXED: Typed Transaction interface — no any[]

import type { Transaction } from '../models/models.js';
import { formatCurrency } from '../utils/financialUtils.js';

/** Renders the transactions table safely (no innerHTML). */
export function renderTransactions(container: HTMLElement, transactions: Transaction[]): void {
  container.replaceChildren();

  if (transactions.length === 0) {
    const empty = document.createElement('p');
    empty.textContent = 'No transactions found.';
    container.appendChild(empty);
    return;
  }

  const table = document.createElement('table');
  const headers = ['ID', 'Description', 'Amount', 'Category', 'Type', 'Date'];
  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  for (const h of headers) {
    const th = document.createElement('th');
    th.textContent = h;
    headerRow.appendChild(th);
  }
  thead.appendChild(headerRow);
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  for (const tx of transactions) {
    const row = document.createElement('tr');
    const cells = [
      String(tx.id),
      tx.description,
      formatCurrency(tx.amount),
      tx.category,
      tx.type,
      tx.date,
    ];
    cells.forEach((val, idx) => {
      const td = document.createElement('td');
      td.textContent = val;
      if (idx === 2 && tx.type === 'Expense') td.className = 'negative';
      row.appendChild(td);
    });
    tbody.appendChild(row);
  }

  table.appendChild(tbody);
  container.appendChild(table);
}
