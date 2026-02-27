// ✅ SMELL-21 FIXED: Account table extracted into own component
// ✅ SMELL-18 FIXED: textContent — no innerHTML XSS risk
// ✅ SMELL-22 FIXED: Typed Account interface

import type { Account } from '../models/models.js';
import { formatCurrency } from '../utils/financialUtils.js';

export function renderAccounts(container: HTMLElement, accounts: Account[]): void {
  container.replaceChildren();

  if (accounts.length === 0) {
    const empty = document.createElement('p');
    empty.textContent = 'No accounts found.';
    container.appendChild(empty);
    return;
  }

  const table = document.createElement('table');
  const thead = document.createElement('thead');
  const hr = document.createElement('tr');
  for (const h of ['ID', 'Name', 'Balance', 'Type']) {
    const th = document.createElement('th');
    th.textContent = h;
    hr.appendChild(th);
  }
  thead.appendChild(hr);
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  for (const a of accounts) {
    const row = document.createElement('tr');
    for (const val of [String(a.id), a.name, formatCurrency(a.balance), a.type]) {
      const td = document.createElement('td');
      td.textContent = val;
      row.appendChild(td);
    }
    tbody.appendChild(row);
  }

  table.appendChild(tbody);
  container.appendChild(table);
}
